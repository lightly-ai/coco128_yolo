First 128 train and val images from the COCO dataset in YOLO object detection format.

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/object_detection.zip && unzip -q object_detection.zip
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
