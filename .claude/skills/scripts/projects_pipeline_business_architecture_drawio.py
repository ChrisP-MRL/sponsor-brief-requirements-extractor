# -*- coding: utf-8 -*-
"""Build the one-page Business Architecture diagram for the short-term projects pipeline.

Scope: TOGAF BDAT Tier 1 (Business Architecture) only, mining-adapted. This page answers
"which business capabilities is the short-term pipeline actually investing in, and where
is it silent" — it is a coverage and gap view, not an investment case and not a schedule.

Source of content: input/Projects Pipeline - Short Term.csv

ACTIVE PIPELINE ONLY. Stage = Complete or Cancelled is excluded at read time, so the page
shows live demand: Opportunity, In Progress and On Hold. Every remaining project appears
by name — nothing is silently aggregated away.

Framework applied: .claude/rules/TOGAF_BDAT_MINING_ADAPTED_Enterprise_Architecture_Framework.html
  - EMMM Business Capability Reference Map as the capability spine (Discover, Establish,
    Exploit, Beneficiate, Sell, Support), tailored to the MinRes portfolio
  - Plus an explicit ENABLING IT/OT PLATFORM layer beneath the spine. Half the active
    pipeline is network, compute, cyber and workplace work that enables every capability
    and belongs to none. Forcing it into "Support" would hide the portfolio's real shape.
  - Principle 1 bidirectional strategy flow: corporate drivers down, site constraints up
  - Principle 2 co-equal IT/OT: capability columns and platform groups tagged IT, OT or
    convergence
  - Principle 3 safety first: OT control-system and safety-system work held to its own
    governance gate
  - Federated governance: corporate / hub / site authority plus the escalation path
  - Application portfolio classification: Strategic / Operational / Tactical

Brand rules from .claude/rules/MINRES_Content_Guidelines.html: Century Gothic throughout;
MinRes Red #CE372F for title and accents; Dark Teal #00444C for band headers; Teal family
for In Progress, Brown family for Opportunity, Coral/Peach family for On Hold.

Data-quality note carried onto the page: in the CSV the High-Level Summary column is
offset against Title for a block of rows (e.g. "Vulnerability Management" is described as
a radio frequency management framework; "Spectrum Management Database" as fire detection).
Classification here is therefore driven by Title, never by that summary text.

Page is A2 landscape (2245 x 1587 px at 96dpi) with 24px margins.
"""
import csv
import os
from xml.sax.saxutils import escape

CG = "Century Gothic"
cells = []
_id = [1]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CSV_PATH = os.path.join(ROOT, "input", "Projects Pipeline - Short Term.csv")

ACTIVE_STAGES = ("Opportunity", "In Progress", "On Hold")
DEAD_STAGES = ("Complete", "Cancelled")


def add(value, style, x, y, w, h, parent="1"):
    _id[0] += 1
    cells.append(
        '        <mxCell id="n%d" value="%s" style="%s" vertex="1" parent="%s">\n'
        '          <mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry" />\n'
        '        </mxCell>\n'
        % (_id[0], escape(value, {'"': '&quot;'}), escape(style, {'"': '&quot;'}),
           parent, x, y, w, h))


def h(s):
    """HTML-escape CSV data before it is embedded as draw.io rich text."""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- page grid
X0, RIGHT = 24, 2221
W = RIGHT - X0            # 2197


def grid(n, gap=8, x=X0, width=W):
    """n equal columns spanning width, separated by gap."""
    cw = (width - gap * (n - 1)) / float(n)
    return [(x + i * (cw + gap), cw) for i in range(n)]


# ---------------------------------------------------------------- flow arrow geometry
# The Principle 1 up/down flow arrows sit on a 5-column grid. Their captions must live in
# the gap between the last two arrows: a right-aligned caption spanning to the page margin
# runs straight through the fifth arrow.
ARROW_W, ARROW_H = 52, 20
FLOW_COLS = grid(5, 10)


def arrow_x(i):
    x, w = FLOW_COLS[i]
    return x + w / 2.0 - ARROW_W / 2.0


CAP_X = arrow_x(3) + ARROW_W + 6
CAP_W = arrow_x(4) - CAP_X - 6


# ---------------------------------------------------------------- palette
RED = "#CE372F"
TEAL = "#00444C"
INK = "#000000"
GREY = "#5C5C5C"

# Stage families — one visual language for the whole page.
STAGE = {
    "In Progress": {"fill": "#E0F7F9", "line": "#B0EDF3", "ink": "#1A7C87", "bar": "#2AB8C9"},
    "Opportunity": {"fill": "#F1EDE7", "line": "#D9CDB8", "ink": "#6B5435", "bar": "#A58D62"},
    "On Hold":     {"fill": "#F5E5DD", "line": "#E8C4B0", "ink": "#8E5239", "bar": "#C37556"},
}

# Domain families — Principle 2, co-equal IT and OT.
DOMAIN = {
    "IT": {"fill": "#E0F7F9", "line": "#B0EDF3", "ink": "#1A7C87", "bar": "#2AB8C9"},
    "OT": {"fill": "#F5E5DD", "line": "#E8C4B0", "ink": "#8E5239", "bar": "#C37556"},
    "CV": {"fill": "#F4D9DD", "line": "#E8A5AD", "ink": "#8B2E45", "bar": "#C5556B"},
}

BAND_HEAD = ("rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;fontFamily=%s;"
             "fontSize=9.5;fontStyle=1;fontColor=#FFFFFF;align=left;verticalAlign=middle;"
             "spacingLeft=10;" % (TEAL, CG))


def band(y, hh, label, note=""):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % RED, X0, y, 5, hh)
    txt = label
    if note:
        txt += ("&#160;&#160;&#160;<font color=\"#B0EDF3\" style=\"font-size:8px\">%s</font>"
                % note)
    add(txt, BAND_HEAD, X0 + 5, y, W - 5, hh)


def box(text, x, y, w, hh, fill, line, ink, fs=8, valign="top", pad=7):
    add(text,
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=%s;"
        "fontSize=%s;fontColor=%s;align=left;verticalAlign=%s;spacingLeft=%s;spacingRight=%s;"
        "spacingTop=4;" % (fill, line, CG, fs, ink, valign, pad, pad - 1),
        x, y, w, hh)


def head_desc(title, desc, tcol, tsize=9, dsize=7.5):
    return ("<b><font style=\"font-size:%spx\" color=\"%s\">%s</font></b><br>"
            "<font style=\"font-size:%spx\" color=\"#000000\">%s</font>"
            % (tsize, tcol, title, dsize, desc))


# ================================================================ read the pipeline
LABOUR = ["PM", "BA", "IE", "CD", "SA", "Other"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def short_date(raw):
    """'1/08/2026' -> 'Aug 26'. Blank or unparseable -> ''."""
    parts = raw.strip().split("/")
    if len(parts) != 3:
        return ""
    try:
        month, year = int(parts[1]), int(parts[2])
    except ValueError:
        return ""
    if not 1 <= month <= 12:
        return ""
    return "%s %02d" % (MONTHS[month - 1], year % 100)


def read_pipeline(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out, dropped, dead = {}, 0, {}
    for r in rows:
        stage = (r.get("Stage") or "").strip()
        if stage in DEAD_STAGES:
            dropped += 1
            dead[(r.get("Title") or "").strip()] = stage
            continue
        if stage not in ACTIVE_STAGES:
            continue
        days = 0.0
        for c in LABOUR:
            v = (r.get("%s - Est Project Labour Days" % c) or "").strip()
            if v:
                try:
                    days += float(v)
                except ValueError:
                    pass
        title = (r.get("Title") or "").strip()
        out[title] = {
            "title": title,
            "stage": stage,
            "sponsor": (r.get("Sponsor") or "").strip(),
            "author": (r.get("Author") or "").strip(),
            "budget": (r.get("Budget") or "").strip() == "Yes",
            "start": short_date(r.get("Start Date - Est Project") or ""),
            "months": (r.get("Duration - Est Project (months)") or "").strip(),
            "days": days,
            "labour": {c: (r.get("%s - Est Project Labour Days" % c) or "").strip()
                       for c in LABOUR},
        }
    return out, dropped, dead


PIPE, DROPPED, DEAD = read_pipeline(CSV_PATH)

# ================================================================ capability classification
# Analyst judgement, by Title only. Each active project appears exactly once.
CAPS = [
    ("DISCOVER", "Exploration &amp; ore body knowledge", "IT",
     "Only one active initiative touches ore body knowledge, and it is On Hold. "
     "The related visualisation initiative was cancelled.",
     ["Voxel Farm: Phase 2"]),
    ("ESTABLISH", "Mine development &amp; site establishment", "CV",
     "Growth work: Mt Marion underground and floatation, Onslow accommodation, Winu. "
     "Driven by capital schedules, not by IT.",
     ["Winu EPC FID",
      "Mt Marion Underground - Infrastructure",
      "Mt Marion Floatation Plant - Infrastructure",
      "Mt Marion Village Expansion (perm)",
      "Lot 300"]),
    ("EXPLOIT", "Production operations", "CV",
     "Mining execution and production visibility. Thin for the capability that earns the "
     "revenue: two of the four are unfunded, and the Ampla, operational reporting and Bald "
     "Hill roadmap work was cancelled.",
     ["Remote Monitoring Centre",
      "Mt Marion Underground - Mining Systems",
      "AHS Vehicle Data",
      "Lamb Creek - Ampla",
      "Operational Reporting Improvement (POC)",
      "Bald Hill Operational Apps - Roadmap",
      "Kens Bore - Ground Probing Radar"]),
    ("BENEFICIATE", "Mineral processing", "OT",
     "Plant control and plant visibility — the largest OT concentration in the capability "
     "spine, and safety-critical. Three of the five are On Hold; metallurgical accounting "
     "and assay (CCLAS) were cancelled.",
     ["Mt Marion Floatation Plant - Control System",
      "Mt Marion Floatation Plant - Business Systems",
      "Mt Marion Metallurgical Accounting",
      "Control Systems Uplift - West Angeles and Granites",
      "Control Systems Uplift - Granites",
      "SCADA Visualisation @ 20 Walters Drive",
      "Plant Cameras Viewable at HQ",
      "IV CCLAS"]),
    ("SELL", "Market, logistics &amp; customer", "IT",
     "No active initiative. The Phase 2 demand chain scheduling work was cancelled, so "
     "product movement to port and customer is now wholly unrepresented.",
     ["Demand Chain Scheduling System - Phase 2"]),
    ("SUPPORT", "HSE, workforce, security &amp; corporate", "IT",
     "The broadest capability by count: site security and access, village services, "
     "worker health and PPE, and PMO method.",
     ["Access Control - Onslow In-land",
      "Mobile Phone FOBs - Access Control",
      "Camp CCTV Tech Standards",
      "Camp CCTV Upgrade",
      "Central CCTV viewing - Onslow",
      "Catering System Selection",
      "Mine Site Clinic Digital Intake & Calendar Application",
      "PPE Express - Sponsor Brief (Define Phase)",
      "MtM Tool Tracker",
      "Project Management Methodology Refresh"]),
]

# ---------------------------------------------------------------- enabling platform layer
PLATFORM = [
    ("OT CYBER &amp; SITE HARDENING", "OT",
     "Safety-critical. Five of seven On Hold.",
     ["OT Cyber Initiatives – Tranche 3",
      "OT Cyber - Tranche 3",
      "OT Cyber for Energy Assets",
      "Mt Marion OT Cyber - Phase 3",
      "OT Cyber - Rod Ore",
      "Mt Marion Firewall Refresh",
      "Site Firewall EOL Refresh"]),
    ("IT SECURITY &amp; IDENTITY", "IT",
     "All four are Opportunity — none started.",
     ["Identity And Access Management – Tranche 2",
      "Zero Trust Network Architecture",
      "Vulnerability Management",
      "Firewall Rule Optimisation"]),
    ("NETWORK, RADIO &amp; SPECTRUM", "CV",
     "Site connectivity and licensed spectrum.",
     ["Mt Marion Fibre Upgrade",
      "Mt Marion DMR Tower Relocation",
      "Site WAN Optimisation",
      "Spectrum Management Database",
      "Resilient IT Infrastructure Installation",
      "IPAM"]),
    ("COMPUTE, STORAGE &amp; CLOUD", "IT",
     "VMware exit is the forcing event.",
     ["VMWare Replacement",
      "VMWare 9.0 Upgrade",
      "Data Centre Storage Refresh",
      "Cross Data Centre Resiliency - Switching",
      "Extend OT Compute to Cloud",
      "CSI File Server Consolidation",
      "Crushing File storage standardisation"]),
    ("RESILIENCE, INTEGRATION &amp; ITSM", "IT",
     "Recovery, integration and IT operations.",
     ["Onslow IT Disaster Recovery Improvement",
      "IT Infrastructure End of Life Replacement - Distribution Centre",
      "Design & Harden Enterprise Application Integration",
      "Deploy ITOM"]),
    ("WORKPLACE &amp; COMMS FACILITIES", "CV",
     "Offices, meeting rooms, comms room protection.",
     ["Meeting Room AV Study",
      "20WD Meeting Room Refresh Phase 1",
      "18 Hasler Meeting Room Upgrade",
      "18 Hasler Training Room Uplift",
      "Onslow Comms Rooms Fire Detection and Suppression",
      "Onslow Fire Detection and Suppression"]),
]

# ---------------------------------------------------------------- resolve & validate
_seen = set()
RETIRED = []


def resolve(names, where):
    """Map classification titles onto CSV records; report anything that does not match.

    A classified title that has since moved to Complete or Cancelled is expected, not an
    error — the CSV is refreshed between runs and the page tracks the live pipeline. It is
    reported separately from a title that no longer appears in the source file at all,
    which is a real classification defect.
    """
    got = []
    for n in names:
        key = n.strip()
        rec = PIPE.get(key)
        if rec is None:
            # tolerate the stray leading/trailing spaces present in the source file
            match = [t for t in PIPE if t.strip() == key]
            rec = PIPE[match[0]] if match else None
        if rec is None:
            stage = DEAD.get(key) or next(
                (s for t, s in DEAD.items() if t.strip() == key), None)
            if stage:
                RETIRED.append((key, stage, where))
            else:
                print("  !! not in the CSV at all: %r (%s) — stale classification"
                      % (key, where))
            continue
        if rec["title"] in _seen:
            print("  !! classified twice: %r (%s)" % (rec["title"], where))
        _seen.add(rec["title"])
        got.append(rec)
    return got


CAP_ROWS = [(c[0], c[1], c[2], c[3], resolve(c[4], c[0])) for c in CAPS]
PLAT_ROWS = [(p[0], p[1], p[2], resolve(p[3], p[0])) for p in PLATFORM]

UNCLASSIFIED = sorted(t for t in PIPE if t not in _seen)
for t in UNCLASSIFIED:
    print("  !! active project not placed on the page: %r" % t)

# ---------------------------------------------------------------- portfolio counters
ALL = list(PIPE.values())
N = len(ALL)
BY_STAGE = dict((s, sum(1 for r in ALL if r["stage"] == s)) for s in ACTIVE_STAGES)
N_FUNDED = sum(1 for r in ALL if r["budget"])
NO_SPONSOR = [r for r in ALL if not r["sponsor"]]
NO_AUTHOR = [r for r in ALL if not r["author"]]
NO_START = [r for r in ALL if not r["start"]]
NO_EST = [r for r in ALL if r["days"] == 0]
DAYS = dict((c, sum(float(r["labour"][c]) for r in ALL if r["labour"][c]))
            for c in LABOUR)
TOTAL_DAYS = sum(DAYS.values())
def top_of(field):
    tally = {}
    for r in ALL:
        if r[field]:
            tally[r[field]] = tally.get(r[field], 0) + 1
    return sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))[0]


TOP_SPONSOR = top_of("sponsor")
TOP_AUTHOR = top_of("author")


def stage_counts(recs):
    return dict((s, sum(1 for r in recs if r["stage"] == s)) for s in ACTIVE_STAGES)


# ================================================================ header
add("", "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;" % RED, X0, 24, 8, 62)
add("Demand Profile: Short-Term Projects Pipeline",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=20;fontStyle=1;fontColor=%s;"
    "align=left;verticalAlign=top;" % (CG, RED), 44, 21, 1100, 28)
add("<b>Mineral Resources Limited</b>&#160;&#160;·&#160;&#160;<b>%d active initiatives</b> — "
    "Opportunity %d&#160;·&#160;In Progress %d&#160;·&#160;On Hold %d&#160;&#160;·&#160;&#160;"
    "<b><font color=\"#CE372F\">ACTIVE ONLY — %d Complete and Cancelled projects excluded"
    "</font></b><br>TOGAF BDAT <b>Tier 1 — Business Architecture</b>, mining-adapted. "
    "Capability spine is the Open Group <b>EMMM</b> Business Capability Reference Map, with an "
    "explicit <b>Enabling IT/OT Platform</b> layer for the cross-cutting work that serves every "
    "capability and belongs to none. Purpose: <b>capability coverage and gap analysis</b> — "
    "not an investment case and not a schedule."
    % (N, BY_STAGE["Opportunity"], BY_STAGE["In Progress"], BY_STAGE["On Hold"], DROPPED),
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8.5;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, 44, 50, 1390, 44)   # stops clear of the marker legend at x1442
add("Prepared for: <b>Portfolio &amp; Architecture Governance</b><br>"
    "Source: input/Projects Pipeline - Short Term.csv (generated, not hand-drawn)<br>"
    "Rule: TOGAF BDAT Mining-Adapted EA Framework v2.0<br>"
    "12 August 2026&#160;&#160;·&#160;&#160;<b>Draft — capability mapping is analyst "
    "interpretation, not sponsor-confirmed</b>",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7.5;fontColor=%s;align=right;"
    "verticalAlign=top;" % (CG, GREY), 1600, 22, 621, 58)   # ends above the marker legend

# legend
LEG = ("rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=" + CG +
       ";fontSize=7;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;")
LEG_W, LEG_PITCH = 144, 148
LEG_X0 = RIGHT - 4 - LEG_W - 2 * LEG_PITCH    # right-aligned, 4px inside the page margin
for i, s in enumerate(["In Progress", "Opportunity", "On Hold"]):
    d = STAGE[s]
    add("%s (%d)" % (s, BY_STAGE[s]), LEG % (d["fill"], d["line"], d["ink"]),
        LEG_X0 + i * LEG_PITCH, 70, LEG_W, 14)
add("Chip second line — <b>sponsor</b> at left, <b>author</b> at right:&#160;&#160;"
    "<b>$</b> budget approved&#160;·&#160;<b>&#8211;</b> not funded&#160;·&#160;"
    "<i>Aug 26</i> estimated start&#160;·&#160;<b><font color=\"#CE372F\">no sponsor</font></b> "
    "/ <b><font color=\"#CE372F\">no author</font></b> = field blank in the source",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.8;fontColor=%s;align=right;"
    "verticalAlign=top;" % (CG, GREY), RIGHT - 8 - 771, 81, 771, 11)

# ================================================================ Band A — corporate drivers
YA = 96
band(YA, 22, "CORPORATE STRATEGY &amp; BUSINESS DRIVERS&#160;&#160;·&#160;&#160;CORPORATE LEVEL",
     "Principle 1 — corporate strategy flows DOWN and should determine what the pipeline "
     "contains")
DRIVERS = [
    ("Volume growth &amp; new capacity",
     "Onslow Iron ramp-up, Mt Marion underground and floatation, Winu. Growth capital sets "
     "immovable dates that the pipeline must serve, not negotiate."),
    ("Cost per tonne",
     "Lowest-quartile $/t. Every initiative competes with the alternative of not doing it; "
     "unfunded pipeline items are not cost-free — they consume scarce PM, BA and IE capacity."),
    ("Safety &amp; licence to operate",
     "Zero harm. OT control systems, plant SCADA, access control and worker health carry "
     "obligations that do not pause when a project goes On Hold."),
    ("Cyber resilience &amp; asset protection",
     "IT and OT exposure across remote sites, energy assets and plants. The largest single "
     "cluster of active demand and the most stalled."),
    ("Standardised operating platform",
     "One network, compute, identity and reporting standard across iron ore, lithium and "
     "energy assets, so capability is portable between sites and crews."),
]
for (x, w), (t, d) in zip(grid(5, 10), DRIVERS):
    box(head_desc(t, d, TEAL), x, YA + 26, w, 62, "#E3F2F4", "#B8DDE3", INK)

YD = YA + 92
for i in range(len(FLOW_COLS)):
    add("", "shape=singleArrow;html=1;direction=south;dy=0.55;dx=9;fillColor=#2D686F;"
        "strokeColor=none;", arrow_x(i), YD, ARROW_W, ARROW_H)
add("Corporate strategy, standards and targets flow DOWN &#8595;",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=2;fontColor=#2D686F;"
    "align=center;verticalAlign=middle;" % CG, CAP_X, YD + 2, CAP_W, 16)

# ================================================================ Band B — capability coverage
YB = YD + 26
band(YB, 22, "EMMM BUSINESS CAPABILITY COVERAGE&#160;&#160;·&#160;&#160;WHERE THE ACTIVE "
     "PIPELINE IS INVESTING, AND WHERE IT IS SILENT",
     "Tailored to the MinRes portfolio — count, stage split and the coverage verdict per "
     "capability")
CB_Y, CB_H = YB + 26, 62
for (x, w), (cap, cover, dom, verdict, recs) in zip(grid(6), CAP_ROWS):
    d = DOMAIN[dom]
    sc = stage_counts(recs)
    n = len(recs)
    thin = n <= 1
    line = RED if thin else d["line"]
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;strokeWidth=%s;"
        % (d["fill"], line, 2 if thin else 1), x, CB_Y, w, CB_H)
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % d["bar"], x, CB_Y, w, 3)
    add("<b><font style=\"font-size:11px\" color=\"%s\">%s</font></b>&#160;&#160;"
        "<b><font style=\"font-size:11px\" color=\"%s\">%d</font></b>"
        "<font style=\"font-size:6.5px\" color=\"#5C5C5C\"> active</font>"
        "&#160;&#160;<font style=\"font-size:6.5px\" color=\"%s\"><b>%s</b></font><br>"
        "<font style=\"font-size:7px\" color=\"#5C5C5C\">%s&#160;&#160;·&#160;&#160;"
        "In Progress %d · Opportunity %d · On Hold %d</font><br>"
        "<font style=\"font-size:7px\" color=\"#000000\">%s</font>"
        % (TEAL, cap, RED if thin else d["ink"], n, d["ink"], dom,
           cover, sc["In Progress"], sc["Opportunity"], sc["On Hold"], verdict),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 8, CB_Y + 5, w - 16, CB_H - 8)

# ================================================================ Band C — the projects
CHIP_H, CHIP_GAP = 32, 3
MAX_CAP = max(len(r[4]) for r in CAP_ROWS)
# This band holds only the capability-mapped work. The remaining initiatives are named in
# the Enabling IT/OT Platform band below, so the header must not claim the portfolio total.
N_CAP = sum(len(r[4]) for r in CAP_ROWS)

YC = CB_Y + CB_H + 6
band(YC, 22, "ACTIVE INITIATIVES BY BUSINESS CAPABILITY&#160;&#160;·&#160;&#160;%d OF %d "
     "ACTIVE INITIATIVES (%d%%)&#160;&#160;·&#160;&#160;THE OTHER %d ARE NAMED IN THE "
     "ENABLING PLATFORM LAYER BELOW" % (N_CAP, N, round(100.0 * N_CAP / N), N - N_CAP),
     "Every one named, none aggregated away. Colour = stage; every chip carries its sponsor, "
     "funding state and estimated start exactly as the source records them")


def chip(rec, x, y, w):
    """One initiative. Second line: sponsor at the left, author at the right."""
    d = STAGE[rec["stage"]]
    meta = []
    if rec["sponsor"]:
        meta.append("<font color=\"#5C5C5C\">%s</font>" % h(rec["sponsor"]))
    else:
        meta.append("<b><font color=\"%s\">no sponsor</font></b>" % RED)
    meta.append("<b><font color=\"%s\">%s</font></b>"
                % (d["ink"], "$" if rec["budget"] else "&#8211;"))
    if rec["start"]:
        meta.append("<i><font color=\"#5C5C5C\">%s</font></i>" % rec["start"])
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % d["bar"], x, y, 3, CHIP_H)
    box("<b><font style=\"font-size:7.5px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:6.3px\">%s</font>"
        % (d["ink"], h(rec["title"]), "&#160;·&#160;".join(meta)),
        x + 3, y, w - 3, CHIP_H, d["fill"], d["line"], INK, fs=7, pad=6)
    if rec["author"]:
        auth = ("<font color=\"#9A9A9A\">auth&#160;</font><font color=\"%s\">%s</font>"
                % (d["ink"], h(rec["author"])))
    else:
        auth = ("<font color=\"#9A9A9A\">auth&#160;</font>"
                "<b><font color=\"%s\">no author</font></b>" % RED)
    add(auth,
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.3;align=right;"
        "verticalAlign=middle;" % CG, x + w - 156, y + 14, 150, 12)


for (x, w), (cap, cover, dom, verdict, recs) in zip(grid(6), CAP_ROWS):
    y = YC + 26
    for rec in recs:
        chip(rec, x, y, w)
        y += CHIP_H + CHIP_GAP
    if not recs:
        box("<i>No active initiative</i>", x, y, w, CHIP_H,
            "#EFEFEF", "#D4D4D4", GREY, fs=7)

# ================================================================ Band D — enabling platform
YE = YC + 26 + MAX_CAP * (CHIP_H + CHIP_GAP) + 4
MAX_PLAT = max(len(p[3]) for p in PLAT_ROWS)
N_PLAT = sum(len(p[3]) for p in PLAT_ROWS)
band(YE, 22, "ENABLING IT/OT PLATFORM LAYER&#160;&#160;·&#160;&#160;SERVES EVERY CAPABILITY, "
     "OWNED BY NONE&#160;&#160;·&#160;&#160;%d OF %d ACTIVE INITIATIVES (%d%%)"
     % (N_PLAT, N, round(100.0 * N_PLAT / N)),
     "Not an EMMM capability — added deliberately, because forcing this into Support would "
     "hide the real shape of the portfolio")
PH_Y = YE + 26
for (x, w), (grp, dom, note, recs) in zip(grid(6), PLAT_ROWS):
    d = DOMAIN[dom]
    sc = stage_counts(recs)
    add("<b><font color=\"#FFFFFF\">%s</font></b>&#160;&#160;"
        "<font style=\"font-size:6.5px\" color=\"#FFFFFF\">%d&#160;·&#160;%s&#160;·&#160;"
        "IP %d / Op %d / OH %d</font>"
        % (grp, len(recs), dom, sc["In Progress"], sc["Opportunity"], sc["On Hold"]),
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;fontFamily=%s;"
        "fontSize=7;align=left;verticalAlign=middle;spacingLeft=6;" % (d["bar"], CG),
        x, PH_Y, w, 18)
    y = PH_Y + 20
    for rec in recs:
        chip(rec, x, y, w)
        y += CHIP_H + CHIP_GAP
    add("<i>%s</i>" % note,
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.5;fontColor=%s;align=left;"
        "verticalAlign=top;" % (CG, d["ink"]), x + 4, y, w - 6, 12)

# --- upward flow arrows
YU = PH_Y + 20 + MAX_PLAT * (CHIP_H + CHIP_GAP) + 14
for i in range(len(FLOW_COLS)):
    add("", "shape=singleArrow;html=1;direction=north;dy=0.55;dx=9;fillColor=#A58D62;"
        "strokeColor=none;", arrow_x(i), YU, ARROW_W, ARROW_H)
add("&#8593; Site-level operational reality flows UP and constrains what the pipeline can "
    "actually deliver",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=2;fontColor=#6B5435;"
    "align=center;verticalAlign=middle;" % CG, CAP_X, YU + 2, CAP_W, 16)

# ================================================================ Band E — site realities
YS = YU + 26
band(YS, 22, "SITE-LEVEL OPERATIONAL REALITIES&#160;&#160;·&#160;&#160;SITE LEVEL",
     "Legitimate input to corporate strategy — neither level dominates")
SITE = [
    ("Growth schedules are not negotiable",
     "Mt Marion underground, the floatation plant and Onslow accommodation have construction "
     "dates. IT work that serves them inherits those dates and cannot be deferred by an IT "
     "prioritisation decision."),
    ("Delivery capacity is the real constraint",
     "%d estimated labour days sit on just %d of %d initiatives — IE %d, BA %d, PM %d, SA %d. "
     "The other %d are unestimated, so true demand is unknown and certainly larger."
     % (int(TOTAL_DAYS), N - len(NO_EST), N, int(DAYS["IE"]), int(DAYS["BA"]),
        int(DAYS["PM"]), int(DAYS["SA"]), len(NO_EST))),
    ("Remote sites and connectivity windows",
     "Onslow, Kens Bore, Mt Marion, Bald Hill and the energy assets. Network, radio and "
     "spectrum work gates almost everything else, so platform slippage propagates."),
    ("OT cannot be treated like IT",
     "Plant control systems and OT cyber sit behind production availability. Change windows "
     "are set by the plant, not by an IT release calendar."),
    ("On Hold is not free",
     "%d initiatives are On Hold. Risk, End-of-Life exposure and obligations continue to "
     "accrue while the work does not." % BY_STAGE["On Hold"]),
    ("Sponsor and author attention is concentrated",
     "%s sponsors %d of %d active initiatives and %s authored %d of them; %d have no sponsor and "
     "%d no author. Decision and analysis throughput, not appetite, becomes the bottleneck."
     % (h(TOP_SPONSOR[0]), TOP_SPONSOR[1], N, h(TOP_AUTHOR[0]), TOP_AUTHOR[1],
        len(NO_SPONSOR), len(NO_AUTHOR))),
]
for (x, w), (t, d) in zip(grid(6), SITE):
    box(head_desc(t, d, "#6B5435", tsize=8.5, dsize=7), x, YS + 26, w, 66,
        "#F1EDE7", "#D9CDB8", INK, fs=7)

# ================================================================ Band F — governance
YG = YS + 98
band(YG, 22, "FEDERATED GOVERNANCE&#160;&#160;·&#160;&#160;WHO DECIDES WHAT, AND THE "
     "ESCALATION PATH",
     "Governance is earned through demonstrated value to operations, not process rigour")
GOV = [
    ("CORPORATE — sets the standard and the envelope",
     "<b>Approves:</b> the enabling platform standards (network, compute, identity, cyber) · "
     "portfolio classification and sequencing · funding gates for the %d budget-approved "
     "initiatives · End-of-Life and cyber risk acceptance.<br>"
     "<b>Authority:</b> Corporate Architecture with IT/OT leadership and Group Risk.<br>"
     "<b>Owns the platform layer</b> — no site may solve a platform problem locally."
     % N_FUNDED,
     "#E0F7F9", "#B0EDF3", "#1A7C87"),
    ("HUB / REGIONAL — adapts within the standard",
     "<b>Approves:</b> which optional capability initiatives a hub runs · sequencing against "
     "the site's production and construction calendar · local acceptance of platform rollouts · "
     "hub-level benefit claims.<br>"
     "<b>Authority:</b> Hub Operations Manager with the Regional Asset owner.",
     "#E3F2F4", "#B8DDE3", "#2D686F"),
    ("SITE — executes and escalates",
     "<b>Decides:</b> change windows for plant and OT systems · day-to-day operational "
     "acceptance · whether a deployment is safe to proceed on shift.<br>"
     "<b>Escalates:</b> any initiative whose slip creates a safety, statutory or production "
     "exposure &#8594; Hub &#8594; Corporate, in the same reporting period.<br>"
     "<b>Authority:</b> Site Senior Executive.",
     "#F5E5DD", "#E8C4B0", "#8E5239"),
    ("STALLED &amp; UNGOVERNED DEMAND — special control",
     "<b>%d On Hold and %d unsponsored initiatives are the highest-risk item on this page.</b> "
     "An initiative with no sponsor has no one accountable for the benefit and no one to "
     "escalate to.<br>"
     "<b>Rule:</b> every active initiative carries a named sponsor or it leaves the pipeline. "
     "On Hold requires a stated reason, a review date and an explicit owner of the accruing "
     "risk.<br>"
     "<b>OT exception:</b> OT cyber and control-system work cannot be held on IT grounds alone "
     "— holding it is a safety and production risk decision, and must be taken as one."
     % (BY_STAGE["On Hold"], len(NO_SPONSOR)),
     "#F4D9DD", RED, "#8B2E45"),
]
GOVW = grid(4, 10)
GOV_H = 128
for (x, w), (t, d, fill, line, ink) in zip(GOVW, GOV):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (fill, line), x, YG + 26, w, GOV_H)
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % ink, x, YG + 26, w, 3)
    add("<b><font style=\"font-size:8.5px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:7px\" color=\"#000000\">%s</font>" % (ink, t, d),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 8, YG + 32, w - 16, GOV_H - 8)

# ================================================================ Band G — portfolio health
YM = YG + 26 + GOV_H + 8
band(YM, 22, "PORTFOLIO HEALTH MEASURES&#160;&#160;·&#160;&#160;ALL SIX MUST HOLD TOGETHER",
     "Success is not maximising throughput at the expense of coverage, governance or safety")
METRICS = [
    ("CAPABILITY COVERAGE",
     "No revenue-earning capability left with a single active initiative. Today Discover has "
     "one — On Hold — and Sell has none at all."),
    ("GOVERNANCE COMPLETENESS",
     "Every active initiative has a named sponsor, a stage reason and a review date. Today %d "
     "of %d have no sponsor." % (len(NO_SPONSOR), N)),
    ("ESTIMATE COMPLETENESS",
     "Every active initiative carries a labour estimate before it competes for capacity. Today "
     "%d of %d do not." % (len(NO_EST), N)),
    ("SCHEDULE INTEGRITY",
     "Every In Progress and funded initiative has an estimated start. Today %d of %d have no "
     "start date." % (len(NO_START), N)),
    ("STALL RATE",
     "On Hold trending down, with the accruing risk explicitly owned. Today %d of %d (%d%%) "
     "are On Hold." % (BY_STAGE["On Hold"], N, round(100.0 * BY_STAGE["On Hold"] / N))),
    ("SAFETY &amp; OBLIGATION EXPOSURE",
     "No safety, statutory or End-of-Life obligation sitting behind an On Hold or unsponsored "
     "initiative. OT cyber and plant control are the test cases."),
]
for (x, w), (t, d) in zip(grid(6), METRICS):
    box(head_desc(t, d, TEAL, tsize=8, dsize=7), x, YM + 26, w, 54,
        "#EFEFEF", "#D4D4D4", INK, fs=7)

# ================================================================ footer — traceability & gaps
YF = YM + 88
FH = 176
# Two equal halves. Both blocks carry a lot of text; a narrow right-hand column would
# overflow its box at this font size.
(_lx, LW), (RX, RW) = grid(2, 10)

add("", "rounded=0;html=1;fillColor=#FFFFFF;strokeColor=#B8DDE3;", X0, YF, LW, FH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % TEAL, X0, YF, 5, FH)
add("BIDIRECTIONAL TRACEABILITY&#160;&#160;·&#160;&#160;REQUIRED BY THE FRAMEWORK",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, TEAL), X0 + 14, YF + 8, LW - 28, 12)
add("<b><font color=\"#2D686F\">DOWNWARD</font></b> — corporate driver (volume growth · cost "
    "per tonne · safety and licence · cyber resilience · standardised platform) &#8594; EMMM "
    "business capability (<b>Establish</b> %d · <b>Exploit</b> %d · <b>Beneficiate</b> %d · "
    "<b>Support</b> %d · <b>Discover</b> %d · <b>Sell</b> %d) &#8594; the %d named active "
    "initiatives on this page &#8594; Tier 2 Data and Application and Tier 3 Technology "
    "architecture, <b>deliberately out of scope on this page</b>.<br>"
    "<b><font color=\"#6B5435\">UPWARD</font></b> — site constraints (immovable construction "
    "dates · plant change windows · remote connectivity · %d labour days of known demand "
    "against finite PM/BA/IE/SA capacity · concentrated sponsor attention) &#8594; therefore the "
    "enabling platform layer must be sequenced <b>ahead of</b> the capability initiatives that "
    "depend on it, and OT work must be scheduled to the plant's calendar, not IT's.<br>"
    "<b><font color=\"#8B2E45\">PORTFOLIO CLASSIFICATION</font></b> — <b>Strategic</b> (formal "
    "architecture review, coordinated enterprise rollout): the platform layer — VMware "
    "replacement, data centre storage and resiliency, identity, zero trust, OT cyber tranches, "
    "site WAN. <b>Operational</b> (hub or site review, may vary by location): plant control and "
    "SCADA, access control, camp CCTV, ground probing radar. <b>Tactical</b> "
    "(solve a local problem, retire when superseded): tool tracker, catering selection, meeting "
    "room and training room refreshes."
    % (len(CAP_ROWS[1][4]), len(CAP_ROWS[2][4]), len(CAP_ROWS[3][4]), len(CAP_ROWS[5][4]),
       len(CAP_ROWS[0][4]), len(CAP_ROWS[4][4]), N, int(TOTAL_DAYS)),
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7.2;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, X0 + 14, YF + 24, LW - 28, FH - 30)

add("", "rounded=0;html=1;fillColor=#F1EDE7;strokeColor=#D9CDB8;", RX, YF, RW, FH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % RED, RX, YF, 5, FH)
add("GAPS, DATA QUALITY &amp; NEXT STEPS",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, RED), RX + 14, YF + 8, RW - 28, 12)
add("<b>Source data defect — fix before circulation:</b> in the CSV the High-Level Summary "
    "column is offset against Title across a block of rows, so descriptions belong to the wrong "
    "projects (Vulnerability Management is described as a radio frequency framework; Spectrum "
    "Management Database as fire detection; Onslow IT Disaster Recovery as an AMS-to-GIS "
    "integration). Capability mapping here was therefore driven by <b>Title only</b>, and the "
    "summary text is not used anywhere on this page.<br>"
    "<b>Data completeness:</b> %d of %d have no sponsor · %d have no author · %d have no "
    "estimated start date · %d carry no labour estimate. Coverage conclusions are sound; "
    "capacity and sequencing conclusions are not, until estimates exist.<br>"
    "<b>Assumptions to confirm:</b> capability assignment is analyst judgement from titles, not "
    "sponsor-confirmed — Beneficiate versus Exploit for plant visibility work, and Establish "
    "versus Support for camps and villages, are the two boundaries most likely to be disputed.<br>"
    "<b>Scoped out:</b> Tier 2 Data and Application Architecture and Tier 3 Technology "
    "Architecture; benefit cases, dependencies between initiatives, and the Complete and "
    "Cancelled history (%d rows) that would show delivery track record.<br>"
    "<b>Next steps:</b> assign a sponsor to every active initiative or retire it; estimate the "
    "%d unestimated; give every On Hold item a reason, an owner and a review date; then sequence "
    "the platform layer ahead of the capability work that depends on it."
    % (len(NO_SPONSOR), N, len(NO_AUTHOR), len(NO_START), len(NO_EST), DROPPED, len(NO_EST)),
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.9;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, RX + 14, YF + 24, RW - 28, FH - 30)

BOTTOM = YF + FH
add("Mineral Resources Limited&#160;&#160;·&#160;&#160;Business Architecture, one-page view"
    "&#160;&#160;·&#160;&#160;<b>active pipeline only</b>&#160;&#160;·&#160;&#160;A2 landscape"
    "&#160;&#160;·&#160;&#160;Generated from input/Projects Pipeline - Short Term.csv — "
    "regenerate the page rather than editing it by hand",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;fontColor=#888888;align=left;"
    "verticalAlign=middle;" % CG, X0, BOTTOM + 6, W, 12)

# ================================================================ assemble
PW, PGH = 2245, 1587
XML = (
    '<mxfile host="app.diagrams.net" agent="Claude Code" version="24.0.0" type="device">\n'
    '  <diagram name="Demand Profile - Short-Term Projects Pipeline" '
    'id="minres-pipeline-bizarch">\n'
    '    <mxGraphModel dx="%d" dy="%d" grid="0" gridSize="10" guides="1" tooltips="1" '
    'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" '
    'math="0" shadow="0" background="#FFFFFF">\n'
    '      <root>\n'
    '        <mxCell id="0" />\n'
    '        <mxCell id="1" parent="0" />\n'
    % (PW, PGH, PW, PGH)
    + "".join(cells) +
    '      </root>\n'
    '    </mxGraphModel>\n'
    '  </diagram>\n'
    '</mxfile>\n')

if __name__ == "__main__":
    outdir = os.path.join(ROOT, "output")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dest = os.path.join(outdir, "MinRes_Projects_Pipeline_Business_Architecture.drawio")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(XML)
    print("wrote %s" % dest)
    print("active = %d (Complete/Cancelled excluded = %d) ; placed = %d ; unplaced = %d"
          % (N, DROPPED, len(_seen), len(UNCLASSIFIED)))
    if RETIRED:
        print("classified but since retired (correctly off the page) = %d:" % len(RETIRED))
        for key, stage, where in RETIRED:
            print("     %-52s %-10s was %s" % (key[:52], stage, where))
    print("capability %d + platform %d = %d"
          % (sum(len(r[4]) for r in CAP_ROWS), N_PLAT,
             sum(len(r[4]) for r in CAP_ROWS) + N_PLAT))
    print("content bottom = %spx of %s ; %d cells" % (BOTTOM + 18, PGH, _id[0] - 1))
