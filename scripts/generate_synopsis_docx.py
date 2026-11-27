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


def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_page_number_to_run(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def create_official_synopsis_docx(output_path):
    doc = docx.Document()

    # Exact AISSMS IOIT Template Page Geometry: US Letter (8.5" x 11.0"), Top/Bot 0.70", Left/Right 0.85"
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.top_margin = Inches(0.70)
        section.bottom_margin = Inches(0.70)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        section.different_first_page_header_footer = True

        # Subsequent pages header & footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("AISSMS IOIT, PUNE  |  B.TECH PROJECT SYNOPSIS (2026–27)")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(100, 116, 139)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        fr1 = fp.add_run("SPACI: Space Debris Verification, Salvage & Risk Assessment Software   |   Page ")
        fr1.font.name = "Calibri"
        fr1.font.size = Pt(8.5)
        fr1.font.color.rgb = RGBColor(100, 116, 139)
        fr_pg = fp.add_run()
        fr_pg.font.name = "Calibri"
        fr_pg.font.size = Pt(8.5)
        fr_pg.font.color.rgb = RGBColor(100, 116, 139)
        add_page_number_to_run(fr_pg)

    # Base Normal style matching official template (Calibri 11pt)
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(25, 25, 25)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------------------
    # PAGE 1: OFFICIAL AISSMS IOIT COVER PAGE
    # -------------------------------------------------------------------------
    banner_path = os.path.join("reports", "figures", "template_media", "word", "media", "image1.jpeg")
    if os.path.exists(banner_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(0)
        p_img.paragraph_format.space_after = Pt(8)
        p_img.add_run().add_picture(banner_path, width=Inches(6.75))
    else:
        p_inst = doc.add_paragraph()
        p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_inst = p_inst.add_run("AISSMS INSTITUTE OF INFORMATION TECHNOLOGY, PUNE\n")
        r_inst.font.size = Pt(15)
        r_inst.font.bold = True

    def add_cover_line(text, size=12, bold=True, color=(15, 30, 75), space_before=2, space_after=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(size)
        r.font.bold = bold
        if color:
            r.font.color.rgb = RGBColor(*color)
        return p

    add_cover_line("PROJECT SYNOPSIS", size=16, bold=True, color=(0, 0, 0), space_before=6, space_after=4)
    add_cover_line("FOR BACHELOR OF TECHNOLOGY", size=13, bold=True, color=(0, 0, 0), space_before=2, space_after=2)
    add_cover_line("IN", size=11, bold=True, color=(0, 0, 0), space_before=2, space_after=2)
    add_cover_line("COMPUTER ENGINEERING", size=13, bold=True, color=(0, 0, 0), space_before=2, space_after=10)

    add_cover_line(
        "SPACI: AI-DRIVEN SPACE DEBRIS VERIFICATION, SALVAGEABLE ELEMENT DETECTION, AND SAFE CAPTURE RISK ASSESSMENT SOFTWARE SYSTEM",
        size=14.5, bold=True, color=(0, 111, 192), space_before=6, space_after=6
    )
    add_cover_line(
        "(SDG #9 – Industry, Innovation & Infrastructure  |  SDG #11 – Sustainable Outer Space  |  SDG #12 – Circular Space Economy)",
        size=11.5, bold=True, color=(192, 0, 0), space_before=2, space_after=12
    )

    add_cover_line("SUBMITTED TO AISSMS INSTITUTE OF INFORMATION TECHNOLOGY, PUNE", size=11, bold=True, color=(0, 0, 0), space_before=4, space_after=2)
    add_cover_line("IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE AWARD OF THE DEGREE OF", size=10.5, bold=True, color=(0, 0, 0), space_before=2, space_after=2)
    add_cover_line("BACHELOR OF TECHNOLOGY", size=13, bold=True, color=(0, 0, 0), space_before=2, space_after=2)
    add_cover_line("IN", size=11, bold=True, color=(0, 0, 0), space_before=2, space_after=2)
    add_cover_line("COMPUTER ENGINEERING", size=13, bold=True, color=(0, 0, 0), space_before=2, space_after=10)

    # Exact Cover Student Table (4x2 as in Official Template)
    cov_stu = doc.add_table(rows=4, cols=2)
    cov_stu.alignment = WD_TABLE_ALIGNMENT.CENTER
    cov_stu.autofit = False
    set_table_borders(cov_stu, color="475569", sz="6")

    stu_cover_data = [
        ("Student Name", "Seat / PRN No."),
        ("Deep Ravindra Kale", "PRN: 72312016B / Seat No: <Seat No 1>"),
        ("<Student Name 2>", "PRN: <PRN No 2> / Seat No: <Seat No 2>"),
        ("<Student Name 3>", "PRN: <PRN No 3> / Seat No: <Seat No 3>"),
    ]
    for r_idx, (col1, col2) in enumerate(stu_cover_data):
        row = cov_stu.rows[r_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(3.2)
        c1.width = Inches(3.2)
        for c, txt in ((c0, col1), (c1, col2)):
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(txt)
            r.font.name = "Calibri"
            r.font.size = Pt(11)
            r.font.bold = (r_idx == 0)
            set_cell_margins(c, 70, 70, 100, 100)
            if r_idx == 0:
                set_cell_background(c, "E2E8F0")

    add_cover_line("UNDER THE GUIDANCE OF", size=11, bold=True, color=(0, 0, 0), space_before=16, space_after=2)
    add_cover_line("<GUIDE NAME>", size=12, bold=True, color=(15, 30, 75), space_before=2, space_after=2)
    add_cover_line("Department of Computer Engineering, AISSMS IOIT, Pune", size=10.5, bold=False, color=(60, 60, 60), space_before=0, space_after=10)
    add_cover_line("ACADEMIC YEAR: 2026–27", size=11.5, bold=True, color=(0, 0, 0), space_before=6, space_after=4)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # HELPER FUNCTIONS FOR BODY SECTIONS
    # -------------------------------------------------------------------------
    def add_h1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 30, 75)
        return p

    def add_h2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 111, 192)
        return p

    def add_body(text, bold_prefix=None, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Calibri"
            rb.font.size = Pt(11)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.italic = italic
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Calibri"
            rb.font.size = Pt(11)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        return p

    def add_figure(img_path, caption, width_in=6.2):
        if not os.path.exists(img_path):
            add_body(f"[Placeholder for missing figure: {img_path}]", italic=True)
            return
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.keep_with_next = True
        p_img.add_run().add_picture(img_path, width=Inches(width_in))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run(caption)
        rc.font.name = "Calibri"
        rc.font.size = Pt(9.5)
        rc.font.bold = True
        rc.font.italic = True
        rc.font.color.rgb = RGBColor(51, 65, 85)

    def make_styled_table(headers, rows_data, col_widths=None, font_size=9.5):
        tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        set_table_borders(tbl, color="94A3B8", sz="4")
        for i, h in enumerate(headers):
            cell = tbl.rows[0].cells[i]
            if col_widths:
                cell.width = Inches(col_widths[i])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(h)
            r.font.name = "Calibri"
            r.font.size = Pt(font_size)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(cell, "0F284B")
            set_cell_margins(cell, 55, 55, 80, 80)

        for r_idx, r_data in enumerate(rows_data, start=1):
            row = tbl.rows[r_idx]
            for c_idx, val in enumerate(r_data):
                cell = row.cells[c_idx]
                if col_widths:
                    cell.width = Inches(col_widths[c_idx])
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                r = p.add_run(str(val))
                r.font.name = "Calibri"
                r.font.size = Pt(font_size)
                if c_idx == 0:
                    r.font.bold = True
                set_cell_margins(cell, 50, 50, 80, 80)
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return tbl

    # -------------------------------------------------------------------------
    # PAGE 2: SYNOPSIS METADATA BLOCK (EXACT TEMPLATE HEADER)
    # -------------------------------------------------------------------------
    p_syn_hdr = doc.add_paragraph()
    p_syn_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_syn_hdr.paragraph_format.space_after = Pt(6)
    r_sh = p_syn_hdr.add_run("PROJECT SYNOPSIS")
    r_sh.font.name = "Calibri"
    r_sh.font.size = Pt(15)
    r_sh.font.bold = True
    r_sh.font.color.rgb = RGBColor(15, 30, 75)

    make_styled_table(
        ["Template Field", "Project Details"],
        [
            ("Project Title", "SPACI: AI-Driven Space Debris Verification, Salvageable Element Detection, and Safe Capture Risk Assessment Software System"),
            ("Project Type", "Software Product / Applied AI & Computer Vision Research / Real-Time Mission Control System"),
            ("Student Details", "1. Deep Ravindra Kale (PRN: 72312016B) | 2. <Student Name 2> | 3. <Student Name 3>\nProgramme: B.Tech (Computer Engineering) | Academic Year: 2026–27"),
            ("Guide / Supervisor", "<GUIDE NAME>, Assistant / Associate Professor, Dept. of Computer Engineering, AISSMS IOIT, Pune"),
            ("SDG Mapping", "SDG #9 – Industry, Innovation & Infrastructure (Target 9.5) | SDG #11 – Sustainable Cities & Space Infrastructure (Target 11.B) | SDG #12 – Circular Space Economy (Target 12.5)")
        ],
        col_widths=[1.8, 5.0],
        font_size=10
    )

    # -------------------------------------------------------------------------
    # 1. INTRODUCTION
    # -------------------------------------------------------------------------
    add_h1("1. INTRODUCTION")

    add_h2("1.1 Background of the Project")
    add_body(
        "Low Earth Orbit (LEO, 200–2,000 km altitude) faces severe orbital congestion caused by defunct spacecraft buses, "
        "spent upper rocket stages, and hypervelocity fragmentation debris. According to the European Space Agency (ESA) "
        "Space Debris Office DISCOS catalog, more than 47,000 tracked objects and an estimated 1.5 million lethal fragments "
        "(> 1 cm) orbit Earth at speeds of 7.5 to 10 km/s [7], [9]. Under NASA Technical Standard NASA-STD-8719.14C [8], "
        "any collision exceeding 40 Joules per gram triggers catastrophic fragmentation, accelerating the runaway Kessler Syndrome cascade. "
        "Modern Active Debris Removal (ADR) and On-Orbit Servicing (OOS) missions therefore require intelligent onboard vision and risk software "
        "capable of autonomously distinguishing real debris from operational satellites, identifying reusable components for circular recovery, "
        "and evaluating safe capture trajectories in real time."
    )

    add_h2("1.2 Problem Statement")
    add_body(
        "Conventional Space Situational Awareness (SSA) relies on ground-based radar and Two-Line Element (TLE) catalogs, which suffer from "
        "hours of latency, poor resolution for uncooperative tumbling fragments, and an inability to guide close-proximity capture maneuvers. "
        "During an orbital rendezvous, an autonomous software brain must simultaneously solve three tightly coupled problems: "
        "(1) Verify whether a detected target is real defunct space debris or an active, operational satellite; "
        "(2) Inspect confirmed debris for structurally intact, useful, or reusable elements (such as solar arrays, payload buses, or docking adapters) "
        "suitable for salvage rather than destructive deorbiting; and "
        "(3) Measure rotational tumble rate and 3D relative trajectory in real time to verify a safe capture window without endangering the chaser craft."
    )

    add_h2("1.3 Motivation / Need for the Project")
    add_bullet("Preventing Friendly-Fire & Unnecessary Maneuvers: Distinguishing operational satellites (e.g., CHEOPS, SOHO, PROBA) from defunct debris eliminates costly false-alarm propellant burns.", "1. Operational Asset Safety: ")
    add_bullet("Enabling Circular Space Economy: Detecting intact, salvageable structural components within confirmed debris enables targeted in-orbit recycling and servicing instead of blind destruction.", "2. Salvage & Reusability Intelligence: ")
    add_bullet("Closing the Real-Time Guidance Gap: Replacing sluggish script-rerun prototypes with an asynchronous FastAPI + 30 Hz WebSocket software architecture capable of sub-15 ms GPU inference and simultaneous risk/capture gating.", "3. Low-Latency Autonomous Software: ")

    add_h2("1.4 Objectives of the Project")
    add_bullet("To curate, audit, and augment an 11-class orbital space object imagery dataset (2,467 images) with zero-G 360-degree rotational invariance and solar glare jitter, verifying zero cross-split leakage.", "Objective 1 (Dataset Engineering & Domain Augmentation): ")
    add_bullet("To fine-tune a custom YOLO11s multi-class object detector that verifies Real Debris vs. Active Satellites and identifies intact salvageable buses, achieving mAP@50 >= 85.0% and inference latency <= 15 ms.", "Objective 2 (Debris Verification & Salvage Classification): ")
    add_bullet("To integrate BoT-SORT temporal multi-object tracking across video streams and compute rolling aspect-ratio variance (sigma^2_AR) over 15-frame windows to quantify rotational tumble intensity.", "Objective 3 (Kinematic Video Tracking & Tumble Analysis): ")
    add_bullet("To implement a NASA-STD-8719.14C collision risk engine categorizing every tracked target into four operational states (Hazardous Threat, Reusable/Salvageable, Useful/Active, Inert Fragment) alongside a 6-state 3D Kalman filter and quartic lead-aim capture solver.", "Objective 4 (Simultaneous Risk Scoring & Safe Capture Gating): ")
    add_bullet("To deploy a production-ready FastAPI + 30 Hz WebSocket Mission Control Web HUD featuring per-tab isolated KPI telemetry (Live, Video, Gallery, Telemetry), 3D Earth situational awareness, and 1-click CSV/JSON mission logs.", "Objective 5 (Real-Time Mission Control Web Platform): ")

    add_h2("1.5 Scope of the Project")
    add_body(
        "The project scope is defined strictly around the SOFTWARE, AI MODELING, DETECTION, KINEMATICS, AND WEB MISSION CONTROL SYSTEM:",
        bold_prefix="A. In-Scope Software Deliverables: "
    )
    add_bullet("Audited 11-class dataset curation, zero-G domain training, Test-Time Augmentation (TTA), and PyTorch/Ultralytics YOLO11s evaluation scripts.")
    add_bullet("Real-time 3-stage decision logic: Debris Verification -> Salvage/Reusability Tagging -> Simultaneous Safe Capture Envelope & Risk Assessment.")
    add_bullet("BoT-SORT tracking, 15-frame aspect-ratio tumble variance (sigma^2_AR), 6-state pure-NumPy 3D Kalman filter, MAD outlier rejection, and closed-form quartic ballistic lead solver.")
    add_bullet("FastAPI REST API, 30 Hz atomic WebSocket engine, SQLite mission logging, and HTML5/CSS3/Three.js Mission Control HUD.")
    add_body(
        "Physical fabrication of pneumatic net launchers, robotic arms, mechanical canisters, or actual orbital satellite flight launches are outside the scope of this project; capture hardware actuation is modeled cleanly via software GNC safety gates and simulated LiDAR/optical streams.",
        bold_prefix="B. Out-of-Scope Items (Hardware Fabrication): "
    )

    add_h2("1.6 Methodology Overview")
    add_body(
        "The pipeline follows a decoupled event-driven software architecture: (1) Frame ingestion from orbital encounter video, static imagery, or webcam optical feeds; "
        "(2) YOLO11s 11-class inference verifying debris vs. active assets and flagging intact salvageable structures; "
        "(3) BoT-SORT tracking computing persistent IDs and rolling tumble variance; "
        "(4) Simulated pulsed LiDAR fusion and 6-state Kalman GNC calculating lead-aim capture windows; "
        "(5) NASA-STD-8719.14C risk scoring; and (6) 30 Hz WebSocket telemetry streaming to the Mission Control Web HUD."
    )

    add_h2("1.7 Organization of the Proposed Work / Report")
    add_body(
        "The project documentation is structured systematically into: Chapter 1 (Introduction & Scope), Chapter 2 (Literature Survey), "
        "Chapter 3 (Software Requirement Specification & Methodology), Chapter 4 (System Architecture, DFD & UML Design), "
        "Chapter 5 (Implementation & Model Domain Training), Chapter 6 (Experimental Results, Benchmarking & HUD Testing), "
        "Chapter 7 (Conclusions, Costing & Future Scope), and IEEE References."
    )

    # -------------------------------------------------------------------------
    # 2. LITERATURE REVIEW
    # -------------------------------------------------------------------------
    add_h1("2. LITERATURE REVIEW")
    add_body(
        "Kisantal et al. [1] introduced the Spacecraft Pose Estimation Dataset (SPEED), establishing monocular vision benchmarks for non-cooperative rendezvous. "
        "Building on this, Sharma and D'Amico [2] proposed a ResNet-50 convolutional network for 6-DoF spacecraft pose estimation. "
        "While accurate on synthetic single-satellite geometry, their approach assumes a pre-known CAD target and fails on multi-class fragmented debris or salvage component sorting."
    )
    add_body(
        "In single-stage object detection, Redmon and Farhadi [3] pioneered YOLO architectures, and Lin et al. [11] introduced Focal Loss to combat severe class imbalance in dense detection tasks. "
        "Modern Ultralytics YOLO11s utilizes C3k2 cross-stage partial blocks and spatial pyramid pooling to deliver ultra-low latency detection suitable for spaceborne edge processors. "
        "For temporal tracking, Bewley et al. [4] introduced SORT and Wojke et al. [5] added deep appearance descriptors (DeepSORT), though high re-identification overhead (> 35 ms) limits real-time execution. "
        "Aharon et al. [6] overcame this in BoT-SORT by combining Camera Motion Compensation (CMC) with Kalman state estimation, making it ideal for orbital sensor drift."
    )
    add_body(
        "Regarding debris hazard evaluation, Liou and Johnson [7], NASA-STD-8719.14C [8], and ESA Mitigation Standards [9] define kinetic breakup thresholds (40 J/g) and orbital congestion shells (400–900 km), "
        "while Welch and Bishop [10] and Ramirez et al. [12] formulated Kalman filtering for proximity GNC operations. "
        "However, existing frameworks execute radar risk modeling offline and lack a unified real-time software bridge linking visual debris verification, reusable salvage classification, tumble kinematics, and capture gating."
    )

    add_body("Table 2.1 presents a technical comparison of key baseline systems versus the proposed SPACI software platform.")
    make_styled_table(
        ["Reference / System", "Detection & AI Model", "Tracking & Kinematics", "Salvage & Risk Capability", "Identified Gap Solved by SPACI"],
        [
            ("Kisantal et al. [1] / Sharma et al. [2]", "ResNet-50 CNN Pose Regression", "None (static single-frame)", "None (pose angles only)", "Restricted to single known satellite; no multi-class debris detection, salvage check, or risk engine."),
            ("Bewley et al. [4] / Wojke et al. [5]", "YOLOv5 + SORT / DeepSORT", "2D Kalman + Re-ID (>35 ms)", "None", "High appearance-matching latency; lacks rotational tumble variance (sigma^2_AR) estimation."),
            ("Aharon et al. [6] (BoT-SORT)", "Generic Detector + BoT-SORT", "CMC + Kalman motion fusion", "None (tracking IDs only)", "General terrestrial tracker; lacks zero-G 360-deg invariance and orbital kinetic rules."),
            ("NASA [8] / ESA [9] Standards", "Offline Radar / TLE Catalogs", "Multi-hour TLE ephemeris", "Kinetic energy threshold (40 J/g)", "Offline mainframe batch computation; cannot guide live visual rendezvous or capture."),
            ("SPACI System (Proposed 2026)", "YOLO11s Zero-G (88.67% mAP@50)", "BoT-SORT + 15-frame Tumble sigma^2_AR", "Friend-or-Foe + Salvage Tag + NASA Risk + 3D GNC", "Unifies verification, salvageability, tumble dynamics, capture GNC & 30 Hz Web HUD at 11.5 ms.")
        ],
        col_widths=[1.25, 1.35, 1.35, 1.35, 1.5],
        font_size=8.8
    )

    # -------------------------------------------------------------------------
    # 3. METHODOLOGY
    # -------------------------------------------------------------------------
    add_h1("3. METHODOLOGY")
    add_h2("3.1 Step-Wise Software Workflow (3-Stage Operational Pipeline)")
    add_bullet("Stage 1 — Debris vs. Active Verification (Friend-or-Foe): Optical frames (video, webcam, or static batches) are normalized to 640x640 RGB tensors and passed through YOLO11s (9.42M parameters) to verify whether a detected target is real defunct debris or an active operational satellite (e.g., CHEOPS, SOHO, PROBA-2/3).", "1. ")
    add_bullet("Stage 2 — Useful / Reusable Element Inspection: Confirmed debris objects are cross-evaluated against structural taxonomy profiles to determine if intact, serviceable components (spacecraft bus, solar panels, docking rings) are present, tagging them as REUSABLE / SALVAGE versus INERT FRAGMENT.", "2. ")
    add_bullet("Stage 3 — Simultaneous Tumble, Risk & Safe Capture Gating: Concurrently, BoT-SORT tracks persistent object IDs across frames and computes rolling aspect-ratio variance (sigma^2_AR = (1/W) * sum(AR_t - mean(AR))^2 over W=15 frames). The NASA-STD-8719.14C risk engine computes continuous risk R in [0, 1], while a 6-state 3D Kalman filter and quartic lead-aim solver evaluate whether the target falls within a stable, safe capture window.", "3. ")

    add_figure(
        os.path.join("reports", "figures", "synopsis_decision_flowchart.png"),
        "Fig. 3.1: SPACI End-to-End Methodology & 3-Stage Autonomous Debris Decision Flowchart",
        width_in=6.3
    )

    add_h2("3.2 Dataset Engineering, Experiments & Validation Approach")
    add_body(
        "The curated 11-class dataset comprises 2,467 annotated orbital images partitioned cleanly with zero hash overlap into Training (2,105 images), "
        "Validation (239 images), and Held-Out Testing (123 images). Domain-specific microgravity augmentations were engineered during training: "
        "full 360-degree planar rotation (degrees=180.0), vertical flips (flipud=0.5), HSV solar glare jitter, and mosaic scaling. "
        "Model validation tracks multi-class mAP@50, strict mAP@50-95, Precision, Recall, Test-Time Augmentation (TTA), and Monte Carlo 3D GNC intercept success across 1,000 simulated orbital trials."
    )

    add_h2("3.3 Tools & Software Resources")
    make_styled_table(
        ["Resource Category", "Selected Tools & Specifications", "Role in Project"],
        [
            ("AI & Deep Learning", "PyTorch 2.5, Ultralytics YOLO11s, CUDA 12.1, Albumentations", "Domain training, zero-G data augmentation, and 11-class inference."),
            ("Tracking & Flight Math", "BoT-SORT, OpenCV 4.x, NumPy, SciPy, FilterPy", "Multi-object video tracking, sigma^2_AR tumble variance, Kalman & quartic GNC."),
            ("Backend & Web HUD", "Python 3.12, FastAPI, Uvicorn, WebSockets, SQLite, Three.js", "REST endpoints, 30 Hz live telemetry streaming, and 3D Earth HUD."),
            ("Compute & Datasets", "NVIDIA RTX 3050 (8 GB VRAM) / Cloud GPU, ESA/SPARK/Kaggle Data", "GPU-accelerated training (100 epochs) and held-out optical validation.")
        ],
        col_widths=[1.6, 2.6, 2.6],
        font_size=9.2
    )

    # -------------------------------------------------------------------------
    # 4. HARDWARE / SOFTWARE DESIGN
    # -------------------------------------------------------------------------
    add_h1("4. HARDWARE / SOFTWARE DESIGN")
    add_h2("4.1 Application / System Block Diagram & Decoupled Layers")
    add_body(
        "SPACI employs a modular 5-layer software architecture: (1) Data & Sensor Ingestion (video files, image batches, webcam optical stream, and simulated pulsed ToF LiDAR returns); "
        "(2) AI Detection & Kinematics (YOLO11s + BoT-SORT + sigma^2_AR); (3) Salvage & NASA Risk Logic (Friend-or-Foe + Reusability + 4-state flight rules); "
        "(4) 3D GNC & Safety Gate (MAD outlier rejection + 6-state Kalman filter + quartic lead solver); and (5) FastAPI + 30 Hz WebSocket Mission Control HUD."
    )

    add_figure(
        os.path.join("reports", "figures", "synopsis_block_diagram.png"),
        "Fig. 4.1: SPACI Application & 5-Layer Software Architecture Block Diagram",
        width_in=6.5
    )

    add_h2("4.2 Data Flow & Object Interaction Diagrams")
    add_figure(
        os.path.join("reports", "figures", "dfd_level1.png"),
        "Fig. 4.2: Data Flow Diagram (DFD Level 1) – Functional Software Decomposition",
        width_in=6.1
    )
    add_figure(
        os.path.join("reports", "figures", "uml_sequence.png"),
        "Fig. 4.3: UML Sequence Diagram – Live WebSocket Detection, Risk & GNC Cycle",
        width_in=6.1
    )

    add_h2("4.3 Algorithmic Core: 6-Condition Safety Interlock & NASA Risk Formulation")
    add_body(
        "Collision risk R is evaluated over normalized optical area ratio r_A = (w*h)/(W*H) using Size_Proxy = min(1.0, 2.5*sqrt(r_A)): "
        "R = 0.55*Size_Proxy + 0.30*Threat_Prior + 0.15*(1 - Confidence) + Delta_R(v, h). To prevent false-positive capture triggers, the GNC gate enforces a deterministic 6-condition interlock:",
        bold_prefix="Risk & Safety Pseudo-Code: "
    )
    add_body(
        "IF (Is_Confirmed_Debris) AND (Track_Locked >= 5 frames) AND (Range_Z in [1.5m, 3.5m]) AND (|Slew_Error| <= 1.5 deg) "
        "AND (Tumble_Variance sigma^2_AR <= 0.035) AND (Safety_Interlock == DISENGAGED) THEN Authorize_Safe_Capture() ELSE Hold_Standby_Or_Avoid()",
        italic=True
    )

    # -------------------------------------------------------------------------
    # 5. EXPECTED RESULTS AND ANALYSIS
    # -------------------------------------------------------------------------
    add_h1("5. EXPECTED RESULTS AND ANALYSIS")
    add_h2("5.1 Experimental Setup & Measurable Performance Indicators")
    add_body(
        "System benchmarks were conducted on an NVIDIA RTX 3050 GPU (CUDA 12.1) against 123 held-out orbital test images and 30 Hz video encounter streams. "
        "Key measurable indicators include Multi-Class mAP@50, strict localization mAP@50-95, Precision, Recall, GPU Inference Latency, End-to-End Pipeline Latency, and Track ID Retention."
    )

    make_styled_table(
        ["Performance Metric", "Initial Baseline (YOLO11n)", "Proposed SPACI (YOLO11s)", "Engineering Significance"],
        [
            ("Multi-Class mAP@50", "46.00%", "88.67%", "+42.67% accuracy improvement across 11 spacecraft/debris classes."),
            ("Strict Localization (mAP@50-95)", "23.10%", "50.56%", "+27.46% tighter bounding boxes for accurate 3D Kalman centroiding."),
            ("Precision / Recall", "32.0% / 56.9%", "82.46% / 84.99%", "Minimizes false alarms on active satellites while catching real debris."),
            ("GPU Inference / E2E Latency", "8.2 ms / 125.0 ms", "11.5 ms / 18.2 ms", "Sustains real-time 30 Hz WebSocket HUD streaming without UI lag."),
            ("BoT-SORT Track Retention", "None (Static)", "96.20%", "Reliable rolling tumble variance (sigma^2_AR) across occlusions.")
        ],
        col_widths=[1.75, 1.35, 1.45, 2.25],
        font_size=9.2
    )

    add_figure(
        os.path.join("reports", "figures", "confusion_matrix_normalized.png"),
        "Fig. 5.1: Normalized 11-Class Confusion Matrix Validating Debris vs. Active Satellite Discrimination",
        width_in=5.3
    )
    add_figure(
        os.path.join("reports", "figures", "verified_unified_cockpit.png"),
        "Fig. 5.2: SPACI Mission Control Web HUD – Live Detection, Salvage Tagging & Isolated KPI Console",
        width_in=6.2
    )

    add_h2("5.2 Expected Deliverables")
    add_body(
        "1. Trained & quantized YOLO11s orbital weights (best.pt); "
        "2. Full FastAPI + 30 Hz WebSocket Web HUD (Landing 3D Earth + Live/Video/Gallery/Telemetry Cockpit); "
        "3. Automated evaluation & Monte Carlo 3D GNC verification suite; "
        "4. Complete B.Tech Project Report and open-source GitHub repository (DeepKale16/Project_SPACI)."
    )

    # -------------------------------------------------------------------------
    # 6. CONCLUSIONS AND FUTURE SCOPE
    # -------------------------------------------------------------------------
    add_h1("6. CONCLUSIONS AND FUTURE SCOPE")
    add_h2("6.1 Expected Achievement & Contribution")
    add_body(
        "SPACI successfully demonstrates a unified AI software brain for orbital debris mitigation—verifying real debris versus active satellites, "
        "flagging intact reusable components for salvage, and gating safe capture maneuvers via NASA-STD-8719.14C risk scoring and 3D Kalman tracking at 88.67% mAP@50 and 18.2 ms end-to-end latency."
    )
    add_h2("6.2 Limitations & Future Scope")
    add_bullet("Current visual training relies on curated space agency imagery; extreme unattenuated solar eclipse transitions require ongoing domain adaptation.", "Limitation: ")
    add_bullet("TensorRT INT8/FP16 compilation for space-qualified NVIDIA Jetson Orin flight hardware, 6-DoF quaternion pose regression, and NASA cFS C++ module integration.", "Future Scope: ")

    # -------------------------------------------------------------------------
    # 7. PO MAPPING & 8. PSO MAPPING
    # -------------------------------------------------------------------------
    add_h1("7. PROGRAMME OUTCOMES (PO) MAPPING")
    add_body("Table 7.1 maps the project contributions to the institutional Programme Outcomes (PO1–PO11).")
    make_styled_table(
        ["PO #", "Programme Outcome", "Project Justification"],
        [
            ("PO1", "Engineering Knowledge", "Applies deep CNNs, linear algebra, Kalman state estimation, and quartic physics to space debris kinematics."),
            ("PO2", "Problem Analysis", "Analyzes hypervelocity kinetic hazards under NASA-STD-8719.14C using confusion matrices and tumble variance."),
            ("PO3", "Design / Development of Solutions", "Designs a 5-layer decoupled FastAPI, WebSocket, YOLO11s, and BoT-SORT platform with 6-condition safety gating."),
            ("PO4", "Conduct Investigations", "Executes YOLO11n vs. YOLO11s ablation studies, TTA testing, and 1,000-trial Monte Carlo GNC validation."),
            ("PO5", "Modern Tool Usage", "Integrates PyTorch 2.5, Ultralytics, OpenCV, FastAPI, Three.js WebGL, and GitHub version control."),
            ("PO6", "The Engineer and Society", "Safeguards vital global satellite communications, GPS, and climate infrastructure from collision cascades."),
            ("PO7", "Environment and Sustainability", "Directly supports orbital sustainability and circular salvage recovery to curb Kessler Syndrome growth."),
            ("PO8", "Ethics", "Maintains transparent, defensive SSA software design aligned with the 1967 UN Outer Space Treaty."),
            ("PO9", "Individual and Team Work", "Developed collaboratively using modular code contracts, automated pytest suites, and Git workflows."),
            ("PO10", "Communication", "Documented via IEEE-referenced reports, architectural diagrams, API docs, and interactive 3D visualizations."),
            ("PO11", "Project Management & Finance", "Executed across phased semester milestones with realistic GPU training, hosting, and testbed budgeting.")
        ],
        col_widths=[0.65, 1.95, 4.2],
        font_size=8.8
    )

    add_h1("8. PROGRAMME SPECIFIC OUTCOMES (PSO) MAPPING")
    make_styled_table(
        ["PSO #", "Programme Specific Outcome", "Project Justification"],
        [
            ("PSO1", "AI & Data Science Modeling", "Trains and validates a domain-augmented YOLO11s detector and BoT-SORT tracker achieving 88.67% mAP@50."),
            ("PSO2", "Full-Stack Software Engineering", "Deploys an asynchronous FastAPI + 30 Hz WebSocket architecture with real-time 3D WebGL telemetry dashboards.")
        ],
        col_widths=[0.7, 2.0, 4.1],
        font_size=9.2
    )

    # -------------------------------------------------------------------------
    # 9. SDG MAPPING
    # -------------------------------------------------------------------------
    add_h1("9. SUSTAINABLE DEVELOPMENT GOALS (SDG) MAPPING")
    add_bullet("Target 9.5 (Scientific Research & Innovation): Advances autonomous deep learning and computer vision pipelines for next-generation aerospace robotics.", "SDG #9 – Industry, Innovation and Infrastructure: ")
    add_bullet("Target 11.B (Disaster & Infrastructure Resilience): Protects orbital weather, navigation, and disaster-response satellites from catastrophic debris collisions.", "SDG #11 – Sustainable Cities and Space Communities: ")
    add_bullet("Target 12.5 (Waste Reduction & Reuse): Enables in-orbit salvage prioritization by separating reusable defunct spacecraft buses from inert fragments.", "SDG #12 – Responsible Consumption and Circular Economy: ")

    # -------------------------------------------------------------------------
    # 10. ENVIRONMENT / SUSTAINABILITY
    # -------------------------------------------------------------------------
    add_h1("10. ENVIRONMENT / SUSTAINABILITY")
    add_bullet("Orbital Ecology Protection: Prevents cascading fragment generation (Kessler Syndrome), keeping Low Earth Orbit clean for long-term scientific missions.", "Space Environment Impact: ")
    add_bullet("Green AI Compute Efficiency: YOLO11s operates at just 21.5 GFLOPs per frame (~15W edge GPU power profile), drastically reducing training and continuous inference energy footprint compared to heavy transformer detectors.", "Resource & Energy Efficiency: ")
    add_bullet("Circular Economy Alignment: Tagging intact debris structures as REUSABLE / SALVAGE supports future satellite refurbishing instead of single-use launch waste.", "Sustainability Mitigation: ")

    # -------------------------------------------------------------------------
    # 11. SAFETY / ETHICS / LEGAL
    # -------------------------------------------------------------------------
    add_h1("11. SAFETY / ETHICS / LEGAL")
    add_bullet("Algorithmic Safety Interlocks: Deterministic 6-condition safety gating prevents false-positive capture triggers or hazardous chaser collisions.", "Safety & Precautions: ")
    add_bullet("Data Privacy & Security: Operates purely on non-personal aerospace imagery and telemetry; enforces strict input file validation and isolated per-session storage.", "Privacy / Data Protection: ")
    add_bullet("UN Outer Space Treaty (1967) & IADC Compliance: Developed strictly for peaceful, defensive Space Situational Awareness and debris remediation without offensive capability.", "Ethical, Legal & Standards Compliance: ")

    # -------------------------------------------------------------------------
    # 12. COST (REALISTIC DOMAIN TRAINING, HOSTING, PERIPHERALS, DOCUMENTATION)
    # -------------------------------------------------------------------------
    add_h1("12. PROJECT COST ESTIMATE")
    add_body(
        "While SPACI leverages zero-cost open-source software libraries, real-world project execution incurs genuine expenditure for "
        "domain-specific GPU model training, cloud hosting & domain registration, optical calibration peripherals, and academic documentation. "
        "Table 12.1 presents the comprehensive, realistic cost breakdown."
    )
    make_styled_table(
        ["Cost Category", "Item / Resource Description", "Estimated Cost (INR ₹)"],
        [
            ("1. Software & AI Libraries", "PyTorch 2.5, Ultralytics YOLO11, OpenCV, BoT-SORT, FastAPI, Three.js (Open-Source Licenses)", "₹ 0"),
            ("2. Domain Model Training & Cloud GPU", "Cloud GPU Compute (Colab Pro+ / RTX A4000 hours) for 100-epoch Zero-G Domain Training, TTA & Ablation Runs + Workstation Electricity", "₹ 3,200"),
            ("3. Domain Registration & Cloud Hosting", "Custom Project Domain Name (1-Year .in/.tech) + Cloud VPS / Backend Demo Deployment Hosting (FastAPI + WebSocket)", "₹ 2,650"),
            ("4. Hardware & Testing Consumables", "HD Optical Webcam Sensor, Calibration Mount, & Printed Scale Debris Test Targets (Laptop GPU Workstation already owned)", "₹ 1,200"),
            ("5. Documentation & Printing", "Synopsis, Semester 1 & Semester 2 Color-Printed Hardbound Reports (4 Copies) & Spiral Drafts", "₹ 1,850"),
            ("6. Data Bandwidth & Contingency", "High-Speed Dataset Transfer (2,467+ images / test videos), Cloud Backups & 10% Miscellaneous Buffer", "₹ 900"),
            ("TOTAL ESTIMATED COST", "Approx. ₹ 3,267 per student (Shared equally across 3-member project group)", "₹ 9,800")
        ],
        col_widths=[1.85, 3.65, 1.3],
        font_size=9.3
    )
    add_body(
        "The project is self-funded equally by all team members, supplemented by free academic open-source toolkits and laboratory workstation infrastructure provided by the Department of Computer Engineering, AISSMS IOIT, Pune.",
        bold_prefix="Source of Resources / Funding: "
    )

    # -------------------------------------------------------------------------
    # 13. TIMELINE
    # -------------------------------------------------------------------------
    add_h1("13. PROJECT TIMELINE")
    make_styled_table(
        ["Phase", "Key Activity & Deliverables", "Target Dates", "Status"],
        [
            ("Phase 1", "Literature Survey, IEEE Research Audit & Problem Formulation", "Aug 2026 – Sep 2026", "Completed"),
            ("Phase 2", "SRS, System Architecture Design & 11-Class Dataset Auditing", "Sep 2026 – Oct 2026", "Completed"),
            ("Phase 3", "Zero-G Domain Training (YOLO11s) & BoT-SORT Tumble Engine", "Oct 2026 – Nov 2026", "Completed"),
            ("Phase 4", "NASA Risk Engine, 3D Kalman GNC & FastAPI Web HUD Integration", "Nov 2026 – Jan 2027", "Completed"),
            ("Phase 5", "Ablation Testing, Monte Carlo Validation & UI/UX Optimization", "Jan 2027 – Mar 2027", "In Progress"),
            ("Phase 6", "Final Thesis Documentation, Hardware/Camera Demo & Submission", "Mar 2027 – Apr 2027", "Scheduled")
        ],
        col_widths=[0.95, 3.35, 1.45, 1.05],
        font_size=9.2
    )

    # -------------------------------------------------------------------------
    # 14. RISK MANAGEMENT
    # -------------------------------------------------------------------------
    add_h1("14. RISK MANAGEMENT")
    make_styled_table(
        ["Identified Risk", "Category", "Prob. / Impact", "Preventive Measures & Contingency Plan"],
        [
            ("Domain Shift Under Harsh Solar Glare", "Technical", "Medium / High", "Applied HSV illumination jitter & zero-G 360-deg rotation; fallback to TTA multi-scale inference."),
            ("GPU Memory / Compute Bottlenecks", "Resource", "Low / High", "Budgeted cloud GPU training bursts; enforced GPU inference thread locking and FP16 precision."),
            ("Misclassification of Active Satellites", "Safety / Technical", "Low / Critical", "Dual verification via taxonomy prior + rolling tumble threshold before enabling capture state."),
            ("Cloud Cost Overrun or Schedule Delay", "Financial / Schedule", "Low / Medium", "Pre-allocated ₹9,800 budget with 10% buffer and modular weekly milestones tracked on GitHub.")
        ],
        col_widths=[1.6, 1.05, 1.15, 3.0],
        font_size=8.8
    )

    # -------------------------------------------------------------------------
    # 15. REFERENCES (IEEE TRANSACTIONS STYLE)
    # -------------------------------------------------------------------------
    add_h1("15. REFERENCES")
    refs = [
        "[1] M. Kisantal, S. Sharma, T. H. Park, D. Izzo, M. Martens, and S. D'Amico, “Satellite Pose Estimation Challenge: Dataset, Competition Design, and Results,” IEEE Transactions on Aerospace and Electronic Systems, vol. 56, no. 5, pp. 4083–4098, Oct. 2020. DOI: 10.1109/TAES.2020.2989063.",
        "[2] S. Sharma and S. D'Amico, “Neural Network-Based Pose Estimation for Noncooperative Spacecraft Rendezvous,” IEEE Transactions on Aerospace and Electronic Systems, vol. 56, no. 6, pp. 4638–4658, Dec. 2020. DOI: 10.1109/TAES.2020.2999450.",
        "[3] J. Redmon and A. Farhadi, “YOLOv3: An Incremental Improvement,” arXiv preprint arXiv:1804.02767, Apr. 2018. [Online]. Available: https://arxiv.org/abs/1804.02767.",
        "[4] A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft, “Simple Online and Realtime Tracking,” in Proc. IEEE International Conference on Image Processing (ICIP), Phoenix, AZ, USA, Sep. 2016, pp. 3464–3468. DOI: 10.1109/ICIP.2016.7533003.",
        "[5] N. Wojke, A. Bewley, and D. Paulus, “Simple Online and Realtime Tracking with a Deep Association Metric,” in Proc. IEEE International Conference on Image Processing (ICIP), Beijing, China, Sep. 2017, pp. 3645–3649. DOI: 10.1109/ICIP.2017.8296962.",
        "[6] N. Aharon, R. Orfaig, and B.-Z. Bobrovsky, “BoT-SORT: Robust Associations Multi-Pedestrian Tracking,” arXiv preprint arXiv:2206.14651, Jun. 2022. [Online]. Available: https://arxiv.org/abs/2206.14651.",
        "[7] J.-C. Liou and N. L. Johnson, “Risks in Orbit: Assessing the Impact of Space Debris on Operational Spacecraft,” Science, vol. 311, no. 5759, pp. 340–341, Jan. 2006. DOI: 10.1126/science.1121337.",
        "[8] NASA, “Process for Limiting Orbital Debris,” NASA Technical Standard NASA-STD-8719.14C, National Aeronautics and Space Administration, Washington, D.C., USA, Nov. 2021. [Online]. Available: https://standards.nasa.gov/standard/NASA/NASA-STD-871914.",
        "[9] European Space Agency (ESA), “ESA's Annual Space Environment Report & DISCOS Catalog,” ESA Space Debris Office, ESOC, Darmstadt, Germany, 2024. [Online]. Available: https://www.esa.int/Space_Safety/Space_Debris.",
        "[10] G. Welch and G. Bishop, “An Introduction to the Kalman Filter,” Dept. Comput. Sci., Univ. North Carolina at Chapel Hill, Tech. Rep. TR 95-041, 2006.",
        "[11] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollar, “Focal Loss for Dense Object Detection,” in Proc. IEEE International Conference on Computer Vision (ICCV), Venice, Italy, Oct. 2017, pp. 2980–2988. DOI: 10.1109/ICCV.2017.324.",
        "[12] S. Ramirez, J. A. Perez, and M. Torres, “Real-Time Computer Vision Algorithms for Spacecraft Proximity Operations,” Acta Astronautica, vol. 182, pp. 450–462, May 2021."
    ]
    for rf in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.12
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(rf)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)

    # -------------------------------------------------------------------------
    # APPROVAL TABLE (EXACT OFFICIAL TEMPLATE STRUCTURE)
    # -------------------------------------------------------------------------
    add_h1("APPROVAL")
    make_styled_table(
        ["Role", "Name & Signature", "Date"],
        [
            ("Project Guide / Supervisor", "<GUIDE NAME>\nSignature: ________________________", "____ / ____ / 2026"),
            ("Project Coordinator", "<COORDINATOR NAME>\nSignature: ________________________", "____ / ____ / 2026"),
            ("Head of Department", "<HOD NAME>\nSignature: ________________________", "____ / ____ / 2026"),
        ],
        col_widths=[2.1, 3.2, 1.5],
        font_size=10
    )

    doc.save(output_path)
    print(f"Successfully generated Official AISSMS Synopsis: {output_path}")


if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    primary = os.path.join("reports", "SPACI_OFFICIAL_SYNOPSIS_AISSMS.docx")
    create_official_synopsis_docx(primary)

    for extra in ("SPACI_SOFTWARE_SYNOPSIS_AISSMS.docx", "SPACI_PROJECT_SYNOPSIS_AISSMS.docx"):
        target = os.path.join("reports", extra)
        try:
            create_official_synopsis_docx(target)
        except PermissionError:
            print(f"Notice: {target} is currently locked (open in Word). Primary file updated cleanly at {primary}.")
