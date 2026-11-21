"""
ui_components.py - Reusable Streamlit UI & Plotly Analytics for SPACI 2.0
==========================================================================
Provides modular visual components, metric cards, Plotly charts, and sample
test image definitions for the deployment dashboard.
"""

from typing import Dict, List, Any, Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src.config import (
    STATE_HAZARDOUS,
    STATE_REUSABLE,
    STATE_ACTIVE,
    STATE_FRAGMENT,
    STATE_COLORS_HEX,
    CLASS_DISPLAY_NAMES,
)

SAMPLE_TEST_IMAGES = {
    "CHEOPS (ESA Exoplanet Observatory)": "img010033_jpg.rf.32ef88458356049c1726406ec802d3ba.jpg",
    "Space Debris Fragment": "img021927_jpg.rf.91830c181251b09d0664c76dbafb9d5c.jpg",
    "Double Start / Ambiguous Body": "img030225_jpg.rf.07359beb506faa15dee6b2416bd2f714.jpg",
    "Earth Observation Sat-1": "img040342_jpg.rf.613e64136c166993b418d92cbf807a70.jpg",
    "LISA Pathfinder (ESA Tech Demonstrator)": "img050582_jpg.rf.7041faffb8910ffd424e156960718d2d.jpg",
    "PROBA-2 (Sun Observer)": "img000124_jpg.rf.dcf525bbc6c6c45a3e387abc33d15112.jpg",
    "PROBA-3 CSC (Coronagraph Spacecraft)": "img060265_jpg.rf.300fa9d6f8f06522f9dc5c6c1e724317.jpg",
    "PROBA-3 OCS (Occulter Spacecraft)": "img071318_jpg.rf.c3a8771650fec77976cfbc9b35b8c46f.jpg",
    "SMART-1 (Lunar Demonstrator)": "img080433_jpg.rf.13778d212f5eb8b2fe728c9899fd29a9.jpg",
    "SOHO (Solar & Heliospheric Observatory)": "img090877_jpg.rf.74c9d4ecaa18d18a5f6c684e14beb770.jpg",
    "XMM-Newton (X-Ray Multi-Mirror Telescope)": "img100270_jpg.rf.0ae42f6549b65ab4df27f0dfec3ff709.jpg",
}


def render_hero():
    """Renders the top executive header banner."""
    st.markdown(
        """
        <div class="spaci-hero">
            <div class="spaci-badge-pill pill-orbital">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10b981; margin-right:4px; box-shadow:0 0 8px #10b981;"></span>
                AUTONOMOUS ORBITAL SITUATIONAL AWARENESS ACTIVE
            </div>
            <h1>SPACI 2.0 ?" Space Debris Detection & Risk Assessment</h1>
            <p>
                Physics-grounded computer vision system powered by deep transfer learning and calibrated
                under <b>NASA-STD-8719.14C</b> and <b>ESA MASTER-8</b> standards. Detects, tracks, and classifies
                orbital objects into 11 visual classes and 4 operational hazard states.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(summary: Dict[str, Any]):
    """Renders the top metric cards."""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            label="Total Detections",
            value=summary.get("total_objects", 0),
            delta="In Field of View",
            delta_color="off",
        )
    with col2:
        st.metric(
            label="Hazardous",
            value=summary.get("hazardous_count", 0),
            delta="Critical Threat",
            delta_color="inverse",
        )
    with col3:
        st.metric(
            label="Reusable / Salvage",
            value=summary.get("reusable_count", 0),
            delta="Serviceable Bus",
            delta_color="normal",
        )
    with col4:
        st.metric(
            label="Useful / Active",
            value=summary.get("active_count", 0),
            delta="Active Satellites",
            delta_color="normal",
        )
    with col5:
        mean_r = summary.get("mean_risk", 0.0)
        st.metric(
            label="Mean Risk Index",
            value=f"{mean_r:.2f}",
            delta="Low" if mean_r < 0.4 else ("High" if mean_r > 0.6 else "Medium"),
            delta_color="inverse" if mean_r > 0.6 else "normal",
        )


def render_state_badge_html(state: str) -> str:
    """Returns styled HTML badge string for an operational state."""
    cls_map = {
        STATE_HAZARDOUS: "badge-hazardous",
        STATE_REUSABLE: "badge-reusable",
        STATE_ACTIVE: "badge-active",
        STATE_FRAGMENT: "badge-fragment",
    }
    badge_cls = cls_map.get(state, "badge-fragment")
    return f'<span class="badge-state {badge_cls}">{state}</span>'


def create_risk_gauge(score: float) -> go.Figure:
    """Plotly radial indicator gauge for orbital risk score."""
    val = round(score * 100, 1)

    if score > 0.60:
        bar_color = "#ef4444"
    elif score < 0.40:
        bar_color = "#10b981"
    else:
        bar_color = "#f59e0b"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=val,
            title={"text": "Orbital Collision Risk", "font": {"size": 15, "color": "#f8fafc"}},
            number={"suffix": "%", "font": {"size": 28, "color": "#f8fafc", "family": "JetBrains Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#64748b"},
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "rgba(15, 23, 42, 0.6)",
                "borderwidth": 1,
                "bordercolor": "rgba(56, 189, 248, 0.2)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(16, 185, 129, 0.15)"},
                    {"range": [40, 60], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [60, 100], "color": "rgba(239, 68, 68, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#ef4444", "width": 3},
                    "thickness": 0.75,
                    "value": 60,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cbd5e1"},
        height=220,
        margin={"t": 35, "b": 10, "l": 25, "r": 25},
    )
    return fig


def create_states_donut(state_counts: Dict[str, int]) -> go.Figure:
    """Plotly donut chart for the 4 operational classification states."""
    labels = list(state_counts.keys())
    values = list(state_counts.values())

    colors = [STATE_COLORS_HEX.get(k, "#94a3b8") for k in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
                textinfo="label+value",
                hoverinfo="label+percent+value",
                textfont=dict(size=12, color="#f8fafc"),
            )
        ]
    )
    fig.update_layout(
        title={"text": "Operational Classification Breakdown", "font": {"size": 14, "color": "#f8fafc"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cbd5e1"},
        height=240,
        margin={"t": 35, "b": 10, "l": 10, "r": 10},
        showlegend=False,
    )
    return fig


def create_class_bar_chart(detections: List[Dict[str, Any]]) -> go.Figure:
    """Plotly bar chart of detected classes and confidence."""
    if not detections:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=200,
        )
        return fig

    classes = [d["display_name"] for d in detections]
    confs = [round(d["confidence"] * 100, 1) for d in detections]
    colors = [STATE_COLORS_HEX.get(d["operational_state"], "#38bdf8") for d in detections]

    fig = go.Figure(
        data=[
            go.Bar(
                x=classes,
                y=confs,
                marker_color=colors,
                text=[f"{c}%" for c in confs],
                textposition="auto",
                marker_line_color="#1e293b",
                marker_line_width=1.5,
            )
        ]
    )
    fig.update_layout(
        title={"text": "Detected Objects & Model Confidence", "font": {"size": 14, "color": "#f8fafc"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cbd5e1"},
        height=240,
        margin={"t": 35, "b": 40, "l": 20, "r": 20},
        yaxis={"title": "Confidence (%)", "range": [0, 100], "gridcolor": "rgba(100, 116, 139, 0.2)"},
        xaxis={"tickangle": -25},
    )
    return fig
