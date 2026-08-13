100 train and 100 val images from the COCO dataset with YOLO-seg polygon instance
segmentation labels ("thing" classes only).

Derived from `panoptic_segmentation/`'s COCO panoptic annotations by converting each
instance's panoptic mask to a polygon — see `../scripts/build_instance_segmentation.py`.
Class ids match the COCO panoptic "thing" category ids.

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.1.0/instance_segmentation.zip && unzip -q instance_segmentation.zip
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
