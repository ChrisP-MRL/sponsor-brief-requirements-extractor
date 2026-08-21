# -*- coding: utf-8 -*-
"""Build the one-page 12-month Demand Profile for the short-term projects pipeline.

Scope: SCOR **Plan** process only (Section 2 of the rule) — demand forecasting, capacity
and resource planning, and the business rules that fall out of the profile. Source, Make,
Deliver, Return are out of scope on this page: this pipeline's constrained supply is
internal delivery labour, not equipment, so the Plan process is where the analysis bites.

Source of content: input/Projects Pipeline - Short Term.csv
Framework applied: .claude/rules/SCOR_demand_planning.html
Layout convention: output/MinRes_Projects_Pipeline_Business_Architecture.drawio (sibling page)

FILTER: Stage = "In Progress" or "Opportunity" only, as requested. On Hold, Complete and
Cancelled rows are excluded at read time and the excluded counts are carried onto the page
so the reader knows what is not in the profile.

HORIZON: the 12 calendar months from the month of the run date (Aug 2026 - Jul 2027).
Labour days are prorated across the horizon by calendar-day overlap of each initiative's
window (start date -> start + duration months), so a project that straddles the horizon
boundary contributes only the part that falls inside it.

THE CENTRAL DATA PROBLEM, and how this page handles it rather than hiding it:
only 9 of the 42 in-scope initiatives carry any labour estimate at all, and only 6 carry
a start date AND a duration AND an estimate. A profile built on those 6 alone would read
as a portfolio that stops working in Jan 2027, which is false. So the page shows two
things in one stack:
  - ESTIMATED demand   - the 9 initiatives that carry estimates, placed on their own dates
  - ALLOWANCE          - a parametric allowance for the 33 unquantified initiatives, sized
                         from the quartiles of the 9 that are estimated (Q1 / median / Q3
                         = downside / base / upside) and spread evenly across the horizon
                         because no dates exist to place it with
The allowance is drawn in grey with a dashed edge and labelled, so it is never mistaken
for estimated demand. This is the SCOR 2.1 multi-scenario method applied to the real
uncertainty in this data set, which is estimate coverage, not commodity price.

Brand rules from .claude/rules/MINRES_Content_Guidelines.html: Century Gothic throughout;
MinRes Red #CE372F reserved for title and accents; Dark Teal #00444C for band headers.

Series palette was chosen by running the dataviz skill's validator over the MinRes brand
ramps, not by eye. Final order Teal 300 / Brown 400 / Olive 300 / Wine 400 / Terra Cotta
300 clears CVD separation at deltaE 16.1 and the normal-vision floor at 16.8 on the
adjacent pairlist (the operative list for a stacked bar), with lightness band and 3:1
surface contrast passing. The validator's chroma floor still fails on Teal 300, Brown 400
and Olive 300: the MinRes palette is deliberately low-chroma and no brand step clears that
floor, so the deviation is accepted and relieved the way the skill requires - every
segment is directly labelled and the full month-by-role table is on the page.

Page is A2 landscape (2245 x 1587 px at 96dpi) with 24px margins.
"""
import csv
import datetime as dt
import os
import statistics
from xml.sax.saxutils import escape

CG = "Century Gothic"
cells = []
_id = [1]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CSV_PATH = os.path.join(ROOT, "input", "Projects Pipeline - Short Term.csv")

IN_SCOPE = ("In Progress", "Opportunity")
OUT_OF_SCOPE = ("On Hold", "Complete", "Cancelled")

RUN_DATE = dt.date(2026, 8, 13)      # page date; horizon starts at the 1st of this month
DAYS_PER_FTE_MONTH = 21.0            # stated assumption, not sourced from the CSV


def add(value, style, x, y, w, h, parent="1"):
    _id[0] += 1
    cells.append(
        '        <mxCell id="n%d" value="%s" style="%s" vertex="1" parent="%s">\n'
        '          <mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry" />\n'
        '        </mxCell>\n'
        % (_id[0], escape(value, {'"': '&quot;'}), escape(style, {'"': '&quot;'}),
           parent, round(x, 2), round(y, 2), round(w, 2), round(h, 2)))


def h(s):
    """HTML-escape CSV data before it is embedded as draw.io rich text."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- page grid
X0, RIGHT = 24, 2221
W = RIGHT - X0            # 2197


def grid(n, gap=8, x=X0, width=W):
    """n equal columns spanning width, separated by gap."""
    cw = (width - gap * (n - 1)) / float(n)
    return [(x + i * (cw + gap), cw) for i in range(n)]


# ---------------------------------------------------------------- palette
RED = "#CE372F"           # Coral 400 - reserved for title and accents
TEAL = "#00444C"          # Dark Teal - band headers
INK = "#000000"
GREY = "#5C5C5C"
RULE = "#D1D1D1"          # Grey 200
SURF = "#F1EDE7"          # Brown 100
SURF2 = "#E8E8E8"         # Grey 100

# Stage families - same visual language as the sibling Business Architecture page.
STAGE = {
    "In Progress": {"fill": "#E0F7F9", "line": "#B0EDF3", "ink": "#1A7C87"},
    "Opportunity": {"fill": "#F1EDE7", "line": "#D9CDB8", "ink": "#6B5435"},
}

# Role series - validator-chosen order, largest role at the bottom of the stack.
# label, hex, label-ink-on-fill (contrast-driven: white only where it clears 4.5:1)
SERIES = [
    ("IE", "#3F939C", INK),        # Teal 300        white 3.58 : black 5.86 -> black
    ("BA", "#6B5435", "#FFFFFF"),  # Brown 400       white 7.13 -> white
    ("PM", "#878C56", INK),        # Olive 300       white 3.55 : black 5.92 -> black
    ("SA", "#8B2E45", "#FFFFFF"),  # Wine 400        white 8.16 -> white
    ("Other", "#C37556", INK),     # Terra Cotta 300 white 3.50 : black 6.00 -> black
]
SERIES_ORDER = [s[0] for s in SERIES]          # bottom -> top of the stack
SERIES_COL = {s[0]: s[1] for s in SERIES}
SERIES_TXT = {s[0]: s[2] for s in SERIES}
ALLOW_FILL, ALLOW_LINE, ALLOW_INK = SURF2, "#888888", GREY

ROLE_FULL = {
    "PM": "Project Manager",
    "BA": "Business Analyst",
    "IE": "Infrastructure Engineer",
    "CD": "Change / Delivery",
    "SA": "Solution Architect",
    "Other": "Other / specialist",
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


def box(text, x, y, w, hh, fill, line, ink, fs=8, valign="top", pad=7, align="left"):
    add(text,
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=%s;"
        "fontSize=%s;fontColor=%s;align=%s;verticalAlign=%s;spacingLeft=%s;spacingRight=%s;"
        "spacingTop=4;" % (fill, line, CG, fs, ink, align, valign, pad, pad - 1),
        x, y, w, hh)


def txt(s, x, y, w, hh, fs=7.5, col=INK, align="left", valign="top", bold=False):
    add(s, "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=%s;fontColor=%s;align=%s;"
           "verticalAlign=%s;%s" % (CG, fs, col, align, valign,
                                    "fontStyle=1;" if bold else ""),
        x, y, w, hh)


def rect(x, y, w, hh, fill, line="none", dashed=False):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=%s;%s"
        % (fill, line, "dashed=1;dashPattern=3 3;" if dashed else ""), x, y, w, hh)


def head_desc(title, desc, tcol=TEAL, tsize=9, dsize=7.2):
    return ("<b><font style=\"font-size:%spx\" color=\"%s\">%s</font></b><br>"
            "<font style=\"font-size:%spx\" color=\"#000000\">%s</font>"
            % (tsize, tcol, title, dsize, desc))


def num(v):
    """Trim a float for display: 82.5 -> '82.5', 85.0 -> '85'."""
    return ("%.1f" % v).rstrip("0").rstrip(".")


# ================================================================ read the pipeline
LABOUR = ["PM", "BA", "IE", "CD", "SA", "Other"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def clean(s):
    """The source CSV already contains U+FFFD where en dashes were lost upstream
    ('Identity And Access Management � Tranche 2'). Restore the dash."""
    return (s or "").replace("�", "–").strip()


def fnum(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def pdate(s):
    s = (s or "").strip()
    if not s:
        return None
    parts = s.split("/")
    if len(parts) != 3:
        return None
    try:
        return dt.date(int(parts[2]), int(parts[1]), int(parts[0]))
    except ValueError:
        return None


def short_date(d):
    return "" if d is None else "%s %02d" % (MONTHS[d.month - 1], d.year % 100)


def add_months(d, n):
    y = d.year + (d.month - 1 + n) // 12
    m = (d.month - 1 + n) % 12 + 1
    last = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return dt.date(y, m, min(d.day, last))


# ---------------------------------------------------------------- horizon
H_START = dt.date(RUN_DATE.year, RUN_DATE.month, 1)
HZ = [add_months(H_START, i) for i in range(12)]
HZ_END = add_months(H_START, 12)
HZ_LABEL = [short_date(d) for d in HZ]


def m_start(i):
    return HZ[i]


def m_end(i):
    return add_months(H_START, i + 1)


with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as fh:
    ROWS = list(csv.DictReader(fh))

PROJ, EXCLUDED = [], {}
for r in ROWS:
    stage = clean(r.get("Stage"))
    if stage not in IN_SCOPE:
        EXCLUDED[stage] = EXCLUDED.get(stage, 0) + 1
        continue
    lab = {c: (fnum(r.get("%s - Est Project Labour Days" % c)) or 0.0) for c in LABOUR}
    PROJ.append({
        "title": clean(r.get("Title")),
        "stage": stage,
        "sponsor": clean(r.get("Sponsor")),
        "budget": clean(r.get("Budget")) == "Yes",
        "start": pdate(r.get("Start Date - Est Project")),
        "dur": fnum(r.get("Duration - Est Project (months)")),
        "labour": lab,
        "days": sum(lab.values()),
    })

N = len(PROJ)
N_IP = sum(1 for p in PROJ if p["stage"] == "In Progress")
N_OP = sum(1 for p in PROJ if p["stage"] == "Opportunity")
N_EXCL = sum(EXCLUDED.values())

# ================================================================ tier the demand
# A  start + duration + estimate  -> placed exactly as estimated
# B  start + estimate, no duration -> placed from its start, portfolio-median duration
# C  estimate only, no start       -> placed from horizon month 1, median duration
# D  no estimate at all            -> cannot be placed or sized; goes to the allowance
EST = [p for p in PROJ if p["days"] > 0]
UNQ = [p for p in PROJ if p["days"] <= 0]
EST_TOTALS = sorted(p["days"] for p in EST)
Q1, Q2, Q3 = statistics.quantiles(EST_TOTALS, n=4, method="inclusive")
MEAN_EST = statistics.mean(EST_TOTALS)
MED_DUR = statistics.median([p["dur"] for p in EST if p["dur"]]) or 3.0

TIER_A, TIER_B, TIER_C = [], [], []
for p in EST:
    if p["start"] and p["dur"]:
        p["tier"], p["win_start"], p["win_dur"] = "A", p["start"], p["dur"]
        TIER_A.append(p)
    elif p["start"]:
        p["tier"], p["win_start"], p["win_dur"] = "B", p["start"], MED_DUR
        TIER_B.append(p)
    else:
        p["tier"], p["win_start"], p["win_dur"] = "C", H_START, MED_DUR
        TIER_C.append(p)

# ---------------------------------------------------------------- prorate onto months
PROFILE = {c: [0.0] * 12 for c in LABOUR}
for p in EST:
    s = p["win_start"]
    e = add_months(s, int(round(p["win_dur"])))
    span = float((e - s).days) or 1.0
    p["in_horizon"] = 0.0
    p["months"] = [0.0] * 12
    for i in range(12):
        a, b = max(s, m_start(i)), min(e, m_end(i))
        ov = (b - a).days
        if ov > 0:
            f = ov / span
            for c in LABOUR:
                PROFILE[c][i] += p["labour"][c] * f
            p["months"][i] = p["days"] * f
            p["in_horizon"] += p["days"] * f

EST_M = [sum(PROFILE[c][i] for c in LABOUR) for i in range(12)]
EST_IN_HZ = sum(EST_M)
EST_TOTAL = sum(p["days"] for p in EST)
OUTSIDE = EST_TOTAL - EST_IN_HZ
ACTIVE_ROLES = [c for c in SERIES_ORDER if sum(PROFILE[c]) > 0]
NIL_ROLES = [c for c in LABOUR if sum(p["labour"][c] for p in PROJ) <= 0]

# ---------------------------------------------------------------- allowance scenarios
SCEN = [
    ("Downside", "low case", Q1, "#F0F2E5", "#D9DCBC", "#5E623C"),
    ("Base case", "central", Q2, "#E3F2F4", "#B8DDE3", TEAL),
    ("Upside", "high case", Q3, "#F5E5DD", "#E8C4B0", "#8E5239"),
]
ALLOW = {}
for name, _sub, per, _f, _l, _i in SCEN:
    pool = per * len(UNQ)
    ALLOW[name] = {"per": per, "pool": pool, "per_month": pool / 12.0,
                   "total": EST_IN_HZ + pool}
BASE_ALLOW = ALLOW["Base case"]["per_month"]

BASE_M = [EST_M[i] + BASE_ALLOW for i in range(12)]
PEAK_I = max(range(12), key=lambda i: BASE_M[i])
EST_PEAK_I = max(range(12), key=lambda i: EST_M[i])

AXMAX = int((max(BASE_M) // 40 + 1) * 40)

# ---------------------------------------------------------------- concentration metrics
BY_SIZE = sorted(EST, key=lambda p: -p["days"])
TOP1 = BY_SIZE[0]
TOP2_SHARE = (BY_SIZE[0]["days"] + BY_SIZE[1]["days"]) / EST_TOTAL * 100
COVERAGE = len(EST) / float(N) * 100
IE_SHARE = sum(PROFILE["IE"]) / EST_IN_HZ * 100
# initiatives still In Progress whose estimated window closed before the horizon opened
OVERRUN = [p for p in TIER_A
           if p["stage"] == "In Progress"
           and add_months(p["start"], int(round(p["dur"]))) <= H_START]
NO_DATE = [p for p in PROJ if not p["start"]]
NO_DUR = [p for p in PROJ if not p["dur"]]
UNFUNDED = [p for p in PROJ if not p["budget"]]

# ================================================================ TITLE BLOCK
add("", "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;" % RED,
    X0, 24, 8, 62)
txt("Demand Profile: Next 12 Months &#8212; Short-Term Projects Pipeline",
    44, 21, 1180, 28, fs=20, col=RED, bold=True)
txt("<b>Mineral Resources Limited</b>&#160;&#160;·&#160;&#160;<b>%d in-scope initiatives</b> "
    "&#8212; In Progress %d&#160;·&#160;Opportunity %d&#160;&#160;·&#160;&#160;"
    "<b><font color=\"%s\">IN PROGRESS AND OPPORTUNITY ONLY &#8212; %d rows excluded "
    "(On Hold %d, Complete %d, Cancelled %d)</font></b><br>"
    "SCOR <b>Plan</b> process, Section 2 of the rule: 2.1 demand forecasting, 2.2 capacity "
    "and resource planning, 2.3 business rules. The constrained supply in this pipeline is "
    "<b>internal delivery labour</b>, not equipment, so Source / Make / Deliver / Return "
    "are out of scope here. Purpose: <b>size and shape the next 12 months of resource "
    "demand</b> &#8212; it is not an investment case and not a schedule."
    % (N, N_IP, N_OP, RED, N_EXCL, EXCLUDED.get("On Hold", 0),
       EXCLUDED.get("Complete", 0), EXCLUDED.get("Cancelled", 0)),
    44, 50, 1420, 44, fs=8.5)
txt("Prepared for: <b>Portfolio &amp; Resource Governance</b><br>"
    "Source: input/Projects Pipeline - Short Term.csv (generated, not hand-drawn)<br>"
    "Rule: .claude/rules/SCOR_demand_planning.html<br>"
    "%d %s %d&#160;&#160;·&#160;&#160;<b>Draft &#8212; %.0f%% of in-scope initiatives carry "
    "no labour estimate; the allowance is parametric, not sponsor-confirmed</b>"
    % (RUN_DATE.day, ["January", "February", "March", "April", "May", "June", "July",
                      "August", "September", "October", "November", "December"]
       [RUN_DATE.month - 1], RUN_DATE.year, 100 - COVERAGE),
    1520, 22, 701, 58, fs=7.5, col=GREY, align="right")

cw = 150
for i, (st, cnt) in enumerate([("In Progress", N_IP), ("Opportunity", N_OP)]):
    s = STAGE[st]
    add("%s (%d)" % (st, cnt),
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=%s;"
        "fontSize=7;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;"
        % (s["fill"], s["line"], CG, s["ink"]),
        RIGHT - 2 * (cw + 4) + i * (cw + 4), 84, cw, 14)

# ================================================================ SECTION 1
Y = 108
band(Y, 22, "1&#160;&#160;DEMAND CONTEXT &amp; UNIT OF DEMAND",
     "SCOR Section 1 &#8212; define the demand before forecasting it")
Y += 26
CTX = [
    ("Planning horizon",
     "<b>%s &#8594; %s</b>, 12 calendar months from the run date. Monthly buckets. Each "
     "initiative's labour is prorated by <b>calendar-day overlap</b> of its window "
     "(start &#8594; start + duration), so work straddling the horizon edge contributes "
     "only the part inside it."
     % (HZ_LABEL[0], HZ_LABEL[11])),
    ("Scope filter (as requested)",
     "<b>Stage = In Progress or Opportunity</b> only: %d of %d rows. <b>%d excluded</b> "
     "&#8212; On&#160;Hold %d, Complete %d, Cancelled %d. On&#160;Hold is real latent "
     "demand and is <b>not</b> in this profile; treat it as a queue behind it."
     % (N, len(ROWS), N_EXCL, EXCLUDED.get("On Hold", 0), EXCLUDED.get("Complete", 0),
        EXCLUDED.get("Cancelled", 0))),
    ("Unit of demand",
     "<b>Internal delivery labour days by role</b>: PM, BA, IE, CD, SA, Other. Converted "
     "to FTE at <b>%d working days = 1 FTE-month</b> (stated assumption &#8212; not in the "
     "source). <b>CD demand is nil</b> across all %d in-scope initiatives, so it carries "
     "no series on the chart."
     % (DAYS_PER_FTE_MONTH, N)),
    ("Supply model",
     "<b>Engineer-to-Order analogue.</b> Each initiative is a bespoke deployment with a "
     "long lead time and site-specific design &#8212; SCOR's ETO assumptions hold, but the "
     "scarce input is <b>skilled internal delivery capacity</b>, so lead time is measured "
     "in people-months, not shipping weeks."),
    ("Estimate coverage",
     "<b>%d of %d</b> initiatives carry any labour estimate (<b>%.0f%%</b>), totalling "
     "<b>%s days</b>. <b><font color=\"%s\">%d initiatives (%.0f%%) are unquantified</font>"
     "</b>. Only <b>%d</b> carry start + duration + estimate together."
     % (len(EST), N, COVERAGE, num(EST_TOTAL), RED, len(UNQ), 100 - COVERAGE,
        len(TIER_A))),
    ("Sizing basis for the unquantified",
     "Quartiles of the %d estimated initiatives: <b>Q1 %s d</b> · <b>median %s d</b> · "
     "<b>Q3 %s d</b> (mean %s d &#8212; converges on Q3, so the high case is not an "
     "outlier artefact). These drive the downside / base / upside allowance."
     % (len(EST), num(Q1), num(Q2), num(Q3), num(MEAN_EST))),
]
for i, (ttl, desc) in enumerate(CTX):
    x, w = grid(6, 8)[i]
    box(head_desc(ttl, desc), x, Y, w, 76, "#FFFFFF", RULE, INK, fs=7.2)
Y += 76

# ================================================================ SECTION 2.1 - CHART
Y += 12
band(Y, 22, "2.1&#160;&#160;DEMAND FORECAST &#8212; MONTHLY RESOURCE DEMAND, %s &#8594; %s"
     % (HZ_LABEL[0].upper(), HZ_LABEL[11].upper()),
     "SCOR Section 2.1 &#8212; multi-scenario demand forecasting; labour days per month")
Y += 26

RX, RW = 1706, RIGHT - 1706          # right-hand scenario panel
PLOT_X, PLOT_R = 96, 1686
PLOT_W = PLOT_R - PLOT_X
PLOT_TOP = Y + 22
PLOT_H = 292
PLOT_BOT = PLOT_TOP + PLOT_H
PITCH = PLOT_W / 12.0
BARW = 92.0


def ypx(v):
    return PLOT_BOT - v / float(AXMAX) * PLOT_H


# legend row - single axis (labour days); the FTE restatement lives under the axis, not as
# a second tick column, so this is never read as a dual-axis chart.
txt("days", X0, Y, 66, 12, fs=6.8, col=GREY, align="right", bold=True)
txt("Estimated demand by role &#8212; stacked, largest role at the base:",
    PLOT_X, Y, 252, 12, fs=7, col=GREY)
lx = PLOT_X + 256
for name in ACTIVE_ROLES:
    rect(lx, Y + 2, 9, 9, SERIES_COL[name], SERIES_COL[name])
    txt("<b>%s</b> %s" % (name, ROLE_FULL[name]), lx + 13, Y - 1, 118, 12, fs=7, col=INK)
    lx += 132
rect(lx, Y + 2, 9, 9, ALLOW_FILL, ALLOW_LINE, dashed=True)
txt("<b>Allowance</b> &#8212; %d unquantified initiatives, median-sized, spread evenly"
    % len(UNQ), lx + 13, Y - 1, PLOT_R - lx - 13, 12, fs=7, col=ALLOW_INK)

# plot frame + gridlines
rect(PLOT_X, PLOT_TOP, PLOT_W, PLOT_H, "#FFFFFF", RULE)
g = 40
v = 0
while v <= AXMAX:
    yy = ypx(v)
    if v > 0:
        rect(PLOT_X + 1, yy, PLOT_W - 2, 1, "#EFEFEF", "none")
    txt("%d" % v, X0, yy - 6, 66, 12, fs=6.8, col=GREY, align="right")
    v += g

AVG = ALLOW["Base case"]["total"] / 12.0

# bars
for i in range(12):
    cx = PLOT_X + i * PITCH + PITCH / 2.0
    bx = cx - BARW / 2.0
    if i % 2 == 0:
        rect(PLOT_X + i * PITCH + 1, PLOT_TOP + 1, PITCH - 2, PLOT_H - 2, "#FCFCFB", "none")
    run = 0.0
    for name in ACTIVE_ROLES:
        val = PROFILE[name][i]
        if val <= 0:
            continue
        y1, y0 = ypx(run + val), ypx(run)
        hh = max(y0 - y1 - 2, 1)            # 2px surface gap between segments
        rect(bx, y1, BARW, hh, SERIES_COL[name], SERIES_COL[name])
        if hh >= 11:
            add("<b>%s</b>" % num(val),
                "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.6;fontColor=%s;"
                "align=center;verticalAlign=middle;" % (CG, SERIES_TXT[name]),
                bx, y1, BARW, hh)
        run += val
    # allowance cap
    y1, y0 = ypx(run + BASE_ALLOW), ypx(run)
    hh = max(y0 - y1 - 2, 1)
    rect(bx, y1, BARW, hh, ALLOW_FILL, ALLOW_LINE, dashed=True)
    if hh >= 11 and i == 0:
        add("<b>+%s</b><br><font style=\"font-size:5.8px\">allowance,<br>every month</font>"
            % num(BASE_ALLOW),
            "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=6.6;fontColor=%s;"
            "align=center;verticalAlign=middle;" % (CG, ALLOW_INK),
            bx, y1, BARW, hh)
    # month total above the bar
    tot = BASE_M[i]
    peak = " <font color=\"%s\">&#9650;peak</font>" % RED if i == PEAK_I else ""
    txt("<b>%s</b>%s" % (num(tot), peak), bx - 20, ypx(tot) - 15, BARW + 40, 13,
        fs=7, col=INK, align="center")

# base-case average threshold, drawn over the bars so it reads as a reference line
rect(PLOT_X + 1, ypx(AVG), PLOT_W - 2, 1, RED, "none")
txt("base-case average <b>%s d/mth &#8226; %.1f FTE</b>" % (num(AVG), AVG / DAYS_PER_FTE_MONTH),
    PLOT_R - 306, ypx(AVG) - 13, 302, 12, fs=6.6, col=RED, align="right")

# month axis labels
for i in range(12):
    cx = PLOT_X + i * PITCH + PITCH / 2.0
    fyr = HZ[i].year != HZ[i - 1].year if i else True
    txt("<b>%s</b>" % HZ_LABEL[i].replace(" ", "&#160;"),
        cx - PITCH / 2.0, PLOT_BOT + 4, PITCH, 12, fs=7.4,
        col=TEAL if fyr else INK, align="center")

# under-axis readout rows
RY = PLOT_BOT + 20
ROWS_OUT = [
    ("FTE required (base case)",
     [("%.1f" % (BASE_M[i] / DAYS_PER_FTE_MONTH)) for i in range(12)], INK, True),
    ("of which estimated", [num(EST_M[i]) for i in range(12)], "#1A7C87", False),
    ("of which allowance", [("+%s" % num(BASE_ALLOW)) for i in range(12)], ALLOW_INK, False),
]
for r, (lbl, vals, col, bold) in enumerate(ROWS_OUT):
    yy = RY + r * 15
    if r % 2 == 0:
        rect(X0, yy, PLOT_R - X0, 14, SURF if r == 0 else "#FFFFFF", "none")
    txt(lbl, X0 + 2, yy + 1, 66 + 4, 12, fs=6.4, col=GREY, align="right")
    for i in range(12):
        cx = PLOT_X + i * PITCH
        txt(("<b>%s</b>" % vals[i]) if bold else vals[i], cx, yy + 1, PITCH, 12,
            fs=6.8, col=col, align="center")

# chart reading note
NY = RY + 3 * 15 + 4
txt("<b><font color=\"%s\">How to read the shape, and what is not real about it.</font></b> "
    "The estimated bars fall away after <b>%s</b> and reach zero from <b>%s</b>. That is "
    "<b>not</b> a fall in demand &#8212; it is the horizon of the source data. %d of %d "
    "in-scope initiatives have no start date and %d have no duration, so nothing can be "
    "placed in the back half of the year. The <b>allowance</b> band is flat for the same "
    "reason: with no dates, an even spread is the only defensible placement, and it is "
    "certainly wrong month by month even if the annual pool is right. Read the annual "
    "pool and the peak, not the month-to-month contour. Estimated demand falling outside "
    "the horizon (earlier starts, longer tails): <b>%s days</b>."
    % (RED, HZ_LABEL[4], HZ_LABEL[9], len(NO_DATE), N, len(NO_DUR), num(OUTSIDE)),
    X0, NY, PLOT_R - X0 - 4, 46, fs=6.9)

# ---------------------------------------------------------------- scenario panel
SY = Y
box("", RX, SY, RW, (NY + 46) - SY, "#FCFCFB", RULE, INK)
txt("SCOR 2.1 &#8212; THREE DEMAND SCENARIOS", RX + 10, SY + 7, RW - 20, 12,
    fs=8, col=TEAL, bold=True)
txt("All three hold the %d estimated initiatives constant on their own dates "
    "(<b>%s days in horizon</b>) and vary only how the <b>%d unquantified</b> initiatives "
    "are sized. Estimate coverage &#8212; not commodity price &#8212; is the dominant "
    "uncertainty in this data set, so that is what the scenarios flex."
    % (len(EST), num(EST_IN_HZ), len(UNQ)),
    RX + 10, SY + 22, RW - 20, 34, fs=6.8, col=GREY)

sy = SY + 58
SBAR_X = RX + 128
SBAR_W = RW - 128 - 96
SMAX = max(ALLOW[n]["total"] for n, _s, _p, _f, _l, _i in SCEN)
for name, sub, per, fill, line, ink in SCEN:
    a = ALLOW[name]
    is_base = name == "Base case"
    box("", RX + 8, sy, RW - 16, 46, fill if is_base else "#FFFFFF",
        line if is_base else RULE, INK)
    txt("<b>%s</b><br><font color=\"%s\" style=\"font-size:6.2px\">%s &#8212; %s d/initiative</font>"
        % (name, GREY, sub, num(per)), RX + 14, sy + 5, 116, 26, fs=7.6, col=ink)
    # stacked horizontal bar: estimated (teal) + allowance (grey)
    ew = EST_IN_HZ / SMAX * SBAR_W
    aw = a["pool"] / SMAX * SBAR_W
    rect(SBAR_X, sy + 8, ew, 13, "#3F939C", "#3F939C")
    rect(SBAR_X + ew + 2, sy + 8, max(aw - 2, 1), 13, ALLOW_FILL, ALLOW_LINE, dashed=True)
    txt("<b>%s d</b>" % num(a["total"]), SBAR_X, sy + 24, SBAR_W - 12, 12, fs=6.6, col=INK)
    txt("<b>%.1f</b> FTE avg<br><font style=\"font-size:6.2px\">%.1f FTE peak</font>"
        % (a["total"] / 12.0 / DAYS_PER_FTE_MONTH,
           (max(EST_M) + a["per_month"]) / DAYS_PER_FTE_MONTH),
        RIGHT - 100, sy + 8, 92, 30, fs=7.6, col=ink, align="right")
    sy += 50

txt("<b>Peak month is %s</b> at <b>%s days / %.1f FTE</b> in the base case "
    "(estimated demand alone peaks in %s). The <b>%.0f&#215; spread</b> between downside "
    "and upside is the cost of not estimating: at Q1 sizing the portfolio needs "
    "<b>%.1f FTE</b> on average, at Q3 sizing it needs <b>%.1f FTE</b>. No resourcing "
    "decision can be made across that range &#8212; closing it is an estimation task, not "
    "a forecasting one."
    % (HZ_LABEL[PEAK_I], num(max(BASE_M)), max(BASE_M) / DAYS_PER_FTE_MONTH,
       HZ_LABEL[EST_PEAK_I], ALLOW["Upside"]["total"] / ALLOW["Downside"]["total"],
       ALLOW["Downside"]["total"] / 12.0 / DAYS_PER_FTE_MONTH,
       ALLOW["Upside"]["total"] / 12.0 / DAYS_PER_FTE_MONTH),
    RX + 10, sy + 2, RW - 20, 56, fs=6.9)

txt("<b>Forecast accuracy (SCOR 2.1).</b> The mining-sector MAPE benchmark in the rule is "
    "<b>15&#8211;25%%</b>. This profile cannot be held to it: with <b>%.0f%%</b> estimate "
    "coverage the error is dominated by <b>missing scope</b>, not by forecasting method. "
    "Establish the benchmark once coverage clears 80%%; until then track coverage as the "
    "leading indicator."
    % COVERAGE, RX + 10, sy + 60, RW - 20, 40, fs=6.9, col=GREY)

Y = NY + 46

# ================================================================ SECTION 2.2
Y += 12
band(Y, 22, "2.2&#160;&#160;CAPACITY &amp; RESOURCE PLANNING",
     "SCOR Section 2.2 &#8212; resource requirements by role, initiative register, and the "
     "unquantified pool")
Y += 26
CH = 286
C1 = 726
C2 = 704
C3 = W - C1 - C2 - 16
CX1 = X0
CX2 = X0 + C1 + 8
CX3 = CX2 + C2 + 8

# ---------------------------------------------------------------- role table
box("", CX1, Y, C1, CH, "#FFFFFF", RULE, INK)
txt("A&#160;&#160;RESOURCE REQUIREMENTS BY ROLE &#8212; estimated demand only",
    CX1 + 10, Y + 7, C1 - 20, 12, fs=8, col=TEAL, bold=True)
txt("Capacity and gap are <b>left blank on purpose</b>: the source carries no team "
    "establishment. They are the resource owner's input, not an analyst assumption.",
    CX1 + 10, Y + 21, C1 - 20, 22, fs=6.6, col=GREY)

COLS = [(0, 168, "Role", "left"), (168, 78, "Days in<br>horizon", "right"),
        (246, 74, "FTE-<br>months", "right"), (320, 74, "Peak mth<br>FTE", "right"),
        (394, 62, "Share", "right"), (456, 130, "Establishment<br>(to confirm)", "center"),
        (586, 130, "Gap<br>(to confirm)", "center")]
ty = Y + 46
rect(CX1 + 8, ty, C1 - 16, 20, SURF, "none")
for ox, cwd, lbl, al in COLS:
    txt("<b>%s</b>" % lbl, CX1 + 10 + ox, ty + 2, cwd - 4, 18, fs=6.4, col=TEAL, align=al)
ty += 21
for name in SERIES_ORDER + ["CD"]:
    tot = sum(PROFILE[name])
    pk = max(PROFILE[name]) if tot else 0.0
    nil = tot <= 0
    rect(CX1 + 8, ty, C1 - 16, 19, "#FCFCFB" if nil else "#FFFFFF", "none")
    if not nil:
        rect(CX1 + 10, ty + 5, 8, 8, SERIES_COL[name], SERIES_COL[name])
    vals = [("<b>%s</b>&#160;&#160;<font color=\"%s\" style=\"font-size:6.2px\">%s</font>"
             % (name, GREY, ROLE_FULL[name]), "left"),
            ("&#8212;" if nil else "<b>%s</b>" % num(tot), "right"),
            ("&#8212;" if nil else "%.1f" % (tot / DAYS_PER_FTE_MONTH), "right"),
            ("&#8212;" if nil else "%.1f" % (pk / DAYS_PER_FTE_MONTH), "right"),
            ("&#8212;" if nil else "%.0f%%" % (tot / EST_IN_HZ * 100), "right")]
    for (ox, cwd, _l, al), (v, va) in zip(COLS[:5], vals):
        txt(v, CX1 + 10 + ox + (12 if ox == 0 and not nil else 0), ty + 3,
            cwd - 4 - (12 if ox == 0 and not nil else 0), 15,
            fs=6.8, col="#A5A5A5" if nil else INK, align=va)
    for ox, cwd, _l, _al in COLS[5:]:
        rect(CX1 + 12 + ox, ty + 3, cwd - 8, 13, "#FFFFFF", RULE)
    ty += 19
rect(CX1 + 8, ty, C1 - 16, 20, SURF, "none")
txt("<b>TOTAL estimated</b>", CX1 + 10, ty + 3, 164, 16, fs=6.8, col=TEAL)
txt("<b>%s</b>" % num(EST_IN_HZ), CX1 + 178, ty + 3, 74, 16, fs=6.8, col=TEAL, align="right")
txt("<b>%.1f</b>" % (EST_IN_HZ / DAYS_PER_FTE_MONTH), CX1 + 256, ty + 3, 70, 16,
    fs=6.8, col=TEAL, align="right")
txt("<b>%.1f</b>" % (max(EST_M) / DAYS_PER_FTE_MONTH), CX1 + 330, ty + 3, 70, 16,
    fs=6.8, col=TEAL, align="right")
txt("<b>100%</b>", CX1 + 404, ty + 3, 58, 16, fs=6.8, col=TEAL, align="right")
ty += 24
txt("<b><font color=\"%s\">%s carries %.0f%% of all estimated demand in the horizon.</font></b> "
    "Roles are not interchangeable: <b>IE is %.0f%%</b> of estimated demand and is the "
    "binding constraint. <b>CD demand is nil</b> across all %d in-scope initiatives &#8212; "
    "either change and adoption effort is genuinely not planned, or it is being absorbed "
    "unrecorded. Both are worth a decision."
    % (RED, h(TOP1["title"]), TOP1["in_horizon"] / EST_IN_HZ * 100, IE_SHARE, N),
    CX1 + 10, ty, C1 - 20, 40, fs=6.9)

# ---------------------------------------------------------------- initiative register
box("", CX2, Y, C2, CH, "#FFFFFF", RULE, INK)
txt("B&#160;&#160;ESTIMATED INITIATIVE REGISTER &#8212; every initiative carrying an estimate",
    CX2 + 10, Y + 7, C2 - 20, 12, fs=8, col=TEAL, bold=True)
txt("Tier <b>A</b> start + duration + estimate (placed as estimated) · <b>B</b> start, no "
    "duration (placed at portfolio-median %s months) · <b>C</b> no start (placed from "
    "horizon month 1)." % num(MED_DUR),
    CX2 + 10, Y + 21, C2 - 20, 22, fs=6.6, col=GREY)
RCOLS = [(0, 262, "Initiative", "left"), (262, 34, "Tier", "center"),
         (296, 62, "Start", "left"), (358, 44, "Dur", "right"),
         (402, 58, "Est<br>days", "right"), (460, 66, "In horizon", "right"),
         (526, 62, "Days /<br>month", "right")]
ty = Y + 46
rect(CX2 + 8, ty, C2 - 16, 20, SURF, "none")
for ox, cwd, lbl, al in RCOLS:
    txt("<b>%s</b>" % lbl, CX2 + 10 + ox, ty + 2, cwd - 4, 18, fs=6.4, col=TEAL, align=al)
ty += 21
for k, p in enumerate(sorted(EST, key=lambda q: (-q["in_horizon"], q["title"]))):
    s = STAGE[p["stage"]]
    if k % 2 == 0:
        rect(CX2 + 8, ty, C2 - 16, 16, "#FCFCFB", "none")
    rate = p["days"] / p["win_dur"] if p["win_dur"] else 0.0
    over = p in OVERRUN
    ttl = h(p["title"])
    if over:
        ttl += " <font color=\"%s\">&#9650;</font>" % RED
    txt(ttl, CX2 + 10, ty + 2, 250, 15, fs=6.6, col=INK)
    txt(p["tier"], CX2 + 272 - 10, ty + 2, 30, 15, fs=6.6,
        col=s["ink"], align="center", bold=True)
    txt(short_date(p["start"]) or "<font color=\"%s\">none</font>" % RED,
        CX2 + 306, ty + 2, 48, 15, fs=6.6, col=INK)
    txt(num(p["dur"]) if p["dur"] else "<font color=\"%s\">none</font>" % RED,
        CX2 + 358, ty + 2, 40, 15, fs=6.6, col=INK, align="right")
    txt("<b>%s</b>" % num(p["days"]), CX2 + 402, ty + 2, 54, 15, fs=6.6, col=INK,
        align="right")
    txt(num(p["in_horizon"]) if p["in_horizon"] > 0
        else "<font color=\"%s\">0</font>" % RED,
        CX2 + 460, ty + 2, 62, 15, fs=6.6, col=INK, align="right")
    txt(num(rate), CX2 + 526, ty + 2, 58, 15, fs=6.6, col=GREY, align="right")
    ty += 17
rect(CX2 + 8, ty, C2 - 16, 19, SURF, "none")
txt("<b>%d initiatives estimated</b>" % len(EST), CX2 + 10, ty + 3, 250, 15,
    fs=6.6, col=TEAL)
txt("<b>%s</b>" % num(EST_TOTAL), CX2 + 402, ty + 3, 54, 15, fs=6.6, col=TEAL, align="right")
txt("<b>%s</b>" % num(EST_IN_HZ), CX2 + 460, ty + 3, 62, 15, fs=6.6, col=TEAL, align="right")
ty += 23
txt("<b><font color=\"%s\">&#9650; %s</font></b> is still <b>In Progress</b> but its "
    "estimated window closed <b>%s</b>, before this horizon opened &#8212; so it "
    "contributes <b>0 days</b> to the profile while still consuming real effort. Either the "
    "stage or the dates are wrong. Top two initiatives are <b>%.0f%%</b> of all estimated "
    "demand: the profile is a small-sample view of a large portfolio."
    % (RED, h(OVERRUN[0]["title"]) if OVERRUN else "&#8212;",
       short_date(add_months(OVERRUN[0]["start"], int(round(OVERRUN[0]["dur"]))))
       if OVERRUN else "&#8212;", TOP2_SHARE),
    CX2 + 10, ty, C2 - 20, 40, fs=6.9)

# ---------------------------------------------------------------- unquantified pool
box("", CX3, Y, C3, CH, "#FCFCFB", RULE, INK)
txt("C&#160;&#160;UNQUANTIFIED POOL &#8212; %d initiatives, no labour estimate" % len(UNQ),
    CX3 + 10, Y + 7, C3 - 20, 12, fs=8, col=TEAL, bold=True)
txt("Everything below is <b>in scope and unsized</b>. It is the allowance band on the "
    "chart. Sponsor and stage shown so the list can be worked through by owner.",
    CX3 + 10, Y + 21, C3 - 20, 22, fs=6.6, col=GREY)
ULIST = sorted(UNQ, key=lambda p: (p["stage"], p["title"]))
UC = 3
ucw = (C3 - 20 - (UC - 1) * 6) / float(UC)
per_col = (len(ULIST) + UC - 1) // UC
ty = Y + 44
for ci in range(UC):
    chunk = ULIST[ci * per_col:(ci + 1) * per_col]
    cx = CX3 + 10 + ci * (ucw + 6)
    for j, p in enumerate(chunk):
        s = STAGE[p["stage"]]
        yy = ty + j * 15
        rect(cx, yy, ucw, 14, s["fill"], s["line"])
        rect(cx, yy, 2, 14, s["ink"], "none")
        txt("%s <font color=\"%s\" style=\"font-size:5.8px\">%s</font>"
            % (h(p["title"]), s["ink"],
               h(p["sponsor"]) if p["sponsor"] else "no sponsor"),
            cx + 5, yy + 1, ucw - 8, 12, fs=6.1, col=INK)
uy = ty + per_col * 15 + 4
txt("<b>Sizing.</b> No initiative here can be placed in time or sized from the source. The "
    "allowance uses the quartiles of the %d estimated initiatives &#8212; <b>Q1 %s</b> / "
    "<b>median %s</b> / <b>Q3 %s</b> days each &#8212; giving pools of <b>%s</b> / "
    "<b>%s</b> / <b>%s</b> days over the horizon. The estimated sample is heavily skewed "
    "(one initiative is %s days), so the median understates a pool that contains several "
    "large infrastructure and cyber programs; <b>Q3 is the more realistic central case</b> "
    "if the pool resembles the estimated sample."
    % (len(EST), num(Q1), num(Q2), num(Q3), num(ALLOW["Downside"]["pool"]),
       num(ALLOW["Base case"]["pool"]), num(ALLOW["Upside"]["pool"]), num(TOP1["days"])),
    CX3 + 10, uy, C3 - 20, 58, fs=6.8)
Y += CH

# ================================================================ SECTION 2.3
Y += 12
band(Y, 22, "2.3&#160;&#160;BUSINESS RULES &amp; ALIGNMENT PROCESSES",
     "SCOR Section 2.3 &#8212; the decision rules this profile obliges, with trigger points")
Y += 26
BH = 140
RULES = [
    ("Rule 1", "Demand admission &#8212; no estimate, no place in the plan",
     "<b>Trigger:</b> an initiative reaches Opportunity gate or is set In Progress.<br>"
     "<b>Rule:</b> it does not enter the 12-month resource plan without <b>start date + "
     "duration + role-level day estimate</b>. Until all three exist it sits in the "
     "unquantified pool and is planned for by allowance, not by name.<br>"
     "<b>Why:</b> %d of %d in-scope initiatives (%.0f%%) currently fail this test, which is "
     "why the downside-to-upside spread is <b>%.0f&#215;</b>. Nothing else on this page can "
     "be fixed before this one is."
     % (len(UNQ), N, 100 - COVERAGE,
        ALLOW["Upside"]["total"] / ALLOW["Downside"]["total"])),
    ("Rule 2", "Sourcing &#8212; make, buy or contract, decided by role and by month",
     "<b>Trigger:</b> monthly demand for a role exceeds confirmed establishment for "
     "<b>two consecutive months</b>.<br>"
     "<b>Rule:</b> permanent hire only where demand is sustained beyond the horizon; "
     "contract for peaks; vendor-delivered for one-off deployments with no retained-skill "
     "need.<br>"
     "<b>Why:</b> demand is <b>role-specific and lumpy</b> &#8212; <b>IE at %.0f%%</b> of "
     "estimated demand, peaking at <b>%.1f FTE</b> in %s. A single blended-FTE number would "
     "hide the only constraint that matters. Establishment must be supplied before this "
     "rule can be evaluated."
     % (IE_SHARE, max(PROFILE["IE"]) / DAYS_PER_FTE_MONTH,
        HZ_LABEL[max(range(12), key=lambda i: PROFILE["IE"][i])])),
    ("Rule 3", "Levelling &amp; sequencing &#8212; protect the peak, sequence the platform",
     "<b>Trigger:</b> base-case demand in any month exceeds the annual average by "
     "<b>&gt;25%%</b>.<br>"
     "<b>Rule:</b> defer discretionary Opportunity work out of the peak before adding "
     "capacity; platform and network work sequences <b>ahead</b> of the initiatives that "
     "depend on it.<br>"
     "<b>Why:</b> %s peaks at <b>%s days (%.1f FTE)</b> against a <b>%s day (%.1f FTE)</b> "
     "average &#8212; <b>%.0f%% above</b>. The peak is built from two large programs "
     "running concurrently, so levelling is a sequencing decision, not a hiring one."
     % (HZ_LABEL[PEAK_I], num(max(BASE_M)), max(BASE_M) / DAYS_PER_FTE_MONTH,
        num(AVG), AVG / DAYS_PER_FTE_MONTH, (max(BASE_M) / AVG - 1) * 100)),
    ("Rule 4", "Commitment &#8212; unfunded demand is not committed capacity",
     "<b>Trigger:</b> resource is allocated against an initiative.<br>"
     "<b>Rule:</b> only <b>budget-approved</b> initiatives draw on committed capacity. "
     "Unfunded work is planned as <b>contingent demand</b> and released on funding "
     "approval, with the resourcing lead time stated.<br>"
     "<b>Why:</b> <b>%d of %d</b> in-scope initiatives carry no approved budget. Treating "
     "them as committed would over-commit the establishment; treating them as absent would "
     "leave no lead time when funding lands."
     % (len(UNFUNDED), N)),
]
for i, (tag, ttl, body) in enumerate(RULES):
    x, w = grid(4, 8)[i]
    box("", x, Y, w, BH, "#FFFFFF", RULE, INK)
    rect(x, Y, w, 3, TEAL)
    txt("<b><font color=\"%s\">%s</font>&#160;&#160;%s</b>" % (RED, tag, ttl),
        x + 10, Y + 9, w - 20, 26, fs=7.6, col=TEAL)
    txt(body, x + 10, Y + 38, w - 20, BH - 46, fs=6.9)
Y += BH

# ================================================================ RISK + KPI
Y += 12
band(Y, 22, "3&#160;&#160;RISK REGISTER &amp; DEMAND-PLANNING KPIs",
     "SCOR Sections 7.2 and 8 &#8212; what could make this profile wrong, and what to "
     "measure so you find out")
Y += 26
KH = 168
KW = 604
RSW = W - KW - 8

box("", X0, Y, RSW, KH, "#FFFFFF", RULE, INK)
txt("RISKS TO THE DEMAND PROFILE", X0 + 10, Y + 7, RSW - 20, 12, fs=8, col=TEAL, bold=True)
RISKS = [
    ("R1", "Critical", "Estimate coverage",
     "%.0f%% of in-scope initiatives are unsized. The profile's central estimate is a "
     "parametric allowance, not a forecast." % (100 - COVERAGE),
     "Estimate the %d unquantified initiatives to role level. Sequence by stage: In "
     "Progress first, then Opportunity by expected gate date." % len(UNQ)),
    ("R2", "Serious", "Single-initiative concentration",
     "%s alone is %.0f%% of estimated demand and the top two are %.0f%%. Its slip or "
     "re-scope moves the whole profile." % (h(TOP1["title"]),
                                            TOP1["days"] / EST_TOTAL * 100, TOP2_SHARE),
     "Re-baseline these two monthly, not quarterly. Treat their estimates as the profile's "
     "primary sensitivity."),
    ("R3", "Serious", "Role bottleneck, not headcount",
     "IE is %.0f%% of estimated demand, peaking at %.1f FTE. A headcount-level plan would "
     "read as balanced while IE is over-committed."
     % (IE_SHARE, max(PROFILE["IE"]) / DAYS_PER_FTE_MONTH),
     "Plan and report capacity by role, never blended. Confirm IE establishment first."),
    ("R4", "Moderate", "Date and stage integrity",
     "%d in-scope initiatives have no start date and %d no duration. %d In Progress "
     "initiative's estimated window closed before the horizon opened."
     % (len(NO_DATE), len(NO_DUR), len(OVERRUN)),
     "Stage and dates must agree. Re-date or re-stage on exception; make it a gate check."),
    ("R5", "Moderate", "Back-half blindness",
     "Estimated demand reaches zero from %s. Any real work in the back half of the horizon "
     "is invisible, so late-year over-commitment cannot be detected." % HZ_LABEL[9],
     "Require indicative dates on Opportunity work at gate, even at low confidence, and "
     "re-forecast the profile monthly."),
]
SEV = {"Critical": ("#F4D9DD", "#E8A5AD", "#8B2E45"),
       "Serious": ("#F5E5DD", "#E8C4B0", "#8E5239"),
       "Moderate": ("#F1EDE7", "#D9CDB8", "#6B5435")}
ty = Y + 24
rect(X0 + 8, ty, RSW - 16, 17, SURF, "none")
for ox, cwd, lbl in [(0, 26, "#"), (26, 68, "Severity"), (94, 170, "Risk"),
                     (264, 560, "What it does to the profile"),
                     (824, RSW - 844, "Mitigation")]:
    txt("<b>%s</b>" % lbl, X0 + 10 + ox, ty + 2, cwd - 4, 14, fs=6.4, col=TEAL)
ty += 18
for k, (rid, sev, name, effect, mit) in enumerate(RISKS):
    f, l, ik = SEV[sev]
    hh = 25
    if k % 2 == 0:
        rect(X0 + 8, ty, RSW - 16, hh - 1, "#FCFCFB", "none")
    txt("<b>%s</b>" % rid, X0 + 10, ty + 5, 22, 14, fs=6.6, col=INK)
    add(sev, "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontFamily=%s;"
             "fontSize=6;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;"
             % (f, l, CG, ik), X0 + 34, ty + 5, 60, 13)
    txt("<b>%s</b>" % name, X0 + 104, ty + 4, 164, 20, fs=6.6, col=INK)
    txt(effect, X0 + 274, ty + 4, 554, 20, fs=6.5)
    txt(mit, X0 + 834, ty + 4, RSW - 848, 20, fs=6.5, col=GREY)
    ty += hh

box("", X0 + RSW + 8, Y, KW, KH, "#FFFFFF", RULE, INK)
txt("KPIs &#8212; SCOR 7.2, adapted to a project-demand portfolio",
    X0 + RSW + 18, Y + 7, KW - 20, 12, fs=8, col=TEAL, bold=True)
KPIS = [
    ("Estimate coverage", "%.0f%%" % COVERAGE, "target &#8805;80%", RED,
     "%d of %d sized. <b>Leading indicator</b> &#8212; nothing else is trustworthy below "
     "this." % (len(EST), N)),
    ("Scenario spread", "%.0f&#215;" % (ALLOW["Upside"]["total"] / ALLOW["Downside"]["total"]),
     "target &#8804;1.5&#215;", RED,
     "Downside to upside range. Collapses as coverage rises."),
    ("Peak-to-average", "%.0f%%" % ((max(BASE_M) / AVG - 1) * 100), "target &#8804;25%",
     "#8E5239", "%s peak vs annual average. Levelling KPI." % HZ_LABEL[PEAK_I]),
    ("Role concentration", "%.0f%%" % IE_SHARE, "watch", "#8E5239",
     "IE share of estimated demand. Flags the binding constraint."),
    ("Schedule integrity", "%.0f%%" % (len([p for p in PROJ if p["start"]]) / float(N) * 100),
     "target 100%", "#8E5239", "%d of %d carry a start date." % (N - len(NO_DATE), N)),
    ("Funded share", "%.0f%%" % ((N - len(UNFUNDED)) / float(N) * 100), "context", TEAL,
     "Budget-approved share &#8212; separates committed from contingent demand."),
]
kx, ky = X0 + RSW + 16, Y + 24
kw = (KW - 32 - 8) / 2.0
for i, (name, val, tgt, col, note) in enumerate(KPIS):
    x = kx + (i % 2) * (kw + 8)
    y = ky + (i // 2) * 44
    box("", x, y, kw, 42, "#FCFCFB", RULE, INK)
    rect(x, y, 3, 42, col)
    txt("<b>%s</b>" % name, x + 10, y + 3, kw - 98, 12, fs=6.8, col=TEAL)
    txt("<b>%s</b>" % val, x + kw - 86, y + 2, 78, 15, fs=12, col=col, align="right")
    txt("<font color=\"%s\" style=\"font-size:5.8px\">%s</font><br>%s" % (GREY, tgt, note),
        x + 10, y + 18, kw - 20, 22, fs=6.2)
Y += KH

# ================================================================ FOOTER
Y += 12
band(Y, 22, "METHOD, ASSUMPTIONS, WHAT IS NOT HERE, AND NEXT STEPS",
     "read this before quoting a number off the page")
Y += 26
FH = 122
box("", X0, Y, W, FH, SURF, "#D9CDB8", INK)
txt("<b>Method.</b> %d rows read; Stage filtered to In Progress and Opportunity per the "
    "request (%d in scope, %d excluded). Labour days per role prorated onto calendar months "
    "by day-overlap of each initiative's window (start &#8594; start + duration months). "
    "Tier B (start, no duration) uses the portfolio-median duration of <b>%s months</b>; "
    "Tier C (no start) is placed from horizon month 1. Unquantified initiatives are sized "
    "at the Q1 / median / Q3 of the %d estimated initiatives and spread evenly, because no "
    "dates exist. FTE at <b>%d days per FTE-month</b>. Series colours were chosen by "
    "running the dataviz validator over the MinRes brand ramps &#8212; CVD separation "
    "&#916;E&#160;16.1 on the adjacent pairlist; the brand's low chroma fails that check "
    "and is relieved by direct labels plus the full table above.<br>"
    "<b>Assumptions to confirm:</b> even in-month spread of each initiative's labour (real "
    "profiles ramp and taper); even spread of the allowance across the horizon; median "
    "duration applied to Tier B and C; %d working days per FTE-month; and that the "
    "unquantified pool resembles the estimated sample. The <b>Q3 allowance is the more "
    "realistic central case</b> if it does, because the pool holds several large "
    "infrastructure and cyber programs while the median is dragged down by small studies.<br>"
    "<b>What is not here.</b> <b>On Hold (%d) is excluded by the requested filter</b> and "
    "is real latent demand &#8212; a queue immediately behind this profile. No team "
    "establishment or available capacity (not in the source), so <b>no gap is calculated</b> "
    "and the capacity columns are deliberately blank. No dependencies between initiatives, "
    "no benefit cases, no cost, no non-labour demand (equipment, vendor, capital), no "
    "external SCOR processes (Source / Make / Deliver / Return), and no delivery track "
    "record from the %d Complete and Cancelled rows.<br>"
    "<b>Next steps, in order.</b> 1&#160;Estimate the %d unquantified initiatives to role "
    "level &#8212; In Progress first. 2&#160;Supply the role establishment so a gap and a "
    "sourcing decision become possible. 3&#160;Give every in-scope initiative a start date "
    "and duration; re-stage or re-date the %d whose window has already closed. 4&#160;Level "
    "the %s peak by sequencing, before considering capacity. 5&#160;Re-cut this page monthly "
    "and track estimate coverage as the leading KPI."
    % (len(ROWS), N, N_EXCL, num(MED_DUR), len(EST), DAYS_PER_FTE_MONTH,
       DAYS_PER_FTE_MONTH, EXCLUDED.get("On Hold", 0),
       EXCLUDED.get("Complete", 0) + EXCLUDED.get("Cancelled", 0), len(UNQ),
       len(OVERRUN), HZ_LABEL[PEAK_I]),
    X0 + 14, Y + 8, W - 28, FH - 14, fs=6.9)
Y += FH

txt("Mineral Resources Limited&#160;&#160;·&#160;&#160;Demand Profile, one-page view"
    "&#160;&#160;·&#160;&#160;<b>In Progress and Opportunity only</b>&#160;&#160;·"
    "&#160;&#160;SCOR Plan process&#160;&#160;·&#160;&#160;A2 landscape&#160;&#160;·"
    "&#160;&#160;Generated from input/Projects Pipeline - Short Term.csv &#8212; regenerate "
    "the page rather than editing it by hand",
    X0, Y + 6, W, 12, fs=7, col="#888888", valign="middle")
BOTTOM = Y + 18

# ================================================================ assemble
PW, PGH = 2245, 1587
XML = (
    '<mxfile host="app.diagrams.net" agent="Claude Code" version="24.0.0" type="device">\n'
    '  <diagram name="Demand Profile - Next 12 Months" id="minres-pipeline-demand">\n'
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
    dest = os.path.join(outdir, "MinRes_Projects_Pipeline_Demand_Profile.drawio")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(XML)
    print("wrote %s" % dest)
    print("in scope = %d (In Progress %d, Opportunity %d) ; excluded = %d %s"
          % (N, N_IP, N_OP, N_EXCL, EXCLUDED))
    print("horizon  = %s -> %s" % (HZ_LABEL[0], HZ_LABEL[11]))
    print("estimated = %d initiatives, %s days, %s in horizon (%s outside)"
          % (len(EST), num(EST_TOTAL), num(EST_IN_HZ), num(OUTSIDE)))
    print("tiers A=%d B=%d C=%d ; unquantified D=%d"
          % (len(TIER_A), len(TIER_B), len(TIER_C), len(UNQ)))
    print("quartiles Q1=%s Q2=%s Q3=%s (mean %s)"
          % (num(Q1), num(Q2), num(Q3), num(MEAN_EST)))
    for name, _s, _p, _f, _l, _i in SCEN:
        a = ALLOW[name]
        print("  %-10s pool %8s d  total %8s d  avg %5.1f FTE"
              % (name, num(a["pool"]), num(a["total"]),
                 a["total"] / 12.0 / DAYS_PER_FTE_MONTH))
    print("axis max = %d ; peak month = %s at %s d (%.1f FTE)"
          % (AXMAX, HZ_LABEL[PEAK_I], num(max(BASE_M)),
             max(BASE_M) / DAYS_PER_FTE_MONTH))
    print("nil roles = %s" % (NIL_ROLES or "none"))
    print("content bottom = %spx of %s ; %d cells" % (BOTTOM, PGH, _id[0] - 1))
