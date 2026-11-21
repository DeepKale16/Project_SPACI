"""
run_training.py - CLI Script to Launch GPU Model Training for SPACI 2.0
======================================================================
Usage:
    python scripts/run_training.py --model yolo11s.pt --epochs 100 --batch 16
    python scripts/run_training.py --model yolo11m.pt --epochs 120 --batch 8 --imgsz 640
"""
import sys
import argparse
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TrainingConfig
from src.train import run_training

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SPACI 2.0 High-Accuracy Training Pipeline")
    parser.add_argument("--model", type=str, default="yolo11s.pt", help="Model family: yolo11s.pt, yolo11m.pt, yolo11x.pt")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (reduce to 8 or 4 for larger models)")
    parser.add_argument("--imgsz", type=int, default=640, help="Input resolution (640 or 800)")
    parser.add_argument("--lr", type=float, default=0.001, help="Initial learning rate")
    args = parser.parse_args()

    cfg = TrainingConfig(
        model_family=args.model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        lr0=args.lr,
        name=f"spaci2_{Path(args.model).stem}_e{args.epochs}",
    )

    print(f"[SPACI 2.0] Launching GPU Deep Transfer Learning ({cfg.model_family}, {cfg.epochs} epochs)...")
    run_training(cfg)

