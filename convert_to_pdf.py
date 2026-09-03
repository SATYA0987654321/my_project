import os
import re
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, FrameBreak, NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def parse_markdown_paper(md_content):
    lines = md_content.split('\n')
    
    title = ""
    authors = []
    abstract_paragraphs = []
    keywords = ""
    body_lines = []
    
    phase = "title" # title, authors, abstract, body
    current_author = []
    
    for line in lines:
        stripped = line.strip()
        
        if phase == "title":
            if stripped.startswith('# '):
                title = stripped[2:]
                phase = "authors"
            continue
            
        elif phase == "authors":
            if stripped == '---':
                if current_author:
                    authors.append(current_author)
                phase = "abstract"
                continue
            if not stripped:
                if current_author:
                    authors.append(current_author)
                    current_author = []
            else:
                current_author.append(stripped)
            continue
            
        elif phase == "abstract":
            if stripped == '---':
                phase = "body"
                continue
            if stripped.startswith('**Abstract—'):
                cleaned = stripped.replace('**', '')
                abstract_paragraphs.append(cleaned)
            elif stripped.startswith('**Keywords—'):
                keywords = stripped.replace('**', '')
            elif stripped.startswith('**'):
                abstract_paragraphs.append(stripped.replace('**', ''))
            continue
            
        elif phase == "body":
            body_lines.append(line)
            
    return title, authors, abstract_paragraphs, keywords, body_lines

def compile_pdf():
    md_path = 'proposal.md'
    pdf_path = 'proposal.pdf'

    if not os.path.exists(md_path):
        print("Error: proposal.md not found.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    title, authors, abstract_paragraphs, keywords, body_lines = parse_markdown_paper(md_text)

    # Document dimensions (Letter: 612 x 792)
    # Margins: 40pt
    # Width = 532, Height = 712
    doc = BaseDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    # Columns calculation
    col_gap = 18
    col_width = (532 - col_gap) / 2 # 257

    # First Page Frames
    # Top frame for Title + Authors
    frame_first_top = Frame(40, 532, 532, 220, id='first_top', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    # Bottom columns for Abstract + beginning of text
    frame_first_col1 = Frame(40, 40, col_width, 477, id='first_col1', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_first_col2 = Frame(40 + col_width + col_gap, 40, col_width, 477, id='first_col2', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    # Later Pages Frames (Full 2-column layout)
    frame_later_col1 = Frame(40, 40, col_width, 712, id='col1', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_later_col2 = Frame(40 + col_width + col_gap, 40, col_width, 712, id='col2', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    template_first = PageTemplate(id='FirstPage', frames=[frame_first_top, frame_first_col1, frame_first_col2])
    template_later = PageTemplate(id='LaterPages', frames=[frame_later_col1, frame_later_col2])
    doc.addPageTemplates([template_first, template_later])

    styles = getSampleStyleSheet()

    # IEEE style formatting styles (Serif typeface Times-Roman)
    title_style = ParagraphStyle(
        'PaperTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.black,
        alignment=1, # Centered
        spaceAfter=15
    )

    author_cell_style = ParagraphStyle(
        'AuthorCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=1 # Centered
    )

    author_name_style = ParagraphStyle(
        'AuthorName',
        parent=author_cell_style,
        fontName='Times-Bold',
        fontSize=10.5,
        leading=13
    )

    abstract_style = ParagraphStyle(
        'PaperAbstract',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9,
        leading=12.5,
        textColor=colors.black,
        alignment=4, # Justified
        spaceAfter=6
    )

    keywords_style = ParagraphStyle(
        'PaperKeywords',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9,
        leading=12.5,
        textColor=colors.black,
        alignment=4,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.black,
        alignment=1, # Centered
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.black,
        alignment=0, # Left
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'PaperBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.black,
        alignment=4, # Justified
        firstLineIndent=14, # Standard IEEE paragraph indent
        spaceAfter=0
    )

    bullet_style = ParagraphStyle(
        'PaperBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=2
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8,
        leading=10,
        textColor=colors.black
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.black
    )

    story = [NextPageTemplate('LaterPages')]

    # 1. Add Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))

    # 2. Add Authors Row Table
    author_table_data = [[]]
    for author in authors:
        # Expected structure: Name, dept, university, position, location, email
        name = author[0] if len(author) > 0 else ""
        dept = author[1] if len(author) > 1 else ""
        univ = author[2] if len(author) > 2 else ""
        pos = author[3] if len(author) > 3 else ""
        loc = author[4] if len(author) > 4 else ""
        email = author[5] if len(author) > 5 else ""

        cell_flow = [
            Paragraph(name, author_name_style),
            Paragraph(f"<i>{dept}</i>", author_cell_style),
            Paragraph(f"<i>{univ}</i>", author_cell_style),
            Paragraph(pos, author_cell_style),
            Paragraph(loc, author_cell_style),
            Paragraph(f"<u>{email}</u>", author_cell_style)
        ]
        author_table_data[0].append(cell_flow)

    author_table = Table(author_table_data, colWidths=[177, 177, 177])
    author_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(author_table)
    
    # Break top frame to flow text into columns below
    story.append(FrameBreak())

    # 3. Add Abstract & Keywords
    for p in abstract_paragraphs:
        story.append(Paragraph(p, abstract_style))
    
    if keywords:
        story.append(Paragraph(keywords, keywords_style))

    # 4. Parse & Add Body Content
    def format_text(text):
        t = text.strip()
        t = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'\*(.*?)\*', r'<i>\1</i>', t)
        t = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', t)
        t = t.replace('&', '&amp;')
        return t

    in_table = False
    table_rows = []
    
    for line in body_lines:
        stripped = line.strip()

        # Skip horizontal dividers and raw mermaid tags in IEEE paper
        if stripped == '---' or stripped.startswith('```'):
            continue
        if 'graph TD' in line or '-->' in line or 'subgraph' in line or 'User([' in line or 'UI[' in line or 'AuthMgr[' in line:
            continue

        # Lists
        if (stripped.startswith('* ') or stripped.startswith('- ') or re.match(r'^\d+\.', stripped)):
            if stripped.startswith('* ') or stripped.startswith('- '):
                content = stripped[2:]
            else:
                match = re.match(r'^\d+\.\s*(.*)', stripped)
                content = match.group(1) if match else stripped
                
            formatted_content = format_text(content)
            story.append(Paragraph(f"&bull; {formatted_content}", bullet_style))
            continue

        # Headings
        if stripped.startswith('# I') or stripped.startswith('# V') or stripped.startswith('# ACKNOWLEDGMENT') or stripped.startswith('# REFERENCES'):
            h1_text = format_text(stripped[2:] if stripped.startswith('# ') else stripped[1:])
            story.append(Spacer(1, 10))
            story.append(Paragraph(h1_text, h1_style))
            continue
        elif stripped.startswith('## '):
            h2_text = format_text(stripped[3:])
            story.append(Spacer(1, 8))
            story.append(Paragraph(h2_text, h2_style))
            continue

        # Tables
        if stripped.startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            if ':---' in stripped or '---:' in stripped:
                continue
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            table_rows.append(cells)
            continue
        else:
            if in_table:
                formatted_data = []
                for i, row in enumerate(table_rows):
                    formatted_row = []
                    for cell in row:
                        cell_text = format_text(cell)
                        if i == 0:
                            formatted_row.append(Paragraph(cell_text, table_header_style))
                        else:
                            formatted_row.append(Paragraph(cell_text, table_cell_style))
                    formatted_data.append(formatted_row)
                
                # Full column width is 257 pt
                t = Table(formatted_data, colWidths=[90, 167])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 6))
                in_table = False
                table_rows = []

        if not stripped:
            continue

        p_text = format_text(stripped)
        if p_text:
            story.append(Paragraph(p_text, body_style))

    # Build PDF
    doc.build(story)
    print("Success: proposal.pdf updated in two-column format.")

if __name__ == '__main__':
    compile_pdf()
