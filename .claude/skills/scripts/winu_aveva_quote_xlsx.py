"""Build the AVEVA MRL Greenfield budget-estimate breakdown workbook.

Splits the AVEVA proposal (36-slide PDF, Oct 2026) into Software, Hardware and
External Labour, with every line traced to a PDF page / table row.

Usage: python winu_aveva_quote_xlsx.py [output.xlsx]
"""
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output" / "Cost estimate" / "AVEVA_MRL_Greenfield_Quote_Breakdown.xlsx"
PDF_REL = "../../input/Vendor/AVEVA/Quote/Aveva Proposal MRL Greenfield Site.pdf"
RATE = 21.24  # AUD per Flex credit unit, "Flex Top-Up Rate" printed on PDF p.6-9

NAVY, GREY, AMBER = "1F3864", "F2F2F2", "FFF2CC"
HDR = PatternFill("solid", fgColor=NAVY)
INPUT = PatternFill("solid", fgColor="DDEBF7")
FLAG = PatternFill("solid", fgColor=AMBER)
SUB = PatternFill("solid", fgColor=GREY)
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY = '#,##0.00;[Red]-#,##0.00;"-"'
NUM = '#,##0;[Red]-#,##0;"-"'


def link(page):
    return f'=HYPERLINK("{PDF_REL}#page={page}","PDF p.{page}")'


def header(ws, row, cols):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HDR
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BOX
    ws.row_dimensions[row].height = 32


def title(ws, text, sub):
    ws["A1"] = text
    ws["A1"].font = Font(bold=True, size=14, color=NAVY)
    ws["A2"] = sub
    ws["A2"].font = Font(italic=True, color="595959")


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def style_body(ws, first, last, ncols, money=(), nums=(), wrap=()):
    for r in range(first, last + 1):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BOX
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if c in money:
                cell.number_format = MONEY
            if c in nums:
                cell.number_format = NUM


wb = Workbook()

# --------------------------------------------------------------------------
# SOFTWARE
# --------------------------------------------------------------------------
sw = wb.active
sw.title = "Software"
title(sw, "Software - AVEVA Flex subscription licences (annual, ex GST)",
      "Each row is one product line from the licence tables on PDF p.6-9. AUD per line is DERIVED (credits x rate); AVEVA only prints group totals.")
sw["A3"], sw["B3"], sw["C3"] = "Flex top-up rate", "AUD / credit unit (PDF p.6-9)", RATE
sw["C3"].fill, sw["C3"].number_format = INPUT, "0.00"
SW_COLS = ["Ref", "Source ID", "Product group", "Line item (plain English)", "AVEVA description (as printed)",
           "Product code", "Qty", "Credits / unit", "Total credits / yr", "Derived AUD / yr", "Status",
           "Cost basis", "PDF page", "Slide / table", "Table row", "Notes"]
header(sw, 5, SW_COLS)

PIDI, CON, PA, AMP = "PI Data Infrastructure (PIDI)", "CONNECT", "Predictive Analytics", "Production Management (Ampla)"
# (group, plain, printed, code, qty, credits/unit or None, status, page, slide, row, note)
SW = [
    (PIDI, "Core PI historian licence, 10,000 tags (data points), production", "PI Server (10,000 tags) / AVEVA PI Data Infrastructure 10K (GQ)", "FLEX-PIDI-018-GQ", 1, 3288, "Priced", 6, "PIDI - Flex subscription", 1, ""),
    (PIDI, "Connectivity pack: all interfaces to PI", "All interfaces / AVEVA PI System Connectivity Pack", "FLEX-PIDI-051", 1, None, "Included", 6, "PIDI - Flex subscription", 2, "Shown as 'Included' in the Rate Plan column."),
    (PIDI, "Client pack for 10 named users (x2 packs; description reads '10 Named users')", "10 Named users / AVEVA PI Client Pack 10", "FLEX-PIDI-054", 2, 456, "Priced", 6, "PIDI - Flex subscription", 3, "456 credits per pack x 2 packs = 912. Whether 2 packs = 20 users is not stated."),
    (PIDI, "CONNECT data services, up to 200 data streams (bundled)", "(included) CONNECT data services / CONNECT data services (up to 200 Data Stream)", "FLEX-ADH-001", 1, None, "Included", 6, "PIDI - Flex subscription", 4, "Same code is also listed as included on p.7 and p.9."),
    (PIDI, "CONNECT visualisation, up to 5 users (bundled)", "(included) CONNECT visualisation services / CONNECT visualisation (up to 5 CVS Users)", "FLEX-CVS-001", 1, None, "Included", 6, "PIDI - Flex subscription", 5, "Same code is also listed as included on p.7 and p.9."),
    (PIDI, "Test PI Server, 10,000 tags (non-production copy)", "Test PI Server (10,000 tags) / AVEVA PI Server - Test 10K", "(none printed)", 1, None, "Included", 6, "PIDI - Flex subscription", 6, "No product code printed."),
    (CON, "CONNECT anchor line (CONNECT sold alongside PIDI)", "CONNECT (with anchor product) / CONNECT when sold in addition to an AVEVA portfolio anchor product", "FLEX-CON-027-GQ", 1, None, "Header line (no credits shown)", 7, "CONNECT - Flex subscription", 1, "No credit value printed on this row; credits sit on the next row (FLEX-CON-028)."),
    (CON, "CONNECT Starter core services: 10,000 data streams + visualisation users matching PI users", "CONNECT (with anchor product) core services - Starter", "FLEX-CON-028", 1, 2004, "Priced", 7, "CONNECT - Flex subscription", 2, ""),
    (CON, "Cloud connectivity from plant data sources, incl. Edge Data Store and standard adapters", "CONNECT data services Connectivity Pack / AVEVA Cloud - Connectivity from industrial data sources", "FLEX-ADH-002", 1, None, "Included", 7, "CONNECT - Flex subscription", 3, ""),
    (CON, "CONNECT data services, up to 200 data streams (bundled)", "(included) CONNECT data services", "FLEX-ADH-001", 1, None, "Included", 7, "CONNECT - Flex subscription", 4, "Duplicate of p.6 row 4 and p.9 row 5 (all $0)."),
    (CON, "CONNECT visualisation, up to 5 users (bundled)", "(included) CONNECT visualisation services", "FLEX-CVS-001", 1, None, "Included", 7, "CONNECT - Flex subscription", 5, "Duplicate of p.6 row 5 and p.9 row 6 (all $0)."),
    (CON, "Enterprise data integration add-on (Databricks, Snowflake, Microsoft Fabric)", "CONNECT Add-On Enterprise Data Integration - Starter", "FLEX-CON-015", 1, 1008, "Priced", 7, "CONNECT - Flex subscription", 6, ""),
    (CON, "Flows add-on: 500 tags, unlimited AVEVA non-tag sources, 1 non-AVEVA source", "CONNECT Add-on flows OT and IT edition - Starter", "FLEX-FLOWS-012", 1, None, "Included", 7, "CONNECT - Flex subscription", 7, ""),
    (PA, "Predictive analytics, on-premise, up to 50 models", "AVEVA Predictive Analytics - On Premise - Medium / On Premises - 50 Models, requires premium support", "FLEX-PRED-002", 1, 5796, "Priced", 8, "Predictive Analytics - Flex subscription", 1, "'Requires premium support' - no premium support line is priced anywhere in the proposal."),
    (AMP, "Ampla server: unlimited client access, plus Test and Dev environments with same config", "AVEVA Production Management - Server", "FLEX-MES-096", 1, 12, "Priced", 9, "Production Management (Ampla) - Flex subscription", 1, ""),
    (AMP, "Ampla site licence: one geographical site (10 km circle), unlimited users", "AVEVA Production Management - Geographical Site", "FLEX-MES-075", 1, 996, "Priced", 9, "Production Management (Ampla) - Flex subscription", 2, "Restricted to one site."),
    (AMP, "Ampla license units for Delay Accounting (60 units x 50 credits)", "AVEVA Production Management - License Unit (minimum qty 100) - for Delay Accounting", "FLEX-MES-077", 60, 50, "Priced", 9, "Production Management (Ampla) - Flex subscription", 3, "Qty 60 is below the printed 'minimum qty 100' - see Flag 2."),
    (AMP, "Ampla license units for Inventory (100 units x 50 credits)", "AVEVA Production Management - License Unit (minimum qty 100) - for Inventory", "FLEX-MES-077", 100, 50, "Priced", 9, "Production Management (Ampla) - Flex subscription", 4, ""),
    (AMP, "CONNECT data services, up to 200 data streams (bundled)", "(included) CONNECT data services", "FLEX-ADH-001", 1, None, "Included", 9, "Production Management (Ampla) - Flex subscription", 5, "Duplicate of p.6 row 4 and p.7 row 4 (all $0)."),
    (AMP, "CONNECT visualisation, up to 5 users (bundled)", "(included) CONNECT visualisation services", "FLEX-CVS-001", 1, None, "Included", 9, "Production Management (Ampla) - Flex subscription", 6, "Duplicate of p.6 row 5 and p.7 row 5 (all $0)."),
]
r0 = 6
for i, (grp, plain, printed, code, qty, cpu, status, pg, slide, trow, note) in enumerate(SW):
    r = r0 + i
    sw.cell(r, 1, f"SW-{i+1:02d}")
    sw.cell(r, 2, f"AV-P{pg:02d}-R{trow:02d}")
    sw.cell(r, 3, grp); sw.cell(r, 4, plain); sw.cell(r, 5, printed); sw.cell(r, 6, code)
    sw.cell(r, 7, qty)
    if cpu is not None:
        sw.cell(r, 8, cpu)
        sw.cell(r, 9, f"=G{r}*H{r}")
        sw.cell(r, 10, f"=I{r}*$C$3")
    else:
        sw.cell(r, 9, 0); sw.cell(r, 10, 0)
    sw.cell(r, 11, status); sw.cell(r, 12, "Recurring - annual subscription")
    sw.cell(r, 13, link(pg)); sw.cell(r, 14, slide); sw.cell(r, 15, trow); sw.cell(r, 16, note)
    if "Duplicate" in note or "below" in note or "premium" in note:
        sw.cell(r, 16).fill = FLAG
SW_LAST = r0 + len(SW) - 1
tr = SW_LAST + 1
sw.cell(tr, 4, "TOTAL (derived)").font = Font(bold=True)
sw.cell(tr, 9, f"=SUM(I{r0}:I{SW_LAST})"); sw.cell(tr, 10, f"=SUM(J{r0}:J{SW_LAST})")
for c in range(1, 17):
    sw.cell(tr, c).fill = SUB; sw.cell(tr, c).font = Font(bold=True)
style_body(sw, r0, tr, 16, money=(10,), nums=(8, 9))
widths(sw, [8, 13, 22, 44, 48, 18, 6, 10, 11, 14, 14, 18, 10, 26, 7, 46])
sw.freeze_panes = "E6"

# --------------------------------------------------------------------------
# HARDWARE
# --------------------------------------------------------------------------
hw = wb.create_sheet("Hardware")
title(hw, "Hardware - none quoted by AVEVA",
      "The proposal contains NO hardware or hosting line. Rows HW-02 onward are infrastructure the quoted software implies; they are NOT priced and carry no cost here.")
header(hw, 4, ["Ref", "Source ID", "Item", "Evidence in proposal (why it is implied)", "Quoted AUD ex GST",
               "Status", "PDF page", "Slide", "Action / owner"])
HW = [
    ("Hardware lines in AVEVA pricing slides", "Licence tables (p.6-9) and Services table (p.10) contain only software credits and service fees.", 0, "None quoted", 6, "Budget estimate - Licences / Services", "Confirm with AVEVA that hardware is out of scope (customer-supplied)."),
    ("Production PI Server host (10,000 tags)", "'PI Server (10,000 tags)' licence; p.23 says PI Server 'on-premises'.", None, "Not priced", 6, "PIDI - Flex subscription", "MRL IT/OT to size and cost server or VM."),
    ("Test PI Server host", "'Test PI Server (10,000 tags)' licence included.", None, "Not priced", 6, "PIDI - Flex subscription", "MRL IT/OT to size and cost."),
    ("Production Management (Ampla) server(s): Production, Test and Development", "FLEX-MES-096 covers 'deployment of the same Production configuration for a Test and a Development environment'.", None, "Not priced", 9, "Production Management (Ampla) - Flex subscription", "Confirm VM count and database platform with AVEVA."),
    ("Predictive Analytics on-premise host (50 models)", "FLEX-PRED-002 is 'On Premises - 50 Models'.", None, "Not priced", 8, "Predictive Analytics - Flex subscription", "AVEVA to supply sizing for model hosting."),
    ("Edge / data-collector hosts at plant (adapters, Edge Data Store, OPC)", "FLEX-ADH-002 includes Edge Data Store and adapters; p.31 shows Data Collectors (OPC-DA/HDA) feeding Ampla.", None, "Not priced", 7, "CONNECT - Flex subscription", "Resolve against the Winu OT network and server design."),
]
for i, (item, ev, aud, status, pg, slide, act) in enumerate(HW):
    r = 5 + i
    hw.cell(r, 1, f"HW-{i+1:02d}"); hw.cell(r, 2, f"AV-P{pg:02d}-HW{i+1:02d}")
    hw.cell(r, 3, item); hw.cell(r, 4, ev)
    hw.cell(r, 5, aud if aud is not None else "Not priced")
    hw.cell(r, 6, status); hw.cell(r, 7, link(pg)); hw.cell(r, 8, slide); hw.cell(r, 9, act)
    if aud is None:
        hw.cell(r, 5).fill = FLAG
HW_LAST = 5 + len(HW) - 1
hw.cell(HW_LAST + 1, 3, "TOTAL QUOTED HARDWARE").font = Font(bold=True)
hw.cell(HW_LAST + 1, 5, f"=SUM(E5:E{HW_LAST})")
for c in range(1, 10):
    hw.cell(HW_LAST + 1, c).fill = SUB; hw.cell(HW_LAST + 1, c).font = Font(bold=True)
style_body(hw, 5, HW_LAST + 1, 9, money=(5,))
widths(hw, [8, 14, 44, 60, 16, 13, 10, 36, 44])
hw.freeze_panes = "D5"

# --------------------------------------------------------------------------
# EXTERNAL LABOUR
# --------------------------------------------------------------------------
lb = wb.create_sheet("External Labour")
title(lb, "External labour - AVEVA professional services (one-off, ex GST)",
      "Non-binding budgetary estimate +/-50% (PDF p.10). AVEVA gives one fee per service line; no days, roles or rates are provided.")
lb["A3"], lb["B3"], lb["C3"] = "Accuracy band", "+/- (PDF p.10)", 0.5
lb["C3"].fill, lb["C3"].number_format = INPUT, "0%"
header(lb, 5, ["Ref", "Source ID", "Service line (as printed)", "What it covers (plain English - interpretation)",
               "Supports software", "Quoted AUD ex GST", "% of services", "Low (-band)", "High (+band)",
               "Cost basis", "PDF page", "Slide / table", "Table row", "Notes"])
LB = [
    ("AVEVA Production Management - Delay Accounting", "Design, build, test and deploy Ampla delay and downtime accounting (processing downtime by cause and equipment, availability, utilisation).", "SW-17", 426122),
    ("AVEVA Production Management - Inventory Management", "Design, build, test and deploy Ampla inventory, material and metal accounting (stocks, quality, reconciliation). Largest single line.", "SW-18", 917973),
    ("AVEVA Predictive Analytics (50 Models) - Services", "Data prep, model build and operationalisation of up to 50 predictive / data-verification models.", "SW-14", 226435),
    ("AVEVA PI System - Install and Configuration Services", "Install and configure PI Server (production and test) and interfaces.", "SW-01 to SW-06", 83786),
    ("AVEVA PI AF Services", "Build the PI Asset Framework model (asset hierarchy and context) for the plant.", "SW-01 to SW-06", 164045),
    ("AVEVA Connect Core Services", "Set up CONNECT data services and visualisation, and the cloud connection.", "SW-07 to SW-13", 115612),
    ("AVEVA Overall Integration Services", "Integration across PIDI, CONNECT, Predictive Analytics and Ampla.", "All SW", 29877),
]
for i, (name, what, supports, aud) in enumerate(LB):
    r = 6 + i
    lb.cell(r, 1, f"LB-{i+1:02d}"); lb.cell(r, 2, f"AV-P10-R{i+1:02d}")
    lb.cell(r, 3, name); lb.cell(r, 4, what); lb.cell(r, 5, supports)
    lb.cell(r, 6, aud)
    lb.cell(r, 7, f"=F{r}/$F${6+len(LB)}")
    lb.cell(r, 8, f"=F{r}*(1-$C$3)"); lb.cell(r, 9, f"=F{r}*(1+$C$3)")
    lb.cell(r, 10, "One-off project fee")
    lb.cell(r, 11, link(10)); lb.cell(r, 12, "Budget Estimate - Services"); lb.cell(r, 13, i + 1)
    lb.cell(r, 14, "Scope description and software mapping are our reading of the line title; AVEVA does not itemise." if i == 0 else "")
LB_LAST = 6 + len(LB) - 1
t = LB_LAST + 1
lb.cell(t, 3, "TOTAL SERVICES (sum of lines)").font = Font(bold=True)
lb.cell(t, 6, f"=SUM(F6:F{LB_LAST})"); lb.cell(t, 7, f"=SUM(G6:G{LB_LAST})")
lb.cell(t, 8, f"=SUM(H6:H{LB_LAST})"); lb.cell(t, 9, f"=SUM(I6:I{LB_LAST})")
for c in range(1, 15):
    lb.cell(t, c).fill = SUB; lb.cell(t, c).font = Font(bold=True)
style_body(lb, 6, t, 14, money=(6, 8, 9))
for r in range(6, t + 1):
    lb.cell(r, 7).number_format = "0.0%"
lb.cell(t + 2, 3, "Scope stated to be included in the fees (PDF p.10, applies to all lines):").font = Font(bold=True)
lb.cell(t + 3, 3, "Design | Build | Test | Deploy, Training & Warranty | Cont & Governance (as printed) | Project Management")
lb.cell(t + 4, 3, "Basis (PDF p.10): 'Full-size resource to market operation'; sized on functional coverage and operation scale, not users. AVEVA offers full, partial or assisted services, or SI partners.")
widths(lb, [8, 12, 40, 54, 14, 16, 10, 14, 14, 18, 10, 24, 7, 40])
lb.freeze_panes = "D6"

# --------------------------------------------------------------------------
# RECONCILIATION & FLAGS
# --------------------------------------------------------------------------
rc = wb.create_sheet("Reconciliation & Flags")
title(rc, "Reconciliation to AVEVA printed totals, and flags",
      "Blue cells are values typed from the PDF. Everything else is a formula against the Software / External Labour sheets.")
header(rc, 4, ["Group", "Credits (sum of lines)", "Credits quoted", "Credit diff", "Derived AUD / yr",
               "Quoted AUD / yr (ex GST)", "AUD diff (quoted - derived)", "Check", "Source"])
GR = [(PIDI, 4200, 89208.00, 6), (CON, 3012, 73010.88, 7), (PA, 5796, 123107.04, 8), (AMP, 9008, 191329.92, 9)]
for i, (g, cq, aq, pg) in enumerate(GR):
    r = 5 + i
    rc.cell(r, 1, g)
    rc.cell(r, 2, f"=SUMIF(Software!$C${r0}:$C${SW_LAST},A{r},Software!$I${r0}:$I${SW_LAST})")
    rc.cell(r, 3, cq).fill = INPUT
    rc.cell(r, 4, f"=B{r}-C{r}")
    rc.cell(r, 5, f"=B{r}*Software!$C$3")
    rc.cell(r, 6, aq).fill = INPUT
    rc.cell(r, 7, f"=F{r}-E{r}")
    rc.cell(r, 8, f'=IF(ABS(G{r})<0.01,"OK","MISMATCH")')
    rc.cell(r, 9, link(pg))
rc.cell(9, 1, "TOTAL LICENCES")
for col in "BCDEFG":
    rc[f"{col}9"] = f"=SUM({col}5:{col}8)"
for c in range(1, 10):
    rc.cell(9, c).fill = SUB; rc.cell(9, c).font = Font(bold=True)
rc.cell(11, 1, "Services")
rc.cell(11, 2, "Sum of 7 lines"); rc.cell(11, 5, f"='External Labour'!F{t}")
rc.cell(11, 6, 1963850).fill = INPUT
rc.cell(11, 7, "=F11-E11"); rc.cell(11, 8, '=IF(ABS(G11)<0.01,"OK","MISMATCH")'); rc.cell(11, 9, link(10))
style_body(rc, 5, 11, 9, money=(5, 6, 7), nums=(2, 3, 4))

rc.cell(13, 1, "Flags and open questions").font = Font(bold=True, size=12, color=NAVY)
header(rc, 14, ["#", "Flag", "Impact (AUD ex GST)", "", "", "", "", "", "Source / suggested action"])
FL = [
    ("CONNECT total does not reconcile. 3,012 credits x 21.24 = 63,974.88, but AVEVA prints 73,010.88 (equal to ~3,437 credits). The 3,012 total does equal the sum of its lines (2,004 + 1,008).",
     "=G6", "PDF p.7. Ask AVEVA which is right. Headline uses the printed figure; the derived figure is shown as a sensitivity on Summary."),
    ("Ampla Delay Accounting license units are qty 60 but the line says 'minimum qty 100'. If the minimum applies per line, 40 more units are needed.",
     "=(100-60)*50*Software!C3", "PDF p.9. Potential extra per year, NOT included in totals. Confirm whether the minimum applies per line or across both lines (60+100=160)."),
    ("Predictive Analytics 'requires premium support' but no support line is priced.",
     "Not priced", "PDF p.8. Ask AVEVA for premium support cost."),
    ("Licences are annual Flex subscriptions (recurring); services are one-off. No subscription term, escalation or multi-year pricing is given, so totals are Year-1 only.",
     "Recurring", "PDF p.6-9. Model term and uplift separately."),
    ("The Flex rate is labelled 'Top-Up Rate'. A pre-purchased credit pack may carry a lower rate; the credit counts are fixed but the AUD may fall.",
     "Rate risk", "PDF p.6-9. Confirm commercial credit rate."),
    ("Services are +/-50% and non-binding, with no breakdown by phase, role, days or rate. Labour cannot be split further from this document.",
     "=-'External Labour'!H"+str(t)+"+'External Labour'!F"+str(t)+"", "PDF p.10. Impact shown is the downside/upside magnitude (+/-). Request a services breakdown by role and days."),
    ("No hardware, hosting, SQL/database licences, networking or MRL-side labour are priced. On-premise PI, Ampla and Predictive Analytics need host infrastructure.",
     "Not priced", "See Hardware sheet. Costed by MRL IT/OT."),
    ("Sizing basis is uncertain: the flowsheet gave no detail on single vs parallel trains (PDF p.3). Tag counts, models and units may change with the Winu design.",
     "Scope risk", "PDF p.3. Re-baseline once the Winu process design is fixed."),
    ("The PDF text layer scrambles the licence and services tables (p.6-10). Figures here were read from the rendered slides and checked arithmetically against AVEVA's printed totals.",
     "n/a", "Method note."),
]
for i, (flag, impact, act) in enumerate(FL):
    r = 15 + i
    rc.cell(r, 1, i + 1); rc.cell(r, 2, flag); rc.cell(r, 3, impact); rc.cell(r, 9, act)
    rc.merge_cells(start_row=r, start_column=3, end_row=r, end_column=8)
    rc.cell(r, 3).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    rc.cell(r, 3).number_format = MONEY
    rc.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
    rc.cell(r, 9).alignment = Alignment(wrap_text=True, vertical="top")
    rc.row_dimensions[r].height = 62
widths(rc, [30, 62, 16, 12, 16, 22, 22, 12, 60])

# --------------------------------------------------------------------------
# SOURCE INDEX
# --------------------------------------------------------------------------
si = wb.create_sheet("Source Index")
title(si, "Source index - Aveva Proposal MRL Greenfield Site.pdf (36 slides)",
      "Slides carry no page numbers; 'PDF p.' is the position in the file. Source ID format: AV-P<page>-R<table row>.")
header(si, 4, ["PDF page", "Slide title", "Content", "Used in"])
SI = [
    (1, "Cover", "Aveva Solution Budget Estimate for MRL Greenfield Site, Oct 2026", "Context"),
    (3, "MRL Business Requirement", "Flowsheet basis: typical Cu/Au concentrator, key process areas; no detail on single vs parallel trains", "Flag 8"),
    (4, "Key Business Objectives", "Delay accounting, metal accounting, inventory tracking, mine-to-port dashboards", "Context"),
    (5, "Aveva Solution Proposed", "Four offers: PIDI, CONNECT, Advanced Analytics, Ampla", "Context"),
    (6, "Budget Estimate - Licenses: PIDI", "6 lines; 4,200 credits; AUD 89,208 ex GST / yr", "Software SW-01 to SW-06"),
    (7, "Budget Estimate - Licenses: CONNECT", "7 lines; 3,012 credits; AUD 73,010.88 ex GST / yr", "Software SW-07 to SW-13"),
    (8, "Budget Estimate - Licenses: Predictive Analytics", "1 line; 5,796 credits; AUD 123,107.04 ex GST / yr", "Software SW-14"),
    (9, "Budget Estimate - Licenses: Production Management (Ampla)", "6 lines; 9,008 credits; AUD 191,329.92 ex GST / yr", "Software SW-15 to SW-20"),
    (10, "Budget Estimate - Services", "7 lines; AUD 1,963,850 ex GST; +/-50% non-binding", "External Labour LB-01 to LB-07"),
    (11, "Aveva Solution Information", "Section divider. Pages 12-31 are product collateral with no pricing", "Not used for costs"),
    (31, "AVEVA Production Management", "Architecture: data collectors (OPC), SCADA, LIMS, ERP integrations", "Hardware HW-06 (evidence)"),
    (23, "Integration with CONNECT data services", "PI Server on-premises, Edge Data Store", "Hardware HW-02 (evidence)"),
]
for i, row in enumerate(SI):
    r = 5 + i
    si.cell(r, 1, link(row[0]))
    for c in range(1, 4):
        si.cell(r, c + 1, row[c])
style_body(si, 5, 4 + len(SI), 4)
widths(si, [12, 52, 80, 34])

# --------------------------------------------------------------------------
# SUMMARY (placed first)
# --------------------------------------------------------------------------
sm = wb.create_sheet("Summary", 0)
title(sm, "AVEVA budget estimate - MRL Greenfield site (Winu): Software / Hardware / External Labour",
      "Source: Aveva Proposal MRL Greenfield Site.pdf (Oct 2026). All values AUD ex GST. Budgetary and non-binding. Year-1 view.")
header(sm, 4, ["Category", "Nature", "Quoted AUD ex GST", "% of total", "Detail sheet", "Source"])
sm["A5"], sm["B5"], sm["C5"] = "Software", "Annual subscription (recurring)", "='Reconciliation & Flags'!F9"
sm["E5"], sm["F5"] = "Software", link(6) + ""
sm["A6"], sm["B6"], sm["C6"] = "Hardware", "None quoted by AVEVA", f"=Hardware!E{HW_LAST+1}"
sm["E6"], sm["F6"] = "Hardware", link(6)
sm["A7"], sm["B7"], sm["C7"] = "External labour", "One-off AVEVA services", f"='External Labour'!F{t}"
sm["E7"], sm["F7"] = "External Labour", link(10)
sm["A8"], sm["C8"] = "TOTAL YEAR 1", "=SUM(C5:C7)"
for r in (5, 6, 7, 8):
    sm[f"D{r}"] = f"=C{r}/$C$8"
    sm[f"D{r}"].number_format = "0.0%"
for c in range(1, 7):
    sm.cell(8, c).fill = SUB; sm.cell(8, c).font = Font(bold=True)
style_body(sm, 5, 8, 6, money=(3,))
for r in range(5, 9):
    sm[f"D{r}"].number_format = "0.0%"

sm["A10"] = "Sensitivities"; sm["A10"].font = Font(bold=True, size=12, color=NAVY)
header(sm, 11, ["Case", "Basis", "AUD ex GST", "", "", ""])
SENS = [
    ("Software if CONNECT is the derived value", "Flag 1: 3,012 credits x rate instead of printed 73,010.88", "=C5-'Reconciliation & Flags'!G6"),
    ("External labour low", "-50% band (PDF p.10)", f"='External Labour'!H{t}"),
    ("External labour high", "+50% band (PDF p.10)", f"='External Labour'!I{t}"),
    ("Total Year 1 - low", "Software at derived CONNECT + labour low", "=C12+C13+C6"),
    ("Total Year 1 - high", "Software as printed + labour high", "=C5+C14+C6"),
    ("Not in totals: extra Delay Accounting units", "Flag 2: if minimum qty 100 applies", "='Reconciliation & Flags'!C16"),
]
for i, (a, b, f) in enumerate(SENS):
    r = 12 + i
    sm.cell(r, 1, a); sm.cell(r, 2, b); sm.cell(r, 3, f)
style_body(sm, 12, 12 + len(SENS) - 1, 6, money=(3,))

sm["A19"] = "Software by group (annual)"; sm["A19"].font = Font(bold=True, size=12, color=NAVY)
header(sm, 20, ["Group", "Credits / yr", "Quoted AUD / yr", "% of software", "Source", ""])
for i, (g, _, _, pg) in enumerate(GR):
    r = 21 + i
    sm.cell(r, 1, g)
    sm.cell(r, 2, f"='Reconciliation & Flags'!B{5+i}")
    sm.cell(r, 3, f"='Reconciliation & Flags'!F{5+i}")
    sm.cell(r, 4, f"=C{r}/$C$25")
    sm.cell(r, 5, link(pg))
sm.cell(25, 1, "Total"); sm.cell(25, 2, "=SUM(B21:B24)"); sm.cell(25, 3, "=SUM(C21:C24)"); sm.cell(25, 4, "=SUM(D21:D24)")
for c in range(1, 7):
    sm.cell(25, c).fill = SUB; sm.cell(25, c).font = Font(bold=True)
style_body(sm, 21, 25, 6, money=(3,), nums=(2,))
for r in range(21, 26):
    sm[f"D{r}"].number_format = "0.0%"

sm["A27"] = "External labour by service line (one-off)"; sm["A27"].font = Font(bold=True, size=12, color=NAVY)
header(sm, 28, ["Service line", "Ref", "Quoted AUD", "% of services", "Source", ""])
for i in range(len(LB)):
    r = 29 + i
    sm.cell(r, 1, f"='External Labour'!C{6+i}")
    sm.cell(r, 2, f"='External Labour'!A{6+i}")
    sm.cell(r, 3, f"='External Labour'!F{6+i}")
    sm.cell(r, 4, f"='External Labour'!G{6+i}")
    sm.cell(r, 5, link(10))
sm.cell(36, 1, "Total"); sm.cell(36, 3, "=SUM(C29:C35)"); sm.cell(36, 4, "=SUM(D29:D35)")
for c in range(1, 7):
    sm.cell(36, c).fill = SUB; sm.cell(36, c).font = Font(bold=True)
style_body(sm, 29, 36, 6, money=(3,))
for r in range(29, 37):
    sm[f"D{r}"].number_format = "0.0%"

sm["A38"] = "Check status"; sm["A38"].font = Font(bold=True)
sm["B38"] = ("=IF(AND('Reconciliation & Flags'!H5=\"OK\",'Reconciliation & Flags'!H6=\"OK\","
             "'Reconciliation & Flags'!H7=\"OK\",'Reconciliation & Flags'!H8=\"OK\",'Reconciliation & Flags'!H11=\"OK\"),"
             "\"All AVEVA totals reconcile\",\"CHECK Reconciliation & Flags sheet: a printed total does not reconcile\")")
sm["B38"].font = Font(bold=True, color="C00000")
widths(sm, [44, 52, 20, 14, 16, 12])

OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print("saved", OUT)
