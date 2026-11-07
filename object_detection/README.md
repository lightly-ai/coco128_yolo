<div align="center">
  <a href="https://www.lightly.ai/lightly-train">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_dark.svg">
      <img src="https://raw.githubusercontent.com/lightly-ai/lightly-train/main/docs/source/_static/lightly_train_light.svg" alt="LightlyTrain" width="280" style="max-width: 100%; height: auto;">
    </picture>
  </a>
</div>

# Object detection

First 128 train and val images from the COCO dataset, in YOLO object detection format.
The class ids are the contiguous 0-79 YOLO numbering.

## Download

The archive holds the images, labels and `config.yaml`:

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.3/object_detection.zip && unzip -q object_detection.zip
```

## Train

Pass the config straight to `lightly_train.train_object_detection`:

```python
import lightly_train

lightly_train.train_object_detection(
    out="out/my_experiment",
    model="ltdetrv2-s-coco",
    data="object_detection/config.yaml",
)
```

## Pretrain and distill

Pretraining and distillation need no labels. Point `data` at the image folder:

```python
lightly_train.pretrain(
    out="out/my_pretrain",
    model="dinov3/vitt16",
    method="distillation",
    data="object_detection/images/train2017",
)
```

---

Part of [coco128_yolo](https://github.com/lightly-ai/coco128_yolo), the example datasets
for [LightlyTrain](https://github.com/lightly-ai/lightly-train) ·
[Docs](https://docs.lightly.ai/train/stable/) · [Discord](https://discord.gg/xvNJW94)
