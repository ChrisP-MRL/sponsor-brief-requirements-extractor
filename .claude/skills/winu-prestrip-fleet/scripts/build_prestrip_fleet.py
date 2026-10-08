#!/usr/bin/env python3
"""Build the Winu pre-strip fleet sizing and mining schedule workbook.

All assumptions come from the JSON config. The workbook is formula-driven: change
Inputs, the fleet Override column or the monthly volume override column and every
sheet recalculates in Excel.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

NMONTHS = 48            # schedule rows (supports slower fleets / larger volumes)
HEAD = PatternFill("solid", fgColor="1F3864")
SUB = PatternFill("solid", fgColor="D9E1F2")
INP = PatternFill("solid", fgColor="FFF2CC")
OUTF = PatternFill("solid", fgColor="E2EFDA")
WHITE = Font(bold=True, color="FFFFFF")
BOLD = Font(bold=True)
BLUE = Font(color="0000FF")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")


def hdr(ws, row, labels, col=1):
    for i, t in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=t)
        c.font, c.fill, c.border = WHITE, HEAD, BOX
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = Font(bold=True, size=14)
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(italic=True, color="595959")


def ru(x):
    return f"ROUNDUP(ROUND({x},4),0)"


def build(cfg, out, carry):
    wb = Workbook()
    names = {}

    def name(key, ref):
        names[key] = ref
        wb.defined_names[key] = DefinedName(key, attr_text=ref)

    # ------------------------------------------------------------ README
    rd = wb.active
    rd.title = "README"
    # ------------------------------------------------------------ Inputs
    wi = wb.create_sheet("Inputs")
    title(wi, "Inputs and assumptions", "Yellow cells are inputs. Every figure on the other sheets is a formula driven from here, the fleet Override column and the monthly volume override.")
    hdr(wi, 4, ["Key (defined name)", "Parameter", "Value", "Unit", "Basis / source"])
    r = 5
    sect = None
    weather_rows = []
    for s, key, label, val, unit, basis in cfg["inputs"]:
        if s != sect:
            c = wi.cell(row=r, column=1, value=s)
            c.font = BOLD
            for col in range(1, 6):
                wi.cell(row=r, column=col).fill = SUB
            r += 1
            sect = s
        if unit == "date":
            val = dt.datetime.strptime(val, "%Y-%m-%d")
        wi.cell(row=r, column=1, value=key)
        wi.cell(row=r, column=2, value=label)
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
        name(key, f"Inputs!$C${r}")
        if key.startswith("w_m"):
            weather_rows.append(r)
        r += 1
    for col, w in zip("ABCDE", (22, 58, 16, 10, 100)):
        wi.column_dimensions[col].width = w
    wi.freeze_panes = "A5"
    wref = f"Inputs!$C${weather_rows[0]}:$C${weather_rows[-1]}"

    # ------------------------------------------------------------ Haul_Cycle
    wh = wb.create_sheet("Haul_Cycle")
    title(wh, "Material classes, haul cycle and loading productivity",
          "One row per material class. Cycle time = load + spot + ramp + in-pit flat + surface lead + dump + queue. Change inputs on the Inputs sheet.")
    cols = ["Material class", "Volume (bcm)", "Bank density (t/bcm)", "Swell (x)", "Avg dig depth (m)", "Surface lead (km)",
            "Loader", "Loose density (t/lcm)", "Truck payload (t)", "Payload (bcm)", "Passes", "Load + spot (min)",
            "Ramp length (km)", "Fixed cycle time (min)", "Cycle time (min)", "Trips per op-h", "Truck prod (bcm/op-h)",
            "Truck hours (h)", "Loader prod (bcm/op-h)", "Loader hours (h)", "Blasted (1/0)", "Drill prod (bcm/op-h/rig)",
            "Cumulative start (bcm)"]
    hdr(wh, 5, cols)
    wh.row_dimensions[5].height = 45
    classes = [
        ("1 Free-dig sand (to 15 m)", "vol_total*sand_share*freedig", "dens_sand", "swell_sand", "dig_depth_c1", "mix_c1", "EX", 0),
        ("2 Blasted sand (to 15 m)", "vol_total*sand_share*(1-freedig)", "dens_sand", "swell_sand", "dig_depth_c2", "mix_c2", "EX", 1),
        ("3 Cemented sand / sandstone / regolith (15-50 m)", "vol_total*mid_share", "dens_mid", "swell_mid", "dig_depth_c3", "mix_c3", "EX", 1),
        ("4 Mudstone / leach cap (50-70 m)", "vol_total*mud_share", "dens_mud", "swell_mud", "dig_depth_c4", "mix_c4", "EX", 1),
        ("5 TSF stockpile reclaim (re-handle)", "rehandle_pct*(B6*mix_c1_tsf+B7*mix_c2_tsf+B8*mix_c3_tsf+B9*mix_c4_tsf)", "dens_sand", "swell_sand", "0", None, "WL", 0),
    ]
    HC0 = 6
    drill_cls = {7: ("pen_c2", "area_c2"), 8: ("pen_c3", "area_c3"), 9: ("pen_c4", "area_c4")}
    for i, (nm, vol, dn, sw, dd, mix, ld, bl) in enumerate(classes):
        r = HC0 + i
        wh.cell(row=r, column=1, value=nm)
        wh.cell(row=r, column=2, value="=" + vol)
        wh.cell(row=r, column=3, value=f"={dn}")
        wh.cell(row=r, column=4, value=f"={sw}")
        wh.cell(row=r, column=5, value=f"={dd}")
        lead = "lead_rehandle" if mix is None else f"{mix}_wrl*d_wrl+{mix}_tsf*d_tsf+{mix}_inf*d_inf"
        wh.cell(row=r, column=6, value="=" + lead)
        wh.cell(row=r, column=7, value=ld)
        wh.cell(row=r, column=8, value=f"=C{r}/D{r}")
        wh.cell(row=r, column=9, value=f"=MIN(truck_payload,truck_body_m3*H{r})")
        wh.cell(row=r, column=10, value=f"=I{r}/C{r}")
        bucket = f'IF(G{r}="EX",ex_bucket*ex_fill,wl_bucket*wl_fill)'
        cyc = f'IF(G{r}="EX",ex_cycle_s,wl_cycle_s)'
        wh.cell(row=r, column=11, value=f"={ru(f'(I{r}/H{r})/{bucket}')}")
        wh.cell(row=r, column=12, value=f"=K{r}*{cyc}/60+t_spot")
        wh.cell(row=r, column=13, value=f"=E{r}/ramp_grade/1000")
        wh.cell(row=r, column=14, value=f'=L{r}+t_dump+t_queue+M{r}*(60/v_ramp_loaded+60/v_ramp_empty)+IF(G{r}="EX",inpit_flat_km,0)*(60/v_loaded+60/v_empty)')
        wh.cell(row=r, column=15, value=f"=N{r}+F{r}*haul_mult*min_per_km")
        wh.cell(row=r, column=16, value=f"=60/O{r}*op_eff")
        wh.cell(row=r, column=17, value=f"=P{r}*J{r}")
        wh.cell(row=r, column=18, value=f"=B{r}/Q{r}")
        wh.cell(row=r, column=19, value=f'={bucket}/D{r}*3600/{cyc}*op_eff*IF(G{r}="EX",ex_exch,wl_exch)')
        wh.cell(row=r, column=20, value=f"=B{r}/S{r}")
        wh.cell(row=r, column=21, value=bl)
        if r in drill_cls:
            pen, area = drill_cls[r]
            wh.cell(row=r, column=22, value=f"={pen}*drill_move_eff*{area}*bench_h/(bench_h+subdrill)")
        else:
            wh.cell(row=r, column=22, value=0)
        wh.cell(row=r, column=23, value=0 if i == 0 else f"=W{r-1}+B{r-1}")
        for col, f in ((2, "#,##0"), (3, "0.00"), (4, "0.00"), (5, "0.0"), (6, "0.00"), (8, "0.00"), (9, "0"), (10, "0.0"),
                       (12, "0.00"), (13, "0.00"), (14, "0.00"), (15, "0.00"), (16, "0.00"), (17, "#,##0"), (18, "#,##0"),
                       (19, "#,##0"), (20, "#,##0"), (22, "#,##0"), (23, "#,##0")):
            wh.cell(row=r, column=col).number_format = f
    wh.cell(row=11, column=1, value="Total classes 1-4").font = BOLD
    wh["B11"] = "=SUM(B6:B9)"
    wh["B11"].number_format = "#,##0"
    wh["R11"] = "=SUM(R6:R9)"
    wh["R11"].number_format = "#,##0"
    wh["R11"].font = BOLD
    wh.column_dimensions["A"].width = 46
    for c in range(2, 24):
        wh.column_dimensions[CL(c)].width = 13
    wh.freeze_panes = "B6"

    # ------------------------------------------------------------ Fleet_Register
    wr = wb.create_sheet("Fleet_Register")
    title(wr, "Fleet register - primary and ancillary equipment",
          "Calculated quantity is a formula. Type a number in the Override column to test a different fleet (blank = use calculated). The Selected quantity drives the schedule.")
    hdr(wr, 5, ["ID", "Group", "Equipment", "Class / basis", "Calculated qty", "Override qty", "Selected qty", "Provision",
                "Op hours / yr / unit", "Fuel (L/op-h)", "Fuel (kL/yr)", "Operated seat (1/0)", "Basis of quantity",
                "Client fleet list qty (enter)", "Selected minus list"])
    wr.row_dimensions[5].height = 45
    FREE = "Company free-issue HME (assumed - confirm vs C-WN-0000-G-LST-00005)"
    CON = "Contractor supplied"
    # id, group, equipment, class, calc formula (str with {ID} refs), provision, hours name, fuel, seat, basis
    reg = [
        ("P01", "Load and haul", "Rear dump truck", "XCMG XDE260-class, ~260 t", "trucks_rec", FREE, "hryr_truck", 190, 1, "Truck hours from cycle time (Haul_Cycle) / available hours per truck, plus contingency"),
        ("P02", "Load and haul", "Large hydraulic excavator", "~700 t class, ~40 m3 (matched to 260 t trucks)", "ex_rec", FREE, "hryr_ex", 380, 1, "Excavator hours / available hours, minimum concurrent dig faces"),
        ("P03", "Load and haul", "Large wheel loader", "~20 m3 class", "wl_rec", FREE, "hryr_wl", 130, 1, "TSF stockpile reclaim hours / available hours, plus extra loader for stemming, pads, ore"),
        ("P04", "Load and haul", "Medium excavator", "~120-200 t class", "med_ex", CON, "hryr_supp", 110, 1, "Input: batter trimming, ore harvest, drains, sumps"),
        ("P05", "Load and haul", "Ore / clean-up / stemming truck", "90-100 t rigid", "ore_trucks", CON, "hryr_supp", 70, 1, "Input: first 600 kt ore, clean-up, stemming and aggregate haul"),
        ("D01", "Drill and blast", "Production blasthole drill rig", "165-200 mm rotary / DTH, 10 m benches", "drills_rec", CON, "hryr_drill", 75, 1, "Drill metres / net penetration / available hours, minimum rigs"),
        ("D02", "Drill and blast", "Ore pre-split / trim drill rig", "Smaller rig, 5 m benches", "presplit_rigs", CON, "hryr_supp", 45, 1, "Input: pre-split required in ore only"),
        ("D03", "Drill and blast", "Bulk emulsion MPU / charging unit", "~12-15 t emulsion", "mpu_rec", CON, "hryr_mpu", 25, 1, "Explosive tonnes / charging rate / available hours, minimum units"),
        ("D04", "Drill and blast", "Initiation and stemming support vehicle", "Utility with crane / cargo body", "{D03}", CON, "hryr_supp", 12, 1, "One per charging unit"),
        ("R01", "Road, dump and floor support", "Dump-face dozer", "Track dozer ~600 kW", "ROUNDUP({P01}*dump_dozer_ratio,0)", FREE, "hryr_wl", 130, 1, "Ratio to selected trucks"),
        ("R02", "Road, dump and floor support", "Dig-face / floor clean-up dozer", "Track dozer ~600 kW", "ROUNDUP({P02}*face_dozer_per_ex,0)", FREE, "hryr_wl", 130, 1, "Ratio to selected large excavators"),
        ("R03", "Road, dump and floor support", "TSF paddock spreading dozer", "Track dozer ~600 kW", "tsf_dozers", FREE, "hryr_wl", 130, 1, "Input"),
        ("R04", "Road, dump and floor support", "Wheel dozer", "~400 kW", "wheel_dozers", CON, "hryr_supp", 110, 1, "Input"),
        ("R05", "Road, dump and floor support", "Motor grader", "~24 ft blade", "ROUNDUP((maint_km_perm+maint_km_temp)/km_per_grader,0)+grader_extra", FREE, "hryr_wl", 45, 1, "Road length maintained / km per grader, plus extra"),
        ("R06", "Road, dump and floor support", "Water cart (dust suppression)", ">= 100 kL off-highway", "ROUNDUP((maint_km_perm+maint_km_temp)/km_per_cart,0)+cart_tsf", FREE, "hryr_wl", 100, 1, "Road length maintained / km per cart, plus TSF and pit"),
        ("R07", "Road, dump and floor support", "Compactor (smooth drum / padfoot)", "~20 t", "rollers", CON, "hryr_supp", 25, 1, "Input"),
        ("W01", "Dewatering", "In-pit diesel pump set / sump pump", "High-head and trash pumps", "pumps", CON, "hryr_pump", 10, 0, "Input"),
        ("S01", "Support and ancillary", "Fuel and lube tanker", "~20 kL with lube pods", "ROUNDUP(fuel_kl_yr*1000*(1+veh_fuel_allow)/365/(tanker_cap*fills_per_day),0)+fuel_spare", CON, "hryr_supp", 18, 1, "Annual fuel of selected fleet / tanker throughput, plus spare"),
        ("S02", "Support and ancillary", "Service truck (mechanical / field lube)", "With crane", "MAX(2,ROUNDUP(({P01}+{P02}+{P03}+{R01}+{R02}+{R03}+{R05}+{R06})/svc_units_per_truck,0))", CON, "hryr_supp", 15, 1, "Heavy units per service truck, minimum 2"),
        ("S03", "Support and ancillary", "Tyre handler", "260 t class", "tyre_handlers", CON, "hryr_supp", 25, 1, "Input"),
        ("S04", "Support and ancillary", "Lighting plant", "Diesel tower", "{P02}*lp_per_ex+lp_dump+{D01}*lp_per_drill", CON, "hryr_supp", 3, 0, "Per excavator, per drill, plus dumps and TSF"),
        ("S05", "Support and ancillary", "Mobile crane", "~50 t", "cranes", CON, "hryr_supp", 20, 1, "Input"),
        ("S06", "Support and ancillary", "Telehandler / Franna-type crane", "", "telehandlers", CON, "hryr_supp", 10, 1, "Input"),
        ("S07", "Support and ancillary", "Float (prime mover and low loader)", "", "floats", CON, "hryr_supp", 30, 1, "Input; ITT s10.3.2 lists float as Contractor-supplied"),
        ("S08", "Support and ancillary", "Ambulance / emergency response vehicle", "", "amb", CON, "hryr_supp", 0, 0, "Input"),
        ("S09", "Support and ancillary", "Fire / rescue truck", "", "fire", CON, "hryr_supp", 0, 0, "Input"),
        ("S10", "Support and ancillary", "Light vehicle (4WD)", "Supervision, survey, geology, maintenance, blast crew", "ROUNDUP(onsite_heads*lv_per_head,0)", CON, "hryr_supp", 0, 0, "Heads on site x light vehicles per head (fuel not modelled; see allowance)"),
        ("S11", "Support and ancillary", "Personnel bus", "~21 seat", "ROUNDUP(onsite_heads/shifts_per_day/bus_seats,0)+1", CON, "hryr_supp", 0, 0, "One shift of people per changeover, plus spare"),
        ("F01", "Fleet management and comms", "FMS on-board units (Wenco or approved equivalent)", "One per mobile unit P01-R07", "SUM({RANGE_PR})", CON, "hryr_supp", 0, 0, "ITT s6.2.16: FMS in Contractor scope for full duration"),
        ("F02", "Fleet management and comms", "FMS / radio mesh repeater trailer", "", "repeaters", CON, "hryr_supp", 0, 0, "ITT s6.2.16"),
    ]
    R0 = 6
    row_of = {x[0]: R0 + i for i, x in enumerate(reg)}

    def sel(i):
        return f"$G${row_of[i]}"

    def expand(f):
        for i in row_of:
            f = f.replace("{" + i + "}", sel(i))
        return f.replace("{RANGE_PR}", f"G{row_of['P01']}:G{row_of['R07']}")

    carried_ov, carried_list, carried_sched = {}, {}, {}
    if carry and Path(out).exists():
        try:
            old = load_workbook(out)
            if "Fleet_Register" in old.sheetnames:
                for row in old["Fleet_Register"].iter_rows(min_row=6, values_only=True):
                    if row[0]:
                        carried_ov[row[0]] = row[5]
                        carried_list[row[0]] = row[13]
            if "Schedule" in old.sheetnames:
                for row in old["Schedule"].iter_rows(min_row=8, values_only=True):
                    if isinstance(row[0], int):
                        carried_sched[row[0]] = row[12]
        except Exception as e:  # noqa: BLE001
            print(f"carry-forward skipped: {e}", file=sys.stderr)

    for i, (rid, grp, eq, cls, calc, prov, hn, fuel, seat, basis) in enumerate(reg):
        r = R0 + i
        wr.cell(row=r, column=1, value=rid)
        wr.cell(row=r, column=2, value=grp)
        wr.cell(row=r, column=3, value=eq)
        wr.cell(row=r, column=4, value=cls)
        wr.cell(row=r, column=5, value="=" + expand(calc))
        c = wr.cell(row=r, column=6, value=carried_ov.get(rid))
        c.fill, c.font, c.border = INP, BLUE, BOX
        wr.cell(row=r, column=7, value=f'=IF(F{r}="",E{r},F{r})').font = BOLD
        wr.cell(row=r, column=8, value=prov)
        wr.cell(row=r, column=9, value=f"={hn}").number_format = "#,##0"
        wr.cell(row=r, column=10, value=fuel)
        wr.cell(row=r, column=11, value=f"=G{r}*I{r}*J{r}/1000").number_format = "#,##0"
        wr.cell(row=r, column=12, value=seat)
        wr.cell(row=r, column=13, value=basis).alignment = WRAP
        c = wr.cell(row=r, column=14, value=carried_list.get(rid))
        c.fill, c.font, c.border = INP, BLUE, BOX
        wr.cell(row=r, column=15, value=f'=IF(N{r}="","",G{r}-N{r})')
        wr.cell(row=r, column=7).fill = OUTF
    RLAST = R0 + len(reg) - 1
    rt = RLAST + 2
    wr.cell(row=rt, column=3, value="Total mobile equipment (P, D, R, W, S01-S09)").font = BOLD
    wr.cell(row=rt, column=7, value=f"=SUM(G{R0}:G{row_of['S09']})").font = BOLD
    wr.cell(row=rt + 1, column=3, value="Total annual fuel at full rate (kL/yr)").font = BOLD
    wr.cell(row=rt + 1, column=11, value=f"=SUM(K{R0}:K{row_of['W01']})").number_format = "#,##0"
    for col, w in zip("ABCDEFGHIJKLMNO", (6, 26, 44, 42, 12, 12, 12, 34, 14, 10, 12, 10, 60, 14, 12)):
        wr.column_dimensions[col].width = w
    wr.freeze_panes = "D6"
    for key, i in (("sel_trucks", "P01"), ("sel_ex", "P02"), ("sel_wl", "P03"), ("sel_drills", "D01"), ("sel_mpu", "D03")):
        name(key, f"Fleet_Register!$G${row_of[i]}")
    name("fuel_kl_yr", f"Fleet_Register!$K${rt+1}")
    seats_ref = f"SUMPRODUCT(Fleet_Register!$G${R0}:$G${row_of['S09']},Fleet_Register!$L${R0}:$L${row_of['S09']})"

    # ------------------------------------------------------------ Fleet_Calc
    wc = wb.create_sheet("Fleet_Calc")
    title(wc, "Fleet requirement calculations", "Required hours from Haul_Cycle divided by available hours per unit over the target production window.")
    hdr(wc, 4, ["Quantity", "Value", "Unit", "Basis"])
    HCR = "Haul_Cycle!"
    calc = [
        ("Programme and shares", None, None, None, None),
        ("sand_share", "Sand share of volume", "depth_sand/depth_total", "fraction", "Thickness share; assumes constant thickness across the two cutbacks"),
        ("mid_share", "Cemented sand / sandstone share", "(depth_mid-depth_sand)/depth_total", "fraction", ""),
        ("mud_share", "Mudstone / leach cap share", "(depth_total-depth_mid)/depth_total", "fraction", ""),
        ("weather_total", "Weather lost days per year", f"SUM({wref})", "days", "Sum of monthly lost days"),
        ("sched_hr_yr", "Scheduled hours per year", "(days_per_year-weather_total)*hours_per_day", "h", ""),
        ("prod_months", "Equivalent full-rate months", "dur_months-ramp_months*(1-ramp_eff)", "months", "Duration less ramp-up shortfall"),
        ("rate_bcm_month", "Target production rate", "vol_total/prod_months", "bcm/month", ""),
        ("rate_bcm_year", "Target production rate (annual)", "rate_bcm_month*12", "bcm/yr", ""),
        ("mass_total", "Total tonnes moved", f"SUMPRODUCT({HCR}B6:B9,{HCR}C6:C9)", "t", "Bank tonnes"),
        ("rate_mtpa", "Target tonnes per annum", "mass_total/prod_months*12/1000000", "Mt/yr", ""),
        ("min_per_km", "Haul time per km of surface lead (loaded + empty)", "60/v_loaded+60/v_empty", "min/km", ""),
        ("Available operating hours per unit over the target window", None, None, None, None),
        ("hrs_truck_unit", "Truck", "sched_hr_yr/12*prod_months*truck_avail*truck_util", "h", ""),
        ("hrs_ex_unit", "Large excavator", "sched_hr_yr/12*prod_months*ex_avail*ex_util", "h", ""),
        ("hrs_wl_unit", "Wheel loader", "sched_hr_yr/12*prod_months*wl_avail*wl_util", "h", ""),
        ("hrs_drill_unit", "Drill rig", "sched_hr_yr/12*prod_months*drill_avail*drill_util", "h", ""),
        ("hrs_mpu_unit", "MPU", "sched_hr_yr/12*prod_months*mpu_avail*mpu_util", "h", ""),
        ("Operating hours per unit per year (fuel and registers)", None, None, None, None),
        ("hryr_truck", "Truck", "sched_hr_yr*truck_avail*truck_util", "h/yr", ""),
        ("hryr_ex", "Large excavator", "sched_hr_yr*ex_avail*ex_util", "h/yr", ""),
        ("hryr_wl", "Wheel loader / dozer / grader / water cart", "sched_hr_yr*wl_avail*wl_util", "h/yr", "Wheel loader availability and utilisation used as proxy"),
        ("hryr_drill", "Drill rig", "sched_hr_yr*drill_avail*drill_util", "h/yr", ""),
        ("hryr_mpu", "MPU", "sched_hr_yr*mpu_avail*mpu_util", "h/yr", ""),
        ("hryr_supp", "Other support equipment", "sched_hr_yr*supp_avail*supp_util", "h/yr", ""),
        ("hryr_pump", "Pumps", "sched_hr_yr*0.9", "h/yr", "Run near-continuously"),
        ("Trucks", None, None, None, None),
        ("truck_hrs_total", "Truck hours, all classes incl. re-handle", f"SUM({HCR}R6:R10)", "h", ""),
        ("trucks_calc", "Trucks required (unrounded)", "truck_hrs_total/hrs_truck_unit", "units", ""),
        ("trucks_inservice", "Trucks in service (rounded up)", ru("trucks_calc"), "units", ""),
        ("trucks_rec", "Trucks recommended (incl. contingency)", ru("trucks_inservice*(1+fleet_contingency)"), "units", ""),
        ("rehandle_ovh", "Re-handle truck-hour overhead", f"{HCR}R10/SUM({HCR}R6:R9)", "fraction", "Applied to schedule truck capacity"),
        ("Loading", None, None, None, None),
        ("ex_hrs_total", "Large excavator hours", f'SUMIF({HCR}G6:G10,"EX",{HCR}T6:T10)', "h", ""),
        ("ex_calc", "Large excavators required (unrounded)", "ex_hrs_total/hrs_ex_unit", "units", ""),
        ("ex_rec", "Large excavators recommended", f"MAX({ru('ex_calc')},min_faces)", "units", "Minimum concurrent faces governs if higher"),
        ("wl_hrs_total", "Wheel loader hours (re-handle)", f'SUMIF({HCR}G6:G10,"WL",{HCR}T6:T10)', "h", ""),
        ("wl_calc", "Wheel loaders for re-handle (unrounded)", "wl_hrs_total/hrs_wl_unit", "units", ""),
        ("wl_rec", "Wheel loaders recommended", f"MAX({ru('wl_calc')},1)+wl_extra", "units", ""),
        ("Drill and blast", None, None, None, None),
        ("blast_vol", "Blasted volume", f"SUM({HCR}B7:B9)", "bcm", "Classes 2-4"),
        ("drill_hrs_total", "Drill hours", f"{HCR}B7/{HCR}V7+{HCR}B8/{HCR}V8+{HCR}B9/{HCR}V9", "h", ""),
        ("drills_calc", "Production rigs required (unrounded)", "drill_hrs_total/hrs_drill_unit", "units", ""),
        ("drills_rec", "Production rigs recommended", f"MAX({ru('drills_calc')},min_drills)", "units", ""),
        ("expl_t_total", "Explosives total", f"({HCR}B7*pf_c2+{HCR}B8*pf_c3+{HCR}B9*pf_c4)/1000", "t", "Bulk inhibited emulsion"),
        ("mpu_hrs_total", "MPU hours", "expl_t_total/mpu_rate", "h", ""),
        ("mpu_calc", "MPU required (unrounded)", "mpu_hrs_total/hrs_mpu_unit", "units", ""),
        ("mpu_rec", "MPU recommended", f"MAX({ru('mpu_calc')},min_mpu)", "units", ""),
        ("People (indicative)", None, None, None, None),
        ("seats_total", "Operated seats", seats_ref, "units", "Selected fleet"),
        ("ops_roster", "Operators on roster", "seats_total*shifts_per_day*roster_factor*absent_factor", "heads", ""),
        ("maint_heads", "Maintenance heads on roster", "ops_roster*maint_ratio", "heads", ""),
        ("superv_heads", "Supervision, technical and support heads on roster", "ops_roster*superv_ratio", "heads", ""),
        ("roster_total", "Total roster", "ops_roster+maint_heads+superv_heads", "heads", ""),
        ("onsite_heads", "Heads on site at any time", "roster_total/roster_factor", "heads", "Two thirds of roster on a 14/7 cycle"),
    ]
    r = 5
    for item in calc:
        if item[1] is None:
            c = wc.cell(row=r, column=1, value=item[0])
            c.font = BOLD
            for col in range(1, 5):
                wc.cell(row=r, column=col).fill = SUB
        else:
            key, label, f, unit, note = item
            wc.cell(row=r, column=1, value=label)
            c = wc.cell(row=r, column=2, value="=" + f)
            c.number_format = "0.00" if unit in ("fraction", "min/km", "units") else "#,##0"
            if key in ("trucks_inservice", "trucks_rec", "ex_rec", "wl_rec", "drills_rec", "mpu_rec"):
                c.fill, c.font = OUTF, BOLD
                c.number_format = "0"
            wc.cell(row=r, column=3, value=unit)
            wc.cell(row=r, column=4, value=note)
            name(key, f"Fleet_Calc!$B${r}")
        r += 1
    for col, w in zip("ABCD", (58, 16, 12, 70)):
        wc.column_dimensions[col].width = w
    wc.freeze_panes = "A5"

    # ------------------------------------------------------------ Schedule
    ws = wb.create_sheet("Schedule")
    title(ws, "Monthly mining schedule", "Capacity-constrained: monthly volume = lesser of selected-fleet capacity and remaining volume, unless a volume override is typed in column M. Material is mined top-down (sand, then cemented sand / sandstone, then mudstone).")
    S0, S1 = 9, 9 + NMONTHS - 1
    cols = ["Month #", "Month start", "Days", "Weather lost days", "Scheduled hours", "Ramp factor", "Cumulative start (bcm)",
            "Class at start", "Truck capacity (bcm)", "Excavator capacity (bcm)", "Drill capacity (bcm)", "Fleet capacity (bcm)",
            "Volume override (bcm) - enter", "Remaining at start (bcm)", "PLANNED VOLUME (bcm)", "Cumulative end (bcm)",
            "Free-dig sand (bcm)", "Blasted sand (bcm)", "Cemented sand / sandstone (bcm)", "Mudstone / leach cap (bcm)",
            "Tonnes moved (t)", "Truck hours required", "Truck utilisation", "Excavator hours required", "Drill hours required",
            "Explosives (t)", "Fuel, fleet (kL)", "% complete", "Target cumulative (bcm)", "Ahead / (behind) target (bcm)", "Flag"]
    hdr(ws, 8, cols)
    ws.row_dimensions[8].height = 60
    ws["A4"], ws["A5"], ws["A6"] = "Planned last production month", "Months of production", "Volume not scheduled in 48 months (bcm)"
    ws["E4"] = f'=_xlfn.MAXIFS(B{S0}:B{S1},O{S0}:O{S1},">0")'
    ws["E5"] = f'=COUNTIF(O{S0}:O{S1},">0")'
    ws["E6"] = f"=vol_total-MAX(P{S0}:P{S1})"
    ws["G4"], ws["G5"], ws["G6"] = "Demobilisation complete", "Target duration (months)", "Peak monthly volume (bcm)"
    ws["K4"] = "=EOMONTH(E4,demob_months)"
    ws["K5"] = "=dur_months"
    ws["K6"] = f"=MAX(O{S0}:O{S1})"
    for a in ("A4", "A5", "A6", "G4", "G5", "G6"):
        ws[a].font = BOLD
    ws["E4"].number_format = ws["K4"].number_format = "mmm-yyyy"
    ws["E6"].number_format = ws["K6"].number_format = "#,##0"
    name("sched_finish_month", "Schedule!$E$4")
    name("sched_months", "Schedule!$E$5")
    name("sched_unscheduled", "Schedule!$E$6")
    name("sched_demob_end", "Schedule!$K$4")
    th = f"{HCR}$W$6:$W$9"
    for k in range(NMONTHS):
        r = S0 + k
        ws.cell(row=r, column=1, value=k + 1)
        ws.cell(row=r, column=2, value=f"=EDATE(start_date,A{r}-1)").number_format = "mmm-yyyy"
        ws.cell(row=r, column=3, value=f"=DAY(EOMONTH(B{r},0))")
        ws.cell(row=r, column=4, value=f"=INDEX({wref},MONTH(B{r}))")
        ws.cell(row=r, column=5, value=f"=(C{r}-D{r})*hours_per_day").number_format = "#,##0"
        ws.cell(row=r, column=6, value=f"=IF(A{r}<=ramp_months,ramp_eff,1)")
        ws.cell(row=r, column=7, value=0 if k == 0 else f"=P{r-1}")
        ws.cell(row=r, column=8, value=f"=MATCH(G{r}+0.5,{th},1)")
        ws.cell(row=r, column=9, value=f"=sel_trucks*E{r}*truck_avail*truck_util*F{r}*MIN(INDEX({HCR}$Q$6:$Q$9,H{r}),INDEX({HCR}$Q$6:$Q$9,MIN(H{r}+1,4)))/(1+rehandle_ovh)")
        ws.cell(row=r, column=10, value=f"=sel_ex*E{r}*ex_avail*ex_util*F{r}*MIN(INDEX({HCR}$S$6:$S$9,H{r}),INDEX({HCR}$S$6:$S$9,MIN(H{r}+1,4)))")
        ws.cell(row=r, column=11, value=f"=IF(INDEX({HCR}$U$6:$U$9,H{r})=1,sel_drills*E{r}*drill_avail*drill_util*F{r}*MIN(INDEX({HCR}$V$6:$V$9,H{r}),INDEX({HCR}$V$6:$V$9,MIN(H{r}+1,4))),1E+12)")
        ws.cell(row=r, column=12, value=f"=MIN(I{r},J{r},K{r})")
        c = ws.cell(row=r, column=13, value=carried_sched.get(k + 1))
        c.fill, c.font, c.border = INP, BLUE, BOX
        ws.cell(row=r, column=14, value=f"=MAX(0,vol_total-G{r})")
        ws.cell(row=r, column=15, value=f'=IF(N{r}<=0,0,MIN(N{r},IF(M{r}="",L{r},M{r})))').fill = OUTF
        ws.cell(row=r, column=16, value=f"=G{r}+O{r}")
        for j in range(4):
            cr = HC0 + j
            ws.cell(row=r, column=17 + j, value=f"=MAX(0,MIN($P{r},{HCR}$W${cr}+{HCR}$B${cr})-MAX($G{r},{HCR}$W${cr}))")
        ws.cell(row=r, column=21, value=f"=Q{r}*dens_sand+R{r}*dens_sand+S{r}*dens_mid+T{r}*dens_mud")
        ws.cell(row=r, column=22, value=f"=(Q{r}/{HCR}$Q$6+R{r}/{HCR}$Q$7+S{r}/{HCR}$Q$8+T{r}/{HCR}$Q$9)*(1+rehandle_ovh)")
        ws.cell(row=r, column=23, value=f"=V{r}/(sel_trucks*E{r}*truck_avail*truck_util)").number_format = "0%"
        ws.cell(row=r, column=24, value=f"=Q{r}/{HCR}$S$6+R{r}/{HCR}$S$7+S{r}/{HCR}$S$8+T{r}/{HCR}$S$9")
        ws.cell(row=r, column=25, value=f"=R{r}/{HCR}$V$7+S{r}/{HCR}$V$8+T{r}/{HCR}$V$9")
        ws.cell(row=r, column=26, value=f"=(R{r}*pf_c2+S{r}*pf_c3+T{r}*pf_c4)/1000")
        ws.cell(row=r, column=27, value=f"=fuel_kl_yr*(E{r}/sched_hr_yr)*MIN(1,W{r})")
        ws.cell(row=r, column=28, value=f"=P{r}/vol_total").number_format = "0.0%"
        ws.cell(row=r, column=29, value=f"=MIN(vol_total,{'0' if k == 0 else f'AC{r-1}'}+rate_bcm_month*F{r})")
        ws.cell(row=r, column=30, value=f"=P{r}-AC{r}")
        ws.cell(row=r, column=31, value=f'=IF(AND(M{r}<>"",O{r}>L{r}),"Over fleet capacity",IF(W{r}>1.0001,"Truck hours exceed available",""))')
        for col in (7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 29, 30):
            ws.cell(row=r, column=col).number_format = "#,##0"
        ws.cell(row=r, column=6).number_format = "0.00"
        ws.cell(row=r, column=4).number_format = "0.0"
        ws.cell(row=r, column=11).number_format = '[>=1E+11]"no limit";#,##0'
    tr = S1 + 1
    ws.cell(row=tr, column=2, value="Total").font = BOLD
    for col in (15, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27):
        c = ws.cell(row=tr, column=col, value=f"=SUM({CL(col)}{S0}:{CL(col)}{S1})")
        c.font, c.number_format = BOLD, "#,##0"
    ws.column_dimensions["A"].width = 8
    for c in range(2, 32):
        ws.column_dimensions[CL(c)].width = 13
    ws.freeze_panes = ws.cell(row=S0, column=3)
    ws.conditional_formatting.add(f"A{S0}:AE{S1}", FormulaRule(formula=[f"$O{S0}=0"], font=Font(color="BFBFBF")))
    ws.conditional_formatting.add(f"AE{S0}:AE{S1}", FormulaRule(formula=[f'AE{S0}<>""'], font=Font(color="C00000", bold=True)))

    # ------------------------------------------------------------ Gantt
    wg = wb.create_sheet("Gantt")
    title(wg, "Mining schedule - summary bar chart", "Bars are driven by the Schedule sheet. Dates update when volume, fleet or inputs change.")
    GM = NMONTHS + 8
    hdr(wg, 5, ["Activity", "Basis", "Start", "End"])
    G0 = 5
    for m in range(GM):
        c = wg.cell(row=G0, column=5 + m, value=f"=EDATE(start_date,{m}-mob_months)")
        c.number_format = "mmm-yy"
        c.font, c.fill = WHITE, HEAD
        c.alignment = Alignment(text_rotation=90, horizontal="center")
    wg.row_dimensions[G0].height = 48
    B, Sx = f"Schedule!$B${S0}:$B${S1}", {}
    for j, col in enumerate("QRST"):
        Sx[j] = (f"Schedule!${col}${S0}:${col}${S1}")

    def first(rng):
        return f'_xlfn.MINIFS({B},{rng},">0")'

    def last(rng):
        return f'EOMONTH(_xlfn.MAXIFS({B},{rng},">0"),0)'

    acts = [
        ("Mobilisation, site establishment, free-issue fleet acceptance", "Before production start", "=EDATE(start_date,-mob_months)", "=start_date-1"),
        ("Fleet ramp-up", "Ramp months at reduced rate", "=start_date", "=EDATE(start_date,ramp_months)-1"),
        ("Free-dig sand (0-15 m)", "First to last month with volume", "=" + first(Sx[0]), "=" + last(Sx[0])),
        ("Blasted sand (0-15 m)", "", "=" + first(Sx[1]), "=" + last(Sx[1])),
        ("Cemented sand / sandstone / regolith (15-50 m)", "", "=" + first(Sx[2]), "=" + last(Sx[2])),
        ("Mudstone / leach cap (50-70 m)", "", "=" + first(Sx[3]), "=" + last(Sx[3])),
        ("Drill and blast", "Any blasted class", f"=MIN({first(Sx[1])},{first(Sx[2])},{first(Sx[3])})", f"=MAX({last(Sx[1])},{last(Sx[2])},{last(Sx[3])})"),
        ("TSF fill supply (sand and regolith)", "Classes 1-3", f"=MIN({first(Sx[0])},{first(Sx[1])},{first(Sx[2])})", f"=MAX({last(Sx[0])},{last(Sx[1])},{last(Sx[2])})"),
        ("Waste Rock Landform build and haul road maintenance", "Whole production span", f"=MIN({first(Sx[0])},{first(Sx[1])},{first(Sx[2])})", "=EOMONTH(sched_finish_month,0)"),
        ("Pit dewatering below ~50 m water table", "From mudstone start", "=" + first(Sx[3]), "=EOMONTH(sched_finish_month,0)"),
        ("Demobilisation and rehabilitation", "After last bcm", "=EDATE(sched_finish_month,1)", "=sched_demob_end"),
        ("Separable Part 1 Completion Date", "Agreement Schedule Item 13(b)", "=completion_date", "=completion_date"),
    ]
    for i, (a, bsis, s, e) in enumerate(acts):
        r = G0 + 1 + i
        wg.cell(row=r, column=1, value=a)
        wg.cell(row=r, column=2, value=bsis)
        wg.cell(row=r, column=3, value=s).number_format = "dd-mmm-yy"
        wg.cell(row=r, column=4, value=e).number_format = "dd-mmm-yy"
    GL = G0 + len(acts)
    wg.cell(row=GL + 2, column=1, value="Planned volume (bcm)").font = BOLD
    wg.cell(row=GL + 3, column=1, value="Cumulative % complete").font = BOLD
    for m in range(GM):
        col = CL(5 + m)
        wg.cell(row=GL + 2, column=5 + m, value=f"=SUMIF({B},{col}${G0},Schedule!$O${S0}:$O${S1})").number_format = "#,##0,"
        wg.cell(row=GL + 3, column=5 + m, value=f"=SUMIFS(Schedule!$AB${S0}:$AB${S1},{B},{col}${G0})").number_format = "0%"
    last_col = CL(5 + GM - 1)
    rng = f"E{G0+1}:{last_col}{GL}"
    wg.conditional_formatting.add(f"E{GL}:{last_col}{GL}", FormulaRule(formula=[f"AND(E${G0}<=$C{GL},EOMONTH(E${G0},0)>=$C{GL})"], fill=PatternFill("solid", bgColor="C00000"), stopIfTrue=True))
    wg.conditional_formatting.add(rng, FormulaRule(formula=[f"AND(E${G0}<=$D{G0+1},EOMONTH(E${G0},0)>=$C{G0+1},ISNUMBER($C{G0+1}),$C{G0+1}>0)"], fill=PatternFill("solid", bgColor="2F75B5")))
    wg.column_dimensions["A"].width = 56
    wg.column_dimensions["B"].width = 30
    wg.column_dimensions["C"].width = wg.column_dimensions["D"].width = 11
    for m in range(GM):
        wg.column_dimensions[CL(5 + m)].width = 6
    wg.freeze_panes = "E6"

    # ------------------------------------------------------------ Sensitivity
    wsn = wb.create_sheet("Sensitivity")
    title(wsn, "Sensitivity - fleet needed for a different duration or haul distance",
          "Same logic as Fleet_Calc, recalculated for each duration and an absolute multiplier on the base surface leads. Trucks include the contingency.")
    durs = [18, 22, 26, 28, 32, 36, 42]
    mults = [0.75, 1.0, 1.25, 1.5, 2.0]
    wsn["A4"] = "Trucks recommended"
    wsn["A4"].font = BOLD
    wsn["A5"] = "Duration (months) \\ lead multiplier"
    for j, m in enumerate(mults):
        c = wsn.cell(row=5, column=2 + j, value=m)
        c.fill, c.font, c.border = INP, BLUE, BOX
    for i, d in enumerate(durs):
        r = 6 + i
        c = wsn.cell(row=r, column=1, value=d)
        c.fill, c.font, c.border = INP, BLUE, BOX
        for j in range(len(mults)):
            col = CL(2 + j)
            f = (f"=ROUNDUP(ROUND({ru(f'SUMPRODUCT({HCR}$B$6:$B$10,({HCR}$N$6:$N$10+{HCR}$F$6:$F$10*{col}$5*min_per_km)/({HCR}$J$6:$J$10*60*op_eff))/(sched_hr_yr/12*($A{r}-ramp_months*(1-ramp_eff))*truck_avail*truck_util)')}*(1+fleet_contingency),4),0)")
            wsn.cell(row=r, column=2 + j, value=f)
    r2 = 6 + len(durs) + 2
    wsn.cell(row=r2, column=1, value="Large excavators, drill rigs and production rate by duration").font = BOLD
    hdr(wsn, r2 + 1, ["Duration (months)", "Large excavators", "Production rigs", "MPU", "Rate (Mbcm/yr)", "Rate (Mt/yr)"])
    for i, d in enumerate(durs):
        r = r2 + 2 + i
        wsn.cell(row=r, column=1, value=f"=A{6+i}")
        eq = f"(sched_hr_yr/12*($A{r}-ramp_months*(1-ramp_eff)))"
        wsn.cell(row=r, column=2, value=f"=MAX({ru(f'ex_hrs_total/({eq}*ex_avail*ex_util)')},min_faces)")
        wsn.cell(row=r, column=3, value=f"=MAX({ru(f'drill_hrs_total/({eq}*drill_avail*drill_util)')},min_drills)")
        wsn.cell(row=r, column=4, value=f"=MAX({ru(f'mpu_hrs_total/({eq}*mpu_avail*mpu_util)')},min_mpu)")
        wsn.cell(row=r, column=5, value=f"=vol_total/($A{r}-ramp_months*(1-ramp_eff))*12/1000000").number_format = "0.0"
        wsn.cell(row=r, column=6, value=f"=mass_total/($A{r}-ramp_months*(1-ramp_eff))*12/1000000").number_format = "0.0"
    wsn.column_dimensions["A"].width = 36
    for c in range(2, 8):
        wsn.column_dimensions[CL(c)].width = 16

    # ------------------------------------------------------------ Checks
    wk = wb.create_sheet("Checks")
    title(wk, "Validation checks")
    hdr(wk, 3, ["Check", "Result", "Detail"])
    checks = [
        ("Class volumes sum to total volume", f'=IF(ABS({HCR}B11-vol_total)<1,"OK","CHECK")', "Haul_Cycle B11 vs vol_total"),
        ("Class 1 destination mix sums to 1", '=IF(ABS(mix_c1_wrl+mix_c1_tsf+mix_c1_inf-1)<0.001,"OK","CHECK")', "Inputs"),
        ("Class 2 destination mix sums to 1", '=IF(ABS(mix_c2_wrl+mix_c2_tsf+mix_c2_inf-1)<0.001,"OK","CHECK")', "Inputs"),
        ("Class 3 destination mix sums to 1", '=IF(ABS(mix_c3_wrl+mix_c3_tsf+mix_c3_inf-1)<0.001,"OK","CHECK")', "Inputs"),
        ("Class 4 destination mix sums to 1", '=IF(ABS(mix_c4_wrl+mix_c4_tsf+mix_c4_inf-1)<0.001,"OK","CHECK")', "Inputs"),
        ("Stratigraphy depths are increasing", '=IF(AND(depth_sand<depth_mid,depth_mid<depth_total),"OK","CHECK")', "Inputs"),
        ("Selected trucks cover in-service requirement", '=IF(sel_trucks>=trucks_inservice,"OK","BELOW REQUIRED")', "Fleet_Register override vs Fleet_Calc"),
        ("Selected excavators cover requirement", '=IF(sel_ex>=ex_rec,"OK","BELOW REQUIRED")', ""),
        ("Selected drill rigs cover requirement", '=IF(sel_drills>=drills_rec,"OK","BELOW REQUIRED")', ""),
        ("Selected MPU cover requirement", '=IF(sel_mpu>=mpu_rec,"OK","BELOW REQUIRED")', ""),
        ("All volume scheduled within 48 months", '=IF(sched_unscheduled<1,"OK","EXTEND / ADD FLEET")', "Schedule E6"),
        ("Schedule finishes within target duration", '=IF(sched_months<=dur_months,"OK","LATER THAN TARGET")', "Schedule E5 vs dur_months"),
        ("Demobilisation completes before Separable Part 1 Completion Date", '=IF(sched_demob_end<=completion_date,"OK","LATE")', "Schedule K4 vs completion_date"),
        ("No month needs more truck hours than available", f'=IF(COUNTIF(Schedule!AE{S0}:AE{S1},"?*")=0,"OK","CHECK")', "Schedule flag column"),
    ]
    for i, (a, f, d) in enumerate(checks):
        wk.cell(row=4 + i, column=1, value=a)
        wk.cell(row=4 + i, column=2, value=f)
        wk.cell(row=4 + i, column=3, value=d)
    n = 4 + len(checks)
    wk.cell(row=n + 1, column=1, value="Overall").font = BOLD
    wk.cell(row=n + 1, column=2, value=f'=IF(COUNTIF(B4:B{n-1},"OK")=ROWS(B4:B{n-1}),"ALL OK","REVIEW")').font = BOLD
    wk.conditional_formatting.add(f"B4:B{n+1}", FormulaRule(formula=['OR(B4="OK",B4="ALL OK")'], fill=PatternFill("solid", bgColor="C6EFCE")))
    wk.conditional_formatting.add(f"B4:B{n+1}", FormulaRule(formula=['AND(B4<>"OK",B4<>"ALL OK")'], fill=PatternFill("solid", bgColor="FFC7CE")))
    wk.column_dimensions["A"].width = 64
    wk.column_dimensions["B"].width = 22
    wk.column_dimensions["C"].width = 50

    # ------------------------------------------------------------ README
    lines = [
        (cfg["title"], Font(bold=True, size=14)),
        ("Indicative fleet sizing and mining schedule for the Winu pre-strip (ITT WIN-CON-EPC-001, Australian Contractor Scope of Work s6.2). Built from the ITT design parameters plus the engineering assumptions listed on the Inputs sheet.", None),
        ("", None),
        ("How to use", BOLD),
        ("1. Change the volume, duration, haul distances, productivities or any ratio on the Inputs sheet (yellow cells). All sheets recalculate.", None),
        ("2. To test a specific fleet, type quantities in the Override column on Fleet_Register (blank = calculated). The Schedule uses the selected quantities, so a smaller fleet lengthens the schedule and a larger one shortens it.", None),
        ("3. To impose your own production profile, type monthly volumes in column M of the Schedule. Months flagged red exceed fleet capacity.", None),
        ("4. Enter the quantities from the Client Supplied Fleet List (C-WN-0000-G-LST-00005) in the last columns of Fleet_Register to see the difference to this design.", None),
        ("5. Check the Checks sheet. Sensitivity shows trucks and rigs needed for other durations and haul distances.", None),
        ("", None),
        ("Sheets", BOLD),
        ("Inputs - all assumptions with source or ASSUMPTION label. Haul_Cycle - material classes, cycle times and productivity. Fleet_Calc - required hours and unit counts. Fleet_Register - full primary and ancillary list. Schedule - monthly plan. Gantt - bar chart. Sensitivity. Checks.", None),
        ("", None),
        ("Limits", BOLD),
        ("The ITT gives no pre-strip duration, haul distances, destination volumes or fleet quantities. Those are assumptions here and are labelled as such. Replace them from the Haul Infinity model (C0007-REF-00340), the waste rock landform design and the Three Month Production Plan before relying on the output.", None),
        ("Material is mined top-down in sequence. A real plan works several benches and both cutbacks at once, so monthly material splits are indicative. Each month's capacity uses the slower of the material class at the start of the month and the next class, so months that cross a boundary are slightly conservative.", None),
        ("Primary HME is marked Company free-issue (assumed). The ITT states the free-issued fleet is the list in C-WN-0000-G-LST-00005 and that the Contractor remains responsible for confirming it is sufficient (s10.2).", None),
        ("Fuel, people and light vehicle figures are order-of-magnitude allowances.", None),
    ]
    for i, (t, f) in enumerate(lines, start=1):
        c = rd.cell(row=i, column=1, value=t)
        c.alignment = WRAP
        if f:
            c.font = f
    rd.column_dimensions["A"].width = 150

    order = ["README", "Inputs", "Fleet_Register", "Schedule", "Gantt", "Fleet_Calc", "Haul_Cycle", "Sensitivity", "Checks"]
    wb._sheets = [wb[s] for s in order]
    wb.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--output")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--carry-forward", action="store_true",
                    help="keep fleet overrides, client fleet list quantities and monthly volume overrides from the existing output")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    out = a.output or cfg["output_default"]
    if Path(out).exists() and not (a.force or a.carry_forward):
        sys.exit(f"{out} exists. Use --force to overwrite or --carry-forward to rebuild and keep typed values.")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    build(cfg, out, a.carry_forward)
    print("wrote", out)


if __name__ == "__main__":
    main()
