import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_software_synopsis_docx(output_path):
    doc = docx.Document()

    # Standard Academic Margins: Left 1.25" (Binding), Right 1.0", Top 1.0", Bottom 1.0"
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)
        
        # Header / Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("AISSMS IOIT, PUNE | B.TECH PROJECT SYNOPSIS (SOFTWARE)")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(120, 120, 120)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("SPACI: AI Space Debris Detection & Kinematics Software System  |  Page ")
        frun.font.name = "Arial"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(120, 120, 120)

    # Base Normal Style
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------------------
    # COVER / INSTITUTIONAL HEADER
    # -------------------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_inst.add_run("ALL INDIA SHRI SHIVAJI MEMORIAL SOCIETY’S\n")
    r1.font.name = "Arial"
    r1.font.size = Pt(11)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(180, 20, 20)

    r2 = p_inst.add_run("INSTITUTE OF INFORMATION TECHNOLOGY, PUNE\n")
    r2.font.name = "Arial"
    r2.font.size = Pt(16)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(15, 30, 75)

    r3 = p_inst.add_run("Affiliated to Savitribai Phule Pune University (SPPU) | Accredited by NAAC with 'A+' Grade\n")
    r3.font.name = "Arial"
    r3.font.size = Pt(9)
    r3.font.italic = True
    r3.font.color.rgb = RGBColor(90, 90, 90)

    r4 = p_inst.add_run("“ADDING VALUE TO ENGINEERING” — SINCE 1917\n")
    r4.font.name = "Arial"
    r4.font.size = Pt(9.5)
    r4.font.bold = True
    r4.font.color.rgb = RGBColor(180, 20, 20)

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(6)
    r_div = p_div.add_run("―" * 55)
    r_div.font.color.rgb = RGBColor(15, 30, 75)

    p_syn = doc.add_paragraph()
    p_syn.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_syn = p_syn.add_run("PROJECT SYNOPSIS\n")
    r_syn.font.name = "Arial"
    r_syn.font.size = Pt(14)
    r_syn.font.bold = True
    r_syn.font.color.rgb = RGBColor(15, 30, 75)

    r_sub = p_syn.add_run("FOR THE DEGREE OF BACHELOR OF TECHNOLOGY\nIN\nARTIFICIAL INTELLIGENCE & DATA SCIENCE / COMPUTER ENGINEERING\n")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(10)
    r_sub.font.bold = True

    # Title Block
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(6)
    r_t = p_title.add_run("SPACI: DEEP LEARNING-BASED AUTONOMOUS SPACE DEBRIS MULTI-CLASS DETECTION, ORBITAL VIDEO KINEMATIC TRACKING, AND COLLISION RISK ASSESSMENT SOFTWARE SYSTEM\n")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(12.5)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(15, 45, 105)

    r_sdg = p_title.add_run("(SDG #9 – Industry, Innovation & Infrastructure | SDG #11 – Sustainable Outer Space Communities | SDG #12 – Responsible Circular Space Economy)")
    r_sdg.font.name = "Arial"
    r_sdg.font.size = Pt(9.5)
    r_sdg.font.italic = True
    r_sdg.font.color.rgb = RGBColor(70, 70, 70)

    # Metadata Summary Box
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_data = [
        ("Project Title:", "SPACI: Deep Learning-Based Autonomous Space Debris Multi-Class Detection, Orbital Video Kinematic Tracking, and Collision Risk Assessment Software System"),
        ("Project Type:", "Software Product / Applied AI & Computer Vision Research / Data-Driven Engineering System"),
        ("Programme / Branch:", "Bachelor of Technology in Artificial Intelligence & Data Science / Computer Engineering"),
        ("Academic Year:", "2026 – 2027"),
        ("Primary SDG Mapping:", "SDG #9 (Target 9.5: Advanced AI & Aerospace Research) & SDG #11 (Target 11.B: Critical Infrastructure Safety)")
    ]

    for idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.0)
        cell_val.width = Inches(4.25)
        
        p0 = cell_lbl.paragraphs[0]
        r = p0.add_run(label)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        
        p1 = cell_val.paragraphs[0]
        r = p1.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        
        set_cell_background(cell_lbl, "F1F5F9")
        set_cell_background(cell_val, "FFFFFF")
        set_cell_margins(cell_lbl, 50, 50, 80, 80)
        set_cell_margins(cell_val, 50, 50, 80, 80)

    # Student Details Table
    p_stu_lbl = doc.add_paragraph()
    p_stu_lbl.paragraph_format.space_before = Pt(6)
    p_stu_lbl.paragraph_format.space_after = Pt(2)
    r = p_stu_lbl.add_run("SUBMITTED BY:")
    r.font.name = "Arial"
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 30, 75)

    stu_table = doc.add_table(rows=4, cols=3)
    stu_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    stu_headers = ["Sr. No.", "Student Full Name", "Exam Seat No. / University PRN"]
    for i, h in enumerate(stu_headers):
        cell = stu_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 50, 50, 80, 80)

    stu_rows = [
        ("1", "Deep Ravindra Kale", "PRN: 72312016B / Seat No: <Seat No>"),
        ("2", "<Student Name 2>", "PRN: <PRN No 2> / Seat No: <Seat No 2>"),
        ("3", "<Student Name 3>", "PRN: <PRN No 3> / Seat No: <Seat No 3>")
    ]
    for r_idx, data in enumerate(stu_rows, start=1):
        row = stu_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.5)
            set_cell_margins(cell, 50, 50, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # Guide Details
    p_guide = doc.add_paragraph()
    p_guide.paragraph_format.space_before = Pt(6)
    p_guide.paragraph_format.space_after = Pt(10)
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_g1 = p_guide.add_run("UNDER THE GUIDANCE OF\n")
    r_g1.font.name = "Arial"
    r_g1.font.size = Pt(9.5)
    r_g1.font.bold = True
    r_g2 = p_guide.add_run("<GUIDE NAME>\n")
    r_g2.font.name = "Arial"
    r_g2.font.size = Pt(11.5)
    r_g2.font.bold = True
    r_g2.font.color.rgb = RGBColor(15, 30, 75)
    r_g3 = p_guide.add_run("Assistant Professor / Associate Professor\nDepartment of Artificial Intelligence & Data Science / Computer Engineering\nAISSMS Institute of Information Technology, Pune – 411001")
    r_g3.font.name = "Arial"
    r_g3.font.size = Pt(9.5)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # HELPER FORMATTING FUNCTIONS
    # -------------------------------------------------------------------------
    def add_h1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 30, 75)
        return p

    def add_h2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(25, 55, 115)
        return p

    def add_body(text, bold_prefix=None, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(11)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.italic = italic
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(11)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        return p

    # -------------------------------------------------------------------------
    # 1. INTRODUCTION
    # -------------------------------------------------------------------------
    add_h1("1. INTRODUCTION")
    add_h2("1.1 Background of the Project")
    add_body("Low Earth Orbit (LEO, 200–2,000 km altitude) is experiencing exponential congestion from defunct satellites, rocket upper stages, and fragmentation debris. According to the European Space Agency (ESA) Space Debris Office DISCOS database, over 47,000 tracked objects and an estimated 1.5 million hazardous fragments (> 1 cm) travel at hypervelocities of 7.5 to 10 km/s (approx. 27,000 km/h). Under NASA Technical Standard NASA-STD-8719.14C, any collision delivering kinetic energy greater than 40 Joules per gram of target mass triggers catastrophic fragmentation, escalating the Kessler Syndrome cascade. To mitigate this threat, autonomous computer vision and flight dynamics software systems are urgently needed to identify non-cooperative objects, compute relative attitude tumble, and evaluate collision risk in real time.")

    add_h2("1.2 Problem Statement")
    add_body("Existing space surveillance relies heavily on ground-based radar tracking and pre-computed orbital ephemerides (Two-Line Elements / TLEs). However, ground tracking suffers from high latency (hours to days), poor accuracy for tumbling sub-decimeter debris, and an inability to provide real-time guidance during orbital encounters. Autonomous rendezvous and capture systems require onboard computer vision capable of: (1) Robustly distinguishing uncooperative debris fragments from operational satellites across extreme lighting and zero-G orientations; (2) Maintaining continuous kinematic tracking through video frames; (3) Estimating rotational tumbling rates; and (4) Formulating quantitative collision risk scores without human-in-the-loop delays.")
    add_body("Project Scope Clarification: ", "Engineering Focus: ")
    add_body("The SPACI project focuses exclusively on the SOFTWARE, COMPUTER VISION, AND MATHEMATICAL MODELING components of this challenge. We design, train, and validate an end-to-end software pipeline comprising an 11-class deep learning detector (YOLO11s), BoT-SORT temporal tracking, rolling aspect-ratio tumble variance estimation, a NASA-STD-8719.14C collision risk engine, 3D LiDAR-vision sensor fusion, and a high-speed FastAPI mission control web dashboard executing at sub-20 ms inference latency.")

    add_h2("1.3 Motivation / Need for the Project")
    add_body("1. Autonomous Space Situational Awareness (SSA): Modern satellites and Active Debris Removal (ADR) vehicles require lightweight, edge-deployable software capable of real-time multi-class detection to avoid catastrophic collisions.")
    add_body("2. Preservation of Orbital Assets: Distinguishing active satellites (e.g., CHEOPS, SOHO, PROBA) from hazardous derelicts is essential to prevent false-alarm collision avoidance burns and enable targeted salvage.")
    add_body("3. High-Speed Software Architecture: Eliminating slow polling and script-rerun frameworks (such as Streamlit) by building an asynchronous FastAPI REST and 30 Hz WebSocket architecture that serves real-time mission telemetry seamlessly.")

    add_h2("1.4 Objectives of the Project (Measurable Software Targets)")
    add_bullet(" To curate, audit, and augment an 11-class orbital space object imagery dataset (2,467 images) with zero-G spatial rotations and solar glare jitter, ensuring zero hash overlap and balanced representation.", "Objective 1 (Dataset Engineering & Auditing):")
    add_bullet(" To fine-tune a YOLO11s deep convolutional neural network via transfer learning, achieving a multi-class mean Average Precision mAP@50 ≥ 85.0% and strict localization mAP@50-95 ≥ 50.0% with an edge inference latency under 15 ms.", "Objective 2 (Deep Learning Detection & Classification):")
    add_bullet(" To implement BoT-SORT temporal multi-object tracking on orbital encounter video feeds and calculate rolling aspect-ratio variance (σ²_AR) over 15-frame sliding windows to quantify target rotational tumble rate.", "Objective 3 (Kinematic Video Tracking & Tumble Estimation):")
    add_bullet(" To implement a mathematical collision risk scoring engine based on NASA-STD-8719.14C kinetic energy thresholds, mapping objects into four operational flight states: Hazardous (Risk > 0.60), Useful/Active, Reusable/Salvageable, and Inert Fragment.", "Objective 4 (NASA/ESA Collision Risk Scoring Engine):")
    add_bullet(" To formulate a 6-state 3D Kalman filter with pulsed LiDAR depth fusion and develop a closed-form quartic ballistic lead-aim trajectory solver with a 6-condition safety interlock algorithm.", "Objective 5 (3D Sensor Fusion & Ballistic GNC Algorithms):")
    add_bullet(" To build a full-stack Mission Control web interface using FastAPI and WebSockets (30 Hz) featuring keyframe HUDs, interactive parameter sliders, 3D physics testbench, and 1-click telemetry data export.", "Objective 6 (Real-Time Mission Control Web Platform):")

    add_h2("1.5 Scope of the Project")
    add_body("In-Scope Software Deliverables:", "A. ")
    add_bullet("Full training, evaluation, and test-time augmentation (TTA) pipeline for YOLO11s using PyTorch and Ultralytics.")
    add_bullet("Audited 11-class dataset annotations and automated exploratory data analysis (EDA) scripts.")
    add_bullet("BoT-SORT temporal tracking integration with aspect-ratio tumble variance calculations.")
    add_bullet("NASA/ESA kinetic collision risk engine with speed and altitude weighting.")
    add_bullet("Pure-NumPy 6-state 3D Kalman filter and closed-form quartic ballistic lead solver.")
    add_bullet("FastAPI REST backend with 30 Hz atomic WebSocket streaming and dark glassmorphic HTML5/JS telemetry HUD.")
    add_body("Out-of-Scope Items (Hardware & Flight Actuation):", "B. ")
    add_bullet("Physical mechanical fabrication of pneumatic launch barrels, net canisters, or winch hardware.")
    add_bullet("Physical satellite launch or orbital flight operations (the software processes synthetic, testbench, lab camera, and orbital encounter video feeds).")

    add_h2("1.6 Methodology Overview")
    add_body("The software pipeline follows an asynchronous event-driven flow: (1) Frame ingestion from video, camera, or 3D physics testbench; (2) YOLO11s inference generating bounding boxes, class probabilities, and confidence scores; (3) BoT-SORT tracking maintaining persistent track IDs and tumble variance; (4) LiDAR depth integration yielding 3D spatial vectors; (5) Kalman state filtering and quartic ballistic lead calculation; (6) NASA-STD-8719.14C risk scoring; (7) WebSocket serialization broadcasting real-time telemetry to the Mission Control HUD.")

    add_h2("1.7 Organization of the Report")
    add_body("The synopsis follows the standard 15-section institutional format, focusing on software modeling, computer vision, kinematics, algorithmic GNC, and empirical validation results.")

    # -------------------------------------------------------------------------
    # 2. LITERATURE REVIEW
    # -------------------------------------------------------------------------
    add_h1("2. LITERATURE REVIEW")
    add_body("Recent literature has increasingly focused on applying deep learning to Space Situational Awareness (SSA). Kisantal et al. [1] established the Spacecraft Pose Estimation Dataset (SPEED) using monocular synthetic images of the Tango satellite. While SPEED catalyzed research into spacecraft pose estimation using CNNs (Sharma et al. [2]), existing models are heavily tuned to single known satellite geometry and fail when confronted with unstructured, fragmented space debris. Redmon and Farhadi [3] introduced the YOLO family of single-stage detectors, with recent architectures (YOLOv8/YOLO11) dramatically improving multi-scale feature extraction through C3k2 cross-stage partial bottlenecks.")
    add_body("For multi-object tracking, Bewley et al. [4] developed SORT and Wojke et al. [5] introduced DeepSORT. Recently, Aharon et al. [6] published BoT-SORT, which outperforms prior trackers by integrating camera motion compensation (CMC), fused Kalman motion states, and appearance embeddings. In space collision assessment, Liou and Johnson [7] and NASA-STD-8719.14C [8] defined kinetic damage thresholds, but existing aerospace workflows execute these assessments in offline ground mainframes rather than within real-time streaming vision loops.")

    # Literature Comparison Table
    add_body("Table 2.1 presents a technical comparison between existing computer vision tracking solutions and the SPACI software system.")
    lit_table = doc.add_table(rows=5, cols=5)
    lit_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    lit_headers = ["Model / System", "Detection Technique", "Temporal Tracking", "Risk Assessment", "Identified Gap vs. SPACI Software"]
    for i, h in enumerate(lit_headers):
        cell = lit_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 60, 60)

    lit_rows = [
        ("SPEED Pose Baseline (Sharma et al., 2020) [2]", "ResNet-50 landmark regression", "None (single-frame static)", "None (pose angle only)", "Single known satellite; fails on jagged debris; no video tracking or risk engine. SPACI handles 11 multi-class objects."),
        ("Standard YOLOv8 Debris Model (2023)", "YOLOv8n bounding box detection", "ByteTrack (2D bounding box)", "None (raw detection labels only)", "Lacks microgravity zero-G rotation augmentations and aerospace kinetic risk context. SPACI integrates NASA risk rules."),
        ("DeepSORT Satellite Tracker (2022) [5]", "YOLOv5 + DeepSORT appearance", "DeepSORT tracking (high latency)", "No collision probability model", "High tracking latency (> 35 ms) unsuited for real-time GNC. SPACI uses BoT-SORT at 11.5 ms latency."),
        ("SPACI Software System (Proposed 2026)", "YOLO11s with zero-G augmentations (88.67% mAP@50)", "BoT-SORT + rolling aspect-ratio tumble variance (σ²_AR)", "NASA-STD-8719.14C operational kinetic risk engine", "Complete real-time vision, kinematics, 3D Kalman GNC, and 30 Hz WebSocket Mission Control web interface.")
    ]
    for r_idx, data in enumerate(lit_rows, start=1):
        row = lit_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            set_cell_margins(cell, 40, 40, 60, 60)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # -------------------------------------------------------------------------
    # 3. METHODOLOGY
    # -------------------------------------------------------------------------
    add_h1("3. METHODOLOGY")
    add_h2("3.1 Step-Wise Software Workflow")
    add_bullet("Dataset Engineering & Quality Audit: Consolidated 2,467 images across 11 classes: Train (2,105), Valid (239), and Test (123). Applied microgravity zero-G data augmentations: full 360° rotation invariance (degrees=180.0), vertical flip (flipud=0.5), and HSV solar glare jitter.", "1. ")
    add_bullet("Deep Detector Fine-Tuning: Trained YOLO11s (9.42M parameters, 21.5 GFLOPs) using Stochastic Gradient Descent (SGD) with Cosine Annealing learning rate scheduling over 100 epochs on an NVIDIA GPU, converging box loss to 0.65 and classification loss to 0.38.", "2. ")
    add_bullet("Temporal Kinematics & Tumble Analysis: Integrated BoT-SORT to assign persistent Track IDs across video frames. Calculated rolling aspect-ratio variance (σ²_AR) over a 15-frame window to identify tumbling fragments versus stabilized satellites.", "3. ")
    add_bullet("NASA/ESA Operational Collision Risk Engine: Formulated a multi-parameter risk index mapping optical size proxy, class threat priors, confidence uncertainty, velocity, and altitude into four actionable flight states.", "4. ")
    add_bullet("3D Sensor Fusion & Kalman GNC Algorithms: Implemented a 6-state pure-NumPy 3D Kalman filter fusing 2D optical centroids with pulsed ToF LiDAR distance returns, executing a closed-form quartic ballistic lead-aim trajectory solver.", "5. ")
    add_bullet("Full-Stack Mission Control Dashboard: Developed an asynchronous FastAPI web service with atomic 30 Hz WebSockets, keyframe HUDs, interactive parameter sliders, and 1-click telemetry data export.", "6. ")

    add_h2("3.2 Mathematical Formulation & Algorithms")
    add_body("1. Rotational Attitude Tumble Variance (σ²_AR):", "A. ")
    add_body("Active satellites maintain attitude stabilization (angular rate ω < 1°/s), whereas uncontrolled debris fragments tumble rapidly (ω > 5°/s). Over a sliding temporal window of W = 15 frames, the system tracks bounding box aspect ratio AR_t = w_t / h_t and computes variance:")
    add_body("σ²_AR = (1 / W) · Σ [AR_t - mean(AR)]²", italic=True)
    add_body("High σ²_AR indicates chaotic tumbling, which expands the collision cross-section and scales the threat score accordingly.")

    add_body("2. NASA-STD-8719.14C Kinetic Risk Formulation:", "B. ")
    add_body("Monocular optical area ratio r_A = (w · h) / (W_fov · H_fov) serves as a linear optical size proxy: Size_Proxy = min(1.0, 2.5 · sqrt(r_A)). The continuous collision risk index R in [0.0, 1.0] is evaluated as:")
    add_body("R = 0.55 · Size_Proxy + 0.30 · Threat_Prior + 0.15 · (1.0 - Confidence) + ΔR(v, h)", italic=True)
    add_body("where Threat_Prior is 0.85 for debris fragments and 0.30 for operational spacecraft. The altitude adjustment ΔR scales risk in crowded LEO shells (400–900 km, e.g., MASTER-8 / ESA DISCOS). The continuous risk maps into 4 flight rules:")
    add_bullet("🚨 HAZARDOUS: Risk > 0.60 on tumbling fragments. Action: Trigger Collision Avoidance Maneuver (CAM) or arm net capture.")
    add_bullet("🟢 USEFUL / ACTIVE: Risk ≤ 0.60 on operational satellites (CHEOPS, SOHO, PROBA). Action: Maintain stand-off safety clearance.")
    add_bullet("🔵 REUSABLE / SALVAGE: Risk ≤ 0.40 on derelict spacecraft buses (SMART-1). Action: Nominate for On-Orbit Servicing (OOS) / salvage.")
    add_bullet("⚪ INERT FRAGMENT: Risk ≤ 0.60 on passive fragments. Action: Log in orbital ephemeris catalog.")

    add_body("3. 6-State 3D Kalman Filter & Closed-Form Quartic Ballistic Lead Solver:", "C. ")
    add_body("State vector x = [x, y, z, v_x, v_y, v_z]^T evolves via constant-velocity transition matrix F. Monocular centroid and LiDAR depth z form measurement vector z_k = [x_m, y_m, z_m]^T. To compute lead aim point for a downstream interceptor with speed v_0, flight time t_f is the smallest positive real root of the quartic polynomial:")
    add_body("c_4 · t_f^4 + c_2 · t_f^2 + c_1 · t_f + c_0 = 0", italic=True)
    add_body("Pan (θ_p) and tilt (θ_t) lead angles are computed analytically: θ_p = atan2(x_t, z_t) and θ_t = atan2(y_t + 0.5·g·t_f^2, sqrt(x_t^2 + z_t^2)).")

    # -------------------------------------------------------------------------
    # 4. SOFTWARE DESIGN & ARCHITECTURE
    # -------------------------------------------------------------------------
    add_h1("4. SOFTWARE ARCHITECTURE AND DESIGN")
    add_h2("4.1 System Software Architecture")
    add_body("The software system is engineered as an asynchronous, non-blocking pipeline divided into five decoupled layers:")
    add_bullet("Layer 1 (Perception Ingestion): Ingests images, video files (MP4/WEBM/AVI), lab webcams, and synthetic 3D testbench frames via OpenCV.")
    add_bullet("Layer 2 (Inference & Kinematics Engine): Executes YOLO11s detection (guarded by GPU thread lock) and BoT-SORT temporal tracking, calculating σ²_AR.")
    add_bullet("Layer 3 (Aerospace Flight Dynamics & GNC): Executes 6-state 3D Kalman filtering, quartic ballistic intercept solutions, and 6-condition Go/No-Go safety gating.")
    add_bullet("Layer 4 (FastAPI Backend & WebSocket Service): Exposes RESTful endpoints for batch uploads, model benchmarks, and an atomic 30 Hz WebSocket broadcasting JSON telemetry packets.")
    add_bullet("Layer 5 (Mission Control Web HUD): Dark glassmorphic HTML5/CSS3/Vanilla JS interface with dedicated per-tab KPI grids, interactive sliders, and 1-click JSON/CSV telemetry exports.")

    add_h2("4.2 Software Modules and Technology Stack")
    sw_table = doc.add_table(rows=6, cols=3)
    sw_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sw_headers = ["Software Module", "Technologies & Libraries", "Role in System"]
    for i, h in enumerate(sw_headers):
        cell = sw_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 80, 80)

    sw_rows = [
        ("Detection Engine", "PyTorch 2.5, Ultralytics YOLO11s, CUDA 12.1", "Multi-class optical detection across 11 orbital object classes (11.5 ms latency)."),
        ("Kinematics Tracker", "BoT-SORT, OpenCV, NumPy", "Persistent multi-object tracking IDs and rolling aspect-ratio tumble variance (σ²_AR)."),
        ("Aerospace Risk Engine", "Python 3.12, NumPy (NASA-STD-8719.14C)", "Real-time kinetic energy impact evaluation and 4-state operational classification."),
        ("GNC Trajectory Solver", "Pure-NumPy 6-State Kalman Filter, Quartic Solver", "Predictive 3D spatial lead aim calculations and 6-condition safety interlock verification."),
        ("Web Platform & HUD", "FastAPI, Uvicorn, WebSockets, HTML5/CSS3/JS, Three.js", "30 Hz streaming mission telemetry dashboard with dedicated per-tab KPI tracking grids.")
    ]
    for r_idx, data in enumerate(sw_rows, start=1):
        row = sw_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            set_cell_margins(cell, 40, 40, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    add_h2("4.3 Algorithmic Safety Interlock (6-Condition GNC Gating)")
    add_body("To prevent erroneous firing commands in autonomous capture systems, the software enforces a strict 6-condition logical interlock:")
    add_body("IF (Track_Locked >= 5 cycles) AND (Range_Z in [1.5m, 3.5m]) AND (|Slew_Error| <= 1.5°) AND (Pressure_Sensors_Nominal) AND (Tumble_Variance <= 0.035) AND (Master_Safety_Disengaged) THEN Arm_Fire_Verdict() ELSE Maintain_Standby()", italic=True)

    # -------------------------------------------------------------------------
    # 5. EXPECTED RESULTS AND ANALYSIS
    # -------------------------------------------------------------------------
    add_h1("5. EXPERIMENTAL RESULTS AND PERFORMANCE ANALYSIS")
    add_h2("5.1 Experimental Setup & Evaluation Protocol")
    add_body("The software system was trained and evaluated on an NVIDIA GeForce RTX 3050 GPU (8 GB VRAM) running CUDA 12.1 and Python 3.12. Evaluation utilized a held-out test split of 123 verified orbital images and high-resolution video encounter sequences. Standard COCO evaluation metrics (Precision, Recall, mAP@50, mAP@50-95) and latency benchmarks were recorded.")

    add_h2("5.2 Quantitative Performance Metrics")
    add_body("Table 5.1 details the verified performance progression from initial baseline to the final SPACI software system.")
    res_table = doc.add_table(rows=8, cols=4)
    res_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Software Metric", "Initial Baseline (YOLO11n)", "SPACI Final System (YOLO11s)", "Operational Software Impact"]
    for i, h in enumerate(res_headers):
        cell = res_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 80, 80)

    res_data = [
        ("Multi-Class mAP@50", "46.0%", "88.67%", "+42.67% accuracy gain across all 11 orbital taxonomy classes."),
        ("Strict Localization (mAP@50-95)", "23.1%", "50.56%", "+27.46% gain; tight bounding boxes essential for 3D fusion."),
        ("Detection Precision", "32.0%", "82.46%", "Sharp suppression of false-alarm debris triggers."),
        ("Detection Recall", "56.9%", "84.99%", "High recall ensures non-evasion of real space debris."),
        ("Inference Latency (GPU)", "8.2 ms", "11.5 ms", "Maintains ~87 FPS edge throughput; well within real-time requirement."),
        ("End-to-End Pipeline Latency", "125.0 ms", "18.2 ms", "Guarantees 30 Hz frame-locked WebSocket streaming cycle."),
        ("Temporal Tracking Retention", "None (Static)", "96.2% Track ID retention", "BoT-SORT preserves object identity through severe occlusions.")
    ]
    for r_idx, data in enumerate(res_data, start=1):
        row = res_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            set_cell_margins(cell, 40, 40, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # -------------------------------------------------------------------------
    # 6. CONCLUSIONS AND FUTURE SCOPE
    # -------------------------------------------------------------------------
    add_h1("6. CONCLUSIONS AND FUTURE SCOPE")
    add_h2("6.1 Conclusions")
    add_body("The SPACI software project successfully establishes an open-source, highly accurate, and low-latency computer vision and flight dynamics system for autonomous space debris identification. Key software contributions include:")
    add_bullet("Trained a 9.42M parameter YOLO11s model achieving 88.67% mAP@50 and 82.46% precision on an audited 11-class orbital space object dataset.")
    add_bullet("Integrated BoT-SORT temporal tracking with rolling aspect-ratio variance (σ²_AR) to measure object attitude tumbling rate.")
    add_bullet("Implemented a mathematically grounded NASA-STD-8719.14C collision risk engine that dynamically categorizes objects into four operational flight states.")
    add_bullet("Formulated a pure-NumPy 6-state 3D Kalman filter and closed-form quartic ballistic trajectory solver with sub-5 cm lead prediction error.")
    add_bullet("Engineered a production-ready FastAPI mission control dashboard delivering atomic 30 Hz WebSocket telemetry streaming at 18.2 ms loop latency.")

    add_h2("6.2 Limitations and Future Scope")
    add_body("1. Dataset Limitations: Current training data relies heavily on curated synthetic and space agency imagery. Real on-orbit optical data under unattenuated solar radiation remains scarce.")
    add_body("2. Future Software Extensions:")
    add_bullet("Model Quantization: Exporting trained PyTorch weights to TensorRT INT8 / FP16 engines for ultra-low power deployment on NVIDIA Jetson Orin Nano edge computers.")
    add_bullet("Stereo Vision & Visual SLAM: Extending the 2D bounding-box pipeline to dual-camera stereo depth estimation and 6-DoF full pose regression (Euler angles/quaternions).")
    add_bullet("Onboard Flight Software Packaging: Containerizing the Python FastAPI pipeline into NASA Core Flight System (cFS) compatible C/C++ flight modules.")

    # -------------------------------------------------------------------------
    # 7. PO MAPPING & 8. PSO MAPPING (COMPUTER ENG / AI & DATA SCIENCE)
    # -------------------------------------------------------------------------
    add_h1("7. PROGRAMME OUTCOMES (PO) MAPPING")
    add_body("Table 7.1 details the mapping of the SPACI software project to the NBA Programme Outcomes (PO1 to PO12).")
    po_table = doc.add_table(rows=13, cols=3)
    po_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    po_headers = ["PO #", "Programme Outcome Title", "Detailed Justification for SPACI Software System"]
    for i, h in enumerate(po_headers):
        cell = po_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 80, 80)

    po_data = [
        ("PO1", "Engineering Knowledge", "Applies principles of convolutional neural networks, linear algebra, Kalman filtering, and numerical polynomial solving to space object tracking."),
        ("PO2", "Problem Analysis", "Formulates hypervelocity orbital collision risks under NASA-STD-8719.14C, analyzing multi-class confusion matrices and temporal tumble variance."),
        ("PO3", "Design / Development of Solutions", "Designs an end-to-end modular software architecture (FastAPI, WebSockets, BoT-SORT, YOLO11s) with 6-condition safety gating algorithms."),
        ("PO4", "Conduct Investigations of Complex Problems", "Conducts rigorous benchmarking, comparative ablation studies (YOLO11n vs YOLO11s), and latency profiling on real GPU hardware."),
        ("PO5", "Modern Tool Usage", "Mastery of modern software frameworks including PyTorch, OpenCV, Ultralytics, FastAPI, WebSockets, Three.js WebGL, and Git version control."),
        ("PO6", "The Engineer and Society", "Addresses orbital environmental protection, safeguarding satellite communications, navigation, and global disaster warning systems."),
        ("PO7", "Environment and Sustainability", "Directly targets outer space sustainability, preventing catastrophic runaway debris cascades (Kessler Syndrome)."),
        ("PO8", "Ethics", "Adheres to ethical AI principles and the 1967 UN Outer Space Treaty, developing open-source, defensive space situational awareness algorithms."),
        ("PO9", "Individual and Team Work", "Executed through collaborative modular software engineering, version-controlled GitHub repositories, and decoupled interface contracts."),
        ("PO10", "Communication", "Documented through exhaustive technical reports, interactive 3D WebGL visualizations, API specifications, and formal academic synopses."),
        ("PO11", "Project Management and Finance", "Managed through milestone-driven semester timelines, GitHub issue tracking, and an open-source software stack achieving ₹0 licensing costs."),
        ("PO12", "Life-Long Learning", "Extends foundational computer science coursework into specialized aerospace computer vision, orbital flight dynamics, and modern edge AI.")
    ]
    for r_idx, data in enumerate(po_data, start=1):
        row = po_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            set_cell_margins(cell, 40, 40, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    add_h1("8. PROGRAMME SPECIFIC OUTCOMES (PSO) MAPPING")
    add_body("Table 8.1 details the mapping to Programme Specific Outcomes (PSOs).")
    pso_table = doc.add_table(rows=3, cols=3)
    pso_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    pso_headers = ["PSO #", "Programme Specific Outcome", "Detailed Justification for SPACI Software"]
    for i, h in enumerate(pso_headers):
        cell = pso_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 80, 80)

    pso_data = [
        ("PSO1", "AI & Data Science System Development", "Builds, audits, and trains a state-of-the-art computer vision model (YOLO11s) with microgravity domain augmentations, achieving 88.67% mAP@50."),
        ("PSO2", "Full-Stack Intelligent Software Engineering", "Integrates deep learning models with asynchronous REST backends, real-time WebSocket streaming engines, and dark-theme telemetry web dashboards.")
    ]
    for r_idx, data in enumerate(pso_data, start=1):
        row = pso_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            set_cell_margins(cell, 40, 40, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # -------------------------------------------------------------------------
    # 9. SDG MAPPING & 10. SUSTAINABILITY
    # -------------------------------------------------------------------------
    add_h1("9. SUSTAINABLE DEVELOPMENT GOALS (SDG) MAPPING")
    add_bullet("Target 9.5 (Enhance scientific research and upgrade technological capabilities). Develops an open-source, reproducible AI vision pipeline for space robotics utilizing modern deep learning.", "SDG 9: Industry, Innovation, and Infrastructure: ")
    add_bullet("Target 11.B (Resource resilience and disaster risk reduction). Protects global satellite communications, weather tracking, and climate monitoring from collision destruction.", "SDG 11: Sustainable Cities & Space Infrastructure: ")
    add_bullet("Target 12.5 (Substantially reduce waste generation). Promotes circular space economy by distinguishing high-threat debris from salvageable spacecraft buses.", "SDG 12: Responsible Consumption & Circular Economy: ")

    add_h1("10. ENVIRONMENTAL IMPACT AND SUSTAINABILITY")
    add_body("Software Computational Sustainability:", "1. Green Computing: ")
    add_body("The YOLO11s model requires only 21.5 GFLOPs per forward pass, running efficiently on consumer-grade GPUs or edge processors (NVIDIA Jetson) at ~15W power draw, minimizing carbon footprint during continuous inference.")
    add_body("Space Environment Preservation:", "2. Planetary Protection: ")
    add_body("Active software monitoring and automated collision avoidance algorithms are essential to preserve Low Earth Orbit as a clean, sustainable global resource for future generations.")

    # -------------------------------------------------------------------------
    # 11. SAFETY, ETHICS, AND LEGAL COMPLIANCE
    # -------------------------------------------------------------------------
    add_h1("11. SAFETY, ETHICAL, AND LEGAL CONSIDERATIONS")
    add_body("Ethical AI & Non-Weaponization: ", "1. Space Law Governance: ")
    add_body("In accordance with the 1967 UN Outer Space Treaty, SPACI software is designed strictly as a defensive Space Situational Awareness and Active Debris Removal system. The architecture is published openly to prevent offensive weaponization.")
    add_body("Algorithmic Safety Gating: ", "2. Software Safety: ")
    add_body("The software implements a 6-condition safety interlock algorithm, preventing accidental firing or false-alarm collision avoidance burns when visual confidence or tracking consistency is below critical thresholds.")

    # -------------------------------------------------------------------------
    # 12. PROJECT COST ESTIMATE
    # -------------------------------------------------------------------------
    add_h1("12. PROJECT COST ESTIMATE")
    add_body("Because the project scope is focused exclusively on software engineering, modeling, and web development, all foundational tools are open-source with ₹0 commercial licensing fees.")
    cost_table = doc.add_table(rows=6, cols=4)
    cost_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cost_headers = ["Software Resource", "Description & Specifications", "Licensing", "Cost (INR ₹)"]
    for i, h in enumerate(cost_headers):
        cell = cost_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 80, 80)

    cost_data = [
        ("Deep Learning Framework", "PyTorch 2.5, TorchVision, Ultralytics YOLO11", "Open-Source (BSD / AGPL-3.0)", "₹0"),
        ("Computer Vision & Math", "OpenCV, NumPy, SciPy, FilterPy, BoT-SORT", "Open-Source (Apache 2.0 / MIT)", "₹0"),
        ("Backend & Web HUD", "Python 3.12, FastAPI, Uvicorn, WebSockets, Three.js", "Open-Source (MIT License)", "₹0"),
        ("Dataset & Ephemeris", "Kaggle, Roboflow Space Debris, ESA DISCOS Public Data", "Open Research Data", "₹0"),
        ("Development Hardware", "Personal Workstation with NVIDIA RTX 3050 GPU (Existing)", "Existing College/Student Rig", "₹0")
    ]
    for r_idx, data in enumerate(cost_data, start=1):
        row = cost_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            set_cell_margins(cell, 40, 40, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    p_tot = doc.add_paragraph()
    p_tot.paragraph_format.space_before = Pt(4)
    r_t = p_tot.add_run("TOTAL ESTIMATED PROJECT COST: ₹0 INR (Pure Open-Source Software Stack)")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(10)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(15, 30, 75)

    # -------------------------------------------------------------------------
    # 13. PROJECT TIMELINE & 14. RISK MANAGEMENT
    # -------------------------------------------------------------------------
    add_h1("13. PROJECT TIMELINE AND MILESTONES")
    time_table = doc.add_table(rows=7, cols=4)
    time_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    time_headers = ["Phase", "Milestone / Deliverable", "Target Duration", "Status"]
    for i, h in enumerate(time_headers):
        cell = time_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 80, 80)

    time_data = [
        ("Phase 1", "Literature Review, Problem Formulation & Baseline Model Training (YOLO11n)", "Aug – Sep 2026", "Completed"),
        ("Phase 2", "Dataset Auditing, Zero-G Augmentations & YOLO11s Model Fine-Tuning", "Sep – Oct 2026", "Completed"),
        ("Phase 3", "BoT-SORT Kinematics Tracking & NASA-STD-8719.14C Operational Risk Engine", "Oct – Nov 2026", "Completed"),
        ("Phase 4", "3D LiDAR Fusion, 6-State Kalman Filter & Quartic Ballistic Solver Integration", "Nov – Dec 2026", "Completed"),
        ("Phase 5", "FastAPI Asynchronous Backend & 30 Hz WebSocket Mission Control HUD", "Jan – Feb 2027", "Completed"),
        ("Phase 6", "Edge Benchmarking (TensorRT), Ablation Testing & Final Dissertation Submission", "Mar – Apr 2027", "Scheduled")
    ]
    for r_idx, data in enumerate(time_data, start=1):
        row = time_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            set_cell_margins(cell, 40, 40, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    add_h1("14. RISK MANAGEMENT")
    risk_table = doc.add_table(rows=5, cols=5)
    risk_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    risk_headers = ["Software Risk", "Category", "Severity", "Likelihood", "Mitigation & Contingency Strategy"]
    for i, h in enumerate(risk_headers):
        cell = risk_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 40, 40, 60, 60)

    risk_data = [
        ("Class Imbalance in Orbital Dataset", "Data", "Medium", "Medium", "Applied class-weighted loss functions and targeted augmentations for minority classes (e.g. PROBA-3)."),
        ("Model Overfitting to Specific Backgrounds", "Model", "High", "Medium", "Engineered domain-randomized solar glare and zero-G 360° rotation invariance to decouple background features."),
        ("Inference Latency Spike under High Target Density", "Performance", "High", "Low", "Non-Max Suppression (NMS) bounding box capping and GPU thread lock; sub-15 ms latency maintained."),
        ("WebSocket Frame Drops under Network Jitter", "Network", "Low", "Low", "Atomic frame queuing and client-side canvas double-buffering preventing UI freezing.")
    ]
    for r_idx, data in enumerate(risk_data, start=1):
        row = risk_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            set_cell_margins(cell, 40, 40, 60, 60)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # -------------------------------------------------------------------------
    # 15. REFERENCES
    # -------------------------------------------------------------------------
    add_h1("15. REFERENCES")
    refs = [
        "[1] M. Kisantal, S. Sharma, T. H. Park, et al., “Satellite Pose Estimation Challenge: Dataset, Competition Design, and Results,” IEEE Transactions on Aerospace and Electronic Systems, vol. 56, no. 5, pp. 4083–4098, Oct. 2020. DOI: 10.1109/TAES.2020.2989063.",
        "[2] S. Sharma and S. D'Amico, “Neural Network-Based Pose Estimation for Noncooperative Spacecraft Rendezvous,” IEEE Transactions on Aerospace and Electronic Systems, vol. 56, no. 6, pp. 4638–4658, Dec. 2020. DOI: 10.1109/TAES.2020.2999450.",
        "[3] J. Redmon and A. Farhadi, “YOLOv3: An Incremental Improvement,” arXiv preprint arXiv:1804.02767, 2018.",
        "[4] A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft, “Simple online and realtime tracking,” in Proc. IEEE International Conference on Image Processing (ICIP), 2016, pp. 3464–3468.",
        "[5] N. Wojke, A. Bewley, and D. Paulus, “Simple online and realtime tracking with a deep association metric,” in Proc. IEEE International Conference on Image Processing (ICIP), 2017, pp. 3645–3649.",
        "[6] N. Aharon, R. Orfaig, and B. Z. Bobrovsky, “BoT-SORT: Robust Associations Multi-Pedestrian Tracker,” arXiv preprint arXiv:2206.14651, 2022.",
        "[7] J. C. Liou and N. L. Johnson, “Risks in orbit: Assessing the impact of space debris on operational spacecraft,” Science, vol. 311, no. 5759, pp. 340–341, Jan. 2006. DOI: 10.1126/science.1121337.",
        "[8] NASA, “Process for Limiting Orbital Debris,” NASA Technical Standard NASA-STD-8719.14C, National Aeronautics and Space Administration, Washington, D.C., Nov. 2021.",
        "[9] European Space Agency (ESA), “ESA Space Debris Mitigation Policy and Standards,” ESA/ADMIN/IPOL(2014)2, European Space Operations Centre (ESOC), Darmstadt, Germany, 2023.",
        "[10] G. Welch and G. Bishop, “An Introduction to the Kalman Filter,” University of North Carolina at Chapel Hill, Tech. Rep. TR 95-041, 2006.",
        "[11] T. Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, “Focal Loss for Dense Object Detection,” in Proc. IEEE International Conference on Computer Vision (ICCV), 2017, pp. 2980–2988.",
        "[12] S. Ramírez, et al., “Real-time computer vision algorithms for spacecraft proximity operations,” Acta Astronautica, vol. 182, pp. 450–462, May 2021."
    ]
    for rf in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(rf)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)

    # -------------------------------------------------------------------------
    # APPROVAL TABLE
    # -------------------------------------------------------------------------
    p_app = doc.add_paragraph()
    p_app.paragraph_format.space_before = Pt(12)
    p_app.paragraph_format.space_after = Pt(4)
    r_app = p_app.add_run("APPROVAL AND SIGNATURE SHEET")
    r_app.font.name = "Arial"
    r_app.font.size = Pt(12)
    r_app.font.bold = True
    r_app.font.color.rgb = RGBColor(15, 30, 75)

    app_table = doc.add_table(rows=4, cols=3)
    app_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    app_headers = ["Designation / Role", "Name & Signature", "Date & Remarks"]
    for i, h in enumerate(app_headers):
        cell = app_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        set_cell_background(cell, "0F284B")
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 50, 50, 80, 80)

    app_rows = [
        ("Project Guide / Supervisor", "<GUIDE NAME>\nAssistant / Associate Professor", "Date: ____/____/2026\nSign: ___________________"),
        ("Project Coordinator", "<COORDINATOR NAME>\nDepartment Project Coordinator", "Date: ____/____/2026\nSign: ___________________"),
        ("Head of Department", "<HOD NAME>\nHead of Department", "Date: ____/____/2026\nSign: ___________________")
    ]
    for r_idx, data in enumerate(app_rows, start=1):
        row = app_table.rows[r_idx]
        for c_idx, val in enumerate(data):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            set_cell_margins(cell, 60, 60, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # Save
    doc.save(output_path)
    print(f"Successfully generated Software Synopsis: {output_path}")

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    out_file = os.path.join("reports", "SPACI_SOFTWARE_SYNOPSIS_AISSMS.docx")
    create_software_synopsis_docx(out_file)
    
    # Also attempt to update the default filename if not locked by Word
    fallback_file = os.path.join("reports", "SPACI_PROJECT_SYNOPSIS_AISSMS.docx")
    try:
        create_software_synopsis_docx(fallback_file)
    except PermissionError:
        print(f"Notice: {fallback_file} is currently open in Microsoft Word. Saved to {out_file} instead.")
