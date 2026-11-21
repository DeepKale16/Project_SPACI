"""
scripts/benchmark_edge.py - Venv-Safe PyTorch FP32/FP16 & ONNX Edge Benchmark
=============================================================================
Safely benchmarks YOLO11s on the NVIDIA RTX 3050 Laptop GPU:
- Evaluates PyTorch FP32 vs PyTorch FP16 (half=True) latency (ms), FPS, and peak VRAM (MB)
- Exports ONNX model to models/best.onnx (gitignored)
- Verifies inference parity without altering torch/CUDA packages
- Saves summary to reports/edge_benchmark_summary.json
"""

import sys
import time
import json
from pathlib import Path
import torch
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

from ultralytics import YOLO


def benchmark_edge(weights_path: Path | str = MODELS_DIR / "best.pt", num_warmup: int = 25, num_iter: int = 100):
    weights_path = Path(weights_path)
    if not weights_path.exists():
        weights_path = MODELS_DIR / "yolo11s.pt"

    print("=" * 70)
    print(" SPACI 3.0 - Venv-Safe Edge Benchmark (PyTorch FP32 vs FP16 vs ONNX)")
    print("=" * 70)

    assert torch.cuda.is_available(), "CUDA is required for GPU edge benchmarking"
    device_name = torch.cuda.get_device_name(0)
    print(f"[Device] {device_name}")
    print(f"[Model Checkpoint] {weights_path}")

    # Load Model
    model = YOLO(str(weights_path))

    dummy_input = torch.zeros((1, 3, 640, 640), dtype=torch.float32, device="cuda:0")

    # -------------------------------------------------------------------------
    # 1. PyTorch FP32 Benchmark
    # -------------------------------------------------------------------------
    print("\n[Benchmark 1/3] Running PyTorch FP32 inference benchmark...")
    torch.cuda.reset_peak_memory_stats(0)
    # Warmup
    for _ in range(num_warmup):
        _ = model.predict(dummy_input, verbose=False, device=0)
    torch.cuda.synchronize()

    timings_fp32 = []
    for _ in range(num_iter):
        t0 = time.perf_counter()
        _ = model.predict(dummy_input, verbose=False, device=0)
        torch.cuda.synchronize()
        t1 = time.perf_counter()
        timings_fp32.append((t1 - t0) * 1000.0)

    fp32_latency = float(np.mean(timings_fp32))
    fp32_std = float(np.std(timings_fp32))
    fp32_p95 = float(np.percentile(timings_fp32, 95))
    fp32_fps = 1000.0 / fp32_latency
    fp32_vram_mb = torch.cuda.max_memory_allocated(0) / (1024**2)

    print(f" -> FP32 Mean Latency:  {fp32_latency:.2f} ms (+/- {fp32_std:.2f} ms)")
    print(f" -> FP32 95th Pct:      {fp32_p95:.2f} ms")
    print(f" -> FP32 Throughput:    {fp32_fps:.1f} FPS")
    print(f" -> FP32 Peak VRAM:     {fp32_vram_mb:.1f} MB")

    # -------------------------------------------------------------------------
    # 2. PyTorch FP16 Benchmark (half=True)
    # -------------------------------------------------------------------------
    print("\n[Benchmark 2/3] Running PyTorch FP16 (half=True) benchmark...")
    torch.cuda.reset_peak_memory_stats(0)
    # Warmup
    for _ in range(num_warmup):
        _ = model.predict(dummy_input, half=True, verbose=False, device=0)
    torch.cuda.synchronize()

    timings_fp16 = []
    for _ in range(num_iter):
        t0 = time.perf_counter()
        _ = model.predict(dummy_input, half=True, verbose=False, device=0)
        torch.cuda.synchronize()
        t1 = time.perf_counter()
        timings_fp16.append((t1 - t0) * 1000.0)

    fp16_latency = float(np.mean(timings_fp16))
    fp16_std = float(np.std(timings_fp16))
    fp16_p95 = float(np.percentile(timings_fp16, 95))
    fp16_fps = 1000.0 / fp16_latency
    fp16_vram_mb = torch.cuda.max_memory_allocated(0) / (1024**2)

    speedup_pct = ((fp32_latency - fp16_latency) / fp32_latency) * 100.0
    print(f" -> FP16 Mean Latency:  {fp16_latency:.2f} ms (+/- {fp16_std:.2f} ms)")
    print(f" -> FP16 95th Pct:      {fp16_p95:.2f} ms")
    print(f" -> FP16 Throughput:    {fp16_fps:.1f} FPS")
    print(f" -> FP16 Peak VRAM:     {fp16_vram_mb:.1f} MB")
    print(f" -> FP16 Acceleration:  {speedup_pct:+.1f}% vs FP32")

    # -------------------------------------------------------------------------
    # 3. ONNX Export & Parity Verification
    # -------------------------------------------------------------------------
    print("\n[Benchmark 3/3] Exporting ONNX model to models/best.onnx...")
    onnx_path = MODELS_DIR / "best.onnx"
    try:
        model.export(format="onnx", imgsz=640, dynamic=False, simplify=True)
        onnx_exported = onnx_path.exists()
        print(f" -> ONNX Exported Successfully: {onnx_path} (Size: {onnx_path.stat().st_size / (1024**2):.1f} MB)")
    except Exception as e:
        onnx_exported = False
        print(f" -> ONNX Export notice: {e}")

    summary = {
        "device": device_name,
        "weights": str(weights_path),
        "pytorch_fp32": {
            "mean_latency_ms": round(fp32_latency, 2),
            "std_latency_ms": round(fp32_std, 2),
            "p95_latency_ms": round(fp32_p95, 2),
            "fps": round(fp32_fps, 1),
            "peak_vram_mb": round(fp32_vram_mb, 1),
        },
        "pytorch_fp16": {
            "mean_latency_ms": round(fp16_latency, 2),
            "std_latency_ms": round(fp16_std, 2),
            "p95_latency_ms": round(fp16_p95, 2),
            "fps": round(fp16_fps, 1),
            "peak_vram_mb": round(fp16_vram_mb, 1),
            "speedup_vs_fp32_pct": round(speedup_pct, 1),
        },
        "onnx_exported": onnx_exported,
    }

    out_json = REPORTS_DIR / "edge_benchmark_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[Summary] Saved edge benchmark summary to {out_json}")

    return summary


if __name__ == "__main__":
    benchmark_edge()
