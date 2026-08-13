# coco128

Small, ready-to-use example datasets for every task
[LightlyTrain](https://github.com/lightly-ai/lightly-train) supports training, all
derived from the first 128 images of COCO train2017 / val2017. Each task has its own
subfolder with a `config.yaml` that works directly as `data=` input to the
corresponding `lightly_train.train_*` function, and its own release asset so you only
have to download the data you actually need.

| Task | Folder | Download |
|---|---|---|
| Object detection | [`object_detection/`](object_detection) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/object_detection.zip && unzip -q object_detection.zip` |
| Instance segmentation | [`instance_segmentation/`](instance_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/instance_segmentation.zip && unzip -q instance_segmentation.zip` |
| Panoptic segmentation | [`panoptic_segmentation/`](panoptic_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/panoptic_segmentation.zip && unzip -q panoptic_segmentation.zip` |
| Semantic segmentation | [`semantic_segmentation/`](semantic_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/semantic_segmentation.zip && unzip -q semantic_segmentation.zip` |
| Pretraining / distillation | [`pretrain_distill/`](pretrain_distill) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/pretrain_distill.zip && unzip -q pretrain_distill.zip` |

Each `wget ... && unzip` command extracts straight into the current directory (e.g.
`object_detection/`), so run it in the same directory as your training script and
reference the data as `data="object_detection/config.yaml"`.

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
`panoptic_segmentation/`, all three cover the same 100 train / 100 val images.
