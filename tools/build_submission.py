"""Rebuild the submission diagrams, report PDF, and slides from tracked sources.

Run from any directory: python tools/build_submission.py
Install tools/submission_requirements.txt in a virtual environment first.
Application dependencies and runtime are unchanged.
"""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from html import escape

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as PDFImage, Preformatted, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
NAVY, TEAL, INK, MUTED = '#101E32', '#007F82', '#15283E', '#526477'
FONT_DIR = Path('/usr/share/fonts/truetype/open-sans')
# Embed fonts so PDF viewers do not substitute mismatched glyph metrics.
for pdf_name, font_file in [('Helvetica', 'OpenSans-Regular.ttf'), ('Helvetica-Bold', 'OpenSans-Bold.ttf'),
                            ('Helvetica-Oblique', 'OpenSans-Italic.ttf'), ('Helvetica-BoldOblique', 'OpenSans-BoldItalic.ttf')]:
    if (FONT_DIR / font_file).exists():
        pdfmetrics.registerFont(TTFont(pdf_name, str(FONT_DIR / font_file)))
pdfmetrics.registerFontFamily('Helvetica', normal='Helvetica', bold='Helvetica-Bold', italic='Helvetica-Oblique', boldItalic='Helvetica-BoldOblique')


def font(size, bold=False):
    path = FONT_DIR / ('OpenSans-Bold.ttf' if bold else 'OpenSans-Regular.ttf')
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)


def diagram_text(draw, position, text, **kwargs):
    # Keep generated labels legible with Pillow's portable default font too.
    label = text.replace('–', '-').replace('→', '->')
    draw.text(position, label, **kwargs)


def diagram_base(title, subtitle, height):
    im = Image.new('RGB', (1600, height), '#F4F7FA')
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, 1600, 125), fill=NAVY)
    diagram_text(draw, (45, 20), title, font=font(36, True), fill='white')
    diagram_text(draw, (45, 76), subtitle, font=font(21), fill='#B9D5E9')
    return im, draw


def process_diagram():
    # One layout drives both the PNG and editable draw.io source.
    im, d = diagram_base('Two-sprint Scrum process', 'AAM-13 | November 2026 | Planned events, not attendance evidence', 850)
    mxfile = ET.Element('mxfile', host='app.diagrams.net')
    diagram = ET.SubElement(mxfile, 'diagram', id='scrum', name='Two-sprint Scrum')
    model = ET.SubElement(diagram, 'mxGraphModel', page='1', pageWidth='1600', pageHeight='850')
    graph = ET.SubElement(model, 'root')
    ET.SubElement(graph, 'mxCell', id='0')
    ET.SubElement(graph, 'mxCell', id='1', parent='0')

    positions = {}

    def node(key, label, x, y, width=225, height=100, heading=False):
        positions[key] = (x, y, width, height)
        cell = ET.SubElement(graph, 'mxCell', id=key, value=label, vertex='1', parent='1',
                             style='rounded=1;whiteSpace=wrap;html=0;fontSize=21;fillColor=#FFFFFF;strokeColor=#007F82;')
        ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(width), height=str(height), attrib={'as': 'geometry'})
        d.rounded_rectangle((x,y,x+width,y+height), radius=10, fill='white', outline=TEAL, width=2)
        for j, line in enumerate(label.split('\n')):
            diagram_text(d, (x+12,y+14+j*28), line, font=font(21, heading), fill=INK)

    def arrow(source, target, points):
        sx, sy, sw, sh = positions[source]
        tx, ty, tw, th = positions[target]
        exit_x, exit_y = (points[0][0]-sx)/sw, (points[0][1]-sy)/sh
        entry_x, entry_y = (points[-1][0]-tx)/tw, (points[-1][1]-ty)/th
        cell = ET.SubElement(graph, 'mxCell', id=f'{source}-{target}', edge='1', parent='1', source=source, target=target,
                             style=f'edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;strokeColor=#007F82;strokeWidth=2;exitX={exit_x};exitY={exit_y};entryX={entry_x};entryY={entry_y};')
        geometry = ET.SubElement(cell, 'mxGeometry', relative='1', attrib={'as': 'geometry'})
        if len(points) > 2:
            waypoints = ET.SubElement(geometry, 'Array', attrib={'as': 'points'})
            for x, y in points[1:-1]:
                ET.SubElement(waypoints, 'mxPoint', x=str(x), y=str(y))
        d.line(points, fill=TEAL, width=4)
        x,y=points[-1]; px,py=points[-2]
        if x > px:
            d.polygon([(x,y),(x-10,y-7),(x-10,y+7)], fill=TEAL)
        elif y > py:
            d.polygon([(x,y),(x-7,y-10),(x+7,y-10)], fill=TEAL)
        else:
            d.polygon([(x,y),(x-7,y+10),(x+7,y+10)], fill=TEAL)

    node('title', 'Two-sprint Scrum / November 2026\nAAM-13 | Planned events, not attendance evidence', 45, 20, 1500, 90, True)
    for sprint, y, dates, work in [(1,210,'19–22 Nov 2026','Requirements, design, planning'),
                                    (2,490,'23–26 Nov 2026','Build and test')]:
        node(f's{sprint}-heading', f'Sprint {sprint}: {dates} / {work}',45,y-70,1500,55,True)
        labels=['Backlog', 'Sprint planning', f'Sprint {sprint}\nDaily updates', 'Review', 'Retrospective', 'Backlog\nrefinement']
        for i,label in enumerate(labels):
            node(f's{sprint}-{i}',label,45+i*255,y)
            if i:
                arrow(f's{sprint}-{i-1}',f's{sprint}-{i}',[(45+(i-1)*255+225,y+50),(45+i*255,y+50)])
    arrow('s1-5','s2-0',[(1432,310),(1432,345),(25,345),(25,540),(45,540)])
    node('increment1','Increment 1: reviewed requirements, models and plan',45,365,1500,45)
    arrow('s1-3','increment1',[(922,310),(922,365)])
    node('increment2','Increment 2: tested prototype and submission artifacts',45,625,1500,55)
    node('submission','27 Nov: final checks and submission checkpoint; retain receipt',45,720,1500,60)
    arrow('s2-5','s1-0',[(1545,540),(1575,540),(1575,190),(157,190),(157,210)])
    arrow('s2-3','increment2',[(922,590),(922,625)])
    arrow('increment2','submission',[(795,680),(795,720)])
    node('feedback-note','Feedback refines the next backlog; unfinished work stays visible. S4: Madiha Iram',45,800,1500,40)
    ET.indent(mxfile)
    ET.ElementTree(mxfile).write(ROOT / 'planning/process-model.drawio', encoding='utf-8', xml_declaration=True)
    im.save(ROOT / 'planning/process-model.png')


def gantt_diagram():
    im, d = diagram_base('Baseline schedule: 19–27 November', 'AAM-16 | Sprint work: 19–26 Nov | 27 Nov: submission checkpoint | Planned dates', 1400)
    x0, cell, y0, rowh = 540, 110, 235, 51
    diagram_text(d, (45, 155), 'WORK PACKAGE / OWNER', font=font(22, True), fill=INK)
    for i in range(9):
        diagram_text(d, (x0+i*cell+17, 155), str(19+i), font=font(25, True), fill=INK)
        d.line((x0+i*cell, 200, x0+i*cell, 1260), fill='#D5DFE8', width=1)
    tasks = [('Requirements / S1', 19, 21), ('Process model / S4', 19, 20), ('WBS, schedule, risks / S4', 19, 21),
             ('Design + models / S2, S1', 21, 22), ('Attendance / S3', 23, 23),
             ('Marks, risk, cases / S3', 24, 24), ('Ethics / S1, S4', 23, 24),
             ('Tests + deployment / S3, S4', 25, 25), ('Report + slides / S4, all', 25, 26),
             ('Rehearsal / all', 26, 26), ('Final check + submission', 27, 27)]
    for i, (title, start, end) in enumerate(tasks):
        y = y0+i*rowh
        diagram_text(d, (45, y), title, font=font(22), fill=INK)
        d.rounded_rectangle((x0+(start-19)*cell+5, y, x0+(end-18)*cell-10, y+31), radius=6,
                            fill=TEAL if start < 23 else '#4767AE')
    milestones = [('M1 Requirements + plan (20–21 Nov)',20,21), ('M2 Design review',22,22),
                  ('M3 Attendance working',23,23), ('M4 Marks / risk working',24,24),
                  ('M5 Submission readiness',26,26), ('M6 Submission checkpoint',27,27)]
    for i,(label,start,end) in enumerate(milestones):
        y=825+i*68
        diagram_text(d,(45,y-12),label,font=font(21,True),fill=INK)
        x=x0+(end-19)*cell+cell//2
        if start != end:
            d.line((x0+(start-19)*cell+cell//2,y,x,y),fill='#AA4925',width=5)
        d.polygon([(x,y-12),(x+12,y),(x,y+12),(x-12,y)],fill='#AA4925')
    diagram_text(d, (45, 1285), 'Diamonds: milestone gates. M1 spans 20–21 Nov; diamond at the 21 Nov gate.',font=font(22),fill=TEAL)
    diagram_text(d, (45, 1330), 'Sprint 1: 19–22 Nov | Sprint 2: 23–26 Nov | Submission: 27 Nov. See WBS.md for dependencies.',font=font(21),fill=MUTED)
    im.save(ROOT / 'planning/gantt.png')


def safe_text(text):
    # Standard PDF fonts cover Latin punctuation; normalize symbols outside that set.
    for src, dst in {'→':' -> ', '≥':'>=', '×':' x ', '≠':'does not equal', '•':' | '}.items():
        text = text.replace(src, dst)
    return text


def rich(text):
    text = escape(safe_text(text))
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#007F82">\1</link>', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text).replace('&lt;br/&gt;', '<br/>')


def markdown_pdf(source, target):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyAAM', fontName='Helvetica', fontSize=10, leading=15, spaceAfter=8, textColor=colors.HexColor(INK)))
    styles.add(ParagraphStyle(name='CellAAM', fontSize=8, leading=11, textColor=colors.HexColor(INK)))
    for name in ('Heading1', 'Heading2', 'Heading3'):
        styles[name].textColor = colors.HexColor(TEAL)
        styles[name].spaceBefore = 14
        styles[name].spaceAfter = 8
    lines = source.read_text().splitlines()
    story, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(safe_text(lines[i])); i += 1
            story.append(Preformatted('\n'.join(code), ParagraphStyle(name='CodeAAM', fontName='Courier', fontSize=7, leading=10, spaceAfter=8)))
        elif line.startswith('!['):
            match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', line)
            if match:
                path = (source.parent / match.group(1)).resolve()
                with Image.open(path) as pic:
                    width, height = pic.size
                story.append(PDFImage(str(path), width=480, height=480*height/width))
                story.append(Spacer(1, 10))
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[: -]+', c) for c in cells):
                    rows.append([Paragraph(rich(c), styles['CellAAM']) for c in cells])
                i += 1
            count = len(rows[0])
            if count == 3:
                widths = [85, 180, 215]
            elif count == 2:
                widths = [145, 335]
            else:
                widths = [480/count]*count
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2EFF1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F4F7FA')]),
                ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOX', (0,0), (-1,-1), .5, colors.HexColor('#CCD9E4')),
                ('LINEBELOW', (0,0), (-1,0), .8, colors.HexColor(TEAL)),
                ('LEFTPADDING', (0,0), (-1,-1), 7), ('RIGHTPADDING', (0,0), (-1,-1), 7),
                ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ]))
            story.extend([table, Spacer(1, 12)])
            continue
        elif line.startswith('#'):
            level = len(line)-len(line.lstrip('#'))
            story.append(Paragraph(rich(line.lstrip('# ')), styles[f'Heading{min(level,3)}']))
        else:
            chunks = [line]
            while i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#', '|', '![', '```', '- ')) and not line.startswith('- '):
                i += 1; chunks.append(lines[i].strip())
            story.append(Paragraph(rich(' '.join(chunks)), styles['BodyAAM']))
        i += 1

    def footer(c, doc):
        c.setStrokeColor(colors.HexColor('#CBD9E3')); c.line(55, 38, 535, 38)
        c.setFillColor(colors.HexColor(MUTED)); c.setFont('Helvetica', 8)
        c.drawString(55, 24, 'AAM | Academic prototype | 26 November 2026')
        c.drawRightString(535, 24, str(doc.page))
    SimpleDocTemplate(str(target), pagesize=(595.28,841.89), leftMargin=55, rightMargin=60,
                      topMargin=45, bottomMargin=55, title='AAM Final Report', author='Madiha Iram / S4').build(story, onFirstPage=footer, onLaterPages=footer)


def deck():
    slides = json.loads((ROOT / 'presentation/slides.json').read_text())
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    pdf = canvas.Canvas(str(ROOT / 'presentation/AAM_PRESENTATION.pdf'), pagesize=(960,540))
    pdf.setTitle('AAM Presentation'); pdf.setAuthor('Madiha Iram / S4')
    notes = ['# Presentation slides and speaker notes (AAM-35)', '',
             'Source: `slides.json`. Rebuild PPTX/PDF and this file with `tools/build_submission.py`.',
             'Target: 10 minutes. Team speaker names and actual rehearsal remain to be confirmed.', '']

    def textbox(slide, x,y,w,h, text, size, color, bold=False):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, part in enumerate(text.split('\n')):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = part; p.font.size = Pt(size); p.font.bold = bold
            p.font.name = 'Aptos'; p.font.color.rgb = RGBColor.from_string(color.lstrip('#'))
            p.space_after = Pt(10)
        return box

    def pdf_para(text, x, ytop, width, size=16, color='#FFFFFF', bold=False):
        style = ParagraphStyle(name='Slide', fontName='Helvetica-Bold' if bold else 'Helvetica',
                               fontSize=size, leading=size*1.35, textColor=colors.HexColor(color), alignment=TA_LEFT)
        p = Paragraph(rich(text), style)
        _, h = p.wrap(width, 500)
        p.drawOn(pdf,x,ytop-h)
        return h

    for n, data in enumerate(slides,1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid(); slide.background.fill.fore_color.rgb = RGBColor.from_string('101E32')
        textbox(slide,.5,.32,12,.45,data['kicker'],12,'#7EDBDD',True)
        textbox(slide,.5,1,12.3,1.1,data['title'],30,'#FFFFFF',True)
        textbox(slide,.5,6.96,12,.35,f"{n:02d} / 12    •    {data['speaker']}    •    {data['seconds']} seconds    |    Evidence and limits in report/FINAL_REPORT.md",10,'#B9C9D8')
        pdf.setFillColor(colors.HexColor(NAVY)); pdf.rect(0,0,960,540,fill=1,stroke=0)
        pdf_para(data['kicker'],36,516,885,9,'#7EDBDD',True)
        pdf_para(data['title'],36,466,885,25,'#FFFFFF',True)
        if 'visual' in data:
            path = (ROOT / 'presentation' / data['visual']).resolve()
            with Image.open(path) as diagram:
                pw, ph = diagram.size
            image_width = min(8.3, 4.55 * pw / ph)
            slide.shapes.add_picture(str(path), Inches(.5), Inches(2.1), width=Inches(image_width))
            pdf.drawImage(str(path),36,80,width=600,height=315, preserveAspectRatio=True,anchor='c')
            textbox(slide,9.15,2.2,3.6,2.8,'\n'.join(data['bullets']),16,'#FFFFFF')
            textbox(slide,9.15,5.25,3.6,1.3,data['evidence'],13,'#7EDBDD')
            y=385
            for b in data['bullets']:
                y-=pdf_para(b,661,y,260,13)+15
            pdf_para(data['evidence'].replace('\n','<br/>'),661,170,260,11,'#7EDBDD')
        else:
            y = 2.25
            yp = 378
            for bullet in data['bullets']:
                textbox(slide,.65,y,8.05,1.12,bullet,23,'#FFFFFF')
                y += 1.33
                yp -= pdf_para(bullet,47,yp,575,18)+24
            textbox(slide,9.1,2.3,3.55,3.9,data['evidence'],20,'#7EDBDD')
            pdf_para(data['evidence'].replace('\n','<br/>'),660,375,260,16,'#7EDBDD')
        pdf_para(f"{n:02d} / 12  |  {data['speaker']}  |  {data['seconds']} seconds",36,30,885,8,'#B9C9D8')
        pdf.showPage()
        slide.notes_slide.notes_text_frame.text = f"{data['speaker']} • {data['seconds']} seconds\n\n{data['notes']}"
        notes += [f"## {n}. {data['title']}", '', f"Speaker: {data['speaker']} | Target: {data['seconds']} seconds", '', data['kicker'], '']
        notes += ['- '+b for b in data['bullets']]
        notes += ['', data['evidence'].replace('\n','\n\n'), '', '**Speaker notes:** '+data['notes'], '']
    prs.core_properties.title = 'Online Student Attendance & Academic Monitoring'
    prs.core_properties.author = 'Madiha Iram / S4'
    prs.save(ROOT / 'presentation/AAM_PRESENTATION.pptx')
    pdf.save()
    (ROOT / 'presentation/SLIDES.md').write_text('\n'.join(notes).rstrip()+'\n')


if __name__ == '__main__':
    process_diagram()
    gantt_diagram()
    markdown_pdf(ROOT / 'report/FINAL_REPORT.md', ROOT / 'report/FINAL_REPORT.pdf')
    deck()
    print('Built process-model.png, gantt.png, FINAL_REPORT.pdf, AAM_PRESENTATION.pptx/.pdf and SLIDES.md')
