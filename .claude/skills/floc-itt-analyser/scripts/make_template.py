#!/usr/bin/env python3
"""Write an empty, formula-ready FLOC workbook template.

Usage: python -I make_template.py <config.json> <out.xlsx>
Builds the workbook from a one-node skeleton so every sheet, validation and formula is present.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I mode does not add the script folder
from build_workbook import build

META_KEYS = ("project", "project_code", "client", "document_id", "document_title", "pdf_file", "pdf_page_count",
             "currency", "workbook_version", "levels", "level_colours", "level_font_white", "parts", "link_note",
             "numbering")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    data = {"meta": {k: cfg[k] for k in META_KEYS}, "sources": [], "pricing": [], "allocation_rules": [], "rfis": [],
            "resolve_errors": [],
            "flocs": [{"floc_id": cfg["project_code"], "parent_id": None, "level": 1, "key": "root",
                       "description": "[Project]", "disciplines": [], "responsibility": "", "scope_status": "In scope",
                       "assumption": True, "notes": "Template row", "primary_source": None, "supporting_sources": []}]}
    build(data, sys.argv[2])
    print("wrote", sys.argv[2])
