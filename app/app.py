"""
app.py - SPACI 2.0 Space Debris Detection & Operational Risk Assessment System
==============================================================================
Production-grade Streamlit web application featuring luxury dark glassmorphism,
real-time YOLO inference, BoT-SORT kinematics/tumble tracking, NASA/ESA risk
matrix analysis, interactive Plotly visualizations, and telemetry data export.

Run:
    streamlit run app/app.py
"""

from __future__ import annotations

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

import cv2
import numpy as np
import pandas as pd
import streamlit as st
import torch

# Ensure both project root and app directory are in sys.path
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

for p in [str(PROJECT_ROOT), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.config import (
    DATASET_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
    STATE_HAZARDOUS,
    STATE_REUSABLE,
    STATE_ACTIVE,
    STATE_FRAGMENT,
    STATE_COLORS_HEX,
    OPERATIONAL_STATES,
)
from src.taxonomy import get_category_for_class, get_display_name
from src.risk_engine import RiskEngine
from src.detector import SpaceDebrisDetector

try:
    from components.ui_components import (
        SAMPLE_TEST_IMAGES,
        render_hero,
        render_kpi_cards,
        render_state_badge_html,
        create_risk_gauge,
        create_states_donut,
        create_class_bar_chart,
    )
except (ModuleNotFoundError, ImportError):
    from app.components.ui_components import (
        SAMPLE_TEST_IMAGES,
        render_hero,
        render_kpi_cards,
        render_state_badge_html,
        create_risk_gauge,
        create_states_donut,
        create_class_bar_chart,
    )

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS Injection
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="SPACI 2.0 - Space Debris Detection & Risk Assessment",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS
css_file = PROJECT_ROOT / "app" / "assets" / "style.css"
if css_file.exists():
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Cached Model Loader
# -----------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_cached_detector(weights_path: str, conf: float, iou: float) -> SpaceDebrisDetector:
    """Loads and caches the SpaceDebrisDetector instance in memory."""
    detector = SpaceDebrisDetector(
        weights_path=weights_path,
        conf_threshold=conf,
        iou_threshold=iou,
        device="0" if torch.cuda.is_available() else "cpu",
    )
    return detector


def find_available_weights() -> List[str]:
    """Finds all available .pt model weight files in models/ and runs/."""
    candidates = []
    best_target = MODELS_DIR / "best.pt"
    if best_target.exists():
        candidates.append(str(best_target))

    base_target = MODELS_DIR / "yolo11n.pt"
    if base_target.exists():
        candidates.append(str(base_target))

    # Search runs directory
    runs_dir = PROJECT_ROOT / "runs"
    if runs_dir.exists():
        for p in runs_dir.glob("**/*.pt"):
            candidates.append(str(p))

    # Search SPACI legacy folder if exists
    legacy_runs = Path("E:/SPACI/runs")
    if legacy_runs.exists():
        for p in legacy_runs.glob("**/*.pt"):
            candidates.append(str(p))

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    return unique or ["yolo11n.pt"]


# -----------------------------------------------------------------------------
# 3. Sidebar Controls & Mission Telemetry
# -----------------------------------------------------------------------------

def render_sidebar():
    """Renders the dark glassmorphic control sidebar."""
    st.sidebar.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:1.2rem;">
            <div style="font-size:1.8rem;">??</div>
            <div>
                <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#f8fafc;">SPACI 2.0</h3>
                <span style="font-size:0.75rem; color:#38bdf8; font-weight:600; text-transform:uppercase;">Mission Control Station</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hardware & System Status
    st.sidebar.markdown("### ??? System Telemetry")
    cuda_ok = torch.cuda.is_available()
    dev_name = torch.cuda.get_device_name(0) if cuda_ok else "CPU (Host)"
    vram_str = f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB" if cuda_ok else "N/A"

    st.sidebar.markdown(
        f"""
        <div class="spaci-glass-card" style="padding:0.8rem; font-size:0.82rem; margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="color:#94a3b8;">Compute Device:</span>
                <span style="color:#10b981; font-weight:700;">{'CUDA GPU' if cuda_ok else 'CPU'}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="color:#94a3b8;">Hardware:</span>
                <span style="color:#cbd5e1; font-weight:600;">{dev_name.split()[0]} {dev_name.split()[-2:] if len(dev_name.split()) > 2 else ''}</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#94a3b8;">Available VRAM:</span>
                <span style="color:#38bdf8; font-family:'JetBrains Mono';">{vram_str}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Model Selection
    st.sidebar.markdown("### ?? Detection Weights")
    available_weights = find_available_weights()
    selected_weights = st.sidebar.selectbox(
        "Active Model Checkpoint",
        options=available_weights,
        format_func=lambda p: Path(p).name if "/" in p or "\\" in p else p,
        help="Select trained weights file. Defaults to models/best.pt.",
    )

    # Threshold Controls
    st.sidebar.markdown("### ??? Detection Thresholds")
    conf_thresh = st.sidebar.slider(
        "Confidence Cutoff",
        min_value=0.05,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Minimum prediction confidence required to display detection.",
    )
    iou_thresh = st.sidebar.slider(
        "IoU NMS Threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.45,
        step=0.05,
        help="Intersection-over-Union threshold for Non-Maximum Suppression.",
    )

    # Orbital Sensor Telemetry (NASA / ESA parameters)
    st.sidebar.markdown("### ?? Orbital Sensor Telemetry")
    enable_telemetry = st.sidebar.checkbox("Inject Real-Time Ephemeris", value=False)
    speed_mps = None
    altitude_km = None

    if enable_telemetry:
        speed_mps = st.sidebar.slider(
            "Relative Velocity (m/s)",
            min_value=0.0,
            max_value=15000.0,
            value=7500.0,
            step=250.0,
            help="Relative approach velocity (typical LEO encounter: 7,000-11,000 m/s).",
        )
        altitude_km = st.sidebar.slider(
            "Orbital Altitude (km)",
            min_value=200.0,
            max_value=36000.0,
            value=650.0,
            step=50.0,
            help="LEO crowded shell is 400-900 km (ESA MASTER-8).",
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size:0.75rem; color:#64748b; text-align:center;">
            SPACI v2.0 Production Release<br>
            NASA-STD-8719.14C / ESA MASTER-8
        </div>
        """,
        unsafe_allow_html=True,
    )

    return {
        "weights": selected_weights,
        "conf": conf_thresh,
        "iou": iou_thresh,
        "speed_mps": speed_mps,
        "altitude_km": altitude_km,
    }


# -----------------------------------------------------------------------------
# 4. Main Application Layout & Tabs
# -----------------------------------------------------------------------------

def main():
    render_hero()
    sidebar_params = render_sidebar()

    detector = get_cached_detector(
        weights_path=sidebar_params["weights"],
        conf=sidebar_params["conf"],
        iou=sidebar_params["iou"],
    )
    detector.set_thresholds(sidebar_params["conf"], sidebar_params["iou"])

    tabs = st.tabs([
        "?? Real-Time Detection & Hazard Assessment",
        "?? Video Trajectory & Tumble Tracking",
        "?? Operational Decision Matrix & Standards",
        "?? Model Benchmark & Dataset Audit",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Real-Time Detection & Hazard Assessment
    # -------------------------------------------------------------------------
    with tabs[0]:
        col_src1, col_src2 = st.columns([1, 1])

        with col_src1:
            source_mode = st.radio(
                "Select Input Modality:",
                options=["Pre-Loaded Space Object Gallery (11 Classes)", "Upload Custom Media (Image / Video)"],
                horizontal=True,
            )

        input_image = None
        source_label = ""

        if "Gallery" in source_mode:
            with col_src2:
                selected_sample_name = st.selectbox(
                    "Choose Space Object Sample:",
                    options=list(SAMPLE_TEST_IMAGES.keys()),
                )
            sample_filename = SAMPLE_TEST_IMAGES[selected_sample_name]
            sample_path = DATASET_DIR / "test" / "images" / sample_filename
            if sample_path.exists():
                input_image = cv2.imread(str(sample_path))
                source_label = selected_sample_name
            else:
                st.error(f"Sample file not found at {sample_path}")
        else:
            with col_src2:
                uploaded_file = st.file_uploader(
                    "Upload Image (JPG, PNG) or Video (MP4, AVI)",
                    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"],
                )
            if uploaded_file is not None:
                source_label = uploaded_file.name
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                if uploaded_file.type.startswith("image") or uploaded_file.name.lower().endswith((".jpg", ".png", ".jpeg")):
                    input_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                else:
                    st.info("Video detected! Please switch to the 'Video Trajectory & Tumble Tracking' tab for full temporal analysis.")

        if input_image is not None:
            # Perform Detection & Risk Analysis
            with st.spinner("Analyzing optical signatures and calculating NASA/ESA risk vectors..."):
                annotated_bgr, detections, summary = detector.predict_image(
                    image=input_image,
                    speed_mps=sidebar_params["speed_mps"],
                    altitude_km=sidebar_params["altitude_km"],
                )
                annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

            # Top KPI metrics
            render_kpi_cards(summary)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Side-by-side display: Annotated Image vs Mission Analytics
            disp_col1, disp_col2 = st.columns([3, 2])

            with disp_col1:
                st.markdown(f"#### ?? Optical Field-of-View: `{source_label}`")
                st.image(
                    annotated_rgb,
                    channels="RGB",
                    use_container_width=True,
                )

            with disp_col2:
                st.markdown("#### ?? Proximity Analytics & Hazard Index")
                # Highest risk gauge
                max_score = summary.get("max_risk", 0.0)
                gauge_fig = create_risk_gauge(max_score)
                st.plotly_chart(gauge_fig, use_container_width=True)

                # Operational States Donut
                donut_fig = create_states_donut(summary.get("state_counts", {}))
                st.plotly_chart(donut_fig, use_container_width=True)

            # Class breakdown bar chart
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            bar_fig = create_class_bar_chart(detections)
            st.plotly_chart(bar_fig, use_container_width=True)

            # Detections Data Table
            st.markdown("#### ?? Tactical Detection Telemetry")
            if detections:
                table_rows = []
                for i, det in enumerate(detections, 1):
                    risk_b = det["risk_breakdown"]
                    table_rows.append({
                        "#": i,
                        "Target Identifier": det["display_name"],
                        "Raw Class": det["class_name"],
                        "Operational State": det["operational_state"],
                        "Confidence": f"{det['confidence'] * 100:.1f}%",
                        "FOV Area Ratio": f"{det['area_ratio'] * 100:.2f}%",
                        "Risk Score": f"{det['risk_score']:.3f}",
                        "Size Hazard": f"{risk_b.size_risk:.2f}",
                        "Threat Prior": f"{risk_b.threat_risk:.2f}",
                        "Serviceable": "Yes" if det["risk_breakdown"].details.get("is_intact_structure") else "No",
                    })

                df_detections = pd.DataFrame(table_rows)
                st.dataframe(df_detections, use_container_width=True, hide_index=True)

                # Export Telemetry
                exp_col1, exp_col2, _ = st.columns([1, 1, 2])
                with exp_col1:
                    csv_data = df_detections.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="?? Export Telemetry (CSV)",
                        data=csv_data,
                        file_name=f"spaci_telemetry_{Path(source_label).stem}.csv",
                        mime="text/csv",
                    )
                with exp_col2:
                    json_data = json.dumps(
                        {"summary": summary, "detections": [d for d in detections if "risk_breakdown" not in d]},
                        indent=2,
                        default=str,
                    )
                    st.download_button(
                        label="?? Export Telemetry (JSON)",
                        data=json_data,
                        file_name=f"spaci_telemetry_{Path(source_label).stem}.json",
                        mime="application/json",
                    )
            else:
                st.warning("No orbital objects detected above the current confidence threshold. Try lowering the Confidence Cutoff in the sidebar.")

    # -------------------------------------------------------------------------
    # TAB 2: Video Trajectory & Tumble Tracking
    # -------------------------------------------------------------------------
    with tabs[1]:
        st.markdown("### ?? Multi-Object Kinematics & Aspect Ratio Tumble Tracking")
        st.markdown(
            r"""
            Under **ESA Clean Space ADR criteria**, uncontrolled space objects lose attitude stabilization and
            enter 3D rotational tumbling due to solar radiation pressure (YORP), gravity gradients, and outgassing.
            Tumble rates are estimated using rolling aspect ratio variance $\sigma^2(AR)$ via **BoT-SORT** Kalman tracking.
            """
        )

        vid_file = st.file_uploader(
            "Upload Proximity Video Feed (MP4, AVI, MOV)",
            type=["mp4", "avi", "mov"],
            key="video_uploader",
        )

        if vid_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(vid_file.read())
            tfile.flush()

            cap = cv2.VideoCapture(tfile.name)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

            st.markdown(f"**Video Metrics:** {total_frames} Frames | {fps:.1f} FPS")
            run_btn = st.button("?? Execute Kinematic Tracking", type="primary")

            if run_btn:
                prog_bar = st.progress(0)
                frame_placeholder = st.empty()
                detector.tracker.clear()

                frame_idx = 0
                max_process = min(total_frames, 150)  # Safe frame cap for responsive interactive UI

                while cap.isOpened() and frame_idx < max_process:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    ann_frame, dets, sum_data = detector.track_video_frame(
                        frame=frame,
                        speed_mps=sidebar_params["speed_mps"],
                        altitude_km=sidebar_params["altitude_km"],
                    )

                    ann_rgb = cv2.cvtColor(ann_frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(ann_rgb, channels="RGB", use_container_width=True)

                    frame_idx += 1
                    prog_bar.progress(frame_idx / max_process)

                cap.release()
                st.success(f"Successfully processed {frame_idx} video frames with continuous BoT-SORT trajectory tracking!")
        else:
            st.info("Upload a video clip above to observe real-time Kalman tracking, dynamic aspect ratio variance, and velocity vectors.")

    # -------------------------------------------------------------------------
    # TAB 3: Operational Decision Matrix & Standards
    # -------------------------------------------------------------------------
    with tabs[2]:
        st.markdown("### ?? SPACI 2.0 Operational Decision Matrix & Aerospace Standards")

        # 4 State cards
        st.markdown("#### The Four Operational States")
        sc1, sc2, sc3, sc4 = st.columns(4)

        with sc1:
            st.markdown(
                """
                <div class="spaci-glass-card" style="border-top: 4px solid #ef4444;">
                    <span class="badge-state badge-hazardous">HAZARDOUS</span>
                    <h4 style="margin:8px 0 4px 0; color:#f8fafc;">Critical Threat</h4>
                    <p style="font-size:0.83rem; color:#94a3b8; line-height:1.4;">
                        Risk Score &gt; 0.60. Large debris fragment, spent rocket stage, or rapidly tumbling object.
                        Requires immediate Collision Avoidance Maneuver (CAM) per NASA-STD-8719.14C.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sc2:
            st.markdown(
                """
                <div class="spaci-glass-card" style="border-top: 4px solid #0ea5e9;">
                    <span class="badge-state badge-reusable">REUSABLE / SALVAGE</span>
                    <h4 style="margin:8px 0 4px 0; color:#f8fafc;">Serviceable Asset</h4>
                    <p style="font-size:0.83rem; color:#94a3b8; line-height:1.4;">
                        Risk Score &le; 0.40 and intact structure. Intact defunct satellites retaining structural integrity.
                        Eligible for On-Orbit Servicing (OOS), refueling, or controlled ADR capture.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sc3:
            st.markdown(
                """
                <div class="spaci-glass-card" style="border-top: 4px solid #10b981;">
                    <span class="badge-state badge-active">USEFUL / ACTIVE</span>
                    <h4 style="margin:8px 0 4px 0; color:#f8fafc;">Active Payload</h4>
                    <p style="font-size:0.83rem; color:#94a3b8; line-height:1.4;">
                        Active satellite (CHEOPS, PROBA, LISA Pathfinder, SOHO). Actively maintained orbit with
                        attitude stabilization and telemetry transmission. Preservation priority.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sc4:
            st.markdown(
                """
                <div class="spaci-glass-card" style="border-top: 4px solid #f59e0b;">
                    <span class="badge-state badge-fragment">INERT FRAGMENT</span>
                    <h4 style="margin:8px 0 4px 0; color:#f8fafc;">Passive Debris</h4>
                    <p style="font-size:0.83rem; color:#94a3b8; line-height:1.4;">
                        Passive fragments and non-operational bodies with moderate risk (0.40 &le; Score &le; 0.60).
                        Continuously cataloged and monitored by Space Surveillance Networks.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### Regulatory & Physical Foundations")
        st.markdown(
            r"""
            | Organization | Standard Reference | Applied Aerospace Principle in SPACI 2.0 |
            |---|---|---|
            | **NASA** | **NASA-STD-8719.14C** | Catastrophic Breakup Threshold ($E_p/M_t \ge 40\text{ J/g}$), Collision Probability Constraint ($P_c < 10^{-4}$). |
            | **IADC** | **IADC-02-01** | Size-based triage ($d < 1\text{ cm}$ shieldable, $1\text{--}10\text{ cm}$ lethal non-trackable, $>10\text{ cm}$ trackable). |
            | **ESA** | **MASTER-8 & DISCOS** | Spatial flux density across altitude shells (400?900 km peak crowding), Clean Space ADR capture criteria ($\omega < 5^\circ/\text{s}$). |
            | **ISO** | **ISO 24113:2023** | Space debris mitigation, spacecraft survivability, and collision avoidance trigger criteria. |
            """
        )

    # -------------------------------------------------------------------------
    # TAB 4: Model Benchmark & Dataset Audit
    # -------------------------------------------------------------------------
    with tabs[3]:
        st.markdown("### ?? Deep Model Benchmarks & Exploratory Data Analysis")

        eval_rep_path = REPORTS_DIR / "evaluation_test_report.json"
        if eval_rep_path.exists():
            with open(eval_rep_path) as f:
                eval_data = json.load(f)
            ov = eval_data.get("overall", {})
            mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
            with mcol1:
                st.metric("Test Precision", f"{ov.get('precision', 0) * 100:.2f}%")
            with mcol2:
                st.metric("Test Recall", f"{ov.get('recall', 0) * 100:.2f}%")
            with mcol3:
                st.metric("Test mAP@50", f"{ov.get('map50', 0) * 100:.2f}%")
            with mcol4:
                st.metric("Test mAP@75", f"{ov.get('map75', 0) * 100:.2f}%")
            with mcol5:
                st.metric("Test mAP@50-95", f"{ov.get('map50_95', 0) * 100:.2f}%")
        else:
            st.info("Evaluation metrics will update here once model training and benchmark scripts complete.")

        st.markdown("#### Exploratory Data Analysis Figures (2,467 Samples)")
        gcol1, gcol2 = st.columns(2)

        p1 = REPORTS_DIR / "eda_class_distribution.png"
        p2 = REPORTS_DIR / "eda_bbox_dimensions.png"
        p3 = REPORTS_DIR / "eda_spatial_heatmap.png"

        with gcol1:
            if p1.exists():
                st.image(str(p1), caption="Dataset Class Distribution Across Splits (Train, Valid, Test)", use_container_width=True)
            if p3.exists():
                st.image(str(p3), caption="Debris Centroid Spatial Heatmap Across Camera Field-of-View", use_container_width=True)

        with gcol2:
            if p2.exists():
                st.image(str(p2), caption="Bounding Box Dimensions, Area Ratio & Aspect Ratio Distributions", use_container_width=True)

            pr_curve = REPORTS_DIR / "PR_curve.png"
            if pr_curve.exists():
                st.image(str(pr_curve), caption="Precision-Recall Curve Across 11 Visual Classes", use_container_width=True)


if __name__ == "__main__":
    main()
