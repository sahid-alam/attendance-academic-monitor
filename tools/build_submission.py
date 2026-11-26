"""Rebuild the submission diagrams, report PDF, and slides from tracked sources.

Run from any directory: python tools/build_submission.py
Install tools/submission_requirements.txt in a virtual environment first.
Application dependencies and runtime are unchanged.
"""
from pathlib import Path
import json
import re
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
    im, d = diagram_base('Two-sprint Scrum process', 'AAM-13 | Baseline process, November 2026 | Planned events, not attendance evidence', 780)
    boxes = [
        (45, 170, 490, 415, 'SPRINT 1  /  19–22 NOV', ['Plan the sprint backlog', 'Requirements, design, plan', 'Daily progress / blocker updates', 'Review + retrospective']),
        (575, 170, 1020, 415, 'SPRINT 2  /  23–26 NOV', ['Refine and plan backlog', 'Build, verify, write, rehearse', 'Daily progress / blocker updates', 'Review + retrospective']),
        (1105, 170, 1550, 415, 'SUBMISSION  /  27 NOV', ['Select verified revision', 'Check artifacts and links', 'Complete team review', 'Submit; retain receipt']),
    ]
    for x1, y1, x2, y2, title, lines in boxes:
        d.rounded_rectangle((x1, y1, x2, y2), radius=16, fill='white', outline='#CCD9E4', width=2)
        diagram_text(d, (x1+22, y1+22), title, font=font(24, True), fill=TEAL)
        for j, line in enumerate(lines):
            diagram_text(d, (x1+22, y1+76+j*38), line, font=font(21), fill=INK)
    for x in (500, 1030):
        d.line((x, 285, x+65, 285), fill=TEAL, width=7)
        d.polygon([(x+65, 285), (x+48, 274), (x+48, 296)], fill=TEAL)
    diagram_text(d, (65, 455), 'INCREMENT 1', font=font(22, True), fill=TEAL)
    diagram_text(d, (65, 493), 'Reviewed requirements, models and plan', font=font(24), fill=INK)
    diagram_text(d, (595, 455), 'INCREMENT 2', font=font(22, True), fill=TEAL)
    diagram_text(d, (595, 493), 'Tested prototype and submission pack', font=font(24), fill=INK)
    d.rounded_rectangle((45, 565, 1550, 690), radius=14, fill='#DEEDF0')
    diagram_text(d, (70, 580), 'FEEDBACK RETURNS TO THE BACKLOG', font=font(24, True), fill=TEAL)
    diagram_text(d, (70, 625), 'Review findings → reprioritize tasks → next sprint / future work. Unfinished work stays visible.', font=font(23), fill=INK)
    diagram_text(d, (45, 730), 'Source: planning/PROJECT_PLAN.md and PROCESS_MODEL.md | S4: Madiha Iram', font=font(18), fill=MUTED)
    im.save(ROOT / 'planning/process-model.png')


def gantt_diagram():
    im, d = diagram_base('Baseline schedule: 19–27 November', 'AAM-16 | Calendar days | Original plan; actual completion must be recorded separately', 955)
    x0, cell, y0, rowh = 540, 110, 235, 51
    diagram_text(d, (45, 155), 'WORK PACKAGE / OWNER', font=font(22, True), fill=INK)
    for i in range(9):
        diagram_text(d, (x0+i*cell+17, 155), str(19+i), font=font(25, True), fill=INK)
        d.line((x0+i*cell, 200, x0+i*cell, 830), fill='#D5DFE8', width=1)
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
    diagram_text(d, (45, 845), 'Sprint 1: 19–22 Nov     |     Sprint 2: 23–26 Nov     |     Final submission: 27 Nov', font=font(23, True), fill=TEAL)
    diagram_text(d, (45, 895), 'See WBS.md for predecessors. Late preparation on 26 Nov does not change the baseline.', font=font(21), fill=MUTED)
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
