# -*- coding: utf-8 -*-
"""Build the MinRes operational systems capability scope workbook (ISA-95 framing).

Reads the MinRes quotation scope/EWP workbook and the FLOC workbook (Source_Register),
applies the capability content in a JSON config, and writes a new workbook.
Never modifies the inputs. Run with: python -I build_ops_capability_workbook.py --help
"""
import argparse, datetime, json, os, shutil, sys, tempfile, warnings
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

warnings.filterwarnings("ignore")

HDR_FILL = PatternFill("solid", start_color="D9D9D9", end_color="D9D9D9")
INPUT_FILL = PatternFill("solid", start_color="FFFF99", end_color="FFFF99")
TITLE_FONT = Font(bold=True, size=14)
BOLD = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

LEVEL_COL = {"Level 0": "E7E6E6", "Level 1": "DDEBF7", "Level 2": "E2EFDA", "Level 3": "FCE4D6",
             "Level 4": "E4DFEC", "Cross-cutting": "FFF2CC"}
POS_COL = {"Within MinRes scope": "C6EFCE", "Owner scope": "D9D9D9", "Third-party scope": "E4DFEC",
           "Interface only": "BDD7EE", "Not in ITT": "FFC7CE", "Clarify": "FFEB9C"}
POS_CODE = {"Within MinRes scope": "W", "Owner scope": "O", "Third-party scope": "T",
            "Interface only": "I", "Not in ITT": "N", "Clarify": "C"}


def fill(hex_):
    return PatternFill("solid", start_color=hex_, end_color=hex_)


def header(ws, row, names, widths=None):
    for i, n in enumerate(names, 1):
        c = ws.cell(row=row, column=i, value=n)
        c.font = BOLD; c.fill = HDR_FILL; c.alignment = WRAP; c.border = BORDER
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[L(i)].width = w


def put(ws, row, values, wrap=True):
    for i, v in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.border = BORDER
        if wrap:
            c.alignment = WRAP


def cf_map(ws, rng, mapping):
    for text, hexc in mapping.items():
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"%s"' % text], fill=fill(hexc)))


def add_list(ws, rng, ref):
    dv = DataValidation(type="list", formula1=ref, allow_blank=True)
    ws.add_data_validation(dv); dv.add(rng)


def load_inputs(scope_path, floc_path):
    tmp = tempfile.mkdtemp(prefix="ops_in_")
    out = []
    for p in (scope_path, floc_path):
        dst = os.path.join(tmp, os.path.basename(p))
        shutil.copy2(p, dst)
        out.append(openpyxl.load_workbook(dst, data_only=True))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--scope-workbook", required=True)
    ap.add_argument("--floc-workbook", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if os.path.exists(a.output) and not a.force:
        sys.exit("Output exists; use --force to overwrite: " + a.output)

    cfg = json.load(open(a.config, encoding="utf-8"))
    meta, lists = cfg["meta"], cfg["lists"]
    caps, ifaces, rfis, assumptions = cfg["capabilities"], cfg["interfaces"], cfg["rfis"], cfg["assumptions"]
    props, fw = cfg["proposed_ewps"], cfg["framework"]
    PAGES = meta["itt_pdf_pages"]
    today = datetime.date.today().strftime("%d/%m/%Y")

    swb, fwb = load_inputs(a.scope_workbook, a.floc_workbook)

    # ---------------- read inputs
    flocs = {}
    for r in list(swb["Scope_Decision"].iter_rows(min_row=2, values_only=True)):
        if r[0]:
            flocs[r[0]] = dict(desc=r[2], leaf=r[4], status=r[5], decision=r[6], src=r[10], page=r[11], ewp=r[15])
    ewps = {}
    for r in list(swb["EWP_Register"].iter_rows(min_row=2, values_only=True)):
        if r[0]:
            ewps[r[0]] = dict(title=r[1], disc=r[5], owner=r[14], risk=r[12])
    rfi_rows = [r for r in swb["RFI_Log"].iter_rows(min_row=2, values_only=True) if r[0]]
    roles = [r[0] for r in swb["Team"].iter_rows(min_row=2, values_only=True) if r[0]]
    srcs = {}
    for r in fwb["Source_Register"].iter_rows(min_row=2, values_only=True):
        if r[0]:
            srcs[r[0]] = dict(page=r[4], title=r[9])

    # ---------------- validate config references
    errs = []
    prop_ids = {p["id"] for p in props}
    cap_ids = [c["id"] for c in caps]
    if len(set(cap_ids)) != len(cap_ids):
        errs.append("Duplicate capability IDs in config")
    rfi_ids = {r[0] for r in rfi_rows} | {r["id"] for r in rfis}
    if_ids = {i["id"] for i in ifaces}
    for c in caps:
        for s in c["src"]:
            if s not in srcs: errs.append("%s: unknown Source ID %s" % (c["id"], s))
        for f in c["floc"]:
            if f not in flocs: errs.append("%s: unknown FLOC %s" % (c["id"], f))
        for e in c["ewp"]:
            if e not in ewps: errs.append("%s: unknown EWP %s" % (c["id"], e))
        for p in c["prop"]:
            if p not in prop_ids: errs.append("%s: unknown proposed EWP %s" % (c["id"], p))
        for i in c["ifs"]:
            if i not in if_ids: errs.append("%s: unknown interface %s" % (c["id"], i))
        for r in c["rfi"]:
            if r not in rfi_ids: errs.append("%s: unknown RFI %s" % (c["id"], r))
        if c["pos"] not in lists["positions"]: errs.append("%s: bad position" % c["id"])
    for i in ifaces:
        for s in i["sources"]:
            if s not in srcs: errs.append("%s: unknown Source ID %s" % (i["id"], s))
        for cp in i["caps"]:
            if cp not in cap_ids: errs.append("%s: unknown capability %s" % (i["id"], cp))
    for r in rfis:
        if r["source"] not in srcs: errs.append("%s: unknown Source ID %s" % (r["id"], r["source"]))
    if errs:
        sys.exit("Config errors:\n" + "\n".join(errs))

    # derive EWP links from FLOC map
    for c in caps:
        derived = {flocs[f]["ewp"] for f in c["floc"] if flocs[f]["ewp"]}
        c["ewp_all"] = sorted(derived | set(c["ewp"]))
    # reverse RFI -> caps
    rfi_caps = {}
    for c in caps:
        for r in c["rfi"]:
            rfi_caps.setdefault(r, []).append(c["id"])

    def pages_of(ids):
        ps = sorted({srcs[s]["page"] for s in ids})
        return ", ".join(str(p) for p in ps)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    names = ["README", "Dashboard", "ISA95_Framework", "Capability_Catalogue", "Capability_to_FLOC_EWP_Map",
             "Capability_Matrix", "Interface_Register", "EWP_Impact", "Assumptions_and_RFIs", "Validation",
             "Capability_Sources", "Lists", "Ref_FLOC", "Ref_EWP", "Ref_Source", "Ref_RFI"]
    S = {n: wb.create_sheet(n) for n in names}

    # ---------------- Lists
    ws = S["Lists"]
    status_list = ["Open", "Draft", "Answered", "Closed", "Assumed"]
    list_defs = [("Position", lists["positions"]), ("ISA-95 level", lists["levels"]), ("Domain", lists["domains"]),
                 ("Delivery type", lists["delivery"]), ("Confidence", lists["confidence"]), ("Activity model", lists["activity"]),
                 ("Link type", ["FLOC", "EWP", "EWP-Proposed", "RFI"]), ("Priority", ["High", "Medium", "Low"]),
                 ("Status", status_list), ("Role", roles), ("Basis", ["Standard", "Adaptation"]),
                 ("Interface type", ["System-to-system", "Party-to-party"]),
                 ("Input availability", ["In ITT pack", "Partly in ITT pack", "Not available in ITT"]),
                 ("Category", ["Assumption", "Ambiguity", "Clarification", "Missing information", "Missing document", "Input conflict"]),
                 ("Input status", ["Not requested", "Requested", "Received"]),
                 ("EWP change", ["New", "Amend"])]
    LIST_REF = {}
    for i, (h, vals) in enumerate(list_defs, 1):
        ws.cell(row=1, column=i, value=h).font = BOLD
        for j, v in enumerate(vals, 2):
            ws.cell(row=j, column=i, value=v)
        LIST_REF[h] = "=Lists!$%s$2:$%s$%d" % (L(i), L(i), len(vals) + 1)
        ws.column_dimensions[L(i)].width = 24
    kc = len(list_defs) + 2
    ws.cell(row=1, column=kc, value="Constant").font = BOLD
    ws.cell(row=1, column=kc + 1, value="Value").font = BOLD
    consts = [("ITT PDF page count", PAGES), ("Input FLOC count at build", len(flocs)),
              ("Input EWP count at build", len(ewps)), ("Input RFI/gap rows at build", len(rfi_rows))]
    for j, (k, v) in enumerate(consts, 2):
        ws.cell(row=j, column=kc, value=k); ws.cell(row=j, column=kc + 1, value=v)
    PG, NF, NE, NR = ["Lists!$%s$%d" % (L(kc + 1), r) for r in (2, 3, 4, 5)]
    ws.column_dimensions[L(kc)].width = 30

    # ---------------- Ref sheets
    ws = S["Ref_FLOC"]; header(ws, 1, ["FLOC ID", "Description", "Leaf (Y/N)", "ITT scope status", "MinRes Scope Decision", "EWP ID", "Source ID", "PDF page"], [18, 60, 8, 14, 26, 14, 12, 8])
    for i, (k, v) in enumerate(flocs.items(), 2):
        for j, x in enumerate([k, v["desc"], v["leaf"], v["status"], v["decision"], v["ewp"], v["src"], v["page"]], 1):
            ws.cell(row=i, column=j, value=x)
    ws = S["Ref_EWP"]; header(ws, 1, ["EWP ID", "Title", "Owner (role)", "Discipline", "Risk"], [14, 60, 28, 26, 10])
    for i, (k, v) in enumerate(ewps.items(), 2):
        for j, x in enumerate([k, v["title"], v["owner"], v["disc"], v["risk"]], 1):
            ws.cell(row=i, column=j, value=x)
    ws = S["Ref_Source"]; header(ws, 1, ["Source ID", "PDF page", "Title"], [12, 10, 80])
    for i, (k, v) in enumerate(srcs.items(), 2):
        for j, x in enumerate([k, v["page"], v["title"]], 1):
            ws.cell(row=i, column=j, value=x)
    ws = S["Ref_RFI"]; header(ws, 1, ["RFI / gap ID", "Topic", "Priority", "Status", "Source ID", "PDF page"], [14, 60, 10, 10, 12, 8])
    for i, r in enumerate(rfi_rows, 2):
        for j, x in enumerate([r[0], r[3], r[5], r[11], r[6], r[7]], 1):
            ws.cell(row=i, column=j, value=x)
    for n in ("Ref_FLOC", "Ref_EWP", "Ref_Source", "Ref_RFI"):
        S[n].freeze_panes = "A2"

    # ---------------- Catalogue
    CC = [("id", "Capability ID", 16), ("name", "Capability name", 40), ("lvl", "ISA-95 level", 13), ("act", "Operations activity model", 22),
          ("gen", "Generic activities", 24), ("dom", "Primary domain", 14), ("oth", "Other domains affected", 20), ("desc", "Description", 60),
          ("basis", "ISA-95 basis", 12), ("pos", "MinRes Scope Position", 18), ("dt", "Primary delivery type", 14), ("dto", "Other delivery types", 22),
          ("src", "Source ID(s)", 28), ("pages", "PDF page(s)", 12), ("floc", "Linked FLOC IDs", 30), ("ewp", "Linked EWP IDs (input workbook)", 22),
          ("prop", "Proposed EWP (Proposed - to confirm)", 20), ("ifs", "Interfaces", 18), ("conf", "Confidence", 11), ("risk", "Key risk", 46),
          ("impact", "Commercial impact (no pricing)", 46), ("rfi", "Linked RFIs", 22), ("note", "Position basis / notes", 44),
          ("nfloc", "# FLOC links", 9), ("newp", "# EWP links", 9), ("nprop", "# Proposed EWP links", 10), ("nrfi", "# RFI links", 9),
          ("flag", "No existing EWP", 14), ("rank", "Helper rank", 8)]
    K = {k: L(i) for i, (k, _, _) in enumerate(CC, 1)}
    ws = S["Capability_Catalogue"]
    header(ws, 1, [h for _, h, _ in CC], [w for _, _, w in CC])
    MAP = "Capability_to_FLOC_EWP_Map"
    for r, c in enumerate(caps, 2):
        vals = {
            "id": c["id"], "name": c["name"], "lvl": c["lvl"], "act": c["act"], "gen": c["gen"], "dom": c["dom"], "oth": c["oth"],
            "desc": c["desc"], "basis": c["basis"], "pos": c["pos"], "dt": c["dt"], "dto": c["dto"],
            "src": ", ".join(c["src"]) if c["src"] else "n/a (absence confirmed by text search)",
            "pages": pages_of(c["src"]) if c["src"] else "n/a",
            "floc": ", ".join(c["floc"]), "ewp": ", ".join(c["ewp_all"]), "prop": ", ".join(c["prop"]), "ifs": ", ".join(c["ifs"]),
            "conf": c["conf"], "risk": c["risk"], "impact": c["impact"], "rfi": ", ".join(c["rfi"]), "note": c["note"],
        }
        for k, v in vals.items():
            cell = ws["%s%d" % (K[k], r)]; cell.value = v; cell.alignment = WRAP; cell.border = BORDER
        mb, md = "%s!$B$2:$B$1000" % MAP, "%s!$D$2:$D$1000" % MAP
        for key, lt in (("nfloc", "FLOC"), ("newp", "EWP"), ("nprop", "EWP-Proposed"), ("nrfi", "RFI")):
            ws["%s%d" % (K[key], r)] = '=COUNTIFS(%s,$A%d,%s,"%s")' % (mb, r, md, lt)
        ws["%s%d" % (K["flag"], r)] = '=IF(AND(OR(%s%d="Within MinRes scope",%s%d="Interface only",%s%d="Clarify"),%s%d=0),"No EWP","")' % (
            K["pos"], r, K["pos"], r, K["pos"], r, K["newp"], r)
        ws["%s%d" % (K["rank"], r)] = '=IF(%s%d="No EWP",COUNTIF(%s$2:%s%d,"No EWP"),"")' % (K["flag"], r, K["flag"], K["flag"], r)
    NC = len(caps) + 1
    ws.freeze_panes = "C2"; ws.auto_filter.ref = "A1:%s%d" % (K["rank"], NC)
    rng = lambda k: "%s2:%s200" % (K[k], K[k])
    add_list(ws, rng("lvl"), LIST_REF["ISA-95 level"]); add_list(ws, rng("act"), LIST_REF["Activity model"])
    add_list(ws, rng("dom"), LIST_REF["Domain"]); add_list(ws, rng("pos"), LIST_REF["Position"])
    add_list(ws, rng("dt"), LIST_REF["Delivery type"]); add_list(ws, rng("conf"), LIST_REF["Confidence"])
    add_list(ws, rng("basis"), LIST_REF["Basis"])
    cf_map(ws, rng("lvl"), LEVEL_COL); cf_map(ws, rng("pos"), POS_COL)
    cat = lambda k: "Capability_Catalogue!$%s$2:$%s$200" % (K[k], K[k])

    # ---------------- Capability_Sources
    ws = S["Capability_Sources"]
    header(ws, 1, ["Capability ID", "Source ID", "PDF page", "Source title (input workbook)", "Check"], [16, 12, 10, 80, 10])
    r = 2
    for c in caps:
        for s in c["src"]:
            ws.cell(row=r, column=1, value=c["id"]); ws.cell(row=r, column=2, value=s)
            ws.cell(row=r, column=3, value='=IFERROR(INDEX(Ref_Source!$B:$B,MATCH(B%d,Ref_Source!$A:$A,0)),"NOT FOUND")' % r)
            ws.cell(row=r, column=4, value='=IFERROR(INDEX(Ref_Source!$C:$C,MATCH(B%d,Ref_Source!$A:$A,0)),"NOT FOUND")' % r)
            ws.cell(row=r, column=5, value='=IF(C%d="NOT FOUND","ORPHAN","OK")' % r)
            r += 1
    ws.freeze_panes = "A2"; ws.auto_filter.ref = "A1:E%d" % max(r - 1, 2)

    # ---------------- Assumptions_and_RFIs
    ws = S["Assumptions_and_RFIs"]
    header(ws, 1, ["ID", "Category", "Statement or question", "Source ID", "PDF page", "Owner (role)", "Priority", "Status",
                   "Impact on scope", "Linked capabilities", "Related input workbook RFIs"], [13, 18, 70, 12, 9, 26, 9, 10, 50, 36, 22])
    r = 2
    for x in assumptions:
        row = [x["id"], "Assumption", x["text"], x["source"], None, "Lead Estimator", "", "Assumed", "Basis for classification; confirm with Lead Estimator.", "", ""]
        put(ws, r, row)
        r += 1
    for x in rfis:
        rel = sorted({rr for cid in rfi_caps.get(x["id"], []) for rr in next(c for c in caps if c["id"] == cid)["rfi"] if not rr.startswith("OPS-")})
        put(ws, r, [x["id"], x["category"], x["text"], x["source"], None, x["owner"], x["priority"], x["status"], x["impact"],
                    ", ".join(rfi_caps.get(x["id"], [])), ", ".join(rel)])
        r += 1
    NA_ = r - 1
    for rr in range(2, NA_ + 1):
        ws["E%d" % rr] = '=IF(OR(D%d="Not stated",D%d=""),"n/a",IFERROR(INDEX(Ref_Source!$B:$B,MATCH(D%d,Ref_Source!$A:$A,0)),"NOT FOUND"))' % (rr, rr, rr)
        ws["H%d" % rr].fill = INPUT_FILL
    ws.freeze_panes = "C2"; ws.auto_filter.ref = "A1:K%d" % NA_
    add_list(ws, "B2:B200", LIST_REF["Category"]); add_list(ws, "F2:F200", LIST_REF["Role"])
    add_list(ws, "G2:G200", LIST_REF["Priority"]); add_list(ws, "H2:H200", LIST_REF["Status"])
    AR = lambda col: "Assumptions_and_RFIs!$%s$2:$%s$300" % (col, col)

    # ---------------- Map
    ws = S[MAP]
    header(ws, 1, ["Map ID", "Capability ID", "Capability name", "Link type", "Linked ID", "Linked description", "Input workbook decision / status",
                   "EWP of FLOC (input workbook)", "Basis Source ID", "PDF page", "Note", "ID check", "Capability position"],
           [9, 16, 40, 14, 18, 56, 24, 16, 12, 9, 40, 10, 20])
    P0 = None  # filled after EWP_Impact layout is known; placeholder rows are written afterwards
    rows = []
    for c in caps:
        bs = c["src"][0] if c["src"] else ""
        for f in c["floc"]: rows.append((c["id"], "FLOC", f, bs, "FLOC named in the capability's source text"))
        for e in c["ewp_all"]: rows.append((c["id"], "EWP", e, bs, "Derived from linked FLOC mapping" if e not in c["ewp"] else "Added by judgement"))
        for p in c["prop"]: rows.append((c["id"], "EWP-Proposed", p, bs, "Proposed - to confirm"))
        for q in c["rfi"]: rows.append((c["id"], "RFI", q, bs, "Open question or related gap"))
    NM = len(rows) + 1

    # ---------------- EWP_Impact (layout first, so Map can reference it)
    wsE = S["EWP_Impact"]
    linked_ewps = sorted({e for c in caps for e in c["ewp_all"]})
    wsE["A1"] = "EWP impact: existing EWPs affected, proposed new or amended EWPs, and estimation inputs"; wsE["A1"].font = TITLE_FONT
    wsE["A2"] = "Table A. Existing EWPs affected (from the input workbook)"; wsE["A2"].font = BOLD
    A_HDR = 3
    header(wsE, A_HDR, ["EWP ID", "Title (input workbook)", "Owner (role)", "# capabilities linked", "Capabilities", "Coverage assessment", "Recommended action"],
           [16, 46, 28, 12, 50, 40, 44])
    for i, e in enumerate(linked_ewps, A_HDR + 1):
        cl = [c for c in caps if e in c["ewp_all"]]
        clar = [c["id"] for c in cl if c["pos"] == "Clarify"]
        pr = [p for p in props if p["ewp"] == e or e in p["derived"].split("; ")]
        cov = "Systems content present; %d Clarify item(s): %s" % (len(clar), ", ".join(clar)) if clar else "Systems content present; no Clarify items"
        act = "; ".join("%s %s (%s)" % (p["type"], p["id"], p["title"]) for p in pr) or "No change proposed"
        put(wsE, i, [e, '=IFERROR(INDEX(Ref_EWP!$B:$B,MATCH(A%d,Ref_EWP!$A:$A,0)),"NOT FOUND")' % i,
                     '=IFERROR(INDEX(Ref_EWP!$C:$C,MATCH(A%d,Ref_EWP!$A:$A,0)),"NOT FOUND")' % i,
                     '=COUNTIFS(%s!$E$2:$E$1000,A%d,%s!$D$2:$D$1000,"EWP")' % (MAP, i, MAP),
                     ", ".join(c["id"] for c in cl), cov, act])
    A_END = A_HDR + len(linked_ewps)
    B_T = A_END + 2
    wsE.cell(row=B_T, column=1, value="Table B. Proposed new or amended EWPs (Proposed - to confirm)").font = BOLD
    B_HDR = B_T + 1
    hdrB = ["Proposed ID", "Type", "Suggested or existing EWP ID", "Title", "Scope description", "Derived from", "Proposed owner (role)",
            "Delivery method", "Capabilities covered", "Rationale", "Status", "# capabilities linked"]
    header(wsE, B_HDR, hdrB)
    for i, p in enumerate(props, B_HDR + 1):
        put(wsE, i, [p["id"], p["type"], p["ewp"], p["title"], p["scope"], p["derived"], p["owner"], "Proposed - to confirm",
                     ", ".join(c["id"] for c in caps if p["id"] in c["prop"]), p["rationale"], "Proposed - to confirm",
                     '=COUNTIFS(%s!$E$2:$E$1000,A%d,%s!$D$2:$D$1000,"EWP-Proposed")' % (MAP, i, MAP)])
    B_END = B_HDR + len(props)
    add_list(wsE, "B%d:B%d" % (B_HDR + 1, B_END), LIST_REF["EWP change"]); add_list(wsE, "G%d:G%d" % (B_HDR + 1, B_END), LIST_REF["Role"])
    C_T = B_END + 2
    wsE.cell(row=C_T, column=1, value="Table C. Estimation inputs required by capability").font = BOLD
    C_HDR = C_T + 1
    header(wsE, C_HDR, ["Input ID", "Capability ID", "Capability name", "Input required", "Input type", "Availability in ITT pack",
                        "Source ID (capability)", "Linked EWP", "Linked RFIs", "Status"])
    r = C_HDR + 1; n = 1
    for c in caps:
        if c["pos"] in ("Not in ITT",): continue
        for (inp, typ, avail) in c["inputs"]:
            put(wsE, r, ["INP-%03d" % n, c["id"], '=IFERROR(INDEX(%s,MATCH(B%d,%s,0)),"NOT FOUND")' % (cat("name"), r, cat("id")), inp, typ, avail,
                         c["src"][0] if c["src"] else "", ", ".join(c["ewp_all"] + c["prop"]), ", ".join(c["rfi"]), "Not requested"])
            wsE["J%d" % r].fill = INPUT_FILL
            r += 1; n += 1
    C_END = r - 1
    add_list(wsE, "F%d:F%d" % (C_HDR + 1, C_END + 50), LIST_REF["Input availability"]); add_list(wsE, "J%d:J%d" % (C_HDR + 1, C_END + 50), LIST_REF["Input status"])
    for col, w in zip("HIJKL", (24, 30, 22, 50, 14)):
        wsE.column_dimensions[col].width = max(wsE.column_dimensions[col].width or 0, w)
    wsE.freeze_panes = "A4"
    EPROP = "EWP_Impact!$A$%d:$A$%d" % (B_HDR + 1, B_END)
    EINP = "EWP_Impact!$B$%d:$B$%d" % (C_HDR + 1, C_END + 50)

    # ---------------- Map rows
    for i, (cid, lt, lid, bs, note) in enumerate(rows, 2):
        ws.cell(row=i, column=1, value="M-%04d" % (i - 1))
        ws.cell(row=i, column=2, value=cid)
        ws.cell(row=i, column=3, value='=IFERROR(INDEX(%s,MATCH(B%d,%s,0)),"NOT FOUND")' % (cat("name"), i, cat("id")))
        ws.cell(row=i, column=4, value=lt); ws.cell(row=i, column=5, value=lid)
        ws.cell(row=i, column=6, value=(
            '=IF(D{r}="FLOC",IFERROR(INDEX(Ref_FLOC!$B:$B,MATCH(E{r},Ref_FLOC!$A:$A,0)),"NOT FOUND"),'
            'IF(D{r}="EWP",IFERROR(INDEX(Ref_EWP!$B:$B,MATCH(E{r},Ref_EWP!$A:$A,0)),"NOT FOUND"),'
            'IF(D{r}="EWP-Proposed",IFERROR(INDEX(EWP_Impact!$D$%d:$D$%d,MATCH(E{r},EWP_Impact!$A$%d:$A$%d,0)),"NOT FOUND"),'
            'IFERROR(INDEX(Ref_RFI!$B:$B,MATCH(E{r},Ref_RFI!$A:$A,0)),IFERROR(INDEX(%s,MATCH(E{r},%s,0)),"NOT FOUND"))))) ' % (
                B_HDR + 1, B_END, B_HDR + 1, B_END, AR("C"), AR("A"))).format(r=i).strip())
        ws.cell(row=i, column=7, value=(
            '=IF(D{r}="FLOC",IFERROR(INDEX(Ref_FLOC!$E:$E,MATCH(E{r},Ref_FLOC!$A:$A,0)),"NOT FOUND"),'
            'IF(D{r}="RFI",IFERROR(INDEX(Ref_RFI!$D:$D,MATCH(E{r},Ref_RFI!$A:$A,0)),IFERROR(INDEX(%s,MATCH(E{r},%s,0)),"NOT FOUND")),""))' % (AR("H"), AR("A"))).format(r=i))
        ws.cell(row=i, column=8, value='=IF(D{r}="FLOC",IFERROR(INDEX(Ref_FLOC!$F:$F,MATCH(E{r},Ref_FLOC!$A:$A,0)),"NOT FOUND"),"")'.format(r=i))
        ws.cell(row=i, column=9, value=bs)
        ws.cell(row=i, column=10, value='=IF(I{r}="","n/a",IFERROR(INDEX(Ref_Source!$B:$B,MATCH(I{r},Ref_Source!$A:$A,0)),"NOT FOUND"))'.format(r=i))
        ws.cell(row=i, column=11, value=note)
        ws.cell(row=i, column=12, value='=IF(OR(ISNUMBER(SEARCH("NOT FOUND",F{r})),G{r}="NOT FOUND",H{r}="NOT FOUND"),"ORPHAN","OK")'.format(r=i))
        ws.cell(row=i, column=13, value='=IFERROR(INDEX(%s,MATCH(B%d,%s,0)),"NOT FOUND")' % (cat("pos"), i, cat("id")))
        for j in range(1, 14):
            ws.cell(row=i, column=j).border = BORDER
    ws.freeze_panes = "C2"; ws.auto_filter.ref = "A1:M%d" % NM
    add_list(ws, "D2:D1000", LIST_REF["Link type"])
    cf_map(ws, "M2:M1000", POS_COL)
    M = lambda col: "%s!$%s$2:$%s$1000" % (MAP, col, col)

    # ---------------- Interface_Register
    ws = S["Interface_Register"]
    header(ws, 1, ["Interface ID", "Interface type", "Primary capability", "Other capabilities", "From", "To", "Direction", "Data exchanged",
                   "Protocol or standard", "Responsible party", "Source ID", "PDF page", "Other Source IDs", "Linked RFI", "Note"],
           [10, 16, 16, 28, 36, 36, 20, 50, 40, 34, 11, 9, 20, 14, 30])
    for r, i in enumerate(ifaces, 2):
        put(ws, r, [i["id"], i["type"], i["caps"][0], ", ".join(i["caps"][1:]), i["from"], i["to"], i["direction"], i["data"], i["protocol"],
                    i["responsible"], i["sources"][0], None, ", ".join(i["sources"][1:]), i["rfi"], ""])
        ws["L%d" % r] = '=IFERROR(INDEX(Ref_Source!$B:$B,MATCH(K%d,Ref_Source!$A:$A,0)),"NOT FOUND")' % r
    NI = len(ifaces) + 1
    ws.freeze_panes = "B2"; ws.auto_filter.ref = "A1:O%d" % NI
    add_list(ws, "B2:B200", LIST_REF["Interface type"])
    IR = lambda col: "Interface_Register!$%s$2:$%s$200" % (col, col)

    # ---------------- Matrix
    ws = S["Capability_Matrix"]
    ws["A1"] = "Capability matrix: ISA-95 level by domain"; ws["A1"].font = TITLE_FONT
    ws["A2"] = "Counts are formulas on Capability_Catalogue. Primary domain only; other domains are listed in the catalogue."
    doms = lists["domains"]; lvls = lists["levels"]
    ws["A4"] = "Table 1. Capability count"; ws["A4"].font = BOLD
    header(ws, 5, ["ISA-95 level"] + doms + ["Total"], [22, 22, 22, 22, 22, 12])
    for i, lv in enumerate(lvls, 6):
        ws.cell(row=i, column=1, value=lv).fill = fill(LEVEL_COL[lv])
        for j, d in enumerate(doms, 2):
            ws.cell(row=i, column=j, value='=COUNTIFS(%s,$A%d,%s,%s$5)' % (cat("lvl"), i, cat("dom"), L(j)))
        ws.cell(row=i, column=6, value="=SUM(B%d:E%d)" % (i, i))
    t = 6 + len(lvls)
    ws.cell(row=t, column=1, value="Total").font = BOLD
    for j in range(2, 7):
        ws.cell(row=t, column=j, value="=SUM(%s6:%s%d)" % (L(j), L(j), t - 1))
    ws["A%d" % (t + 2)] = "Table 2. Scope position by cell (W within MinRes, O Owner, T Third-party, I Interface only, N Not in ITT, C Clarify; number before the letter)"
    ws["A%d" % (t + 2)].font = BOLD
    header(ws, t + 3, ["ISA-95 level"] + doms)
    for i, lv in enumerate(lvls, t + 4):
        ws.cell(row=i, column=1, value=lv).fill = fill(LEVEL_COL[lv])
        for j, d in enumerate(doms, 2):
            parts = []
            for p, code in POS_CODE.items():
                cnt = 'COUNTIFS(%s,$A%d,%s,%s$%d,%s,"%s")' % (cat("lvl"), i, cat("dom"), L(j), t + 3, cat("pos"), p)
                parts.append('IF(%s>0,%s&"%s ","")' % (cnt, cnt, code))
            ws.cell(row=i, column=j, value="=TRIM(%s)" % "&".join(parts))
    u = t + 4 + len(lvls) + 1
    ws["A%d" % u] = "Table 3. Scope position by ISA-95 level"; ws["A%d" % u].font = BOLD
    header(ws, u + 1, ["ISA-95 level"] + lists["positions"] + ["Total"])
    ws.column_dimensions["G"].width = 22; ws.column_dimensions["H"].width = 14
    for i, lv in enumerate(lvls, u + 2):
        ws.cell(row=i, column=1, value=lv).fill = fill(LEVEL_COL[lv])
        for j, p in enumerate(lists["positions"], 2):
            ws.cell(row=i, column=j, value='=COUNTIFS(%s,$A%d,%s,%s$%d)' % (cat("lvl"), i, cat("pos"), L(j), u + 1))
        ws.cell(row=i, column=8, value="=SUM(B%d:G%d)" % (i, i))
    cf_map(ws, "B%d:G%d" % (u + 1, u + 1), POS_COL)
    for j, p in enumerate(lists["positions"], 2):
        ws.cell(row=u + 1, column=j).fill = fill(POS_COL[p])
    ws["A%d" % (u + 2 + len(lvls) + 1)] = "Level 0 is the physical process; no systems capability is recorded there (assumption OPS-A-09)."

    # ---------------- ISA95_Framework
    ws = S["ISA95_Framework"]
    ws["A1"] = "ISA-95 framework used for classification"; ws["A1"].font = TITLE_FONT
    ws["A2"] = ("ISA-95 (ANSI/ISA-95, IEC 62264) is used as a classification framework only. The ITT does not require ISA-95 compliance. "
                "'Adaptation' marks where the model has been bent to fit mining.")
    ws["A2"].alignment = WRAP
    ws.merge_cells("A2:G2"); ws.row_dimensions[2].height = 32
    r = 4
    ws.cell(row=r, column=1, value="Table 1. Functional hierarchy levels").font = BOLD
    header(ws, r + 1, ["Level", "Name", "ISA-95 meaning", "Typical mining systems", "Winu ITT relevance (Source IDs)", "ISA-95 basis", "# capabilities"], [20, 28, 56, 40, 52, 14, 14])
    for i, row in enumerate(fw["levels"], r + 2):
        put(ws, i, list(row) + ['=COUNTIF(%s,A%d)' % (cat("lvl"), i)])
    cf_map(ws, "A%d:A%d" % (r + 2, r + 1 + len(fw["levels"])), LEVEL_COL)
    r = r + 3 + len(fw["levels"])
    ws.cell(row=r, column=1, value="Table 2. Level 3 operations management activity models").font = BOLD
    header(ws, r + 1, ["Activity model", "Purpose", "Generic activities (each model uses all eight)", "Winu mapping", "ISA-95 basis", "# capabilities"])
    ws.cell(row=r + 1, column=3, value="Generic activities: detailed scheduling, dispatching, execution management, resource management, definition management, data collection, tracking, analysis").alignment = WRAP
    for i, row in enumerate(fw["activities"], r + 2):
        put(ws, i, [row[0], row[1], "Detailed scheduling; dispatching; execution management; resource management; definition management; data collection; tracking; analysis", row[3], row[4], '=COUNTIF(%s,A%d)' % (cat("act"), i)])
    r = r + 3 + len(fw["activities"])
    ws.cell(row=r, column=1, value="Table 3. Information exchanged between levels").font = BOLD
    header(ws, r + 1, ["Direction", "ISA-95 information", "Meaning", "Winu mapping", "ITT status", "Source ID", "Interface or RFI"])
    for i, row in enumerate(fw["flows"], r + 2):
        put(ws, i, row)
    r = r + 3 + len(fw["flows"])
    ws.cell(row=r, column=1, value="Table 4. Mining adaptations of ISA-95").font = BOLD
    header(ws, r + 1, ["Adaptation ID", "Element", "Adaptation", "Rationale", "ISA-95 basis"])
    for i, row in enumerate(fw["adaptations"], r + 2):
        put(ws, i, list(row) + ["Adaptation"])
    r = r + 3 + len(fw["adaptations"])
    ws.cell(row=r, column=1, value="Table 5. Domains").font = BOLD
    header(ws, r + 1, ["Domain", "Meaning in this workbook", "", "", "", "", "# capabilities (primary)"])
    dm = {"Mining": "Pre-strip mining, drill and blast, fleet, haulage, stockpiling, mine water, site-wide infrastructure.",
          "Processing": "Mineral processing plant (MPP) systems and product handling; mostly outside the Contract.",
          "Waste Handling": "Landfill, waste tracking, wastewater, tailings storage facility interfaces.",
          "Logistics": "Inbound transport, materials, fuel, aerodrome and site access."}
    for i, d in enumerate(doms, r + 2):
        put(ws, i, [d, dm[d], "", "", "", "", '=COUNTIF(%s,A%d)' % (cat("dom"), i)])
    r = r + 3 + len(doms)
    ws.cell(row=r, column=1, value="Table 6. Owner architecture items the ITT does not state (all raised as RFIs)").font = BOLD
    header(ws, r + 1, ["Item", "ITT status", "RFI"])
    for i, row in enumerate(fw["arch_not_stated"], r + 2):
        put(ws, i, row)
    ws.freeze_panes = "A4"

    # ---------------- Validation
    ws = S["Validation"]
    header(ws, 1, ["#", "Check", "Result", "Count (should be 0)", "Detail and action"], [5, 62, 10, 12, 80])
    IFid, IFresp, IFcap, IFpg = IR("A"), IR("J"), IR("C"), IR("L")
    pg_chk = lambda rg: "ISNUMBER(%s)*(((%s<1)+(%s>%s))>0)" % (rg, rg, rg, PG)
    checks = [
     ("Capabilities with no Source ID or page (excluding Not in ITT)",
      '=SUMPRODUCT((%s<>"")*(%s<>"Not in ITT")*(((%s="")+(%s=""))>0))' % (cat("id"), cat("pos"), cat("src"), cat("pages")), "Add the Source ID and PDF page, or set the position to Clarify."),
     ("Within-scope capabilities with no linked FLOC or EWP",
      '=COUNTIFS(%s,"Within MinRes scope",%s,0,%s,0,%s,0)' % (cat("pos"), cat("nfloc"), cat("newp"), cat("nprop")), "Link a FLOC or EWP in the config."),
     ("Clarify capabilities with no linked RFI", '=COUNTIFS(%s,"Clarify",%s,0)' % (cat("pos"), cat("nrfi")), "Add an RFI in the config and link it."),
     ("Capabilities with no ISA-95 level, domain or activity model",
      '=SUMPRODUCT((%s<>"")*(((%s="")+(%s="")+(%s=""))>0))' % (cat("id"), cat("lvl"), cat("dom"), cat("act")), "Complete the classification."),
     ("Duplicate capability IDs", '=SUMPRODUCT((%s<>"")*(COUNTIF(%s,%s)>1))' % (cat("id"), cat("id"), cat("id")), "IDs must be unique."),
     ("Orphan FLOC references (not in input workbook)", '=COUNTIFS(%s,"FLOC",%s,"ORPHAN")' % (M("D"), M("L")), "Reconciliation: FLOC IDs must exist in the input workbook."),
     ("Orphan EWP references (not in input workbook)", '=COUNTIFS(%s,"EWP",%s,"ORPHAN")' % (M("D"), M("L")), "Reconciliation: EWP IDs must exist in the input workbook."),
     ("Orphan proposed EWP references (not in EWP_Impact Table B)", '=COUNTIFS(%s,"EWP-Proposed",%s,"ORPHAN")' % (M("D"), M("L")), "Add the proposal to the config."),
     ("Orphan RFI references (not in input RFI_Log or Assumptions_and_RFIs)", '=COUNTIFS(%s,"RFI",%s,"ORPHAN")' % (M("D"), M("L")), "Add the RFI."),
     ("Orphan Source IDs (capabilities)", '=COUNTIF(Capability_Sources!$E$2:$E$1000,"ORPHAN")', "Source ID must exist in the FLOC workbook Source_Register."),
     ("Orphan Source IDs (interfaces, assumptions and RFIs)",
      '=SUMPRODUCT((%s<>"")*(%s="NOT FOUND"))+SUMPRODUCT((%s<>"")*(%s="NOT FOUND"))' % (IR("K"), IFpg, AR("A"), AR("E")), "Source ID must exist in Source_Register."),
     ("Page numbers outside the ITT page count",
      "=SUMPRODUCT(%s)+SUMPRODUCT(%s)+SUMPRODUCT(%s)" % (pg_chk("Capability_Sources!$C$2:$C$1000"), pg_chk(IFpg), pg_chk(AR("E"))), "PDF page must be between 1 and the ITT page count (Lists sheet)."),
     ("Interfaces with an unassigned responsible party", '=COUNTIF(%s,"Unassigned")+SUMPRODUCT((%s<>"")*(%s=""))' % (IFresp, IFid, IFresp),
      "FAILs here are genuine ITT gaps (central control system and weighbridge ownership); see OPS-RFI-02 and OPS-RFI-11."),
     ("Interface capability references not in the catalogue", '=SUMPRODUCT((%s<>"")*(COUNTIF(%s,%s)=0))' % (IFcap, cat("id"), IFcap), "Fix the capability ID."),
     ("Duplicate interface IDs", '=SUMPRODUCT((%s<>"")*(COUNTIF(%s,%s)>1))' % (IFid, IFid, IFid), "IDs must be unique."),
     ("Reconciliation: extract row counts differ from the input workbook counts recorded at build",
      "=(COUNTA(Ref_FLOC!$A$2:$A$2000)<>%s)+(COUNTA(Ref_EWP!$A$2:$A$500)<>%s)+(COUNTA(Ref_RFI!$A$2:$A$2000)<>%s)" % (NF, NE, NR), "Re-run the build against the current input workbook."),
     ("Within-scope capabilities linked to a FLOC the input workbook excludes", '=COUNTIFS(%s,"Within MinRes scope",%s,"FLOC",%s,"Exclude")' % (M("M"), M("D"), M("G")), "Review the FLOC decision or the capability position."),
     ("Within-scope capabilities with no estimation input listed", '=SUMPRODUCT((%s="Within MinRes scope")*(COUNTIF(%s,%s)=0))' % (cat("pos"), EINP, cat("id")), "Add inputs in EWP_Impact Table C."),
     ("Duplicate capability-to-link rows", '=SUMPRODUCT((%s<>"")*(COUNTIFS(%s,%s,%s,%s,%s,%s)>1))' % (M("B"), M("B"), M("B"), M("D"), M("D"), M("E"), M("E")), "Remove duplicate links."),
     ("Values outside the data validation lists (position, level, domain, delivery, confidence)",
      "=" + "+".join('SUMPRODUCT((%s<>"")*(COUNTIF(%s,%s)=0))' % (cat(k), ref[1:], cat(k)) for k, ref in
                     (("pos", LIST_REF["Position"]), ("lvl", LIST_REF["ISA-95 level"]), ("dom", LIST_REF["Domain"]), ("dt", LIST_REF["Delivery type"]), ("conf", LIST_REF["Confidence"]))),
      "Use values from the Lists sheet."),
     ("Assumptions and RFIs (not assumptions) missing Source ID, page or owner",
      '=SUMPRODUCT((%s<>"")*(%s<>"Assumption")*(((%s="")+(%s="")+(%s="n/a")+(%s=""))>0))' % (AR("A"), AR("B"), AR("D"), AR("E"), AR("E"), AR("F")), "Complete the row."),
     ("Duplicate assumption or RFI IDs", '=SUMPRODUCT((%s<>"")*(COUNTIF(%s,%s)>1))' % (AR("A"), AR("A"), AR("A")), "IDs must be unique."),
     ("Not in ITT capabilities that carry a FLOC, EWP or MinRes delivery type",
      '=COUNTIFS(%s,"Not in ITT",%s,">0")+COUNTIFS(%s,"Not in ITT",%s,">0")+COUNTIFS(%s,"Not in ITT",%s,"<>None (not MinRes)")' % (cat("pos"), cat("nfloc"), cat("pos"), cat("newp"), cat("pos"), cat("dt")), "Not in ITT rows must have no links and delivery type None."),
     ("Owner or third-party capabilities with a MinRes delivery type",
      '=COUNTIFS(%s,"Owner scope",%s,"<>None (not MinRes)")+COUNTIFS(%s,"Third-party scope",%s,"<>None (not MinRes)")' % (cat("pos"), cat("dt"), cat("pos"), cat("dt")), "Set delivery type to None (not MinRes)."),
    ]
    for i, (name, f, act) in enumerate(checks, 2):
        put(ws, i, [i - 1, name, '=IF(D%d=0,"PASS","FAIL")' % i, f, act])
    NV = len(checks) + 1
    ws.freeze_panes = "A2"; ws.auto_filter.ref = "A1:E%d" % NV
    cf_map(ws, "C2:C%d" % NV, {"PASS": "C6EFCE", "FAIL": "FFC7CE"})

    # ---------------- Dashboard
    ws = S["Dashboard"]
    ws.column_dimensions["A"].width = 52
    for c_ in "BCD": ws.column_dimensions[c_].width = 18
    ws["A1"] = "Winu - MinRes operational systems capability scope dashboard"; ws["A1"].font = TITLE_FONT
    ws["A2"] = "All figures are formulas on the sheets in this workbook."
    r = 4

    def block(title, labels, fn, total_label="Total", pct=True, ref_total=None):
        nonlocal r
        ws.cell(row=r, column=1, value=title).font = BOLD
        ws.cell(row=r, column=2, value="Count").font = BOLD
        if pct: ws.cell(row=r, column=3, value="% of capabilities").font = BOLD
        start = r + 1
        for i, lab in enumerate(labels, start):
            ws.cell(row=i, column=1, value=lab)
            ws.cell(row=i, column=2, value=fn(i, lab))
        end = start + len(labels) - 1
        ws.cell(row=end + 1, column=1, value=total_label).font = BOLD
        ws.cell(row=end + 1, column=2, value="=SUM(B%d:B%d)" % (start, end))
        if pct:
            for i in range(start, end + 2):
                ws.cell(row=i, column=3, value='=IF($B$%d=0,0,B%d/$B$%d)' % (end + 1, i, end + 1)).number_format = "0%"
        r = end + 3
        return start, end

    ws.cell(row=r, column=1, value="Input workbook review (from Ref sheets)").font = BOLD; r += 1
    inp = [("FLOCs", "=COUNTA(Ref_FLOC!$A$2:$A$2000)"), ("Leaf FLOCs", '=COUNTIF(Ref_FLOC!$C$2:$C$2000,"Y")'),
           ("Decision: Price", '=COUNTIF(Ref_FLOC!$E$2:$E$2000,"Price")'), ("Decision: Price as Provisional Sum", '=COUNTIF(Ref_FLOC!$E$2:$E$2000,"Price as Provisional Sum")'),
           ("Decision: Price as Option or Alternative", '=COUNTIF(Ref_FLOC!$E$2:$E$2000,"Price as Option or Alternative")'),
           ("Decision: Exclude", '=COUNTIF(Ref_FLOC!$E$2:$E$2000,"Exclude")'), ("Decision: Clarify", '=COUNTIF(Ref_FLOC!$E$2:$E$2000,"Clarify")'),
           ("EWPs", "=COUNTA(Ref_EWP!$A$2:$A$500)"), ("Open RFIs and gaps (input workbook)", '=COUNTIF(Ref_RFI!$D$2:$D$2000,"Open")'),
           ("High-priority open RFIs and gaps (input workbook)", '=COUNTIFS(Ref_RFI!$D$2:$D$2000,"Open",Ref_RFI!$C$2:$C$2000,"High")'),
           ("FLOCs linked to at least one capability", '=SUMPRODUCT((COUNTIFS(%s,Ref_FLOC!$A$2:$A$600,%s,"FLOC")>0)*1)' % (M("E"), M("D"))),
           ("EWPs linked to at least one capability", '=SUMPRODUCT((COUNTIFS(%s,Ref_EWP!$A$2:$A$100,%s,"EWP")>0)*1)' % (M("E"), M("D")))]
    for lab, f in inp:
        ws.cell(row=r, column=1, value=lab); ws.cell(row=r, column=2, value=f); r += 1
    r += 1
    block("Capabilities by MinRes Scope Position", lists["positions"], lambda i, l: '=COUNTIF(%s,A%d)' % (cat("pos"), i))
    block("Capabilities by ISA-95 level", lists["levels"], lambda i, l: '=COUNTIF(%s,A%d)' % (cat("lvl"), i))
    block("Capabilities by primary domain", lists["domains"], lambda i, l: '=COUNTIF(%s,A%d)' % (cat("dom"), i))
    block("Capabilities by confidence", lists["confidence"], lambda i, l: '=COUNTIF(%s,A%d)' % (cat("conf"), i))
    ws.cell(row=r, column=1, value="Open items").font = BOLD; r += 1
    for lab, f in [("OPS RFIs and ambiguities open (this workbook)", '=COUNTIFS(%s,"Open")' % AR("H")),
                   ("OPS RFIs open, High priority", '=COUNTIFS(%s,"Open",%s,"High")' % (AR("H"), AR("G"))),
                   ("Assumptions recorded", '=COUNTIF(%s,"Assumption")' % AR("B")),
                   ("Interfaces recorded", '=COUNTA(%s)' % IFid), ("Interfaces with unassigned responsible party", '=COUNTIF(%s,"Unassigned")' % IFresp),
                   ("Proposed new or amended EWPs", '=COUNTA(%s)' % EPROP),
                   ("Capabilities with no existing EWP (in scope, interface or Clarify)", '=COUNTIF(%s,"No EWP")' % cat("flag")),
                   ("Validation checks failing", '=COUNTIF(Validation!$C$2:$C$%d,"FAIL")' % NV)]:
        ws.cell(row=r, column=1, value=lab); ws.cell(row=r, column=2, value=f); r += 1
    r += 1
    ws.cell(row=r, column=1, value="Capabilities with no existing EWP (first 20)").font = BOLD
    ws.cell(row=r, column=2, value="Position").font = BOLD; ws.cell(row=r, column=3, value="Proposed EWP").font = BOLD; r += 1
    for n in range(1, 21):
        m = 'MATCH(%d,%s,0)' % (n, cat("rank"))
        ws.cell(row=r, column=1, value='=IFERROR(INDEX(%s,%s)&" - "&INDEX(%s,%s),"")' % (cat("id"), m, cat("name"), m))
        ws.cell(row=r, column=2, value='=IFERROR(INDEX(%s,%s),"")' % (cat("pos"), m))
        ws.cell(row=r, column=3, value='=IFERROR(INDEX(%s,%s),"")' % (cat("prop"), m))
        r += 1
    cf_map(ws, "B1:B200", POS_COL)

    # ---------------- README
    ws = S["README"]
    ws.column_dimensions["A"].width = 26; ws.column_dimensions["B"].width = 120
    dec = {}
    for v in flocs.values(): dec[v["decision"]] = dec.get(v["decision"], 0) + 1
    rows = [
     ("Winu - MinRes operational systems capability scope (ISA-95)", None),
     ("Purpose", "Defines which operational systems capabilities fall within the MinRes quotation, classified on ISA-95 levels and four domains, and links each capability to the FLOCs and estimation work packages (EWPs) in the quotation scope workbook. It holds no prices."),
     ("Tender role", "MinRes is the Australian Contractor bidding to the Owner (Rio Tinto, called 'Company' in the ITT) under the EPC ITT pack."),
     ("Input files", "%s (FLOCs, EWPs, RFIs); %s (Source_Register: Source IDs and PDF pages). Neither was altered." % (a.scope_workbook, a.floc_workbook)),
     ("Version / date", "%s / %s" % (meta["version"], today)),
     ("Currency", "AUD if any amounts appear later. No amounts are held."),
     ("Input at build", "%d FLOCs; decisions %s; %d EWPs; %d RFI and gap rows." % (len(flocs), ", ".join("%s %d" % (k, v) for k, v in sorted(dec.items())), len(ewps), len(rfi_rows))),
     ("ISA-95 explained", "ISA-95 (ANSI/ISA-95, IEC 62264) models how enterprise (IT, information technology) systems connect to plant control (OT, operations technology). Level 0 physical process; Level 1 sensing and actuation; Level 2 supervisory control (PLC programmable logic controller, DCS distributed control system, SCADA supervisory control and data acquisition, HMI human-machine interface); Level 3 manufacturing operations management (MOM, also called MES manufacturing execution system) with production, maintenance, quality and inventory activity models; Level 4 business planning and logistics (ERP enterprise resource planning). Other terms: LIMS laboratory information management system; CMMS computerised maintenance management system; FMS fleet management system; NPI non-process infrastructure; MSA mine services area; MPP mineral processing plant."),
     ("ISA-95 status", "ISA-95 is a classification framework here. The ITT does not mention it or require compliance. Mining adaptations are marked 'Adaptation' (see ISA95_Framework)."),
     ("Key finding", "The Contract is construction-led with limited pre-strip mining operation. The ITT states an FMS, temporary communications, materials control, fuel monitoring, a field laboratory and installation of site communications, data centres and NPI instrumentation. It excludes process plant EI&C, backbone fibre, CCTV and access control, and permanent laboratory equipment, and does not state SCADA, DCS, HMI, historian, LIMS, CMMS, alarm management, time synchronisation or an Owner systems architecture."),
     ("Timing caution", "The tender closing date (07/10/2026 4:00pm AWST) and RFI cut-off (04/10/2026) have passed (OPS-A-07). Treat OPS RFIs as qualifications or stated assumptions unless an extension is confirmed."),
     ("Sheets", "Dashboard; ISA95_Framework; Capability_Catalogue; Capability_to_FLOC_EWP_Map (one row per link); Capability_Matrix; Interface_Register; EWP_Impact; Assumptions_and_RFIs; Validation; supporting: Capability_Sources, Lists, Ref_FLOC, Ref_EWP, Ref_Source, Ref_RFI (extracts of the input workbooks used by the formulas)."),
     ("Assumptions", "See Assumptions_and_RFIs (OPS-A-01 onward). Scope positions are 'Proposed - to confirm'. Confidence: High explicit in ITT; Medium implied; Low assumed."),
     ("Re-running", "Edit config/winu_ops_config.json in the minres-operational-systems-capability-scope skill and re-run the build script (see SKILL.md). Edits made directly to this workbook's catalogue, map, interfaces or RFIs are replaced on a re-run; yellow cells are for tracking only."),
     ("Colour legend", None),
    ]
    for i, (k, v) in enumerate(rows, 1):
        ws.cell(row=i, column=1, value=k).font = BOLD if i > 1 else TITLE_FONT
        if v: ws.cell(row=i, column=2, value=v).alignment = WRAP
        ws.cell(row=i, column=1).alignment = WRAP
    i = len(rows) + 1
    for lv, hx in LEVEL_COL.items():
        ws.cell(row=i, column=1, value=lv).fill = fill(hx); ws.cell(row=i, column=2, value="ISA-95 level"); i += 1
    for p, hx in POS_COL.items():
        ws.cell(row=i, column=1, value=p).fill = fill(hx); ws.cell(row=i, column=2, value="MinRes Scope Position"); i += 1
    ws.cell(row=i, column=1, value="Yellow").fill = INPUT_FILL; ws.cell(row=i, column=2, value="Tracking cell for the estimator (status)"); i += 1
    ws.cell(row=i, column=1, value="Grey header").fill = HDR_FILL; ws.cell(row=i, column=2, value="Column headers")

    for n in names:
        S[n].sheet_view.zoomScale = 90
    os.makedirs(os.path.dirname(a.output), exist_ok=True)
    wb.save(a.output)
    print("Wrote", a.output, "| capabilities", len(caps), "| map rows", len(rows) if False else NM - 1, "| interfaces", len(ifaces))

    # Independent recomputation of key dashboard counts for the build log
    import collections
    print("By position:", dict(collections.Counter(c["pos"] for c in caps)))
    print("By level:", dict(collections.Counter(c["lvl"] for c in caps)))
    noewp = [c["id"] for c in caps if c["pos"] in ("Within MinRes scope", "Interface only", "Clarify") and not c["ewp_all"]]
    print("No existing EWP:", noewp)


if __name__ == "__main__":
    main()
