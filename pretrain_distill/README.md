First 128 train images from the COCO dataset without labels, for pretraining /
distillation.

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip
```

This task needs no labels, so the shared image pool is the whole download — there is no
separate `pretrain_distill.zip`.

Use directly with `lightly_train.pretrain`:

```python
import lightly_train

lightly_train.pretrain(
    out="out/my_pretrain_experiment",
    data="images/train2017",
    model="torchvision/resnet50",
    method="distillation",
)
```
