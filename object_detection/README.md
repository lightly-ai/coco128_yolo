<div align="center">
  <a href="https://www.lightly.ai/lightly-train">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_dark.svg">
      <img src="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_light.svg" alt="LightlyTrain" width="280" style="max-width: 100%; height: auto;">
    </picture>
  </a>
</div>

# Object detection

First 128 train and val images from the COCO dataset in YOLO object detection format.

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/object_detection.zip && unzip -q object_detection.zip
```

Use directly with `lightly_train.train_object_detection`:

```python
import lightly_train

lightly_train.train_object_detection(
    out="out/my_experiment",
    model="ltdetrv2-s-coco",
    data="object_detection/config.yaml",
)
```

---

Part of [coco128_yolo](https://github.com/lightly-ai/coco128_yolo), the example datasets
for [LightlyTrain](https://github.com/lightly-ai/lightly-train) ·
[Docs](https://docs.lightly.ai/train/stable/) · [Discord](https://discord.gg/xvNJW94)
