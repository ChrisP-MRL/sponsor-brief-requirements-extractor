# -*- coding: utf-8 -*-
"""Build the one-page Data Architecture diagram for the blasting software as Draw.io.

Companion to blasting_business_architecture_drawio.py. Scope: TOGAF BDAT Tier 2A
(Data Architecture) only, mining-adapted, and SURFACE OPERATIONS ONLY — underground and
tunnel blasting (2DRing, 2DFace) are out of scope by decision, which closes the open
question the Business Architecture page carried. Application-internal (Tier 2B) and
Technology (Tier 3) architecture stay out of scope and the gaps are stated on the page, as
the framework's traceability checklist requires.

Source of content: input/JKTech Software/ — the eight vendor capability analyses
(JKSimBlast, 2DBench, Design Importer, StockView, TimeHEx, FragmentO, JKVBOC and
SOFT-BLAST Blastatistics). Every entity, format and store named on the page is traceable
to those documents; anything inferred is marked as an assumption or a gap.

Framework applied: .claude/rules/TOGAF_BDAT_MINING_ADAPTED_Enterprise_Architecture_Framework.html
  - Tier 2A must map to Business Architecture — the data lifecycle band uses the same
    eight-stage Exploit capability chain as the Business Architecture page
  - Mining data domains (exploration, production, processing, environmental, supply chain)
  - Challenge A remote connectivity — edge curation / hot-warm-cold layering / async sync
  - Challenge B ownership ambiguity — three-tier stewardship (producer, consumer, enterprise)
  - Challenge C regulatory complexity — regulatory data mapping and retention by jurisdiction
  - Data quality and observability across completeness, accuracy, timeliness, consistency,
    traceability
  - Principle 3 safety first — probabilistic model output carries model version, inputs and
    the engineer decision, and stays advisory

Brand rules from .claude/rules/MINRES_Content_Guidelines.html: Century Gothic throughout;
MinRes Red #CE372F for title and accents; Dark Teal #00444C for band headers; Teal family
for IT, Coral/Peach family for OT, Wine family for IT/OT convergence and probabilistic
systems; Brown 100 #F1EDE7 for regulatory; Olive family for data quality.

Page is A3 landscape (1587 x 1123 px at 96dpi) with 24px margins, matching the companion
Business Architecture page.
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


def chip(text, x, y, w, h, fill, fs=6.5, fcol="#FFFFFF"):
    add(text,
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;fontFamily=%s;"
        "fontSize=%s;fontColor=%s;align=left;verticalAlign=middle;spacingLeft=6;"
        "spacingRight=5;" % (fill, CG, fs, fcol), x, y, w, h)


# ================================================================ header
add("", "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;" % RED, X0, 24, 8, 58)
add("Data Architecture — Drill &amp; Blast Blasting Software",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=19;fontStyle=1;fontColor=%s;"
    "align=left;verticalAlign=top;" % (CG, RED), 44, 21, 720, 26)
add("<b>Mineral Resources Limited</b>&#160;&#160;·&#160;&#160;JKTech JKSimBlast suite "
    "(2DBench, JKBMS, Design Importer, StockView, TimeHEx, 2DView, FragmentO, JKVBOC) + "
    "SOFT-BLAST Blastatistics<br><b><font color=\"#CE372F\">SURFACE OPERATIONS ONLY — "
    "underground and tunnel blasting (2DRing, 2DFace) are out of scope by decision"
    "</font></b><br>TOGAF BDAT <b>Tier 2A — Data Architecture</b>, mining-adapted. Maps to "
    "the <b>Business Architecture</b> page: same eight-stage EMMM <b>Exploit</b> chain, as "
    "data entities, stores and stewardship.",
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
for i, (k, lbl) in enumerate([("IT", "IT data"), ("CV", "IT/OT + model output"),
                              ("OT", "OT / field-captured data")]):
    d = DOMAIN[k]
    add(lbl, LEG % (d["fill"], d["line"], d["ink"]), 1060 + i * 130, 66, 126, 14)

# ================================================================ Band A — mining data domains
YA = 92
band(YA, 22, "MINING DATA DOMAINS&#160;&#160;·&#160;&#160;WHAT DATA THIS ARCHITECTURE HOLDS, "
     "AND WHAT IT ONLY BORROWS",
     "Framework domains — exploration, production, processing, environmental, supply chain")
DOMAINS = [
    ("GEOLOGY &amp; ROCK MASS", "CONSUMED, NOT MASTERED",
     "Block model grades and attributes, rock mass classification (RQD, RMQR), UCS, "
     "discontinuity orientation / spacing / persistence, in-situ block size, weathering, "
     "water saturation, hardness maps. Mastered outside this suite; the blasting tools read "
     "it and must not fork it.",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("D&amp;B DESIGN &amp; INTENT", "PRIMARY — MASTERED HERE",
     "Blast header (ID, pit, bench, domain, version, approval), excavation outline polygons, "
     "blasthole geometry in full 3D (east, north, level), decks, stemming, subdrill, delays, "
     "connection network, timing and MIC. The suite is the authoritative source.",
     "#F9E5E3", RED, RED),
    ("EXPLOSIVES MASTER DATA", "PRIMARY — MASTERED HERE",
     "Product specifications (type, density, VOD, weight strength vs ANFO, energy, coupling), "
     "detonators, primers, boosters, connectors, delay elements and their scatter, "
     "user-defined unit systems. Loaded from Orica and Enaex supplier data by text import.",
     "#F9E5E3", RED, RED),
    ("PRODUCTION FIELD ACTUALS", "PRIMARY — CAPTURED AT THE EDGE",
     "As-drilled collars and deviation from design, actual product and mass loaded per hole "
     "and deck, stemming, water, non-conformances, comments, photographs, crew, timestamps. "
     "High-velocity, remote, intermittently connected — the hardest data in the architecture.",
     "#F5E5DD", "#E8C4B0", "#8E5239"),
    ("ENVIRONMENTAL &amp; SAFETY", "SPLIT — PREDICTED HERE, MEASURED ELSEWHERE",
     "Predicted and measured ground vibration (PPV), airblast, scaled distance, MIC by time "
     "window, sensitive receiver register, dust and fume events, misfire and flyrock records. "
     "Prediction is native; the monitor feed is not — a named gap.",
     "#EFEFEF", "#D4D4D4", "#6E6E6E"),
    ("PROCESSING &amp; SUPPLY CHAIN", "INTERFACE — MINE-TO-MILL HAND-OFF",
     "Fragmentation size distribution, muckpile shape and 3D movement vectors, ore loss and "
     "dilution, post-blast dig polygons and reserves, explosives consumption and cost per "
     "blast and per tonne, crusher and mill throughput and comminution energy (external).",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
]
for (x, w), (t, cov, d, fill, line, ink) in zip(grid(6, 6), DOMAINS):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, YA + 26, w, 66)
    add("<b><font style=\"font-size:8px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:6.2px\" color=\"%s\"><b>%s</b></font><br>"
        "<font style=\"font-size:6.4px\" color=\"#000000\">%s</font>" % (ink, t, ink, cov, d),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, YA + 29, w - 13, 60)

# ================================================================ Band B — data lifecycle
YB = 190
band(YB, 22, "DATA ENTITIES ALONG THE EXPLOIT CAPABILITY CHAIN&#160;&#160;·&#160;&#160;"
     "SYSTEM OF RECORD AND STEWARDSHIP AT EACH STAGE",
     "Same eight stages as the Business Architecture page — Tier 2A must map to Tier 1")

STAGES = [
    ("1 · Plan &amp; design",
     "<b>Blast header</b> — blast ID, pit, bench, RL, geotech and blasting domain, design "
     "version, engineer, approval state.<br><b>Excavation outline</b> — bench, crest and toe, "
     "ramp, trench, sump and boundary polygons — <b>surface bench blasting in plan view</b>."
     "<br><b>Blasthole</b> — collar E/N/RL, diameter, depth, angle, "
     "bearing, subdrill, burden, spacing.<br><b>Deck</b> — product, mass, length, stemming.",
     "2DBench &#8594; JKBMS&#160;·&#160;MS Access, site-held",
     "Producer: site D&amp;B engineer &#8594; Consumer: shotfirer, geology, mine planning",
     "IT"),
    ("2 · Design data in",
     "<b>Survey and pit geometry</b> — lines, polygons, topography surfaces, pit walls, "
     "ore/waste interfaces.<br><b>Surveyed collars</b> — designed vs surveyed positions."
     "<br><b>Receiver register</b> — infrastructure and sensitive structure locations."
     "<br><b>Metadata</b> — coordinate system, units, and an import audit record (source "
     "file, parameters, modifications).",
     "Design Importer&#160;·&#160;DXF / AutoCAD R14, Datamine, Surpac, Vulcan, CSV, TXT",
     "Producer: mine survey and mine planning &#8594; Consumer: D&amp;B design",
     "CV"),
    ("3 · Explosives master data",
     "<b>Explosive product</b> — type, density, VOD, weight strength vs ANFO, energy, "
     "coupling, confinement behaviour.<br><b>Accessories</b> — detonators, primers, boosters, "
     "connectors.<br><b>Delay element</b> — nominal delay and scatter.<br><b>Unit system</b> — "
     "user-defined, metric or imperial.<br><b>Reference data — should be corporate MDM.</b>",
     "StockView&#160;·&#160;MS Access, per install; text import from supplier data",
     "Producer: Corporate (approved catalogue) &#8594; Consumer: every designer",
     "IT"),
    ("4 · Charge &amp; timing",
     "<b>Charge rule</b> — mass per deck, stemming height, multi-deck configuration."
     "<br><b>Delay assignment</b> — downhole and surface delays, connection and tie-up "
     "network.<br><b>Initiation sequence</b> — firing time per hole and deck, arrival times."
     "<br><b>MIC by time window</b>, timing scatter (Monte Carlo).<br><b>Timing file issued "
     "to the electronic detonator system — the OT boundary.</b>",
     "2DBench + TimeHEx &#8594; JKBMS&#160;·&#160;MS Access; timing export to detonator OEM",
     "Producer: D&amp;B engineer &#8594; Consumer: licensed shotfirer, detonator OEM system",
     "CV"),
    ("5 · Predicted outcomes",
     "<b>Fragmentation curve</b> — size distribution and characteristic passing size (Kuz-Ram, "
     "Rosin-Rammler, Swebrec), energy distribution contours.<br><b>Vibration prediction</b> — "
     "PPV and arrival time per receiver, scaled distance, airblast.<br><b>Movement "
     "prediction</b> — 3D block displacement vectors, muckpile shape, ore loss and dilution, "
     "post-blast grade polygons.<br><b>Mandatory metadata: model, version, calibration set, "
     "inputs, engineer decision.</b>",
     "FragmentO, TimeHEx, JKVBOC + 2DView&#160;·&#160;model output, ADVISORY ONLY",
     "Producer: D&amp;B engineer &#8594; Consumer: grade control, processing, environment",
     "CV"),
    ("6 · Field actuals &amp; QA/QC",
     "<b>As-drilled hole</b> — actual collar, depth, angle, deviation vs design."
     "<br><b>As-charged deck</b> — product and mass actually loaded, stemming, water."
     "<br><b>Non-conformance</b> — deviation, comment, photograph, corrective action."
     "<br><b>Context</b> — crew, licensed shotfirer, timestamp, position."
     "<br><b>Sync state</b> — offline capture queue, sync status, conflict flag.",
     "Blastatistics mobile app&#160;·&#160;offline-first capture, vendor-hosted web platform",
     "Producer: field crew and shotfirer &#8594; Consumer: engineer, hub, regulator",
     "OT"),
    ("7 · Measured outcomes &amp; statutory record",
     "<b>Measured environmental</b> — PPV and airblast per monitor and receiver, complaints."
     "<br><b>Measured fragmentation</b> — image analysis (Split-Desktop), oversize count."
     "<br><b>Measured movement</b> — muckpile survey, dig polygon and reserve reconciliation."
     "<br><b>Explosives reconciliation</b> — issued vs used vs returned.<br><b>Incident</b> — "
     "misfire, flyrock, fume.<br><b>Blast cost.</b>",
     "JKBMS — the long-term statutory record&#160;·&#160;MS Access; inbound feeds manual/CSV",
     "Producer: monitoring and survey providers &#8594; Enterprise steward: Corporate",
     "IT"),
    ("8 · Analytics, benchmark &amp; mine-to-mill",
     "<b>Blast KPI set</b> — powder factor, design compliance %, $/t and $/BCM, oversize %, "
     "blast-to-report time.<br><b>Back-analysis</b> — predicted vs measured, recalibration "
     "record per domain.<br><b>Trend graphs and KPI precision maps.</b><br><b>Multi-site "
     "benchmark</b> — permissioned per mine.<br><b>Downstream</b> — crusher and mill "
     "throughput, comminution energy per tonne (external historian).",
     "Blastatistics analytics + JKSimBlast&#160;·&#160;exports to Excel, AcQuire, ArcGIS",
     "Producer: hub analyst &#8594; Consumer: Corporate, Processing, Mining Services",
     "IT"),
]

CHY, CHH = YB + 26, 26                # chevron stage header
EY, EH = CHY + CHH + 4, 106           # entity list
SRY, SRH = EY + EH + 4, 24            # system of record / format
STY, STH = SRY + SRH + 4, 22          # stewardship

for (x, w), (name, ents, sor, stew, dom) in zip(grid(8, 5), STAGES):
    d = DOMAIN[dom]
    add(name,
        "shape=step;perimeter=stepPerimeter;whiteSpace=wrap;html=1;fixedSize=1;size=8;"
        "fillColor=%s;strokeColor=none;fontFamily=%s;fontSize=7.5;fontStyle=1;"
        "fontColor=#FFFFFF;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=6;"
        % (d["bar"], CG), x, CHY, w, CHH)
    box("<font style=\"font-size:6.3px\" color=\"#000000\">%s</font>" % ents,
        x, EY, w, EH, d["fill"], d["line"], INK, fs=6.3, pad=6)
    chip("<b>%s</b>" % sor, x, SRY, w, SRH, d["ink"])
    chip(stew, x, STY, w, STH, "#EFEFEF", fs=6.2, fcol="#424242")

# ================================================================ Band C — integration points
YC = STY + STH + 6
band(YC, 22, "INTEGRATION POINTS &amp; DATA EXCHANGE FORMATS&#160;&#160;·&#160;&#160;WHERE "
     "DATA CROSSES AN OWNERSHIP BOUNDARY",
     "File-based exchange dominates. Every &#9888; is a manual re-keying or reconciliation risk")
INTEG = [
    ("IN", "Mine planning &amp; survey",
     "AutoCAD R14 / DXF, Datamine, Surpac, Vulcan, CSV, TXT. Validated on import — coordinate "
     "system, units, geometry.", False),
    ("IN", "Explosives suppliers",
     "Orica and Enaex product specifications loaded to StockView by text import. No live "
     "supplier feed.", True),
    ("IN", "Drill rigs / MWD",
     "As-drilled collars, depth and penetration rate. <b>No native interface</b> — actuals are "
     "hand-entered or re-surveyed.", True),
    ("OUT", "Electronic detonator systems",
     "Timing and delay sequence issued to the OEM firing system. One-way, deterministic, "
     "safety-critical.", False),
    ("IN", "Vibration &amp; airblast monitors",
     "Measured PPV and airblast per receiver. <b>No native feed</b> — results are typed into "
     "JKBMS from monitor reports.", True),
    ("IN", "Fragmentation measurement",
     "Split-Desktop image analysis linked to Blastatistics; closes the predicted-vs-measured "
     "loop for FragmentO.", False),
    ("IN/OUT", "Grade control &amp; geology",
     "Block model in, post-blast polygons out — AcQuire, Leapfrog, ArcGIS, Minesight, "
     "AutoCAD, Excel. <b>Exchange, not integration.</b>", True),
    ("IN", "Cost, ERP &amp; plant historian",
     "Explosives cost, $/t and mill throughput for mine-to-mill KPIs. <b>Not interfaced</b> — "
     "assembled by hand.", True),
]
for (x, w), (dirn, t, d, gap) in zip(grid(8, 5), INTEG):
    fill, line = ("#F1EDE7", "#D9CDB8") if gap else ("#E0F7F9", "#B0EDF3")
    ink = "#6B5435" if gap else "#1A7C87"
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, YC + 26, w, 52)
    add("<font style=\"font-size:6px\" color=\"#FFFFFF\">&#160;%s&#160;</font>" % dirn,
        "rounded=0;html=1;whiteSpace=wrap;fillColor=%s;strokeColor=none;fontFamily=%s;"
        "fontSize=6;fontStyle=1;fontColor=#FFFFFF;align=center;verticalAlign=middle;"
        % (ink, CG), x + w - 34, YC + 26, 34, 11)
    add("<b><font style=\"font-size:7px\" color=\"%s\">%s%s</font></b><br>"
        "<font style=\"font-size:6.2px\" color=\"#000000\">%s</font>"
        % (ink, "&#9888; " if gap else "", t, d),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 6, YC + 29, w - 44, 48)

# ================================================================ Band D — layered storage
YD = YC + 84
band(YD, 22, "LAYERED DATA ARCHITECTURE FOR REMOTE OPERATIONS&#160;&#160;·&#160;&#160;"
     "EDGE &#8594; SITE &#8594; HUB &#8594; ENTERPRISE",
     "Framework Challenge A — remote collection with intermittent connectivity")
LAYERS = [
    ("EDGE — in-pit curation",
     "Capture at the blast on shift, on a ruggedised tablet, <b>with no connectivity assumed"
     "</b>. Validate at the point of capture — mandatory fields, range checks, photographs "
     "attached to the hole. Curate before transmission: full-resolution images stay local "
     "until a window opens.<br><b>Holds:</b> today's blast, open non-conformances, sync queue.",
     "#F5E5DD", "#E8C4B0", "#8E5239"),
    ("HOT — site",
     "The working design and record set, on site infrastructure, independent of corporate "
     "connectivity. This is where a blast is designed, approved and fired from."
     "<br><b>Holds:</b> live designs, explosives catalogue in use, current bench and pit "
     "geometry, this campaign's blasts.<br><b>Today: MS Access files on a site share — "
     "concurrency, backup and audit are a Tier 3 decision, not solved here.</b>",
     "#E0F7F9", "#B0EDF3", "#1A7C87"),
    ("WARM — hub / regional",
     "Recent history for comparison, benchmarking and hub oversight, with access permissioned "
     "per mine so cross-site learning does not mean uncontrolled access."
     "<br><b>Holds:</b> rolling recent blasts, KPI trends, precision maps, hub targets and "
     "parameter ranges per ore type.<br><b>Today: the Blastatistics web platform, "
     "vendor-hosted — residency and exit are open.</b>",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("COLD — enterprise archive",
     "The statutory and corporate memory. Written once, never edited: design as approved, "
     "as-fired actuals, measured outcomes, model version and the engineer decision."
     "<br><b>Holds:</b> full blast record to the longest applicable retention period, "
     "explosives reconciliation, incident and exceedance evidence."
     "<br><b>Today: JKBMS long-term retention — enterprise archive not yet designed.</b>",
     "#F4D9DD", "#E8A5AD", "#8B2E45"),
]
LG = grid(4, 30)
for (x, w), (t, d, fill, line, ink) in zip(LG, LAYERS):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, YD + 26, w, 90)
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % ink, x, YD + 26, w, 3)
    add("<b><font style=\"font-size:8px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:6.4px\" color=\"#000000\">%s</font>" % (ink, t, d),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, YD + 31, w - 14, 84)
for i in range(3):
    gx = LG[i][0] + LG[i][1] + 3
    add("", "shape=singleArrow;html=1;direction=east;dy=0.5;dx=8;fillColor=#2D686F;"
        "strokeColor=none;", gx, YD + 64, 24, 14)

add("<b>Asynchronous synchronisation</b> — field capture is queued and synchronises in "
    "connectivity windows, not in real time; nothing waits on the network to be recorded. "
    "<b>Conflict rule (to ratify):</b> the office design file is authoritative for design "
    "intent; the field capture is authoritative for what was actually drilled, charged and "
    "fired. Neither silently overwrites the other — a conflict is flagged and closed by the "
    "engineer, and the resolution is retained.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.8;fontColor=#1D4347;align=left;"
    "verticalAlign=middle;" % CG, X0 + 2, YD + 118, W - 4, 20)

# ================================================================ Band E — stewardship
YE = YD + 138
band(YE, 22, "THREE-TIER DATA STEWARDSHIP&#160;&#160;·&#160;&#160;WHO IS ACCOUNTABLE FOR "
     "WHICH DATA, AND WHERE OWNERSHIP IS STILL UNCLEAR",
     "Framework Challenge B — ownership ambiguity in siloed operations")
STEW = [
    ("PRODUCER STEWARDSHIP",
     "The function that generates the data owns its initial quality, validation and "
     "documentation.<br><b>Mine survey and planning</b> — pit and bench geometry, surveyed "
     "collars, coordinate system.<br><b>D&amp;B engineering</b> — design, charge rules, "
     "timing, MIC, and the model run behind every prediction.<br><b>Field crew and shotfirer"
     "</b> — as-drilled and as-charged actuals, deviations, photographs.<br><b>Geology and "
     "geotech</b> — domains, rock mass and grade attributes.",
     "#E0F7F9", "#B0EDF3", "#1A7C87"),
    ("CONSUMER STEWARDSHIP",
     "The functions that use the data validate fitness for purpose and must raise quality "
     "issues rather than work around them.<br><b>Shotfirer</b> — is this design fireable as "
     "drilled?<br><b>Grade control</b> — are post-blast polygons trustworthy enough to dig "
     "to?<br><b>Processing</b> — does predicted fragmentation match what the crusher saw?"
     "<br><b>HSE and Environment</b> — is the receiver register current and complete?"
     "<br><b>Finance</b> — does consumption reconcile to cost?",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("ENTERPRISE STEWARDSHIP",
     "Corporate governance holds cross-domain consistency, regulatory compliance and lineage."
     "<br><b>Owns:</b> the approved explosives catalogue as reference data; the blast "
     "identifier and conformed keys (site, pit, bench, domain, product) that make any two "
     "sites comparable; the retention matrix; model version and calibration policy; the "
     "definition of every reported KPI.<br><b>Assumption to confirm:</b> this sits with "
     "Corporate Architecture, with Group Safety for explosives reference data.",
     "#F4D9DD", "#E8A5AD", "#8B2E45"),
    ("OWNERSHIP STILL UNRESOLVED",
     "<b>Two candidate systems of record for as-fired QA/QC</b> — JKBMS and Blastatistics "
     "hold overlapping records and exchange by CSV/plugin. One must be nominated; the other "
     "becomes a consumer.<br><b>Third-party held data</b> — drill contractor MWD, explosives "
     "supplier delivery and magazine records, detonator OEM firing logs, and monitoring "
     "provider results. Access, format and retention are contract terms, not architecture."
     "<br><b>Vendor-hosted platform</b> — who owns the data, and how is it exported on exit?",
     "#F1EDE7", "#D9CDB8", "#6B5435"),
]
SG = grid(4, 8)
for (x, w), (t, d, fill, line, ink) in zip(SG, STEW):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, YE + 26, w, 90)
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % ink, x, YE + 26, w, 3)
    add("<b><font style=\"font-size:8px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:6.4px\" color=\"#000000\">%s</font>" % (ink, t, d),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, YE + 31, w - 14, 84)

# ================================================================ Band F — regulatory mapping
YF = YE + 122
band(YF, 22, "REGULATORY DATA MAPPING &amp; RETENTION&#160;&#160;·&#160;&#160;WHICH DATA "
     "SUPPORTS WHICH OBLIGATION, IN WHICH JURISDICTION",
     "Framework Challenge C — retention periods below are indicative and must be confirmed "
     "with Legal and Regulatory")
REG = [
    ("WHS (MINES) — WA",
     "<b>Data:</b> approved design, charge and tie-up sheets, as-fired record, shotfirer "
     "competency and authorisation, misfire and flyrock records, exclusion zone clearance."
     "<br><b>Store:</b> JKBMS + Blastatistics.<br><b>Retention:</b> confirm — safety records "
     "typically outlive the blast by years."),
    ("DANGEROUS GOODS (EXPLOSIVES) — WA",
     "<b>Data:</b> product and accessory specifications, quantity issued, used and returned "
     "per blast, magazine and transport records, reconciliation of every detonator."
     "<br><b>Store:</b> StockView (specifications) + JKBMS; issue/return sits with the "
     "supplier.<br><b>Retention:</b> confirm; reconciliation must be complete, not sampled."),
    ("ENVIRONMENTAL LICENCE — DWER / EPA",
     "<b>Data:</b> predicted and measured PPV and airblast at each nominated receiver, "
     "exceedance and complaint register, dust and fume events, monitor calibration records."
     "<br><b>Store:</b> TimeHEx (predicted) + JKBMS (measured).<br><b>Retention:</b> for the "
     "life of the licence and any condition period beyond it."),
    ("MULTI-JURISDICTION &amp; CONTRACT SITES",
     "Mining Services works on client sites and potentially across state lines. Conflicting "
     "obligations are the norm — the framework's own example is 10-year versus 25-year "
     "retention.<br><b>Rule to adopt:</b> hold to the longest applicable period, and record "
     "which jurisdiction and which client contract each blast record answers to."),
    ("RESIDENCY, PRIVACY &amp; VENDOR HOSTING",
     "Field capture carries personal data — crew names, licence numbers, positions and "
     "timestamps (Privacy Act 1988 obligations). Blastatistics is a vendor-hosted platform "
     "outside MinRes infrastructure.<br><b>Open:</b> hosting location, cross-border transfer, "
     "access logging, and a contractual export and deletion right on exit."),
]
for (x, w), (t, d) in zip(grid(5, 8), REG):
    box(head_desc(t, d, "#6B5435", tsize=7.6, dsize=6.4), x, YF + 26, w, 74,
        "#F1EDE7", "#D9CDB8", INK, fs=7)

# ================================================================ Band G — data quality
YG = YF + 106
band(YG, 22, "DATA QUALITY &amp; OBSERVABILITY&#160;&#160;·&#160;&#160;TREATED AS AN "
     "OPERATIONAL CAPABILITY, NOT A REPORTING AFTERTHOUGHT",
     "All five framework dimensions monitored, with an alert before the decision is made")
QUAL = [
    ("COMPLETENESS",
     "Every hole has an as-drilled record and every fired blast has a QA/QC record before the "
     "blast report closes. Monitor: % holes captured, mandatory fields empty, photographs "
     "missing, blasts with no measured outcome."),
    ("ACCURACY",
     "As-drilled collar within tolerance of design or explained; import unit and coordinate "
     "checks (Design Importer validation); monitor and instrument calibration currency. "
     "Distinguish a real deviation from a faulty sensor or a bad transform."),
    ("TIMELINESS",
     "Blast to report same day, as the field capture design intends. Monitor: sync latency "
     "from capture to platform, age of the oldest unsynced record, and explosives catalogue "
     "currency against supplier updates."),
    ("CONSISTENCY",
     "The same blast must agree wherever it is held — JKBMS versus Blastatistics, design mass "
     "versus consumption, predicted versus measured. One definition of powder factor, MIC and "
     "design compliance across every site."),
    ("TRACEABILITY",
     "Unbroken chain per blast: imported source file &#8594; approved design version &#8594; "
     "charge and tie-up issued &#8594; as-fired actuals &#8594; measured outcome &#8594; "
     "model and version, inputs and the engineer decision. This is what a regulator asks for."),
]
for (x, w), (t, d) in zip(grid(5, 8), QUAL):
    box(head_desc(t, d, "#5E623C", tsize=7.6, dsize=6.4), x, YG + 26, w, 58,
        "#F0F2E5", "#D9DCBC", INK, fs=7)

# ================================================================ footer
YH = YG + 90
FH = 150
FG = grid(2, 8)
LX, LW = FG[0]
RX, RW = FG[1]

add("", "rounded=0;html=1;fillColor=#FFFFFF;strokeColor=#B8DDE3;", LX, YH, LW, FH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % TEAL, LX, YH, 5, FH)
add("TRACEABILITY&#160;&#160;·&#160;&#160;IN THE FORM THE FRAMEWORK REQUIRES",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, TEAL), LX + 14, YH + 7, LW - 28, 12)
add("<b><font color=\"#2D686F\">SUPPORTS BUSINESS CAPABILITY</font></b> — EMMM "
    "<b>Exploit: design, fire and reconcile a surface blast</b>, with interfaces into "
    "<b>Establish</b> (vibration and airblast limits for permitting), <b>Beneficiate</b> "
    "(fragmentation to crusher and mill) and <b>Support</b> (HSE, QA/QC evidence, statutory "
    "retention) — "
    "<b>at corporate, hub and site level</b>. Corporate holds reference data, conformed keys, "
    "retention and KPI definitions; hub holds comparison and benchmarking; site holds the "
    "live design and record.<br>"
    "<b><font color=\"#8E5239\">ADDRESSES MINING DATA CHALLENGES</font></b> — "
    "<b>remote connectivity</b> (edge capture, hot/warm/cold layering, asynchronous sync, "
    "conflict rule); <b>siloed operations</b> (three-tier stewardship, and the unresolved dual "
    "system of record); <b>regulatory complexity</b> (obligation-to-data mapping, longest "
    "applicable retention, per-jurisdiction tagging).<br>"
    "<b><font color=\"#5E623C\">DATA QUALITY MONITORING INCLUDES</font></b> — completeness, "
    "accuracy, timeliness, consistency and traceability, each with a named metric above.<br>"
    "<b><font color=\"#8B2E45\">SAFETY CONSTRAINT CARRIED DOWN FROM TIER 1</font></b> — "
    "FragmentO, JKVBOC and scaled-distance vibration output are <b>model results, not "
    "measurements</b>. They are stored as predictions, tagged with model version, calibration "
    "set and inputs, never written into an as-fired field, and never drive an OT action. "
    "Fallback when a model is unavailable or out of calibration: site empirical charts and "
    "conservative MIC limits.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.8;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, LX + 14, YH + 22, LW - 28, FH - 28)

add("", "rounded=0;html=1;fillColor=#F1EDE7;strokeColor=#D9CDB8;", RX, YH, RW, FH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % RED, RX, YH, 5, FH)
add("GAPS, ASSUMPTIONS &amp; NEXT STEPS",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, RED), RX + 14, YH + 7, RW - 28, 12)
add("<b><font color=\"#CE372F\">SCOPE — SURFACE ONLY.</font></b> Underground and tunnel "
    "blasting are <b>out of scope by decision</b>, closing the open question the "
    "Business Architecture page carried. Excluded with them: 2DRing, 2DFace and every underground "
    "data entity — ring and face geometry, stope and drive outlines. If underground returns, "
    "only stage 1 needs re-scoping; the rest of this architecture holds either way.<br>"
    "<b>Structural gaps in the data architecture as it stands:</b> "
    "(1) <b>no single system of record for as-fired QA/QC</b> — JKBMS and Blastatistics "
    "overlap and exchange by CSV; nominate one before either is rolled out further. "
    "(2) <b>Explosives reference data is mastered per install</b> in a local StockView "
    "database, so the \"approved catalogue\" can diverge site by site — it needs a corporate "
    "master with controlled distribution. "
    "(3) <b>No conformed blast identifier or shared dimensions</b> across sites, so cross-site "
    "benchmarking inherits whatever conventions each site typed in. "
    "(4) <b>Actuals arrive by hand</b> — no interface to drill/MWD, vibration monitors, plant "
    "historian or cost systems, undercutting the same-day feedback loop. "
    "(5) <b>Measured environmental data has no native home</b> — it is re-keyed from monitor "
    "reports. "
    "(6) <b>Model metadata is a requirement, not a feature</b> — confirm the suite can store "
    "model version, calibration set and inputs against a prediction; if not, that is a "
    "Tier 2B/3 requirement.<br>"
    "<b>Assumptions to confirm:</b> MS Access is the JKSimBlast v2 backend (v3 is stated to "
    "change database systems — confirm before any build). Retention periods, jurisdictions and "
    "the personal-data position are analyst interpretation, not legal advice. Volumes, "
    "concurrency and connectivity windows per site are unmeasured.<br>"
    "<b>Deliberately out of scope:</b> Tier 2B Application Architecture (module-level "
    "integration, IT/OT interface design) and Tier 3 Technology Architecture (database "
    "platform, edge devices, hosting, licensing, backup).<br>"
    "<b>Next steps:</b> nominate the system of record; define the blast key and conformed "
    "dimensions; build the obligation-to-data retention matrix with Legal; profile one site's "
    "existing blast data against the five quality dimensions to get a real baseline; then "
    "take Tier 2B.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.5;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, RX + 14, YH + 22, RW - 28, FH - 28)

BOTTOM = YH + FH
add("Mineral Resources Limited&#160;&#160;·&#160;&#160;Data Architecture, one-page view"
    "&#160;&#160;·&#160;&#160;A3 landscape&#160;&#160;·&#160;&#160;Companion to "
    "MinRes_Blasting_Software_Business_Architecture (TOGAF BDAT Tier 1)",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;fontColor=#888888;align=left;"
    "verticalAlign=middle;" % CG, X0, BOTTOM + 6, W, 12)

# ================================================================ assemble
PW, PH = 1587, 1123
XML = (
    '<mxfile host="app.diagrams.net" agent="Claude Code" version="24.0.0" type="device">\n'
    '  <diagram name="Data Architecture - Blasting Software" id="minres-blast-dataarch">\n'
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
                        "MinRes_Blasting_Software_Data_Architecture.drawio")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(XML)
    print("wrote %s" % dest)
    print("content bottom = %spx of %s ; %d cells" % (BOTTOM + 18, PH, _id[0] - 1))
