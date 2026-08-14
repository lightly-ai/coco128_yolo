"""Build and verify the zip assets published as a GitHub release.

Two things make this release easy to get wrong by hand, which is why it is a script:

1. object_detection/images and instance_segmentation/images are symlinks to ../images.
   A plain `zip -r` follows them and bakes a full 41 MB copy of the image pool into each
   of those archives, silently undoing the deduplication the repo layout is built around.
   Here they are written as real symlink entries instead (see add_symlink).
2. The READMEs hardcode the release version in their download URLs. Building assets for
   a version the READMEs don't point at produces a release nobody can follow, so the
   version is checked against every README before anything is built.

Usage:
    python3 scripts/package_release.py --version v0.0.2      # build into dist/ + verify
    python3 scripts/package_release.py --verify-published v0.0.2   # check a live release
"""

import argparse
import os
import re
import shutil
import stat
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

# Asset name -> folder packed at the root of the archive. pretrain_distill/ is
# deliberately absent: it holds only a README, and the data it trains on is
# images/train2017 from the shared pool, so it needs no asset of its own.
ASSETS = {
    "images": "images",
    "object_detection": "object_detection",
    "instance_segmentation": "instance_segmentation",
    "panoptic_segmentation": "panoptic_segmentation",
    "semantic_segmentation": "semantic_segmentation",
}

# Task folders whose images/ entry must survive as a symlink to ../images.
SYMLINKED_TASKS = ["object_detection", "instance_segmentation"]

# A task archive that accidentally swallowed the image pool is ~42 MB, so anything
# above this ceiling means the symlink handling broke.
MAX_TASK_ZIP_BYTES = 5 * 1024 * 1024

# Expected file counts per split, verified after extraction.
EXPECTED_COUNTS = {
    "images": ("images/{split}", 128, "*.jpg"),
    "object_detection": ("object_detection/labels/{split}", 128, "*.txt"),
    "instance_segmentation": ("instance_segmentation/labels/{split}", 100, "*.txt"),
    "semantic_segmentation": ("semantic_segmentation/masks/{split}", 100, "*.png"),
    "panoptic_segmentation": (
        "panoptic_segmentation/annotations/panoptic_{split}",
        100,
        "*.png",
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


def add_symlink(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    """Store a symlink as a link entry rather than following it.

    The link target becomes the entry's contents and the symlink bit is set in the
    high half of external_attr, which is how Info-ZIP records symlinks and how `unzip`
    recognises them on extraction.
    """
    info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
    info.create_system = 3  # Unix, so the mode bits below are honoured.
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    zf.writestr(info, os.readlink(path))


def walk_sorted(root: Path) -> list[Path]:
    """All entries under `root`, sorted, without descending into symlinked dirs."""
    entries = []
    for child in sorted(root.iterdir()):
        if child.name == ".DS_Store":
            continue
        if child.is_symlink() or child.is_file():
            entries.append(child)
        elif child.is_dir():
            entries.extend(walk_sorted(child))
    return entries


def build_asset(name: str, folder: str) -> Path:
    source = REPO / folder
    if not source.is_dir():
        raise VerifyError(f"Missing source folder {folder}/")

    out_path = DIST / f"{name}.zip"
    symlinks = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        entries = walk_sorted(source)
        for path in entries:
            # Archives contain no wrapper directory: the folder itself is the root, so
            # unzipping drops images/ and object_detection/ as siblings in the cwd,
            # which is what the relative paths in the task configs assume.
            arcname = str(path.relative_to(REPO))
            if path.is_symlink():
                add_symlink(zf, path, arcname)
                symlinks += 1
            else:
                add_file(zf, path, arcname)

    size_mb = out_path.stat().st_size / 1024 / 1024
    suffix = f", {symlinks} symlink(s)" if symlinks else ""
    print(f"Built {out_path.relative_to(REPO)}: {len(entries)} entries{suffix}, {size_mb:.1f} MB")
    return out_path


def unzip(archive: Path, dest: Path) -> None:
    """Extract with the unzip CLI, which restores symlinks.

    zipfile.extractall() does not: it writes a symlink entry out as a regular file
    containing the target path, so verifying through it would pass on an archive that
    is broken for anyone following the README.
    """
    subprocess.run(
        ["unzip", "-q", "-o", str(archive), "-d", str(dest)],
        check=True,
        capture_output=True,
    )


def count_files(directory: Path, glob: str) -> int:
    return len(list(directory.glob(glob)))


def verify_asset(name: str, archives: dict[str, Path]) -> None:
    """Extract images.zip + this asset into a temp dir and check it works."""
    archive = archives[name]

    if name != "images" and archive.stat().st_size > MAX_TASK_ZIP_BYTES:
        raise VerifyError(
            f"{archive.name} is {archive.stat().st_size / 1024 / 1024:.1f} MB, over the "
            f"{MAX_TASK_ZIP_BYTES / 1024 / 1024:.0f} MB ceiling - it probably swallowed "
            "the image pool through a followed symlink."
        )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        unzip(archives["images"], root)
        if name != "images":
            unzip(archive, root)

        if name in SYMLINKED_TASKS:
            link = root / name / "images"
            if not link.is_symlink():
                raise VerifyError(
                    f"{name}/images extracted as a {'directory' if link.is_dir() else 'file'}, "
                    "not a symlink"
                )
            target = os.readlink(link)
            if target != "../images":
                raise VerifyError(f"{name}/images points at {target!r}, expected '../images'")
            # Reading through the link is the thing lightly-train actually does.
            through_link = count_files(link / "train2017", "*.jpg")
            if through_link != 128:
                raise VerifyError(
                    f"{name}/images/train2017 lists {through_link} images through the "
                    "symlink, expected 128"
                )

        template, expected, glob = EXPECTED_COUNTS[name]
        for split in SPLITS:
            directory = root / template.format(split=split)
            if not directory.is_dir():
                raise VerifyError(f"Missing {directory.relative_to(root)}")
            actual = count_files(directory, glob)
            if actual != expected:
                raise VerifyError(
                    f"{directory.relative_to(root)}: {actual} files, expected {expected}"
                )

        if name == "panoptic_segmentation":
            for split in SPLITS:
                ann = root / f"panoptic_segmentation/annotations/panoptic_{split}.json"
                if not ann.is_file():
                    raise VerifyError(f"Missing {ann.relative_to(root)}")

        if name != "images":
            verify_config_paths(root / name / "config.yaml")

    print(f"Verified {archive.name}")


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
        verify_asset(name, archives)

    total_mb = sum(p.stat().st_size for p in archives.values()) / 1024 / 1024
    print(f"\n{len(archives)} assets, {total_mb:.1f} MB total. Next:\n")
    print(f"  gh release create {version} \\")
    print(f'      --title "{version}" \\')
    print('      --notes "..." \\')
    print("      dist/*.zip\n")
    print("Do not delete or re-upload v0.0.1 - the published lightly-train docs use it.")


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
            verify_asset(name, downloaded)

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
