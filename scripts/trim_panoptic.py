"""The upstream coco128_panoptic repo ships 128 annotation entries per split but only
100 of the matching mask PNGs (always the same tail set - looks like an incomplete
upload). Trim the migrated panoptic_segmentation/ JSON to only the entries that
actually have a mask, so downstream consumers (panoptic/instance/semantic
segmentation builders) don't hit a missing-file error.

This only trims the annotation JSON. Each task folder ships only the images it has
labels for, so the 28-per-split images with no panoptic mask are not part of
panoptic_segmentation/images/ at all.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent / "panoptic_segmentation"


def trim_split(split: str) -> None:
    ann_path = REPO / "annotations" / f"panoptic_{split}.json"
    mask_dir = REPO / "annotations" / f"panoptic_{split}"

    data = json.loads(ann_path.read_text())
    available_masks = {p.name for p in mask_dir.glob("*.png")}

    kept_annotations = [
        a for a in data["annotations"] if a["file_name"] in available_masks
    ]
    kept_image_ids = {a["image_id"] for a in kept_annotations}
    kept_images = [img for img in data["images"] if img["id"] in kept_image_ids]

    dropped = len(data["annotations"]) - len(kept_annotations)
    print(
        f"{split}: {len(data['annotations'])} -> {len(kept_annotations)} "
        f"annotations ({dropped} dropped, no mask file)"
    )

    data["annotations"] = kept_annotations
    data["images"] = kept_images
    ann_path.write_text(json.dumps(data))


for split in ["train2017", "val2017"]:
    trim_split(split)
