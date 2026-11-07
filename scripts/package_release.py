"""Build and verify the zip assets published as a GitHub release.

Each task folder is self-contained: it holds its own images, labels and config.yaml,
so every archive works on its own after a single unzip. This script exists because:

1. The READMEs hardcode the release version in their download URLs. Building assets for
   a version the READMEs don't point at produces a release nobody can follow, so the
   version is checked against every README before anything is built.
2. Each archive is extracted on its own into an empty directory and checked there, which
   is exactly what a user following the README does.

Usage:
    python3 scripts/package_release.py --version v0.0.3      # build into dist/ + verify
    python3 scripts/package_release.py --verify-published v0.0.3   # check a live release
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"

REPO_URL = "https://github.com/lightly-ai/coco128_yolo"

# Fixed so that rebuilding the same commit produces byte-identical archives.
FIXED_DATE = (2025, 1, 1, 0, 0, 0)

# Asset name -> folder packed at the root of the archive. Pretraining and distillation
# have no asset of their own: they use object_detection/images/train2017.
ASSETS = {
    "object_detection": "object_detection",
    "instance_segmentation": "instance_segmentation",
    "panoptic_segmentation": "panoptic_segmentation",
    "semantic_segmentation": "semantic_segmentation",
}

# Sanity ceiling. A task archive is at most ~41 MB (128 images per split), so anything
# above this means something unexpected got packed.
MAX_TASK_ZIP_BYTES = 50 * 1024 * 1024

# Per task: (label dir template, label glob, expected count per split). Every task also
# ships images/{split} with exactly one image per label file.
EXPECTED_COUNTS = {
    "object_detection": ("object_detection/labels/{split}", "*.txt", 128),
    "instance_segmentation": ("instance_segmentation/labels/{split}", "*.txt", 100),
    "semantic_segmentation": ("semantic_segmentation/masks/{split}", "*.png", 100),
    "panoptic_segmentation": (
        "panoptic_segmentation/annotations/panoptic_{split}",
        "*.png",
        100,
    ),
}

SPLITS = ["train2017", "val2017"]


class VerifyError(Exception):
    """A built or published asset failed a correctness check."""


def check_readme_versions(version: str) -> None:
    """Abort unless every README download URL points at `version` and a known asset.

    Guards against the failure mode where the READMEs advertise one version and the
    release is cut under another, leaving every documented download a 404.
    """
    pattern = re.compile(re.escape(REPO_URL) + r"/releases/download/([^/]+)/([^\s`]+)")
    expected_assets = {f"{name}.zip" for name in ASSETS}
    problems = []
    urls_found = 0

    for readme in sorted(REPO.glob("*/README.md")) + [REPO / "README.md"]:
        for lineno, line in enumerate(readme.read_text().splitlines(), start=1):
            for found_version, asset in pattern.findall(line):
                urls_found += 1
                where = f"{readme.relative_to(REPO)}:{lineno}"
                if found_version != version:
                    problems.append(
                        f"{where}: URL points at {found_version}, releasing {version}"
                    )
                if asset not in expected_assets:
                    problems.append(f"{where}: unknown asset {asset}")

    if problems:
        raise VerifyError(
            "README download URLs disagree with the release:\n  "
            + "\n  ".join(problems)
            + f"\n\nEither release the version the READMEs point at, or update them to "
            f"{version} first."
        )
    if not urls_found:
        raise VerifyError("No download URLs found in any README - wrong repo layout?")
    print(f"READMEs: {urls_found} download URLs, all on {version}")


def add_file(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
    info.external_attr = 0o644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, path.read_bytes())


def walk_sorted(root: Path) -> list[Path]:
    """All files under `root`, sorted. Symlinks are rejected: archives must be
    self-contained, and Windows unzip tools don't restore symlinks."""
    entries = []
    for child in sorted(root.iterdir()):
        if child.name == ".DS_Store":
            continue
        if child.is_symlink():
            raise VerifyError(f"{child.relative_to(REPO)} is a symlink, expected real files")
        if child.is_file():
            entries.append(child)
        elif child.is_dir():
            entries.extend(walk_sorted(child))
    return entries


def build_asset(name: str, folder: str) -> Path:
    source = REPO / folder
    if not source.is_dir():
        raise VerifyError(f"Missing source folder {folder}/")

    out_path = DIST / f"{name}.zip"
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        entries = walk_sorted(source)
        for path in entries:
            # The task folder itself is the archive root, so unzipping creates
            # e.g. object_detection/ in the cwd, matching data="<task>/config.yaml".
            add_file(zf, path, str(path.relative_to(REPO)))

    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"Built {out_path.relative_to(REPO)}: {len(entries)} entries, {size_mb:.1f} MB")
    return out_path


def unzip(archive: Path, dest: Path) -> None:
    """Extract with the unzip CLI, the same tool the README tells users to run."""
    subprocess.run(
        ["unzip", "-q", "-o", str(archive), "-d", str(dest)],
        check=True,
        capture_output=True,
    )


def count_files(directory: Path, glob: str) -> int:
    return len(list(directory.glob(glob)))


def verify_asset(name: str, archive: Path) -> None:
    """Extract this asset alone into an empty temp dir and check it works."""
    size = archive.stat().st_size
    if size > MAX_TASK_ZIP_BYTES:
        raise VerifyError(
            f"{archive.name} is {size / 1024 / 1024:.1f} MB, over the "
            f"{MAX_TASK_ZIP_BYTES / 1024 / 1024:.0f} MB ceiling"
        )

    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise VerifyError(f"{archive.name}: {info.filename} is a symlink entry")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        unzip(archive, root)

        template, glob, expected = EXPECTED_COUNTS[name]
        for split in SPLITS:
            label_dir = root / template.format(split=split)
            image_dir = root / name / "images" / split
            for directory in (label_dir, image_dir):
                if not directory.is_dir():
                    raise VerifyError(f"Missing {directory.relative_to(root)}")
            actual = count_files(label_dir, glob)
            if actual != expected:
                raise VerifyError(
                    f"{label_dir.relative_to(root)}: {actual} files, expected {expected}"
                )
            check_images_match_labels(image_dir, label_dir, glob)

        if name == "panoptic_segmentation":
            for split in SPLITS:
                ann = root / f"panoptic_segmentation/annotations/panoptic_{split}.json"
                if not ann.is_file():
                    raise VerifyError(f"Missing {ann.relative_to(root)}")

        verify_config_paths(root / name / "config.yaml")

    print(f"Verified {archive.name}")


def check_images_match_labels(image_dir: Path, label_dir: Path, glob: str) -> None:
    """Every image has exactly one label file and vice versa, matched by file stem."""
    images = {p.stem for p in image_dir.iterdir() if p.name != ".DS_Store"}
    labels = {p.stem for p in label_dir.glob(glob)}
    problems = []
    if stray := sorted(p.name for p in image_dir.iterdir() if p.suffix != ".jpg" and p.name != ".DS_Store"):
        problems.append(f"non-jpg files {stray[:5]}")
    if unlabeled := sorted(images - labels):
        problems.append(f"{len(unlabeled)} images without labels, e.g. {unlabeled[:5]}")
    if orphaned := sorted(labels - images):
        problems.append(f"{len(orphaned)} labels without images, e.g. {orphaned[:5]}")
    if problems:
        raise VerifyError(f"{image_dir.parent.parent.name}/images/{image_dir.name}: " + "; ".join(problems))


def verify_config_paths(config: Path) -> None:
    """Every path referenced by a config must resolve, relative to the config itself."""
    if not config.is_file():
        raise VerifyError(f"Missing {config.name} in {config.parent.name}/")

    text = config.read_text()
    # Only the path-valued keys; `names:`/`classes:` entries are label maps.
    keys = ["train", "val", "images", "masks", "annotations", "path"]
    for line in text.splitlines():
        match = re.match(r"^\s*(" + "|".join(keys) + r"):\s*(\S+)\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        if key in ("train", "val") and value in ("", "|"):
            continue
        target = (config.parent / value).resolve()
        if not target.exists():
            raise VerifyError(
                f"{config.parent.name}/config.yaml: '{key}: {value}' resolves to "
                f"{target}, which does not exist"
            )
        if target.is_dir() and not any(target.iterdir()):
            raise VerifyError(
                f"{config.parent.name}/config.yaml: '{key}: {value}' resolves to an "
                "empty directory"
            )


def build(version: str) -> None:
    check_readme_versions(version)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    archives = {name: build_asset(name, folder) for name, folder in ASSETS.items()}

    print()
    for name in ASSETS:
        verify_asset(name, archives[name])

    total_mb = sum(p.stat().st_size for p in archives.values()) / 1024 / 1024
    print(f"\n{len(archives)} assets, {total_mb:.1f} MB total. Next:\n")
    print(f"  gh release create {version} \\")
    print(f'      --title "{version}" \\')
    print('      --notes "..." \\')
    print("      dist/*.zip\n")
    print("Do not delete or re-upload v0.0.1 or v0.0.2 - older lightly-train docs use them.")


def verify_published(version: str) -> None:
    """Download the assets from a live release and run the same checks on them."""
    with tempfile.TemporaryDirectory() as tmp:
        downloaded = {}
        for name in ASSETS:
            url = f"{REPO_URL}/releases/download/{version}/{name}.zip"
            dest = Path(tmp) / f"{name}.zip"
            print(f"Downloading {url}")
            result = subprocess.run(
                ["curl", "-fsSL", "-o", str(dest), url], capture_output=True
            )
            if result.returncode != 0:
                raise VerifyError(f"Could not download {url} (curl exit {result.returncode})")
            downloaded[name] = dest

        print()
        for name in ASSETS:
            verify_asset(name, downloaded[name])

    print(f"\nRelease {version} is complete and correct.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--version", help="Version to build assets for, e.g. v0.0.2")
    group.add_argument(
        "--verify-published",
        metavar="VERSION",
        help="Skip building; download and check an already-published release",
    )
    args = parser.parse_args()

    try:
        if args.verify_published:
            verify_published(args.verify_published)
        else:
            build(args.version)
    except VerifyError as error:
        print(f"\nFAILED: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
