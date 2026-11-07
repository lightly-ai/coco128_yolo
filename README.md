<div align="center">
  <a href="https://www.lightly.ai/lightly-train">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_dark.svg">
      <img src="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_light.svg" alt="LightlyTrain" width="400" style="max-width: 100%; height: auto;">
    </picture>
  </a>

<h1>COCO128 Example Datasets</h1>

<p><em>One small dataset per task, ready to train</em></p>

[![Documentation](https://img.shields.io/badge/Documentation-blue)](https://docs.lightly.ai/train/stable/)
[![LightlyTrain](https://img.shields.io/badge/lightly--train-%E2%89%A5%200.16.3-blue)](https://github.com/lightly-ai/lightly-train)
[![Discord](https://img.shields.io/discord/752876370337726585?logo=discord&logoColor=white&label=discord&color=7289da)](https://discord.gg/xvNJW94)

</div>

Small COCO subsets, one for every task that
[LightlyTrain](https://github.com/lightly-ai/lightly-train) supports. They all come from
the first 128 images of COCO train2017 and val2017.

Each task folder holds a `config.yaml`. Pass it straight to `data=`:

```python
import lightly_train

lightly_train.train_object_detection(
    out="out/my_experiment",
    model="ltdetrv2-s-coco",
    data="object_detection/config.yaml",
)
```

## Datasets

| Task | Folder | Images | Labels |
|---|---|---|---|
| Object detection | [`object_detection/`](object_detection) | 128 train, 128 val | YOLO boxes, class ids 0-79 |
| Instance segmentation | [`instance_segmentation/`](instance_segmentation) | 100 train, 100 val | YOLO-seg polygons, 80 thing classes |
| Panoptic segmentation | [`panoptic_segmentation/`](panoptic_segmentation) | 100 train, 100 val | COCO panoptic JSON and mask PNGs |
| Semantic segmentation | [`semantic_segmentation/`](semantic_segmentation) | 100 train, 100 val | Class-index PNG masks, 130 classes |

Every task folder is self-contained: it holds its own images, labels and `config.yaml`.
[Provenance](#provenance) explains why three of the tasks have only 100 images per split.

Pretraining and distillation need no labels. Use the object detection images:
`data="object_detection/images/train2017"`.

## Requirements

lightly-train 0.16.3 or later. Older versions resolve the relative paths inside a
`config.yaml` against the working directory, not against the location of the config file.

## Download

Each task is one archive. Take the line for your task:

```bash
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.3/object_detection.zip && unzip -q object_detection.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.3/instance_segmentation.zip && unzip -q instance_segmentation.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.3/panoptic_segmentation.zip && unzip -q panoptic_segmentation.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.3/semantic_segmentation.zip && unzip -q semantic_segmentation.zip
```

## Layout

Each archive unzips into one task folder:

```text
object_detection/
├── config.yaml
├── images/
│   ├── train2017/          128 images
│   └── val2017/            128 images
└── labels/
    ├── train2017/          128 label files
    └── val2017/            128 label files
```

The paths in `config.yaml` are relative to the config file, so the folder works wherever
you put it. Reference it as `data="object_detection/config.yaml"` from the directory you
unzipped into.

Older releases: `v0.0.2` used a shared `images.zip` plus a symlink in each task folder.
`v0.0.1` shipped a single flat `coco128_yolo.zip`. Both stay available for older docs.

## Provenance

- `object_detection/`: the original first-128-image YOLO subset. Its train images are
  also the unlabeled set formerly published as `lightly-ai/coco128_unlabeled`. Two train
  images (`000000000250`, `000000000508`) contain no objects and have empty label files.
  Up to `v0.0.2`, their label files were missing and two label files for images outside
  the subset (`000000000656`, `000000000659`) were shipped instead.
- `panoptic_segmentation/`: migrated from the original `lightly-ai/coco128_panoptic`
  repo. See `scripts/trim_panoptic.py`.
- `instance_segmentation/`: YOLO-seg polygon labels, built from the COCO panoptic
  annotations in `panoptic_segmentation/` (thing classes only). See
  `scripts/build_instance_segmentation.py`. The class ids are the COCO panoptic category
  ids, not the contiguous 0-79 ids that `object_detection/` uses.
- `semantic_segmentation/`: single-channel class-index PNG masks, built from the same
  panoptic annotations (thing and stuff classes). See
  `scripts/build_semantic_segmentation.py`. Class id `0` means "unlabeled".

### Why three tasks have only 100 images

The upstream `coco128_panoptic` repo listed 128 annotation entries per split, but shipped
only 100 mask PNGs. The upload was incomplete. Both splits were trimmed to the 100 images
that have a mask. `instance_segmentation/` and `semantic_segmentation/` come from
`panoptic_segmentation/`, so all three cover the same 100 train and 100 val images, and
each ships exactly those images.

## Maintainers

See [RELEASE.md](RELEASE.md) for how to build the download assets and cut a release.

## About Lightly

[Lightly](https://www.lightly.ai) builds open-source tools for computer vision teams.

<p>
<a href="https://github.com/lightly-ai/lightly-train"><picture><source media="(prefers-color-scheme: dark)" srcset="https://storage.googleapis.com/lightly-public/train/lightlytrain_standard_horizontal_light.png"><img src="https://storage.googleapis.com/lightly-public/train/lightlytrain_standard_horizontal_dark.png" alt="LightlyTrain" height="40"/></picture></a>
<span>&nbsp;&nbsp;&nbsp;&nbsp;</span>
<a href="https://github.com/lightly-ai/lightly-studio"><picture><source media="(prefers-color-scheme: dark)" srcset="https://storage.googleapis.com/lightly-public/studio/lightlystudio_standard_horizontal_light.png"><img src="https://storage.googleapis.com/lightly-public/studio/lightlystudio_standard_horizontal_dark.png" alt="LightlyStudio" height="40"/></picture></a>
</p>

- [LightlyTrain](https://github.com/lightly-ai/lightly-train) — pretraining, fine-tuning
  and distillation. The datasets here are its example data.
- [LightlyStudio](https://github.com/lightly-ai/lightly-studio) — curate, annotate and
  manage image datasets.
- [LightlySSL](https://github.com/lightly-ai/lightly) — self-supervised learning
  framework.

Questions go to [Discord](https://discord.gg/xvNJW94). For commercial use,
[contact us](https://www.lightly.ai/contact).
