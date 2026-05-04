#!/usr/bin/env python3
"""
Convert the manuscript markdown into three submission-ready .docx files:

  1. Manuscript.docx
       Main paper. Order: title page, abstract, introduction, methods,
       results, discussion, limitations, conclusions, acknowledgments,
       references, tables (Table 1, Table 2), figures (Figure 1-4 with
       images + legends).

  2. Supplementary_Tables.docx
       Supplementary Tables S1-S3 with descriptions and tabular content
       where size permits; full lookup tables noted as accompanying CSVs.

  3. Supplementary_Figures.docx
       Supplementary Figures S1-S3 with embedded images and legends.

Formatting: 12pt Times New Roman, double-spaced, 1-inch margins,
page numbers in footer.
"""
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR = Path(__file__).resolve().parent.parent
SRC = BASE_DIR / 'manuscript' / 'manuscript.md'
FIG_DIR = BASE_DIR / 'output'
SUP_DIR = FIG_DIR / 'supplementary'

OUT_MAIN = BASE_DIR / 'manuscript' / 'Manuscript.docx'
OUT_TABLES = BASE_DIR / 'manuscript' / 'Supplementary_Tables.docx'
OUT_FIGS = BASE_DIR / 'manuscript' / 'Supplementary_Figures.docx'


# ===========================================================================
# Document helpers
# ===========================================================================
def new_doc():
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(1)
        s.left_margin = s.right_margin = Inches(1)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    style.paragraph_format.space_after = Pt(0)

    for hname, hsize in [('Heading 1', 14), ('Heading 2', 12),
                         ('Heading 3', 12)]:
        s = doc.styles[hname]
        s.font.name = 'Times New Roman'
        s.font.size = Pt(hsize)
        s.font.bold = True
        s.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        s.paragraph_format.space_before = Pt(12)
        s.paragraph_format.space_after = Pt(6)

    add_page_numbers(doc)
    return doc


def add_page_numbers(doc):
    p = doc.sections[0].footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE')
    run._r.append(fld)


def add_runs(paragraph, text):
    pattern = re.compile(
        r'(\*\*[^*]+\*\*|(?<![*\w])\*[^*]+\*(?!\w)|`[^`]+`)'
    )
    pieces = pattern.split(text)
    for piece in pieces:
        if not piece:
            continue
        if piece.startswith('**') and piece.endswith('**'):
            r = paragraph.add_run(piece[2:-2])
            r.bold = True
        elif piece.startswith('*') and piece.endswith('*'):
            r = paragraph.add_run(piece[1:-1])
            r.italic = True
        elif piece.startswith('`') and piece.endswith('`'):
            r = paragraph.add_run(piece[1:-1])
            r.font.name = 'Courier New'
        else:
            paragraph.add_run(piece)


def add_md_paragraph(doc, text, alignment=None):
    p = doc.add_paragraph()
    if alignment is not None:
        p.alignment = alignment
    add_runs(p, text)
    return p


def add_heading_md(doc, text, level):
    if level == 1:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        run.font.name = 'Times New Roman'
        return p
    h = doc.add_heading(level=min(level - 1, 3))
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h.text = ''
    add_runs(h, text)
    for r in h.runs:
        r.font.name = 'Times New Roman'
        r.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
    return h


def parse_md_table(lines):
    rows = []
    for line in lines:
        if re.match(r'^\s*\|[-:\s|]+\|\s*$', line):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    return rows


def add_md_table(doc, rows):
    if not rows:
        return
    n_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Light Grid Accent 1'
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            if j >= n_cols:
                continue
            cell = table.cell(i, j)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.text = ''
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            add_runs(p, cell_text)
            for run in p.runs:
                run.font.size = Pt(10)
                if i == 0:
                    run.bold = True
    doc.add_paragraph('')


def add_image(doc, path, width_inches=6.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width_inches))


def page_break(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    br = OxmlElement('w:br')
    br.set(qn('w:type'), 'page')
    run._r.append(br)


# ===========================================================================
# Markdown parser — section-aware
# ===========================================================================
def split_sections(md_text):
    """Split markdown into named sections by their level-2 (##) headings.
    Returns a dict of section_name -> list of lines (excluding the heading
    line itself). The 'header' bucket contains everything before the first
    section (title block, metadata, keywords)."""
    lines = md_text.split('\n')
    sections = {'header': []}
    order = ['header']
    current = 'header'
    for line in lines:
        m = re.match(r'^##\s+(.+)$', line)
        if m:
            current = m.group(1).strip().upper()
            sections[current] = []
            order.append(current)
        elif line.startswith('# '):
            # Title (level 1) — keep in header
            sections['header'].append(line)
        else:
            sections[current].append(line)
    return sections, order


def render_section(doc, section_name, lines, render_heading=True):
    """Render a list of markdown lines into the doc. If render_heading is
    True and section_name is set, emit a Heading 1 for the section name."""
    if render_heading and section_name and section_name != 'header':
        add_heading_md(doc, section_name, level=2)

    para_buf = []
    table_buf = []
    in_table = False

    def flush_para():
        if para_buf:
            text = ' '.join(para_buf).strip()
            if text:
                add_md_paragraph(doc, text)
            para_buf.clear()

    def flush_table():
        if table_buf:
            rows = parse_md_table(table_buf)
            add_md_table(doc, rows)
            table_buf.clear()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if re.match(r'^\s*-{3,}\s*$', line):
            flush_para()
            flush_table()
            in_table = False
            i += 1
            continue

        if line.startswith('|') and line.endswith('|'):
            flush_para()
            in_table = True
            table_buf.append(line)
            i += 1
            continue
        elif in_table:
            flush_table()
            in_table = False

        h_match = re.match(r'^(#{1,6})\s+(.*)$', line)
        if h_match:
            flush_para()
            flush_table()
            level = len(h_match.group(1))
            text = h_match.group(2).strip()
            add_heading_md(doc, text, level)
            i += 1
            continue

        if not line.strip():
            flush_para()
            i += 1
            continue

        list_match = re.match(r'^(\d+)\.\s+(.*)$', line)
        if list_match:
            flush_para()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.first_line_indent = Inches(-0.4)
            rest = list_match.group(2)
            next_i = i + 1
            while next_i < len(lines) and lines[next_i].strip() and \
                    not re.match(r'^(#{1,6}\s|\d+\.\s|\|.*\||---)',
                                 lines[next_i]):
                rest = rest + ' ' + lines[next_i].strip()
                next_i += 1
            p.add_run(f"{list_match.group(1)}. ")
            add_runs(p, rest)
            i = next_i
            continue

        para_buf.append(line.strip())
        i += 1

    flush_para()
    flush_table()


# ===========================================================================
# Build the three documents
# ===========================================================================
md = SRC.read_text()
sections, order = split_sections(md)

# ---------------------------------------------------------------------------
# DOCUMENT 1 — Main manuscript with tables + figures at the bottom
# ---------------------------------------------------------------------------
print(f"Building {OUT_MAIN.name} ...")
doc = new_doc()

# Title page (header section)
render_section(doc, 'header', sections.get('header', []),
               render_heading=False)

# Body sections in canonical order
body_order = [
    'ABSTRACT', 'INTRODUCTION', 'METHODS', 'RESULTS', 'DISCUSSION',
    'LIMITATIONS', 'CONCLUSIONS', 'ACKNOWLEDGMENTS', 'FUNDING',
    'CONFLICTS OF INTEREST',
]
for name in body_order:
    if name in sections:
        render_section(doc, name, sections[name])

# References (before tables/figures)
if 'REFERENCES' in sections:
    render_section(doc, 'REFERENCES', sections['REFERENCES'])

# Tables on a new page
page_break(doc)
if 'TABLES' in sections:
    render_section(doc, 'TABLES', sections['TABLES'])

# Figures on a new page — embed images with their legends
page_break(doc)
add_heading_md(doc, 'FIGURES', level=2)

figure_specs = [
    ('Figure 1', FIG_DIR / 'Figure_1.png'),
    ('Figure 2', FIG_DIR / 'Figure_2.png'),
    ('Figure 3', FIG_DIR / 'Figure_3.png'),
    ('Figure 4', FIG_DIR / 'Figure_4.png'),
]

# Pull the figure-legend text out of the FIGURE LEGENDS section.
# Each legend is a paragraph beginning with "**Figure N. ..."
legends_raw = '\n'.join(sections.get('FIGURE LEGENDS', []))
legend_paras = re.split(
    r'\n(?=\*\*Figure \d+\.)', legends_raw)
legend_map = {}
for para in legend_paras:
    m = re.match(r'\*\*Figure (\d+)\.', para)
    if m:
        legend_map[f'Figure {m.group(1)}'] = para.strip()

for label, image_path in figure_specs:
    if image_path.exists():
        add_image(doc, image_path, width_inches=6.5)
    legend_text = legend_map.get(label,
                                  f'**{label}.** [legend missing]')
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_runs(p, legend_text)
    doc.add_paragraph('')
    if label != figure_specs[-1][0]:
        page_break(doc)

doc.save(OUT_MAIN)
print(f"  saved {OUT_MAIN.stat().st_size / 1024:.1f} KB")


# ---------------------------------------------------------------------------
# DOCUMENT 2 — Supplementary Tables
# ---------------------------------------------------------------------------
print(f"\nBuilding {OUT_TABLES.name} ...")
doc = new_doc()

# Title
add_heading_md(doc,
               'Supplementary Tables — Shifting Geography of Robotic '
               'Surgery Clinical Trials, 2001–2025', level=1)

# Pull out the SUPPLEMENTARY MATERIALS section
supp_lines = sections.get('SUPPLEMENTARY MATERIALS', [])
supp_text = '\n'.join(supp_lines)

# Find the supplementary table descriptions and emit each as a section
table_blocks = re.split(
    r'\n(?=\*\*Supplementary Table S\d+\.)', supp_text)

# --- S1: brief description + pointer to CSV
s1_block = next((b for b in table_blocks
                 if 'Supplementary Table S1' in b), '')
if s1_block:
    add_heading_md(doc, 'Supplementary Table S1', level=2)
    p = doc.add_paragraph()
    add_runs(p, s1_block.strip())
    p2 = doc.add_paragraph()
    add_runs(p2, '*Full content provided as the accompanying CSV file '
                 '(`Supplementary_Table_S1_historical_WB_classifications'
                 '.csv`); 8,281 country-year rows.*')
    page_break(doc)

# --- S2: include the full content (small table)
s2_block = next((b for b in table_blocks
                 if 'Supplementary Table S2' in b), '')
if s2_block:
    add_heading_md(doc, 'Supplementary Table S2', level=2)
    p = doc.add_paragraph()
    add_runs(p, s2_block.strip())
    s2_csv = SUP_DIR / 'Supplementary_Table_S2_static_vs_time_varying.csv'
    if s2_csv.exists():
        import csv
        with open(s2_csv) as f:
            rows = list(csv.reader(f))
        if rows:
            add_md_paragraph(doc, '')
            t = doc.add_table(rows=len(rows), cols=len(rows[0]))
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.style = 'Light Grid Accent 1'
            for i, row in enumerate(rows):
                for j, cell_text in enumerate(row):
                    cell = t.cell(i, j)
                    cell.text = ''
                    p = cell.paragraphs[0]
                    p.paragraph_format.line_spacing = 1.15
                    add_runs(p, cell_text)
                    for run in p.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.bold = True
    page_break(doc)

# --- S3: large per-country table; include description + first 20 rows
s3_block = next((b for b in table_blocks
                 if 'Supplementary Table S3' in b), '')
if s3_block:
    add_heading_md(doc, 'Supplementary Table S3', level=2)
    p = doc.add_paragraph()
    add_runs(p, s3_block.strip())
    p2 = doc.add_paragraph()
    add_runs(p2, '*Per-country counts by year are provided in full as the '
                 'accompanying CSV file '
                 '(`Supplementary_Table_S3_country_year_counts.csv`); '
                 '47 countries × 25 years. The 15 highest-contributing '
                 'countries are reproduced below for reference.*')
    s3_csv = SUP_DIR / 'Supplementary_Table_S3_country_year_counts.csv'
    if s3_csv.exists():
        import csv
        with open(s3_csv) as f:
            rows = list(csv.reader(f))
        # Header + first 15 data rows
        rows = rows[:16]
        # Trim to first 11 cols so it fits on the page
        rows = [r[:1] + r[-10:] for r in rows]  # country + last 9 years + total
        add_md_paragraph(doc, '')
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.style = 'Light Grid Accent 1'
        for i, row in enumerate(rows):
            for j, cell_text in enumerate(row):
                cell = t.cell(i, j)
                cell.text = ''
                p = cell.paragraphs[0]
                p.paragraph_format.line_spacing = 1.15
                add_runs(p, cell_text)
                for run in p.runs:
                    run.font.size = Pt(8)
                    if i == 0:
                        run.bold = True

doc.save(OUT_TABLES)
print(f"  saved {OUT_TABLES.stat().st_size / 1024:.1f} KB")


# ---------------------------------------------------------------------------
# DOCUMENT 3 — Supplementary Figures
# ---------------------------------------------------------------------------
print(f"\nBuilding {OUT_FIGS.name} ...")
doc = new_doc()

add_heading_md(doc,
               'Supplementary Figures — Shifting Geography of Robotic '
               'Surgery Clinical Trials, 2001–2025', level=1)

figure_blocks = re.split(
    r'\n(?=\*\*Supplementary Figure S\d+\.)', supp_text)

s_figure_specs = [
    ('Supplementary Figure S1',
     SUP_DIR / 'Supplementary_Figure_S1.png'),
    ('Supplementary Figure S2',
     SUP_DIR / 'Supplementary_Figure_S2.png'),
    ('Supplementary Figure S3',
     SUP_DIR / 'Supplementary_Figure_S3.png'),
]

for label, image_path in s_figure_specs:
    block = next((b for b in figure_blocks if label in b), '')
    add_heading_md(doc, label, level=2)
    if image_path.exists():
        add_image(doc, image_path, width_inches=6.5)
    if block:
        p = doc.add_paragraph()
        add_runs(p, block.strip())
    if label != s_figure_specs[-1][0]:
        page_break(doc)

doc.save(OUT_FIGS)
print(f"  saved {OUT_FIGS.stat().st_size / 1024:.1f} KB")

print("\nDone.")
print(f"  - {OUT_MAIN}")
print(f"  - {OUT_TABLES}")
print(f"  - {OUT_FIGS}")
