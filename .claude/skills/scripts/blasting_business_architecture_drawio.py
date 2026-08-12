# -*- coding: utf-8 -*-
"""Build the one-page Business Architecture diagram for the blasting software as Draw.io.

Scope: TOGAF BDAT Tier 1 (Business Architecture) only, mining-adapted. Data,
Application-internal and Technology architecture are deliberately scoped out and the
gaps are stated on the page, as the framework's traceability checklist requires.

Surface only. Underground production and development blasting is out of scope, which
removes the 2DRing (stope ring) and 2DFace (tunnel / development face) design modules
and narrows the EMMM "Establish" interface to surface pre-strip, box cut and blast
permitting rather than underground development.

Source of content: input/JKTech Software/ — the eight vendor capability analyses
(JKSimBlast, 2DBench, Design Importer, StockView, TimeHEx, FragmentO, JKVBOC and
SOFT-BLAST Blastatistics).

Framework applied: .claude/rules/TOGAF_BDAT_MINING_ADAPTED_Enterprise_Architecture_Framework.html
  - EMMM Business Capability Reference Map as the capability spine (Discover,
    Establish, Exploit, Beneficiate, Sell, Support)
  - Principle 1 bidirectional strategy flow: corporate drivers down, site constraints up
  - Principle 2 co-equal IT/OT: every enabler tagged IT, OT or convergence
  - Principle 3 safety first: probabilistic modules held to advisory-only with fallback
  - Federated governance: corporate / hub / site authority plus escalation
  - Mining success metrics across production, cost, safety, environment, reliability,
    workforce

Brand rules from .claude/rules/MINRES_Content_Guidelines.html: Century Gothic
throughout; MinRes Red #CE372F for title and accents; Dark Teal #00444C for band
headers; Teal family for IT, Coral/Peach family for OT, Wine family for IT/OT
convergence and probabilistic systems; Brown 100 #F1EDE7 for the site-reality band.

Page is A3 landscape (1587 x 1123 px at 96dpi) with 24px margins.
"""
from xml.sax.saxutils import escape

CG = "Century Gothic"
cells = []
_id = [1]


def add(value, style, x, y, w, h, parent="1"):
    _id[0] += 1
    cells.append(
        '        <mxCell id="n%d" value="%s" style="%s" vertex="1" parent="%s">\n'
        '          <mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry" />\n'
        '        </mxCell>\n'
        % (_id[0], escape(value, {'"': '&quot;'}), escape(style, {'"': '&quot;'}),
           parent, x, y, w, h))


# ---------------------------------------------------------------- page grid
X0, RIGHT = 24, 1563
W = RIGHT - X0            # 1539


def grid(n, gap=6, x=X0, width=W):
    """n equal columns spanning width, separated by gap."""
    cw = (width - gap * (n - 1)) / float(n)
    return [(x + i * (cw + gap), cw) for i in range(n)]


# ---------------------------------------------------------------- palette
RED = "#CE372F"
TEAL = "#00444C"
INK = "#000000"
GREY = "#5C5C5C"

DOMAIN = {
    # IT — teal family
    "IT": {"fill": "#E0F7F9", "line": "#B0EDF3", "ink": "#1A7C87", "bar": "#2AB8C9"},
    # OT — coral / peach family
    "OT": {"fill": "#F5E5DD", "line": "#E8C4B0", "ink": "#8E5239", "bar": "#C37556"},
    # IT/OT convergence and probabilistic — wine family
    "CV": {"fill": "#F4D9DD", "line": "#E8A5AD", "ink": "#8B2E45", "bar": "#C5556B"},
}

BAND_HEAD = ("rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;fontFamily=%s;"
             "fontSize=9;fontStyle=1;fontColor=#FFFFFF;align=left;verticalAlign=middle;"
             "spacingLeft=10;" % (TEAL, CG))


def band(y, h, label, note=""):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % RED, X0, y, 5, h)
    txt = label
    if note:
        txt += ("&#160;&#160;&#160;<font color=\"#B0EDF3\" style=\"font-size:7.5px\">%s</font>"
                % note)
    add(txt, BAND_HEAD, X0 + 5, y, W - 5, h)


def box(text, x, y, w, h, fill, line, ink, fs=8, valign="top", pad=7):
    add(text,
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=%s;"
        "fontSize=%s;fontColor=%s;align=left;verticalAlign=%s;spacingLeft=%s;spacingRight=%s;"
        "spacingTop=4;" % (fill, line, CG, fs, ink, valign, pad, pad - 1),
        x, y, w, h)


def head_desc(title, desc, tcol, tsize=9, dsize=7.5):
    return ("<b><font style=\"font-size:%spx\" color=\"%s\">%s</font></b><br>"
            "<font style=\"font-size:%spx\" color=\"#000000\">%s</font>"
            % (tsize, tcol, title, dsize, desc))


# ================================================================ header
add("", "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;" % RED, X0, 24, 8, 58)
add("Business Architecture — Surface Drill &amp; Blast Blasting Software",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=19;fontStyle=1;fontColor=%s;"
    "align=left;verticalAlign=top;" % (CG, RED), 44, 21, 900, 26)
add("<b>Mineral Resources Limited</b>&#160;&#160;·&#160;&#160;JKTech JKSimBlast suite "
    "(2DBench, JKBMS, Design Importer, StockView, TimeHEx, 2DView, FragmentO, JKVBOC) "
    "+ SOFT-BLAST Blastatistics&#160;&#160;·&#160;&#160;<b><font color=\"#CE372F\">SURFACE ONLY "
    "— underground production and development blasting (2DRing, 2DFace) is out of "
    "scope</font></b><br>TOGAF BDAT <b>Tier 1 — Business Architecture</b>, "
    "mining-adapted. Capability spine is the Open Group <b>EMMM</b> Business Capability "
    "Reference Map. ADM phase: <b>Business Architecture</b>.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8.5;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, 44, 48, 1000, 34)
add("Prepared for: <b>Manager Drill &amp; Blast / Mining Services</b><br>"
    "Source: input/JKTech Software — 8 vendor capability analyses<br>"
    "Rule: TOGAF BDAT Mining-Adapted EA Framework v2.0<br>"
    "12 August 2026&#160;&#160;·&#160;&#160;<b>Draft — analyst interpretation, "
    "not vendor-confirmed and not site-validated</b>",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7.5;fontColor=%s;align=right;"
    "verticalAlign=top;" % (CG, GREY), 1060, 22, 503, 60)

# legend
LEG = ("rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=" + CG +
       ";fontSize=7;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;")
for i, (k, lbl) in enumerate([("IT", "IT domain"), ("CV", "IT/OT convergence"),
                              ("OT", "OT domain — safety-critical")]):
    d = DOMAIN[k]
    add(lbl, LEG % (d["fill"], d["line"], d["ink"]), 1060 + i * 130, 66, 126, 14)

# ================================================================ Band A — corporate drivers
YA = 92
band(YA, 22, "CORPORATE STRATEGY &amp; BUSINESS DRIVERS&#160;&#160;·&#160;&#160;CORPORATE LEVEL",
     "Principle 1 — corporate strategy flows DOWN into the D&amp;B capability")
DRIVERS = [
    ("Cost per tonne",
     "Drill &amp; blast is the first cost lever in the mine-to-mill chain — fragmentation "
     "sets load, haul, crush and grind energy. Target: lowest-quartile $/t."),
    ("Safety &amp; licence to operate",
     "Zero harm around explosives. Initiation must stay deterministic; misfire, flyrock and "
     "magazine control are non-negotiable."),
    ("Environmental &amp; community compliance",
     "Ground vibration, airblast, dust and fume within limits at every sensitive receiver; "
     "auditable ESG and regulator evidence."),
    ("Ore value realisation",
     "Post-blast movement defines the grade that reaches the crusher. Control ore loss and "
     "dilution; reduce reconciliation variance."),
    ("Standardised D&amp;B practice across the portfolio",
     "One design, prediction and QA/QC method reusable across iron ore hubs, lithium "
     "operations and Mining Services contract sites; knowledge retained when crews move."),
]
for (x, w), (t, d) in zip(grid(5, 8), DRIVERS):
    box(head_desc(t, d, TEAL), x, YA + 26, w, 62, "#E3F2F4", "#B8DDE3", INK)

# --- downward flow arrows
YD = YA + 92
for x, w in grid(5, 8):
    add("", "shape=singleArrow;html=1;direction=south;dy=0.55;dx=9;fillColor=#2D686F;"
        "strokeColor=none;", x + w / 2.0 - 26, YD, 52, 20)
add("Corporate strategy, standards and targets flow DOWN &#8595;",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7.5;fontStyle=2;fontColor=#2D686F;"
    "align=right;verticalAlign=middle;" % CG, 1180, YD + 2, 383, 16)

# ================================================================ Band B — EMMM capabilities
YB = YD + 26
band(YB, 22, "EMMM BUSINESS CAPABILITY REFERENCE MAP&#160;&#160;·&#160;&#160;WHERE THIS "
     "SOFTWARE SITS", "Tailored to the MinRes portfolio — scope of the blasting suite marked")
EMMM = [
    ("DISCOVER", "Exploration", "OUT OF SCOPE", "No exploration capability in this suite.",
     "#EFEFEF", "#D4D4D4", "#6E6E6E"),
    ("ESTABLISH", "Mine development &amp; permitting", "PARTIAL",
     "Box cut and pre-strip blasting; vibration and airblast limits set for blast permits.",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("EXPLOIT", "Production operations", "PRIMARY SCOPE",
     "Design, predict, fire and reconcile every blast — detailed below.",
     "#F9E5E3", RED, RED),
    ("BENEFICIATE", "Mineral processing", "INTERFACE",
     "Fragmentation prediction is the mine-to-mill hand-off to crusher and mill throughput.",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("SELL", "Market &amp; customer", "OUT OF SCOPE",
     "Indirect only, via product grade and quality consistency.",
     "#EFEFEF", "#D4D4D4", "#6E6E6E"),
    ("SUPPORT", "HSE, HR &amp; compliance", "ENABLED",
     "Blast records, QA/QC evidence, statutory retention, shotfirer competency.",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
]
for (x, w), (cap, cov, scope, note, fill, line, ink) in zip(grid(6, 6), EMMM):
    strong = 2 if scope == "PRIMARY SCOPE" else 1
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;strokeWidth=%s;" % (fill, line, strong),
        x, YB + 26, w, 48)
    add("<b><font style=\"font-size:10px\" color=\"%s\">%s</font></b>&#160;&#160;"
        "<font style=\"font-size:6.5px\" color=\"%s\"><b>%s</b></font><br>"
        "<font style=\"font-size:7px\" color=\"#5C5C5C\">%s</font><br>"
        "<font style=\"font-size:7px\" color=\"#000000\">%s</font>"
        % (ink, cap, ink, scope, cov, note),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, YB + 28, w - 13, 44)

# ================================================================ Band C — Exploit value chain
YC = YB + 82
band(YC, 22, "EXPLOIT&#160;&#160;·&#160;&#160;THE DRILL &amp; BLAST CAPABILITY CHAIN AND ITS "
     "APPLICATION ENABLERS",
     "Every enabler is tagged IT / OT / convergence — Principle 2, co-equal IT and OT")

STAGES = [
    ("1. Blast plan &amp; design",
     "Lay out the pattern to an approved site standard.",
     [("2DBench", "The surface design module and the anchor of the suite. Any blast in plan "
                  "view — open cut benches, ramps, trenches, sumps and contour blasts — laid "
                  "out as blast holes, decks, downhole and surface delays and connections, "
                  "with excavation outlines, hole pattern generation and per-hole "
                  "characterisation, then run as a detonation simulation.", 150)],
     "IT", "IT — office engineering"),
    ("2. Design data integration",
     "Get pit, survey and collars in without re-keying.",
     [("Design Importer", "Imports lines, polygons and blasthole collars from AutoCAD DXF, "
                          "mine planning packages and survey text / CSV. Removes the manual "
                          "data-entry bottleneck and transcription error between survey, "
                          "mine planning and blast design.", 150)],
     "CV", "IT &#8592; OT / survey data in"),
    ("3. Explosives master data",
     "One approved product and accessory catalogue.",
     [("StockView", "Central specifications for explosives, detonators, primers, boosters and "
                    "connectors; loadable from Orica and Enaex supplier data. Gives every site "
                    "the same approved catalogue and removes ad-hoc local records.", 150)],
     "IT", "IT — master data"),
    ("4. Charge &amp; timing design",
     "Deck the hole, set the delays, sequence the blast.",
     [("2DBench — decks &amp; delays", "Multi-deck charging, downhole and surface delays, "
                                       "connection architecture, burden relief.", 74),
      ("TimeHEx", "Electronic detonator timing design; Maximum Instantaneous Charge by "
                  "variable time window.", 72)],
     "CV", "IT design &#8594; OT initiation"),
    ("5. Outcome prediction",
     "Predict fragmentation, vibration and movement BEFORE firing.",
     [("FragmentO", "Fragmentation size distribution — Kuz-Ram, Rosin-Rammler, Swebrec; "
                    "energy distribution.", 50),
      ("TimeHEx — vibration", "Arrival time and scaled-distance vibration at nominated "
                              "receivers.", 48),
      ("JKVBOC + 2DView", "3D blast movement, ore loss and dilution; energy contours.", 46)],
     "CV", "IT — probabilistic, ADVISORY ONLY"),
    ("6. Field execution &amp; in-pit QA/QC",
     "Drill, charge and fire to design; capture what actually happened.",
     [("Blastatistics — mobile app", "Digital quality control at the blast on shift: design "
                                     "versus actual, deviations, comments and photographs. "
                                     "Deliberately minimal training for field crews.", 96),
      ("Drill rigs / MWD, shotfiring systems", "OT systems outside this suite — an integration "
                                               "point, not a component.", 50)],
     "OT", "OT — safety-critical, deterministic"),
    ("7. Record, reconcile &amp; report",
     "One record of design versus actual, kept for statute.",
     [("JKBMS — Blast Management System", "Pit and blast geometry, geotechnical and blasting "
                                          "domains, drilling parameters, costs, fragmentation "
                                          "and vibration results, reports and comments; "
                                          "long-term statutory retention.", 96),
      ("Blastatistics — web reports", "Same-day blast report with consumption, quality and "
                                      "cost.", 50)],
     "IT", "IT — records &amp; compliance"),
    ("8. Improve &amp; mine-to-mill",
     "Close the loop into throughput, cost and the next design.",
     [("Blastatistics — analytics", "Trend graphs, KPI precision maps, multi-site benchmarking "
                                    "with permissioned access per mine.", 74),
      ("JKSimBlast — optimisation", "Parametric and sensitivity analysis; feeds the crusher and "
                                    "mill throughput loop back into Beneficiate.", 72)],
     "IT", "IT &#8594; Beneficiate interface"),
]

SY, SH = YC + 26, 34          # stage header
EY, EH = SY + SH + 4, 150     # enabler stack
DY, DH = EY + EH + 4, 24      # domain tag

for (x, w), (name, purpose, prods, dom, domlbl) in zip(grid(8, 5), STAGES):
    d = DOMAIN[dom]
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % d["bar"], x, SY, w, 3)
    add("<b><font style=\"font-size:8.5px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:6.5px\" color=\"#000000\">%s</font>" % (TEAL, name, purpose),
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D1D1D1;fontFamily=%s;"
        "fontSize=7;align=left;verticalAlign=top;spacingLeft=6;spacingRight=5;spacingTop=3;"
        % CG, x, SY + 3, w, SH - 3)
    ey = EY
    for pname, pdesc, ph in prods:
        box("<b><font style=\"font-size:7.5px\" color=\"%s\">%s</font></b><br>"
            "<font style=\"font-size:6.5px\" color=\"#000000\">%s</font>"
            % (d["ink"], pname, pdesc),
            x, ey, w, ph, d["fill"], d["line"], INK, fs=7, pad=6)
        ey += ph + 4
    add(domlbl,
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;fontFamily=%s;"
        "fontSize=6.5;fontStyle=1;fontColor=#FFFFFF;align=center;verticalAlign=middle;"
        % (d["bar"], CG), x, DY, w, DH)

# --- upward flow arrows
YU = DY + DH + 6
for x, w in grid(5, 8):
    add("", "shape=singleArrow;html=1;direction=north;dy=0.55;dx=9;fillColor=#A58D62;"
        "strokeColor=none;", x + w / 2.0 - 26, YU, 52, 20)
add("&#8593; Site-level operational reality flows UP and constrains the architecture",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7.5;fontStyle=2;fontColor=#6B5435;"
    "align=right;verticalAlign=middle;" % CG, 1120, YU + 2, 443, 16)

# ================================================================ Band D — site realities
YE = YU + 26
band(YE, 22, "SITE-LEVEL OPERATIONAL REALITIES&#160;&#160;·&#160;&#160;SITE LEVEL",
     "Legitimate input to corporate strategy — neither level dominates")
SITE = [
    ("Ore body variability",
     "One design standard cannot span iron ore benches, pegmatite and hard banded ore. Sites "
     "need parameter freedom inside a corporate envelope."),
    ("Remote-pit connectivity",
     "In-pit QC capture must work offline and synchronise in connectivity windows. A "
     "central-only platform strands field data on the shift it matters."),
    ("Harsh environment",
     "Dust, heat and vibration in the pit. Ruggedised industrial tablets, not consumer "
     "devices, for field capture."),
    ("Crew capability &amp; turnover",
     "Licensed shotfirers are scarce. If the tool is not usable on-shift with minimal "
     "training it gets bypassed and the record is lost."),
    ("Contractor &amp; OEM boundaries",
     "Explosives suppliers (Orica, Enaex), drill contractors and electronic detonator OEMs "
     "each own part of the chain and its data."),
    ("Statutory limits per jurisdiction",
     "WA WHS (Mines) Regulations and Dangerous Goods Safety (Explosives) obligations; "
     "vibration and airblast limits per receiver; record retention."),
]
for (x, w), (t, d) in zip(grid(6, 6), SITE):
    box(head_desc(t, d, "#6B5435", tsize=8.5, dsize=7), x, YE + 26, w, 62,
        "#F1EDE7", "#D9CDB8", INK, fs=7)

# ================================================================ Band E — governance
YG = YE + 94
band(YG, 22, "FEDERATED GOVERNANCE&#160;&#160;·&#160;&#160;WHO DECIDES WHAT, AND THE "
     "ESCALATION PATH",
     "Governance is earned through demonstrated value to field operations, not process rigour")
GOV = [
    ("CORPORATE — sets the standard",
     "<b>Approves:</b> D&amp;B design standards and templates · the approved explosives "
     "catalogue held in StockView · prediction model versions and calibration policy · "
     "statutory record retention in JKBMS · licence pool and software versions · the IT/OT "
     "integration standard for drill, MWD and detonator systems.<br>"
     "<b>Authority:</b> Corporate Architecture with Group Safety and Mining Services "
     "leadership.",
     "#E0F7F9", "#B0EDF3", "#1A7C87"),
    ("HUB / REGIONAL — adapts within the standard",
     "<b>Approves:</b> design parameter ranges per ore type and bench · vibration and airblast "
     "limit sets per receiver · hub KPI targets and cross-site benchmarking in Blastatistics · "
     "which optional modules a hub runs.<br>"
     "<b>Authority:</b> Hub Operations Manager with the Regional D&amp;B Superintendent.",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("SITE — executes and escalates",
     "<b>Decides:</b> blast-by-blast design inside the approved envelope · delay selection · "
     "charge rules on the day · acceptance of in-pit QC.<br>"
     "<b>Escalates same shift:</b> any design outside the approved envelope, predicted "
     "exceedance at a receiver, misfire or flyrock event &#8594; Hub &#8594; Corporate.<br>"
     "<b>Authority:</b> Site Senior Executive and licensed shotfirer.",
     "#F5E5DD", "#E8C4B0", "#8E5239"),
    ("PROBABILISTIC SYSTEMS — special control",
     "FragmentO, JKVBOC and scaled-distance vibration prediction are <b>models, not "
     "measurements</b>.<br>"
     "<b>Advisory only</b> — no automated OT action, ever. <b>Human-in-the-loop:</b> engineer "
     "signs the design, shotfirer fires it.<br>"
     "<b>Fallback:</b> model unavailable or out of calibration &#8594; revert to site empirical "
     "charts, conservative MIC limits and the standard pattern.<br>"
     "<b>Validation:</b> predicted versus measured fragmentation, vibration and movement "
     "back-analysed every blast; recalibrate per domain. <b>Audit trail:</b> model version, "
     "inputs, engineer decision and measured outcome retained per blast.",
     "#F4D9DD", RED, "#8B2E45"),
]
GOVW = grid(4, 8)
for (x, w), (t, d, fill, line, ink) in zip(GOVW, GOV):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, YG + 26, w, 116)
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % ink, x, YG + 26, w, 3)
    add("<b><font style=\"font-size:8.5px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:6.8px\" color=\"#000000\">%s</font>" % (ink, t, d),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, YG + 32, w - 14, 108)

# ================================================================ Band F — success metrics
YM = YG + 150
band(YM, 22, "SUCCESS METRICS&#160;&#160;·&#160;&#160;ALL SIX MUST HOLD TOGETHER",
     "Success is not maximising any single dimension at the expense of the others")
METRICS = [
    ("PRODUCTION", "Tonnes fired to plan · dig rate and loader productivity · crusher and mill "
                   "throughput uplift from fragmentation."),
    ("COST", "Drill &amp; blast $/t and $/BCM · explosives consumed versus design · downstream "
             "comminution energy per tonne."),
    ("SAFETY", "Zero misfires, flyrock and explosives incidents · LTI and near-miss trend · "
               "shotfirer competency currency."),
    ("ENVIRONMENT", "Zero vibration and airblast exceedances at receivers · dust and fume "
                    "events · complete regulator and ESG evidence."),
    ("EQUIPMENT RELIABILITY", "Drill availability · oversize-driven crusher stoppages · boulder "
                              "rehandle and secondary breakage."),
    ("WORKFORCE", "Design compliance % · blast-to-report time (target same day) · manual "
                  "re-keying eliminated · capability retained through crew turnover."),
]
for (x, w), (t, d) in zip(grid(6, 6), METRICS):
    box(head_desc(t, d, TEAL, tsize=8, dsize=7), x, YM + 26, w, 52,
        "#EFEFEF", "#D4D4D4", INK, fs=7)

# ================================================================ footer — traceability & gaps
YF = YM + 86
FH = 164
LW = GOVW[2][0] + GOVW[2][1] - X0          # left block spans first three columns
RX = GOVW[3][0]
RW = GOVW[3][1]

add("", "rounded=0;html=1;fillColor=#FFFFFF;strokeColor=#B8DDE3;", X0, YF, LW, FH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % TEAL, X0, YF, 5, FH)
add("BIDIRECTIONAL TRACEABILITY&#160;&#160;·&#160;&#160;REQUIRED BY THE FRAMEWORK",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, TEAL), X0 + 14, YF + 7, LW - 28, 12)
add("<b><font color=\"#2D686F\">DOWNWARD</font></b> — corporate driver "
    "(cost per tonne · safety and licence · environmental compliance · ore value · portfolio "
    "standardisation) &#8594; EMMM business capability <b>Exploit: design, fire and reconcile a "
    "surface blast</b>, with interfaces into <b>Establish</b>, <b>Beneficiate</b> and "
    "<b>Support</b> &#8594; application enablers (2DBench, Design Importer, StockView, TimeHEx, "
    "FragmentO, JKVBOC, 2DView, JKBMS, Blastatistics) &#8594; Technology architecture "
    "<b>deliberately out of scope on this page</b>.<br>"
    "<b><font color=\"#6B5435\">UPWARD</font></b> — site constraints (remote-pit connectivity · "
    "harsh environment · crew turnover · ore body variability · contractor and OEM boundaries) "
    "&#8594; require offline-first in-pit capture that synchronises asynchronously, ruggedised "
    "devices, low-training interfaces and site-tunable parameters &#8594; therefore the design "
    "and record core must remain site-local and must not depend on corporate connectivity, and "
    "field QC cannot be a browser-only product.<br>"
    "<b><font color=\"#8B2E45\">PORTFOLIO CLASSIFICATION</font></b> — "
    "<b>Strategic</b> (formal architecture review, coordinated rollout): JKBMS, 2DBench, "
    "StockView. <b>Operational</b> (hub or site review, may vary by location): TimeHEx, "
    "FragmentO, JKVBOC, Design Importer, Blastatistics. <b>Tactical to retire</b>: site blast "
    "spreadsheets and local design records this architecture replaces.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, X0 + 14, YF + 22, LW - 28, FH - 28)

add("", "rounded=0;html=1;fillColor=#F1EDE7;strokeColor=#D9CDB8;", RX, YF, RW, FH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % RED, RX, YF, 5, FH)
add("GAPS, ASSUMPTIONS &amp; NEXT STEPS",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, RED), RX + 14, YF + 7, RW - 28, 12)
add("<b>Assumptions to confirm before circulation:</b> portfolio taken as iron ore hubs, "
    "lithium operations and Mining Services contract sites, with D&amp;B capability held in "
    "Mining Services. Stakeholder names and approval bodies are indicative.<br>"
    "<b>Scoped out, not yet traceable:</b> Tier 2A Data Architecture (blast, drill/MWD, "
    "vibration and reconciliation data domains; producer / consumer / enterprise stewardship; "
    "retention by jurisdiction) and Tier 3 Technology Architecture (edge and offline strategy, "
    "ruggedised devices, licensing).<br>"
    "<b>Open decisions:</b> Blastatistics is a separate vendor (Blastics / Soft-Blast) — "
    "integration with JKBMS is unproven and its QA/QC records overlap JKBMS; pick one system "
    "of record. As-is baseline and as-is to to-be gap analysis not yet done.<br>"
    "<b>Surface-only consequence:</b> if underground production or development blasting is "
    "later brought in, 2DRing and 2DFace re-enter the design stage and the Establish capability "
    "widens — the design standard, licence pool and governance envelope on this page would all "
    "need to be re-scoped rather than extended.<br>"
    "<b>Next steps:</b> gather site-level input (Principle 1 — this is not agreed architecture "
    "until sites have spoken), then phase implementation so it can pause and resume through "
    "commodity price cycles.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.8;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, RX + 14, YF + 22, RW - 28, FH - 28)

BOTTOM = YF + FH
add("Mineral Resources Limited&#160;&#160;·&#160;&#160;Business Architecture, one-page view"
    "&#160;&#160;·&#160;&#160;<b>surface only</b>&#160;&#160;·&#160;&#160;A3 landscape"
    "&#160;&#160;·&#160;&#160;Companion to the JKTech and Orica D&amp;B capability matrices",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;fontColor=#888888;align=left;"
    "verticalAlign=middle;" % CG, X0, BOTTOM + 6, W, 12)

# ================================================================ assemble
PW, PH = 1587, 1123
XML = (
    '<mxfile host="app.diagrams.net" agent="Claude Code" version="24.0.0" type="device">\n'
    '  <diagram name="Business Architecture - Blasting Software" id="minres-blast-bizarch">\n'
    '    <mxGraphModel dx="%d" dy="%d" grid="0" gridSize="10" guides="1" tooltips="1" '
    'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" '
    'math="0" shadow="0" background="#FFFFFF">\n'
    '      <root>\n'
    '        <mxCell id="0" />\n'
    '        <mxCell id="1" parent="0" />\n'
    % (PW, PH, PW, PH)
    + "".join(cells) +
    '      </root>\n'
    '    </mxGraphModel>\n'
    '  </diagram>\n'
    '</mxfile>\n')

if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    dest = os.path.join(root, "output",
                       "MinRes_Blasting_Software_Business_Architecture.drawio")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(XML)
    print("wrote %s" % dest)
    print("content bottom = %spx of %s ; %d cells" % (BOTTOM + 18, PH, _id[0] - 1))
