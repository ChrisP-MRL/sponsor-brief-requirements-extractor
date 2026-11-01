#!/usr/bin/env python3
"""Build the Winu processing plant (MPP) sample point design workbook (Excel).

Sources:
  - output/Winu/WIN-CON-EPC-001_Process_Review.html : MPP facility breakdown, process areas, concrete
    milestone dates, laboratory and sample storage buildings, 10 Mtpa, 25% Cu concentrate, gaps G-58 to G-61.
  - output/Winu/Winu Technical Info - Document Register.xlsx : the only process-relevant technical files
    (water balance #7, water balance memo #3, hydrogeology #4, clean water pond #10/#11, TSF #28,
    process plant geotechnical #19). The register records that the folder holds no flowsheet or
    metallurgical test work, so the flowsheet is notional (every unit operation not stated is flagged).
  - input/Vendor/Datamine (CCLAS)/Winu_Lab_Instrumentation_Requirements.xlsx and
    Winu_CCLAS_Instrument_Module_Matrix.xlsx : lab stream names, instrument capacities and peak quantities
    (hard-coded below, with the source named on the sheet) so the plant load can be checked against the lab.

Run: python -I -X utf8 winu_process_sample_points_xlsx.py --output <xlsx> [--force]
"""
import argparse
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as CL

NAVY = "1F3864"
HDR = PatternFill("solid", fgColor=NAVY)
WHITE = Font(bold=True, color="FFFFFF")
BOLD = Font(bold=True)
TITLE = Font(bold=True, size=13)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="top", wrap_text=True)
INPUT = PatternFill("solid", fgColor="FFF2CC")
TIER_FILL = {
    "1 Essential": PatternFill("solid", fgColor="DDEBF7"),
    "2 Recommended": PatternFill("solid", fgColor="E2EFDA"),
    "3 Optional / survey": PatternFill("solid", fgColor="F2F2F2"),
}
P, O = "●", "○"

# ---- processing areas (code, name, concrete milestone, date, milestone basis) ---------------------------
AREAS = [
    (100, "ROM and ore crushing", "Ore Crushing Concrete (Milestone 3)", date(2028, 10, 25), "Stated, AGR Item 13(c) PDF p.55"),
    (200, "Grinding and classification", "Grinding Concrete - Mill Foundations (Milestone 2)", date(2028, 10, 18), "Stated, AGR Item 13(c) PDF p.55"),
    (250, "Oversized (pebble) crushing", "Oversized Crushing Concrete (Milestone 9)", date(2029, 1, 15), "Stated, AGR Item 13(c) PDF p.55"),
    (300, "Gravity gold concentration", "Grinding Concrete - Mill Foundations (Milestone 2)", date(2028, 10, 18),
     "ASSUMPTION: gravity gold is a named MPP facility but has no milestone of its own; placed with Grinding"),
    (400, "Flotation and regrind", "Flotation and Regrind Concrete (Milestone 1)", date(2028, 10, 11), "Stated, AGR Item 13(c) PDF p.55"),
    (500, "Concentrate dewatering and product handling", "Concentrate Dewatering Concrete (Milestone 4)", date(2028, 11, 4),
     "Milestone Stated; ASSUMPTION that product sampling, handling and reclaim concrete sits with it"),
    (600, "Tailings dewatering and handling", "Tailings Dewatering and Handling Concrete (Milestone 5)", date(2029, 1, 8), "Stated, AGR Item 13(c) PDF p.55"),
    (700, "Reagents", "Reagents Concrete (Milestone 6)", date(2029, 1, 8), "Stated, AGR Item 13(c) PDF p.55"),
    (800, "Utilities and water", "Utilities Concrete (Milestone 7)", date(2029, 1, 8), "Stated, AGR Item 13(c) PDF p.55"),
]

# ---- analyte / test packages (column key, header, description, lab workbook instruments) ---------------
PKGS = [
    ("CUF", "Cu multi-element (4-acid ICP-OES)", "Cu, Ag, S, Fe, As and others after 4-acid digest", "A4 hot-block digestion, A5 ICP-OES"),
    ("AUF", "Au fire assay (AAS finish)", "30-50 g fire assay; nugget effect, so coarse gold may need screen-metallics", "A1 fire assay furnace, A2 cupellation, A3 AAS"),
    ("SEQ", "Sequential Cu (acid / cyanide soluble)", "Oxide and transition ore deportment", "A3 AAS"),
    ("SC", "Total and sulphide S, C (Leco)", "S balance, HS / LS split control, ARD", "A7 Leco"),
    ("ME", "Penalty elements (ICP-MS)", "As, Sb, Bi, Cd, Pb, Zn, F for concentrate settlement", "A6 ICP-MS"),
    ("HG", "Mercury", "Hg penalty element", "A8 mercury analyser"),
    ("PSD", "Particle size", "Laser or sieve; P80 at cyclones and concentrate size", "A10 laser PSD, A14 sieve set"),
    ("SOL", "% solids / density", "Slurry density by weigh-dry; plant laboratory or at-plant", "Plant laboratory bench (balances A13, oven B1)"),
    ("MOI", "Moisture", "Dry-mass basis for tonnage and settlement", "Drying oven B1, balances A11/A13"),
    ("TML", "Transportable moisture limit", "Concentrate shipping safety test", "Not in lab workbook: confirm method and owner"),
    ("ARD", "Acid-base accounting (NAG / ANC)", "Tailings and waste geochemistry", "A9 auto-titrator"),
    ("WTR", "Water chemistry (pH, EC, TDS, metals, anions)", "Process, raw and discharge water", "A5 ICP-OES, A6 ICP-MS, A9 titrator / meters"),
    ("REAG", "Reagent QA", "Strength, density, moisture, concentration against supplier spec", "Plant laboratory bench; method per reagent"),
    ("MET", "Retained for metallurgical composite", "Split kept for monthly composite, comminution and flotation testwork", "Metallurgical bench; sample store"),
]
PKG_KEYS = [k for k, *_ in PKGS]

# ---- sampler classes (for the equipment summary) --------------------------------------------------------
CLASSES = [
    ("C1", "Cross-belt / belt-cut sampler (automatic)",
     "Cross-belt hammer or swing-arm cutter with weightometer interlock; secondary crusher and divider for coarse ore",
     "Power, instrument air, sample return chute to belt, dust control, sample cabin, label printer, platform access"),
    ("C2", "Cross-stream slurry sampler (automatic)",
     "Linear or rotary cross-cut (Vezin-type) cutter on launder, box or falling stream; full-stream cut, cutter-gap by top size",
     "Power, instrument air, flush water, sample return launder to sump, sample cabin, label printer"),
    ("C3", "In-line pipe sampler (automatic)",
     "Pressure-pipe cutter or sample-loop on pump discharge; paired with density gauge",
     "Instrument air, flush water, return to process, valve isolation for maintenance"),
    ("C4", "Batch capture station (semi-automatic)",
     "Whole-batch weigh, split and bag at the discharge of an intermittent process",
     "Batch trigger signal from DCS, weigh scale, secure area (gold-bearing), CCTV"),
    ("C5", "Product / lot sampling station (automatic, multi-stage)",
     "Primary cutter, crusher, secondary and tertiary cutters with moisture and archive portions; design intent follows ISO 12743 for copper concentrates (confirm with buyer)",
     "Power, instrument air, enclosed building or cabin, dust and moisture-loss control, label printer, split sample store"),
    ("C6", "Manual survey point",
     "Stopped-belt cut, hose or ladle sample at a fitted port; used for circuit surveys and commissioning mass balances",
     "Safe access, lockable port, drip tray, lighting, label printer at the nearest cabin"),
    ("C7", "Manual grab / tap",
     "Tap, scoop or auger sample on a schedule; reagent receipt and water streams",
     "Tap with flush, safe access, sample bottles and preservation, label printer"),
]
CLASS_NAME = {c: n for c, n, *_ in CLASSES}

LAB_STREAMS = [
    "Plant feed (ROM / SAG feed)",
    "Flotation circuit streams",
    "Gravity gold products",
    "Tailings (HST / LST)",
    "Cu concentrate (commercial)",
    "Concentrate moisture / TML and size",
    "Process and environmental water",
    "Reagents (receipt QA) - not in lab workbook",
]

# Inputs sheet cell addresses used by formulas
IN_MTPA, IN_AVAIL, IN_TPH, IN_QAQC, IN_OCC, IN_LOTS, IN_GRAV, IN_REAG, IN_UTIL = (
    "Inputs!$C$5", "Inputs!$C$6", "Inputs!$C$7", "Inputs!$C$8", "Inputs!$C$9",
    "Inputs!$C$10", "Inputs!$C$11", "Inputs!$C$12", "Inputs!$C$13")

CON_FOUND = "Foundation / plinth / sump / launder embeds in MPP concrete (WBS 2000 series, SoW p.260-261); sampler and cabin by others (s18)"
CON_COND = CON_FOUND + "; conduits and pits in buried utilities (p.265-268)"


def pk(*marks):
    """marks: 'CUF' = primary, '~CUF' = occasional."""
    out = {}
    for m in marks:
        out[m.lstrip("~")] = O if m.startswith("~") else P
    return out


# ---- sample points -------------------------------------------------------------------------------------
# id, area, stream, location, purpose, tier, class, method, companion, interval_h, events (value or formula),
# packages, lab stream, cclas route, install, touchpoint, basis, rationale
SP = [
    # ---------- 100 ROM and ore crushing
    ("SP-101", 100, "ROM stockpile - first ~600 kt of ore delivered by the Contractor",
     "ROM stockpile fingers (Contractor-built ROM bulk fill and stockpile fingers)",
     "Mine-to-mill reconciliation of the pre-strip ore", "2 Recommended", "C6",
     "Channel or auger sample on the working face by material code, per stockpile lot; no entry under an unsupported face",
     "Truck-load tonnage from FMS; surveyed stockpile volume", None, 1,
     pk("CUF", "AUF", "SC", "MOI", "~SEQ"), LAB_STREAMS[0], "Manual registration with barcode label at ROM",
     "Safe access to stockpile edge; designated sample point and laydown for lot bags",
     "Contractor builds the ROM bulk fill and stockpile fingers (SoW s6.2.9, p.252). Sampling responsibility for the first 600 kt is not assigned (Process Review G-59).",
     "Stated stream; assumed method",
     "Review G-59/G-60: no weighing, sampling or reconciliation instrumentation at ROM beyond FMS tracking."),
    ("SP-102", 100, "Primary crusher product",
     "Primary crusher discharge conveyor to stockpile / COS reclaim chamber",
     "Ore-type tracking and tonnage reconciliation before the stockpile", "2 Recommended", "C1",
     "Belt-cut sampler, increment every 15 min, crush and split to shift composite; weightometer-interlocked",
     "Belt weightometer; tramp metal detector", 12, None,
     pk("CUF", "AUF", "SC", "MOI", "~SEQ"), LAB_STREAMS[0], "Auto label at sampler cabin; barcode scan to lab",
     "Primary crusher product belt with platform; secondary crusher and divider housing; return chute to belt",
     CON_COND + ". Primary Crusher select-fill pocket is completed by others (p.256).",
     "Stated facility; assumed to be needed",
     "Optional once SP-103 exists, but it is the only point that measures ore before blending on the stockpile."),
    ("SP-103", 100, "SAG mill feed (plant head)",
     "SAG mill feed conveyor downstream of the COS reclaim chamber",
     "Head grade, metallurgical accounting and reconciliation", "1 Essential", "C1",
     "Cross-belt hammer sampler, primary increment about 20-40 kg every 10 min (belt top size about 150 mm), crushed to minus 10 mm and divided to a shift composite",
     "Belt weightometer; online moisture; sample-triggered label", 4, None,
     pk("CUF", "AUF", "SC", "MOI", "SEQ", "MET", "~ME", "~HG", "~PSD", "~ARD"), LAB_STREAMS[0],
     "Auto label at sampler cabin; barcode scan to lab",
     "Belt gallery position with clear belt span, platform, dust extraction; sample cabin within 30 m",
     CON_COND + ". SAG mill feed conveyors are by others (s18, p.322-323).",
     "Stated facility; assumed design",
     "Primary head-grade point. Au nugget effect and coarse feed mean a large primary increment; confirm mass and cut interval in a sampling-theory study."),
    ("SP-104", 100, "SAG mill feed - size and comminution survey",
     "SAG mill feed conveyor (stopped-belt cut position)",
     "Feed size distribution, comminution testwork and model calibration", "3 Optional / survey", "C6",
     "Stopped-belt full-section cut, 1 m of belt, bagged and weighed",
     None, None, "=1/30",
     pk("PSD", "MET"), LAB_STREAMS[0], "Manual registration with barcode label",
     "Belt lockout / stop position, platform, drop-out tray", "Platform access only; belt is by others",
     "Assumed", "Quarterly-to-monthly survey; not part of daily load."),
    # ---------- 250 Oversized crushing
    ("SP-251", 250, "Oversized (pebble) crusher feed and product",
     "Oversized crushing conveyor, feed and discharge",
     "Pebble rate and size for circuit surveys", "3 Optional / survey", "C6",
     "Stopped-belt cut on each belt; size distribution and mass",
     "Belt weightometer on pebble return", None, "=1/30",
     pk("PSD"), LAB_STREAMS[0], "Manual registration with barcode label",
     "Stopped-belt position and platform", "Oversized Crushing is a named MPP process area (Milestone 9); crusher type is assumed.",
     "Stated area; equipment assumed", "Survey only."),
    # ---------- 200 Grinding and classification
    ("SP-201", 200, "SAG mill discharge", "SAG mill discharge sump / trommel undersize",
     "Circuit survey and mill performance", "3 Optional / survey", "C6",
     "Survey port with hose or ladle sample at pump discharge",
     "Density gauge", None, "=1/30",
     pk("PSD", "SOL"), LAB_STREAMS[1], "Manual registration with barcode label",
     "Port with isolation valve, drip tray, safe access", CON_FOUND + " (mill deck slab and sump)",
     "Assumed", "Survey only. Mill types and sizes are not in the pack."),
    ("SP-202", 200, "Cyclone feed", "Cyclone cluster feed pipe",
     "Cyclone performance and circulating load", "2 Recommended", "C3",
     "In-line pressure sampler, 20-min cut interval, composited per 4 h",
     "Density gauge; flow meter", 4, None,
     pk("PSD", "SOL"), LAB_STREAMS[1], "Auto label at sampler cabin",
     "Straight pipe run, isolation valves, flush water, return to sump", CON_FOUND,
     "Assumed", "Needed to close the grinding-circuit mass balance."),
    ("SP-203", 200, "Cyclone overflow = flotation feed",
     "Cyclone overflow launder / flotation distribution box",
     "Flotation head grade and grind (P80) control; metallurgical accounting", "1 Essential", "C2",
     "Cross-stream cutter on the overflow launder, 20-min cut interval, composited per 4 h",
     "Online particle size monitor; density gauge; online stream analyser (multiplexed); option to confirm", 4, None,
     pk("CUF", "AUF", "SC", "PSD", "SOL", "~SEQ", "~MET"), LAB_STREAMS[1],
     "Auto label at sampler cabin; barcode scan to lab",
     "Launder drop of 0.5-1 m for the cutter; sample return launder to sump; cabin adjacent",
     CON_COND + " Launder and sump geometry must be fixed before Grinding / Flotation concrete.",
     "Stated area; assumed design",
     "First of the three main metallurgical accounting points (feed, concentrate, tailings)."),
    ("SP-204", 200, "Cyclone underflow", "Cyclone underflow launder / mill feed chute",
     "Circulating load", "3 Optional / survey", "C6",
     "Survey port with timed cut",
     "Density gauge", None, "=1/30", pk("PSD", "SOL"), LAB_STREAMS[1],
     "Manual registration with barcode label", "Port, drip tray, safe access", CON_FOUND,
     "Assumed", "Survey only."),
    # ---------- 300 Gravity gold
    ("SP-301", 300, "Gravity circuit feed", "Gravity feed screen undersize or cyclone underflow split",
     "Gravity feed grade and recovery to gravity", "2 Recommended", "C2",
     "Timed cross-stream cut, composited per 12 h",
     "Flow meter; density gauge", 12, None,
     pk("AUF", "SOL", "~CUF", "~PSD"), LAB_STREAMS[2], "Auto label at sampler cabin",
     "Launder with drop for cutter; return to circuit", CON_FOUND,
     "Stated facility; assumed design",
     "Gold-bearing: gravity gold concentration is a named MPP facility (SoW 2.4, p.211)."),
    ("SP-302", 300, "Gravity concentrate (batch)", "Gravity concentrator batch discharge",
     "Gold recovery to gravity and value accounting", "1 Essential", "C4",
     "Capture the whole batch, weigh, split by rotary divider; screen-metallics fire assay for coarse gold",
     "Batch weigh scale; batch trigger from DCS", None, f"={IN_GRAV}",
     pk("AUF", "~CUF", "SOL"), LAB_STREAMS[2], "Batch registration with security-controlled barcode label",
     "Secure room with scale, CCTV, restricted access; connection to the lab or gold room by controlled route",
     "Within MPP; secure room structure if a building is needed is not defined in the pack",
     "Stated facility; assumed design",
     "Gravity concentrate treatment route (intensive leach, direct smelting or sale with the Cu concentrate) is not stated: RFI."),
    ("SP-303", 300, "Gravity tailings", "Gravity concentrator tailings return line",
     "Gravity recovery", "3 Optional / survey", "C2",
     "Timed cross-stream cut, composited per 12 h", None, 12, None,
     pk("AUF"), LAB_STREAMS[2], "Auto label at sampler cabin", "Launder with drop; return to circuit", CON_FOUND,
     "Assumed", "Can be computed from SP-301 and SP-302 if a survey-only point is preferred."),
    # ---------- 400 Flotation and regrind
    ("SP-401", 400, "Rougher concentrate", "Rougher launder",
     "Rougher performance", "2 Recommended", "C2",
     "Launder cross-cut, composited per 12 h", "Online stream analyser (multiplexed); froth camera", 12, None,
     pk("CUF", "SOL", "~AUF", "~SC"), LAB_STREAMS[1], "Auto label at sampler cabin", "Launder drop; return to sump", CON_COND,
     "Assumed flowsheet", "Rougher-scavenger-cleaner layout is assumed: the pack gives no flowsheet."),
    ("SP-402", 400, "Rougher tailings", "Rougher tailings box / scavenger feed",
     "Rougher recovery and tailings Au loss", "1 Essential", "C2",
     "Cross-stream cutter, composited per 4 h", "Online stream analyser (multiplexed)", 4, None,
     pk("CUF", "AUF", "SC", "SOL"), LAB_STREAMS[1], "Auto label at sampler cabin", "Box or launder with drop for cutter; return to sump", CON_COND,
     "Assumed flowsheet", "Key loss stream."),
    ("SP-403", 400, "Scavenger concentrate", "Scavenger launder",
     "Scavenger performance", "3 Optional / survey", "C2",
     "Launder cross-cut, composited per 12 h", None, 12, None, pk("CUF"), LAB_STREAMS[1],
     "Auto label at sampler cabin", "Launder drop; return to sump", CON_FOUND, "Assumed flowsheet", "Present only if a scavenger bank is installed."),
    ("SP-404", 400, "Scavenger tailings", "Scavenger tailings box",
     "Scavenger performance and tail check", "2 Recommended", "C2",
     "Cross-stream cutter, composited per 12 h", "Online stream analyser (multiplexed)", 12, None,
     pk("CUF", "AUF", "SC"), LAB_STREAMS[1], "Auto label at sampler cabin", "Box drop; return to sump", CON_COND,
     "Assumed flowsheet", None),
    ("SP-405", 400, "Regrind mill feed", "Regrind cyclone feed pump box",
     "Regrind survey", "3 Optional / survey", "C6", "Survey port", "Density gauge", None, "=1/30",
     pk("PSD", "SOL"), LAB_STREAMS[1], "Manual registration with barcode label", "Port, drip tray, safe access", CON_FOUND,
     "Assumed flowsheet", "Regrind is a named process area (Milestone 1)."),
    ("SP-406", 400, "Regrind cyclone overflow", "Regrind cyclone overflow launder",
     "Regrind P80 control (liberation for cleaner grade)", "2 Recommended", "C2",
     "Cross-stream cutter, composited per 4 h", "Online particle size monitor; density gauge", 4, None,
     pk("PSD", "CUF", "SOL"), LAB_STREAMS[1], "Auto label at sampler cabin", "Launder drop; return to sump", CON_COND,
     "Assumed flowsheet", None),
    ("SP-407", 400, "First cleaner concentrate", "First cleaner launder",
     "Cleaner circuit balance", "2 Recommended", "C2",
     "Launder cross-cut, composited per 12 h", "Online stream analyser (multiplexed)", 12, None,
     pk("CUF", "SOL", "~AUF"), LAB_STREAMS[1], "Auto label at sampler cabin", "Launder drop; return to sump", CON_COND,
     "Assumed flowsheet", None),
    ("SP-408", 400, "Cleaner tailings", "Cleaner tailings box (recycle to rougher / regrind)",
     "Cleaner circuit balance and recycle load", "2 Recommended", "C2",
     "Cross-stream cutter, composited per 12 h", None, 12, None,
     pk("CUF", "AUF", "SOL"), LAB_STREAMS[1], "Auto label at sampler cabin", "Box drop; return to sump", CON_FOUND,
     "Assumed flowsheet", None),
    ("SP-409", 400, "Final concentrate (cleaner product to thickener)", "Final cleaner launder / concentrate thickener feed",
     "Concentrate grade and recovery; process control", "1 Essential", "C2",
     "Cross-stream cutter, composited per 4 h", "Online stream analyser (multiplexed); density gauge; flow meter", 4, None,
     pk("CUF", "AUF", "SC", "SOL", "~ME", "~PSD"), LAB_STREAMS[1], "Auto label at sampler cabin; barcode scan to lab",
     "Launder drop; return to sump; cabin adjacent", CON_COND,
     "Stated product (Cu concentrate about 25% Cu); assumed design",
     "Second main accounting point. Commercial settlement samples are taken later at SP-505 / SP-506, not here."),
    ("SP-410", 400, "High-sulphur tailings (HST) stream, about 6% of tailings",
     "HS tailings pump box / discharge to HS cell line",
     "S grade control of the HS / LS split; ARD classification; Cu and Au loss", "1 Essential", "C3",
     "In-line pressure sampler, composited per 12 h", "Density gauge; flow meter", 12, None,
     pk("SC", "ARD", "CUF", "AUF", "SOL"), LAB_STREAMS[3], "Auto label at sampler cabin; barcode scan to lab",
     "Pipe run with isolation; flush water; return to HS delivery line", CON_COND,
     "Stated stream (water balance, #7); location assumed",
     "Water balance model splits tailings into high- and low-sulphur streams, HS about 6% to a water-covered cell. Where the split is made in the flowsheet is not stated."),
    ("SP-411", 400, "Low-sulphur tailings (LST) stream = LST thickener feed",
     "Tailings box / LST thickener feed",
     "Final tailings Cu and Au; S check against the LS cut-off; mass balance", "1 Essential", "C2",
     "Cross-stream cutter, composited per 4 h", "Online stream analyser (multiplexed); density gauge", 4, None,
     pk("CUF", "AUF", "SC", "SOL", "~ARD"), LAB_STREAMS[3], "Auto label at sampler cabin; barcode scan to lab",
     "Box drop for cutter; return to thickener feed line", CON_COND,
     "Stated stream (water balance, #7); location assumed",
     "Third main accounting point. Final tailings = SP-410 + SP-411."),
    # ---------- 500 Concentrate dewatering and product handling
    ("SP-501", 500, "Concentrate thickener overflow", "Thickener overflow launder",
     "Solids and Cu carry-over to process water", "3 Optional / survey", "C7",
     "Daily grab", None, None, 1, pk("SOL", "CUF", "~WTR"), LAB_STREAMS[1], "Manual registration with barcode label",
     "Tap or launder access", CON_FOUND, "Assumed flowsheet", None),
    ("SP-502", 500, "Concentrate thickener underflow", "Underflow pump discharge to filter feed tank",
     "Underflow density and size to the filter", "2 Recommended", "C3",
     "In-line pressure sampler, composited per 12 h", "Density gauge; flow meter", 12, None,
     pk("SOL", "PSD", "~CUF"), LAB_STREAMS[1], "Auto label at sampler cabin", "Pipe run with isolation and flush", CON_COND,
     "Assumed flowsheet", None),
    ("SP-503", 500, "Concentrate filter cake", "Filter discharge conveyor",
     "Cake moisture for filter control and handling", "1 Essential", "C1",
     "Cross-belt cut every 30 min, composited per 2 h for moisture", "Online moisture analyser (option); belt weightometer", 2, None,
     pk("MOI", "~PSD"), LAB_STREAMS[5], "Auto label at sampler cabin", "Belt position, platform, sealed sample hand-over to prevent moisture loss",
     CON_COND, "Stated facility; assumed design", "Moisture drives filter throughput and the TML margin."),
    ("SP-504", 500, "Concentrate filtrate", "Filtrate tank outlet",
     "Cu loss to filtrate", "3 Optional / survey", "C7", "Daily grab", None, None, 1,
     pk("SOL", "CUF"), LAB_STREAMS[1], "Manual registration with barcode label", "Tap", CON_FOUND, "Assumed flowsheet", None),
    ("SP-505", 500, "Concentrate product - plant sampling station",
     "Concentrate conveyor to stockpile / shed (product sampling facility)",
     "Commercial settlement (Cu, Au, Ag, penalty elements, moisture) and reconciliation", "1 Essential", "C5",
     "Automatic multi-stage sampler: primary cutter, crusher, secondary and tertiary cutters; moisture portion taken at the primary stage; shift composite split into seller, buyer, umpire and reserve portions (typical practice, confirm with offtake terms)",
     "Belt weightometer; belt moisture analyser (option)", 12, None,
     pk("CUF", "AUF", "ME", "HG", "SC", "MOI", "PSD"), LAB_STREAMS[4],
     "Auto label at sampler building; chain of custody barcode to lab and archive",
     "Enclosed sampler building or cabin, weatherproof; stable weightometer; split sample store within 50 m",
     CON_COND + ". Product sampling is a named MPP facility (SoW 2.4, p.211); product handling design is by the MPP EPC Contractor (p.292).",
     "Stated facility; assumed design",
     "Reference Cu concentrate point for all commercial results. Copper concentrate sampling standard and offtake sampling clauses are not in the pack."),
    ("SP-506", 500, "Concentrate load-out lots", "Concentrate reclaim / truck load-out conveyor",
     "Lot sample per shipment for provisional invoicing and TML", "1 Essential", "C5",
     "Lot-based cross-cut sampler on the load-out conveyor; spear / auger of loaded trucks as back-up and audit",
     "Truck weighbridge; belt weightometer", None, f"={IN_LOTS}",
     pk("CUF", "AUF", "ME", "HG", "MOI", "TML", "PSD", "SC"), LAB_STREAMS[4],
     "Auto label at sampler building; lot ID linked to truck / consignment",
     "Load-out building or cabin; weighbridge tie-in; split sample store",
     CON_COND + ". Concentrate loop road (C-WN-2810-Y-DRG-00003) sets the truck circuit.",
     "Stated facility (product reclaiming); assumed design",
     "Port or ship sampling and destination sampling are by others and not designed here."),
    ("SP-507", 500, "Concentrate stockpile / shed audit", "Concentrate storage shed",
     "Audit of stored quality and moisture", "3 Optional / survey", "C7",
     "Auger sample of the stored heap", None, None, "=1/7", pk("MOI", "~TML", "~CUF"), LAB_STREAMS[5],
     "Manual registration with barcode label", "Safe heap access", "Shed by others", "Assumed", None),
    # ---------- 600 Tailings dewatering and handling
    ("SP-601", 600, "LST thickener overflow (returns to process water)", "LST thickener overflow launder",
     "Return-water solids and chemistry", "2 Recommended", "C7",
     "Grab, twice per day", "Turbidity meter (option)", None, 2, pk("SOL", "WTR", "~CUF"), LAB_STREAMS[3],
     "Manual registration with barcode label", "Tap or launder access", CON_FOUND,
     "Stated equipment (LST thickeners named in the Process Review equipment list); assumed method", None),
    ("SP-602", 600, "LST thickener underflow (to TSF-LS delivery)", "Underflow pump discharge",
     "Underflow density against the 64% (oxide) / 68% (sulphide) base case", "2 Recommended", "C3",
     "In-line pressure sampler, grab twice per day for density check", "Density gauge; flow meter", None, 2,
     pk("SOL", "~ARD"), LAB_STREAMS[3], "Manual registration with barcode label", "Pipe run with isolation and flush", CON_COND,
     "Stated densities (water balance, #7); assumed method",
     "Water balance base case uses oxide tailings density 64% and sulphide 68%; commissioning density is lower for the first two years."),
    ("SP-603", 600, "HS tailings at delivery to the water-covered HS cell", "HS tailings delivery line near the TSF",
     "Confirm HS stream S and solids at discharge", "2 Recommended", "C7",
     "Daily grab at a fitted tap", None, None, 1, pk("SC", "ARD", "SOL"), LAB_STREAMS[3],
     "Manual registration with barcode label", "Tap with flush; safe access at TSF corridor",
     "Tailings pipeline corridors, sumps and spigot protection are Contractor TSF scope; the tailings pumping WBS 2458 and 's18 excludes TSF process and delivery systems' conflict (Process Review finding 12a)",
     "Stated stream; assumed method", None),
    ("SP-604", 600, "TSF reclaim pond water (to process)", "Reclaim pump station tap",
     "Return-water chemistry and its effect on flotation", "2 Recommended", "C7",
     "Daily grab", None, None, 1, pk("WTR"), LAB_STREAMS[6], "Manual registration with barcode label",
     "Tap at pump station; safe access", "TSF and reclaim are Contractor scope in part; sampling tap by others",
     "Stated stream (water balance, #7)", "Reclaim water is solely used for processing (water balance 3.4)."),
    ("SP-605", 600, "Tailings geochemical check", "TSF delivery line spigot",
     "ARD classification of deposited tailings", "3 Optional / survey", "C7",
     "Weekly grab of slurry", None, None, "=1/7", pk("ARD", "SC", "SOL"), LAB_STREAMS[3],
     "Manual registration with barcode label", "Spigot access", "TSF scope", "Assumed", None),
    # ---------- 700 Reagents
    ("SP-701", 700, "Reagent deliveries (collector, frother, depressant, flocculant, lime)",
     "Reagent receipt bay in the Plant Reagent Storage building area",
     "Check delivered reagent against specification before it enters make-up", "2 Recommended", "C7",
     "Manual grab per delivery from tanker, drum or bulk bag by supplier procedure", None, None, f"={IN_REAG}",
     pk("REAG"), LAB_STREAMS[7], "Manual registration with barcode label; supplier batch number captured",
     "Receipt bay with sample tap and spill containment",
     "Reagents Concrete (Milestone 6); Plant Reagent Storage building is in MSA scope (SoW p.272)",
     "Stated area; reagent list not stated", "Reagent types are not in the pack."),
    ("SP-702", 700, "Reagent make-up and distribution (lime slurry, flocculant)",
     "Make-up tank outlets and ring main",
     "Strength and density at point of use", "3 Optional / survey", "C7",
     "Daily grab", None, None, 1, pk("REAG", "SOL"), LAB_STREAMS[7],
     "Manual registration with barcode label", "Taps on ring main", CON_FOUND, "Assumed", None),
    # ---------- 800 Utilities and water
    ("SP-801", 800, "Raw water supply to the MPP (bores WINU0913 and WINU0925)", "Raw water tank inlet",
     "Raw water quality for make-up and reagent preparation", "2 Recommended", "C7",
     "Weekly grab, preserved for metals", None, None, "=1/7", pk("WTR"), LAB_STREAMS[6],
     "Manual registration with barcode label; preservation recorded",
     "Tap with flush at tank inlet", "Raw water pipe is buried scope (SoW 6.5.2, p.265); tap and pit by Contractor if specified",
     "Stated bores (SoW p.265)", "Hydrogeology (#4) and water balance (#3, #7) describe groundwater and borefield supply; chemistry is in #4."),
    ("SP-802", 800, "Process water distribution header", "Process water tank outlet",
     "Process water chemistry (TDS, hardness, pH, Cu) for flotation control", "1 Essential", "C7",
     "Daily grab", "Online pH and conductivity", None, 1, pk("WTR"), LAB_STREAMS[6],
     "Manual registration with barcode label", "Tap with flush at tank outlet", CON_FOUND,
     "Assumed", "Process water is a blend of reclaim, clean water dam and bore water (water balance priority table), so its chemistry changes with supply."),
    ("SP-803", 800, "Clean water pond / dam outlet", "Clean water pond transfer pump",
     "Source water quality (pit dewatering and bores)", "2 Recommended", "C7",
     "Weekly grab", None, None, "=1/7", pk("WTR"), LAB_STREAMS[6],
     "Manual registration with barcode label", "Tap at pump station",
     "Clean water pond is Contractor scope (design: Knight Piesold, #10/#11, 400,000 m3)", "Stated facility (#10, #11)", None),
    ("SP-804", 800, "Wastewater treatment plant effluent", "WWTP outlet",
     "Compliance with discharge licence", "3 Optional / survey", "C7",
     "Weekly grab by a licensed collector", None, None, "=1/7", pk("WTR"), LAB_STREAMS[6],
     "Register only; analysis by an external NATA laboratory",
     "Outlet tap and flow measurement", "Wastewater is a named MPP utility (SoW 2.4, p.211)", "Stated utility",
     "Licence parameters are not in the pack."),
]

# ---- notional flowsheet basis -------------------------------------------------------------------------
FLOW = [
    ("1", "ROM pad, dump pocket, primary crusher, stockpile", "Stated: ROM wall, dump pocket, Primary Crusher (SoW p.233, 252, 322)", "SP-101, SP-102"),
    ("2", "COS reclaim chamber and SAG mill feed conveyors", "Stated: COS reclaim chamber, SAG mill feed conveyors (p.322)", "SP-103, SP-104"),
    ("3", "SAG mill, cyclones (grinding and classification)", "Stated: grinding and classification, mill plinths, mill deck (p.211 and Process Review equipment list). Mill types and sizes not stated", "SP-201 to SP-204"),
    ("4", "Oversized (pebble) crushing", "Stated: Oversized Crushing process area; crusher type assumed", "SP-251"),
    ("5", "Gravity gold concentration", "Stated: gravity gold concentration facility (p.211). Circuit position assumed", "SP-301 to SP-303"),
    ("6", "Rougher / scavenger / cleaner flotation and regrind", "Stated: Flotation and Regrind area (Milestone 1). Bank layout and cell counts not stated: ASSUMPTION", "SP-401 to SP-409"),
    ("7", "High- / low-sulphur tailings split", "Stated in the water balance (#7): HS about 6% of tailings. Split location assumed", "SP-410, SP-411"),
    ("8", "Concentrate thickening and filtration", "Stated: Concentrate Dewatering area (Milestone 4). Thickener / filter types assumed", "SP-501 to SP-504"),
    ("9", "Product sampling, handling, stockpile, reclaim, load-out", "Stated: product sampling, handling, conveying, stockpiling, reclaiming (p.211)", "SP-505 to SP-507"),
    ("10", "LST thickeners, HS cell delivery, TSF reclaim", "Stated: LST thickeners (Process Review equipment list); HS and LS cells and Reclaim Pond (#7)", "SP-601 to SP-605"),
    ("11", "Reagents storage and make-up", "Stated: Reagents area and Plant Reagent Storage building (p.272). Reagent types not stated", "SP-701, SP-702"),
    ("12", "Raw, process, clean water, wastewater", "Stated: plant utilities (water, wastewater); bores WINU0913 / WINU0925 (p.265); clean water pond (#10, #11)", "SP-801 to SP-804"),
]

# ---- RFIs and gaps ------------------------------------------------------------------------------------
RFIS = [
    ("R1", "Scope", "Who supplies and installs samplers, analysers, sample cabins and sample transport for the MPP?",
     "MPP above top of concrete, including E, I and communications, is by others (SoW s18, p.322-323). The Contractor installs 'samplers, analysers and in-line instruments' only in non-MPP piping (p.277).",
     "Confirm samplers are MPP EPC scope and that the Contractor provides only the embeds, sumps, launders, plinths, conduits and pits listed on the Sample_Points sheet.", "High"),
    ("R2", "Programme", "Fix sample point locations before each area's concrete milestone.",
     "Launder drops, sample return sumps, cabin plinths and conduit routes are cast into MPP concrete. First milestone is Flotation and Regrind on 11 Oct 2028; Site Access is 23 Nov 2027.",
     "Issue this sample point layout to the MPP EPC designer as an input to the concrete design; latest dates are on the Sample_Points sheet.", "High"),
    ("R3", "Basis", "Provide the MPP flowsheet, mass balance and P&IDs.",
     "None are in the pack (Process Review) and none are in the technical folder (Document Register summary: no flowsheet or metallurgical testwork). All flowsheet-dependent points are flagged 'Assumed flowsheet'.",
     "Re-run the sample point list against the real flowsheet; delete or add survey points.", "High"),
    ("R4", "Basis", "Provide head grade, ore types and metallurgical testwork.",
     "Water balance (#7) names oxide, secondary and primary ore with different water demand, so sequential Cu is kept as a routine test on plant feed. Feed Cu and Au grade, Au deportment and nugget effect are unknown, so sampler increment mass is provisional.",
     "Run a sampling-theory study (fundamental sampling error by stream) before sampler selection.", "High"),
    ("R5", "Commercial", "Provide offtake terms and the concentrate sampling standard.",
     "Product sampling (SP-505, SP-506) follows an assumed ISO 12743 approach; the offtake agreement, umpire rules, penalty elements and TML method are not in the pack.",
     "Confirm sampling, splitting and umpire clauses before sampler design.", "High"),
    ("R6", "Scope", "Assign sampling responsibility for the first ~600 kt of ore.",
     "Process Review G-59: tonnage measurement basis and sampling responsibility are not stated; the Contractor stockpiles the ore but no sampling is specified.",
     "State who samples, how lots are defined (truck, bench, stockpile) and how results reconcile to plant weightometers.", "Medium"),
    ("R7", "Interface", "Define the plant-to-CCLAS data exchange.",
     "LIMS.drawio shows an 'Automated Data Exchange' link with no endpoints. Sampler PLC to CCLAS (sample created, composite closed, label printed) and DCS tag exchange are not defined.",
     "Agree sample ID format, trigger events and result return to the plant information system.", "Medium"),
    ("R8", "Conflict", "Tailings delivery scope conflict.",
     "Process Review finding 12(a): s18 excludes 'TSF process and delivery systems' but TSF scope includes tailings pipeline corridors, sumps and spigot protection and the concrete scope includes WBS 2458 Tailings Pumping and Delivery. SP-603, SP-604 and SP-605 sit on this boundary.",
     "Clarify who provides taps and access at the TSF corridor and reclaim pump station.", "Medium"),
    ("R9", "Gold", "State the gravity concentrate treatment route.",
     "Intensive leach, direct smelting or sale with Cu concentrate are all plausible; each needs different sampling and security (SP-302).",
     "Confirm route and any gold room before the secure sample room is sized.", "Medium"),
    ("R10", "Lab", "Confirm a TML method and owner.",
     "TML is a shipping requirement but no TML apparatus is in the laboratory workbook.",
     "Add TML to the laboratory instrument list or contract it out.", "Medium"),
    ("R11", "Lab", "Confirm that online XRF-type stream analysers are acceptable.",
     "The laboratory workbook excludes XRF as an iron-ore method. Online stream analysers on flotation streams are a separate plant-control item; they are listed as options only.",
     "Decide with the Process Engineer; if adopted, they need a DCS interface, not a CCLAS one.", "Low"),
    ("R12", "Environment", "Water discharge licence parameters.",
     "SP-804 and SP-803 need the licence parameter list; not in the pack.", "Provide licence conditions.", "Low"),
]

# ---- source trace -------------------------------------------------------------------------------------
SOURCES = [
    ("Process Review", "WIN-CON-EPC-001_Process_Review.html", "10 Mtpa, ~25% Cu concentrate; MPP facility breakdown (SoW 2.4, p.211); named equipment and process areas; nine concrete milestone dates (AGR Item 13(c), p.55); Laboratory 503 m2 and Sample Storage 180 m2 (p.272); MPP above top of concrete by others (s18, p.322-323); gaps G-58 to G-61; finding 12(a)."),
    ("Document Register #7", "311012-01475-REP-WB-039.00.INF.pdf (Water Balance 2025, Worley)", "HS tailings ~6% to water-covered cell; LS cell; Reclaim Pond; Clean Water Dam; oxide / secondary / primary water demand 980 / 870 / 800 L/t; base tailings density 64% oxide, 68% sulphide; supply priority table. Verified in the PDF text."),
    ("Document Register #3", "311012-01475-5.1.3-TM-001.01.INF.pdf (Water Balance and Dewatering Update 2023)", "Process vs non-process demand and TSF return; cited from the register description."),
    ("Document Register #4", "311012-01475-REP-HG-032.01.USE.pdf (H3 Hydrogeological Assessment)", "Groundwater chemistry and borefield supply; cited from the register description."),
    ("Document Register #10, #11", "C0007-0300-B-REP-00003.C (Clean Water Pond Design Report)", "400,000 m3 clean water pond for process water from pit dewatering and borefield; cited from the register description."),
    ("Document Register #28", "C0007-2300-G-PRE-00002.A.INF.pdf (Yearly TSF Development)", "TSF Cells 1 and 2 development; cited from the register description."),
    ("Document Register #19", "C0007-0300-C-REP-00033.00.INF.pdf (Factual Geotechnical Report - Process Plant and NPI)", "Process plant foundation zones; relevant to sampler plinths and sumps; not read in detail."),
    ("Document Register summary", "Summary sheet, Notes", "No file in the folder is principally about process / metallurgy or laboratory operations; no flowsheet, metallurgical testwork or assay QA/QC document. Process Engineer appears only as a secondary discipline in 6 files."),
    ("Lab workbook", "input/Vendor/Datamine (CCLAS)/Winu_Lab_Instrumentation_Requirements.xlsx", "Lab stream names; plant demand assumptions (12 / 42 / 4 / 6 / 10 / 10 samples per day); instrument capacities and utilisation 0.8; QA/QC uplift 0.1."),
    ("Module matrix", "input/Vendor/Datamine (CCLAS)/Winu_CCLAS_Instrument_Module_Matrix.xlsx", "Peak instrument quantities; CCLAS module names (sample receipt, barcode and chain of custody, instrument result capture, Taskman, automated data exchange)."),
]


def style_header(ws, row, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row, c)
        cell.fill, cell.font, cell.alignment = HDR, WHITE, CENTER


def build(path: Path):
    wb = Workbook()

    # ============ Notes ============
    nt = wb.active
    nt.title = "Notes"
    notes = [
        ("Title", "Winu - Processing plant (MPP) sample point design for CCLAS"),
        ("Purpose", "Defines where, how and how often the Winu processing plant is sampled, what each sample is tested for, how it enters CCLAS, and how much work it puts on the laboratory. Intended as an input to the MPP EPC designer, the CCLAS interface scope and the laboratory sizing."),
        ("Sources", "WIN-CON-EPC-001_Process_Review.html; Winu Technical Info - Document Register.xlsx (and the water balance PDF it points to); Winu_Lab_Instrumentation_Requirements.xlsx; Winu_CCLAS_Instrument_Module_Matrix.xlsx. See the Sources sheet."),
        ("Headline", "41 sample points in 9 process areas. 3 main metallurgical accounting points (flotation feed SP-203, final concentrate SP-409, tailings SP-410 / SP-411) plus plant head (SP-103) and the commercial concentrate stations (SP-505, SP-506). Counts by tier and sampler class are on the Equipment_Summary sheet; laboratory load is on Lab_Load."),
        ("Flowsheet is notional", "Neither the ITT pack nor the technical folder contains a flowsheet, mass balance or equipment list (Process Review; Document Register Summary notes). The unit operations are taken from the MPP facility breakdown and named process areas (stated) and filled in with a conventional Cu-Au layout (rougher, scavenger, cleaner, regrind). Every point is labelled Stated or Assumed in the Basis column. Re-run against the real flowsheet before use."),
        ("Why it matters now", "MPP above-ground works are by others, but the Contractor casts the MPP concrete and lays buried utilities. Launder drops, sample return sumps, cabin plinths and conduits for samplers must be fixed before each concrete milestone (first: Flotation and Regrind, 11 Oct 2028). The 'Latest fix date' column gives the date per point."),
        ("Tiers", "1 Essential = needed for metallurgical accounting, commercial settlement or a key control loop. 2 Recommended = closes the circuit balance or protects process chemistry. 3 Optional / survey = survey ports and low-frequency checks; can be added later but the port, access and drain must be built in."),
        ("Sampling rules (design intent)", "Full-stream cross-cut sampling wherever the stream can drop; in-line pipe samplers only where it cannot. Cut interval and increment mass are provisional until a sampling-theory study is done (Au nugget effect, coarse feed). Composites close at the Routine interval (h); batch and lot streams use Events per day. Each sampler writes a sample-created event and prints a barcode label at its cabin so the sample is registered in CCLAS at source."),
        ("Sample ID convention (proposed)", "P-<SP number>-<yymmdd>-<hh> for composites, P-<SP number>-<lot number> for lots and batches, e.g. P-SP103-261019-08. Confirm with Datamine against CCLAS ID rules."),
        ("QA/QC", "Inputs sheet QA/QC uplift (10%, aligned to the lab workbook) covers blanks, CRMs, duplicates and check samples. Sampling duplicates on SP-103, SP-203, SP-409, SP-411 and SP-505 are recommended to measure sampling variance; they are inside the uplift."),
        ("Stated vs assumed", "Stated: 10 Mtpa, ~25% Cu concentrate, facility list, process areas, concrete milestone dates, laboratory 503 m2, sample store 180 m2, bores WINU0913 / WINU0925, HS tailings ~6%, base tailings densities. Assumed (yellow cells and the Basis column): availability, cut intervals, composite periods, batch and lot rates, flowsheet details."),
        ("Not designed here", "Grade control and exploration drilling samples (mine side), port and ship sampling, destination sampling, TSF monitoring bores, and environmental monitoring outside the plant."),
        ("Open items", "See Interfaces_RFIs (12 items). The largest are: who supplies the samplers (R1), a real flowsheet (R3), offtake sampling terms (R5), and the concrete milestone dates (R2)."),
    ]
    for i, (a, b) in enumerate(notes, start=1):
        nt.cell(i, 1, a).font = TITLE if i == 1 else BOLD
        nt.cell(i, 1).alignment = WRAP
        nt.cell(i, 2, b).alignment = WRAP
    nt.column_dimensions["A"].width = 30
    nt.column_dimensions["B"].width = 140

    # ============ Inputs ============
    inp = wb.create_sheet("Inputs")
    inp["A1"] = "Inputs and derived values"
    inp["A1"].font = TITLE
    inp["A2"] = "Yellow cells are inputs. Stated values come from the ITT; everything else is an ASSUMPTION to replace when the design basis is issued."
    inp["A2"].alignment = WRAP
    for c, h in enumerate(["Key", "Item", "Value", "Unit", "Basis"], start=1):
        inp.cell(4, c, h)
    style_header(inp, 4, 5)
    rows = [
        ("mtpa", "Concentrator throughput", 10, "Mtpa", "Stated: SoW s2.3 PDF p.210 (Process Review)"),
        ("avail", "Plant availability", 0.92, "fraction", "ASSUMPTION: not stated in the pack"),
        ("tph", "Nominal feed rate", f"={IN_MTPA.split('!')[1]}*1000000/(8760*{IN_AVAIL.split('!')[1]})", "t/h", "Derived"),
        ("qaqc", "QA/QC insertion uplift", 0.1, "fraction", "Aligned to lab workbook Demand sheet (ASSUMPTION there)"),
        ("occ", "Weight given to occasional (○) tests", 0.25, "fraction", "ASSUMPTION: share of samples that need an occasional test"),
        ("lots", "Concentrate lots per day", 4, "lots/day", "ASSUMPTION: depends on truck size and offtake lot definition; SoW s9 logistics (PDF p.295-301) not detailed"),
        ("grav", "Gravity concentrate batches per day", 4, "batches/day", "ASSUMPTION: matches 4 samples/day for gravity in the lab workbook"),
        ("reag", "Reagent deliveries sampled per day", 0.5, "per day", "ASSUMPTION"),
        ("util", "Target instrument utilisation", 0.8, "fraction", "Lab workbook Demand sheet (ASSUMPTION there)"),
    ]
    for i, r in enumerate(rows):
        for c, v in enumerate(r, start=1):
            cell = inp.cell(5 + i, c, v)
            cell.alignment = WRAP
        if not str(r[2]).startswith("="):
            inp.cell(5 + i, 3).fill = INPUT
    inp["A16"] = "Check"
    inp["A16"].font = BOLD
    inp["B16"] = "Tonnes represented by one 4-hour SAG feed composite"
    inp["C16"] = f"={IN_TPH.split('!')[1]}*4"
    inp["D16"] = "t"
    inp["E16"] = "Derived: shows how little ore each composite represents, which is why increment mass and cut frequency matter"
    inp["C16"].number_format = "#,##0"
    inp["C7"].number_format = "#,##0"
    for col, w in zip("ABCDE", (10, 52, 14, 14, 90)):
        inp.column_dimensions[col].width = w

    # ============ Areas ============
    ar = wb.create_sheet("Areas")
    ar["A1"] = "Process areas and the concrete milestone that fixes sample station embeds"
    ar["A1"].font = TITLE
    for c, h in enumerate(["Code", "Process area", "Concrete milestone (latest date to fix embeds)", "Date", "Basis"], start=1):
        ar.cell(3, c, h)
    style_header(ar, 3, 5)
    for i, (code, name, ms, d, basis) in enumerate(AREAS):
        r = 4 + i
        ar.cell(r, 1, code)
        ar.cell(r, 2, name)
        ar.cell(r, 3, ms)
        ar.cell(r, 4, d).number_format = "dd mmm yyyy"
        ar.cell(r, 5, basis)
        for c in range(1, 6):
            ar.cell(r, c).alignment = WRAP
    r0 = 4 + len(AREAS) + 1
    ar.cell(r0, 1, "Site Access 23 Nov 2027 and Completion 30 Nov 2029 (AGR Items 12 and 13, PDF p.54-55). Other contract milestone dates are in the Process Review.").alignment = WRAP
    for col, w in zip("ABCDE", (8, 40, 52, 14, 80)):
        ar.column_dimensions[col].width = w
    ar_last = 3 + len(AREAS)

    # ============ Sample_Points ============
    sp = wb.create_sheet("Sample_Points")
    sp["A1"] = "Winu processing plant (MPP) sample point register"
    sp["A1"].font = TITLE
    sp["A2"] = ("● = routine test on this stream   ○ = occasional test (weighted by Inputs). Yellow = input. Samples/day = 24 / Routine interval, or Events/day for batch, lot and "
                "scheduled-grab streams. Locations are notional until a flowsheet is issued.")
    sp["A2"].alignment = WRAP
    base_hdr = ["ID", "Area code", "Process area", "Stream", "Notional location / equipment", "Purpose", "Tier", "Sampler class",
                "Sampling method and cut basis", "Companion measurement / online analyser", "Routine interval (h)", "Events / day", "Samples / day"]
    tail_hdr = ["Lab stream (lab workbook)", "CCLAS registration route", "Installation needs", "Contractor (WIN-CON-EPC-001) touchpoint",
                "Latest fix date (concrete milestone)", "Basis", "Rationale / source note"]
    hdr = base_hdr + [f"{k}\n{h}" for k, h, *_ in PKGS] + tail_hdr
    HR = 4
    for c, h in enumerate(hdr, start=1):
        sp.cell(HR, c, h)
    style_header(sp, HR, len(hdr))
    sp.row_dimensions[HR].height = 75
    c_int, c_ev, c_smp = 11, 12, 13
    c_pk0 = 14
    c_lab = c_pk0 + len(PKGS)
    c_fix = c_lab + 4
    area_name = {a[0]: a[1] for a in AREAS}
    for i, row in enumerate(SP):
        (sid, area, stream, loc, purpose, tier, cls, method, comp, interval, events, packs, labs, cclas, inst, touch, basis, why) = row
        r = HR + 1 + i
        vals = [sid, area, area_name[area], stream, loc, purpose, tier, CLASS_NAME[cls], method, comp, interval, events]
        for c, v in enumerate(vals, start=1):
            sp.cell(r, c, v)
        sp.cell(r, c_smp, f'=IF(K{r}>0,24/K{r},N(L{r}))')
        sp.cell(r, c_smp).number_format = "0.00"
        for j, k in enumerate(PKG_KEYS):
            if k in packs:
                sp.cell(r, c_pk0 + j, packs[k]).alignment = CENTER
        sp.cell(r, c_lab, labs)
        sp.cell(r, c_lab + 1, cclas)
        sp.cell(r, c_lab + 2, inst)
        sp.cell(r, c_lab + 3, touch)
        sp.cell(r, c_fix, f"=VLOOKUP(B{r},Areas!$A$4:$D${ar_last},4,FALSE)").number_format = "dd mmm yyyy"
        sp.cell(r, c_fix + 1, basis)
        sp.cell(r, c_fix + 2, why)
        for c in range(1, len(hdr) + 1):
            if c < c_pk0 or c >= c_lab:
                sp.cell(r, c).alignment = WRAP
        sp.cell(r, 7).fill = TIER_FILL[tier]
        for c in (c_int, c_ev):
            sp.cell(r, c).fill = INPUT
            sp.cell(r, c).alignment = CENTER
        sp.cell(r, c_smp).alignment = CENTER
        sp.cell(r, 2).alignment = CENTER
        sp.cell(r, 1).font = BOLD
        if isinstance(events, str) and events.startswith("="):
            sp.cell(r, c_ev).number_format = "0.000"
    last = HR + len(SP)
    widths = {1: 9, 2: 7, 3: 22, 4: 30, 5: 34, 6: 34, 7: 14, 8: 26, 9: 50, 10: 30, 11: 9, 12: 9, 13: 9}
    for c, w in widths.items():
        sp.column_dimensions[CL(c)].width = w
    for j in range(len(PKGS)):
        sp.column_dimensions[CL(c_pk0 + j)].width = 8
    for off, w in enumerate((26, 32, 36, 52, 14, 22, 52)):
        sp.column_dimensions[CL(c_lab + off)].width = w
    sp.freeze_panes = sp.cell(HR + 1, 5)
    sp.auto_filter.ref = f"A{HR}:{CL(len(hdr))}{last}"

    # ============ Flowsheet_Basis ============
    fb = wb.create_sheet("Flowsheet_Basis")
    fb["A1"] = "Notional flowsheet used to place the sample points"
    fb["A1"].font = TITLE
    fb["A2"] = "The pack gives the facility list and process area names but no flowsheet. Order below is the conventional Cu-Au sequence."
    for c, h in enumerate(["Step", "Unit operation", "Basis in the pack", "Sample points"], start=1):
        fb.cell(4, c, h)
    style_header(fb, 4, 4)
    for i, row in enumerate(FLOW):
        for c, v in enumerate(row, start=1):
            fb.cell(5 + i, c, v).alignment = WRAP
    for col, w in zip("ABCD", (7, 52, 100, 22)):
        fb.column_dimensions[col].width = w

    # ============ Lab_Load ============
    ll = wb.create_sheet("Lab_Load")
    ll["A1"] = "Laboratory load from the plant sample points"
    ll["A1"].font = TITLE
    ll["A2"] = "All values are formulas on Sample_Points and Inputs. QA/QC uplift is applied to routine samples."
    spr = f"Sample_Points!$%s${HR + 1}:$%s${last}"

    def rng(col):
        return spr % (CL(col), CL(col))

    # Table A: streams
    ll["A4"] = "A. Samples per day by laboratory stream, against the lab workbook Demand sheet"
    ll["A4"].font = BOLD
    for c, h in enumerate(["Lab stream", "Points", "Samples/day (routine)", "Samples/day incl. QA/QC", "Lab workbook Demand assumption (samples/day)", "Difference", "Note"], start=1):
        ll.cell(5, c, h)
    style_header(ll, 5, 7)
    lab_demand = {
        LAB_STREAMS[0]: (12, "Lab workbook: 4 composites x 3 shifts"),
        LAB_STREAMS[1]: (42, "Lab workbook: 14 streams x 3 composites"),
        LAB_STREAMS[2]: (4, "Lab workbook: assumption"),
        LAB_STREAMS[3]: (6, "Lab workbook: 2 streams x 3 shifts"),
        LAB_STREAMS[4]: (10, "Lab workbook: 'shift and lot samples'; also covers the moisture / TML row below"),
        LAB_STREAMS[5]: (None, "Included in the Cu concentrate demand above"),
        LAB_STREAMS[6]: (10, "Lab workbook: process and environmental water"),
        LAB_STREAMS[7]: (None, "New stream: not in the lab workbook"),
    }
    for i, s in enumerate(LAB_STREAMS):
        r = 6 + i
        ll.cell(r, 1, s)
        ll.cell(r, 2, f"=COUNTIF({rng(c_lab)},A{r})")
        ll.cell(r, 3, f"=SUMIF({rng(c_lab)},A{r},{rng(c_smp)})").number_format = "0.0"
        ll.cell(r, 4, f"=C{r}*(1+{IN_QAQC})").number_format = "0.0"
        d, note = lab_demand[s]
        if d is not None:
            ll.cell(r, 5, d)
        ll.cell(r, 7, note)
    # combined concentrate row for comparison
    ll.cell(5 + len(LAB_STREAMS) + 1, 1, "Total plant samples/day").font = BOLD
    rt = 5 + len(LAB_STREAMS) + 1
    ll.cell(rt, 2, f"=SUM(B6:B{rt - 1})")
    ll.cell(rt, 3, f"=SUM(C6:C{rt - 1})").number_format = "0.0"
    ll.cell(rt, 4, f"=SUM(D6:D{rt - 1})").number_format = "0.0"
    ll.cell(rt, 5, f"=SUM(E6:E{rt - 1})")
    ll.cell(rt, 6, f"=D{rt}-E{rt}").number_format = "0.0"
    ll.cell(rt, 7, "Design load against the lab workbook's plant-side assumptions (feed, flotation, gravity, tailings, concentrate, water)")
    for r in range(6, rt):
        if ll.cell(r, 5).value is not None:
            ll.cell(r, 6, f"=D{r}-E{r}").number_format = "0.0"
    # concentrate pair difference
    ll.cell(10, 6, "=(D10+D11)-E10").number_format = "0.0"
    ll.cell(10, 7, "Lab workbook: 'shift and lot samples'; compare with rows 10 + 11 together (difference shown here)")
    ll.cell(11, 6, None)
    for r in range(6, rt + 1):
        for c in range(1, 8):
            ll.cell(r, c).alignment = WRAP

    # Table B: packages
    tb = rt + 3
    ll.cell(tb - 1, 1, "B. Tests per day by package, and plant share of the instrument capacity in the lab workbook").font = BOLD
    hdrs = ["Package", "Description", "Tests/day incl. QA/QC", "Lab instrument (lab workbook ref)", "Instrument capacity in lab workbook (tests/day)",
            "Plant share of capacity", "Capacity basis"]
    for c, h in enumerate(hdrs, start=1):
        ll.cell(tb, c, h)
    style_header(ll, tb, 7)
    cap_basis = {
        "CUF": (6 * 160, "A4 hot-block digestion: peak qty 6 x 160/day x utilisation"),
        "AUF": (3 * 400, "A1 fire assay furnace: peak qty 3 x 400/day x utilisation"),
        "SEQ": (3 * 600, "A3 AAS: peak qty 3 x 600/day x utilisation (shared with the Au finish)"),
        "SC": (2 * 250, "A7 Leco: peak qty 2 x 250/day x utilisation"),
        "ME": (1 * 350, "A6 ICP-MS: peak qty 1 x 350/day x utilisation"),
        "HG": (1 * 200, "A8 mercury analyser: peak qty 1 x 200/day x utilisation"),
        "PSD": (1 * 100, "A10 laser PSD: peak qty 1 x 100/day x utilisation"),
    }
    for i, (k, h, desc, inst) in enumerate(PKGS):
        r = tb + 1 + i
        col = c_pk0 + i
        rg = rng(col)
        ll.cell(r, 1, k).font = BOLD
        ll.cell(r, 2, f"{h}. {desc}")
        ll.cell(r, 3, f'=(SUMPRODUCT(({rg}="{P}")*{rng(c_smp)})+{IN_OCC}*SUMPRODUCT(({rg}="{O}")*{rng(c_smp)}))*(1+{IN_QAQC})').number_format = "0.0"
        ll.cell(r, 4, inst)
        if k in cap_basis:
            n, basis = cap_basis[k]
            ll.cell(r, 5, f"={n}*{IN_UTIL}").number_format = "#,##0"
            ll.cell(r, 6, f"=C{r}/E{r}").number_format = "0.0%"
            ll.cell(r, 7, basis + ". Quantities from the module matrix; capacities are lab-workbook ASSUMPTIONS.")
        else:
            ll.cell(r, 7, "No capacity figure in the lab workbook for this test")
        for c in range(1, 8):
            ll.cell(r, c).alignment = WRAP
    tb_end = tb + len(PKGS)
    ll.cell(tb_end + 2, 1, "Reading the result: the plant is a small share of instrument capacity; grade control from the pit is the lab's sizing driver. The plant matters more for turnaround (composites needed within hours for control) and for sample-registration points than for instrument count. "
                           "Particle size is the exception: the plant would use about 45% of the single laser PSD in the lab workbook, so cyclone and regrind P80 control should rely on online particle size monitors (SP-203, SP-406) with the lab as the check. "
                           "Plant tests marked 'Plant laboratory bench' (SOL, MOI, REAG) and TML are not sized in the lab workbook.").alignment = WRAP
    ll.merge_cells(start_row=tb_end + 2, start_column=1, end_row=tb_end + 2, end_column=7)
    ll.row_dimensions[tb_end + 2].height = 64
    for col, w in zip("ABCDEFG", (36, 58, 18, 40, 22, 14, 70)):
        ll.column_dimensions[col].width = w

    # ============ Equipment_Summary ============
    es = wb.create_sheet("Equipment_Summary")
    es["A1"] = "Sampler summary"
    es["A1"].font = TITLE
    for c, h in enumerate(["Class", "Sampler class", "Points", "Typical specification (design intent)", "Services and civil needs"], start=1):
        es.cell(3, c, h)
    style_header(es, 3, 5)
    for i, (code, name, spec, svc) in enumerate(CLASSES):
        r = 4 + i
        es.cell(r, 1, code)
        es.cell(r, 2, name)
        es.cell(r, 3, f"=COUNTIF({rng(8)},B{r})")
        es.cell(r, 4, spec)
        es.cell(r, 5, svc)
        for c in range(1, 6):
            es.cell(r, c).alignment = WRAP
    rr = 4 + len(CLASSES)
    es.cell(rr, 2, "Total").font = BOLD
    es.cell(rr, 3, f"=SUM(C4:C{rr - 1})").font = BOLD

    ra = rr + 3
    es.cell(ra - 1, 1, "Points by tier").font = BOLD
    for c, h in enumerate(["", "Tier", "Points"], start=1):
        es.cell(ra, c, h)
    style_header(es, ra, 3)
    for i, t in enumerate(TIER_FILL):
        es.cell(ra + 1 + i, 2, t).fill = TIER_FILL[t]
        es.cell(ra + 1 + i, 3, f"=COUNTIF({rng(7)},B{ra + 1 + i})")
    rb = ra + 1 + len(TIER_FILL) + 2
    es.cell(rb - 1, 1, "Points by process area").font = BOLD
    for c, h in enumerate(["Code", "Process area", "Points", "Tier 1", "Latest fix date"], start=1):
        es.cell(rb, c, h)
    style_header(es, rb, 5)
    for i, (code, name, *_rest) in enumerate(AREAS):
        r = rb + 1 + i
        es.cell(r, 1, code)
        es.cell(r, 2, name)
        es.cell(r, 3, f"=COUNTIF({rng(2)},A{r})")
        es.cell(r, 4, f'=COUNTIFS({rng(2)},A{r},{rng(7)},"1 Essential")')
        es.cell(r, 5, f"=VLOOKUP(A{r},Areas!$A$4:$D${ar_last},4,FALSE)").number_format = "dd mmm yyyy"
    rc = rb + 1 + len(AREAS) + 1
    es.cell(rc, 2, "Points with an online analyser option (OSA)").font = BOLD
    es.cell(rc, 3, f'=COUNTIF({rng(10)},"*stream analyser*")')
    es.cell(rc + 1, 2, "Points with a density gauge companion").font = BOLD
    es.cell(rc + 1, 3, f'=COUNTIF({rng(10)},"*density gauge*")')
    es.cell(rc + 2, 2, "Points with a weightometer companion").font = BOLD
    es.cell(rc + 2, 3, f'=COUNTIF({rng(10)},"*weightometer*")')
    for col, w in zip("ABCDE", (10, 52, 10, 70, 70)):
        es.column_dimensions[col].width = w

    # ============ Interfaces_RFIs ============
    rf = wb.create_sheet("Interfaces_RFIs")
    rf["A1"] = "Interfaces, gaps and clarification questions"
    rf["A1"].font = TITLE
    for c, h in enumerate(["#", "Type", "Question", "Why it matters / evidence", "Proposed action", "Priority"], start=1):
        rf.cell(3, c, h)
    style_header(rf, 3, 6)
    for i, row in enumerate(RFIS):
        for c, v in enumerate(row, start=1):
            rf.cell(4 + i, c, v).alignment = WRAP
    rf.conditional_formatting.add(f"F4:F{3 + len(RFIS)}", CellIsRule(operator="equal", formula=['"High"'], fill=PatternFill("solid", fgColor="F8CBAD")))
    for col, w in zip("ABCDEF", (6, 12, 48, 90, 60, 10)):
        rf.column_dimensions[col].width = w

    # ============ Sources ============
    so = wb.create_sheet("Sources")
    so["A1"] = "Sources and how each was used"
    so["A1"].font = TITLE
    for c, h in enumerate(["Reference", "File", "Used for"], start=1):
        so.cell(3, c, h)
    style_header(so, 3, 3)
    for i, row in enumerate(SOURCES):
        for c, v in enumerate(row, start=1):
            so.cell(4 + i, c, v).alignment = WRAP
    for col, w in zip("ABC", (28, 70, 120)):
        so.column_dimensions[col].width = w

    wb.move_sheet("Sample_Points", offset=-2)  # place right after Notes
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return len(SP)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    p = Path(a.output)
    if p.exists() and not a.force:
        sys.exit(f"{p} exists; use --force")
    n = build(p)
    print(f"wrote {p} with {n} sample points")


if __name__ == "__main__":
    main()
