"""Check a chapter source against the fixed FYP structure and the writing rules.

Usage:
    python check_report.py <chapter.md> [--docx <chapter.docx>]

Blocking checks:
  1. Every required top-level section number for that chapter is present as a heading.
  2. No em dash (U+2014) anywhere in the file.
  3. No contractions.
  4. No first or second person in body text.

Reported only:
  5. Heading count, pipe-table count, and docx paragraph and table structure.

Exit code 1 when a blocking check fails, 0 when all pass.
"""

import argparse
import io
import os
import re
import sys

REQUIRED = {
    "1": ["1.1", "1.2", "1.3", "1.4", "1.5"],
    "2": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"],
    "3": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10"],
}

CONTRACTIONS = re.compile(
    r"\b(?:don't|doesn't|didn't|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|"
    r"can't|won't|wouldn't|shouldn't|couldn't|it's|that's|there's|what's|let's|"
    r"we're|they're|you're|I'm|I've|I'll|I'd|we've|we'll|they've|they'll|"
    r"you've|you'll|he's|she's|here's)\b",
    re.IGNORECASE,
)

PERSON = re.compile(r"\b(?:I|we|We|our|Our|us|my|My|me|you|You|your|Your|yours)\b")

HEADING = re.compile(r"^(#{2,4})\s+(.+)$")


def is_reference_line(s):
    """Bibliography entries carry author initials and a year; skip them in the person check."""
    s = s.strip()
    if not s:
        return False
    return bool(re.match(r"^[-*]\s+[A-Z].*\((?:19|20)\d\d", s))


def chapter_of(headings):
    for h in headings:
        m = re.match(r"^(\d+)\.\d", h.strip())
        if m:
            return m.group(1)
    return None


def check_md(path):
    lines = io.open(path, encoding="utf-8").read().split("\n")
    headings = []
    tables = 0
    in_table = False
    for line in lines:
        s = line.strip()
        m = HEADING.match(line)
        if m:
            headings.append(m.group(2).strip())
        if s.startswith("|"):
            if not in_table:
                tables += 1
                in_table = True
        else:
            in_table = False

    ch = chapter_of(headings)
    problems = []

    if ch and ch in REQUIRED:
        present = {re.match(r"^(\d+\.\d+)", h).group(1) for h in headings if re.match(r"^(\d+\.\d+)", h)}
        missing = [n for n in REQUIRED[ch] if n not in present]
        if missing:
            problems.append("missing required sections: " + ", ".join(missing))

    body = [(i + 1, l) for i, l in enumerate(lines)
            if not l.strip().startswith(">") and l.strip() and not is_reference_line(l)]

    em = [(i, l) for i, l in enumerate(lines, 1) if "\u2014" in l]
    if em:
        problems.append("em dash on line(s): " + ", ".join(str(i) for i, _ in em))

    con = [(i, l) for i, l in body if CONTRACTIONS.search(l)]
    if con:
        problems.append("contractions on line(s): " + ", ".join(str(i) for i, _ in con))

    per = [(i, l) for i, l in body if PERSON.search(l)]
    if per:
        problems.append("first or second person on line(s): " + ", ".join(str(i) for i, _ in per))

    print("source:", path)
    print("  chapter:", ch or "unknown", "| headings:", len(headings), "| pipe tables:", tables)
    if per:
        for i, l in per[:6]:
            for hit in set(PERSON.findall(l)):
                print("    line %d: %r" % (i, hit))
    if con:
        for i, l in con[:6]:
            for hit in set(CONTRACTIONS.findall(l)):
                print("    line %d: %r" % (i, hit))
    return problems


def check_docx(path):
    from docx import Document

    d = Document(path)
    text = "\n".join(p.text for p in d.paragraphs)
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                text += "\n" + c.text
    print("docx:", path)
    print("  paragraphs:", len(d.paragraphs), "| tables:", len(d.tables),
          "| rows:", [len(t.rows) for t in d.tables])
    print("  em dash:", text.count("\u2014"), "| contractions:", len(CONTRACTIONS.findall(text)))
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--docx", default=None)
    a = ap.parse_args()
    if not os.path.isfile(a.md):
        print("Source not found:", a.md)
        return 1

    problems = check_md(a.md)
    if a.docx and os.path.isfile(a.docx):
        problems += check_docx(a.docx)
    elif a.docx:
        problems.append("docx not found: " + a.docx)

    if problems:
        print("FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
