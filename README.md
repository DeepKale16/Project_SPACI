# SPACI 3.0: Space-Debris Detection, Tracking & Capture Demonstrator

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PyTorch 2.6 CUDA](https://img.shields.io/badge/PyTorch-2.6%20%2B%20CUDA-EE4C2C.svg)](https://pytorch.org/)
[![Hardware Accelerated](https://img.shields.io/badge/GPU-RTX%203050%20(6GB)-76B900.svg)](https://www.nvidia.com/)
[![Ultralytics YOLO11](https://img.shields.io/badge/Model-YOLO11s%20%2B%20BoT--SORT-00FFFF.svg)](https://docs.ultralytics.com/)
[![Mission Control HUD](https://img.shields.io/badge/HUD-FastAPI%20%2B%20WebSocket%20%2B%20Canvas-009688.svg)](https://fastapi.tiangolo.com/)
[![Standard Compliance](https://img.shields.io/badge/Standard-NASA--STD--8719.14C%20%2F%20ESA-0B3D91.svg)](https://standards.nasa.gov/)

**SPACI 3.0** is a mathematically exact, thread-safe, sponsor-grade aerospace software platform delivering real-time space debris detection, multi-object tracking, and closed-loop terrestrial tethered-net capture Guidance, Navigation & Control (GNC) on a local GPU workstation without physical hardware dependencies.

---

## What's New in SPACI 3.0

1. **Dual-Mode Mission Engine:**
   - **Mode A: Orbital Surveillance:** Full SPACI 2.0 NASA-STD-8719.14C and ESA MASTER-8 orbital risk engine with 4 operational states (`Useful/Active`, `Reusable/Salvageable`, `Hazardous`, `Inert Fragment`).
   - **Mode B: Ground Demonstrator:** Active terrestrial tethered-net capture GNC with pure-NumPy 3D Kalman filtering, deterministic target lock policy, and closed-form quartic ballistic trajectory solver.

2. **Frame-Locked Atomic WebSocket Live Engine (`/ws/live`):**
   - Sustained **28–30 FPS** with **16–22 ms total latency** (< 35 ms envelope) on NVIDIA RTX 3050.
   - Drop-oldest latest-frame queue (`maxsize=1`) and producer-consumer architecture eliminating stale frame backlog.
   - 3 selectable input sources: **Deterministic 3D Physics Testbench**, **Video Stream Loop**, and **Physical Webcam (with Lab Frame Recorder)**.

3. **Non-Circular Ray-Cast LiDAR Fusion & MAD/IQR Filtering:**
   - Multi-object LiDAR ray simulation intersecting ground-truth 3D object silhouettes with 8.0 m wall clutter.
   - Median Absolute Deviation (MAD) & IQR outlier filter rejecting spurious environment returns.
   - Metric diameter estimation ($D_{\text{est}} = w \cdot Z / f_x$) decoupled from monocular depth proxies.

4. **Closed-Form 3D Ballistic GNC & 6-Condition Safety Gate:**
   - Exact quartic polynomial ballistic intercept solver with terrestrial gravity compensation ($g = 9.81\text{ m/s}^2$) via `np.roots`.
   - 6-state pure-NumPy 3D Kalman Filter ($\mathbf{x} = [X, Y, Z, \dot{X}, \dot{Y}, \dot{Z}]^T$) with velocity-jump gating ($> 20\text{ m/s}$).
   - Deterministic multi-target lock policy enforcing safety rules (strict prohibition against targeting active spacecraft payloads).
   - 6-Condition Tethered Net Go/No-Go safety gate: Target Lock, Kinematic Stability ($< 0.5\text{ m/s}$ residual), Ballistic Solvability, Deployment Corridor ($1.5\text{–}6.5\text{ m}$), Gimbal Limits ($\pm 75^\circ$ Pan, $-15^\circ\text{ to }+45^\circ$ Tilt), and Net Aperture ($R_{\text{open}}(d) \ge 1.25 \cdot R_{\text{debris}}$).

5. **Tactical Trajectory Radar & Automated Monte Carlo Suite:**
   - Dual real-time HTML5 2D canvas radar displays: **Top-Down (X-Z)** and **Side-Elevation (Y-Z)** with parabolic net flight arc and launcher FOV cone.
   - Thread-safe SQLite/CSV/JSON trial logging (`data/spaci_trials.db`) recording the 3 core KPIs: **Detection Accuracy**, **Deployment Distance**, and **Capture Success Rate**.
   - Automated 140-trial Monte Carlo parameter sweep generating operating envelope heatmaps.

6. **Artifact-Free Multi-Object Pipeline & Zero-Leakage Hash Audit:**
   - Background-aware 20% padded ROI GrabCut / luminance-threshold cutout pipeline with 3px Gaussian alpha feathering.
   - Source-hash MD5 zero-leakage manifest assertion (`Dataset_multi/composite_manifest.json`) verifying $train \cap val = \emptyset$ and $train \cap test = \emptyset$.
   - A/B model promotion gate verifying recall on small `debris` fragments and multi-object stress test sets.

---

## Edge Inference Benchmark (NVIDIA GeForce RTX 3050 Laptop GPU 6GB)

| Precision Format | Mean Latency | 95th Percentile | Throughput | Peak VRAM | Speedup vs FP32 |
|---|---|---|---|---|---|
| **PyTorch FP32** | 11.22 ms | 11.81 ms | 89.1 FPS | 110.4 MB | Baseline |
| **PyTorch FP16** | **9.46 ms** | **12.98 ms** | **105.7 FPS** | **112.2 MB** | **+15.7%** |

*Validated via `scripts/benchmark_edge.py`.*

---

## Single-Source-of-Truth Test Evaluation Metrics (123 Held-Out Test Images)

| Class Key | Display Name | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|---|---|
| `cheops` | CHEOPS (ESA Exoplanet) | 100.0% | 100.0% | 99.5% | 65.4% |
| `debris` | Space Debris Fragment | 100.0% | 72.7% | 72.5% | 40.4% |
| `double_start` | Double Start / Ambiguous | 100.0% | 100.0% | 99.5% | 60.5% |
| `earth_observation_sat_1` | Earth Observation Sat-1 | 77.8% | 63.6% | 52.1% | 27.4% |
| `lisa_pathfinder` | LISA Pathfinder (ESA) | 100.0% | 100.0% | 99.5% | 48.3% |
| `proba_2` | PROBA-2 (Sun Observer) | 66.9% | 80.0% | 78.4% | 39.2% |
| `proba_3_csc` | PROBA-3 Coronagraph (CSC) | 100.0% | 100.0% | 99.5% | 60.1% |
| `proba_3_ocs` | PROBA-3 Occulter (OCS) | 90.9% | 100.0% | 99.5% | 57.0% |
| `smart_1` | SMART-1 (Lunar Demonstrator) | 57.9% | 72.7% | 58.1% | 22.1% |
| `soho` | SOHO (Solar Observatory) | 90.9% | 90.9% | 89.7% | 45.2% |
| `xmm_newton` | XMM-Newton (X-Ray Telescope) | 76.9% | 83.3% | 78.8% | 30.0% |
| **OVERALL** | **All 11 Classes Combined** | **87.39%** | **87.58%** | **84.28%** | **45.06%** |

*Generated from single checkpoint `models/best.pt` via `scripts/generate_verified_report_assets.py`.*

---

## Repository Structure

```
Project_SPACI/
├── configs/
│   └── spaci_botsort.yaml              # Ultra-low latency BoT-SORT configuration
├── core/
│   ├── sensor_fusion.py                # 2D/3D projection, MAD/IQR LiDAR filter, metric diameter
│   ├── tracking_control.py             # 3D Kalman Filter, Target Lock, Quartic Solver, Safety Gate
│   ├── stream_manager.py               # Unified atomic WebSocket producer-consumer thread
│   └── kpi_logger.py                   # Thread-safe SQLite & CSV/JSON trial logger
├── sensors/
│   └── lidar_adapter.py                # DepthProvider ABC, SimulatedLidarProvider, MonocularProxy
├── simulation/
│   └── physics_testbench.py            # Deterministic 3D multi-object space mockups simulator
├── scripts/
│   ├── build_multi_object_dataset.py   # Alpha-feathered GrabCut/luminance multi-object pipeline
│   ├── train_phase3.py                 # Phase 3 training with safe VRAM defaults & A/B gate
│   ├── run_monte_carlo_eval.py         # 140-trial parameter sweep & envelope heatmap generator
│   ├── benchmark_edge.py               # Edge latency & VRAM benchmark (FP32 vs FP16 vs ONNX)
│   └── generate_verified_report_assets.py # Single-source-of-truth metrics & confusion matrix
├── reports/
│   ├── capture_envelope_heatmap.png    # Monte Carlo capture operating envelope heatmap
│   ├── composite_sanity_grid.jpg       # 4x4 visual validation of composited multi-object cutouts
│   ├── confusion_matrix_verified.png   # Watermarked confusion matrix evaluated on test split
│   ├── metrics_summary.json            # Overall and per-class test metrics
│   ├── per_class_metrics.csv           # Synchronized metrics table
│   └── edge_benchmark_summary.json     # PyTorch FP32 vs FP16 latency and VRAM summary
├── web/
│   ├── index.html                      # Glassmorphic Mission Control HUD with Tactical Radar
│   ├── css/style.css                   # Dual-mode and radar layout styles
│   └── js/app.js                       # Frame-locked WebSocket client & Canvas 2D radar engine
├── server.py                           # FastAPI application & REST/WebSocket routes
└── tests/                              # Complete 33-test automated test suite
    ├── test_dataset.py
    ├── test_detector.py
    ├── test_gnc_quartic.py
    ├── test_kalman_filter.py
    ├── test_lidar_fusion.py
    ├── test_live_system.py
    ├── test_risk_engine.py
    ├── test_taxonomy.py
    └── test_testbench.py
```

---

## Quickstart

### 1. Launch Mission Control HUD (Port 8080)
```bash
python server.py --port 8080
```
Open your browser at `http://localhost:8080`.

### 2. Run Automated Verification Suite (33 Unit Tests)
```bash
python -m pytest tests
```

### 3. Generate Report Assets from Single Source of Truth
```bash
python scripts/generate_verified_report_assets.py
```

### 4. Run Edge Performance Benchmark
```bash
python scripts/benchmark_edge.py
```

### 5. Run Monte Carlo Operating Envelope Sweep
```bash
python scripts/run_monte_carlo_eval.py --trials 140
```
