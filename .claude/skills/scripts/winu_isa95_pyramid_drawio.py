"""Draw the ISA-95 functional hierarchy as a layered pyramid with call-out cards.
Usage: python winu_isa95_pyramid_drawio.py <output.drawio>
Edit LEVELS below to change names, descriptors or capability counts."""
import sys, html

out = sys.argv[1] if len(sys.argv) > 1 else "ISA95_pyramid.drawio"

# (code, name, descriptor, capabilities, fill top, fill bottom)
LEVELS = [
    ("L4", "Business Planning & Logistics", "Enterprise planning, scheduling, supply chain and logistics", 14, "#0B3C5D", "#1D6A96"),
    ("L3", "Manufacturing Operations Management", "Production dispatch, performance, quality and maintenance management", 35, "#1D6A96", "#2E8BC0"),
    ("L2", "Monitoring & Supervising", "SCADA, HMI, alarming and supervisory control", 30, "#2E8BC0", "#3FA7A0"),
    ("L1", "Sensing & Local Control", "PLCs, controllers, instruments and drive control", 11, "#3FA7A0", "#5BBF8A"),
    ("L0", "Physical Process", "Plant, fleet and equipment performing the physical work", 11, "#5BBF8A", "#8FD19E"),
]
TOTAL = sum(l[3] for l in LEVELS)

CX, TOP, LAYER_H, GAP, BASE_HALF = 380, 110, 86, 6, 340
H = len(LEVELS) * LAYER_H + (len(LEVELS) - 1) * GAP
slope = BASE_HALF / H
hw = lambda y: slope * (y - TOP)  # half-width of pyramid at absolute y

cells, n = [], 1
def add(xml):
    cells.append(xml)
def nid():
    global n; n += 1; return n
def vertex(style, val, x, y, w, h):
    i = nid()
    add(f'<mxCell id="{i}" parent="1" style="{style}" value="{html.escape(val, quote=True)}" vertex="1">'
        f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')
    return i
def line(style, x1, y1, x2, y2):
    i = nid()
    add(f'<mxCell id="{i}" parent="1" style="{style}" edge="1"><mxGeometry relative="1" as="geometry">'
        f'<mxPoint x="{x1:.0f}" y="{y1:.0f}" as="sourcePoint"/><mxPoint x="{x2:.0f}" y="{y2:.0f}" as="targetPoint"/></mxGeometry></mxCell>')

FONT = "fontFamily=Helvetica;"
CARD_X, CARD_W, CARD_H = 800, 400, 76

# title
vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=24;fontStyle=1;fontColor=#0B3C5D;{FONT}",
       "ISA-95 Functional Hierarchy", 40, 20, 700, 36)
vertex(f"text;html=1;align=left;verticalAlign=middle;fontSize=13;fontColor=#6B7785;{FONT}",
       f"{TOTAL} capabilities across five levels, from business planning down to the physical process", 40, 56, 900, 24)

for i, (code, name, desc, cnt, c1, c2) in enumerate(LEVELS):
    y = TOP + i * (LAYER_H + GAP)
    yb = y + LAYER_H
    w_top, w_bot = hw(y), hw(yb)
    cy = y + LAYER_H / 2
    shadow = "shadow=1;"
    grad = f"fillColor={c1};gradientColor={c2};gradientDirection=south;strokeColor=#FFFFFF;strokeWidth=2;"
    label = f'<b style="font-size:26px">{code}</b>'
    if i == 0:
        style = f"shape=triangle;direction=north;html=1;{grad}{shadow}fontColor=#FFFFFF;verticalAlign=bottom;spacingBottom=6;{FONT}"
        vertex(style, label, CX - w_bot, y, 2 * w_bot, LAYER_H)
    else:
        style = (f"shape=trapezoid;perimeter=trapezoidPerimeter;fixedSize=1;size={w_bot - w_top:.1f};html=1;"
                 f"{grad}{shadow}fontColor=#FFFFFF;{FONT}")
        vertex(style, label, CX - w_bot, y, 2 * w_bot, LAYER_H)

    # connector to card
    edge_x = CX + (w_top + w_bot) / 2 - 4
    line("endArrow=oval;endFill=1;endSize=5;startArrow=none;dashed=1;strokeColor=#9AA7B4;strokeWidth=1.5;",
         CARD_X, cy, edge_x, cy)

    # card: accent bar, text, count pill
    vertex(f"rounded=1;arcSize=12;html=1;fillColor=#FFFFFF;strokeColor=#D5DDE5;shadow=1;", "", CARD_X, cy - CARD_H / 2, CARD_W, CARD_H)
    vertex(f"rounded=0;html=1;fillColor={c1};gradientColor={c2};gradientDirection=south;strokeColor=none;", "", CARD_X, cy - CARD_H / 2 + 6, 8, CARD_H - 12)
    vertex(f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;spacingLeft=6;{FONT}",
           f'<b style="font-size:14px;color:#0B3C5D">LEVEL {code[1]}: {html.escape(name.upper())}</b><br>'
           f'<span style="font-size:11px;color:#6B7785">{html.escape(desc)}</span>',
           CARD_X + 20, cy - CARD_H / 2 + 8, CARD_W - 120, CARD_H - 16)
    vertex(f"ellipse;html=1;fillColor={c1};strokeColor=none;fontColor=#FFFFFF;fontSize=18;fontStyle=1;{FONT}",
           str(cnt), CARD_X + CARD_W - 78, cy - 25, 50, 50)
    vertex(f"text;html=1;align=center;verticalAlign=top;fontSize=9;fontColor=#6B7785;{FONT}",
           "capabilities", CARD_X + CARD_W - 88, cy + 26, 70, 14)

# left-hand axis: business to physical
ax = 60
line("endArrow=block;startArrow=block;endFill=1;startFill=1;strokeColor=#9AA7B4;strokeWidth=2;", ax, TOP + 6, ax, TOP + H - 6)
vertex(f"text;html=1;align=center;verticalAlign=middle;fontSize=11;fontColor=#6B7785;fontStyle=1;{FONT}", "BUSINESS", ax - 40, TOP - 22, 80, 18)
vertex(f"text;html=1;align=center;verticalAlign=middle;fontSize=11;fontColor=#6B7785;fontStyle=1;{FONT}", "PHYSICAL", ax - 40, TOP + H + 4, 80, 18)

W, Hpg = CARD_X + CARD_W + 40, TOP + H + 50
xml = (f'<mxfile><diagram name="ISA-95 pyramid" id="isa95"><mxGraphModel dx="1200" dy="900" grid="0" page="1" '
       f'pageWidth="{W}" pageHeight="{Hpg}" background="#FFFFFF"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       f'{"".join(cells)}</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out)
