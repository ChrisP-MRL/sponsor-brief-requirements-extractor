"""Build the Winu GroundProbe slope stability radar capability diagram (.drawio).
Same style as output/Winu/Winu_LinkOA_D65_Drill_Capability.drawio and Winu_GNSS_RTK_Capability.drawio (swimlanes left to right).
Usage: python winu_groundprobe_drawio.py <output.drawio>

Figures are taken from input/Vendor/GroundProbe/GroundProbe.md (a generic GroundProbe / Orica Digital Solutions
implementation guide: no Winu quote, radar count or price). Winu pit context reuses the LinkOA diagram.
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
    "1. Monitored area (Winu pit)",
    "2. Site installation",
    "3. GroundProbe sensors",
    "4. Site data network (comms)",
    "5. Software and integration",
    "6. Outputs and decisions",
]

# key: (lane 0-5, row 0-3, colour, text)
B = {
    "pit": (0, 0, "rig", "Open pit Cutbacks 1+2 (~60 ha), 10 m benches\ndeepening to ~70 m: high-wall stability is the\nmain target (pre-strip ~21.6 Mbcm overburden)"),
    "scope": (0, 1, "grey", "Initial 2-year scope: PIT WALL monitoring only.\nOUT of scope: TSF (tailings dam) and waste rock\nlandform / dump monitoring (revisit after year 2)"),
    "trig": (0, 2, "grey", "Hazard triggers named in guide: blasting vibration,\nheavy equipment, rainfall / weather, seismic\nactivity and excavation undercutting"),
    "xt": (2, 0, "rig", "SSR-XT: 3D Real Aperture Radar, targeted and\nsafety-critical, mobile; 30 m to 5,600 m range\n(pit high-wall)"),
    "fx": (2, 1, "rig", "SSR-FX: 2D RAR broad-area, fast update across\nbenches; shares hardware and software with XT\n(interchangeable parts, common training)"),
    "rgr": (2, 2, "chk", "RGR-Velox reactive radar: tracks a collapse already\nunderway; sirens, lights, digital alerts. Radar mix\nand count for Winu NOT defined - confirm"),
    "mnt": (1, 0, "chk", "Rigid, vibration-isolated mounting pad with line of\nsight to the benches and safe service access;\nsite on pit rim - positions not in register"),
    "pwr": (1, 1, "chk", "Power: grid + UPS, hybrid solar-battery (guide: up to\n38% lower consumption) or generator backup;\nWinu remote pit rim - choice not made"),
    "ctl": (1, 2, "ref", "Reference points and common coordinate frame with\nmine survey; DEM alignment to 2025 LiDAR; datum\nMGA94 Zone 51 / AHD (GDA2020 unconfirmed)"),
    "cal": (1, 3, "chk", "Calibration and acceptance: accuracy checks against\nknown references, controlled test movements;\nperiodic re-calibration (guide s4.2, s8.1)"),
    "rad": (3, 0, "gap", "Radar-to-base wireless link (guide: no long cables);\ntemporary Contractor radio + FMS mesh, Company\nTETRA NOT available - capacity not confirmed"),
    "red": (3, 1, "link", "Redundant paths (LTE / 5G, dedicated radio, mesh)\nand encrypted channels; communication redundancy\nrecommended for safety-critical radar"),
    "bh": (3, 2, "link", "Site backhaul to MinRes environment (4G / satellite);\nbandwidth and latency for radar data not stated;\nrepeaters on pit rim shared with RTK UHF (assumed)"),
    "sto": (3, 3, "chk", "Data volume: guide says potentially terabytes per\nyear; multi-year redundant storage and archive\nlocation (MRL hosted or vendor) not defined"),
    "miq": (4, 0, "off", "MonitorIQ Next (Desktop) with SSR-Viewer embedded:\nsite setup of pit geometry, zones, sensor positions,\nrole-based access (geotech, ops, safety, supervisors)"),
    "atm": (4, 1, "off", "Precision Atmospherics correction of atmospheric\nnoise; six stackable alarm types that trigger in\nsequence ahead of failure"),
    "fus": (4, 2, "link", "Multi-sensor fusion: GNSS monitoring, robotic total\nstations (Trimble 4D Control), piezometers, cameras;\nWinu GNSS base and bore data reuse - assumed"),
    "ent": (4, 3, "chk", "Enterprise links: REST API / OPC-UA to mine mgmt,\nSCADA, Wenco FMS, block model and scheduling;\ninterfaces not defined in sources"),
    "alm": (5, 0, "out", "Alarms and TARP: threshold alerts to geotech, ops\nand safety; escalation, equipment withdrawal,\nevacuation of the pit floor and shutdown criteria"),
    "pln": (5, 1, "out", "Mine planning feedback: pit sequencing, equipment\npositioning and production rate within geotech\nlimits; slope behaviour vs geology (block model)"),
    "aud": (5, 2, "out", "Geotech reports, audit trail and data archive for\nregulatory due diligence (system configuration,\nmaintenance, alert and response records)"),
    "sup": (5, 3, "out", "Operations support: 24/7 GroundProbe support desk,\npreventive maintenance, health monitoring, critical\nspares, trained geotech and ops users"),
}

# source, target, label, dashed
E = [
    ("pit", "mnt", "radar view", False),
    ("mnt", "xt", "hosts", False),
    ("xt", "rad", "radar data", False),
    ("rad", "miq", "IP", False),
    ("miq", "alm", "alarms", False),
    ("pwr", "fx", "powers", False),
    ("fx", "red", "", False),
    ("red", "atm", "", False),
    ("atm", "pln", "", False),
    ("ctl", "xt", "datum", False),
    ("rgr", "bh", "alerts", False),
    ("bh", "fus", "", False),
    ("fus", "aud", "", False),
    ("miq", "atm", "", False),
    ("alm", "pln", "", False),
    ("pln", "aud", "", False),
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
text("Winu Pre-Strip - GroundProbe pit wall slope stability radar capability (initial 2 years; TSF and waste landform out of scope)", 20, 10, W_TOTAL - 40, 30, 18, True)
text("Source: input/Vendor/GroundProbe/GroundProbe.md (generic vendor implementation guide, no Winu quote); site context from "
     "Winu_LinkOA_D65_Drill_Capability.drawio and Winu_GNSS_RTK_Capability.drawio. Yellow = assumption or open item.", 20, 38, W_TOTAL - 40, 20, 11)

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
    else:
        ex, ey, nx, ny = 1, 0.5, 0, 0.5
    st = (f"endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#333333;edgeStyle=none;fontSize=10;labelBackgroundColor=#ffffff;"
          f"exitX={ex};exitY={ey};entryX={nx};entryY={ny};" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{box_id[s]}" target="{box_id[t]}" style="{st}" value="{esc(lab)}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')

LY = LANE_Y + LANE_H + 20
text("Relative radar location (no pit, radar or base coordinates in the Technical Info register; distances are assumptions measured from the pit)",
     20, LY, W_TOTAL - 40, 22, 12, True, "left")
LOC = [
    ("rig", "Radar coverage zone: pit Cutbacks 1+2 high-walls;\nXT / FX within 30 m to 5,600 m of the slope,\ncovering the whole pit from the rim"),
    ("chk", "Radar position: pit rim or crest pad with line of sight\nto the walls, clear of blast fly-rock and haul roads;\nre-sited as the pit deepens (assumed, confirm)"),
    ("ref", "Power and comms node: shared with the GNSS base /\nUHF repeater on the pit rim or infrastructure area\n(assumed, confirm)"),
    ("grey", "ROM pad / infrastructure fill\n3.5 km from pit (assumed)"),
    ("grey", "OUT of initial 2-year scope: waste rock landform\n(4.0 km from pit) and TSF Stage 0 (4.9 km from pit)\nmonitoring"),
    ("grey", "In-pit: 0.6 km flat haul to a 10% ramp;\nborrow pit ~3 km lead (assumed)"),
]
lw = (W_TOTAL - 40 - 5 * 12) // 6
for i, (col, t) in enumerate(LOC):
    fill, stroke = C[col]
    add(f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;", esc(t),
        20 + i * (lw + 12), LY + 26, lw, 68)
FY = LY + 26 + 68 + 20
note = ("Commercial basis: NONE in the source. GroundProbe.md is a generic Orica Digital Solutions implementation guide with no\n"
        "quote, price, radar count, lease terms or delivery dates (cost drivers listed: number/type of systems, site infrastructure,\n"
        "MonitorIQ Next subscription, integration engineering). The guide cites trial leasing (Thompson Creek) as a way to reduce adoption risk.\n"
        "Schedule basis: drilling and digging start M1 (Dec-27); first radar needed before cutback walls build height (assumed).")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(note), 20, FY, 900, 110)
openi = ("Open items to resolve with GroundProbe / MinRes Geotechnical:\n"
         "1. No Winu-specific design: radar mix (XT / FX / RGR-Velox), count and lease vs purchase to be scoped.\n"
         "2. Pit-wall design, slope TARP and alarm thresholds come from the Geotechnical Engineer - not in the guide.\n"
         "3. Power and comms at radar pads (remote pit rim): grid, solar-battery or generator; bandwidth over the temporary mesh.\n"
         "4. Interfaces to Wenco FMS, SCADA and survey / GNSS not defined; Company TETRA unavailable.\n"
         "5. Contractor vs Company scope (survey control and radios are excluded from Contractor scope) - confirm with EPC.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(openi), 940, FY, W_TOTAL - 960, 110)

PAGE_H = FY + 140
xml = ('<mxfile host="65bd71144e"><diagram name="GroundProbe slope radar" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W_TOTAL}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, W_TOTAL, PAGE_H)
