#!/usr/bin/env python3
"""Build the FLOC / cost-allocation workbook from data.json (output of resolve_spec.py).

Usage: python -I build_workbook.py <data.json> <out.xlsx> [--pages-dir DIR] [--sample 0.10] [--author NAME]

Sheets: README, FLOC_Hierarchy, Source_Register, FLOC_to_Source_Map, Scope_Extraction, FLOC_to_Pricing_Map,
Allocation_Rules, Cost_Model_Template, Gaps_and_RFIs, Validation.
All values are static except the Cost_Model_Template formulas and a few live checks on the Validation sheet.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I mode does not add the script folder
from validate import pdf_url, run_checks

HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF")
RED = PatternFill("solid", fgColor="FF9999")
AMBER = PatternFill("solid", fgColor="FFE699")
GREEN = PatternFill("solid", fgColor="C6E0B4")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
LINK_FONT = Font(color="0563C1", underline="single")
SCOPE_TYPES_OUT = {"Scope", "Area/Facility", "Work Package", "Discipline", "Interface", "Exclusion",
                   "Provisional Sum", "Pricing Structure", "Commercial Form", "Allocation Basis", "Programme",
                   "Quantity/Rate Stated"}


def header(ws, row, cols, widths=None):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.fill, cell.font, cell.border = HDR_FILL, HDR_FONT, BORDER
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[L(i)].width = w
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def put(ws, r, c, v, wrap=False, fill=None, font=None, link=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.border = BORDER
    if wrap:
        cell.alignment = WRAP
    if fill:
        cell.fill = fill
    if font:
        cell.font = font
    if link:
        cell.hyperlink = link
        cell.font = LINK_FONT
    return cell


def build(data, out, pages_dir=None, sample=0.10, author="Claude (floc-itt-analyser)"):
    meta, src_list, flocs = data["meta"], data["sources"], data["flocs"]
    results, spot, d = run_checks(data, pages_dir, sample)
    src, fmap, children, ranges = d["src"], d["flocs"], d["children"], d["ranges"]
    pdf = meta["pdf_file"]
    lvl_fill = {int(k): PatternFill("solid", fgColor=v) for k, v in meta["level_colours"].items()}
    lvl_font = {int(k): Font(color="FFFFFF" if v else "000000", bold=int(k) <= 2)
                for k, v in meta["level_font_white"].items()}
    # source -> flocs (links + mapping)
    src_floc = {}
    for fid, sid, _ in d["links"]:
        src_floc.setdefault(sid, set()).add(fid)
    for s in src_list:
        if s.get("mapped_floc"):
            src_floc.setdefault(s["source_id"], set()).add(s["mapped_floc"])

    def printed_range(fid):
        r = ranges.get(fid)
        if not r:
            return ""
        part = lambda pg: next((q["name"] for q in meta["parts"] if q["pdf_from"] <= pg <= q["pdf_to"]), None)
        if part(r[0]) != part(r[1]):
            return "spans several parts (see PDF range)"
        ps = []
        for pg in r:
            lab = next((s["printed_page"] for s in src_list if s["pdf_page"] == pg and s.get("printed_page")), None)
            ps.append(lab or "n/a")
        return ps[0] if ps[0] == ps[1] else f"{ps[0]}-{ps[1]}"

    wb = Workbook()

    # ---------------- README ----------------
    ws = wb.active
    ws.title = "README"
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 120
    rows = [
        ("Purpose", "Functional Location (FLOC) hierarchy for cost allocation and cost modelling, with page-level traceability to the source tender pack. Aligned to WBS / FLOC / CBS / PBS practice: the FLOC tree is a physical/scope breakdown (PBS-style) that cost elements (CBS) are applied to."),
        ("Project", meta["project"]),
        ("Source document", f"{meta['document_title']} (tender no. {meta['document_id']})"),
        ("Source file", pdf),
        ("PDF page count", meta["pdf_page_count"]),
        ("Workbook version", meta["workbook_version"]),
        ("Date", date.today().strftime("%d/%m/%Y")),
        ("Prepared by", author),
        ("Currency", f"All amounts are in {meta['currency']} unless the document states otherwise. The cost model is deliberately blank: no quantities or rates are stated in the tender pack's schedules."),
        ("Page-numbering convention", "PDF page = the physical page in the PDF file (1 to %d); this is the authoritative reference and the one used for hyperlinks. Printed page = the page number printed on the page, which restarts in every embedded document, so the PDF-to-printed offset differs by part (table below). Every page column is labelled PDF or Printed." % meta["pdf_page_count"]),
        ("FLOC numbering convention", meta["numbering"]["note"] + "  Format: " + meta["numbering"]["format"]),
        ("Hierarchy levels", "; ".join(f"L{k} {v}" for k, v in meta["levels"].items())),
        ("Colour coding", "Row colour = hierarchy level (see FLOC_Hierarchy). Red = FLOC with no source reference. Amber = Assumption / REVIEW. Green = PASS."),
        ("Traceability", "Every FLOC carries a Primary Source ID (where the area or scope is defined) and Supporting Source IDs (where it is mentioned, priced or excluded). Each Source ID is one row in Source_Register with section, PDF page, printed page, a short evidence note (paraphrase or quote of 15 words or fewer) and confidence (High = explicit named area/scope; Medium = inferred; Low = assumed)."),
        ("Page range", "A parent's page range is the min-max PDF page across its own and all descendant references (parents inherit their children's pages)."),
        ("Hyperlinks", meta["link_note"]),
        ("Assumptions", "1) The contract is construction-only; engineering, procurement and fabrication sit with an Offshore EPF Contractor (SoW s2.6). 2) Referenced documents not contained in the PDF (Pricing Schedule template, drawing sets, MTOs) are recorded as gaps, not assumed. 3) FLOC boundaries follow the Scope of Work Separable Parts and facility list; where the pack gives no boundary the node is flagged. 4) Level 5 nodes are created only where the pack names discrete equipment or cost objects."),
        ("Limitations", "Extraction was a page-by-page text pass; scanned images, drawings and figures were not interpreted. Nodes and cost allocation drivers marked Assumption are proposals for Cost Control review, not statements by the Company."),
    ]
    ws["A1"] = "FLOC and Cost Allocation Workbook"
    ws["A1"].font = Font(bold=True, size=14)
    for i, (k, v) in enumerate(rows, 3):
        put(ws, i, 1, k, font=Font(bold=True))
        put(ws, i, 2, v, wrap=True)
    r0 = len(rows) + 5
    ws.cell(row=r0 - 1, column=1, value="PDF-to-printed page offset by part").font = Font(bold=True)
    for j, h in enumerate(("Part", "PDF pages / offset (PDF minus printed) / note"), 1):
        c = ws.cell(row=r0, column=j, value=h)
        c.fill, c.font = HDR_FILL, HDR_FONT
    for i, p in enumerate(meta["parts"], r0 + 1):
        put(ws, i, 1, p["name"])
        put(ws, i, 2, f"PDF {p['pdf_from']}-{p['pdf_to']}; offset {p['offset'] if p['offset'] is not None else 'none (unnumbered)'}"
            + (f"; {p['note']}" if p.get("note") else ""), wrap=True)
    r1 = r0 + len(meta["parts"]) + 3
    ws.cell(row=r1, column=1, value="Sheet index").font = Font(bold=True)
    for i, (n, t) in enumerate([
        ("FLOC_Hierarchy", "Coded structure with level indent, sources, page range, confidence, link"),
        ("Source_Register", "One row per Source ID"),
        ("FLOC_to_Source_Map", "Long-form FLOC-to-Source links (Primary / Supporting)"),
        ("Scope_Extraction", "Extracted scope, interface, exclusion, pricing and allocation items with FLOC mapping"),
        ("FLOC_to_Pricing_Map", "Pricing schedule lines with page numbers; FLOC x pricing matrix below"),
        ("Allocation_Rules", "Shared and indirect cost drivers with sources"),
        ("Cost_Model_Template", "Blank, formula-ready cost model with roll-up by hierarchy level"),
        ("Gaps_and_RFIs", "Ambiguities, missing information, assumptions, clarification questions"),
        ("Validation", "Checklist results and spot-check sample")], r1 + 1):
        put(ws, i, 1, n, font=Font(bold=True))
        put(ws, i, 2, t)

    # ---------------- FLOC_Hierarchy ----------------
    ws = wb.create_sheet("FLOC_Hierarchy")
    cols = ["FLOC ID", "Level", "Description", "Parent ID", "Discipline(s)", "Contractor / package responsibility",
            "Scope status", "Primary Source ID", "Supporting Source IDs", "Primary PDF page", "Primary printed page",
            "Section", "Page range (PDF)", "Page range (printed)", "Confidence", "Link (PDF page)", "Notes"]
    header(ws, 1, cols, [20, 7, 52, 18, 24, 34, 12, 13, 32, 10, 10, 30, 14, 14, 11, 12, 40])
    r = 2
    order = []

    def emit(fid):
        order.append(fid)
        for c in children.get(fid, []):
            emit(c)
    for root in children.get(None, []):
        emit(root)
    for fid in order:
        f = fmap[fid]
        lv = f["level"]
        ps = src.get(f["primary_source"]) if f["primary_source"] else None
        nosrc = ps is None
        fill = RED if nosrc and not f["assumption"] else lvl_fill[lv]
        sup = f["supporting_sources"]
        sup_txt = ", ".join(sup[:6]) + (f" (+{len(sup) - 6} more)" if len(sup) > 6 else "")
        rr = ranges.get(fid)
        vals = [fid, lv, f["description"], f["parent_id"] or "", ", ".join(f["disciplines"]), f["responsibility"],
                f["scope_status"], ps["source_id"] if ps else "No source - Assumption" if f["assumption"] else "",
                sup_txt, ps["pdf_page"] if ps else None, ps["printed_page"] if ps else None,
                ps["section"] if ps else None, f"{rr[0]}-{rr[1]}" if rr else "", printed_range(fid),
                ps["confidence"] if ps else "Low", None, f["notes"]]
        for c, v in enumerate(vals, 1):
            cell = put(ws, r, c, v, wrap=c in (3, 6, 9, 12, 17), fill=fill, font=lvl_font[lv] if c in (1, 3) else None)
            if c == 3:
                cell.alignment = Alignment(indent=lv - 1, wrap_text=True, vertical="top")
        if ps:
            put(ws, r, 16, f"p.{ps['pdf_page']}", fill=fill, link=pdf_url(pdf, ps["pdf_page"]))
        else:
            put(ws, r, 16, "", fill=fill)
        ws.row_dimensions[r].outlineLevel = max(0, lv - 1)
        r += 1
    ws.auto_filter.ref = f"A1:{L(len(cols))}{r - 1}"
    dv = DataValidation(type="list", formula1='"In scope,Excluded,Provisional"', allow_blank=False)
    dv.add(f"G2:G{r + 200}")
    ws.add_data_validation(dv)
    dv2 = DataValidation(type="list", formula1='"High,Medium,Low"', allow_blank=False)
    dv2.add(f"O2:O{r + 200}")
    ws.add_data_validation(dv2)
    ws.freeze_panes = "D2"
    hier_last = r - 1

    # ---------------- Source_Register ----------------
    ws = wb.create_sheet("Source_Register")
    cols = ["Source ID", "Document", "Part", "Section", "PDF page", "Printed page", "Printed page basis",
            "Figure / Table / Schedule", "Item type", "Title", "Evidence note", "Confidence", "Linked FLOC IDs",
            "Mapped FLOC (exactly one)", "Mapping basis", "Link (PDF page)"]
    header(ws, 1, cols, [11, 16, 28, 34, 9, 9, 10, 20, 17, 44, 60, 10, 28, 20, 10, 10])
    for i, s in enumerate(src_list, 2):
        vals = [s["source_id"], s["document"], s["part"], s["section"], s["pdf_page"], s["printed_page"],
                s["printed_page_basis"], s["figure_table"], s["item_type"], s["title"], s["evidence"], s["confidence"],
                ", ".join(sorted(src_floc.get(s["source_id"], []))), s.get("mapped_floc") or "", s.get("mapped_by"), None]
        for c, v in enumerate(vals, 1):
            put(ws, i, c, v, wrap=c in (4, 10, 11, 13))
        put(ws, i, 16, f"p.{s['pdf_page']}", link=pdf_url(pdf, s["pdf_page"]))
    ws.auto_filter.ref = f"A1:{L(len(cols))}{len(src_list) + 1}"
    ws.freeze_panes = "B2"

    # ---------------- FLOC_to_Source_Map ----------------
    ws = wb.create_sheet("FLOC_to_Source_Map")
    cols = ["FLOC ID", "FLOC description", "Level", "Source ID", "PDF page", "Printed page", "Primary / Supporting",
            "Confidence", "Section", "Item type", "Evidence note"]
    header(ws, 1, cols, [20, 44, 7, 11, 9, 9, 12, 11, 30, 16, 60])
    r = 2
    for fid in order:
        mine = [(sid, role) for f2, sid, role in d["links"] if f2 == fid]
        mine.sort(key=lambda t: (0 if t[1] == "Primary" else 1, src[t[0]]["pdf_page"] if t[0] in src else 0))
        for sid, role in mine:
            s = src.get(sid)
            if not s:
                continue
            vals = [fid, fmap[fid]["description"], fmap[fid]["level"], sid, s["pdf_page"], s["printed_page"], role,
                    s["confidence"], s["section"], s["item_type"], s["evidence"]]
            for c, v in enumerate(vals, 1):
                put(ws, r, c, v, wrap=c in (2, 9, 11), fill=lvl_fill[fmap[fid]["level"]] if c == 1 else None)
            r += 1
        if fmap[fid]["assumption"] and not fmap[fid]["primary_source"]:
            for c, v in enumerate([fid, fmap[fid]["description"], fmap[fid]["level"], "No source - Assumption", None, None,
                                   "Primary", "Low", None, None, "Not stated in the document"], 1):
                put(ws, r, c, v, fill=AMBER)
            r += 1
    ws.auto_filter.ref = f"A1:{L(len(cols))}{max(r - 1, 2)}"
    ws.freeze_panes = "C2"

    # ---------------- Scope_Extraction ----------------
    ws = wb.create_sheet("Scope_Extraction")
    cols = ["Source ID", "Item type", "Title", "Section", "Figure / Table / Schedule", "PDF page", "Printed page",
            "Evidence note", "Suggested area", "Package", "Discipline(s)", "Mapped FLOC ID", "Mapped FLOC description",
            "Confidence", "Link"]
    header(ws, 1, cols, [11, 17, 44, 32, 18, 9, 9, 60, 26, 10, 22, 20, 36, 10, 10])
    rows_ = sorted((s for s in src_list if s["item_type"] in SCOPE_TYPES_OUT),
                   key=lambda s: (s["item_type"], s["pdf_page"], s["source_id"]))
    for i, s in enumerate(rows_, 2):
        mf = s.get("mapped_floc")
        vals = [s["source_id"], s["item_type"], s["title"], s["section"], s["figure_table"], s["pdf_page"],
                s["printed_page"], s["evidence"], s["suggested_area"], s["suggested_package"],
                ", ".join(s["disciplines"]), mf or "UNMAPPED", fmap[mf]["description"] if mf in fmap else "",
                s["confidence"], None]
        for c, v in enumerate(vals, 1):
            put(ws, i, c, v, wrap=c in (3, 4, 8, 13),
                fill=RED if (c == 12 and not mf and s["item_type"] in ("Scope", "Area/Facility", "Work Package", "Exclusion", "Provisional Sum")) else None)
        put(ws, i, 15, f"p.{s['pdf_page']}", link=pdf_url(pdf, s["pdf_page"]))
    ws.auto_filter.ref = f"A1:{L(len(cols))}{len(rows_) + 1}"
    ws.freeze_panes = "C2"

    # ---------------- FLOC_to_Pricing_Map ----------------
    ws = wb.create_sheet("FLOC_to_Pricing_Map")
    cols = ["Pricing ID", "Schedule", "Item no.", "Description", "Unit", "Pricing basis", "PDF page", "Printed page",
            "Source ID", "Mapped FLOC IDs", "Notes", "Link (PDF page)"]
    header(ws, 1, cols, [10, 16, 10, 52, 10, 20, 9, 9, 11, 40, 40, 10])
    for i, p in enumerate(data["pricing"], 2):
        s = src.get(p["source_id"]) if p["source_id"] else None
        vals = [p["pricing_id"], p["schedule"], p["item_no"], p["description"], p["unit"], p["basis"], p["pdf_page"],
                s["printed_page"] if s else None, p["source_id"], ", ".join(p["floc_ids"]), p["notes"], None]
        for c, v in enumerate(vals, 1):
            put(ws, i, c, v, wrap=c in (4, 10, 11))
        put(ws, i, 12, f"p.{p['pdf_page']}", link=pdf_url(pdf, p["pdf_page"]))
    last = len(data["pricing"]) + 1
    ws.auto_filter.ref = f"A1:{L(len(cols))}{max(last, 2)}"
    # matrix
    m0 = last + 4
    ws.cell(row=m0 - 1, column=1, value="Matrix: FLOC (levels 2-4) x pricing line. Circle = pricing line is mapped to that FLOC (or an ancestor of it is in the mapped list). Pricing schedule PDF page shown under each column.").font = Font(bold=True)
    mcols = ["FLOC ID", "Description", "Level"] + [p["pricing_id"] for p in data["pricing"]]
    for c, h in enumerate(mcols, 1):
        cell = ws.cell(row=m0, column=c, value=h)
        cell.fill, cell.font, cell.border = HDR_FILL, HDR_FONT, BORDER
    for c, p in enumerate(data["pricing"], 4):
        put(ws, m0 + 1, c, f"Sch {p['schedule']} {p['item_no'] or ''} p.{p['pdf_page']}", wrap=True)
    put(ws, m0 + 1, 1, "Schedule / item / PDF page")
    rr = m0 + 2
    for fid in order:
        f = fmap[fid]
        if f["level"] not in (2, 3, 4):
            continue
        put(ws, rr, 1, fid, fill=lvl_fill[f["level"]], font=lvl_font[f["level"]])
        put(ws, rr, 2, f["description"])
        put(ws, rr, 3, f["level"])
        anc = set(d["ancestors"](fid))
        for c, p in enumerate(data["pricing"], 4):
            hit = fid in p["floc_ids"]
            put(ws, rr, c, "●" if hit else None, fill=GREEN if hit else None)
        rr += 1
    ws.row_dimensions[m0 + 1].height = 45
    ws.freeze_panes = "A2"

    # ---------------- Allocation_Rules ----------------
    ws = wb.create_sheet("Allocation_Rules")
    cols = ["Rule ID", "Cost pool", "Rule / treatment", "Allocation driver", "Applies to", "Basis (Stated / Assumption)",
            "Source IDs", "PDF pages", "Notes"]
    header(ws, 1, cols, [9, 26, 60, 34, 30, 16, 22, 14, 44])
    for i, a in enumerate(data["allocation_rules"], 2):
        pgs = sorted({src[x]["pdf_page"] for x in a["source_ids"] if x in src})
        vals = [a["rule_id"], a["cost_pool"], a["description"], a["driver"], a["applies_to"], a["basis"],
                ", ".join(a["source_ids"]) or "Assumption", ", ".join(map(str, pgs)), a["notes"]]
        for c, v in enumerate(vals, 1):
            put(ws, i, c, v, wrap=True, fill=AMBER if (c == 6 and str(v).lower().startswith("assum")) else None)
    ws.auto_filter.ref = f"A1:{L(len(cols))}{len(data['allocation_rules']) + 1}"
    dv3 = DataValidation(type="list", formula1='"Stated,Assumption,Stated + assumption"', allow_blank=True)
    dv3.add(f"F2:F{len(data['allocation_rules']) + 100}")
    ws.add_data_validation(dv3)

    # ---------------- Cost_Model_Template ----------------
    ws = wb.create_sheet("Cost_Model_Template")
    cols = ["FLOC ID", "Description", "Level", "Ancestor path (helper)", "Cost element", "Unit", "Quantity", "Rate (AUD)",
            "Amount (AUD)", "Currency", "Estimate basis", "Contingency %", "Contingency amount", "Escalation %",
            "Escalation amount", "Total (AUD)", "Source ID", "PDF page", "Pricing line", "Notes"]
    header(ws, 1, cols, [20, 44, 6, 14, 16, 8, 11, 11, 14, 9, 22, 11, 14, 11, 14, 14, 11, 9, 10, 36])
    elements = ["Labour", "Materials", "Equipment", "Subcontract", "Indirects (allocated)"]
    leaves = [fid for fid in order if not children.get(fid) and fmap[fid]["scope_status"] != "Excluded"]
    price_by_floc = {}
    for p in data["pricing"]:
        for fid in p["floc_ids"]:
            price_by_floc.setdefault(fid, []).append(p["pricing_id"])
    r = 2
    for fid in leaves:
        f = fmap[fid]
        ps = src.get(f["primary_source"]) if f["primary_source"] else None
        path = "|" + "|".join(d["ancestors"](fid)) + "|"
        for el in elements:
            vals = [fid, f["description"], f["level"], path, el, None, None, None,
                    f'=IF(AND(ISNUMBER(G{r}),ISNUMBER(H{r})),G{r}*H{r},0)', meta["currency"], None, None,
                    f"=I{r}*N(L{r})", None, f"=(I{r}+M{r})*N(N{r})", f"=I{r}+M{r}+O{r}",
                    ps["source_id"] if ps else None, ps["pdf_page"] if ps else None,
                    ", ".join(price_by_floc.get(fid, [])) or None, None]
            for c, v in enumerate(vals, 1):
                cell = put(ws, r, c, v, fill=lvl_fill[f["level"]] if c == 1 else None)
                if c in (9, 13, 15, 16, 8):
                    cell.number_format = '#,##0.00'
                if c in (12, 14):
                    cell.number_format = '0.0%'
            r += 1
    last = r - 1
    ws.auto_filter.ref = f"A1:T{max(last, 2)}"
    ws.column_dimensions["D"].hidden = True
    dv4 = DataValidation(type="list", formula1='"Labour,Materials,Equipment,Subcontract,Indirects (allocated)"', allow_blank=True)
    dv4.add(f"E2:E{last + 200}")
    ws.add_data_validation(dv4)
    # roll-up block
    c0 = 22  # column V
    heads = ["FLOC ID", "Description", "Level", "Amount (AUD)", "Contingency", "Escalation", "Total (AUD)"]
    ws.cell(row=1, column=c0 - 0, value=None)
    for j, h in enumerate(heads):
        cell = ws.cell(row=1, column=c0 + j, value=h)
        cell.fill, cell.font, cell.border = HDR_FILL, HDR_FONT, BORDER
        ws.column_dimensions[L(c0 + j)].width = [20, 44, 6, 15, 14, 14, 15][j]
    rr = 2
    for fid in order:
        f = fmap[fid]
        put(ws, rr, c0, fid, fill=lvl_fill[f["level"]], font=lvl_font[f["level"]])
        put(ws, rr, c0 + 1, f["description"])
        put(ws, rr, c0 + 2, f["level"])
        crit = f'"*|"&{L(c0)}{rr}&"|*"'
        for j, col in enumerate(("I", "M", "O", "P")):
            cell = put(ws, rr, c0 + 3 + j, f"=SUMIF($D$2:$D${max(last, 2)},{crit},${col}$2:${col}${max(last, 2)})")
            cell.number_format = '#,##0.00'
        rr += 1
    rr += 1
    put(ws, rr, c0, "Total by level", font=Font(bold=True))
    for lv in range(1, 6):
        rr += 1
        put(ws, rr, c0, f"Level {lv}", fill=lvl_fill[lv], font=lvl_font[lv])
        put(ws, rr, c0 + 1, meta["levels"][str(lv)])
        put(ws, rr, c0 + 2, lv)
        for j in range(4):
            cell = put(ws, rr, c0 + 3 + j, f"=SUMIF(${L(c0 + 2)}$2:${L(c0 + 2)}${len(order) + 1},{lv},{L(c0 + 3 + j)}$2:{L(c0 + 3 + j)}${len(order) + 1})")
            cell.number_format = '#,##0.00'
    ws.cell(row=rr + 2, column=c0, value="Roll-up note: the level totals are the sum of each level's roll-up and so equal the project total only at level 1. Amounts are entered at leaf FLOCs only; fill Quantity and Rate (or overwrite Amount for lump sums). Excluded FLOCs carry no rows.").alignment = WRAP
    ws.freeze_panes = "F2"

    # ---------------- Gaps_and_RFIs ----------------
    ws = wb.create_sheet("Gaps_and_RFIs")
    cols = ["ID", "Origin", "Type", "Topic", "Question / gap", "Impact on cost allocation", "Priority", "Source ID",
            "PDF page", "Printed page", "Linked FLOC IDs", "Status", "Link"]
    header(ws, 1, cols, [10, 18, 18, 30, 70, 44, 9, 11, 9, 9, 28, 10, 10])
    r = 2
    for q in data["rfis"]:
        s = src.get(q["source_id"]) if q["source_id"] else None
        vals = [q["rfi_id"], "Authored RFI", q["type"], q["topic"], q["question"], q["impact"], q["priority"],
                q["source_id"], q["pdf_page"], s["printed_page"] if s else None, ", ".join(q["floc_ids"]), "Open", None]
        for c, v in enumerate(vals, 1):
            put(ws, r, c, v, wrap=c in (4, 5, 6, 11))
        put(ws, r, 13, f"p.{q['pdf_page']}", link=pdf_url(pdf, q["pdf_page"]))
        r += 1
    g = 0
    for s in src_list:
        if s["item_type"] in ("Referenced Not Included", "Ambiguity/Risk"):
            g += 1
            typ = "Missing document / schedule" if s["item_type"] == "Referenced Not Included" else "Ambiguity / risk"
            vals = [f"GAP-{g:03d}", "Auto - extraction", typ, s["title"], s["evidence"], s["notes"], "Medium", s["source_id"],
                    s["pdf_page"], s["printed_page"], s.get("mapped_floc") or "", "Open", None]
            for c, v in enumerate(vals, 1):
                put(ws, r, c, v, wrap=c in (4, 5, 6))
            put(ws, r, 13, f"p.{s['pdf_page']}", link=pdf_url(pdf, s["pdf_page"]))
            r += 1
    for f in data["flocs"]:
        if not f["primary_source"] and f["assumption"]:
            g += 1
            vals = [f"GAP-{g:03d}", "Auto - FLOC", "No source - Assumption", f["description"],
                    "FLOC has no source reference in the pack; confirm the boundary with the Company.", f["notes"],
                    "High", "", None, None, f["floc_id"], "Open", None]
            for c, v in enumerate(vals, 1):
                put(ws, r, c, v, wrap=c in (4, 5, 6), fill=AMBER)
            r += 1
    ws.auto_filter.ref = f"A1:{L(len(cols))}{max(r - 1, 2)}"
    dv5 = DataValidation(type="list", formula1='"Open,Raised,Answered,Closed"', allow_blank=True)
    dv5.add(f"L2:L{r + 200}")
    ws.add_data_validation(dv5)
    dv6 = DataValidation(type="list", formula1='"High,Medium,Low"', allow_blank=True)
    dv6.add(f"G2:G{r + 200}")
    ws.add_data_validation(dv6)

    # ---------------- Validation ----------------
    ws = wb.create_sheet("Validation")
    header(ws, 1, ["#", "Check", "Result", "Count", "Detail"], [5, 90, 10, 9, 90])
    for i, x in enumerate(results, 2):
        fill = {"PASS": GREEN, "FAIL": RED, "WARN": AMBER}.get(x["status"])
        for c, v in enumerate([i - 1, x["check"], x["status"], x["count"], x["detail"]], 1):
            put(ws, i, c, v, wrap=c in (2, 5), fill=fill if c == 3 else None)
    r = len(results) + 4
    ws.cell(row=r - 1, column=2, value="Live checks (recalculate in Excel)").font = Font(bold=True)
    live = [("FLOCs with blank Primary Source ID (live)", f'=COUNTBLANK(FLOC_Hierarchy!H2:H{hier_last})'),
            ("Duplicate FLOC IDs (live)", f'=SUMPRODUCT((COUNTIF(FLOC_Hierarchy!A2:A{hier_last},FLOC_Hierarchy!A2:A{hier_last})>1)*1)'),
            ("FLOCs with Primary page outside 1-%d (live)" % meta["pdf_page_count"],
             f'=COUNTIF(FLOC_Hierarchy!J2:J{hier_last},">{meta["pdf_page_count"]}")+COUNTIF(FLOC_Hierarchy!J2:J{hier_last},"<1")'),
            ("Source IDs in register (live)", f'=COUNTA(Source_Register!A2:A{len(src_list) + 1})')]
    for k, (name, fml) in enumerate(live):
        put(ws, r + k, 2, name)
        put(ws, r + k, 4, fml)
    r += len(live) + 2
    ws.cell(row=r, column=2, value="Spot-check sample (links re-read against the extracted page text; REVIEW rows need a human read of the PDF)").font = Font(bold=True)
    r += 1
    for c, h in enumerate(["FLOC ID", "Source ID", "Role", "PDF page", "Method / score / result / evidence"], 1):
        cell = ws.cell(row=r, column=c if c > 1 else 1, value=h)
    for j, h in enumerate(["FLOC ID", "Source ID", "Role", "PDF page", "Method | score | result | evidence"]):
        cell = ws.cell(row=r, column=1 + j, value=h)
        cell.fill, cell.font = HDR_FILL, HDR_FONT
    for k, sp in enumerate(spot, r + 1):
        put(ws, k, 1, sp["floc_id"])
        put(ws, k, 2, sp["source_id"])
        put(ws, k, 3, sp["role"])
        put(ws, k, 4, sp["pdf_page"])
        put(ws, k, 5, f"{sp['method']} | {sp['score']} | {sp['result']} | {sp['evidence']}", wrap=True,
            fill=GREEN if sp["result"] == "PASS" else AMBER)
    ws.freeze_panes = "A2"

    wb.save(out)
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("out")
    ap.add_argument("--pages-dir")
    ap.add_argument("--sample", type=float, default=0.10)
    ap.add_argument("--author", default="Claude (floc-itt-analyser)")
    a = ap.parse_args()
    res = build(json.load(open(a.data, encoding="utf-8")), a.out, a.pages_dir, a.sample, a.author)
    for x in res:
        print(f"[{x['status']:4}] {x['check']}: {x['count']}")
    print("wrote", a.out)
