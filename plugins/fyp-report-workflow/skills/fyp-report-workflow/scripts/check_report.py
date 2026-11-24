"""Check a chapter source against the fixed FYP structure and the writing rules.

Usage:
    python check_report.py <chapter.md> [--docx <chapter.docx>]

Blocking checks (exit 1):
  1. Every required top-level section number for that chapter is present as a heading.
  2. No em dash (U+2014) anywhere in the file.
  3. No contractions.
  4. No first or second person in body text.
  5. In-text citations map to the chapter reference list (chapters that carry one).
  6. Same-chapter section cross-references point to an existing heading number.
  7. Derived docx carries no leftover markdown markers (**, backticks).

Warnings (printed, do not block delivery):
  8. Reference-list entries never cited in the body (orphans).
  9. docx vs md paragraph / word count delta beyond tolerance.
 10. Project abbreviation used before its full-term definition.
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
HEADING_NUM = re.compile(r"^(\d+\.\d+(?:\.\d+)?)")

SUR = r"[A-ZÀ-ſ][A-Za-zÀ-ſ'’\-]+"
INIT = r"(?:[A-Z]\.[\-A-Z]?\s*)+"
AUTHOR_LIST = (
    SUR + r"(?:,\s+" + INIT + r")?"
    r"(?:,\s+" + SUR + r"(?:,\s+" + INIT + r")?)*"
    r"(?:,\s+and\s+" + SUR + r"|\s+and\s+" + SUR + r")?"
)

# Citations. The whole author list is consumed so co-authors are not treated
# as separate references; only the first surname is kept.
CITE_NARR = re.compile(r"\b(" + AUTHOR_LIST + r")(?:\s+et al\.)?\s*\((?:19|20)\d\d\)")
CITE_PAREN = re.compile(
    r"\(\s*(" + AUTHOR_LIST + r")(?:\s+et al\.)?,?\s*(?:19|20)\d\d\)"
)
CITE_INITIALS_PAREN = re.compile(
    r"\(\s*(?:" + INIT + r")(" + SUR + r")(?:\s+et al\.)?,?\s*(?:19|20)\d\d\)"
)
CITE_TABLE = re.compile(
    r"\(\s*(" + SUR + r")(?:\s+et al\.)?\s+(?:19|20)\d\d\)"
)
REF_AUTHOR = re.compile(r"^[-*]\s+([A-ZÀ-ſ][A-Za-zÀ-ſ'’\-]+)")
SECTION_REF = re.compile(r"[Ss]ection\s+(\d+\.\d+(?:\.\d+)?)")

# Prose lines that restate a full reference entry (author initials included);
# they duplicate the bibliography and are not counted as body citations.
RESTATEMENT = re.compile(r",\s*" + INIT)

# Names that are tool or system labels, never a citation author.
EXCLUDE_SURNAMES = {
    "Section", "Chapter", "Test", "Stage", "The", "This", "Each", "FYP",
    "OJ", "RAG", "LC-RAG", "TutorLLM", "HypoCompass", "PyTutor", "DCC",
    "Iris", "Online", "DebugTutor", "ChartCode", "Sidekick", "Python",
}

# Project abbreviations that should carry a full-term definition at first use.
ABBREV = {
    "AI": "artificial intelligence",
    "LLM": "large language model",
    "OOP": "object-oriented programming",
    "RAG": "retrieval-augmented generation",
}


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


def heading_numbers(headings):
    nums = set()
    for h in headings:
        m = HEADING_NUM.match(h.strip())
        if m:
            nums.add(m.group(1))
    return nums


def count_words(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def _first_surname(token):
    m = re.match(SUR, token)
    return m.group(0) if m else None


def collect_citations(body_lines):
    cited = set()
    for line in body_lines:
        if RESTATEMENT.search(line):
            continue
        for m in CITE_NARR.finditer(line):
            name = _first_surname(m.group(1))
            if name and name not in EXCLUDE_SURNAMES:
                cited.add(name)
        for m in CITE_PAREN.finditer(line):
            name = _first_surname(m.group(1))
            if name and name not in EXCLUDE_SURNAMES:
                cited.add(name)
        for m in CITE_INITIALS_PAREN.finditer(line):
            name = m.group(1)
            if name not in EXCLUDE_SURNAMES:
                cited.add(name)
        for m in CITE_TABLE.finditer(line):
            name = m.group(1)
            if name not in EXCLUDE_SURNAMES:
                cited.add(name)
    return cited


def collect_ref_authors(lines):
    listed = set()
    for line in lines:
        m = REF_AUTHOR.match(line.strip())
        if m:
            listed.add(m.group(1))
    return listed


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
    warnings = []

    if ch and ch in REQUIRED:
        present = {re.match(r"^(\d+\.\d+)", h).group(1) for h in headings if re.match(r"^(\d+\.\d+)", h)}
        missing = [n for n in REQUIRED[ch] if n not in present]
        if missing:
            problems.append("missing required sections: " + ", ".join(missing))

    body = [(i + 1, l) for i, l in enumerate(lines)
            if not l.strip().startswith(">") and l.strip() and not is_reference_line(l)]
    body_lines = [l for _, l in body]

    em = [(i, l) for i, l in enumerate(lines, 1) if "\u2014" in l]
    if em:
        problems.append("em dash on line(s): " + ", ".join(str(i) for i, _ in em))

    con = [(i, l) for i, l in body if CONTRACTIONS.search(l)]
    if con:
        problems.append("contractions on line(s): " + ", ".join(str(i) for i, _ in con))

    per = [(i, l) for i, l in body if PERSON.search(l)]
    if per:
        problems.append("first or second person on line(s): " + ", ".join(str(i) for i, _ in per))

    # 5. Citation <-> reference list correspondence (only when the chapter has a list).
    ref_lines = [l for l in lines if is_reference_line(l)]
    has_list = len(ref_lines) > 0
    cited = collect_citations(body_lines)
    listed = collect_ref_authors(ref_lines)
    if has_list:
        missing_ref = sorted(cited - listed - EXCLUDE_SURNAMES)
        if missing_ref:
            problems.append("cited but missing from reference list: " + ", ".join(missing_ref))
        orphans = sorted(listed - cited)
        if orphans:
            warnings.append("reference entries never cited in body: " + ", ".join(orphans))

    # 6. Same-chapter section cross-references must resolve to a local heading.
    nums = heading_numbers(headings)
    for i, l in body:
        for m in SECTION_REF.finditer(l):
            ref = m.group(1)
            ref_ch = ref.split(".")[0]
            if ch and ref_ch == ch and ref not in nums:
                problems.append("section reference %s has no matching heading (line %d)" % (ref, i))

    # 10. Abbreviation first-use definition (warning level). Headings and the
    # project-title compound "AI-Assisted" do not count as a body first use.
    abbrev_lines = [l for l in body_lines if not l.lstrip().startswith("#")]
    full_text = "\n".join(abbrev_lines)
    for abbr, full in ABBREV.items():
        m_abbr = re.search(r"\b" + abbr + r"\b(?!-Assisted)", full_text)
        if not m_abbr:
            continue
        first = m_abbr.start()
        def_pat = re.compile(re.escape(full) + r"\s*\(\s*" + abbr + r"\s*\)", re.IGNORECASE)
        window = full_text[:first + len(abbr) + 3]
        if def_pat.search(window) is None:
            warnings.append("abbreviation %s first used without a preceding '%s (...)' definition" % (abbr, full))

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
    return problems, warnings, lines


def check_docx(path, md_lines):
    from docx import Document

    d = Document(path)
    docx_paras = [p.text for p in d.paragraphs if p.text.strip()]
    text = "\n".join(p.text for p in d.paragraphs)
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                text += "\n" + c.text

    problems = []
    warnings = []

    leftover_bold = text.count("**")
    leftover_backtick = text.count("`")
    if leftover_bold:
        problems.append("leftover ** markdown marker in docx: %d occurrence(s)" % leftover_bold)
    if leftover_backtick:
        problems.append("leftover backtick markdown marker in docx: %d occurrence(s)" % leftover_backtick)

    # 9. docx <-> md structural delta. Bibliography and table lines count on the md side.
    md_paras = [l for l in md_lines if l.strip() and not l.strip().startswith("|") and not re.match(r"^-{3,}$", l.strip())]
    md_words = count_words("\n".join(md_lines))
    docx_words = count_words(text)
    para_delta = abs(len(docx_paras) - len(md_paras))
    if para_delta > 3:
        warnings.append("paragraph count delta md=%d docx=%d (diff %d)" % (len(md_paras), len(docx_paras), para_delta))
    if md_words:
        word_ratio = abs(docx_words - md_words) / md_words
        if word_ratio > 0.10:
            warnings.append("word count delta md=%d docx=%d (%.0f%%)" % (md_words, docx_words, word_ratio * 100))

    print("docx:", path)
    print("  paragraphs:", len(docx_paras), "| tables:", len(d.tables),
          "| rows:", [len(t.rows) for t in d.tables])
    print("  em dash:", text.count("\u2014"), "| contractions:", len(CONTRACTIONS.findall(text)))
    return problems, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--docx", default=None)
    a = ap.parse_args()
    if not os.path.isfile(a.md):
        print("Source not found:", a.md)
        return 1

    problems, warnings, md_lines = check_md(a.md)
    if a.docx and os.path.isfile(a.docx):
        p2, w2 = check_docx(a.docx, md_lines)
        problems += p2
        warnings += w2
    elif a.docx:
        problems.append("docx not found: " + a.docx)

    for w in warnings:
        print("  WARN:", w)

    if problems:
        print("FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())