"""Convert a markdown report file into a formatted .docx working copy.

Usage:
    python md2docx.py <source.md> <target.docx> [--cjk]

Handles headings (# to ######), bullet lists, numbered lists, pipe tables,
inline bold (**text**), and blockquote lines. Body is Times New Roman 12 pt
with 1.5 line spacing; Chinese documents use Microsoft YaHei 12 pt.
"""

import argparse
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BLACK = RGBColor(0x00, 0x00, 0x00)
GREY = RGBColor(0x40, 0x40, 0x40)


def _set_run_font(run, cjk, size, bold=False):
    run.font.size = Pt(size)
    run.bold = bold
    if cjk:
        run.font.name = "Microsoft YaHei"
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    else:
        run.font.name = "Times New Roman"
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:ascii"), "Times New Roman")
        rfonts.set(qn("w:hAnsi"), "Times New Roman")


def _emit_runs(p, text, cjk, size, bold):
    """Inner pass: split `code` spans; inherit the outer bold state."""
    for part in re.split(r"(`.+?`)", text):
        if part.startswith("`") and part.endswith("`"):
            run = p.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(size - 1)
            run.bold = bold
            rpr = run._element.get_or_add_rPr()
            rfonts = rpr.get_or_add_rFonts()
            rfonts.set(qn("w:ascii"), "Consolas")
            rfonts.set(qn("w:hAnsi"), "Consolas")
        else:
            run = p.add_run(part)
            _set_run_font(run, cjk, size, bold=bold)


def _add_inline(p, text, cjk, size, bold=False):
    """Split **bold** markup first, then `code` inside each segment."""
    for part in re.split(r"(\*\*.+?\*\*)", text):
        if part.startswith("**") and part.endswith("**"):
            _emit_runs(p, part[2:-2], cjk, size, True)
        else:
            _emit_runs(p, part, cjk, size, bold)


def md_to_docx(md_path, docx_path, cjk=False):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    doc = Document()
    for s in doc.sections:
        s.top_margin = Cm(2.2)
        s.bottom_margin = Cm(2.2)
        s.left_margin = Cm(2.5)
        s.right_margin = Cm(2.5)
    st = doc.styles["Normal"]
    st.font.size = Pt(12)
    st.paragraph_format.line_spacing = 1.5
    if cjk:
        st.font.name = "Microsoft YaHei"
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    else:
        st.font.name = "Times New Roman"
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:ascii"), "Times New Roman")
        rfonts.set(qn("w:hAnsi"), "Times New Roman")

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        # horizontal rule
        if re.match(r"^-{3,}$", line.strip()):
            i += 1
            continue
        # blockquote changelog
        if line.strip().startswith(">"):
            p = doc.add_paragraph()
            _add_inline(p, line.strip().lstrip("> "), cjk, 9.5)
            for r in p.runs:
                r.italic = True
                r.font.color.rgb = GREY
            p.paragraph_format.space_after = Pt(4)
            i += 1
            continue
        # fenced code block: keep indentation, monospace
        if line.strip().startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip().replace("\t", "    "))
                i += 1
            i += 1
            for cl in code:
                p = doc.add_paragraph()
                r = p.add_run(cl if cl else " ")
                r.font.name = "Consolas"
                r.font.size = Pt(10)
                rpr = r._element.get_or_add_rPr()
                rfonts = rpr.get_or_add_rFonts()
                rfonts.set(qn("w:eastAsia"), "Consolas")
                for t in r._element.findall(qn("w:t")):
                    t.set(qn("xml:space"), "preserve")
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.left_indent = Cm(0.5)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue
        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            p = doc.add_paragraph(style="Heading %d" % min(level, 4))
            r = p.add_run(text)
            sizes = {1: 14, 2: 12, 3: 12, 4: 11, 5: 11, 6: 10.5}
            _set_run_font(r, cjk, sizes.get(level, 12), bold=True)
            r.font.color.rgb = BLACK
            p.paragraph_format.space_before = Pt(12 if level <= 2 else 8)
            p.paragraph_format.space_after = Pt(4)
            i += 1
            continue
        # table detection (consecutive | lines)
        if line.strip().startswith("|"):
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1
            rows = []
            for tl in tbl_lines:
                cells = [c.strip() for c in tl.strip("|").split("|")]
                if all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                    continue
                rows.append(cells)
            if rows:
                ncols = max(len(r) for r in rows)
                table = doc.add_table(rows=len(rows), cols=ncols)
                table.style = "Table Grid"
                for ri, rdata in enumerate(rows):
                    for ci in range(ncols):
                        cell = table.cell(ri, ci)
                        cell.text = ""
                        para = cell.paragraphs[0]
                        _add_inline(para, rdata[ci] if ci < len(rdata) else "",
                                    cjk, 10, bold=(ri == 0))
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue
        # bullet
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            p = doc.add_paragraph(style="List Bullet")
            _add_inline(p, m.group(1).strip(), cjk, 12)
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue
        # numbered: literal numbering, restarts per block
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m:
            num = int(m.group(1))
            p = doc.add_paragraph()
            r0 = p.add_run("%d. " % num)
            _set_run_font(r0, cjk, 12)
            _add_inline(p, m.group(2).strip(), cjk, 12)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.left_indent = Cm(0.7)
            p.paragraph_format.first_line_indent = Cm(-0.45)
            i += 1
            continue
        # normal paragraph, may contain inline bold
        p = doc.add_paragraph()
        _add_inline(p, line.strip(), cjk, 12)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(6)
        i += 1

    doc.save(docx_path)
    print("Saved:", docx_path, os.path.getsize(docx_path))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="markdown file to convert")
    ap.add_argument("target", help="docx file to write")
    ap.add_argument("--cjk", action="store_true",
                    help="use a Chinese-capable font for a Chinese document")
    a = ap.parse_args()
    if not os.path.isfile(a.source):
        print("Source not found:", a.source)
        return 1
    md_to_docx(a.source, a.target, cjk=a.cjk)
    return 0


if __name__ == "__main__":
    sys.exit(main())