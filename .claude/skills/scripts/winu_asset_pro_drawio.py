"""Build the Winu Asset Pro Advantage capability diagram (.drawio).
Same style as output/Winu/Winu_GNSS_RTK_Capability.drawio (swimlanes left to right, coloured boxes).
Usage: python winu_asset_pro_drawio.py <output.drawio> <APA Proposal.xlsx>

Equipment, quantities, Asset Pro Option kits and totals come from the Wenco_HME_Register worksheet of
input/Vendor/Asset Pro Advantage/APA Proposal.xlsx (columns Equipment, Asset Pro Option, CAPEX and annual totals). Winu fit comes from the WIN-CON-EPC-001 Mining and Process reviews.
Yellow boxes are open items or judgement calls."""
import sys, html

out = sys.argv[1]

# fill, stroke
C = {"ref": ("#d5e8d4", "#82b366"), "link": ("#ffe6cc", "#d79b00"), "gap": ("#f8cecc", "#b85450"),
     "rig": ("#dae8fc", "#6c8ebf"), "off": ("#b0e3e6", "#0e8088"), "out": ("#e1d5e7", "#9673a6"),
     "chk": ("#fff2cc", "#d6b656"), "grey": ("#f5f5f5", "#666666")}

LANE_X0, LANE_W, LANE_GAP, LANE_Y, LANE_H = 20, 270, 40, 80, 1000
BOX_W, BOX_DX = 230, 20

LANES = [
    "1. Order + install (MinRes process)",
    "2. Winu equipment (Wenco_HME_Register)",
    "3. Asset Pro Option (kit)",
    "4. Platform + monitoring",
    "5. Outputs",
]

# ---- read the register: columns Equipment (C), Peak qty (E), Asset Pro Option (H), CAPEX / annual totals (K, L) ----
import openpyxl, shutil, tempfile, os
tmp = os.path.join(tempfile.mkdtemp(), "apa.xlsx")
shutil.copyfile(sys.argv[2], tmp)      # the source may be locked by Excel / OneDrive
ws = openpyxl.load_workbook(tmp, data_only=True)["Wenco_HME_Register"]
REG = []
for r in ws.iter_rows(min_row=5, values_only=True):
    if r[0] and r[2]:
        REG.append(dict(ref=r[0], tier=str(r[1]), eq=r[2], qty=r[4] or 0, kit=str(r[7]).replace("MRL", "").replace("Kit", "").replace("KIT", "").strip(),
                        capex=r[10] or 0, annual=r[11] or 0))

SHORT = {"Track-type dozer (dump face, dig face, TSF)": "Track dozer", "Track-type dozer - clearing, topsoil, pads": "Track dozer (clearing)",
         "Padfoot / smooth drum compactor": "Compactor", "Bulk emulsion MPU / charging unit": "Emulsion MPU",
         "Ore / clean-up / stemming / borrow trucks": "Ore / borrow trucks", "Float (prime mover and low loader)": "Float",
         "Light vehicle (mine-specification)": "Light vehicle", "Ambulance / emergency response vehicle": "Ambulance",
         "Fire / rescue truck": "Fire / rescue truck", "Production blasthole drill rig": "Production drill", "Pre-split / trim drill rig": "Pre-split drill"}
LV = {"F8", "F10", "F11", "F9"}


def group(pred):
    rows = [r for r in REG if pred(r)]
    names = ", ".join(f"{SHORT.get(r['eq'], r['eq'])} {r['qty'] if r['ref'] != 'F9' else 'qty n/a'}" for r in rows)
    return sum(r["qty"] for r in rows), names, sum(r["capex"] for r in rows), sum(r["annual"] for r in rows)


GROUPS = [
    ("tier1", lambda r: r["kit"] == "-" and r["tier"].startswith("1"), "Tier 1 dispatched"),
    ("drill", lambda r: r["kit"] == "-" and r["tier"].startswith("2"), "Tier 2 drills"),
    ("G2a", lambda r: r["kit"] == "G2a", "Tier 2 graders"),
    ("G5h", lambda r: r["kit"] == "G5a" and r["tier"].startswith("2"), "Tier 2 heavy mobile"),
    ("G5s", lambda r: r["kit"] == "G5a" and r["tier"].startswith("3") and r["ref"] not in LV, "Tier 3 support plant"),
    ("G5l", lambda r: r["ref"] in LV, "Tier 3 light vehicles + emergency"),
    ("E7", lambda r: r["kit"] == "E7", "Tier 2 backhoe"),
    ("E2", lambda r: r["kit"] == "E2", "Tier 2 / 3 tow plant"),
]
G = {k: group(f) + (t,) for k, f, t in GROUPS}      # qty, names, capex, annual, title
Q = {k: v[0] for k, v in G.items()}
gq = Q["G2a"] + Q["G5h"] + Q["G5s"] + Q["G5l"]
eq_ = Q["E7"] + Q["E2"]
TOT_CAPEX = sum(r["capex"] for r in REG)
TOT_ANN = sum(r["annual"] for r in REG)
KIT_TXT = {
    "G2a": "Kit G2a: IVMS + DFMS\nSmart Eye + secondary camera, seat vibration,\ndriver ID",
    "G5a": "Kit G5a: IVMS + DFMS + driver ID",
    "E7": "Kit E7: hard-wired asset tracker\nGR09 IP67; location and usage, no camera",
    "E2": "Kit E2: battery GPS tracker\nBarra Edge 4G LTE NBIOT",
}


def usd(v):
    return f"${v:,.0f}"


def rowtxt(k):
    q, names, cx, an, title = G[k]
    return f"{title}: {q}\n{names}"


def kittxt(k):
    q, names, cx, an, title = G[k]
    kit = "G5a" if k.startswith("G5") else k
    return f"{KIT_TXT[kit]}\n{q} units: {usd(cx)} hardware, {usd(an)} / yr"


YS = {k: 296 + 80 * i for i, k in enumerate(G)}
RH = 72
B = {
    "order": (0, 120, 72, "link", "Order hardware kit via Coupa or part number\none kit per asset; bulk rates lower"),
    "ship": (0, 210, 56, "link", "Kit delivered to the DC,\nshipped to site for free"),
    "inst": (0, 290, 650, "ref", "INSTALL - three options\n\n"
             "A. Site staff who completed Asset Pro 'Train the Trainer'\n$1,280 / day Perth, $2,160 / day on site\n\n"
             "B. Asset Pro as contractor: site $115 / hour, or Perth metro per asset (LV $240-360, HME $480-960); "
             "recommended for complex or first install on a site\n\n"
             "C. Trained, inducted sub-contractor: Ejan, Autonimo, Kaynar"),
    "coi": (0, 960, 74, "link", "Certificate of Installation to Asset Pro; Asset Pro\nchecks, AMG uploads to Asset Register and\nsets up user accounts (names, site / asset group)"),
    "ask": (1, 120, 112, "chk", "Is Asset Pro required at Winu? ITT does not name it.\nWenco tier 1 (21 units) fits Wenco on-board;\nAsset Pro covers tiers 2 and 3 per the register\n(16 trucks, excavators, loaders assumed free-issue)"),
    "plat": (3, 290, 650, "link", "ASSET PRO PLATFORM (AI-enabled)\n\nDigital Matter / Geotab devices\nreport over cellular, satellite where fitted\n\nassets viewed by site or asset group\naccess via AMG request\n\n3-year fixed pricing, two optional 2-year extensions;\n3-year warranty from installation"),
    "sw": (3, 120, 100, "link", f"Register totals: {usd(TOT_CAPEX)} hardware,\n{usd(TOT_ANN)} / yr software for {gq + eq_} fitted units;\npro rata first year; unused software credited\non demob or resale (deactivation form)"),
    "supp": (3, 230, 50, "grey", "Support: Asset Pro, AMG, TOP; 2 h response KPI;\nescalation to Asset Pro and AMG leads"),
    "top": (3, 960, 74, "off", "Transport Operations Platform (TOP)\nmonitors assets with live DFMS events"),
    "o1": (4, 340, 84, "out", f"Asset location, geofences and CANBUS vehicle data\nfor {gq + eq_} Winu units on Asset Pro;\n{eq_} tracking-only (E-series)"),
    "o4": (4, 560, 64, "out", "Evidence for ITT in-vehicle monitoring and\nfatigue controls (App C-2 s4.6, SOW s9.15)"),
    "o5": (4, 650, 84, "chk", "Link to Wenco FMS / Winu data platform:\nnot defined; Wenco SmartCap fatigue option\nis excluded from the quote"),
    "o2": (4, 960, 74, "out", f"Driver fatigue, distraction, seatbelt and\nphone alerts for {gq} G-series vehicles; live DFMS events\nreviewed in TOP"),
}
for k in G:
    nokit = k in ("tier1", "drill")
    B["a_" + k] = (1, YS[k], RH, "grey" if nokit else ("chk" if k in ("E7", "E2") else "rig"), rowtxt(k))
    if nokit:
        B["k_" + k] = (2, YS[k], RH, "grey", "Wenco on-board unit - no Asset Pro kit" if k == "tier1" else "No Asset Pro kit in register (price #N/A);\nOEM telematics assumed")
    else:
        B["k_" + k] = (2, YS[k], RH, "off", kittxt(k))

# source, target, label, dashed
E = [
    ("order", "ship", "", False),
    ("ship", "inst", "", False),
    ("inst", "coi", "", False),
] + [("inst", "a_" + k, "", k in ("tier1", "drill")) for k in G] + [("a_" + k, "k_" + k, "", k in ("tier1", "drill")) for k in G] + [
    ("k_" + k, "plat", "", k in ("tier1", "drill")) for k in G] + [
    ("plat", "top", "", False),
    ("plat", "o1", "", False),
    ("plat", "o4", "", True),
    ("o4", "o5", "", True),
    ("top", "o2", "", False),
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
text("Winu Pre-Strip - Asset Pro Advantage telematics capability (asset tracking, IVMS, driver fatigue)", 20, 10, W_TOTAL - 40, 30, 18, True)
text("Source: APA Proposal.xlsx, Wenco_HME_Register (Equipment, Asset Pro Option); Asset Pro Contract Roll Out deck + MRL3524 Roll out Briefing Document; "
     "WIN-CON-EPC-001 Mining and Process reviews. Option 1 = MinRes minimum-standard kit. Yellow = open item or judgement call.", 20, 38, W_TOTAL - 40, 20, 11)

for i, name in enumerate(LANES):
    add("swimlane;startSize=30;rounded=0;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;fontStyle=1;swimlaneFillColor=#fafafa;",
        esc(name), LANE_X0 + i * (LANE_W + LANE_GAP), LANE_Y, LANE_W, LANE_H)

box_id = {}
for k, (ln, y, h, col, t) in B.items():
    fill, stroke = C[col]
    tall = k in ("inst", "plat")
    style = (f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontSize=10;"
             + ("strokeWidth=2;" if tall else "") + ("align=left;spacingLeft=6;spacingRight=6;" if k == "inst" else ""))
    box_id[k] = add(style, esc(t), LANE_X0 + ln * (LANE_W + LANE_GAP) + BOX_DX, y, BOX_W, h)

for s, t, lab, dashed in E:
    i = nid()
    sl, tl = B[s][0], B[t][0]
    sy, sh, ty, th = B[s][1], B[s][2], B[t][1], B[t][2]
    if sl == tl:    # vertical hop inside a lane
        ex, ey, nx, ny = (0.5, 1, 0.5, 0) if sy < ty else (0.5, 0, 0.5, 1)
    else:           # horizontal hop at the centre line of the smaller box, so the arrow is straight
        cy = (sy + sh / 2) if sh <= th else (ty + th / 2)
        ex, ey, nx, ny = 1, round((cy - sy) / sh, 4), 0, round((cy - ty) / th, 4)
    st = (f"endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor=#333333;edgeStyle=none;rounded=0;"
          f"fontSize=9;labelBackgroundColor=#ffffff;exitX={ex};exitY={ey};entryX={nx};entryY={ny};" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{i}" edge="1" parent="1" source="{box_id[s]}" target="{box_id[t]}" style="{st}" value="{esc(lab)}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')

FY = LANE_Y + LANE_H + 20
note = ("What Asset Pro supplies (MinRes preferred supplier, selected by tender; site trial on 9 x 785D dump trucks at Roy Hill):\n"
        "Asset tracking for equipment | IVMS (GO9 / G70 BLE unit, CANBUS, geofences) | DFMS (APA Smart Eye AI dash cam; HME secondary camera) | accessories\n"
        "Cost from the register (Asset Pro Option column x unit cost; excludes install, accessories, GST): "
        "hardware " + usd(TOT_CAPEX) + ", software " + usd(TOT_ANN) + " per year for " + str(gq + eq_) + " fitted units "
        "(G-series $960, E7 $324, E2 $156 per device per year).\n"
        "Terms: hardware paid upfront; software annual per device, pro rata first year; fixed pricing for 3 years. Long-term plan: migrate legacy MinRes hardware onto the platform.\n"
        "Winu drivers: light vehicles need in-vehicle monitoring; 2 h driving then 15 min break, 12 h / 10 h break working hours; "
        "heavy vehicle controls incl. fatigue and journey management (SOW s9.15).")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(note), 20, FY, 900, 130)
openi = ("Open items to resolve with MinRes / Asset Pro:\n"
         "1. ITT does not name Asset Pro: confirm it is required at Winu and who buys, installs and owns the kits (16 trucks, excavators and loaders assumed Company free-issue).\n"
         "2. Register leaves " + str(Q["tier1"]) + " tier 1 units to Wenco and " + str(Q["drill"]) + " drills with no Asset Pro kit (price #N/A); kit per category is judgement, validate with Asset Pro.\n"
         "3. XCMG XDE260 CANBUS / camera mounting not covered by the Roy Hill 785D trial; personnel bus qty not in the register.\n"
         "4. Cellular / satellite coverage at pit and ROM pad; overlap with Wenco SmartCap option; lighting plants, pumps and other plant could be tracked with Asset Pro trackers if wanted.")
add("rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#666666;fontSize=11;align=left;spacingLeft=10;",
    esc(openi), 940, FY, W_TOTAL - 960, 130)

PAGE_H = FY + 160
xml = ('<mxfile host="65bd71144e"><diagram name="Asset Pro capability" id="0"><mxGraphModel grid="1" page="1" gridSize="10" guides="1" '
       f'tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="{W_TOTAL}" pageHeight="{PAGE_H}" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(out, "w", encoding="utf-8").write(xml)
print("wrote", out, W_TOTAL, PAGE_H)
