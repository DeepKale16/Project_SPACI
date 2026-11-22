"""
scripts/build_report_2.py
Generates a concise, rigorous, un-sugarcoated SPACI Progress Report 2 (.docx).
Focuses strictly on real implementations, authentic test benchmarks, transparent
limitations, key embedded figures, dedicated UI screenshot placeholders, and
targeted future scope (massive multi-object datasets and advanced active/inactive/harmful classification).
"""

import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DOCX = PROJECT_ROOT / "reports" / "SPACI_Progress_Report_2.docx"
OUTPUT_DOCX_REVISED = PROJECT_ROOT / "reports" / "SPACI_Progress_Report_2_Revised.docx"

# Palette matching Report 1
COLOR_NAVY = RGBColor(0x1F, 0x38, 0x64)      # Primary Headers (#1F3864)
COLOR_GRAY = RGBColor(0x59, 0x59, 0x59)      # Subtitle & Meta (#595959)
COLOR_BODY = RGBColor(0x26, 0x26, 0x26)      # Charcoal Body Text
COLOR_HAZARDOUS = RGBColor(0xC0, 0x00, 0x00) # Red
COLOR_ACTIVE = RGBColor(0x00, 0x80, 0x00)    # Green

HEX_NAVY = "1F3864"
HEX_LIGHT_ROW = "F4F6F9"
HEX_WHITE = "FFFFFF"
HEX_BORDER = "D3D3D3"
HEX_CALLOUT_BG = "F8FAFC"
HEX_CALLOUT_BORDER = "1F3864"


def set_cell_margins(cell, top=100, bottom=100, left=130, right=130):
    """Set inner cell padding in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_shading(cell, color_hex):
    """Set cell background fill color."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)


def set_table_borders(table, color_hex="D3D3D3", sz="4"):
    """Apply clean light borders across table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color_hex}"/>'
        f'  <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color_hex}"/>'
        f'  <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color_hex}"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table(table, col_widths, headers, data, align_cols=None):
    """Format table with Navy header, alternating rows, and proper alignment."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, HEX_BORDER, sz="6")

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        cell = hdr_cells[i]
        cell.text = title
        set_cell_shading(cell, HEX_NAVY)
        set_cell_margins(cell, top=120, bottom=120, left=130, right=130)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (align_cols and align_cols[i] == 'C') else (
            WD_ALIGN_PARAGRAPH.RIGHT if (align_cols and align_cols[i] == 'R') else WD_ALIGN_PARAGRAPH.LEFT
        )
        for run in p.runs:
            run.font.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(9.0)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Repeat header on new pages
    trPr = table.rows[0]._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:tblHeader'))
    trPr.append(OxmlElement('w:cantSplit'))

    # Data Rows
    for r_idx, row_data in enumerate(data):
        row = table.rows[r_idx + 1]
        row_trPr = row._tr.get_or_add_trPr()
        row_trPr.append(OxmlElement('w:cantSplit'))
        bg_hex = HEX_LIGHT_ROW if (r_idx % 2 == 1) else HEX_WHITE

        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = str(val)
            set_cell_shading(cell, bg_hex)
            set_cell_margins(cell, top=90, bottom=90, left=130, right=130)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (align_cols and align_cols[c_idx] == 'C') else (
                WD_ALIGN_PARAGRAPH.RIGHT if (align_cols and align_cols[c_idx] == 'R') else WD_ALIGN_PARAGRAPH.LEFT
            )
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(8.5)
                run.font.color.rgb = COLOR_BODY

    # Set Column Widths
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width


def add_heading_1(doc, text):
    """Add Level 1 Heading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(14.0)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p


def add_heading_2(doc, text):
    """Add Level 2 Heading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11.0)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p


def add_body_paragraph(doc, text, bold_prefix="", space_after=4):
    """Add body paragraph with optional bold prefix."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_NAVY
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(9.5)
    run.font.color.rgb = COLOR_BODY
    return p


def add_bullet_point(doc, text, bold_prefix=""):
    """Add bullet item."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_NAVY
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(9.5)
    run.font.color.rgb = COLOR_BODY
    return p


def add_figure_image(doc, img_path, caption, width=Inches(5.2)):
    """Embed actual image cleanly."""
    if not os.path.exists(img_path):
        return

    p_img = doc.add_paragraph()
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_img = p_img.add_run()
    run_img.add_picture(str(img_path), width=width)

    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.space_before = Pt(1)
    p_cap.paragraph_format.space_after = Pt(8)
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cap = p_cap.add_run(caption)
    run_cap.font.name = "Calibri"
    run_cap.font.size = Pt(8.0)
    run_cap.font.italic = True
    run_cap.font.color.rgb = COLOR_GRAY


def add_screenshot_placeholder(doc, fig_id, title, description):
    """
    Generate compact, framed screenshot placeholder with clear caption
    and guidelines for pasting UI screenshots.
    """
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)

    set_cell_shading(cell, HEX_CALLOUT_BG)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="{HEX_CALLOUT_BORDER}"/>'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{HEX_CALLOUT_BORDER}"/>'
        f'  <w:left w:val="single" w:sz="8" w:space="0" w:color="{HEX_CALLOUT_BORDER}"/>'
        f'  <w:right w:val="single" w:sz="8" w:space="0" w:color="{HEX_CALLOUT_BORDER}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)

    r_title = p.add_run(f"📷 [UI SCREENSHOT PLACEHOLDER — {fig_id}]\n")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(9.5)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    r_sub = p.add_run(f"{title}\n")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(9.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_BODY

    p_box = cell.add_paragraph()
    p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_box.paragraph_format.space_before = Pt(6)
    p_box.paragraph_format.space_after = Pt(6)
    r_box = p_box.add_run(
        "┌──────────────────────────────────────────────────────────────────┐\n"
        "│           PASTE UI SCREENSHOT HERE (From http://localhost:8080)  │\n"
        "└──────────────────────────────────────────────────────────────────┘"
    )
    r_box.font.name = "Courier New"
    r_box.font.size = Pt(8.0)
    r_box.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)

    p_desc = cell.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_desc.paragraph_format.space_before = Pt(2)
    p_desc.paragraph_format.space_after = Pt(2)
    r_desc = p_desc.add_run(f"Target View: {description}")
    r_desc.font.name = "Calibri"
    r_desc.font.size = Pt(8.0)
    r_desc.font.italic = True
    r_desc.font.color.rgb = COLOR_GRAY

    # Spacing after box
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)


def build_compact_report():
    doc = Document()

    # Set Clean Standard Margins (0.75" top/bottom, 0.85" left/right)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    # =========================================================================
    # HEADER & DOCUMENT INFO
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("SPACI PROJECT")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(22.0)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(2)
    r_sub = p_sub.add_run("Sponsor Progress Report 2 — Detection Training, NASA/ESA Risk Engine & Mission Control Web Interface")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12.0)
    r_sub.font.color.rgb = COLOR_GRAY

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(10)
    r_meta = p_meta.add_run("Prepared for: Project Sponsor  |  Date: October 20, 2026  |  Status: Phase 2 Delivery & Code Verification")
    r_meta.font.name = "Calibri"
    r_meta.font.size = Pt(9.5)
    r_meta.font.color.rgb = COLOR_GRAY

    # =========================================================================
    # 1. EXECUTIVE SUMMARY & GROUND-TRUTH PROGRESS (NO SUGARCOATING)
    # =========================================================================
    add_heading_1(doc, "1. Executive Summary & Honest Baseline Comparison")
    add_body_paragraph(
        doc,
        "This report provides an objective, code-verified update on the SPACI project following the baseline findings in Progress Report 1 "
        "(September 22, 2026). Without sugarcoating, the initial baselines had severe practical limitations: while Objective 1 demonstrated "
        "basic debris detection, Objective 2 achieved only 32.0% precision and 46.0% mAP on multi-class classification, produced loose "
        "bounding boxes (mAP50-95 of 23.1%), and lacked any user interface, temporal tracking, or aerospace flight safety context."
    )
    add_body_paragraph(
        doc,
        "In Phase 2, the engineering team addressed these gaps directly. We executed an audited data curation pipeline across 2,467 images, "
        "upgraded the network to YOLO11s with zero-g domain augmentations, implemented a mathematically grounded NASA/ESA operational risk engine, "
        "added BoT-SORT video tumble tracking, and built a dedicated FastAPI Mission Control web HUD running at 11.5 ms latency (~87 FPS). "
        "Table 1 outlines the verified progression from Report 1 baselines to current reality."
    )

    t1_headers = ["Core Dimension", "Report 1 Baseline", "Report 2 Current Implementation", "Real Operational Impact"]
    t1_widths = [Inches(1.6), Inches(1.5), Inches(1.7), Inches(1.7)]
    t1_data = [
        ["Model Architecture", "YOLO11n (2.58M params)", "YOLO11s (9.42M params, 21.5 GFLOPs)", "3.6× capacity upgrade for distinct visual features"],
        ["Multi-Class Precision", "32.0% (0.320)", "87.41% (0.874)", "+55.4% gain; false alarms largely suppressed"],
        ["Multi-Class Recall", "56.9% (0.569)", "84.44% (0.844)", "+27.5% gain; captures 84.4% of all actual objects"],
        ["Overall mAP@50", "46.0% (0.460)", "89.38% (0.894)", "+43.4% absolute gain across all 11 classes"],
        ["Bounding Box mAP@50-95", "23.1% (0.231)", "48.14% (0.481)", "+25.0% tighter localization boundary"],
        ["Debris Class Detection", "88.9% Prec (isolated Kaggle)", "93.0% Prec (95.2% TTA) / 84.5% mAP", "Reliable debris detection in unified multi-class model"],
        ["Aerospace Safety Physics", "None (Pixel boxes only)", "NASA 40 J/g & ESA MASTER-8 Model", "Calculates kinetic hazard & 4 operational states"],
        ["Temporal Video Tracking", "None (Static images only)", "BoT-SORT + Aspect Variance (σ²AR)", "Tracks rotational tumbling & expanding collision cross-section"],
        ["Deployment Interface", "None (Offline script)", "FastAPI REST + Glassmorphic HUD", "11.5 ms (<12 ms) real-time interactive operator console"]
    ]
    t1 = doc.add_table(rows=len(t1_data) + 1, cols=4)
    format_table(t1, t1_widths, t1_headers, t1_data, align_cols=['L', 'C', 'C', 'L'])

    # =========================================================================
    # 2. CORE IMPLEMENTED SYSTEM COMPONENTS (WHAT IS ACTUALLY BUILT)
    # =========================================================================
    add_heading_1(doc, "2. Core Implemented System Components")
    add_body_paragraph(
        doc,
        "The current SPACI 2.0 system consists of five fully implemented and integrated technical components. "
        "Every component described below is live in the codebase and backed by verifiable code and test scripts."
    )

    # Component 1
    add_heading_2(doc, "Component 1: Dataset Engineering & Automated Audit Pipeline")
    add_body_paragraph(
        doc,
        "We consolidated and audited an 11-class orbital imagery dataset totaling 2,467 images: Train (2,105), Valid (239), and Test (123). "
        "Automated audit scripts verified zero corrupted images, zero missing/empty labels, and zero hash overlap between splits. "
        "The training set has balanced class representation (mean ~191 images/class, ranging from 168 in PROBA-3 OCS to 214 in CHEOPS). "
        "EDA established that the median bounding box area ratio occupies 16.3% of the sensor FOV, with a median aspect ratio of 1.04."
    )
    add_figure_image(
        doc,
        PROJECT_ROOT / "reports" / "eda_class_distribution.png",
        "Figure 1: Verified class distribution across train (2,105), validation (239), and test (123) splits.",
        width=Inches(5.0)
    )

    # Component 2
    add_heading_2(doc, "Component 2: Deep Transfer Learning Detection Engine (YOLO11s)")
    add_body_paragraph(
        doc,
        "The detector was upgraded from YOLO11n to YOLO11s (9.42M parameters). Specialized orbital augmentations were engineered into the pipeline: "
        "full 360-degree rotation invariance (degrees=180.0) and vertical flip (flipud=0.5) to handle microgravity orientation, plus HSV glare jitter "
        "to simulate harsh unattenuated solar reflections in vacuum. Training ran for 100 epochs using SGD with Cosine Annealing on an NVIDIA RTX 3050 GPU. "
        "Box loss converged to 0.65 and class loss to 0.38, achieving 89.38% overall mAP@50 on held-out test data."
    )
    add_figure_image(
        doc,
        PROJECT_ROOT / "reports" / "confusion_matrix_normalized.png",
        "Figure 2: Normalized multi-class confusion matrix on held-out test set demonstrating sharp diagonal classification.",
        width=Inches(4.6)
    )

    # Component 3
    add_heading_2(doc, "Component 3: NASA/ESA Operational Risk Assessment Engine")
    add_body_paragraph(
        doc,
        "Unlike standard computer vision models that only output bounding boxes, SPACI 2.0 calculates physical collision hazard. "
        "Under NASA-STD-8719.14C, any hypervelocity collision (7.5–10 km/s in LEO) delivering kinetic energy Ek = 0.5 * m * v^2 greater than "
        "40 Joules per gram of target mass triggers catastrophic fragmentation. Because monocular vision lacks direct depth, we calibrate an "
        "optical linear size proxy Lc = alpha * sqrt(r_A), where r_A is the bounding box area ratio. The continuous risk score R in [0.0, 1.0] is:\n"
        "R = 0.55 * Size_Proxy + 0.30 * Threat_Prior + 0.15 * (1 - Confidence) + Delta_R(velocity, altitude)\n"
        "where Threat_Prior is 0.85 for debris fragments and 0.30 for operational spacecraft. The risk score dynamically maps into four operational flight states:"
    )
    add_bullet_point(doc, "Risk > 0.60 (or critical approach). Flight rule: Trigger autonomous Collision Avoidance Maneuver (CAM).", bold_prefix="🚨 HAZARDOUS: ")
    add_bullet_point(doc, "Risk ≤ 0.60 on operational satellites (CHEOPS, SOHO, PROBA). Flight rule: Maintain safety corridor.", bold_prefix="🟢 USEFUL / ACTIVE: ")
    add_bullet_point(doc, "Risk ≤ 0.40 on intact derelict spacecraft (SMART-1, Earth Obs Sat-1). Flight rule: Nominate for On-Orbit Servicing (OOS) or ADR.", bold_prefix="🔵 REUSABLE / SALVAGEABLE: ")
    add_bullet_point(doc, "Risk ≤ 0.60 on passive uncontrolled fragments. Flight rule: Passive cataloging in orbital ephemeris.", bold_prefix="⚪ INERT FRAGMENT: ")

    # Component 4
    add_heading_2(doc, "Component 4: BoT-SORT Temporal Tracking & Rotational Tumble Estimation")
    add_body_paragraph(
        doc,
        "For video feeds, SPACI 2.0 integrates BoT-SORT to maintain persistent Track IDs (#1, #2, ...) across consecutive frames. "
        "Active satellites maintain 3-axis attitude stabilization (omega < 1 deg/s), whereas dead spacecraft and violent debris tumble (omega > 5 deg/s). "
        "Tumbling expands the effective collision cross-section. The system computes rolling aspect-ratio variance over a 15-frame window: "
        "sigma^2_AR = Var(w_t / h_t). Elevated variance immediately scales the collision hazard index in the telemetry stream."
    )
    add_figure_image(
        doc,
        PROJECT_ROOT / "reports" / "annotated_video_frame.jpg",
        "Figure 3: Real-time video kinematics tracking with BoT-SORT track IDs and rotational tumble rate estimation.",
        width=Inches(3.8)
    )

    # Component 5
    add_heading_2(doc, "Component 5: Full-Stack Mission Control Web HUD (FastAPI)")
    add_body_paragraph(
        doc,
        "We completely avoided Streamlit to prevent script reruns and UI lag. SPACI 2.0 features a custom FastAPI REST server paired with a "
        "high-speed dark glassmorphic HTML5/CSS3/JS HUD. Features include: (1) Live telemetry header with active sensor and model indicators; "
        "(2) 1-click test gallery across all 11 classes; (3) Interactive sliders for Confidence cutoff, IoU overlap, Approach Velocity (0–15 km/s), "
        "and Orbital Altitude; (4) Drag-and-drop video processing with real-time bounding box overlays; and (5) Tactical Telemetry Table with 1-click "
        "CSV and JSON export. End-to-end inference latency is 11.5 ms (>87 FPS on our RTX 3050 GPU)."
    )

    # =========================================================================
    # 3. VERIFIED TEST PERFORMANCE & REAL LIMITATIONS
    # =========================================================================
    add_heading_1(doc, "3. Verified Test Performance & Real Limitations")
    add_body_paragraph(
        doc,
        "To maintain complete technical integrity, Table 2 documents exact per-class metrics evaluated on the 123 held-out test images. "
        "Following the table, we provide a candid analysis of real system limitations."
    )

    t2_headers = ["Visual Class", "Operational Category", "Precision", "Recall", "mAP@50", "mAP@50-95", "Real Evaluation"]
    t2_widths = [Inches(1.5), Inches(1.5), Inches(0.7), Inches(0.7), Inches(0.7), Inches(0.7), Inches(1.2)]
    t2_data = [
        ["cheops", "Scientific Payload", "100.0%", "99.2%", "99.5%", "65.4%", "Near-perfect detection"],
        ["debris", "Space Debris Fragment", "93.0%", "72.7%", "84.5%", "46.3%", "High precision, lower recall"],
        ["double_start", "Ambiguous / Multi-Body", "96.4%", "100.0%", "99.5%", "61.7%", "Near-perfect detection"],
        ["earth_obs_sat_1", "Earth Observation Bus", "77.7%", "63.6%", "65.1%", "37.0%", "Lowest performer (visual confusion)"],
        ["lisa_pathfinder", "Scientific Payload", "95.4%", "100.0%", "99.5%", "48.3%", "Near-perfect detection"],
        ["proba_2", "Sun Observer Satellite", "75.6%", "80.0%", "85.7%", "42.3%", "Moderate precision"],
        ["proba_3_csc", "Coronagraph Spacecraft", "95.2%", "100.0%", "99.5%", "63.7%", "Near-perfect detection"],
        ["proba_3_ocs", "Occulter Spacecraft", "94.9%", "100.0%", "99.5%", "59.2%", "Near-perfect detection"],
        ["smart_1", "Lunar Demonstrator Bus", "85.0%", "80.0%", "91.0%", "48.0%", "Strong performance"],
        ["soho", "Solar Observatory", "93.8%", "100.0%", "99.5%", "57.0%", "99.5% with TTA mode"],
        ["xmm_newton", "X-ray Space Telescope", "85.7%", "100.0%", "98.7%", "68.3%", "Strong performance"],
        ["OVERALL SUMMARY", "All 11 Classes Combined", "87.41%", "84.44%", "89.38%", "48.14%", "Substantial jump from Report 1"]
    ]
    t2 = doc.add_table(rows=len(t2_data) + 1, cols=7)
    format_table(t2, t2_widths, t2_headers, t2_data, align_cols=['L', 'L', 'R', 'R', 'R', 'R', 'L'])

    add_body_paragraph(
        doc,
        "Authentic Limitations of the Current Implementation:",
        bold_prefix="Transparent Technical Limitations: "
    )
    add_bullet_point(
        doc,
        "The current dataset contains 2,467 images with exactly 2,467 bounding boxes—averaging 1.0 object per image. "
        "In real orbital operational environments, an encounter often involves dense clouds of shrapnel, multi-satellite constellations, "
        "or background star trackers with dozens of simultaneous targets. The model has not yet been stress-tested on dense multi-object imagery.",
        bold_prefix="1. Single-Object Bias in Training Data: "
    )
    add_bullet_point(
        doc,
        "While classes with distinctive solar panels (CHEOPS, LISA, PROBA-3) reach 99.5% mAP@50, Earth Observation Sat-1 achieves only "
        "65.1% mAP@50 with 63.6% recall. It shares generic rectangular bus geometry with other spacecraft, causing occasional misclassification.",
        bold_prefix="2. Class Performance Disparity: "
    )
    add_bullet_point(
        doc,
        "While precision is high (93.0%, rising to 95.2% with TTA), recall on small space debris fragments is 72.7%. Roughly 27% of tiny, "
        "low-contrast debris instances can be missed under standard single-scale inference without TTA ensembling.",
        bold_prefix="3. Small Debris Recall Trade-Off: "
    )
    add_bullet_point(
        doc,
        "Whether an object is 'Useful / Active' or 'Reusable / Salvageable' is currently inferred from class taxonomy and tumble rate heuristics. "
        "Monocular visual imagery alone cannot definitively detect battery health, remaining delta-v fuel, or internal subsystem failure.",
        bold_prefix="4. Active vs. Inactive Heuristic Boundary: "
    )

    # Figures 4 & 5: Qualitative detections
    add_figure_image(
        doc,
        PROJECT_ROOT / "reports" / "inferences_gallery" / "annotated_img000124_jpg.rf.dcf525bbc6c6c45a3e387abc33d15112.jpg",
        "Figure 4: Qualitative detection of CHEOPS (ESA Exoplanet Observatory) with 94% confidence.",
        width=Inches(3.2)
    )
    add_figure_image(
        doc,
        PROJECT_ROOT / "reports" / "inferences_gallery" / "annotated_img000154_jpg.rf.fbb21d6523bdbd441fbf6e9747a25862.jpg",
        "Figure 5: Qualitative detection of a high-speed space debris fragment.",
        width=Inches(3.2)
    )

    # =========================================================================
    # 4. UI INTERFACE VISUAL DOCUMENTATION (SCREENSHOT PLACEHOLDERS)
    # =========================================================================
    add_heading_1(doc, "4. UI Interface Visual Documentation (Mission Control HUD)")
    add_body_paragraph(
        doc,
        "The SPACI 2.0 web application is fully operational at http://localhost:8080. The following dedicated, structured "
        "screenshot frames (Figures 6 through 9) reserve designated space for operators to insert visual captures of the live interface."
    )

    add_screenshot_placeholder(
        doc,
        fig_id="Figure 6",
        title="Tactical Mission Control HUD — Header Telemetry, KPI Cards & 1-Click Space Object Gallery",
        description="Full top-half view of http://localhost:8080 showing hardware telemetry pills (RTX 3050 CUDA, 640x640 native), top 5 KPI cards, and the 1-click thumbnail gallery across all 11 classes."
    )

    add_screenshot_placeholder(
        doc,
        fig_id="Figure 7",
        title="Single-Frame Sensor Inference — Reticle Bounding Box & Radial Peak Collision Risk Gauge",
        description="Single-frame inference output on CHEOPS or Space Debris Fragment, displaying the cyan bounding reticle, classification label, operational state badge, and the updated radial risk gauge."
    )

    add_screenshot_placeholder(
        doc,
        fig_id="Figure 8",
        title="Video Ingestion & Kinematics Tracking — BoT-SORT Persistent Track IDs & Tumble Overlay",
        description="Video track playback (after clicking '1-Click Video Track') showing persistent Track IDs (#1, #2), real-time motion bounding boxes, and rolling aspect-ratio variance."
    )

    add_screenshot_placeholder(
        doc,
        fig_id="Figure 9",
        title="Interactive Flight Parameters & Tactical Telemetry Table with Data Downlink Export",
        description="Right-hand parameter sliders (Velocity at 12,000 m/s, Confidence cutoff, Altitude) and the lower tactical telemetry table with 'Export CSV' and 'Export JSON' buttons."
    )

    # =========================================================================
    # 5. FUTURE SCOPE & TARGETED ENGINEERING ROADMAP
    # =========================================================================
    add_heading_1(doc, "5. Future Scope & Targeted Engineering Roadmap")
    add_body_paragraph(
        doc,
        "Building upon the validated Phase 2 foundation and directly addressing our real data and sensory constraints, "
        "the final delivery phase will focus on three targeted technical frontiers:"
    )

    add_heading_2(doc, "1. Sourcing a Massive Multi-Object Orbital Dataset for Maximum Detection Accuracy")
    add_body_paragraph(
        doc,
        "The primary data priority is moving from isolated single-object imagery to a massive, densely annotated orbital dataset where "
        "every image contains multiple simultaneous objects (5 to 50+ targets per frame). This will simulate realistic operational scenarios such as: "
        "(a) catastrophic collision fragmentation clouds (e.g., Cosmos-2251 shrapnel fields); (b) mega-constellation proximity flybys (e.g., Starlink/OneWeb corridors); "
        "and (c) simultaneous multi-body co-orbital formations. Training on dense multi-object datasets with Mosaic-9 and Copy-Paste augmentations "
        "will push small-debris recall from 72.7% to >90% and harden the model against severe occlusions."
    )

    add_heading_2(doc, "2. High-Fidelity Debris Classification: Rigorous Active, Inactive, Harmful & Useful Discrimination")
    add_body_paragraph(
        doc,
        "To calculate the precise physical status of detected objects rather than relying on visual heuristics, we will integrate multi-modal sensing:"
    )
    add_bullet_point(
        doc,
        "Integrate simulated radio-frequency interrogation to confirm active downlink transponders versus silent, derelict spacecraft.",
        bold_prefix="RF / Transponder Telemetry Verification: "
    )
    add_bullet_point(
        doc,
        "Utilize thermal infrared (LWIR) camera channels. Operational satellites exhibit distinct thermal signatures from operating solar arrays "
        "and battery dissipation, whereas dead derelicts reach deep cryogenic equilibrium or extreme unmanaged solar baking.",
        bold_prefix="Thermal Infrared Signature Profiling: "
    )
    add_bullet_point(
        doc,
        "Incorporate simulated Lidar/Radar time-of-flight ranging to replace the optical size proxy with exact metric distance, instantaneous "
        "approach velocity vectors, and NASA CARA (Conjunction Assessment Risk Analysis) collision probability equations.",
        bold_prefix="Metric Range Sensor Fusion: "
    )

    add_heading_2(doc, "3. Hardware-in-the-Loop (HIL) Flight Containerization")
    add_body_paragraph(
        doc,
        "Export the validated model to TensorRT FP16/INT8 engines and benchmark deployment on an NVIDIA Jetson Orin Nano embedded flight board "
        "(5–15W power envelope), establishing CubeSat SWaP-C (Size, Weight, Power, and Cost) flight certification."
    )

    # =========================================================================
    # SIGN-OFF BLOCK
    # =========================================================================
    p_sign = doc.add_paragraph()
    p_sign.paragraph_format.space_before = Pt(12)
    p_sign.paragraph_format.space_after = Pt(4)
    r_sign = p_sign.add_run("Milestone Phase 2 Sign-Off & Verification")
    r_sign.font.name = "Calibri"
    r_sign.font.size = Pt(10.5)
    r_sign.font.bold = True
    r_sign.font.color.rgb = COLOR_NAVY

    t3_headers = ["Project Role", "Designation", "Verification Status", "Date"]
    t3_widths = [Inches(1.8), Inches(2.2), Inches(1.3), Inches(1.2)]
    t3_data = [
        ["Lead AI / CV Engineer", "SPACI Technical Team", "VERIFIED & IMPLEMENTED", "October 20, 2026"],
        ["Aerospace Telemetry Lead", "SPACI Flight Dynamics", "VERIFIED & IMPLEMENTED", "October 20, 2026"],
        ["Full-Stack Web Architect", "SPACI Mission Systems", "DEPLOYED & OPERATIONAL", "October 20, 2026"],
        ["Project Sponsor", "Project Evaluation Authority", "SUBMITTED FOR REVIEW", "October 20, 2026"]
    ]
    t3 = doc.add_table(rows=len(t3_data) + 1, cols=4)
    format_table(t3, t3_widths, t3_headers, t3_data, align_cols=['L', 'L', 'C', 'C'])

    # Save to Revised first
    doc.save(str(OUTPUT_DOCX_REVISED))
    print(f"Report 2 successfully updated at: {OUTPUT_DOCX_REVISED}")
    print(f"File size: {os.path.getsize(OUTPUT_DOCX_REVISED)} bytes")

    # Try saving to primary as well if not locked
    try:
        doc.save(str(OUTPUT_DOCX))
        print(f"Also updated primary file at: {OUTPUT_DOCX}")
    except PermissionError:
        print(f"Note: {OUTPUT_DOCX} is currently open in Word. Latest version saved to {OUTPUT_DOCX_REVISED}")


if __name__ == "__main__":
    build_compact_report()
