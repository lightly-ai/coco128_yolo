First 128 train images from the COCO dataset without labels, for pretraining /
distillation.

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/pretrain_distill.zip && unzip -q pretrain_distill.zip
```

Use directly with `lightly_train.pretrain`:

```python
import lightly_train

lightly_train.pretrain(
    out="out/my_pretrain_experiment",
    data="pretrain_distill/images",
    model="torchvision/resnet50",
    method="distillation",
)
```
