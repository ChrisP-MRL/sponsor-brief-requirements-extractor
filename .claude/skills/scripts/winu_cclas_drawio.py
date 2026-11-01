"""Build the Winu CCLAS (Datamine LIMS) capability diagram (.drawio).
Same style as output/Winu/Winu_GNSS_RTK_Capability.drawio (swimlanes left to right, coloured boxes).
Usage: python -I -X utf8 winu_cclas_drawio.py <output.drawio>

Content is taken from input/Vendor/Datamine (CCLAS)/Winu_CCLAS_Instrument_Module_Matrix.xlsx (Instrument_x_Module,
Instrument_Detail, Module_Catalogue, Notes) and LIMS.drawio. No quantities are shown. Yellow boxes are open items or
judgement calls; red boxes are gaps against the reference (iron-ore) lab drawing.
The sample-requirements strip is informed by output/Winu/WIN-CON-EPC-001_Process_Review.html (SoW 2.3, 2.4, 4.7,
7.1.2, 18; FMS 6.2.16). Samples/day figures are ASSUMPTIONS from the laboratory workbook Demand sheet."""
import sys, html

out = sys.argv[1]
C = {"ref": ("#d5e8d4", "#82b366"), "link": ("#ffe6cc", "#d79b00"), "gap": ("#f8cecc", "#b85450"),
     "rig": ("#dae8fc", "#6c8ebf"), "out": ("#e1d5e7", "#9673a6"), "chk": ("#fff2cc", "#d6b656"),
     "grey": ("#f5f5f5", "#666666")}
LANE_X0, LANE_W, LANE_GAP, LANE_Y, LANE_H = 20, 300, 50, 80, 520
BOX_W, BOX_DX, BOX_H = 260, 20, 64
LANES = ["1. CCLAS platform (reference)", "2. Data capture links", "3. Laboratory stations (users)", "4. Outputs"]

B = {
    "inst": (1, 125, "gap", "Instrument result capture: ICP-OES, ICP-MS, AAS,\nLeco, Hg analyser, laser PSD\n(no interface in LIMS.drawio; Datamine to confirm)"),
    "core": (0, 125, "ref", "CCLAS application + database servers\n(Mine - Comms Room)\nhost every module"),
    "task": (0, 215, "ref", "CCLAS Taskman\nworklists, manual batch and result entry"),
    "ids": (0, 305, "ref", "Sample ID + barcode scheme\nper process sampling point (see strip below);\npoints not defined in pack"),
    "spec": (0, 395, "chk", "Methods, specifications, QC rules (CRM, blank,\nduplicate): to define; no Winu assay suite in pack"),
    "bal": (1, 215, "link", "Balance + platform scale integration\nweights to sample / batch record"),
    "scan": (1, 305, "link", "Barcode scanners + Zebra label printers\nscan at every room hand-over"),
    "xch": (1, 395, "gap", "Automated data exchange\nendpoints not drawn: grade control, geology\ndatabase, plant information"),
    "an": (2, 125, "rig", "ANALYSERS: ICP-OES / MS, AAS, Leco, Hg, PSD\nresult capture, QC, reporting; titrator keyed or captured"),
    "fa": (2, 215, "rig", "FIRE ASSAY + DIGEST BATCHES (manual)\nfurnaces, hot-blocks: label, worklist, balance weights"),
    "prep": (2, 305, "rig", "SAMPLE PREP: dry, split, crush, pulverise\nmanual at Winu (no Scott robotics), so CCLAS\nmust track manual prep"),
    "met": (2, 395, "grey", "Bench metallurgy: products re-register as samples;\nno CCLAS function on the equipment itself"),
    "ex": (2, 485, "gap", "Excluded (iron-ore reference lab): XRF, fusion bead,\nTGA, Scott Automation robotics"),
    "o1": (3, 125, "out", "Validated assay results\n(grade control turnaround is the driver)"),
    "o2": (3, 215, "out", "QC-released batch reports and certificates"),
    "o4": (3, 305, "out", "Sample storage + retention records\n(180 m2 store stated; rejects / pulps;\ninferred module)"),
    "o3": (3, 395, "chk", "Data feeds to mine + plant systems for\nreconciliation: interface not defined in sources"),
}
E = [("ids", "scan", "labels", False), ("task", "bal", "", False), ("core", "inst", "results", False), ("spec", "xch", "", True),
     ("scan", "prep", "", False), ("bal", "fa", "", False), ("inst", "an", "", False), ("xch", "an", "interface TBC", True),
     ("an", "o1", "", False), ("fa", "o2", "", False), ("prep", "o4", "", False), ("an", "o3", "", True)]

cells, n = [], [1]
def nid():
    n[0] += 1
    return f"l{n[0]}"
def esc(t):
    return html.escape(t, quote=True).replace("\n", "&#xa;")
def add(style, val, x, y, w, h):
    i = nid()
    cells.append(f'<mxCell id="{i}" parent="1" style="{style}" value="{val}" vertex="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i
def text(val, x, y, w, h, size=11, bold=False):
    return add(f"text;html=0;align=center;verticalAlign=middle;fontSize={size};fontStyle={1 if bold else 0};whiteSpace=wrap;", esc(val), x, y, w, h)

W = LANE_X0 * 2 + 4 * LANE_W + 3 * LANE_GAP
text("Winu Laboratory - CCLAS (Datamine LIMS) capability required (Cu-Au concentrator, ~10 Mtpa)", 20, 10, W - 40, 30, 18, True)
text("Source: Winu_CCLAS_Instrument_Module_Matrix.xlsx; LIMS.drawio; WIN-CON-EPC-001 Process Review. Module list is inferred (no CCLAS capability document in pack). "
     "Yellow = open item or judgement; red = gap vs reference lab.", 20, 38, W - 40, 20, 11)
for i, name in enumerate(LANES):
    add("swimlane;startSize=30;rounded=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;fontStyle=1;swimlaneFillColor=#fafafa;",
        esc(name), LANE_X0 + i * (LANE_W + LANE_GAP), LANE_Y, LANE_W, LANE_H)
ids = {}
for k, (ln, y, col, t) in B.items():
    f, s = C[col]
    big = k in ("an", "fa", "prep")
    ids[k] = add(f"rounded=1;whiteSpace=wrap;html=0;fillColor={f};strokeColor={s};fontSize=10;" + ("strokeWidth=2;" if big else ""),
                 esc(t), LANE_X0 + ln * (LANE_W + LANE_GAP) + BOX_DX, y, BOX_W, BOX_H)
for s, t, lab, dashed in E:
    i = nid()
    st = ("endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#333333;edgeStyle=orthogonalEdgeStyle;rounded=0;fontSize=9;"
          "labelBackgroundColor=#ffffff;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{ids[s]}" target="{ids[t]}" style="{st}" value="{esc(lab)}"><mxGeometry relative="1" as="geometry"/></mxCell>')

PY = LANE_Y + LANE_H + 20
text("Process sample requirements - from WIN-CON-EPC-001 Process Review (green = stated in pack; yellow = assumed, no basis in pack; grey = outside CCLAS)",
     20, PY, W - 40, 24, 13, True)
SAMPLES = [
    ("chk", "ROM + GRADE CONTROL\nMPP: ROM handling, crushing, stockpiling (stated). First ~600 kt ore in pre-strip (stated). Feed grade not in pack.\n~270 samples/day at 10 Mtpa / 100 t (ASSUMPTION): the turnaround driver"),
    ("chk", "GRINDING + CLASSIFICATION\nStated as MPP area; plant feed composites ~12/day (ASSUMPTION). Mill sizes, sample points and P&IDs not in pack"),
    ("chk", "FLOTATION + REGRIND\nProcess area stated; ~42/day rougher, cleaner, regrind (ASSUMPTION). Cell counts, flowsheet and mass balance not in pack"),
    ("ref", "GRAVITY GOLD\n'Gravity gold concentration' named in MPP breakdown (stated). ~4/day (ASSUMPTION); Au by fire assay, nugget effect"),
    ("ref", "CU CONCENTRATE (~25% Cu)\nConcentrate dewatering + product sampling named (stated). ~10/day lot and shift (ASSUMPTION). Tonnage, load-out/export scope, settlement lab not in pack"),
    ("ref", "TAILINGS HST / LST\nLST thickener area and HST/LST TSF cells stated. ~6/day (ASSUMPTION); sulphur and ARD classification"),
    ("chk", "WASTE / ARD, WATER, BENCH MET\nPermanent lab ~15 + 10 + 6 /day (ASSUMPTION). Bench met may go off-site. No assay suite or sampling plan in pack"),
    ("grey", "OUTSIDE CCLAS\nContractor construction lab (SoW 4.7): AS 1289 geotech, HDPE seam tests, concrete, borrow QA, Leco on mine waste per AMD plan. NATA, contractor-run"),
]
SW = (W - 40 - 7 * 10) // 8
for i, (col, t) in enumerate(SAMPLES):
    f, st = C[col]
    add(f"rounded=1;whiteSpace=wrap;html=0;fillColor={f};strokeColor={st};fontSize=9;align=left;verticalAlign=top;spacingLeft=5;spacingRight=5;spacingTop=4;",
        esc(t), 20 + i * (SW + 10), PY + 30, SW, 175)
cons = ("Facility + interface constraints (Process Review): laboratory building 503 m2 excluding equipment and sample store 180 m2 are stated (SoW 7.1.2); "
        "permanent laboratory equipment is excluded from the EPC scope, so CCLAS and instruments are a Company item (SoW s18); "
        "MPP electrical, instrumentation and communications are excluded, so on-stream sampler / analyser interfaces are undefined; "
        "FMS gives file exports only (SoW 6.2.16), so grade control and reconciliation exchange is assumed file-based.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;align=left;spacingLeft=10;", esc(cons), 20, PY + 215, W - 40, 60)
FY = PY + 295
note = ("Module fit by instrument tier (from the matrix):\n"
        "Core analytical (AAS, ICP, Leco, Hg, PSD): core, barcode, result capture, Taskman, QC, reporting; data exchange optional\n"
        "Fire assay furnaces, digest, balances, sieves: core, barcode, Taskman; balances add balance integration\n"
        "Prep (oven, crushers, divider, pulveriser): core, barcode, prep tracking; Bench metallurgy: optional only\n"
        "Support: scanners, printers, workstations and servers carry the traceability backbone\n"
        "Rating: primary = CCLAS captures or tracks the item as core workflow; optional = method-dependent (judgement).")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;", esc(note), 20, FY, 780, 130)
openi = ("Open items to resolve with Datamine / MinRes:\n"
         "1. Datamine module names, packaging and licensing; storage and retention is inferred.\n"
         "2. CCLAS interfaces for ICP, AAS, Leco, Hg, PSD, titrator.\n"
         "3. Manual prep support; data exchange endpoints.\n"
         "4. Quantities are assumption-based (lab workbook Sizing).\n"
         "5. Feed grade, flowsheet, mass balance, sampling plan, assay suite not in pack.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;", esc(openi), 820, FY, W - 840, 130)
H = FY + 160
xml = ('<mxfile host="65bd71144e"><diagram name="CCLAS LIMS capability" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W}" pageHeight="{H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, W, H)
