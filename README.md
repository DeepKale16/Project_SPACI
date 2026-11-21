# SPACI 2.0: Space Debris Detection & Operational Risk Assessment System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.6](https://img.shields.io/badge/PyTorch-2.6-EE4C2C.svg)](https://pytorch.org/)
[![CUDA Accelerated](https://img.shields.io/badge/Hardware-NVIDIA%20RTX%203050-76B900.svg)](https://www.nvidia.com/)
[![Ultralytics YOLO](https://img.shields.io/badge/Model-YOLO11-00FFFF.svg)](https://docs.ultralytics.com/)
[![FastAPI HUD](https://img.shields.io/badge/Dashboard-FastAPI%20%2B%20HTML5%20HUD-009688.svg)](https://fastapi.tiangolo.com/)
[![Standard Compliance](https://img.shields.io/badge/Standard-NASA--STD--8719.14C-0B3D91.svg)](https://standards.nasa.gov/)

SPACI 2.0 is an autonomous, end-to-end computer vision and aerospace telemetry framework designed for real-time space debris detection, multi-object kinematics tracking, and operational hazard assessment in Low Earth Orbit (LEO) and Geostationary Earth Orbit (GEO).

---

## Key Features

- **Deep Transfer Learning Detection:** Multi-class detection across 11 space object and satellite categories at 640x640 resolution.
- **NASA/ESA Calibrated Risk Engine:** Implements the NASA Standard Breakup Model ($40\text{ J/g}$ catastrophic threshold), optical linear proxies ($L_c \propto \sqrt{r_A}$), and ESA MASTER-8 crowding factors.
- **Dynamic BoT-SORT Tumble Estimation:** Computes aspect ratio variance ($\sigma^2_{\text{AR}}$) to track 3D rotational tumbling and dynamic collision swept envelopes.
- **Four Operational States:**
  1. `Hazardous` (Risk > 0.60 ?" Collision Avoidance Maneuver trigger)
  2. `Reusable / Salvageable` (Risk &le; 0.40 ?" On-Orbit Servicing & ADR candidate)
  3. `Useful / Active` (Active satellites ?" Preservation priority)
  4. `Inert Fragment` (Uncontrolled passive fragments)
- **Deployment-Ready Web Dashboard:** Dark glassmorphic interface with 1-click test gallery, video scrubber, interactive Plotly charts, and telemetry export (CSV/JSON).
- **Comprehensive EDA & Audit Pipeline:** Verified dataset of 2,467 images with zero missing annotations and zero data leakage across train/val/test splits.

---

## System Architecture

```
Project_SPACI/
??? Dataset/                       # Clean 11-class dataset
?   ??? data.yaml                  # Verified dataset config
?   ??? train/ (2,105 images)
?   ??? valid/ (239 images)
?   ??? test/ (123 images)
??? src/                           # Core modular Python package
?   ??? config.py                  # Central hyperparameters & paths
?   ??? eda.py                     # Statistical data audit & visualization
?   ??? taxonomy.py                # Operational taxonomy & category mappings
?   ??? risk_engine.py             # NASA/ESA multi-factor hazard scoring
?   ??? tracker.py                 # BoT-SORT kinematics & tumble rate tracker
?   ??? detector.py                # Unified YOLO inference engine
?   ??? train.py                   # GPU-accelerated training pipeline
?   ??? evaluate.py                # Test set evaluation & metrics export
??? app/                           # Production Web Application
?   ??? app.py                     # Streamlit dashboard
?   ??? components/
?   ?   ??? ui_components.py       # Reusable UI widgets & Plotly charts
?   ??? assets/
?       ??? style.css              # Luxury dark glassmorphism styling
??? models/                        # Checkpoints & weights
?   ??? best.pt                    # Trained high-accuracy model
?   ??? yolo11n.pt                 # Pretrained base weights
??? reports/                       # Generated EDA plots & metrics
?   ??? eda_class_distribution.png
?   ??? eda_bbox_dimensions.png
?   ??? eda_spatial_heatmap.png
?   ??? evaluation_test_report.json
??? scripts/                       # Command-line utility tools
?   ??? run_eda.py                 # Launch EDA pipeline
?   ??? run_training.py            # Launch GPU training
?   ??? run_inference.py           # Run CLI inference on images/videos
??? tests/                         # Automated unit test suite
    ??? test_dataset.py
    ??? test_taxonomy.py
    ??? test_risk_engine.py
    ??? test_detector.py
```

---

## Quickstart Guide

### 1. Installation

Ensure Python 3.10+ is installed with CUDA support:

```bash
pip install -r requirements.txt
```

### 2. Launch Web Application

Run the mission control HUD dashboard:

```bash
python server.py --port 8080
```
or
```bash
python app.py
```

Then open your browser at `http://localhost:8080`.

### 3. Run Command-Line Inference

```bash
# Test on a single image
python scripts/run_inference.py --source Dataset/test/images/img010033_jpg.rf.32ef88458356049c1726406ec802d3ba.jpg

# Batch test on directory
python scripts/run_inference.py --source Dataset/test/images/ --output reports/inference_batch/
```

### 4. Run Dataset Audit & EDA

```bash
python scripts/run_eda.py
```

### 5. Run Automated Unit Tests

```bash
python -m unittest discover tests
```

---

## Aerospace Object Taxonomy (11 Visual Classes)

| Class Key | Display Name | Operational Category | Primary State |
|---|---|---|---|
| `cheops` | CHEOPS (ESA Exoplanet) | Scientific Payload | Useful / Active |
| `debris` | Space Debris Fragment | Trackable Debris | Hazardous / Inert |
| `double_start` | Double Start / Ambiguous | Ambiguous Object | Inert Fragment |
| `earth_observation_sat_1` | Earth Observation Sat-1 | Defunct Spacecraft Bus | Reusable / Salvageable |
| `lisa_pathfinder` | LISA Pathfinder (ESA) | Scientific Payload | Useful / Active |
| `proba_2` | PROBA-2 (Sun Observer) | Scientific Payload | Useful / Active |
| `proba_3_csc` | PROBA-3 Coronagraph (CSC) | Scientific Payload | Useful / Active |
| `proba_3_ocs` | PROBA-3 Occulter (OCS) | Scientific Payload | Useful / Active |
| `smart_1` | SMART-1 (Lunar Demonstrator) | Defunct Spacecraft Bus | Reusable / Salvageable |
| `soho` | SOHO (Solar Observatory) | Scientific Payload | Useful / Active |
| `xmm_newton` | XMM-Newton (X-Ray Telescope) | Scientific Payload | Useful / Active |

---

## Scientific Grounding

See [`RESEARCH_FOUNDATION.md`](file:///E:/Project_SPACI/RESEARCH_FOUNDATION.md) for full orbital mechanics equations, hypervelocity collision kinetics, and sensor proxy calibrations under NASA-STD-8719.14C and ESA MASTER-8.
