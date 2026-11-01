#!/usr/bin/env python3
"""Helpers for the winu-bod-translator skill. Needs python-docx. Run with python -I.

  outline  <docx>                 Print the heading outline, with caption and table counts.
  find     <docx> <text>          Print the heading path, style and text of paragraphs containing <text>.
  scan     <file> [--term T ...]  Report leftover Rhodes Ridge terms in a text file (exit 1 if any).
"""
import argparse
import re
import sys
from pathlib import Path

DEFAULT_TERMS = ["Rhodes Ridge", "Rhodes", "RR1", "RR Phase"]


def load(path):
    from docx import Document
    return Document(str(path))


def heading_level(style):
    parts = style.split()
    return int(parts[-1]) if style.startswith("Heading") and parts[-1].isdigit() else None


def outline(path):
    d = load(path)
    for p in d.paragraphs:
        s = p.style.name
        if p.text.strip() and (s.startswith("Heading") or s in ("Title", "Caption")):
            lvl = heading_level(s)
            indent = "  " * (lvl - 1) if lvl else ""
            print(f"{indent}[{s}] {p.text.strip()}")
    print(f"\n{len(d.tables)} tables, {len(d.inline_shapes)} inline images")


def find(path, text):
    d = load(path)
    trail = {}
    needle = text.lower()
    hits = 0
    for p in d.paragraphs:
        s = p.style.name
        lvl = heading_level(s)
        if lvl:
            trail = {k: v for k, v in trail.items() if k < lvl}
            trail[lvl] = p.text.strip()
        if needle in p.text.lower():
            hits += 1
            print(f"{' > '.join(trail[k] for k in sorted(trail))}\n  [{s}] {p.text.strip()}\n")
    for ti, t in enumerate(d.tables, 1):
        for r in t.rows:
            row = [c.text.strip() for c in r.cells]
            if needle in " ".join(row).lower():
                hits += 1
                print(f"Table {ti} (order in document body): {row}\n")
    if not hits:
        print("No match. The passage may be paraphrased; search a shorter distinctive phrase.")
        sys.exit(1)


def scan(path, terms):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    found = 0
    for n, line in enumerate(text.splitlines(), 1):
        for t in terms:
            if re.search(re.escape(t), line, re.I):
                found += 1
                print(f"line {n}: '{t}' -> {line.strip()[:120]}")
    print(f"{found} leftover(s)" if found else "Clean: no leftover terms")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("outline").add_argument("docx")
    f = sub.add_parser("find")
    f.add_argument("docx")
    f.add_argument("text")
    s = sub.add_parser("scan")
    s.add_argument("file")
    s.add_argument("--term", action="append", default=[])
    a = ap.parse_args()
    if a.cmd == "outline":
        outline(a.docx)
    elif a.cmd == "find":
        find(a.docx, a.text)
    else:
        scan(a.file, DEFAULT_TERMS + a.term)
