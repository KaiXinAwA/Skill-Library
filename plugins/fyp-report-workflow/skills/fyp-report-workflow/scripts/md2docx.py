"""Convert a markdown report file into a formatted .docx working copy.

Usage:
    python md2docx.py <source.md> <target.docx>

Handles headings (# to ######), bullet lists, numbered lists, pipe tables,
inline bold (**text**), and blockquote lines. Output is a Calibri 11 working
copy, not the final thesis layout.
"""

import argparse
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GREY = RGBColor(0x40, 0x40, 0x40)


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
    if cjk:
        st.font.name = "Microsoft YaHei"
        st.font.size = Pt(10.5)
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    else:
        st.font.name = "Calibri"
        st.font.size = Pt(11)

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
            r = p.add_run(line.strip().lstrip("> "))
            r.italic = True
            r.font.size = Pt(9.5)
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
            # built-in heading styles so Word's navigation pane shows the outline;
            # level 5 and 6 reuse Heading 4 rather than inventing uncatalogued styles
            p = doc.add_paragraph(style="Heading %d" % min(level, 4))
            r = p.add_run(text)
            r.bold = True
            r.font.color.rgb = NAVY
            sizes = {1: 16, 2: 14, 3: 12, 4: 11, 5: 10.5, 6: 10}
            r.font.size = Pt(sizes.get(level, 11))
            if cjk:
                r.font.name = "Microsoft YaHei"
                rpr = r._element.get_or_add_rPr()
                rfonts = rpr.get_or_add_rFonts()
                rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")
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
                    continue  # separator row
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
                        run = para.add_run(rdata[ci] if ci < len(rdata) else "")
                        run.font.size = Pt(9.5)
                        if ri == 0:
                            run.bold = True
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue
        # bullet
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            p = doc.add_paragraph(style="List Bullet")
            r = p.add_run(m.group(1).strip())
            r.font.size = Pt(11)
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue
        # numbered: literal numbering, restarts per block
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m:
            num = int(m.group(1))
            p = doc.add_paragraph()
            r = p.add_run("%d. %s" % (num, m.group(2).strip()))
            r.font.size = Pt(11)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.left_indent = Cm(0.7)
            p.paragraph_format.first_line_indent = Cm(-0.45)
            i += 1
            continue
        # normal paragraph, may contain inline bold
        p = doc.add_paragraph()
        text = line.strip()
        parts = re.split(r"(\*\*.+?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = p.add_run(part[2:-2])
                run.bold = True
            else:
                run = p.add_run(part)
            run.font.size = Pt(11)
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
