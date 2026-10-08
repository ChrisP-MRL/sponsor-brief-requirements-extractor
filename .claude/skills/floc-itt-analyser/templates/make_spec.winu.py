"""Winu-specific FLOC spec generator (writes build/winu_floc_spec.json).
Hooks are (pdf_page, regex) pairs resolved against sources.json by resolve_spec.py.
"""
import json
import re
import sys

SRC = json.load(open("build/sources.json", encoding="utf8"))
SP1 = "Contractor - Separable Part 1"
SP2 = "Contractor - Separable Part 2"
BOTH = "Contractor - SP1 and SP2"
PRELIM = "Contractor - Preliminaries (Schedule A.1, apportioned SP1/SP2)"
COMP = "Company"
OTH = "Others (not the Contractor)"

keys = set()


def N(name, key, p=None, kw=None, status="In scope", disc=(), resp=BOTH, maps=(), kids=(), note=None, assumption=False):
    assert key not in keys, key
    keys.add(key)
    d = {"key": key, "name": name, "status": status, "disciplines": list(disc), "responsibility": resp,
         "children": list(kids)}
    if p:
        d["primary"] = {"page": p, "kw": kw}
    if maps:
        d["maps"] = []
        for m in maps:
            e = {"pages": [m[0], m[1]]}
            if len(m) > 2 and m[2]:
                e["kw"] = m[2]
            if len(m) > 3 and m[3]:
                e["types"] = m[3]
            if len(m) > 4 and m[4]:
                e["default"] = True
            d["maps"].append(e)
    if note:
        d["notes"] = note
    if assumption:
        d["assumption"] = True
    return d


def default(a, b):
    return (a, b, None, None, True)


def item_nodes(prefix, pattern, nums, resp, disc, group_key, page_lo, page_hi, status="In scope"):
    """L5 nodes for numbered building/system items ('MSA item 5: Mine Warehouse')."""
    out = []
    for n in nums:
        rx = re.compile(rf"{pattern} item {n}:", re.I)
        hit = next((s for s in SRC if page_lo <= s["pdf_page"] <= page_hi and rx.search(s["title"] or "")), None)
        if not hit:
            raise SystemExit(f"missing {pattern} item {n}")
        nm = re.sub(rf"^{pattern} item {n}:\s*", "", hit["title"], flags=re.I)
        out.append(N(f"{prefix} item {n}: {nm}", f"{group_key}_{n}", hit["pdf_page"], rf"{pattern} item {n}:", status=status,
                     disc=disc, resp=resp, maps=[(page_lo, page_hi, rf"\b{pattern} item {n}:")]))
    return out


# ------------------------------------------------------------------ Shared / preliminaries
prelims = N("Site-wide Preliminaries and Shared Services", "PRE", 328, "SP1 - Preliminaries", resp=PRELIM,
            note="Cross-cutting indirects priced in Schedule A.1 Table A.1.1 (SP1 and SP2 Preliminaries). Allocated to physical FLOCs by Allocation_Rules; do not double-count in area FLOCs.",
            kids=[
    N("Project management, engineering, survey, geotechnical interface, QA/QC and reporting", "PRE_PM", 214, "management, engineering, supervision",
      disc=["Project management", "Survey", "QA/QC"], resp=PRELIM, maps=[(214, 217), (306, 307), (313, 314)]),
    N("Mobilisation, travel and Site establishment", "PRE_MOB", 218, "Mobilisation includes all airfares",
      disc=["Logistics"], resp=PRELIM, maps=[(218, 219, r"5\.1|5\.2|Flights|Mobilisation"), (358, 360, r"Flights"), (397, 397, r"Flights|air|Perth")]),
    N("Construction and fly camps, and accommodation", "PRE_CAMP", 220, "Option B: Contractor-provided", resp=PRELIM,
      disc=["Accommodation"], maps=[(219, 222), (334, 334, r"Camp"), (356, 358, r"ccommodation|Camp"), (394, 397, r"ccommodation|camp|Camp|room|messing|Messing")],
      kids=[
        N("Existing 175-person camp (125 rooms available to the Contractor at start-up)", "CAMP_EXIST", 214, "existing camp",
          resp="Company operates; Contractor occupies and pays A$200 per person per day", maps=[(214, 214, r"Accommodation|camp")]),
        N("Fly camp(s) on Mine Access Road", "CAMP_FLY", 219, "Fly camp"),
        N("Construction camp adjacent to Permanent Village", "CAMP_ADJ", 219, "adjacent to Permanent Village"),
        N("Option A - Company free-issued camps (priced option)", "CAMP_A", 220, "Option A: Company free-issued camps", status="Provisional",
          resp="Company / Offshore EPF Contractor supplies; Contractor installs and maintains", maps=[(220, 222, r"Option A|5\.3\.1")]),
        N("Option B - Contractor-provided camps (priced option)", "CAMP_B", 220, "Option B: Contractor-provided", status="Provisional",
          resp=PRELIM, maps=[(220, 222, r"Option B|5\.3\.2")]),
      ]),
    N("Laydown areas and temporary construction facilities", "PRE_TEMP", 223, "All temporary construction facilities and utilities", resp=PRELIM,
      disc=["Temporary facilities"], maps=[(222, 225, r"5\.[456]|Laydown|Fuel|Temporary|Site Office|Workshop|Equipment Assembly|Explosives")],
      kids=[
        N("Laydown areas", "TEMP_LAY", 222, "Company designates laydown areas", maps=[(222, 223, r"Laydown")]),
        N("Contractor and Company site offices, workshops and operational facilities", "TEMP_OFF", 223, "temporary construction facilities", maps=[(223, 224, r"5\.6\.[1-4]|Office|Workshop")]),
        N("Fuel storage and distribution", "TEMP_FUEL", 222, "Company supplies fuel free of charge", maps=[(222, 222, r"Fuel|5\.4"), (346, 347, r"Fuel"), (103, 105, r"Fuel")]),
        N("Temporary explosives magazine and ANFO storage", "TEMP_EXP", 225, "explosives, detonators", maps=[(225, 225, r"5\.6\.5|xplosive")]),
      ]),
    N("Construction water supply and management", "PRE_WATER", 225, "Defects, leaks, erosion", resp=PRELIM,
      disc=["Water"], maps=[(225, 227, r"5\.7|[Cc]onstruction [Ww]ater|[Bb]ore"), (339, 339, r"[Ww]ater")]),
    N("Temporary communications, IT and radio", "PRE_COMMS", 227, "TETRA", resp=PRELIM, disc=["Communications", "IT"],
      maps=[(227, 228, r"5\.8|Radio|Internet|IT,")]),
    N("Plant and equipment fleet (pre-strip HME and construction fleet options)", "PRE_FLEET", 302, "Contractor supplies, mobilises, operates", resp=BOTH,
      disc=["Plant and equipment"], maps=[default(302, 306)],
      kids=[
        N("Pre-strip heavy mining equipment fleet (Company free-issue; Contractor operates and maintains)", "FLEET_HME", 302, "Pre-Strip heavy mining equipment fleet is Company free-issue",
          resp="Company supplies; Contractor operates, maintains, fuels", maps=[(302, 304, r"10\.2|Pre-Strip|HME|Go-Line|Acceptance"), (332, 333, r"HME")]),
        N("Construction fleet - Option 1 (Contractor-supplied, priced option)", "FLEET_OPT1", 304, "Option 1 - Contractor-Supplied Construction Fleet", status="Provisional",
          maps=[(304, 304, r"Option 1"), (332, 332, r"Option 1")]),
        N("Construction fleet - Option 2 (Company free-issued, priced option)", "FLEET_OPT2", 304, "Option 2 - Company Free-Issued Construction Fleet", status="Provisional",
          resp="Company / Offshore EPF Contractor supplies; Contractor operates", maps=[(304, 306, r"Option 2|10\.[456]"), (332, 333, r"Option 2")]),
      ]),
    N("Transport, logistics and materials management", "PRE_TL", 295, "Transport/logistics for all Project materials", resp=PRELIM,
      disc=["Logistics"], maps=[(295, 302, r"^9|\s9\.|Transport|Logistics|Port|Storage|Surplus|Spares|Materials|Customs|Traffic"), (625, 631, None)],
      kids=[
        N("Onshore transport and logistics (Port Hedland port battery limit to Site)", "TL_ONSHORE", 297, "Route surveys", maps=[(296, 301, r"9\.[2-9]|9\.1[0-5]|Port|INCOTERM|Route|Traffic|Vessel|Customs")]),
        N("Materials management, storage, spares and surplus", "TL_MAT", 301, "Contractor provides storage facilities", maps=[(301, 302, r"9\.16|Storage|Surplus|Spares")]),
      ]),
    N("Site management, security, signage, lighting and waste", "PRE_SITE", 307, "Contractor plans, establishes, operates, secures", resp=PRELIM,
      disc=["Site management"], maps=[default(307, 313)],
      kids=[
        N("Site security and access control", "SITE_SEC", 310, "Contractor secures its facilities", maps=[(309, 311, r"12\.7|Security|Gate|Access control")]),
        N("Waste management and off-Site disposal", "SITE_WASTE", 312, "Off-Site removal of construction", maps=[(311, 312, r"12\.9|Waste")]),
      ]),
    N("Temporary works", "PRE_TW", 313, "Contractor designs and provides all temporary works", resp=PRELIM, disc=["Temporary works"],
      maps=[(313, 313, r"12\.10|Temporary")]),
    N("Interface management and simultaneous operations (SIMOPS)", "PRE_IFACE", 292, "Interface management meetings", resp=PRELIM,
      disc=["Interface"], maps=[(292, 295)]),
    N("Health, safety, environment, security and community (HSESC)", "PRE_HSE", 314, "HSE", resp=PRELIM,
      disc=["HSE"], maps=[(314, 320), (407, 595)]),
    N("Pre-commissioning, commissioning support and handover", "PRE_COMM", 321, "Support Company/Others commissioning", resp=PRELIM,
      disc=["Commissioning"], maps=[(320, 321, r"(?:^|\s)15(?:\.\d)?\s")]),
    N("Demobilisation and rehabilitation", "PRE_DEMOB", 322, "Demobilise all personnel, plant, tools", resp=PRELIM,
      disc=["Demobilisation"], maps=[(321, 322, r"(?:^|\s)16\s"), (218, 218, r"4\.8|Progressive"), (516, 518, r"ehabilitation")]),
    N("Company Supplied Items - receipt, custody, storage and installation (supply by Company)", "PRE_FREE", 215, "Receipt, custody, storage and installation of Company Supplied Items", resp="Company supplies; Contractor handles and installs",
      note="Supply is by the Company (excluded from Contract Price); handling and installation costs sit with the Contractor.",
      maps=[(322, 322, r"17 Company|Company supplies|Company provides"), (196, 198, None)]),
    N("Concrete supply, reinforcement and cast-in items (site-wide shared)", "PRE_CONC", 262, "batch plant", resp=SP1, disc=["Civil", "Concrete"],
      note="Shared concrete supply pool; allocate to area FLOCs by concrete volume (Allocation_Rules AR-07).",
      maps=[default(260, 266)],
      kids=[
        N("Concrete batch plant (adjacent to MPP/MSA)", "CONC_BATCH", 262, "Concrete batch plant", maps=[(262, 263, r"[Bb]atch")]),
        N("Reinforcing, cast-in items and consumables (Company free-issues rebar, mesh, conduit, earth bonds, piping)", "CONC_REBAR", 263, "Company supplies all reinforcing bar", maps=[(263, 265, r"6\.4\.[4-9]|6\.4\.1[0-2]|[Rr]ebar|Reinforc|Cast-in|Holding|Bollard|Consumable")]),
      ]),
    N("SP2 general requirements (common structural, mechanical, piping and E&I scope, welding, cable, earthing, battery limits)", "PRE_SP2GEN", 268, "SP2 facilities", resp=SP2,
      disc=["Structural", "Mechanical", "Electrical"], maps=[default(268, 292)]),
    N("Excluded scope - non-physical (design, survey control, geotechnical support, third-party battery limits)", "PRE_EXCL", 322, "Excluded: permanent works design",
      status="Excluded", resp=OTH, maps=[(322, 323, r"Excluded|18 Work Excluded|Work Excluded"), default(322, 323)]),
    N("Contract, commercial and administration (non-physical)", "PRE_COMMERCIAL", 53, "Schedule A.1", resp=BOTH,
      note="Tender requirements, contract conditions, securities, insurance, LDs, price adjustment, payment, pricing schedules and appendices. Carries no physical scope.",
      maps=[(1, 46, None, None), (47, 156, None, None), (324, 391, None, None), (392, 406, None, None), (596, 638, None, None), (157, 198, None, None)]),
])

# ------------------------------------------------------------------ Site development
site_dev = N("Site Development - Clearing, Topsoil and Borrow (site-wide earthworks)", "SITE", 238, "Clearing, grubbing and topsoil stripping measured", resp=SP1,
             disc=["Civil", "Earthworks"], maps=[default(228, 240), (238, 240, r"6\.1\.[345]|Clearing|Topsoil|Borrow")], kids=[
    N("Clearing, grubbing and topsoil removal", "SITE_CLEAR", 238, "Clearing, grubbing and topsoil stripping measured", maps=[(238, 239, r"6\.1\.3|Clearing|Grubbing")]),
    N("Topsoil stripping and stockpiling", "SITE_TOP", 239, "opsoil", maps=[(239, 240, r"6\.1\.4|Topsoil")]),
    N("Borrow development (borrow pits)", "SITE_BORROW", 240, "Borrow pits within Mine", maps=[(240, 240, r"6\.1\.5|Borrow"), (183, 183, r"Borrow")]),
])

# ------------------------------------------------------------------ Mine Access Road
mar = N("Mine Access Road and Site Access (Company WBS 5100/5150)", "MAR", 230, "Work Area 1 - Mine Access Road", resp=SP1, disc=["Civil", "Earthworks"],
        maps=[(230, 231, r"Work Area 1"), (170, 181, r"5150|Access Road"), (213, 214, r"Access Road|[Tt]rack|[Dd]une")], kids=[
    N("Mine Access Road - 182 km sealed road (earthworks and pavement)", "MAR_ROAD", 230, "Work Area 1 - Mine Access Road, 182 km sealed", maps=[(230, 231, r"Work Area 1|Mine Access Road"), (170, 181, r"Access Road")]),
    N("Highway intersections (Great Northern Highway / Nyangumarta Highway)", "MAR_INT", 230, "Great Northern Highway intersection", maps=[(180, 180, r"intersection")]),
    N("Access road rest areas 1 to 3", "MAR_REST", 181, "Rest Areas"),
    N("Drainage structures - culverts and floodways", "MAR_DRAIN", 181, "culvert schedule"),
    N("Weed and seed facility and weighbridge (WBS 5100 mechanical and E&I)", "MAR_WEED", 279, "Weed and seed facility", resp=SP2, disc=["Mechanical", "Electrical"],
      maps=[(279, 279, r"Mine Access Road"), (283, 284, r"Mine Access Road|Weigh|Weed")]),
    N("Existing Site Access Road, tracks and dune crossings (use, maintenance and reinstatement)", "MAR_EXIST", 213, "Existing tracks, two dune crossings", maps=[(213, 214, None)]),
    N("Concrete - Mine Access Road (WBS 5100 series)", "MAR_CONC", 261, "Concrete work area - Mine Access Road", maps=[(261, 261, r"Mine Access Road")]),
])

# ------------------------------------------------------------------ Permanent Village
vil_acc = item_nodes("Village", "Village", [1, 2, 3], SP2, ["Structural", "Architectural"], "VIL_ACC", 272, 273)
vil_cen = item_nodes("Village", "Village", [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], SP2, ["Structural", "Architectural"], "VIL_CEN", 272, 274)
vil_ext = item_nodes("Village", "Village", [17, 18, 25, 26, 27], SP2, ["Civil", "Structural"], "VIL_EXT", 272, 274)
vil_wtr = item_nodes("Village", "Village", [19, 20], SP2, ["Mechanical", "Piping"], "VIL_WTR", 272, 274)
vil_ww = item_nodes("Village", "Village", [21, 22], SP2, ["Mechanical", "Piping"], "VIL_WW", 272, 274)
vil_pwr = item_nodes("Village", "Village", [23, 24], SP2, ["Electrical", "Communications"], "VIL_PWR", 272, 274)
village = N("Permanent Village (Company WBS 5600 series)", "VIL", 231, "Work Area 2 - Permanent Village bulk earthworks", resp=BOTH,
            disc=["Civil", "Structural", "Mechanical", "Electrical"],
            maps=[(231, 232, r"Work Area 2"), (182, 190, r"5650|5610|5680|5684|Camp|Village|Accommodation"), (261, 261, r"Village"), (265, 265, r"Village")], kids=[
    N("Village bulk earthworks, access roads and laydown (WA2; Company WBS 5610)", "VIL_EW", 231, "Work Area 2 - Permanent Village bulk earthworks", resp=SP1,
      disc=["Civil", "Earthworks"], maps=[(231, 232, r"Village|Camp Access|Pedestrian"), (182, 185, r"5610|Permanent Camp|Camp Access")],
      kids=[
        N("Camp Access Road and waste management facilities layout", "VIL_ROAD", 232, "Camp Access Road and Waste Management Facilities layout", resp=SP1),
        N("Unsealed gravel access road between Mine Access Road and Village", "VIL_GRAVEL", 231, "Unsealed gravel access road", resp=SP1),
        N("Pedestrian access track to sacred tree grove", "VIL_PED", 231, "Pedestrian access track", resp=SP1),
      ]),
    N("Village accommodation modules", "VIL_ACCOM", 272, "Village item 1:", disc=["Structural", "Architectural"], resp=SP2, kids=vil_acc),
    N("Village central, administration, mess and support facilities", "VIL_CENTRAL", 273, "Village item 4:", disc=["Structural", "Architectural"], resp=SP2, kids=vil_cen),
    N("Village external works (court, yarning circle, parking, walking track)", "VIL_EXTERNAL", 273, "Village item 17:", disc=["Civil", "Structural"], resp=SP2, kids=vil_ext),
    N("Village potable and fire water (treatment, storage, distribution)", "VIL_WATER", 273, "Village item 19:", disc=["Mechanical", "Piping"], resp=SP2, kids=vil_wtr,
      maps=[(271, 271, r"Water Treatment Plant"), (280, 280, r"Village Water Treatment"), (283, 283, r"Village Water Treatment"), (186, 188, r"P-GAD|hydraulic")]),
    N("Village wastewater collection, treatment plant and spray field", "VIL_SEWAGE", 273, "Village item 21:", disc=["Mechanical", "Piping"], resp=SP2, kids=vil_ww,
      maps=[(271, 271, r"Sewage"), (280, 280, r"Sewage"), (283, 283, r"Sewage"), (231, 231, r"Spray"), (265, 265, r"[Ss]pray"), (185, 185, r"5684|Sewerage")]),
    N("Village power distribution, emergency back-up power and communications network", "VIL_POWER", 273, "Village item 23:", disc=["Electrical", "Communications"], resp=SP2, kids=vil_pwr,
      maps=[(283, 283, r"back-up power|Permanent Village"), (187, 187, r"electrical|comms|415V")]),
    N("Village modular building structural works (factory versus on-site fit-out split)", "VIL_MOD", 273, "factory vs on-site split", resp=SP2, disc=["Structural"],
      maps=[(273, 275, r"factory|Factory|HVAC|modular|Modular"), (186, 189, r"Village|Accommodation|structural|chassis")]),
    N("Village mechanical (HVAC) and E&I areas", "VIL_ME", 280, "Permanent Village (WBS 5600) mechanical areas", resp=SP2, disc=["Mechanical", "Electrical"],
      maps=[(280, 280, r"Village|5600"), (283, 283, r"Village|5600")]),
    N("Concrete - Permanent Village (WBS 5600 series)", "VIL_CONC", 261, "Concrete work area - Permanent Village", resp=SP1, maps=[(261, 261, r"Village|Communications Towers")]),
    N("Village buried utilities (incl. tie-in at IPP battery limit)", "VIL_BU", 265, "Permanent Village - utilities", resp=SP1, maps=[(265, 265, r"Village")]),
])

# ------------------------------------------------------------------ MSA
msa_work = item_nodes("MSA", "MSA", [1, 2, 3, 4, 7, 8, 9], SP2, ["Structural"], "MSA_WRK", 271, 272)
msa_wh = item_nodes("MSA", "MSA", [5, 11, 17, 25, 26], SP2, ["Structural"], "MSA_WH", 271, 272)
msa_fuel = item_nodes("MSA", "MSA", [6, 10], SP2, ["Structural", "Mechanical"], "MSA_FUEL", 271, 272)
msa_ops = item_nodes("MSA", "MSA", [12, 13, 14, 15, 16, 18, 19, 20, 21, 23], SP2, ["Structural", "Architectural"], "MSA_OPS", 271, 272)
msa_dc = item_nodes("MSA", "MSA", [22, 24], SP2, ["Structural", "Electrical"], "MSA_DC", 271, 272)
msa = N("Mine Services Area - MSA (Company WBS 2900 series)", "MSA", 270, "Mine Services Area (WBS 2900 series)", resp=BOTH,
        disc=["Civil", "Structural", "Mechanical", "Electrical"],
        maps=[(189, 190, r"2900|2910|2920|2940|2970|Mine Services|MSA"), (232, 232, r"Mine Services Area"), (265, 265, r"Mining Services Area|MSA"), (261, 261, r"Mine Services Area")], kids=[
    N("MSA bulk earthworks (WBS 2810)", "MSA_EW", 232, "Work Area 3 - Mine Services Area bulk earthworks", resp=SP1, disc=["Civil", "Earthworks"], maps=[(182, 184, r"MSA|Mine Services")]),
    N("MSA workshops, tool storage and tyre change facilities", "MSA_WORK", 271, "MSA item 1:", disc=["Structural"], resp=SP2, kids=msa_work),
    N("MSA warehouse, storage yards and laydown", "MSA_STORE", 271, "MSA item 5:", disc=["Structural"], resp=SP2, kids=msa_wh),
    N("MSA fuel facilities (bulk fuel storage and refuelling office)", "MSA_FUELS", 271, "MSA item 6:", disc=["Structural", "Mechanical"], resp=SP2, kids=msa_fuel),
    N("MSA operations, administration and amenities", "MSA_OPSF", 272, "MSA item 12:", disc=["Structural", "Architectural"], resp=SP2, kids=msa_ops),
    N("MSA data centre and laboratory (excluding laboratory equipment)", "MSA_DCLAB", 272, "MSA item 22:", disc=["Structural", "Electrical"], resp=SP2, kids=msa_dc),
    N("MSA mechanical and piping systems (workshops, tyre change, bulk fuel, warehouse, oily water separators, containerised WWTP)", "MSA_MECH", 279, "MSA sub-area - HME Workshop", resp=SP2,
      disc=["Mechanical", "Piping"], maps=[(279, 279, r"MSA sub-area")]),
    N("MSA electrical and instrumentation (sub-area E&I)", "MSA_EI", 283, "E&I MSA sub-area - HME Workshop", resp=SP2, disc=["Electrical", "Instrumentation"], maps=[(283, 283, r"MSA sub-area")]),
    N("MSA buried utilities", "MSA_BU", 265, "Mining Services Area (MSA) - utilities work area", resp=SP1, disc=["Civil", "Piping"]),
    N("Concrete - MSA (WBS 2900 series)", "MSA_CONC", 261, "Concrete work area - Mine Services Area", resp=SP1),
    N("MSA laboratory equipment (Company; excluded)", "MSA_LABEQ", 272, "Laboratory equipment excluded", status="Excluded", resp=COMP, maps=[(323, 323, r"aboratory")]),
    N("MSA communications systems designed by others", "MSA_COMMS_EX", 286, "MSA communications systems designed by others", status="Excluded", resp=OTH),
])

# ------------------------------------------------------------------ MPP
mpp = N("Mineral Processing Plant - MPP enabling works (Company WBS 2000/2810)", "MPP", 232, "Work Area 3 - Mineral Processing Plant bulk earthworks", resp=SP1,
        disc=["Civil", "Earthworks"],
        maps=[(232, 232, r"Mineral Processing Plant|Process Plant"), (182, 184, r"2810|Process Plant|Concentrate"), (252, 252, r"ROM|[Cc]rusher"), (233, 233, r"ROM"), (261, 261, r"Mineral Process Plant")], kids=[
    N("MPP bulk earthworks and in-plant roads (WBS 2810)", "MPP_EW", 232, "Work Area 3 - Mineral Processing Plant bulk earthworks", maps=[(182, 184, r"2810|Process Plant")]),
    N("Concentrate loop road", "MPP_LOOP", 182, "concentrate loop road", maps=[(182, 182, r"Concentrate")]),
    N("ROM pad, ROM wall and dump pocket (earthworks)", "MPP_ROM", 233, "ROM Wall (proposed) and dump pocket", maps=[(233, 233, r"ROM"), (252, 252, r"ROM|skyway|[Ss]tockpile fingers"), (257, 257, r"ROM")]),
    N("Concrete - MPP (WBS 2000 series)", "MPP_CONC", 261, "Concrete work area - Mineral Process Plant", resp=SP1),
    N("MPP buried utilities", "MPP_BU", 265, "Mineral Processing Plant (MPP) - utilities work area", resp=SP1, disc=["Civil", "Piping"]),
    N("Process plant above top of concrete incl. ROM pocket mechanical (by MPP EPC Contractor)", "MPP_EX", 322, "top-of-concrete MPP process plant", status="Excluded", resp=OTH,
      maps=[(269, 269, r"Mineral process plant excluded"), (233, 233, r"mechanical equipment install")]),
    N("MPP electrical, instrumentation and communications systems (excluded)", "MPP_EI_EX", 323, "MPP electrical, instrumentation and communications", status="Excluded", resp=OTH),
    N("Primary crusher select-fill pocket (completed by others)", "MPP_CRUSH_EX", 252, "Primary Crusher select-fill pocket excluded", status="Excluded", resp=OTH),
])

# ------------------------------------------------------------------ IPP
ipp = N("Power Generation Area - IPP enabling earthworks (thermal power station, wind farm, solar and BESS)", "IPP", 232, "Independent Power Provider (IPP) area earthworks", resp=SP1,
        disc=["Civil", "Earthworks"], maps=[(233, 237, r"IPP|Power Station|Wind|Solar|BESS|[Pp]ower"), (185, 185, r"5500|Wind"), (232, 232, r"IPP")], kids=[
    N("Power station (thermal) pad", "IPP_PAD", 233, "Power Station (thermal generation facility) pad", maps=[(233, 233, r"Power Station")]),
    N("Wind farm development areas and road corridors (WBS 5500)", "IPP_WIND", 233, "Wind farm development areas", maps=[(185, 185, r"Wind")]),
    N("Solar farm and BESS development areas", "IPP_SOLAR", 233, "Solar farm and BESS development areas", maps=[(237, 237, r"Solar")]),
    N("Concrete supply to the IPP Contractor (recharge model to be established)", "IPP_CONC", 263, "Recharge model to be established for IPP concrete", status="Provisional", resp="Contractor supplies; IPP Contractor recharged"),
    N("IPP final site preparation, internal roads and equipment (by IPP Contractor)", "IPP_EX", 234, "IPP Contractor completes final site prep", status="Excluded", resp="IPP Contractor", maps=[(234, 234, r"IPP")]),
    N("Conduits for incoming power from the IPP (excluded)", "IPP_COND_EX", 268, "Conduits for incoming power from the IPP excluded", status="Excluded", resp="IPP Contractor"),
])

# ------------------------------------------------------------------ Stockpiles & surface water
stk = N("Ore Stockpiles and Surface Water Management (Company WBS 1810; WA4)", "STK", 234, "Work Area 4 - Stockpiles and Surface Water Management", resp=SP1,
        disc=["Civil", "Earthworks"], maps=[(234, 235, r"Work Area 4|Pond|Dam|stockpile|Stockpile"), (184, 184, r"Stockpile Berms|1810"), (254, 254, r"Mudstone|6\.2\.1[234]"), (183, 183, r"Stockpile")], kids=[
    N("Primary sulphides stockpile (< 8 years)", "STK_PS8", 234, "Primary Sulphides stockpile (< 8 years storage)"),
    N("Primary sulphides stockpile (> 8 years) incl. HDPE liner", "STK_PS8P", 234, r"Primary Sulphides stockpile \(> 8 years\)"),
    N("Low grade primary sulphides stockpile (> 8 years) incl. HDPE liner", "STK_LG", 234, "Low grade primary sulphides stockpile"),
    N("Leach cap stockpile", "STK_LEACH", 234, "Leach cap stockpile"),
    N("Clean water bunds", "STK_BUND", 234, "Clean Water bunds"),
    N("Mudstone stockpile bases", "STK_MUD", 254, "Mudstone", maps=[(254, 254, r"Mudstone|6\.2\.12")]),
    N("Mine stockpile detention ponds 1 and 2 (HDPE lined)", "STK_DET", 234, r"Mine Stockpile Detention Ponds 1 and 2"),
    N("Process plant and MSA stormwater ponds", "STK_STORM", 235, "Process Plant Stormwater Pond", maps=[(235, 235, r"MSA Stormwater|Stormwater Pond"), (232, 232, r"Stormwater")]),
    N("Clean Water Pond / Clean Water Dam", "STK_CWP", 235, "Clean Water Dam", maps=[(232, 233, r"Clean Water")]),
    N("Pit (Mine) Dewatering Pond", "STK_PDP", 235, "Pit Dewatering Pond", maps=[(254, 254, r"Dewatering Pond")]),
])

# ------------------------------------------------------------------ Aerodrome
aer_bld = item_nodes("Aerodrome", "Aerodrome", [], SP2, [], "AER_X", 275, 275) if False else []
aerodrome = N("Aerodrome (Company WBS 5800/5880; WA5)", "AER", 235, "Work Area 5 - Aerodrome (air and land side)", resp=BOTH,
              disc=["Civil", "Structural", "Electrical"],
              maps=[(235, 236, r"Work Area 5|Aerodrome|Runway|Taxiway"), (190, 194, r"Aerodrome|Airport|Runway|Taxiway|PAPI|0000-G-DRG"), (182, 185, r"5880|Aerodrome|Airport"), (261, 261, r"Aerodrome"), (275, 275, r"Aerodrome"), (284, 284, r"Aerodrome"), (265, 265, r"Aerodrome"), (280, 280, r"Aerodrome")], kids=[
    N("Aerodrome access and loop roads (WBS 5880)", "AER_ROAD", 235, "Aerodrome access road", resp=SP1, maps=[(182, 185, r"5880|Airport access|Aerodrome access")]),
    N("Runway, taxiway and apron earthworks and pavements", "AER_AIR", 236, "Runway, taxiway and apron pavements", resp=SP1, disc=["Civil", "Earthworks"],
      maps=[(236, 236, None), (191, 194, r"runway|Runway|taxiway|apron|Apron|clearing|GA")]),
    N("Aerodrome laydown and temporary construction camp area", "AER_LAY", 235, "Aerodrome laydown areas", resp=SP1, maps=[(235, 235, r"laydown|camp")]),
    N("Aerodrome line marking and perimeter fencing", "AER_MARK", 193, "line marking", resp=SP1, maps=[(193, 193, r"marking|fencing")]),
    N("Aerodrome terminal facility and ancillary buildings", "AER_BLD", 275, "Aerodrome Terminal Facility", resp=SP2, disc=["Structural"], maps=[(275, 275, None), (280, 280, r"Terminal")],
      kids=[
        N("Aerodrome terminal facility (40 ft modular building)", "AER_TERM", 275, "Aerodrome Terminal Facility", resp=SP2),
        N("Aerodrome ablutions facility", "AER_ABL", 275, "Aerodrome ablutions facility", resp=SP2),
        N("Aerodrome passenger shade structure (steel frame)", "AER_SHADE", 275, "passenger shade structure", resp=SP2),
        N("Aerodrome shade structure and equipment storage shed (steel frame)", "AER_SHED", 275, "equipment storage shed", resp=SP2),
      ]),
    N("Aerodrome airfield lighting, aids and electrical (PAPI, wind direction indicator, control switchboard)", "AER_LIGHT", 194, "PAPI", resp=SP2, disc=["Electrical"], maps=[(284, 284, r"Aerodrome"), (194, 194, r"PAPI|lighting|LGHTING|WDI")]),
    N("Concrete - Aerodrome (WBS 5800 series)", "AER_CONC", 261, "Concrete work area - Aerodrome", resp=SP1),
])

# ------------------------------------------------------------------ TSF
tsf = N("Tailings Storage Facility - TSF Stage 0 (Company WBS 2300; WA6)", "TSF", 257, "Tailings Storage Facility (TSF) designed by WWL", resp=SP1,
        disc=["Civil", "Earthworks", "Geosynthetics"],
        maps=[(257, 260, None), (237, 237, r"Tailings"), (166, 170, r"TSF|2300|Tailings"), (261, 261, r"Tailings"), (232, 232, r"[Tt]ailings"), (254, 254, r"6\.2\.11|Tailings")], kids=[
    N("TSF Stage 0 impoundment earthworks (LST Cell 1B, HST Cells 1A/1B, dune fill)", "TSF_EW", 260, "Stage 0 impoundment", maps=[(257, 258, r"Detailed Scope|Stage 0|earthworks|Dune|dune|Zones|haul")]),
    N("TSF liner system (HDPE) and construction quality assurance interface", "TSF_LINER", 259, "Liner price basis", disc=["Geosynthetics"], maps=[(259, 260, r"[Ll]iner|CQA|Testing|6\.3\.7")]),
    N("TSF drainage (toe trench drains, underdrainage, LST1-B sump and riser)", "TSF_DRAIN", 258, "Over-liner underdrainage", maps=[(258, 258, r"[Dd]rain|sump|riser")]),
    N("Tailings pipeline corridors, collection sumps and LST thickener area", "TSF_CORR", 257, "HDPE-lined pipeline corridors", maps=[(257, 257, r"pipeline|corridor|sump|thickener"), (232, 232, r"Tailings Corridor"), (265, 265, r"LST Thickener"), (184, 184, r"Tailings|decant")]),
    N("Material supply to TSF (pit to transfer node; pricing split with Mine Pre-Strip)", "TSF_FILL", 253, "TSF Pricing Schedule covers haul beyond node", maps=[(253, 254, r"TSF|Tailings"), (260, 260, r"[Hh]aulage|battery limit")]),
    N("Concrete - TSF and tailings corridor (WBS 2300; riser rings, sump bases)", "TSF_CONC", 261, "Concrete work area - Tailings Storage Facility", resp=SP1, maps=[(261, 261, r"Tailings")]),
    N("TSF process and delivery systems (excluded)", "TSF_PROC_EX", 322, "TSF process and delivery systems and future TSF stages", status="Excluded", resp=OTH),
    N("TSF Stage 1 (Years 4-5) and later stages (by others in operations)", "TSF_LATER_EX", 257, "TSF Stage 1 (Years 4-5) and later stages excluded", status="Excluded", resp=OTH),
])

# ------------------------------------------------------------------ Explosives
exp = N("Explosives Facility (Company WBS 1950; WA7)", "EXP", 237, "Explosives Area", resp=BOTH, disc=["Civil", "Structural", "Mechanical", "Electrical"],
        maps=[(237, 238, r"Explosives"), (181, 184, r"[Ee]xplosives|1810-Y|1950"), (270, 271, r"Explosive"), (261, 261, r"Explosives"), (265, 265, r"Explosives"), (279, 279, r"Explosives"), (283, 283, r"Explosives")], kids=[
    N("Explosives area earthworks, access road and pond", "EXP_EW", 237, "Explosives Area access road", resp=SP1, disc=["Civil", "Earthworks"], maps=[(237, 238, r"Explosives"), (181, 184, r"[Ee]xplosives")]),
    N("Detonator and booster storage (containerised)", "EXP_DET", 271, "Detonator and booster storage", resp=SP2),
    N("AN prill storage (steel frame building, 250 t bulka bags)", "EXP_PRILL", 271, "AN Prill storage", resp=SP2),
    N("AN emulsion and AN inhibitor storage", "EXP_EMUL", 271, "AN emulsion and AN inhibitor storage", resp=SP2),
    N("Explosives Area mechanical and E&I (WBS 1950)", "EXP_ME", 279, "Mechanical work area - Explosives Area", resp=SP2, disc=["Mechanical", "Electrical"], maps=[(279, 279, r"Explosives"), (283, 283, r"Explosives")]),
    N("Concrete - Explosives Area (WBS 1950)", "EXP_CONC", 261, "Concrete work area - Explosives Area", resp=SP1),
    N("Explosives Area buried utilities", "EXP_BU", 265, "Explosives Facility work area (utilities)", resp=SP1),
    N("Explosive Facility firefighting and emergency rescue equipment (Company supplied)", "EXP_FIRE_EX", 271, "firefighting and emergency rescue equipment", status="Excluded", resp=COMP),
])

# ------------------------------------------------------------------ Mine Pre-Strip
mine = N("Mine Pre-Strip, Waste Rock Landform and Mine Roads (first two pit cutbacks)", "MIN", 240, "Mine Pre-Strip (overburden removal above ore body)", resp=SP1,
         disc=["Mining", "Earthworks"], maps=[(240, 257, None)], kids=[
    N("Mine planning and production control", "MIN_PLAN", 242, "6.2.3|production", maps=[(242, 243, r"6\.2\.3|Mine Planning|production")]),
    N("Drill and blast (overburden)", "MIN_DB", 243, "blast", maps=[(243, 245, r"6\.2\.4|[Dd]rill|[Bb]last|Stemming")]),
    N("Overburden mining and excavation requirements", "MIN_OB", 245, "overburden", maps=[(245, 246, r"6\.2\.[56]|[Oo]verburden|[Ee]xcavation")]),
    N("Mine haul roads (~17 km permanent) and roads to topsoil stockpiles", "MIN_ROAD", 252, "Permanent and long-term mine haul roads", maps=[(247, 248, r"6\.2\.7|Road"), (252, 252, r"6\.2\.10|[Hh]aul road")]),
    N("Waste Rock Landform (WRL) incl. PAF repository", "MIN_WRL", 248, "Waste Rock Landform (WRL) incl PAF repository", maps=[(248, 252, r"WRL|Waste Rock|6\.2\.8|PAF")]),
    N("Mining exclusion area, MIA zone and drill-and-blast facilities", "MIN_MEA", 256, "Mining Exclusion Area", maps=[(255, 257, r"6\.2\.1[78]|Exclusion|MIA|Battery|Interface")]),
    N("Fleet management system (FMS) integration", "MIN_FMS", 255, "FMS", maps=[(255, 255, r"6\.2\.16|FMS|Fleet Management")]),
    N("Mine drainage, dewatering and spillage protection (pre-strip)", "MIN_DRAIN", 254, "Mine Dewatering Pond", maps=[(254, 255, r"6\.2\.1[45]|[Dd]ewater|Spillage|Drainage")]),
])

# ------------------------------------------------------------------ Site-wide utilities
utl = N("Site-wide Utilities, Borefields and IS&T (Company WBS 1500)", "UTL", 280, "Site Wide Utilities - Dewatering and transfer water", resp=BOTH,
        disc=["Piping", "Electrical", "Communications"],
        maps=[(265, 268, None), (277, 292, r"Site Wide|Site-wide|Utilities|Tower|Data Centre|IS&T|Borefield|MAR|tower|Communications"), (183, 183, r"1500|Dewatering"), (227, 227, r"[Bb]ore"), (238, 238, r"[Bb]orefield|Topsoil and borefield")], kids=[
    N("Mine dewatering and transfer water (in-pit and ex-pit), raw water pipelines (WBS 1500)", "UTL_DEW", 280, "Site Wide Utilities - Dewatering and transfer water", disc=["Piping"],
      maps=[(284, 284, r"Dewatering and transfer"), (183, 183, r"1500|Dewatering"), (227, 227, r"[Bb]ore")]),
    N("Managed aquifer recharge (MAR) injection and recharge system", "UTL_MAR", 280, "MAR injection and recharge", disc=["Piping"], maps=[(284, 284, r"MAR")]),
    N("Raw water feed to Permanent Village; raw and process water", "UTL_RAW", 280, "Raw water feed to Permanent Village", disc=["Piping"], maps=[(280, 280, r"Raw water"), (284, 284, r"Raw water")]),
    N("Potable and fire water distribution", "UTL_POT", 280, "Site Wide Utilities - Potable water", disc=["Piping"], maps=[(280, 280, r"Potable|Fire water")]),
    N("Sewer and wastewater (pumped and gravity)", "UTL_SEW", 280, "Pumped and gravity sewer", disc=["Piping"]),
    N("Diesel and fuel transfer; plant and instrument air", "UTL_FUEL", 280, "Diesel and fuel transfer", disc=["Piping"], maps=[(280, 280, r"Plant and instrument air")]),
    N("Site-wide electrical power reticulation, E&I and lighting", "UTL_PWR", 284, "E&I area - Site Wide Utilities", disc=["Electrical", "Instrumentation"], maps=[(284, 292, r"Site Wide|Lighting|light pole|Cable|Earthing")]),
    N("Communications towers - 40 m and 80 m (Village and MSA)", "UTL_TOWER", 288, "80 m communications tower", disc=["Structural", "Communications"], maps=[(271, 271, r"Communications Tower"), (276, 276, r"Tower"), (280, 280, r"Communications Tower"), (284, 284, r"Communications Tower"), (288, 291, r"[Tt]ower")]),
    N("Data centres DC1 and DC2 (IS&T infrastructure)", "UTL_DC", 287, "Data centres (DC1 and DC2)", disc=["Communications", "Electrical"], maps=[(284, 284, r"Data Centres"), (287, 289, r"[Dd]ata [Cc]entre|IS&T")]),
    N("Borefield and topsoil access tracks", "UTL_TRACK", 238, "Borefield access track network", resp=SP1, disc=["Civil"], maps=[(237, 238, r"[Bb]orefield|[Tt]opsoil and borefield")]),
    N("Buried utilities - common requirements (common service trenches, quantity survey, battery limits)", "UTL_BU", 265, "Buried utilities consolidated into common service trenches", resp=SP1, disc=["Civil", "Piping"], maps=[(265, 268, None)]),
])

# ------------------------------------------------------------------ Landfill & waste
waste = N("Landfill and Waste Management Area (Company WBS 5400)", "WST", 212, "Landfill and waste management area", resp=BOTH, disc=["Civil", "Mechanical"],
          maps=[(182, 184, r"5400|Waste Management"), (232, 232, r"Waste Management"), (280, 280, r"Solids Waste"), (283, 283, r"Solids Waste"), (261, 261, r"Solids Waste")], kids=[
    N("Waste management area bulk earthworks (WBS 5400)", "WST_EW", 182, "Waste Management area (5400) bulk earthworks", resp=SP1, maps=[(182, 184, r"5400|Waste Management")]),
    N("Solids waste management facility (mechanical, E&I, concrete)", "WST_SWMF", 280, "Solids Waste Management Facility", resp=SP2, maps=[(280, 280, r"Solids Waste"), (283, 283, r"Solids Waste"), (261, 261, r"Solids Waste")]),
    N("On-Site landfill (operated by the Contractor until handover)", "WST_LF", 312, "On-Site landfill", resp=BOTH),
])

root = N("Winu Project - Australian Contractor Construction Works (Tender WIN-CON-EPC-001)", "ROOT", 211, "Mine: pre-strip", resp=BOTH,
         disc=["All"], maps=[(209, 212), (207, 208), default(199, 206)],
         kids=[prelims, site_dev, mar, village, msa, mpp, ipp, stk, aerodrome, tsf, exp, mine, utl, waste])

# ------------------------------------------------------------------ pricing, allocation, RFIs
pricing = [
    dict(schedule="A", item_no="Summary A.1", description="Lump Sum (Preliminaries SP1 + SP2)", unit="Lump sum", basis="Lump sum", page=327, kw="A.1 Lump Sum", floc_keys=["PRE"]),
    dict(schedule="A", item_no="Summary A.2.1", description="Schedule of Rates SP1 - Bulk Earthworks, Mine Pre-strip, TSF, Concrete, Buried Utilities", unit="Not stated", basis="Schedule of rates (remeasure)", page=327, kw="A.2.1 Schedule of Rates SP1", floc_keys=["SITE", "MAR", "MIN", "TSF", "STK", "PRE_CONC", "UTL_BU", "AER_EW" if False else "AER_AIR"]),
    dict(schedule="A", item_no="Summary A.2.2", description="Schedule of Rates SP2 - Above-ground SMP / EIC", unit="Not stated", basis="Schedule of rates (remeasure)", page=327, kw="A.2.2 Schedule of Rates SP2", floc_keys=["VIL_CENTRAL", "MSA_WORK", "MSA_MECH", "MSA_EI", "AER_BLD", "UTL_PWR"]),
    dict(schedule="A.1", item_no="A.1.1 SP1", description="SP1 Preliminaries (lump sum line)", unit="Lump sum", basis="Lump sum", page=328, kw="SP1 - Preliminaries", floc_keys=["PRE_PM", "PRE_MOB", "PRE_CAMP", "PRE_TEMP", "PRE_WATER", "PRE_COMMS", "PRE_TL", "PRE_SITE", "PRE_TW", "PRE_IFACE", "PRE_HSE", "PRE_COMM", "PRE_DEMOB"]),
    dict(schedule="A.1", item_no="A.1.1 SP2", description="SP2 Preliminaries (lump sum line)", unit="Lump sum", basis="Lump sum", page=328, kw="SP2 - Preliminaries", floc_keys=["PRE_PM", "PRE_MOB", "PRE_CAMP", "PRE_TEMP", "PRE_WATER", "PRE_COMMS", "PRE_TL", "PRE_SITE", "PRE_TW", "PRE_IFACE", "PRE_HSE", "PRE_COMM", "PRE_DEMOB"]),
    dict(schedule="A.1", item_no="Prelim (a)", description="Project management and administration", unit="Lump sum", basis="Lump sum", page=328, kw=r"Prelim \(a\) Project management", floc_keys=["PRE_PM"]),
    dict(schedule="A.1", item_no="Prelim (b)", description="Terms and conditions - securities, insurance, finance", unit="Lump sum", basis="Lump sum", page=329, kw=r"Prelim \(b\)", floc_keys=["PRE_COMMERCIAL"]),
    dict(schedule="A.1", item_no="Prelim (c)", description="Mobilisation and Site establishment", unit="Lump sum", basis="Lump sum", page=329, kw=r"Prelim \(c\)", floc_keys=["PRE_MOB"]),
    dict(schedule="A.1", item_no="Prelim (d)", description="Site facilities (workshops, offices, power, fuel)", unit="Lump sum", basis="Lump sum", page=329, kw=r"Prelim \(d\)", floc_keys=["PRE_TEMP", "PRE_CAMP"]),
    dict(schedule="A.1", item_no="Prelim (e)", description="Demobilisation incl. laydown rehabilitation", unit="Lump sum", basis="Lump sum", page=330, kw=r"Prelim \(e\)", floc_keys=["PRE_DEMOB"]),
    dict(schedule="A.1", item_no="Prelim (f)", description="Management, staff, administration and indirect labour", unit="Lump sum", basis="Lump sum", page=330, kw=r"Prelim \(f\)", floc_keys=["PRE_PM", "PRE_SITE"]),
    dict(schedule="A.1", item_no="Prelim (g)", description="Plant and equipment mobilisation, set-up and maintenance", unit="Lump sum", basis="Lump sum", page=330, kw=r"Prelim \(g\)", floc_keys=["PRE_FLEET"]),
    dict(schedule="A.1", item_no="Prelim (h)", description="Close-out documentation", unit="Lump sum", basis="Lump sum", page=330, kw=r"Prelim \(h\)", floc_keys=["PRE_COMM"]),
    dict(schedule="A.2", item_no="HME/CME Option 1", description="Construction fleet - Contractor-supplied (Base Case per Schedule A.2; SoW s10.3 differs)", unit="Not stated", basis="Option (unit rates)", page=332, kw="Option 1 \\(Base Case\\)", floc_keys=["FLEET_OPT1"]),
    dict(schedule="A.2", item_no="HME/CME Option 2", description="Construction fleet - Company free-issued (Alternative)", unit="Not stated", basis="Option (unit rates)", page=332, kw="Option 2 \\(Alternative\\)", floc_keys=["FLEET_OPT2", "FLEET_HME"]),
    dict(schedule="A.2", item_no="Camp Option B / 1B", description="Contractor-provided Construction / Fly Camp (Base Case per Schedule A.2); pricing line SP1/SP2-1.13 is in the Company Pricing Schedule template, not in the pack", unit="Not stated", basis="Option (priced)", page=334, kw="Camp Option B", floc_keys=["CAMP_B"]),
    dict(schedule="A.2", item_no="Camp Option A", description="Company free-issued Construction / Fly Camp (Alternative)", unit="Not stated", basis="Option (priced)", page=334, kw="Camp Option A", floc_keys=["CAMP_A"]),
    dict(schedule="A.2", item_no="Take-out 1A/2A/2B", description="Priced take-out options 1A, 2A and 2B", unit="Not stated", basis="Option (take-out)", page=334, kw="take-out Option 1A", floc_keys=["CAMP_A", "CAMP_B", "FLEET_OPT1", "FLEET_OPT2"]),
    dict(schedule="A.6", item_no="Table A.6.1", description="Nominated Sub-contractors (price plus allowance cap)", unit="Not stated", basis="Nominated sub-contract", page=338, kw="Nominated Sub-contractors", floc_keys=["PRE_COMMERCIAL"]),
    dict(schedule="A.7", item_no="Table A.7.1", description="Variation unit rates", unit="AUD per unit", basis="Variation rates", page=343, kw="Table A.7.1", floc_keys=["PRE_COMMERCIAL"]),
    dict(schedule="A.7", item_no="Table A.7.2", description="Dayworks labour rates", unit="AUD/hr", basis="Dayworks", page=343, kw="Table A.7.2", floc_keys=["PRE_COMMERCIAL"]),
    dict(schedule="A.7", item_no="Table A.7.3", description="Dayworks materials mark-up", unit="%", basis="Dayworks", page=343, kw="Table A.7.3", floc_keys=["PRE_COMMERCIAL"]),
    dict(schedule="A.7", item_no="Table A.7.4", description="Dayworks plant and equipment rates", unit="AUD/hr", basis="Dayworks", page=344, kw="Table A.7.4", floc_keys=["PRE_COMMERCIAL"]),
    dict(schedule="A.9", item_no="A.9 (1)-(4)", description="Fuel consumption (litres by month) and equipment fuel estimate", unit="Litres", basis="Fuel (Company supplied)", page=346, kw="A.9\\(1\\)", floc_keys=["TEMP_FUEL"]),
    dict(schedule="A.13", item_no="Table A.13.1", description="Milestone payments for Lump Sum Works", unit="AUD", basis="Milestone", page=351, kw="Table A.13.1", floc_keys=["PRE"]),
    dict(schedule="C", item_no="Table C.1", description="Personnel deployment", unit="Number / week", basis="Information (blank)", page=354, kw="Table C.1", floc_keys=["PRE_PM"]),
    dict(schedule="C", item_no="Table C.3", description="Man-hour requirements (manual direct, manual indirect, non-manual)", unit="Hours", basis="Information (blank)", page=355, kw="Table C.3", floc_keys=["PRE_PM"]),
    dict(schedule="C", item_no="Table C.4.1", description="Accommodation beds per week (14/7 roster)", unit="Beds / week", basis="Information (blank); back-charged at A$200 per person per day", page=356, kw="Table C.4.1", floc_keys=["PRE_CAMP"]),
    dict(schedule="C", item_no="Table C.4.6", description="Flights Perth to Site, per week", unit="Flights / week", basis="Information (blank); back-charged", page=359, kw="Table C.4.6", floc_keys=["PRE_MOB"]),
    dict(schedule="D", item_no="Table D.1", description="Cash flow forecast (24 months)", unit="AUD", basis="Information (blank)", page=364, kw="Table D.1", floc_keys=["PRE"]),
    dict(schedule="G.1", item_no="Table G.1.1", description="Priority work fronts and required dates (concrete)", unit="Date", basis="Programme", page=369, kw="G.1", floc_keys=["PRE_CONC"]),
    dict(schedule="H", item_no="Table H.1", description="Proposed sub-contracts", unit="AUD", basis="Information (blank)", page=371, kw="Table H.1", floc_keys=["PRE_COMMERCIAL"]),
]

allocation = [
    dict(rule_id="AR-01", cost_pool="Preliminaries (project management, supervision, indirect labour, close-out)", description="Priced as Schedule A.1 lump sum Preliminaries, one line per Separable Part. Allocate each SP's preliminaries pool to the FLOCs of that SP.", driver="Direct cost % within each Separable Part (alternative: direct manual work-hours per Appendix E)", applies_to="SP1 and SP2 FLOCs", basis="Stated + assumption", sources=[dict(page=328, kw="SP1 - Preliminaries"), dict(page=328, kw="Preliminaries list is non-exhaustive")], notes="Pack states the pools (Table A.1.1 SP1, SP2) but not the driver; driver is an assumption."),
    dict(rule_id="AR-02", cost_pool="Mobilisation and Site establishment", description="Mobilisation includes airfares, ground travel, stopovers and R&R; indirect labour and plant set-up sit in Preliminaries; direct labour mobilisation sits in the unit rates (not Preliminaries).", driver="Direct labour mobilisation: man-hours by FLOC; indirect mobilisation: direct cost %", applies_to="All FLOCs", basis="Stated + assumption", sources=[dict(page=218, kw="Mobilisation includes all airfares"), dict(page=330, kw="Direct Labour mobilisation is in Unit Rates")], notes="Split between prelim and rate mobilisation is stated; the allocation driver is an assumption."),
    dict(rule_id="AR-03", cost_pool="Construction camp and accommodation (incl. Company charge-back A$200 per person per day)", description="Accommodation charged by the Company per occupied room-day up to the Table C.4.1 total; camp lines are priced in Preliminaries (Option A/B).", driver="Man-hours (peak headcount x days) by FLOC; bed-days from Table C.4.1", applies_to="All FLOCs with site labour", basis="Stated + assumption", sources=[dict(page=395, kw="cost recovered by Company charge-back|Camp/accommodation cost"), dict(page=334, kw="Temp Construction Camp priced at line 1.13")], notes="Rate (A$200/person/day) is stated at Appendix A; Table C.4.1 quantities are blank."),
    dict(rule_id="AR-04", cost_pool="Flights", description="Flights Perth to Site are back-charged by the Company; mobilisation includes all airfares; the A$ rate wording is ambiguous.", driver="Man-hours / roster headcount by FLOC", applies_to="All FLOCs with site labour", basis="Stated + assumption", sources=[dict(page=359, kw="Table C.4.6"), dict(page=397, kw="Project discounted air services")], notes="See RFI on flight rate."),
    dict(rule_id="AR-05", cost_pool="Temporary works and temporary facilities (roads, hardstands, dewatering, fuel, explosives, crane pads, power and comms)", description="All temporary works are Contractor-designed and Contractor-cost with no separate payment; deemed included in the Contract Price.", driver="Direct cost % of the FLOC they serve; where a temporary work serves one area (e.g. aerodrome laydown/camp area) charge that FLOC directly", applies_to="All FLOCs", basis="Stated + assumption", sources=[dict(page=313, kw="Contractor designs and provides all temporary works"), dict(page=235, kw="Temporary construction camp area priced within Aerodrome")], notes="Open-ended 'any other temporary works' wording; driver is an assumption."),
    dict(rule_id="AR-06", cost_pool="Construction water, dust suppression, power, communications and IT", description="Contractor self-sufficient; construction water drawn from nominated Company bores; all costs deemed included.", driver="Earthworks volume (m3) for water; man-hours for power, IT and comms", applies_to="SP1 earthworks FLOCs (water); all FLOCs (comms)", basis="Stated + assumption", sources=[dict(page=215, kw="construction water and dust suppression"), dict(page=224, kw="self-sufficient for communications")], notes=""),
    dict(rule_id="AR-07", cost_pool="Concrete batch plant and concrete supply (shared)", description="One batch plant near MPP/MSA serves all areas; delivery priced within 2 km of the batch plant; concrete to the IPP Contractor on a recharge model.", driver="Concrete volume (m3) per area FLOC", applies_to="Concrete FLOCs in each area; IPP recharge", basis="Stated + assumption", sources=[dict(page=262, kw="Batch plant: supply, establish, operate"), dict(page=263, kw="Recharge model")], notes="Volumes not in the pack (drawings/MTO not included)."),
    dict(rule_id="AR-08", cost_pool="Plant and equipment (construction fleet, Options 1 and 2; pre-strip HME)", description="Equipment ownership cost is embedded in the SP1 Schedule of Rates run rates; free-issued fleet operating, maintenance, consumables and performance risk stay with the Contractor.", driver="Equipment hours by FLOC (plant-hours per Schedule F / F.1)", applies_to="SP1 earthworks and mining FLOCs", basis="Stated + assumption", sources=[dict(page=334, kw="Equipment ownership cost embedded"), dict(page=333, kw="Contractor bears operation, maintenance, consumables")], notes="Two fleet options and four take-out scenarios must be priced separately."),
    dict(rule_id="AR-09", cost_pool="Survey, QA/QC testing and field laboratory", description="Survey, quantity verification, all testing and the field laboratory are Contractor cost, deemed included.", driver="Direct cost % (or number of tests / survey area where measured)", applies_to="All FLOCs", basis="Stated + assumption", sources=[dict(page=215, kw="Survey, quantity verification"), dict(page=217, kw="All testing performed and paid for by Contractor")], notes=""),
    dict(rule_id="AR-10", cost_pool="HSESC, environmental, community and emergency response resources", description="Dedicated HSESC Manager and staff at 1 HSESC professional per 50 workers; ERT of 20 personnel; waste management and landfill costs included.", driver="Man-hours (headcount) by FLOC", applies_to="All FLOCs", basis="Stated + assumption", sources=[dict(page=410, kw="HSESC"), dict(page=312, kw="All waste collection, transport, treatment and disposal costs")], notes="Ratio stated; driver for allocation is an assumption."),
    dict(rule_id="AR-11", cost_pool="Transport and logistics (Port Hedland to Site) and materials management", description="Onshore transport from the Port Battery Limit (FCA) to Site, OSOM movements, laydown and storage are Contractor scope; no pricing basis stated.", driver="Mass/volume of goods delivered by FLOC (tonnes or m3) from the offshore EPF packing lists", applies_to="SP2 FLOCs and Company Supplied Items", basis="Assumption", sources=[dict(page=295, kw="Transport/logistics for all Project materials")], notes="Pack gives no quantities."),
    dict(rule_id="AR-12", cost_pool="Pre-commissioning, commissioning support and handover", description="Pre-commissioning of all systems and commissioning support for Company/Others are in scope; duration of commissioning support is undefined.", driver="Direct cost % of SP2 FLOCs (or number of systems/loops)", applies_to="SP2 FLOCs (and SP1 pipework)", basis="Assumption", sources=[dict(page=321, kw="Support Company/Others commissioning"), dict(page=321, kw="Commissioning support duration")], notes="Duration undefined."),
    dict(rule_id="AR-13", cost_pool="Spares, surplus materials and Company Supplied Items handling", description="Contractor receives, stores, preserves, reconciles and installs all Company Supplied Items and spares through to handover; no quantities.", driver="Value or tonnes of free-issued goods by FLOC", applies_to="All FLOCs receiving free-issue goods", basis="Assumption", sources=[dict(page=301, kw="Contractor manages surplus materials"), dict(page=215, kw="Receipt, custody, storage and installation of Company Supplied Items")], notes=""),
    dict(rule_id="AR-14", cost_pool="Interface management and SIMOPS", description="Interface coordination and SIMOPS participation are deemed priced in the Pricing Schedule; no separate payment.", driver="Direct cost % within each Separable Part", applies_to="All FLOCs", basis="Stated + assumption", sources=[dict(page=292, kw="Interface management meetings"), dict(page=308, kw="Interface/third-party coordination deemed priced")], notes=""),
    dict(rule_id="AR-15", cost_pool="Demobilisation and rehabilitation", description="Demobilisation, reinstatement of laydowns and temporary facilities, and progressive rehabilitation are included in the price; demobilisation is a Preliminaries line (e).", driver="Disturbed area (ha) by FLOC; otherwise direct cost %", applies_to="All FLOCs", basis="Stated + assumption", sources=[dict(page=330, kw="Prelim \\(e\\)"), dict(page=218, kw="Progressive rehabilitation costs")], notes="Disturbed areas are not in the pack."),
    dict(rule_id="AR-16", cost_pool="Securities, insurance, finance (terms and conditions)", description="Securities, insurance and finance costs sit in Preliminaries item (b) and are carried by the Contractor.", driver="Direct cost %", applies_to="All FLOCs", basis="Stated + assumption", sources=[dict(page=329, kw=r"Prelim \(b\)")], notes=""),
]

rfis = [
    dict(topic="Pricing Schedule template missing", question="The Pricing Schedule Template (C0007-0000-U-TMP-00006, XLS) and the camp lines SP1-1.13 / SP2-1.13 are not in the pack. Please issue it, or confirm that Schedule A.2 has no line items.", impact="No pricing line items to map FLOCs to; cost model cannot be keyed to Company pricing codes.", priority="High", type="Missing document", page=159, kw="Pricing Schedule", floc_keys=["PRE_COMMERCIAL"]),
    dict(topic="Base case for construction fleet and camp", question="SoW s10.3 and Table 4 describe Company free-issued options as the mandatory/base case, while Schedule A.2 calls the Contractor-supplied fleet (Option 1) and Contractor camp (Option B) the Base Case. Which is the conforming base case?", impact="Changes which fleet and camp costs are in the base price and the Option/take-out pricing structure.", priority="High", type="Ambiguity", page=332, kw="Option 1 \\(Base Case\\)", floc_keys=["FLEET_OPT1", "FLEET_OPT2", "CAMP_A", "CAMP_B"]),
    dict(topic="Preliminaries versus rates boundary", question="Table A.1.1 shows only SP1 and SP2 Preliminaries. Please confirm which indirects (supervision, plant maintenance, temporary works, camp) are in Preliminaries and which in Schedule of Rates, and confirm rates are fixed regardless of quantity.", impact="Determines whether indirects are allocated by lump sum driver or embedded in unit rates.", priority="High", type="Clarification", page=330, kw="Direct Labour mobilisation is in Unit Rates", floc_keys=["PRE", "PRE_PM"]),
    dict(topic="Schedule of Rates structure", question="Schedule A.2 has no itemised lines, units or quantities in the pack. Please provide the measured line items (SP1 and SP2) and the Rules of Credit.", impact="Quantities and units are needed to cost FLOCs and test remeasurement exposure.", priority="High", type="Missing information", page=331, kw="SOR quantities are estimates", floc_keys=["PRE_COMMERCIAL"]),
    dict(topic="MPP in Separable Part 2", question="2.4 lists the Mineral Processing Plant as a project facility, but SP2 (s7) names Village, Aerodrome, MSA, Explosive Facility and site-wide utilities only, and s18 excludes top-of-concrete MPP works. Confirm the MPP scope boundary for SP1 and SP2.", impact="Whether any MPP above-ground cost is in the Contractor's FLOC structure.", priority="High", type="Ambiguity", page=228, kw="Separable Part 2", floc_keys=["MPP", "MPP_EX"]),
    dict(topic="Light pole footings split", question="Light pole footings appear in Buried Utilities (SP1), Concrete (SP1) and SP2 lighting scope. Confirm which package carries footings, trenching and cable.", impact="Double-count or gap at SP1/SP2 boundary.", priority="Medium", type="Ambiguity", page=292, kw="Light pole|light pole|footing", floc_keys=["UTL_PWR", "UTL_BU"]),
    dict(topic="Village emergency power configuration", question="Village emergency back-up power is 3 x 500 kVA in 7.3.2 area list but 2 x 1000 kVA free-issued in 7.3.2.3. Which applies, and is the 'gas reticulation network' in scope?", impact="Electrical cost and free-issue interface for Village power.", priority="Medium", type="Ambiguity", page=283, kw="back-up power", floc_keys=["VIL_POWER"]),
    dict(topic="HVAC commissioning responsibility", question="Village factory-versus-site table shows HVAC refrigerant piping and commissioning 'by others' while 7.1.2 has the Contractor installing HVAC. Who commissions HVAC?", impact="Commissioning allocation for Village modular buildings.", priority="Medium", type="Ambiguity", page=274, kw="HVAC refrigerant", floc_keys=["VIL_MOD"]),
    dict(topic="Pre-strip to TSF pricing split", question="The transfer node / reference axis for the Pre-Strip versus TSF price split is not in the text provided. Please provide the node location drawing.", impact="Splits haulage cost between Mine Pre-Strip and TSF FLOCs.", priority="High", type="Missing information", page=253, kw="Pre-Strip vs TSF Pricing Schedule split", floc_keys=["TSF_FILL", "MIN"]),
    dict(topic="Liner supply responsibilities", question="TSF 2 mm HDPE is Contractor-procured; pipeline-corridor and sump liner is free-issue; supply for Clean Water Pond and stockpile detention ponds is not stated. Please confirm.", impact="Materials cost ownership per FLOC (TSF, ponds, stockpiles).", priority="Medium", type="Ambiguity", page=260, kw="1.5 mm smooth HDPE liner", floc_keys=["TSF_LINER", "STK_DET", "STK_CWP"]),
    dict(topic="Exclusion boundary versus pre-commissioning", question="s18 excludes MPP E&I, backbone fibre, CCTV and access control, yet s15.2 requires pre-commissioning of all systems in every area. Clarify what must be pre-commissioned.", impact="Commissioning allocation and scope gaps at the MPP boundary.", priority="High", type="Ambiguity", page=323, kw="MPP electrical, instrumentation and communications", floc_keys=["MPP_EI_EX", "PRE_COMM"]),
    dict(topic="Free-issue lists not in the pack", question="Equipment list C-WN-0000-G-LST-00005, the Scope and Responsibility Matrices and Table 4 items 3 and 4 (MSA/NPI, camp - 'to be confirmed by Supplementary Tender Notice') are not in the pack. Please issue.", impact="Free-issue versus Contractor-supply split cannot be costed; handling allocation unquantified.", priority="High", type="Missing document", page=198, kw="Table 4", floc_keys=["PRE_FREE", "FLEET_HME"]),
    dict(topic="Quantity documents not in the pack", question="MTOs (REF-00318 Overall Bulk Earthworks, REF-00325 Prestrip, TSF MTO), the plot plan REF-00324 and the TSF Appendices 1 to 4 are referenced but not included. Please issue.", impact="No quantities to cost earthworks, pre-strip or TSF FLOCs.", priority="High", type="Missing document", page=160, kw="MTO|Takeoff|Overall Bulk", floc_keys=["SITE", "MIN", "TSF"]),
    dict(topic="Accommodation and flights rates", question="Appendix A states A$650 for flights with '(return)' next to 'one way'; Table C.4.3-C.4.5 are missing from numbering. Confirm flight charge basis and the Schedule C table numbering.", impact="Flight cost per head could differ by 2x; accommodation back-charge basis.", priority="Medium", type="Ambiguity", page=397, kw="A\\$650|flights|Flights", floc_keys=["PRE_MOB", "PRE_CAMP"]),
    dict(topic="Schedule O not used but Acceptance Tests apply", question="Schedule O is 'NOT USED' but the General Conditions rely on it for Acceptance Tests, Guaranteed Performance Standards and performance LDs. Confirm intended position.", impact="Uncapped general-damages exposure; contingency allocation.", priority="High", type="Ambiguity", page=53, kw="Schedule O|not used|NOT USED", floc_keys=["PRE_COMMERCIAL"]),
    dict(topic="Offer validity", question="Clause 4.3 states 240 days; the Form of Tender states 90 days. Confirm validity.", impact="Escalation exposure and price hold period.", priority="Medium", type="Ambiguity", page=17, kw="240 days|validity", floc_keys=["PRE_COMMERCIAL"]),
    dict(topic="Landfill construction", question="s12.9.4 has the Contractor operating the on-Site landfill; who constructs it, its capacity, and whether other contractors' waste is accepted are not stated.", impact="Landfill FLOC scope and cost allocation.", priority="Medium", type="Missing information", page=312, kw="On-Site landfill", floc_keys=["WST_LF"]),
    dict(topic="Commissioning support duration", question="Commissioning support duration and start-up period are undefined (s15.3). Provide the duration or an allowance basis.", impact="Open-ended labour/plant allowance for commissioning support.", priority="High", type="Missing information", page=321, kw="duration and start-up period undefined", floc_keys=["PRE_COMM"]),
    dict(topic="Mine Access Road bitumen extent and aerodrome access road ownership", question="Bitumen extent is left to Contractor strategy and no loadings are given; the unsealed Aerodrome Access Road has no stated owner. Confirm design basis and ownership.", impact="Pavement quantities for Mine Access Road and Aerodrome access FLOCs.", priority="Medium", type="Ambiguity", page=231, kw="Aerodrome Access Road|sealed", floc_keys=["MAR_ROAD", "AER_ROAD"]),
]

spec = {"project": root, "pricing": pricing, "allocation_rules": allocation, "rfis": rfis}
json.dump(spec, open("build/winu_floc_spec.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
print("keys", len(keys))
