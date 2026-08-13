"""The upstream coco128_panoptic repo ships 128 annotation entries per split but only
100 of the matching mask PNGs (always the same tail set - looks like an incomplete
upload). Trim the migrated panoptic_segmentation/ JSON + images to only the entries
that actually have a mask, so downstream consumers (panoptic/instance/semantic
segmentation builders) don't hit a missing-file error.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent / "panoptic_segmentation"


def trim_split(split: str) -> None:
    ann_path = REPO / "annotations" / f"panoptic_{split}.json"
    mask_dir = REPO / "annotations" / f"panoptic_{split}"
    image_dir = REPO / "images" / split

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

    # Drop the now-unreferenced extra images from images/<split> so the repo doesn't
    # ship dead weight images with no matching panoptic annotation.
    kept_filenames = {img["file_name"] for img in kept_images}
    removed = 0
    for img_path in list(image_dir.glob("*.jpg")):
        if img_path.name not in kept_filenames:
            img_path.unlink()
            removed += 1
    print(f"{split}: removed {removed} unreferenced images from images/{split}")


for split in ["train2017", "val2017"]:
    trim_split(split)
