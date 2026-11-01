#!/usr/bin/env python3
"""Build the Winu laboratory instrumentation requirements and sizing workbook (Excel).

Layout follows input/Vendor/Wenco/Winu_Wenco_Equipment_Module_Matrix.xlsx (matrix sheet, detail sheet,
catalogue sheet, notes). Instrument types replace equipment types; sample streams replace Wenco modules.
Quantities are formula-driven: Demand (inputs and stream x test fractions) -> Sizing (instrument counts)
-> Space_Check (floor area against the 503 m2 MSA laboratory and 180 m2 sample store).

Sources: output/Winu/WIN-CON-EPC-001_Mining_Review.html and _Process_Review.html (10 Mtpa Cu-Au
concentrator, ~25% Cu concentrate, laboratory 503 m2 and sample storage 180 m2 excluding laboratory
equipment, Leco analysis of mine waste, HST/LST tailings); input/Vendor/Datamine (CCLAS)/LIMS.drawio
(LIMS and barcode pattern only; that layout is an iron-ore lab). No Winu head grade, assay suite or
sampling document exists in the pack, so every rate in yellow cells is an ASSUMPTION.

Run: python -I winu_lab_instrumentation_xlsx.py --output <xlsx> [--force]
"""
import argparse
import math
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as CL

NAVY = "1F3864"
HDR = PatternFill("solid", fgColor=NAVY)
WHITE = Font(bold=True, color="FFFFFF")
BOLD = Font(bold=True)
INP = PatternFill("solid", fgColor="FFF2CC")
TIER_FILL = {
    "1 Core analytical": PatternFill("solid", fgColor="DDEBF7"),
    "2 Preparation / bench": PatternFill("solid", fgColor="E2EFDA"),
    "3 Support (tracking only)": PatternFill("solid", fgColor="F2F2F2"),
    "Excluded": PatternFill("solid", fgColor="D9D9D9"),
}
GREY_FONT = Font(color="7F7F7F")
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# ---- matrix columns (E..R): letter -> (group, group colour, stream name, description) --------------
STREAMS = [
    ("E", "Data", "7030A0", "LIMS and barcode traceability", "Sample registration, chain of custody, result capture and QA/QC reporting (CCLAS-class LIMS pattern from LIMS.drawio)."),
    ("F", "Mine", "2E75B6", "Grade control (blasthole / RC)", "Ore-waste and Cu/Au grade-control samples; the largest daily stream and the turnaround driver."),
    ("G", "Mine", "2E75B6", "Resource / exploration drilling", "Core and RC samples for resource definition and infill. Set the Demand input to 0 if done off-site."),
    ("H", "Mine", "2E75B6", "Waste and ARD characterisation", "Total and sulphide S, carbon, NAG / ANC for waste rock and pit materials (ITT: Leco analysis of mine waste)."),
    ("I", "Plant", "548235", "Plant feed (ROM / SAG feed)", "Shift composites of crusher or mill feed for head grade, reconciliation and metallurgical accounting."),
    ("J", "Plant", "548235", "Flotation circuit streams", "Rougher, cleaner, scavenger and regrind streams for recovery control and mass balance."),
    ("K", "Plant", "548235", "Gravity gold products", "Gravity concentrate and tails; gold recovery to concentrate is a value driver."),
    ("L", "Plant", "548235", "Tailings (HST / LST)", "High- and low-sulphur tailings streams; sulphur and Cu/Au losses."),
    ("M", "Product", "BF8F00", "Cu concentrate (commercial)", "Concentrate Cu, Au, Ag and penalty elements (As, Sb, Bi, Hg, F, Pb, Zn) for settlement and plant control."),
    ("N", "Product", "BF8F00", "Concentrate moisture / TML and size", "Moisture, transportable moisture limit and size for shipping."),
    ("O", "Water", "1F8A8A", "Process and environmental water", "Metals, pH, EC and alkalinity for process water, bore water and monitoring."),
    ("P", "Metallurgy", "C55A11", "Bench metallurgical testing", "Grind calibration, rougher flotation and gravity tests on variability samples."),
    ("Q", "QA/QC", "C00000", "CRM, blank, duplicate, umpire", "Insertions and check samples for precision and bias (JORC Table 1 expectations)."),
    ("R", "Geotech", "7F7F7F", "Geotech and pit materials", "Density, moisture and size on pit materials. Strength testing stays with the contractor construction lab."),
]
SCOLS = [s[0] for s in STREAMS]

# ---- demand model ---------------------------------------------------------------------------------
TESTS = [  # key, label
    ("PREP", "Dry, crush, split, pulverise"),
    ("FA", "Fire assay Au"),
    ("DIG", "4-acid digest"),
    ("CU", "ICP-OES multi-element (Cu, Ag, S, Fe)"),
    ("ME", "ICP-MS trace and penalty elements"),
    ("SEQ", "Sequential Cu (acid / cyanide soluble)"),
    ("SC", "Leco total and sulphide S, C"),
    ("HGF", "Mercury (and fluoride)"),
    ("PSD", "Laser particle size"),
]
# stream: (name, samples/day (None = formula), basis, fractions in TESTS order)
DEM = [
    ("Grade control (blasthole / RC)", None, "ore t/day / t per sample", [1, 1, 1, 1, 0.1, 0.3, 0.5, 0, 0]),
    ("Resource / exploration drilling", 120, "ASSUMPTION: about 2 rigs, on-site scope", [1, 1, 1, 1, 1, 0.3, 0.5, 0.1, 0]),
    ("Waste and ARD characterisation", 15, "ASSUMPTION", [1, 0.1, 1, 1, 1, 0, 1, 0, 0]),
    ("Plant feed (ROM / SAG feed)", 12, "ASSUMPTION: 4 composites x 3 shifts", [1, 1, 1, 1, 0.2, 0.1, 1, 0.1, 0.1]),
    ("Flotation circuit streams", 42, "ASSUMPTION: 14 streams x 3 composites", [1, 0.5, 1, 1, 0.1, 0, 0.5, 0, 0.3]),
    ("Gravity gold products", 4, "ASSUMPTION", [1, 1, 1, 1, 0, 0, 0, 0, 0]),
    ("Tailings (HST / LST)", 6, "ASSUMPTION: 2 streams x 3 shifts", [1, 1, 1, 1, 0.5, 0, 1, 0, 0.1]),
    ("Cu concentrate (commercial)", 10, "ASSUMPTION: shift and lot samples", [1, 1, 1, 1, 1, 0, 0.5, 1, 0.2]),
    ("Water (process and environmental)", 10, "ASSUMPTION", [0, 0, 0, 1, 1, 0, 0, 0, 0]),
    ("Bench metallurgical samples", 6, "ASSUMPTION", [1, 1, 1, 1, 0.5, 0.1, 0.5, 0, 0.2]),
]
INPUTS = [  # key, label, value, unit, basis
    ("mtpa", "Concentrator throughput", 10, "Mtpa", "ITT SoW s2.3 PDF p.210 (Stated)"),
    ("tps", "Grade-control tonnes per sample", 100, "t", "ASSUMPTION: depends on drill spacing and sample interval"),
    ("qaqc", "QA/QC insertion uplift", 0.10, "fraction", "ASSUMPTION: blanks, CRMs, duplicates, check samples"),
    ("util", "Target instrument utilisation", 0.80, "fraction", "ASSUMPTION: leaves headroom for calibration, maintenance and peaks"),
    ("rej_d", "Coarse reject retention", 30, "days", "ASSUMPTION"),
    ("pulp_d", "Pulp retention on site", 90, "days", "ASSUMPTION: longer-term pulps go to off-site storage"),
    ("rej_m2", "Store area per retained reject", 0.004, "m2", "ASSUMPTION: shelving plus aisle share"),
    ("pulp_m2", "Store area per retained pulp", 0.001, "m2", "ASSUMPTION: shelving plus aisle share"),
    ("lab_m2", "Laboratory building area (excl. equipment)", 503, "m2", "SoW s7.1.2 MSA table item 24, PDF p.272 (Stated)"),
    ("store_m2", "Laboratory sample storage area", 180, "m2", "SoW s7.1.2 MSA table item 25, PDF p.272 (Stated)"),
    ("mult", "Room area per m2 of instrument footprint", 2.2, "x", "ASSUMPTION: bench, clearance, services, circulation"),
    ("allow", "Offices, amenities, entry allowance", 80, "m2", "ASSUMPTION"),
]

R1, R2, R3, R4, R5, R6, R7, R8 = (
    "Sample receipt & registration", "Sample preparation", "Fire assay", "Wet chemistry & ICP",
    "Instrument & physical testing", "Metallurgical bench", "Control room / LIMS", "Services",
)
T1, T2, T3, TX = "1 Core analytical", "2 Preparation / bench", "3 Support (tracking only)", "Excluded"

# ref, tier, name, make/class, room, driver, cap/unit/day, fixed qty, redundancy, m2/unit, primary, optional, rationale, LIMS ref
INSTR = [
    ("A1", T1, "Fire assay furnace", "Electric, 84-position", R3, "FA", 400, 1, 1, 6, "FGIKLMQ", "JP", "Au by 30-50 g fire assay (nugget effect); the Au value driver.", "LIMS.drawio fusion room (Claisse LeDoser 12) is the iron-ore analogue; not reused"),
    ("A2", T1, "Cupellation furnace", "Electric, matched to A1", R3, "FA", 400, 1, 1, 5, "FGIKLMQ", "JP", "Lead button cupellation to a prill for the Au finish.", ""),
    ("A3", T1, "Atomic absorption spectrometer", "Flame / graphite furnace, autosampler", R4, "FA+SEQ", 600, 1, 1, 4, "FGIJKLMQ", "HOP", "Au finish after fire assay; sequential acid- and cyanide-soluble Cu for oxide and transition ore.", ""),
    ("A4", T1, "Hot-block 4-acid digestion system", "40-position blocks in fume cupboards", R4, "DIG", 160, 1, 1, 5, "FGHIJLMQ", "KOP", "Near-total digest for Cu, Ag, S, Fe and trace elements.", ""),
    ("A5", T1, "ICP-OES", "Axial, autosampler", R4, "CU", 400, 1, 1, 4, "FGHIJLMOQ", "KP", "Cu, Ag, S, Fe, Zn, Pb, As and more. Replaces the XRF used on iron ore.", ""),
    ("A6", T1, "ICP-MS", "Quadrupole, collision cell", R4, "ME", 350, 1, 0, 4, "GHMO", "ILQ", "Penalty and trace elements (As, Sb, Bi, Hg, Cd) and low-level water metals.", ""),
    ("A7", T1, "Combustion S/C analyser (Leco)", "Induction furnace, total and sulphide S", R5, "SC", 250, 1, 0, 2, "HIL", "FGJM", "ARD classification and sulphur balance (ITT names Leco analysis of mine waste; HST / LST tailings).", ""),
    ("A8", T1, "Mercury analyser", "Direct thermal decomposition AAS", R5, "HGF", 200, 1, 0, 1.5, "M", "GHI", "Hg penalty element in Cu concentrate.", ""),
    ("A9", T1, "Auto-titrator, pH / EC meters", "NAG / ANC acid-base accounting; fluoride ISE", R5, None, 0, 1, 0, 2, "HL", "O", "Acid-base accounting, water pH, EC, alkalinity and fluoride.", ""),
    ("A10", T1, "Laser particle size analyser", "Wet dispersion", R5, "PSD", 100, 1, 0, 2, "JN", "ILMR", "Cyclone overflow P80 and concentrate size.", ""),
    ("A11", T1, "Analytical balances (0.1 mg)", "", R4, None, 0, 4, 0, 0.5, "FGHIJKLMNOQ", "PR", "Weighing for digests, fusion charges and solutions.", "LIMS.drawio uses Ohaus Explorer balances"),
    ("A12", T1, "Microbalance (0.001 mg)", "", R3, None, 0, 1, 0, 0.5, "FGIKMQ", "L", "Au prill weighing (gravimetric finish and check).", ""),
    ("A13", T1, "Top-loading balances and platform scales", "", R1, None, 0, 4, 0, 1, "FGHIJKLMNQR", "OP", "Sample receipt weights, moisture and split weights.", "LIMS.drawio: Alsto platform scales, Ohaus Explorer"),
    ("A14", T1, "Sieve shaker and wet-screen set", "", R5, None, 0, 2, 0, 2, "NR", "IJP", "Size distribution of concentrate and pit materials; screen-fire-assay checks.", ""),
    ("B1", T2, "Drying oven", "Forced-air, trolley", R2, "PREP", 300, 1, 1, 4, "FGHIJKLMNQR", "P", "Dry samples before crushing; moisture by mass loss.", ""),
    ("B2", T2, "Jaw crusher (primary)", "Lab, to about 6 mm", R2, "PREP", 600, 1, 1, 4, "FGHIQR", "P", "Primary crush of drill and pit samples.", ""),
    ("B3", T2, "Roll crusher (secondary)", "Lab, to about 2 mm", R2, "PREP", 500, 1, 0, 4, "FGHIQ", "PR", "Secondary crush before splitting.", ""),
    ("B4", T2, "Rotary sample divider", "Lab", R2, "PREP", 800, 1, 0, 3, "FGHIJKLMNQR", "P", "Representative splits to pulverising charge.", ""),
    ("B5", T2, "Ring pulveriser", "LM5 class, bowl set", R2, "PREP", 220, 1, 1, 3, "FGHIJKLMQ", "PR", "Pulverise to 85% passing 75 um for assay.", "LIMS.drawio mine sample prep room is the pattern"),
    ("B6", T2, "Dust extraction system", "Ducted, filtered", R2, None, 0, 1, 0, 4, "FGHIQ", "R", "Silica dust control in crushing and pulverising.", ""),
    ("M1", T2, "Bench flotation cells", "2 L and 5 L", R6, None, 0, 2, 0, 3, "P", "", "Rougher and cleaner flotation tests on variability samples.", ""),
    ("M2", T2, "Laboratory ball mill", "Grind calibration", R6, None, 0, 1, 0, 4, "P", "R", "Grind-time calibration to target P80.", ""),
    ("M3", T2, "Laboratory filter", "Pressure / vacuum", R6, None, 0, 1, 0, 2, "P", "JLM", "Dewatering of flotation products for assay.", ""),
    ("M4", T2, "Laboratory gravity concentrator", "Mozley / Knelson class", R6, None, 0, 1, 0, 2, "P", "K", "Gravity recoverable gold tests.", ""),
    ("S1", T3, "Barcode scanners", "", R7, None, 0, 10, 0, 0.2, "EFGHIJKLMNOQ", "PR", "Barcode scanning at every sample hand-over.", "LIMS.drawio: 1 to 4 per room (13 total)"),
    ("S2", T3, "Label printers", "Zebra class", R7, None, 0, 4, 0, 0.3, "EFGHIJKLMNOQ", "PR", "Sample and pulp packet labels.", "LIMS.drawio: 2 Zebra printers"),
    ("S3", T3, "Workstations", "", R7, None, 0, 12, 0, 1.5, "EFGHIJKLMNOQ", "PR", "Instrument and LIMS terminals.", "LIMS.drawio: 15 computers"),
    ("S4", T3, "LIMS application and database servers", "CCLAS-class", R7, None, 0, 2, 0, 1.5, "EFGHIJKLMNOQ", "PR", "LIMS, automated data exchange, Taskman equivalent.", "LIMS.drawio: CCLAS app and DB servers, Taskman"),
    ("S5", T3, "Fume cupboards and scrubber", "", R4, None, 0, 4, 0, 2.5, "FGHIJLMQ", "KOP", "Acid digests and fire-assay fumes.", ""),
    ("S6", T3, "Deionised water plant", "", R8, None, 0, 1, 0, 3, "FGHIJKLMOQ", "NP", "Reagent and rinse water.", ""),
    ("S7", T3, "Gas and compressed air supply", "Acetylene, argon, air", R8, None, 0, 1, 0, 4, "FGIJKLMQ", "H", "AAS, ICP and furnace supplies.", ""),
    ("S8", T3, "Flux and reagent store", "Cabinets, segregated", R8, None, 0, 1, 0, 6, "FGIKLMQ", "J", "Lead flux, nitric / hydrochloric / hydrofluoric / perchloric acid control.", ""),
    ("X1", TX, "Benchtop XRF (pressed pellet / fusion bead)", "", None, None, 0, 0, 0, 0, "", "", "Excluded: Cu and Au assay by fire assay and 4-acid ICP/AAS; XRF is the iron-ore (Rhodes Ridge) method.", "LIMS.drawio: 3 XRF"),
    ("X2", TX, "Portable XRF", "", None, None, 0, 0, 0, 0, "", "", "Excluded: not used for Cu-Au grade control.", ""),
    ("X3", TX, "Fusion bead preparation", "Claisse LeDoser class", None, None, 0, 0, 0, 0, "", "", "Excluded: only needed for XRF.", "LIMS.drawio: Claisse LeDoser 12"),
    ("X4", TX, "Thermogravimetric analyser (LOI)", "", None, None, 0, 0, 0, 0, "", "", "Excluded: loss on ignition is an iron-ore product test.", "LIMS.drawio: 4 TGA"),
    ("X5", TX, "Sample-prep robotics (Scott Automation)", "", None, None, 0, 0, 0, 0, "", "", "Excluded: iron-ore automation; revisit only if volumes justify.", "LIMS.drawio: Scott Automation"),
    ("X6", TX, "Geotechnical test frames (UCS, point load, AS 1289 set)", "", None, None, 0, 0, 0, 0, "", "", "Excluded: contractor construction laboratory, SoW s4.7.", ""),
]


def hdr(c, fill=HDR):
    c.font = WHITE
    c.fill = fill
    c.alignment = CENTER


def build(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Instrument_x_Stream"
    de = wb.create_sheet("Instrument_Detail")
    ca = wb.create_sheet("Stream_Catalogue")
    dm = wb.create_sheet("Demand")
    sz = wb.create_sheet("Sizing")
    sp = wb.create_sheet("Space_Check")
    nt = wb.create_sheet("Notes")

    # ---------------- Demand -----------------
    dm["A1"] = "Winu laboratory - sample demand and test load"
    dm["A1"].font = Font(bold=True, size=14)
    dm["A2"] = "Yellow cells are inputs. Every rate is an ASSUMPTION unless the basis says Stated; replace with the Contract Production Requirements, sampling plan and block-model data when issued."
    dm.merge_cells("A2:L2")
    dm["A2"].alignment = WRAP
    dm.row_dimensions[2].height = 32
    for i, h in enumerate(["Key", "Input", "Value", "Unit", "Basis"]):
        hdr(dm.cell(4, 1 + i))
    ref = {}
    for i, (k, lab, v, u, b) in enumerate(INPUTS):
        r = 5 + i
        dm.cell(r, 1, k)
        dm.cell(r, 2, lab)
        c = dm.cell(r, 3, v)
        c.fill = INP
        dm.cell(r, 4, u)
        dm.cell(r, 5, b)
        ref[k] = f"Demand!$C${r}"
    r0 = 5 + len(INPUTS) + 2  # stream table header row
    dm.cell(r0 - 1, 1, "Samples per day by stream and share receiving each test").font = BOLD
    heads = ["#", "Stream", "Samples/day", "Basis"] + [t[1] for t in TESTS]
    for i, h in enumerate(heads):
        hdr(dm.cell(r0, 1 + i))
    dm.row_dimensions[r0].height = 62
    first = r0 + 1
    for i, (nm, sd, basis, fr) in enumerate(DEM):
        r = first + i
        dm.cell(r, 1, i + 1)
        dm.cell(r, 2, nm)
        if sd is None:
            dm.cell(r, 3, f"={ref['mtpa']}*1000000/365/{ref['tps']}")
        else:
            dm.cell(r, 3, sd).fill = INP
        dm.cell(r, 3).number_format = "0"
        dm.cell(r, 4, basis)
        for j, f in enumerate(fr):
            c = dm.cell(r, 5 + j, f)
            c.fill = INP
            c.number_format = "0.0#"
    last = first + len(DEM) - 1
    tr = last + 2
    dm.cell(tr, 2, "Total samples/day (before QA/QC)").font = BOLD
    dm.cell(tr, 3, f"=SUM(C{first}:C{last})").number_format = "0"
    dm.cell(tr + 1, 2, "Tests per day incl. QA/QC uplift").font = BOLD
    tot = {}
    for j, (k, _) in enumerate(TESTS):
        col = CL(5 + j)
        c = dm.cell(tr + 1, 5 + j, f"=SUMPRODUCT($C${first}:$C${last},{col}{first}:{col}{last})*(1+{ref['qaqc']})")
        c.number_format = "0"
        c.font = BOLD
        tot[k] = f"Demand!${col}${tr + 1}"
    tot["FA+SEQ"] = f"({tot['FA']}+{tot['SEQ']})"
    dm.column_dimensions["A"].width = 8
    dm.column_dimensions["B"].width = 44
    dm.column_dimensions["C"].width = 14
    dm.column_dimensions["D"].width = 40
    dm.column_dimensions["E"].width = 16
    for j in range(len(TESTS)):
        dm.column_dimensions[CL(5 + j)].width = 16
    dm.freeze_panes = "A5"

    # ---------------- Sizing -----------------
    sz["A1"] = "Winu laboratory - instrument sizing"
    sz["A1"].font = Font(bold=True, size=14)
    sz["A2"] = "Calculated qty = ROUNDUP(demand / (capacity x utilisation)). Selected qty = MAX(calculated, fixed minimum) + redundancy. Capacities are typical vendor-class figures and ASSUMPTIONS; confirm with OEMs."
    sz.merge_cells("A2:P2")
    sz["A2"].alignment = WRAP
    sz.row_dimensions[2].height = 32
    sh = ["Ref", "Tier", "Instrument", "Room", "Driver", "Demand /day", "Capacity /unit /day", "Utilisation",
          "Calculated qty", "Fixed minimum", "Redundancy (+)", "Selected qty", "m2 per unit", "Footprint m2", "Basis", "Datamine LIMS reference"]
    for i, h in enumerate(sh):
        hdr(sz.cell(4, 1 + i))
    sz.row_dimensions[4].height = 34
    srow = {}
    pyq = {}
    pydem = {}
    r = 5
    for it in INSTR:
        rf, tier, nm, mk, room, drv, cap, fq, red, ar, pri, opt, why, lims = it
        if tier == TX:
            continue
        srow[rf] = r
        sz.cell(r, 1, rf)
        sz.cell(r, 2, tier)
        sz.cell(r, 3, nm)
        sz.cell(r, 4, room)
        sz.cell(r, 5, drv or "fixed")
        if drv:
            sz.cell(r, 6, f"={tot[drv]}").number_format = "0"
            sz.cell(r, 7, cap).fill = INP
            sz.cell(r, 8, f"={ref['util']}").number_format = "0%"
            sz.cell(r, 9, f"=ROUNDUP(F{r}/(G{r}*H{r}),0)")
        else:
            sz.cell(r, 9, 0)
        sz.cell(r, 10, fq).fill = INP
        sz.cell(r, 11, red).fill = INP
        sz.cell(r, 12, f"=MAX(I{r},J{r})+K{r}").font = BOLD
        sz.cell(r, 13, ar).fill = INP
        sz.cell(r, 14, f"=L{r}*M{r}").number_format = "0.0"
        sz.cell(r, 15, why)
        sz.cell(r, 16, lims)
        for c in range(1, 17):
            if not sz.cell(r, c).fill.fill_type:
                sz.cell(r, c).fill = TIER_FILL[tier]
        r += 1
    send = r - 1
    sz.cell(r + 1, 3, "Total instrument footprint (m2)").font = BOLD
    sz.cell(r + 1, 14, f"=SUM(N5:N{send})").number_format = "0.0"
    for col, w in zip("ABCDEFGHIJKLMNOP", [6, 24, 44, 28, 10, 12, 14, 12, 12, 10, 11, 10, 10, 11, 70, 46]):
        sz.column_dimensions[col].width = w
    sz.freeze_panes = "D5"

    # python mirror for verification and reporting
    tests_py = {}
    for j, (k, _) in enumerate(TESTS):
        s = 0.0
        for nm, sd, _, fr in DEM:
            n = sd if sd is not None else 10 * 1e6 / 365 / 100
            s += n * fr[j]
        tests_py[k] = s * 1.10
    tests_py["FA+SEQ"] = tests_py["FA"] + tests_py["SEQ"]
    foot = {}
    for it in INSTR:
        rf, tier, nm, mk, room, drv, cap, fq, red, ar, *_ = it
        if tier == TX:
            continue
        calc = math.ceil(round(tests_py[drv] / (cap * 0.8), 9)) if drv else 0
        pyq[rf] = max(calc, fq) + red
        foot[room] = foot.get(room, 0) + pyq[rf] * ar

    # ---------------- Matrix -----------------
    ws["A1"] = "Winu - laboratory instrument applicability by sample stream"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = ("● = primary fit   ○ = optional / conditional   blank = not applicable. Instrument types and sample streams from the Winu "
                "Mining and Process ITT reviews and the Datamine LIMS layout; quantities from the Sizing sheet (ASSUMPTION-based). "
                "Cu by 4-acid ICP-OES / AAS and Au by fire assay; XRF methods are excluded (iron-ore practice).")
    ws.merge_cells("A2:T2")
    ws["A2"].alignment = WRAP
    ws.row_dimensions[1].height = 18.45
    ws.row_dimensions[2].height = 32.05
    ws.row_dimensions[5].height = 62.05
    for col, grp, colr, nm, _ in STREAMS:
        c = ws[f"{col}4"]
        c.value = grp
        hdr(c, PatternFill("solid", fgColor=colr))
        ws[f"{col}5"] = nm
        hdr(ws[f"{col}5"])
    for i, h in enumerate(["Ref", "Instrument tier", "Instrument", "Peak qty"]):
        ws.cell(5, 1 + i, h)
        hdr(ws.cell(5, 1 + i))
    ws["S5"] = "Streams (primary)"
    ws["T5"] = "Streams (incl. optional)"
    hdr(ws["S5"])
    hdr(ws["T5"])
    first_m = 6
    for i, it in enumerate(INSTR):
        rf, tier, nm, mk, room, drv, cap, fq, red, ar, pri, opt, why, lims = it
        r = first_m + i
        ws.cell(r, 1, rf)
        ws.cell(r, 2, tier)
        ws.cell(r, 3, nm)
        if tier != TX:
            ws.cell(r, 4, f"=Sizing!L{srow[rf]}")
        for c in range(1, 5):
            ws.cell(r, c).fill = TIER_FILL[tier]
            if tier == TX:
                ws.cell(r, c).font = GREY_FONT
        for col in SCOLS:
            c = ws[f"{col}{r}"]
            if col in pri:
                c.value = "●"
            elif col in opt:
                c.value = "○"
            c.alignment = Alignment(horizontal="center")
        if tier != TX:
            ws[f"S{r}"] = f'=COUNTIF(E{r}:R{r},"●")'
            ws[f"T{r}"] = f"=COUNTA(E{r}:R{r})"
    last_m = first_m + len(INSTR) - 1
    ws.conditional_formatting.add(f"E{first_m}:R{last_m}", CellIsRule(operator="equal", formula=['"●"'], fill=PatternFill("solid", bgColor="C6E0B4")))
    ws.conditional_formatting.add(f"E{first_m}:R{last_m}", CellIsRule(operator="equal", formula=['"○"'], fill=PatternFill("solid", bgColor="FFF2CC")))
    fr = last_m + 2
    ws.cell(fr, 3, "Instrument types serving stream (count)").font = BOLD
    for col in SCOLS:
        c = ws[f"{col}{fr}"]
        c.value = f"=COUNTA({col}{first_m}:{col}{last_m})"
        c.alignment = Alignment(horizontal="center")
    ws.cell(fr + 1, 3, "Selected instruments in scope (units)").font = BOLD
    ws.cell(fr + 1, 4, f"=SUM(D{first_m}:D{last_m})")
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 25.15
    ws.column_dimensions["C"].width = 46
    ws.column_dimensions["D"].width = 9
    for col in SCOLS:
        ws.column_dimensions[col].width = 15
    ws.column_dimensions["S"].width = 12
    ws.column_dimensions["T"].width = 12
    ws.freeze_panes = "E6"

    # ---------------- Detail -----------------
    dh = ["Ref", "Instrument tier", "Instrument", "Make / class", "Peak qty", "Room", "Primary streams", "Optional streams",
          "Duty", "Datamine LIMS reference", "Sizing driver"]
    for i, h in enumerate(dh):
        hdr(de.cell(1, 1 + i))
    name = {s[0]: s[3] for s in STREAMS}
    for i, it in enumerate(INSTR):
        rf, tier, nm, mk, room, drv, cap, fq, red, ar, pri, opt, why, lims = it
        r = 2 + i
        vals = [rf, tier, nm, mk, f"=Sizing!L{srow[rf]}" if tier != TX else None, room or "", "; ".join(name[c] for c in pri),
                "; ".join(name[c] for c in opt), why, lims, drv or ("fixed" if tier != TX else "")]
        for j, v in enumerate(vals):
            c = de.cell(r, 1 + j, v)
            c.alignment = WRAP
            if j < 3:
                c.fill = TIER_FILL[tier]
    for col, w in zip("ABCDEFGHIJK", [6, 24, 40, 34, 9, 28, 60, 50, 60, 44, 12]):
        de.column_dimensions[col].width = w
    de.freeze_panes = "D2"

    # ---------------- Catalogue -----------------
    for i, h in enumerate(["Group", "Stream", "Description", "Primary instruments", "Optional instruments"]):
        hdr(ca.cell(1, 1 + i))
    for i, (col, grp, colr, nm, desc) in enumerate(STREAMS):
        r = 2 + i
        pri = [it[2] for it in INSTR if col in it[10]]
        opt = [it[2] for it in INSTR if col in it[11]]
        for j, v in enumerate([grp, nm, desc, "; ".join(pri), "; ".join(opt)]):
            ca.cell(r, 1 + j, v).alignment = WRAP
    for col, w in zip("ABCDE", [14, 34, 60, 90, 60]):
        ca.column_dimensions[col].width = w

    # ---------------- Space check -----------------
    sp["A1"] = "Winu laboratory - floor area check"
    sp["A1"].font = Font(bold=True, size=14)
    for i, h in enumerate(["Room", "Instrument footprint m2", "Room area m2"]):
        hdr(sp.cell(3, 1 + i))
    rooms = [R1, R2, R3, R4, R5, R6, R7, R8]
    for i, rm in enumerate(rooms):
        r = 4 + i
        sp.cell(r, 1, rm)
        sp.cell(r, 2, f'=SUMIF(Sizing!$D$5:$D${send},A{r},Sizing!$N$5:$N${send})').number_format = "0.0"
        sp.cell(r, 3, f"=B{r}*{ref['mult']}").number_format = "0.0"
    rr = 4 + len(rooms)
    sp.cell(rr, 1, "Offices, amenities, entry allowance")
    sp.cell(rr, 3, f"={ref['allow']}").number_format = "0.0"
    sp.cell(rr + 1, 1, "Required laboratory area").font = BOLD
    sp.cell(rr + 1, 3, f"=SUM(C4:C{rr})").number_format = "0.0"
    sp.cell(rr + 2, 1, "Available (MSA laboratory building, excl. equipment)")
    sp.cell(rr + 2, 3, f"={ref['lab_m2']}")
    sp.cell(rr + 3, 1, "Surplus / (shortfall) m2").font = BOLD
    sp.cell(rr + 3, 3, f"=C{rr + 2}-C{rr + 1}").number_format = "0.0"
    sp.cell(rr + 4, 1, "Utilisation of building")
    sp.cell(rr + 4, 3, f"=C{rr + 1}/C{rr + 2}").number_format = "0%"
    s0 = rr + 7
    sp.cell(s0 - 1, 1, "Sample storage").font = BOLD
    sp.cell(s0, 1, "Retained rejects (count)")
    sp.cell(s0, 3, f"={tot['PREP']}*{ref['rej_d']}").number_format = "0"
    sp.cell(s0 + 1, 1, "Retained pulps (count)")
    sp.cell(s0 + 1, 3, f"={tot['PREP']}*{ref['pulp_d']}").number_format = "0"
    sp.cell(s0 + 2, 1, "Required storage area m2").font = BOLD
    sp.cell(s0 + 2, 3, f"=C{s0}*{ref['rej_m2']}+C{s0 + 1}*{ref['pulp_m2']}").number_format = "0.0"
    sp.cell(s0 + 3, 1, "Available (Laboratory Sample Storage)")
    sp.cell(s0 + 3, 3, f"={ref['store_m2']}")
    sp.cell(s0 + 4, 1, "Surplus / (shortfall) m2").font = BOLD
    sp.cell(s0 + 4, 3, f"=C{s0 + 3}-C{s0 + 2}").number_format = "0.0"
    for rw in (rr + 3, s0 + 4):
        sp.conditional_formatting.add(f"C{rw}", CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", bgColor="F8CBAD")))
        sp.conditional_formatting.add(f"C{rw}", CellIsRule(operator="greaterThanOrEqual", formula=["0"], fill=PatternFill("solid", bgColor="C6E0B4")))
    sp.column_dimensions["A"].width = 52
    sp.column_dimensions["B"].width = 24
    sp.column_dimensions["C"].width = 18

    # ---------------- Notes -----------------
    notes = [
        ("Purpose", "Defines the laboratory instrumentation for Winu (Cu-Au concentrator, about 10 Mtpa) and sizes quantities and floor area against the MSA laboratory building."),
        ("Sources", "output/Winu/WIN-CON-EPC-001_Mining_Review.html and _Process_Review.html (throughput, laboratory and sample storage areas, Leco and HST/LST references); input/Vendor/Datamine (CCLAS)/LIMS.drawio (LIMS and barcode pattern); layout from input/Vendor/Wenco/Winu_Wenco_Equipment_Module_Matrix.xlsx."),
        ("Rating rule", "● = the instrument is the standard method for that stream. ○ = used for some samples or as backup. Judgement, not a vendor statement."),
        ("Method choice", "Cu by 4-acid digest with ICP-OES (sequential Cu by AAS for oxide and transition), Au by fire assay with AAS finish, penalty elements by ICP-MS and Hg analyser, S and C by Leco. XRF (benchtop, portable, fusion bead) and TGA are excluded because they are iron-ore methods in the Datamine layout."),
        ("Stated vs assumed", "Stated: 10 Mtpa, laboratory 503 m2 and sample storage 180 m2 excluding laboratory equipment. Everything else (samples per day, test shares, capacities, utilisation, area factors, retention) is an ASSUMPTION in yellow cells."),
        ("Scope gap", "Laboratory equipment for the permanent laboratory is excluded from the EPC scope (Process Review, Work Excluded part 2), so these instruments are a Company procurement item. No assay suite, sampling document or sample-prep document is listed in the pack."),
        ("Grade control", "No resource, grade or ore tonnage by pit stage is in the pack, so grade-control volume is ore t/day divided by tonnes per sample. Pre-strip has only about 600 kt of ore, so early volumes will be far below the steady-state sizing."),
        ("Off-site option", "Resource drilling and metallurgical testing can move off-site. Set those Demand rows to 0 to see the on-site core lab."),
        ("Next to confirm", "Head grade and Cu / Au mineralogy, sampling plan and drill spacing, turnaround targets, commercial settlement lab arrangement, on-site vs off-site split, accreditation (ISO/IEC 17025)."),
    ]
    for i, (a, b) in enumerate(notes):
        nt.cell(1 + i, 1, a).font = BOLD
        nt.cell(1 + i, 2, b).alignment = WRAP
        nt.cell(1 + i, 1).alignment = WRAP
    nt.column_dimensions["A"].width = 28
    nt.column_dimensions["B"].width = 130

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return tests_py, pyq, foot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    p = Path(a.output)
    if p.exists() and not a.force:
        sys.exit(f"{p} exists; use --force")
    tests, q, foot = build(p)
    print("tests/day:", {k: round(v) for k, v in tests.items()})
    print("qty:", q)
    mult, allow = 2.2, 80
    req = sum(foot.values()) * mult + allow
    print("footprint by room:", {k: round(v, 1) for k, v in foot.items()})
    print(f"required area {req:.0f} m2 vs 503 m2")
    prep = tests["PREP"]
    print(f"storage {(prep*30*0.004 + prep*90*0.001):.0f} m2 vs 180 m2")


if __name__ == "__main__":
    main()
