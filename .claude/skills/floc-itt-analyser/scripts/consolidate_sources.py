#!/usr/bin/env python3
"""Merge per-range extraction files into one Source Register with stable Source IDs.

Usage: python -I consolidate_sources.py <extract_dir> <pages_dir> <config.json> <out_sources.json>

  <extract_dir>  holds items_*.json written during the page-by-page pass (each element has pdf_page)
  <pages_dir>    output of extract_pages.py (pages.jsonl + page_NNNN.txt)

Source IDs (SRC-0001 ...) are assigned in PDF page order, then file order, so they are stable for a
given set of extraction files. Printed page = detected label on that PDF page; where there is none the
config 'parts' offset is used and the record is flagged printed_page_basis='offset' (never guessed
silently). Items whose pdf_page is outside the document are dropped and listed.
"""
import glob, json, re, sys
from pathlib import Path

CONF_OK = {"High", "Medium", "Low"}


def load_labels(pages_dir):
    lab = {}
    for line in open(Path(pages_dir) / "pages.jsonl", encoding="utf-8"):
        r = json.loads(line)
        lab[r["pdf_page"]] = r
    return lab


def part_for(page, parts):
    for p in parts:
        if p["pdf_from"] <= page <= p["pdf_to"]:
            return p
    return None


def main(extract_dir, pages_dir, config_path, out):
    cfg = json.load(open(config_path, encoding="utf-8"))
    labels = load_labels(pages_dir)
    n_pages = len(labels)
    items, dropped = [], []
    for fn in sorted(glob.glob(str(Path(extract_dir) / "items_*.json"))):
        for k, it in enumerate(json.load(open(fn, encoding="utf-8"))):
            it["_file"], it["_seq"] = Path(fn).name, k
            if not isinstance(it.get("pdf_page"), int) or not 1 <= it["pdf_page"] <= n_pages:
                dropped.append(it); continue
            items.append(it)
    items.sort(key=lambda i: (i["pdf_page"], i["_file"], i["_seq"]))
    out_rows = []
    for n, it in enumerate(items, 1):
        pg = it["pdf_page"]; rec = labels[pg]; part = part_for(pg, cfg["parts"])
        label, basis = rec["printed_label"], "detected"
        if label is None:
            if part and part.get("offset") is not None and pg - part["offset"] > 0:
                label, basis = str(pg - part["offset"]), "offset"
            else:
                label, basis = None, "none"
        conf = it.get("confidence") if it.get("confidence") in CONF_OK else "Low"
        out_rows.append({
            "source_id": f"SRC-{n:04d}", "document": cfg["document_id"],
            "part": part["name"] if part else "Unknown", "section": it.get("section"),
            "pdf_page": pg, "printed_page": label, "printed_page_basis": basis,
            "figure_table": it.get("figure_table"), "item_type": it.get("item_type"),
            "title": it.get("title"), "evidence": it.get("evidence"),
            "suggested_area": it.get("suggested_area"), "suggested_package": it.get("suggested_package"),
            "disciplines": it.get("disciplines") or [], "confidence": conf, "notes": it.get("notes"),
        })
    json.dump(out_rows, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(out_rows)} sources written to {out}; {len(dropped)} dropped (page out of range/invalid)")
    for d in dropped[:20]:
        print("  dropped:", d.get("_file"), d.get("pdf_page"), d.get("title"))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
