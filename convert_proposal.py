import re
import os

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
                # Strip the bold markers
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

def format_body_to_html(body_lines):
    html_lines = []
    in_list = False
    in_table = False
    table_headers = []
    
    for line in body_lines:
        stripped = line.strip()
        
        # Lists
        if (stripped.startswith('* ') or stripped.startswith('- ') or re.match(r'^\d+\.', stripped)):
            if not in_list:
                html_lines.append('<ul class="paper-list">')
                in_list = True
            # Strip list prefix
            if stripped.startswith('* ') or stripped.startswith('- '):
                content = stripped[2:]
            else:
                match = re.match(r'^\d+\.\s*(.*)', stripped)
                content = match.group(1) if match else stripped
                
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
            html_lines.append(f'<li>{content}</li>')
            continue
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
                
        # Horizontal lines
        if stripped == '---':
            html_lines.append('<hr class="section-divider" />')
            continue
            
        # Section Headings (Roman numerals)
        if stripped.startswith('# I') or stripped.startswith('# V') or stripped.startswith('# ACKNOWLEDGMENT') or stripped.startswith('# REFERENCES'):
            content = stripped[2:] if stripped.startswith('# ') else stripped[1:]
            html_lines.append(f'<h2 class="section-heading">{content}</h2>')
            continue
            
        # Subsections (3.1, 3.2, etc. or A., B., C.)
        if stripped.startswith('## '):
            content = stripped[3:]
            html_lines.append(f'<h3 class="subsection-heading">{content}</h3>')
            continue
            
        # Tables
        if stripped.startswith('|'):
            if not in_table:
                html_lines.append('<table class="paper-table">')
                in_table = True
            if ':---' in stripped or '---:' in stripped:
                continue
                
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            formatted_cells = []
            for cell in cells:
                c = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', cell)
                c = re.sub(r'\*(.*?)\*', r'<em>\1</em>', c)
                c = re.sub(r'`(.*?)`', r'<code>\1</code>', c)
                formatted_cells.append(c)
                
            if len(table_headers) == 0:
                table_headers = formatted_cells
                html_lines.append('<thead><tr>')
                for h in table_headers:
                    html_lines.append(f'<th>{h}</th>')
                html_lines.append('</tr></thead><tbody>')
            else:
                html_lines.append('<tr>')
                for c in formatted_cells:
                    html_lines.append(f'<td>{c}</td>')
                html_lines.append('</tr>')
            continue
        else:
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False
                table_headers = []
                
        if not stripped:
            html_lines.append('<br/>')
            continue
            
        # Standard paragraph formatting
        p_content = stripped
        p_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_content)
        p_content = re.sub(r'`(.*?)`', r'<code>\1</code>', p_content)
        html_lines.append(f'<p class="paper-text">{p_content}</p>')
        
    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</tbody></table>')
        
    return '\n'.join(html_lines)

def build_html():
    proposal_path = 'proposal.md'
    if not os.path.exists(proposal_path):
        print("Error: proposal.md not found.")
        return

    with open(proposal_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    title, authors, abstract_paragraphs, keywords, body_lines = parse_markdown_paper(md_content)
    
    # Format author block
    authors_html = []
    for author in authors:
        # Expected structure: Name, dept, university, position, location, email
        name = author[0] if len(author) > 0 else ""
        dept = author[1] if len(author) > 1 else ""
        univ = author[2] if len(author) > 2 else ""
        pos = author[3] if len(author) > 3 else ""
        loc = author[4] if len(author) > 4 else ""
        email = author[5] if len(author) > 5 else ""
        
        authors_html.append(f"""
        <div class="author-col">
            <div class="author-name">{name}</div>
            <div class="author-dept">{dept}</div>
            <div class="author-univ">{univ}</div>
            <div class="author-pos">{pos}</div>
            <div class="author-loc">{loc}</div>
            <div class="author-email"><a href="mailto:{email}">{email}</a></div>
        </div>
        """)
        
    authors_block = '\n'.join(authors_html)
    
    # Format abstract block
    abstract_content = []
    for p in abstract_paragraphs:
        abstract_content.append(f'<p class="abstract-text">{p}</p>')
    abstract_block = '\n'.join(abstract_content)
    
    body_html = format_body_to_html(body_lines)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Times New Roman', Times, serif;
            color: #000000;
            background-color: #FFFFFF;
            margin: 0;
            padding: 40px;
        }}
        .paper-container {{
            max-width: 960px;
            margin: 0 auto;
        }}
        .paper-title {{
            font-size: 24pt;
            font-weight: normal;
            text-align: center;
            margin-bottom: 25px;
            color: #000000;
        }}
        .authors-row {{
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin-bottom: 30px;
            font-size: 10pt;
        }}
        .author-col {{
            flex: 1;
            padding: 0 10px;
            line-height: 1.3;
        }}
        .author-name {{
            font-size: 11pt;
            margin-bottom: 2px;
        }}
        .author-dept, .author-univ {{
            font-style: italic;
        }}
        .author-email a {{
            color: #1E3A8A;
            text-decoration: none;
        }}
        .author-email a:hover {{
            text-decoration: underline;
        }}
        
        /* Two column layout for abstract + body */
        .two-column-layout {{
            column-count: 2;
            column-gap: 24px;
            text-align: justify;
            font-size: 10pt;
            line-height: 1.25;
        }}
        
        .abstract-block {{
            margin-bottom: 15px;
        }}
        .abstract-text {{
            font-weight: bold;
            text-indent: 0;
            margin: 0 0 10px 0;
        }}
        .keywords-text {{
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .section-heading {{
            font-size: 11pt;
            font-weight: bold;
            text-align: center;
            text-transform: uppercase;
            margin-top: 22px;
            margin-bottom: 10px;
            column-span: none;
            page-break-after: avoid;
        }}
        
        .subsection-heading {{
            font-size: 10pt;
            font-style: italic;
            font-weight: bold;
            text-align: left;
            margin-top: 15px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}
        
        .paper-text {{
            text-indent: 18px;
            margin: 0 0 8px 0;
        }}
        
        .paper-list {{
            margin: 0 0 10px 0;
            padding-left: 20px;
        }}
        .paper-list li {{
            margin-bottom: 4px;
        }}
        
        .paper-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 8.5pt;
            column-span: all;
        }}
        .paper-table th, .paper-table td {{
            border: 1px solid #000000;
            padding: 6px;
            text-align: left;
        }}
        .paper-table th {{
            font-weight: bold;
            background-color: #F3F4F6;
        }}
        
        .section-divider {{
            border: 0;
            height: 0.5px;
            background: #000000;
            margin: 20px 0;
        }}
        
        @media print {{
            body {{
                padding: 0;
            }}
            .paper-container {{
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="paper-container">
        <h1 class="paper-title">{title}</h1>
        <div class="authors-row">
            {authors_block}
        </div>
        
        <hr class="section-divider" />
        
        <div class="two-column-layout">
            <div class="abstract-block">
                {abstract_block}
                <p class="keywords-text">{keywords}</p>
            </div>
            
            {body_html}
        </div>
    </div>
</body>
</html>"""

    with open('proposal.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("Success: proposal.html updated.")

if __name__ == '__main__':
    build_html()
