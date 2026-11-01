"""Build the Winu GNSS / RTK coverage map (.drawio): where the GNSS RTK solution has to reach on site.
Usage: python winu_gnss_coverage_map_drawio.py <output.drawio>

Schematic only, NOT TO SCALE and NOT SURVEYED. Areas and associations come from output/Winu/WIN-CON-EPC-001_Mining_Review.html
(scope of work, work areas WA1-WA7, mine pre-strip, haul roads) and output/Winu/Winu Technical Info - Document Register.xlsx.
No facility coordinates are in the pack (pit designs, plot plan, haul road info and disturbance footprint are 'referenced only'),
so positions of areas, base station and repeaters are indicative. Solution content follows
input/Vendor/Ultimate Positioning Group/GNSS_RTK_Capability-Diagram.png."""
import sys, html

out = sys.argv[1]
cells = []
n = [0]


def nid():
    n[0] += 1
    return f"m{n[0]}"


def esc(t):
    return html.escape(t, quote=True).replace("\n", "&#xa;")


def add(style, val, x, y, w, h):
    i = nid()
    cells.append(f'<mxCell id="{i}" parent="1" style="{style}" value="{esc(val)}" vertex="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i


def text(val, x, y, w, h, size=11, bold=False, align="center"):
    return add(f"text;html=0;align={align};verticalAlign=middle;fontSize={size};fontStyle={1 if bold else 0};whiteSpace=wrap;",
               val, x, y, w, h)


def edge(a, b, label="", dashed=False, width=3, color="#7f7f7f"):
    i = nid()
    st = (f"endArrow=none;html=1;strokeWidth={width};strokeColor={color};fontSize=9;labelBackgroundColor=#ffffff;"
          + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{a}" target="{b}" style="{st}" value="{esc(label)}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')


# fill, stroke
C = {"A": ("#d5e8d4", "#82b366"), "B": ("#ffe6cc", "#d79b00"), "C": ("#f5f5f5", "#666666"),
     "pit": ("#dae8fc", "#6c8ebf"), "feat": ("#ffffff", "#666666"), "chk": ("#fff2cc", "#d6b656"),
     "gap": ("#f8cecc", "#b85450"), "base": ("#e1d5e7", "#9673a6")}

MX, MY, MW, MH = 20, 90, 1480, 790

text("Winu Pre-Strip - GNSS / RTK coverage required (schematic map: areas and general associations)", 20, 10, 1480, 30, 18, True)
text("Schematic, NOT TO SCALE, not surveyed. No facility coordinates exist in the tender pack (pit designs, plot plan, haul road info and "
     "disturbance footprint are referenced only), so area positions, base station and repeaters are indicative. "
     "Site centroid 121°45'35\"E, 20°43'58\"S (SOW s2.1); survey drawings use MGA94 Zone 51.", 20, 40, 1480, 40, 11)

add("rounded=0;fillColor=#fafafa;strokeColor=#999999;dashed=0;", "", MX, MY, MW, MH)
text("WINU SITE - Paterson Province, Pilbara WA (~350 km east of Port Hedland; figures conflict, 320 km on p210)", MX + 10, MY + 4, 900, 22, 12, True, "left")

# coverage tiers (drawn first so features sit on top)
add("rounded=1;arcSize=4;dashed=1;dashPattern=8 4;strokeWidth=2;fillColor=#ffe6cc;strokeColor=#d79b00;opacity=45;", "", 70, 130, 1190, 720)
add("rounded=1;dashed=1;dashPattern=8 4;strokeWidth=2;fillColor=#f5f5f5;strokeColor=#666666;opacity=60;", "", 1280, 130, 210, 740)
add("ellipse;dashed=1;dashPattern=8 4;strokeWidth=2;fillColor=#d5e8d4;strokeColor=#82b366;opacity=55;", "", 100, 200, 960, 520)
text("TIER B - construction earthworks area\n(rovers, UAV, machine guidance; NTRIP or UHF extension)", 80, 805, 520, 36, 11, True, "left")
text("TIER A - core mining area: site-wide UHF RTK + NTRIP\n(rovers, UAV, machine guidance, Wenco FMS, light vehicles)", 330, 205, 520, 36, 11, True, "left")
text("TIER C - outside the mine core\nconfirm whether in the RTK scope", 1290, 135, 190, 36, 11, True)

# --- Tier A features
pit = add("ellipse;whiteSpace=wrap;html=0;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;fontSize=11;",
          "OPEN PIT\npre-strip of cutbacks 1-2\n~21.6 Mbcm to ~70 m bgl\n(ultimate ~480 m deep)\nMining Exclusion Area", 440, 340, 300, 210)
wrl = add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
          "Waste Rock Landforms (WRL)\nPAF cells encapsulated by NAF\n5 m lifts", 150, 330, 200, 80)
rom = add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
          "ROM pad + primary crusher\nbulk fill zone (WA3)", 850, 380, 150, 70)
stk = add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
          "Stockpile bases + SWM (WA4)\nfirst ~600 kt ore to stockpiles", 840, 520, 160, 70)
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
    "Topsoil strip + clearing\nahead of cutbacks, drainage", 470, 590, 200, 50)
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;",
    "Borrow pits - locations not supplied\n(Borrow Pit Management Plan)", 190, 640, 190, 50)

# --- Tier B features
msa = add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
          "Mineral Processing Plant, MSA,\nIPP / power station, ponds (WA3)", 1080, 340, 160, 90)
tsf = add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
          "TSF Stage 0 (WA6)\nYears 2-3, embankment + basin\ndirect haul from pit", 1070, 600, 170, 80)
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
    "Ancillary Explosives Area\n(WA7) + access road, pond", 150, 150, 190, 50)
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
    "Borefield access tracks (~4 m),\ntopsoil + solar farm (WA7)", 420, 150, 190, 50)
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
    "Tailings corridor, Clean Water Pond,\nPit Dewatering Pond (WA3)", 780, 150, 200, 50)

# --- Tier C features
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
    "Permanent Village (WA2)\nbulk earthworks, comms tower,\nWTP / STP, spray field", 1295, 185, 180, 80)
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
    "Aerodrome (WA5)\nrunway, apron, camp laydown\n(survey drawings in MGA94 Z51)", 1295, 290, 180, 80)
road = add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;",
           "Mine Access Road (WA1)\n182 km sealed, runs off-map to\nGreat Northern Hwy / Port Hedland\n(corridor coverage not stated)", 1295, 410, 180, 90)
edge(msa, road, "", False, 5, "#b3b3b3")

# haul roads
edge(pit, wrl, "", False, 4)
edge(pit, rom, "", False, 4)
edge(pit, stk, "", False, 4)
edge(pit, tsf, "direct haul to TSF", True, 3)
text("~17 km long-term haul roads (XCMG XDE260-class, two-way)", 640, 548, 190, 34, 10, True)

# --- GNSS infrastructure markers
base = add("triangle;whiteSpace=wrap;html=0;fillColor=#e1d5e7;strokeColor=#9673a6;strokeWidth=2;fontSize=9;", "", 1030, 290, 34, 34)
text("Trimble R750 permanent base + Zephyr 3 antenna + TDL450B UHF\nposition TBC: central, high ground, line of sight to pit / ROM / WRL", 770, 244, 250, 44, 9, False, "right")
for i, (rx, ry) in enumerate([(380, 250), (770, 660), (1040, 520), (330, 500)], 1):
    add("ellipse;whiteSpace=wrap;html=0;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=9;fontStyle=1;", f"R{i}", rx, ry, 28, 28)
text("R1-R4 = indicative UHF repeater / radio-mesh sites (positions TBC; needed as the pit deepens and walls block line of sight)", 650, 690, 360, 30, 9, False, "left")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=9;",
    "Surveyed control point: survey control is excluded from Contractor scope - confirm who provides it (datum MGA94 vs GDA2020 also to confirm)", 1000, 745, 250, 50)

# --- Legend
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=9;align=left;spacingLeft=6;",
    "LEGEND\nGreen ellipse = Tier A UHF + NTRIP\nOrange area = Tier B extension\nGrey area = Tier C confirm\nThick line = haul road (dashed = to TSF)\nPurple triangle = base station\nR# = repeater, yellow box = open item", 1290, 700, 195, 155)

# --- Coverage requirement table
TY = MY + MH + 25
text("Coverage required by area (general associations; positions and distances not stated in the pack)", 20, TY, 1480, 26, 14, True, "left")
COLS = [("Area", 300), ("Source (tender PDF page)", 190), ("GNSS RTK users needed", 430), ("Correction link", 360), ("Tier", 200)]
ROWS = [
    ("Open pit, cutbacks 1-2 (Mining Exclusion Area)", "SOW 6.2.1, 6.2.17 p240-256", "Rovers (as-builts), UAV, dozers / excavators / drills, Wenco FMS, light vehicles", "UHF broadcast + NTRIP; repeaters as pit deepens", "A", "A"),
    ("Waste Rock Landforms + PAF cells", "SOW 6.2.8 p248-249", "Rovers, UAV volumes, dozers and dump trucks (FMS)", "UHF + NTRIP", "A", "A"),
    ("Long-term haul roads (~17 km), bench roads, ramps", "SOW 6.2.7, 6.2.10 p247-252", "Machine guidance (dozers, graders), FMS haul cycle, light vehicles, rover stakeout", "UHF with repeater coverage along route", "A", "A"),
    ("ROM pad, crusher bulk fill zone", "SOW 6.1.2 p233", "Rovers (stakeout, as-builts), dozers, UAV, FMS", "UHF + NTRIP", "A", "A"),
    ("Stockpile bases + stormwater (WA4)", "SOW 6.1.2 p234-235", "Rovers, UAV, dozers / graders, FMS", "UHF + NTRIP", "A", "A"),
    ("Topsoil strip, clearing, drainage ahead of pit", "SOW 6.2.2 p241", "Rovers (initial ground survey, post-strip DTM), UAV, dozers", "UHF + NTRIP", "A", "A"),
    ("Borrow pits (location not supplied)", "SOW 6.1.5 p240", "Rovers, UAV volumes, loaders / trucks", "NTRIP or UHF extension; location TBC", "A / B", "B"),
    ("TSF Stage 0 embankment + basin (WA6)", "SOW 6.3 p257-260", "Rovers, UAV, dozers / compactors / graders with guidance, trucks (FMS)", "UHF extension or NTRIP backhaul", "B", "B"),
    ("Process plant, MSA, IPP, ponds, tailings corridor (WA3)", "SOW 6.1.2 p232-234", "Rovers (stakeout, as-builts), UAV, graders / dozers", "UHF extension or NTRIP", "B", "B"),
    ("Explosives area, borefield tracks, solar (WA7)", "SOW 6.1.2 p237-238", "Rovers, graders / dozers (track construction)", "NTRIP; UHF only if line of sight", "B", "B"),
    ("Permanent Village (WA2) + Aerodrome (WA5)", "SOW 6.1.2 p231, p235-236", "Rovers, UAV; earthworks guidance if Contractor machines used", "NTRIP over 4G / satellite; coverage to confirm", "C - confirm", "C"),
    ("Mine Access Road 182 km (WA1)", "SOW 6.1.2 p230", "Rovers, road-construction guidance", "NTRIP (satellite); corridor not stated", "C - confirm", "C"),
]
y = TY + 30
x = 20
for name, w in COLS:
    add("rounded=0;whiteSpace=wrap;html=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=10;fontStyle=1;", name, x, y, w, 26)
    x += w
y += 26
for r in ROWS:
    x = 20
    fill, stroke = C[r[5]]
    for j, (name, w) in enumerate(COLS):
        f, s = (fill, stroke) if j == 4 else ("#ffffff", "#999999")
        add(f"rounded=0;whiteSpace=wrap;html=0;fillColor={f};strokeColor={s};fontSize=9;align=left;spacingLeft=4;", r[j], x, y, w, 34)
        x += w
    y += 34

# --- Notes
NY = y + 20
note = ("Solution content (from the UPG capability diagram):\n"
        "Reference: Trimble R980 RTK receiver x2 (base-station enabled, one spare), R750 permanent base, Zephyr 3 antenna, surveyed control point\n"
        "Link: Trimble TDL450B UHF site-wide broadcast (line of sight, repeaters); NTRIP over 4G / satellite for rovers and UAV; temporary Contractor radio + FMS mesh (Company TETRA not available)\n"
        "Users: R980 survey rovers, UAV (RTK/PPK), machine guidance / fleet positioning (Wenco FMS), light vehicles\n"
        "Outputs: initial ground survey <=48 hrs, post topsoil-strip DTM <=7 days, mass-haul / pit / ROM pad as-builts, FMS data exports")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=10;align=left;spacingLeft=10;", note, 20, NY, 730, 130)
openi = ("Open items (coverage cannot be sized from the pack):\n"
         "1. No coordinates: Plot Plan, Pit Designs - Cutbacks, Haul Road Info and Disturbance Footprint (p160-161) are referenced only, not supplied\n"
         "2. Transfer-node coordinates for the TSF reference axis are requested (R-50); HTML review also flags the ~170 ha footprint against ~17 km of haul road\n"
         "3. Are Village, Aerodrome and Access Road survey/guidance in the RTK scope, and who owns survey control?\n"
         "4. Base and repeater siting, UHF licence, and radio mesh vs Company TETRA need confirmation")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;align=left;spacingLeft=10;", openi, 770, NY, 730, 130)

PAGE_W, PAGE_H = MX * 2 + MW, NY + 160
xml = ('<mxfile host="65bd71144e"><diagram name="GNSS RTK coverage map" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{PAGE_W}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, PAGE_W, PAGE_H)
