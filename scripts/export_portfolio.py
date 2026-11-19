"""Build the downloadable PDF. Install scripts/requirements-export.txt first."""
from html.parser import HTMLParser
from pathlib import Path
from html import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Flowable, PageBreak)

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'downloads' / 'John-Benedict-Pal-lingayan-Portfolio.pdf'


class PortfolioParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.section = None
        self.capture = None
        self.parts = []
        self.blocks = []
        self.block_kind = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id') == 'about':
            self.active = True
        if attrs.get('id') == 'contact':
            self.active = False
        if attrs.get('id') in ('about', 'skills', 'projects', 'experience', 'training', 'education'):
            self.section = attrs['id']
        if not self.active:
            return
        if tag in ('h2', 'h3', 'h4', 'p', 'li', 'span'):
            # Preserve inline date spans without replacing an active paragraph.
            if self.capture:
                return
            self.capture = tag
            self.parts = []
            classes = attrs.get('class', '').split()
            self.block_kind = tag
            if 'skills-highlight' in classes:
                self.block_kind = 'highlight'
            elif 'career-date' in classes:
                self.block_kind = 'date'
            elif 'career-tag' in classes:
                self.block_kind = 'tag'
        if tag == 'br' and self.capture:
            self.parts.append(' ')
        if 'data-date' in attrs:
            self.blocks.append(('date', attrs['data-date'], self.section))

    def handle_data(self, data):
        if self.active and self.capture:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.capture:
            value = ' '.join(''.join(self.parts).split())
            if value:
                kind = self.block_kind
                self.blocks.append((kind, value, self.section))
            self.capture = None
            self.parts = []


BLUE = colors.HexColor('#3498db')
INK = colors.HexColor('#374054')
GRAY = colors.HexColor('#e4e4ea')
WIDTH = A4[0] - 88


class Hero(Flowable):
    def __init__(self):
        super().__init__()
        self.width = WIDTH
        self.height = 182

    def draw(self):
        c = self.canv
        c.setFillColor(BLUE)
        c.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=0)
        c.saveState()
        path = c.beginPath()
        path.circle(self.width / 2, 136, 30)
        c.clipPath(path, stroke=0)
        c.drawImage(str(ROOT / 'images' / 'ben2.jpg'), self.width / 2 - 30, 106,
                    width=60, height=60, mask='auto')
        c.restoreState()
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 21)
        c.drawCentredString(self.width / 2, 80, 'John Benedict Pal-lingayan')
        c.setFont('Helvetica', 11)
        c.drawCentredString(self.width / 2, 59, 'Automation Test Engineer | ISTQB-CTFL')
        c.drawCentredString(self.width / 2, 41, 'Cypress | TypeScript | JavaScript')
        c.setFont('Helvetica', 9)
        c.drawCentredString(self.width / 2, 19, 'jbpallingayan@gmail.com | LinkedIn')
        c.linkURL('mailto:jbpallingayan@gmail.com', (80, 13, 300, 29), relative=1)
        c.linkURL('https://www.linkedin.com/in/john-benedict-p-6b795061/',
                  (300, 13, self.width - 70, 29), relative=1)


class SkillTags(Flowable):
    def __init__(self, tags):
        super().__init__()
        self.tags = tags

    def wrap(self, available_width, available_height):
        self.positions = []
        x = y = 0
        from reportlab.pdfbase.pdfmetrics import stringWidth
        for tag in self.tags:
            width = stringWidth(tag, 'Helvetica', 9) + 18
            if x and x + width > available_width:
                x = 0
                y += 27
            self.positions.append((tag, x, y, width))
            x += width + 7
        self.height = y + 28
        return available_width, self.height

    def draw(self):
        c = self.canv
        for text, x, y, width in self.positions:
            bottom = self.height - y - 23
            c.setFillColor(GRAY)
            c.roundRect(x, bottom, width, 22, 3, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont('Helvetica', 9)
            c.drawString(x + 9, bottom + 7, text)


def main():
    parser = PortfolioParser()
    parser.feed((ROOT / 'index.html').read_text())
    base = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=13,
                          textColor=INK, spaceAfter=4)
    styles = {
        'h2': ParagraphStyle('Section', parent=base, fontName='Helvetica-Bold',
                             fontSize=17, leading=22, textColor=BLUE,
                             spaceBefore=12, spaceAfter=8, keepWithNext=True),
        'h3': ParagraphStyle('Heading', parent=base, fontName='Helvetica-Bold',
                             fontSize=11, leading=15, spaceBefore=6, keepWithNext=True),
        'h4': ParagraphStyle('Role', parent=base, fontName='Helvetica-Bold', keepWithNext=True),
        'date': ParagraphStyle('Date', parent=base, fontName='Helvetica-Oblique',
                               fontSize=8.5, textColor=colors.HexColor('#74808a'), keepWithNext=True),
        'highlight': ParagraphStyle('Highlight', parent=base, backColor=GRAY,
                                    borderPadding=11, spaceBefore=8, spaceAfter=14),
        'li': ParagraphStyle('Bullet', parent=base, leftIndent=11, firstLineIndent=-8),
    }
    story = [Hero(), Spacer(1, 4)]
    tags = []
    def flush_tags():
        if tags:
            story.append(SkillTags(tags.copy()))
            tags.clear()
    for kind, text, section in parser.blocks:
        if (section == 'skills' and kind == 'li') or kind == 'tag':
            tags.append(text)
            continue
        flush_tags()
        if kind == 'h2' and section in ('projects', 'experience', 'training'):
            story.append(PageBreak())
        value = escape(text)
        if kind == 'p' and ':' in text:
            label, rest = text.split(':', 1)
            value = '<b>' + escape(label + ':') + '</b>' + escape(rest)
        if kind == 'highlight':
            value = value.replace('AI-assisted. Quality-focused.', '<b>AI-assisted. Quality-focused.</b><br/>')
        if kind == 'li':
            value = '&#8226; ' + value
        story.append(Paragraph(value, styles.get(kind, styles.get('date') if kind == 'span' else base)))
    flush_tags()
    def footer(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(INK)
        canvas.drawString(44, 24, 'John Benedict Pal-lingayan | Portfolio')
        canvas.drawRightString(A4[0] - 44, 24, str(doc.page))
    OUTPUT.parent.mkdir(exist_ok=True)
    SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=44, leftMargin=44,
                      topMargin=38, bottomMargin=42, title='John Benedict Pal-lingayan Portfolio',
                      author='John Benedict Pal-lingayan').build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == '__main__':
    main()
