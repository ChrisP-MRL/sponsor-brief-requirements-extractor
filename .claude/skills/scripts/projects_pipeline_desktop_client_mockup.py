# -*- coding: utf-8 -*-
"""Build the interactive HTML mock-up of the Projects Pipeline Desktop Client, for UI review.

WHAT THIS IS
------------
A single self-contained HTML file that a reviewer opens by double-click, with no install,
no server and no network call. It behaves like the specified client against the real
extract: filters, sorting, hover detail, drill-down and every derived figure recalculate
live in the browser. Three things a mock-up cannot do are visibly stubbed and labelled:
choosing a file, writing a file, and verified pagination.

Requirement source: requirements/FRS_Projects_Pipeline_Desktop_Client_20260818_055848.xlsx
  183 functional requirements (FR-001..FR-183) across 6 modules
   42 non-functional requirements (NFR-001..NFR-042) across 12 BABOK s10.30 categories

Content authorities — the tables below are ported from these two scripts, not re-derived:
  .claude/skills/scripts/projects_pipeline_business_architecture_drawio.py
  .claude/skills/scripts/projects_pipeline_demand_profile_drawio.py
Brand authority: .claude/rules/MINRES_Content_Guidelines.html

DIVISION OF LABOUR
------------------
This generator does NO analysis. It reads the extract, embeds it as a JSON snapshot, and
emits the CSS/CONFIG/derive/render/app sections. Every count, tier, proration, quartile,
scenario and measure is computed in the emitted JavaScript, so the figures recalculate on
every filter change and the derivation logic is what the reviewer actually exercises.
That also means the production client is one localised change away: swap the embedded
snapshot for a FileReader.

Run: python projects_pipeline_desktop_client_mockup.py
Writes: output/MinRes_Projects_Pipeline_Desktop_Client_Mockup.html
Regenerate the file rather than editing it by hand.
"""
import csv
import datetime as dt
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CSV_PATH = os.path.join(ROOT, "input", "Projects Pipeline - Short Term.csv")
OUT_DIR = os.path.join(ROOT, "output")
OUT_NAME = "MinRes_Projects_Pipeline_Desktop_Client_Mockup.html"

CLIENT_VERSION = "0.9-mockup"
BUILD_DATE = "18 August 2026"

FIELDS = [
    "Title", "High-Level Summary", "Stage", "Author", "Sponsor", "Budget",
    "Start Date - Est Project", "Duration - Est Project (months)",
    "PM - Est Project Labour Days", "BA - Est Project Labour Days",
    "IE - Est Project Labour Days", "CD - Est Project Labour Days",
    "SA - Est Project Labour Days", "Other - Est Project Labour Days",
]


# ================================================================ read the extract
def read_extract(path):
    """Read the extract verbatim. No normalisation here — the client does that in JS,
    because FR-149..FR-156 normalisation is behaviour the reviewer must be able to see."""
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8-sig")
    physical = len(text.splitlines())
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        header = list(rdr.fieldnames or [])
        rows = [[(r.get(f) or "") for f in FIELDS] for r in rdr]
    stat = os.stat(path)
    return {
        "name": os.path.basename(path),
        "path": "input/" + os.path.basename(path),
        "bytes": len(raw),
        "bom": raw[:3] == b"\xef\xbb\xbf",
        "physicalLines": physical,
        "header": header,
        "fields": FIELDS,
        "rows": rows,
        "modified": dt.datetime.fromtimestamp(stat.st_mtime).strftime("%d %B %Y %H:%M"),
    }


SNAP = read_extract(CSV_PATH)
MISSING = [f for f in FIELDS if f not in SNAP["header"]]
if MISSING:
    raise SystemExit("extract is missing required columns: %s" % ", ".join(MISSING))

# ================================================================ CONFIG — one surface
# NFR-018: the whole configuration surface is declared here and emitted as one JS object.
# Nothing below is computed; every table is content ported from an authority script.

CONFIG = {
    "meta": {
        "clientVersion": CLIENT_VERSION,
        "buildDate": BUILD_DATE,
        "sensitivity": "MinRes INTERNAL",
        "daysPerFteMonth": 21.0,
        "horizonMonths": 12,
        "canvas": {"w": 2245, "h": 1587, "margin": 24},
        "frameworks": {
            "ba": "TOGAF BDAT Mining-Adapted EA Framework v2.0 — Tier 1 Business "
                  "Architecture; Open Group EMMM Business Capability Reference Map",
            "dp": "SCOR Plan process — 2.1 demand forecasting, 2.2 capacity and resource "
                  "planning, 2.3 business rules; KPIs from SCOR 7.2 and 8",
        },
    },

    # ---------------------------------------------------------- scope sets (FR-123..126)
    "scope": {
        "active": ["Opportunity", "In Progress", "On Hold"],
        "dead": ["Complete", "Cancelled"],
        "demand": ["In Progress", "Opportunity"],
        "demandExcluded": ["On Hold", "Complete", "Cancelled"],
    },

    # ---------------------------------------------------------- palette
    "palette": {
        "red": "#CE372F", "teal": "#00444C", "ink": "#000000", "grey": "#5C5C5C",
        "rule": "#D1D1D1", "surf": "#F1EDE7", "surf2": "#E8E8E8",
        # MinRes Red is a title and accent colour and clears 4.5:1 only on white. Small
        # bold alert text sits on a tinted chip fill instead, where the brand red reaches
        # 4.07:1 at worst, so a darker red carries that text and #CE372F keeps the titles,
        # the peak marker and the focus ring (NFR-039).
        "redInk": "#A82A23",
        # Within each family: fill is the surface, line the 1px boundary that identifies
        # the chip as a control, bar the saturated stage marker, ink the text on the fill.
        # line and bar are graphical objects and clear 3:1 on white; ink clears 4.5:1 on
        # its own fill (WCAG 1.4.11 and 1.4.3 — NFR-039).
        "stage": {
            "In Progress": {"fill": "#E0F7F9", "line": "#1F97A6",
                            "ink": "#166D78", "bar": "#1A8D9B"},
            "Opportunity": {"fill": "#F1EDE7", "line": "#A58D62",
                            "ink": "#6B5435", "bar": "#967E55"},
            "On Hold": {"fill": "#F5E5DD", "line": "#C37556",
                        "ink": "#8E5239", "bar": "#B2694C"},
        },
        "domain": {
            "IT": {"fill": "#E0F7F9", "line": "#1F97A6", "ink": "#166D78", "bar": "#1A8D9B"},
            "OT": {"fill": "#F5E5DD", "line": "#C37556", "ink": "#8E5239", "bar": "#B2694C"},
            "CV": {"fill": "#F4D9DD", "line": "#CE6B7C", "ink": "#8B2E45", "bar": "#C5556B"},
        },
        "severity": {
            "Critical": ["#F4D9DD", "#E8A5AD", "#8B2E45"],
            "Serious": ["#F5E5DD", "#E8C4B0", "#8E5239"],
            "Moderate": ["#F1EDE7", "#D9CDB8", "#6B5435"],
        },
        # Role series: bottom -> top of the stack. Third value is the label ink, chosen by
        # contrast against the fill (white only where it clears 4.5:1) — FR-001..003.
        "series": [
            ["IE", "#3F939C", "#000000"],
            ["BA", "#6B5435", "#FFFFFF"],
            ["PM", "#878C56", "#000000"],
            ["SA", "#8B2E45", "#FFFFFF"],
            ["Other", "#C37556", "#000000"],
        ],
        "allowance": {"fill": "#E8E8E8", "line": "#888888", "ink": "#5C5C5C"},
    },

    "roles": ["PM", "BA", "IE", "CD", "SA", "Other"],
    "roleFull": {
        "PM": "Project Manager", "BA": "Business Analyst",
        "IE": "Infrastructure Engineer", "CD": "Change / Delivery",
        "SA": "Solution Architect", "Other": "Other / specialist",
    },

    # ---------------------------------------------------------- capability spine (FR-108..113)
    # Analyst judgement, by Title only. The High-Level Summary column is offset against
    # Title across a block of records in the source, so it is never used to classify.
    "capabilities": [
        {"key": "DISCOVER", "cover": "Exploration &amp; ore body knowledge", "domain": "IT",
         "verdict": "Only one active initiative touches ore body knowledge, and it is On "
                    "Hold. The related visualisation initiative was cancelled.",
         "titles": ["Voxel Farm: Phase 2"]},
        {"key": "ESTABLISH", "cover": "Mine development &amp; site establishment",
         "domain": "CV",
         "verdict": "Growth work: Mt Marion underground and floatation, Onslow "
                    "accommodation, Winu. Driven by capital schedules, not by IT.",
         "titles": ["Winu EPC FID",
                    "Mt Marion Underground - Infrastructure",
                    "Mt Marion Floatation Plant - Infrastructure",
                    "Mt Marion Village Expansion (perm)",
                    "Lot 300"]},
        {"key": "EXPLOIT", "cover": "Production operations", "domain": "CV",
         "verdict": "Mining execution and production visibility. Thin for the capability "
                    "that earns the revenue: two of the four are unfunded, and the Ampla, "
                    "operational reporting and Bald Hill roadmap work was cancelled.",
         "titles": ["Remote Monitoring Centre",
                    "Mt Marion Underground - Mining Systems",
                    "AHS Vehicle Data",
                    "Lamb Creek - Ampla",
                    "Operational Reporting Improvement (POC)",
                    "Bald Hill Operational Apps - Roadmap",
                    "Kens Bore - Ground Probing Radar"]},
        {"key": "BENEFICIATE", "cover": "Mineral processing", "domain": "OT",
         "verdict": "Plant control and plant visibility — the largest OT concentration in "
                    "the capability spine, and safety-critical. Three of the five are On "
                    "Hold; metallurgical accounting and assay (CCLAS) were cancelled.",
         "titles": ["Mt Marion Floatation Plant - Control System",
                    "Mt Marion Floatation Plant - Business Systems",
                    "Mt Marion Metallurgical Accounting",
                    "Control Systems Uplift - West Angeles and Granites",
                    "Control Systems Uplift - Granites",
                    "SCADA Visualisation @ 20 Walters Drive",
                    "Plant Cameras Viewable at HQ",
                    "IV CCLAS"]},
        {"key": "SELL", "cover": "Market, logistics &amp; customer", "domain": "IT",
         "verdict": "No active initiative. The Phase 2 demand chain scheduling work was "
                    "cancelled, so product movement to port and customer is now wholly "
                    "unrepresented.",
         "titles": ["Demand Chain Scheduling System - Phase 2"]},
        {"key": "SUPPORT", "cover": "HSE, workforce, security &amp; corporate",
         "domain": "IT",
         "verdict": "The broadest capability by count: site security and access, village "
                    "services, worker health and PPE, and PMO method.",
         "titles": ["Access Control - Onslow In-land",
                    "Mobile Phone FOBs - Access Control",
                    "Camp CCTV Tech Standards",
                    "Camp CCTV Upgrade",
                    "Central CCTV viewing - Onslow",
                    "Catering System Selection",
                    "Mine Site Clinic Digital Intake & Calendar Application",
                    "PPE Express - Sponsor Brief (Define Phase)",
                    "MtM Tool Tracker",
                    "Project Management Methodology Refresh"]},
    ],

    # ---------------------------------------------------------- platform layer (FR-120..122)
    "platform": [
        {"key": "OT CYBER &amp; SITE HARDENING", "domain": "OT",
         "note": "Safety-critical. Five of seven On Hold.",
         "titles": ["OT Cyber Initiatives – Tranche 3",
                    "OT Cyber - Tranche 3",
                    "OT Cyber for Energy Assets",
                    "Mt Marion OT Cyber - Phase 3",
                    "OT Cyber - Rod Ore",
                    "Mt Marion Firewall Refresh",
                    "Site Firewall EOL Refresh"]},
        {"key": "IT SECURITY &amp; IDENTITY", "domain": "IT",
         "note": "All four are Opportunity — none started.",
         "titles": ["Identity And Access Management – Tranche 2",
                    "Zero Trust Network Architecture",
                    "Vulnerability Management",
                    "Firewall Rule Optimisation"]},
        {"key": "NETWORK, RADIO &amp; SPECTRUM", "domain": "CV",
         "note": "Site connectivity and licensed spectrum.",
         "titles": ["Mt Marion Fibre Upgrade",
                    "Mt Marion DMR Tower Relocation",
                    "Site WAN Optimisation",
                    "Spectrum Management Database",
                    "Resilient IT Infrastructure Installation",
                    "IPAM"]},
        {"key": "COMPUTE, STORAGE &amp; CLOUD", "domain": "IT",
         "note": "VMware exit is the forcing event.",
         "titles": ["VMWare Replacement",
                    "VMWare 9.0 Upgrade",
                    "Data Centre Storage Refresh",
                    "Cross Data Centre Resiliency - Switching",
                    "Extend OT Compute to Cloud",
                    "CSI File Server Consolidation",
                    "Crushing File storage standardisation"]},
        {"key": "RESILIENCE, INTEGRATION &amp; ITSM", "domain": "IT",
         "note": "Recovery, integration and IT operations.",
         "titles": ["Onslow IT Disaster Recovery Improvement",
                    "IT Infrastructure End of Life Replacement - Distribution Centre",
                    "Design & Harden Enterprise Application Integration",
                    "Deploy ITOM"]},
        {"key": "WORKPLACE &amp; COMMS FACILITIES", "domain": "CV",
         "note": "Offices, meeting rooms, comms room protection.",
         "titles": ["Meeting Room AV Study",
                    "20WD Meeting Room Refresh Phase 1",
                    "18 Hasler Meeting Room Upgrade",
                    "18 Hasler Training Room Uplift",
                    "Onslow Comms Rooms Fire Detection and Suppression",
                    "Onslow Fire Detection and Suppression"]},
    ],

    # ---------------------------------------------------------- BA prose (FR-033..038, 016..019)
    # {TOKEN} is substituted at render time from the live model, so these read correctly
    # under any filter. Substituted values are escaped before insertion.
    "drivers": [
        ["Volume growth &amp; new capacity",
         "Onslow Iron ramp-up, Mt Marion underground and floatation, Winu. Growth capital "
         "sets immovable dates that the pipeline must serve, not negotiate."],
        ["Cost per tonne",
         "Lowest-quartile $/t. Every initiative competes with the alternative of not doing "
         "it; unfunded pipeline items are not cost-free — they consume scarce PM, BA and IE "
         "capacity."],
        ["Safety &amp; licence to operate",
         "Zero harm. OT control systems, plant SCADA, access control and worker health "
         "carry obligations that do not pause when a project goes On Hold."],
        ["Cyber resilience &amp; asset protection",
         "IT and OT exposure across remote sites, energy assets and plants. The largest "
         "single cluster of active demand and the most stalled."],
        ["Standardised operating platform",
         "One network, compute, identity and reporting standard across iron ore, lithium "
         "and energy assets, so capability is portable between sites and crews."],
    ],
    "site": [
        ["Growth schedules are not negotiable",
         "Mt Marion underground, the floatation plant and Onslow accommodation have "
         "construction dates. IT work that serves them inherits those dates and cannot be "
         "deferred by an IT prioritisation decision."],
        ["Delivery capacity is the real constraint",
         "{TOTAL_DAYS} estimated labour days sit on just {N_WITH_EST} of {N} initiatives — "
         "IE {D_IE}, BA {D_BA}, PM {D_PM}, SA {D_SA}. The other {N_NO_EST} are unestimated, "
         "so true demand is unknown and certainly larger."],
        ["Remote sites and connectivity windows",
         "Onslow, Kens Bore, Mt Marion, Bald Hill and the energy assets. Network, radio and "
         "spectrum work gates almost everything else, so platform slippage propagates."],
        ["OT cannot be treated like IT",
         "Plant control systems and OT cyber sit behind production availability. Change "
         "windows are set by the plant, not by an IT release calendar."],
        ["On Hold is not free",
         "{N_ON_HOLD} initiatives are On Hold. Risk, End-of-Life exposure and obligations "
         "continue to accrue while the work does not."],
        ["Sponsor and author attention is concentrated",
         "{TOP_SPONSOR} sponsors {TOP_SPONSOR_N} of {N} active initiatives and "
         "{TOP_AUTHOR} authored {TOP_AUTHOR_N} of them; {N_NO_SPONSOR} have no sponsor and "
         "{N_NO_AUTHOR} no author. Decision and analysis throughput, not appetite, becomes "
         "the bottleneck."],
    ],
    "governance": [
        ["CORPORATE — sets the standard and the envelope",
         "<b>Approves:</b> the enabling platform standards (network, compute, identity, "
         "cyber) · portfolio classification and sequencing · funding gates for the "
         "{N_FUNDED} budget-approved initiatives · End-of-Life and cyber risk "
         "acceptance.<br><b>Authority:</b> Corporate Architecture with IT/OT leadership "
         "and Group Risk.<br><b>Owns the platform layer</b> — no site may solve a platform "
         "problem locally.", "#E0F7F9", "#B0EDF3", "#1A7C87"],
        ["HUB / REGIONAL — adapts within the standard",
         "<b>Approves:</b> which optional capability initiatives a hub runs · sequencing "
         "against the site's production and construction calendar · local acceptance of "
         "platform rollouts · hub-level benefit claims.<br><b>Authority:</b> Hub "
         "Operations Manager with the Regional Asset owner.",
         "#E3F2F4", "#B8DDE3", "#2D686F"],
        ["SITE — executes and escalates",
         "<b>Decides:</b> change windows for plant and OT systems · day-to-day operational "
         "acceptance · whether a deployment is safe to proceed on shift.<br>"
         "<b>Escalates:</b> any initiative whose slip creates a safety, statutory or "
         "production exposure &#8594; Hub &#8594; Corporate, in the same reporting "
         "period.<br><b>Authority:</b> Site Senior Executive.",
         "#F5E5DD", "#E8C4B0", "#8E5239"],
        ["STALLED &amp; UNGOVERNED DEMAND — special control",
         "<b>{N_ON_HOLD} On Hold and {N_NO_SPONSOR} unsponsored initiatives are the "
         "highest-risk item on this page.</b> An initiative with no sponsor has no one "
         "accountable for the benefit and no one to escalate to.<br><b>Rule:</b> every "
         "active initiative carries a named sponsor or it leaves the pipeline. On Hold "
         "requires a stated reason, a review date and an explicit owner of the accruing "
         "risk.<br><b>OT exception:</b> OT cyber and control-system work cannot be held on "
         "IT grounds alone — holding it is a safety and production risk decision, and must "
         "be taken as one.", "#F4D9DD", "#CE372F", "#8B2E45"],
    ],
    "metrics": [
        ["CAPABILITY COVERAGE",
         "No revenue-earning capability left with a single active initiative. Today "
         "{THIN_LIST}."],
        ["GOVERNANCE COMPLETENESS",
         "Every active initiative has a named sponsor, a stage reason and a review date. "
         "Today {N_NO_SPONSOR} of {N} have no sponsor."],
        ["ESTIMATE COMPLETENESS",
         "Every active initiative carries a labour estimate before it competes for "
         "capacity. Today {N_NO_EST} of {N} do not."],
        ["SCHEDULE INTEGRITY",
         "Every In Progress and funded initiative has an estimated start. Today "
         "{N_NO_START} of {N} have no start date."],
        ["STALL RATE",
         "On Hold trending down, with the accruing risk explicitly owned. Today "
         "{N_ON_HOLD} of {N} ({PCT_ON_HOLD}%) are On Hold."],
        ["SAFETY &amp; OBLIGATION EXPOSURE",
         "No safety, statutory or End-of-Life obligation sitting behind an On Hold or "
         "unsponsored initiative. OT cyber and plant control are the test cases."],
    ],
    "baFooter": {
        "leftTitle": "BIDIRECTIONAL TRACEABILITY&#160;&#160;·&#160;&#160;REQUIRED BY THE "
                     "FRAMEWORK",
        "left":
            "<b><font color=\"#2D686F\">DOWNWARD</font></b> — corporate driver (volume "
            "growth · cost per tonne · safety and licence · cyber resilience · "
            "standardised platform) &#8594; EMMM business capability (<b>Establish</b> "
            "{C_ESTABLISH} · <b>Exploit</b> {C_EXPLOIT} · <b>Beneficiate</b> "
            "{C_BENEFICIATE} · <b>Support</b> {C_SUPPORT} · <b>Discover</b> {C_DISCOVER} · "
            "<b>Sell</b> {C_SELL}) &#8594; the {N} named active initiatives on this page "
            "&#8594; Tier 2 Data and Application and Tier 3 Technology architecture, "
            "<b>deliberately out of scope on this page</b>.<br>"
            "<b><font color=\"#6B5435\">UPWARD</font></b> — site constraints (immovable "
            "construction dates · plant change windows · remote connectivity · "
            "{TOTAL_DAYS} labour days of known demand against finite PM/BA/IE/SA capacity "
            "· concentrated sponsor attention) &#8594; therefore the enabling platform "
            "layer must be sequenced <b>ahead of</b> the capability initiatives that depend "
            "on it, and OT work must be scheduled to the plant's calendar, not IT's.<br>"
            "<b><font color=\"#8B2E45\">PORTFOLIO CLASSIFICATION</font></b> — "
            "<b>Strategic</b> (formal architecture review, coordinated enterprise "
            "rollout): the platform layer — VMware replacement, data centre storage and "
            "resiliency, identity, zero trust, OT cyber tranches, site WAN. "
            "<b>Operational</b> (hub or site review, may vary by location): plant control "
            "and SCADA, access control, camp CCTV, ground probing radar. <b>Tactical</b> "
            "(solve a local problem, retire when superseded): tool tracker, catering "
            "selection, meeting room and training room refreshes.",
        "rightTitle": "GAPS, DATA QUALITY &amp; NEXT STEPS",
        "right":
            "<b>Source data defect — fix before circulation:</b> in the CSV the High-Level "
            "Summary column is offset against Title across a block of rows, so descriptions "
            "belong to the wrong projects (Vulnerability Management is described as a radio "
            "frequency framework; Spectrum Management Database as fire detection; Onslow IT "
            "Disaster Recovery as an AMS-to-GIS integration). Capability mapping here was "
            "therefore driven by <b>Title only</b>, and the summary text is not used "
            "anywhere on this page.<br>"
            "<b>Data completeness:</b> {N_NO_SPONSOR} of {N} have no sponsor · "
            "{N_NO_AUTHOR} have no author · {N_NO_START} have no estimated start date · "
            "{N_NO_EST} carry no labour estimate. Coverage conclusions are sound; capacity "
            "and sequencing conclusions are not, until estimates exist.<br>"
            "<b>Assumptions to confirm:</b> capability assignment is analyst judgement from "
            "titles, not sponsor-confirmed — Beneficiate versus Exploit for plant "
            "visibility work, and Establish versus Support for camps and villages, are the "
            "two boundaries most likely to be disputed.<br>"
            "<b>Scoped out:</b> Tier 2 Data and Application Architecture and Tier 3 "
            "Technology Architecture; benefit cases, dependencies between initiatives, and "
            "the Complete and Cancelled history ({N_DEAD} rows) that would show delivery "
            "track record.<br>"
            "<b>Next steps:</b> assign a sponsor to every active initiative or retire it; "
            "estimate the {N_NO_EST} unestimated; give every On Hold item a reason, an owner "
            "and a review date; then sequence the platform layer ahead of the capability "
            "work that depends on it.",
    },

    # ---------------------------------------------------------- DP prose
    "dpContext": [
        ["Planning horizon",
         "<b>{HZ_FROM} &#8594; {HZ_TO}</b>, 12 calendar months from the run date. Monthly "
         "buckets. Each initiative's labour is prorated by <b>calendar-day overlap</b> of "
         "its window (start &#8594; start + duration), so work straddling the horizon edge "
         "contributes only the part inside it."],
        ["Scope filter (as requested)",
         "<b>Stage = In Progress or Opportunity</b> only: {N} of {N_LOADED} rows. "
         "<b>{N_EXCL} excluded</b> — On&#160;Hold {X_OH}, Complete {X_CO}, Cancelled "
         "{X_CA}. On&#160;Hold is real latent demand and is <b>not</b> in this profile; "
         "treat it as a queue behind it."],
        ["Unit of demand",
         "<b>Internal delivery labour days by role</b>: PM, BA, IE, CD, SA, Other. "
         "Converted to FTE at <b>21 working days = 1 FTE-month</b> (stated assumption — not "
         "in the source). <b>{NIL_STMT}</b>"],
        ["Supply model",
         "<b>Engineer-to-Order analogue.</b> Each initiative is a bespoke deployment with a "
         "long lead time and site-specific design — SCOR's ETO assumptions hold, but the "
         "scarce input is <b>skilled internal delivery capacity</b>, so lead time is "
         "measured in people-months, not shipping weeks."],
        ["Estimate coverage",
         "<b>{N_EST} of {N}</b> initiatives carry any labour estimate "
         "(<b>{COVERAGE}%</b>), totalling <b>{EST_TOTAL} days</b>. <b><font "
         "color=\"#CE372F\">{N_UNQ} initiatives ({UNCOVERAGE}%) are unquantified</font></b>. "
         "Only <b>{N_TIER_A}</b> carry start + duration + estimate together."],
        ["Sizing basis for the unquantified",
         "Quartiles of the {N_EST} estimated initiatives: <b>Q1 {Q1} d</b> · <b>median {Q2} "
         "d</b> · <b>Q3 {Q3} d</b> (mean {MEAN_EST} d — converges on Q3, so the high case is "
         "not an outlier artefact). These drive the downside / base / upside allowance."],
    ],
    "scenarios": [
        ["Downside", "low case", "q1", "#F0F2E5", "#D9DCBC", "#5E623C"],
        ["Base case", "central", "q2", "#E3F2F4", "#B8DDE3", "#00444C"],
        ["Upside", "high case", "q3", "#F5E5DD", "#E8C4B0", "#8E5239"],
    ],
    "planningRules": [
        ["Rule 1", "Demand admission — no estimate, no place in the plan",
         "<b>Trigger:</b> an initiative reaches Opportunity gate or is set In "
         "Progress.<br><b>Rule:</b> it does not enter the 12-month resource plan without "
         "<b>start date + duration + role-level day estimate</b>. Until all three exist it "
         "sits in the unquantified pool and is planned for by allowance, not by "
         "name.<br><b>Why:</b> {N_UNQ} of {N} in-scope initiatives ({UNCOVERAGE}%) "
         "currently fail this test, which is why the downside-to-upside spread is "
         "<b>{SPREAD}&#215;</b>. Nothing else on this page can be fixed before this one is."],
        ["Rule 2", "Sourcing — make, buy or contract, decided by role and by month",
         "<b>Trigger:</b> monthly demand for a role exceeds confirmed establishment for "
         "<b>two consecutive months</b>.<br><b>Rule:</b> permanent hire only where demand "
         "is sustained beyond the horizon; contract for peaks; vendor-delivered for one-off "
         "deployments with no retained-skill need.<br><b>Why:</b> demand is "
         "<b>role-specific and lumpy</b> — <b>IE at {IE_SHARE}%</b> of estimated demand, "
         "peaking at <b>{IE_PEAK_FTE} FTE</b> in {IE_PEAK_MONTH}. A single blended-FTE "
         "number would hide the only constraint that matters. Establishment must be "
         "supplied before this rule can be evaluated."],
        ["Rule 3", "Levelling &amp; sequencing — protect the peak, sequence the platform",
         "<b>Trigger:</b> base-case demand in any month exceeds the annual average by "
         "<b>&gt;25%</b>.<br><b>Rule:</b> defer discretionary Opportunity work out of the "
         "peak before adding capacity; platform and network work sequences <b>ahead</b> of "
         "the initiatives that depend on it.<br><b>Why:</b> {PEAK_MONTH} peaks at "
         "<b>{PEAK_DAYS} days ({PEAK_FTE} FTE)</b> against a <b>{AVG_DAYS} day ({AVG_FTE} "
         "FTE)</b> average — <b>{PEAK_OVER}% above</b>. The peak is built from two large "
         "programs running concurrently, so levelling is a sequencing decision, not a "
         "hiring one."],
        ["Rule 4", "Commitment — unfunded demand is not committed capacity",
         "<b>Trigger:</b> resource is allocated against an initiative.<br><b>Rule:</b> only "
         "<b>budget-approved</b> initiatives draw on committed capacity. Unfunded work is "
         "planned as <b>contingent demand</b> and released on funding approval, with the "
         "resourcing lead time stated.<br><b>Why:</b> <b>{N_UNFUNDED} of {N}</b> in-scope "
         "initiatives carry no approved budget. Treating them as committed would "
         "over-commit the establishment; treating them as absent would leave no lead time "
         "when funding lands."],
    ],
    "risks": [
        ["R1", "Critical", "Estimate coverage",
         "{UNCOVERAGE}% of in-scope initiatives are unsized. The profile's central estimate "
         "is a parametric allowance, not a forecast.",
         "Estimate the {N_UNQ} unquantified initiatives to role level. Sequence by stage: "
         "In Progress first, then Opportunity by expected gate date."],
        ["R2", "Serious", "Single-initiative concentration",
         "{TOP1} alone is {TOP1_SHARE}% of estimated demand and the top two are "
         "{TOP2_SHARE}%. Its slip or re-scope moves the whole profile.",
         "Re-baseline these two monthly, not quarterly. Treat their estimates as the "
         "profile's primary sensitivity."],
        ["R3", "Serious", "Role bottleneck, not headcount",
         "IE is {IE_SHARE}% of estimated demand, peaking at {IE_PEAK_FTE} FTE. A "
         "headcount-level plan would read as balanced while IE is over-committed.",
         "Plan and report capacity by role, never blended. Confirm IE establishment first."],
        ["R4", "Moderate", "Date and stage integrity",
         "{N_NO_DATE} in-scope initiatives have no start date and {N_NO_DUR} no duration. "
         "{N_OVERRUN} In Progress initiative's estimated window closed before the horizon "
         "opened.",
         "Stage and dates must agree. Re-date or re-stage on exception; make it a gate "
         "check."],
        ["R5", "Moderate", "Back-half blindness",
         "Estimated demand reaches zero from {ZERO_MONTH}. Any real work in the back half "
         "of the horizon is invisible, so late-year over-commitment cannot be detected.",
         "Require indicative dates on Opportunity work at gate, even at low confidence, and "
         "re-forecast the profile monthly."],
    ],
    "kpis": [
        ["Estimate coverage", "{COVERAGE}%", "target &#8805;80%", "#CE372F",
         "{N_EST} of {N} sized. <b>Leading indicator</b> — nothing else is trustworthy "
         "below this."],
        ["Scenario spread", "{SPREAD}&#215;", "target &#8804;1.5&#215;", "#CE372F",
         "Downside to upside range. Collapses as coverage rises."],
        ["Peak-to-average", "{PEAK_OVER}%", "target &#8804;25%", "#8E5239",
         "{PEAK_MONTH} peak vs annual average. Levelling KPI."],
        ["Role concentration", "{IE_SHARE}%", "watch", "#8E5239",
         "IE share of estimated demand. Flags the binding constraint."],
        ["Schedule integrity", "{SCHED_PCT}%", "target 100%", "#8E5239",
         "{N_WITH_DATE} of {N} carry a start date."],
        ["Funded share", "{FUNDED_PCT}%", "context", "#00444C",
         "Budget-approved share — separates committed from contingent demand."],
    ],
    "dpFooter":
        "<b>Method.</b> {N_LOADED} rows read; Stage filtered to In Progress and Opportunity "
        "per the request ({N} in scope, {N_EXCL} excluded). Labour days per role prorated "
        "onto calendar months by day-overlap of each initiative's window (start &#8594; "
        "start + duration months). Tier B (start, no duration) uses the portfolio-median "
        "duration of <b>{MED_DUR} months</b>; Tier C (no start) is placed from horizon month "
        "1. Unquantified initiatives are sized at the Q1 / median / Q3 of the {N_EST} "
        "estimated initiatives and spread evenly, because no dates exist. FTE at <b>21 days "
        "per FTE-month</b>. Series colours were chosen by running the dataviz validator over "
        "the MinRes brand ramps — CVD separation &#916;E&#160;16.1 on the adjacent pairlist; "
        "the brand's low chroma fails that check and is relieved by direct labels plus the "
        "full table above.<br>"
        "<b>Assumptions to confirm:</b> even in-month spread of each initiative's labour "
        "(real profiles ramp and taper); even spread of the allowance across the horizon; "
        "median duration applied to Tier B and C; 21 working days per FTE-month; and that "
        "the unquantified pool resembles the estimated sample. The <b>Q3 allowance is the "
        "more realistic central case</b> if it does, because the pool holds several large "
        "infrastructure and cyber programs while the median is dragged down by small "
        "studies.<br>"
        "<b>What is not here.</b> <b>On Hold ({X_OH}) is excluded by the requested "
        "filter</b> and is real latent demand — a queue immediately behind this profile. No "
        "team establishment or available capacity (not in the source), so <b>no gap is "
        "calculated</b> and the capacity columns are deliberately blank. No dependencies "
        "between initiatives, no benefit cases, no cost, no non-labour demand (equipment, "
        "vendor, capital), no external SCOR processes (Source / Make / Deliver / Return), "
        "and no delivery track record from the {N_DEAD_DP} Complete and Cancelled rows.<br>"
        "<b>Next steps, in order.</b> 1&#160;Estimate the {N_UNQ} unquantified initiatives "
        "to role level — In Progress first. 2&#160;Supply the role establishment so a gap "
        "and a sourcing decision become possible. 3&#160;Give every in-scope initiative a "
        "start date and duration; re-stage or re-date the {N_OVERRUN} whose window has "
        "already closed. 4&#160;Level the {PEAK_MONTH} peak by sequencing, before "
        "considering capacity. 5&#160;Re-cut this page monthly and track estimate coverage "
        "as the leading KPI.",

    # ---------------------------------------------------------- traceability overlay
    # Sub-category groupings and ID ranges as they appear in the FRS Functional
    # Requirements sheet. status: full | partial (mock boundary stated in `note`).
    "traceability": [
        ["Brand and Rendering Conformance", "Colour Vision Safety", "FR-001..FR-003",
         "full", "Direct labels on every chart segment, texture difference on the "
         "allowance series, and the full month-by-role table as the relief."],
        ["Brand and Rendering Conformance", "Stage Colour Semantics", "FR-004..FR-006",
         "full", "Teal In Progress, Brown Opportunity, Coral On Hold; severity colours "
         "held distinct from stage colours."],
        ["Brand and Rendering Conformance", "Typeface and Colour Palette", "FR-007..FR-010",
         "full", "Century Gothic with the documented Avenir fallback; MinRes Red reserved "
         "for titles, alerts and accents and never used as a data fill."],
        ["Business Architecture View", "Capability Coverage Band", "FR-011..FR-013",
         "full", ""],
        ["Business Architecture View", "Enabling Platform Band", "FR-014..FR-015",
         "full", ""],
        ["Business Architecture View", "Health Measures and Footer", "FR-016..FR-019",
         "full", ""],
        ["Business Architecture View", "Initiative Chips", "FR-020..FR-026", "full", ""],
        ["Business Architecture View", "Page Structure and Legend", "FR-027..FR-032",
         "full", ""],
        ["Business Architecture View", "Site Realities and Governance Bands",
         "FR-033..FR-035", "full", ""],
        ["Business Architecture View", "Strategy and Driver Band", "FR-036..FR-038",
         "full", ""],
        ["Demand Profile View", "Allowance Pool", "FR-039..FR-043", "full", ""],
        ["Demand Profile View", "Demand Forecast Chart", "FR-044..FR-051", "full", ""],
        ["Demand Profile View", "Estimate Tiering", "FR-052..FR-057", "full", ""],
        ["Demand Profile View", "Initiative Register", "FR-058..FR-061", "full", ""],
        ["Demand Profile View", "Monthly Proration", "FR-062..FR-066", "full", ""],
        ["Demand Profile View", "Planning Business Rules", "FR-067..FR-072", "full", ""],
        ["Demand Profile View", "Planning Horizon", "FR-073..FR-077", "full", ""],
        ["Demand Profile View", "Risk and Measure Panels", "FR-078..FR-082", "full", ""],
        ["Demand Profile View", "Role Capacity Table", "FR-083..FR-085", "full", ""],
        ["Demand Profile View", "Scenario Panel", "FR-086..FR-089", "full", ""],
        ["Output Generation", "File Writing and Naming", "FR-090..FR-094", "partial",
         "The dialog composes and shows the generated file names, but writes nothing. "
         "Deferred to build."],
        ["Output Generation", "Print and Page Rendition", "FR-095..FR-099", "partial",
         "The A2 landscape print stylesheet is applied and interactive chrome drops, but "
         "one-page pagination is not verified in a mock-up."],
        ["Output Generation", "Provenance Stamping", "FR-100..FR-103", "full",
         "The stamp is composed from the live model and previewed in full."],
        ["Output Generation", "Self Contained Packaging", "FR-104..FR-107", "full",
         "This file is the proof: one HTML file, no external asset, inline SVG only."],
        ["Portfolio Classification", "Capability Mapping", "FR-108..FR-113", "full", ""],
        ["Portfolio Classification", "Mapping Assurance", "FR-114..FR-119", "full",
         "Unmapped, double-mapped, stale and retired mappings all reported in "
         "Diagnostics."],
        ["Portfolio Classification", "Platform Layer Grouping", "FR-120..FR-122",
         "full", ""],
        ["Portfolio Classification", "Stage Scope Sets", "FR-123..FR-126", "full", ""],
        ["Source Data Ingestion", "Defect Detection and Reporting", "FR-127..FR-134",
         "full", "Counts and the titles behind them, in Diagnostics."],
        ["Source Data Ingestion", "File Selection and Loading", "FR-135..FR-142", "partial",
         "The picker and drop target are present and the parse is reported, but they read "
         "the embedded snapshot rather than a chosen file."],
        ["Source Data Ingestion", "Record Parsing and Field Mapping", "FR-143..FR-148",
         "full", "Including the named halt when a required column is absent — see "
         "Diagnostics, Simulate load error."],
        ["Source Data Ingestion", "Value Normalisation", "FR-149..FR-156", "full",
         "Trim, en-dash restoration with a substitution count, Budget Yes/other, and "
         "summary text never used for classification."],
        ["View Interaction", "Drill-down Inspection", "FR-157..FR-161", "full", ""],
        ["View Interaction", "Filter Controls", "FR-162..FR-167", "full", ""],
        ["View Interaction", "Filter State Disclosure", "FR-168..FR-171", "full", ""],
        ["View Interaction", "Hover Detail", "FR-172..FR-175", "full", ""],
        ["View Interaction", "Live Recalculation", "FR-176..FR-179", "full", ""],
        ["View Interaction", "Sorting and Ranking", "FR-180..FR-183", "full", ""],
    ],
}

# ================================================================ section 1 — <style>
# NFR-018: one :root token block is the single configuration surface for presentation.
# Brand authority: .claude/rules/MINRES_Content_Guidelines.html
# Print rules last (FR-095..FR-099).
CSS = r"""
:root{
  /* --- MinRes brand ------------------------------------------------------ */
  --cg:'Century Gothic','Avenir',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;
  --red:#CE372F;          /* titles, accents, focus ring ONLY — never a data fill */
  --red-ink:#A82A23;      /* the same alert, darkened for small text on a tinted fill */
  --teal:#00444C;         /* band headings */
  --teal-2:#2D686F;
  --ink:#000000;
  --grey:#5C5C5C;
  --rule:#D1D1D1;
  --surf:#F1EDE7;         /* Brown 100 */
  --surf2:#E8E8E8;
  --white:#FFFFFF;

  /* --- stage families (FR-004..FR-006) ----------------------------------
     line and bar clear 3:1 on white as graphical objects; ink clears 4.5:1 on
     its own fill. The fills sit within 1.1:1 of the page, so the chip is only
     identifiable by its border and that border carries the burden (NFR-039). */
  --ip-fill:#E0F7F9; --ip-line:#1F97A6; --ip-ink:#166D78; --ip-bar:#1A8D9B;
  --op-fill:#F1EDE7; --op-line:#A58D62; --op-ink:#6B5435; --op-bar:#967E55;
  --oh-fill:#F5E5DD; --oh-line:#C37556; --oh-ink:#8E5239; --oh-bar:#B2694C;

  /* --- domain families (IT / OT / converged) ---------------------------- */
  --it-fill:#E0F7F9; --it-line:#1F97A6; --it-ink:#166D78; --it-bar:#1A8D9B;
  --ot-fill:#F5E5DD; --ot-line:#C37556; --ot-ink:#8E5239; --ot-bar:#B2694C;
  --cv-fill:#F4D9DD; --cv-line:#CE6B7C; --cv-ink:#8B2E45; --cv-bar:#C5556B;

  /* --- severity, held distinct from stage colours (FR-006) -------------- */
  --sev-crit-fill:#F4D9DD; --sev-crit-line:#E8A5AD; --sev-crit-ink:#8B2E45;
  --sev-ser-fill:#F5E5DD;  --sev-ser-line:#E8C4B0;  --sev-ser-ink:#8E5239;
  --sev-mod-fill:#F1EDE7;  --sev-mod-line:#D9CDB8;  --sev-mod-ink:#6B5435;

  /* --- canvas ----------------------------------------------------------- */
  --page-w:2245px; --page-h:1587px; --page-margin:24px;

  /* --- shell chrome ----------------------------------------------------- */
  --chrome-bg:#FAFAFA; --chrome-line:#D1D1D1; --chrome-ink:#000000;
  --rail-w:246px;
  --mock:#8B2E45;         /* the badge colour for anything not real */
}

*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:var(--cg); color:var(--ink); background:#EDEDED;
  font-size:13px; line-height:1.5; -webkit-font-smoothing:antialiased;
}
button,select,input{font-family:var(--cg); font-size:12px; color:var(--ink)}
button{cursor:pointer; background:var(--white); border:1px solid var(--chrome-line);
  border-radius:2px; padding:4px 10px}
button:hover{background:var(--surf)}
button:focus-visible,select:focus-visible,input:focus-visible,
[tabindex]:focus-visible{outline:2px solid var(--red); outline-offset:1px}
a{color:var(--teal)}
.hide{display:none !important}
.mono{font-variant-numeric:tabular-nums}

/* ---------------------------------------------------------------- ribbon */
#ribbon{
  background:var(--mock); color:#fff; padding:5px 14px; font-size:11.5px;
  letter-spacing:.06em; display:flex; gap:16px; align-items:baseline;
}
#ribbon b{letter-spacing:.12em}
#ribbon span{opacity:.92; letter-spacing:0}

/* -------------------------------------------------------------- file bar */
#filebar{
  background:var(--white); border-bottom:1px solid var(--chrome-line);
  padding:7px 14px; display:flex; gap:18px; align-items:center; flex-wrap:wrap;
  font-size:11.5px;
}
#filebar .fname{font-weight:bold; font-size:12.5px}
#filebar .sep{color:var(--rule)}
.sensitivity{
  border:1px solid var(--red); color:var(--red); font-weight:bold;
  padding:1px 6px; font-size:10.5px; letter-spacing:.08em; border-radius:2px;
}
.badge-mock{
  background:var(--mock); color:#fff; font-size:9.5px; font-weight:bold;
  letter-spacing:.09em; padding:1px 5px; border-radius:2px; vertical-align:2px;
}

/* ------------------------------------------------------------- tab strip */
#tabs{
  background:var(--white); border-bottom:1px solid var(--chrome-line);
  padding:0 14px; display:flex; gap:2px; align-items:stretch; flex-wrap:wrap;
}
#tabs .tab{
  border:none; border-bottom:3px solid transparent; background:none;
  padding:9px 16px; font-size:13px; border-radius:0;
}
#tabs .tab[aria-selected="true"]{
  border-bottom-color:var(--red); font-weight:bold; color:var(--teal);
}
#tabs .spacer{flex:1}
#tabs .tools{display:flex; gap:8px; align-items:center; padding:5px 0}
#tabs label{font-size:11.5px; display:flex; gap:5px; align-items:center}

/* ---------------------------------------------------------------- banner */
#banner{
  background:var(--surf); border-bottom:1px solid var(--chrome-line);
  padding:6px 14px; font-size:11.5px; display:flex; gap:10px;
  align-items:baseline; flex-wrap:wrap;
}
#banner .lead{font-weight:bold; color:var(--teal)}
#banner .chip{
  background:var(--white); border:1px solid var(--op-line); border-radius:2px;
  padding:1px 6px;
}
#banner .warn{
  background:var(--sev-crit-fill); border:1px solid var(--red); color:var(--sev-crit-ink);
  font-weight:bold; padding:1px 7px; border-radius:2px;
}
#banner .sortnote{color:var(--grey)}

/* ------------------------------------------------------------------ body */
#body{display:flex; align-items:stretch; min-height:calc(100vh - 132px)}
#rail{
  width:var(--rail-w); min-width:var(--rail-w); background:var(--white);
  border-right:1px solid var(--chrome-line); padding:10px 12px 30px;
  overflow-y:auto; max-height:calc(100vh - 132px);
}
#rail h3{
  font-size:11px; letter-spacing:.09em; color:var(--teal); margin:14px 0 6px;
  border-bottom:1px solid var(--rule); padding-bottom:3px; text-transform:uppercase;
}
#rail h3:first-child{margin-top:2px}
#rail label{display:block; font-size:10.5px; color:var(--grey); margin:7px 0 2px}
#rail select,#rail input[type=text]{
  width:100%; padding:3px 4px; border:1px solid var(--chrome-line); border-radius:2px;
  background:var(--white);
}
#rail select[multiple]{height:auto; min-height:64px}
#rail .row{display:flex; gap:6px; margin-top:12px}
#rail .row button{flex:1}
#rail .count{font-size:10.5px; color:var(--grey); margin-top:3px}
.railwarn{color:var(--red); font-weight:bold}

#stage{flex:1; overflow:auto; padding:14px; max-height:calc(100vh - 132px)}

/* ------------------------------------------------------- screen-only layout */
/* The height of the chrome above the canvas is measured by the browser rather than
   hardcoded: the shell is a flex column and the stage takes whatever is left. Hiding the
   ribbon and the file bar therefore hands that height straight to the canvas, and there is
   no calc() to keep in step with the chrome. Scoped to screen so the print path keeps
   ordinary block flow and its page breaks. The filter rail is untouched. */
@media screen{
  html,body{height:100%}
  /* the document itself does not scroll: the stage does, so the chrome and the filter rail
     stay put while the page is panned */
  body{display:flex; flex-direction:column; height:100vh; overflow:hidden}
  #ribbon,#filebar,#tabs,#banner{flex:0 0 auto}
  #loadscreen,#errorscreen{flex:1 1 auto; overflow:auto}
  #shell{display:flex; flex-direction:column; flex:1 1 auto; min-height:0}
  #body{flex:1 1 auto; min-height:0}
  #rail,#stage{max-height:none; min-height:0}
  /* FR-134 reading aid: the two rows of review chrome fold away, nothing is redesigned */
  body.maxcanvas #ribbon,body.maxcanvas #filebar{display:none}
  body.maxcanvas #stage{padding:5px}
}

/* ---------------------------------------------------------------- canvas */
/* The scale sits on .canvas, not on the wrap: the wrap is then free to carry the SCALED
   size as its layout box, so the checklist below it follows the visible bottom edge of the
   page and the stage scrolls exactly the visible width. Scaling the wrap while also
   writing the scaled size onto it would square the factor and over-reserve above 100%. */
.canvas-wrap{
  width:var(--page-w); height:var(--page-h);
  margin:0 auto; position:relative;
}
.canvas{
  position:relative; width:var(--page-w); height:var(--page-h);
  transform-origin:top left;
  background:var(--white); box-shadow:0 1px 6px rgba(0,0,0,.22); overflow:hidden;
}
.canvas .abs{position:absolute; overflow:hidden}
/* every glyph size below is the coordinate from the authority draw.io scripts */
.pt{font-size:8px; line-height:1.28}
.ptx{font-size:7.2px; line-height:1.3}
.pxs{font-size:6.4px; line-height:1.3}
.band{
  background:var(--teal); color:#fff; font-size:11px; font-weight:bold;
  letter-spacing:.1em; padding:5px 8px 4px 14px;
}
.band .note{
  float:right; font-weight:normal; letter-spacing:.02em; font-size:8.6px;
  opacity:.9; padding-top:2px;
}
.bandtab{background:var(--red)}
.box{border:1px solid; padding:6px 7px}
.boxhead{font-weight:bold; font-size:8.4px; letter-spacing:.03em}
.chip{border:1px solid; position:absolute; cursor:pointer}
.chip .bar{position:absolute; left:0; top:0; bottom:0; width:3px}
.chip .t{
  position:absolute; left:8px; top:3px; right:158px; font-size:7.5px;
  font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.chip .m{
  position:absolute; left:8px; top:16px; right:158px; font-size:6.3px;
  color:var(--grey); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.chip .a{
  position:absolute; right:5px; top:14px; width:150px; text-align:right;
  font-size:6.3px; color:var(--grey); white-space:nowrap; overflow:hidden;
}
/* the darker red, because this text is 6.3px bold on a tinted fill, not a title on white */
.chip .alert{color:var(--red-ink); font-weight:bold}
.chip.sel{outline:2px solid var(--red); outline-offset:-2px}
.thin{border-width:2px !important; border-color:var(--red) !important}
.arrow{position:absolute}
.pagetitle{font-size:20px; font-weight:bold; color:var(--red)}
.pagesub{font-size:9px; color:var(--grey)}
.stamp{font-size:6.6px; color:var(--grey); line-height:1.35}
.tbl{border-collapse:collapse; width:100%; font-size:6.6px}
.tbl th{
  text-align:left; font-size:6.4px; letter-spacing:.04em; color:var(--teal);
  border-bottom:1px solid var(--rule); padding:2px 4px 2px 0; white-space:nowrap;
  cursor:pointer; user-select:none;
}
.tbl th .ind{color:var(--red); font-weight:bold}
.tbl td{border-bottom:1px solid #EFEFEF; padding:1.5px 4px 1.5px 0; vertical-align:top}
.tbl td.n{text-align:right; font-variant-numeric:tabular-nums}
.tbl tr.hot:hover td{background:var(--surf)}
.tbl tr.hot{cursor:pointer}
.blankcol{color:#B9B9B9}
.chartsvg{position:absolute; left:0; overflow:visible}
.chartsvg text{font-family:var(--cg)}
.chartsvg .seg{cursor:pointer}
.chartsvg .seg:hover{filter:brightness(.93)}

/* ----------------------------------------------------------- load screen */
#loadscreen,#errorscreen{padding:56px 24px; display:flex; justify-content:center}
.loadcard{
  background:var(--white); border:1px solid var(--chrome-line); max-width:760px;
  width:100%; padding:30px 34px 34px; box-shadow:0 1px 6px rgba(0,0,0,.14);
}
.loadcard h1{font-size:26px; color:var(--red); margin:0 0 4px; font-weight:bold}
.loadcard h2{font-size:15px; color:var(--teal); margin:0 0 20px; font-weight:bold}
.loadcard p{font-size:12.5px; margin:0 0 12px}
.loadcard .small{font-size:11px; color:var(--grey)}
.droptarget{
  border:2px dashed var(--op-line); background:var(--surf); padding:26px;
  text-align:center; margin:18px 0; font-size:12.5px;
}
.droptarget.over{border-color:var(--red); background:#FBF2F1}
.loadcard .primary{
  background:var(--teal); color:#fff; border-color:var(--teal); font-size:13px;
  padding:7px 16px;
}
.loadcard .primary:hover{background:#00363D}
.parsereport{
  background:var(--surf); border-left:3px solid var(--teal); padding:10px 12px;
  font-size:11.5px; margin-top:16px;
}
.parsereport b{color:var(--teal)}
#errorscreen .loadcard{border-top:4px solid var(--red)}
#errorscreen h1{color:var(--red)}
.errfield{
  background:var(--sev-crit-fill); border:1px solid var(--sev-crit-line);
  padding:10px 12px; font-size:12px; margin:14px 0;
}

/* --------------------------------------------------------- drawer, modal */
#scrim{
  position:fixed; inset:0; background:rgba(0,0,0,.34); z-index:40;
}
#drawer{
  position:fixed; top:0; right:0; bottom:0; width:660px; max-width:94vw;
  background:var(--white); z-index:50; box-shadow:-2px 0 14px rgba(0,0,0,.3);
  display:flex; flex-direction:column;
}
#drawer .dhead{
  border-bottom:1px solid var(--chrome-line); padding:12px 16px;
  display:flex; gap:12px; align-items:flex-start;
}
#drawer .dhead h2{margin:0; font-size:16px; color:var(--teal); flex:1}
#drawer .dbody{overflow:auto; padding:14px 16px 40px}
.dstage{
  display:inline-block; font-size:10.5px; font-weight:bold; padding:1px 7px;
  border:1px solid; border-radius:2px;
}
.twocol{display:grid; grid-template-columns:1fr 1fr; gap:18px}
.dsec h4{
  font-size:10.5px; letter-spacing:.09em; color:var(--teal); margin:16px 0 6px;
  border-bottom:1px solid var(--rule); padding-bottom:3px; text-transform:uppercase;
}
.kv{width:100%; border-collapse:collapse; font-size:11.5px}
.kv th{
  text-align:left; font-weight:normal; color:var(--grey); padding:2px 8px 2px 0;
  width:44%; vertical-align:top;
}
.kv td{padding:2px 0; vertical-align:top}
.kv td.miss{color:var(--red); font-weight:bold}
.unverified{
  background:var(--sev-mod-fill); border-left:3px solid var(--sev-mod-ink);
  padding:8px 10px; font-size:11.5px;
}
.unverified .tag{
  color:var(--sev-mod-ink); font-weight:bold; font-style:italic; display:block;
  margin-bottom:4px; font-size:10.5px;
}
.modal{
  position:fixed; top:5vh; left:50%; transform:translateX(-50%); width:1020px;
  max-width:94vw; max-height:88vh; background:var(--white); z-index:50;
  box-shadow:0 3px 20px rgba(0,0,0,.34); display:flex; flex-direction:column;
}
.modal .mhead{
  border-bottom:1px solid var(--chrome-line); padding:12px 16px; display:flex;
  gap:12px; align-items:center;
}
.modal .mhead h2{margin:0; font-size:16px; color:var(--teal); flex:1}
.modal .mbody{overflow:auto; padding:14px 16px 26px}
.modal .mfoot{
  border-top:1px solid var(--chrome-line); padding:10px 16px; display:flex;
  gap:10px; justify-content:flex-end; align-items:center;
}
.diagtbl{width:100%; border-collapse:collapse; font-size:11.5px}
.diagtbl th{
  text-align:left; color:var(--teal); font-size:10.5px; letter-spacing:.05em;
  border-bottom:1px solid var(--rule); padding:3px 8px 3px 0;
}
.diagtbl td{border-bottom:1px solid #F0F0F0; padding:3px 8px 3px 0; vertical-align:top}
.diagtbl td.n{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}
details.dq{margin:4px 0}
details.dq summary{cursor:pointer; font-size:11.5px}
details.dq ul{margin:5px 0 10px 18px; font-size:11px; color:var(--grey)}
.warnlist li{margin-bottom:4px}
.stampbox{
  background:var(--surf); border:1px solid var(--op-line); padding:12px 14px;
  font-size:11px; line-height:1.6; white-space:pre-wrap;
}
.genrow{display:flex; gap:14px; align-items:center; margin:10px 0}
.genfile{
  font-weight:bold; color:var(--teal); font-size:12px;
}

/* --------------------------------------------------- tooltip (hover FR-172) */
#tip{
  position:fixed; z-index:60; max-width:420px; background:#1C1C1C; color:#fff;
  font-size:11.5px; line-height:1.5; padding:8px 11px; border-radius:3px;
  box-shadow:0 2px 10px rgba(0,0,0,.4); pointer-events:none;
}
#tip .tt{font-weight:bold; margin-bottom:3px}
#tip .tr{color:#D9D9D9}
#tip .tr b{color:#fff}
#tip .tk{color:#F0B7B3}

/* ------------------------------------------- annotation overlay (screen J) */
.frbadge{
  position:absolute; z-index:9; background:var(--mock); color:#fff;
  font-size:7px; font-weight:bold; letter-spacing:.04em; padding:0 3px;
  border-radius:2px; white-space:nowrap; cursor:help; top:0; right:0;
}
body:not(.annot) .frbadge{display:none}
body.annot [data-fr]{outline:1px dashed rgba(139,46,69,.55); outline-offset:-1px}
#coverage{
  max-width:var(--page-w); margin:16px auto 40px; background:var(--white);
  border:1px solid var(--chrome-line); padding:16px 20px 22px;
}
#coverage h2{font-size:15px; color:var(--teal); margin:0 0 3px}
#coverage .sub{font-size:11.5px; color:var(--grey); margin-bottom:12px}
#coverage table{width:100%; border-collapse:collapse; font-size:11.5px}
#coverage th{
  text-align:left; color:var(--teal); font-size:10.5px; letter-spacing:.05em;
  border-bottom:1px solid var(--rule); padding:3px 10px 3px 0;
}
#coverage td{border-bottom:1px solid #F0F0F0; padding:3px 10px 3px 0; vertical-align:top}
#coverage .ok{color:var(--teal); font-weight:bold; white-space:nowrap}
#coverage .part{color:var(--mock); font-weight:bold; white-space:nowrap}
.tally{display:flex; gap:26px; margin-bottom:14px; flex-wrap:wrap}
.tally div{font-size:11.5px}
.tally b{display:block; font-size:22px; color:var(--teal); font-weight:bold}
.tally .p b{color:var(--mock)}

/* =========================================================== print rules */
/* FR-095..FR-099: A2 landscape, one page per view, interactive chrome drops,
   the filter statement stays so a printed page cannot misrepresent its scope. */
@page{size:594mm 420mm; margin:0}
@media print{
  body{background:#fff}
  #ribbon,#filebar,#tabs,#rail,#drawer,#scrim,.modal,#tip,#coverage,
  #loadscreen,#errorscreen{display:none !important}
  #body{display:block; min-height:0}
  #stage{padding:0; overflow:visible; max-height:none}
  #banner{
    border:none; background:#fff; padding:2px 24px; font-size:9px;
    page-break-after:avoid;
  }
  #banner .warn{border-color:#000; color:#000; background:#fff}
  /* the reading scale is an on-screen device only; print is always true A2 */
  .canvas-wrap{
    width:var(--page-w) !important; height:var(--page-h) !important; margin:0;
  }
  .canvas{transform:none !important}
  .canvas{box-shadow:none; page-break-after:always; break-after:page}
  .canvas:last-of-type{page-break-after:auto; break-after:auto}
  .frbadge{display:none !important}
  *{-webkit-print-color-adjust:exact; print-color-adjust:exact}
}
"""

# ================================================================ HTML skeleton
# Screens A (first load), B (load error) and C (client shell) are all in this one
# document; the chrome switches between them. Nothing here is source-derived, so it is
# authored markup; every value that comes from the extract is written by JS via
# textContent (NFR-037).
BODY = r"""
<div id="ribbon">
  <b>MOCK-UP FOR UI REVIEW</b>
  <span>Not a working client. <b>File selection</b> reads an embedded snapshot of the real
  extract, not a chosen file. <b>Generate</b> writes nothing. <b>Print</b> applies the A2
  stylesheet but pagination is not verified. Everything else &mdash; filters, sorting,
  hover, drill-down and every derived figure &mdash; is live.</span>
</div>

<div id="filebar">
  <span class="fname" id="fb-name">&mdash;</span>
  <span class="sep">|</span>
  <span>last modified <b id="fb-mod">&mdash;</b></span>
  <span class="sep">|</span>
  <span><b id="fb-recs">0</b> records loaded</span>
  <span class="sep">|</span>
  <span>client <b id="fb-ver">&mdash;</b></span>
  <span class="sep">|</span>
  <span class="sensitivity" id="fb-sens">&mdash;</span>
  <span style="flex:1"></span>
  <button id="btn-reload" type="button">Load replacement extract&hellip;
    <span class="badge-mock">MOCK</span></button>
</div>

<!-- ================================================== screen A: first load -->
<div id="loadscreen">
  <div class="loadcard">
    <h1>Projects Pipeline Desktop Client</h1>
    <h2>Short-term pipeline briefing &mdash; Business Architecture and Demand Profile</h2>
    <p>Select the pipeline extract to begin. The client runs entirely on this workstation:
      the file is read in the browser, nothing is uploaded, and no network request is made
      at any point.</p>
    <p class="small">Expected format: comma-separated values, UTF-8 encoding, byte-order
      mark tolerated, one header row, 14 named columns. Quoted multi-line cells are
      supported.</p>

    <div class="droptarget" id="drop">
      Drag the extract here <span class="badge-mock">MOCK</span>
      <div class="small" style="margin-top:6px">or</div>
      <div style="margin-top:10px">
        <button class="primary" id="btn-choose" type="button">Choose extract&hellip;</button>
        <span class="badge-mock">MOCK</span>
      </div>
    </div>

    <p class="small">In this mock-up both controls parse the embedded snapshot of
      <b id="ls-name">the extract</b> so that the review runs against real records.</p>

    <div class="parsereport hide" id="ls-report"></div>
  </div>
</div>

<!-- ============================================== screen B: named load error -->
<div id="errorscreen" class="hide">
  <div class="loadcard">
    <h1>The extract could not be read</h1>
    <h2>No data has been loaded, and nothing has been changed</h2>
    <p id="err-lead"></p>
    <div class="errfield" id="err-detail"></div>
    <p id="err-remedy"></p>
    <p class="small">This message is deliberately written in business language and names
      the column, the file and the remedy. The client raises no technical exception text at
      the reviewer (NFR-040).</p>
    <div style="margin-top:18px">
      <button class="primary" id="btn-err-back" type="button">Back to file
        selection</button>
    </div>
  </div>
</div>

<!-- ================================================= screen C: client shell -->
<div id="shell" class="hide">
  <div id="tabs">
    <button class="tab" id="tab-ba" type="button" role="tab" aria-selected="true">
      Business Architecture</button>
    <button class="tab" id="tab-dp" type="button" role="tab" aria-selected="false">
      Demand Profile</button>
    <span class="spacer"></span>
    <div class="tools">
      <label for="zoom">Zoom</label>
      <select id="zoom">
        <option value="fit">Fit to window</option>
        <option value="0.75">75%</option>
        <option value="1">100% (true print size)</option>
        <option value="1.25">125%</option>
        <option value="1.5" selected>150% &mdash; readable</option>
        <option value="1.75">175%</option>
        <option value="2">200%</option>
      </select>
      <button id="btn-max" type="button" aria-pressed="false">Maximise canvas</button>
      <label><input type="checkbox" id="chk-annot"> Show requirement IDs</label>
      <label><input type="checkbox" id="chk-fixdate"> Fixed run date</label>
      <button id="btn-diag" type="button">Diagnostics</button>
      <button id="btn-gen" type="button">Generate&hellip;</button>
      <button id="btn-print" type="button">Print</button>
    </div>
  </div>

  <div id="banner"></div>

  <div id="body">
    <div id="rail"></div>
    <div id="stage">
      <div class="canvas-wrap" id="wrap-ba"><div class="canvas" id="canvas-ba"></div></div>
      <div class="canvas-wrap hide" id="wrap-dp"><div class="canvas" id="canvas-dp"></div>
      </div>
      <div id="coverage" class="hide"></div>
    </div>
  </div>
</div>

<!-- ============================== screens F/G: drill-down drawer, and modals -->
<div id="scrim" class="hide"></div>
<div id="drawer" class="hide" role="dialog" aria-modal="true" aria-label="Detail">
  <div class="dhead">
    <div style="flex:1">
      <h2 id="dw-title">&mdash;</h2>
      <div id="dw-sub" style="font-size:11.5px;color:var(--grey);margin-top:3px"></div>
    </div>
    <button id="dw-close" type="button" aria-label="Close">Close &times;</button>
  </div>
  <div class="dbody" id="dw-body"></div>
</div>

<div class="modal hide" id="modal-diag" role="dialog" aria-modal="true"
     aria-label="Diagnostics">
  <div class="mhead"><h2>Diagnostics</h2>
    <button id="dg-err" type="button">Simulate load error</button>
    <button id="dg-close" type="button" aria-label="Close">Close &times;</button></div>
  <div class="mbody" id="dg-body"></div>
</div>

<div class="modal hide" id="modal-gen" role="dialog" aria-modal="true"
     aria-label="Generate output">
  <div class="mhead"><h2>Generate briefing files</h2>
    <button id="gn-close" type="button" aria-label="Close">Close &times;</button></div>
  <div class="mbody" id="gn-body"></div>
  <div class="mfoot">
    <span class="badge-mock">MOCK &mdash; no file is written</span>
    <button id="gn-cancel" type="button">Cancel</button>
    <button id="gn-go" class="primary" type="button" style="background:var(--teal);
      color:#fff;border-color:var(--teal)">Generate</button>
  </div>
</div>

<div id="tip" class="hide" role="tooltip"></div>
"""

# ================================================================ section 4 — derive.js
# Pure functions, each defined once (NFR-017). Rounding happens only in fmt() (NFR-014).
# No Date.now() inside the derivation itself: the run date is passed in, so the same
# extract and the same run date always produce the same model (NFR-029).
JS_DERIVE = r"""
/* ============================================================== primitives */
var ROLES = CONFIG.roles;
var MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
var DPM = CONFIG.meta.daysPerFteMonth;

/* FR-149..FR-151 value normalisation. U+FFFD is the mojibake left where an en dash was
   written in a non-UTF-8 editor; restore it and count the substitutions so the reviewer
   can see the extract was repaired rather than silently altered. */
function clean(s){
  if(s===null||s===undefined) return '';
  return String(s).replace(/�/g,'–').replace(/\s+$/,'').replace(/^\s+/,'');
}
function fffd(s){ var m=String(s||'').match(/�/g); return m?m.length:0; }
function deent(s){
  return String(s||'').replace(/&amp;/g,'&').replace(/&#160;/g,' ')
    .replace(/&#8594;/g,'→').replace(/&#8805;/g,'≥')
    .replace(/&#8804;/g,'≤').replace(/&#215;/g,'×');
}
function esc(s){
  return String(s===null||s===undefined?'':s).replace(/&/g,'&amp;')
    .replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
/* the ONLY place a number is rounded for display (NFR-014) */
function fmt(v,dp){
  if(v===null||v===undefined||isNaN(v)) return '—';
  dp = (dp===undefined)?1:dp;
  var s = Number(v).toFixed(dp);
  if(dp>0 && s.indexOf('.')>=0) s = s.replace(/0+$/,'').replace(/\.$/,'');
  return s;
}
function fmt0(v){ return fmt(v,0); }
function pct(a,b,dp){ return (!b) ? '0' : fmt(a/b*100, dp===undefined?1:dp); }

/* UTC-only date arithmetic, so the model cannot shift with a timezone (NFR-029) */
function mkd(y,m,d){ return new Date(Date.UTC(y,m,d)); }
function dnum(s){
  var m = String(s||'').match(/^\s*(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})/);
  if(!m) return null;
  var d=+m[1], mo=+m[2], y=+m[3];
  if(y<100) y += 2000;
  if(mo<1||mo>12||d<1||d>31) return null;
  var dt = mkd(y,mo-1,d);
  if(dt.getUTCMonth()!==mo-1) return null;   /* 31 Feb and friends */
  return dt;
}
function addMonths(d,n){
  var m = d.getUTCMonth()+n, y = d.getUTCFullYear()+Math.floor(m/12);
  m = ((m%12)+12)%12;
  var dim = new Date(Date.UTC(y,m+1,0)).getUTCDate();
  return mkd(y,m,Math.min(d.getUTCDate(),dim));
}
function days(a,b){ return Math.round((b-a)/86400000); }
function shortDate(d){ return d ? MON[d.getUTCMonth()]+' '+
  String(d.getUTCFullYear()).slice(2) : '—'; }
function longDate(d){ return d ? d.getUTCDate()+' '+MON[d.getUTCMonth()]+' '+
  d.getUTCFullYear() : '—'; }
function fnum(s){
  var t = clean(s); if(t==='') return null;
  var v = parseFloat(t.replace(/,/g,''));
  return isNaN(v) ? null : v;
}
function median(a){
  var d = a.slice().sort(function(x,y){return x-y;}), n=d.length;
  if(!n) return 0;
  return (n%2) ? d[(n-1)/2] : (d[n/2-1]+d[n/2])/2;
}
/* matches Python statistics.quantiles(data, n=4, method='inclusive') exactly, so the
   allowance pool is sized the same way the draw.io page sizes it */
function quantiles4(data){
  var d = data.slice().sort(function(x,y){return x-y;}), N=d.length;
  if(!N) return [0,0,0];
  if(N===1) return [d[0],d[0],d[0]];
  var m=N-1, n=4, out=[];
  for(var i=1;i<n;i++){
    var j=Math.floor(i*m/n), delta=(i*m)%n;
    out.push((d[j]*(n-delta)+d[j+1]*delta)/n);
  }
  return out;
}
function listPhrase(a){
  if(!a.length) return 'none';
  if(a.length===1) return a[0];
  return a.slice(0,-1).join(', ')+' and '+a[a.length-1];
}
function topOf(counter){
  var best=null, n=0;
  for(var k in counter){ if(counter[k]>n){ n=counter[k]; best=k; } }
  return {name:best||'—', n:n};
}
function tally(arr, key){
  var c={}; arr.forEach(function(r){ var v=key(r); if(v) c[v]=(c[v]||0)+1; }); return c;
}

/* ============================================ mapping index (FR-108..FR-122) */
/* Built once from CONFIG. Matching is on the cleaned, case-folded title, so a stray
   leading or trailing space in the extract does not lose an initiative (FR-111). */
var MAPIDX = (function(){
  var cap={}, plat={}, dbl=[];
  function add(store, key, label, idx){
    var k = clean(key).toLowerCase();
    if(store[k]) dbl.push({title:key, a:store[k].label, b:label});
    else store[k] = {label:label, idx:idx};
  }
  CONFIG.capabilities.forEach(function(c,i){
    c.titles.forEach(function(t){ add(cap, t, c.key, i); });
  });
  CONFIG.platform.forEach(function(p,i){
    p.titles.forEach(function(t){ add(plat, t, deent(p.key), i); });
  });
  return {cap:cap, plat:plat, doubleMapped:dbl};
})();

/* ================================================ parse (FR-143..FR-156) */
function parseSnapshot(snap){
  var recs=[], subs=0, blank=0, warn=[];
  var known = CONFIG.scope.active.concat(CONFIG.scope.dead);

  snap.rows.forEach(function(row, i){
    var raw={};
    snap.fields.forEach(function(f,j){ raw[f] = (row[j]===null||row[j]===undefined)?'':row[j]; });

    var line = i + 2;                       /* +1 header, +1 to one-based */
    snap.fields.forEach(function(f){ subs += fffd(raw[f]); });

    var title = clean(raw['Title']);
    if(title==='' && clean(raw['Stage'])===''){ blank++; return; }

    var stage = clean(raw['Stage']);
    if(known.indexOf(stage) < 0){
      warn.push({kind:'stage', line:line, title:title,
        text:'Record '+line+' ("'+(title||'untitled')+'") carries stage "'+stage+
             '", which is not one of the five recognised stages. It is excluded from both '+
             'views rather than guessed at.'});
    }

    var startRaw = clean(raw['Start Date - Est Project']);
    var start = dnum(startRaw);
    if(startRaw!=='' && !start){
      warn.push({kind:'date', line:line, title:title,
        text:'Record '+line+' ("'+title+'") has start date "'+startRaw+
             '", which is not a recognisable day/month/year. Treated as no start date.'});
    }
    var durRaw = clean(raw['Duration - Est Project (months)']);
    var dur = fnum(durRaw);
    if(durRaw!=='' && dur===null){
      warn.push({kind:'dur', line:line, title:title,
        text:'Record '+line+' ("'+title+'") has duration "'+durRaw+
             '", which is not a number. Treated as no duration.'});
    }
    if(dur!==null && dur<=0){
      warn.push({kind:'dur', line:line, title:title,
        text:'Record '+line+' ("'+title+'") has a duration of '+durRaw+
             ' months. A non-positive duration cannot be prorated; treated as absent.'});
      dur = null;
    }

    var labour={}, tot=0, anyEst=false;
    ROLES.forEach(function(c){
      var v = fnum(raw[c+' - Est Project Labour Days']);
      if(v!==null && v<0){
        warn.push({kind:'neg', line:line, title:title,
          text:'Record '+line+' ("'+title+'") has '+v+' '+c+
               ' labour days. A negative estimate is treated as absent.'});
        v = null;
      }
      labour[c] = v===null?0:v;
      if(v!==null && v>0){ tot += v; anyEst = true; }
    });

    /* FR-152: Budget is a funding flag, not a money value. Only an explicit Yes funds. */
    var budgetRaw = clean(raw['Budget']);
    var funded = budgetRaw.toLowerCase()==='yes';

    var sponsor = clean(raw['Sponsor']);
    var author  = clean(raw['Author']);
    var lk = title.toLowerCase();
    var cm = MAPIDX.cap[lk] || null, pm = MAPIDX.plat[lk] || null;

    recs.push({
      id: recs.length, line: line, raw: raw,
      title: title,
      /* FR-155: held for the drill-down only. Never used to classify, because the column
         is offset against Title across a block of rows in the source. */
      summary: clean(raw['High-Level Summary']),
      stage: stage, valid: known.indexOf(stage)>=0,
      sponsor: sponsor, author: author,
      budgetRaw: budgetRaw, funded: funded,
      startRaw: startRaw, start: start,
      durRaw: durRaw, dur: dur,
      labour: labour, days: tot, hasEst: anyEst,
      cap: cm?cm.label:null, capIdx: cm?cm.idx:-1,
      plat: pm?pm.label:null, platIdx: pm?pm.idx:-1
    });
  });

  return {records:recs, substitutions:subs, blankRows:blank, warnings:warn,
          physicalLines:snap.physicalLines, header:snap.header};
}

/* ================================================== mapping assurance (FR-114..119) */
function mappingAssurance(recs){
  var byTitle={};
  recs.forEach(function(r){ byTitle[r.title.toLowerCase()] = r; });
  var stale=[], retired=[], unmapped=[];
  function walk(store){
    for(var k in store){
      var r = byTitle[k];
      if(!r) stale.push({key:k, group:store[k].label});
      else if(CONFIG.scope.dead.indexOf(r.stage)>=0)
        retired.push({title:r.title, group:store[k].label, stage:r.stage});
    }
  }
  walk(MAPIDX.cap); walk(MAPIDX.plat);
  recs.forEach(function(r){
    if(CONFIG.scope.active.indexOf(r.stage)>=0 && !r.cap && !r.plat) unmapped.push(r);
  });
  return {stale:stale, retired:retired, unmapped:unmapped,
          doubleMapped:MAPIDX.doubleMapped};
}

/* ============================================================ filtering */
function passes(r, f, useStage){
  if(useStage && f.stage && r.stage!==f.stage) return false;
  if(f.sponsor && r.sponsor!==f.sponsor) return false;
  if(f.author && r.author!==f.author) return false;
  if(f.cap && r.cap!==f.cap) return false;
  if(f.plat && r.plat!==f.plat) return false;
  if(f.funding==='funded' && !r.funded) return false;
  if(f.funding==='unfunded' && r.funded) return false;
  if(f.role && !(r.labour[f.role]>0)) return false;
  if(f.q){
    var q = f.q.toLowerCase();
    if(r.title.toLowerCase().indexOf(q) < 0) return false;
  }
  return true;
}

/* ============================================== business architecture model */
function buildBA(all, f){
  var pool   = all.filter(function(r){ return r.valid && passes(r, f, false); });
  var active = pool.filter(function(r){
    return CONFIG.scope.active.indexOf(r.stage)>=0 && (!f.stage || r.stage===f.stage); });
  var dead   = pool.filter(function(r){ return CONFIG.scope.dead.indexOf(r.stage)>=0; });

  var byStage={}; CONFIG.scope.active.forEach(function(s){ byStage[s]=0; });
  var deadBy={};  CONFIG.scope.dead.forEach(function(s){ deadBy[s]=0; });
  active.forEach(function(r){ byStage[r.stage]++; });
  dead.forEach(function(r){ deadBy[r.stage]++; });

  var caps = CONFIG.capabilities.map(function(c,i){
    return {cfg:c, idx:i, items:active.filter(function(r){ return r.capIdx===i; })};
  });
  var plats = CONFIG.platform.map(function(p,i){
    return {cfg:p, idx:i, items:active.filter(function(r){ return r.platIdx===i; })};
  });

  var d = {noSponsor:[], noAuthor:[], noStart:[], noEst:[]};
  active.forEach(function(r){
    if(!r.sponsor) d.noSponsor.push(r);
    if(!r.author) d.noAuthor.push(r);
    if(!r.start) d.noStart.push(r);
    if(!r.hasEst) d.noEst.push(r);
  });

  var labour={}; ROLES.forEach(function(c){ labour[c]=0; });
  var totalDays=0, withEst=0, funded=0;
  active.forEach(function(r){
    ROLES.forEach(function(c){ labour[c]+=r.labour[c]; });
    totalDays += r.days; if(r.hasEst) withEst++; if(r.funded) funded++;
  });

  var sp = topOf(tally(active,function(r){return r.sponsor;}));
  var au = topOf(tally(active,function(r){return r.author;}));
  var thin = caps.filter(function(c){ return c.items.length<=1; })
    .map(function(c){ return c.cfg.key.charAt(0)+c.cfg.key.slice(1).toLowerCase()+
      ' ('+c.items.length+')'; });

  return {pool:pool, active:active, dead:dead, byStage:byStage, deadBy:deadBy,
          caps:caps, plats:plats, defects:d, labour:labour, totalDays:totalDays,
          withEst:withEst, funded:funded, topSponsor:sp, topAuthor:au, thin:thin};
}

/* ======================================================= demand profile model */
function buildDP(all, f, runDate){
  var hStart = mkd(runDate.getUTCFullYear(), runDate.getUTCMonth(), 1);
  var HZ=[], HZE=[];
  for(var i=0;i<CONFIG.meta.horizonMonths;i++){
    HZ.push(addMonths(hStart,i)); HZE.push(addMonths(hStart,i+1));
  }
  var NM = HZ.length;

  var pool = all.filter(function(r){ return r.valid && passes(r, f, false); });
  var scope = pool.filter(function(r){
    return CONFIG.scope.demand.indexOf(r.stage)>=0 && (!f.stage || r.stage===f.stage); });
  var excl={}; CONFIG.scope.demandExcluded.forEach(function(s){ excl[s]=0; });
  pool.forEach(function(r){ if(excl[r.stage]!==undefined) excl[r.stage]++; });

  /* --- tiering (FR-052..FR-057) ------------------------------------------ */
  var est = scope.filter(function(r){ return r.hasEst; });
  var unq = scope.filter(function(r){ return !r.hasEst; });
  var durs = est.filter(function(r){ return r.dur; }).map(function(r){ return r.dur; });
  var medDur = median(durs) || 3.0;

  var proj = est.map(function(r){
    var tier, ws, wd;
    if(r.start && r.dur){ tier='A'; ws=r.start; wd=r.dur; }
    else if(r.start){ tier='B'; ws=r.start; wd=medDur; }
    else { tier='C'; ws=hStart; wd=medDur; }
    var months=[]; for(var k=0;k<NM;k++) months.push(0);
    return {rec:r, tier:tier, winStart:ws, winDur:wd, months:months, inHz:0};
  });

  /* --- calendar-day-overlap proration (FR-062..FR-066) ------------------- */
  var profile={}; ROLES.forEach(function(c){
    profile[c]=[]; for(var k=0;k<NM;k++) profile[c].push(0); });

  proj.forEach(function(p){
    var s = p.winStart, e = addMonths(s, Math.round(p.winDur));
    var span = days(s,e) || 1;
    for(var i=0;i<NM;i++){
      var a = (s>HZ[i])?s:HZ[i], b = (e<HZE[i])?e:HZE[i];
      var ov = days(a,b);
      if(ov>0){
        var fr = ov/span;
        ROLES.forEach(function(c){ profile[c][i] += p.rec.labour[c]*fr; });
        p.months[i] = p.rec.days*fr;
        p.inHz += p.rec.days*fr;
      }
    }
  });

  var estM=[]; for(var i2=0;i2<NM;i2++){
    var t=0; ROLES.forEach(function(c){ t+=profile[c][i2]; }); estM.push(t); }
  var estTotal=0; est.forEach(function(r){ estTotal+=r.days; });
  var estInHz=0; proj.forEach(function(p){ estInHz+=p.inHz; });

  /* --- quartile-sized allowance pool (FR-039..FR-043) ------------------- */
  var totals = est.map(function(r){ return r.days; });
  var q = quantiles4(totals);
  var qmap = {q1:q[0], q2:q[1], q3:q[2]};
  var meanEst = totals.length ? estTotal/totals.length : 0;

  var allow={};
  CONFIG.scenarios.forEach(function(s){
    var per = qmap[s[2]], p2 = per*unq.length;
    allow[s[0]] = {per:per, pool:p2, perMonth:p2/NM, total:estInHz+p2};
  });
  var baseAllow = allow['Base case'].perMonth;
  var baseM = estM.map(function(v){ return v + baseAllow; });
  var maxB = Math.max.apply(null, baseM.concat([0]));
  var axMax = (Math.floor(maxB/40)+1)*40;

  var peakIdx=0; baseM.forEach(function(v,i){ if(v>baseM[peakIdx]) peakIdx=i; });
  var avg = allow['Base case'].total/NM;

  /* --- role-level measures ---------------------------------------------- */
  var roleTot={}, rolePeak={};
  ROLES.forEach(function(c){
    var t=0, pk=0, pi=0;
    profile[c].forEach(function(v,i){ t+=v; if(v>pk){pk=v;pi=i;} });
    roleTot[c]=t; rolePeak[c]={days:pk, idx:pi};
  });
  var nil = ROLES.filter(function(c){ return roleTot[c]<=0.0001; });
  var series = CONFIG.palette.series.filter(function(s){ return roleTot[s[0]]>0.0001; });

  /* --- concentration, integrity, back-half blindness -------------------- */
  var ranked = est.slice().sort(function(a,b){ return b.days-a.days; });
  var top1 = ranked[0]||null, top2 = ranked[1]||null;
  var overrun = proj.filter(function(p){
    return p.tier==='A' && p.rec.stage==='In Progress' &&
           addMonths(p.winStart, Math.round(p.winDur)) <= hStart; });
  var noDate = scope.filter(function(r){ return !r.start; });
  var noDur  = scope.filter(function(r){ return !r.dur; });
  var funded = scope.filter(function(r){ return r.funded; });

  var zeroIdx=-1;
  for(var z=NM-1; z>=0; z--){ if(estM[z]>=0.05) break; zeroIdx=z; }

  return {hStart:hStart, HZ:HZ, HZE:HZE, NM:NM, pool:pool, scope:scope, excl:excl,
          est:est, unq:unq, proj:proj, medDur:medDur, profile:profile, estM:estM,
          estTotal:estTotal, estInHz:estInHz, q:qmap, meanEst:meanEst, allow:allow,
          baseM:baseM, axMax:axMax, peakIdx:peakIdx, avg:avg, roleTot:roleTot,
          rolePeak:rolePeak, nil:nil, series:series, ranked:ranked, top1:top1, top2:top2,
          overrun:overrun, noDate:noDate, noDur:noDur, funded:funded, zeroIdx:zeroIdx};
}

/* ================================================ token substitution values */
/* CONFIG prose carries {TOKEN} placeholders so the panels read correctly under any
   filter. Values are escaped in fill(), so a crafted sponsor name cannot inject
   markup (NFR-037). */
function tokens(P, ba, dp){
  var t={};
  t.N_LOADED = String(P.records.length);
  t.N_DEAD   = String(ba.dead.length);
  t.N_DEAD_DP= String((dp.excl['Complete']||0)+(dp.excl['Cancelled']||0));

  /* --- business architecture ------------------------------------------- */
  t.N            = String(ba.active.length);
  t.N_ON_HOLD    = String(ba.byStage['On Hold']||0);
  t.PCT_ON_HOLD  = pct(ba.byStage['On Hold']||0, ba.active.length, 0);
  t.N_FUNDED     = String(ba.funded);
  t.N_NO_SPONSOR = String(ba.defects.noSponsor.length);
  t.N_NO_AUTHOR  = String(ba.defects.noAuthor.length);
  t.N_NO_START   = String(ba.defects.noStart.length);
  t.N_NO_EST     = String(ba.defects.noEst.length);
  t.N_WITH_EST   = String(ba.withEst);
  t.TOTAL_DAYS   = fmt(ba.totalDays);
  ROLES.forEach(function(c){ t['D_'+c.toUpperCase()] = fmt(ba.labour[c]); });
  t.TOP_SPONSOR   = ba.topSponsor.name;
  t.TOP_SPONSOR_N = String(ba.topSponsor.n);
  t.TOP_AUTHOR    = ba.topAuthor.name;
  t.TOP_AUTHOR_N  = String(ba.topAuthor.n);
  t.THIN_LIST     = ba.thin.length
      ? listPhrase(ba.thin)+(ba.thin.length>1?' are at or below that line':
        ' is at or below that line')
      : 'no capability is at or below that line';
  ba.caps.forEach(function(c){ t['C_'+c.cfg.key] = String(c.items.length); });

  /* --- demand profile --------------------------------------------------- */
  var n = dp.scope.length;
  t.HZ_FROM   = shortDate(dp.HZ[0]);
  t.HZ_TO     = shortDate(dp.HZ[dp.NM-1]);
  t.N_EXCL    = String((dp.excl['On Hold']||0)+(dp.excl['Complete']||0)+
                       (dp.excl['Cancelled']||0));
  t.X_OH      = String(dp.excl['On Hold']||0);
  t.X_CO      = String(dp.excl['Complete']||0);
  t.X_CA      = String(dp.excl['Cancelled']||0);
  t.N_EST     = String(dp.est.length);
  t.N_UNQ     = String(dp.unq.length);
  t.COVERAGE  = pct(dp.est.length, n);
  t.UNCOVERAGE= pct(dp.unq.length, n);
  t.EST_TOTAL = fmt(dp.estTotal);
  t.EST_IN_HZ = fmt(dp.estInHz);
  t.EST_OUT   = fmt(dp.estTotal - dp.estInHz);
  t.N_TIER_A  = String(dp.proj.filter(function(p){return p.tier==='A';}).length);
  t.Q1 = fmt(dp.q.q1); t.Q2 = fmt(dp.q.q2); t.Q3 = fmt(dp.q.q3);
  t.MEAN_EST  = fmt(dp.meanEst);
  t.MED_DUR   = fmt(dp.medDur);
  t.NIL_STMT  = dp.nil.length
      ? dp.nil.map(function(c){ return CONFIG.roleFull[c]+' ('+c+')'; }).join(', ')+
        (dp.nil.length>1?' carry':' carries')+' no estimated days across the in-scope '+
        'set, so '+(dp.nil.length>1?'those series are':'that series is')+
        ' absent from the chart rather than drawn flat.'
      : 'Every role carries estimated days somewhere in the in-scope set.';
  t.SPREAD    = fmt(dp.allow['Downside'].total ?
                dp.allow['Upside'].total/dp.allow['Downside'].total : 0, 1);
  t.PEAK_MONTH= shortDate(dp.HZ[dp.peakIdx]);
  t.PEAK_DAYS = fmt(dp.baseM[dp.peakIdx]||0);
  t.PEAK_FTE  = fmt((dp.baseM[dp.peakIdx]||0)/DPM);
  t.AVG_DAYS  = fmt(dp.avg);
  t.AVG_FTE   = fmt(dp.avg/DPM);
  t.PEAK_OVER = dp.avg ? fmt((dp.baseM[dp.peakIdx]/dp.avg-1)*100, 0) : '0';
  t.IE_SHARE  = pct(dp.roleTot['IE'], dp.estInHz);
  t.IE_PEAK_FTE   = fmt(dp.rolePeak['IE'].days/DPM);
  t.IE_PEAK_MONTH = shortDate(dp.HZ[dp.rolePeak['IE'].idx]);
  t.N_UNFUNDED= String(n - dp.funded.length);
  t.FUNDED_PCT= pct(dp.funded.length, n, 0);
  t.N_NO_DATE = String(dp.noDate.length);
  t.N_NO_DUR  = String(dp.noDur.length);
  t.N_WITH_DATE = String(n - dp.noDate.length);
  t.SCHED_PCT = pct(n - dp.noDate.length, n, 0);
  t.N_OVERRUN = String(dp.overrun.length);
  t.TOP1       = dp.top1 ? dp.top1.title : '—';
  t.TOP1_SHARE = dp.top1 ? pct(dp.top1.days, dp.estTotal) : '0';
  t.TOP2_SHARE = dp.top2 ? pct(dp.top1.days+dp.top2.days, dp.estTotal) :
                 (dp.top1?pct(dp.top1.days, dp.estTotal):'0');
  t.ZERO_MONTH = dp.zeroIdx<0 ? 'no month in the horizon'
                 : (dp.zeroIdx===0 ? 'the first month of the horizon'
                    : shortDate(dp.HZ[dp.zeroIdx]));
  return t;
}
function fill(tpl, t){
  return String(tpl).replace(/\{([A-Z0-9_]+)\}/g, function(m,k){
    return (k in t) ? esc(t[k]) : m;
  });
}

/* ==================================================== the one model object */
function buildModel(parsed, filters, runDate){
  var ba = buildBA(parsed.records, filters);
  var dp = buildDP(parsed.records, filters, runDate);
  return {parsed:parsed, filters:filters, runDate:runDate, ba:ba, dp:dp,
          assurance:mappingAssurance(parsed.records),
          vars:tokens(parsed, ba, dp)};
}
"""

# ================================================================ section 5 — render.js
# Every coordinate below is the coordinate from the authority draw.io script, because
# those numbers are proven to fit one A2 landscape page (2245 x 1587). Absolute
# positioning, not flow layout, for the same reason.
# All source-derived strings go in via textContent (NFR-037). innerHTML is used only for
# authored CONFIG prose, and the values substituted into it are escaped by fill().
JS_RENDER = r"""
/* ============================================================ page geometry */
var X0=24, RIGHT=2221, W=RIGHT-X0;               /* 2197 */
var ARROW_W=52, ARROW_H=20;
var PAL = CONFIG.palette;

function grid(n, gap, x, width){
  gap = (gap===undefined)?8:gap; x=(x===undefined)?X0:x; width=(width===undefined)?W:width;
  var cw=(width-gap*(n-1))/n, out=[];
  for(var i=0;i<n;i++) out.push([x+i*(cw+gap), cw]);
  return out;
}
function el(tag, cls, parent){
  var d=document.createElement(tag);
  if(cls) d.className=cls;
  if(parent) parent.appendChild(d);
  return d;
}
function abs(parent, x, y, w, h, cls){
  var d=el('div','abs '+(cls||''),parent);
  d.style.left=x+'px'; d.style.top=y+'px';
  if(w!==null) d.style.width=w+'px';
  if(h!==null) d.style.height=h+'px';
  return d;
}
function fr(node, ids, label){ node.dataset.fr=ids; node.dataset.frl=label; return node; }
/* A sortable column header is an operable control, so it takes focus, announces its
   sort state, and answers Enter and Space as well as a click (NFR-041). Defined once
   here and used by both tables. */
function sortable(th, label, on, desc){
  th.tabIndex = 0;
  th.setAttribute('role','columnheader');
  th.setAttribute('aria-sort', on ? (desc?'descending':'ascending') : 'none');
  th.setAttribute('aria-label', label + ' — sort' +
    (on ? (desc?', sorted descending':', sorted ascending') : ''));
  return th;
}
function txt(node, s){ node.textContent = (s===null||s===undefined)?'':String(s); return node;}
function bandRow(parent, y, label, note, ids, frl){
  var b = abs(parent, X0, y, W, 22, 'band');
  var tab = abs(parent, X0, y, 5, 22, 'bandtab');
  tab.style.zIndex='2';
  if(note){ var n=el('span','note',b); n.innerHTML=note; }
  b.insertBefore(document.createTextNode(label), b.firstChild);
  if(ids) fr(b, ids, frl);
  return b;
}
function box(parent, x, y, w, h, fill, line, cls){
  var d = abs(parent, x, y, w, h, 'box '+(cls||''));
  d.style.background=fill; d.style.borderColor=line;
  return d;
}
function headDesc(node, head, desc, ink){
  var h=el('div','boxhead',node); h.style.color=ink||PAL.teal; h.innerHTML=head;
  var p=el('div','pxs',node); p.style.marginTop='3px'; p.style.color='#1A1A1A';
  p.innerHTML=desc;
  return node;
}
function swatch(parent, fill, line, label, sub){
  var s=el('span',null,parent);
  s.style.cssText='display:inline-flex;align-items:center;gap:4px;margin-right:12px';
  var b=el('span',null,s);
  b.style.cssText='width:11px;height:11px;border:1px solid '+line+';background:'+fill;
  var t=el('span',null,s); t.style.cssText='font-size:8px';
  t.textContent = label + (sub?(' '+sub):'');
  return s;
}
function downArrow(parent, x, y, colour){
  var s=document.createElementNS('http://www.w3.org/2000/svg','svg');
  s.setAttribute('width',ARROW_W); s.setAttribute('height',ARROW_H);
  s.setAttribute('class','arrow'); s.style.left=x+'px'; s.style.top=y+'px';
  var p=document.createElementNS('http://www.w3.org/2000/svg','polygon');
  p.setAttribute('points','12,0 40,0 40,9 49,9 26,20 3,9 12,9');
  p.setAttribute('fill',colour); p.setAttribute('opacity','0.85');
  s.appendChild(p); parent.appendChild(s); return s;
}
function upArrow(parent, x, y, colour){
  var s=document.createElementNS('http://www.w3.org/2000/svg','svg');
  s.setAttribute('width',ARROW_W); s.setAttribute('height',ARROW_H);
  s.setAttribute('class','arrow'); s.style.left=x+'px'; s.style.top=y+'px';
  var p=document.createElementNS('http://www.w3.org/2000/svg','polygon');
  p.setAttribute('points','26,0 49,11 40,11 40,20 12,20 12,11 3,11');
  p.setAttribute('fill',colour); p.setAttribute('opacity','0.85');
  s.appendChild(p); parent.appendChild(s); return s;
}
function svgEl(tag, attrs, parent){
  var e=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(var k in attrs) e.setAttribute(k, attrs[k]);
  if(parent) parent.appendChild(e);
  return e;
}

/* ================================================= initiative chip (FR-020..026) */
function chip(parent, x, y, w, r, M){
  var st = PAL.stage[r.stage] || PAL.stage['Opportunity'];
  var c = abs(parent, x, y, w, 32, 'chip');
  c.style.background=st.fill; c.style.borderColor=st.line;
  c.tabIndex = 0;
  c.dataset.rid = r.id;
  el('div','bar',c).style.background = st.bar;

  var t = el('div','t',c); t.style.color = st.ink; t.textContent = r.title;

  var m = el('div','m',c);
  if(r.sponsor) m.appendChild(document.createTextNode(r.sponsor));
  else { var ns=el('span','alert',m); ns.textContent='no sponsor'; }
  m.appendChild(document.createTextNode('  ·  '));
  m.appendChild(document.createTextNode(r.funded ? 'funded' : 'unfunded'));
  if(r.start){
    m.appendChild(document.createTextNode('  ·  '));
    var i=el('i',null,m); i.textContent = shortDate(r.start);
  } else {
    m.appendChild(document.createTextNode('  ·  '));
    var nd=el('span','alert',m); nd.textContent='no start';
  }

  var a = el('div','a',c);
  if(r.author) a.textContent = 'auth ' + r.author;
  else { var na=el('span','alert',a); na.textContent='no author'; }
  return c;
}
function chipStack(parent, x, y, w, items, maxN, M){
  var shown = items.slice(0, maxN);
  shown.forEach(function(r,i){ chip(parent, x, y+i*35, w, r, M); });
  if(items.length > maxN){
    var more = abs(parent, x, y+maxN*35, w, 14, 'pxs');
    more.style.color = PAL.grey; more.style.cursor='pointer';
    more.dataset.more = '1';
    more.textContent = '+ ' + (items.length-maxN) + ' more — open the list';
    more.dataset.ids = items.slice(maxN).map(function(r){return r.id;}).join(',');
  }
}

/* ================================================================ sort order */
function sortItems(items, key){
  var a = items.slice();
  var by = {
    stage: function(r){ return [CONFIG.scope.active.indexOf(r.stage), r.title]; },
    title: function(r){ return [r.title.toLowerCase()]; },
    days:  function(r){ return [-r.days, r.title.toLowerCase()]; },
    start: function(r){ return [r.start?r.start.getTime():9e15, r.title.toLowerCase()]; },
    sponsor:function(r){ return [(r.sponsor||'zzz').toLowerCase(), r.title.toLowerCase()]; }
  }[key] || function(r){ return [r.title.toLowerCase()]; };
  a.sort(function(p,q){
    var u=by(p), v=by(q);
    for(var i=0;i<u.length;i++){ if(u[i]<v[i]) return -1; if(u[i]>v[i]) return 1; }
    return 0;
  });
  return a;
}

/* ====================================================================== */
/*  BUSINESS ARCHITECTURE VIEW  (FR-011..FR-038)                          */
/*  TOGAF BDAT Mining-Adapted, Tier 1; EMMM Business Capability Ref Map   */
/* ====================================================================== */
function renderBA(root, M){
  root.innerHTML='';
  var V = M.vars, ba = M.ba, T = M.vars;

  /* ---------------------------------------------- header, legend (FR-027..032) */
  var hdr = fr(abs(root, X0, 24, W, 68), 'FR-027..FR-032', 'Page Structure and Legend');
  var ti = el('div','pagetitle',hdr);
  ti.textContent = 'SHORT-TERM PROJECTS PIPELINE — BUSINESS ARCHITECTURE';
  var sub = el('div','pagesub',hdr); sub.style.marginTop='3px';
  sub.innerHTML = CONFIG.meta.frameworks.ba +
    '<br>Scope: the <b>' + esc(T.N) + ' active initiatives</b> (' +
    CONFIG.scope.active.join(' · ') + '). <b>' + esc(T.N_DEAD) +
    ' omitted</b> as Complete or Cancelled, from ' + esc(T.N_LOADED) + ' records read.';

  var lg = abs(root, 1290, 24, 931, 30);
  lg.style.textAlign='right';
  CONFIG.scope.active.forEach(function(s){
    swatch(lg, PAL.stage[s].fill, PAL.stage[s].bar, s, '('+(ba.byStage[s]||0)+')');
  });
  var lg2 = abs(root, 1290, 44, 931, 26); lg2.style.textAlign='right';
  swatch(lg2, PAL.domain.IT.fill, PAL.domain.IT.bar, 'IT-led');
  swatch(lg2, PAL.domain.OT.fill, PAL.domain.OT.bar, 'OT-led');
  swatch(lg2, PAL.domain.CV.fill, PAL.domain.CV.bar, 'Converged IT/OT');
  var th = el('span',null,lg2);
  th.style.cssText='display:inline-flex;align-items:center;gap:4px;font-size:8px';
  var tb = el('span',null,th);
  tb.style.cssText='width:11px;height:11px;border:2px solid '+PAL.red+';background:#fff';
  txt(el('span',null,th), 'thin coverage (≤1 active)');
  var stamp = abs(root, 1290, 70, 931, 24, 'stamp'); stamp.style.textAlign='right';
  stamp.textContent = provenanceLine(M);

  /* ---------------------------------------------- band A: drivers (FR-036..038) */
  bandRow(root, 96, 'A  ·  CORPORATE STRATEGY & DRIVERS',
    'Set at corporate level. Everything below must trace to one of these.',
    'FR-036..FR-038', 'Strategy and Driver Band');
  var gA = grid(5,10);
  CONFIG.drivers.forEach(function(d,i){
    var b = box(root, gA[i][0], 122, gA[i][1], 62, PAL.surf, PAL.stage['Opportunity'].line);
    headDesc(b, d[0], d[1], PAL.stage['Opportunity'].ink);
  });

  /* down flow arrows */
  gA.forEach(function(g){
    downArrow(root, g[0]+g[1]/2-ARROW_W/2, 188, PAL.teal_2 || '#2D686F'); });

  /* ------------------------------------- band B: capability coverage (FR-011..013) */
  bandRow(root, 214, 'B  ·  BUSINESS CAPABILITY COVERAGE',
    'Open Group EMMM Business Capability Reference Map. Count = active initiatives '+
    'touching that capability.', 'FR-011..FR-013', 'Capability Coverage Band');
  var gB = grid(6,8);
  ba.caps.forEach(function(c,i){
    var dm = PAL.domain[c.cfg.domain], thin = c.items.length<=1;
    var b = box(root, gB[i][0], 240, gB[i][1], 62, dm.fill, dm.line,
      (thin?'thin':'')+' hot');
    b.dataset.cap = c.cfg.key;
    b.tabIndex = 0;
    fr(b, 'FR-011..FR-013', 'Capability Coverage Band');
    var h = el('div','boxhead',b); h.style.color=dm.ink;
    h.innerHTML = c.cfg.key + ' &nbsp;<span style="font-weight:normal">' +
      c.items.length + ' active</span>';
    var cv = el('div','pxs',b); cv.style.color=PAL.grey; cv.innerHTML = c.cfg.cover;
    var vd = el('div','pxs',b); vd.style.marginTop='2px'; vd.innerHTML = c.cfg.verdict;
  });

  /* ------------------------------------------- band C: initiative chips (FR-020..026) */
  bandRow(root, 308, 'C  ·  ACTIVE INITIATIVES SERVING EACH CAPABILITY',
    'One chip per active initiative: title · sponsor · funding · estimated start · '+
    'author. Click any chip for the source record.',
    'FR-020..FR-026', 'Initiative Chips');
  ba.caps.forEach(function(c,i){
    var items = sortItems(c.items, M.filters.order);
    if(!items.length){
      var e = abs(root, gB[i][0], 334, gB[i][1], 32, 'box pxs');
      e.style.background='#FFFFFF'; e.style.borderColor=PAL.rule;
      e.style.color=PAL.red; e.style.fontWeight='bold';
      e.textContent = 'no active initiative';
      fr(e, 'FR-013', 'Capability Coverage Band');
    } else {
      chipStack(root, gB[i][0], 334, gB[i][1], items, 10, M);
    }
  });

  /* ------------------------------------- band D: enabling platform (FR-014..015) */
  bandRow(root, 688, 'D  ·  ENABLING IT / OT PLATFORM LAYER',
    'Not an EMMM capability. Declared explicitly because it gates almost everything '+
    'above it and must be sequenced first.', 'FR-014..FR-015', 'Enabling Platform Band');
  var gD = grid(6,8);
  ba.plats.forEach(function(p,i){
    var dm = PAL.domain[p.cfg.domain];
    var h = abs(root, gD[i][0], 714, gD[i][1], 18, 'box hot');
    h.style.background=dm.fill; h.style.borderColor=dm.line; h.style.padding='2px 6px';
    h.dataset.plat = deent(p.cfg.key); h.tabIndex=0;
    fr(h, 'FR-014..FR-015', 'Enabling Platform Band');
    var hh = el('div','boxhead',h); hh.style.color=dm.ink;
    hh.innerHTML = p.cfg.key + ' &nbsp;<span style="font-weight:normal">' +
      p.items.length + '</span>';
    chipStack(root, gD[i][0], 734, gD[i][1], sortItems(p.items, M.filters.order), 7, M);
    var n = abs(root, gD[i][0], 979, gD[i][1], 12, 'pxs');
    n.style.color=PAL.grey; n.innerHTML = p.cfg.note;
  });

  /* up flow arrows */
  gA.forEach(function(g){
    upArrow(root, g[0]+g[1]/2-ARROW_W/2, 993, PAL.stage['Opportunity'].ink); });

  /* ------------------------------------------ band E: site realities (FR-033..035) */
  bandRow(root, 1019, 'E  ·  SITE & OPERATING REALITIES THAT CONSTRAIN THE PLAN',
    'Flows upward. These are not IT choices; the plan adapts to them.',
    'FR-033..FR-035', 'Site Realities and Governance Bands');
  var gE = grid(6,8);
  CONFIG.site.forEach(function(s,i){
    var b = box(root, gE[i][0], 1045, gE[i][1], 66, '#FFFFFF', PAL.rule);
    headDesc(b, s[0], fill(s[1], T), PAL.stage['Opportunity'].ink);
  });

  /* ---------------------------------------- band F: federated governance (FR-035) */
  bandRow(root, 1117, 'F  ·  FEDERATED GOVERNANCE — WHO DECIDES WHAT',
    'Framework requirement: corporate sets the standard, hubs adapt within it, sites '+
    'execute and escalate.', 'FR-033..FR-035', 'Site Realities and Governance Bands');
  var gF = grid(4,10);
  CONFIG.governance.forEach(function(g,i){
    var b = box(root, gF[i][0], 1143, gF[i][1], 128, g[2], g[3]);
    if(i===3) b.style.borderWidth='2px';
    var h = el('div','boxhead',b); h.style.color=g[4]; h.innerHTML=g[0];
    var p = el('div','pxs',b); p.style.marginTop='3px'; p.innerHTML = fill(g[1], T);
  });

  /* ------------------------------------- band G: portfolio health (FR-016..019) */
  bandRow(root, 1279, 'G  ·  PORTFOLIO HEALTH MEASURES — WHAT GOOD LOOKS LIKE',
    'Target condition, then today’s reading from this extract.',
    'FR-016..FR-019', 'Health Measures and Footer');
  var gG = grid(6,8);
  CONFIG.metrics.forEach(function(m,i){
    var b = box(root, gG[i][0], 1305, gG[i][1], 54, PAL.surf2, PAL.rule);
    headDesc(b, m[0], fill(m[1], T), PAL.teal);
  });

  /* ------------------------------------------------- footer (FR-016..FR-019) */
  var fw = Math.round(W*0.56), rw = W-fw-10;
  var f1 = box(root, X0, 1367, fw, 176, '#FFFFFF', PAL.teal);
  f1.style.borderWidth='0 0 0 3px';
  fr(f1, 'FR-016..FR-019', 'Health Measures and Footer');
  var f1h = el('div','boxhead',f1); f1h.style.color=PAL.teal;
  f1h.innerHTML = CONFIG.baFooter.leftTitle;
  var f1p = el('div','pxs',f1); f1p.style.marginTop='4px';
  f1p.innerHTML = fill(CONFIG.baFooter.left, T);

  var f2 = box(root, X0+fw+10, 1367, rw, 176, '#FFFFFF', PAL.red);
  f2.style.borderWidth='0 0 0 3px';
  fr(f2, 'FR-016..FR-019', 'Health Measures and Footer');
  var f2h = el('div','boxhead',f2); f2h.style.color=PAL.red;
  f2h.innerHTML = CONFIG.baFooter.rightTitle;
  var f2p = el('div','pxs',f2); f2p.style.marginTop='4px';
  f2p.innerHTML = fill(CONFIG.baFooter.right, T);

  bottomStrip(root, M, 'Business Architecture');
}

/* ------------------------------------------------- shared page furniture */
function provenanceLine(M){
  var p = M.parsed, s = SNAPSHOT;
  return 'Source ' + s.name + '  ·  last modified ' + s.modified +
    '  ·  ' + p.records.length + ' records from ' + p.physicalLines +
    ' physical lines  ·  generated ' + longDate(M.runDate) +
    '  ·  client ' + CONFIG.meta.clientVersion;
}
function bottomStrip(root, M, viewName){
  var r = abs(root, X0, 1557, W, 1); r.style.background=PAL.rule;
  var s = abs(root, X0, 1563, W, 20, 'stamp');
  var l = el('span',null,s);
  l.textContent = CONFIG.meta.sensitivity + '  ·  ' + viewName +
    '  ·  sponsor and author names are internal information.';
  l.style.color = PAL.red; l.style.fontWeight='bold';
  var rr = el('span',null,s);
  rr.style.cssText='float:right';
  rr.textContent = filterStatement(M, true);
}
"""

JS_RENDER_DP = r"""
/* ====================================================================== */
/*  DEMAND PROFILE VIEW  (FR-039..FR-089)                                 */
/*  SCOR Plan: 2.1 demand forecasting · 2.2 capacity and resource         */
/*  planning · 2.3 business rules · KPIs from SCOR 7.2 and 8              */
/* ====================================================================== */
var PLOT_X=96, PLOT_R=1686, PLOT_TOP=270, PLOT_H=292;
var PLOT_W=PLOT_R-PLOT_X, PLOT_BOT=PLOT_TOP+PLOT_H, PITCH=PLOT_W/12, BARW=92;
var SVG_TOP=248, SVG_H=330, RX=1706, RW=RIGHT-RX;

function renderDP(root, M){
  root.innerHTML='';
  var T=M.vars, dp=M.dp, n=dp.scope.length;
  var colX = function(i){ return PLOT_X + i*PITCH + PITCH/2; };

  /* ------------------------------------------------------------- header */
  var hdr = abs(root, X0, 24, 1260, 80);
  var ti = el('div','pagetitle',hdr);
  ti.textContent = 'SHORT-TERM PROJECTS PIPELINE — 12-MONTH DEMAND PROFILE';
  var sub = el('div','pagesub',hdr); sub.style.marginTop='3px';
  sub.innerHTML = CONFIG.meta.frameworks.dp +
    '<br>Demand unit: <b>internal delivery labour days by role</b>. Supply analogue: '+
    '<b>Engineer-to-Order</b>, where the scarce input is skilled internal capacity.';

  var lg = abs(root, 1300, 24, 921, 34); lg.style.textAlign='right';
  dp.series.forEach(function(s){
    swatch(lg, s[1], s[1], s[0]+' — '+CONFIG.roleFull[s[0]]);
  });
  var lg2 = abs(root, 1300, 58, 921, 20); lg2.style.textAlign='right';
  var aw = el('span',null,lg2);
  aw.style.cssText='display:inline-flex;align-items:center;gap:4px;margin-right:12px;'+
    'font-size:8px';
  var ab = el('span',null,aw);
  ab.style.cssText='width:11px;height:11px;background:'+PAL.allowance.fill+
    ';border:1px dashed '+PAL.allowance.line;
  txt(el('span',null,aw), 'allowance for unquantified initiatives (base case)');
  var pk = el('span',null,lg2);
  pk.style.cssText='font-size:8px;color:'+PAL.red+';font-weight:bold';
  pk.textContent = '▲ peak month';
  var stamp = abs(root, 1300, 78, 921, 26, 'stamp'); stamp.style.textAlign='right';
  stamp.textContent = provenanceLine(M) + '  ·  run date ' + longDate(M.runDate) +
    '  ·  horizon ' + T.HZ_FROM + ' → ' + T.HZ_TO + '  ·  ' + DPM +
    ' working days = 1 FTE-month';

  /* =========================================== section 1: demand context */
  bandRow(root, 108, '1  ·  DEMAND CONTEXT — WHAT IS BEING PLANNED, AND ON WHAT BASIS',
    'SCOR Plan 2.1. Read this before the chart: the scope filter and the estimate '+
    'coverage govern everything that follows.',
    'FR-073..FR-077', 'Planning Horizon');
  var g1 = grid(6,8);
  CONFIG.dpContext.forEach(function(c,i){
    var b = box(root, g1[i][0], 134, g1[i][1], 76, PAL.surf, PAL.stage['Opportunity'].line);
    headDesc(b, c[0], fill(c[1], T), PAL.stage['Opportunity'].ink);
    if(i===0) fr(b,'FR-073..FR-077','Planning Horizon');
    if(i===1) fr(b,'FR-123..FR-126','Stage Scope Sets');
    if(i===4) fr(b,'FR-052..FR-057','Estimate Tiering');
    if(i===5) fr(b,'FR-039..FR-043','Allowance Pool');
  });

  /* ============================== section 2.1: monthly demand forecast chart */
  bandRow(root, 222, '2.1  ·  MONTHLY DEMAND FORECAST — LABOUR DAYS BY ROLE',
    'Prorated by calendar-day overlap of each initiative’s window. Grey cap = '+
    'allowance for the unquantified. Every segment is directly labelled.',
    'FR-044..FR-051', 'Demand Forecast Chart');

  var svg = svgEl('svg', {width:2245, height:SVG_H, class:'chartsvg'}, root);
  svg.style.top = SVG_TOP+'px';
  var L = function(y){ return y - SVG_TOP; };
  fr(svg, 'FR-044..FR-051', 'Demand Forecast Chart');

  svgEl('text', {x:X0, y:L(262), 'font-size':7.4, fill:PAL.grey}, svg)
    .textContent = 'labour days required per calendar month';

  /* gridlines and y axis */
  for(var v=0; v<=dp.axMax; v+=40){
    var y = PLOT_BOT - (v/dp.axMax)*PLOT_H;
    svgEl('line', {x1:PLOT_X, y1:L(y), x2:PLOT_R, y2:L(y),
      stroke:(v===0?PAL.grey:PAL.rule), 'stroke-width':(v===0?1:0.7)}, svg);
    svgEl('text', {x:PLOT_X-6, y:L(y+2.5), 'font-size':7, fill:PAL.grey,
      'text-anchor':'end'}, svg).textContent = v;
  }

  /* base-case average reference line (FR-050) */
  var ay = PLOT_BOT - (Math.min(dp.avg,dp.axMax)/dp.axMax)*PLOT_H;
  svgEl('line', {x1:PLOT_X, y1:L(ay), x2:PLOT_R, y2:L(ay), stroke:PAL.grey,
    'stroke-width':1, 'stroke-dasharray':'5 3'}, svg);
  svgEl('text', {x:PLOT_R-2, y:L(ay-3), 'font-size':6.8, fill:PAL.grey,
    'text-anchor':'end'}, svg).textContent =
    'base-case average ' + fmt(dp.avg) + ' d/mo (' + fmt(dp.avg/DPM) + ' FTE)';

  /* stacked columns */
  var scale = function(v){ return (v/dp.axMax)*PLOT_H; };
  for(var i=0;i<dp.NM;i++){
    var x = colX(i) - BARW/2, ybase = PLOT_BOT;
    var stack = dp.series.map(function(s){
      return {role:s[0], fill:s[1], ink:s[2], v:dp.profile[s[0]][i]};
    });
    stack.push({role:'Allowance', fill:PAL.allowance.fill, ink:PAL.allowance.ink,
                v:dp.allow['Base case'].perMonth, dash:true});
    stack.forEach(function(sg){
      if(sg.v <= 0.0001) return;
      var h = scale(sg.v), y1 = ybase - h, hh = Math.max(h-2, 1);
      var r = svgEl('rect', {x:x, y:L(y1), width:BARW, height:hh, fill:sg.fill,
        stroke:(sg.dash?PAL.allowance.line:'none'),
        'stroke-width':(sg.dash?1:0),
        'stroke-dasharray':(sg.dash?'4 2':''), class:'seg'}, svg);
      r.dataset.mon = i; r.dataset.role = sg.role;
      /* setAttribute rather than the tabIndex property, because SVG elements do not
         reliably expose that property; without it the chart would be mouse-only
         and the month detail unreachable by keyboard (NFR-041). */
      r.setAttribute('tabindex','0');
      r.setAttribute('role','button');
      r.setAttribute('aria-label', sg.role + ' ' + fmt(sg.v,1) + ' days in ' +
        shortDate(dp.HZ[i]) + ' — open the month');
      if(hh >= 11){
        svgEl('text', {x:colX(i), y:L(y1+hh/2+2.6), 'font-size':7, fill:sg.ink,
          'text-anchor':'middle', 'pointer-events':'none'}, svg).textContent =
          sg.role + ' ' + fmt(sg.v,0);
      }
      ybase = y1;
    });
    /* column total, with the peak marked in MinRes Red (accent use only) */
    var tot = dp.baseM[i], peak = (i===dp.peakIdx);
    var lab = svgEl('text', {x:colX(i), y:L(ybase-4), 'font-size':7.8,
      'text-anchor':'middle', 'font-weight':'bold',
      fill:(peak?PAL.red:PAL.teal)}, svg);
    lab.textContent = (peak?'▲ ':'') + fmt(tot,0) + ' d';
    /* month label */
    svgEl('text', {x:colX(i), y:L(PLOT_BOT+12), 'font-size':7.6,
      'text-anchor':'middle', 'font-weight':(peak?'bold':'normal'),
      fill:(peak?PAL.red:PAL.ink)}, svg).textContent = shortDate(dp.HZ[i]);
  }

  /* under-axis readout rows (FR-049) */
  var rows = [
    ['FTE required (base case)', function(i){ return fmt(dp.baseM[i]/DPM); }, true],
    ['of which estimated', function(i){ return fmt(dp.estM[i]/DPM); }, false],
    ['of which allowance', function(i){
      return fmt(dp.allow['Base case'].perMonth/DPM); }, false]
  ];
  rows.forEach(function(r,k){
    var y = 582 + k*15;
    var lb = abs(root, X0, y, PLOT_X-X0-6, 14, 'pxs');
    lb.style.textAlign='right'; lb.style.color=r[2]?PAL.teal:PAL.grey;
    if(r[2]) lb.style.fontWeight='bold';
    lb.textContent = r[0];
    for(var i2=0;i2<dp.NM;i2++){
      var c = abs(root, colX(i2)-PITCH/2, y, PITCH, 14, 'pxs');
      c.style.textAlign='center'; c.style.color=r[2]?PAL.teal:PAL.grey;
      if(r[2]) c.style.fontWeight='bold';
      c.textContent = r[1](i2);
    }
  });

  /* chart reading note (FR-001..FR-003) */
  var nb = box(root, X0, 631, PLOT_R-X0, 46, '#FFFFFF', PAL.rule);
  fr(nb, 'FR-001..FR-003', 'Colour Vision Safety');
  var nbh = el('div','boxhead',nb); nbh.style.color=PAL.teal;
  nbh.textContent = 'READING THE CHART';
  var nbp = el('div','pxs',nb); nbp.style.marginTop='2px';
  nbp.innerHTML = 'Every segment carries its <b>role code and value directly on the '+
    'segment</b>, so the chart does not depend on colour to be read; segments too short '+
    'to label are read from the register below. The <b>allowance cap is grey with a '+
    'dashed outline</b> — a texture difference, not only a colour difference — because '+
    'it is a parametric estimate and not observed demand. Roles carrying no estimated '+
    'days are absent rather than drawn flat: ' + esc(T.NIL_STMT) + ' MinRes Red appears '+
    'only on the peak marker and on alerts — darkened where an alert is small text on a '+
    'tinted fill, so it still clears 4.5:1 — and never as a data fill.';

  /* ---------------------------------------- scenario panel (FR-086..FR-089) */
  var sp = box(root, RX, SVG_TOP, RW, 20, PAL.teal, PAL.teal);
  sp.style.padding='3px 7px';
  var sph = el('div','boxhead',sp); sph.style.color='#fff';
  sph.textContent = 'SCENARIOS — HOW THE UNQUANTIFIED ARE SIZED';
  CONFIG.scenarios.forEach(function(s,i){
    var y = 270 + i*72;
    var b = box(root, RX, y, RW, 66, s[3], s[4]);
    fr(b, 'FR-086..FR-089', 'Scenario Panel');
    b.dataset.scen = s[0]; b.classList.add('hot'); b.tabIndex=0;
    var A = dp.allow[s[0]];
    var h = el('div','boxhead',b); h.style.color=s[5];
    h.innerHTML = s[0].toUpperCase() + ' &nbsp;<span style="font-weight:normal">' +
      s[1] + '</span>';
    var p = el('div','pxs',b); p.style.marginTop='2px';
    p.innerHTML = 'Each of the <b>' + esc(T.N_UNQ) + '</b> unquantified initiatives sized '+
      'at <b>' + fmt(A.per) + ' days</b> (' + (s[2]==='q1'?'Q1':(s[2]==='q2'?'median':'Q3')) +
      ' of the ' + esc(T.N_EST) + ' estimated) → allowance pool <b>' + fmt(A.pool) +
      ' d</b>, spread evenly at ' + fmt(A.perMonth) + ' d/mo.<br>' +
      '<b>Total in-horizon demand ' + fmt(A.total) + ' days</b> = ' + fmt(dp.estInHz) +
      ' estimated + ' + fmt(A.pool) + ' allowance &nbsp;·&nbsp; average <b>' +
      fmt(A.total/dp.NM/DPM) + ' FTE</b>, peak-month <b>' +
      fmt((dp.estM[dp.peakIdx]+A.perMonth)/DPM) + ' FTE</b>.';
  });
  var rc = box(root, RX, 486, RW, 92, '#FFFFFF', PAL.red);
  rc.style.borderWidth='0 0 0 3px';
  fr(rc, 'FR-052..FR-057', 'Estimate Tiering');
  var rch = el('div','boxhead',rc); rch.style.color=PAL.red;
  rch.textContent = 'RECONCILIATION & ESTIMATE TIERS';
  var tierN = {A:0,B:0,C:0};
  dp.proj.forEach(function(p){ tierN[p.tier]++; });
  var rcp = el('div','pxs',rc); rcp.style.marginTop='3px';
  rcp.innerHTML =
    '<b>' + esc(T.EST_TOTAL) + ' estimated days</b> total, of which <b>' +
    esc(T.EST_IN_HZ) + '</b> fall inside the horizon and <b>' + esc(T.EST_OUT) +
    '</b> outside it (windows that start before ' + esc(T.HZ_FROM) + ' or run past ' +
    esc(T.HZ_TO) + '). Those two figures reconcile to the total by construction.<br>' +
    '<b>Tier A</b> ' + tierN.A + ' — start + duration + estimate, placed as dated. ' +
    '<b>Tier B</b> ' + tierN.B + ' — start, no duration, given the portfolio-median ' +
    esc(T.MED_DUR) + ' months. <b>Tier C</b> ' + tierN.C + ' — estimate only, placed '+
    'from horizon month 1 at median duration. <b>Tier D</b> ' + esc(T.N_UNQ) +
    ' — no estimate at all, carried in the allowance pool above and <b>not</b> shown '+
    'as a named initiative in the chart.';

  /* ========================= section 2.2: capacity and resource planning */
  bandRow(root, 689, '2.2  ·  CAPACITY & RESOURCE PLANNING — BY ROLE, BY INITIATIVE',
    'SCOR Plan 2.2. Establishment and gap are deliberately blank: the source carries no '+
    'team capacity, so no gap can honestly be calculated.',
    'FR-083..FR-085', 'Role Capacity Table');

  /* --- A: role capacity table ------------------------------------------- */
  var A_X=X0, A_W=560;
  var ah = abs(root, A_X, 715, A_W, 14, 'boxhead');
  ah.style.color=PAL.teal;
  ah.textContent = 'A · DEMAND BY ROLE ACROSS THE HORIZON';
  var atw = abs(root, A_X, 732, A_W, 269);
  fr(atw, 'FR-083..FR-085', 'Role Capacity Table');
  var at = el('table','tbl',atw);
  var ROLE_COLS = [
    ['Role','role'], ['Days in horizon','days'], ['Avg FTE','avg'],
    ['Peak d/mo','peak'], ['Peak month','pm'], ['Peak FTE','pfte'],
    ['Establishment','est'], ['Gap','gap']
  ];
  var atr = el('tr',null,el('thead',null,at));
  ROLE_COLS.forEach(function(c){
    var th = el('th',null,atr);
    th.textContent = c[0];
    if(c[1]==='est'||c[1]==='gap'){ th.style.color=PAL.grey; th.style.cursor='default'; }
    else { th.dataset.sortRole = c[1]; sortable(th, c[0], M.filters.roleSort===c[1],
             M.filters.roleDesc);
      if(M.filters.roleSort===c[1]){
        var ind=el('span','ind',th);
        ind.textContent = M.filters.roleDesc?' ▼':' ▲'; }
    }
  });
  var atb = el('tbody',null,at);
  var roleRows = ROLES.slice();
  var rkey = {role:function(c){return c;}, days:function(c){return -dp.roleTot[c];},
    avg:function(c){return -dp.roleTot[c];}, peak:function(c){return -dp.rolePeak[c].days;},
    pm:function(c){return dp.rolePeak[c].idx;},
    pfte:function(c){return -dp.rolePeak[c].days;}}[M.filters.roleSort] ||
    function(c){return -dp.roleTot[c];};
  roleRows.sort(function(a,b){
    var u=rkey(a), v=rkey(b); return (u<v?-1:(u>v?1:0)); });
  if(M.filters.roleDesc) roleRows.reverse();
  roleRows.forEach(function(c){
    var t = dp.roleTot[c], nil = t<=0.0001;
    var tr = el('tr','hot',atb); tr.dataset.role=c; tr.tabIndex=0;
    var td0 = el('td',null,tr);
    td0.innerHTML = '<b>'+c+'</b> <span style="color:'+PAL.grey+'">'+
      esc(CONFIG.roleFull[c])+'</span>';
    if(nil){
      ['—','—','—','—','—'].forEach(function(){ el('td','n blankcol',tr).textContent='—'; });
      var g1c=el('td','n blankcol',tr); g1c.textContent='—';
      var g2c=el('td','n blankcol',tr); g2c.textContent='—';
      td0.innerHTML += ' <span style="color:'+PAL.grey+'">nil</span>';
      return;
    }
    el('td','n',tr).textContent = fmt(t);
    el('td','n',tr).textContent = fmt(t/dp.NM/DPM);
    el('td','n',tr).textContent = fmt(dp.rolePeak[c].days);
    el('td','n',tr).textContent = shortDate(dp.HZ[dp.rolePeak[c].idx]);
    el('td','n',tr).textContent = fmt(dp.rolePeak[c].days/DPM);
    var e1=el('td','n blankcol',tr); e1.textContent='to confirm';
    var e2=el('td','n blankcol',tr); e2.textContent='to confirm';
  });
  var an = abs(root, A_X, 960, A_W, 41, 'pxs');
  an.style.color=PAL.grey;
  an.innerHTML = 'Days shown are <b>estimated</b> demand only — the allowance for the '+
    esc(T.N_UNQ) + ' unquantified initiatives is not attributable to a role and is '+
    'excluded here. <b>Establishment and Gap are blank by design</b>: the extract '+
    'carries no team capacity, so a gap figure would be invented. Supply it and both '+
    'columns compute.';

  /* --- B: estimated initiative register (FR-058..FR-061) ---------------- */
  var B_X=594, B_W=1000;
  var bh = abs(root, B_X, 715, B_W, 14, 'boxhead'); bh.style.color=PAL.teal;
  bh.textContent = 'B · ESTIMATED INITIATIVE REGISTER — ' + dp.est.length +
    ' OF ' + n + ' IN SCOPE';
  var btw = abs(root, B_X, 732, B_W, 269);
  fr(btw, 'FR-058..FR-061', 'Initiative Register');
  var bt = el('table','tbl',btw);
  var RCOLS = [['Initiative','title'],['Stage','stage'],['Tier','tier'],
    ['Start','start'],['Dur','dur'],['Est days','days'],['In horizon','inhz']];
  var btr = el('tr',null,el('thead',null,bt));
  RCOLS.forEach(function(c){
    var th = el('th',null,btr); th.textContent=c[0]; th.dataset.sortReg=c[1];
    sortable(th, c[0], M.filters.regSort===c[1], M.filters.regDesc);
    if(M.filters.regSort===c[1]){
      var ind=el('span','ind',th); ind.textContent = M.filters.regDesc?' ▼':' ▲'; }
  });
  for(var mi=0; mi<dp.NM; mi++){
    var th2 = el('th',null,btr); th2.style.textAlign='right';
    th2.textContent = shortDate(dp.HZ[mi]).slice(0,3);
    th2.style.cursor='default';
    if(mi===dp.peakIdx) th2.style.color=PAL.red;
  }
  var btb = el('tbody',null,bt);
  var regKey = {
    title:function(p){return p.rec.title.toLowerCase();},
    stage:function(p){return p.rec.stage;},
    tier:function(p){return p.tier;},
    start:function(p){return p.winStart.getTime();},
    dur:function(p){return -p.winDur;},
    days:function(p){return -p.rec.days;},
    inhz:function(p){return -p.inHz;}
  }[M.filters.regSort] || function(p){return -p.rec.days;};
  var regRows = dp.proj.slice().sort(function(a,b){
    var u=regKey(a), v=regKey(b); return (u<v?-1:(u>v?1:0)); });
  if(M.filters.regDesc) regRows.reverse();
  var over = {}; dp.overrun.forEach(function(p){ over[p.rec.id]=1; });
  var CAPR = 24;
  regRows.slice(0,CAPR).forEach(function(p){
    var st = PAL.stage[p.rec.stage];
    var tr = el('tr','hot',btb); tr.dataset.rid=p.rec.id; tr.tabIndex=0;
    var t0 = el('td',null,tr);
    if(over[p.rec.id]){
      var fl = el('span',null,t0); fl.style.cssText='color:'+PAL.red+';font-weight:bold';
      fl.textContent='▲ ';
    }
    t0.appendChild(document.createTextNode(p.rec.title));
    if(!p.rec.funded){
      var uf=el('span',null,t0); uf.style.color=PAL.grey; uf.textContent=' · unfunded'; }
    var t1 = el('td',null,tr); t1.textContent=p.rec.stage; t1.style.color=st.ink;
    el('td',null,tr).textContent = p.tier;
    var t3 = el('td',null,tr);
    t3.textContent = shortDate(p.winStart);
    if(p.tier!=='A'){ t3.style.color=PAL.grey; t3.style.fontStyle='italic'; }
    var t4 = el('td','n',tr); t4.textContent = fmt(p.winDur);
    if(!p.rec.dur){ t4.style.color=PAL.grey; t4.style.fontStyle='italic'; }
    el('td','n',tr).textContent = fmt(p.rec.days);
    el('td','n',tr).textContent = fmt(p.inHz);
    for(var k=0;k<dp.NM;k++){
      var td = el('td','n',tr);
      td.textContent = p.months[k]>0.05 ? fmt(p.months[k],0) : '';
      if(k===dp.peakIdx && p.months[k]>0.05) td.style.color=PAL.red;
    }
  });
  var bn = abs(root, B_X, 960, B_W, 41, 'pxs'); bn.style.color=PAL.grey;
  bn.innerHTML = (regRows.length>CAPR ?
      '<b>'+(regRows.length-CAPR)+' further estimated initiatives are not shown</b> at '+
      'this page height — they are in the drill-down and in every total. ' : '') +
    'Italic start and duration are <b>imputed</b>, not sourced: Tier B takes the '+
    'portfolio-median ' + esc(T.MED_DUR) + ' months, Tier C is placed from horizon '+
    'month 1. <b>▲</b> marks an In Progress initiative whose estimated window closed '+
    'before the horizon opened — stage and dates disagree, and the dates are what the '+
    'plan uses.';

  /* --- C: unquantified pool (FR-039..FR-043) --------------------------- */
  var C_X=1604, C_W=617;
  var ch = abs(root, C_X, 715, C_W, 14, 'boxhead'); ch.style.color=PAL.red;
  ch.textContent = 'C · UNQUANTIFIED — ' + dp.unq.length + ' OF ' + n +
    ' CARRY NO ESTIMATE';
  var cw = abs(root, C_X, 732, C_W, 269);
  fr(cw, 'FR-039..FR-043', 'Allowance Pool');
  var cols = grid(3, 8, 0, C_W);
  var per = Math.ceil(dp.unq.length/3);
  var unqSorted = sortItems(dp.unq.map(function(r){return r;}), M.filters.order);
  cols.forEach(function(cg, ci){
    var wrap = abs(cw, cg[0], 0, cg[1], 269);
    unqSorted.slice(ci*per, (ci+1)*per).forEach(function(r, ri){
      var row = abs(wrap, 0, ri*23, cg[1], 22, 'pxs');
      row.style.cursor='pointer'; row.dataset.rid=r.id; row.tabIndex=0;
      row.style.borderBottom='1px solid #F2F2F2';
      var t = el('div',null,row);
      t.style.cssText='white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'+
        'font-weight:bold';
      t.textContent = r.title;
      var s = el('div',null,row);
      s.style.cssText='color:'+PAL.grey+';white-space:nowrap;overflow:hidden;'+
        'text-overflow:ellipsis';
      s.textContent = (r.sponsor||'no sponsor') + ' · ' + r.stage +
        (r.funded?' · funded':' · unfunded');
    });
  });
  var cn = abs(root, C_X, 960, C_W, 41, 'pxs'); cn.style.color=PAL.grey;
  cn.innerHTML = 'These carry <b>no labour estimate in any role</b>, so they cannot be '+
    'placed by name or by month. They are sized parametrically at the Q1 / median / Q3 '+
    'of the ' + esc(T.N_EST) + ' estimated initiatives and spread evenly across the '+
    'horizon. <b>This is the single largest source of error on the page</b> and the '+
    'first thing to fix.';

  /* ============================== section 2.3: planning business rules */
  bandRow(root, 1013, '2.3  ·  PLANNING BUSINESS RULES — HOW THE PROFILE IS USED',
    'SCOR Plan 2.3. Each rule states its trigger, the rule itself, and why this extract '+
    'makes it necessary.', 'FR-067..FR-072', 'Planning Business Rules');
  var g3 = grid(4,10);
  CONFIG.planningRules.forEach(function(r,i){
    var b = box(root, g3[i][0], 1039, g3[i][1], 140, '#FFFFFF', PAL.teal);
    b.style.borderWidth='0 0 0 3px';
    fr(b, 'FR-067..FR-072', 'Planning Business Rules');
    var h = el('div','boxhead',b); h.style.color=PAL.teal;
    h.innerHTML = '<span style="color:'+PAL.red+'">'+r[0]+'</span> &nbsp;'+r[1];
    var p = el('div','pxs',b); p.style.marginTop='3px'; p.innerHTML = fill(r[2], T);
  });

  /* ================ section 3: risks and measures (FR-078..FR-082) */
  bandRow(root, 1191, '3  ·  RISKS TO THIS FORECAST & THE MEASURES THAT TRACK THEM',
    'Risk per SCOR 8; KPIs per SCOR 7.2. Severity colours are held distinct from the '+
    'stage colours used elsewhere.', 'FR-078..FR-082', 'Risk and Measure Panels');
  var R_W=1350, K_X=X0+R_W+10, K_W=W-R_W-10;
  var rw2 = abs(root, X0, 1217, R_W, 168);
  fr(rw2, 'FR-078..FR-082', 'Risk and Measure Panels');
  CONFIG.risks.forEach(function(r,i){
    var sv = PAL.severity[r[1]];
    var y = i*34;
    var b = abs(rw2, 0, y, R_W, 32, 'box');
    b.style.background=sv[0]; b.style.borderColor=sv[1]; b.style.padding='3px 6px';
    var idb = el('span',null,b);
    idb.style.cssText='font-weight:bold;font-size:8px;color:'+sv[2];
    idb.textContent = r[0] + '  ' + r[1].toUpperCase() + '  ·  ' + r[2] + ' — ';
    var tx = el('span','pxs',b);
    tx.innerHTML = fill(r[3], T) + ' <b style="color:'+sv[2]+'">Action:</b> ' +
      fill(r[4], T);
  });
  var kw = abs(root, K_X, 1217, K_W, 168);
  fr(kw, 'FR-078..FR-082', 'Risk and Measure Panels');
  var gk = grid(3, 8, 0, K_W);
  CONFIG.kpis.forEach(function(k,i){
    var col = i%3, row = Math.floor(i/3);
    var b = abs(kw, gk[col][0], row*86, gk[col][1], 80, 'box');
    b.style.background=PAL.surf2; b.style.borderColor=PAL.rule;
    var h = el('div','boxhead',b); h.style.color=PAL.teal; h.innerHTML=k[0];
    var v = el('div',null,b);
    v.style.cssText='font-size:17px;font-weight:bold;margin:1px 0;color:'+k[3];
    v.innerHTML = fill(k[1], T);
    var tg = el('div','pxs',b); tg.style.color=PAL.grey; tg.innerHTML=k[2];
    var d = el('div','pxs',b); d.style.marginTop='2px'; d.innerHTML=fill(k[4], T);
  });

  /* ---------------------------------------------------------- footer */
  bandRow(root, 1397, 'METHOD, ASSUMPTIONS, WHAT IS NOT HERE & NEXT STEPS',
    'Read this before acting on any number above.', 'FR-100..FR-103',
    'Provenance Stamping');
  var fb = box(root, X0, 1423, W, 122, '#FFFFFF', PAL.red);
  fb.style.borderWidth='0 0 0 3px';
  fr(fb, 'FR-100..FR-103', 'Provenance Stamping');
  var fbp = el('div','pxs',fb); fbp.innerHTML = fill(CONFIG.dpFooter, T);

  bottomStrip(root, M, 'Demand Profile');
}
"""

# ================================================================ section 6 — app.js
JS_APP = r"""
/* ================================================================== state */
var STATE = {
  view:'ba', loaded:false, annot:false, zoom:'1.5', maxCanvas:false, fixedDate:false,
  parsed:null, base:null, M:null,
  filters:{stage:'', sponsor:'', author:'', cap:'', plat:'', funding:'', role:'', q:'',
           order:'stage', roleSort:'days', roleDesc:false, regSort:'days', regDesc:false}
};
/* The authority draw.io pages were cut at this run date. The toggle exists so a reviewer
   can prove the client is deterministic (NFR-029) and reconcile against those pages. */
var FIXED_RUN_DATE = mkd(2026, 7, 13);
function runDate(){
  if(STATE.fixedDate) return FIXED_RUN_DATE;
  var d = new Date();
  return mkd(d.getFullYear(), d.getMonth(), d.getDate());
}
function $(id){ return document.getElementById(id); }
function on(id, ev, fn){ var e=$(id); if(e) e.addEventListener(ev, fn); }

/* =============================================== filter statement (FR-168..171) */
/* Takes the filter object rather than reading STATE, so that the statement printed on a
   canvas always describes the model that canvas was built from. A page that misstates its
   own scope is worse than no page. */
function activeFilters(f){
  f = f || STATE.filters;
  var out=[];
  if(f.stage)   out.push(['Stage', f.stage]);
  if(f.sponsor) out.push(['Sponsor', f.sponsor]);
  if(f.author)  out.push(['Author', f.author]);
  if(f.cap)     out.push(['Capability', f.cap]);
  if(f.plat)    out.push(['Enabling group', f.plat]);
  if(f.funding) out.push(['Funding', f.funding==='funded'?'budget approved':
                          'no approved budget']);
  if(f.role)    out.push(['Carries days for role', f.role]);
  if(f.q)       out.push(['Title contains', f.q]);
  return out;
}
function filterStatement(M, short){
  var a = activeFilters(M.filters);
  var scope = (STATE.view==='ba')
    ? M.ba.active.length + ' active initiatives of ' + M.parsed.records.length + ' loaded'
    : M.dp.scope.length + ' in-scope initiatives of ' + M.parsed.records.length +
      ' loaded';
  if(!a.length) return 'No filter in force  ·  ' + scope;
  var s = a.map(function(p){ return p[0]+' = '+p[1]; }).join('  ·  ');
  return (short?'':'Filtered: ') + s + '  ·  ' + scope;
}
function renderBanner(){
  var M = STATE.M, b = $('banner');
  b.innerHTML='';
  var a = activeFilters();
  var lead = el('span','lead',b);
  lead.textContent = a.length ? 'Filtered' : 'No filter in force';
  a.forEach(function(p){
    var c = el('span','chip',b);
    c.textContent = p[0] + ' = ' + p[1];
  });
  var count = el('span',null,b);
  var n = (STATE.view==='ba') ? M.ba.active.length : M.dp.scope.length;
  var nb = (STATE.view==='ba') ? STATE.base.ba.active.length : STATE.base.dp.scope.length;
  count.innerHTML = 'showing <b>' + n + '</b> of <b>' + M.parsed.records.length +
    ' loaded</b> — ' + (STATE.view==='ba'
      ? 'the active set (' + CONFIG.scope.active.join(', ') + ')'
      : 'the demand set (' + CONFIG.scope.demand.join(', ') + ')');
  if(nb && n < nb/2){
    var w = el('span','warn',b);
    w.textContent = 'This filter removes ' + (nb-n) + ' of ' + nb + ' (' +
      pct(nb-n, nb, 0) + '%). Totals, quartiles and every measure below are recomputed '+
      'for the filtered set only.';
  }
  if(!n){
    var w2 = el('span','warn',b);
    w2.textContent = 'Nothing is in scope under this filter, so there is nothing to '+
      'plan. Reset, or widen the filter.';
  }
  var sn = el('span','sortnote',b);
  sn.textContent = (STATE.view==='ba')
    ? 'chips ordered by ' + STATE.filters.order
    : 'register ordered by ' + STATE.filters.regSort +
      (STATE.filters.regDesc?' (descending)':'') +
      ', roles by ' + STATE.filters.roleSort;
}

/* ============================================================ filter rail */
function optionsFor(key){
  var c={};
  STATE.parsed.records.forEach(function(r){
    if(CONFIG.scope.active.indexOf(r.stage)<0) return;
    var v = key(r); if(v) c[v]=(c[v]||0)+1;
  });
  return Object.keys(c).sort().map(function(k){ return [k, c[k]]; });
}
function sel(parent, id, label, opts, cur, blank){
  var lb = el('label',null,parent); lb.textContent=label; lb.htmlFor=id;
  var s = el('select',null,parent); s.id=id;
  var o0 = el('option',null,s); o0.value=''; o0.textContent=blank;
  opts.forEach(function(p){
    var o = el('option',null,s);
    /* p = [value, count-or-null, display-label]. The value is always the raw model
       value so that passes() can compare it directly; only the label is prettified. */
    o.value = p[0];
    o.textContent = (p[2]!==undefined?p[2]:p[0]) +
      (p[1]!==null&&p[1]!==undefined?('  ('+p[1]+')'):'');
    if(cur===p[0]) o.selected=true;
  });
  return s;
}
function buildRail(){
  var r = $('rail'), f = STATE.filters;
  r.innerHTML='';
  var h = el('h3',null,r); h.textContent='Filters';
  fr(r, 'FR-162..FR-167', 'Filter Controls');

  var stages = (STATE.view==='ba'?CONFIG.scope.active:CONFIG.scope.demand)
    .map(function(s){
      var n = STATE.parsed.records.filter(function(x){return x.stage===s;}).length;
      return [s, n]; });
  sel(r,'f-stage','Stage', stages, f.stage, 'All in-scope stages')
    .addEventListener('change', function(e){ f.stage=e.target.value; refresh(); });

  sel(r,'f-sponsor','Sponsor', optionsFor(function(x){return x.sponsor;}), f.sponsor,
    'Any sponsor').addEventListener('change',
    function(e){ f.sponsor=e.target.value; refresh(); });

  sel(r,'f-author','Author', optionsFor(function(x){return x.author;}), f.author,
    'Any author').addEventListener('change',
    function(e){ f.author=e.target.value; refresh(); });

  sel(r,'f-cap','EMMM capability',
    CONFIG.capabilities.map(function(c){ return [c.key, null]; }), f.cap,
    'Any capability').addEventListener('change',
    function(e){ f.cap=e.target.value; refresh(); });

  /* The option VALUE must be the decoded key, because that is what parseSnapshot stored
     on the record and what passes() compares against. */
  sel(r,'f-plat','Enabling platform group',
    CONFIG.platform.map(function(p){ return [deent(p.key), null]; }), f.plat,
    'Any group').addEventListener('change',
    function(e){ f.plat=e.target.value; refresh(); });

  sel(r,'f-fund','Funding',
    [['funded', null, 'budget approved'], ['unfunded', null, 'no approved budget']],
    f.funding, 'Funded and unfunded')
    .addEventListener('change', function(e){ f.funding=e.target.value; refresh(); });

  if(STATE.view==='dp'){
    sel(r,'f-role','Carries days for role',
      ROLES.map(function(c){ return [c, null, c + ' — ' + CONFIG.roleFull[c]]; }),
      f.role, 'Any role').addEventListener('change',
      function(e){ f.role=e.target.value; refresh(); });
  }

  var lb = el('label',null,r); lb.textContent='Title contains'; lb.htmlFor='f-q';
  var q = el('input',null,r); q.type='text'; q.id='f-q'; q.value=f.q;
  q.placeholder='free text';
  q.addEventListener('input', function(e){ f.q=e.target.value; refresh(); });

  var h2 = el('h3',null,r); h2.textContent='Ordering';
  fr(h2, 'FR-180..FR-183', 'Sorting and Ranking');
  sel(r,'f-order','Order initiative chips by',
    [['stage', null, 'stage, then title'], ['title', null, 'title, A to Z'],
     ['days', null, 'estimated days, largest first'],
     ['start', null, 'estimated start, earliest first'],
     ['sponsor', null, 'sponsor, then title']], f.order, '')
    .addEventListener('change', function(e){ f.order=e.target.value; refresh(); });
  $('f-order').options[0].remove();            /* ordering is never "none" */

  var row = el('div','row',r);
  var rb = el('button',null,row); rb.type='button'; rb.textContent='Reset all filters';
  rb.addEventListener('click', function(){
    STATE.filters = {stage:'',sponsor:'',author:'',cap:'',plat:'',funding:'',role:'',q:'',
      order:f.order, roleSort:f.roleSort, roleDesc:f.roleDesc,
      regSort:f.regSort, regDesc:f.regDesc};
    refresh(true);
  });

  var h3 = el('h3',null,r); h3.textContent='Reading now';
  var c = el('div','count',r);
  var M = STATE.M;
  c.innerHTML = (STATE.view==='ba')
    ? '<b>'+M.ba.active.length+'</b> active · '+
      CONFIG.scope.active.map(function(s){ return (M.ba.byStage[s]||0)+' '+s; })
        .join(' · ')+'<br><b>'+M.ba.dead.length+'</b> omitted as Complete or Cancelled'+
      '<br><b>'+M.ba.withEst+'</b> carry an estimate, '+fmt(M.ba.totalDays)+' days'
    : '<b>'+M.dp.scope.length+'</b> in scope · <b>'+M.dp.est.length+'</b> estimated ('+
      M.vars.COVERAGE+'%) · <b>'+M.dp.unq.length+'</b> unquantified<br>'+
      fmt(M.dp.estTotal)+' estimated days, '+fmt(M.dp.estInHz)+' in horizon<br>'+
      'peak '+M.vars.PEAK_MONTH+' at '+M.vars.PEAK_DAYS+' d ('+M.vars.PEAK_FTE+' FTE)';
  var dq = el('div','count',r);
  var nd = M.ba.defects;
  dq.innerHTML = '<span class="railwarn">Data quality:</span> '+nd.noSponsor.length+
    ' no sponsor · '+nd.noAuthor.length+' no author · '+nd.noStart.length+
    ' no start · '+nd.noEst.length+' no estimate';
}

/* ================================================================== hover */
function showTip(html, ev){
  var t = $('tip'); t.innerHTML = html; t.classList.remove('hide');
  var r = t.getBoundingClientRect();
  var x = ev.clientX + 16, y = ev.clientY + 16;
  if(x + r.width > window.innerWidth - 8) x = ev.clientX - r.width - 16;
  if(y + r.height > window.innerHeight - 8) y = ev.clientY - r.height - 16;
  t.style.left = Math.max(4,x)+'px'; t.style.top = Math.max(4,y)+'px';
}
function hideTip(){ $('tip').classList.add('hide'); }
function recTip(r){
  var M = STATE.M;
  var rows = ROLES.filter(function(c){ return r.labour[c]>0; })
    .map(function(c){ return c+' '+fmt(r.labour[c]); }).join(' · ');
  var h = '<div class="tt">'+esc(r.title)+'</div><div class="tr">';
  h += '<b>'+esc(r.stage)+'</b>'+(r.funded?' · budget approved':
    ' · <span class="tk">no approved budget</span>')+'<br>';
  h += 'Sponsor: '+(r.sponsor?'<b>'+esc(r.sponsor)+'</b>':
    '<span class="tk">none — nobody accountable for the benefit</span>')+'<br>';
  h += 'Author: '+(r.author?esc(r.author):'<span class="tk">none</span>')+'<br>';
  h += 'Start: '+(r.start?'<b>'+longDate(r.start)+'</b>':
    '<span class="tk">none</span>')+
    ' · duration '+(r.dur?fmt(r.dur)+' months':'<span class="tk">none</span>')+'<br>';
  h += 'Estimate: '+(r.hasEst?'<b>'+fmt(r.days)+' days</b> — '+rows:
    '<span class="tk">no estimate in any role</span>')+'<br>';
  h += 'Capability: '+(r.cap?esc(r.cap):'—')+
       (r.plat?' · platform group: '+esc(deent(r.plat)):'')+'<br>';
  h += '<i>Record '+r.line+' of the extract. Click for the full source record.</i>';
  return h + '</div>';
}
function monTip(i){
  var dp = STATE.M.dp;
  var h = '<div class="tt">'+shortDate(dp.HZ[i])+' — base case '+fmt(dp.baseM[i])+
    ' days ('+fmt(dp.baseM[i]/DPM)+' FTE)</div><div class="tr">';
  dp.series.forEach(function(s){
    var v = dp.profile[s[0]][i];
    if(v>0.0001) h += '<b>'+s[0]+'</b> '+fmt(v)+' d ('+fmt(v/DPM)+' FTE) — '+
      esc(CONFIG.roleFull[s[0]])+'<br>';
  });
  h += '<span class="tk">Allowance '+fmt(dp.allow['Base case'].perMonth)+
    ' d</span> — the unattributed share for the '+dp.unq.length+
    ' unquantified initiatives<br>';
  var contrib = dp.proj.filter(function(p){ return p.months[i]>0.05; })
    .sort(function(a,b){ return b.months[i]-a.months[i]; });
  if(contrib.length){
    h += '<br><b>Estimated initiatives in this month</b><br>';
    contrib.slice(0,8).forEach(function(p){
      h += '· '+esc(p.rec.title)+' — '+fmt(p.months[i])+' d<br>'; });
    if(contrib.length>8) h += '<i>and '+(contrib.length-8)+' more</i><br>';
  } else {
    h += '<br><span class="tk">No estimated initiative falls in this month — the column '+
      'is allowance only.</span><br>';
  }
  h += '<i>Click to list every initiative in this month.</i></div>';
  return h;
}
/* The one list of what carries detail, and the one list of what opens a drill-down.
   Named once so hover, focus and click can never drift apart. */
var HOVER_SEL = '[data-rid],[data-mon],[data-cap],[data-plat],[data-role],'+
                '[data-scen],.frbadge';
var CLICK_SEL = '[data-rid],[data-mon],[data-cap],[data-plat],[data-role],'+
                '[data-scen],[data-more]';
function bindHover(root){
  root.addEventListener('mouseover', function(e){
    var t = e.target.closest ? e.target.closest(HOVER_SEL) : null;
    if(!t) return;
    if(t.classList.contains('frbadge')){
      showTip('<div class="tt">'+esc(t.dataset.ids)+'</div><div class="tr">'+
        esc(t.dataset.label)+' — this region satisfies these functional requirements. '+
        'The coverage checklist below the canvas lists every requirement and its '+
        'status.</div>', e);
      return;
    }
    if(t.dataset.rid!==undefined){
      var r = STATE.parsed.records[+t.dataset.rid];
      if(r) showTip(recTip(r), e);
    } else if(t.dataset.mon!==undefined){
      showTip(monTip(+t.dataset.mon), e);
    } else if(t.dataset.cap){
      var c = STATE.M.ba.caps.filter(function(x){return x.cfg.key===t.dataset.cap;})[0];
      if(c) showTip('<div class="tt">'+esc(c.cfg.key)+' — '+c.items.length+
        ' active</div><div class="tr">'+deent(c.cfg.cover)+'<br><br>'+
        deent(c.cfg.verdict)+'<br><br><i>Click to list the initiatives serving this '+
        'capability.</i></div>', e);
    } else if(t.dataset.plat){
      var p = STATE.M.ba.plats.filter(function(x){
        return deent(x.cfg.key)===t.dataset.plat;})[0];
      if(p) showTip('<div class="tt">'+esc(deent(p.cfg.key))+' — '+p.items.length+
        '</div><div class="tr">'+deent(p.cfg.note)+
        '<br><br><i>Click to list this group.</i></div>', e);
    } else if(t.dataset.role){
      var c2 = t.dataset.role, dp = STATE.M.dp;
      if(dp.roleTot[c2]!==undefined) showTip('<div class="tt">'+esc(c2)+' — '+
        esc(CONFIG.roleFull[c2])+'</div><div class="tr">'+
        (dp.roleTot[c2]>0.0001
          ? fmt(dp.roleTot[c2])+' estimated days in the horizon · average '+
            fmt(dp.roleTot[c2]/dp.NM/DPM)+' FTE · peak '+fmt(dp.rolePeak[c2].days)+
            ' d in '+shortDate(dp.HZ[dp.rolePeak[c2].idx])+' ('+
            fmt(dp.rolePeak[c2].days/DPM)+' FTE)<br><i>Click to list the initiatives '+
            'drawing on this role.</i>'
          : '<span class="tk">No estimated days in any in-scope initiative.</span> The '+
            'series is absent from the chart rather than drawn flat, so the chart does '+
            'not imply a capacity call that the data cannot support.')+'</div>', e);
    } else if(t.dataset.scen){
      var A = STATE.M.dp.allow[t.dataset.scen];
      showTip('<div class="tt">'+esc(t.dataset.scen)+'</div><div class="tr">'+
        'Allowance pool '+fmt(A.pool)+' d = '+fmt(A.per)+' d × '+STATE.M.dp.unq.length+
        ' unquantified.<br>Total in-horizon demand '+fmt(A.total)+' d, average '+
        fmt(A.total/STATE.M.dp.NM/DPM)+' FTE.<br><i>Click to see the pool this '+
        'scenario sizes.</i></div>', e);
    }
  });
  root.addEventListener('mouseout', hideTip);
  /* Focus shows exactly what hover shows, by replaying the pointer event from the
     centre of the focused element rather than repeating the branch list above. One
     definition, so a detail panel cannot exist for the mouse and not the keyboard
     (NFR-017, NFR-041). */
  root.addEventListener('focusin', function(e){
    var t = e.target;
    if(!t || !t.getBoundingClientRect) return;
    if(!t.closest || !t.closest(HOVER_SEL)) return;
    var b = t.getBoundingClientRect();
    t.dispatchEvent(new MouseEvent('mouseover', {bubbles:true,
      clientX: b.left + b.width/2, clientY: b.bottom}));
  });
  root.addEventListener('focusout', hideTip);
}

/* ============================================ drill-down: drawer (FR-157..161) */
function openDrawer(){ $('scrim').classList.remove('hide');
  $('drawer').classList.remove('hide'); hideTip(); }
function closeDrawer(){ $('scrim').classList.add('hide');
  $('drawer').classList.add('hide'); }
function kvRow(tb, k, v, miss){
  var tr = el('tr',null,tb);
  el('th',null,tr).textContent = k;
  var td = el('td', miss?'miss':null, tr);
  td.textContent = (v===''||v===null||v===undefined) ? '(empty)' : v;
  return tr;
}
function showRecord(r){
  var M = STATE.M, dp = M.dp;
  $('dw-title').textContent = r.title || '(untitled)';
  var sub = $('dw-sub'); sub.innerHTML='';
  var st = PAL.stage[r.stage] || {fill:'#EEE',line:'#CCC',ink:'#333'};
  var sb = el('span','dstage',sub);
  sb.textContent = r.stage; sb.style.background=st.fill;
  sb.style.borderColor=st.line; sb.style.color=st.ink;
  sub.appendChild(document.createTextNode('  record ' + r.line + ' of ' +
    SNAPSHOT.name + '  ·  ' + (r.funded?'budget approved':'no approved budget')));

  var b = $('dw-body'); b.innerHTML='';
  var g = el('div','twocol',b);

  /* --- left: raw source values --------------------------------------- */
  var L = el('div','dsec',g);
  el('h4',null,L).textContent = 'Raw source values, exactly as read';
  var lt = el('table','kv',L); var ltb = el('tbody',null,lt);
  SNAPSHOT.fields.forEach(function(f){
    if(f==='High-Level Summary') return;
    kvRow(ltb, f, r.raw[f], r.raw[f]==='');
  });

  /* --- right: derived values ----------------------------------------- */
  var R = el('div','dsec',g);
  el('h4',null,R).textContent = 'Derived values, and how they were derived';
  var rt = el('table','kv',R); var rtb = el('tbody',null,rt);
  kvRow(rtb, 'Stage scope', CONFIG.scope.active.indexOf(r.stage)>=0
    ? 'active — appears on Business Architecture'
    : 'omitted from Business Architecture');
  kvRow(rtb, 'Demand scope', CONFIG.scope.demand.indexOf(r.stage)>=0
    ? 'in scope — appears on Demand Profile'
    : 'excluded from Demand Profile by the stage filter');
  kvRow(rtb, 'Funding flag', r.funded
    ? 'funded — Budget reads exactly "Yes"'
    : 'unfunded — Budget is "' + (r.budgetRaw||'empty') + '", which is not "Yes"',
    !r.funded);
  kvRow(rtb, 'Start date parsed', r.start ? longDate(r.start) + '  (day/month/year)'
    : 'none — cannot be dated on the plan', !r.start);
  kvRow(rtb, 'Duration', r.dur ? fmt(r.dur) + ' months (sourced)'
    : 'none — imputed at the portfolio median ' + fmt(dp.medDur) + ' months', !r.dur);
  kvRow(rtb, 'EMMM capability', r.cap || 'not mapped to a capability', !r.cap);
  kvRow(rtb, 'Enabling platform group', r.plat ? deent(r.plat)
    : 'not a platform-layer initiative');
  kvRow(rtb, 'Total estimated labour', r.hasEst ? fmt(r.days) + ' days'
    : 'no estimate in any role — carried in the allowance pool', !r.hasEst);
  ROLES.forEach(function(c){
    if(r.labour[c]>0) kvRow(rtb, c + ' — ' + CONFIG.roleFull[c],
      fmt(r.labour[c]) + ' days  ·  ' + fmt(r.labour[c]/DPM) + ' FTE-months');
  });

  /* --- proration, if it is in the demand profile --------------------- */
  var p = dp.proj.filter(function(x){ return x.rec.id===r.id; })[0];
  var S = el('div','dsec',b);
  el('h4',null,S).textContent = 'Placement on the 12-month horizon';
  if(p){
    var pw = el('div',null,S);
    pw.style.fontSize='11.5px';
    pw.innerHTML = '<b>Tier ' + p.tier + '</b> — window <b>' + longDate(p.winStart) +
      '</b> to <b>' + longDate(addMonths(p.winStart, Math.round(p.winDur))) +
      '</b> (' + fmt(p.winDur) + ' months' + (r.dur?'':', imputed') + '). ' +
      '<b>' + fmt(p.inHz) + ' of ' + fmt(r.days) + ' days</b> fall inside the horizon; ' +
      fmt(r.days-p.inHz) + ' fall outside it. Each month below is that month\'s '+
      'calendar-day overlap with the window, as a share of the whole window.';
    var mt = el('table','kv',S); var mtb=el('tbody',null,mt);
    var tr1 = el('tr',null,mtb), tr2 = el('tr',null,mtb);
    el('th',null,tr1).textContent='Month';
    el('th',null,tr2).textContent='Days';
    tr1.firstChild.style.width='auto'; tr2.firstChild.style.width='auto';
    for(var i=0;i<dp.NM;i++){
      var a=el('td',null,tr1); a.textContent=shortDate(dp.HZ[i]);
      a.style.fontSize='10.5px';
      var c2=el('td',null,tr2); c2.textContent = p.months[i]>0.05?fmt(p.months[i]):'—';
      c2.style.fontSize='10.5px';
      if(p.months[i]<=0.05) c2.style.color=PAL.grey;
    }
    if(dp.overrun.filter(function(x){return x.rec.id===r.id;}).length){
      var ov = el('div','unverified',S); ov.style.marginTop='10px';
      ov.style.borderLeftColor=PAL.red;
      var ovt = el('span','tag',ov); ovt.style.color=PAL.red;
      ovt.textContent='Stage and dates disagree';
      ov.appendChild(document.createTextNode('This initiative is In Progress, but its '+
        'estimated window closed before the horizon opened. The plan uses the dates, so '+
        'it contributes nothing to the forecast. Re-date it or re-stage it.'));
    }
  } else {
    var np = el('div',null,S); np.style.fontSize='11.5px';
    np.textContent = (CONFIG.scope.demand.indexOf(r.stage)<0)
      ? 'Not placed: its stage is outside the demand scope (' +
        CONFIG.scope.demand.join(' or ') + ').'
      : 'Not placed by name: it carries no labour estimate, so it sits in the '+
        'unquantified pool and is planned for by allowance only.';
  }

  /* --- summary text, marked unverified (FR-155) ---------------------- */
  var U = el('div','dsec',b);
  el('h4',null,U).textContent = 'High-Level Summary, from the source';
  var uv = el('div','unverified',U);
  var tag = el('span','tag',uv);
  tag.textContent = 'Unverified against the title — not used to classify this initiative';
  uv.appendChild(document.createTextNode(r.summary ||
    '(no summary text in this record)'));
  var note = el('div',null,U);
  note.style.cssText='font-size:10.5px;color:'+PAL.grey+';margin-top:6px';
  note.textContent = 'In this extract the High-Level Summary column is offset against '+
    'Title across a block of records, so a summary may describe a different initiative. '+
    'Capability and platform mapping is therefore driven by Title only, and this text is '+
    'shown here and nowhere else.';
  openDrawer();
}
function showList(title, subtitle, recs, extra){
  $('dw-title').textContent = title;
  $('dw-sub').textContent = subtitle;
  var b = $('dw-body'); b.innerHTML='';
  if(extra){ var x=el('div',null,b);
    x.style.cssText='font-size:11.5px;margin-bottom:12px'; x.innerHTML=extra; }
  var t = el('table','diagtbl',b);
  var tr = el('tr',null,el('thead',null,t));
  ['Initiative','Stage','Sponsor','Funding','Start','Est days','In horizon']
    .forEach(function(h){ el('th',null,tr).textContent=h; });
  var tb = el('tbody',null,t);
  var dp = STATE.M.dp, byId={};
  dp.proj.forEach(function(p){ byId[p.rec.id]=p; });
  var tot=0, inhz=0;
  recs.forEach(function(r){
    var row = el('tr',null,tb);
    row.style.cursor='pointer';
    row.addEventListener('click', function(){ showRecord(r); });
    el('td',null,row).textContent = r.title;
    var s = el('td',null,row); s.textContent = r.stage;
    if(PAL.stage[r.stage]) s.style.color = PAL.stage[r.stage].ink;
    var sp = el('td',null,row);
    if(r.sponsor) sp.textContent = r.sponsor;
    else { sp.textContent='no sponsor'; sp.style.color=PAL.red;
      sp.style.fontWeight='bold'; }
    el('td',null,row).textContent = r.funded?'approved':'none';
    el('td',null,row).textContent = r.start?shortDate(r.start):'—';
    el('td','n',row).textContent = r.hasEst?fmt(r.days):'—';
    el('td','n',row).textContent = byId[r.id]?fmt(byId[r.id].inHz):'—';
    tot += r.days; if(byId[r.id]) inhz += byId[r.id].inHz;
  });
  var f = el('div',null,b);
  f.style.cssText='margin-top:12px;font-size:11.5px;font-weight:bold;color:'+PAL.teal;
  f.textContent = recs.length + ' initiatives  ·  ' + fmt(tot) +
    ' estimated days  ·  ' + fmt(inhz) + ' days inside the horizon  ·  ' +
    fmt(inhz/DPM) + ' FTE-months';
  var hint = el('div',null,b);
  hint.style.cssText='margin-top:6px;font-size:10.5px;color:'+PAL.grey;
  hint.textContent = 'Click any row for the full source record.';
  openDrawer();
}

/* =========================================================== click routing */
function bindClicks(root){
  root.addEventListener('click', function(e){
    var t = e.target.closest ? e.target.closest(CLICK_SEL) : null;
    if(!t) return;
    routeSelect(t);
  });
  root.addEventListener('keydown', function(e){
    if(e.key!=='Enter' && e.key!==' ') return;
    var t = e.target.closest ? e.target.closest(CLICK_SEL) : null;
    if(!t) return;
    e.preventDefault(); routeSelect(t);
  });
}
function routeSelect(t){
  var M = STATE.M, dp = M.dp;
  if(t.dataset.more){
    var ids = t.dataset.ids.split(',').map(Number);
    showList('Remaining initiatives in this group',
      ids.length + ' not shown on the canvas at this page height',
      ids.map(function(i){ return STATE.parsed.records[i]; }));
  } else if(t.dataset.rid!==undefined){
    showRecord(STATE.parsed.records[+t.dataset.rid]);
  } else if(t.dataset.mon!==undefined){
    var i = +t.dataset.mon;
    var recs = dp.proj.filter(function(p){ return p.months[i]>0.05; })
      .sort(function(a,b){ return b.months[i]-a.months[i]; })
      .map(function(p){ return p.rec; });
    showList(shortDate(dp.HZ[i]) + ' — ' + fmt(dp.baseM[i]) + ' days base case',
      recs.length + ' estimated initiatives contribute to this month',
      recs,
      'Base case ' + fmt(dp.baseM[i]) + ' d = <b>' + fmt(dp.estM[i]) +
      ' d estimated</b> + <b>' + fmt(dp.allow['Base case'].perMonth) +
      ' d allowance</b> for the ' + dp.unq.length + ' unquantified initiatives, which '+
      'cannot be attributed to a named initiative or a role. The <b>In horizon</b> '+
      'column is each initiative\'s whole-horizon contribution, not this month\'s.');
  } else if(t.dataset.cap){
    var c = M.ba.caps.filter(function(x){return x.cfg.key===t.dataset.cap;})[0];
    if(c) showList(c.cfg.key + ' — ' + deent(c.cfg.cover),
      c.items.length + ' active initiatives serve this capability', c.items,
      deent(c.cfg.verdict) + (c.items.length<=1
        ? ' <b style="color:'+PAL.red+'">This capability is at or below the thin-coverage '+
          'line, which is why it carries the alert border on the canvas.</b>' : ''));
  } else if(t.dataset.plat){
    var p = M.ba.plats.filter(function(x){
      return deent(x.cfg.key)===t.dataset.plat;})[0];
    if(p) showList(deent(p.cfg.key), p.items.length +
      ' active initiatives in this enabling group', p.items, deent(p.cfg.note) +
      ' The platform layer must be sequenced ahead of the capability work that depends '+
      'on it.');
  } else if(t.dataset.role){
    var c2 = t.dataset.role;
    var recs2 = dp.scope.filter(function(r){ return r.labour[c2]>0; })
      .sort(function(a,b){ return b.labour[c2]-a.labour[c2]; });
    showList(c2 + ' — ' + CONFIG.roleFull[c2],
      recs2.length + ' in-scope initiatives draw on this role',
      recs2, recs2.length
        ? fmt(dp.roleTot[c2]) + ' estimated days inside the horizon, peaking at <b>' +
          fmt(dp.rolePeak[c2].days) + ' d (' + fmt(dp.rolePeak[c2].days/DPM) +
          ' FTE) in ' + shortDate(dp.HZ[dp.rolePeak[c2].idx]) + '</b>.'
        : 'No in-scope initiative carries days for this role.');
  } else if(t.dataset.scen){
    var A = dp.allow[t.dataset.scen];
    showList(t.dataset.scen + ' — the unquantified pool it sizes',
      dp.unq.length + ' initiatives sized at ' + fmt(A.per) + ' days each',
      dp.unq, 'Nothing in this list carries a labour estimate, so none of them can be '+
      'placed by name or by month. Under <b>' + esc(t.dataset.scen) + '</b> the pool is '+
      '<b>' + fmt(A.pool) + ' days</b>, spread evenly at ' + fmt(A.perMonth) +
      ' d/mo, giving total in-horizon demand of <b>' + fmt(A.total) + ' days</b>. '+
      'Estimating these is the single highest-value action on either view.');
  }
}
"""

JS_APP2 = r"""
/* ==================================================== sorting (FR-180..FR-183) */
function bindSorts(root){
  root.addEventListener('click', function(e){
    var th = e.target.closest ? e.target.closest('[data-sort-role],[data-sort-reg]') : null;
    if(!th) return;
    var f = STATE.filters;
    if(th.dataset.sortRole){
      if(f.roleSort===th.dataset.sortRole) f.roleDesc = !f.roleDesc;
      else { f.roleSort = th.dataset.sortRole; f.roleDesc = false; }
    } else {
      if(f.regSort===th.dataset.sortReg) f.regDesc = !f.regDesc;
      else { f.regSort = th.dataset.sortReg; f.regDesc = false; }
    }
    refresh();
  });
  root.addEventListener('keydown', function(e){
    if(e.key!=='Enter' && e.key!==' ') return;
    var th = e.target.closest ? e.target.closest('[data-sort-role],[data-sort-reg]') : null;
    if(th){ e.preventDefault(); th.click(); }
  });
}

/* ============================================================ zoom (FR-134) */
/* The page is authored at A2, so its smallest glyphs are 6.4 px of print type. Fit to
   window scales that DOWN — legible on paper, not on a monitor — which is why the scale
   runs past 100% and defaults to a reading scale rather than to fit. Above 100% the page
   is wider than the stage and pans; that is the trade the reviewer is choosing. */
function applyZoom(){
  var C = CONFIG.meta.canvas;
  var w = $('stage').clientWidth - 28;   /* 28 = the stage's own left+right padding */
  /* clientWidth reads 0 while the stage is hidden — during print, or before layout —
     which would otherwise compute a negative scale and blank both canvases. Floored
     at a legible 25%. */
  var s = (STATE.zoom==='fit')
    ? Math.max(0.25, Math.min(1, w / C.w))
    : +STATE.zoom;
  ['ba','dp'].forEach(function(v){
    var cv = $('canvas-'+v), wr = $('wrap-'+v);
    cv.style.transform = 'scale(' + s + ')';
    /* The wrap carries the scaled size so the coverage checklist below it sits against the
       visible bottom edge of the page and the stage scrolls the visible width exactly. */
    wr.style.width  = (C.w * s) + 'px';
    wr.style.height = (C.h * s) + 'px';
    /* centre only while the whole width is in view; once it pans, centring would hide the
       left edge of band A behind the rail. */
    wr.style.margin = (C.w * s <= w) ? '0 auto' : '0';
  });
}
/* FR-134: hide the two rows of review chrome so the stage gets their height. The filter
   rail stays — it is part of the reading, not chrome. */
function applyMax(){
  document.body.classList.toggle('maxcanvas', STATE.maxCanvas);
  var b = $('btn-max');
  b.setAttribute('aria-pressed', STATE.maxCanvas ? 'true' : 'false');
  b.textContent = STATE.maxCanvas ? 'Restore chrome' : 'Maximise canvas';
  applyZoom();
}

/* ================================================= diagnostics (NFR-020, NFR-040) */
function dsec(parent, title, ids){
  var h = el('h4',null,parent);
  h.style.cssText='font-size:13px;color:'+PAL.teal+';margin:18px 0 6px';
  h.textContent = title;
  if(ids) fr(h, ids, title);
  return parent;
}
function showDiag(){
  var M = STATE.M, P = M.parsed, b = $('dg-body');
  b.innerHTML='';

  dsec(b, 'Parse statistics', 'FR-143..FR-147');
  var t1 = el('table','diagtbl',b), tb1 = el('tbody',null,t1);
  [['Source file', SNAPSHOT.name],
   ['Full path as read by the generator', SNAPSHOT.path],
   ['Last modified', SNAPSHOT.modified],
   ['Size on disk', fmt0(SNAPSHOT.bytes) + ' bytes'],
   ['Byte-order mark', SNAPSHOT.bom ? 'present, and stripped' : 'absent'],
   ['Physical lines in the file', fmt0(P.physicalLines) +
     ' — more than the record count, because summary cells contain line breaks'],
   ['Header columns', fmt0(P.header.length) + ' — ' + P.header.join(', ')],
   ['Logical records parsed', fmt0(P.records.length)],
   ['Blank rows skipped', fmt0(P.blankRows)],
   ['Replacement characters restored', fmt0(P.substitutions) +
     ' — U+FFFD restored to an en dash, which is what the source intended'],
   ['Run date in force', longDate(M.runDate) +
     (STATE.fixedDate ? '  (fixed, for reconciliation against the draw.io pages)'
                      : '  (this workstation\'s clock)')],
   ['Planning horizon', M.vars.HZ_FROM + ' to ' + M.vars.HZ_TO + ', ' +
     CONFIG.meta.horizonMonths + ' months'],
   ['Client version', CONFIG.meta.clientVersion + ', built ' + CONFIG.meta.buildDate],
   ['Sensitivity', CONFIG.meta.sensitivity]
  ].forEach(function(p){
    var tr = el('tr',null,tb1);
    el('th',null,tr).textContent = p[0];
    el('td',null,tr).textContent = p[1];
  });

  dsec(b, 'Assumptions applied to every figure on both views', 'FR-148..FR-156');
  var ul = el('ul','warnlist',b);
  [ 'One FTE-month is ' + fmt(DPM) + ' working days. Every FTE figure is days ÷ ' +
      fmt(DPM) + '.',
    'Budget is read as a funding flag, not a money value: only the exact word "Yes" '+
      'counts as approved. Anything else is treated as unfunded.',
    'A missing duration is imputed at the portfolio median of ' + fmt(M.dp.medDur) +
      ' months, and the register marks the imputed value in italic.',
    'A missing start date is imputed at the run date, so the initiative appears at the '+
      'front of the horizon rather than disappearing from it.',
    'Labour is spread across the horizon by calendar-day overlap: each month receives '+
      'the share of the window\'s calendar days that fall inside it. No S-curve, no '+
      'front-loading — the extract carries nothing that would justify either.',
    'The unquantified allowance is sized from the quartiles of the initiatives that do '+
      'carry estimates: Q1 ' + M.vars.Q1 + ' d downside, median ' + M.vars.Q2 +
      ' d base case, Q3 ' + M.vars.Q3 + ' d upside.',
    'Capability and platform mapping is driven by Title alone. The High-Level Summary '+
      'column is offset against Title across a block of records in this extract, so '+
      'using it would misclassify.',
    'All date arithmetic is UTC, so the model cannot shift with a timezone or a daylight '+
      'saving boundary.',
    'Rounding happens only where a number is displayed. Every intermediate figure is '+
      'carried at full precision, which is why the parts of a column may not visibly sum '+
      'to its printed total.'
  ].forEach(function(s){ el('li',null,ul).textContent = s; });

  dsec(b, 'Warnings raised while reading this extract', 'FR-146');
  if(!P.warnings.length){
    var ok = el('div',null,b);
    ok.style.cssText='font-size:11.5px;color:'+PAL.teal;
    ok.textContent = 'None. Every record carried a recognised stage, and every date, '+
      'duration and labour figure that was present was readable.';
  } else {
    var wl = el('ul','warnlist',b);
    P.warnings.forEach(function(w){ el('li',null,wl).textContent = w.text; });
  }

  dsec(b, 'Mapping assurance', 'FR-114..FR-119');
  var A = M.assurance, ml = el('ul','warnlist',b);
  [ A.unmapped.length
      ? A.unmapped.length + ' active initiatives are not mapped to any capability or '+
        'enabling group, and are therefore missing from the coverage band: ' +
        A.unmapped.map(function(r){return r.title;}).join('; ')
      : 'Every active initiative is mapped to a capability or an enabling group. Nothing '+
        'is missing from the coverage band.',
    A.retired.length
      ? A.retired.length + ' mapped titles have since gone Complete or Cancelled. They '+
        'are retained in the mapping so the page can be re-cut against an older extract, '+
        'and are excluded from every count: ' +
        A.retired.map(function(x){return x.title+' ('+x.stage+')';}).join('; ')
      : 'No mapped title has gone Complete or Cancelled.',
    A.stale.length
      ? A.stale.length + ' mapped titles no longer appear in the extract at all, which '+
        'means either a rename or a deletion upstream: ' +
        A.stale.map(function(x){return x.key;}).join('; ')
      : 'Every mapped title still appears in the extract.',
    A.doubleMapped.length
      ? A.doubleMapped.length + ' titles are claimed by more than one group, which would '+
        'double-count them: ' + A.doubleMapped.join('; ')
      : 'No title is claimed by more than one capability or by more than one enabling '+
        'group, so nothing is double-counted.'
  ].forEach(function(s){ el('li',null,ml).textContent = s; });

  dsec(b, 'Data quality report — the titles behind each count', 'FR-120..FR-125');
  var D = M.ba.defects;
  [['No sponsor named — nobody is accountable for the benefit', D.noSponsor],
   ['No author named — nobody is accountable for the estimate', D.noAuthor],
   ['No estimated start date — cannot be placed on a plan', D.noStart],
   ['No labour estimate in any role — cannot be resourced', D.noEst]
  ].forEach(function(pair){
    var h = el('div',null,b);
    h.style.cssText='font-size:11.5px;font-weight:bold;margin:12px 0 4px;color:'+
      (pair[1].length?PAL.red:PAL.teal);
    h.textContent = pair[1].length + ' — ' + pair[0];
    if(!pair[1].length) return;
    var byStage = {};
    pair[1].forEach(function(r){ (byStage[r.stage]=byStage[r.stage]||[]).push(r); });
    CONFIG.scope.active.forEach(function(s){
      if(!byStage[s]) return;
      var d = el('div',null,b);
      d.style.cssText='font-size:11px;margin:0 0 3px 14px';
      var sp = el('b',null,d);
      sp.style.color = PAL.stage[s] ? PAL.stage[s].ink : PAL.ink;
      sp.textContent = s + ' (' + byStage[s].length + '): ';
      d.appendChild(document.createTextNode(
        byStage[s].map(function(r){return r.title;}).join('; ')));
    });
  });

  $('modal-diag').classList.remove('hide');
  $('scrim').classList.remove('hide');
  hideTip();
}
function closeDiag(){
  $('modal-diag').classList.add('hide');
  if($('drawer').classList.contains('hide') && $('modal-gen').classList.contains('hide'))
    $('scrim').classList.add('hide');
}

/* ======================================================= generate (FR-090..FR-107) */
function stampDate(d){
  return longDate(d) + ' ' + String(d.getUTCHours()).padStart(2,'0') + ':' +
    String(d.getUTCMinutes()).padStart(2,'0');
}
function fileStamp(d){
  return '' + d.getUTCFullYear() + String(d.getUTCMonth()+1).padStart(2,'0') +
    String(d.getUTCDate()).padStart(2,'0');
}
function showGen(){
  var M = STATE.M, b = $('gn-body');
  b.innerHTML='';
  var intro = el('p',null,b);
  intro.style.cssText='font-size:11.5px;margin:0 0 14px';
  intro.innerHTML = 'Each generated file is <b>self-contained</b>: one HTML file with its '+
    'styles, its data and its provenance stamp inside it, so it can be mailed or filed '+
    'and still read correctly with no network access. The current filter is carried into '+
    'the generated file and stated on its face.';

  dsec(b, 'What to generate', 'FR-090..FR-094');
  var scopes = [['both','Both views','one file per view, two files'],
                ['ba','Business Architecture only',''],
                ['dp','Demand Profile only','']];
  scopes.forEach(function(s){
    var row = el('label','genrow',b);
    var r = el('input',null,row);
    r.type='radio'; r.name='gnscope'; r.value=s[0];
    if(s[0]==='both') r.checked=true;
    r.addEventListener('change', showGen);
    var sp = el('span',null,row);
    sp.innerHTML = '<b>'+s[1]+'</b>' + (s[2]?' <span style="color:'+PAL.grey+'"> — '+
      s[2]+'</span>':'');
  });
  var chosen = 'both';
  var rr = b.querySelectorAll('input[name=gnscope]');
  for(var i=0;i<rr.length;i++) if(rr[i].checked) chosen = rr[i].value;

  dsec(b, 'Files that would be written', 'FR-100..FR-103');
  var st = fileStamp(M.runDate);
  var names = [];
  if(chosen==='both'||chosen==='ba')
    names.push(['MinRes_Projects_Pipeline_Business_Architecture_'+st+'.html',
      'Business Architecture', M.ba.active.length + ' active initiatives']);
  if(chosen==='both'||chosen==='dp')
    names.push(['MinRes_Projects_Pipeline_Demand_Profile_'+st+'.html',
      'Demand Profile', M.dp.scope.length + ' in-scope initiatives']);
  names.forEach(function(n){
    var f = el('div','genfile',b);
    f.innerHTML = '<span class="mono">'+esc(n[0])+'</span>' +
      '<span style="color:'+PAL.grey+'"> — '+esc(n[1])+', '+esc(n[2])+'</span>';
  });

  dsec(b, 'Provenance stamp that each file would carry', 'FR-104..FR-107');
  names.forEach(function(n){
    var box2 = el('div','stampbox',b);
    var lines = [
      'Source: ' + SNAPSHOT.name + ', last modified ' + SNAPSHOT.modified + ', ' +
        M.parsed.records.length + ' records read',
      'Scope: ' + (n[1]==='Business Architecture'
        ? 'stages ' + CONFIG.scope.active.join(', ') + '. ' + M.ba.dead.length +
          ' omitted (' + CONFIG.scope.dead.map(function(s){
            return (M.ba.deadBy[s]||0) + ' ' + s; }).join(', ') + ')'
        : 'stages ' + CONFIG.scope.demand.join(', ') + '. ' + M.vars.N_EXCL +
          ' excluded (' + M.vars.X_OH + ' On Hold, ' + M.vars.X_CO + ' Complete, ' +
          M.vars.X_CA + ' Cancelled)'),
      'Filter in force at generation: ' + filterStatement(M, true),
      'Generated: ' + stampDate(new Date()) + ' by client ' + CONFIG.meta.clientVersion +
        ', built ' + CONFIG.meta.buildDate,
      'Sensitivity: ' + CONFIG.meta.sensitivity +
        ' — contains named sponsors and authors. Do not forward outside MinRes.'
    ];
    if(n[1]==='Demand Profile') lines.splice(2, 0,
      'Run date ' + longDate(M.runDate) + '. Horizon ' + M.vars.HZ_FROM + ' to ' +
      M.vars.HZ_TO + '. One FTE-month = ' + fmt(DPM) + ' working days.');
    var hd = el('div',null,box2);
    hd.style.cssText='font-weight:bold;color:'+PAL.teal+';margin-bottom:4px';
    hd.textContent = n[0];
    lines.forEach(function(L){ el('div',null,box2).textContent = L; });
  });

  var warn = el('p',null,b);
  warn.style.cssText='font-size:11px;color:'+PAL.grey+';margin-top:14px';
  warn.textContent = 'In the finished client, Generate writes these files beside the '+
    'extract using the browser download path, with no network request. In this mock-up '+
    'it writes nothing — the stamp above is the whole of what the button proves.';

  $('modal-gen').classList.remove('hide');
  $('scrim').classList.remove('hide');
  hideTip();
}
function closeGen(){
  $('modal-gen').classList.add('hide');
  if($('drawer').classList.contains('hide') && $('modal-diag').classList.contains('hide'))
    $('scrim').classList.add('hide');
}

/* ============================ annotation overlay + coverage checklist (screen J) */
function frLabel(ids){
  for(var i=0;i<CONFIG.traceability.length;i++)
    if(CONFIG.traceability[i][2]===ids) return CONFIG.traceability[i][1];
  return '';
}
function applyAnnot(){
  document.body.classList.toggle('annot', STATE.annot);
  /* The rail is annotated as well as the two canvases: filtering and ordering are
     requirements in their own right, and a reviewer looking for FR-162..FR-167 must
     find them on the control that satisfies them. */
  ['canvas-ba','canvas-dp','rail'].forEach(function(id){
    var root = $(id);
    var old = root.querySelectorAll('.frbadge');
    for(var i=0;i<old.length;i++) old[i].remove();
    if(!STATE.annot) return;
    /* querySelectorAll searches descendants only, and the rail carries its own
       data-fr, so the root is added explicitly or its badge would be missing. */
    var nodes = [].slice.call(root.querySelectorAll('[data-fr]'));
    if(root.dataset.fr) nodes.unshift(root);
    for(var j=0;j<nodes.length;j++){
      var n = nodes[j];
      if(getComputedStyle(n).position==='static') n.style.position='relative';
      var badge = el('span','frbadge',n);
      badge.textContent = n.dataset.fr;
      badge.dataset.ids = n.dataset.fr;
      badge.dataset.label = n.dataset.frl || frLabel(n.dataset.fr) || '';
      badge.title = badge.dataset.label;
    }
  });
  renderCoverage();
}
function frCount(range){
  var m = range.match(/FR-(\d+)\.\.FR-(\d+)/);
  if(m) return (+m[2]) - (+m[1]) + 1;
  return range.match(/FR-\d+/) ? 1 : 0;
}
function renderCoverage(){
  var c = $('coverage');
  if(!STATE.annot){ c.classList.add('hide'); return; }
  c.classList.remove('hide');
  c.innerHTML='';
  var full=0, part=0, total=0;
  CONFIG.traceability.forEach(function(r){
    var n = frCount(r[2]); total += n;
    if(r[3]==='full') full += n; else part += n;
  });
  el('h2',null,c).textContent = 'Requirement coverage in this mock-up';
  var sub = el('div','sub',c);
  sub.innerHTML = 'Every region on both canvases, and the filter rail beside them, '+
    'carries a badge naming the functional '+
    'requirements it satisfies. Of the <b>' + total + ' functional requirements</b> in '+
    'the specification, <b class="ok" style="display:inline">' + full +
    '</b> are represented in full and <b class="part" style="display:inline">' + part +
    '</b> in part. A requirement is <b>partial</b> where the mock-up shows the interface '+
    'but the behaviour behind it belongs to the build — reading a chosen file, writing a '+
    'download, and verified pagination. Nothing in the specification is unrepresented. '+
    'Comment against the ID, not the picture.';
  var t = el('table',null,c);
  var tr = el('tr',null,el('thead',null,t));
  ['Module','Requirement group','IDs','In this mock-up','How it is represented, or what '+
    'is deferred to build'].forEach(function(h){ el('th',null,tr).textContent=h; });
  var tb = el('tbody',null,t);
  var lastMod = '';
  CONFIG.traceability.forEach(function(r){
    var row = el('tr',null,tb);
    var m = el('td',null,row);
    if(r[0]!==lastMod){ m.innerHTML = '<b>'+esc(r[0])+'</b>'; lastMod = r[0]; }
    el('td',null,row).textContent = r[1];
    var idc = el('td','mono',row); idc.textContent = r[2];
    var st = el('td', r[3]==='full'?'ok':'part', row);
    st.textContent = r[3]==='full' ? 'full ('+frCount(r[2])+')'
                                   : 'partial ('+frCount(r[2])+')';
    var nt = el('td',null,row);
    nt.innerHTML = r[4] ? deent(r[4]) : '<span style="color:'+PAL.grey+
      '">Rendered as specified; no deviation to note.</span>';
  });
  var nf = el('div',null,c);
  nf.style.cssText='margin-top:14px;font-size:11.5px;color:'+PAL.grey;
  nf.innerHTML = 'Non-functional requirements are demonstrated rather than listed: '+
    '<b>NFR-035, NFR-038</b> by the absence of any outbound request — open the browser '+
    'network trace and it stays empty; <b>NFR-027</b> by the single-file size; '+
    '<b>NFR-029</b> by the fixed run date toggle, which reproduces identical figures on '+
    'any machine in any timezone; <b>NFR-037</b> by rendering every source string as '+
    'text, so a crafted title cannot execute; <b>NFR-036</b> by the INTERNAL mark in the '+
    'file bar and in every provenance stamp; <b>NFR-041</b> by keyboard reachability of '+
    'every chip, sort header and chart segment.';
}

/* ================================================== screens A and B, and boot */
function parseAndLoad(){
  STATE.parsed = parseSnapshot(SNAPSHOT);
  var rep = $('ls-report');
  rep.classList.remove('hide');
  rep.innerHTML = 'Read <b>' + esc(SNAPSHOT.name) + '</b> — ' + fmt0(SNAPSHOT.bytes) +
    ' bytes, ' + fmt0(STATE.parsed.physicalLines) + ' physical lines, ' +
    SNAPSHOT.fields.length + ' named columns, <b>' + STATE.parsed.records.length +
    ' logical records</b> parsed' +
    (STATE.parsed.blankRows ? ', ' + STATE.parsed.blankRows + ' blank rows skipped' : '') +
    (STATE.parsed.warnings.length
      ? ', <b>' + STATE.parsed.warnings.length + ' warnings</b> raised — see Diagnostics'
      : ', no warnings raised') +
    '. The physical line count exceeds the record count because summary cells contain '+
    'line breaks.';
  $('fb-name').textContent = SNAPSHOT.name;
  $('fb-mod').textContent  = SNAPSHOT.modified;
  $('fb-recs').textContent = STATE.parsed.records.length;
  $('fb-ver').textContent  = CONFIG.meta.clientVersion + ' (' + CONFIG.meta.buildDate + ')';
  $('fb-sens').textContent = CONFIG.meta.sensitivity;
  setTimeout(function(){
    $('loadscreen').classList.add('hide');
    $('shell').classList.remove('hide');
    STATE.loaded = true;
    refresh(true);
  }, 550);
}
function showError(){
  $('shell').classList.add('hide');
  $('loadscreen').classList.add('hide');
  $('errorscreen').classList.remove('hide');
  closeDiag(); closeGen(); closeDrawer();
  $('err-lead').textContent = 'The file you selected does not carry the columns this '+
    'briefing depends on, so no figure could be trusted and nothing has been loaded.';
  $('err-detail').innerHTML =
    '<b>File</b><br>' + esc(SNAPSHOT.name) + '<br><br>' +
    '<b>What is missing</b><br>The column <b>Sponsor</b> was not found in the header '+
    'row. Without it the briefing cannot say who is accountable for any initiative, and '+
    'the accountability measure on both views would read zero rather than unknown.'+
    '<br><br><b>Header row as read</b><br>' +
    esc(SNAPSHOT.header.filter(function(h){ return h!=='Sponsor'; }).join(', '));
  $('err-remedy').innerHTML = 'Re-export the pipeline with all ' +
    SNAPSHOT.fields.length + ' columns included, keeping the header names unchanged, '+
    'then load it again. If the column has been renamed upstream, tell the portfolio '+
    'team rather than editing the export by hand — the name is the contract between the '+
    'pipeline and this client.';
}

/* ====================================================== the one refresh path */
function refresh(rebuildRail){
  /* boot() sets the opening view before anything is loaded, and the view tabs are
     live behind the load screen, so refresh must be a no-op until an extract has
     been parsed rather than derive a model from nothing. */
  if(!STATE.parsed) return;
  var rd = runDate();
  STATE.M = buildModel(STATE.parsed, STATE.filters, rd);
  STATE.base = buildModel(STATE.parsed,
    {stage:'',sponsor:'',author:'',cap:'',plat:'',funding:'',role:'',q:'',
     order:STATE.filters.order, roleSort:STATE.filters.roleSort,
     roleDesc:STATE.filters.roleDesc, regSort:STATE.filters.regSort,
     regDesc:STATE.filters.regDesc}, rd);

  renderBA($('canvas-ba'), STATE.M);
  renderDP($('canvas-dp'), STATE.M);
  buildRail();
  renderBanner();
  applyZoom();
  applyAnnot();
  if(rebuildRail===true){ /* rail is rebuilt every pass; the flag documents intent */ }
}
function setView(v){
  STATE.view = v;
  $('tab-ba').classList.toggle('on', v==='ba');
  $('tab-dp').classList.toggle('on', v==='dp');
  $('tab-ba').setAttribute('aria-selected', v==='ba' ? 'true':'false');
  $('tab-dp').setAttribute('aria-selected', v==='dp' ? 'true':'false');
  $('wrap-ba').classList.toggle('hide', v!=='ba');
  $('wrap-dp').classList.toggle('hide', v!=='dp');
  if(v==='ba' && STATE.filters.role){ STATE.filters.role=''; }
  refresh();
  $('stage').scrollTop = 0;
}
function boot(){
  $('ls-name').textContent = SNAPSHOT.name;
  on('btn-choose','click', parseAndLoad);
  var d = $('drop');
  d.addEventListener('click', parseAndLoad);
  ['dragenter','dragover'].forEach(function(ev){
    d.addEventListener(ev, function(e){ e.preventDefault(); d.classList.add('over'); }); });
  ['dragleave','drop'].forEach(function(ev){
    d.addEventListener(ev, function(e){ e.preventDefault(); d.classList.remove('over'); }); });
  d.addEventListener('drop', parseAndLoad);

  on('btn-err-back','click', function(){
    $('errorscreen').classList.add('hide');
    if(STATE.loaded) $('shell').classList.remove('hide');
    else $('loadscreen').classList.remove('hide');
  });
  on('btn-reload','click', function(){
    $('shell').classList.add('hide');
    $('loadscreen').classList.remove('hide');
    $('ls-report').classList.add('hide');
  });

  on('tab-ba','click', function(){ setView('ba'); });
  on('tab-dp','click', function(){ setView('dp'); });
  on('zoom','change', function(e){ STATE.zoom=e.target.value; applyZoom(); });
  on('btn-max','click', function(){ STATE.maxCanvas = !STATE.maxCanvas; applyMax(); });
  on('chk-annot','change', function(e){ STATE.annot=e.target.checked; applyAnnot(); });
  on('chk-fixdate','change', function(e){ STATE.fixedDate=e.target.checked; refresh(); });
  on('btn-diag','click', showDiag);
  on('dg-close','click', closeDiag);
  on('dg-err','click', function(){ closeDiag(); showError(); });
  on('btn-gen','click', showGen);
  on('gn-close','click', closeGen);
  on('gn-cancel','click', closeGen);
  on('gn-go','click', function(){
    var m = el('div',null,$('gn-body'));
    m.style.cssText='margin-top:12px;padding:10px 12px;background:#FBEEF1;border:1px '+
      'solid '+PAL.red+';font-size:11.5px;color:'+PAL.red+';font-weight:bold';
    m.textContent = 'Nothing was written. This is a mock-up: the dialog exists so the '+
      'file names, the scope statement and the provenance stamp can be reviewed before '+
      'the generator is built.';
    $('gn-go').disabled = true;
  });
  on('btn-print','click', function(){ hideTip(); window.print(); });
  on('dw-close','click', closeDrawer);
  on('scrim','click', function(){ closeDrawer(); closeDiag(); closeGen(); });
  document.addEventListener('keydown', function(e){
    if(e.key==='Escape'){ closeDrawer(); closeDiag(); closeGen(); hideTip(); }
  });
  /* re-applied at any scale, not only at fit: the width of the stage also decides whether
     the page is still centred or has begun to pan. */
  window.addEventListener('resize', applyZoom);

  ['canvas-ba','canvas-dp'].forEach(function(id){
    bindHover($(id)); bindClicks($(id)); bindSorts($(id));
  });
  bindHover($('dw-body')); bindClicks($('dw-body'));
  bindHover($('rail'));   /* so the rail's requirement badges answer hover too */

  setView('ba');
  $('tab-ba').classList.add('on');
}
document.addEventListener('DOMContentLoaded', boot);
"""

# ================================================================ assembly
HTML = """<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Projects Pipeline Desktop Client &mdash; MOCK-UP for UI review</title>
<meta name="robots" content="noindex, nofollow">
<!--
  ============================================================================
  MinRes Projects Pipeline Desktop Client &mdash; MOCK-UP FOR UI REVIEW
  ----------------------------------------------------------------------------
  Generated by .claude/skills/scripts/projects_pipeline_desktop_client_mockup.py
  DO NOT EDIT THIS FILE. Change the generator and regenerate.

  Sensitivity: __SENS__ &mdash; contains named sponsors and authors.

  Self-contained by requirement: one file, no external stylesheet, no external
  script, no font download, no image, no analytics, no telemetry, no outbound
  request of any kind (NFR-035, NFR-038). Opening this file must leave the
  browser network trace empty.

  Sections, in order:
    1  <style>       one :root token block, the single configuration surface
    2  CONFIG        framework content ported from the two draw.io generators
    3  SNAPSHOT      the extract, as read, embedded via JSON
    4  derive.js     pure derivation; every figure on both views comes from here
    5  render.js     the two A2 canvases
    6  app.js        chrome, filters, sorting, hover, drill-down, dialogs
  ============================================================================
-->
<style>
__CSS__
</style>
</head>
<body>
__BODY__
<script>
"use strict";
/* ============================================================ 2 &mdash; CONFIG */
var CONFIG = __CONFIG__;
/* ========================================================== 3 &mdash; SNAPSHOT */
/* The extract, exactly as read from disk, emitted through JSON so that no value in
   it can break out of its string and become markup or code (NFR-037). In the
   finished client this one assignment is replaced by a FileReader result; nothing
   downstream of it changes. */
var SNAPSHOT = __SNAPSHOT__;
/* ========================================================= 4 &mdash; derive.js */
__DERIVE__
/* ========================================================= 5 &mdash; render.js */
__RENDER__
__RENDER_DP__
/* ============================================================ 6 &mdash; app.js */
__APP__
__APP2__
</script>
</body>
</html>
"""


def js_json(obj, indent=None):
    """Serialise for embedding inside an inline <script> element.

    The HTML parser ends a script block at the first literal '</script>' in the text,
    whatever the JavaScript around it means. A title or summary cell containing that
    string would therefore split the file in two and leave the remainder of the payload
    parsed as markup — an executable injection straight out of the extract. Escaping
    every '<' as \\u003c makes that impossible; JSON decodes the escape back to '<', so
    no value is altered. '>' and '&' go the same way so no cell can start an entity or
    close a comment. This is the NFR-037 guarantee at the embedding boundary; render.js
    holds the other half by writing source strings as text nodes.
    """
    return (json.dumps(obj, ensure_ascii=False, indent=indent)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def build_html():
    doc = HTML
    doc = doc.replace("__SENS__", CONFIG["meta"]["sensitivity"])
    doc = doc.replace("__CSS__", CSS.strip())
    doc = doc.replace("__BODY__", BODY.strip())
    doc = doc.replace("__CONFIG__", js_json(CONFIG, indent=1))
    doc = doc.replace("__SNAPSHOT__", js_json(SNAP))
    doc = doc.replace("__DERIVE__", JS_DERIVE.strip())
    doc = doc.replace("__RENDER__", JS_RENDER.strip())
    doc = doc.replace("__RENDER_DP__", JS_RENDER_DP.strip())
    doc = doc.replace("__APP__", JS_APP.strip())
    doc = doc.replace("__APP2__", JS_APP2.strip())
    return doc


def reconcile():
    """Report the counts a reviewer must be able to see on the rendered page.

    The generator does no analysis, so this is a read of the extract only: stage
    counts, blank-column counts and the mapping tallies. Everything that requires
    proration or quartiles is computed in the browser and is checked there.
    """
    rows = SNAP["rows"]
    idx = {f: i for i, f in enumerate(SNAP["fields"])}
    def g(r, f):
        return (r[idx[f]] or "").replace("�", "–").strip()

    stages = {}
    for r in rows:
        stages[g(r, "Stage")] = stages.get(g(r, "Stage"), 0) + 1
    active_names = CONFIG["scope"]["active"]
    dead_names = CONFIG["scope"]["dead"]
    demand_names = CONFIG["scope"]["demand"]

    act = [r for r in rows if g(r, "Stage") in active_names]
    dead = [r for r in rows if g(r, "Stage") in dead_names]
    dem = [r for r in rows if g(r, "Stage") in demand_names]

    def daysof(r):
        t = 0.0
        for c in CONFIG["roles"]:
            v = g(r, "%s - Est Project Labour Days" % c)
            try:
                f = float(v)
            except ValueError:
                f = 0.0
            if f > 0:
                t += f
        return t

    mapped = set()
    for grp in CONFIG["capabilities"]:
        for t in grp["titles"]:
            mapped.add(t.replace("�", "–").strip().lower())
    for grp in CONFIG["platform"]:
        for t in grp["titles"]:
            mapped.add(t.replace("�", "–").strip().lower())
    titles_active = set(g(r, "Title").lower() for r in act)
    titles_all = set(g(r, "Title").lower() for r in rows)
    unmapped = sorted(titles_active - mapped)
    retired = sorted((titles_all - titles_active) & mapped)
    stale = sorted(mapped - titles_all)

    est = [r for r in dem if daysof(r) > 0]
    total_days = sum(daysof(r) for r in rows if g(r, "Stage") in demand_names)

    print("  extract            %s" % SNAP["name"])
    print("  bytes / lines      %s / %s  (BOM %s)"
          % (SNAP["bytes"], SNAP["physicalLines"], "yes" if SNAP["bom"] else "no"))
    print("  modified           %s" % SNAP["modified"])
    print("  columns            %d" % len(SNAP["fields"]))
    print("  logical records    %d" % len(rows))
    print("  by stage           %s"
          % ", ".join("%s %d" % (k, stages[k]) for k in sorted(stages)))
    print("  active (BA view)   %d   omitted %d" % (len(act), len(dead)))
    print("  in scope (DP view) %d   estimated %d, unquantified %d"
          % (len(dem), len(est), len(dem) - len(est)))
    print("  estimated days     %.1f across the in-scope set" % total_days)
    print("  active defects     %d no sponsor, %d no author, %d no start, %d no estimate"
          % (sum(1 for r in act if not g(r, "Sponsor")),
             sum(1 for r in act if not g(r, "Author")),
             sum(1 for r in act if not g(r, "Start Date - Est Project")),
             sum(1 for r in act if daysof(r) == 0)))
    print("  mapping            %d unmapped, %d retired, %d stale"
          % (len(unmapped), len(retired), len(stale)))
    if unmapped:
        print("  UNMAPPED           %s" % "; ".join(unmapped))


def main():
    doc = build_html()
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    out = os.path.join(OUT_DIR, OUT_NAME)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    kb = len(doc.encode("utf-8")) / 1024.0
    print("MinRes Projects Pipeline Desktop Client - mock-up for UI review")
    print("-" * 78)
    reconcile()
    print("-" * 78)
    print("  wrote              %s" % out)
    print("  size               %.0f KB  (NFR-027 budget 2048 KB)" % kb)
    print("  open it            double-click the file; no server, no network request")


if __name__ == "__main__":
    main()
