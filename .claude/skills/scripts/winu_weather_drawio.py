"""Build the Winu Weatherzone weather and alerting capability diagram (.drawio and .png).
Same style as output/Winu/Winu_GNSS_RTK_Capability.drawio (swimlanes left to right, coloured boxes).
Usage: python winu_weather_drawio.py <output.drawio> <output.png> <Weatherzone_Winu_Requirements_updated.xlsx>

Prices, quantities and totals come from the 'Winu Cost Estimate' worksheet (unit price x qty x include switch;
annual rows vs one-off rows follow the Annual recurring / One-off columns). Only packages with Include = 1 are drawn
as selected. Yellow boxes are open items or judgement calls."""
import sys, html, os, shutil, tempfile
import openpyxl

out_drawio, out_png, src = sys.argv[1:4]

# ---- read the cost estimate (copy first: the source may be locked by Excel / OneDrive) ----
tmp = os.path.join(tempfile.mkdtemp(), "wz.xlsx")
shutil.copyfile(src, tmp)
ws = openpyxl.load_workbook(tmp)["Winu Cost Estimate"]
P = {}          # key -> dict(unit, qty, inc, annual?)
for r in range(2, ws.max_row + 1):
    name, unit, qty, inc, f, g = (ws.cell(r, c).value for c in (1, 3, 4, 5, 6, 7))
    if not (name and str(name).startswith("Package") and isinstance(unit, (int, float))):
        continue
    key = name.split(" ")[1]
    if "AWS" in name:
        key = "6b_cap"
    elif "monitoring" in name:
        key = "6b_ann"
    elif key == "7" and "hardware" in name:
        key = "7_cap"
    elif key == "7":
        key = "7_ann"
    P[key] = dict(val=unit * qty * inc, qty=qty, inc=inc, unit=unit, annual=str(f).startswith("="))
TOT_ANN = sum(p["val"] for p in P.values() if p["annual"])
TOT_ONE = sum(p["val"] for p in P.values() if not p["annual"])


def usd(k):
    return f"${P[k]['val']:,.0f}"


R35 = P["3"]["val"] + P["3b"]["val"] + P["3c"]["val"]

# fill, stroke
C = {"ref": ("#d5e8d4", "#82b366"), "link": ("#ffe6cc", "#d79b00"), "gap": ("#f8cecc", "#b85450"),
     "rig": ("#dae8fc", "#6c8ebf"), "out": ("#e1d5e7", "#9673a6"), "chk": ("#fff2cc", "#d6b656")}

LANE_X0, LANE_W, LANE_GAP, LANE_Y, LANE_H = 20, 330, 60, 80, 720
BOX_W, BOX_DX, BOX_H, ROW0, ROW_STEP = 290, 20, 76, 50, 94
LANES = ["1. Weather data sources", "2. Weatherzone packages (required)", "3. Delivery to Winu", "4. Winu outputs and decisions"]

# key: (lane, row, colour, text)
B = {
    "ltn": (0, 0, "ref", "WZTLN lightning detection network\nstrike data around the Winu site"),
    "nwp": (0, 1, "ref", "NWP models + Weatherzone forecast engine\nhourly site forecast, 10-minute update"),
    "met": (0, 2, "ref", "Weatherzone meteorologists\n24/7 access in cyclone events"),
    "rad": (0, 3, "ref", "Oracle synthetic radar + BOM radar\ncoverage where no BOM radar; nowcast to 3 h"),
    "sta": (0, 4, "link", f"On-site weather station, WMO standard\ninstalled + maintained by Weatherzone\nalso supplies site obs to Pkg 2"),
    "air": (0, 5, "link", "Airstrip AWS + AWIS (Aerodrome Weather\nInformation Service) + spares\nAustralian-Standard Aviation Weather Station"),
    "p1": (1, 0, "rig", f"Pkg 1 Lightning detection and alerting (Core)\nSMS to 100 users + unlimited email"),
    "p2": (1, 1, "rig", f"Pkg 2 Operational site-specific weather (Core)\n7-day site forecast; rain, wind, temperature"),
    "p3": (1, 2, "rig", f"Pkg 3 Tropical Cyclone (Nov-Apr)\nPkg 3b Risk Communicator\nPkg 3c Seasonal Briefings"),
    "p4": (1, 3, "rig", f"Pkg 4 Flood Risk + Oracle\ncatchment + road-corridor alerting"),
    "p5": (1, 4, "rig", f"Pkg 5 Dust Dispersion (blast management)\nblast planning on weather + observations"),
    "p6": (1, 5, "rig", f"Pkg 6 Weather Station DAAS\nPkg 6b Airport Weather Stations"),
    "bob": (2, 0, "link", f"Pkg 7 WZBob lights and sirens, {P['7_cap']['qty']} units\nhigh-traffic areas, plant, admin, camps"),
    "dash": (2, 1, "link", "Miningzone dashboard + Weatherguard app\nSMS and email alerts; forecasts, radar, reports"),
    "brief": (2, 2, "link", "Meteorologist briefings and calls\nweekly / 15-min imminent-weather briefings,\ncyclone tracking, seasonal outlooks"),
    "flood": (2, 3, "link", "Flood and road-corridor alerts\nvia Miningzone dashboard / Weatherguard app"),
    "blast": (2, 4, "link", "Automated blast and dust reports\nblast teams; audit reports available"),
    "obs": (2, 5, "link", "Aviation-standard observations feed\nAPI / dashboard (CASA-reportable)"),
    "train": (2, 6, "link", f"Pkg 8 Weather Training (2-day course)\n{P['8']['qty']} delegates assumed"),
    "o1": (3, 0, "out", "Lightning stand-down\npit, plant, camp, haul roads"),
    "o2": (3, 1, "out", "Shut + earthworks planning\n7-day forecast, rainfall, wind, fire hotspots"),
    "o3": (3, 2, "out", "Cyclone + severe weather response\nOperational Control call cadence"),
    "o4": (3, 3, "out", "Flood and road-closure decisions"),
    "o5": (3, 4, "out", "Blast go / no-go\ndust management"),
    "o6": (3, 5, "out", "Airstrip operations\nobservations for flights"),
    "o7": (3, 6, "out", "Winu staff understand weather\nevents and conditions"),
}
# (src, tgt, label): one straight chain per row, so no lines cross
E = [("ltn", "p1", "strikes"), ("nwp", "p2", "model data"), ("met", "p3", "expert input"), ("rad", "p4", "radar"),
     ("sta", "p5", "wind obs"), ("air", "p6", "obs"),
     ("p1", "bob", "trigger"), ("p2", "dash", ""), ("p3", "brief", ""), ("p4", "flood", ""), ("p5", "blast", ""), ("p6", "obs", ""),
     ("bob", "o1", ""), ("dash", "o2", ""), ("brief", "o3", ""), ("flood", "o4", ""), ("blast", "o5", ""), ("obs", "o6", ""),
     ("train", "o7", "")]


def geom(k):
    ln, row = B[k][:2]
    return LANE_X0 + ln * (LANE_W + LANE_GAP) + BOX_DX, LANE_Y + ROW0 + row * ROW_STEP, BOX_W, BOX_H


W_TOTAL = LANE_X0 * 2 + 4 * LANE_W + 3 * LANE_GAP
FY = LANE_Y + LANE_H + 20
TITLE = "Winu Pre-Strip - Weatherzone weather and alerting capability required (selected packages)"
SUB = ("Source: Weatherzone_Winu_Requirements_updated.xlsx (Winu Cost Estimate); MRL Global MSA, Weatherzone / DTN APAC (MRL Operations proposed price table). "
       "Yellow = open item or judgement call.")
NOTE = (f"Selected: Packages 1, 2, 3, 3b, 3c, 4, 5, 6, 6b, 7 ({P['7_cap']['qty']} units), 8. Not selected: Package 9 Ports.\n"
        "MSA term ends 31 May 2027; minimum 12-month PO; 24/7 support; 99.9% alerting uptime target.")
OPEN = ("Open items:\n"
        "1. Winu is not named in the MSA: confirm it is added at the core rates and the start date.\n"
        "2. Packages 3, 3b, 4 are listed per site: confirm no Pilbara regional overlap.\n"
        f"3. WZBob unit count (quote says 2 and 3), delegate count ({P['8']['qty']}) and 6b scope are assumptions.\n"
        "4. Installation scope for Package 4, 6, 6b and 7 is not defined in the quote.")

# ---------------- draw.io ----------------
cells, _n = [], [1]


def nid():
    _n[0] += 1
    return f"c{_n[0]}"


def esc(t):
    return html.escape(t, quote=True).replace("\n", "&#xa;")


def add(style, val, x, y, w, h):
    i = nid()
    cells.append(f'<mxCell id="{i}" parent="1" style="{style}" value="{esc(val)}" vertex="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i


def text(val, x, y, w, h, size=11, bold=False):
    add(f"text;html=0;align=center;verticalAlign=middle;fontSize={size};fontStyle={1 if bold else 0};whiteSpace=wrap;", val, x, y, w, h)


text(TITLE, 20, 10, W_TOTAL - 40, 30, 18, True)
text(SUB, 20, 38, W_TOTAL - 40, 20, 11)
for i, name in enumerate(LANES):
    add("swimlane;startSize=30;rounded=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;fontStyle=1;swimlaneFillColor=#fafafa;",
        name, LANE_X0 + i * (LANE_W + LANE_GAP), LANE_Y, LANE_W, LANE_H)
ids = {}
for k, (ln, row, col, t) in B.items():
    fill, stroke = C[col]
    x, y, w, h = geom(k)
    ids[k] = add(f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;", t, x, y, w, h)
for s, t, lab in E:
    i = nid()
    st = ("endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#333333;edgeStyle=none;rounded=0;fontSize=9;"
          "labelBackgroundColor=#ffffff;exitX=1;exitY=0.5;entryX=0;entryY=0.5;")
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{ids[s]}" target="{ids[t]}" style="{st}" value="{esc(lab)}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')
BOXSTYLE = "rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;"
add(BOXSTYLE, NOTE, 20, FY, 900, 100)
add(BOXSTYLE.replace("#ffffff", "#fff2cc").replace("#666666", "#d6b656"), OPEN, 940, FY, W_TOTAL - 960, 100)
PAGE_H = FY + 120
xml = ('<mxfile host="65bd71144e"><diagram name="Weather capability" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W_TOTAL}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out_drawio, "w", encoding="utf-8").write(xml)

# ---------------- PNG (matplotlib, same coordinates) ----------------
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

fig = plt.figure(figsize=(W_TOTAL / 100, PAGE_H / 100), dpi=110)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W_TOTAL)
ax.set_ylim(PAGE_H, 0)
ax.axis("off")
ax.text(W_TOTAL / 2, 25, TITLE, ha="center", va="center", fontsize=15, fontweight="bold")
ax.text(W_TOTAL / 2, 48, SUB, ha="center", va="center", fontsize=8.5)
for i, name in enumerate(LANES):
    x = LANE_X0 + i * (LANE_W + LANE_GAP)
    ax.add_patch(Rectangle((x, LANE_Y), LANE_W, LANE_H, fc="#fafafa", ec="#999999", lw=1))
    ax.add_patch(Rectangle((x, LANE_Y), LANE_W, 30, fc="#f5f5f5", ec="#999999", lw=1))
    ax.text(x + LANE_W / 2, LANE_Y + 15, name, ha="center", va="center", fontsize=10.5, fontweight="bold")
for s, t, lab in E:
    x1, y1, w1, h1 = geom(s)
    x2, y2, w2, h2 = geom(t)
    ax.add_patch(FancyArrowPatch((x1 + w1, y1 + h1 / 2), (x2, y2 + h2 / 2), arrowstyle="-|>", mutation_scale=14, lw=1.6, color="#333333",
                                 shrinkA=0, shrinkB=0, zorder=2))
    if lab:
        ax.text((x1 + w1 + x2) / 2, (y1 + y2 + h1 / 2 + h2 / 2) / 2 - 7, lab, ha="center", va="center", fontsize=7.5, zorder=4,
                bbox=dict(fc="white", ec="none", pad=1))
for k, (ln, row, col, t) in B.items():
    fill, stroke = C[col]
    x, y, w, h = geom(k)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=8", fc=fill, ec=stroke, lw=1.2, zorder=3))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=7.8, zorder=5, linespacing=1.25)
for (x, w, t, fc, ec) in ((20, 900, NOTE, "#ffffff", "#666666"), (940, W_TOTAL - 960, OPEN, "#fff2cc", "#d6b656")):
    ax.add_patch(FancyBboxPatch((x, FY), w, 100, boxstyle="round,pad=0,rounding_size=8", fc=fc, ec=ec, lw=1.2))
    ax.text(x + 10, FY + 50, t, ha="left", va="center", fontsize=8, linespacing=1.35)
fig.savefig(out_png, dpi=110)
print("wrote", out_drawio, out_png, W_TOTAL, PAGE_H, f"annual={TOT_ANN:,.0f} one-off={TOT_ONE:,.0f}")
