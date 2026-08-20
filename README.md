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

Example datasets for every task
[LightlyTrain](https://github.com/lightly-ai/lightly-train) supports, all derived from
the first 128 images of COCO train2017 / val2017. Each task has its own subfolder with a
`config.yaml` that works directly as `data=` input to the corresponding
`lightly_train.train_*` function. All tasks share one `images/` pool (released as its own
`images.zip` asset) instead of each shipping its own copy, so you only have to download
the image bytes once no matter how many tasks you use.

Requires `lightly-train >= 0.16.3` — earlier versions resolve relative `data=` paths
against the current working directory instead of the YAML config file's location, which
breaks the `../images/...` references used by the mask-based task configs below.

| Task | Folder | Download |
|---|---|---|
| Object detection | [`object_detection/`](object_detection) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/object_detection.zip && unzip -q object_detection.zip` |
| Instance segmentation | [`instance_segmentation/`](instance_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/instance_segmentation.zip && unzip -q instance_segmentation.zip` |
| Panoptic segmentation | [`panoptic_segmentation/`](panoptic_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/panoptic_segmentation.zip && unzip -q panoptic_segmentation.zip` |
| Semantic segmentation | [`semantic_segmentation/`](semantic_segmentation) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip && wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/semantic_segmentation.zip && unzip -q semantic_segmentation.zip` |
| Pretraining / distillation | [`pretrain_distill/`](pretrain_distill) | `wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip` |

Every labeled task needs `images.zip` (the shared image pool) plus its own task zip.
Unzip both into the same directory — the task zip's `config.yaml` references `images/` by
relative path (directly, or through an `images` symlink for the YOLO-format tasks), so
`images/` must end up as a sibling of e.g. `object_detection/`. Run your training script
from that same directory and reference the data as `data="object_detection/config.yaml"`.
Pretraining / distillation needs no labels, so `images.zip` on its own is enough — point
`data` straight at `images/train2017`.

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
