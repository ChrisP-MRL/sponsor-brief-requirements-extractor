---
name: winu-prestrip-fleet
description: Size a realistic Pilbara pre-strip mining fleet (primary load and haul, drill and blast, road and dump support, dewatering, ancillary, light vehicles) and produce a monthly mining schedule with Gantt, as a formula-driven Excel workbook. Use when asked what fleet the Winu pre-strip needs, to test a different volume, duration, haul distance or fleet, to build or re-run the pre-strip mining schedule, or to compare the design fleet with the Client Supplied Fleet List.
---

# Winu pre-strip fleet and mining schedule

Builds a workbook from the ITT design parameters (21.6 Mbcm, 0-70 m stratigraphy, 10 m benches, 80% free-dig sand, XDE260-class trucks, 17 km haul roads, Wenco FMS, 14/7 roster, Separable Part 1 completion 30 Nov 2029) plus engineering assumptions held in a JSON config. The ITT gives no pre-strip duration, haul distances or fleet quantities, so those are labelled ASSUMPTION on the Inputs sheet.

## Files
- `config/winu_prestrip_fleet.json`: every input with unit and source or ASSUMPTION note. Edit here to change the defaults.
- `scripts/build_prestrip_fleet.py`: the generator. Needs `openpyxl`. Run with `python -I`.

## Run
```
python -I .claude/skills/winu-prestrip-fleet/scripts/build_prestrip_fleet.py \
  --config .claude/skills/winu-prestrip-fleet/config/winu_prestrip_fleet.json \
  --output output/Winu/Winu_PreStrip_Fleet_and_Schedule.xlsx \
  --carry-forward
```
- Without a flag the script refuses to overwrite an existing output. `--force` overwrites.
- `--carry-forward` rebuilds from the config but keeps what was typed into the old workbook: fleet Override quantities, Client Supplied Fleet List quantities, and monthly volume overrides.
- The output is formulas only. Excel calculates it on open. Check that the Checks sheet reads ALL OK.

## Changing volume or fleet (no re-run needed)
- Volume, duration, start date, haul distances, destination mix, productivities, ratios: Inputs sheet, yellow cells.
- Test a specific fleet: Fleet_Register, Override column. Blank uses the calculated quantity. The Schedule uses the selected quantity, so fewer trucks lengthen the schedule and the Checks sheet flags it.
- Impose a production profile: Schedule column M (volume override). Months above fleet capacity are flagged.
- Compare with the free-issued fleet: type quantities from C-WN-0000-G-LST-00005 into the Client fleet list column of Fleet_Register.

## When to re-run the script
Only when the structure changes: new default inputs in the JSON, new equipment rows, a different number of months (`NMONTHS` in the script), or new material classes. Update the JSON, re-run with `--carry-forward`.

## Method
1. Volume splits by stratigraphy thickness: free-dig sand, blasted sand, cemented sand / sandstone, mudstone / leach cap, plus TSF stockpile re-handle.
2. Truck cycle = load passes + spot + ramp (depth / gradient) + in-pit flat + surface lead (weighted by destination mix) + dump + queue, at operating efficiency.
3. Required hours / available hours per unit over the target window gives units. Contingency on trucks, minimum dig faces, drills and charging units.
4. Ratios give dozers, graders, water carts, service, fuel, lighting, light vehicles, buses and FMS units from the selected fleet.
5. Schedule: monthly capacity = lesser of truck, excavator and drill capacity, with weather days and ramp-up, limited by remaining volume. Material is mined top-down.

## Caveats to state when reporting results
- Haul distances, destination volumes, densities, productivities and the pre-strip duration are assumptions. Replace them from the Haul Infinity model (C0007-REF-00340), the waste rock landform design and the Three Month Production Plan.
- Primary HME is marked Company free-issue (assumed). Confirm against the Client Supplied Fleet List, which is not in the ITT PDF.
- Truck and excavator class figures are nominal for the XCMG XDE260 class and a matched ~700 t excavator, not manufacturer data.
- Monthly material splits are indicative because a real plan works several benches and both cutbacks at once.
- Fuel, people and light vehicle counts are order-of-magnitude.
