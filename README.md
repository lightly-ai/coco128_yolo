# coco128

Small, ready-to-use example datasets for every task
[LightlyTrain](https://github.com/lightly-ai/lightly-train) supports training, all
derived from the first 128 images of COCO train2017 / val2017. Each task has its own
subfolder with a `config.yaml` that works directly as `data=` input to the
corresponding `lightly_train.train_*` function. All tasks share one `images/` pool
(released as its own `images.zip` asset) instead of each shipping its own copy, so you
only have to download the image bytes once no matter how many tasks you use.

Requires `lightly-train >= 0.16.3` — earlier versions resolve relative `data=` paths
against the current working directory instead of the YAML config file's location, which
breaks the `../images/...` references used by the mask-based task configs below.

| Task | Folder | Download |
|---|---|---|
| Object detection | [`object_detection/`](object_detection) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/object_detection.zip && unzip -q object_detection.zip` |
| Instance segmentation | [`instance_segmentation/`](instance_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/instance_segmentation.zip && unzip -q instance_segmentation.zip` |
| Panoptic segmentation | [`panoptic_segmentation/`](panoptic_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/panoptic_segmentation.zip && unzip -q panoptic_segmentation.zip` |
| Semantic segmentation | [`semantic_segmentation/`](semantic_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/semantic_segmentation.zip && unzip -q semantic_segmentation.zip` |
| Pretraining / distillation | [`pretrain_distill/`](pretrain_distill) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/pretrain_distill.zip && unzip -q pretrain_distill.zip` |

Every task needs `images.zip` (the shared image pool) plus its own task zip. Unzip both
into the same directory — the task zip's `config.yaml` references `images/` by relative
path (directly, or through an `images` symlink for the YOLO-format tasks), so `images/`
must end up as a sibling of e.g. `object_detection/`. Run your training script from that
same directory and reference the data as `data="object_detection/config.yaml"`.

`object_detection.zip` and `instance_segmentation.zip` ship an `images` entry that's a
**symlink** to `../images`, not a real directory (required because lightly-train's YOLO
loader derives the labels directory from the same base path as the images directory, so
they must be siblings under one task folder even though the images themselves live in
the shared pool). Most `unzip` versions preserve this correctly. If you're on a tool that
doesn't (e.g. some Windows zip clients materialize it as a text file with the target path
instead of a real symlink), recreate it manually:
```
ln -s ../images object_detection/images        # macOS/Linux
mklink /D object_detection\images ..\images     # Windows
```
(and the same for `instance_segmentation/images`).

## Provenance

- `object_detection/`, `pretrain_distill/`: the original first-128-image YOLO and
  unlabeled subsets, unchanged apart from folder location.
- `panoptic_segmentation/`: migrated from the original `coco128_panoptic` repo. The
  upstream repo was missing 28 of the 128 panoptic mask PNGs in each split (an
  incomplete upload); both splits were trimmed down to the 100 images that have a
  matching mask, see `scripts/trim_panoptic.py`.
- `instance_segmentation/`: YOLO-seg polygon labels derived from
  `panoptic_segmentation/`'s COCO panoptic annotations (thing classes only), see
  `scripts/build_instance_segmentation.py`. Class ids match the COCO panoptic category
  ids.
- `semantic_segmentation/`: single-channel class-index PNG masks derived from the same
  panoptic annotations (thing + stuff classes), see
  `scripts/build_semantic_segmentation.py`. Class id `0` means "unlabeled".

Because `instance_segmentation/` and `semantic_segmentation/` are both derived from
`panoptic_segmentation/`, all three cover the same 100 train / 100 val images — but all
five tasks reference the same top-level `images/` pool (128 train / 128 val), since
lightly-train's mask-based loaders silently skip any image with no matching mask, and
`instance_segmentation/config.yaml` sets `skip_if_label_file_missing: true` for the same
reason. `scripts/trim_panoptic.py` only trims the panoptic annotation JSON now; it no
longer deletes images, since `images/` is shared with tasks that need the full 128.
