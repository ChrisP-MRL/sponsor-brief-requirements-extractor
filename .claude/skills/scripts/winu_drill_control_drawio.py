"""Build the Winu Drill Control System concept diagram (.drawio).
Same style as output/Winu/Winu_Wenco_FMS_Capability.drawio (swimlanes left to right, coloured boxes).
Usage: python winu_drill_control_drawio.py <output.drawio>

Figures are taken from input/Vendor/Epiroc/MRL D65 LinkOA Technology {Drill,Office,Software}.pdf (AUC-ADS-JH-EST, 30/01/2026)
and, for rig counts and drilling quantities, output/Winu/Winu_Mine_Schedule_First_24_Months.xlsx (as used in
Winu_LinkOA_D65_Drill_Capability.drawio). Yellow boxes are open items or judgement calls, not stated in the Epiroc quotes."""
import sys, html

out = sys.argv[1]

# fill, stroke
C = {"ref": ("#d5e8d4", "#82b366"), "link": ("#ffe6cc", "#d79b00"), "gap": ("#f8cecc", "#b85450"),
     "rig": ("#dae8fc", "#6c8ebf"), "off": ("#b0e3e6", "#0e8088"), "out": ("#e1d5e7", "#9673a6"),
     "chk": ("#fff2cc", "#d6b656"), "grey": ("#f5f5f5", "#666666")}

LANE_X0, LANE_W, LANE_GAP, LANE_Y, LANE_H = 20, 270, 40, 80, 500
BOX_W, BOX_DX = 230, 20

LANES = [
    "1. Positioning (GNSS RTK)",
    "2. Drill rig (on-board)",
    "3. Site network",
    "4. LinkOA + SAMS (off-board)",
    "5. Reporting + integration",
    "6. Outputs",
]

# key: (lane 0-5, y top, height, colour, text). Linked boxes in adjacent lanes share a centre line (straight arrows);
# other links use a single elbow in the gap.
B = {
    # lane 0
    "gnss": (0, 120, 64, "ref", "GNSS RTK reference (R750 base, Zephyr 3)\nsee Winu_GNSS_RTK_Capability.drawio"),
    "uhf": (0, 210, 64, "link", "RTK corrections to the rig\nUHF broadcast (line of sight, repeaters) or\nNTRIP over IP as fallback"),
    "ctl": (0, 390, 64, "chk", "Survey control and datum: MGA94 Zone 51 / AHD,\nGDA2020 unconfirmed; survey control excluded\nfrom Contractor scope"),
    # lane 1
    "rx": (1, 210, 64, "chk", "GNSS RTK receiver + antenna on each rig:\nhole collar position and navigation\nnot in Epiroc quote - confirm fitted, RTK format"),
    "rig": (1, 300, 64, "rig", "Epiroc D65 MKII blasthole drill rig\n2 rigs from M1, peak 5; ~200 mm hole, 11 m\nExcluded from Wenco FMS modules"),
    "onb": (1, 390, 64, "rig", "On-board LinkOA / automation software\nEpiroc SW alignment + configuration of the\nD65 (Onboard estimate $16,992)"),
    "go": (1, 480, 64, "rig", "Go-live support: 6 days Epiroc specialist on site\n(2 x 3-day blocks recommended; scope TBD)"),
    # lane 2
    "rem": (2, 210, 64, "link", "Epiroc remote access into MRL environment\nfor set-up and commissioning (Office quote)"),
    "bh": (2, 300, 64, "link", "Site backhaul to MinRes environment\n(4G / satellite); capacity and latency for\nLinkOA not stated in quote"),
    "mesh": (2, 390, 64, "gap", "Temporary Contractor radio + FMS mesh:\nrepeater trailers carry rig traffic to the pit edge\n(Company TETRA NOT available)"),
    # lane 3
    "des": (3, 210, 64, "chk", "Blast design / design surface from Mine Planner\nand surveyor to the rig: path assumed,\nnot in the Epiroc quotes"),
    "srv": (3, 300, 64, "off", "LinkOA + SAMS (off-board) in MRL environment\nEpiroc assists set-up; MinRes supplies network\n+ supporting hardware to Epiroc requirements"),
    "lic": (3, 390, 64, "off", "LinkOA annual licence x 6 @ $25,542 = $153,252\nexcludes remote support (Epiroc service dept)"),
    "set": (3, 480, 64, "off", "Office set-up: specialist 48 h $11,328 +\ntraining 3 days $6,786.15 = $18,114.15"),
    # lane 4
    "wen": (4, 120, 64, "chk", "Drill status / positions into Wenco FMS dispatch\nview: not defined in sources; Wencomine has\nno drill module"),
    "rpt": (4, 300, 64, "off", "LinkOA reporting: as-drilled hole collar,\ndepth and drilling data\n(Drill quote: 'effective LinkOA reporting')"),
    "sur": (4, 480, 64, "chk", "Survey and mass-haul as-built reconciliation:\ninterface not defined in sources"),
    # lane 5
    "o4": (5, 120, 64, "chk", "Drill progress visible alongside fleet in\nthe FMS view (if the feed is agreed)"),
    "o2": (5, 210, 64, "out", "Drilled-vs-plan: 60,943 holes, 670,371 m\nover ~21 months; peak ~47,100 m/month;\n28,897 rig hours (schedule model)"),
    "o1": (5, 300, 64, "out", "As-drilled hole collars, depth and drilling\ndata for blast design and reconciliation"),
    "o3": (5, 390, 64, "out", "Blast loading reconciliation: one electronic\ndetonator per hole (60,943) and 6,283 t bulk\nemulsion"),
    "o5": (5, 480, 64, "chk", "Survey / production reconciliation of\ndrilled and blasted volumes"),
}

# source, target, label, dashed
E = [
    ("gnss", "uhf", "RTK", False),
    ("uhf", "rx", "UHF / NTRIP", False),
    ("rx", "rig", "position", False),
    ("rig", "onb", "machine data", False),
    ("onb", "mesh", "LinkOA data", False),
    ("mesh", "bh", "", False),
    ("bh", "srv", "IP", False),
    ("rem", "srv", "remote access", True),
    ("des", "srv", "designs", True),
    ("srv", "rpt", "reports", False),
    ("srv", "wen", "", True),
    ("srv", "sur", "", True),
    ("rpt", "o1", "", False),
    ("rpt", "o2", "", False),
    ("rpt", "o3", "", False),
    ("wen", "o4", "", True),
    ("sur", "o5", "", True),
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
text("Winu Pre-Strip - Drill Control System concept (Epiroc D65 MKII, LinkOA + SAMS)", 20, 10, W_TOTAL - 40, 30, 18, True)
text("Source: Epiroc estimates AUC-ADS-JH-EST 30/01/2026 (Onboard, Offboard, Software); quantities from Winu_Mine_Schedule_First_24_Months.xlsx. "
     "Yellow = open item or judgement call; validate with Epiroc before pricing.", 20, 38, W_TOTAL - 40, 20, 11)

for i, name in enumerate(LANES):
    add("swimlane;startSize=30;rounded=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;fontStyle=1;swimlaneFillColor=#fafafa;",
        esc(name), LANE_X0 + i * (LANE_W + LANE_GAP), LANE_Y, LANE_W, LANE_H)

box_id = {}
for k, (ln, y, h, col, t) in B.items():
    fill, stroke = C[col]
    box_id[k] = add(f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;",
                    esc(t), LANE_X0 + ln * (LANE_W + LANE_GAP) + BOX_DX, y, BOX_W, h)

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
note = ("Commercial basis (Epiroc estimates dated 30/01/2026, excl. GST, customer site shown as Kens Bore):\n"
        "Onboard $16,992 (6 days specialist labour; mobilisation, car hire, flights TBD) + Offboard $18,114.15 (mobilisation TBD) "
        "+ Software $153,252 (6 licences, annual) = $188,358.15 before TBD items.\n"
        "Epiroc applies SW installation and configuration changes to its own deliverables only; remote support is not in the licence.\n"
        "Schedule basis: drilling starts M1 (Dec-27), one month ahead of mining, and ends Aug-29.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(note), 20, FY, 900, 130)
openi = ("Open items to resolve with Epiroc / MinRes:\n"
         "1. Quote is for Kens Bore and its 90-day validity lapsed 30/04/2026 - re-quote for Winu.\n"
         "2. Licences quoted x 6; schedule peaks at 5 D65 plus 1 ore-only pre-split rig that is not a D65 - confirm count.\n"
         "3. Software total appears under both AUD and USD lines - confirm currency. SAMS scope is not described in the quotes.\n"
         "4. Rig GNSS option, RTK format and bandwidth over the temporary mesh are not in the quotes.\n"
         "5. LinkOA to Wenco FMS and survey interfaces not defined; Company TETRA unavailable.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(openi), 940, FY, W_TOTAL - 960, 130)

PAGE_H = FY + 160
xml = ('<mxfile host="65bd71144e"><diagram name="Drill Control System" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W_TOTAL}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, W_TOTAL, PAGE_H)
