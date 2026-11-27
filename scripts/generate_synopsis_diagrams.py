import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("reports/figures", exist_ok=True)


def make_decision_flowchart():
    """Fig 3.1: 3-Stage Autonomous Debris Verification, Salvageability & Safe Capture Flowchart."""
    fig, ax = plt.subplots(figsize=(11.4, 8.4), dpi=300)
    ax.set_xlim(0, 11.4)
    ax.set_ylim(-0.2, 9.2)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Title
    ax.text(
        5.5, 8.88,
        "SPACI End-to-End Methodology & 3-Stage Decision Flowchart",
        fontsize=13.5, fontweight="bold", ha="center", color="#0F284B"
    )
    ax.text(
        5.5, 8.55,
        "Simultaneous Debris Verification, Salvageable Element Evaluation, and Safe Capture Gating",
        fontsize=9, fontstyle="italic", ha="center", color="#475569"
    )

    def draw_box(cx, cy, w, h, text, bg="#EFF6FF", border="#1D4ED8", tc="#0F284B", fs=8.3, bold=True):
        box = patches.FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h,
            boxstyle="round,pad=0.08", facecolor=bg, edgecolor=border, linewidth=1.6
        )
        ax.add_patch(box)
        ax.text(
            cx, cy, text, fontsize=fs,
            fontweight="bold" if bold else "normal",
            ha="center", va="center", color=tc, multialignment="center"
        )

    def draw_diamond(cx, cy, w, h, text, bg="#FEF3C7", border="#D97706", tc="#78350F", fs=8.1):
        pts = [[cx, cy + h / 2], [cx + w / 2, cy], [cx, cy - h / 2], [cx - w / 2, cy]]
        poly = patches.Polygon(pts, closed=True, facecolor=bg, edgecolor=border, linewidth=1.7)
        ax.add_patch(poly)
        ax.text(cx, cy, text, fontsize=fs, fontweight="bold", ha="center", va="center", color=tc, multialignment="center")

    def arrow(x1, y1, x2, y2, label=None, lx=None, ly=None, color="#1E293B"):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.45", color=color, lw=1.5)
        )
        if label:
            tx = (x1 + x2) / 2 if lx is None else lx
            ty = (y1 + y2) / 2 if ly is None else ly
            ax.text(
                tx, ty, label, fontsize=7.8, fontweight="bold", ha="center", va="center",
                color=color, bbox=dict(boxstyle="round,pad=0.14", facecolor="#FFFFFF", edgecolor="none", alpha=0.92)
            )

    # Row 1: Ingestion
    draw_box(
        4.1, 8.05, 4.8, 0.62,
        "Optical Input Ingestion & Preprocessing (640x640)\n(Orbital Video Feed / Live Camera / Simulated LiDAR)",
        bg="#F1F5F9", border="#0F284B", tc="#0F284B"
    )

    # Row 2: YOLO11s + BoT-SORT
    draw_box(
        4.1, 7.05, 4.8, 0.66,
        "YOLO11s 11-Class Detector + BoT-SORT Tracker\n(Bounding Boxes, Class Probabilities, Track IDs, Tumble σ²_AR)",
        bg="#EFF6FF", border="#1D4ED8", tc="#1E3A8A"
    )
    arrow(4.1, 7.66, 4.1, 7.46)

    # Stage 1 Decision: Real Debris vs Active Satellite
    draw_diamond(
        4.1, 5.82, 3.6, 1.05,
        "STAGE 1: Verification\nIs Object Real Debris\n(Not Active Satellite)?",
        bg="#FEF3C7", border="#D97706"
    )
    arrow(4.1, 6.64, 4.1, 6.36)

    # Branch NO -> Active / Useful Satellite
    draw_box(
        8.65, 5.82, 3.55, 0.85,
        "STATE: USEFUL / ACTIVE\n(Operational Satellite e.g. CHEOPS, SOHO)\nAction: Preserve Asset & Stand-off Clearance",
        bg="#ECFDF5", border="#059669", tc="#065F46", fs=7.8
    )
    arrow(5.90, 5.82, 6.80, 5.82, label="NO (Active)", lx=6.35, ly=6.04, color="#059669")

    # Branch YES -> Stage 2 Decision: Reusable / Salvageable Elements?
    draw_diamond(
        4.1, 4.22, 3.7, 1.08,
        "STAGE 2: Salvage Check\nAre Useful / Reusable\nElements Present?",
        bg="#E0F2FE", border="#0284C7", tc="#0C4A6E"
    )
    arrow(4.1, 5.30, 4.1, 4.78, label="YES (Confirmed Debris)", lx=5.05, ly=5.04, color="#B45309")

    # Branch YES -> Reusable / Salvageable Tag
    draw_box(
        8.65, 4.22, 3.55, 0.85,
        "TAG: REUSABLE / SALVAGE\n(Intact Bus, Solar Panels, Adapters)\nAction: Prioritize Non-Destructive Recovery",
        bg="#EFF6FF", border="#0284C7", tc="#075985", fs=7.8
    )
    arrow(5.95, 4.22, 6.80, 4.22, label="YES (Intact)", lx=6.38, ly=4.44, color="#0284C7")
    # Route reusable target cleanly into Stage 3 capture check
    arrow(8.65, 3.72, 6.08, 2.75, label="Route to Capture Check", lx=7.55, ly=3.36, color="#0284C7")

    # Stage 3: Tumble, Risk & Capture Window
    draw_diamond(
        4.1, 2.65, 4.1, 1.12,
        "STAGE 3: Simultaneous GNC\nRisk <= Threshold & Tumble σ²_AR\nWithin Safe Capture Window?",
        bg="#FEE2E2", border="#DC2626", tc="#7F1D1D"
    )
    arrow(4.1, 3.68, 4.1, 3.22, label="Inert / Fragment", lx=4.85, ly=3.45, color="#475569")

    # Left outcome: Safe Capture Ready
    draw_box(
        2.15, 1.25, 3.55, 0.80,
        "SAFE CAPTURE READY (GO)\n6-State Kalman Lead Aim + Quartic Solver\n-> Deploy Retrieval / Capture Guidance",
        bg="#DCFCE7", border="#16A34A", tc="#14532D", fs=7.8
    )
    arrow(2.85, 2.25, 2.15, 1.73, label="YES (Safe Window)", lx=2.12, ly=2.03, color="#16A34A")

    # Right outcome: Hazardous Threat
    draw_box(
        6.35, 1.25, 3.55, 0.80,
        "HAZARDOUS THREAT (NO-GO)\nNASA-STD-8719.14C Risk > 0.60 / High Spin\n-> Abort Capture & Trigger Avoidance",
        bg="#FEE2E2", border="#DC2626", tc="#7F1D1D", fs=7.8
    )
    arrow(5.35, 2.25, 6.35, 1.73, label="NO (High Risk/Spin)", lx=6.35, ly=2.03, color="#DC2626")

    # Bottom Full-Width Bar: 30 Hz HUD
    draw_box(
        5.5, 0.30, 9.8, 0.50,
        "30 Hz WebSocket Telemetry HUD  |  Per-Tab KPI Metrics (Live / Video / Gallery)  |  SQLite & CSV/JSON Export",
        bg="#FAF5FF", border="#7E22CE", tc="#581C87", fs=8.3
    )
    arrow(2.15, 0.77, 2.15, 0.63, color="#7E22CE")
    arrow(6.35, 0.77, 6.35, 0.63, color="#7E22CE")
    # Route right-hand branch cleanly outside the Reusable box
    ax.plot([10.50, 10.85, 10.85], [5.82, 5.82, 0.30], color="#7E22CE", lw=1.5)
    arrow(10.85, 0.30, 10.48, 0.30, color="#7E22CE")

    plt.tight_layout()
    plt.savefig("reports/figures/synopsis_decision_flowchart.png", dpi=300, bbox_inches="tight")
    plt.close()


def make_application_block_diagram():
    """Fig 4.1: Application & Software Module Block Diagram."""
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    ax.text(
        5.75, 6.08,
        "SPACI Application & 5-Layer Software Architecture Block Diagram",
        fontsize=13.5, fontweight="bold", ha="center", color="#0F284B"
    )
    ax.text(
        5.75, 5.75,
        "Modular Perception, Salvage Classification, NASA Risk Assessment, Kalman GNC & FastAPI Telemetry Stack",
        fontsize=9, fontstyle="italic", ha="center", color="#475569"
    )

    cols = [
        ("1. Data & Sensor Input", 0.3, 0.7, 2.0, 4.7, "#F1F5F9", "#334155", [
            "Orbital Video Feeds\n(MP4 / AVI / WEBM)",
            "Static Imagery\n& Multi-Batch Gallery",
            "Live Camera / WebRTC\nOptical Stream",
            "Simulated ToF LiDAR\nRange Sensor Feed"
        ]),
        ("2. AI Detection & Tracking", 2.55, 0.7, 2.1, 4.7, "#EFF6FF", "#1D4ED8", [
            "Frame Normalizer\n(640x640 RGB Tensor)",
            "YOLO11s Engine\n(9.42M Params, 11 Classes)",
            "BoT-SORT Tracker\n(Persistent Track IDs)",
            "Tumble Estimator\n(15-Frame Variance σ²_AR)"
        ]),
        ("3. Salvage & Risk Logic", 4.9, 0.7, 2.1, 4.7, "#FEFCE8", "#B45309", [
            "Friend-or-Foe Filter\n(Debris vs Active Sat)",
            "Salvage Classifier\n(Reusable Bus / Panels)",
            "NASA-STD-8719.14C\nKinetic Risk Scorer",
            "4-State Flight Rules\n(Hazard/Active/Salvage/Inert)"
        ]),
        ("4. 3D GNC & Safety Gate", 7.25, 0.7, 2.0, 4.7, "#ECFDF5", "#047857", [
            "MAD Outlier Rejector\n(2D+LiDAR 3D Fusion)",
            "6-State Kalman Filter\n([x,y,z,vx,vy,vz])",
            "Quartic Lead Solver\n(Intercept Prediction)",
            "6-Condition Interlock\n(GO / NO-GO Capture)"
        ]),
        ("5. Mission Control HUD", 9.5, 0.7, 1.7, 4.7, "#FAF5FF", "#7E22CE", [
            "FastAPI Async Core\n(REST Endpoints)",
            "30 Hz WebSockets\n(Atomic Telemetry)",
            "Interactive Web HUD\n(Three.js + Tab KPIs)",
            "SQLite & CSV/JSON\nMission Export"
        ]),
    ]

    for title, x, y, w, h, bg, border, items in cols:
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.08",
            facecolor=bg, edgecolor=border, linewidth=1.7
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h - 0.3, title, fontsize=8.8, fontweight="bold", ha="center", color=border)
        iy = y + h - 0.92
        for item in items:
            sub = patches.FancyBboxPatch(
                (x + 0.12, iy - 0.58), w - 0.24, 0.64,
                boxstyle="round,pad=0.05", facecolor="#FFFFFF", edgecolor=border, linewidth=1.0
            )
            ax.add_patch(sub)
            ax.text(x + w / 2, iy - 0.26, item, fontsize=7.4, ha="center", va="center", color="#1E293B", multialignment="center")
            iy -= 0.96

    # Inter-column arrows
    arrow_xs = [(2.32, 2.53), (4.67, 4.88), (7.02, 7.23), (9.27, 9.48)]
    for x1, x2 in arrow_xs:
        ax.annotate(
            "", xy=(x2, 3.05), xytext=(x1, 3.05),
            arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.4", color="#0F284B", lw=1.8)
        )

    # Bottom feedback arrow
    ax.annotate(
        "", xy=(3.6, 0.42), xytext=(10.35, 0.42),
        arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.35", color="#64748B", lw=1.3, linestyle="--")
    )
    ax.text(
        6.9, 0.22,
        "Operator Real-Time Threshold Tuning (Confidence, Risk Cutoff, Capture Range Envelope)",
        fontsize=8, fontstyle="italic", ha="center", color="#475569"
    )

    plt.tight_layout()
    plt.savefig("reports/figures/synopsis_block_diagram.png", dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    make_decision_flowchart()
    make_application_block_diagram()
    print("Generated synopsis_decision_flowchart.png and synopsis_block_diagram.png")
