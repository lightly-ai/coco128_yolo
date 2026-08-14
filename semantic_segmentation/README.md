100 train and 100 val images from the COCO dataset with single-channel semantic
segmentation masks (thing + stuff classes).

Derived from `panoptic_segmentation/`'s COCO panoptic annotations by mapping every
pixel's panoptic segment to its category id — see
`../scripts/build_semantic_segmentation.py`. Class id `0` means "unlabeled" (no
panoptic segment for that pixel).

Download with

```
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/images.zip && unzip -q images.zip
wget https://github.com/lightly-ai/coco128_yolo/releases/download/v0.0.2/semantic_segmentation.zip && unzip -q semantic_segmentation.zip
```

Use directly with `lightly_train.train_semantic_segmentation`:

```python
import lightly_train

lightly_train.train_semantic_segmentation(
    out="out/my_experiment",
    model="dinov2/vitl14-eomt",
    data="semantic_segmentation/config.yaml",
)
```
