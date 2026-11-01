"""Build the Winu Wenco FMS capability diagram (.drawio).
Same style as output/Winu/Winu_GNSS_RTK_Capability.drawio (swimlanes left to right, coloured boxes).
Usage: python winu_wenco_drawio.py <output.drawio>

Figures are taken from input/Vendor/Wenco/Winu_Wenco_Equipment_Module_Matrix.xlsx (Equipment_x_Module, Equipment_Detail,
Module_Catalogue, Notes). No equipment counts are shown. Focus is Wenco Tier 1 Dispatched and Tier 2 Tracked; Tier 3 is
tracking only. Yellow boxes are open items or judgement calls."""
import sys, html

out = sys.argv[1]

# fill, stroke
C = {"ref": ("#d5e8d4", "#82b366"), "link": ("#ffe6cc", "#d79b00"), "gap": ("#f8cecc", "#b85450"),
     "rig": ("#dae8fc", "#6c8ebf"), "off": ("#b0e3e6", "#0e8088"), "out": ("#e1d5e7", "#9673a6"),
     "chk": ("#fff2cc", "#d6b656"), "grey": ("#f5f5f5", "#666666")}

LANE_X0, LANE_W, LANE_GAP, LANE_Y, LANE_H = 20, 270, 40, 80, 620
BOX_W, BOX_DX = 230, 20

LANES = [
    "1. Site FMS infrastructure",
    "2. Equipment (Tier 1 + Tier 2)",
    "3. Wencomine core + Dispatch",
    "4. Guidance + asset health",
    "5. Data + safety options",
    "6. Outputs",
]

# key: (lane 0-5, y top, height, colour, text). Boxes are placed so that linked boxes share a centre line
# (straight arrows across the lane gaps); fan-in / fan-out links use a single elbow in the gap.
B = {
    # lane 0
    "srv": (0, 120, 64, "link", "Wencomine FMS server + network (1 set)\nsupports all modules; hosting / location TBC"),
    "gnss": (0, 259, 64, "ref", "GNSS RTK reference (R750 base, UHF / NTRIP)\npositions every fitted unit - see\nWinu_GNSS_RTK_Capability.drawio"),
    "xcmg": (0, 349, 64, "chk", "XCMG-to-Wenco on-board / CAN interface\nunconfirmed: affects Dynamic, Fuel and\nParkup Dispatch data on the XCMG trucks"),
    "mesh": (0, 469, 64, "gap", "Temporary Contractor radio + FMS mesh:\nrepeater trailers (Company TETRA NOT\navailable)"),
    # lane 1
    "ex": (1, 120, 56, "gap", "Excluded - drill rigs (production, pre-split)\nEpiroc supplies drill control; no Wenco module"),
    "t1": (1, 196, 190, "rig", "TIER 1 DISPATCHED\n"
           "Rear dump trucks + rigid ore / clean-up / borrow trucks: core FMS, Dynamic, Fuel + Parkup Dispatch, Downtime, Analytics\n"
           "Hydraulic + medium excavators, wheel loaders: core FMS, Dynamic Dispatch, BenchManager, Downtime, Analytics\n"
           "Ore Quality Dispatching optional on all"),
    "t2": (1, 406, 190, "rig", "TIER 2 TRACKED (not dispatched)\n"
           "Dump / dig-face + TSF dozers, graders: core FMS, BenchManager, Downtime, Analytics\n"
           "Water carts, impact roller, emulsion MPU: core FMS, Downtime, Analytics\n"
           "Clearing dozer, wheel dozers, compactors, backhoe: BenchManager optional"),
    "t3": (1, 616, 56, "grey", "Tier 3 Support, tracking only: light vehicles,\nservice / lube trucks, tankers, crane, float -\ncore FMS (other modules optional)"),
    # lane 2
    "oreq": (2, 169, 64, "chk", "Ore Quality Dispatching - optional\npre-strip is mostly waste, so conditional"),
    "dyn": (2, 259, 64, "link", "Dynamic Dispatch\ntruck-to-loader / destination assignment\n(trucks and load units)"),
    "fuel": (2, 349, 64, "link", "Fuel Dispatch + Activity (Parkup) Dispatch\nhaul trucks only; fuel point must be defined in\nWenco (link to MIN-L2-07 Fuel Management)"),
    "core": (2, 469, 64, "off", "Wencomine FMS core - all fitted equipment\nGPS tracking, MDT, production monitoring,\ndelay / status accounting, reporting"),
    # lane 3
    "bench": (3, 369, 64, "off", "BenchManager (dig / doze / grade)\nprimary on excavators, loaders, graders, dozers;\noptional on other earthmoving"),
    "down": (3, 549, 64, "off", "Downtime Tracking\nprimary on Tier 1 and Tier 2;\noptional on Tier 3 support"),
    # lane 4
    "epi": (4, 120, 64, "chk", "Epiroc drill status feed into FMS / dispatch view:\nopen item (drill positions not in Wencomine)"),
    "saf": (4, 210, 64, "chk", "Safety options only, not in the quote:\nSmartCap fatigue, collision awareness (Wenco: in\ndevelopment toward EMESRT level 9)"),
    "api": (4, 369, 64, "link", "Open API / structured exports to MinRes\n(haul cycle, tracking); consumer and format\nnot defined in sources"),
    "ana": (4, 549, 64, "off", "Analytics, BI + Open API export\nprimary on Tier 1 and Tier 2, optional on\nTier 3 (ITT s6.2.16, s10.6)"),
    # lane 5
    "o4": (5, 120, 64, "chk", "Production reconciliation with survey / mass-haul\nas-builts: interface not defined in sources"),
    "o3": (5, 369, 64, "out", "Dig / dump-face and road grade guidance data\n(17 km long-term roads, TSF and dump dozing)"),
    "o1": (5, 459, 64, "out", "Haul cycle, payload and source-to-destination\ntracking; dispatch compliance for the pre-strip"),
    "o2": (5, 549, 64, "out", "Fleet availability, delays and downtime reports"),
}

# source, target, label, dashed
E = [
    ("gnss", "t1", "RTK", False),
    ("xcmg", "t1", "", True),
    ("mesh", "t2", "radio", False),
    ("t1", "dyn", "", False),
    ("t1", "core", "", False),
    ("t2", "core", "", False),
    ("t3", "core", "", False),
    ("dyn", "fuel", "", False),
    ("dyn", "oreq", "", True),
    ("core", "bench", "", False),
    ("core", "down", "", False),
    ("bench", "api", "", False),
    ("down", "ana", "", False),
    ("ana", "o1", "", False),
    ("ana", "o2", "", False),
    ("api", "o3", "", False),
    ("epi", "o4", "", True),
]

cells = []
n = [1]


def nid():
    n[0] += 1
    return f"w{n[0]}"


def esc(t):
    return html.escape(t, quote=True).replace("\n", "&#xa;")


def add(style, val, x, y, w, h, extra=""):
    i = nid()
    cells.append(f'<mxCell id="{i}" parent="1" style="{style}" value="{val}" vertex="1"{extra}>'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i


def text(val, x, y, w, h, size=11, bold=False, align="center"):
    return add(f"text;html=0;align={align};verticalAlign=middle;fontSize={size};fontStyle={1 if bold else 0};whiteSpace=wrap;",
               esc(val), x, y, w, h)


W_TOTAL = LANE_X0 * 2 + len(LANES) * LANE_W + (len(LANES) - 1) * LANE_GAP
text("Winu Pre-Strip - Wenco FMS capability by equipment type (Wencomine FMS assumed, ITT s6.2.16)", 20, 10, W_TOTAL - 40, 30, 18, True)
text("Source: Winu_Wenco_Equipment_Module_Matrix.xlsx (module fit from Wenco Product Capabilities). "
     "Yellow = open item or judgement call; validate with Wenco before pricing.", 20, 38, W_TOTAL - 40, 20, 11)

for i, name in enumerate(LANES):
    add("swimlane;startSize=30;rounded=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;fontStyle=1;swimlaneFillColor=#fafafa;",
        esc(name), LANE_X0 + i * (LANE_W + LANE_GAP), LANE_Y, LANE_W, LANE_H)

box_id = {}
for k, (ln, y, h, col, t) in B.items():
    fill, stroke = C[col]
    big = k in ("t1", "t2")
    style = (f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;"
             + ("align=left;spacingLeft=6;spacingRight=6;strokeWidth=2;" if big else ""))
    box_id[k] = add(style, esc(t), LANE_X0 + ln * (LANE_W + LANE_GAP) + BOX_DX, y, BOX_W, h)

for s, t, lab, dashed in E:
    i = nid()
    sl, tl = B[s][0], B[t][0]
    if sl == tl:    # vertical hop inside a lane
        ex, ey, nx, ny = (0.5, 1, 0.5, 0) if B[s][1] < B[t][1] else (0.5, 0, 0.5, 1)
    else:
        ex, ey, nx, ny = 1, 0.5, 0, 0.5
    st = (f"endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#333333;edgeStyle=orthogonalEdgeStyle;rounded=0;"
          f"fontSize=9;labelBackgroundColor=#ffffff;exitX={ex};exitY={ey};entryX={nx};entryY={ny};" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{box_id[s]}" target="{box_id[t]}" style="{st}" value="{esc(lab)}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')

FY = LANE_Y + LANE_H + 20
note = ("Module fit by Wenco tier:\n"
        "Tier 1 Dispatched (dump + rigid trucks, excavators, wheel loaders): Wencomine FMS core, Dynamic Dispatch, Downtime, Analytics; Fuel + Parkup Dispatch on trucks; "
        "BenchManager on excavators and loaders; Ore Quality Dispatching optional\n"
        "Tier 2 Tracked (dozers, graders, water carts, compactors, roller, backhoe, emulsion MPU): core FMS, Downtime, Analytics; "
        "BenchManager on dump / dig-face dozers and graders, optional on other earthmoving\n"
        "Tier 3 Support (tracking only): core FMS; other modules optional | Drill rigs: no Wenco module (Epiroc) | "
        "Stockpile Manager, ReadyLine, TireMax: not marked in matrix | SmartCap, collision awareness: options, excluded\n"
        "Rating: primary = Wenco states cover or core purpose of the unit; optional = plausible or value-dependent (judgement where Wenco is silent).")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(note), 20, FY, 900, 130)
openi = ("Open items to resolve with Wenco / MinRes:\n"
         "1. Wenco publishes no module-by-equipment matrix: BenchManager on compactors, backhoes, wheel dozers and clearing dozers is inferred.\n"
         "2. XCMG-to-Wenco interface unconfirmed; A1-A3 free-issue fleet is modelled, not from the Client Supplied Fleet List.\n"
         "3. Collision awareness is not yet a released product; Epiroc drill status feed into Wencomine undecided.\n"
         "4. Light vehicle fit is derived and indicative; Wencolite and autonomy (ISO 23725) not mapped.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(openi), 940, FY, W_TOTAL - 960, 130)

PAGE_H = FY + 160
xml = ('<mxfile host="65bd71144e"><diagram name="Wenco FMS capability" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W_TOTAL}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, W_TOTAL, PAGE_H)
