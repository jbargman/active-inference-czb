"""
Build a PDF from a markdown source file.

The markdown is the source of truth; the PDF is generated from it. Edit the .md and rebuild,
never the other way round.

Uses ReportLab's platypus flowables. An earlier version used pandoc plus PyMuPDF's Story
engine, which was simpler but broke wide tables badly when they split across a page boundary
(columns collapsed and overlapped). Platypus splits tables correctly and repeats header rows.

Supported markdown subset: ATX headings, paragraphs, bold/italic/inline code, bullet and
numbered lists, fenced code blocks, pipe tables, horizontal rules, blockquotes.

Usage:
    python docs/build_pdf.py docs/data_requirements.md
    python docs/build_pdf.py docs/data_requirements.md -o docs/data_requirements-v2.pdf
"""
import argparse
import html
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether, ListFlowable, ListItem,
    PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle,
)

NAVY = colors.HexColor("#10305A")
STEEL = colors.HexColor("#2B4C7E")
GREY = colors.HexColor("#6B7280")
RULE = colors.HexColor("#C7D0DC")
HEADBG = colors.HexColor("#E8EDF4")
CODEBG = colors.HexColor("#F4F6F9")


def styles():
    ss = getSampleStyleSheet()
    base = dict(fontName="Helvetica", fontSize=9.3, leading=13.2,
                alignment=TA_LEFT, textColor=colors.HexColor("#1A1A1A"))
    s = {
        "body": ParagraphStyle("body", **base, spaceAfter=5),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=17, leading=21,
                             textColor=NAVY, spaceAfter=3),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16,
                             textColor=NAVY, spaceBefore=13, spaceAfter=3),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.3, leading=14,
                             textColor=STEEL, spaceBefore=9, spaceAfter=2),
        "sub": ParagraphStyle("sub", **{**base, "fontSize": 9.5, "textColor": GREY},
                              spaceAfter=2),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.9, leading=9.8,
                               alignment=TA_LEFT),
        "cellh": ParagraphStyle("cellh", fontName="Helvetica-Bold", fontSize=7.9,
                                leading=9.8, alignment=TA_LEFT),
        "quote": ParagraphStyle("quote", **{**base, "textColor": GREY}, leftIndent=10),
        "li": ParagraphStyle("li", **base, spaceAfter=1),
    }
    return s


# ------------------------------------------------------------------ inline markdown
def inline(text: str) -> str:
    """Convert inline markdown to ReportLab mini-HTML, escaping the rest."""
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "`":
            j = text.find("`", i + 1)
            if j == -1:
                out.append(html.escape(ch)); i += 1; continue
            out.append(f'<font face="Courier" size="8.3">'
                       f'{html.escape(text[i+1:j])}</font>')
            i = j + 1
        elif text.startswith("**", i):
            j = text.find("**", i + 2)
            if j == -1:
                out.append(html.escape("**")); i += 2; continue
            out.append(f"<b>{inline(text[i+2:j])}</b>")
            i = j + 2
        elif ch == "*":
            j = text.find("*", i + 1)
            if j == -1:
                out.append(html.escape(ch)); i += 1; continue
            out.append(f"<i>{inline(text[i+1:j])}</i>")
            i = j + 1
        elif text.startswith("[", i):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", text[i:])
            if m:
                out.append(f'<font color="#2B4C7E">{inline(m.group(1))}</font>')
                i += m.end(); continue
            out.append(html.escape(ch)); i += 1
        else:
            out.append(html.escape(ch)); i += 1
    return "".join(out)


# ------------------------------------------------------------------------- tables
def split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def build_table(rows, avail_width, st):
    header, body = rows[0], rows[1:]
    ncol = len(header)

    # column widths proportional to a robust measure of content length
    weights = []
    for c in range(ncol):
        lens = [len(header[c])] + [len(r[c]) if c < len(r) else 0 for r in body]
        lens.sort()
        typ = lens[int(0.75 * (len(lens) - 1))]          # 75th percentile
        weights.append(max(typ, len(header[c]), 6))
    # a column must at least fit the longest single word of its header, otherwise the
    # header wraps mid-word ("Symb / ol") no matter how short the body cells are
    mins = []
    for c in range(ncol):
        longest = max(stringWidth(w, "Helvetica-Bold", 7.9)
                      for w in (header[c].split() or [""])) if header[c] else 0
        mins.append(longest + 9)

    total = float(sum(weights))
    widths = [max(avail_width * w / total, mins[c]) for c, w in enumerate(weights)]
    scale = avail_width / sum(widths)
    if scale < 1:                       # shrink only the columns that have slack
        slack = [max(w - mins[c], 0) for c, w in enumerate(widths)]
        excess = sum(widths) - avail_width
        tot_slack = sum(slack) or 1.0
        widths = [w - excess * slack[c] / tot_slack for c, w in enumerate(widths)]
    else:
        widths = [w * scale for w in widths]

    data = [[Paragraph(inline(h), st["cellh"]) for h in header]]
    for r in body:
        r = (r + [""] * ncol)[:ncol]
        data.append([Paragraph(inline(c), st["cell"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADBG),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, colors.HexColor("#E6E9EE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return t


# -------------------------------------------------------------------------- parser
def parse(md: str, avail_width: float, st, base_dir: str = '.'):
    flow = []
    lines = md.replace("\r\n", "\n").split("\n")
    i, n = 0, len(lines)
    para: list[str] = []

    def flush():
        nonlocal para
        if para:
            flow.append(Paragraph(inline(" ".join(para)), st["body"]))
            para = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush(); i += 1; continue

        m = re.match(r"^!\[[^\]]*\]\(([^)]+)\)\s*$", stripped)
        if m:
            flush()
            img_path = os.path.join(base_dir, m.group(1))
            if os.path.exists(img_path):
                from reportlab.lib.utils import ImageReader
                from reportlab.platypus import Image as RLImage
                iw, ih = ImageReader(img_path).getSize()
                w = min(avail_width, iw * 0.5)
                flow.append(RLImage(img_path, width=w, height=ih * w / iw))
                flow.append(Spacer(1, 6))
            i += 1
            continue

        if stripped.startswith("```"):
            flush()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            code = "\n".join(buf)
            pre = Preformatted(code, ParagraphStyle(
                "code", fontName="Courier", fontSize=7.4, leading=9.2,
                backColor=CODEBG, borderPadding=4, leftIndent=0))
            flow.append(pre); flow.append(Spacer(1, 5))
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush()
            level = len(m.group(1))
            key = "h1" if level == 1 else ("h2" if level == 2 else "h3")
            flow.append(Paragraph(inline(m.group(2).rstrip("#").strip()), st[key]))
            if level == 1:
                flow.append(HRFlowable(width="100%", thickness=1.1, color=NAVY,
                                       spaceBefore=3, spaceAfter=7))
            i += 1
            continue

        if re.match(r"^(\*\*\*|---|___)\s*$", stripped):
            flush()
            flow.append(HRFlowable(width="100%", thickness=0.5, color=RULE,
                                   spaceBefore=5, spaceAfter=7))
            i += 1; continue

        if stripped.startswith(">"):
            flush()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            flow.append(Paragraph(inline(" ".join(buf)), st["quote"]))
            flow.append(Spacer(1, 3))
            continue

        if stripped.startswith("|") and i + 1 < n and re.match(
                r"^\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1].strip()):
            flush()
            rows = [split_row(lines[i])]
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i])); i += 1
            flow.append(build_table(rows, avail_width, st))
            flow.append(Spacer(1, 6))
            continue

        m = re.match(r"^\s*([-*+]|\d+\.)\s+(.*)$", line)
        if m:
            flush()
            ordered = bool(re.match(r"^\d+\.$", m.group(1)))
            items = []
            while i < n:
                mm_ = re.match(r"^\s*([-*+]|\d+\.)\s+(.*)$", lines[i])
                if not mm_:
                    if lines[i].strip() and lines[i].startswith(("  ", "\t")) and items:
                        items[-1] += " " + lines[i].strip(); i += 1; continue
                    break
                items.append(mm_.group(2)); i += 1
            flow.append(ListFlowable(
                [ListItem(Paragraph(inline(t), st["li"]), leftIndent=12)
                 for t in items],
                bulletType="1" if ordered else "bullet",
                bulletFontSize=7, leftIndent=12, spaceAfter=5))
            continue

        para.append(stripped)
        i += 1

    flush()
    return flow


# ------------------------------------------------------------------------- output
def build(md_path: str, pdf_path: str, footer: str):
    with open(md_path, encoding="utf-8") as f:
        md = f.read()

    st = styles()
    left = right = 20 * mm
    top, bottom = 18 * mm, 20 * mm
    avail = A4[0] - left - right

    doc = BaseDocTemplate(pdf_path, pagesize=A4,
                          leftMargin=left, rightMargin=right,
                          topMargin=top, bottomMargin=bottom,
                          title=os.path.basename(md_path), author="Chalmers")
    frame = Frame(left, bottom, avail, A4[1] - top - bottom, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    def decorate(canv, d):
        canv.saveState()
        canv.setFont("Helvetica", 7.3)
        canv.setFillColor(GREY)
        canv.drawString(left, 11 * mm, footer)
        canv.drawRightString(A4[0] - right, 11 * mm, f"{canv.getPageNumber()}")
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.4)
        canv.line(left, 14 * mm, A4[0] - right, 14 * mm)
        canv.restoreState()

    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=decorate)])
    doc.build(parse(md, avail, st, base_dir=os.path.dirname(os.path.abspath(md_path))))
    return doc.page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--footer", default="WaymoActiveInference · Chalmers")
    args = ap.parse_args()

    out = args.output or os.path.splitext(args.markdown)[0] + ".pdf"
    if os.path.exists(out):
        try:
            with open(out, "ab"):
                pass
        except PermissionError:
            sys.exit(f"{out} is locked (open in a viewer?). "
                     f"Close it, or pass -o with a new versioned name.")

    pages = build(args.markdown, out, args.footer)
    print(f"wrote {out}  ({pages} pages, {os.path.getsize(out)/1024:.0f} kB)")


if __name__ == "__main__":
    main()
