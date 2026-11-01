#!/usr/bin/env python3
"""Build the Winu CCLAS (Datamine LIMS) module applicability workbook (Excel).

Layout follows input/Vendor/Wenco/Winu_Wenco_Equipment_Module_Matrix.xlsx (matrix sheet, detail sheet,
module catalogue, notes). Laboratory instrument types replace Wenco equipment types; CCLAS functional
modules replace Wenco modules.

Inputs:
  - the Winu laboratory instrumentation workbook (Instrument_x_Stream sheet) for instrument refs, tiers,
    names and peak quantities (cached Sizing values), and Instrument_Detail for make/class and room;
  - input/Vendor/Datamine (CCLAS)/LIMS.drawio for the CCLAS process stages and room contents.
No CCLAS product-capability document is in the pack, so the module list is derived from the LIMS.drawio
stages plus standard LIMS functions, and every rating is judgement (see Notes sheet).

Run: python -I -X utf8 winu_cclas_module_matrix_xlsx.py --lab <lab xlsx> --output <xlsx> [--force]
"""
import argparse
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as CL

NAVY = "1F3864"
HDR = PatternFill("solid", fgColor=NAVY)
WHITE = Font(bold=True, color="FFFFFF")
BOLD = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
TIER_FILL = {
    "1 Core analytical": PatternFill("solid", fgColor="DDEBF7"),
    "2 Preparation / bench": PatternFill("solid", fgColor="E2EFDA"),
    "3 Support (tracking only)": PatternFill("solid", fgColor="F2F2F2"),
    "Excluded": PatternFill("solid", fgColor="D9D9D9"),
}
P, O = "●", "○"

# ---- matrix columns (E..P): letter -> (group, group colour, module, description, coverage basis) -----
MODULES = [
    ("E", "Core", "1F3864", "CCLAS core (LIMS application and database)",
     "Sample, batch and result records; users, methods and specifications; the single database all other modules write to.",
     "LIMS.drawio: Mine - Comms Room (CCLAS APP server, CCLAS DB server)"),
    ("F", "Intake and custody", "2E75B6", "Sample receipt and registration",
     "Receive field samples, weigh, assign sample IDs, record source (pit, stream, drill hole) and job.",
     "LIMS.drawio: AMS Sample Receipt and AMS Sample Registration stages (shown as Scott Automation)"),
    ("G", "Intake and custody", "2E75B6", "Barcode labelling and chain of custody",
     "Barcode / label printing and scan-based hand-over tracking from room to room.",
     "LIMS.drawio: barcode scanners in every room, Zebra printers in XRF and Control rooms"),
    ("H", "Intake and custody", "2E75B6", "Sample storage and retention",
     "Location, retention period and disposal of rejects and pulps. Inferred; not drawn in LIMS.drawio.",
     "Inferred (standard LIMS function). Winu needs 180 m2 sample store: Space_Check in the laboratory workbook"),
    ("I", "Preparation", "548235", "Prep tracking - dry, split, composite",
     "Track drying, splitting and compositing steps and weights against the sample.",
     "LIMS.drawio: ADF Drying Splitting Compositing stage (shown as Scott Automation)"),
    ("J", "Preparation", "548235", "Prep tracking - crush and pulverise",
     "Track crushing and pulverising steps, product size and pulp packets against the sample.",
     "LIMS.drawio: BCF Sample Crushing & Pulverising stage (shown as Scott Automation)"),
    ("K", "Analysis", "BF8F00", "Balance and scale integration",
     "Direct weight capture from balances and platform scales into the sample or batch record.",
     "LIMS.drawio: Ohaus Explorer, Alsto platform scales and HV-15KCP in prep, mine prep and fusion rooms"),
    ("L", "Analysis", "BF8F00", "Instrument result capture",
     "Automatic transfer of results from analytical instruments into CCLAS (file or serial interface per instrument).",
     "LIMS.drawio: XRF and TGA rooms with LIMS computers. Winu analysers (ICP, AAS, Leco, Hg) are not drawn: interfaces to confirm"),
    ("M", "Analysis", "BF8F00", "Taskman (worklists and manual entry)",
     "Task and worklist management for bench work, plus manual result and batch entry where no instrument interface exists.",
     "LIMS.drawio: CCLAS Taskman computer linked to the Mine - Comms Room; Manual Fusion Room workstation"),
    ("N", "Quality and output", "C00000", "Data processing and quality control",
     "Apply QC rules (CRM, blank, duplicate, drift), validate and release results.",
     "LIMS.drawio: Data Processing and Quality Control stage"),
    ("O", "Quality and output", "C00000", "Reporting and results delivery",
     "Certificates, batch reports and result release to requesters.",
     "LIMS.drawio: Reporting and Results Delivery stage"),
    ("P", "Data", "7030A0", "Automated data exchange (interfaces)",
     "Machine-to-machine exchange with mine and plant systems (grade control, geology database, plant information).",
     "LIMS.drawio: Automated Data Exchange link (endpoints not drawn)"),
]
MCOLS = [m[0] for m in MODULES]
MNAME = {m[0]: m[3] for m in MODULES}

# ref -> (primary letters, optional letters, rationale, drawio reference)
RATE = {
    "A1": ("EGM", "N", "Manual batch: charge weighed, fused and tracked by label and worklist; the Au result arrives later from the AAS finish.", "Manual Fusion Room pattern (workstation, scanners, balance)"),
    "A2": ("EGM", "N", "Manual batch step after fusion; tracked by label and worklist, no result of its own.", "Manual Fusion Room pattern"),
    "A3": ("EGLMNO", "P", "Au finish and sequential Cu results flow from the autosampler into CCLAS.", "No AAS drawn; XRF room is the analyser pattern"),
    "A4": ("EGM", "N", "Digest batches are manual: rack and batch tracking by worklist. No result of its own.", ""),
    "A5": ("EGLMNO", "P", "Main Cu multi-element analyser; replaces the XRF in the reference lab. Needs a CCLAS instrument interface.", "XRF Room (3 XRF) is the iron-ore analogue; not reused"),
    "A6": ("EGLMNO", "P", "Penalty and trace element results; same interface pattern as ICP-OES.", ""),
    "A7": ("EGLMNO", "P", "Total and sulphide S and C for ARD classification; instrument export to CCLAS.", ""),
    "A8": ("EGLMNO", "P", "Hg result for concentrate settlement; low volume.", ""),
    "A9": ("EGMNO", "L", "NAG / ANC and pH / EC are often keyed in; automatic capture is optional per meter.", ""),
    "A10": ("EGLMNO", "P", "Size distribution results exported from the analyser software.", ""),
    "A11": ("EGKM", "N", "Weights feed digest and fusion charges; direct capture avoids transcription errors.", "Ohaus Explorer in fusion, mine prep and Scott PC rooms"),
    "A12": ("EGKM", "N", "Au prill weights; direct capture.", ""),
    "A13": ("EFGK", "IM", "Receipt weights and split weights; platform scales sit at registration.", "Alsto platform scales, HV-15KCP in Sample Preparation Room"),
    "A14": ("EGM", "KL", "Screen weights usually keyed or taken from a balance; no instrument result.", ""),
    "B1": ("EGI", "M", "Drying stage tracked per rack; moisture by mass loss uses the balance.", "ADF Drying Splitting Compositing stage"),
    "B2": ("EGJ", "M", "Crush stage tracked per sample.", "BCF Sample Crushing & Pulverising stage"),
    "B3": ("EGJ", "M", "Second crush stage tracked per sample.", "BCF stage"),
    "B4": ("EGI", "JM", "Splitting is part of the dry, split, composite stage; split weights recorded.", "ADF stage"),
    "B5": ("EGJ", "M", "Pulverise stage; pulp packet label printed here.", "BCF stage"),
    "M1": ("", "EGM", "Bench flotation is not a LIMS function; products come back as registered samples for assay.", ""),
    "M2": ("", "EGM", "Grind calibration data usually kept by the metallurgist; optional worklist entry.", ""),
    "M3": ("", "EGM", "Filter products re-enter as samples; no CCLAS function on the filter itself.", ""),
    "M4": ("", "EGM", "Gravity concentrate and tail register as new samples.", ""),
    "S1": ("EFGHIJM", "K", "Scan at every hand-over; the CCLAS traceability backbone.", "11 scanners across 6 rooms (1 to 4 per room)"),
    "S2": ("EFGH", "IJ", "Labels at registration and pulp packets; Zebra class.", "2 Zebra printers (XRF room, Control Room)"),
    "S3": ("EFMNO", "GHIJKL", "Client terminals for registration, worklists, QC review and reports.", "14 computers across 8 locations"),
    "S4": ("EFGHIJKLMNOP", "", "Hosts every module: CCLAS app and DB servers plus the Taskman host.", "1 CCLAS app server, 1 CCLAS DB server, Taskman computer"),
}
# Support items with no CCLAS function are left off the matrix and listed on Notes
NOT_CCLAS = ["B6", "S5", "S6", "S7", "S8"]

TX_REASON = {
    "X1": "Excluded: Winu uses fire assay and 4-acid ICP / AAS, not XRF. CCLAS XRF interface not needed.",
    "X2": "Excluded: not used for Cu-Au grade control.",
    "X3": "Excluded: only needed for XRF fusion beads (the reference lab's Fusion Bead Preparation stage).",
    "X4": "Excluded: loss on ignition is an iron-ore product test (the reference lab's TGA stage).",
    "X5": "Excluded: Scott Automation robotics run the reference lab's receipt, registration, ADF and BCF stages. Winu prep is manual, so CCLAS must track manual prep (columns I and J).",
    "X6": "Excluded: strength testing stays with the contractor construction laboratory.",
}


def hdr(c, fill=HDR):
    c.font = WHITE
    c.fill = fill
    c.alignment = CENTER


def load_instruments(lab):
    wv = load_workbook(lab, data_only=True)
    qty = {}
    tier = {}
    name = {}
    for r in wv["Instrument_x_Stream"].iter_rows(min_row=6, values_only=True):
        if r[0]:
            qty[r[0]] = r[3]
            tier[r[0]] = r[1]
            name[r[0]] = r[2]
    det = {}
    for r in wv["Instrument_Detail"].iter_rows(min_row=2, values_only=True):
        if r[0]:
            det[r[0]] = {"make": r[3], "room": r[5]}
    return qty, tier, name, det


def names(rows, letter, mark):
    return "; ".join(r["name"] for r in rows if (mark == P and letter in r["pri"]) or (mark == O and letter in r["opt"]))


def build(path, lab):
    qty, tier, name, det = load_instruments(lab)
    rows = []
    for ref in name:
        if ref in NOT_CCLAS:
            continue
        pri, opt, why, dref = RATE.get(ref, ("", "", TX_REASON.get(ref, ""), ""))
        rows.append({"ref": ref, "tier": tier[ref], "name": name[ref], "qty": qty[ref],
                     "make": (det.get(ref) or {}).get("make") or "", "room": (det.get(ref) or {}).get("room") or "",
                     "pri": pri, "opt": opt, "why": why, "dref": dref})
    n = len(rows)
    first, last = 6, 5 + n

    wb = Workbook()
    ws = wb.active
    ws.title = "Instrument_x_Module"
    de = wb.create_sheet("Instrument_Detail")
    ca = wb.create_sheet("Module_Catalogue")
    nt = wb.create_sheet("Notes")

    # ---------------- matrix -----------------
    ws["A1"] = "Winu - CCLAS (Datamine LIMS) module applicability by laboratory instrument type"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = ("● = primary fit   ○ = optional / conditional   blank = not applicable. Instrument types, tiers and quantities from "
                "Winu_Lab_Instrumentation_Requirements.xlsx (ASSUMPTION-based sizing); module list derived from LIMS.drawio stages and standard LIMS "
                "functions (no CCLAS capability document in the pack, so ratings are judgement). Cu-Au methods (fire assay, ICP, AAS, Leco) replace the "
                "iron-ore XRF / TGA / fusion-bead methods drawn in LIMS.drawio; those instruments (X1 to X5) are excluded and carry no marks.")
    ws.merge_cells("A2:R2")
    ws["A2"].alignment = WRAP
    ws.row_dimensions[2].height = 48
    ws.row_dimensions[5].height = 62
    for col, grp, colr, mod, _, _ in MODULES:
        hdr(ws[f"{col}4"], PatternFill("solid", fgColor=colr))
        ws[f"{col}4"] = grp
        hdr(ws[f"{col}5"])
        ws[f"{col}5"] = mod
    for col, h in zip("ABCD", ["Ref", "Instrument tier", "Instrument", "Peak qty"]):
        hdr(ws[f"{col}5"])
        ws[f"{col}5"] = h
    hdr(ws["Q5"])
    ws["Q5"] = "Modules (primary)"
    hdr(ws["R5"])
    ws["R5"] = "Modules (incl. optional)"
    for i, rw in enumerate(rows):
        r = first + i
        ws.cell(r, 1, rw["ref"])
        ws.cell(r, 2, rw["tier"])
        ws.cell(r, 3, rw["name"])
        ws.cell(r, 4, rw["qty"])
        for c in range(1, 5):
            ws.cell(r, c).fill = TIER_FILL[rw["tier"]]
        for col in MCOLS:
            mark = P if col in rw["pri"] else (O if col in rw["opt"] else None)
            c = ws[f"{col}{r}"]
            c.value = mark
            c.alignment = Alignment(horizontal="center")
        ws[f"Q{r}"] = f'=COUNTIF(E{r}:P{r},"{P}")'
        ws[f"R{r}"] = f"=COUNTA(E{r}:P{r})"
    s = last + 2
    ws.cell(s, 3, "Instrument types using module (count)").font = BOLD
    ws.cell(s + 1, 3, "Units fitted - primary fit (peak qty)").font = BOLD
    ws.cell(s + 2, 3, "Units fitted - primary + optional (peak qty)").font = BOLD
    for col in MCOLS:
        rng = f"{col}{first}:{col}{last}"
        q = f"$D{first}:$D{last}"
        ws[f"{col}{s}"] = f"=COUNTA({rng})"
        ws[f"{col}{s + 1}"] = f'=SUMIF({rng},"{P}",{q})'
        ws[f"{col}{s + 2}"] = f'=SUMIF({rng},"{P}",{q})+SUMIF({rng},"{O}",{q})'
        for k in range(3):
            ws[f"{col}{s + k}"].alignment = Alignment(horizontal="center")
    ws.cell(s + 4, 3, ("Quantities are the laboratory workbook's selected peak counts (ASSUMPTION-based). Unit totals mix instruments and devices "
                       "(for example scanners and workstations) so read them as relative weight, not a licence count. Excluded rows X1 to X5 carry no "
                       "quantity and no marks; X6 likewise. Items with no CCLAS function (" + ", ".join(f"{r} {name[r]}" for r in NOT_CCLAS) + ") are off the matrix."))
    ws.conditional_formatting.add(f"E{first}:P{last}", CellIsRule(operator="equal", formula=[f'"{P}"'], fill=PatternFill("solid", start_color="C6E0B4", end_color="C6E0B4")))
    ws.conditional_formatting.add(f"E{first}:P{last}", CellIsRule(operator="equal", formula=[f'"{O}"'], fill=PatternFill("solid", start_color="FFF2CC", end_color="FFF2CC")))
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 46
    ws.column_dimensions["D"].width = 9
    for col in MCOLS:
        ws.column_dimensions[col].width = 15
    ws.column_dimensions["Q"].width = 12
    ws.column_dimensions["R"].width = 12
    ws.freeze_panes = "E6"

    # ---------------- detail -----------------
    heads = ["Ref", "Instrument tier", "Instrument", "Make / class", "Peak qty", "Room", "Primary modules",
             "Optional modules", "LIMS.drawio reference", "Applicability rationale"]
    for i, h in enumerate(heads):
        hdr(de.cell(1, 1 + i))
    for i, rw in enumerate(rows):
        r = 2 + i
        vals = [rw["ref"], rw["tier"], rw["name"], rw["make"], rw["qty"], rw["room"],
                "; ".join(MNAME[c] for c in MCOLS if c in rw["pri"]),
                "; ".join(MNAME[c] for c in MCOLS if c in rw["opt"]),
                rw["dref"], rw["why"]]
        for j, v in enumerate(vals):
            c = de.cell(r, 1 + j, v)
            c.alignment = WRAP
    for col, w in zip("ABCDEFGHIJ", [6, 22, 34, 30, 9, 26, 60, 50, 44, 70]):
        de.column_dimensions[col].width = w
    de.freeze_panes = "D2"
    de.auto_filter.ref = f"A1:J{1 + n}"

    # ---------------- catalogue -----------------
    for i, h in enumerate(["Group", "CCLAS module / function", "What it does", "Coverage basis", "Instrument types - primary", "Instrument types - optional"]):
        hdr(ca.cell(1, 1 + i))
    for i, (col, grp, _, mod, what, basis) in enumerate(MODULES):
        r = 2 + i
        for j, v in enumerate([grp, mod, what, basis, names(rows, col, P), names(rows, col, O)]):
            ca.cell(r, 1 + j, v).alignment = WRAP
    for col, w in zip("ABCDEF", [18, 40, 60, 62, 70, 70]):
        ca.column_dimensions[col].width = w
    ca.freeze_panes = "C2"

    # ---------------- notes -----------------
    notes = [
        ("Purpose", "Maps each laboratory instrument type in the Winu laboratory instrumentation workbook to the CCLAS (Datamine LIMS) functions that apply to it, so the LIMS scope and interface list can be sized."),
        ("Sources", "input/Vendor/Datamine (CCLAS)/Winu_Lab_Instrumentation_Requirements.xlsx (instruments, tiers, peak quantities, rooms); input/Vendor/Datamine (CCLAS)/LIMS.drawio (CCLAS stages, rooms, servers, Taskman); layout from input/Vendor/Wenco/Winu_Wenco_Equipment_Module_Matrix.xlsx."),
        ("Rating rule", "● = CCLAS captures, controls or tracks this instrument or its output as a core part of the sample workflow. ○ = plausible or method-dependent; includes judgement."),
        ("No vendor module list", "Unlike Wenco, the pack has no CCLAS product-capability document. The 12 module columns are derived from the LIMS.drawio stages (receipt, registration, ADF, BCF, data processing and QC, reporting, automated data exchange, Taskman, servers) plus standard LIMS functions (storage and retention is inferred). Datamine's actual module names, packaging and licensing must be confirmed before this is used for scope or price."),
        ("Reference lab is iron ore", "LIMS.drawio shows an iron-ore lab: XRF, fusion bead and TGA stages with Scott Automation robotics for receipt, registration, drying / splitting and crushing / pulverising. Winu is Cu-Au (fire assay, 4-acid ICP / AAS, Leco, Hg), so X1 to X5 are excluded and the Winu analysers have no drawn CCLAS interface."),
        ("Interfaces to confirm", "CCLAS result-capture interfaces for ICP-OES, ICP-MS, AAS, Leco, mercury analyser, laser PSD and auto-titrator. Automated data exchange endpoints (grade control, geology database, plant information). Whether manual prep (no Scott robotics) is supported by the prep-tracking modules."),
        ("Not CCLAS-integrated", "Left off the matrix as having no CCLAS function: " + "; ".join(f"{r} {name[r]}" for r in NOT_CCLAS) + "."),
        ("LIMS.drawio counts", "Counted from the drawing: 11 barcode scanners (Prep 1, Mine prep 1, Scott PC 1, XRF 2, Fusion 2, TGA 4), 14 computers (Prep 2, Mine prep 1, Scott PC 1, XRF 2, Fusion 1, TGA 4, Control 2, Taskman 1), 2 Zebra printers, 1 CCLAS app server, 1 CCLAS DB server. The laboratory workbook's Sizing notes say 13 scanners and 15 computers; that does not match the drawing. Winu quantities in this workbook follow the laboratory workbook, not the drawing."),
        ("Quantities", "Peak quantities are ASSUMPTION-based outputs of the laboratory workbook's Sizing sheet and move when its Demand inputs change; this workbook holds the values at build time."),
    ]
    for i, (a, b) in enumerate(notes):
        nt.cell(1 + i, 1, a).font = BOLD
        nt.cell(1 + i, 2, b).alignment = WRAP
        nt.cell(1 + i, 1).alignment = WRAP
    nt.column_dimensions["A"].width = 28
    nt.column_dimensions["B"].width = 130

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", required=True, help="Winu_Lab_Instrumentation_Requirements.xlsx")
    ap.add_argument("--output", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    p = Path(a.output)
    if p.exists() and not a.force:
        sys.exit(f"{p} exists; use --force")
    rows = build(p, Path(a.lab))
    print(f"wrote {p} with {len(rows)} instrument rows")


if __name__ == "__main__":
    main()
