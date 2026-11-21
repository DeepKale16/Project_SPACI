"""
train.py - GPU-Accelerated YOLO Training Pipeline for Space Debris Detection
=============================================================================
Trains YOLO on the 11-class space debris dataset using RTX 3050 CUDA GPU.
Logs metrics, saves checkpoints, and exports best weights to models/best.pt.
"""

import sys
import shutil
import time
from pathlib import Path
import torch
from ultralytics import YOLO

from src.config import (
    PROJECT_ROOT,
    DATA_YAML_PATH,
    MODELS_DIR,
    REPORTS_DIR,
    TrainingConfig,
)


def run_training(config: TrainingConfig | None = None) -> Path:
    """
    Executes the training process using Ultralytics YOLO with GPU acceleration.
    """
    cfg = config or TrainingConfig()

    print("=" * 70)
    print(" SPACI 2.0 - Space Debris Detection Deep Training Pipeline")
    print("=" * 70)
    print(f"[Device Audit] PyTorch: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"[Device Audit] CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"[Device Audit] Device Name: {torch.cuda.get_device_name(0)}")
        print(f"[Device Audit] VRAM Total: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        device_arg = "0"
    else:
        print("[Device Audit] Running on CPU (Warning: slower)")
        device_arg = "cpu"

    print(f"[Config] Dataset: {cfg.data_yaml}")
    print(f"[Config] Base Model: {cfg.model_family}")
    print(f"[Config] Image Size: {cfg.imgsz}x{cfg.imgsz}")
    print(f"[Config] Epochs: {cfg.epochs}")
    print(f"[Config] Batch Size: {cfg.batch}")
    print(f"[Config] Optimizer: {cfg.optimizer} (lr0={cfg.lr0})")
    print("=" * 70)

    # Base model resolution
    base_model_path = MODELS_DIR / cfg.model_family
    if not base_model_path.exists():
        base_model_path = cfg.model_family  # Ultralytics will auto-download if needed

    model = YOLO(str(base_model_path))

    start_time = time.time()
    results = model.train(
        data=str(cfg.data_yaml),
        epochs=cfg.epochs,
        imgsz=cfg.imgsz,
        batch=cfg.batch,
        device=device_arg,
        workers=cfg.workers,
        optimizer=cfg.optimizer,
        lr0=cfg.lr0,
        lrf=cfg.lrf,
        cos_lr=cfg.cos_lr,
        warmup_epochs=cfg.warmup_epochs,
        weight_decay=cfg.weight_decay,
        patience=cfg.patience,
        save=True,
        project=cfg.project,
        name=cfg.name,
        exist_ok=cfg.exist_ok,
        pretrained=cfg.pretrained,
        seed=cfg.seed,
        plots=True,
        val=True,
        verbose=True,
        # Orbital Physics Augmentations
        degrees=cfg.degrees,
        flipud=cfg.flipud,
        fliplr=cfg.fliplr,
        scale=cfg.scale,
        perspective=cfg.perspective,
        hsv_h=cfg.hsv_h,
        hsv_s=cfg.hsv_s,
        hsv_v=cfg.hsv_v,
        mosaic=cfg.mosaic,
        mixup=cfg.mixup,
        close_mosaic=cfg.close_mosaic,
        # Loss Optimization
        cls=cfg.cls_loss_gain,
        box=cfg.box_loss_gain,
        dfl=cfg.dfl_loss_gain,
        label_smoothing=cfg.label_smoothing,
    )
    elapsed = time.time() - start_time
    print(f"\n[Training Complete] Finished in {elapsed / 60:.2f} minutes.")

    # Locate and copy best weights
    run_dir = Path(cfg.project) / cfg.name
    best_weights = run_dir / "weights" / "best.pt"
    target_weights = MODELS_DIR / "best.pt"

    if best_weights.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, target_weights)
        print(f"[Checkpoint] Best weights saved to: {target_weights}")
    else:
        print(f"[Warning] Best weights not found at {best_weights}")

    # Copy plots to reports/
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for plot_name in [
        "results.png",
        "confusion_matrix.png",
        "confusion_matrix_normalized.png",
        "PR_curve.png",
        "F1_curve.png",
        "labels.jpg",
        "val_batch0_labels.jpg",
        "val_batch0_pred.jpg",
    ]:
        src_plot = run_dir / plot_name
        if src_plot.exists():
            shutil.copy2(src_plot, REPORTS_DIR / plot_name)
            print(f"[Report] Exported {plot_name} -> {REPORTS_DIR}")

    return target_weights


if __name__ == "__main__":
    run_training()
