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

| Task | Folder | Images used | Labels |
|---|---|---|---|
| Object detection | [`object_detection/`](object_detection) | 128 train, 128 val | YOLO boxes, class ids 0-79 |
| Instance segmentation | [`instance_segmentation/`](instance_segmentation) | 100 train, 100 val | YOLO-seg polygons, 80 thing classes |
| Panoptic segmentation | [`panoptic_segmentation/`](panoptic_segmentation) | 100 train, 100 val | COCO panoptic JSON and mask PNGs |
| Semantic segmentation | [`semantic_segmentation/`](semantic_segmentation) | 100 train, 100 val | Class-index PNG masks, 130 classes |
| Pretraining, distillation | [`pretrain_distill/`](pretrain_distill) | 128 train | none |

The `images/` pool always holds 128 train and 128 val images. [Provenance](#provenance)
explains why three of the tasks label only 100 of them.

## Requirements

lightly-train 0.16.3 or later. Older versions resolve a relative `data=` path against the
working directory, not against the location of the config file. This breaks the
`../images/...` paths that the mask-based configs use.

## Download

A labeled task needs two archives: the shared image pool, and the labels for that task.
Unzip both into the same directory.

```bash
# The image pool. Every task needs it.
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip

# The labels. Take the line for your task.
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/object_detection.zip && unzip -q object_detection.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/instance_segmentation.zip && unzip -q instance_segmentation.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/panoptic_segmentation.zip && unzip -q panoptic_segmentation.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/semantic_segmentation.zip && unzip -q semantic_segmentation.zip
```

Pretraining and distillation use no labels. For those two, `images.zip` is the whole
download. Point `data` at `images/train2017`.

## Layout

The archives carry no wrapper directory. After you unzip, the task folder and `images/`
are siblings:

```text
.
├── images/
│   ├── train2017/          128 images
│   └── val2017/            128 images
└── object_detection/
    ├── config.yaml
    ├── images -> ../images
    └── labels/
```

Each config points at `images/` by a relative path, so this layout is what makes the
paths resolve. Run your training script from this directory. Then reference the data as
`data="object_detection/config.yaml"`.

All five tasks read the same `images/` pool. You download the image bytes one time, for
any number of tasks.

### The images symlink

In `object_detection/` and `instance_segmentation/`, the `images` entry is a symlink to
`../images`. It is not a real directory. The YOLO loader in lightly-train takes the
labels directory from the same base path as the images directory. The two must therefore
be siblings inside one task folder.

Most versions of `unzip` keep the symlink. Some Windows zip tools write it out as a text
file that holds the target path. If that happens, make the link by hand:

```
ln -s ../images object_detection/images         # macOS, Linux
mklink /D object_detection\images ..\images     # Windows
```

Do the same for `instance_segmentation/images`.

## Provenance

- `object_detection/`, `pretrain_distill/`: the original first-128-image YOLO and
  unlabeled subsets. Only the folder location changed.
- `panoptic_segmentation/`: migrated from the original `coco128_panoptic` repo. See
  `scripts/trim_panoptic.py`.
- `instance_segmentation/`: YOLO-seg polygon labels, built from the COCO panoptic
  annotations in `panoptic_segmentation/` (thing classes only). See
  `scripts/build_instance_segmentation.py`. The class ids are the COCO panoptic category
  ids, not the contiguous 0-79 ids that `object_detection/` uses.
- `semantic_segmentation/`: single-channel class-index PNG masks, built from the same
  panoptic annotations (thing and stuff classes). See
  `scripts/build_semantic_segmentation.py`. Class id `0` means "unlabeled".

### Why three tasks label only 100 images

The upstream `coco128_panoptic` repo listed 128 annotation entries per split, but shipped
only 100 mask PNGs. The upload was incomplete. Both splits were trimmed to the 100 images
that have a mask. `instance_segmentation/` and `semantic_segmentation/` come from
`panoptic_segmentation/`, so all three cover the same 100 train and 100 val images.

The `images/` pool keeps all 128 images per split, because object detection and
pretraining need them. The mask-based loaders in lightly-train skip an image with no
matching mask, and `instance_segmentation/config.yaml` sets
`skip_if_label_file_missing: true` for the same reason. `scripts/trim_panoptic.py` now
trims the panoptic annotation JSON only. It no longer deletes images.

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
