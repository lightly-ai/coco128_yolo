<div align="center">
  <a href="https://www.lightly.ai/lightly-train">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_dark.svg">
      <img src="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_light.svg" alt="LightlyTrain" width="280" style="max-width: 100%; height: auto;">
    </picture>
  </a>
</div>

# Instance segmentation

100 train and 100 val images from the COCO dataset with YOLO-seg polygon instance
segmentation labels ("thing" classes only).

Derived from `panoptic_segmentation/`'s COCO panoptic annotations by converting each
instance's panoptic mask to a polygon — see `../scripts/build_instance_segmentation.py`.
Class ids match the COCO panoptic "thing" category ids.

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/instance_segmentation.zip && unzip -q instance_segmentation.zip
```

Use directly with `lightly_train.train_instance_segmentation`:

```python
import lightly_train

lightly_train.train_instance_segmentation(
    out="out/my_experiment",
    model="dinov2/vitl14-eomt",
    data="instance_segmentation/config.yaml",
)
```

---

Part of [coco128_yolo](https://github.com/lightly-ai/coco128_yolo), the example datasets
for [LightlyTrain](https://github.com/lightly-ai/lightly-train) ·
[Docs](https://docs.lightly.ai/train/stable/) · [Discord](https://discord.gg/xvNJW94)
