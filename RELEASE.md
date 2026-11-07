# Cutting a release

The four zip assets attached to a GitHub release are what the download URLs in every
README point at. They are built by `scripts/package_release.py`, never by hand.

## Never touch old releases

**Do not delete, retag, or re-upload `v0.0.1` or `v0.0.2`.** Docs of already-released
lightly-train versions download them directly:

- `v0.0.1/coco128_yolo.zip`: the old flat `coco128_yolo/{images,labels}` layout with a
  wrapper directory. Used by lightly-train docs and notebooks before the per-task layout.
- `v0.0.2`: a shared `images.zip` plus one task zip each, linked by an
  `images -> ../images` symlink. Superseded by `v0.0.3`.

Both are marked `immutable: false`, so nothing on GitHub's side prevents an accidental
overwrite.

## Steps

1. **Start from a clean, up-to-date `main`.** The assets are built from the working tree,
   so anything uncommitted ends up in the release.

   ```bash
   git checkout main && git pull && git status
   ```

2. **Build and verify.** Takes about a minute, writes to `dist/` (gitignored).

   ```bash
   python3 scripts/package_release.py --version v0.0.3
   ```

   This refuses to build unless every README download URL already points at the version
   you named. It then extracts each archive **on its own** into an empty temp directory
   and checks that:

   - there are no symlinks in the archive,
   - every image has exactly one label file and vice versa,
   - the file counts are right,
   - the config's relative paths resolve.

   If it prints anything other than a clean run, stop and fix it. A broken asset is far
   more annoying to withdraw than to not publish.

   Expected sizes, roughly:

   | Asset | Size |
   |---|---|
   | `object_detection.zip` | 40 MB |
   | `panoptic_segmentation.zip` | 33 MB |
   | `semantic_segmentation.zip` | 33 MB |
   | `instance_segmentation.zip` | 32 MB |

3. **Publish.** This creates the tag from the current `main`, no separate `git tag`
   push needed.

   ```bash
   gh release create v0.0.3 \
       --title "v0.0.3" \
       --notes-file notes.md \
       dist/*.zip
   ```

   See [Release notes](#release-notes) for what to put in `notes.md`.

4. **Verify what actually got published**, by downloading the assets back from their
   public URLs and re-running the same checks:

   ```bash
   python3 scripts/package_release.py --verify-published v0.0.3
   ```

5. **Spot-check one README command verbatim** in an empty directory, the thing a user
   will actually copy and paste:

   ```bash
   cd "$(mktemp -d)"
   wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.3/object_detection.zip && unzip -q object_detection.zip
   ls object_detection        # config.yaml  images  labels  README.md
   ```

## Bumping the version

The version is hardcoded in the download URLs across all five READMEs (root plus one per
task folder). To release a new version, **edit those URLs first**, in the same commit as
whatever data change prompted the release. `package_release.py` refuses to build for a
version the READMEs don't agree on.

```bash
grep -rn "releases/download" --include="*.md" .    # every URL that needs updating
```

## Adding or removing an asset

Edit the `ASSETS` dict in `scripts/package_release.py`, and add a matching entry to
`EXPECTED_COUNTS`. The README check derives its set of valid asset filenames from
`ASSETS`, so a folder that is documented but not packaged, or packaged but not
documented, fails the build rather than shipping a dead link.

A new task folder must be self-contained: its own `images/`, its labels, and a
`config.yaml` whose paths stay inside the folder. Copy the images in as real files, not
symlinks. Git stores identical files as one blob, so duplicates across task folders
don't grow the repo. The build rejects symlinks.

## Release notes

Worth covering for `v0.0.3`:

- Every task zip is self-contained: images, labels and `config.yaml` in one folder. One
  download per task, no symlinks, works with Windows unzip tools.
- `images.zip` is gone. For pretraining and distillation, use
  `object_detection/images/train2017`.
- Instance, semantic and panoptic segmentation ship only the 100 images per split that
  have labels. `instance_segmentation/config.yaml` no longer needs
  `skip_if_label_file_missing`.
- Requires `lightly-train >= 0.16.3`, which resolves relative paths in a config file
  against the config file's location.
- `v0.0.1` and `v0.0.2` remain available for older docs.
