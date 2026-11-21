"""
evaluate.py - Test Set Benchmark & Metric Assessment for SPACI 2.0
==================================================================
Runs validation and held-out test split evaluation. Computes detailed
per-class precision, recall, mAP50, mAP50-95, and saves evaluation_report.json.
"""

import sys
import json
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO

from src.config import (
    DATA_YAML_PATH,
    MODELS_DIR,
    REPORTS_DIR,
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
)


def evaluate_model(
    weights_path: Path | str = MODELS_DIR / "best.pt",
    split: str = "test",
    augment: bool = False,
    imgsz: int = 640,
) -> dict:
    """
    Evaluates the YOLO model on the specified split ('test' or 'val').
    Supports test-time augmentation (TTA) and multi-resolution benchmarks.
    """
    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError(f"Model weights not found at {weights_path}")

    print("=" * 70)
    print(f" SPACI 2.0 - Model Evaluation on '{split}' Split (TTA: {augment}, imgsz: {imgsz})")
    print("=" * 70)
    print(f"[Model] {weights_path}")
    print(f"[Dataset] {DATA_YAML_PATH}")

    model = YOLO(str(weights_path))
    metrics = model.val(
        data=str(DATA_YAML_PATH),
        split=split,
        imgsz=imgsz,
        batch=16,
        device="0",
        plots=True,
        save_json=False,
        augment=augment,
    )

    box = metrics.box
    overall_p = float(box.mp)
    overall_r = float(box.mr)
    overall_map50 = float(box.map50)
    overall_map75 = float(box.map75)
    overall_map = float(box.map)

    print("\n" + "=" * 70)
    print(" OVERALL EVALUATION METRICS")
    print("=" * 70)
    print(f" Precision (mP):     {overall_p * 100:.2f}%")
    print(f" Recall (mR):        {overall_r * 100:.2f}%")
    print(f" mAP@50:             {overall_map50 * 100:.2f}%")
    print(f" mAP@75:             {overall_map75 * 100:.2f}%")
    print(f" mAP@50-95:          {overall_map * 100:.2f}%")
    print("=" * 70)

    # Per-class metrics
    per_class = {}
    print("\nPER-CLASS METRICS:")
    print(f"{'Class':<26} {'Precision':<12} {'Recall':<12} {'mAP50':<12} {'mAP50-95':<12}")
    print("-" * 74)

    for i, cname in enumerate(CLASS_NAMES):
        cp = float(box.p[i]) if i < len(box.p) else 0.0
        cr = float(box.r[i]) if i < len(box.r) else 0.0
        cmap50 = float(box.ap50[i]) if i < len(box.ap50) else 0.0
        cmap = float(box.ap[i]) if i < len(box.ap) else 0.0

        per_class[cname] = {
            "display_name": CLASS_DISPLAY_NAMES.get(cname, cname),
            "precision": cp,
            "recall": cr,
            "map50": cmap50,
            "map50_95": cmap,
        }
        print(f"{cname:<26} {cp * 100:>10.1f}% {cr * 100:>10.1f}% {cmap50 * 100:>10.1f}% {cmap * 100:>10.1f}%")

    report = {
        "split": split,
        "weights": str(weights_path),
        "augment": augment,
        "imgsz": imgsz,
        "overall": {
            "precision": overall_p,
            "recall": overall_r,
            "map50": overall_map50,
            "map75": overall_map75,
            "map50_95": overall_map,
        },
        "per_class": per_class,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "_tta" if augment else ""
    report_file = REPORTS_DIR / f"evaluation_{split}{suffix}_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[Report Saved] -> {report_file}")
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SPACI 2.0 Evaluation Benchmark")
    parser.add_argument("--weights", type=str, default=str(MODELS_DIR / "best.pt"), help="Path to weights file")
    parser.add_argument("--split", type=str, default="test", help="Split: test or valid")
    parser.add_argument("--augment", action="store_true", help="Enable Test-Time Augmentation (TTA)")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image resolution")
    args = parser.parse_args()

    evaluate_model(weights_path=args.weights, split=args.split, augment=args.augment, imgsz=args.imgsz)
