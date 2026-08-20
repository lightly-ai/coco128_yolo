<div align="center">
  <a href="https://www.lightly.ai/lightly-train">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_dark.svg">
      <img src="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_light.svg" alt="LightlyTrain" width="280" style="max-width: 100%; height: auto;">
    </picture>
  </a>
</div>

# Semantic segmentation

100 train and 100 val images from the COCO dataset, with single-channel semantic
segmentation masks. The masks cover both thing and stuff classes.

The masks come from the COCO panoptic annotations in `panoptic_segmentation/`. Every
pixel was mapped to the category id of its panoptic segment by
`../scripts/build_semantic_segmentation.py`. Class id `0` means "unlabeled": no panoptic
segment covers that pixel.

## Download

Unzip both archives into the same directory.

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/semantic_segmentation.zip && unzip -q semantic_segmentation.zip
```

## Train

Pass the config straight to `lightly_train.train_semantic_segmentation`:

```python
import lightly_train

lightly_train.train_semantic_segmentation(
    out="out/my_experiment",
    model="dinov2/vitl14-eomt",
    data="semantic_segmentation/config.yaml",
)
```

---

Part of [coco128_yolo](https://github.com/lightly-ai/coco128_yolo), the example datasets
for [LightlyTrain](https://github.com/lightly-ai/lightly-train) ·
[Docs](https://docs.lightly.ai/train/stable/) · [Discord](https://discord.gg/xvNJW94)
