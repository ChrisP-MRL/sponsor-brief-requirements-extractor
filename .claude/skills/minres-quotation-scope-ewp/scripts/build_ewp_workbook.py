"""Build the MinRes quotation scope and EWP workbook from a FLOC workbook plus a JSON config.

Usage (run in isolated mode):
  python -I build_ewp_workbook.py --input <floc.xlsx> --config <config.json> --output <out.xlsx>
         [--carry-forward] [--force]

Does not alter the input workbook. Holds no costs.
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime

import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

DECISIONS = ["Price", "Price as Provisional Sum", "Price as Option or Alternative", "Exclude", "Clarify"]
STATUSES = ["Not started", "In progress", "In review", "Complete"]
RISKS = ["High", "Medium", "Low"]
DELIVERY = ["Self-perform", "Subcontract", "Supply-only"]
METHODS = ["Quantity-based", "Rate-based", "Vendor quote", "Allowance", "Historical benchmark"]
INPUT_STATUS = ["Not requested", "Requested", "Received", "In ITT pack", "Not available in ITT"]
RFI_STATUS = ["Open", "Draft", "Raised", "Answered", "Closed"]
MILESTONE_STATUS = ["Not started", "In progress", "Complete"]

HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
COLOURS = {
    "Price": "C6EFCE", "Price as Provisional Sum": "FFEB9C", "Price as Option or Alternative": "BDD7EE",
    "Exclude": "D9D9D9", "Clarify": "F8CBAD", "High": "FFC7CE", "Medium": "FFEB9C", "Low": "C6EFCE",
    "Complete": "C6EFCE", "In review": "BDD7EE", "In progress": "FFEB9C",
}
BUF = 400  # formula range depth for the long sheets


def fill(hex_):
    return PatternFill("solid", fgColor=hex_)


def write_table(ws, headers, rows, widths, input_cols=(), wrap_cols=()):
    ws.append(headers)
    for c in ws[1]:
        c.fill, c.font, c.border = HDR_FILL, HDR_FONT, BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append(r)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for c in row:
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=(c.column in wrap_cols))
            if c.column in input_cols:
                c.fill = INPUT_FILL
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{max(ws.max_row, 2)}"


def add_dv(ws, formula, col, first=2, last=BUF):
    dv = DataValidation(type="list", formula1=formula, allow_blank=True, showErrorMessage=True)
    ws.add_data_validation(dv)
    dv.add(f"{col}{first}:{col}{last}")


def colour_cf(ws, rng, names):
    for n in names:
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{n}"'], fill=fill(COLOURS[n])))


def parse_pages(vals):
    """Compress a set of page numbers to '220, 223-225'."""
    ps = sorted({int(v) for v in vals if str(v).strip().isdigit()})
    out, i = [], 0
    while i < len(ps):
        j = i
        while j + 1 < len(ps) and ps[j + 1] == ps[j] + 1:
            j += 1
        out.append(str(ps[i]) if i == j else f"{ps[i]}-{ps[j]}")
        i = j + 1
    return ", ".join(out)


def matches(floc, pat):
    return floc == pat or floc.startswith(pat + "-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--carry-forward", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))

    prior = None
    if os.path.exists(a.output):
        if not (a.force or a.carry_forward):
            sys.exit(f"{a.output} exists. Use --carry-forward to keep entered names, dates, hours and statuses, or --force to overwrite.")
        if a.carry_forward:
            prior = openpyxl.load_workbook(a.output)

    src = openpyxl.load_workbook(a.input, read_only=True, data_only=True)
    hier = [r for r in list(src["FLOC_Hierarchy"].iter_rows(values_only=True))[1:] if r[0]]
    gaps = [r for r in list(src["Gaps_and_RFIs"].iter_rows(values_only=True))[1:] if r[0]]
    n_floc = len(hier)
    parents = {r[3] for r in hier}
    byid = {r[0]: r for r in hier}
    leaves = [r[0] for r in hier if r[0] not in parents]
    itt_counts = defaultdict(int)
    for r in hier:
        itt_counts[r[6]] += 1

    # ---------------- RFIs ----------------
    rfis = []
    for g in gaps:
        origin = "Carried forward - authored" if g[1] == "Authored RFI" else "Carried forward - auto-extracted"
        rfis.append(dict(id=g[0], origin=origin, type=g[2], topic=g[3], question=g[4], priority=g[6],
                         sid=g[7], page=g[8], flocs=g[10] or "", impact=g[5], status=g[11] or "Open",
                         owner=cfg["rfi_owner_defaults"][origin]))
    for n in cfg["new_rfis"]:
        rfis.append(dict(id=n["id"], origin="New - bid specific", type=n["type"], topic=n["topic"], question=n["question"],
                         priority=n["priority"], sid=n["source_id"], page=n["pdf_page"], flocs=n["floc_ids"], impact=n["impact"],
                         status="Draft", owner=cfg["rfi_owner_defaults"]["New - bid specific"]))
    rfi_by_id = {r["id"]: r for r in rfis}
    linked_rfis = defaultdict(set)  # FLOC -> authored/new RFIs (direct + inherited by descendants)
    for r in rfis:
        if r["origin"] == "Carried forward - auto-extracted":
            continue
        for f in [x.strip() for x in r["flocs"].split(",") if x.strip()]:
            for fid in byid:
                if matches(fid, f):
                    linked_rfis[fid].add(r["id"])
    for f, ids in cfg.get("extra_rfi_links", {}).items():
        linked_rfis[f].update(ids)
    for f, o in cfg["decision_overrides"].items():
        linked_rfis[f].update(o.get("rfis", []))

    # ---------------- EWP assignment ----------------
    dr = cfg["decision_rules"]
    leaf_decision = {}
    leaf_reason = {}
    for fid in leaves:
        r = byid[fid]
        status, sid, page = r[6], r[7], r[9]
        if fid in cfg["decision_overrides"]:
            o = cfg["decision_overrides"][fid]
            leaf_decision[fid], leaf_reason[fid] = o["decision"], o["reason"]
        elif not sid or not page:
            leaf_decision[fid], leaf_reason[fid] = dr["no_source"], "No Source ID or PDF page in the input workbook."
        elif status == "In scope":
            leaf_decision[fid], leaf_reason[fid] = dr["In scope"], ""
        elif status == "Excluded":
            leaf_decision[fid], leaf_reason[fid] = dr["Excluded"], ""
        else:
            leaf_decision[fid], leaf_reason[fid] = dr["Provisional_default"], ""

    ewp_of, ewp_basis = {}, {}
    problems = []
    for e in cfg["ewps"]:
        for pat in e["flocs"]:
            hit = [l for l in leaves if matches(l, pat) and leaf_decision[l] != "Exclude"]
            if not hit:
                problems.append(f"{e['id']}: pattern {pat} matches no priceable leaf FLOC")
            for l in hit:
                if l in ewp_of:
                    problems.append(f"{l} assigned to both {ewp_of[l]} and {e['id']}")
                ewp_of[l], ewp_basis[l] = e["id"], f"Rule: {pat}"
    for l in leaves:
        if leaf_decision[l] != "Exclude" and l not in ewp_of:
            problems.append(f"{l} ({leaf_decision[l]}) has no EWP")
    if problems:
        sys.exit("EWP configuration errors:\n  " + "\n  ".join(problems))
    ewp = {e["id"]: e for e in cfg["ewps"]}
    ewp_flocs = defaultdict(list)
    for l in leaves:
        if l in ewp_of:
            ewp_flocs[ewp_of[l]].append(l)

    def delivery_of(e):
        return e.get("delivery") or cfg.get("delivery_by_ewp", {}).get(e["id"]) or cfg["delivery_by_discipline"][e["disc"]]

    # parent decisions (roll-up)
    desc_of = lambda pid: [l for l in leaves if matches(l, pid) and l != pid]
    decision = dict(leaf_decision)
    reason = dict(leaf_reason)
    for r in hier:
        fid = r[0]
        if fid in decision:
            continue
        ds = {leaf_decision[l] for l in desc_of(fid)}
        if ds == {"Exclude"}:
            decision[fid], reason[fid] = "Exclude", "Roll-up: every child FLOC is excluded."
        else:
            decision[fid], reason[fid] = "Price", ""
    expected = dr["expected_by_itt_status"]

    # risk
    def risk_of(fid):
        d = decision[fid]
        if d == "Exclude":
            return "Low" if not linked_rfis[fid] else "Medium"
        pr = [rfi_by_id[i]["priority"] for i in linked_rfis[fid] if i in rfi_by_id]
        if d in dr["high_risk_decisions"] or "High" in pr:
            return "High"
        return dr["default_risk"]

    def interface_of(resp):
        s = (resp or "").strip()
        if s.startswith("Contractor") and "Company" not in s:
            return "Contractor"
        if s.startswith("Others") or s.startswith("IPP Contractor"):
            return "Other contractor"
        if s.startswith("Company") or s.startswith("Owner"):
            return "Owner (Company)"
        return "Contractor and Owner (Company) interface"

    # ---------------- workbook ----------------
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    sheets = {n: wb.create_sheet(n) for n in ["README", "Dashboard", "Scope_Decision", "EWP_Register", "FLOC_to_EWP_Map",
                                              "Inputs_Tracker", "Team", "Bid_Programme", "RFI_Log", "Validation", "Lists"]}

    # Lists
    ls = sheets["Lists"]
    cols = [("Scope Decision", DECISIONS), ("Status", STATUSES), ("Risk", RISKS), ("Delivery method", DELIVERY),
            ("Estimate method", METHODS), ("Input status", INPUT_STATUS), ("RFI status", RFI_STATUS), ("Milestone status", MILESTONE_STATUS)]
    for i, (h, vals) in enumerate(cols, 1):
        ls.cell(1, i, h).font = Font(bold=True)
        for j, v in enumerate(vals, 2):
            ls.cell(j, i, v)
        ls.column_dimensions[get_column_letter(i)].width = 30
    ls.cell(1, 10, "ITT scope status").font = Font(bold=True)
    ls.cell(1, 11, "Expected decision 1").font = Font(bold=True)
    ls.cell(1, 12, "Expected decision 2").font = Font(bold=True)
    for j, (k, v) in enumerate(expected.items(), 2):
        ls.cell(j, 10, k), ls.cell(j, 11, v[0]), ls.cell(j, 12, v[1])
    for c in "JKL":
        ls.column_dimensions[c].width = 30
    L = lambda col, n: f"=Lists!${col}$2:${col}${n + 1}"

    # Team
    roles = [r["role"] for r in cfg["roles"]]
    nR = len(roles)
    tm = sheets["Team"]
    prev_team = {}
    if prior and "Team" in prior.sheetnames:
        for row in prior["Team"].iter_rows(min_row=2, values_only=True):
            if row[0]:
                prev_team[row[0]] = (row[1], row[2])
    rows = []
    for i, r in enumerate(cfg["roles"], 2):
        nm, cap = prev_team.get(r["role"], (None, None))
        rows.append([r["role"], nm, cap, f"=COUNTIF(EWP_Register!$O$2:$O$60,A{i})", f"=COUNTIF(EWP_Register!$Q$2:$Q$60,A{i})",
                     f"=SUMIF(EWP_Register!$O$2:$O$60,A{i},EWP_Register!$U$2:$U$60)",
                     f"=SUMIF(EWP_Register!$O$2:$O$60,A{i},EWP_Register!$V$2:$V$60)", r["remit"]])
    write_table(tm, ["Role", "Name (overwrite)", "Capacity (hours per week)", "Assigned EWPs (owner)", "Reviewing EWPs",
                     "Planned hours", "Actual hours", "Remit (Proposed - to confirm)"], rows, [34, 24, 16, 14, 14, 14, 14, 70],
                input_cols=(2, 3), wrap_cols=(8,))
    tm.auto_filter.ref = f"A1:H{nR + 1}"
    ROLE_DV = f"=Team!$A$2:$A${nR + 1}"

    # Scope_Decision
    sd = sheets["Scope_Decision"]
    prev_reason = {}
    if prior and "Scope_Decision" in prior.sheetnames:
        for row in prior["Scope_Decision"].iter_rows(min_row=2, values_only=True):
            if row[0] and row[9]:
                prev_reason[row[0]] = row[9]
    rows = []
    for i, r in enumerate(hier, 2):
        fid = r[0]
        leaf = fid not in parents
        d = decision[fid]
        status = r[6]
        resp = r[5]
        why = f"ITT scope status: {status}. Responsibility: {resp or 'Not stated'}."
        if d == "Exclude":
            why = f"Outside MinRes scope. {why}"
        elif d == "Price as Option or Alternative":
            why = f"ITT identifies this as a priced option; shown separately from the base price. {why}"
        elif d == "Clarify":
            why = f"Cannot be decided until the linked RFI is answered. {why}"
        elif leaf:
            why = f"Within MinRes scope. {why}"
        else:
            why = f"Roll-up of child FLOCs. {why}"
        if r[16]:
            why += f" Note: {str(r[16])[:200]}"
        rlist = sorted(linked_rfis[fid])
        key_risk = dr["key_risk_text"][d]
        topics = [rfi_by_id[i]["topic"] for i in rlist if i in rfi_by_id][:2]
        if topics:
            key_risk += " Open RFIs: " + "; ".join(topics) + "."
        rows.append([
            fid, r[1], r[2], r[3], "Y" if leaf else "N", status, d, why,
            f'=IF(G{i}="","No decision",IF(OR(G{i}=IFERROR(VLOOKUP(F{i},Lists!$J$2:$L$10,2,FALSE),""),G{i}=IFERROR(VLOOKUP(F{i},Lists!$J$2:$L$10,3,FALSE),"")),"Aligned","Departs from ITT"))',
            prev_reason.get(fid) or reason.get(fid) or None,
            r[7], r[9], r[10], interface_of(resp),
            f'=IF(E{i}="N","Roll-up",IF(P{i}="",IF(G{i}="Exclude","n/a",""),IFERROR(INDEX(EWP_Register!$G$2:$G$60,MATCH(P{i},EWP_Register!$A$2:$A$60,0)),"")))',
            f'=IFERROR(INDEX(FLOC_to_EWP_Map!$C$2:$C${BUF},MATCH(A{i},FLOC_to_EWP_Map!$A$2:$A${BUF},0)),"")',
            key_risk, risk_of(fid), ", ".join(rlist),
            f'=COUNTIFS(RFI_Log!$B$2:$B${BUF},"Carried forward - auto-extracted",RFI_Log!$I$2:$I${BUF},A{i})',
            "Proposed - to confirm",
        ])
    write_table(sd, ["FLOC ID", "Level", "Description", "Parent ID", "Leaf (Y/N)", "ITT scope status", "MinRes Scope Decision",
                     "Decision rationale", "Variance flag", "Reason for departure from ITT", "Source ID", "PDF page", "Printed page",
                     "Scope interface", "Delivery method (from EWP)", "EWP ID", "Key commercial risk", "Risk rating",
                     "Linked RFIs", "Open auto-extracted gaps", "Decision basis"], rows,
                [20, 7, 48, 17, 8, 13, 28, 60, 16, 45, 11, 9, 9, 24, 16, 12, 55, 10, 30, 11, 20],
                input_cols=(7, 10, 18, 19), wrap_cols=(3, 8, 10, 17))
    last_sd = sd.max_row
    add_dv(sd, L("A", 5), "G", 2, last_sd)
    add_dv(sd, L("C", 3), "R", 2, last_sd)
    colour_cf(sd, f"G2:G{last_sd}", DECISIONS)
    colour_cf(sd, f"R2:R{last_sd}", RISKS)
    sd.conditional_formatting.add(f"I2:I{last_sd}", CellIsRule(operator="equal", formula=['"Departs from ITT"'], fill=fill("F8CBAD")))
    sd.conditional_formatting.add(f"I2:I{last_sd}", CellIsRule(operator="equal", formula=['"No decision"'], fill=fill("FFC7CE")))

    # FLOC_to_EWP_Map
    mp = sheets["FLOC_to_EWP_Map"]
    rows = []
    for i, l in enumerate([x for x in leaves if x in ewp_of], 2):
        r = byid[l]
        rows.append([l, r[2], ewp_of[l], f'=IFERROR(INDEX(Scope_Decision!$G$2:$G${BUF},MATCH(A{i},Scope_Decision!$A$2:$A${BUF},0)),"")',
                     ewp_basis[l], r[7], r[9]])
    write_table(mp, ["FLOC ID", "FLOC description", "EWP ID", "MinRes Scope Decision", "Mapping basis", "Source ID", "PDF page"],
                rows, [20, 60, 14, 28, 26, 11, 9], input_cols=(3,), wrap_cols=(2,))
    add_dv(mp, f"=EWP_Register!$A$2:$A${len(cfg['ewps']) + 1}", "C", 2, BUF)
    colour_cf(mp, f"D2:D{BUF}", DECISIONS)

    # Inputs_Tracker
    prev_in = {}
    if prior and "Inputs_Tracker" in prior.sheetnames:
        for row in prior["Inputs_Tracker"].iter_rows(min_row=2, values_only=True):
            if row[0]:
                prev_in[(row[0], row[1])] = row[4:7]
    it = sheets["Inputs_Tracker"]
    rows = []
    n_inputs = defaultdict(int)
    for e in cfg["ewps"]:
        dm = delivery_of(e)
        tpl = list(cfg["inputs"]["all"]) + list(cfg["inputs"].get(dm, []))
        if e["method"] == "Vendor quote" and dm != "Supply-only":
            tpl += cfg["inputs"]["Vendor quote method"]
        tpl += cfg["inputs"]["by_ewp"].get(e["id"].replace("EWP-", ""), [])
        for t in tpl:
            keyname = t["input"]
            pr = prev_in.get((e["id"], keyname))
            rows.append([e["id"], keyname, t["type"], t["source"], (pr[0] if pr else None), (pr[1] if pr else None),
                         ((pr[2] if pr and pr[2] else None) or t["status"])])
            n_inputs[e["id"]] += 1
    write_table(it, ["EWP ID", "Input required", "Type", "Supplier or source", "Date requested", "Date received", "Status"],
                rows, [14, 60, 22, 55, 14, 14, 20], input_cols=(5, 6, 7), wrap_cols=(2, 4))
    for row in it.iter_rows(min_row=2, min_col=5, max_col=6):
        for c in row:
            c.number_format = "dd/mm/yyyy"
    add_dv(it, L("F", 5), "G", 2, BUF)
    add_dv(it, f"=EWP_Register!$A$2:$A${len(cfg['ewps']) + 1}", "A", 2, BUF)

    # EWP_Register
    prev_ewp = {}
    if prior and "EWP_Register" in prior.sheetnames:
        for row in prior["EWP_Register"].iter_rows(min_row=2, values_only=True):
            if row[0]:
                prev_ewp[row[0]] = row
    ew = sheets["EWP_Register"]
    rows = []
    for i, e in enumerate(cfg["ewps"], 2):
        fl = ewp_flocs[e["id"]]
        sids = sorted({byid[f][7] for f in fl})
        pgs = parse_pages(byid[f][9] for f in fl)
        rf = sorted({x for f in fl for x in linked_rfis[f]})
        pv = prev_ewp.get(e["id"])
        dm = delivery_of(e)
        notes = {"EWP-CON-01": "Reinforcement is supply-only (proposed).", "EWP-STR-01": "Modular accommodation is supply-only (proposed).",
                 "EWP-CIV-05": "Liner is a specialist subcontract (proposed)."}.get(e["id"], "")
        rows.append([
            e["id"], e["title"], e["desc"], ", ".join(fl),
            f'=COUNTIF(FLOC_to_EWP_Map!$C$2:$C${BUF},A{i})', cfg["discipline_names"][e["disc"]], dm, cfg["delivery_basis"],
            e["method"], f'=COUNTIF(Inputs_Tracker!$A$2:$A${BUF},A{i})', ", ".join(sids), pgs,
            f'=IF(E{i}=0,"",IF(COUNTIFS(Scope_Decision!$P$2:$P${BUF},A{i},Scope_Decision!$R$2:$R${BUF},"High")>0,"High",IF(COUNTIFS(Scope_Decision!$P$2:$P${BUF},A{i},Scope_Decision!$R$2:$R${BUF},"Medium")>0,"Medium","Low")))',
            cfg["estimate_class"], e["owner"],
            f'=IF(O{i}="","",IFERROR(IF(INDEX(Team!$B$2:$B$30,MATCH(O{i},Team!$A$2:$A$30,0))="","(name not entered)",INDEX(Team!$B$2:$B$30,MATCH(O{i},Team!$A$2:$A$30,0))),""))',
            e["reviewer"], ", ".join(rf) if rf else "None linked",
            (pv[18] if pv and pv[18] else "Not started"), (pv[19] if pv else None), (pv[20] if pv else None), (pv[21] if pv else None),
            ((pv[22] if pv and pv[22] else "") or notes),
        ])
    write_table(ew, ["EWP ID", "Title", "Scope description", "FLOCs included", "FLOC count", "Discipline", "Delivery method",
                     "Delivery basis", "Estimate method", "Inputs required (count)", "Source IDs", "PDF pages", "Risk rating",
                     "Estimate class (Assumption)", "Owner (role)", "Owner (name)", "Reviewer (role)", "RFI dependencies", "Status",
                     "Due date", "Planned hours", "Actual hours", "Notes"], rows,
                [14, 40, 55, 50, 8, 22, 14, 20, 20, 10, 40, 22, 10, 34, 28, 18, 28, 36, 13, 12, 10, 10, 36],
                input_cols=(7, 9, 15, 17, 19, 20, 21, 22, 23), wrap_cols=(2, 3, 4, 11, 12, 14, 18, 23))
    nE = len(cfg["ewps"])
    ew.auto_filter.ref = f"A1:W{nE + 1}"
    add_dv(ew, L("D", 3), "G", 2, nE + 1)
    add_dv(ew, L("E", 5), "I", 2, nE + 1)
    add_dv(ew, ROLE_DV, "O", 2, nE + 1)
    add_dv(ew, ROLE_DV, "Q", 2, nE + 1)
    add_dv(ew, L("B", 4), "S", 2, nE + 1)
    for c in ("T",):
        for row in ew.iter_rows(min_row=2, min_col=20, max_col=20):
            for x in row:
                x.number_format = "dd/mm/yyyy"
    colour_cf(ew, f"M2:M{nE + 1}", RISKS)
    colour_cf(ew, f"S2:S{nE + 1}", ["Complete", "In review", "In progress"])

    # RFI_Log
    prev_rfi = {}
    if prior and "RFI_Log" in prior.sheetnames:
        for row in prior["RFI_Log"].iter_rows(min_row=2, values_only=True):
            if row[0]:
                prev_rfi[row[0]] = row
    rf = sheets["RFI_Log"]
    rows = []
    for r in rfis:
        pv = prev_rfi.get(r["id"])
        rows.append([r["id"], r["origin"], r["type"], r["topic"], r["question"], r["priority"], r["sid"], r["page"], r["flocs"],
                     r["impact"], (pv[10] if pv else r["owner"]), (pv[11] if pv else r["status"]), (pv[12] if pv else None), (pv[13] if pv else None)])
    write_table(rf, ["RFI / gap ID", "Origin", "Type", "Topic", "Question or gap", "Priority", "Source ID", "PDF page",
                     "Linked FLOC IDs", "Impact on scope decisions and allocation", "Owner (role)", "Status", "Date raised", "Date answered"],
                rows, [14, 28, 20, 36, 60, 9, 11, 9, 36, 55, 28, 11, 12, 12], input_cols=(11, 12, 13, 14), wrap_cols=(4, 5, 9, 10))
    add_dv(rf, ROLE_DV, "K", 2, BUF)
    add_dv(rf, L("G", 5), "L", 2, BUF)
    for row in rf.iter_rows(min_row=2, min_col=13, max_col=14):
        for c in row:
            c.number_format = "dd/mm/yyyy"
    colour_cf(rf, f"F2:F{len(rows) + 1}", ["High", "Medium", "Low"])

    # Bid_Programme
    bp = sheets["Bid_Programme"]
    rows = []
    for i, m in enumerate(cfg["bid_programme"], 2):
        dt = datetime.strptime(m["date"], "%d/%m/%Y") if m["date"] else None
        rows.append([m["category"], m["milestone"], dt, m["time"], m["owner"], m["basis"], m["source_id"], m["pdf_page"],
                     "Not started", f'=IF(C{i}="","Date not set",IF(C{i}<TODAY(),"Past","Upcoming"))', m["notes"]])
    write_table(bp, ["Category", "Milestone", "Planned date", "Time", "Owner (role)", "Basis", "Source ID", "PDF page", "Status",
                     "Against today", "Notes"], rows, [18, 44, 14, 14, 28, 18, 11, 9, 14, 14, 70], input_cols=(3, 4, 5, 9), wrap_cols=(11, 2))
    for row in bp.iter_rows(min_row=2, min_col=3, max_col=3):
        for c in row:
            c.number_format = "dd/mm/yyyy"
    add_dv(bp, ROLE_DV, "E", 2, 40)
    add_dv(bp, L("H", 3), "I", 2, 40)
    bp.conditional_formatting.add("J2:J40", CellIsRule(operator="equal", formula=['"Past"'], fill=fill("FFC7CE")))

    # Validation
    va = sheets["Validation"]
    S = lambda c: f"Scope_Decision!${c}$2:${c}${BUF}"
    M = lambda c: f"FLOC_to_EWP_Map!${c}$2:${c}${BUF}"
    E_ = lambda c: f"EWP_Register!${c}$2:${c}$60"
    I_ = lambda c: f"Inputs_Tracker!${c}$2:${c}${BUF}"
    R_ = lambda c: f"RFI_Log!${c}$2:${c}${BUF}"
    checks = [
        ("FLOCs with no MinRes Scope Decision", f'=SUMPRODUCT(({S("A")}<>"")*({S("G")}=""))', "Select a decision in Scope_Decision column G."),
        ("Priceable leaf FLOCs not assigned to an EWP", f'=SUMPRODUCT(({S("E")}="Y")*({S("G")}<>"Exclude")*({S("G")}<>"")*({S("P")}=""))', "Add the FLOC to FLOC_to_EWP_Map."),
        ("FLOC rows assigned to more than one EWP", f'=SUMPRODUCT(({M("A")}<>"")*(COUNTIF({M("A")},{M("A")})>1))', "Each FLOC must have exactly one row in FLOC_to_EWP_Map."),
        ("Excluded FLOCs still assigned to an EWP", f'=SUMPRODUCT(({S("G")}="Exclude")*({S("P")}<>""))', "Remove from FLOC_to_EWP_Map or change the decision."),
        ("EWPs with no owner", f'=SUMPRODUCT(({E_("A")}<>"")*({E_("O")}=""))', "Set the owner role."),
        ("EWPs with no reviewer", f'=SUMPRODUCT(({E_("A")}<>"")*({E_("Q")}=""))', "Set the reviewer role."),
        ("EWPs with no due date", f'=SUMPRODUCT(({E_("A")}<>"")*({E_("T")}=""))', "Enter due dates (none are stated in the ITT; see Bid_Programme)."),
        ("EWPs with no FLOCs", f'=SUMPRODUCT(({E_("A")}<>"")*({E_("E")}=0))', "Map FLOCs or remove the EWP."),
        ("Decisions that depart from the ITT status without a reason", f'=SUMPRODUCT(({S("I")}="Departs from ITT")*({S("J")}=""))', "Enter the reason in Scope_Decision column J."),
        ("Scope decisions with no Source ID or PDF page", f'=SUMPRODUCT(({S("G")}<>"")*((({S("K")}="")+({S("L")}=""))>0))', "Record the source or set the decision to Clarify."),
        ("Clarify decisions with no linked RFI", f'=SUMPRODUCT(({S("G")}="Clarify")*({S("S")}=""))', "Link an RFI in Scope_Decision column S and add it to RFI_Log."),
        ("EWPs with no inputs listed", f'=SUMPRODUCT(({E_("A")}<>"")*(COUNTIF({I_("A")},{E_("A")})=0))', "Add rows in Inputs_Tracker."),
        ("Duplicate FLOC IDs (Scope_Decision)", f'=SUMPRODUCT(({S("A")}<>"")*(COUNTIF({S("A")},{S("A")})>1))', ""),
        ("Duplicate EWP IDs", f'=SUMPRODUCT(({E_("A")}<>"")*(COUNTIF({E_("A")},{E_("A")})>1))', ""),
        ("Duplicate RFI IDs", f'=SUMPRODUCT(({R_("A")}<>"")*(COUNTIF({R_("A")},{R_("A")})>1))', ""),
        ("Orphan: Scope_Decision parent ID not in FLOC list", f'=SUMPRODUCT(({S("D")}<>"")*(COUNTIF({S("A")},{S("D")})=0))', ""),
        ("Orphan: map FLOC not in Scope_Decision", f'=SUMPRODUCT(({M("A")}<>"")*(COUNTIF({S("A")},{M("A")})=0))', ""),
        ("Orphan: map EWP not in EWP_Register", f'=SUMPRODUCT(({M("C")}<>"")*(COUNTIF({E_("A")},{M("C")})=0))', ""),
        ("Orphan: Inputs_Tracker EWP not in EWP_Register", f'=SUMPRODUCT(({I_("A")}<>"")*(COUNTIF({E_("A")},{I_("A")})=0))', ""),
        ("Orphan: EWP owner or reviewer role not in Team", f'=SUMPRODUCT(({E_("O")}<>"")*(COUNTIF(Team!$A$2:$A$30,{E_("O")})=0))+SUMPRODUCT(({E_("Q")}<>"")*(COUNTIF(Team!$A$2:$A$30,{E_("Q")})=0))', ""),
        ("Reconciliation: input workbook FLOC count minus Scope_Decision FLOC count", f"=ABS(B{len(cfg['ewps']) + 30}-COUNTA({S('A')}))", "Input FLOC count is recorded below at build time."),
    ]
    va.append(["#", "Check", "Result", "Count (should be 0)", "Action if failed"])
    for c in va[1]:
        c.fill, c.font, c.border = HDR_FILL, HDR_FONT, BORDER
    ref_row = len(checks) + 3
    for n, (name, f, act) in enumerate(checks, 1):
        r = n + 1
        if n == len(checks):
            f = f"=ABS(B{ref_row}-COUNTA({S('A')}))"
        va.append([n, name, f'=IF(D{r}=0,"PASS","FAIL")', f, act])
    va.cell(ref_row, 1, "Reference value recorded at build time")
    va.cell(ref_row, 2, n_floc)
    va.cell(ref_row, 1).font = Font(bold=True)
    va.cell(ref_row + 1, 1, "Source")
    va.cell(ref_row + 1, 2, f"FLOC_Hierarchy row count in {os.path.basename(a.input)}")
    for w, c in zip([6, 70, 10, 18, 70], "ABCDE"):
        va.column_dimensions[c].width = w
    va.freeze_panes = "A2"
    va.conditional_formatting.add(f"C2:C{len(checks) + 1}", CellIsRule(operator="equal", formula=['"PASS"'], fill=fill("C6EFCE")))
    va.conditional_formatting.add(f"C2:C{len(checks) + 1}", CellIsRule(operator="equal", formula=['"FAIL"'], fill=fill("FFC7CE")))
    va.auto_filter.ref = f"A1:E{len(checks) + 1}"
    n_checks = len(checks)

    # Dashboard
    db = sheets["Dashboard"]
    db["A1"] = "Winu - MinRes quotation scope and EWP dashboard"
    db["A1"].font = Font(bold=True, size=14)
    db["A2"] = "All figures are formulas and update when decisions, statuses or hours change."
    hdr = lambda r, vals: [db.cell(r, i + 1, v).__setattr__("font", Font(bold=True)) or db.cell(r, i + 1).__setattr__("fill", fill("D9E1F2")) for i, v in enumerate(vals)]
    hdr(4, ["Scope Decision", "All FLOCs", "Leaf FLOCs"])
    for i, d in enumerate(DECISIONS, 5):
        db.cell(i, 1, d)
        db.cell(i, 2, f'=COUNTIF({S("G")},A{i})')
        db.cell(i, 3, f'=COUNTIFS({S("G")},A{i},{S("E")},"Y")')
    db.cell(10, 1, "No decision")
    db.cell(10, 2, f'=SUMPRODUCT(({S("A")}<>"")*({S("G")}=""))')
    db.cell(10, 3, f'=SUMPRODUCT(({S("E")}="Y")*({S("G")}=""))')
    db.cell(11, 1, "Total")
    db.cell(11, 2, "=SUM(B5:B10)")
    db.cell(11, 3, "=SUM(C5:C10)")
    db.cell(12, 1, "FLOCs decided (%)")
    db.cell(12, 2, "=IF(B11=0,0,(B11-B10)/B11)")
    db.cell(12, 3, "=IF(C11=0,0,(C11-C10)/C11)")
    db["B12"].number_format = db["C12"].number_format = "0.0%"
    colour_cf(db, "A5:A9", DECISIONS)

    hdr(14, ["ITT scope status", "FLOCs"])
    for i, s in enumerate(["In scope", "Excluded", "Provisional"], 15):
        db.cell(i, 1, s)
        db.cell(i, 2, f'=COUNTIF({S("F")},A{i})')
    db.cell(18, 1, "Variance: decisions departing from ITT")
    db.cell(18, 2, f'=COUNTIF({S("I")},"Departs from ITT")')

    hdr(20, ["EWP status", "EWPs"])
    for i, s in enumerate(STATUSES, 21):
        db.cell(i, 1, s)
        db.cell(i, 2, f'=COUNTIF({E_("S")},A{i})')
    db.cell(25, 1, "Total EWPs")
    db.cell(25, 2, "=SUM(B21:B24)")

    hdr(27, ["Owner (role)", "EWPs", "Planned hours", "Actual hours"])
    for k in range(nR):
        i = 28 + k
        db.cell(i, 1, f"=Team!A{k + 2}")
        db.cell(i, 2, f'=COUNTIF({E_("O")},A{i})')
        db.cell(i, 3, f'=SUMIF({E_("O")},A{i},{E_("U")})')
        db.cell(i, 4, f'=SUMIF({E_("O")},A{i},{E_("V")})')
    t0 = 28 + nR
    db.cell(t0, 1, "Total")
    for c in "BCD":
        db[f"{c}{t0}"] = f"=SUM({c}28:{c}{t0 - 1})"
    db.cell(t0 + 1, 1, "Planned less actual hours")
    db.cell(t0 + 1, 2, f"=C{t0}-D{t0}")
    db.cell(t0 + 2, 1, "Actual as % of planned")
    db.cell(t0 + 2, 2, f"=IF(C{t0}=0,0,D{t0}/C{t0})")
    db.cell(t0 + 2, 2).number_format = "0.0%"

    r0 = t0 + 4
    hdr(r0, ["RFIs and validation", "Count"])
    items = [
        ("Open RFIs and gaps (all)", f'=COUNTIF({R_("L")},"Open")'),
        ("Open authored and new bid RFIs", f'=COUNTIFS({R_("L")},"Open",{R_("B")},"Carried forward - authored")+COUNTIFS({R_("L")},"Open",{R_("B")},"New - bid specific")+COUNTIFS({R_("L")},"Draft",{R_("B")},"New - bid specific")'),
        ("Open auto-extracted gaps", f'=COUNTIFS({R_("L")},"Open",{R_("B")},"Carried forward - auto-extracted")'),
        ("High-priority open items (all)", f'=COUNTIFS({R_("L")},"Open",{R_("F")},"High")'),
        ("Validation checks failing", f'=COUNTIF(Validation!$C$2:$C${n_checks + 1},"FAIL")'),
    ]
    for k, (n_, f) in enumerate(items, 1):
        db.cell(r0 + k, 1, n_)
        db.cell(r0 + k, 2, f)
    db.column_dimensions["A"].width = 44
    for c in "BCD":
        db.column_dimensions[c].width = 16
    ch = BarChart()
    ch.title = "Leaf FLOCs by Scope Decision"
    ch.add_data(Reference(db, min_col=3, min_row=4, max_row=10), titles_from_data=True)
    ch.set_categories(Reference(db, min_col=1, min_row=5, max_row=10))
    ch.legend = None
    ch.height, ch.width = 7.5, 15
    db.add_chart(ch, "F4")
    ch2 = BarChart()
    ch2.title = "EWPs by status"
    ch2.add_data(Reference(db, min_col=2, min_row=20, max_row=24), titles_from_data=True)
    ch2.set_categories(Reference(db, min_col=1, min_row=21, max_row=24))
    ch2.legend = None
    ch2.height, ch2.width = 7.5, 15
    db.add_chart(ch2, "F20")

    # README
    rd = sheets["README"]
    today = date.today().strftime("%d/%m/%Y")
    lines = [
        ("Winu - MinRes quotation scope and estimation work packages", None),
        ("Purpose", "Sets the MinRes scope decision for every FLOC in the ITT pack, groups the priced leaf FLOCs into estimation work packages (EWPs) and assigns them to roles so the estimate can be built, reviewed and consolidated. It holds no costs."),
        ("Tender role", cfg["tender_role"]),
        ("Input file", os.path.abspath(a.input)),
        ("Config file", os.path.abspath(a.config)),
        ("Version", cfg["version"]),
        ("Date", today),
        ("Currency", "AUD unless the ITT states otherwise. No amounts are held."),
        ("Abbreviations", "ITT: invitation to tender. FLOC: functional location. WBS: work breakdown structure. CBS: cost breakdown structure. EWP: estimation work package. RFI: request for information. SP: separable part. MSA: mine services area. MPP: mineral processing plant. IPP: independent power producer. TSF: tailings storage facility. MTO: material take-off. AR: allocation rule (input workbook, Allocation_Rules)."),
        ("Traceability", "Source ID and PDF page columns come from the input workbook (FLOC_Hierarchy primary source). PDF page is the physical page in the PDF."),
        ("", None),
        ("Instructions", None),
        ("1", "Review Scope_Decision. Yellow cells are inputs. Change a decision in column G; a variance flag appears if it departs from the ITT status and column J then needs a reason."),
        ("2", "Overwrite the role names on the Team sheet and enter capacity in hours per week. Names flow to EWP_Register."),
        ("3", "On EWP_Register enter due dates, planned hours and actual hours, and update status. Delivery method and estimate method are proposed defaults to confirm."),
        ("4", "Track inputs on Inputs_Tracker (dates requested and received, status) and RFIs on RFI_Log."),
        ("5", "Check the Validation sheet. All checks should show PASS before the estimate is consolidated."),
        ("6", "To change delivery-method defaults, EWP groupings, owners or decision overrides, edit the config JSON and re-run the build script with --carry-forward (see the minres-quotation-scope-ewp skill). Edits made directly to decisions, delivery, owners or mapping in this workbook are replaced by the config on a re-run."),
        ("", None),
        ("Assumptions", None),
        ("A1", "EWPs are built on leaf FLOCs only. Parent FLOC decisions are roll-ups and are not recalculated if a leaf decision is changed."),
        ("A2", "Provisional FLOCs described as priced options are set to Price as Option or Alternative by default. Other Provisional FLOCs are Clarify until an RFI is answered."),
        ("A3", "Delivery method and estimate method are Proposed - to confirm. Estimate class is an assumption: " + cfg["estimate_class"] + "."),
        ("A4", "Risk ratings are a starting assumption: Medium by default (no quantities in the ITT), High for Clarify, option and provisional items or items linked to a High-priority RFI, Low for excluded items."),
        ("A5", "Due dates, planned hours, capacity and names are not stated in the ITT and are left blank. The FLOCs included text on EWP_Register is generated at build time; FLOC count and risk are live."),
        ("A6", "The ITT tender closing date (07/10/2026, 4:00pm AWST) is before the build date; see BID-RFI-03."),
        ("", None),
        ("Colour legend", None),
    ]
    for r_, (a_, b_) in enumerate(lines, 1):
        rd.cell(r_, 1, a_)
        if b_ is not None:
            rd.cell(r_, 2, b_)
            rd.cell(r_, 2).alignment = Alignment(wrap_text=True, vertical="top")
        if b_ is None and a_:
            rd.cell(r_, 1).font = Font(bold=True, size=12 if r_ > 1 else 14)
    r_ = len(lines) + 1
    legend = [("Yellow fill", "Input cell: change me", "FFF2CC")] + [(d, "Scope Decision", COLOURS[d]) for d in DECISIONS] + \
             [("High", "Risk rating", COLOURS["High"]), ("Medium", "Risk rating", COLOURS["Medium"]), ("Low", "Risk rating", COLOURS["Low"]),
              ("Grey header", "Column headers; no fill elsewhere means a formula or fixed value", "1F3864")]
    for n_, d_, c_ in legend:
        rd.cell(r_, 1, n_).fill = fill(c_)
        if c_ == "1F3864":
            rd.cell(r_, 1).font = Font(color="FFFFFF")
        rd.cell(r_, 2, d_)
        r_ += 1
    rd.column_dimensions["A"].width = 26
    rd.column_dimensions["B"].width = 130

    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    wb.save(a.output)

    dec_counts = defaultdict(int)
    for l in leaves:
        dec_counts[leaf_decision[l]] += 1
    print(f"Wrote {a.output}")
    print(f"FLOCs: {n_floc} (leaves {len(leaves)}); ITT status: {dict(itt_counts)}")
    print(f"Leaf decisions: {dict(dec_counts)}")
    print(f"EWPs: {len(cfg['ewps'])}; leaf FLOCs mapped: {len(ewp_of)}; RFI rows: {len(rfis)}")


if __name__ == "__main__":
    main()
