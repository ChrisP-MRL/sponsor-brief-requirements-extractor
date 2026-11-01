"""Build the Winu Epiroc D65 / LinkOA / GNSS / comms relationship diagram (.drawio).
Same style as output/Winu/Winu_GNSS_RTK_Capability.drawio (swimlanes left to right, coloured boxes).
Usage: python winu_linkoa_drill_drawio.py <output.drawio>

Figures are taken from:
  - output/Winu/Winu_Mine_Schedule_First_24_Months.xlsx (Summary, Schedule, Fleet_Register; recalculated in Excel)
  - input/Vendor/Epiroc/MRL D65 LinkOA Technology {Drill,Office,Software}.pdf (AUC-ADS-JH-EST, 30/01/2026)
  - the GNSS / RTK / comms boxes reuse output/Winu/Winu_GNSS_RTK_Capability.drawio
Yellow boxes are assumptions or open items, not stated in the sources."""
import sys, html

out = sys.argv[1]

# fill, stroke
C = {"ref": ("#d5e8d4", "#82b366"), "link": ("#ffe6cc", "#d79b00"), "gap": ("#f8cecc", "#b85450"),
     "rig": ("#dae8fc", "#6c8ebf"), "off": ("#b0e3e6", "#0e8088"), "out": ("#e1d5e7", "#9673a6"),
     "chk": ("#fff2cc", "#d6b656"), "grey": ("#f5f5f5", "#666666")}

LANE_X0, LANE_W, LANE_GAP, LANE_Y, LANE_H = 20, 270, 40, 80, 385
BOX_W, BOX_H, BOX_DX = 230, 68, 20
ROWS = [125, 210, 295, 380]

LANES = [
    "1. GNSS reference (GPS positioning)",
    "2. Correction link",
    "3. D65 drill rig (on-board)",
    "4. Site data network (comms)",
    "5. Office (off-board)",
    "6. Outputs",
]

# key: (lane 0-5, row 0-3, colour, text)
B = {
    "sat": (0, 0, "grey", "GNSS satellites (GPS + other constellations)\nsignals seen by base and by rig receiver"),
    "base": (0, 1, "ref", "Trimble R750 permanent site base +\nZephyr 3 antenna; R980 x2 spare / mobile base"),
    "ctl": (0, 2, "chk", "Surveyed control point; datum MGA94 Zone 51 / AHD\n(LiDAR map), GDA2020 unconfirmed; survey control\nexcluded from Contractor scope"),
    "uhf": (1, 0, "link", "Trimble TDL450B UHF radio\nsite-wide RTK broadcast (line of sight, repeaters)"),
    "ntrip": (1, 1, "link", "Internet / NTRIP corrections\n(4G / satellite backhaul) - fallback or where\nUHF is shadowed"),
    "shadow": (1, 2, "chk", "Pit deepens to ~70 m (Summary): UHF line of sight\nneeds repeaters kept on the pit rim - confirm"),
    "gnss": (2, 0, "chk", "GNSS RTK receiver + antenna on rig:\nhole collar position and navigation\n(not in Epiroc quote - confirm fitted, RTK format)"),
    "rig": (2, 1, "rig", "Epiroc D65 MKII blasthole drill rig\n2 rigs from M1, peak 5 (Jul-Nov 28, Jan-Feb 29)\n~200 mm hole, 11 m, 28-38 m/h net"),
    "onb": (2, 2, "rig", "On-board LinkOA / automation software\nEpiroc SW alignment + configuration of the D65\n(Onboard estimate)"),
    "go": (2, 3, "rig", "Go-live: 6 days Epiroc specialist on site\n(2 x 3-day blocks recommended; scope TBD)"),
    "mesh": (3, 0, "gap", "Temporary Contractor radio + FMS mesh,\nrepeater trailers (Company TETRA NOT available)\ncarries rig traffic to the pit edge"),
    "bh": (3, 1, "link", "Site backhaul to MinRes environment\n(4G / satellite; link capacity and latency\nfor LinkOA not stated in quote)"),
    "rem": (3, 2, "link", "Epiroc remote access into MRL environment\nfor set-up and commissioning (Office quote)"),
    "srv": (4, 0, "off", "LinkOA + SAMS (off-board) hosted in MRL environment\nEpiroc assists set-up; MinRes supplies network +\nsupporting hardware to Epiroc requirements"),
    "lic": (4, 2, "off", "LinkOA annual licence x 6 @ $25,542\n= $153,252 (excludes remote support - via Epiroc\nservice department)"),
    "set": (4, 3, "off", "Office set-up: specialist 48 h $11,328;\ntraining 3 days $6,786.15 = $18,114.15"),
    "des": (4, 1, "chk", "Blast design / design TIN from Mine Planner and\nsurveyor to rig - path assumed (not in quote)"),
    "as": (5, 0, "out", "As-drilled hole collars, depth and drilling data\nreported through LinkOA (per Drill quote:\n'effective LinkOA reporting')"),
    "kpi": (5, 1, "out", "Drilled-vs-plan: 60,943 holes, 670,371 m\nover ~21 months; peak ~47,100 m/month;\n28,897 rig hours"),
    "chg": (5, 2, "out", "Blast loading reconciliation: one electronic\ndetonator per hole (60,943) and 6,283 t bulk\nemulsion for the MPU / charging unit"),
    "ps": (5, 3, "chk", "Survey and FMS reconciliation: link to production\nreconciliation / Wenco FMS exports - interface\nnot defined in sources"),
}

# source, target, label, dashed
E = [
    ("sat", "base", "GNSS signals", False),
    ("base", "uhf", "RTK corrections", False),
    ("base", "ntrip", "NTRIP", False),
    ("uhf", "gnss", "UHF RTK", False),
    ("ntrip", "gnss", "IP (fallback)", True),
    ("gnss", "rig", "position", False),
    ("rig", "onb", "machine data", False),
    ("onb", "mesh", "LinkOA data", False),
    ("mesh", "bh", "", False),
    ("bh", "srv", "IP", False),
    ("rem", "srv", "remote access", True),
    ("des", "srv", "designs", True),
    ("srv", "as", "reports", False),
    ("as", "kpi", "", False),
    ("kpi", "chg", "", False),
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
text("Winu Pre-Strip - Epiroc D65 / LinkOA drill capability with GNSS (GPS) and comms", 20, 10, W_TOTAL - 40, 30, 18, True)
text("Source: Epiroc estimates AUC-ADS-JH-EST 30/01/2026 (Onboard, Offboard, Software); Winu_Mine_Schedule_First_24_Months.xlsx; "
     "Winu_GNSS_RTK_Capability.drawio. Yellow = assumption or open item.", 20, 38, W_TOTAL - 40, 20, 11)

lane_id = {}
for i, name in enumerate(LANES):
    lane_id[i] = add("swimlane;startSize=30;rounded=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;fontStyle=1;swimlaneFillColor=#fafafa;",
                     esc(name), LANE_X0 + i * (LANE_W + LANE_GAP), LANE_Y, LANE_W, LANE_H)

box_id = {}
for k, (ln, rw, col, t) in B.items():
    fill, stroke = C[col]
    box_id[k] = add(f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;",
                    esc(t), LANE_X0 + ln * (LANE_W + LANE_GAP) + BOX_DX, ROWS[rw], BOX_W, BOX_H)

for s, t, lab, dashed in E:
    i = nid()
    sl, tl = B[s][0], B[t][0]
    if sl == tl:    # vertical hop inside a lane
        ex, ey, nx, ny = (0.5, 1, 0.5, 0) if B[s][1] < B[t][1] else (0.5, 0, 0.5, 1)
    elif B[s][1] == B[t][1]:
        ex, ey, nx, ny = 1, 0.5, 0, 0.5
    else:
        ex, ey, nx, ny = 1, 0.5, 0, 0.5
    st = (f"endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#333333;edgeStyle=none;fontSize=10;labelBackgroundColor=#ffffff;"
          f"exitX={ex};exitY={ey};entryX={nx};entryY={ny};" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{box_id[s]}" target="{box_id[t]}" style="{st}" value="{esc(lab)}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')

LY = LANE_Y + LANE_H + 20
text("Relative drill location (no pit or drill coordinates in the Technical Info register; distances are schedule-model assumptions measured from the pit)",
     20, LY, W_TOTAL - 40, 22, 12, True, "left")
LOC = [
    ("rig", "Drill working area: pit Cutbacks 1+2 (~60 ha)\n10 m benches down to ~70 m; D65 rigs drill one\nmonth ahead of the dig face"),
    ("chk", "Drill position = bench pattern set out on the\ndesign TIN / 2025 LiDAR surface; existing bores\ninside Cutback 1 (e.g. WINU0076) decommissioned Yr 1"),
    ("ref", "Base station / repeater position: not in register -\nsite on the pit rim or infrastructure area with line\nof sight to benches (assumed, confirm)"),
    ("grey", "ROM pad / infrastructure fill\n3.5 km from pit (assumed)"),
    ("grey", "Waste rock landform\n4.0 km from pit (assumed)"),
    ("grey", "TSF Stage 0 reference axis\n4.9 km from pit (C0007-2300-G-PRE-00002)"),
    ("grey", "In-pit: 0.6 km flat haul to a 10% ramp;\nborrow pit ~3 km lead (assumed)"),
]
lw = (W_TOTAL - 40 - 6 * 12) // 7
for i, (col, t) in enumerate(LOC):
    fill, stroke = C[col]
    add(f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;", esc(t),
        20 + i * (lw + 12), LY + 26, lw, 68)
FY = LY + 26 + 68 + 20
note = ("Commercial basis (Epiroc estimates dated 30/01/2026, excl. GST, customer site shown as Kens Bore):\n"
        "Onboard $16,992 (6 days specialist labour, mob / flights / car hire TBD) + Offboard $18,114.15 (mob TBD) "
        "+ Software $153,252 (6 licences, annual) = $188,358.15 before TBD items.\n"
        "Schedule basis: drilling starts M1 (Dec-27) one month ahead of mining and ends Aug-29.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(note), 20, FY, 900, 110)
openi = ("Open items to resolve with Epiroc / MinRes:\n"
         "1. Quote is for Kens Bore and its 90-day validity lapsed 30/04/2026 - re-quote for Winu.\n"
         "2. Licences quoted x 6; schedule peaks at 5 D65 (plus 1 ore-only pre-split rig that is not a D65) - confirm count.\n"
         "3. Software total is shown as AUD software but also under USD miscellaneous - confirm currency.\n"
         "4. GNSS option, RTK format (UHF vs NTRIP) and data bandwidth over the temporary mesh are not in the quotes.\n"
         "5. LinkOA to Wenco FMS / survey interface not defined; Company TETRA unavailable.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(openi), 940, FY, W_TOTAL - 960, 110)

PAGE_H = FY + 140
xml = ('<mxfile host="65bd71144e"><diagram name="LinkOA D65 drill" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W_TOTAL}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, W_TOTAL, PAGE_H)
