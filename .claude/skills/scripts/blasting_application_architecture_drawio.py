# -*- coding: utf-8 -*-
"""Build the one-page Application Architecture diagram for the blasting software as Draw.io.

Third in the set, after blasting_business_architecture_drawio.py (Tier 1) and
blasting_data_architecture_drawio.py (Tier 2A). Scope: TOGAF BDAT Tier 2B
(Application Architecture) only, mining-adapted, for SURFACE OPERATIONS ONLY —
underground and development blasting (2DRing, 2DFace) is out of scope. Technology
architecture (Tier 3 — database platform, devices, hosting, network, backup) is also out
of scope. Both exclusions are stated on the page, as the framework's traceability
checklist requires.

Source of content: input/JKTech Software/ — the eight vendor capability analyses
(JKSimBlast, 2DBench, Design Importer, StockView, TimeHEx, FragmentO, JKVBOC and
SOFT-BLAST Blastatistics). Every module, executable, interface mechanism and licensing
statement on the page is traceable to those documents; anything inferred is marked as an
assumption or a gap.

Framework applied: .claude/rules/TOGAF_BDAT_MINING_ADAPTED_Enterprise_Architecture_Framework.html
  - Tier 2B must map to Business Architecture — the portfolio and integration bands map
    back to the same eight-stage EMMM Exploit capability chain used on Tier 1
  - Dual application streams: enterprise IT, OT, and the integration points between them
  - Probabilistic systems in safety-critical mining — supervised autonomy, confidence
    thresholds, continuous validation, fallback, audit trails, governance gradient
  - Challenge A incompatible technology philosophies — preserve OT autonomy, manage
    integration boundaries, hybrid architecture
  - Challenge B IT/OT convergence cultural barriers — cross-functional teams, shared
    metrics, "purple people", third-party facilitation
  - Application portfolio governance — strategic / operational / tactical / legacy

Brand rules from .claude/rules/MINRES_Content_Guidelines.html: Century Gothic throughout;
MinRes Red #CE372F for title and accents; Dark Teal #00444C for band headers; Teal family
for IT, Coral/Peach family for OT, Wine family for IT/OT convergence and probabilistic
systems; Brown 100 #F1EDE7 for gaps and legacy; Olive family for governance classes.

Page is A3 landscape (1587 x 1123 px at 96dpi) with 24px margins, matching the companion
Business Architecture and Data Architecture pages.
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
    # external / not in this architecture — neutral
    "EX": {"fill": "#EFEFEF", "line": "#D4D4D4", "ink": "#6E6E6E", "bar": "#9A9A9A"},
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


def panel(x, y, w, h, title, desc, fill, line, ink, tsize=8, dsize=6.4, rule=True):
    """Filled card with a coloured top rule and a title / body text block."""
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, y, w, h)
    if rule:
        add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % ink, x, y, w, 3)
    add("<b><font style=\"font-size:%spx\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:%spx\" color=\"#000000\">%s</font>"
        % (tsize, ink, title, dsize, desc),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, y + (5 if rule else 3), w - 14, h - 8)


# ================================================================ header
add("", "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;" % RED, X0, 24, 8, 58)
add("Application Architecture — Drill &amp; Blast Blasting Software",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=19;fontStyle=1;fontColor=%s;"
    "align=left;verticalAlign=top;" % (CG, RED), 44, 21, 760, 26)
add("<b>Mineral Resources Limited</b>&#160;&#160;·&#160;&#160;JKTech JKSimBlast suite "
    "(2DBench, JKBMS, Design Importer, StockView, TimeHEx, 2DView, FragmentO, JKVBOC) "
    "+ SOFT-BLAST Blastatistics<br><b><font color=\"#CE372F\">SURFACE OPERATIONS ONLY — "
    "underground and development blasting (2DRing, 2DFace) is out of scope</font></b>"
    "&#160;&#160;·&#160;&#160;TOGAF BDAT <b>Tier 2B — Application Architecture</b>, "
    "mining-adapted. Maps to the <b>Business Architecture</b> (Tier 1) and <b>Data "
    "Architecture</b> (Tier 2A) pages — same <b>Exploit</b> capability chain, now expressed "
    "as applications, interfaces and governance.",
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
for i, (k, lbl) in enumerate([("IT", "IT domain"), ("CV", "IT/OT + probabilistic"),
                              ("OT", "OT — safety-critical"), ("EX", "external system")]):
    d = DOMAIN[k]
    add(lbl, LEG % (d["fill"], d["line"], d["ink"]), 1060 + i * 126, 66, 122, 14)

# ================================================================ Band A — dual streams
YA = 92
band(YA, 22, "DUAL APPLICATION STREAMS&#160;&#160;·&#160;&#160;ENTERPRISE IT, OPERATIONAL "
     "TECHNOLOGY, AND THE BOUNDARY BETWEEN THEM",
     "Framework Tier 2B item 1 — the two streams are co-equal and must not be collapsed "
     "into one")

STREAMS = [
    ("ENTERPRISE INFORMATION SYSTEMS&#160;&#160;·&#160;&#160;IT-CENTRIC",
     "<b>In this architecture:</b> the whole JKSimBlast design and record suite runs as "
     "Windows desktop applications in the office — 2DBench, Design Importer, "
     "StockView, Units, TimeHEx, 2DView — plus <b>JKBMS</b> as the record repository and the "
     "<b>Blastatistics web platform</b> for reporting and benchmarking.<br>"
     "<b>Depended on, not owned here:</b> mine planning and survey (Vulcan, Datamine, Surpac, "
     "AutoCAD), geology (AcQuire, Leapfrog), GIS (ArcGIS), ERP and cost, document management, "
     "plant historian, JKSimMet for downstream comminution.<br>"
     "<b>Characteristics:</b> data consistency, audit trail, financial accuracy, regulatory "
     "compliance. Controlled environment, reliable connectivity, standard change management.",
     "IT"),
    ("IT/OT INTEGRATION POINTS&#160;&#160;·&#160;&#160;WHERE THE TWO STREAMS MEET",
     "<b>IT &#8594; OT (one-way, safety-critical):</b> the approved design, charge sheet, "
     "tie-up plan and <b>timing / delay sequence</b> issued to the electronic detonator "
     "system for programming and firing.<br>"
     "<b>OT &#8594; IT:</b> as-drilled collars and MWD from the rigs; measured PPV and "
     "airblast from monitors; fragmentation image analysis (Split-Desktop); muckpile survey "
     "and blast movement measurement used to calibrate JKVBOC.<br>"
     "<b>At the bench:</b> the <b>Blastatistics mobile app</b> is the practical crossing "
     "point — design out to the crew, actuals back in.<br>"
     "<b>Hub / ROC:</b> site data surfaces to regional oversight through the web platform.",
     "CV"),
    ("OPERATIONAL TECHNOLOGY SYSTEMS&#160;&#160;·&#160;&#160;OT-CENTRIC",
     "<b>In the architecture but not in this suite:</b> drill rig onboard navigation and MWD; "
     "electronic detonator programming, testing and firing systems (OEM-owned); explosives "
     "delivery and MMU on-bench systems; vibration and airblast monitors; blast clearance, "
     "exclusion zone and radio systems.<br>"
     "<b>Critical statement:</b> the JKSimBlast suite contains <b>no OT control component</b>. "
     "It has no interlocks, no real-time acquisition and no automation — it produces the "
     "design and the timing that certified OT equipment executes.<br>"
     "<b>Characteristics:</b> deterministic behaviour, equipment and personnel safety, "
     "production continuity. Harsh environment, limited connectivity, conservative change.",
     "OT"),
]
AH = 100
for (x, w), (t, d, dom) in zip(grid(3, 10), STREAMS):
    dd = DOMAIN[dom]
    panel(x, YA + 26, w, AH, t, d, dd["fill"], dd["line"], dd["ink"], tsize=8, dsize=6.5)

# ================================================================ Band B — portfolio inventory
YB = YA + 26 + AH + 8
band(YB, 22, "APPLICATION PORTFOLIO&#160;&#160;·&#160;&#160;EVERY COMPONENT, WHAT IT DELIVERS, "
     "HOW IT IS DEPLOYED AND LICENSED",
     "Governance class per component is set in the portfolio governance band below")

APPS = [
    ("2DBench", "2DBench.exe&#160;·&#160;Strategic&#160;·&#160;site",
     "Surface bench, ramp, trench, sump and contour blast design in plan view — holes, decks, "
     "downhole and surface delays, connection architecture — plus detonation simulation, burden "
     "relief, Monte Carlo timing scatter and MIC analysis. Four modes: design, analysis, query, "
     "area. Windows desktop; dongle + licence file.", "IT"),
    ("Design Importer", "utility module&#160;·&#160;Operational&#160;·&#160;site",
     "Imports lines, polygons and blasthole collars from AutoCAD/DXF (R14), Datamine, Surpac, "
     "Vulcan and CSV/TXT straight into the design environment, with coordinate-system and unit "
     "handling and a user review and approval step before commit. <b>A translation tool, not an "
     "error-correction tool</b> — bad source geometry is faithfully reproduced.", "CV"),
    ("StockView + Units", "utility modules&#160;·&#160;Strategic data&#160;·&#160;corporate",
     "Explosives and accessory specification catalogue (type, density, VOD, weight strength, "
     "energy, detonators, primers, boosters, connectors, delay elements) and user-defined unit "
     "systems. Loadable from Orica and Enaex supplier data by text import. Always installed "
     "with every option and <b>needs no dongle</b>, but the database is per install.", "IT"),
    ("JKBMS", "JKBMS.exe&#160;·&#160;Strategic&#160;·&#160;site &#8594; corporate",
     "Blast Management System — the central repository and the long-term statutory record: pit "
     "and blast geometry, geotechnical and blasting domains, drilling parameters, costs, "
     "fragmentation distributions, vibration results, reports and comments. Opens blast "
     "databases saved by 2DBench (.2db).", "IT"),
    ("TimeHEx", "extended analysis&#160;·&#160;Operational&#160;·&#160;site",
     "Blast timing versus holes and explosives — initiation sequence, arrival times, wave "
     "interference and superposition, Maximum Instantaneous Charge by variable time window, "
     "Monte Carlo delay scatter, and single-point scaled-distance vibration. Supports "
     "electronic detonator delay-sequence design. Windows; dongle + licence file.", "CV"),
    ("2DView", "2DView.exe&#160;·&#160;Operational&#160;·&#160;site",
     "Section and oblique views of the design with explosive mass and energy distribution "
     "contours, and contouring of any hole-related attribute. Visual verification of charge "
     "distribution before the blast is approved; pairs with TimeHEx for timing review and with "
     "JKVBOC for movement interpretation.", "IT"),
    ("FragmentO", "extended analysis&#160;·&#160;Operational&#160;·&#160;site + hub",
     "Fragmentation size distribution prediction on a size-energy fan basis, ahead of the "
     "legacy Kuz-Ram / Rosin-Rammler / Swebrec fits, plus energy distribution analysis across "
     "the pattern. <b>Probabilistic output. Vendor-stated run time 30–90 minutes per "
     "blast</b> — a scenario tool, not an on-shift calculator.", "CV"),
    ("JKVBOC", "JK Value Based Ore Control&#160;·&#160;Operational&#160;·&#160;site + hub",
     "3D block-discretised physics engine predicting blast movement, ore loss and dilution, "
     "post-blast grade polygons and reserve value, with a mining polygons generator. "
     "Empirically calibrated against measured movement. <b>Probabilistic output. Run time "
     "10–30 min (vendor) or 30–90 min (secondary source) per simulation.</b>", "CV"),
    ("Blastatistics — web platform",
     "SaaS, different vendor&#160;·&#160;Operational&#160;·&#160;hub + corporate",
     "Multi-mine QA/QC and KPI platform from Blastics / SOFT-BLAST, access permissioned per mine "
     "and per function: same-day blast reports, consumption and cost, KPI dashboards and "
     "precision maps, trend graphs, custom reports. Exports to AcQuire, Minesight, Leapfrog, "
     "ArcGIS, AutoCAD, Excel. <b>Vendor-hosted.</b>", "IT"),
    ("Blastatistics — mobile app", "field app&#160;·&#160;Operational&#160;·&#160;site / in-pit",
     "Quality control at the blast, on shift: design versus actual per hole and deck, deviations, "
     "comments and photographs, synchronised to the platform. Deliberately minimal training for "
     "field crews. <b>The only component that lives in the pit — offline-first behaviour must "
     "be confirmed.</b>", "OT"),
    ("Blastics GEO Surface",
     "optional companion&#160;·&#160;Operational, not yet in scope&#160;·&#160;site",
     "Web platform plus mobile app for geological and grade-control capture in field and office "
     "— lithology, structure, weathering — linked to Blastics Surface so designers can read "
     "hardness maps and adjust the design to ground conditions. <b>Would overlap data geology "
     "already masters; treat as a separate decision, not part of this rollout.</b>", "CV"),
    ("External systems this depends on",
     "not in scope, but in the dependency chain&#160;·&#160;Legacy / third-party",
     "Mine planning and survey (Vulcan, Datamine, Surpac, AutoCAD), geology (AcQuire, Leapfrog), "
     "GIS (ArcGIS, Minesight), Split-Desktop image analysis, drill rig and MWD, detonator OEM "
     "systems, vibration monitors, ERP and cost, plant historian, JKSimMet, and the Orica "
     "toolset being displaced.", "EX"),
]
BH = 74
BG = grid(6, 6)
for i, (name, meta, desc, dom) in enumerate(APPS):
    x, w = BG[i % 6]
    y = YB + 26 + (i // 6) * (BH + 5)
    d = DOMAIN[dom]
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (d["fill"], d["line"]), x, y, w, BH)
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % d["bar"], x, y, w, 3)
    add("<b><font style=\"font-size:7.8px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:5.8px\" color=\"%s\"><b>%s</b></font><br>"
        "<font style=\"font-size:6.2px\" color=\"#000000\">%s</font>"
        % (d["ink"], name, d["ink"], meta, desc),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, y + 4, w - 14, BH - 7)

# ================================================================ Band C — integration
YC = YB + 26 + BH * 2 + 5 + 8
band(YC, 22, "APPLICATION INTEGRATION &amp; INTERFACE MECHANISMS&#160;&#160;·&#160;&#160;"
     "HOW THESE COMPONENTS ACTUALLY TALK TO EACH OTHER",
     "Every &#9888; is an unconfirmed, manual or absent interface — the real integration "
     "risk sits here, not in the modules")

INTEG = [
    ("I1", "Survey &amp; mine planning &#8594; Design Importer",
     "<b>File import, user-triggered.</b> DXF/R14, Datamine, Surpac, Vulcan, CSV, TXT. "
     "Coordinate system and units validated on import; import parameters recorded.", False),
    ("I2", "Design Importer &#8594; 2DBench",
     "<b>In-process, same install.</b> Imported geometry lands in the design environment "
     "after a user review and approval step. Removes the manual re-keying bottleneck.", False),
    ("I3", "StockView, Units &#8596; all design modules",
     "<b>Shared MS Access database.</b> This is the suite's integration bus — modules "
     "integrate by pointing at the same Access files, typically on a site share. "
     "&#9888; concurrency, locking, backup and audit are unaddressed.", True),
    ("I4", "2DBench &#8594; JKBMS",
     "<b>Save blast to blast database</b> (.2db, openable by JKBMS); v3-compatible text "
     "export also available. Gives design history and the statutory record one home.", False),
    ("I5", "Design / JKBMS &#8594; TimeHEx, 2DView, FragmentO, JKVBOC",
     "<b>Read the design, return a result.</b> &#9888; confirm predictions are stored against "
     "the blast with model version — and never into an as-fired field.", True),
    ("I6", "Design / TimeHEx &#8594; electronic detonator system",
     "<b>One-way, deterministic, safety-critical.</b> Timing and delay sequence issued to the "
     "OEM firing system. &#9888; exchange mechanism (file, format, manual entry) is "
     "OEM-specific and unconfirmed.", True),
    ("I7", "JKSimBlast &#8596; Blastatistics",
     "<b>Generic CSV, plus a vendor-stated JKSimBlast plugin.</b> Different vendor, different "
     "platform. &#9888; the two hold overlapping as-fired QA/QC records — the dual system of "
     "record carried from the Data Architecture page.", True),
    ("I8", "Interfaces that do not exist",
     "&#9888; <b>Drill rig / MWD</b>, <b>vibration and airblast monitors</b>, <b>ERP and "
     "cost</b>, <b>plant historian</b> — no native interface; actuals are re-keyed or "
     "re-surveyed. Downstream geology and GIS are <b>export, not integration</b>.", True),
]
CH = 64
for (x, w), (iid, t, d, gap) in zip(grid(8, 5), INTEG):
    fill, line = ("#F1EDE7", "#D9CDB8") if gap else ("#E0F7F9", "#B0EDF3")
    ink = "#6B5435" if gap else "#1A7C87"
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, YC + 26, w, CH)
    add(iid,
        "rounded=0;html=1;whiteSpace=wrap;fillColor=%s;strokeColor=none;fontFamily=%s;"
        "fontSize=6;fontStyle=1;fontColor=#FFFFFF;align=center;verticalAlign=middle;"
        % (ink, CG), x + w - 24, YC + 26, 24, 11)
    add("<b><font style=\"font-size:6.8px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:6.1px\" color=\"#000000\">%s</font>" % (ink, t, d),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 6, YC + 29, w - 32, CH - 6)

# ================================================================ Band D — IT/OT boundary
YD = YC + 26 + CH + 8
band(YD, 22, "THE IT/OT BOUNDARY&#160;&#160;·&#160;&#160;PRESERVING OPERATIONAL AUTONOMY FOR "
     "SAFETY-CRITICAL SYSTEMS",
     "Framework Challenge A — incompatible technology philosophies; hybrid model with managed "
     "boundaries")
BOUND = [
    ("WHAT CROSSES, AND IN WHICH DIRECTION",
     "<b>Out to OT:</b> the approved design, charge and deck sheet, tie-up plan, and the "
     "timing / delay sequence for programming. Issued once the engineer has signed it."
     "<br><b>Back from OT:</b> as-drilled collars and deviation, as-charged product and mass, "
     "non-conformances, firing confirmation, measured vibration, airblast, fragmentation and "
     "muckpile movement.<br><b>Nothing else crosses.</b> The list is deliberately short and "
     "should be treated as the interface contract.",
     "#F4D9DD", "#E8A5AD", "#8B2E45"),
    ("WHAT MUST NEVER CROSS",
     "No IT system initiates, arms, re-arms or commands a firing sequence. No model output "
     "writes directly to an OT device. No component of the firing path depends on corporate "
     "network or cloud availability. No automated change to a live design after the charge "
     "sheet is issued.<br><b>Firing authority stays with the licensed shotfirer on the "
     "certified OEM system</b> — the software's role ends at issuing an approved design.",
     "#F5E5DD", RED, "#8E5239"),
    ("HOW OT AUTONOMY IS PRESERVED HERE",
     "The suite is a <b>design and record system, not a control system</b> — no interlocks, "
     "no real-time acquisition, no automation — so OT change management, conservative upgrade "
     "cycles and the certified firing chain are untouched by anything on this page."
     "<br><b>The corollary binds IT:</b> the design and record core must run site-local and "
     "cannot be made dependent on corporate connectivity or continuous deployment. Cloud-first "
     "cannot be mandated for the design core or for in-pit capture.",
     "#E0F7F9", "#B0EDF3", "#1A7C87"),
    ("HYBRID MODEL &amp; BOUNDARY TRANSLATION",
     "OT produces data on OT terms — rig files, monitor reports, OEM firing logs. IT consumes, "
     "stores, analyses and retains it. Translation at the boundary must reconcile units, "
     "coordinate systems, time base and hole identity between systems that were never designed "
     "to agree.<br><b>Named gap:</b> no translation layer exists today. Every OT&#8594;IT flow "
     "is a person reading one screen and typing into another, which is where the same-day "
     "feedback loop is actually lost.",
     "#F1EDE7", "#D9CDB8", "#6B5435"),
]
DH = 92
for (x, w), (t, d, fill, line, ink) in zip(grid(4, 8), BOUND):
    panel(x, YD + 26, w, DH, t, d, fill, line, ink, tsize=8, dsize=6.4)

# ================================================================ Band E — probabilistic systems
YE = YD + 26 + DH + 8
band(YE, 22, "PROBABILISTIC &amp; MODEL-BASED APPLICATIONS IN A SAFETY-CRITICAL SETTING"
     "&#160;&#160;·&#160;&#160;GOVERNANCE THE FRAMEWORK REQUIRES",
     "FragmentO, JKVBOC, TimeHEx vibration and Monte Carlo timing — uncertain output, "
     "therefore governed as probabilistic")
PROB = [
    ("WHAT IS PROBABILISTIC — AND WHAT IS NOT",
     "<b>There is no machine learning in this suite today.</b> FragmentO is an energy-fan "
     "fragmentation model; JKVBOC a 3D physics engine; TimeHEx uses wave superposition and "
     "scaled distance; timing scatter is Monte Carlo. These are calibrated engineering models — "
     "but their output is <b>uncertain</b>, so the framework's probabilistic controls apply in "
     "full. Vendors flag ML, digital twin and AI optimisation as future direction: treat any "
     "such release as a new governance decision, not an upgrade."),
    ("SUPERVISED AUTONOMY",
     "Model output is a <b>recommendation</b>. The D&amp;B engineer signs the design; the "
     "licensed shotfirer fires it. No automated OT action, ever — including no automatic "
     "adjustment of charge, timing or dig polygons from a prediction. Where a prediction "
     "drives a downstream decision (a dig polygon, a receiver limit), the human decision is "
     "recorded alongside it."),
    ("CONFIDENCE THRESHOLDS &amp; ESCALATION",
     "<b>High consequence</b> — predicted PPV or airblast near a licence limit, predicted "
     "movement redefining an ore boundary, MIC at the envelope edge: engineer plus hub review "
     "before firing.<br><b>Low consequence</b> — comparative fragmentation studies, parameter "
     "sensitivity: site decision.<br><b>&#9888; Two gaps:</b> the thresholds are not defined, "
     "and 30–90 minute run times mean these models cannot be re-run inside an on-shift "
     "decision — scenarios must be pre-computed."),
    ("CONTINUOUS VALIDATION &amp; DRIFT",
     "Back-analyse predicted versus measured every blast — Split-Desktop fragmentation, "
     "monitored PPV and airblast, muckpile survey and movement measurement — and recalibrate "
     "per geotechnical and blasting domain. Version the calibration set. Watch for drift when "
     "ore type, bench height, product or supplier changes; a model calibrated on one domain "
     "is not valid in another. Blastatistics KPI trends are the practical drift detector."),
    ("FALLBACK &amp; FAILURE MODES",
     "Model unavailable, out of calibration, or inputs incomplete &#8594; revert to site "
     "empirical charts, conservative MIC limits and the standard pattern, and widen the dig "
     "envelope rather than trusting a predicted boundary. Blasting continues; only the "
     "optimisation stops.<br><b>&#9888; Real single point of failure:</b> the design modules "
     "need a USB dongle and a matching licence file. A lost or failed dongle stops design "
     "work — needs a spare-key and re-issue procedure."),
    ("AUDIT TRAIL &amp; GOVERNANCE GRADIENT",
     "Retain per blast: the prediction, the model and version, the calibration set, the "
     "inputs, the engineer's decision and the measured outcome — the evidence chain a "
     "regulator or an incident review will ask for.<br><b>Gradient:</b> environmental and "
     "safety-relevant models need governance approval and periodic review; productivity "
     "models are lighter.<br><b>&#9888; Confirm the suite can store model metadata against a "
     "blast</b>; if not, it is a Tier 3 requirement."),
]
EH = 92
for (x, w), (t, d) in zip(grid(6, 6), PROB):
    panel(x, YE + 26, w, EH, t, d, "#F4D9DD", "#E8A5AD", "#8B2E45", tsize=7.4, dsize=6.1)

# ================================================================ Band F — portfolio governance
YF = YE + 26 + EH + 8
band(YF, 22, "APPLICATION PORTFOLIO GOVERNANCE&#160;&#160;·&#160;&#160;CLASS SETS THE LEVEL "
     "OF CONTROL, NOT THE OTHER WAY AROUND",
     "Framework Tier 2B item 4 — strategic / operational / tactical / legacy")
GOVC = [
    ("STRATEGIC — CORE TO THE BUSINESS",
     "<b>JKBMS</b> (statutory record), <b>2DBench</b> (the design standard in practice), "
     "<b>StockView as corporate reference data</b>, and — in the OT stream — the electronic "
     "detonator firing chain as a <b>safety system</b>.<br><b>Governance:</b> formal "
     "architecture review, governance approval, coordinated deployment across the enterprise. "
     "Version, catalogue and record changes are not site decisions.",
     "#E0F7F9", "#B0EDF3", "#1A7C87"),
    ("OPERATIONAL — SUPPORT SPECIFIC FUNCTIONS",
     "Design Importer, TimeHEx, 2DView, FragmentO, JKVBOC, and Blastatistics web and mobile."
     "<br><b>Governance:</b> review at hub or site level; module mix may legitimately vary by "
     "operation — an iron ore bench and a lithium pit need different analysis depth. "
     "Constraint: they must read and write the same design and record core. Any later "
     "underground scope would enter the portfolio here, as a new decision.",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("TACTICAL — LOCAL POINT SOLUTIONS",
     "Site blast spreadsheets, local Access copies, locally maintained explosives lists, "
     "hand-built report templates and the tie-up sketches this architecture is meant to "
     "replace.<br><b>Governance:</b> permitted locally without enterprise approval, but must "
     "not conflict with strategic or operational applications — and must not become the "
     "shadow system of record. Retire deliberately, not by decree.",
     "#F0F2E5", "#D9DCBC", "#5E623C"),
    ("LEGACY — OPERATE WITH AN EXIT DATE",
     "<b>JKSimBlast v2.x itself sits here:</b> MS Access backend, Windows desktop lineage "
     "(XP through 10 in the vendor statements), dongle licensing — and <b>v3.0 in development "
     "is stated to change the database system</b>. Adopting v2.x without a v3 migration "
     "position is buying a migration.<br>Also legacy: the Orica toolset being displaced — see "
     "the companion migration page.<br><b>Governance:</b> explicit retirement dates and a "
     "migration path, maintained but not extended.",
     "#F1EDE7", "#D9CDB8", "#6B5435"),
]
FH2 = 88
for (x, w), (t, d, fill, line, ink) in zip(grid(4, 8), GOVC):
    panel(x, YF + 26, w, FH2, t, d, fill, line, ink, tsize=8, dsize=6.4)

# ================================================================ Band G — cultural barriers
YG = YF + 26 + FH2 + 8
band(YG, 22, "IT/OT CONVERGENCE BARRIERS FLAGGED FOR MANAGEMENT ATTENTION&#160;&#160;·"
     "&#160;&#160;STRUCTURAL, NOT SOLVED BY ARGUMENT",
     "Framework Challenge B — these are the delivery risks most likely to stall the rollout")
CULT = [
    ("CROSS-FUNCTIONAL TEAM WITH SPLIT AUTHORITY",
     "Put D&amp;B engineering, shotfirers, mine survey, geology, HSE and IT on the same team, "
     "with decision rights allocated by domain: IT decides platform and integration with D&amp;B "
     "input; D&amp;B and the shotfirer decide anything touching the firing path, with IT input."),
    ("SHARED SUCCESS METRICS",
     "One scorecard both sides own: design compliance %, blast-to-report time (same day), "
     "re-keying eliminated, zero exceedances and zero misfires. Not \"system delivered\" for IT "
     "and \"tonnes fired\" for operations — that split is what makes the relationship adversarial."),
    ("\"PURPLE PEOPLE\" AND FIELD CREDIBILITY",
     "This architecture needs people who can read a tie-up plan and a database schema. Name "
     "them, fund them and keep them; without that translation the field app gets bypassed on "
     "the first bad shift and the record is lost. Governance is earned by demonstrated value "
     "to the crew, not by process."),
    ("NEUTRAL FACILITATION AND VENDOR REALITY",
     "Two vendors (JKTech and Blastics/SOFT-BLAST) plus explosives suppliers and detonator OEMs "
     "each own part of the chain. Where the integration argument is really commercial, use "
     "neutral facilitation and put the interface obligations in the contract — architecture "
     "cannot fix a boundary the contracts leave open."),
]
GH = 54
for (x, w), (t, d) in zip(grid(4, 8), CULT):
    box(head_desc(t, d, "#5E623C", tsize=7.6, dsize=6.3), x, YG + 26, w, GH,
        "#F0F2E5", "#D9DCBC", INK, fs=7)

# ================================================================ footer
YH = YG + 26 + GH + 8
FTH = 128
FG = grid(2, 8)
LX, LW = FG[0]
RX, RW = FG[1]

add("", "rounded=0;html=1;fillColor=#FFFFFF;strokeColor=#B8DDE3;", LX, YH, LW, FTH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % TEAL, LX, YH, 5, FTH)
add("TRACEABILITY&#160;&#160;·&#160;&#160;IN THE FORM THE FRAMEWORK REQUIRES",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, TEAL), LX + 14, YH + 7, LW - 28, 12)
add("<b><font color=\"#2D686F\">THESE APPLICATIONS DELIVER BUSINESS CAPABILITY</font></b> — "
    "EMMM <b>Exploit: design, fire and reconcile a surface blast</b>, with interfaces into "
    "<b>Establish</b> (vibration and airblast limits for permitting), <b>Beneficiate</b> "
    "(fragmentation to crusher and mill) and <b>Support</b> (QA/QC evidence and retention) — "
    "<b>at corporate level</b> (StockView catalogue, JKBMS record, KPI definitions), "
    "<b>hub level</b> (Blastatistics benchmarking, FragmentO and JKVBOC scenario work) and "
    "<b>site level</b> (design, charge, timing, in-pit capture).<br>"
    "<b><font color=\"#8E5239\">DOMAIN</font></b> — the JKSimBlast suite and Blastatistics web "
    "operate in the <b>IT domain</b>; the Blastatistics mobile app and the Design Importer "
    "boundary operate in <b>integrated IT/OT</b>; drill/MWD, detonator firing systems and "
    "monitors are <b>OT domain</b> and stay outside this suite.<br>"
    "<b><font color=\"#8B2E45\">FOR OT SYSTEMS, THIS ARCHITECTURE PRESERVES</font></b> — "
    "<b>deterministic behaviour</b> (timing issued one-way to a certified firing system), "
    "<b>safety criticality</b> (firing authority with the licensed shotfirer; no IT command "
    "path) and <b>operational autonomy</b> (no interlocks or automation introduced; site-local "
    "operation independent of corporate connectivity).<br>"
    "<b><font color=\"#8B2E45\">FOR MODEL-BASED SYSTEMS, UNCERTAINTY IS ACCOUNTED FOR THROUGH"
    "</font></b> — monitoring (predicted versus measured every blast, per-domain "
    "recalibration), fallback (empirical charts and conservative MIC), governance controls "
    "(advisory only, human-in-the-loop, gradient by consequence), confidence thresholds "
    "(to be defined — a stated gap) and audit trails (model, version, inputs, decision, "
    "outcome).",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.5;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, LX + 14, YH + 22, LW - 28, FTH - 28)

add("", "rounded=0;html=1;fillColor=#F1EDE7;strokeColor=#D9CDB8;", RX, YH, RW, FTH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % RED, RX, YH, 5, FTH)
add("GAPS, ASSUMPTIONS &amp; NEXT STEPS",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, RED), RX + 14, YH + 7, RW - 28, 12)
add("<b>Structural gaps in the application architecture as it stands:</b> "
    "(1) <b>integration is a shared file-based database</b>, not an interface — modules "
    "co-operate by pointing at the same MS Access files, so concurrency, locking, backup and "
    "multi-site sharing are unresolved. "
    "(2) <b>Two overlapping systems of record</b> for as-fired QA/QC (JKBMS and Blastatistics) "
    "exchanging by CSV and a plugin; nominate one before either goes further. "
    "(3) <b>No OT&#8594;IT translation layer</b> — drill/MWD, monitors, ERP and historian are "
    "all manual, which is what breaks the same-day loop the field app is bought for. "
    "(4) <b>Detonator interface unconfirmed</b> — the mechanism for issuing timing to the OEM "
    "firing system is the most safety-relevant interface on the page and the least documented. "
    "(5) <b>Model metadata storage unconfirmed</b>, and <b>no confidence thresholds defined</b>. "
    "(6) <b>Licensing is a dongle and licence file per seat</b> — an availability risk with no "
    "stated redundancy. "
    "(7) <b>Offline behaviour of the mobile app is asserted, not verified.</b><br>"
    "<b>Assumptions to confirm with the vendors:</b> that v2.x uses MS Access and that v3.0 "
    "changes it; that StockView, Import and Units genuinely need no key (one source says the "
    "Design Importer is dongle-controlled — the two statements conflict); that the "
    "Blastatistics JKSimBlast plugin is production, not roadmap; supported Windows baseline "
    "and 64-bit status.<br>"
    "<b>Deliberately out of scope:</b> <b>underground and development blasting</b> — 2DRing "
    "(stope rings) and 2DFace (tunnel, drift and shaft faces) are excluded, so this is a "
    "<b>surface-only</b> portfolio; bringing underground in later re-opens the portfolio and "
    "the licence pool. Also out of scope: Tier 3 Technology Architecture — database platform, "
    "servers and site infrastructure, ruggedised devices, network and connectivity design, "
    "hosting and residency, identity, backup and disaster recovery, licence sizing.<br>"
    "<b>Next steps:</b> confirm the interface inventory with JKTech and Blastics in writing; "
    "nominate the system of record; specify the OT&#8594;IT translation requirement; define "
    "confidence thresholds with HSE and Environment; then take Tier 3.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.1;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, RX + 14, YH + 22, RW - 28, FTH - 28)

BOTTOM = YH + FTH
add("Mineral Resources Limited&#160;&#160;·&#160;&#160;Application Architecture, one-page view"
    "&#160;&#160;·&#160;&#160;Surface operations only — underground out of scope"
    "&#160;&#160;·&#160;&#160;A3 landscape&#160;&#160;·&#160;&#160;Companion to "
    "MinRes_Blasting_Software_Business_Architecture (Tier 1) and "
    "MinRes_Blasting_Software_Data_Architecture (Tier 2A)",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;fontColor=#888888;align=left;"
    "verticalAlign=middle;" % CG, X0, BOTTOM + 6, W, 12)

# ================================================================ assemble
PW, PH = 1587, 1123
XML = (
    '<mxfile host="app.diagrams.net" agent="Claude Code" version="24.0.0" type="device">\n'
    '  <diagram name="Application Architecture - Blasting Software" id="minres-blast-apparch">\n'
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
                        "MinRes_Blasting_Software_Application_Architecture.drawio")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(XML)
    print("wrote %s" % dest)
    print("content bottom = %spx of %s ; %d cells" % (BOTTOM + 18, PH, _id[0] - 1))
