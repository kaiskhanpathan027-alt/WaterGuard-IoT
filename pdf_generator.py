"""
PDF Report Generator for Water Quality Monitoring System.
Produces an attractive, official, publication-quality Water Potability Certificate and Laboratory Report.
Features WaterGuard IoT branding, vector graphical parameter gauges, WHO/BIS benchmark tables,
academic project credentials, and user custom username details.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle, Group
from water_quality import analyze_water_sample

def create_brand_logo_drawing():
    """Generates an embedded vector WaterGuard IoT logo badge."""
    d = Drawing(160, 42)
    # Background rounded container
    d.add(Rect(0, 4, 155, 34, rx=6, ry=6, fillColor=colors.HexColor('#f0f9ff'), strokeColor=colors.HexColor('#0284c7'), strokeWidth=1))
    
    # Droplet icon circle
    d.add(Circle(20, 21, 12, fillColor=colors.HexColor('#0284c7'), strokeColor=None))
    
    # Droplet vector
    d.add(Polygon(points=[20, 30, 14, 21, 20, 14, 26, 21], fillColor=colors.white, strokeColor=None))
    
    # Text
    d.add(String(38, 24, "WaterGuard", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#0c4a6e')))
    d.add(String(104, 24, "IoT", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#0284c7')))
    d.add(String(38, 12, "SMART WATER QUALITY", fontName="Helvetica", fontSize=5.5, fillColor=colors.HexColor('#64748b')))
    return d

def create_parameter_gauge(name, val, min_val, max_val, safe_min, safe_max, unit, status):
    """
    Renders an in-line graphical horizontal bar gauge for a parameter, showing
    Safe / Moderate / Unsafe zones and a visual needle marker pointing to the measured value.
    """
    bar_width = 320
    bar_height = 10
    total_w = 480
    total_h = 32
    d = Drawing(total_w, total_h)

    # Label
    d.add(String(0, 18, f"{name}: {val} {unit}", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor('#0f172a')))

    # Background track start X
    start_x = 145
    y_pos = 16

    # Normalization helper
    def to_x(v):
        clamped = max(min_val, min(max_val, v))
        return start_x + ((clamped - min_val) / (max_val - min_val)) * bar_width

    # Draw color zones based on parameter
    if name == "pH Level":
        # 0 to 6.0: Unsafe (Red), 6.0 to 6.5: Moderate (Amber), 6.5 to 8.5: Safe (Green), 8.5 to 9.0: Moderate, >9.0: Unsafe
        x0 = to_x(min_val)
        x_un1 = to_x(6.0)
        x_mod1 = to_x(6.5)
        x_safe = to_x(8.5)
        x_mod2 = to_x(9.0)
        x_end = to_x(max_val)

        d.add(Rect(x0, y_pos, x_un1 - x0, bar_height, fillColor=colors.HexColor('#fecaca'), strokeColor=None))
        d.add(Rect(x_un1, y_pos, x_mod1 - x_un1, bar_height, fillColor=colors.HexColor('#fde68a'), strokeColor=None))
        d.add(Rect(x_mod1, y_pos, x_safe - x_mod1, bar_height, fillColor=colors.HexColor('#a7f3d0'), strokeColor=None))
        d.add(Rect(x_safe, y_pos, x_mod2 - x_safe, bar_height, fillColor=colors.HexColor('#fde68a'), strokeColor=None))
        d.add(Rect(x_mod2, y_pos, x_end - x_mod2, bar_height, fillColor=colors.HexColor('#fecaca'), strokeColor=None))
    elif name == "Total Dissolved Solids (TDS)":
        # 0 to 500: Safe (Green), 500 to 900: Moderate (Amber), 900 to 1500: Unsafe (Red)
        x0 = to_x(min_val)
        x_safe = to_x(500)
        x_mod = to_x(900)
        x_end = to_x(max_val)

        d.add(Rect(x0, y_pos, x_safe - x0, bar_height, fillColor=colors.HexColor('#a7f3d0'), strokeColor=None))
        d.add(Rect(x_safe, y_pos, x_mod - x_safe, bar_height, fillColor=colors.HexColor('#fde68a'), strokeColor=None))
        d.add(Rect(x_mod, y_pos, x_end - x_mod, bar_height, fillColor=colors.HexColor('#fecaca'), strokeColor=None))
    else: # Turbidity
        # 0 to 5.0: Safe (Green), 5.0 to 10.0: Moderate (Amber), 10.0 to 25.0: Unsafe (Red)
        x0 = to_x(min_val)
        x_safe = to_x(5.0)
        x_mod = to_x(10.0)
        x_end = to_x(max_val)

        d.add(Rect(x0, y_pos, x_safe - x0, bar_height, fillColor=colors.HexColor('#a7f3d0'), strokeColor=None))
        d.add(Rect(x_safe, y_pos, x_mod - x_safe, bar_height, fillColor=colors.HexColor('#fde68a'), strokeColor=None))
        d.add(Rect(x_mod, y_pos, x_end - x_mod, bar_height, fillColor=colors.HexColor('#fecaca'), strokeColor=None))

    # Border around bar
    d.add(Rect(start_x, y_pos, bar_width, bar_height, fillColor=None, strokeColor=colors.HexColor('#94a3b8'), strokeWidth=0.75))

    # Indicator Pointer
    marker_x = to_x(float(val))
    marker_color = colors.HexColor('#10b981') if status == 'Safe' else (colors.HexColor('#f59e0b') if status == 'Moderate' else colors.HexColor('#ef4444'))
    
    # Diamond / Triangle pointer
    d.add(Polygon(points=[marker_x, y_pos + bar_height + 4, marker_x - 3.5, y_pos + bar_height + 9, marker_x + 3.5, y_pos + bar_height + 9], fillColor=marker_color, strokeColor=colors.HexColor('#0f172a'), strokeWidth=0.5))
    d.add(Line(marker_x, y_pos - 2, marker_x, y_pos + bar_height + 3, strokeColor=marker_color, strokeWidth=1.5))

    # Text legends under bar
    d.add(String(start_x, y_pos - 8, f"{min_val}", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748b')))
    d.add(String(start_x + (bar_width / 2) - 15, y_pos - 8, "WHO Standard Range", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#047857')))
    d.add(String(start_x + bar_width - 15, y_pos - 8, f"{max_val}", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748b')))

    return d

def create_wqi_scale_drawing(wqi_score, status):
    """Draws a visual 0-100 WQI index graphical spectrum with pointer."""
    total_w = 480
    bar_w = 420
    bar_h = 10
    start_x = 30
    y_pos = 14
    d = Drawing(total_w, 34)

    # Red zone: 0 to 50
    w_red = (50 / 100) * bar_w
    d.add(Rect(start_x, y_pos, w_red, bar_h, fillColor=colors.HexColor('#fecaca'), strokeColor=None))
    
    # Yellow zone: 50 to 80
    w_yellow = (30 / 100) * bar_w
    d.add(Rect(start_x + w_red, y_pos, w_yellow, bar_h, fillColor=colors.HexColor('#fde68a'), strokeColor=None))

    # Green zone: 80 to 100
    w_green = (20 / 100) * bar_w
    d.add(Rect(start_x + w_red + w_yellow, y_pos, w_green, bar_h, fillColor=colors.HexColor('#a7f3d0'), strokeColor=None))

    # Border
    d.add(Rect(start_x, y_pos, bar_w, bar_h, fillColor=None, strokeColor=colors.HexColor('#64748b'), strokeWidth=0.8))

    # Marker
    clamped_wqi = max(0, min(100, float(wqi_score)))
    marker_x = start_x + (clamped_wqi / 100) * bar_w
    marker_color = colors.HexColor('#10b981') if status == 'Safe' else (colors.HexColor('#f59e0b') if status == 'Moderate' else colors.HexColor('#ef4444'))

    d.add(Polygon(points=[marker_x, y_pos + bar_h + 3, marker_x - 4, y_pos + bar_h + 9, marker_x + 4, y_pos + bar_h + 9], fillColor=marker_color, strokeColor=colors.black, strokeWidth=0.5))
    d.add(Line(marker_x, y_pos - 2, marker_x, y_pos + bar_h + 2, strokeColor=marker_color, strokeWidth=2))

    # Labels
    d.add(String(start_x, y_pos - 8, "0 (Unsafe)", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#b91c1c')))
    d.add(String(start_x + w_red - 8, y_pos - 8, "50 (Moderate)", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#b45309')))
    d.add(String(start_x + w_red + w_yellow - 8, y_pos - 8, "80 (Safe / Potable)", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#047857')))
    d.add(String(start_x + bar_w - 15, y_pos - 8, "100", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#047857')))

    return d

def generate_water_report_pdf(test_data):
    """
    Generates a certified, publication-quality Water Potability Certificate and Laboratory Report.
    Returns: BytesIO buffer containing the PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()

    # Typography styles
    inst_title_style = ParagraphStyle(
        'InstTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15,
        textColor=colors.HexColor('#0369a1'),
        alignment=1
    )

    inst_sub_style = ParagraphStyle(
        'InstSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155'),
        alignment=1
    )

    proj_title_style = ParagraphStyle(
        'ProjTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0c4a6e'),
        alignment=1
    )

    cert_banner_style = ParagraphStyle(
        'CertBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        alignment=1
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=7,
        spaceAfter=3
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )

    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    cell_text = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=9.5,
        textColor=colors.HexColor('#1e293b')
    )

    cell_center = ParagraphStyle(
        'CellCenter',
        parent=cell_text,
        alignment=1
    )

    cell_bold_center = ParagraphStyle(
        'CellBoldCenter',
        parent=cell_text,
        fontName='Helvetica-Bold',
        alignment=1
    )

    elements = []

    # 1. Header with Embedded WaterGuard IoT Logo & Academic Accreditation
    logo_drawing = create_brand_logo_drawing()
    header_table_data = [
        [
            logo_drawing,
            [
                Paragraph("MAHARASHTRA INSTITUTE OF TECHNOLOGY, CHHATRAPATI SAMBHAJINAGAR", inst_title_style),
                Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND DESIGN &bull; ACADEMIC YEAR 2026–2027", inst_sub_style),
                Paragraph("SMART WATER QUALITY MONITORING &amp; ANALYSIS SYSTEM", proj_title_style),
                Paragraph("Project Guide: <b>Vaishali Gaikwad Mam</b> &bull; WHO &amp; BIS IS 10500 Compliant", inst_sub_style)
            ]
        ]
    ]

    header_table = Table(header_table_data, colWidths=[140, 400])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=5))

    # Certificate Title & Unique Report ID
    report_id = f"WQ-2026-REP-{int(test_data['id']):05d}"
    elements.append(Paragraph(f"WATER POTABILITY ANALYSIS CERTIFICATE &bull; REPORT ID: <b>{report_id}</b>", cert_banner_style))
    elements.append(Spacer(1, 5))

    # Scientific analysis computation
    analysis = analyze_water_sample(test_data['ph'], test_data['tds'], test_data['turbidity'])
    status = analysis['overall_status']
    wqi = analysis['wqi_score']

    if status == 'Safe':
        banner_bg = colors.HexColor('#ecfdf5')
        banner_border = colors.HexColor('#10b981')
        badge_text_color = colors.HexColor('#047857')
        status_display = "SAFE FOR CONSUMPTION (POTABLE)"
    elif status == 'Moderate':
        banner_bg = colors.HexColor('#fffbeb')
        banner_border = colors.HexColor('#f59e0b')
        badge_text_color = colors.HexColor('#b45309')
        status_display = "MODERATE QUALITY (TREATMENT ADVISED)"
    else:
        banner_bg = colors.HexColor('#fef2f2')
        banner_border = colors.HexColor('#ef4444')
        badge_text_color = colors.HexColor('#b91c1c')
        status_display = "UNSAFE / HAZARDOUS (NON-POTABLE)"

    # Status & WQI Summary Card Table
    status_card_data = [
        [
            Paragraph(f"<b>STATUS VERDICT:</b> <font color='{badge_text_color.hexval()}'><b>{status_display}</b></font>", meta_label),
            Paragraph(f"<b>Water Quality Index (WQI):</b> <font size='11' color='{badge_text_color.hexval()}'><b>{wqi} / 100</b></font>", ParagraphStyle('R', parent=meta_label, alignment=2))
        ],
        [
            Paragraph(f"<i>{analysis['summary_desc']}</i>", ParagraphStyle('D', parent=cell_text, textColor=colors.HexColor('#334155'))),
            Paragraph("<b>Potability Scale:</b> 80-100 (Safe) | 50-79 (Moderate) | &lt;50 (Unsafe)", ParagraphStyle('S', parent=cell_text, alignment=2, fontSize=7))
        ]
    ]

    status_table = Table(status_card_data, colWidths=[360, 180])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), banner_bg),
        ('BOX', (0, 0), (-1, -1), 1.5, banner_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 6))

    # 2. Sample & Testing Details Table with Custom Username
    elements.append(Paragraph("1. SAMPLE, ANALYST &amp; ACADEMIC SPECIFICATIONS", section_heading))
    
    # Format user display: full name and custom username
    user_name = test_data.get('user_full_name') or test_data.get('tested_by') or test_data.get('username') or 'Student Analyst'
    custom_uname = test_data.get('custom_username') or test_data.get('username') or 'user@water.guard'

    meta_table_data = [
        [
            Paragraph("<b>Sample Designation:</b>", meta_label),
            Paragraph(str(test_data['sample_name']), meta_val),
            Paragraph("<b>Report ID &amp; Sample #:</b>", meta_label),
            Paragraph(f"{report_id} (#{test_data['id']})", meta_val),
        ],
        [
            Paragraph("<b>Sampling Location:</b>", meta_label),
            Paragraph(str(test_data['location']), meta_val),
            Paragraph("<b>Source Category:</b>", meta_label),
            Paragraph(str(test_data['source_type']), meta_val),
        ],
        [
            Paragraph("<b>Analyst Name:</b>", meta_label),
            Paragraph(str(user_name), meta_val),
            Paragraph("<b>Custom Username:</b>", meta_label),
            Paragraph(f"<code>{custom_uname}</code>", ParagraphStyle('CodeU', parent=meta_val, fontName='Helvetica-Bold', textColor=colors.HexColor('#0284c7'))),
        ],
        [
            Paragraph("<b>Testing Timestamp:</b>", meta_label),
            Paragraph(str(test_data['created_at']), meta_val),
            Paragraph("<b>Project Guide:</b>", meta_label),
            Paragraph("Vaishali Gaikwad Mam", meta_val),
        ],
        [
            Paragraph("<b>Project Developers:</b>", meta_label),
            Paragraph("Kais Khan Fakirmat Khan &amp; Rajeshwar Sandip Gaurkar", meta_val),
            Paragraph("<b>Institution / Dept:</b>", meta_label),
            Paragraph("MIT Chhatrapati Sambhajinagar (CSD)", meta_val),
        ]
    ]

    meta_table = Table(meta_table_data, colWidths=[105, 185, 110, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 6))

    # 3. Parameters Table
    elements.append(Paragraph("2. ANALYTICAL PARAMETER MEASUREMENTS vs. WHO / BIS STANDARDS", section_heading))

    param_rows = [
        [
            Paragraph("Parameter", table_header),
            Paragraph("Measured Value", table_header),
            Paragraph("WHO / BIS Standard", table_header),
            Paragraph("Sub-Index", table_header),
            Paragraph("Compliance", table_header),
            Paragraph("Health &amp; Sensory Evaluation", table_header)
        ]
    ]

    params_info = analysis['parameters']
    for p_key in ['ph', 'tds', 'turbidity']:
        p = params_info[p_key]
        if p['status'] == 'Safe':
            status_chip = f"<font color='#047857'><b>SAFE</b></font>"
        elif p['status'] == 'Moderate':
            status_chip = f"<font color='#b45309'><b>MODERATE</b></font>"
        else:
            status_chip = f"<font color='#b91c1c'><b>UNSAFE</b></font>"

        param_rows.append([
            Paragraph(f"<b>{p['name']}</b>", cell_text),
            Paragraph(f"<b>{p['value']} {p['unit']}</b>", cell_bold_center),
            Paragraph(p['standard'], cell_center),
            Paragraph(p['label'], cell_center),
            Paragraph(status_chip, cell_center),
            Paragraph(p['detail'], cell_text)
        ])

    param_table = Table(param_rows, colWidths=[90, 80, 85, 75, 65, 145])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(param_table)
    elements.append(Spacer(1, 6))

    # 4. Graphs and Charts (Visual Parameter Gauges)
    elements.append(Paragraph("3. GRAPHICAL PARAMETER TELEMETRY &amp; RANGE CHARTS", section_heading))

    ph_gauge = create_parameter_gauge("pH Level", test_data['ph'], 3.0, 11.0, 6.5, 8.5, "pH", params_info['ph']['status'])
    tds_gauge = create_parameter_gauge("Total Dissolved Solids (TDS)", test_data['tds'], 0, 1500, 0, 500, "mg/L", params_info['tds']['status'])
    turb_gauge = create_parameter_gauge("Optical Turbidity", test_data['turbidity'], 0, 25.0, 0, 5.0, "NTU", params_info['turbidity']['status'])
    wqi_gauge = create_wqi_scale_drawing(wqi, status)

    chart_table_data = [
        [
            Paragraph("<b>WQI Index Position:</b>", meta_label),
            wqi_gauge
        ],
        [
            Paragraph("<b>pH Telemetry:</b>", meta_label),
            ph_gauge
        ],
        [
            Paragraph("<b>TDS Telemetry:</b>", meta_label),
            tds_gauge
        ],
        [
            Paragraph("<b>Turbidity Telemetry:</b>", meta_label),
            turb_gauge
        ]
    ]

    chart_table = Table(chart_table_data, colWidths=[90, 450])
    chart_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(chart_table)
    elements.append(Spacer(1, 6))

    # 5. Treatment Protocol
    elements.append(Paragraph("4. RECOMMENDED REMEDIATION &amp; WATER TREATMENT PROTOCOL", section_heading))

    recs_data = []
    for rec in analysis['recommendations']:
        recs_data.append([
            Paragraph(f"&bull; <b>{rec['title']}:</b> {rec['body']}", cell_text)
        ])

    recs_table = Table(recs_data, colWidths=[540])
    recs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#bae6fd')),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(recs_table)
    elements.append(Spacer(1, 8))

    # 6. Official Sign-off and Verification Footer
    sig_data = [
        [
            Paragraph("<b>Student Investigator:</b><br/><br/>____________________________<br/><b>Kais Khan Fakirmat Khan</b><br/>Dept. of Computer Science &amp; Design", cell_center),
            Paragraph("<b>Student Investigator:</b><br/><br/>____________________________<br/><b>Rajeshwar Sandip Gaurkar</b><br/>Dept. of Computer Science &amp; Design", cell_center),
            Paragraph("<b>Project Guide:</b><br/><br/>____________________________<br/><b>Vaishali Gaikwad Mam</b><br/>Faculty Project Supervisor", cell_center),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[180, 180, 180])
    sig_table.setStyle(TableStyle([
        ('PADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)

    elements.append(Spacer(1, 6))
    footer_text = Paragraph(
        "<i>* This official water potability report was generated by the Smart Water Quality Monitoring &amp; Analysis System (WaterGuard IoT). Developed by Kais Khan Fakirmat Khan &amp; Rajeshwar Sandip Gaurkar under the guidance of Vaishali Gaikwad Mam, Department of Computer Science and Design, Maharashtra Institute of Technology, Chhatrapati Sambhajinagar, Maharashtra (Academic Year 2026–2027). Standards: WHO Guidelines &amp; BIS IS 10500:2012.</i>",
        ParagraphStyle('F', parent=cell_text, fontSize=5.8, leading=7.5, textColor=colors.HexColor('#64748b'), alignment=1)
    )
    elements.append(footer_text)

    doc.build(elements)
    buffer.seek(0)
    return buffer
