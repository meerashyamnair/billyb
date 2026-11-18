import io
import os
import datetime
from typing import Dict, Any, List
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_student_pdf(student: Dict[str, Any]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#1e3a8a")  # Deep Navy Blue
    secondary_color = colors.HexColor("#3b82f6")  # Accent Blue
    text_dark = colors.HexColor("#0f172a")
    text_muted = colors.HexColor("#64748b")
    border_color = colors.HexColor("#e2e8f0")
    bg_light = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        alignment=1  # Center
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        alignment=1  # Center
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceAfter=6
    )

    cell_label_style = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    cell_value_style = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=text_dark
    )

    elements = []

    # Institution Header
    school_name = student.get('school_name') or "OFFICIAL NOMINAL ROLL PORTAL"
    elements.append(Paragraph(school_name.upper(), title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("STUDENT NOMINAL ROLL VERIFICATION PROFILE", subtitle_style))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=14))

    # Student Highlight Box with Embedded Photo
    student_name = student.get('student_name', 'N/A')
    course_name = student.get('class_course') or student.get('department') or "Standard Nominal Roll"
    admn_no = student.get('admission_no', 'N/A')
    reg_no = student.get('register_no', 'N/A')

    # Prepare photo element if available
    photo_path = student.get('photo_path', '')
    photo_element = None
    if student.get('has_photo') and photo_path and os.path.exists(photo_path):
        try:
            photo_element = RLImage(photo_path, width=65, height=85)
        except Exception as e:
            photo_element = Paragraph("<font size=8 color='#94a3b8'>[Photo Error]</font>", styles['Normal'])
    else:
        photo_element = Paragraph("<font size=8 color='#94a3b8'>[No Photo<br/>in File]</font>", styles['Normal'])

    info_data = [
        [Paragraph(f"<b>STUDENT NAME:</b> <font size=13 color='#1e3a8a'><b>{student_name}</b></font>", styles['Normal'])],
        [Paragraph(f"<b>COURSE:</b> {course_name}", styles['Normal'])],
        [Paragraph(f"<b>Admission No:</b> {admn_no} &nbsp;&nbsp;&nbsp;&nbsp; <b>Register No:</b> {reg_no}", styles['Normal'])],
    ]
    info_table = Table(info_data, colWidths=[425])
    info_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    banner_data = [
        [info_table, photo_element]
    ]
    banner_table = Table(banner_data, colWidths=[445, 95])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 1, secondary_color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 16))

    # All Extracted Fields Table
    elements.append(Paragraph("Extracted Student Record Details", section_heading))

    all_fields = student.get('all_fields', {})
    table_rows = []
    
    # Render fields in 2-column or 4-cell layout (Label, Value, Label, Value)
    field_items = list(all_fields.items())
    
    # Process items in pairs
    for i in range(0, len(field_items), 2):
        k1, v1 = field_items[i]
        c1 = Paragraph(str(k1), cell_label_style)
        c2 = Paragraph(str(v1), cell_value_style)
        
        if i + 1 < len(field_items):
            k2, v2 = field_items[i+1]
            c3 = Paragraph(str(k2), cell_label_style)
            c4 = Paragraph(str(v2), cell_value_style)
        else:
            c3 = Paragraph("", cell_label_style)
            c4 = Paragraph("", cell_value_style)
            
        table_rows.append([c1, c2, c3, c4])

    if table_rows:
        fields_table = Table(table_rows, colWidths=[120, 150, 120, 150])
        fields_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, bg_light]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(fields_table)

    elements.append(Spacer(1, 20))

    # Provenance / Source Verification Section
    elements.append(Paragraph("Document Verification & Source Reference", section_heading))
    source_file = student.get('source_file', 'N/A')
    page_or_sheet = student.get('page_or_sheet', 'N/A')
    record_id = student.get('id', 'N/A')
    gen_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    source_data = [
        [Paragraph("<b>Source File:</b>", cell_label_style), Paragraph(str(source_file), cell_value_style)],
        [Paragraph("<b>Document Location:</b>", cell_label_style), Paragraph(str(page_or_sheet), cell_value_style)],
        [Paragraph("<b>Internal Record ID:</b>", cell_label_style), Paragraph(str(record_id), cell_value_style)],
        [Paragraph("<b>Generated Timestamp:</b>", cell_label_style), Paragraph(f"{gen_time} (Local Server Time)", cell_value_style)],
        [Paragraph("<b>Verification Notice:</b>", cell_label_style), Paragraph("This record was directly extracted from official nominal roll archives without synthetic alteration.", cell_value_style)],
    ]
    source_table = Table(source_data, colWidths=[140, 400])
    source_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(source_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_student_excel(student: Dict[str, Any]) -> io.BytesIO:
    buffer = io.BytesIO()
    
    # Collect core fields + all dynamic fields
    data = {}
    data["Record ID"] = student.get("id")
    data["Student Name"] = student.get("student_name")
    data["Admission No"] = student.get("admission_no")
    data["Register No"] = student.get("register_no")
    data["Roll / Sl No"] = student.get("roll_no")
    data["Course / Class"] = student.get("class_course")
    data["Institution"] = student.get("school_name")
    data["Date of Birth"] = student.get("dob")
    data["Gender"] = student.get("gender")
    data["Father Name"] = student.get("father_name")
    data["Mother Name"] = student.get("mother_name")
    data["Guardian Name"] = student.get("guardian_name")
    data["Category"] = student.get("category")
    data["Caste"] = student.get("caste")
    data["Religion"] = student.get("religion")
    data["Source File"] = student.get("source_file")
    data["Page / Sheet"] = student.get("page_or_sheet")

    # Add any extra extracted fields
    all_fields = student.get("all_fields", {})
    for k, v in all_fields.items():
        if k not in data and str(v).strip():
            data[f"Extracted: {k}"] = v

    df = pd.DataFrame([data])
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Student Profile')
        
    buffer.seek(0)
    return buffer

def generate_search_results_excel(records: List[Dict[str, Any]]) -> io.BytesIO:
    buffer = io.BytesIO()
    rows = []
    for r in records:
        row = {
            "Record ID": r.get("id"),
            "Student Name": r.get("student_name"),
            "Admission No": r.get("admission_no"),
            "Register No": r.get("register_no"),
            "Roll / Sl No": r.get("roll_no"),
            "Course": r.get("class_course"),
            "Gender": r.get("gender"),
            "DOB": r.get("dob"),
            "Father Name": r.get("father_name"),
            "Mother Name": r.get("mother_name"),
            "Category": r.get("category"),
            "Religion": r.get("religion"),
            "Source File": r.get("source_file"),
            "Page / Sheet": r.get("page_or_sheet")
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Nominal Search Results')
        
    buffer.seek(0)
    return buffer
