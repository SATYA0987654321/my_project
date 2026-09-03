import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def generate_pdf(
    name,
    phone,
    email,
    location,
    linkedin,
    objective,
    education,
    languages,
    database,       # Added database parameter
    tools,
    concepts,
    projects,        # list of dicts: [{"title": "...", "desc": "..."}]
    achievements,
    activities,
    extra_curricular, # Added extra_curricular parameter
    template="Classic ATS",
    filename="ATS_Resume.pdf"
):
    # Setup document
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # Determine colors & alignment based on template selection
    if template == "Modern Minimalist":
        header_align = 0  # Left-aligned
        name_color = colors.HexColor('#0F172A')     # Sleek Slate 900
        contact_color = colors.HexColor('#64748B')  # Slate 500
        heading_color = colors.HexColor('#1E3A8A')  # Deep Navy Accent
        body_color = colors.HexColor('#334155')     # Slate 700
        has_dividers = True
        divider_color = colors.HexColor('#E2E8F0')  # Very light subtle divider
        uppercase_headings = False                   # Modern clean text
        extra_space = 10
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
        divider_thickness = 0.5
    elif template == "Elegant Executive":
        header_align = 1  # Centered
        name_color = colors.HexColor('#1E3A8A')     # Deep Navy
        contact_color = colors.HexColor('#475569')  # Slate Gray
        heading_color = colors.HexColor('#1E3A8A')  # Deep Navy Accent
        body_color = colors.HexColor('#1E293B')     # Slate 800
        has_dividers = True
        divider_color = colors.HexColor('#1E3A8A')  # Navy divider
        uppercase_headings = True
        extra_space = 8
        font_name = 'Times-Roman'
        font_name_bold = 'Times-Bold'
        divider_thickness = 1.25                     # Thicker divider
    else:  # "Classic ATS"
        header_align = 1  # Centered
        name_color = colors.HexColor('#1E293B')     # Dark Slate
        contact_color = colors.HexColor('#475569')  # Slate Gray
        heading_color = colors.HexColor('#1E293B')  # Dark Slate
        body_color = colors.HexColor('#334155')     # Charcoal
        has_dividers = True
        divider_color = colors.HexColor('#64748B')  # Gray divider
        uppercase_headings = True
        extra_space = 8
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
        divider_thickness = 0.75

    # Create paragraph styles
    name_style = ParagraphStyle(
        'ResumeName',
        parent=styles['Normal'],
        fontName=font_name_bold,
        fontSize=20,
        leading=24,
        textColor=name_color,
        alignment=header_align,
        spaceAfter=6
    )

    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9.5,
        leading=13,
        textColor=contact_color,
        alignment=header_align,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        'ResumeHeading',
        parent=styles['Normal'],
        fontName=font_name_bold,
        fontSize=11.5,
        leading=14,
        textColor=heading_color,
        spaceBefore=12,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9.5,
        leading=14,
        textColor=body_color,
        spaceAfter=4
    )

    # Indented hanging bullets (Level 1)
    bullet_l1_style = ParagraphStyle(
        'BulletL1',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    # Level 2 Indented key-values (for skills and project Tech:)
    tech_l2_style = ParagraphStyle(
        'TechL2',
        parent=body_style,
        leftIndent=25,
        spaceAfter=2
    )

    # Level 2 Indented bullets (for project descriptions)
    bullet_l2_style = ParagraphStyle(
        'BulletL2',
        parent=body_style,
        leftIndent=35,
        firstLineIndent=-10,
        spaceAfter=2
    )

    content = []

    # Helper function to append section header
    def add_section_header(title):
        display_title = title.upper() if uppercase_headings else title
        content.append(Paragraph(display_title, heading_style))
        
        if has_dividers:
            # Thin divider line
            divider = Table([['']], colWidths=[532], rowHeights=[1])
            divider.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (-1, -1), divider_thickness, divider_color),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            content.append(divider)
            content.append(Spacer(1, 6))
        else:
            content.append(Spacer(1, 4))

    # Helper function to add standard level 1 bullet points
    def add_bullet_point(text):
        clean_line = text.strip()
        if clean_line.startswith("•"):
            clean_line = clean_line[1:].strip()
        elif clean_line.startswith("-"):
            clean_line = clean_line[1:].strip()
        if clean_line:
            content.append(Paragraph(f"&bull; {clean_line}", bullet_l1_style))

    # Get absolute paths to the generated contact icons
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(utils_dir)
    phone_icon = os.path.join(workspace_dir, "assets", "phone_icon.png")
    email_icon = os.path.join(workspace_dir, "assets", "email_icon.png")
    location_icon = os.path.join(workspace_dir, "assets", "location_icon.png")

    # HEADER SECTION
    if name.strip():
        content.append(Paragraph(name.strip(), name_style))

    contact_items = []
    # Build inline image tag strings if icons are found
    if phone.strip():
        p_str = f'<img src="{phone_icon}" width="10" height="10" valign="middle"/> &nbsp;{phone.strip()}' if os.path.exists(phone_icon) else phone.strip()
        contact_items.append(p_str)
    if email.strip():
        e_str = f'<img src="{email_icon}" width="11" height="9" valign="middle"/> &nbsp;{email.strip()}' if os.path.exists(email_icon) else email.strip()
        contact_items.append(e_str)
    if location.strip():
        l_str = f'<img src="{location_icon}" width="9" height="11" valign="middle"/> &nbsp;{location.strip()}' if os.path.exists(location_icon) else location.strip()
        contact_items.append(l_str)

    if contact_items:
        # Separate details with larger spacing
        contact_line = " &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join(contact_items)
        content.append(Paragraph(contact_line, contact_style))

    # Bottom border under the header
    divider = Table([['']], colWidths=[532], rowHeights=[1])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), divider_thickness, divider_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    content.append(divider)
    content.append(Spacer(1, 10))

    # CAREER OBJECTIVE
    if objective.strip():
        add_section_header("Career Objective")
        content.append(Paragraph(objective.strip(), body_style))
        content.append(Spacer(1, extra_space))

    # EDUCATION
    if education.strip():
        add_section_header("Education")
        edu_lines = [line.strip() for line in education.split('\n') if line.strip()]
        for line in edu_lines:
            # Parse line for right-aligned date token splitting using '|'
            if '|' in line:
                parts = line.split('|')
                last_part = parts[-1].strip()
                # If last part looks like a date range or year, align it to the right
                if len(last_part) <= 15 and any(char.isdigit() for char in last_part):
                    left_text = " | ".join(parts[:-1]).strip()
                    right_text = last_part
                else:
                    left_text = line
                    right_text = ""
            else:
                left_text = line
                right_text = ""

            if right_text:
                # 2-column table to align degree details to the left and date to the right
                t = Table([[
                    Paragraph(left_text, body_style),
                    Paragraph(right_text, ParagraphStyle('RightText', parent=body_style, alignment=2))
                ]], colWidths=[430, 102])
                t.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                ]))
                content.append(t)
            else:
                content.append(Paragraph(left_text, body_style))
        content.append(Spacer(1, extra_space))

    # AWARDS & ACHIEVEMENTS
    if achievements.strip():
        add_section_header("Awards & Achievements")
        ach_lines = [line.strip() for line in achievements.split('\n') if line.strip()]
        for line in ach_lines:
            add_bullet_point(line)
        content.append(Spacer(1, extra_space))

    # KEY EXPERTISE & SKILLS (Nested bullet format)
    has_skills = languages.strip() or database.strip() or tools.strip() or concepts.strip()
    if has_skills:
        add_section_header("Key Expertise / Skills")
        
        # Level 1: Technical
        content.append(Paragraph("&bull; <b>Technical :</b>", bullet_l1_style))
        
        # Level 2 nested details
        if languages.strip():
            content.append(Paragraph(f"<b>Languages :</b> {languages.strip()}", tech_l2_style))
        if database.strip():
            content.append(Paragraph(f"<b>Database :</b> {database.strip()}", tech_l2_style))
        if tools.strip():
            content.append(Paragraph(f"<b>Libraries/Tools :</b> {tools.strip()}", tech_l2_style))
        if concepts.strip():
            content.append(Paragraph(f"<b>Concepts :</b> {concepts.strip()}", tech_l2_style))
            
        content.append(Spacer(1, extra_space))

    # PROJECTS
    valid_projects = [p for p in projects if p.get("title", "").strip() and p.get("desc", "").strip()]
    if valid_projects:
        add_section_header("Projects")
        for i, proj in enumerate(valid_projects):
            title = proj["title"].strip()
            desc = proj["desc"].strip()
            
            # Level 1: Project Name
            content.append(Paragraph(f"&bull; <b>{title}</b>", bullet_l1_style))
            
            # Level 2 details (bolds "Tech :" and indents description bullets further)
            proj_desc_lines = [line.strip() for line in desc.split('\n') if line.strip()]
            for line in proj_desc_lines:
                if line.lower().startswith("tech:"):
                    tech_val = line[5:].strip()
                    content.append(Paragraph(f"<b>Tech :</b> {tech_val}", tech_l2_style))
                elif line.lower().startswith("tech :"):
                    tech_val = line[6:].strip()
                    content.append(Paragraph(f"<b>Tech :</b> {tech_val}", tech_l2_style))
                else:
                    add_line = line
                    if add_line.startswith("•"):
                        add_line = add_line[1:].strip()
                    elif add_line.startswith("-"):
                        add_line = add_line[1:].strip()
                    content.append(Paragraph(f"&bull; {add_line}", bullet_l2_style))
            
            if i < len(valid_projects) - 1:
                content.append(Spacer(1, 4))
        content.append(Spacer(1, extra_space))

    # CO-CURRICULAR ACTIVITIES
    if activities.strip():
        add_section_header("Co-Curricular Activities")
        act_lines = [line.strip() for line in activities.split('\n') if line.strip()]
        for line in act_lines:
            add_bullet_point(line)
        content.append(Spacer(1, extra_space))

    # EXTRA CURRICULAR ACTIVITIES
    if extra_curricular.strip():
        add_section_header("Extra Curricular Activities")
        ec_lines = [line.strip() for line in extra_curricular.split('\n') if line.strip()]
        for line in ec_lines:
            add_bullet_point(line)
        content.append(Spacer(1, extra_space))

    # WEBLINKS
    if linkedin.strip():
        add_section_header("Weblinks")
        content.append(Paragraph(f"<b>LinkedIn :</b> {linkedin.strip()}", body_style))

    # Build the document
    doc.build(content)

    return filename


def generate_skill_gap_report_pdf(
    analysis_data: dict,
    user_name: str = "Candidate",
    filename: str = "Elevora_Skill_Gap_Report.pdf"
) -> str:
    """
    Generates a comprehensive executive Skill Gap & Career Readiness PDF Report.
    Includes composite score, TF-IDF semantic alignment, category breakdown,
    prioritized missing skills, and curated project roadmaps.
    """
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    primary_color = colors.HexColor('#7C3AED')
    dark_slate = colors.HexColor('#0F172A')
    light_slate = colors.HexColor('#64748B')
    success_color = colors.HexColor('#10B981')
    danger_color = colors.HexColor('#EF4444')
    border_color = colors.HexColor('#E2E8F0')
    
    title_style = ParagraphStyle(
        'RepTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color
    )
    
    subtitle_style = ParagraphStyle(
        'RepSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=light_slate
    )
    
    sec_header_style = ParagraphStyle(
        'RepSecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=dark_slate,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'RepBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_slate
    )

    story = []
    
    # 1. Header Banner
    header_table = Table([
        [
            Paragraph("<b>ELEVORA</b> | Career Intelligence Report", title_style),
            Paragraph(f"<b>Candidate:</b> {user_name}<br/><b>Target Role:</b> {analysis_data.get('job_role', 'N/A')}", subtitle_style)
        ]
    ], colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, primary_color)
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))
    
    # 2. Executive Score Summary
    score = analysis_data.get('composite_score', 0)
    tier = analysis_data.get('match_tier', 'Candidate Assessment')
    sub_scores = analysis_data.get('sub_scores', {})
    
    score_data = [
        [
            Paragraph(f"<font size=26 color='#7C3AED'><b>{score}%</b></font><br/><font size=8 color='#64748B'>COMPOSITE READINESS</font>", ParagraphStyle('CScore', alignment=1)),
            Paragraph(f"<b>Assessment Status:</b> {tier}<br/>"
                      f"<b>• Must-Have Skill Match:</b> {sub_scores.get('must_have_score', 0)}%<br/>"
                      f"<b>• Semantic TF-IDF Similarity:</b> {sub_scores.get('semantic_similarity', 0)}%<br/>"
                      f"<b>• ATS Format Quality:</b> {sub_scores.get('ats_format_score', 0)}%<br/>"
                      f"<b>• Quantifiable Impact Score:</b> {sub_scores.get('impact_score', 0)}%", body_style)
        ]
    ]
    score_table = Table(score_data, colWidths=[160, 380])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))
    
    # 3. Category Match Breakdown Table
    story.append(Paragraph("<b>1. Domain & Technical Category Breakdown</b>", sec_header_style))
    cat_breakdown = analysis_data.get('category_breakdown', [])
    if cat_breakdown:
        cat_table_data = [["Category", "Required", "Matched", "Match Rate (%)", "Status"]]
        for item in cat_breakdown:
            status = "Strong" if item['score'] >= 75 else ("Moderate" if item['score'] >= 40 else "Gap")
            cat_table_data.append([
                item['category'],
                str(item['required_count']),
                str(item['matched_count']),
                f"{item['score']}%",
                status
            ])
        cat_table = Table(cat_table_data, colWidths=[170, 70, 70, 110, 120])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDE9FE')),
            ('TEXTCOLOR', (0,0), (-1,0), primary_color),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(cat_table)
    story.append(Spacer(1, 14))
    
    # 4. Matched Skills vs Missing Skills Comparison
    story.append(Paragraph("<b>2. Skill Inventory & Critical Gaps</b>", sec_header_style))
    matched_str = ", ".join(analysis_data.get('matched_skills', [])) or "None detected"
    missing_must_str = ", ".join(analysis_data.get('missing_must_have', [])) or "None"
    missing_good_str = ", ".join(analysis_data.get('missing_good_to_have', [])) or "None"
    
    inventory_data = [
        [Paragraph("<b>Matched Skills:</b>", body_style), Paragraph(f"<font color='#10B981'>{matched_str}</font>", body_style)],
        [Paragraph("<b>Must-Have Gaps:</b>", body_style), Paragraph(f"<font color='#EF4444'><b>{missing_must_str}</b></font>", body_style)],
        [Paragraph("<b>Good-to-Have Gaps:</b>", body_style), Paragraph(f"<font color='#F59E0B'>{missing_good_str}</font>", body_style)]
    ]
    inv_table = Table(inventory_data, colWidths=[130, 410])
    inv_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(inv_table)
    story.append(Spacer(1, 14))
    
    # 5. Prioritized Learning Roadmaps
    story.append(Paragraph("<b>3. Actionable AI Learning Pathways & Project Recommendations</b>", sec_header_style))
    recs = analysis_data.get('structured_recommendations', [])
    if recs:
        rec_table_data = [["Skill & Priority", "Curated Concepts to Learn", "Resume Project Architecture", "Est. Time"]]
        for r in recs[:5]: # Top 5 critical items
            rec_table_data.append([
                Paragraph(f"<b>{r['skill']}</b><br/><font size=7 color='#7C3AED'>[{r['priority']}]</font>", body_style),
                Paragraph(r['topics'], body_style),
                Paragraph(r['project_idea'], body_style),
                Paragraph(r['estimated_time'], body_style)
            ])
        rec_table = Table(rec_table_data, colWidths=[110, 160, 200, 70])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(rec_table)
        
    doc.build(story)
    return filename