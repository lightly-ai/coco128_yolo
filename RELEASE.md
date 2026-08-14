# Cutting a release

The five zip assets attached to a GitHub release are what the download URLs in every
README point at. They are built by `scripts/package_release.py`, never by hand — see
[Why not just `zip -r`](#why-not-just-zip--r) below.

## Never touch v0.0.1

**Do not delete, retag, or re-upload the `v0.0.1` release or its `coco128_yolo.zip`
asset.** The published lightly-train docs download it directly:

- `docs/source/quick_start_object_detection.md`
- `docs/source/quick_start_distillation.md`
- `examples/notebooks/object_detection.ipynb`
- `examples/notebooks/distillation.ipynb`

All four `wget` `.../releases/download/v0.0.1/coco128_yolo.zip` and inline their own
`data=` dict, so they are unaffected by the repo layout — but only for as long as that
asset exists byte-for-byte. It has the old flat `coco128_yolo/{images,labels}` shape with
a wrapper directory, which newer releases deliberately do not. The release is marked
`immutable: false`, so nothing on GitHub's side prevents an accidental overwrite.

Once the docs are updated to the new layout, this constraint can be revisited.

## Steps

1. **Start from a clean, up-to-date `main`.** The assets are built from the working tree,
   so anything uncommitted ends up in the release.

   ```bash
   git checkout main && git pull && git status
   ```

2. **Build and verify.** Takes about a minute, writes to `dist/` (gitignored).

   ```bash
   python3 scripts/package_release.py --version v0.0.2
   ```

   This refuses to build unless every README download URL already points at the version
   you named, then checks each archive by extracting it into a temp directory and
   confirming the symlinks survived, the configs' relative paths resolve, and the file
   counts are right. If it prints anything other than a clean run, stop and fix it —
   a broken asset is far more annoying to withdraw than to not publish.

   Expected output ends with the five assets at roughly:

   | Asset | Size |
   |---|---|
   | `images.zip` | 40.2 MB |
   | `panoptic_segmentation.zip` | 1.3 MB |
   | `semantic_segmentation.zip` | 0.9 MB |
   | `instance_segmentation.zip` | 0.3 MB |
   | `object_detection.zip` | 0.1 MB |

3. **Publish.** This creates the tag from the current `main` — no separate `git tag`
   push needed.

   ```bash
   gh release create v0.0.2 \
       --title "v0.0.2" \
       --notes-file notes.md \
       dist/*.zip
   ```

   See [Release notes](#release-notes) for what to put in `notes.md`.

4. **Verify what actually got published**, by downloading the assets back from their
   public URLs and re-running the same checks:

   ```bash
   python3 scripts/package_release.py --verify-published v0.0.2
   ```

5. **Spot-check one README command verbatim** in an empty directory — the thing a user
   will actually copy and paste:

   ```bash
   cd "$(mktemp -d)"
   wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip
   wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/object_detection.zip && unzip -q object_detection.zip
   ls -la object_detection/images        # must show: images -> ../images
   ```

## Bumping the version

The version is hardcoded in the download URLs across all six READMEs (root plus one per
task folder). To release a new version, **edit those URLs first**, in the same commit as
whatever data change prompted the release. `package_release.py` will refuse to build for
a version the READMEs don't agree on — that check exists because the first attempt at
this release was built as `v0.1.0` while the docs said otherwise.

```bash
grep -rn "releases/download" --include="*.md" .    # every URL that needs updating
```

## Adding or removing an asset

Edit the `ASSETS` dict in `scripts/package_release.py`, and add matching entries to
`EXPECTED_COUNTS` (and `SYMLINKED_TASKS` if the new folder carries an `images` symlink).
The README check derives its set of valid asset filenames from `ASSETS`, so a folder that
is documented but not packaged — or packaged but not documented — fails the build rather
than shipping a dead link.

`pretrain_distill/` deliberately has no asset: it contains only a README, and the data it
trains on is `images/train2017` from the shared pool.

## Why not just `zip -r`

`object_detection/images` and `instance_segmentation/images` are symlinks to `../images`,
so that lightly-train's YOLO loader — which derives the labels directory from the images
path — sees labels and images as siblings under one task folder, while the image bytes
live in the shared pool.

Plain `zip -r object_detection.zip object_detection` **follows** that symlink and writes a
full copy of all 256 images into the archive: 40 MB instead of 0.1 MB, once per YOLO task,
which is precisely the duplication the shared pool exists to avoid. `zip --symlinks` gets
this right; the script does too, storing the link target as the entry contents with the
symlink bit set. Both the size ceiling and the post-extraction symlink assertion in the
verification step catch a regression here.

One related trap, if you ever rewrite the verification: `zipfile.extractall()` does *not*
restore symlinks — it writes them out as regular files containing the target path. The
script shells out to the `unzip` CLI instead, which restores them properly and is also
the command the READMEs tell users to run.

## Release notes

Worth covering for the first release on the new layout:

- Restructured into per-task folders; every task has a `config.yaml` usable directly as
  `data=`.
- One shared `images/` pool: **every labeled task needs `images.zip` plus its own task
  zip**, unzipped into the same directory.
- Archives have no wrapper directory (unlike `v0.0.1`), so they unzip as siblings into
  the current directory.
- Requires `lightly-train >= 0.16.3`, which resolves relative `data=` paths against the
  config file's location rather than the working directory.
- `v0.0.1` remains available and is what the current lightly-train docs reference.
