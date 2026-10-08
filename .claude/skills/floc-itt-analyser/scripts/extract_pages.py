#!/usr/bin/env python3
"""Per-page text extraction with printed-page detection.

Usage:  python -I extract_pages.py <pdf> <out_dir>

Writes to <out_dir>:
  pages.jsonl          one record per PDF page: pdf_page, chars, printed_label, printed_of,
                       header_doc, first_lines, scanned_suspect
  page_NNNN.txt        raw text of each page (1-based, zero padded to 4 digits)
  offset_report.md     PDF-to-printed offset runs (offset changes at every section break)
  scanned_pages.txt    pages with little/no text layer (OCR or manual read needed)

Printed-page detection looks for footers/headers such as "Page 12 of 40", "Page i of ii",
and "Page 12". Run-length encoding of (pdf_page - printed_page) gives the offset map; a
multi-part pack (tender docs + contract + schedules) will have several offsets.
Never guess a page number: pages with no detectable label are reported as "not printed".
"""
import json, re, sys
from pathlib import Path
try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF
    import fitz

ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
PAGE_RE = re.compile(r"\bPage\s+([0-9]+|[ivxlc]+)\s+of\s+([0-9]+|[ivxlc]+)\b", re.I)
SLASH_RE = re.compile(r"(?<![\d/])(\d{1,4})\s*/\s*(\d{1,4})(?![\d/])")  # embedded docs: "17 / 125"
DASHED_RE = re.compile(r"^\s*-\s*([0-9]{1,4}|[ivxlc]{1,6})\s*-\s*$", re.I | re.M)  # "- 12 -" header (General Conditions)
PAGE_ONLY_RE = re.compile(r"^\s*-?\s*(?:Page\s+)?([0-9]{1,4}|[ivxlc]{1,6})\s*-?\s*$", re.I | re.M)  # "12", "Page 12", "- 12 -", "- iv -"
DOCNO_RE = re.compile(r"Document\s+No\.?\s*:?\s*([A-Z0-9][A-Z0-9\-_./]+)", re.I)
SCAN_MIN_CHARS = 40


def roman(s):
    s = s.lower(); total = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        total += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return total


def detect_label(text):
    m = PAGE_RE.search(text)
    if m:
        return m.group(1), m.group(2)
    m = SLASH_RE.search(text[:1500])
    if m and int(m.group(1)) <= int(m.group(2)):
        return m.group(1), m.group(2)
    m = DASHED_RE.search("\n".join(text.strip().splitlines()[:3]))
    if m:
        return m.group(1), None
    tail = "\n".join(text.strip().splitlines()[-4:])
    m = PAGE_ONLY_RE.search(tail)
    return (m.group(1), None) if m else (None, None)


def main(pdf, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    recs = []
    for i, page in enumerate(doc, 1):
        text = page.get_text()
        (out / f"page_{i:04d}.txt").write_text(text, encoding="utf-8")
        label, of = detect_label(text)
        dm = DOCNO_RE.search(text)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        recs.append({
            "pdf_page": i, "chars": len(text.strip()), "printed_label": label,
            "printed_of": of, "header_doc": dm.group(1) if dm else None,
            "first_lines": lines[:6], "scanned_suspect": len(text.strip()) < SCAN_MIN_CHARS,
        })
    with open(out / "pages.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

    # offset runs
    runs, cur = [], None
    for r in recs:
        lab = r["printed_label"]
        if lab is None:
            continue
        n = int(lab) if lab.isdigit() else roman(lab) if re.fullmatch(r"[ivxlc]+", lab, re.I) else None
        if n is None:
            continue
        kind = "arabic" if lab.isdigit() else "roman"
        off = r["pdf_page"] - n
        if cur and cur["offset"] == off and cur["kind"] == kind and r["header_doc"] == cur["doc"]:
            cur["end"] = r["pdf_page"]
        else:
            cur = {"start": r["pdf_page"], "end": r["pdf_page"], "offset": off, "kind": kind, "doc": r["header_doc"]}
            runs.append(cur)
    with open(out / "offset_report.md", "w", encoding="utf-8") as f:
        f.write(f"# Offset report\n\nPDF pages: {len(recs)}\n\n| PDF from | PDF to | Offset (pdf - printed) | Numbering | Doc no. |\n|---|---|---|---|---|\n")
        for r in runs:
            f.write(f"| {r['start']} | {r['end']} | {r['offset']} | {r['kind']} | {r['doc'] or ''} |\n")
        unl = [r["pdf_page"] for r in recs if r["printed_label"] is None]
        f.write(f"\nPages with no detectable printed label: {len(unl)}\n")
    scanned = [r["pdf_page"] for r in recs if r["scanned_suspect"]]
    (out / "scanned_pages.txt").write_text("\n".join(map(str, scanned)), encoding="utf-8")
    print(f"{len(recs)} pages; {len(runs)} offset runs; {len(scanned)} low-text pages -> {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
