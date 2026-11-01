"""Build the Winu AVEVA capability diagram (.drawio).
Same style as output/Winu/Winu_GNSS_RTK_Capability.drawio (swimlanes left to right, coloured boxes).
Usage: python winu_aveva_drawio.py <output.drawio>

Sources: input/Vendor/AVEVA/AVEVA.md (AVEVA product mapping for a 10 Mtpa copper-gold concentrator: delay accounting,
metallurgical and plant performance accounting, concentrate quality) and output/Winu/WIN-CON-EPC-001_Process_Review.html
(10 Mtpa crushing / grinding / flotation, ~25% Cu concentrate; no DCS / PLC / SCADA / historian named; plant ore tracking
depends on batch exports until the permanent FMS exists). Yellow boxes are open items or judgement calls."""
import sys, html

out = sys.argv[1]

# fill, stroke
C = {"ref": ("#d5e8d4", "#82b366"), "link": ("#ffe6cc", "#d79b00"), "gap": ("#f8cecc", "#b85450"),
     "rig": ("#dae8fc", "#6c8ebf"), "off": ("#b0e3e6", "#0e8088"), "out": ("#e1d5e7", "#9673a6"),
     "chk": ("#fff2cc", "#d6b656"), "grey": ("#f5f5f5", "#666666")}

LANE_X0, LANE_W, LANE_GAP, LANE_Y, LANE_H = 20, 270, 40, 80, 500
BOX_W, BOX_DX = 230, 20

LANES = [
    "1. Plant data sources",
    "2. Data foundation + integration",
    "3. AVEVA applications",
    "4. Visibility + enterprise",
    "5. Outputs",
]

# key: (lane 0-4, y top, height, colour, text)
B = {
    # lane 0
    "scada": (0, 120, 74, "chk", "DCS / PLC / SCADA + instruments\ncrushing, grinding, flotation, dewatering\nplatform NOT named in the ITT pack"),
    "weigh": (0, 214, 64, "ref", "Weighing + sampling points\nbelt weighers, concentrate weighing,\nprocess stream samplers"),
    "cclas": (0, 298, 64, "ref", "Datamine CCLAS LIMS\nhead, rougher / cleaner, tail and\nconcentrate assays (XRF, ICP)"),
    "fms": (0, 382, 74, "link", "Wenco FMS (mine)\nore tracking from block model to dump;\nbatch / file exports until permanent FMS"),
    # lane 1
    "cloud": (1, 120, 64, "chk", "AVEVA CONNECT (cloud) - optional\nenterprise access, multi-site, analytics\nhosting decision TBC"),
    "pi": (1, 214, 74, "off", "AVEVA PI System (data hub)\ncollect, store, normalise, enrich\nreal-time plant data; redundant servers"),
    "p2b": (1, 340, 84, "link", "Plant2Business connectors /\nAVEVA System Platform integration layer\nOLEDB, REST / SOAP, scheduled CSV / XML"),
    # lane 2
    "dly": (2, 120, 84, "off", "Production Management - Downtime\ndelay event capture (auto + tablet),\nroot cause, availability / MSR KPIs"),
    "inv": (2, 224, 84, "off", "Production Management - Inventory\nROM, WIP and concentrate stock by grade,\nquality hold, blend, shipment reconcile"),
    "acct": (2, 328, 84, "off", "Production Accounting\nmass balance, statistical reconciliation,\nrecovery / yield, month-end close"),
    "mes": (2, 432, 64, "chk", "AVEVA MES - optional\nsample plans, hold / release, genealogy\nscope to be confirmed"),
    # lane 3
    "uoc": (3, 120, 110, "off", "AVEVA Unified Operations Center\nfor Mining\nsingle view of delays, accounting and quality;\nroot cause + deviation detection"),
    "bi": (3, 250, 64, "rig", "BI + mobile / web access\nPower BI, Teams alerts,\nshift dashboards"),
    "erp": (3, 354, 64, "chk", "ERP / financial systems\nproduction + inventory posting;\nERP not named in the pack"),
    # lane 4
    "o1": (4, 120, 74, "out", "Delay accounting (processing)\ndowntime by cause + equipment,\nplant availability, utilisation"),
    "o2": (4, 214, 74, "out", "Metallurgical + plant performance\naccounting: Cu / Au recovery,\nunaccounted loss, throughput vs plan"),
    "o3": (4, 308, 74, "out", "Concentrate quality + product\nmanagement: grade by lot (~25% Cu),\ntraceability, shipment reconciliation"),
    "o4": (4, 402, 64, "out", "Pit-to-port view\nmine to plant to concentrate\nlogistics, one contextual picture"),
}

# source, target, label, dashed
# source, target, label, dashed, exit fraction, entry fraction (distinct points so lines never share a segment)
E = [
    ("scada", "pi", "tags", False, 0.5, 0.25),
    ("weigh", "pi", "mass", False, 0.5, 0.75),
    ("cclas", "p2b", "assays", False, 0.5, 0.25),
    ("fms", "p2b", "files", True, 0.5, 0.75),
    ("pi", "dly", "status", False, 0.2, 0.5),
    ("pi", "acct", "mass / flow", False, 0.8, 0.2),
    ("p2b", "inv", "", False, 0.25, 0.5),
    ("p2b", "acct", "assays", False, 0.5, 0.6),
    ("p2b", "mes", "", True, 0.8, 0.5),
    ("pi", "cloud", "", True, 0.5, 0.5),
    ("dly", "uoc", "", False, 0.5, 0.2),
    ("inv", "uoc", "", False, 0.5, 0.5),
    ("acct", "uoc", "", False, 0.25, 0.8),
    ("acct", "erp", "posting", False, 0.75, 0.5),
    ("uoc", "bi", "", False, 0.5, 0.5),
    ("uoc", "o1", "", False, 0.15, 0.5),
    ("uoc", "o2", "", False, 0.4, 0.5),
    ("uoc", "o3", "", False, 0.65, 0.5),
    ("uoc", "o4", "", False, 0.9, 0.5),
]

cells = []
n = [1]


def nid():
    n[0] += 1
    return f"a{n[0]}"


def esc(t):
    return html.escape(t, quote=True).replace("\n", "&#xa;")


def add(style, val, x, y, w, h):
    i = nid()
    cells.append(f'<mxCell id="{i}" parent="1" style="{style}" value="{val}" vertex="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i


def text(val, x, y, w, h, size=11, bold=False, align="center"):
    return add(f"text;html=0;align={align};verticalAlign=middle;fontSize={size};fontStyle={1 if bold else 0};whiteSpace=wrap;",
               esc(val), x, y, w, h)


W_TOTAL = LANE_X0 * 2 + len(LANES) * LANE_W + (len(LANES) - 1) * LANE_GAP
text("Winu Process Plant - AVEVA capability (delay accounting, metallurgical accounting, concentrate quality)", 20, 10, W_TOTAL - 40, 30, 18, True)
text("Source: AVEVA research (input/Vendor/AVEVA) mapped to WIN-CON-EPC-001 Process Review (10 Mtpa Cu-Au concentrator, ~25% Cu concentrate). "
     "Yellow = open item or judgement call; validate with AVEVA before pricing.", 20, 38, W_TOTAL - 40, 20, 11)

for i, name in enumerate(LANES):
    add("swimlane;startSize=30;rounded=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;fontStyle=1;swimlaneFillColor=#fafafa;",
        esc(name), LANE_X0 + i * (LANE_W + LANE_GAP), LANE_Y, LANE_W, LANE_H)

box_id = {}
for k, (ln, y, h, col, t) in B.items():
    fill, stroke = C[col]
    style = f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;"
    if k == "uoc":
        style += "strokeWidth=2;"
    box_id[k] = add(style, esc(t), LANE_X0 + ln * (LANE_W + LANE_GAP) + BOX_DX, y, BOX_W, h)

# each cross-lane edge gets its own vertical channel in the gap (explicit waypoints) so segments never overlap
gap_edges = {}
for e in E:
    if B[e[0]][0] != B[e[1]][0]:
        gap_edges.setdefault(B[e[0]][0], []).append(e)
chan = {}
for sl, es in gap_edges.items():
    k = len(es)
    for j, e in enumerate(es):
        chan[(e[0], e[1])] = -28 + 56 * j / max(k - 1, 1)

for s, t, lab, dashed, ef, nf in E:
    i = nid()
    sl, tl = B[s][0], B[t][0]
    pts = ""
    if sl == tl:    # vertical hop inside a lane
        ex, ey, nx, ny = (0.5, 1, 0.5, 0) if B[s][1] < B[t][1] else (0.5, 0, 0.5, 1)
    else:
        ex, ey, nx, ny = 1, ef, 0, nf
        wx = LANE_X0 + (sl + 1) * LANE_W + sl * LANE_GAP + LANE_GAP / 2 + chan[(s, t)]
        sy = B[s][1] + B[s][2] * ef
        ty = B[t][1] + B[t][2] * nf
        pts = f'<Array as="points"><mxPoint x="{wx:.0f}" y="{sy:.0f}"/><mxPoint x="{wx:.0f}" y="{ty:.0f}"/></Array>'
    st = (f"endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#333333;edgeStyle=orthogonalEdgeStyle;rounded=0;"
          f"fontSize=9;labelBackgroundColor=#ffffff;exitX={ex};exitY={ey};entryX={nx};entryY={ny};" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{box_id[s]}" target="{box_id[t]}" style="{st}" value="{esc(lab)}">'
                 f'<mxGeometry relative="1" as="geometry">{pts}</mxGeometry></mxCell>')

FY = LANE_Y + LANE_H + 20
note = ("Capability to product mapping:\n"
        "Delay accounting: Production Management (Downtime) with PI System status and tablet entry; root cause and availability KPIs\n"
        "Metallurgical + plant performance accounting: Production Accounting with PI mass / flow data and CCLAS assays; "
        "WIP / concentrate inventory from Production Management\n"
        "Concentrate quality + product management: CCLAS LIMS assays, Production Management inventory (grade, hold, blend), optional MES genealogy\n"
        "Indicative AVEVA sizing (generic 10 Mtpa, not Winu-specific): ~500 PI points / s; 50-200 delay events / day; 200-500 samples / day")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(note), 20, FY, 900, 120)
openi = ("Open items to resolve:\n"
         "1. No DCS / PLC / SCADA / historian named in the ITT pack: PI System as the data hub is an assumption.\n"
         "2. Plant ore tracking relies on batch exports until the permanent FMS exists (SOW s6.2.16).\n"
         "3. ERP, MES scope and CONNECT cloud hosting not defined; CCLAS-to-AVEVA interface to be specified.\n"
         "4. Historian / engineering data on contractor systems must be segregated and returnable at handover (GC cl.12.5).")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(openi), 940, FY, W_TOTAL - 960, 120)

PAGE_H = FY + 150
xml = ('<mxfile host="65bd71144e"><diagram name="AVEVA capability" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W_TOTAL}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, W_TOTAL, PAGE_H)
