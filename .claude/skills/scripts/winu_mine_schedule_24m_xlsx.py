#!/usr/bin/env python3
"""Build the Winu first-24-months mine schedule, earthworks plan and equipment list (Excel).

Source basis: output/Winu/WIN-CON-EPC-001_Mining_Review.html (ITT review). Shared engineering
assumptions (densities, haul speeds, truck / excavator / drill parameters, support ratios) are read
from the winu-prestrip-fleet config so the two workbooks stay consistent; everything specific to the
24-month schedule is defined in this file. The workbook is formula-driven: change a yellow cell on
Inputs, the monthly ramp / volume override on Schedule, the Override column on Fleet_Register or the
Start / Duration cells on Earthworks and everything recalculates in Excel.

Run: python -I winu_mine_schedule_24m_xlsx.py --output <xlsx> [--force]
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as CL

N = 24  # months in the schedule: M1 = Dec 2027 ... M24 = Nov 2029
BASE_CFG = Path(__file__).resolve().parents[1] / "winu-prestrip-fleet" / "config" / "winu_prestrip_fleet.json"

HEAD = PatternFill("solid", fgColor="1F3864")
SUB = PatternFill("solid", fgColor="D9E1F2")
INP = PatternFill("solid", fgColor="FFF2CC")
OUTF = PatternFill("solid", fgColor="E2EFDA")
GREY = PatternFill("solid", fgColor="F2F2F2")
BAR = PatternFill("solid", fgColor="2F75B5")
BAR2 = PatternFill("solid", fgColor="ED7D31")
WHITE = Font(bold=True, color="FFFFFF")
BOLD = Font(bold=True)
BLUE = Font(color="0000FF")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
A_ = "ASSUMPTION"


def hdr(ws, row, labels, col=1, height=None):
    for i, t in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=t)
        c.font, c.fill, c.border = WHITE, HEAD, BOX
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    if height:
        ws.row_dimensions[row].height = height


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = Font(bold=True, size=14)
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(italic=True, color="595959")


def band(ws, row, text, ncols):
    for col in range(1, ncols + 1):
        ws.cell(row=row, column=col).fill = SUB
    ws.cell(row=row, column=1, value=text).font = BOLD


# --------------------------------------------------------------------------- inputs
DROP_BASE = {"days_per_year", "dur_months", "mob_months", "demob_months", "ramp_months", "ramp_eff",
             "start_date"}
DROP_PREFIX = ("mix_",)
D65_NOTE = " | Applied to the Epiroc D65 (client-specified). Confirm hole diameter, single-pass depth and net penetration with Epiroc / a site trial"
D65_KEYS = {"area_c2", "area_c3", "area_c4", "pen_c2", "pen_c3", "pen_c4", "drill_move_eff", "drill_avail",
            "drill_util", "min_drills"}

EXTRA = [
    # section, key, label, value, unit, basis
    ("Programme", "start_date", "Month 1 of the schedule", "2027-12-01", "date",
     "Site Access Date 23/11/2027 (Agreement Schedule Item 12, p054). The SOW says site start January 2027 and Commencement is end Q1 2027 (R-07), but no work front is assumed before Site Access (p214)"),
    ("Programme", "site_access_date", "Site Access Date", "2027-11-23", "date", "Agreement Schedule Item 12, p054"),
    ("Programme", "last_prod_month", "Last month with pre-strip production", 22, "month #",
     A_ + ". Leaves M23-M24 for final clean-up, rehabilitation and demobilisation (SOW s6.2.2) inside the 30/11/2029 Completion date. The ITT states no pre-strip duration (R-24)"),
    ("Programme", "full_rate", "Full production rate (100% ramp, 30-day month)", 1200000, "bcm/month",
     A_ + ". Sized so 21.6 Mbcm completes by the last production month after ramp-up and weather. This is a consequence of the fixed completion date, not an ITT figure"),
    ("Programme", "ore_tot", "Ore to stockpile in pre-strip", 600000, "t", "ITT s6.2.13 p254: first ~600 kt of ore to designated stockpiles"),
    ("Programme", "ore_start_frac", "Ore harvested after this fraction of the mudstone / leach cap layer", 0.4, "fraction",
     A_ + ". The ITT does not say where the ore sits in the column. Assumed in the lower mudstone / leach cap interval so stockpile bases are ready first"),
    ("Destinations and fill", "tsf_tot", "Pre-strip material placed in TSF Stage 0", 6000000, "bcm",
     "Limited by suitable material: ITT s6.2.11 sources TSF fill from aeolian sand and Permian regolith in the upper ~15-20 m, about 6.2 Mbcm of the column. TSF Yearly Development (C0007-2300-G-PRE-00002) lists 8.42 Mm3 for Years 2-3, so about 2.4 Mm3 must come from other sources or later pre-strip. Replace from the Prestrip MTO (C0007-REF-00325)"),
    ("Destinations and fill", "tsf_doc_stage0", "TSF Stage 0 fill per TSF Yearly Development (information)", 8420407, "m3",
     "C0007-2300-G-PRE-00002 Rev A pp5-6: Year 2 7,239,540 m3 + Year 3 1,180,867 m3 (paddock-dumped, divider embankment and bulk fill zones)"),
    ("Destinations and fill", "infra_cap", "Max share of sand + cemented rock sent to infrastructure in any month", 0.35, "fraction",
     A_ + ". Infrastructure is built first (priority 1 haul roads, 2 ROM pad, 3 ponds / bunds, 4 stockpile bases) so the ROM pad is ready ahead of Milestone 3 (25/10/2028)"),
    ("Destinations and fill", "tsf_cap", "Max share of sand + cemented rock sent to TSF in any month", 0.50, "fraction",
     A_ + ". TSF Zone 4A / 2B placement is limited by paddock layer thickness and compaction (ITT s6.2.11)"),
    ("Destinations and fill", "hr_width", "Haul road formation width (running + shoulders + berms + drains)", 40, "m",
     "ITT s6.2.10: running width 3.5 x operating width of the XDE260-class truck plus shoulders, safety berms and batters. " + A_ + " for the total"),
    ("Destinations and fill", "hr_thick", "Haul road average placed thickness", 1.0, "m", A_ + ". Wearing course over cemented sand / sandstone base (ITT s6.2.10)"),
    ("Destinations and fill", "rom_fill", "ROM bulk fill, crusher skyway and stockpile fingers", 1000000, "bcm",
     A_ + ". ITT s6.2.9 gives layers up to 5 m but no volume. Replace from the Pre-strip MTO / Stockpiles and ROM Pad DXF (C0007-REF-00343)"),
    ("Destinations and fill", "misc_fill", "Pond embankments, clean-water bunds, diversion drains, laydown and magazine pads", 300000, "bcm",
     A_ + ". ITT s6.1.2 WA4 and s6.2.14 (surface water diversion, Mine Stockpile Detention Ponds 1 and 2, Mine Dewatering Pond)"),
    ("Destinations and fill", "sp_area_ha", "Stockpile base area (primary sulphide, low grade, leach cap)", 35, "ha",
     A_ + ". ITT WA4 p234-235 lists the stockpiles but gives no areas"),
    ("Destinations and fill", "sp_gran_thk", "Stockpile base granular fill thickness", 1.0, "m", A_),
    ("Destinations and fill", "clay_share", "Share of stockpile base area with clayey mudstone liner", 0.6, "fraction", A_ + ". ITT s6.2.12: liner to selected stockpile bases"),
    ("Destinations and fill", "clay_thk", "Clayey mudstone liner thickness", 2.0, "m", "ITT s6.2.12 p254: 2 m total thickness in nominal 1 m layers"),
    ("Destinations and fill", "borrow_vol", "Borrow pit for initial haul road and hardstand material", 200000, "bcm",
     A_ + ". Extra to the 21.6 Mbcm. The pit has not yet reached cemented sand / sandstone in the first months. Borrow Pit Management Plan C0007-0800-C-PLN-00001 not supplied"),
    ("Destinations and fill", "wrl_swell", "Waste rock landform bulking after placement", 1.25, "x", A_),
    ("Destinations and fill", "wrl_height", "Average waste rock landform height", 25, "m", A_ + ". Sets the WRL footprint to clear"),
    ("Disturbance and early works", "pit_ha", "Pit cutbacks 1 and 2 footprint", 60, "ha", A_ + ". Disturbance Footprint 20260429 (C0007-REF-00323) not supplied"),
    ("Disturbance and early works", "corr_width", "Haul road corridor clearing width", 50, "m", A_),
    ("Disturbance and early works", "rom_ha", "ROM pad and crusher skyway footprint", 12, "ha", A_),
    ("Disturbance and early works", "tsf_ha", "TSF Stage 0 footprint (dune foundation)", 40, "ha", A_ + ". Dune disturbance limited to 1 m depth with Traditional Owner monitors (p258)"),
    ("Disturbance and early works", "support_ha", "Contractor facilities, magazine, workshop, laydown", 12, "ha", A_ + ". ITT s5.5 / s5.6 Contractor laydown, workshop and temporary magazine"),
    ("Disturbance and early works", "itt_footprint_ha", "ITT stated disturbance footprint (information only)", 170, "ha", "ITT s2.3 p210: disturbance footprint ~170 ha"),
    ("Disturbance and early works", "topsoil_gen", "Topsoil recovery depth - general", 0.1, "m", "ITT s6.1.4 p240: 100 mm. Pit and WRL depth was garbled in extraction, 100 mm assumed"),
    ("Disturbance and early works", "topsoil_tsf", "Topsoil recovery depth - TSF", 0.2, "m", "ITT s6.1.4 p240: 200 mm"),
    ("Disturbance and early works", "clear_prod", "Clear, grub and strip topsoil, per dozer", 0.2, "ha/op-h", A_ + ". Combined clear / grub / topsoil push and stockpile in sand and spinifex country"),
    ("Disturbance and early works", "borrow_ex_prod", "Borrow pit excavator productivity (90 t class)", 700, "bcm/op-h", A_),
    ("Disturbance and early works", "borrow_trk_prod", "Borrow haul truck productivity (90-100 t class)", 180, "bcm/op-h", A_ + ". About 3 km lead"),
    ("Disturbance and early works", "grout_prod", "TSF borehole backfill rate per grout plant", 0.04, "holes/op-h", A_ + ". About one 66-304 m borehole per day (24 boreholes, p257)"),
    ("Disturbance and early works", "ew_util", "Utilisation of available hours - early works fleet", 0.75, "fraction", A_),
    ("Disturbance and early works", "rehab_ha", "Temporary area to rehabilitate at demobilisation", 12, "ha", A_ + ". ITT s6.2.2: rehabilitation and demobilisation in pre-strip scope"),
    ("Disturbance and early works", "impact_roller", "Impact roller (TSF dune compaction)", 1, "units", "ITT s6.3.3 p258: high-energy impact roller on loose dune zones"),
    ("Disturbance and early works", "backhoe", "Backhoe excavator (batter raking)", 1, "units", "ITT s6.2.6 p246"),
    ("Disturbance and early works", "crush_plant", "Mobile crushing and screening plant (pavement, stemming)", 1, "units", "ITT s6.2.4 and s6.2.10: crushed aggregate stemming and pavement material"),
    ("Disturbance and early works", "liner_sets", "HDPE liner deployment and welding sets", 2, "units", "ITT WA4: HDPE-lined stockpile bases and detention ponds. " + A_),
    ("Drill and blast (Epiroc D65)", "det_per_hole", "Electronic detonators per hole", 1, "per hole", "ITT s6.2.4: digital / electronic detonators for all blasting"),
    ("Drill and blast (Epiroc D65)", "d65_hole_dia", "Hole diameter assumed for the D65", 200, "mm", A_ + ". Information only. Pattern areas below are consistent with a 165-200 mm hole"),
    ("Drill and blast (Epiroc D65)", "blast_monitors", "Blast vibration / airblast monitors", 4, "units", "ITT s6.2.4: Contractor responsible for vibration, airblast, flyrock. " + A_),
    ("Drill and blast (Epiroc D65)", "expl_trucks", "Explosives delivery trucks (magazine to pit)", 1, "units", A_),
    ("Dewatering", "pump_base", "Sump pumps while above the water table", 2, "units", A_ + ". Stormwater and sump pumping from first excavation. WINU0076 and other existing dewatering bores inside Cutback 1 are decommissioned in Year 1 (HG-032 Table 9-6)"),
    ("Dewatering", "pipe_km", "Relocatable HDPE dewatering pipework", 4, "km", A_ + ". Transfer to the Mine Dewatering Pond (ITT s6.2.14)"),
    ("Fuel and facilities", "fuel_idle", "Burn factor in months without production", 0.2, "fraction", A_),
    ("Fuel and facilities", "fuel_days", "Temporary fuel farm storage", 7, "days of peak use", A_ + ". Company supplies diesel into Contractor bulk tanks (ITT s5.4); storage and dispensing are Contractor scope"),
    ("Fuel and facilities", "bays_per", "Heavy units per temporary workshop bay", 5, "units", A_ + ". Permanent MSA HME workshop concrete is Milestone 8, 08/01/2029 (p055)"),
]


OVERRIDE = {
    "d_tsf": (4.9, "Technical Info C0007-2300-G-PRE-00002 (Yearly TSF Development, Rev A 31/07/2026): Stage 0 fill centroids average ~0.9 km beyond the reference axis at the WRL boundary (volume-weighted Years 2-3). Pit to WRL boundary 4.0 km (" + A_ + ") + 0.9 km"),
    "min_faces": (3, "Three concurrent dig faces: TSF / infrastructure fill, waste rock landform and a third face for ore, stand-by or wet-weather flexibility. " + A_),
}
APPEND = {
    "depth_sand": " | CONFLICT with geotechnical boreholes (C0007-0300-C-REP-00011 Table 9): aeolian sand 18-32 m, mean ~27 m. ITT value kept as the contract basis; set 27 to test (more free-dig, less drilling)",
    "pumps": " | Hydrogeology (311012-01475-REP-HG-032): sandstone / mudstone inflow 'negligible'; bore dewatering by others 125-160 L/s in Years 1-3. Sump pumps cover stormwater and seepage",
    "bench_h": " | Confirmed by Golder 19135779-017: 10 m benches in sand / sandstone / mudstone (20 m in metasediment, below pre-strip)",
}


def load_inputs():
    base = json.loads(BASE_CFG.read_text(encoding="utf-8"))["inputs"]
    keep = []
    for s, k, lab, val, unit, basis in base:
        if k in DROP_BASE or k.startswith(DROP_PREFIX):
            continue
        if k in OVERRIDE and OVERRIDE[k]:
            val, basis = OVERRIDE[k]
        if k in APPEND:
            basis += APPEND[k]
        if k in D65_KEYS:
            basis += D65_NOTE
        keep.append([s, k, lab, val, unit, basis])
    order = ["Programme", "Destinations and fill", "Disturbance and early works", "Weather lost days", "Geology", "Haul",
             "Rear dump trucks", "Large excavators", "Wheel loaders", "Drill and blast", "Drill and blast (Epiroc D65)",
             "Road, dump and support", "Dewatering", "Ancillary and people", "Fuel and facilities"]
    allin = [list(x) for x in EXTRA] + keep
    allin.sort(key=lambda r: order.index(r[0]) if r[0] in order else 99)  # stable: EXTRA before base in a section
    return allin


def build(out):
    wb = Workbook()
    inputs = load_inputs()
    # ------------------------------------------------------------------ Inputs sheet
    wi = wb.active
    wi.title = "Inputs"
    title(wi, "Inputs and assumptions - Winu first 24 months",
          "Yellow cells are inputs. ASSUMPTION marks a figure the ITT does not give (see Assumptions_Log). Everything on the other sheets is a formula.")
    hdr(wi, 4, ["Key", "Parameter", "Value", "Unit", "Basis / source"])
    IA = {}
    weather_rows = []
    r, sect = 5, None
    for s, key, label, val, unit, basis in inputs:
        if s != sect:
            band(wi, r, s, 5)
            r += 1
            sect = s
        wi.cell(row=r, column=1, value=key)
        wi.cell(row=r, column=2, value=label)
        if unit == "date":
            val = dt.datetime.strptime(val, "%Y-%m-%d")
        c = wi.cell(row=r, column=3, value=val)
        c.fill, c.font, c.border = INP, BLUE, BOX
        if unit == "date":
            c.number_format = "dd-mmm-yyyy"
        elif unit == "fraction":
            c.number_format = "0.00"
        elif isinstance(val, (int, float)) and abs(val) >= 1000:
            c.number_format = "#,##0"
        wi.cell(row=r, column=4, value=unit)
        wi.cell(row=r, column=5, value=basis).alignment = WRAP
        IA[key] = f"Inputs!$C${r}"
        if key.startswith("w_m"):
            weather_rows.append(r)
        r += 1
    for col, w in zip("ABCDE", (20, 62, 16, 16, 120)):
        wi.column_dimensions[col].width = w
    wi.freeze_panes = "A5"
    WREF = f"Inputs!$C${weather_rows[0]}:$C${weather_rows[-1]}"

    def I(k):
        return IA[k]

    # ------------------------------------------------------------------ Quantities
    wq = wb.create_sheet("Quantities")
    title(wq, "Quantities - material layers, destinations, fill demand and disturbance",
          "Derived from Inputs. These totals are the targets the monthly Schedule must deliver (see Checks).")
    hdr(wq, 4, ["Item", "Value", "Unit", "Basis"])
    QA = {}
    qrow = [5]

    def qsec(text):
        band(wq, qrow[0], text, 4)
        qrow[0] += 1

    def q(key, label, formula, unit, basis="", fmt="#,##0"):
        rr = qrow[0]
        wq.cell(row=rr, column=1, value=label)
        c = wq.cell(row=rr, column=2, value=formula if str(formula).startswith("=") else formula)
        c.number_format = fmt
        c.fill = OUTF
        wq.cell(row=rr, column=3, value=unit)
        wq.cell(row=rr, column=4, value=basis).alignment = WRAP
        QA[key] = f"Quantities!$B${rr}"
        qrow[0] += 1

    def Q(k):
        return QA[k]

    qsec("1. Pre-strip layers (ITT s6.2.5 stratigraphy)")
    q("vol_A", "Layer A - aeolian sands 0-15 m", f"={I('vol_total')}*{I('depth_sand')}/{I('depth_total')}", "bcm", "Volume split by thickness, as in winu-prestrip-fleet")
    q("vol_B", "Layer B - cemented sands / sandstone / regolith 15-50 m", f"={I('vol_total')}*({I('depth_mid')}-{I('depth_sand')})/{I('depth_total')}", "bcm")
    q("vol_C", "Layer C - mudstone / leach cap 50-70 m", f"={I('vol_total')}*({I('depth_total')}-{I('depth_mid')})/{I('depth_total')}", "bcm")
    q("vol_Afd", "  of which free-dig sand (no blasting)", f"={Q('vol_A')}*{I('freedig')}", "bcm", "ITT s6.2.4: ~80% of sand is free-dig")
    q("vol_blast", "Volume requiring drill and blast", f"={Q('vol_A')}-{Q('vol_Afd')}+{Q('vol_B')}+{Q('vol_C')}", "bcm", "20% of sand plus all underlying material")
    q("blast_pct", "  Share of pre-strip that is blasted", f"={Q('vol_blast')}/{I('vol_total')}", "fraction", "", "0.0%")
    q("tonnes", "Total pre-strip tonnes", f"={Q('vol_A')}*{I('dens_sand')}+{Q('vol_B')}*{I('dens_mid')}+{Q('vol_C')}*{I('dens_mud')}", "t")
    q("ore_bcm", "Ore volume", f"={I('ore_tot')}/{I('dens_mud')}", "bcm", "Ore assumed at mudstone density")
    qsec("2. Infrastructure fill demand (placed direct from the pit, ITT s6.2.1)")
    q("hr_vol", "Haul roads - 17 km long-term", f"={I('maint_km_perm')}*1000*{I('hr_width')}*{I('hr_thick')}", "bcm", "ITT s6.2.10: ~17 km of long-term haul roads")
    q("rom", "ROM pad, crusher skyway and stockpile fingers", f"={I('rom_fill')}", "bcm", "ITT s6.2.9")
    q("misc", "Ponds, bunds, drains, magazine and laydown pads", f"={I('misc_fill')}", "bcm")
    q("sp_gran", "Stockpile bases - granular fill", f"={I('sp_area_ha')}*10000*{I('sp_gran_thk')}", "bcm")
    q("clay", "Stockpile bases - clayey mudstone liner (layer C)", f"={I('sp_area_ha')}*{I('clay_share')}*10000*{I('clay_thk')}", "bcm", "ITT s6.2.12")
    q("infra_dem", "Total infrastructure fill demand", f"={Q('hr_vol')}+{Q('rom')}+{Q('misc')}+{Q('sp_gran')}+{Q('clay')}", "bcm")
    q("borrow", "  less: supplied from borrow pit (not part of the 21.6 Mbcm)", f"={I('borrow_vol')}", "bcm")
    q("infra_pit", "Infrastructure fill sourced from the pre-strip", f"={Q('infra_dem')}-{Q('borrow')}", "bcm")
    q("infra_AB", "  of which from layers A + B (sand, cemented rock)", f"={Q('infra_pit')}-{Q('clay')}", "bcm")
    q("roads_pit", "  Haul road fill from the pit", f"={Q('hr_vol')}-{Q('borrow')}", "bcm", "Haul roads less borrow pit supply")
    qsec("3. Destinations of the 21.6 Mbcm")
    q("d_infra", "Infrastructure (roads, ROM, bunds, stockpile bases)", f"={Q('infra_pit')}", "bcm")
    q("d_tsf", "TSF Stage 0", f"={I('tsf_tot')}", "bcm")
    q("d_wrl", "Waste rock landform (balance)", f"={I('vol_total')}-{Q('d_infra')}-{Q('d_tsf')}", "bcm", "Balancing figure so destinations sum to the pre-strip volume")
    q("tsf_cap_ok", "TSF capacity from layers A + B at the monthly cap", f"=({Q('vol_A')}+{Q('vol_B')})*{I('tsf_cap')}", "bcm", "Must exceed TSF Stage 0 placement")
    q("tsf_gap", "TSF Stage 0 fill per TSF Yearly Development not covered by pre-strip", f"=MAX(0,{I('tsf_doc_stage0')}-{I('tsf_tot')})", "m3", "Must be sourced from borrow, processed sand or later pre-strip. Information only")
    q("wrl_loose", "WRL loose volume", f"={Q('d_wrl')}*{I('wrl_swell')}", "lcm")
    qsec("4. Disturbance to clear (hectares)")
    q("ha_pit", "Pit cutbacks 1-2", f"={I('pit_ha')}", "ha")
    q("ha_wrl", "Waste rock landform (volume / height)", f"={Q('wrl_loose')}/{I('wrl_height')}/10000", "ha")
    q("ha_road", "Haul road corridors", f"={I('maint_km_perm')}*1000*{I('corr_width')}/10000", "ha")
    q("ha_rom", "ROM pad and stockpile footprints", f"={I('rom_ha')}+{I('sp_area_ha')}", "ha")
    q("ha_tsf", "TSF Stage 0 footprint", f"={I('tsf_ha')}", "ha")
    q("ha_sup", "Contractor facilities and laydown", f"={I('support_ha')}", "ha")
    q("ha_tot", "Total area to clear", f"=SUM({QA['ha_pit'].split('!')[1]}:{QA['ha_sup'].split('!')[1]})", "ha", "Compare with the ITT ~170 ha disturbance footprint (p210). The WRL footprint drives the difference")
    q("ha_vs_itt", "  Ratio to ITT ~170 ha", f"={Q('ha_tot')}/{I('itt_footprint_ha')}", "x", "", "0.00")
    for col, w in zip("ABCD", (62, 18, 12, 90)):
        wq.column_dimensions[col].width = w
    wq.freeze_panes = "A5"

    # ------------------------------------------------------------------ Productivity
    wp = wb.create_sheet("Productivity")
    title(wp, "Productivity constants", "Static cycle and productivity figures used by Schedule. Month-specific truck cycles are calculated on Schedule.")
    hdr(wp, 4, ["Item", "Value", "Unit", "Basis"])
    PA = {}
    prow = [5]

    def p(key, label, formula, unit, basis="", fmt="#,##0.0"):
        rr = prow[0]
        wp.cell(row=rr, column=1, value=label)
        c = wp.cell(row=rr, column=2, value=formula)
        c.number_format, c.fill = fmt, OUTF
        wp.cell(row=rr, column=3, value=unit)
        wp.cell(row=rr, column=4, value=basis).alignment = WRAP
        PA[key] = f"Productivity!$B${rr}"
        prow[0] += 1

    band(wp, prow[0], "TSF stockpile re-handle (Zone 2B / processed sand stockpiled then reclaimed, ITT s6.2.11)", 4)
    prow[0] += 1
    p("rh_payload", "Re-handle truck payload", f"=MIN({I('truck_payload')}/{I('dens_sand')},{I('truck_body_m3')}/{I('swell_sand')})", "bcm", "Lesser of weight and body volume limits")
    p("rh_passes", "Wheel loader passes per truck", f"=MAX(1,ROUND({PA['rh_payload']}*{I('swell_sand')}/({I('wl_bucket')}*{I('wl_fill')}),0))", "passes", "", "0")
    p("rh_cycle", "Re-handle truck cycle", f"={PA['rh_passes']}*{I('wl_cycle_s')}/60+{I('t_spot')}+{I('lead_rehandle')}*(60/{I('v_loaded')}+60/{I('v_empty')})+{I('t_dump')}+{I('t_queue')}", "min")
    p("rh_trk", "Re-handle truck productivity", f"=60/{PA['rh_cycle']}*{PA['rh_payload']}*{I('op_eff')}", "bcm/op-h")
    p("rh_wl", "Wheel loader productivity (sand)", f"={I('wl_bucket')}*{I('wl_fill')}*3600/{I('wl_cycle_s')}*{I('wl_exch')}*{I('op_eff')}/{I('swell_sand')}", "bcm/op-h")
    p("ore_wl", "Wheel loader productivity (ore, selective)", f"={I('wl_bucket')}*{I('wl_fill')}*3600/{I('wl_cycle_s')}*{I('wl_exch')}*{I('op_eff')}/{I('swell_mud')}*0.6", "bcm/op-h", "40% selective-loading penalty on 5 m ore benches (ITT s6.2.6). " + A_)
    band(wp, prow[0], "Epiroc D65 drill productivity by layer", 4)
    prow[0] += 1
    for lay, ar, pn in (("B2 Blasted sand", "area_c2", "pen_c2"), ("B3 Cemented sand / sandstone", "area_c3", "pen_c3"), ("B4 Mudstone / leach cap", "area_c4", "pen_c4")):
        k = pn
        p("m_" + k, f"{lay} - effective drilling rate", f"={I(pn)}*{I('drill_move_eff')}", "m/h", "Net penetration x efficiency")
        p("bcm_" + k, f"{lay} - blasted volume per rig-hour", f"={PA['m_' + k]}/({I('bench_h')}+{I('subdrill')})*{I(ar)}*{I('bench_h')}", "bcm/h")
        p("cap_" + k, f"{lay} - monthly capacity per rig (30.4 d)", f"={PA['bcm_' + k]}*{I('hours_per_day')}*30.4*{I('drill_avail')}*{I('drill_util')}", "bcm/month", "", "#,##0")
    p("hole_len", "Hole length (bench + sub-drill)", f"={I('bench_h')}+{I('subdrill')}", "m", "Single-pass capability of the D65 assumed for an 11 m hole - confirm with Epiroc", "0.0")
    for col, w in zip("ABCD", (58, 16, 14, 90)):
        wp.column_dimensions[col].width = w

    # ------------------------------------------------------------------ Schedule
    ws = wb.create_sheet("Schedule")
    FC = 4  # first month column

    def cl(t):
        return CL(FC + t - 1)

    LASTC = cl(N)
    rows = []  # (key, label, unit, fn, fmt, tot)
    RW = {}

    def add(key, label, unit, fn, fmt="#,##0", tot="sum"):
        rows.append((key, label, unit, fn, fmt, tot))

    def sec(text):
        rows.append(("__sec__", text, None, None, None, None))

    def R(key, t, abs_row=False):
        return f"{cl(t)}{RW[key]}"

    def prev(key, t, default="0"):
        return R(key, t - 1) if t > 1 else default

    def nxt(key, t):
        return R(key, t + 1) if t < N else "0"

    # calendar
    sec("CALENDAR")
    add("mno", "Month number", "#", lambda t: t, "0", None)
    add("date", "Month", "", lambda t: f"=DATE(YEAR({I('start_date')}),MONTH({I('start_date')})+{R('mno', t)}-1,1)", "mmm-yy", None)
    add("days", "Calendar days", "days", lambda t: f"=DATE(YEAR({R('date', t)}),MONTH({R('date', t)})+1,1)-{R('date', t)}", "0", "sum")
    add("lost", "Weather days lost", "days", lambda t: f"=INDEX({WREF},MONTH({R('date', t)}))", "0.0", "sum")
    add("work", "Workable days", "days", lambda t: f"={R('days', t)}-{R('lost', t)}", "0.0", "sum")
    add("hrs", "Scheduled hours per unit", "h", lambda t: f"={R('work', t)}*{I('hours_per_day')}", "#,##0", "sum")
    RAMP = [0, 0.10, 0.35, 0.60, 0.80, 0.95] + [1.0] * (N - 6)
    add("ramp", "Production ramp factor (INPUT)", "fraction", lambda t: RAMP[t - 1], "0.00", None)
    add("ov", "Pre-strip volume override (INPUT, blank = plan)", "bcm", lambda t: None, "#,##0", None)
    sec("PRE-STRIP PRODUCTION")
    add("cap", "Fleet / ramp capacity", "bcm", lambda t: f"=IF({R('mno', t)}<={I('last_prod_month')},{I('full_rate')}*{R('ramp', t)}*{R('work', t)}/{R('days', t)},0)", "#,##0", "sum")
    add("vol", "Pre-strip volume mined", "bcm", lambda t: f"=IF(ISNUMBER({R('ov', t)}),{R('ov', t)},MAX(0,MIN({R('cap', t)},{I('vol_total')}-{prev('cum', t)})))", "#,##0", "sum")
    add("cum", "Cumulative pre-strip", "bcm", lambda t: f"={prev('cum', t)}+{R('vol', t)}", "#,##0", "last")
    add("pct", "Cumulative % of 21.6 Mbcm", "%", lambda t: f"={R('cum', t)}/{I('vol_total')}", "0%", "last")
    add("A", "Layer A - aeolian sands (0-15 m)", "bcm", lambda t: f"=MIN({R('vol', t)},{Q('vol_A')}-{prev('cumA', t)})", "#,##0", "sum")
    add("B", "Layer B - cemented sand / sandstone (15-50 m)", "bcm", lambda t: f"=MIN({R('vol', t)}-{R('A', t)},{Q('vol_B')}-{prev('cumB', t)})", "#,##0", "sum")
    add("C", "Layer C - mudstone / leach cap (50-70 m)", "bcm", lambda t: f"=MIN({R('vol', t)}-{R('A', t)}-{R('B', t)},{Q('vol_C')}-{prev('cumC', t)})", "#,##0", "sum")
    add("cumA", "  cum A", "bcm", lambda t: f"={prev('cumA', t)}+{R('A', t)}", "#,##0", "last")
    add("cumB", "  cum B", "bcm", lambda t: f"={prev('cumB', t)}+{R('B', t)}", "#,##0", "last")
    add("cumC", "  cum C", "bcm", lambda t: f"={prev('cumC', t)}+{R('C', t)}", "#,##0", "last")
    add("Afd", "  Free-dig sand (no blasting)", "bcm", lambda t: f"={R('A', t)}*{I('freedig')}", "#,##0", "sum")
    add("floor", "Pit floor depth below surface (end of month)", "m", lambda t: f"={I('depth_sand')}*MIN(1,{R('cumA', t)}/{Q('vol_A')})+({I('depth_mid')}-{I('depth_sand')})*MIN(1,{R('cumB', t)}/{Q('vol_B')})+({I('depth_total')}-{I('depth_mid')})*MIN(1,{R('cumC', t)}/{Q('vol_C')})", "0.0", "last")
    add("bench", "Benches completed (10 m)", "#", lambda t: f"={R('floor', t)}/{I('bench_h')}", "0.0", "last")
    add("avgd", "Average face depth in month", "m", lambda t: f"=({prev('floor', t)}+{R('floor', t)})/2", "0.0", "max")
    add("wtfl", "Pit floor below the ~50 m water table?", "1 = yes", lambda t: f"=IF({R('floor', t)}>{I('depth_mid')},1,0)", "0", "max")
    sec("DESTINATIONS (build order: haul roads, ROM pad, ponds / bunds, stockpile bases; TSF capped; balance to WRL)")
    add("availAB", "Sand + cemented rock available", "bcm", lambda t: f"={R('A', t)}+{R('B', t)}", "#,##0", "sum")
    add("infraAB", "To infrastructure (layers A + B)", "bcm", lambda t: f"=MAX(0,MIN({R('availAB', t)}*{I('infra_cap')},{Q('infra_AB')}-{prev('cumInfraAB', t)}))", "#,##0", "sum")
    add("cumInfraAB", "  cum infrastructure A + B", "bcm", lambda t: f"={prev('cumInfraAB', t)}+{R('infraAB', t)}", "#,##0", "last")
    add("tsf", "To TSF Stage 0 (after foundation prep EW-06)", "bcm", lambda t: f"=IF({R('mno', t)}<=Earthworks!$G$10,0,MAX(0,MIN({R('availAB', t)}*{I('tsf_cap')},{I('tsf_tot')}-{prev('cumTSF', t)},{R('availAB', t)}-{R('infraAB', t)})))", "#,##0", "sum")
    add("cumTSF", "  cum TSF", "bcm", lambda t: f"={prev('cumTSF', t)}+{R('tsf', t)}", "#,##0", "last")
    add("wrlAB", "To WRL (layers A + B)", "bcm", lambda t: f"={R('availAB', t)}-{R('infraAB', t)}-{R('tsf', t)}", "#,##0", "sum")
    add("infraC", "To stockpile base clay liner (layer C)", "bcm", lambda t: f"=IF({Q('vol_C')}=0,0,{R('C', t)}*{Q('clay')}/{Q('vol_C')})", "#,##0", "sum")
    add("cumInfraC", "  cum clay liner", "bcm", lambda t: f"={prev('cumInfraC', t)}+{R('infraC', t)}", "#,##0", "last")
    add("wrlC", "To WRL (layer C, PAF cells)", "bcm", lambda t: f"={R('C', t)}-{R('infraC', t)}", "#,##0", "sum")
    add("infra", "Total to infrastructure", "bcm", lambda t: f"={R('infraAB', t)}+{R('infraC', t)}", "#,##0", "sum")
    add("wrl", "Total to WRL", "bcm", lambda t: f"={R('wrlAB', t)}+{R('wrlC', t)}", "#,##0", "sum")
    add("dchk", "  Destination check (should be 0)", "bcm", lambda t: f"=ROUND({R('infra', t)}+{R('tsf', t)}+{R('wrl', t)}-{R('vol', t)},2)", "#,##0", "sum")
    add("rehandle", "TSF stockpile re-handle (reclaim)", "bcm", lambda t: f"={I('rehandle_pct')}*{R('tsf', t)}", "#,##0", "sum")
    sec("ORE (first ~600 kt to stockpiles)")
    add("oreshare", "  Share of ore harvested in month", "fraction", lambda t: f"=IF({Q('vol_C')}=0,0,MAX(0,{R('cumC', t)}/{Q('vol_C')}-MAX({prev('cumC', t)}/{Q('vol_C')},{I('ore_start_frac')}))/(1-{I('ore_start_frac')}))", "0.00", "sum")
    add("ore", "Ore mined to stockpile", "t", lambda t: f"={I('ore_tot')}*{R('oreshare', t)}", "#,##0", "sum")
    add("orebcm", "Ore volume", "bcm", lambda t: f"={R('ore', t)}/{I('dens_mud')}", "#,##0", "sum")
    add("cumOre", "  cum ore", "t", lambda t: f"={prev('cumOre', t)}+{R('ore', t)}", "#,##0", "last")
    add("presplit", "Pre-split / trim drill required (ore only)", "units", lambda t: f"=IF({R('ore', t)}>0,{I('presplit_rigs')},0)", "0", "max")
    sec("DRILL AND BLAST - Epiroc D65 (drilled one month ahead of mining)")
    nA = lambda t: nxt("A", t)
    nB = lambda t: nxt("B", t)
    nC = lambda t: nxt("C", t)
    add("blnext", "Volume to be blasted for next month", "bcm", lambda t: f"={nA(t)}*(1-{I('freedig')})+{nB(t)}+{nC(t)}", "#,##0", "sum")
    add("holes", "Holes drilled", "holes", lambda t: f"={nA(t)}*(1-{I('freedig')})/({I('area_c2')}*{I('bench_h')})+{nB(t)}/({I('area_c3')}*{I('bench_h')})+{nC(t)}/({I('area_c4')}*{I('bench_h')})", "#,##0", "sum")
    add("metres", "Metres drilled", "m", lambda t: f"={R('holes', t)}*({I('bench_h')}+{I('subdrill')})", "#,##0", "sum")
    add("cumM", "  cum metres", "m", lambda t: f"={prev('cumM', t)}+{R('metres', t)}", "#,##0", "last")
    add("dhrs", "Drill hours required", "h", lambda t: f"=({nA(t)}*(1-{I('freedig')})/({I('area_c2')}*{I('bench_h')})*({I('bench_h')}+{I('subdrill')})/{I('pen_c2')}+{nB(t)}/({I('area_c3')}*{I('bench_h')})*({I('bench_h')}+{I('subdrill')})/{I('pen_c3')}+{nC(t)}/({I('area_c4')}*{I('bench_h')})*({I('bench_h')}+{I('subdrill')})/{I('pen_c4')})/{I('drill_move_eff')}", "#,##0", "sum")
    add("drills", "Epiroc D65 rigs required", "units", lambda t: f"=IF({R('dhrs', t)}<=0,0,MAX({I('min_drills')},ROUNDUP(ROUND({R('dhrs', t)}/({R('hrs', t)}*{I('drill_avail')}*{I('drill_util')}),4),0)))", "0", "max")
    add("expl", "Bulk emulsion", "t", lambda t: f"=({nA(t)}*(1-{I('freedig')})*{I('pf_c2')}+{nB(t)}*{I('pf_c3')}+{nC(t)}*{I('pf_c4')})/1000", "#,##0", "sum")
    add("dets", "Electronic detonators", "each", lambda t: f"={R('holes', t)}*{I('det_per_hole')}", "#,##0", "sum")
    add("mhrs", "MPU charging hours", "h", lambda t: f"={R('expl', t)}/{I('mpu_rate')}", "#,##0", "sum")
    add("mpu", "Bulk emulsion MPU / charging units required", "units", lambda t: f"=IF({R('mhrs', t)}<=0,0,MAX({I('min_mpu')},ROUNDUP(ROUND({R('mhrs', t)}/({R('hrs', t)}*{I('mpu_avail')}*{I('mpu_util')}),4),0)))", "0", "max")
    sec("LOAD AND HAUL (XDE260-class trucks, 700 t-class excavators - free-issue fleet assumed)")
    add("dens", "Weighted bank density", "t/bcm", lambda t: f"=IF({R('vol', t)}=0,0,({R('A', t)}*{I('dens_sand')}+{R('B', t)}*{I('dens_mid')}+{R('C', t)}*{I('dens_mud')})/{R('vol', t)})", "0.00", None)
    add("swell", "Weighted swell", "x", lambda t: f"=IF({R('vol', t)}=0,1,({R('A', t)}*{I('swell_sand')}+{R('B', t)}*{I('swell_mid')}+{R('C', t)}*{I('swell_mud')})/{R('vol', t)})", "0.00", None)
    add("payload", "Truck payload per load", "bcm", lambda t: f"=IF({R('vol', t)}=0,0,MIN({I('truck_payload')}/{R('dens', t)},{I('truck_body_m3')}/{R('swell', t)}))", "0.0", None)
    add("passes", "Excavator passes per truck", "passes", lambda t: f"=IF({R('vol', t)}=0,0,MAX(1,ROUND({R('payload', t)}*{R('swell', t)}/({I('ex_bucket')}*{I('ex_fill')}),0)))", "0", None)
    add("lead", "Weighted surface lead", "km", lambda t: f"=IF({R('vol', t)}=0,0,{I('haul_mult')}*({R('infra', t)}*{I('d_inf')}+{R('tsf', t)}*{I('d_tsf')}+{R('wrl', t)}*{I('d_wrl')})/{R('vol', t)})", "0.0", None)
    add("rampkm", "Ramp length to average face", "km", lambda t: f"={R('avgd', t)}/{I('ramp_grade')}/1000", "0.00", None)
    add("cycle", "Truck cycle time", "min", lambda t: f"=IF({R('vol', t)}=0,0,{R('passes', t)}*{I('ex_cycle_s')}/60+{I('t_spot')}+{R('rampkm', t)}*(60/{I('v_ramp_loaded')}+60/{I('v_ramp_empty')})+({I('inpit_flat_km')}+{R('lead', t)})*(60/{I('v_loaded')}+60/{I('v_empty')})+{I('t_dump')}+{I('t_queue')})", "0.0", None)
    add("tprod", "Truck productivity", "bcm/op-h", lambda t: f"=IF({R('vol', t)}=0,0,60/{R('cycle', t)}*{R('payload', t)}*{I('op_eff')})", "#,##0", None)
    add("thrs", "Truck hours required (incl. TSF re-handle)", "h", lambda t: f"=IF({R('vol', t)}=0,0,{R('vol', t)}/{R('tprod', t)})+{R('rehandle', t)}/{PA['rh_trk']}", "#,##0", "sum")
    add("trucks", "XDE260-class trucks required", "units", lambda t: f"=IF({R('thrs', t)}<=0,0,ROUNDUP(ROUND({R('thrs', t)}*(1+{I('fleet_contingency')})/({R('hrs', t)}*{I('truck_avail')}*{I('truck_util')}),4),0))", "0", "max")
    add("exprod", "Excavator productivity", "bcm/op-h", lambda t: f"=IF({R('vol', t)}=0,0,{I('ex_bucket')}*{I('ex_fill')}*3600/{I('ex_cycle_s')}*{I('ex_exch')}*{I('op_eff')}/{R('swell', t)})", "#,##0", None)
    add("ehrs", "Excavator hours required", "h", lambda t: f"=IF({R('vol', t)}=0,0,{R('vol', t)}/{R('exprod', t)})", "#,##0", "sum")
    add("exc", "700 t-class excavators required", "units", lambda t: f"=IF({R('vol', t)}=0,0,MAX({I('min_faces')},ROUNDUP(ROUND({R('ehrs', t)}/({R('hrs', t)}*{I('ex_avail')}*{I('ex_util')}),4),0)))", "0", "max")
    add("whrs", "Wheel loader hours (re-handle + ore)", "h", lambda t: f"={R('rehandle', t)}/{PA['rh_wl']}+{R('orebcm', t)}/{PA['ore_wl']}", "#,##0", "sum")
    add("wl", "Wheel loaders required (incl. extras)", "units", lambda t: f"=IF({R('vol', t)}=0,0,ROUNDUP(ROUND({R('whrs', t)}/({R('hrs', t)}*{I('wl_avail')}*{I('wl_util')}),4),0)+{I('wl_extra')})", "0", "max")
    add("pumps", "Dewatering pump sets in operation", "units", lambda t: f"=IF({R('vol', t)}=0,0,IF({R('wtfl', t)}=1,{I('pumps')},{I('pump_base')}))", "0", "max")
    sec("MATERIAL MOVED")
    add("borrowv", "Borrow pit excavation (extra to pre-strip)", "bcm", lambda t: f"=Earthworks!{{EW_BORROW_{t}}}", "#,##0", "sum")
    add("topv", "Topsoil stripped and stockpiled", "bcm", lambda t: f"=Earthworks!{{EW_TOP_{t}}}", "#,##0", "sum")
    add("tmm", "Total material moved (pre-strip + re-handle + borrow + topsoil)", "bcm", lambda t: f"={R('vol', t)}+{R('rehandle', t)}+{R('borrowv', t)}+{R('topv', t)}", "#,##0", "sum")

    # assign rows
    r0 = 5
    for i, (key, *_rest) in enumerate(rows):
        rr = r0 + i
        if key != "__sec__":
            RW[key] = rr
    SCH = {k: f"Schedule!$C${v}" for k, v in RW.items()}  # peak / total column
    SCHM = lambda k, t: f"Schedule!{cl(t)}{RW[k]}"  # noqa: E731
    SCHR = lambda k: f"Schedule!${cl(1)}${RW[k]}:${cl(N)}${RW[k]}"  # noqa: E731

    title(ws, "Mine schedule - first 24 months (Dec 2027 to Nov 2029)",
          "Months run from Site Access (23/11/2027) to Completion (30/11/2029). Yellow rows are inputs. Column C is the total, peak or end value as labelled.")
    hdr(ws, 4, ["Line", "Unit", "Total / peak / end"] + [""] * N)
    ws.row_dimensions[4].height = 22
    ws_late = []  # formulas needing Earthworks addresses, patched after Earthworks is built
    for i, (key, label, unit, fn, fmt, tot) in enumerate(rows):
        rr = r0 + i
        if key == "__sec__":
            band(ws, rr, label, FC + N - 1)
            continue
        ws.cell(row=rr, column=1, value=label)
        ws.cell(row=rr, column=2, value=unit)
        for t in range(1, N + 1):
            v = fn(t)
            c = ws.cell(row=rr, column=FC + t - 1, value=v)
            c.number_format = fmt
            if key in ("ramp", "ov"):
                c.fill, c.font = INP, BLUE
            if isinstance(v, str) and "{EW_" in v:
                ws_late.append((rr, FC + t - 1, v))
        a, b = cl(1), cl(N)
        if tot == "sum":
            f = f"=SUM({a}{rr}:{b}{rr})"
        elif tot == "max":
            f = f"=MAX({a}{rr}:{b}{rr})"
        elif tot == "last":
            f = f"={b}{rr}"
        else:
            f = None
        if f:
            c = ws.cell(row=rr, column=3, value=f)
            c.number_format, c.fill, c.font = fmt, OUTF, BOLD
    # month header rows (date) at row 4 via formula
    for t in range(1, N + 1):
        c = ws.cell(row=4, column=FC + t - 1, value=f"={cl(t)}{RW['date']}")
        c.number_format, c.font, c.fill = "mmm-yy", WHITE, HEAD
        c.alignment = Alignment(horizontal="center")
    ws.column_dimensions["A"].width = 58
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 16
    for t in range(1, N + 1):
        ws.column_dimensions[cl(t)].width = 11
    ws.freeze_panes = ws.cell(row=5, column=FC)
    for key in ("vol", "trucks", "exc", "drills", "cum", "pct", "floor"):
        for col in range(1, FC + N):
            ws.cell(row=RW[key], column=col).font = BOLD if col != FC else BOLD

    # ------------------------------------------------------------------ Earthworks
    we = wb.create_sheet("Earthworks")
    EC = 16  # first month column (P)

    def ecl(t):
        return CL(EC + t - 1)

    title(we, "Earthworks and infrastructure schedule (mine-related)",
          "LIN rows spread the quantity evenly across Start-Finish. PIT rows are fed by the Schedule (fill placed direct from the pit); their Start / Finish are calculated. "
          "Plant-site, MAR, Village and Aerodrome earthworks are separate SP1 work areas and are not in this fleet (see Assumptions_Log).")
    hdr(we, 4, ["ID", "Activity", "Quantity", "Unit", "Mode", "Start (M#)", "Finish (M#)", "Duration (months)", "Machine group",
                "Prod. (unit / op-h)", "Machine hours", "Topsoil depth (m)", "Cum. start (bcm)", "Cum. end (bcm)", "Notes / ITT reference"] +
        [f"={SCHM('date', t)}" for t in range(1, N + 1)], height=36)
    for t in range(1, N + 1):
        c = we.cell(row=4, column=EC + t - 1)
        c.number_format = "mmm-yy"
    # month numbers on row 3
    for t in range(1, N + 1):
        c = we.cell(row=3, column=EC + t - 1, value=t)
        c.font = Font(color="808080", size=8)
        c.alignment = Alignment(horizontal="center")
    we.cell(row=3, column=15, value="Month #").font = Font(color="808080", size=8)

    cumAB = SCHR("cumInfraAB")
    cumTSFr = SCHR("cumTSF")
    cumCr = SCHR("cumInfraC")
    cumVol = SCHR("cum")
    # (id, name, qty formula, unit, mode, start, dur, group, prod, topsoil, note)
    ew = [
        ("EW-01", "Mobilise; go-line hardstand, temporary HME workshop, fuel farm, magazine / ANFO store, field lab and laydown pads", f"={I('support_ha')}", "ha", "LIN", 1, 2, "DOZ", f"={I('clear_prod')}", f"={I('topsoil_gen')}", "ITT s5.5-5.6, s6.2.2. Free-issue HME accepted at go-line (s10.2.3)"),
        ("EW-02", "Clear, grub and strip topsoil - haul road corridors and pit access", f"={Q('ha_road')}", "ha", "LIN", 1, 4, "DOZ", f"={I('clear_prod')}", f"={I('topsoil_gen')}", "ITT s6.1.3-6.1.4; single clearing / grubbing item"),
        ("EW-03", "Clear, grub and strip topsoil - pit cutbacks 1-2", f"={Q('ha_pit')}", "ha", "LIN", 2, 4, "DOZ", f"={I('clear_prod')}", f"={I('topsoil_gen')}", "Cleared ahead of the first bench"),
        ("EW-04", "Clear, grub and strip topsoil - waste rock landform footprint (progressive)", f"={Q('ha_wrl')}", "ha", "LIN", 2, 12, "DOZ", f"={I('clear_prod')}", f"={I('topsoil_gen')}", "WRL footprint sized from the WRL volume"),
        ("EW-05", "Clear, grub and strip topsoil - ROM pad and stockpile footprints", f"={Q('ha_rom')}", "ha", "LIN", 2, 4, "DOZ", f"={I('clear_prod')}", f"={I('topsoil_gen')}", "ITT WA3 / WA4"),
        ("EW-06", "Clear, strip topsoil and prepare dune foundation - TSF Stage 0", f"={Q('ha_tsf')}", "ha", "LIN", 2, 3, "DOZ", f"={I('clear_prod')}", f"={I('topsoil_tsf')}", "200 mm topsoil; 1 m maximum dune disturbance; impact roll loose zones (p258)"),
        ("EW-07", "Backfill 24 existing TSF boreholes with cement-bentonite-sand grout", 24, "holes", "LIN", 3, 3, "GRT", f"={I('grout_prod')}", None, "ITT s6.3.2 p257"),
        ("EW-08", "Borrow pit - initial haul road and hardstand material", f"={I('borrow_vol')}", "bcm", "LIN", 2, 3, "EXC", f"={I('borrow_ex_prod')}", None, "Borrow Pit Management Plan not supplied (p240)"),
        ("EW-09", "Haul roads 17 km - pit ramps, in-pit and surface roads (fill from pit)", f"={Q('roads_pit')}", "bcm", "INF", None, None, None, None, None, "Priority 1. XDE260-class two-way, running width 3.5 x truck width; drainage slots every ~20 m (p252)"),
        ("EW-10", "ROM pad, crusher skyway and stockpile fingers (bulk fill, traffic-roll compacted)", f"={Q('rom')}", "bcm", "INF", None, None, None, None, None, "Priority 2. Layers up to 5 m (p252). ROM wall by MPP EPC; select-fill pocket by others"),
        ("EW-11", "Ponds, bunds, diversion drains, magazine and laydown pads", f"={Q('misc')}", "bcm", "INF", None, None, None, None, None, "Priority 3. Detention Ponds 1-2, Mine Dewatering Pond, surface water diversion (p234, p254)"),
        ("EW-12", "Stockpile bases - granular fill (primary sulphide, low grade, leach cap)", f"={Q('sp_gran')}", "bcm", "INF", None, None, None, None, None, "Priority 4. Ready ahead of first ore"),
        ("EW-13", "Stockpile bases - clayey mudstone liner (2 m, layer C)", f"={Q('clay')}", "bcm", "CLY", None, None, None, None, None, "Mudstone from the 50-70 m interval (p254)"),
        ("EW-14", "HDPE liner installation - lined stockpile bases and ponds", f"={I('sp_area_ha')}*{I('clay_share')}", "ha", "LIN", None, 4, None, None, None, "Starts with the clay liner"),
        ("EW-15", "TSF Stage 0 embankment, basin and dune fill (Zone 4A / 2B) placed direct from pit", f"={I('tsf_tot')}", "bcm", "TSF", None, None, None, None, None, "1-2 m paddock layers, traffic-roll compaction; 2 m lift limit at HST interface (p248, p253)"),
        ("EW-16", "Waste rock landform construction (5 m lifts, PAF encapsulated in NAF)", f"={Q('d_wrl')}", "bcm", "WRL", None, None, None, None, None, "ITT s6.2.8 p248"),
        ("EW-17", "Ore recovery to stockpiles (first ~600 kt)", f"={I('ore_tot')}", "t", "ORE", None, None, None, None, None, "5 m ore benches; pre-split in ore only (p244, p246)"),
        ("EW-18", "Pit dewatering - sumps, pumps and pipelines (floor below ~50 m water table)", f"={I('pumps')}", "pumps", "DEW", None, None, None, None, None, "Contractor dewatering with no inflow data (R-25, p254)"),
        ("EW-19", "Rehabilitation, final clean-up and demobilisation", f"={I('rehab_ha')}", "ha", "LIN", 23, 2, "DOZ", f"={I('clear_prod')}", None, "ITT s6.2.2; demobilisation notice 7 days (p321)"),
    ]
    EWR = {}
    for i, e in enumerate(ew):
        EWR[e[0]] = 5 + i
    assert EWR["EW-06"] == 10  # Schedule tsf gate refers to Earthworks!$G$10
    firstdata = 5
    lastdata = 5 + len(ew) - 1
    for i, (eid, name, qty, unit, mode, start, dur, grp, prod, top, note) in enumerate(ew):
        rr = firstdata + i
        we.cell(row=rr, column=1, value=eid)
        we.cell(row=rr, column=2, value=name).alignment = WRAP
        qc = we.cell(row=rr, column=3, value=qty)
        qc.number_format = "#,##0"
        we.cell(row=rr, column=4, value=unit)
        we.cell(row=rr, column=5, value=mode)
        # start / finish / duration
        if mode == "LIN":
            if eid == "EW-14":
                s = f"=F{EWR['EW-13']}"
            else:
                s = start
            cS = we.cell(row=rr, column=6, value=s)
            cD = we.cell(row=rr, column=8, value=dur)
            if eid != "EW-14":
                cS.fill, cS.font = INP, BLUE
            cD.fill, cD.font = INP, BLUE
            we.cell(row=rr, column=7, value=f"=MIN({N},F{rr}+H{rr}-1)")
        else:
            thr0 = thr1 = None
            if mode == "INF":
                if eid == "EW-09":
                    we.cell(row=rr, column=13, value=0)
                else:
                    we.cell(row=rr, column=13, value=f"=N{rr - 1}")
                we.cell(row=rr, column=14, value=f"=M{rr}+C{rr}")
                we.cell(row=rr, column=6, value=f"=MIN({N},COUNTIF({cumAB},\"<\"&(M{rr}+0.5))+1)")
                we.cell(row=rr, column=7, value=f"=MIN({N},COUNTIF({cumAB},\"<\"&(N{rr}-0.5))+1)")
            elif mode == "CLY":
                we.cell(row=rr, column=13, value=0)
                we.cell(row=rr, column=14, value=f"=C{rr}")
                we.cell(row=rr, column=6, value=f"=MIN({N},COUNTIF({cumCr},\"<\"&0.5)+1)")
                we.cell(row=rr, column=7, value=f"=MIN({N},COUNTIF({cumCr},\"<\"&(N{rr}-0.5))+1)")
            elif mode == "TSF":
                we.cell(row=rr, column=6, value=f"=MIN({N},COUNTIF({cumTSFr},\"<\"&0.5)+1)")
                we.cell(row=rr, column=7, value=f"=MIN({N},COUNTIF({cumTSFr},\"<\"&(C{rr}-0.5))+1)")
            elif mode in ("WRL",):
                we.cell(row=rr, column=6, value=f"=MIN({N},COUNTIF({cumVol},\"<\"&0.5)+1)")
                we.cell(row=rr, column=7, value=f"=MIN({N},COUNTIF({cumVol},\"<\"&({I('vol_total')}-0.5))+1)")
            elif mode == "ORE":
                we.cell(row=rr, column=6, value=f"=MIN({N},COUNTIF({SCHR('cumOre')},\"<\"&0.5)+1)")
                we.cell(row=rr, column=7, value=f"=MIN({N},COUNTIF({SCHR('cumOre')},\"<\"&({I('ore_tot')}-0.5))+1)")
            elif mode == "DEW":
                we.cell(row=rr, column=6, value=f"=MIN({N},COUNTIF({SCHR('floor')},\"<=\"&{I('depth_mid')})+1)")
                we.cell(row=rr, column=7, value=f"={N}-2")
            we.cell(row=rr, column=8, value=f"=G{rr}-F{rr}+1")
        we.cell(row=rr, column=9, value=grp)
        if prod:
            we.cell(row=rr, column=10, value=prod).number_format = "0.00"
            we.cell(row=rr, column=11, value=f"=C{rr}/J{rr}").number_format = "#,##0"
        if top:
            we.cell(row=rr, column=12, value=top).number_format = "0.00"
        we.cell(row=rr, column=15, value=note).alignment = WRAP
        for t in range(1, N + 1):
            c_ = ecl(t)
            mcell = f"{c_}$3"
            if mode == "LIN":
                f = f"=IF(AND({mcell}>=$F{rr},{mcell}<=$G{rr}),$C{rr}/$H{rr},0)"
            elif mode == "INF":
                pc = f"Schedule!{cl(t - 1)}{RW['cumInfraAB']}" if t > 1 else "0"
                f = f"=MAX(0,MIN(Schedule!{cl(t)}{RW['cumInfraAB']},$N{rr})-MAX({pc},$M{rr}))"
            elif mode == "CLY":
                f = f"=Schedule!{cl(t)}{RW['infraC']}"
            elif mode == "TSF":
                f = f"=Schedule!{cl(t)}{RW['tsf']}"
            elif mode == "WRL":
                f = f"=Schedule!{cl(t)}{RW['wrl']}"
            elif mode == "ORE":
                f = f"=Schedule!{cl(t)}{RW['ore']}"
            elif mode == "DEW":
                f = f"=IF(AND({mcell}>=$F{rr},{mcell}<=$G{rr}),$C{rr},0)"
            we.cell(row=rr, column=EC + t - 1, value=f).number_format = "#,##0"
        if mode == "LIN" and eid != "EW-14":
            pass
    # monthly summary blocks
    rb = lastdata + 3
    band(we, rb, "MONTHLY SUMMARY", EC + N - 1)
    EW_TOP = rb + 1
    EW_BORROW = rb + 2
    we.cell(row=EW_TOP, column=2, value="Topsoil stripped and stockpiled (bcm)")
    we.cell(row=EW_BORROW, column=2, value="Borrow pit excavation (bcm)")
    for t in range(1, N + 1):
        c_ = ecl(t)
        we.cell(row=EW_TOP, column=EC + t - 1, value=f"=SUMPRODUCT({c_}{firstdata}:{c_}{lastdata},$L{firstdata}:$L{lastdata})*10000").number_format = "#,##0"
        we.cell(row=EW_BORROW, column=EC + t - 1, value=f"={c_}{EWR['EW-08']}").number_format = "#,##0"
    # machine hour block
    rh = EW_BORROW + 2
    band(we, rh, "PRIMARY MACHINE HOURS BY GROUP (early works fleet; pit-fed fill uses the pit HME)", EC + N - 1)
    groups = [("DOZ", "Track dozers - clearing, topsoil, pads, rehabilitation"), ("EXC", "90 t-class excavators - borrow pit"),
              ("TRK", "90-100 t-class trucks - borrow, topsoil, clay"), ("GRT", "Grout plant - TSF boreholes")]
    GH = {}
    for gi, (g, gname) in enumerate(groups):
        rr = rh + 1 + gi
        GH[g] = rr
        we.cell(row=rr, column=2, value=gname + " - machine hours")
        we.cell(row=rr, column=9, value=g)
        for t in range(1, N + 1):
            c_ = ecl(t)
            if g == "TRK":
                f = (f"={c_}{EWR['EW-08']}/{I('borrow_trk_prod')}+{c_}{EW_TOP}/{I('borrow_trk_prod')}")
            else:
                f = (f"=SUMPRODUCT(($I${firstdata}:$I${lastdata}=\"{g}\")*{c_}{firstdata}:{c_}{lastdata}/IF($J${firstdata}:$J${lastdata}=0,1,$J${firstdata}:$J${lastdata}))")
            we.cell(row=rr, column=EC + t - 1, value=f).number_format = "#,##0"
    ru = rh + 1 + len(groups) + 1
    band(we, ru, "UNITS REQUIRED BY MONTH (hours / (scheduled hours x availability x early works utilisation))", EC + N - 1)
    GU = {}
    for gi, (g, gname) in enumerate(groups):
        rr = ru + 1 + gi
        GU[g] = rr
        we.cell(row=rr, column=2, value=gname + " - units")
        for t in range(1, N + 1):
            c_ = ecl(t)
            f = f"=IF({c_}{GH[g]}<=0,0,ROUNDUP(ROUND({c_}{GH[g]}/(Schedule!{cl(t)}{RW['hrs']}*{I('supp_avail')}*{I('ew_util')}),4),0))"
            we.cell(row=rr, column=EC + t - 1, value=f).number_format = "0"
        we.cell(row=rr, column=3, value=f"=MAX({ecl(1)}{rr}:{ecl(N)}{rr})").fill = OUTF
    for col, w in zip(range(1, 16), (8, 62, 13, 8, 7, 9, 9, 10, 9, 10, 11, 9, 11, 11, 60)):
        we.column_dimensions[CL(col)].width = w
    for t in range(1, N + 1):
        we.column_dimensions[ecl(t)].width = 10
    we.freeze_panes = we.cell(row=5, column=3)

    # patch Schedule links to Earthworks
    for rr, cc, v in ws_late:
        t = cc - FC + 1
        if "EW_BORROW" in v:
            ws.cell(row=rr, column=cc, value=f"=Earthworks!{ecl(t)}{EW_BORROW}")
        else:
            ws.cell(row=rr, column=cc, value=f"=Earthworks!{ecl(t)}{EW_TOP}")
    EWU = {g: f"Earthworks!$C${GU[g]}" for g in GU}

    # ------------------------------------------------------------------ Fleet register
    wf = wb.create_sheet("Fleet_Register")
    title(wf, "Equipment list - first 24 months",
          "Calculated quantity is the peak requirement from Schedule / Earthworks. Type an Override to test another fleet. Supply basis follows the ITT: primary HME is Company free-issue (XCMG, list not supplied), everything else is Contractor.")
    hdr(wf, 4, ["Ref", "Section", "Equipment", "Make / class", "Supply basis", "Unit", "Calculated qty", "Override", "Selected qty",
                "Mobilise M#", "Last M#", "Avail.", "Util.", "Diesel L/h", "Role / sizing basis", "ITT / source reference"], height=32)
    FREE = "Company free-issue (assumed)"
    CON = "Contractor"
    items = []

    def S(text):
        items.append(("SEC", text))

    def it(ref, name, model, supply, unit, calc, mob, lph, av, ut, basis, src, drive=None, hrsk=None, op=False):
        items.append(("ITEM", dict(ref=ref, name=name, model=model, supply=supply, unit=unit, calc=calc, mob=mob, lph=lph, av=av,
                                   ut=ut, basis=basis, src=src, drive=drive, hrsk=hrsk, op=op)))

    S("A. PRIMARY LOAD AND HAUL (pre-strip)")
    it("A1", "Rear dump truck", "XCMG XDE260 class, 260 t", FREE, "units", lambda F: f"={SCH['trucks']}", 2, 380, I('truck_avail'), I('truck_util'),
       "Peak monthly truck hours incl. contingency / available hours per truck; cycle varies with depth and destination mix", "ITT s6.2.10 p252 (design truck); s10.2 p302-303 (free-issue); list C-WN-0000-G-LST-00005 not supplied",
       drive="trucks", hrsk="thrs", op=True)
    it("A2", "Hydraulic excavator", "700 t class, ~40 m3 (XCMG class)", FREE, "units", lambda F: f"={SCH['exc']}", 2, 750, I('ex_avail'), I('ex_util'),
       "Larger of minimum dig faces and hours / available hours", "ITT s10.2 p302-303; class assumed, not stated",
       drive="exc", hrsk="ehrs", op=True)
    it("A3", "Wheel loader", "~20 m3 class", FREE, "units", lambda F: f"={SCH['wl']}", 2, 300, I('wl_avail'), I('wl_util'),
       "TSF re-handle and ore loading plus extras for stemming, pads and clean-up", "ITT s6.2.11 (stockpile and reclaim), s6.2.13 (ore)",
       drive="wl", hrsk="whrs", op=True)
    S("B. DRILL AND BLAST")
    it("B1", "Production blasthole drill rig", "Epiroc D65 (client-specified)", CON, "units", lambda F: f"={SCH['drills']}", 1, 110, I('drill_avail'), I('drill_util'),
       "Peak metres drilled / effective rate per rig; one month ahead of mining; 80% of sand is free-dig so drilling starts with the blasted sand and cemented layer", "ITT s6.2.4 p243-245: Contractor selects drill fleet, patterns and powder factor",
       drive="drills", hrsk="dhrs", op=True)
    it("B2", "Pre-split / trim drill rig", "Smaller-diameter rig (ore only)", CON, "units", lambda F: f"={SCH['presplit']}", 1, 80, I('drill_avail'), I('drill_util'),
       "Pre-split required in ore only", "ITT s6.2.4 p244", drive="presplit", op=True)
    it("B3", "Bulk emulsion MPU / charging unit", "Mobile processing unit", CON, "units", lambda F: f"={SCH['mpu']}", 1, 25, I('mpu_avail'), I('mpu_util'),
       "Peak emulsion tonnes / charging rate", "ITT s6.2.4: bulk inhibited emulsion, electronic detonators", drive="mpu", hrsk="mhrs", op=True)
    it("B4", "Explosives delivery truck", "Magazine to pit", CON, "units", lambda F: f"={I('expl_trucks')}", 1, 30, I('supp_avail'), I('supp_util'), "Planner allowance", "ITT s5.6.5 p224-225", op=True)
    it("B5", "Blast vibration / airblast monitor", "Portable units", CON, "sets", lambda F: f"={I('blast_monitors')}", 3, 0, "1", "0", "Planner allowance", "ITT s6.2.4; Contractor responsible for vibration, airblast, flyrock")
    S("C. ROAD, DUMP AND PIT SUPPORT")
    it("C1", "Track-type dozer", "D10 / D375 class", CON, "units", lambda F: f"=ROUNDUP(ROUND({F['A1']}*{I('dump_dozer_ratio')},4),0)+ROUNDUP(ROUND({F['A2']}*{I('face_dozer_per_ex')},4),0)+{I('tsf_dozers')}",
       2, 100, I('supp_avail'), I('supp_util'), "Dump-face dozers per truck + dig-face dozers per excavator + TSF paddock spreading", "ITT s6.2.8-6.2.11", op=True)
    it("C2", "Wheel dozer", "~980 hp class", CON, "units", lambda F: f"={I('wheel_dozers')}", 3, 120, I('supp_avail'), I('supp_util'), "Stockpiles, sand and clean-up", "ITT s6.2.9", op=True)
    it("C3", "Motor grader", "24 ft / 16M class", CON, "units", lambda F: f"=ROUNDUP(({I('maint_km_perm')}+{I('maint_km_temp')})/{I('km_per_grader')},0)+{I('grader_extra')}",
       2, 80, I('supp_avail'), I('supp_util'), "17 km long-term roads + temporary roads, plus pit floor and TSF", "ITT s6.2.7 p247-248", op=True)
    it("C4", "Water cart", "~100 kL class", CON, "units", lambda F: f"=ROUNDUP(({I('maint_km_perm')}+{I('maint_km_temp')})/{I('km_per_cart')},0)+{I('cart_tsf')}",
       2, 120, I('supp_avail'), I('supp_util'), "Dust suppression on haul roads and moisture conditioning at TSF", "ITT s6.2.7, s14.7.5 p319", op=True)
    it("C5", "Padfoot / smooth drum compactor", "~20 t class", CON, "units", lambda F: f"={I('rollers')}", 3, 40, I('supp_avail'), I('supp_util'), "Zone 2B 300 mm lifts, ROM fill, stockpile bases", "ITT s6.2.9, s6.2.11", op=True)
    it("C6", "Impact roller", "High-energy, towed", CON, "units", lambda F: f"={I('impact_roller')}", 3, 40, I('supp_avail'), I('supp_util'), "TSF dune compaction", "ITT s6.3.3 p258", op=True)
    it("C7", "Medium excavator", "90 t class", CON, "units", lambda F: f"=MAX({I('med_ex')},{EWU['EXC']})", 1, 120, I('supp_avail'), I('supp_util'),
       "Larger of batters / ore harvest / drains and borrow-pit hours", "ITT s6.2.5, s6.2.6", op=True)
    it("C8", "Backhoe excavator", "Batter raking", CON, "units", lambda F: f"={I('backhoe')}", 6, 50, I('supp_avail'), I('supp_util'), "Batter raking", "ITT s6.2.6 p246", op=True)
    it("C9", "Ore / clean-up / stemming / borrow trucks", "90-100 t class", CON, "units", lambda F: f"=MAX({I('ore_trucks')},{EWU['TRK']})", 1, 160, I('supp_avail'), I('supp_util'),
       "Larger of ore / stemming haul and borrow, topsoil and clay hours", "ITT s6.2.4, s6.2.13", op=True)
    it("C10", "Mobile crushing and screening plant", "Pavement and stemming aggregate", CON, "units", lambda F: f"={I('crush_plant')}", 3, 120, I('supp_avail'), I('supp_util'),
       "Haul road wearing course and stemming material", "ITT s6.2.4, s6.2.10")
    S("D. EARTHWORKS AND CIVIL (early works)")
    it("D1", "Track-type dozer - clearing, topsoil, pads", "D8 / D9 class", CON, "units", lambda F: f"={EWU['DOZ']}", 1, 85, I('supp_avail'), I('ew_util'),
       "Peak early works hours from Earthworks; can transfer to pit support after M12", "ITT s6.1.3-6.1.4", op=True)
    it("D2", "Grout plant and pump", "Cement-bentonite-sand", CON, "units", lambda F: f"=MAX(1,{EWU['GRT']})", 3, 20, I('supp_avail'), I('ew_util'), "24 boreholes 66-304 m", "ITT s6.3.2 p257")
    it("D3", "HDPE liner deployment and welding set", "Wedge / extrusion welders", CON, "units", lambda F: f"={I('liner_sets')}", 15, 15, I('supp_avail'), I('supp_util'), "Lined stockpile bases and ponds", "ITT WA4 p234-235")
    S("E. DEWATERING")
    it("E1", "Diesel high-head pump set", "Skid-mounted", CON, "units", lambda F: f"={SCH['pumps']}", 2, 40, I('supp_avail'), I('supp_util'),
       "Base sump pumps, stepping up when the floor passes the ~50 m water table", "ITT s6.2.14 p254-255; no inflow data (R-25)", drive="pumps")
    it("E2", "Relocatable HDPE dewatering pipework", "Pipe string", CON, "km", lambda F: f"={I('pipe_km')}", 3, 0, "1", "0", "Transfer to Mine Dewatering Pond", "ITT s6.2.14; s7.2.7 p282 (in-pit piping)")
    S("F. ANCILLARY, SURVEY AND FMS")
    it("F1", "Fuel / lube tanker", "~20 kL", CON, "units",
       lambda F: f"=ROUNDUP(ROUND(Fuel!$C${{FUEL_LDAY}}*(1+{I('veh_fuel_allow')})/({I('tanker_cap')}*{I('fills_per_day')}),4),0)+{I('fuel_spare')}",
       1, 25, I('supp_avail'), I('supp_util'), "Peak daily diesel / (tanker capacity x fills per day) + spare", "ITT s5.4 p222: Contractor dispensing and refuelling")
    it("F2", "Service / lube truck", "Maintenance field service", CON, "units", lambda F: f"=ROUNDUP(ROUND({{HEAVY}}/{I('svc_units_per_truck')},4),0)", 2, 40, I('supp_avail'), I('supp_util'),
       "Heavy mobile units / units per service truck", "ITT s10.2.5 p304")
    it("F3", "Tyre handler", "260 t-class tyres", CON, "units", lambda F: f"={I('tyre_handlers')}", 2, 40, I('supp_avail'), I('supp_util'), "Tyre and rim management", "ITT s10.2.3; Rio Tinto Tyre and Rim Standard (Table 3)")
    it("F4", "Mobile crane", "50 t class", CON, "units", lambda F: f"={I('cranes')}", 1, 30, I('supp_avail'), I('supp_util'), "Equipment assembly area with crane pads", "ITT s5.6.4 p224")
    it("F5", "Telehandler", "", CON, "units", lambda F: f"={I('telehandlers')}", 1, 20, I('supp_avail'), I('supp_util'), "Workshop and field support", "")
    it("F6", "Float (prime mover and low loader)", "", CON, "units", lambda F: f"={I('floats')}", 1, 50, I('supp_avail'), I('supp_util'), "Moving tracked plant between work fronts", "ITT s10.2.5 p304")
    it("F7", "Lighting plant", "Diesel light tower", CON, "units", lambda F: f"=ROUNDUP(ROUND({F['A2']}*{I('lp_per_ex')}+{I('lp_dump')}+({F['B1']}+{F['B2']})*{I('lp_per_drill')},4),0)", 2, 3, "1", "1", "Per excavator, drill rig and dump / TSF area; 24 h operation", "ITT s10.2.5 p304")
    it("F8", "Light vehicle (mine-specification)", "4WD with full fit-out", CON, "units", lambda F: f"=ROUNDUP(ROUND({{HEADS}}*{I('lv_per_head')},4),0)", 1, 0, "1", "0", "Heads on site x vehicles per head; fuel in allowance", "ITT s10.3.3 p305; App C-1 s4.1-4.4 p454-455")
    it("F9", "Personnel bus", "", CON, "units", lambda F: f"=ROUNDUP(ROUND({{HEADS}}/{I('shifts_per_day')}/{I('bus_seats')},4),0)+1", 1, 0, "1", "0", "One shift per bus + spare", "ITT s10.3.2 p305")
    it("F10", "Ambulance / emergency response vehicle", "", CON, "units", lambda F: f"={I('amb')}", 1, 0, "1", "0", "Project Emergency Response Team support", "ITT s14.6 p315-316")
    it("F11", "Fire / rescue truck", "", CON, "units", lambda F: f"={I('fire')}", 1, 0, "1", "0", "", "ITT s14.6 p315-316")
    it("F12", "Wenco FMS on-board units", "Wenco or approved equivalent", CON, "sets", lambda F: f"={{HEAVY}}", 1, 0, "1", "0", "One per heavy mobile unit", "ITT s6.2.16 p255")
    it("F13", "FMS / radio mesh repeater trailer", "", CON, "sets", lambda F: f"={I('repeaters')}", 1, 0, "1", "0", "Temporary radio network, no TETRA (p227-228)", "ITT s6.2.16, s5.8.1")
    it("F14", "Survey: GNSS RTK rovers, base stations, total stations, UAV", "Authorised mine surveyor kit", CON, "sets", lambda F: "=3", 1, 0, "1", "0", "Initial survey 48 h; post-topsoil DTM within 7 days (p216)", "ITT s4.4 p215-216")
    S("G. TEMPORARY FACILITIES (not mobile equipment)")
    it("G1", "Temporary HME workshop bays", "Modular / hardstand", CON, "bays", lambda F: f"=ROUNDUP(ROUND({{HEAVY}}/{I('bays_per')},4),0)", 1, 0, "1", "0", "Until permanent MSA HME workshop (Milestone 8, 08/01/2029)", "ITT s5.6.2 p224; p055; R-30")
    it("G2", "Temporary fuel farm storage", "Self-bunded ASTs", CON, "kL", lambda F: f"=ROUNDUP(Fuel!$C${{FUEL_LDAY}}*{I('fuel_days')}/1000,0)", 1, 0, "1", "0", "Peak daily diesel x storage days; 110% bunding (App C-4 10.5.2)", "ITT s5.4 p222")
    it("G3", "Temporary explosives magazine and ANFO store", "", CON, "sets", lambda F: "=1", 1, 0, "1", "0", "Separate from the permanent Explosive Facility", "ITT s5.6.5 p224-225")
    it("G4", "Field laboratory (NATA)", "AS 1289 testing, Leco analysis", CON, "sets", lambda F: "=1", 1, 0, "1", "0", "", "ITT s4.7 p217")
    it("G5", "FMS server and network", "", CON, "sets", lambda F: "=1", 1, 0, "1", "0", "", "ITT s6.2.16 p255")

    FR = {}
    rr = 5
    for kind, d in items:
        if kind == "SEC":
            rr += 1
        else:
            FR[d["ref"]] = rr
        rr += 1 if kind == "ITEM" else 0
    # recompute properly: sections occupy a row
    FR = {}
    rr = 5
    for kind, d in items:
        if kind == "SEC":
            rr += 1
        else:
            FR[d["ref"]] = rr
            rr += 1
    FLAST = rr - 1
    selref = {k: f"$I${v}" for k, v in FR.items()}
    # heavy unit and head definitions (operated heavy units, section A-E)
    heavy_refs = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "D1"]
    HEAVY = "(" + "+".join(selref[k] for k in heavy_refs) + ")"
    op_refs = [d["ref"] for kind, d in items if kind == "ITEM" and d["op"]]
    OPS = "(" + "+".join(selref[k] for k in op_refs) + ")"
    HEADS = f"({OPS}*{I('shifts_per_day')}*{I('absent_factor')}*(1+{I('maint_ratio')}+{I('superv_ratio')}))"
    rr = 5
    FUEL_LDAY = None  # set after Fuel build; use placeholder in formulas and patch
    reg_late = []
    for kind, d in items:
        if kind == "SEC":
            band(wf, rr, d, 16)
            rr += 1
            continue
        wf.cell(row=rr, column=1, value=d["ref"])
        wf.cell(row=rr, column=2, value=d["ref"][0])
        wf.cell(row=rr, column=3, value=d["name"]).alignment = WRAP
        wf.cell(row=rr, column=4, value=d["model"]).alignment = WRAP
        wf.cell(row=rr, column=5, value=d["supply"])
        wf.cell(row=rr, column=6, value=d["unit"])
        f = d["calc"](selref).replace("{HEAVY}", HEAVY).replace("{HEADS}", HEADS)
        c = wf.cell(row=rr, column=7, value=f)
        c.number_format, c.fill = "#,##0", OUTF
        if "{FUEL_LDAY}" in f:
            reg_late.append((rr, f))
        o = wf.cell(row=rr, column=8)
        o.fill, o.font = INP, BLUE
        s = wf.cell(row=rr, column=9, value=f"=IF(ISNUMBER(H{rr}),H{rr},G{rr})")
        s.number_format, s.font = "#,##0", BOLD
        m = wf.cell(row=rr, column=10, value=d["mob"])
        m.fill, m.font = INP, BLUE
        k = wf.cell(row=rr, column=11, value=N)
        k.fill, k.font = INP, BLUE
        wf.cell(row=rr, column=12, value=f"={d['av']}" if d["av"] != "1" else 1).number_format = "0.00"
        wf.cell(row=rr, column=13, value=f"={d['ut']}" if d["ut"] != "0" else 0).number_format = "0.00"
        wf.cell(row=rr, column=14, value=d["lph"])
        wf.cell(row=rr, column=15, value=d["basis"]).alignment = WRAP
        wf.cell(row=rr, column=16, value=d["src"]).alignment = WRAP
        rr += 1
    for col, w in zip(range(1, 17), (6, 8, 38, 30, 26, 8, 11, 10, 10, 10, 8, 7, 7, 9, 60, 55)):
        wf.column_dimensions[CL(col)].width = w
    wf.freeze_panes = "D5"
    # totals block
    tr = FLAST + 2
    band(wf, tr, "TOTALS", 16)
    wf.cell(row=tr + 1, column=3, value="Heavy mobile units (operated, sections A-D)")
    wf.cell(row=tr + 1, column=9, value=f"={HEAVY}").font = BOLD
    wf.cell(row=tr + 2, column=3, value="Company free-issue (assumed) units")
    wf.cell(row=tr + 2, column=9, value=f"=SUMIF($E$5:$E${FLAST},\"{FREE}\",$I$5:$I${FLAST})").font = BOLD
    wf.cell(row=tr + 3, column=3, value="Contractor-supplied vehicles and mobile plant (units)")
    wf.cell(row=tr + 3, column=9, value=f"=SUMIFS($I$5:$I${FLAST},$E$5:$E${FLAST},\"{CON}\",$F$5:$F${FLAST},\"units\")").font = BOLD
    wf.cell(row=tr + 4, column=3, value="Indicative heads on site at one time (operators + maintenance + supervision)")
    wf.cell(row=tr + 4, column=9, value=f"={HEADS}").font = BOLD
    wf.cell(row=tr + 4, column=15, value="Order-of-magnitude only; the ITT gives no workforce numbers (Schedule C blank)")
    TOT = {"heavy": f"Fleet_Register!$I${tr + 1}", "free": f"Fleet_Register!$I${tr + 2}", "con": f"Fleet_Register!$I${tr + 3}", "heads": f"Fleet_Register!$I${tr + 4}"}

    # ------------------------------------------------------------------ Fleet_Ramp
    wr = wb.create_sheet("Fleet_Ramp")
    title(wr, "Equipment on site by month",
          "Primary equipment follows the monthly requirement from Schedule (never demobilised early); other items are on site between Mobilise M# and Last M# on Fleet_Register.")
    hdr(wr, 4, ["Ref", "Equipment", "Selected qty"] + [""] * N, height=22)
    RC = 4
    rcl = lambda t: CL(RC + t - 1)  # noqa: E731
    for t in range(1, N + 1):
        c = wr.cell(row=3, column=RC + t - 1, value=t)
        c.font = Font(color="808080", size=8)
        c.alignment = Alignment(horizontal="center")
        h = wr.cell(row=4, column=RC + t - 1, value=f"={SCHM('date', t)}")
        h.number_format, h.font, h.fill = "mmm-yy", WHITE, HEAD
    rr = 5
    for kind, d in items:
        if kind == "SEC":
            band(wr, rr, d, RC + N - 1)
            rr += 1
            continue
        wr.cell(row=rr, column=1, value=f"=Fleet_Register!A{rr}")
        wr.cell(row=rr, column=2, value=f"=Fleet_Register!C{rr}")
        wr.cell(row=rr, column=3, value=f"=Fleet_Register!I{rr}").font = BOLD
        for t in range(1, N + 1):
            c_ = rcl(t)
            inwin = f"AND({c_}$3>=Fleet_Register!$J{rr},{c_}$3<=Fleet_Register!$K{rr})"
            if d["drive"]:
                req = SCHM(d["drive"], t)
                pv = f"{rcl(t - 1)}{rr}" if t > 1 else "0"
                f = f"=IF({c_}$3>Fleet_Register!$K{rr},0,MIN($C{rr},MAX({pv},{req})))"
            else:
                f = f"=IF({inwin},$C{rr},0)"
            wr.cell(row=rr, column=RC + t - 1, value=f).number_format = "0"
        rr += 1
    sumrow = FLAST + 2
    band(wr, sumrow, "TOTALS", RC + N - 1)
    wr.cell(row=sumrow + 1, column=2, value="Heavy mobile units on site (A-D)")
    wr.cell(row=sumrow + 2, column=2, value="Trucks on site vs required (check = on site - required)")
    for t in range(1, N + 1):
        c_ = rcl(t)
        hv = "+".join(f"{c_}{FR[k]}" for k in heavy_refs)
        wr.cell(row=sumrow + 1, column=RC + t - 1, value=f"={hv}").number_format = "0"
        wr.cell(row=sumrow + 2, column=RC + t - 1, value=f"={c_}{FR['A1']}-{SCHM('trucks', t)}").number_format = "0"
    wr.column_dimensions["A"].width = 6
    wr.column_dimensions["B"].width = 46
    wr.column_dimensions["C"].width = 10
    for t in range(1, N + 1):
        wr.column_dimensions[rcl(t)].width = 8
    wr.freeze_panes = wr.cell(row=5, column=RC)

    # ------------------------------------------------------------------ Fuel
    wu = wb.create_sheet("Fuel")
    title(wu, "Diesel demand profile (order of magnitude)",
          "Supports Schedule A.9 (Contractor forecast litres, 24-month profile). Primary equipment uses the engine hours from Schedule; other items use on-site units x scheduled hours x availability x utilisation x L/h. L/h figures are planning assumptions, not OEM data.")
    hdr(wu, 4, ["Ref", "Equipment", "Total litres"] + [""] * N, height=22)
    UC = 4
    ucl = lambda t: CL(UC + t - 1)  # noqa: E731
    for t in range(1, N + 1):
        h = wu.cell(row=4, column=UC + t - 1, value=f"={SCHM('date', t)}")
        h.number_format, h.font, h.fill = "mmm-yy", WHITE, HEAD
    rr = 5
    first_burn = None
    last_burn_AE = None
    for kind, d in items:
        if kind == "SEC":
            band(wu, rr, d, UC + N - 1)
            rr += 1
            continue
        wu.cell(row=rr, column=1, value=f"=Fleet_Register!A{rr}")
        wu.cell(row=rr, column=2, value=f"=Fleet_Register!C{rr}")
        for t in range(1, N + 1):
            if d["hrsk"]:
                f = f"={SCHM(d['hrsk'], t)}*Fleet_Register!$N{rr}"
            elif d["lph"]:
                f = (f"=Fleet_Ramp!{rcl(t)}{rr}*{SCHM('hrs', t)}*Fleet_Register!$L{rr}*Fleet_Register!$M{rr}*Fleet_Register!$N{rr}"
                     f"*IF({SCHM('vol', t)}>0,1,{I('fuel_idle')})")
            else:
                f = 0
            wu.cell(row=rr, column=UC + t - 1, value=f).number_format = "#,##0"
        wu.cell(row=rr, column=3, value=f"=SUM({ucl(1)}{rr}:{ucl(N)}{rr})").number_format = "#,##0"
        if d["ref"][0] in "ABCDE":
            last_burn_AE = rr
        rr += 1
    ftot = FLAST + 2
    band(wu, ftot, "TOTALS", UC + N - 1)
    LBL = {1: "Diesel - HME and plant (sections A-E), L", 2: "Diesel - ancillary vehicles (section F), L", 3: "Light vehicles and buses allowance, L",
           4: "Total diesel, L", 5: "Total diesel, ML", 6: "HME and plant incl. allowance, L per calendar day"}
    for k, v in LBL.items():
        wu.cell(row=ftot + k, column=2, value=v).font = BOLD
    ae_first, ae_last = 5, last_burn_AE
    f_first, f_last = FR["F1"], FR["F14"]
    for t in range(1, N + 1):
        c_ = ucl(t)
        wu.cell(row=ftot + 1, column=UC + t - 1, value=f"=SUM({c_}{ae_first}:{c_}{ae_last})").number_format = "#,##0"
        wu.cell(row=ftot + 2, column=UC + t - 1, value=f"=SUM({c_}{f_first}:{c_}{f_last})").number_format = "#,##0"
        wu.cell(row=ftot + 3, column=UC + t - 1, value=f"={c_}{ftot + 1}*{I('veh_fuel_allow')}").number_format = "#,##0"
        wu.cell(row=ftot + 4, column=UC + t - 1, value=f"={c_}{ftot + 1}+{c_}{ftot + 2}+{c_}{ftot + 3}").number_format = "#,##0"
        wu.cell(row=ftot + 5, column=UC + t - 1, value=f"={c_}{ftot + 4}/1000000").number_format = "0.00"
        wu.cell(row=ftot + 6, column=UC + t - 1, value=f"={c_}{ftot + 1}*(1+{I('veh_fuel_allow')})/{SCHM('days', t)}").number_format = "#,##0"
    for k in range(1, 6):
        wu.cell(row=ftot + k, column=3, value=f"=SUM({ucl(1)}{ftot + k}:{ucl(N)}{ftot + k})").number_format = "#,##0.0" if k == 5 else "#,##0"
    wu.cell(row=ftot + 6, column=3, value=f"=MAX({ucl(1)}{ftot + 6}:{ucl(N)}{ftot + 6})").number_format = "#,##0"
    FUEL_LDAY = ftot + 6
    wu.column_dimensions["A"].width = 6
    wu.column_dimensions["B"].width = 46
    wu.column_dimensions["C"].width = 14
    for t in range(1, N + 1):
        wu.column_dimensions[ucl(t)].width = 11
    wu.freeze_panes = wu.cell(row=5, column=UC)
    for rr_, f in reg_late:
        wf.cell(row=rr_, column=7, value=f.replace("{FUEL_LDAY}", str(FUEL_LDAY)))
    TOTL = f"Fuel!$C${ftot + 5}"
    PEAKL = f"Fuel!$C${ftot + 6}"

    # ------------------------------------------------------------------ Gantt
    wg = wb.create_sheet("Gantt")
    title(wg, "Programme - first 24 months",
          "Blue bars = calculated windows (change inputs and they move). Diamonds mark contract dates. Start / Finish are month numbers (M1 = Dec 2027).")
    GC = 8
    gcl = lambda t: CL(GC + t - 1)  # noqa: E731
    hdr(wg, 4, ["Ref", "Activity", "Start M#", "Finish M#", "Months", "Start date", "Finish date"] + [""] * N, height=22)
    wg.cell(row=3, column=7, value="Month #").font = Font(color="808080", size=8)
    for t in range(1, N + 1):
        c = wg.cell(row=3, column=GC + t - 1, value=t)
        c.font = Font(color="808080", size=8)
        c.alignment = Alignment(horizontal="center")
        h = wg.cell(row=4, column=GC + t - 1, value=f"={SCHM('date', t)}")
        h.number_format, h.font, h.fill = "mmm-yy", WHITE, HEAD
        h.alignment = Alignment(horizontal="center", text_rotation=90)
    wg.row_dimensions[4].height = 42

    def mi(datecell):
        return f"MAX(1,(YEAR({datecell})-YEAR({I('start_date')}))*12+MONTH({datecell})-MONTH({I('start_date')})+1)"

    cumv = SCHR("cum")
    EWS = lambda e: f"Earthworks!$F${EWR[e]}"  # noqa: E731
    EWF = lambda e: f"Earthworks!$G${EWR[e]}"  # noqa: E731
    G = [
        ("SEC", "CONTRACT DATES (WIN-CON-EPC-001)"),
        ("MS", "K1", "Site Access Date 23/11/2027", f"={mi(I('site_access_date'))}"),
        ("MS", "K2", "Concrete Milestone 1 - Flotation and Regrind 11/10/2028", f"={mi('DATE(2028,10,11)')}"),
        ("MS", "K3", "Milestone 3 - Ore Crushing Concrete 25/10/2028 (ROM pad needed)", f"={mi('DATE(2028,10,25)')}"),
        ("MS", "K4", "Milestone 8 - MSA Bulk Concrete incl. HME workshop 08/01/2029", f"={mi('DATE(2029,1,8)')}"),
        ("MS", "K5", "Milestone 9 - Oversized Crushing Concrete 15/01/2029", f"={mi('DATE(2029,1,15)')}"),
        ("MS", "K6", "Completion - Works, SP1 and SP2 30/11/2029", f"={mi('DATE(2029,11,30)')}"),
        ("SEC", "ESTABLISHMENT AND EARLY WORKS"),
        ("BAR", "P1", "Mobilise, free-issue HME go-line acceptance, FMS and radio network", f"={EWS('EW-01')}", f"=Earthworks!$G${EWR['EW-01']}"),
        ("BAR", "P2", "Temporary facilities: workshop, fuel farm, magazine, field lab, laydown", f"={EWS('EW-01')}", f"={EWF('EW-01')}"),
        ("BAR", "P3", "Clear and topsoil - haul road corridors", f"={EWS('EW-02')}", f"={EWF('EW-02')}"),
        ("BAR", "P4", "Clear and topsoil - pit cutbacks 1-2", f"={EWS('EW-03')}", f"={EWF('EW-03')}"),
        ("BAR", "P5", "Clear and topsoil - WRL footprint (progressive)", f"={EWS('EW-04')}", f"={EWF('EW-04')}"),
        ("BAR", "P6", "Clear and topsoil - ROM pad and stockpile footprints", f"={EWS('EW-05')}", f"={EWF('EW-05')}"),
        ("BAR", "P7", "TSF Stage 0 clearing and dune foundation preparation", f"={EWS('EW-06')}", f"={EWF('EW-06')}"),
        ("BAR", "P8", "TSF borehole backfill (24 boreholes)", f"={EWS('EW-07')}", f"={EWF('EW-07')}"),
        ("BAR", "P9", "Borrow pit - initial haul road and hardstand material", f"={EWS('EW-08')}", f"={EWF('EW-08')}"),
        ("SEC", "PRE-STRIP MINING (21.6 Mbcm)"),
        ("BAR", "M1", "Pre-strip production (all layers)", f"=COUNTIF({cumv},\"<0.5\")+1", f"=MIN({N},COUNTIF({cumv},\"<\"&({I('vol_total')}-0.5))+1)"),
        ("BAR", "M2", "Layer A - aeolian sands 0-15 m (free-dig and blasted)", f"=COUNTIF({cumv},\"<0.5\")+1", f"=MIN({N},COUNTIF({cumv},\"<\"&({Q('vol_A')}-0.5))+1)"),
        ("BAR", "M3", "Layer B - cemented sand / sandstone / regolith 15-50 m", f"=MIN({N},COUNTIF({cumv},\"<=\"&{Q('vol_A')})+1)", f"=MIN({N},COUNTIF({cumv},\"<\"&({Q('vol_A')}+{Q('vol_B')}-0.5))+1)"),
        ("BAR", "M4", "Layer C - mudstone / leach cap 50-70 m", f"=MIN({N},COUNTIF({cumv},\"<=\"&({Q('vol_A')}+{Q('vol_B')}))+1)", f"=MIN({N},COUNTIF({cumv},\"<\"&({I('vol_total')}-0.5))+1)"),
        ("BAR", "M5", "Drill and blast - Epiroc D65 (one month ahead)", f"=COUNTIF({SCHR('cumM')},\"<0.5\")+1", f"=MIN({N},COUNTIF({SCHR('cumM')},\"<\"&({SCH['metres']}-0.5))+1)"),
        ("BAR", "M6", "Ore recovery to stockpile (600 kt)", f"={EWS('EW-17')}", f"={EWF('EW-17')}"),
        ("BAR", "M7", "Pit dewatering below the ~50 m water table", f"={EWS('EW-18')}", f"={EWF('EW-18')}"),
        ("SEC", "EARTHWORKS FED FROM THE PIT"),
        ("BAR", "E1", "Haul roads 17 km (priority 1)", f"={EWS('EW-09')}", f"={EWF('EW-09')}"),
        ("BAR", "E2", "ROM pad, crusher skyway, stockpile fingers (priority 2)", f"={EWS('EW-10')}", f"={EWF('EW-10')}"),
        ("BAR", "E3", "Ponds, bunds, drains, pads (priority 3)", f"={EWS('EW-11')}", f"={EWF('EW-11')}"),
        ("BAR", "E4", "Stockpile bases - granular (priority 4)", f"={EWS('EW-12')}", f"={EWF('EW-12')}"),
        ("BAR", "E5", "Stockpile bases - clayey mudstone liner", f"={EWS('EW-13')}", f"={EWF('EW-13')}"),
        ("BAR", "E6", "HDPE liner installation", f"={EWS('EW-14')}", f"={EWF('EW-14')}"),
        ("BAR", "E7", "TSF Stage 0 embankment and dune fill", f"={EWS('EW-15')}", f"={EWF('EW-15')}"),
        ("BAR", "E8", "Waste rock landform construction", f"={EWS('EW-16')}", f"={EWF('EW-16')}"),
        ("SEC", "CLOSE-OUT"),
        ("BAR", "Z1", "Rehabilitation, final clean-up, demobilisation", f"={EWS('EW-19')}", f"={EWF('EW-19')}"),
        ("BAR", "Z2", "Float to Completion Date (30/11/2029)", f"=MIN({N},COUNTIF({cumv},\"<\"&({I('vol_total')}-0.5))+2)", f"={N}"),
    ]
    rr = 5
    GR = {}
    for g in G:
        if g[0] == "SEC":
            band(wg, rr, g[1], GC + N - 1)
            rr += 1
            continue
        kind, ref, name = g[0], g[1], g[2]
        GR[ref] = rr
        wg.cell(row=rr, column=1, value=ref)
        wg.cell(row=rr, column=2, value=name)
        if kind == "MS":
            wg.cell(row=rr, column=3, value=g[3])
            wg.cell(row=rr, column=4, value=f"=C{rr}")
        else:
            wg.cell(row=rr, column=3, value=g[3])
            wg.cell(row=rr, column=4, value=g[4])
        wg.cell(row=rr, column=5, value=f"=D{rr}-C{rr}+1")
        wg.cell(row=rr, column=6, value=f"=INDEX({SCHR('date')},C{rr})").number_format = "mmm-yy"
        wg.cell(row=rr, column=7, value=f"=INDEX({SCHR('date')},D{rr})").number_format = "mmm-yy"
        for t in range(1, N + 1):
            c_ = gcl(t)
            if kind == "MS":
                f = f"=IF({c_}$3=$C{rr},\"◆\",\"\")"
            else:
                f = f"=IF(AND({c_}$3>=$C{rr},{c_}$3<=$D{rr}),1,\"\")"
            cell = wg.cell(row=rr, column=GC + t - 1, value=f)
            cell.alignment = Alignment(horizontal="center")
            if kind == "MS":
                cell.font = Font(color="C00000", bold=True)
            else:
                cell.number_format = ";;;"
        rr += 1
    GLAST = rr - 1
    rng = f"{gcl(1)}5:{gcl(N)}{GLAST}"
    # conditional-format fills are read from bgColor, so set both or Excel draws no bar
    wg.conditional_formatting.add(rng, FormulaRule(formula=[f"{gcl(1)}5=1"], fill=PatternFill("solid", bgColor="2F75B5", fgColor="2F75B5"), font=Font(color="2F75B5")))
    wg.column_dimensions["A"].width = 6
    wg.column_dimensions["B"].width = 66
    for col in "CDE":
        wg.column_dimensions[col].width = 9
    wg.column_dimensions["F"].width = 9
    wg.column_dimensions["G"].width = 9
    for t in range(1, N + 1):
        wg.column_dimensions[gcl(t)].width = 5
    wg.freeze_panes = wg.cell(row=5, column=GC)

    # ------------------------------------------------------------------ Checks
    wc = wb.create_sheet("Checks")
    title(wc, "Checks", "Every row should read OK. CHECK means the plan or an override breaks a constraint.")
    hdr(wc, 4, ["Check", "Value", "Limit / target", "Status", "What it means"])
    ck = []

    def chk(label, val, target, test, note, fmt="#,##0", info=False):
        ck.append((label, val, target, test, note, fmt, info))

    last_month = f"MATCH(2,1/({SCHR('vol')}>0))"
    chk("Pre-strip mined = ITT volume", f"={SCH['vol']}", f"={I('vol_total')}", "ABS(B{r}-C{r})<1", "Monthly volumes sum to 21.6 Mbcm")
    chk("Layers A + B + C = pre-strip mined", f"={SCH['A']}+{SCH['B']}+{SCH['C']}", f"={SCH['vol']}", "ABS(B{r}-C{r})<1", "Stratigraphy fully consumed")
    chk("Destinations sum to pre-strip mined", f"={SCH['infra']}+{SCH['tsf']}+{SCH['wrl']}", f"={SCH['vol']}", "ABS(B{r}-C{r})<1", "Infrastructure + TSF + WRL")
    chk("TSF Stage 0 volume delivered", f"={SCH['tsf']}", f"={I('tsf_tot')}", "ABS(B{r}-C{r})<1", "Monthly TSF cap is high enough to deliver the Stage 0 quantity")
    chk("Infrastructure fill (layers A + B) delivered", f"={SCH['infraAB']}", f"={Q('infra_AB')}", "ABS(B{r}-C{r})<1", "Roads, ROM, bunds and stockpile bases all built")
    chk("Clay liner delivered", f"={SCH['infraC']}", f"={Q('clay')}", "ABS(B{r}-C{r})<1", "Layer C mudstone available for stockpile bases")
    chk("Ore delivered", f"={SCH['ore']}", f"={I('ore_tot')}", "ABS(B{r}-C{r})<1", "600 kt to stockpile")
    chk("Last production month <= Completion month - 1", f"=Gantt!$D${GR['M1']}", f"={N - 1}", "B{r}<=C{r}", "Leaves at least one month for rehabilitation and demobilisation before 30/11/2029", "0")
    chk("ROM pad (EW-10) complete before Milestone 3 (25/10/2028)", f"=Gantt!$D${GR['E2']}", f"=Gantt!$C${GR['K3']}-1", "B{r}<=C{r}", "ROM pad and crusher skyway ready the month before the Ore Crushing concrete milestone", "0")
    chk("Haul roads (EW-09) complete before ROM pad starts", f"=Gantt!$D${GR['E1']}", f"=Gantt!$C${GR['E2']}", "B{r}<=C{r}", "Priority 1 before priority 2 (overlap in the changeover month is allowed)", "0")
    chk("Clay liner (EW-13) starts before ore starts", f"=Gantt!$C${GR['E5']}", f"=Gantt!$C${GR['M6']}", "B{r}<=C{r}", "Stockpile base ready for first ore", "0")
    chk("TSF fill starts after TSF foundation prep finishes", f"=Gantt!$C${GR['E7']}", f"=Gantt!$D${GR['P7']}", "B{r}>C{r}", "Foundation (clearing, dune compaction) ahead of Zone 4A fill", "0")
    chk("Dewatering in place when floor passes water table", f"=Gantt!$C${GR['M7']}", f"=COUNTIF({SCHR('wtfl')},\"=0\")+1", "B{r}<=C{r}", "Pumps ready in the month the floor reaches ~50 m", "0")
    chk("TSF Stage 0 capacity at monthly cap", f"={Q('tsf_cap_ok')}", f"={I('tsf_tot')}", "B{r}>=C{r}", "Cap on TSF share does not block delivery")
    chk("Waste rock landform balance is positive", f"={Q('d_wrl')}", 0, "B{r}>0", "TSF + infrastructure do not exceed the pre-strip")
    chk("Infrastructure supply from A + B is positive", f"={Q('infra_AB')}", 0, "B{r}>0", "Clay liner does not exceed infrastructure demand")
    chk("Trucks on site cover the monthly requirement (min over months)", f"=MIN(Fleet_Ramp!$D${sumrow + 2}:${rcl(N)}${sumrow + 2})", 0, "B{r}>=C{r}", "Selected / override truck quantity is enough every month (negative = shortfall)", "0")
    chk("Selected excavators >= peak requirement", f"=Fleet_Register!$I${FR['A2']}", f"={SCH['exc']}", "B{r}>=C{r}", "", "0")
    chk("Selected drills >= peak requirement", f"=Fleet_Register!$I${FR['B1']}", f"={SCH['drills']}", "B{r}>=C{r}", "", "0")
    chk("Disturbance within ITT ~170 ha (information)", f"={Q('ha_tot')}", f"={I('itt_footprint_ha')}", "B{r}<=C{r}", "Information only. Clearing areas are assumptions; the total here is well above the ITT figure, mainly the 17 km road corridor and the WRL footprint", "#,##0", info=True)
    chk("Fill balance: cumulative infrastructure supply >= demand to date", f"={SCH['infraAB']}", f"={Q('infra_AB')}", "ABS(B{r}-C{r})<1", "Same as infrastructure delivered")
    for i, (label, val, target, test, note, fmt, info) in enumerate(ck):
        r_ = 5 + i
        wc.cell(row=r_, column=1, value=label)
        a = wc.cell(row=r_, column=2, value=val)
        a.number_format = fmt
        b = wc.cell(row=r_, column=3, value=target)
        b.number_format = fmt
        wc.cell(row=r_, column=4, value=(f"=IF({test.format(r=r_)},\"OK\",\"INFO\")" if info else f"=IF({test.format(r=r_)},\"OK\",\"CHECK\")")).font = BOLD
        wc.cell(row=r_, column=5, value=note).alignment = WRAP
    last = 5 + len(ck) - 1
    wc.cell(row=last + 2, column=1, value="OVERALL").font = BOLD
    wc.cell(row=last + 2, column=4, value=f"=IF(COUNTIF(D5:D{last},\"CHECK\")=0,\"ALL OK\",\"REVIEW\")").font = BOLD
    wc.conditional_formatting.add(f"D5:D{last + 2}", CellIsRule(operator="equal", formula=['"CHECK"'], fill=PatternFill("solid", bgColor="F8CBAD", fgColor="F8CBAD")))
    wc.conditional_formatting.add(f"D5:D{last + 2}", CellIsRule(operator="equal", formula=['"REVIEW"'], fill=PatternFill("solid", bgColor="F8CBAD", fgColor="F8CBAD")))
    wc.conditional_formatting.add(f"D5:D{last + 2}", CellIsRule(operator="equal", formula=['"OK"'], fill=PatternFill("solid", bgColor="C6EFCE", fgColor="C6EFCE")))
    wc.conditional_formatting.add(f"D5:D{last + 2}", CellIsRule(operator="equal", formula=['"ALL OK"'], fill=PatternFill("solid", bgColor="C6EFCE", fgColor="C6EFCE")))
    for col, w in zip("ABCDE", (64, 16, 16, 10, 90)):
        wc.column_dimensions[col].width = w
    CHECK_OVERALL = f"Checks!$D${last + 2}"

    # ------------------------------------------------------------------ Assumptions log
    wa = wb.create_sheet("Assumptions_Log")
    title(wa, "Assumptions, gaps and open items",
          "What the ITT does not give, what was assumed instead, and what would replace it. Register references (R-xx, Q-xx) are from WIN-CON-EPC-001_Mining_Review.html.")
    hdr(wa, 4, ["#", "Topic", "ITT position", "Assumption used in this workbook", "Impact on schedule / fleet", "Replace with", "Review ref"], height=32)
    log = [
        ("Start and duration", "Site Access 23/11/2027; Completion 30/11/2029; no pre-strip duration, rate or Contract Production Requirements (p054-055, p242).", "M1 = Dec 2027. Production runs M2 to M22 at a ramped 1.25 Mbcm/month full rate, leaving M23-M24 for close-out.", "HIGH - the full rate sets the whole fleet. The SOW January 2027 start and the Commencement end Q1 2027 are not used.", "Contract Production Requirements and Three Month Production Plan", "R-07, R-24, Q-02, Q-04"),
        ("Production dates vs process-plant milestones", "Nine concrete milestones 11/10/2028 to 15/01/2029; ROM / crusher pad and TSF Stage 0 needed by then.", "ROM pad forced early by the infrastructure build order (haul roads, ROM, ponds, stockpile bases).", "MEDIUM - front-loads infrastructure fill in M3-M9.", "Mass-Haul Plan - Site Wide Bulk Earthworks; Process Area work-front dates", "R-29"),
        ("Free-issue fleet", "XCMG HME is Company free-issue; list C-WN-0000-G-LST-00005 not supplied; Contractor carries availability risk (p302-306).", "Trucks XDE260-class 260 t, 700 t-class excavators, 20 m3 wheel loaders, all marked free-issue (assumed).", "HIGH - the free-issue list may be smaller or larger than the calculated fleet. Any shortfall is Contractor-supplied.", "Client Supplied Fleet List", "R-23, Q-18"),
        ("Epiroc D65", "Contractor selects drill fleet, hole diameters, patterns and powder factor (p243-245).", "D65 per instruction; ~200 mm hole; 11 m single pass; penetration 28-38 m/h net; pattern areas 28-32 m2; 80% efficiency.", "MEDIUM - drill count scales directly with penetration rate and pattern area.", "Drill and Blast Review C0007-REF-00339; Epiroc data; site trial", "R-61, Q-10"),
        ("Material strength / blasting", "~80% of the 0-15 m sand is free-dig; everything beneath is blasted (p244-245). No UCS or density.", "Densities, swell factors and powder factors carried from winu-prestrip-fleet.", "MEDIUM - drives payload, powder factor and drill metres.", "Geotechnical and Pit Materials Assessment reports", "R-16, Q-07"),
        ("Haul distances and ramp", "No haul profile, ramp gradient, payload or destination volumes (p246, p252).", "WRL 4.0 km, infrastructure 3.5 km surface lead; TSF 4.9 km (WRL boundary + ~0.9 km volume-weighted centroid from the TSF Yearly Development); 10% ramp; 0.6 km in-pit flat.", "HIGH - the truck count is very sensitive to lead distance.", "Haul Infinity model C0007-REF-00340; WRL and ROM DXF layouts", "R-60, Q-08, Q-09"),
        ("Destination volumes", "Pre-strip MTO and Bulk Earthworks MTO not supplied.", "TSF Stage 0 6.0 Mbcm (limit of sand + regolith in the upper ~20 m); haul roads from 17 km x 40 m x 1.0 m; ROM 1.0 Mbcm; ponds / bunds 0.3 Mbcm; stockpile bases 35 ha; WRL is the balance.", "HIGH for TSF and WRL timing.", "Prestrip MTO C0007-REF-00325; TSF MTO C-WN-2300-Y-MTO-00001", "R-24, Q-08"),
        ("TSF Stage 0 fill volume", "Years 2-3 = Stage 0 (p257).", "TSF Yearly Development (C0007-2300-G-PRE-00002 Rev A, 31/07/2026) shows 8.42 Mm3 for Years 2-3 against 6.0 Mbcm supplied from the pre-strip here. About 2.4 Mm3 has no source in this plan.", "HIGH - extra borrow, processed sand or crushed rock, or later pre-strip. Moves haul and fleet.", "Prestrip MTO; TSF MTO; confirm what is placed by the pre-strip rate vs the TSF rate (R-50)", "R-49, R-50"),
        ("Pit stratigraphy", "0-15 m aeolian sand (~80% free-dig), 15-50 m cemented sand / sandstone, 50-70 m mudstone / leach cap (p245).", "ITT column used as the contract basis.", "HIGH - Pit Materials Assessment (C0007-0300-C-REP-00011 Table 9) logs aeolian sand 18-32 m (mean ~27 m), sandstone to 46-63 m, mudstone 47-92 m. A 27 m sand layer raises the free-dig share and cuts drilling. Set depth_sand = 27 on Inputs to test.", "Pit Materials Assessment; Reliance Information schedule", "R-16, Q-07"),
        ("Rock strength", "Not given in the ITT.", "Pit Materials Assessment: sandstone UCS 8.3-24.7 MPa, mudstone UCS ~10 MPa, leach cap 1.6-21.4 MPa. Supports blasting of all material below the sand and D65 penetration of 28-38 m/h.", "LOW - consistent with the penetration rates used.", "Drill and Blast Review C0007-REF-00339", "-"),
        ("Pit wall stand-off", "Pit slope design is Company scope (p216).", "Golder 19135779-017: 100 m stand-off from the pit crest to infrastructure (DAC 1.5). Cutback 1-2 footprint here is a 60 ha assumption; roads, ROM pad and WRL must sit outside the stand-off.", "MEDIUM - lengthens haul leads if the pit crest pushes infrastructure outward.", "Pit Designs - Cutbacks C0007-REF-00341", "R-60"),
        ("Where the ore sits", "First ~600 kt of ore to stockpiles; ore bench 5 m; 100% of plan ore and >=30% of ore in the overburden zone (p245, p254).", "Ore harvested in the lower 60% of the 50-70 m mudstone / leach cap layer.", "LOW for fleet; MEDIUM for stockpile base timing.", "Mine Plan Extract C0007-REF-00321; pit designs", "R-51, Q-11"),
        ("Water table and dewatering", "Water table ~50 m bgl, pit floor ~70 m; Contractor dewatering with no inflow, bore or permeability data (p240, p254).", "Hydrogeology (311012-01475-REP-HG-032): water table 50-60 m bgl at the base of the unconfined sandstone; sandstone / mudstone inflow negligible; bore dewatering 7 bores x 17.8 L/s in Year 1 and 8 x 20 L/s in Years 2-3 (bores by others, SOW buried utilities). Here: 2 sump pumps above the water table, 6 pump sets and 4 km pipework below 50 m for storm and seepage.", "LOW-MEDIUM - sump scope looks small, but bore dewatering must be commissioned ahead of Cutback 1 and existing bores inside it decommissioned.", "Worley HG-032 Tables 9-6 to 9-9; dewatering bore installation programme", "R-25, Q-13"),
        ("Water balance start date", "Site Access 23/11/2027.", "Advisian TM-001 (20/04/2023) models mining start May 2028 and processing May 2030. This plan starts pit production Jan 2028.", "MEDIUM - the water balance assumes about four months less dewatering lead time than this schedule.", "Updated Winu water balance (311012-01475-REP-WB-039)", "R-07"),
        ("Borrow", "Borrow Pit Management Plan not supplied.", "Mine Site Borrow Areas MSBA01-03 are suitable laterite gravel for roads (C0007-0300-C-REP-00042). The 0.2 Mbcm borrow pit is assumed to come from one of these. Aeolian sand carries ~15% fines (>5% sand-fill limit) and Emerson class 2-6 (possible dispersion).", "LOW for schedule; MEDIUM for TSF filter and select fill quality.", "Borrow Pit Management Plan; MSBA01-03 test pit logs", "Q-45"),
        ("Weather", "Only floods worse than 1 in 100 year and cyclones relieve time (p077, p136).", "Weather days lost per calendar month from winu-prestrip-fleet (Jan 3, Feb 3, Mar 2, Apr 0.5, Nov 0.5, Dec 1).", "MEDIUM - the first wet season Jan-Mar 2028 falls during ramp-up.", "Site rainfall record; ITT weather allowance", "R-35, Q-06"),
        ("Operating pattern", "Normal working hours 06:00-18:00, 11.5 h/day, 80.5 h/week; roster 14 on / 7 off (p354-355).", "Mining runs 24 h in two 12 h shifts, 7 days. Overtime / extended hours need Company approval (App C-2).", "MEDIUM - a 12 h-only mining day would roughly double the fleet.", "Confirm 24 h operation is allowed", "-"),
        ("Borrow pit and initial roads", "Borrow Pit Management Plan C0007-0800-C-PLN-00001 not supplied (p240).", "0.2 Mbcm borrow pit, M2-M4, to build the first roads before the pit reaches cemented rock.", "LOW", "Borrow Pit Management Plan; Haul Road Info as of May 2026", "Q-45"),
        ("Disturbance areas and topsoil", "~170 ha disturbance footprint (p210); topsoil 100 mm general, 200 mm TSF; pit and WRL depth garbled (p240).", "Pit 60 ha, WRL from volume / 25 m, haul road corridor 85 ha (17 km x 50 m), ROM and stockpiles 47 ha, TSF 40 ha, facilities 12 ha. Clearing 0.2 ha/h per dozer.", "LOW for fleet; the total cleared area is about 1.8x the ITT ~170 ha (Checks, information only).", "Disturbance Footprint 20260429 C0007-REF-00323; Soil Management Procedure", "R-48, Q-12"),
        ("Scope not in this schedule", "SP1 also includes Mine Access Road (182 km), Village, MPP / MSA pads, Aerodrome, power station and buried utilities (p230-239, p265).", "Not included. They need their own civil fleet and programme.", "HIGH if the same dozers, graders and compactors are shared. This schedule does not net them off.", "Bulk Earthworks MTO and civil programme", "R-17 to R-19, R-57"),
        ("Fuel", "Company supplies diesel free of charge; volume not stated; Schedule A.9 requires a 24-month profile (p222, p346).", "L/h by equipment class are planning figures. Idle months burn 20% of normal.", "LOW for scheduling; use only as a first Schedule A.9 draft.", "OEM fuel curves; Haul Infinity model", "R-11, Q-22"),
        ("People", "No workforce numbers; Schedule C blank (p354-358).", "Heads on site = operators x 2 shifts x 1.1 absence x (1 + 0.5 maintenance + 0.25 supervision).", "LOW - used only to size light vehicles and buses.", "Schedule C Personnel Deployment", "R-58, Q-41"),
        ("Permanent HME workshop", "MSA workshop concrete is Milestone 8, 08/01/2029 (p055).", "Temporary workshop bays carry the fleet to the end of the schedule.", "MEDIUM - first major services on a 260 t fleet land before the permanent workshop.", "Confirm early workshop access", "R-30, Q-24"),
        ("Reliance", "Reliance Information schedule is blank; all mine-plan and geotech inputs are at Contractor risk (p066-067).", "All figures in this workbook are Contractor planning assumptions, not reliance information.", "-", "Schedule [##] Reliance Information", "R-16, Q-07"),
    ]
    for i, row in enumerate(log):
        r_ = 5 + i
        wa.cell(row=r_, column=1, value=i + 1)
        for j, v in enumerate(row):
            wa.cell(row=r_, column=2 + j, value=v).alignment = WRAP
    for col, w in zip("ABCDEFG", (5, 26, 52, 58, 48, 44, 18)):
        wa.column_dimensions[col].width = w
    wa.freeze_panes = "C5"

    # ------------------------------------------------------------------ Summary (first sheet)
    wsu = wb.create_sheet("Summary", 0)
    title(wsu, "Winu - first 24 months mining schedule, earthworks and equipment list",
          "Dec 2027 (Site Access 23/11/2027) to Nov 2029 (Completion 30/11/2029). Basis: WIN-CON-EPC-001 Mining Review. All figures are planning assumptions where the ITT is silent.")
    sr = [4]

    def sline(label, formula, fmt="#,##0", note=""):
        wsu.cell(row=sr[0], column=1, value=label)
        c = wsu.cell(row=sr[0], column=2, value=formula)
        c.number_format, c.fill, c.font = fmt, OUTF, BOLD
        wsu.cell(row=sr[0], column=3, value=note).alignment = WRAP
        sr[0] += 1

    def ssec(text):
        band(wsu, sr[0], text, 3)
        sr[0] += 1

    ssec("Programme")
    sline("Model status (Checks sheet)", f"={CHECK_OVERALL}", "@", "Should read ALL OK")
    sline("Pre-strip volume", f"={SCH['vol']}", "#,##0", "bcm; ITT s6.2.1 about 21.6 Mbcm to ~70 m (first two of four cutbacks)")
    sline("First production month", f"=INDEX({SCHR('date')},Gantt!$C${GR['M1']})", "mmm-yyyy")
    sline("Last production month", f"=INDEX({SCHR('date')},Gantt!$D${GR['M1']})", "mmm-yyyy", "Close-out, rehabilitation and demobilisation follow; Completion 30/11/2029")
    sline("Peak monthly pre-strip rate", f"=MAX({SCHR('vol')})", "#,##0", "bcm/month")
    sline("Annualised peak rate", f"=MAX({SCHR('vol')})*12/1000000", "0.0", "Mbcm/year")
    sline("Total material moved incl. re-handle, borrow, topsoil", f"={SCH['tmm']}", "#,##0", "bcm")
    sline("Ore to stockpile", f"={SCH['ore']}", "#,##0", "t")
    sline("Pit floor depth at end of schedule", f"={SCH['floor']}", "0", "m below surface")
    sline("Share of pre-strip that is drilled and blasted", f"={Q('blast_pct')}", "0%")
    ssec("Destinations (bcm)")
    sline("Infrastructure (haul roads, ROM pad, bunds, stockpile bases)", f"={SCH['infra']}", "#,##0")
    sline("TSF Stage 0", f"={SCH['tsf']}", "#,##0")
    sline("Waste rock landform", f"={SCH['wrl']}", "#,##0")
    ssec("Drill and blast (Epiroc D65)")
    sline("Metres drilled", f"={SCH['metres']}", "#,##0", "m")
    sline("Holes drilled", f"={SCH['holes']}", "#,##0")
    sline("Bulk emulsion", f"={SCH['expl']}", "#,##0", "t")
    sline("Electronic detonators", f"={SCH['dets']}", "#,##0")
    ssec("Equipment (peak, selected)")
    sline("Epiroc D65 production drill rigs", f"=Fleet_Register!$I${FR['B1']}", "0")
    sline("Rear dump trucks (XDE260 class)", f"=Fleet_Register!$I${FR['A1']}", "0")
    sline("700 t-class excavators", f"=Fleet_Register!$I${FR['A2']}", "0")
    sline("Wheel loaders", f"=Fleet_Register!$I${FR['A3']}", "0")
    sline("Heavy mobile units (operated)", f"={TOT['heavy']}", "0")
    sline("  of which Company free-issue (assumed)", f"={TOT['free']}", "0", "Trucks, excavators and loaders; confirm against the Client Supplied Fleet List")
    sline("  Contractor-supplied vehicles and mobile plant", f"={TOT['con']}", "0")
    sline("Indicative heads on site", f"={TOT['heads']}", "0", "Order of magnitude")
    ssec("Diesel")
    sline("Total diesel, 24 months", f"={TOTL}", "#,##0.0", "ML. First draft for Schedule A.9")
    sline("Peak diesel demand", f"={PEAKL}", "#,##0", "L/day (HME and plant)")
    ssec("Earthworks (see Earthworks and Gantt)")
    sline("Area cleared and topsoiled", f"={Q('ha_tot')}", "#,##0", "ha")
    sline("Topsoil stripped", f"={SCH['topv']}", "#,##0", "bcm")
    sline("Haul roads (long-term)", f"={I('maint_km_perm')}", "0", "km; fill from pit and borrow pit")
    sline("ROM pad complete by", f"=INDEX({SCHR('date')},Gantt!$D${GR['E2']})", "mmm-yyyy", "Milestone 3 (Ore Crushing concrete) is 25/10/2028")
    sline("Stockpile bases complete by", f"=INDEX({SCHR('date')},Gantt!$D${GR['E5']})", "mmm-yyyy")
    sline("TSF Stage 0 fill complete by", f"=INDEX({SCHR('date')},Gantt!$D${GR['E7']})", "mmm-yyyy")
    ssec("Read this first")
    notes = [
        "The ITT gives no pre-strip duration, rate, haul profile or fleet. The rate is set by the fixed Completion Date: 21.6 Mbcm inside 24 months needs about 14 Mbcm/year at full rate.",
        "Trucks, excavators and loaders are marked Company free-issue (assumed). The Client Supplied Fleet List (C-WN-0000-G-LST-00005) was not in the pack, so the calculated fleet cannot be compared with what will be issued.",
        "The Epiroc D65 hole diameter, single-pass depth and net penetration rates are planning figures. Confirm with Epiroc or a site trial; drill count scales directly with them.",
        "Materials and destinations are scheduled top-down by layer. A real plan works several benches and both cutbacks at once, so monthly splits are indicative.",
        "Mine Access Road, Village, MPP / MSA pads, Aerodrome and power station earthworks are separate SP1 work areas and are not netted against this fleet.",
        "Technical Info documents used: TSF Yearly Development (Stage 0 fill 8.42 Mm3 vs 6.0 Mbcm supplied here), Worley hydrogeology (dewatering), Pit Materials Assessment (aeolian sand logged at 18-32 m vs 15 m in the ITT), Golder geotechnical (10 m benches, 100 m infrastructure stand-off), MSBA borrow areas.",
        "Assumptions_Log lists every ITT gap, the value used and the document that would replace it.",
    ]
    for n_ in notes:
        wsu.cell(row=sr[0], column=1, value=n_).alignment = WRAP
        wsu.merge_cells(start_row=sr[0], start_column=1, end_row=sr[0], end_column=3)
        wsu.row_dimensions[sr[0]].height = 32
        sr[0] += 1
    sr[0] += 1
    ssec("Sheets")
    guide = [("Inputs", "All assumptions and ITT figures. Yellow cells are inputs."), ("Quantities", "Layers, destinations, fill demand and disturbance."),
             ("Schedule", "Monthly production, destinations, ore, drill and blast, haul cycle and fleet requirement."),
             ("Earthworks", "Clearing, roads, ROM pad, stockpile bases, TSF, WRL, borrow pit with start / finish and machine hours."),
             ("Gantt", "Programme bars against contract dates."), ("Fleet_Register", "Equipment list with supply basis, sizing basis and override."),
             ("Fleet_Ramp", "Units on site by month."), ("Fuel", "Diesel profile."), ("Checks", "Consistency checks."),
             ("Assumptions_Log", "ITT gaps and the assumption used."), ("Productivity", "Static cycle and drill productivity constants.")]
    for a, b in guide:
        wsu.cell(row=sr[0], column=1, value=a).font = BOLD
        wsu.cell(row=sr[0], column=2, value=b)
        sr[0] += 1
    wsu.column_dimensions["A"].width = 58
    wsu.column_dimensions["B"].width = 18
    wsu.column_dimensions["C"].width = 100

    # sheet order
    order = ["Summary", "Gantt", "Schedule", "Earthworks", "Fleet_Register", "Fleet_Ramp", "Fuel", "Quantities", "Productivity", "Inputs", "Checks", "Assumptions_Log"]
    wb._sheets = [wb[n] for n in order]
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    out = Path(a.output)
    if out.exists() and not a.force:
        sys.exit(f"{out} exists; use --force to overwrite")
    build(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
