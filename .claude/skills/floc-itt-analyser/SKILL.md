---
name: floc-itt-analyser
description: Analyse an ITT, tender or EPC/construction contract pack (PDF) and generate a Functional Location (FLOC) hierarchy, cost-allocation rules and a cost-model workbook in Excel, with page-level traceability (Source IDs, PDF page vs printed page, clickable links) back to the source. Use when asked to build a FLOC, WBS/PBS or cost-allocation structure from a tender document, cross-reference scope to pricing schedules, or trace any cost object back to the page that defines it.
---

# FLOC from ITT pack

Turns a tender pack into a coded, MECE Functional Location tree where every node traces to a page, plus the pricing cross-reference, shared-cost allocation rules, a blank cost model and a validated RFI list. Aligned to WBS / FLOC / CBS / PBS practice: the FLOC tree is the physical/scope breakdown (PBS-style); cost elements (CBS) are applied to its leaves.

Scripts live in `scripts/`; run every one with `python -I` (isolated mode). Requires `pymupdf` and `openpyxl` (`python -m pip install pymupdf openpyxl`).

## Rules that apply throughout
- Never fabricate quantities, rates, scope or page numbers. Use "Not stated" or "Assumption".
- Record the PDF page at the moment each item is captured (do not back-fill later).
- PDF page = physical page, authoritative, used for hyperlinks. Printed page = number on the page; it restarts per embedded document, so the offset is per part.
- Evidence = paraphrase, or a quote of 15 words or fewer.
- British English, dd/mm/yyyy dates, AUD unless the document says otherwise.
- Referenced schedules, drawings, appendices or MTOs not in the PDF, and "NOT USED" schedules, are gaps: record them, do not assume contents.

## Workflow

1. **Set up config.** Copy `config/winu_config.json`; set project code, document id, PDF path, page count, numbering widths. Fill `parts` after step 2.
2. **Extract text per page and detect offsets.**
   `python -I scripts/extract_pages.py <pdf> <work>/pages`
   Writes `page_NNNN.txt`, `pages.jsonl` (printed label per page), `offset_report.md` (PDF-to-printed offset per run), `scanned_pages.txt`. Any page listed as scanned or low-text must be read visually or logged as a gap. Copy the offset runs into the config `parts`.
3. **Read the whole pack before extracting.** Read the contents pages of every embedded document and map the parts (tender documents, agreement, general conditions, specification, scope of work, schedules, appendices). List every referenced document, drawing or schedule and check whether it is in the PDF.
4. **Page-by-page extraction pass.** Follow `references/extraction_pass.md`: read every page in full and write items (one JSON element each, with `pdf_page` set when captured) into `<work>/extract/items_<from>_<to>.json`. Split large packs by page range and run the ranges in parallel; each range owner reads every page. Item types: Scope, Area/Facility, Work Package, Discipline, Interface, Exclusion, Provisional Sum, Pricing Structure, Commercial Form, Allocation Basis, Programme, Quantity/Rate Stated, Referenced Not Included, Ambiguity/Risk.
5. **Consolidate to the Source Register.**
   `python -I scripts/consolidate_sources.py <work>/extract <work>/pages <config> <work>/sources.json`
   Assigns SRC-0001... in page order and the printed page per source.
6. **Design the hierarchy** (`references/numbering_convention.md`): 4-5 levels, MECE, each node with status (In scope / Excluded / Provisional), discipline(s), responsibility, a Primary hook (page + keyword) and mapping rules (page range + optional keyword) that claim every source for exactly one FLOC. Write `floc_spec.json` (schema in the `resolve_spec.py` docstring; example in `templates/floc_spec.example.json`). Add the pricing lines (Schedule A etc.), allocation rules (each cites a source hook or is `Assumption`) and RFIs (each cites the page that prompted it).
7. **Resolve and build.**
   `python -I scripts/resolve_spec.py <sources> <spec> <config> <data.json>` (fix every `resolve_errors` hook)
   `python -I scripts/build_workbook.py <data.json> <out.xlsx> --pages-dir <work>/pages`
8. **Validate** (`references/validation_checklist.md`). Open the Validation sheet; resolve every FAIL, explain every WARN. Read the REVIEW rows of the spot-check against the PDF yourself. Have a second reader re-read a 10% sample of the links before issue.
9. **Report** the page-count and offset findings, the hierarchy outline, key gaps and RFIs. Hand the cost model back blank: only fill values the pack states.

## Reuse notes
- `scripts/make_template.py` writes an empty `FLOC_workbook_template.xlsx` (same sheets, validations, formulas).
- Everything project-specific lives in the config and spec JSON; the scripts are generic.
- Hyperlinks are `file:///<abs path>#page=N`; Acrobat, Edge and Chrome honour the page fragment, some Excel set-ups open page 1. The PDF Page column is the fallback.
