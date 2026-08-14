"""Derive YOLO-seg instance segmentation polygon labels from the COCO panoptic
annotations already present in panoptic_segmentation/. Only "thing" categories are
converted (COCO panoptic "stuff" categories have no instances).
"""

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
PANOPTIC = REPO / "panoptic_segmentation"
OUT = REPO / "instance_segmentation"

MIN_CONTOUR_POINTS = 3


def panoptic_id_map(png_path: Path) -> np.ndarray:
    arr = np.array(Image.open(png_path).convert("RGB"), dtype=np.uint32)
    return arr[..., 0] + arr[..., 1] * 256 + arr[..., 2] * 256 * 256


def mask_to_yolo_line(mask: np.ndarray) -> list[float] | None:
    """Return one flat YOLO-seg coordinate line for a (possibly multi-part) mask.

    Disconnected parts of the same instance are concatenated using the YOLO
    convention of closing each sub-polygon with its own repeated first point
    before starting the next one (see yolo_helpers.split_yolo_polygon).
    """
    h, w = mask.shape
    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    flat: list[float] = []
    for contour in contours:
        if len(contour) < MIN_CONTOUR_POINTS:
            continue
        # Simplify to keep label files small, while staying accurate.
        epsilon = 0.002 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) < MIN_CONTOUR_POINTS:
            approx = contour
        pts = approx.reshape(-1, 2).astype(np.float64)
        pts[:, 0] /= w
        pts[:, 1] /= h
        pts_list = pts.tolist()
        flat.extend(coord for pt in pts_list for coord in pt)
        # Close this sub-polygon by repeating its first point before the next.
        flat.extend(pts_list[0])
    return flat if flat else None


def convert_split(split: str, category_id_to_name: dict[int, str]) -> None:
    ann_file = PANOPTIC / "annotations" / f"panoptic_{split}.json"
    mask_dir = PANOPTIC / "annotations" / f"panoptic_{split}"
    label_dir = OUT / "labels" / split
    label_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(ann_file.read_text())
    thing_ids = set(category_id_to_name.keys())

    n_images = 0
    n_instances = 0
    for ann in data["annotations"]:
        file_stem = Path(ann["file_name"]).stem
        mask_path = mask_dir / ann["file_name"]
        id_map = panoptic_id_map(mask_path)

        lines = []
        for seg in ann["segments_info"]:
            category_id = seg["category_id"]
            if category_id not in thing_ids:
                continue
            binary_mask = id_map == seg["id"]
            if not binary_mask.any():
                continue
            line = mask_to_yolo_line(binary_mask)
            if line is None:
                continue
            coords = " ".join(f"{v:.6f}" for v in line)
            lines.append(f"{category_id} {coords}")
            n_instances += 1

        (label_dir / f"{file_stem}.txt").write_text(
            "\n".join(lines) + ("\n" if lines else "")
        )
        n_images += 1

    print(f"{split}: {n_images} images, {n_instances} instances")


def main() -> None:
    categories = json.loads(
        (PANOPTIC / "annotations" / "panoptic_train2017.json").read_text()
    )["categories"]
    thing_categories = {c["id"]: c["name"] for c in categories if c["isthing"] == 1}
    print(f"{len(thing_categories)} thing categories")

    for split in ["train2017", "val2017"]:
        convert_split(split, thing_categories)

    names_yaml = "\n".join(
        f"  {cid}: {name}" for cid, name in sorted(thing_categories.items())
    )
    config = f"""# COCO128 YOLO-seg instance segmentation config file
# Class ids match the COCO panoptic "thing" category ids (not the contiguous
# 0-79 YOLO detection numbering used in object_detection/config.yaml).
format: yolo
path: .
train: images/train2017
val: images/val2017
skip_if_label_file_missing: true

names:
{names_yaml}
"""
    (OUT / "config.yaml").write_text(config)
    print("Wrote", OUT / "config.yaml")


if __name__ == "__main__":
    main()
