100 train and 100 val images from the COCO dataset with panoptic segmentation
annotations (thing + stuff classes).

The upstream `coco128_panoptic` repo this was migrated from shipped 128 annotation
entries per split but only 100 matching mask PNGs (an incomplete upload). Both splits
were trimmed down to the 100 images that actually have a mask — see
`../scripts/trim_panoptic.py`.

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/panoptic_segmentation.zip && unzip -q panoptic_segmentation.zip
```

Use directly with `lightly_train.train_panoptic_segmentation`:

```python
import lightly_train

lightly_train.train_panoptic_segmentation(
    out="out/my_experiment",
    model="dinov3/vitl16-eomt-panoptic-coco",
    data="panoptic_segmentation/config.yaml",
)
```
