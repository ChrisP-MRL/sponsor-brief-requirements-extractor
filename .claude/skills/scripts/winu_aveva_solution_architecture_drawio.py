"""Draw the proposed AVEVA solution on the ISA-95 pyramid frame (.drawio).
Usage: python winu_aveva_solution_architecture_drawio.py <output.drawio>

Frame: output/ISA95_pyramid.drawio (see winu_isa95_pyramid_drawio.py): same pyramid, gradients, fonts and dashed connectors,
with each level stretched into a band that holds the solution components.
Sources: output/Cost estimate/AVEVA_MRL_Greenfield_Quote_Breakdown.xlsx (what is quoted: PIDI, CONNECT, Predictive Analytics,
Ampla Production Management; credits, AUD ex GST) and input/Vendor/AVEVA/AVEVA.md (capabilities, integrations, Datamine CCLAS).
Plant context (10 Mtpa Cu-Au concentrator, ~25% Cu concentrate; DCS / PLC / SCADA and ERP not named in the pack) is carried over
from winu_aveva_drawio.py. Yellow = outside the AVEVA quote or an open item."""
import sys, html, math

out = sys.argv[1] if len(sys.argv) > 1 else "Winu_AVEVA_Solution_Architecture.drawio"

# (code, name, descriptor, fill top, fill bottom) - same palette as the ISA-95 reference
LEVELS = [
    ("L4", "Business Planning & Logistics", "Enterprise planning, supply chain and logistics", "#0B3C5D", "#1D6A96"),
    ("L3", "Manufacturing Operations Management", "Production dispatch, performance, quality and maintenance", "#1D6A96", "#2E8BC0"),
    ("L2", "Monitoring & Supervising", "SCADA, HMI, alarming, historian", "#2E8BC0", "#3FA7A0"),
    ("L1", "Sensing & Local Control", "PLCs, controllers, instruments and drives", "#3FA7A0", "#5BBF8A"),
    ("L0", "Physical Process", "Plant, fleet and equipment doing the physical work", "#5BBF8A", "#8FD19E"),
]

# status -> (fill, stroke, tag colour, dashed)
ST = {"Q": ("#E3F3F1", "#1D8A84", "#12706B", 0),    # in the AVEVA quote
      "N": ("#FFF4D6", "#D6A93A", "#8A6A0F", 0),    # outside the quote / open item
      "F": ("#EEF2F6", "#9AA7B4", "#4A5866", 0),    # existing plant, field or mine system
      "R": ("#FFFFFF", "#9AA7B4", "#6B7785", 1)}    # researched, not quoted

# key: (row 0=L4..4=L0, slot, span, status, title, body, tag)
CARDS = {
    "conn":  (0, 1, 1, "Q", "AVEVA CONNECT core", "Starter: 10,000 data streams, cloud visualisation (5 users), cloud connectivity",
              "2,004 cr · $42,565/yr · svc $115,612"),
    "addon": (0, 2, 1, "Q", "CONNECT add-ons", "Enterprise data integration (Databricks, Snowflake, Fabric); Flows add-on, 500 tags",
              "1,008 cr · $21,410/yr"),
    "erp":   (0, 3, 1, "N", "ERP / BI consumers", "Financial posting, Power BI, data platforms. ERP not named in the pack; interface not quoted",
              "NOT QUOTED"),
    "res":   (0, 4, 2, "R", "Researched, not in this quote",
              "Production Accounting (mass balance, recovery, month-end), MES (sample plans, hold / release, genealogy), "
              "Unified Operations Center. Described in AVEVA.md; no licence or services line in the proposal", "RESEARCH ONLY"),
    "srv":   (1, 0, 1, "Q", "Ampla server + site", "Server with unlimited clients plus Test and Dev; one geographic site (10 km)",
              "1,008 cr · $21,410/yr"),
    "dly":   (1, 1, 1, "Q", "Delay Accounting (Ampla)", "60 units. Downtime from PI status and tablet entry; root cause, availability",
              "3,000 cr · $63,720/yr · svc $426,122"),
    "inv":   (1, 2, 1, "Q", "Inventory (Ampla)", "100 units. Inventory, material and metal accounting; ROM, WIP, concentrate by grade",
              "5,000 cr · $106,200/yr · svc $917,973"),
    "pred":  (1, 3, 1, "Q", "Predictive Analytics", "On premises, 50 models. Needs premium support, which is not priced",
              "5,796 cr · $123,107/yr · svc $226,435"),
    "lims":  (1, 4, 1, "N", "Datamine CCLAS LIMS", "Head, circuit, tail and concentrate assays (XRF, ICP). Not in the quote; Ampla interface to be specified",
              "NOT QUOTED"),
    "fms":   (1, 5, 1, "F", "Wenco FMS (mine)", "ROM ore tracking. Batch / file exports until the permanent FMS exists (SOW 6.2.16)",
              "EXISTING / OTHER SCOPE"),
    "scada": (2, 0, 1, "N", "SCADA / HMI", "Platform not named in the ITT pack; OPC source for the PI interfaces", "NOT QUOTED"),
    "edge":  (2, 1, 1, "Q", "Connectivity + Edge", "PI Connectivity Pack (all interfaces); Edge Data Store and adapters to cloud",
              "INCLUDED · $0"),
    "pi":    (2, 2, 1, "Q", "PI Server (prod + test)", "10,000-tag historian; Test PI Server included. Real-time data hub",
              "3,288 cr · $69,837/yr · svc $83,786"),
    "af":    (2, 3, 1, "Q", "PI Asset Framework", "Asset hierarchy and context so every tag maps to Winu plant equipment",
              "services only · $164,045"),
    "cli":   (2, 4, 1, "Q", "PI client packs", "2 x client pack 10 (named users) for trends and displays",
              "912 cr · $19,371/yr"),
    "dcs":   (3, 0, 1, "N", "DCS / PLC", "Crushing, grinding, flotation and dewatering control. Platform not named in the pack", "NOT QUOTED"),
    "inst":  (3, 1, 1, "F", "Instruments + analysers", "Flow, density, level, pH, mill load and power, on-stream analysers", "EXISTING / OTHER SCOPE"),
    "wgh":   (3, 2, 1, "F", "Weighing + sampling", "Belt weighers, concentrate weighing, process stream samplers", "EXISTING / OTHER SCOPE"),
    "p1":    (4, 0, 1, "F", "Crushing + grinding", "10 Mtpa primary crush, SAG / ball mill circuit", ""),
    "p2":    (4, 1, 1, "F", "Flotation + regrind", "Rougher, cleaner, scavenger cells", ""),
    "p3":    (4, 2, 1, "F", "Thickening + concentrate", "Dewatering, filtering, ~25% Cu concentrate storage", ""),
    "p4":    (4, 5, 1, "F", "Mine fleet + ROM", "Haul trucks and loaders feeding ROM", ""),
}

# (src, tgt, label, dashed, kind, params) ; kinds: straight, side, up, under, custom
EDGES = [
    ("p1", "dcs", "", 0, "up", dict(fs=.5, ft=.5)),
    ("p2", "inst", "", 0, "up", dict(fs=.5, ft=.5)),
    ("p3", "wgh", "", 0, "up", dict(fs=.5, ft=.5)),
    ("p4", "fms", "GPS / events", 1, "up", dict(fs=.7, ft=.7)),
    ("dcs", "scada", "", 0, "up", dict(fs=.5, ft=.5)),
    ("inst", "edge", "", 0, "up", dict(fs=.3, ft=.3)),
    ("wgh", "edge", "mass", 0, "up", dict(fs=.5, ft=.8, off=20)),
    ("scada", "edge", "OPC", 0, "side", {}),
    ("edge", "pi", "interfaces", 0, "side", {}),
    ("af", "pi", "context", 1, "sideback", {}),
    ("pi", "dly", "status", 0, "up", dict(fs=.25, ft=.5, off=10)),
    ("pi", "inv", "mass / flow", 0, "up", dict(fs=.5, ft=.5)),
    ("pi", "pred", "tags", 0, "up", dict(fs=.75, ft=.5, off=20)),
    ("lims", "inv", "assays", 0, "under", dict(fs=.3, ft=.85, off=30)),
    ("fms", "inv", "files", 1, "under", dict(fs=.3, ft=.65, off=42)),
    ("srv", "dly", "hosts", 1, "side", {}),
    ("dly", "conn", "events", 0, "up", dict(fs=.5, ft=.5)),
    ("inv", "addon", "", 0, "up", dict(fs=.5, ft=.5)),
    ("pred", "conn", "model results", 0, "up", dict(fs=.5, ft=.85, off=25)),
    ("addon", "erp", "", 0, "side", {}),
    ("edge", "conn", "Edge Data Store to cloud", 1, "edgecloud", {}),
]

CAPS = [
    ("Delay accounting", "Ampla Delay Accounting fed by PI status and tablet entry: downtime by cause and equipment, availability",
     "$63,720/yr + svc $426,122"),
    ("Inventory + metal accounting", "Ampla Inventory with CCLAS assays and PI mass / flow: ROM, WIP and concentrate stock by grade, metal balance",
     "$106,200/yr + svc $917,973"),
    ("Predictive analytics", "50 on-premises models on PI data for early warning and process optimisation",
     "$123,107/yr + svc $226,435"),
    ("Real-time data foundation", "PI Server 10,000 tags, Asset Framework model, interfaces to plant sources, 2 client packs",
     "$89,208/yr + svc $247,831"),
    ("Cloud + enterprise integration", "CONNECT core and add-ons: cloud visualisation, Databricks / Snowflake / Fabric feeds, integration across all four offers",
     "$73,011/yr + svc $145,489"),
]

# ---- geometry -----------------------------------------------------------------------------------------------------
CX, TOP, LAYER_H, GAP, BASE_HALF = 210, 130, 150, 6, 190
H = len(LEVELS) * LAYER_H + (len(LEVELS) - 1) * GAP
slope = BASE_HALF / H
hw = lambda y: slope * (y - TOP)
BAND_X, BAND_W = 420, 1580
CARD_X0, SLOT_W, CARD_W, CARD_Y, CARD_H = 565, 240, 224, 22, 106
FONT = "fontFamily=Helvetica;"
PAGE_W = 2020

def row_y(r): return TOP + r * (LAYER_H + GAP)
def box(k):
    r, s, sp = CARDS[k][:3]
    return CARD_X0 + s * SLOT_W, row_y(r) + CARD_Y, CARD_W + (sp - 1) * SLOT_W, CARD_H

cells, n = [], 1
def nid():
    global n; n += 1; return f"v{n}"
def vertex(style, val, x, y, w, h):
    i = nid()
    cells.append(f'<mxCell id="{i}" parent="1" style="{style}" value="{html.escape(val, quote=True)}" vertex="1">'
                 f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')
    return i
def line(style, x1, y1, x2, y2):
    i = nid()
    cells.append(f'<mxCell id="{i}" parent="1" style="{style}" edge="1"><mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="{x1:.0f}" y="{y1:.0f}" as="sourcePoint"/><mxPoint x="{x2:.0f}" y="{y2:.0f}" as="targetPoint"/></mxGeometry></mxCell>')

# ---- title and cost summary ---------------------------------------------------------------------------------------
vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=24;fontStyle=1;fontColor=#0B3C5D;{FONT}",
       "Winu Operational Intelligence: Proposed AVEVA Solution on the ISA-95 Hierarchy", 40, 16, 1200, 36)
vertex(f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=13;fontColor=#6B7785;{FONT}",
       "Four AVEVA offers (PI Data Infrastructure, CONNECT, Predictive Analytics, Ampla Production Management) turn plant data into delay, "
       "inventory and metal accounting for the 10 Mtpa Cu-Au concentrator. Teal = in the AVEVA quote; yellow = outside the quote or open.",
       40, 54, 1180, 44)
vertex(f"rounded=1;arcSize=8;html=1;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor=#D5DDE5;shadow=1;align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;fontSize=11;{FONT}",
       '<b style="font-size:13px;color:#0B3C5D">Year 1 budget: $2,440,506 ex GST</b><br>'
       '<span style="color:#44505C">Software $476,656 / yr recurring (22,016 Flex credits at $21.24) + AVEVA services $1,963,850 one-off '
       '(non-binding, +/-50%). Hardware: none quoted, MRL IT/OT to size.</span>', 1260, 12, 740, 86)

# ---- pyramid and bands --------------------------------------------------------------------------------------------
QUOTED_PER_LEVEL = {r: sum(1 for c in CARDS.values() if c[0] == r and c[3] == "Q") for r in range(5)}
for i, (code, name, desc, c1, c2) in enumerate(LEVELS):
    y = row_y(i); yb = y + LAYER_H
    w_top, w_bot = hw(y), hw(yb)
    cy = y + LAYER_H / 2
    grad = f"fillColor={c1};gradientColor={c2};gradientDirection=south;strokeColor=#FFFFFF;strokeWidth=2;"
    label = f'<b style="font-size:22px">{code}</b>'
    if i == 0:
        vertex(f"shape=triangle;direction=north;html=1;{grad}shadow=1;fontColor=#FFFFFF;verticalAlign=bottom;spacingBottom=6;{FONT}",
               label, CX - w_bot, y, 2 * w_bot, LAYER_H)
    else:
        vertex(f"shape=trapezoid;perimeter=trapezoidPerimeter;fixedSize=1;size={w_bot - w_top:.1f};html=1;{grad}shadow=1;fontColor=#FFFFFF;{FONT}",
               label, CX - w_bot, y, 2 * w_bot, LAYER_H)
    line("endArrow=oval;endFill=1;endSize=5;startArrow=none;dashed=1;strokeColor=#9AA7B4;strokeWidth=1.5;",
         BAND_X, cy, CX + (w_top + w_bot) / 2 - 4, cy)
    # band, accent bar, level label, quoted-component count
    vertex(f"rounded=1;arcSize=3;html=1;fillColor={'#F6F9FC' if i % 2 == 0 else '#EEF3F8'};strokeColor=#D5DDE5;", "", BAND_X, y, BAND_W, LAYER_H)
    vertex(f"rounded=0;html=1;fillColor={c1};gradientColor={c2};gradientDirection=south;strokeColor=none;", "", BAND_X, y + 6, 8, LAYER_H - 12)
    vertex(f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;spacingLeft=6;{FONT}",
           f'<b style="font-size:12px;color:#0B3C5D">LEVEL {code[1]}: {html.escape(name.upper())}</b><br>'
           f'<span style="font-size:10px;color:#6B7785">{html.escape(desc)}</span>', BAND_X + 14, y + 8, 128, 92)
    q = QUOTED_PER_LEVEL[i]
    vertex(f"ellipse;html=1;fillColor={c1};strokeColor=none;fontColor=#FFFFFF;fontSize=15;fontStyle=1;{FONT}", str(q), BAND_X + 20, y + 102, 36, 36)
    vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=9;fontColor=#6B7785;whiteSpace=wrap;{FONT}",
           "AVEVA components in the quote", BAND_X + 62, y + 102, 80, 36)

# left-hand axis
ax = 60
line("endArrow=block;startArrow=block;endFill=1;startFill=1;strokeColor=#9AA7B4;strokeWidth=2;", ax, TOP + 6, ax, TOP + H - 6)
vertex(f"text;html=1;align=center;verticalAlign=middle;fontSize=11;fontColor=#6B7785;fontStyle=1;{FONT}", "BUSINESS", ax - 40, TOP - 22, 80, 18)
vertex(f"text;html=1;align=center;verticalAlign=middle;fontSize=11;fontColor=#6B7785;fontStyle=1;{FONT}", "PHYSICAL", ax - 40, TOP + H + 4, 80, 18)

# ---- cards --------------------------------------------------------------------------------------------------------
ids = {}
for k, (r, s, sp, st, title, body, tag) in CARDS.items():
    x, y, w, h = box(k)
    fill, stroke, tagc, dashed = ST[st]
    val = (f'<b style="font-size:12px;color:#0B3C5D">{html.escape(title)}</b><br>'
           f'<span style="font-size:10px;color:#44505C">{html.escape(body)}</span>')
    if tag:
        val += f'<br><b style="font-size:9px;color:{tagc}">{html.escape(tag)}</b>'
    est = 8 + math.ceil(len(title) / (w / 7.2 - 3)) * 15 + math.ceil(len(body) / (w / 5.4 - 3)) * 13 + (math.ceil(len(tag) / (w / 5.2 - 3)) * 12 if tag else 0)
    if est > h:
        print(f"WARN card {k} text may overflow: est {est} > {h}")
    ids[k] = vertex(f"rounded=1;arcSize=6;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacingLeft=10;spacingRight=8;spacingTop=4;"
                    f"fillColor={fill};strokeColor={stroke};strokeWidth={2 if st == 'Q' else 1};{'dashed=1;' if dashed else ''}{FONT}",
                    val, x, y, w, h)

# ---- edges --------------------------------------------------------------------------------------------------------
def edge(s, t, label, dashed, ex, ey, nx, ny, pts):
    i = nid()
    p = "".join(f'<mxPoint x="{px:.0f}" y="{py:.0f}"/>' for px, py in pts)
    arr = f'<Array as="points">{p}</Array>' if pts else ""
    st = (f"endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#44505C;rounded=0;jumpStyle=arc;jumpSize=8;fontSize=9;"
          f"labelBackgroundColor=#FFFFFF;exitX={ex};exitY={ey};entryX={nx};entryY={ny};" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{ids[s]}" target="{ids[t]}" style="{st}" value="{html.escape(label, quote=True)}">'
                 f'<mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')

for s, t, label, dashed, kind, p in EDGES:
    sx, sy, sw, sh = box(s); tx, ty, tw, th = box(t)
    if kind == "side":
        edge(s, t, label, dashed, 1, .5, 0, .5, [])
    elif kind == "sideback":
        edge(s, t, label, dashed, 0, .5, 1, .5, [])
    elif kind == "up":
        fs, ft, off = p["fs"], p["ft"], p.get("off", 0)
        xs, xt = sx + fs * sw, tx + ft * tw
        pts = [] if abs(xs - xt) < 1 else [(xs, ty + th + off), (xt, ty + th + off)]
        edge(s, t, label, dashed, fs, 0, ft, 1, pts)
    elif kind == "under":
        fs, ft, off = p["fs"], p["ft"], p["off"]
        xs, xt = sx + fs * sw, tx + ft * tw
        yc = sy + sh + off
        edge(s, t, label, dashed, fs, 1, ft, 1, [(xs, yc), (xt, yc)])
    elif kind == "edgecloud":
        # Edge card up through the gap between slots 0 and 1, into the CONNECT core card
        gx = CARD_X0 + SLOT_W - (SLOT_W - CARD_W) / 2
        y_lo = box("dly")[1] + CARD_H + 46          # channel under the L3 cards
        y_hi = ty + th + 10                          # channel under the L4 cards
        fs = 0.03
        edge(s, t, label, dashed, fs, 0, .06, 1,
             [(sx + fs * sw, y_lo), (gx, y_lo), (gx, y_hi), (tx + .06 * tw, y_hi)])

# ---- legend -------------------------------------------------------------------------------------------------------
LY = TOP + H + 34
vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=11;fontStyle=1;fontColor=#0B3C5D;{FONT}", "KEY", 40, LY, 40, 20)
lx = 90
for st, text in [("Q", "In the AVEVA quote (credits are annual Flex; svc = one-off services)"), ("N", "Not in the quote / open item"),
                 ("F", "Existing plant, field or other-scope system"), ("R", "Researched, not quoted")]:
    fill, stroke, _, dashed = ST[st]
    vertex(f"rounded=1;html=1;fillColor={fill};strokeColor={stroke};{'dashed=1;' if dashed else ''}", "", lx, LY + 3, 22, 14)
    wtxt = 7 * len(text) + 20
    vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=10;fontColor=#44505C;{FONT}", text, lx + 28, LY, wtxt, 20)
    lx += 28 + wtxt + 14
vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=10;fontColor=#44505C;{FONT}",
       "Solid arrow = data flow up the hierarchy; dashed = batch file, optional or context link", lx, LY, 520, 20)

# ---- capability strip ---------------------------------------------------------------------------------------------
CY = LY + 40
vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=16;fontStyle=1;fontColor=#0B3C5D;{FONT}",
       "Capabilities the proposed solution delivers", 40, CY, 700, 26)
CW, CG = 380, 20
for i, (name, desc, cost) in enumerate(CAPS):
    x = 20 + i * (CW + CG)
    vertex("rounded=1;arcSize=6;html=1;fillColor=#FFFFFF;strokeColor=#D5DDE5;shadow=1;", "", x, CY + 32, CW, 112)
    vertex("rounded=0;html=1;fillColor=#1D8A84;strokeColor=none;", "", x, CY + 38, 6, 100)
    vertex(f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;spacingLeft=6;{FONT}",
           f'<b style="font-size:13px;color:#0B3C5D">{html.escape(name)}</b><br>'
           f'<span style="font-size:10px;color:#44505C">{html.escape(desc)}</span><br>'
           f'<b style="font-size:10px;color:#12706B">{html.escape(cost)}</b>', x + 14, CY + 38, CW - 24, 100)

# ---- open items ---------------------------------------------------------------------------------------------------
OY = CY + 160
vertex(f"rounded=1;arcSize=4;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;fillColor=#FFF4D6;strokeColor=#D6A93A;fontSize=10;{FONT}",
       '<b style="font-size:12px;color:#8A6A0F">Open items to resolve with AVEVA and MRL IT/OT</b><br>'
       '1. CONNECT printed total $73,011 vs $63,975 derived from credits (+$9,036); the line figures above are derived. '
       '2. Delay Accounting is 60 units against a printed minimum of 100: up to +$42,480/yr if the minimum applies. '
       '3. Predictive Analytics needs premium support, which is not priced. '
       '4. No hardware, hosting or database licences quoted (PI, Ampla, Predictive and Edge hosts). '
       '5. Services are +/-50% and non-binding; service-to-software mapping is our reading of the line titles. '
       '6. DCS / PLC / SCADA, ERP and the CCLAS-to-Ampla interface are not defined in the pack. '
       '7. Credits are priced at the Flex top-up rate ($21.24); confirm the commercial rate.',
       20, OY, PAGE_W - 40, 96)

Hpg = OY + 120
xml = (f'<mxfile><diagram name="AVEVA solution architecture" id="aveva-isa95"><mxGraphModel dx="1200" dy="900" grid="0" page="1" '
       f'pageWidth="{PAGE_W}" pageHeight="{Hpg}" background="#FFFFFF"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       f'{"".join(cells)}</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, PAGE_W, Hpg)
