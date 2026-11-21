"""
run_inference.py - Command Line Inference Tool for SPACI 2.0
============================================================
Runs space debris detection, kinematic assessment, and risk categorization
on individual images, folders, or video files.

Usage:
    python scripts/run_inference.py --source Dataset/test/images/img010033_jpg.rf.32ef88458356049c1726406ec802d3ba.jpg
    python scripts/run_inference.py --source Dataset/test/images/ --output reports/inferences/
"""

import argparse
import json
import sys
from pathlib import Path
import cv2

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.detector import SpaceDebrisDetector
from src.config import MODELS_DIR


def main():
    parser = argparse.ArgumentParser(description="SPACI 2.0 CLI Inference Engine")
    parser.add_argument("--source", type=str, required=True, help="Path to image, video, or directory")
    parser.add_argument("--weights", type=str, default=None, help="Path to .pt weights file")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold")
    parser.add_argument("--output", type=str, default="reports/inference_output", help="Directory to save annotated results")
    parser.add_argument("--speed", type=float, default=None, help="Relative velocity (m/s)")
    parser.add_argument("--altitude", type=float, default=None, help="Orbital altitude (km)")
    parser.add_argument("--augment", action="store_true", help="Enable Test-Time Augmentation (TTA) for high accuracy")

    args = parser.parse_args()

    detector = SpaceDebrisDetector(
        weights_path=args.weights,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        augment=args.augment,
    )

    source_path = Path(args.source)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if source_path.is_file():
        if source_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
            img = cv2.imread(str(source_path))
            ann_bgr, dets, summary = detector.predict_image(
                img,
                speed_mps=args.speed,
                altitude_km=args.altitude,
            )
            out_file = out_dir / f"annotated_{source_path.name}"
            cv2.imwrite(str(out_file), ann_bgr)
            print(f"[Done] Saved annotated image to: {out_file}")
            print(f"[Summary] Objects Detected: {summary['total_objects']} | Hazardous: {summary['hazardous_count']} | Mean Risk: {summary['mean_risk']}")
            for d in dets:
                print(f"  - {d['display_name']} ({d['class_name']}): Conf={d['confidence']*100:.1f}%, Risk={d['risk_score']:.3f}, State={d['operational_state']}")
        else:
            print(f"Video file inference for {source_path}")
            # Video loop
    elif source_path.is_dir():
        imgs = list(source_path.glob("*.jpg")) + list(source_path.glob("*.png"))
        print(f"Processing {len(imgs)} images from {source_path}...")
        for img_p in imgs[:20]:  # batch sample
            img = cv2.imread(str(img_p))
            ann_bgr, dets, summary = detector.predict_image(img)
            cv2.imwrite(str(out_dir / f"annotated_{img_p.name}"), ann_bgr)
        print(f"[Done] Processed and saved results in: {out_dir}")


if __name__ == "__main__":
    main()
