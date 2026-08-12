# -*- coding: utf-8 -*-
"""Build the one-page Technology Architecture diagram for the blasting software as Draw.io.

Fourth and last in the set, after blasting_business_architecture_drawio.py (Tier 1),
blasting_data_architecture_drawio.py (Tier 2A) and
blasting_application_architecture_drawio.py (Tier 2B). Scope: TOGAF BDAT Tier 3
(Technology Architecture) only, mining-adapted, for SURFACE OPERATIONS ONLY — underground
and development blasting (2DRing, 2DFace) is out of scope by decision, carried down from
the companion pages.

Source of content: input/JKTech Software/ — the eight vendor capability analyses
(JKSimBlast, 2DBench, Design Importer, StockView, TimeHEx, FragmentO, JKVBOC and
SOFT-BLAST Blastatistics). Every platform statement traceable to those documents is stated
as vendor-sourced; every sizing, device, network, identity, backup and hosting decision not
in the vendor material is marked as an assumption, a MinRes standard to apply, or a gap.
Vendor-sourced technology facts used on the page:
  - Microsoft Access is the database backend; modules integrate by sharing Access databases
  - blast databases saved by 2DBench (.2db) are opened by JKBMS
  - JKSimBlast 3.0 is in development and is stated to change the database system
  - Windows XP, Vista, 7, 8 or 10 (32-bit or 64-bit); historically 98/NT4/2000/XP
  - electronic security key (USB dongle) plus matching licence file; v2.16 spans
    Hardlock/Sentinel and Keylok; from January 2024 all installers include Keylok drivers
  - StockView, Import and Units need no key and are always installed
  - install options: Surface (Option 1), Underground (Option 2), custom for tunnel
  - FragmentO 30–90 min per blast; JKVBOC 10–30 min (vendor) or 30–90 min (secondary)
  - Blastatistics is a vendor-hosted web platform plus mobile app, subscription-based,
    supported through regional distributors, permissioned per mine

Framework applied: .claude/rules/TOGAF_BDAT_MINING_ADAPTED_Enterprise_Architecture_Framework.html
  - Tier 3 item 1 — technology feasibility constraints by operational context
    (remote site / plant and hub / corporate), each with its upward impact
  - Tier 3 item 2 — the four mining technology patterns: industrial robustness,
    connectivity resilience, safety-first, environmental compliance
  - Tier 3 item 3 — bidirectional traceability; the upward band is the framework's
    mining addition and is given its own band, not a footnote
  - Tier 3 item 4 — governance: corporate standard, regional variation, site flexibility
  - Tier 3 item 5 — investment justification across the five mining criteria
  - Risk classification for the technology domain — infrastructure failure, obsolescence,
    support gaps, safety risk

Cost discipline from .claude/rules/cost_estimate_guidelines.html: this page carries no
dollar figure. Project definition maturity is Class 5 (concept screening) and a single-point
estimate would be false precision; the page states what must be known before any number can
be given, and leaves costing to the sponsor brief with its ±50% / +100% range.

Brand rules from .claude/rules/MINRES_Content_Guidelines.html: Century Gothic throughout;
MinRes Red #CE372F for title and accents; Dark Teal #00444C for band headers; Teal family
for IT, Coral/Peach family for OT and the edge, Wine family for IT/OT convergence and
safety-critical constraints; Brown 100 #F1EDE7 for gaps and unresolved items; Olive family
for governance and value criteria.

Page is A3 landscape (1587 x 1123 px at 96dpi) with 24px margins, matching the companion
Business, Data and Application Architecture pages.
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
    # OT / edge and in-pit — coral / peach family
    "OT": {"fill": "#F5E5DD", "line": "#E8C4B0", "ink": "#8E5239", "bar": "#C37556"},
    # IT/OT convergence and safety-critical — wine family
    "CV": {"fill": "#F4D9DD", "line": "#E8A5AD", "ink": "#8B2E45", "bar": "#C5556B"},
    # unresolved / not owned here — brown
    "GP": {"fill": "#F1EDE7", "line": "#D9CDB8", "ink": "#6B5435", "bar": "#A88F63"},
    # external / outside this architecture — neutral
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
add("Technology Architecture — Drill &amp; Blast Blasting Software",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=19;fontStyle=1;fontColor=%s;"
    "align=left;verticalAlign=top;" % (CG, RED), 44, 21, 760, 26)
add("<b>Mineral Resources Limited</b>&#160;&#160;·&#160;&#160;JKTech JKSimBlast suite "
    "(2DBench, JKBMS, Design Importer, StockView, TimeHEx, 2DView, FragmentO, JKVBOC) "
    "+ SOFT-BLAST Blastatistics<br><b><font color=\"#CE372F\">SURFACE OPERATIONS ONLY — "
    "underground and development blasting (2DRing, 2DFace) is out of scope</font></b>"
    "&#160;&#160;·&#160;&#160;TOGAF BDAT <b>Tier 3 — Technology Architecture</b>, "
    "mining-adapted. Platforms, devices, network, hosting, identity, backup and licensing "
    "under the <b>Application</b> (Tier 2B) and <b>Data</b> (Tier 2A) architectures — and the "
    "constraints that flow <b>upward</b> from the pit into both.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8.5;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, 44, 48, 1000, 34)
add("Prepared for: <b>Manager Drill &amp; Blast / Mining Services</b>&#160;·&#160;"
    "<b>Corporate IT &amp; OT</b><br>"
    "Source: input/JKTech Software — 8 vendor capability analyses<br>"
    "Rule: TOGAF BDAT Mining-Adapted EA Framework v2.0<br>"
    "12 August 2026&#160;&#160;·&#160;&#160;<b>Draft — analyst interpretation, "
    "not vendor-confirmed and not site-validated</b>",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7.5;fontColor=%s;align=right;"
    "verticalAlign=top;" % (CG, GREY), 1060, 22, 503, 60)

# legend
LEG = ("rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=" + CG +
       ";fontSize=7;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;")
for i, (k, lbl) in enumerate([("IT", "IT platform"), ("CV", "IT/OT boundary"),
                              ("OT", "edge / in-pit"), ("GP", "gap or unresolved")]):
    d = DOMAIN[k]
    add(lbl, LEG % (d["fill"], d["line"], d["ink"]), 1060 + i * 126, 66, 122, 14)

# ================================================================ Band A — feasibility by context
YA = 92
band(YA, 22, "TECHNOLOGY FEASIBILITY BY OPERATIONAL CONTEXT&#160;&#160;·&#160;&#160;"
     "CLOUD-FIRST IS ONLY VALID IN ONE OF THESE FOUR COLUMNS",
     "Framework Tier 3 item 1 — constraints, strategy, and the upward impact on data and "
     "application design")

CONTEXT = [
    ("IN-PIT / AT THE BENCH&#160;&#160;·&#160;&#160;EDGE",
     "<b>Constraints:</b> connectivity cannot be assumed; dust, heat, vibration and glare; "
     "gloved operation; a 12-hour shift on one charge; no local IT support at the blast; the "
     "device shares a light vehicle with everything else.<br>"
     "<b>Strategy:</b> ruggedised industrial tablet running the Blastatistics mobile app; "
     "validate at the point of capture; hold full-resolution photographs locally; queue and "
     "synchronise in connectivity windows. <b>No cloud dependency in the capture path.</b><br>"
     "<b>Upward impact — Data:</b> asynchronous sync and a conflict rule, not real-time "
     "writes. <b>Application:</b> the field app must be fully functional offline; the vendor's "
     "\"real-time connectivity\" framing must be tested, not assumed.",
     "OT"),
    ("SITE OFFICE &amp; SITE INFRASTRUCTURE&#160;&#160;·&#160;&#160;HOT LAYER",
     "<b>Constraints:</b> a blast is designed, approved and fired from here, so a WAN outage "
     "cannot stop work; thin on-site IT support; this is also where the statutory record "
     "physically lives today.<br>"
     "<b>Strategy:</b> Windows workstations running the full JKSimBlast suite, a site file "
     "share holding the Access design and record databases, and site-local backup. The whole "
     "design chain must survive loss of the corporate network.<br>"
     "<b>Upward impact — Application:</b> the design and record core cannot be made dependent "
     "on corporate connectivity or continuous deployment. <b>Data:</b> the hot layer is "
     "site-scoped by necessity, which is why cross-site consolidation is a hub problem.",
     "IT"),
    ("HUB / REGIONAL OPERATIONS CENTRE&#160;&#160;·&#160;&#160;WARM LAYER",
     "<b>Constraints:</b> aggregates several sites across a WAN; needs like-for-like "
     "comparison; carries the long model runs the sites cannot afford to sit through on shift."
     "<br><b>Strategy:</b> higher-specification analysis workstations for FragmentO and JKVBOC "
     "(vendor-stated 10–90 minutes per run); the Blastatistics web platform as the hub view, "
     "permissioned per mine; scheduled batch sync from each site rather than live replication."
     "<br><b>Upward impact — Data:</b> conformed keys and shared KPI definitions, or the "
     "benchmark is meaningless. <b>Application:</b> scenario modelling is a hub function with "
     "results published back, not an on-shift site calculation.",
     "CV"),
    ("CORPORATE &amp; CLOUD&#160;&#160;·&#160;&#160;COLD LAYER",
     "<b>Constraints:</b> minimal. Reliable infrastructure, full connectivity, standard "
     "enterprise technology applies — this is the only context on the page where it does."
     "<br><b>Strategy:</b> cloud-first is legitimate here — the enterprise archive and "
     "retention store, the master explosives catalogue and its controlled distribution, "
     "enterprise KPI reporting, identity, and management of the vendor hosting contract."
     "<br><b>Upward impact:</b> the constraint runs the other way. <b>Cloud-first cannot be "
     "mandated downward</b> onto the design core or in-pit capture, and a corporate standard "
     "that assumes always-on connectivity will simply be bypassed at site.",
     "IT"),
]
AH = 104
for (x, w), (t, d, dom) in zip(grid(4, 8), CONTEXT):
    dd = DOMAIN[dom]
    panel(x, YA + 26, w, AH, t, d, dd["fill"], dd["line"], dd["ink"], tsize=8, dsize=6.4)

# ================================================================ Band B — platform inventory
YB = YA + 26 + AH + 6
band(YB, 22, "TECHNOLOGY BUILDING BLOCKS&#160;&#160;·&#160;&#160;WHAT THESE APPLICATIONS "
     "ACTUALLY NEED TO RUN, AND AT WHICH GOVERNANCE LEVEL",
     "&#9888; marks a platform decision that is unmade, unconfirmed by the vendor, or "
     "untested against the MinRes environment")

BLOCKS = [
    ("Design workstation", "Windows desktop&#160;·&#160;site, within corporate SOE",
     "Runs 2DBench, Design Importer, StockView, Units, TimeHEx, 2DView and JKBMS. Vendor "
     "states <b>Windows XP, Vista, 7, 8 or 10, 32- or 64-bit</b>; needs a free USB port for "
     "the dongle. Office-class hardware, not specialised. <b>&#9888; Windows 11 is not in any "
     "vendor statement.</b>", "IT", True),
    ("Model compute", "analysis workstation or shared host&#160;·&#160;hub + site",
     "FragmentO <b>30–90 min</b> per blast; JKVBOC <b>10–30 min</b> (vendor) or 30–90 min "
     "(secondary source) per simulation. <b>&#9888; No published CPU, memory, multi-core or "
     "GPU behaviour</b> — one workstation must be benchmarked on a real blast before any seat "
     "or host is sized.", "IT", True),
    ("Field device", "ruggedised industrial tablet&#160;·&#160;site / in-pit",
     "IP-rated, drop-rated, sunlight-readable, glove-operable, battery for a full shift, "
     "vehicle mount and charging, and a camera good enough that a photograph stands as "
     "evidence. <b>&#9888; Supported mobile OS versions, MDM enrolment and true offline "
     "behaviour all unconfirmed.</b>", "OT", True),
    ("Database platform", "Microsoft Access files&#160;·&#160;site &#8594; corporate decision",
     "Vendor-stated <b>Microsoft Access backend</b>; modules integrate by pointing at shared "
     "Access databases, and 2DBench writes a blast database (.2db) that JKBMS opens. "
     "<b>&#9888; A shared file is not a database service</b> — concurrency, locking, file-size "
     "ceiling and corruption recovery are all unaddressed.", "GP", True),
    ("Site server &amp; storage", "file share + local backup&#160;·&#160;site within standards",
     "Holds the live design set and the statutory record, and must keep serving the office "
     "through a WAN outage. <b>&#9888; Nothing today specifies server class, resilience, "
     "snapshot frequency, storage growth per site, or who administers it at a remote "
     "operation.</b>", "GP", True),
    ("Network &amp; connectivity", "site LAN, pit coverage, WAN backhaul&#160;·&#160;regional",
     "Site LAN for the office; in-pit coverage (private LTE or Wi-Fi mesh) is a benefit, not "
     "an assumption; WAN or satellite backhaul carries sync and SaaS access. <b>&#9888; Photo "
     "and attachment volume per blast is unquantified</b>, so the sync window cannot yet be "
     "sized.", "CV", True),
    ("Hosting &amp; residency", "vendor SaaS + on-premises&#160;·&#160;corporate approval",
     "Hybrid by necessity: the JKSimBlast suite is entirely on-premises and site-local, while "
     "<b>Blastatistics is a vendor-hosted subscription platform</b> supported through regional "
     "distributors. <b>&#9888; Hosting region, tenancy, availability commitment and "
     "export-on-exit are contract terms MinRes does not yet hold.</b>", "GP", True),
    ("Identity &amp; access", "AD / Entra ID + platform roles&#160;·&#160;corporate standard",
     "Windows identity for the desktop suite; Blastatistics permissions set per mine and per "
     "function. <b>&#9888; No SSO or SAML is stated for the SaaS platform, and the Access "
     "databases inherit file-share permissions</b> — that is storage security, not an "
     "application access model, and it cannot express who may approve a design.", "GP", True),
    ("Licence &amp; key management", "Keylok USB dongle + licence file&#160;·&#160;corporate",
     "Per-seat <b>electronic security key plus matching licence file</b>; v2.16 spans legacy "
     "Hardlock/Sentinel and Keylok, and installers have shipped Keylok drivers since January "
     "2024. StockView, Import and Units need no key. <b>&#9888; No floating or network licence "
     "is offered, so seats are bound to physical machines.</b>", "CV", True),
    ("Backup, retention &amp; DR", "compliance control, not IT hygiene&#160;·&#160;corporate",
     "The statutory blast record sits in Access files on a site share, so backup is the "
     "control that makes the record defensible. Needs a stated RPO and RTO per site, an "
     "immutable copy held for the full retention period, and a tested restore. <b>&#9888; None "
     "of the three is defined today.</b>", "GP", True),
    ("Endpoint, SOE &amp; patching", "standard operating environment&#160;·&#160;corporate",
     "The suite has to live inside MinRes's managed environment: patching, EDR, disk "
     "encryption, install rights, and a USB policy that still admits the dongle. <b>&#9888; "
     "Compatibility with the current SOE, EDR and USB restrictions is untested — this is the "
     "most common reason a desktop rollout stalls.</b>", "GP", True),
    ("OT-side technology", "owned by OEMs and contractors&#160;·&#160;not owned here",
     "Detonator programming and firing units, drill rig onboard computers and MWD, vibration "
     "and airblast monitors, and the Split-Desktop image analysis workstation. MinRes provides "
     "network segmentation and a controlled transfer path for the timing file — nothing on "
     "this page changes or controls the firing chain.", "EX", False),
]
BH = 78
BG = grid(6, 6)
for i, (name, meta, desc, dom, warn) in enumerate(BLOCKS):
    x, w = BG[i % 6]
    y = YB + 26 + (i // 6) * (BH + 5)
    d = DOMAIN[dom]
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;" % (d["fill"], d["line"]), x, y, w, BH)
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % d["bar"], x, y, w, 3)
    add("<b><font style=\"font-size:7.8px\" color=\"%s\">%s</font></b><br>"
        "<font style=\"font-size:5.8px\" color=\"%s\"><b>%s</b></font><br>"
        "<font style=\"font-size:6.1px\" color=\"#000000\">%s</font>"
        % (d["ink"], name, d["ink"], meta, desc),
        "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;align=left;verticalAlign=top;"
        % CG, x + 7, y + 4, w - 14, BH - 7)

# ================================================================ Band C — mining patterns
YC = YB + 26 + BH * 2 + 5 + 6
band(YC, 22, "MINING TECHNOLOGY STANDARDS &amp; PATTERNS APPLIED&#160;&#160;·&#160;&#160;"
     "EACH WITH THE GOVERNANCE THAT MAKES IT REAL",
     "Framework Tier 3 item 2 — industrial robustness, connectivity resilience, safety-first, "
     "environmental compliance")
PATTERNS = [
    ("INDUSTRIAL ROBUSTNESS",
     "Industrial-grade equipment proven in mining over consumer computing, accepting higher "
     "unit cost for operational certainty: ruggedised tablets rather than standard laptops, "
     "multi-year warranty with a stated support commitment, and a spare device pool per pit so "
     "a broken screen does not cost a shift's record.<br>"
     "<b>Governance:</b> D&amp;B and OT sign off on device selection with IT; IT cannot "
     "procure the lowest-cost option. IP and drop rating, screen and battery specified before "
     "purchase, and one pit trials the device before any fleet order.",
     "OT"),
    ("CONNECTIVITY RESILIENCE",
     "No part of design, charge, timing or field capture may require the WAN to function. "
     "Edge capture with local cache, asynchronous batch synchronisation, and graceful "
     "degradation rather than a blocking error when the link drops. The site file share and "
     "the design workstations are deliberately local.<br>"
     "<b>Governance:</b> the framework's own rule — <b>connectivity assumptions are validated "
     "at each site before production deployment</b>, not designed from a corporate network "
     "diagram. Measure the real window before promising same-day reporting.",
     "IT"),
    ("SAFETY-FIRST",
     "Layered controls, never software alone: the certified OEM firing chain is the hardware "
     "layer, the software layer only issues an approved design and timing, and procedure backs "
     "both. Segment the design network from OT firing equipment, and make the timing transfer "
     "path controlled, scanned and logged. Prefer the proven version over the newest release."
     "<br><b>Governance:</b> safety and OT approve any change touching the firing path, "
     "including patching and version upgrades on the machine that produces the timing file. "
     "Safety testing precedes production deployment.",
     "CV"),
    ("ENVIRONMENTAL COMPLIANCE",
     "Prefer technology that makes compliance evidence easier to produce: predicted against "
     "measured PPV and airblast retained per blast per receiver, exceedance evidence "
     "retrievable on demand, and digital capture that removes the paper pack and some of the "
     "light-vehicle trips to the bench. Device fleets need a battery and e-waste path.<br>"
     "<b>Governance:</b> sustainability review of the device fleet and hosting decisions; "
     "measure the deployment against ESG targets rather than asserting alignment.",
     "IT"),
]
CH = 90
for (x, w), (t, d, dom) in zip(grid(4, 8), PATTERNS):
    dd = DOMAIN[dom]
    panel(x, YC + 26, w, CH, t, d, dd["fill"], dd["line"], dd["ink"], tsize=8, dsize=6.4)

# ================================================================ Band D — upward constraints
YD = YC + 26 + CH + 6
band(YD, 22, "CONSTRAINTS FLOWING UPWARD FROM TECHNOLOGY INTO APPLICATION AND DATA DESIGN"
     "&#160;&#160;·&#160;&#160;THE MINING ADDITION TO BDAT",
     "Framework Tier 3 item 3 — in mining, technology does not only receive requirements; it "
     "imposes them")
UPWARD = [
    ("U1&#160;&#160;INTERMITTENT PIT CONNECTIVITY",
     "<b>Because</b> the pit has no assumed link, <b>technology must</b> put capture and "
     "validation on the device and sync in windows. <b>So Data</b> needs a queue, a sync state "
     "and a conflict rule; <b>Application</b> must work fully offline and cannot show a "
     "blocking error at the bench."),
    ("U2&#160;&#160;PER-SEAT DONGLE LICENSING",
     "<b>Because</b> design modules need a USB key and matching licence file with no floating "
     "option, <b>technology</b> binds design to specific machines. <b>So Application</b> "
     "cannot assume VDI, thin client or work-from-anywhere design; <b>operations</b> need "
     "spare keys and a re-issue SLA, or a lost dongle stops design work."),
    ("U3&#160;&#160;SHARED-FILE ACCESS BACKEND",
     "<b>Because</b> integration is a shared Access file rather than a service, <b>technology "
     "caps</b> concurrency, file size and audit. <b>So Data</b> must stay site-scoped with "
     "consolidation done at the hub; <b>Application</b> integration stays file-based until v3 "
     "changes the database — <b>enterprise consolidation is not available on this platform.</b>"),
    ("U4&#160;&#160;MODEL RUN TIMES OF 10–90 MINUTES",
     "<b>Because</b> a single run outlasts the decision window, <b>technology</b> cannot make "
     "prediction interactive on shift. <b>So Application</b> must treat FragmentO and JKVBOC "
     "as pre-computed scenario tools; <b>Data</b> must store each prediction with its model "
     "version, calibration set and inputs so a stored result can be trusted later."),
    ("U5&#160;&#160;VENDOR-HOSTED WARM LAYER",
     "<b>Because</b> the hub and reporting layer is a vendor subscription platform outside "
     "MinRes infrastructure, <b>technology</b> inherits someone else's availability, region "
     "and access logging. <b>So Data</b> retention and residency must be designed around it, "
     "and the enterprise cold layer cannot be the vendor's platform."),
]
DH = 64
for (x, w), (t, d) in zip(grid(5, 8), UPWARD):
    box(head_desc(t, d, "#8B2E45", tsize=7.4, dsize=6.2), x, YD + 26, w, DH,
        "#F4D9DD", "#E8A5AD", INK, fs=7)

# ================================================================ Band E — governance
YE = YD + 26 + DH + 6
band(YE, 22, "TECHNOLOGY GOVERNANCE&#160;&#160;·&#160;&#160;CORPORATE STANDARDS WITH REAL "
     "SITE FLEXIBILITY INSIDE THEM",
     "Framework Tier 3 item 4 — governance earns its authority by demonstrated value to the "
     "pit, not by process")
GOV = [
    ("CORPORATE STANDARD — SET ONCE, APPLIES EVERYWHERE",
     "Operating environment and patching baseline, endpoint security, identity, network and "
     "segmentation standards, approved cloud platforms and data residency, backup and "
     "retention standards, and the vendor contract itself.<br>Specific to this architecture: "
     "the dongle and licence pool with serial register and re-issue SLA, and the mechanism by "
     "which the approved explosives catalogue is distributed to every site.",
     "IT"),
    ("REGIONAL / HUB VARIATION — WITHIN STANDARDS",
     "Connectivity design for the region's geography, the model-compute host and how sites "
     "queue long runs against it, sync scheduling and bandwidth allocation, hub analytics "
     "access, and the device fleet model including spares and repair turnaround.<br>"
     "Regional approval also covers upgrades inside an already-approved platform.",
     "CV"),
    ("SITE FLEXIBILITY — LOCAL AUTHORITY",
     "Device selection from the approved ruggedised list, workstation count and placement, the "
     "local module mix, local configuration and templates, file share layout inside the "
     "standard, and local training and support arrangements.<br>Sites legitimately differ: an "
     "iron ore bench and a pegmatite pit do not need the same analysis depth or the same "
     "number of seats.",
     "OT"),
    ("REQUIRES CORPORATE APPROVAL — NO SITE SHORTCUT",
     "Anything touching the firing path or the OT network. Any new SaaS or cross-border data "
     "movement. Changing where the statutory record is held. The v3.0 upgrade and its database "
     "migration. Any move of the design core to cloud or VDI.<br><b>Escalation:</b> where a "
     "corporate standard would make a site unable to design or fire, the site position wins "
     "and the standard is amended — with the decision recorded.",
     "GP"),
]
EH = 84
for (x, w), (t, d, dom) in zip(grid(4, 8), GOV):
    dd = DOMAIN[dom]
    panel(x, YE + 26, w, EH, t, d, dd["fill"], dd["line"], dd["ink"], tsize=8, dsize=6.4)

# ================================================================ Band F — technology risk
YF = YE + 26 + EH + 6
band(YF, 22, "TECHNOLOGY RISK&#160;&#160;·&#160;&#160;CLASSIFIED THE WAY THE FRAMEWORK ASKS, "
     "WITH THE MITIGATION NAMED",
     "Infrastructure failure&#160;·&#160;obsolescence&#160;·&#160;support gaps&#160;·&#160;"
     "safety risk&#160;·&#160;vendor dependency")
RISKS = [
    ("INFRASTRUCTURE FAILURE",
     "The statutory record and the live design set sit in Access files on one site share, with "
     "no stated high availability. A storage failure or a corrupted file is a compliance event, "
     "not an inconvenience.<br><b>Mitigate:</b> resilient storage, frequent snapshots, tested "
     "restore, and an immutable off-site copy of the closed record."),
    ("OBSOLESCENCE",
     "The newest operating system in any vendor statement is Windows 10, which left Microsoft "
     "support in October 2025; the backend is Access; and <b>v3.0 is stated to change the "
     "database system</b>. Adopting v2.x without a v3 position is buying a migration."
     "<br><b>Mitigate:</b> get the Windows 11 and v3 roadmap in writing before committing."),
    ("SUPPORT GAPS",
     "Specialist vendors and a regional distributor model, with no stated response time; the "
     "skills to run this — blast engineering plus Access plus dongle licensing — are scarce and "
     "concentrated in very few people.<br><b>Mitigate:</b> contracted support terms, named "
     "internal owners with a deputy, and documented runbooks rather than tribal knowledge."),
    ("SAFETY RISK",
     "The transfer of the timing file to the OEM firing device is the most safety-relevant "
     "technology path here and the least documented; removable media between an office PC and "
     "OT equipment is a malware route.<br><b>Mitigate:</b> segment the networks, define one "
     "scanned and logged transfer path, and put OT and safety in the approval loop."),
    ("VENDOR &amp; HOSTING DEPENDENCY",
     "Two vendors on different platforms, one of them holding the hub layer as a subscription "
     "service outside MinRes infrastructure, with residency and exit unspecified."
     "<br><b>Mitigate:</b> contractual export and deletion rights, a periodic full export held "
     "by MinRes, and an availability commitment proportionate to how the data is relied on."),
]
FRH = 70
for (x, w), (t, d) in zip(grid(5, 8), RISKS):
    box(head_desc(t, d, "#6B5435", tsize=7.5, dsize=6.2), x, YF + 26, w, FRH,
        "#F1EDE7", "#D9CDB8", INK, fs=7)

# ================================================================ Band G — investment justification
YG = YF + 26 + FRH + 6
band(YG, 22, "TECHNOLOGY INVESTMENT JUSTIFICATION&#160;&#160;·&#160;&#160;VALUE MUST SHOW "
     "ACROSS MULTIPLE MINING CRITERIA, NOT COST ALONE",
     "Framework Tier 3 item 5 — with the cost position stated honestly at Class 5")
VALUE = [
    ("PRODUCTION IMPACT",
     "Fragmentation on specification and a muckpile that digs, feeding crusher and mill "
     "throughput.<br><b>Measured by:</b> oversize %, dig rate, throughput and comminution "
     "energy per tonne."),
    ("COST IMPACT",
     "Explosives consumption reconciled against design, less re-drill and secondary breakage, "
     "less engineering time spent re-keying.<br><b>Measured by:</b> $/t and $/BCM, powder "
     "factor variance, hours saved per blast."),
    ("SAFETY IMPACT",
     "A legible design at the bench, deviations captured, and a defensible record behind every "
     "fired blast.<br><b>Measured by:</b> misfire and flyrock counts, exclusion-zone events, "
     "near-miss reporting, audit findings closed."),
    ("ENVIRONMENTAL IMPACT",
     "Predicted against measured vibration and airblast per receiver, evidence retrievable on "
     "demand.<br><b>Measured by:</b> exceedances and complaints, licence conditions "
     "demonstrably met, dust and fume events."),
    ("WORKFORCE IMPACT",
     "Manual data entry removed, minimal training at the bench, and less dependence on the one "
     "engineer who knows the spreadsheet.<br><b>Measured by:</b> re-keying steps eliminated, "
     "time to competence, retention."),
    ("COST POSITION — CLASS 5, NO FIGURE ON THIS PAGE",
     "Definition maturity is <b>concept screening</b>, so any single number would be false "
     "precision; costing belongs in the sponsor brief with a <b>±50% / +100%</b> range and "
     "risk-based contingency. <b>Needed first:</b> seat and dongle count, device fleet and "
     "spares, site and server count, sizing benchmark on a real blast, subscription terms."),
]
GH = 62
for i, ((x, w), (t, d)) in enumerate(zip(grid(6, 6), VALUE)):
    if i == 5:
        box(head_desc(t, d, RED, tsize=7.2, dsize=6.1), x, YG + 26, w, GH,
            "#F9E5E3", RED, INK, fs=7)
    else:
        box(head_desc(t, d, "#5E623C", tsize=7.5, dsize=6.2), x, YG + 26, w, GH,
            "#F0F2E5", "#D9DCBC", INK, fs=7)

# ================================================================ footer
YH = YG + 26 + GH + 6
FTH = 146
FG = grid(2, 8)
LX, LW = FG[0]
RX, RW = FG[1]

add("", "rounded=0;html=1;fillColor=#FFFFFF;strokeColor=#B8DDE3;", LX, YH, LW, FTH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % TEAL, LX, YH, 5, FTH)
add("TRACEABILITY&#160;&#160;·&#160;&#160;IN THE FORM THE FRAMEWORK REQUIRES",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, TEAL), LX + 14, YH + 7, LW - 28, 12)
add("<b><font color=\"#2D686F\">THIS TECHNOLOGY ENABLES</font></b> — the Tier 2B application "
    "portfolio (JKSimBlast design and record suite, Blastatistics web and mobile) and the "
    "Tier 2A data architecture (edge / hot / warm / cold layering), <b>which ultimately "
    "supports the EMMM Exploit capability: design, fire and reconcile a surface blast</b> — "
    "at <b>site level</b> (workstations, site share, field devices), <b>hub level</b> (model "
    "compute, warm platform) and <b>corporate level</b> (identity, retention, catalogue "
    "distribution, contracts).<br>"
    "<b><font color=\"#8E5239\">MINING CONSTRAINTS ADDRESSED</font></b> — connectivity "
    "(offline capture, site-local design core, batch sync), harsh environment (ruggedised "
    "devices), safety (segmentation and a controlled timing transfer path), operational "
    "autonomy (nothing here touches the certified firing chain), and regulatory retention "
    "(backup treated as a compliance control).<br>"
    "<b><font color=\"#5E623C\">PATTERNS APPLIED</font></b> — industrial robustness, "
    "connectivity resilience, safety-first and environmental compliance, each with its "
    "governance step named above.<br>"
    "<b><font color=\"#8B2E45\">GOVERNANCE LEVEL</font></b> — corporate standard for SOE, "
    "identity, security, residency, retention and licence pool; regional variation for "
    "connectivity, compute and fleet; site flexibility for devices, seats and configuration; "
    "<b>corporate approval for anything touching the firing path, the OT network, or where the "
    "statutory record lives</b>.<br>"
    "<b><font color=\"#CE372F\">UPWARD CONSTRAINTS IMPOSED</font></b> — U1 to U5 above: "
    "offline-first capture, seat-bound design, a site-scoped shared-file data store, "
    "pre-computed prediction, and a vendor-hosted warm layer.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.4;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, LX + 14, YH + 22, LW - 28, FTH - 28)

add("", "rounded=0;html=1;fillColor=#F1EDE7;strokeColor=#D9CDB8;", RX, YH, RW, FTH)
add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % RED, RX, YH, 5, FTH)
add("GAPS, ASSUMPTIONS &amp; NEXT STEPS",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=%s;align=left;"
    "verticalAlign=top;" % (CG, RED), RX + 14, YH + 7, RW - 28, 12)
add("<b>The decisive gap:</b> the vendor material describes what the software does, not what "
    "it needs to run. <b>There is no published system requirement, sizing guide, concurrency "
    "limit, virtualisation position or supported-Windows statement beyond Windows 10</b> — so "
    "every number on a procurement or infrastructure request would be invented today.<br>"
    "<b>Structural gaps:</b> "
    "(1) <b>no database service</b> — a shared Access file caps concurrency, size and audit, "
    "and v3.0 is stated to change it. "
    "(2) <b>Windows baseline ends at 10</b>, out of Microsoft support since October 2025; the "
    "Windows 11 and 64-bit position is unconfirmed. "
    "(3) <b>No backup, RPO/RTO or restore test</b> for a store that holds the statutory record. "
    "(4) <b>Dongle per seat with no floating licence</b> — a single point of failure and a "
    "block on VDI and remote design. "
    "(5) <b>Identity is file-share permissions plus per-mine SaaS roles</b>, with no SSO and no "
    "approval role model. "
    "(6) <b>Timing transfer path to the detonator OEM is undefined</b> — the highest-consequence "
    "technology path on the page. "
    "(7) <b>Hosting region, availability and export-on-exit unheld</b>. "
    "(8) <b>Sync bandwidth and photo volume unquantified</b>, so same-day reporting is a "
    "promise without a measurement.<br>"
    "<b>Assumptions to confirm:</b> that MS Access is the v2.x backend and that v3.0 replaces "
    "it; that a design workstation is office-class (unverified — benchmark FragmentO and "
    "JKVBOC before sizing); that StockView, Import and Units genuinely need no key, since one "
    "source states the Design Importer <i>is</i> key-controlled; that the mobile app is "
    "genuinely offline-first. Device, network and hosting content on this page is MinRes "
    "standard practice applied by the analyst, not vendor-stated.<br>"
    "<b>Out of scope:</b> underground and development blasting; procurement pricing and "
    "commercial terms; the migration sequence from the Orica toolset (see the companion "
    "migration page).<br>"
    "<b>Next steps:</b> get written system requirements and the v3 roadmap from JKTech; "
    "benchmark one real blast on one workstation; run an SOE, EDR and USB compatibility test; "
    "trial one ruggedised device in one pit and measure the actual connectivity window; agree "
    "backup, retention and DR with Corporate IT; put residency, availability and exit into the "
    "Blastatistics contract; then size and cost the rollout.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.1;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, RX + 14, YH + 22, RW - 28, FTH - 28)

BOTTOM = YH + FTH
add("Mineral Resources Limited&#160;&#160;·&#160;&#160;Technology Architecture, one-page view"
    "&#160;&#160;·&#160;&#160;Surface operations only — underground out of scope"
    "&#160;&#160;·&#160;&#160;A3 landscape&#160;&#160;·&#160;&#160;Completes the BDAT set with "
    "MinRes_Blasting_Software_Business_Architecture (Tier 1), "
    "_Data_Architecture (Tier 2A) and _Application_Architecture (Tier 2B)",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;fontColor=#888888;align=left;"
    "verticalAlign=middle;" % CG, X0, BOTTOM + 6, W, 12)

# ================================================================ assemble
PW, PH = 1587, 1123
XML = (
    '<mxfile host="app.diagrams.net" agent="Claude Code" version="24.0.0" type="device">\n'
    '  <diagram name="Technology Architecture - Blasting Software" id="minres-blast-techarch">\n'
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
                        "MinRes_Blasting_Software_Technology_Architecture.drawio")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(XML)
    print("wrote %s" % dest)
    print("content bottom = %spx of %s ; %d cells" % (BOTTOM + 18, PH, _id[0] - 1))
