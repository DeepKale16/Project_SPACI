import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("reports/figures", exist_ok=True)

# -----------------------------------------------------------------------------
# 1. System Architecture Diagram (Fig 4.1)
# -----------------------------------------------------------------------------
def make_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Title
    ax.text(6, 6.6, "SPACI: Software System Architecture", fontsize=15, fontweight='bold', ha='center', color='#0F284B')
    ax.text(6, 6.25, "Decoupled Asynchronous Perception, Kinematics, GNC, and Telemetry Pipeline", fontsize=9.5, fontstyle='italic', ha='center', color='#475569')

    # Boxes (Columns / Layers)
    layers = [
        ("Layer 1: Input Perception", 0.5, 0.8, 2.3, 4.8, "#F1F5F9", "#0F284B", [
            "Video Encounters\n(MP4, WEBM, AVI)",
            "Optical Testbench\n(3D Physics Stream)",
            "Lab Camera Feed\n(Direct WebRTC/Webcam)",
            "Pulsed LiDAR\n(ToF Distance Returns)"
        ]),
        ("Layer 2: AI & Kinematics", 3.3, 0.8, 2.5, 4.8, "#EFF6FF", "#1D4ED8", [
            "YOLO11s Detector\n(9.42M Params, 11 Classes)",
            "BoT-SORT Tracker\n(Camera Motion Comp)",
            "Tumble Analyzer\n(Rolling Aspect Ratio σ²_AR)",
            "NASA Risk Engine\n(NASA-STD-8719.14C)"
        ]),
        ("Layer 3: 3D GNC Guidance", 6.3, 0.8, 2.5, 4.8, "#ECFDF5", "#047857", [
            "3D LiDAR-Vision Fusion\n(MAD Outlier Rejection)",
            "6-State Kalman Filter\n(State: [x,y,z,vx,vy,vz])",
            "Quartic Ballistic Solver\n(Lead Aim & 1-G Flight)",
            "6-Condition Interlock\n(Go/No-Go Safety Gate)"
        ]),
        ("Layer 4: Web Control HUD", 9.3, 0.8, 2.3, 4.8, "#FAF5FF", "#7E22CE", [
            "FastAPI REST Backend\n(Async HTTP Endpoints)",
            "Atomic 30 Hz WebSockets\n(Real-time JSON Telemetry)",
            "Dark Glassmorphic HUD\n(Dedicated Tab KPI Grids)",
            "Telemetry Database\n(SQLite Hardware Log)"
        ])
    ]

    for title, x, y, w, h, bg, border, items in layers:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", facecolor=bg, edgecolor=border, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.35, title, fontsize=10.5, fontweight='bold', ha='center', color=border)

        item_y = y + h - 0.95
        for item in items:
            box = patches.FancyBboxPatch((x + 0.15, item_y - 0.65), w - 0.3, 0.65, boxstyle="round,pad=0.08", facecolor="#FFFFFF", edgecolor=border, linewidth=1, alpha=0.95)
            ax.add_patch(box)
            ax.text(x + w/2, item_y - 0.35, item, fontsize=8, ha='center', va='center', color='#1E293B', multialignment='center')
            item_y -= 0.95

    # Inter-layer connecting arrows
    arrow_opts = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#0F284B", lw=2)
    ax.annotate("", xy=(3.3, 3.2), xytext=(2.8, 3.2), arrowprops=arrow_opts)
    ax.annotate("", xy=(6.3, 3.2), xytext=(5.8, 3.2), arrowprops=arrow_opts)
    ax.annotate("", xy=(9.3, 3.2), xytext=(8.8, 3.2), arrowprops=arrow_opts)

    plt.tight_layout()
    plt.savefig("reports/figures/system_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------------------------------------------------------
# 2. DFD Level 0 (Context Level Diagram - Fig 4.2)
# -----------------------------------------------------------------------------
def make_dfd_level0():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(5, 4.1, "Data Flow Diagram: Level 0 (Context Level)", fontsize=13, fontweight='bold', ha='center', color='#0F284B')

    # Entities
    # User / Operator (Left)
    user_box = patches.FancyBboxPatch((0.6, 1.4), 2.2, 1.4, boxstyle="square,pad=0.1", facecolor="#EFF6FF", edgecolor="#1D4ED8", linewidth=1.8)
    ax.add_patch(user_box)
    ax.text(1.7, 2.1, "Mission Flight Operator\n/ Aerospace Engineer", fontsize=9.5, fontweight='bold', ha='center', va='center', color='#1E293B')

    # Central Process: 0.0 SPACI System
    p_circle = patches.Circle((5.0, 2.1), 1.1, facecolor="#F8FAFC", edgecolor="#0F284B", linewidth=2.2)
    ax.add_patch(p_circle)
    ax.text(5.0, 2.3, "0.0", fontsize=11, fontweight='bold', ha='center', color='#0F284B')
    ax.text(5.0, 1.95, "SPACI AI Vision,\nGNC & Risk System", fontsize=9, fontweight='bold', ha='center', va='center', color='#0F284B')

    # External Systems (Right)
    sensor_box = patches.FancyBboxPatch((7.2, 2.4), 2.3, 1.1, boxstyle="square,pad=0.1", facecolor="#F1F5F9", edgecolor="#475569", linewidth=1.5)
    ax.add_patch(sensor_box)
    ax.text(8.35, 2.95, "Sensors & Video Source\n(Camera, ToF LiDAR, Files)", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1E293B')

    db_box = patches.FancyBboxPatch((7.2, 0.7), 2.3, 1.1, boxstyle="square,pad=0.1", facecolor="#ECFDF5", edgecolor="#047857", linewidth=1.5)
    ax.add_patch(db_box)
    ax.text(8.35, 1.25, "SQLite Telemetry DB\n& Master Catalog", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1E293B')

    # Data Flow Arrows
    arrow_opts = dict(arrowstyle="->,head_width=0.3,head_length=0.5", color="#1E293B", lw=1.4)
    # Operator to System: Thresholds, Config
    ax.annotate("", xy=(3.9, 2.3), xytext=(2.8, 2.3), arrowprops=arrow_opts)
    ax.text(3.35, 2.5, "Controls & Thresholds", fontsize=7.5, ha='center', color='#1E293B')

    # System to Operator: Telemetry, HUD
    ax.annotate("", xy=(2.8, 1.9), xytext=(3.9, 1.9), arrowprops=arrow_opts)
    ax.text(3.35, 1.65, "Telemetry & Visual HUD", fontsize=7.5, ha='center', color='#1E293B')

    # Sensor to System
    ax.annotate("", xy=(6.0, 2.6), xytext=(7.2, 2.8), arrowprops=arrow_opts)
    ax.text(6.65, 2.9, "Frames & Point Clouds", fontsize=7.5, ha='center', color='#1E293B')

    # System to DB
    ax.annotate("", xy=(7.2, 1.4), xytext=(6.0, 1.7), arrowprops=arrow_opts)
    ax.text(6.65, 1.35, "Logged Trials", fontsize=7.5, ha='center', color='#1E293B')

    plt.tight_layout()
    plt.savefig("reports/figures/dfd_level0.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------------------------------------------------------
# 3. DFD Level 1 (Detailed Functional Flow - Fig 4.3)
# -----------------------------------------------------------------------------
def make_dfd_level1():
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(5.5, 5.65, "Data Flow Diagram: Level 1 (Functional Decomposition)", fontsize=13, fontweight='bold', ha='center', color='#0F284B')

    processes = [
        ("1.0 Ingest & Preprocess", 1.0, 3.8, "#EFF6FF", "#1D4ED8"),
        ("2.0 YOLO11s Inference", 4.0, 3.8, "#EFF6FF", "#1D4ED8"),
        ("3.0 BoT-SORT Tracking", 7.0, 3.8, "#EFF6FF", "#1D4ED8"),
        ("4.0 3D Fusion & Kalman", 1.0, 1.4, "#ECFDF5", "#047857"),
        ("5.0 NASA Risk Engine", 4.0, 1.4, "#FEF3C7", "#D97706"),
        ("6.0 Telemetry Streaming", 7.0, 1.4, "#FAF5FF", "#7E22CE")
    ]

    for title, x, y, bg, border in processes:
        box = patches.FancyBboxPatch((x, y), 2.4, 1.2, boxstyle="round,pad=0.1", facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(box)
        num, name = title.split(" ", 1)
        ax.text(x + 1.2, y + 0.8, num, fontsize=9.5, fontweight='bold', ha='center', color=border)
        ax.text(x + 1.2, y + 0.4, name, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1E293B')

    # Flow arrows
    a_opts = dict(arrowstyle="->,head_width=0.3,head_length=0.5", color="#1E293B", lw=1.3)
    ax.annotate("", xy=(4.0, 4.4), xytext=(3.4, 4.4), arrowprops=a_opts)
    ax.text(3.7, 4.6, "Clean Frames", fontsize=7.5, ha='center')

    ax.annotate("", xy=(7.0, 4.4), xytext=(6.4, 4.4), arrowprops=a_opts)
    ax.text(6.7, 4.6, "Detections", fontsize=7.5, ha='center')

    ax.annotate("", xy=(2.2, 2.6), xytext=(7.8, 3.8), arrowprops=a_opts)
    ax.text(5.0, 3.3, "Tracked Centroids + LiDAR", fontsize=7.5, ha='center')

    ax.annotate("", xy=(4.0, 2.0), xytext=(3.4, 2.0), arrowprops=a_opts)
    ax.text(3.7, 2.2, "3D Vectors", fontsize=7.5, ha='center')

    ax.annotate("", xy=(7.0, 2.0), xytext=(6.4, 2.0), arrowprops=a_opts)
    ax.text(6.7, 2.2, "Risk Score", fontsize=7.5, ha='center')

    plt.tight_layout()
    plt.savefig("reports/figures/dfd_level1.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------------------------------------------------------
# 4. UML Use Case Diagram (Fig 4.4)
# -----------------------------------------------------------------------------
def make_uml_usecase():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(5, 5.15, "UML Use Case Diagram: SPACI Mission Control", fontsize=13, fontweight='bold', ha='center', color='#0F284B')

    # System Boundary Box
    boundary = patches.Rectangle((2.8, 0.4), 6.6, 4.4, facecolor="#F8FAFC", edgecolor="#94A3B8", linewidth=1.5, linestyle="--")
    ax.add_patch(boundary)
    ax.text(3.1, 4.5, "SPACI Vision & GNC System", fontsize=9, fontweight='bold', color="#475569")

    # Actors
    # Operator (Left)
    ax.add_patch(patches.Circle((1.2, 3.4), 0.25, facecolor="#0F284B", edgecolor="#0F284B"))
    ax.add_patch(patches.Polygon([[1.2, 3.1], [0.85, 2.5], [1.55, 2.5]], facecolor="#0F284B"))
    ax.text(1.2, 2.2, "Flight Dynamics\nOperator", fontsize=9, fontweight='bold', ha='center', color="#0F284B")

    # Automated Safety Watchdog (Right)
    ax.add_patch(patches.Rectangle((9.35, 3.15), 0.5, 0.5, facecolor="#047857", edgecolor="#047857"))
    ax.add_patch(patches.Polygon([[9.6, 3.1], [9.25, 2.5], [9.95, 2.5]], facecolor="#047857"))
    ax.text(9.6, 2.2, "Autonomous\nSafety System", fontsize=9, fontweight='bold', ha='center', color="#047857")

    # Use Cases (Ovals)
    usecases = [
        ("UC1: Upload Video / Stream", 5.8, 4.1),
        ("UC2: Adjust Model Thresholds", 5.8, 3.3),
        ("UC3: Execute 11-Class Detection", 5.8, 2.5),
        ("UC4: Evaluate Kinetic Collision Risk", 5.8, 1.7),
        ("UC5: Verify 6-Condition GNC Gate", 5.8, 0.9),
    ]

    for title, cx, cy in usecases:
        ellipse = patches.Ellipse((cx, cy), 3.4, 0.6, facecolor="#FFFFFF", edgecolor="#1D4ED8", linewidth=1.4)
        ax.add_patch(ellipse)
        ax.text(cx, cy, title, fontsize=8.5, ha='center', va='center', color="#1E293B", fontweight='bold')

    # Associations
    line_opts = dict(color="#475569", lw=1.2)
    for uc_idx, (title, cx, cy) in enumerate(usecases):
        if uc_idx < 3:
            ax.plot([1.9, cx - 1.7], [2.9, cy], **line_opts)
        else:
            ax.plot([1.9, cx - 1.7], [2.7, cy], **line_opts)
            ax.plot([cx + 1.7, 9.1], [cy, 2.9], **line_opts)

    plt.tight_layout()
    plt.savefig("reports/figures/uml_usecase.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------------------------------------------------------
# 5. UML Sequence Diagram (Fig 4.5)
# -----------------------------------------------------------------------------
def make_uml_sequence():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(5, 5.15, "UML Sequence Diagram: Live Detection & GNC Cycle", fontsize=13, fontweight='bold', ha='center', color='#0F284B')

    lifelines = [
        ("Client HUD", 1.2),
        ("FastAPI Server", 3.7),
        ("YOLO11s Engine", 6.2),
        ("Kalman GNC", 8.7)
    ]

    for name, x in lifelines:
        box = patches.Rectangle((x - 0.9, 4.3), 1.8, 0.6, facecolor="#EFF6FF", edgecolor="#1D4ED8", linewidth=1.4)
        ax.add_patch(box)
        ax.text(x, 4.6, name, fontsize=8.5, fontweight='bold', ha='center', va='center', color="#0F284B")
        ax.plot([x, x], [0.4, 4.3], color="#94A3B8", lw=1, linestyle="--")

    # Sequence calls
    calls = [
        (3.8, 1.2, 3.7, "1: WS Connect & Send Frame"),
        (3.2, 3.7, 6.2, "2: Ingest Frame & Predict"),
        (2.6, 6.2, 3.7, "3: Return Bounding Boxes & Confidence"),
        (2.0, 3.7, 8.7, "4: Pass Centroid + LiDAR Depth"),
        (1.4, 8.7, 3.7, "5: State Estimate & Lead Aim Vector"),
        (0.8, 3.7, 1.2, "6: 30 Hz Telemetry Broadcast (JSON)")
    ]

    for y, x1, x2, msg in calls:
        ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.4", color="#1E293B", lw=1.3))
        ax.text((x1 + x2) / 2, y + 0.12, msg, fontsize=7.5, ha='center', color="#1E293B")

    plt.tight_layout()
    plt.savefig("reports/figures/uml_sequence.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------------------------------------------------------
# 6. UML Activity Diagram (Fig 4.6)
# -----------------------------------------------------------------------------
def make_uml_activity():
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(4, 6.7, "UML Activity Diagram: Perception-to-GNC Loop", fontsize=13, fontweight='bold', ha='center', color='#0F284B')

    # Initial node
    init_dot = patches.Circle((4, 6.2), 0.15, facecolor="#0F284B", edgecolor="#0F284B")
    ax.add_patch(init_dot)

    steps = [
        ("Ingest Optical Frame / Video Stream", 5.4),
        ("Preprocess & Normalize (640×640)", 4.6),
        ("Execute YOLO11s Forward Pass", 3.8),
        ("Update BoT-SORT Track IDs & σ²_AR", 3.0),
        ("Compute NASA Kinetic Risk Index", 2.2),
        ("Evaluate 6-Condition GNC Safety Gate", 1.4),
        ("Broadcast WebSocket Telemetry HUD", 0.6)
    ]

    for idx, (label, y) in enumerate(steps):
        box = patches.FancyBboxPatch((1.6, y - 0.25), 4.8, 0.5, boxstyle="round,pad=0.1", facecolor="#EFF6FF", edgecolor="#1D4ED8", linewidth=1.3)
        ax.add_patch(box)
        ax.text(4, y, label, fontsize=8.5, ha='center', va='center', color="#0F284B", fontweight='bold')
        
        # Arrow down
        prev_y = 6.2 if idx == 0 else steps[idx-1][1] - 0.25
        ax.annotate("", xy=(4, y + 0.25), xytext=(4, prev_y), arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.35", color="#1E293B", lw=1.2))

    plt.tight_layout()
    plt.savefig("reports/figures/uml_activity.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------------------------------------------------------
# 7. SDLC Agile/Iterative Model Diagram (Fig 3.1)
# -----------------------------------------------------------------------------
def make_sdlc_diagram():
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(5, 4.15, "Software Development Life Cycle: Iterative Engineering Model", fontsize=13, fontweight='bold', ha='center', color='#0F284B')

    stages = [
        ("Phase 1: Requirements\n& Baseline Audit", 1.0, 1.8),
        ("Phase 2: Model Design\n& Training (YOLO11s)", 3.0, 1.8),
        ("Phase 3: Kinematics\n& Risk Engine", 5.0, 1.8),
        ("Phase 4: GNC Fusion\n& Safety Gating", 7.0, 1.8),
        ("Phase 5: Web HUD\n& Deployment", 9.0, 1.8)
    ]

    for title, cx, cy in stages:
        box = patches.FancyBboxPatch((cx - 0.85, cy - 0.5), 1.7, 1.0, boxstyle="round,pad=0.1", facecolor="#F1F5F9", edgecolor="#0F284B", linewidth=1.4)
        ax.add_patch(box)
        ax.text(cx, cy, title, fontsize=7.5, ha='center', va='center', color="#0F284B", fontweight='bold', multialignment='center')

    # Forward arrows
    for i in range(len(stages) - 1):
        x1 = stages[i][1] + 0.85
        x2 = stages[i+1][1] - 0.85
        ax.annotate("", xy=(x2, 1.8), xytext=(x1, 1.8), arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.4", color="#1D4ED8", lw=1.5))

    # Iterative Feedback Loop
    ax.annotate("", xy=(3.0, 1.2), xytext=(9.0, 1.2), arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.4", color="#D97706", lw=1.5, connectionstyle="arc3,rad=-0.3"))
    ax.text(6.0, 0.4, "Continuous Validation & Model Iteration Loop", fontsize=8, ha='center', color="#D97706", fontweight='bold')

    plt.tight_layout()
    plt.savefig("reports/figures/sdlc_model.png", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating comprehensive SPACI software report diagrams...")
    make_system_architecture()
    make_dfd_level0()
    make_dfd_level1()
    make_uml_usecase()
    make_uml_sequence()
    make_uml_activity()
    make_sdlc_diagram()
    print("All 7 diagrams generated successfully in reports/figures/")
