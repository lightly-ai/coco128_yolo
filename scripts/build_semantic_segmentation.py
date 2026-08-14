"""Derive single-channel semantic segmentation index masks from the COCO panoptic
annotations already present in panoptic_segmentation/. Every pixel's panoptic segment
id is mapped to its COCO category id (covers both "thing" and "stuff" classes, unlike
YOLO-seg polygon labels which only cover "thing" instances). Pixels with no panoptic
segment (segment id 0 in the COCO panoptic PNG encoding) become class 0 ("unlabeled").
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
PANOPTIC = REPO / "panoptic_segmentation"
OUT = REPO / "semantic_segmentation"

UNLABELED_ID = 0


def panoptic_id_map(png_path: Path) -> np.ndarray:
    arr = np.array(Image.open(png_path).convert("RGB"), dtype=np.uint32)
    return arr[..., 0] + arr[..., 1] * 256 + arr[..., 2] * 256 * 256


def convert_split(split: str) -> set[int]:
    ann_file = PANOPTIC / "annotations" / f"panoptic_{split}.json"
    mask_dir = PANOPTIC / "annotations" / f"panoptic_{split}"
    out_mask_dir = OUT / "masks" / split
    out_mask_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(ann_file.read_text())
    seen_category_ids: set[int] = set()

    for ann in data["annotations"]:
        file_stem = Path(ann["file_name"]).stem
        mask_path = mask_dir / ann["file_name"]
        id_map = panoptic_id_map(mask_path)

        segment_id_to_category = {
            seg["id"]: seg["category_id"] for seg in ann["segments_info"]
        }
        class_mask = np.zeros(id_map.shape, dtype=np.uint8)
        for segment_id, category_id in segment_id_to_category.items():
            class_mask[id_map == segment_id] = category_id
            seen_category_ids.add(category_id)

        Image.fromarray(class_mask).save(out_mask_dir / f"{file_stem}.png")

    print(f"{split}: {len(data['annotations'])} masks written")
    return seen_category_ids


def main() -> None:
    categories = json.loads(
        (PANOPTIC / "annotations" / "panoptic_train2017.json").read_text()
    )["categories"]
    category_id_to_name = {c["id"]: c["name"] for c in categories}

    seen = set()
    for split in ["train2017", "val2017"]:
        seen |= convert_split(split)

    classes = {UNLABELED_ID: "unlabeled"}
    for cid in sorted(seen):
        classes[cid] = category_id_to_name[cid]
    print(f"{len(classes)} classes total (incl. unlabeled)")

    classes_yaml = "\n".join(f"  {cid}: {name}" for cid, name in classes.items())
    config = f"""# COCO128 semantic segmentation config file
# Class ids match the COCO panoptic category ids (both "thing" and "stuff"
# classes), plus 0 = "unlabeled" for pixels with no panoptic segment.
train:
  images: ../images/train2017
  masks: masks/train2017
val:
  images: ../images/val2017
  masks: masks/val2017

classes:
{classes_yaml}
"""
    (OUT / "config.yaml").write_text(config)
    print("Wrote", OUT / "config.yaml")


if __name__ == "__main__":
    main()
