---
name: minres-quotation-scope-ewp
description: Turn a FLOC cost-allocation workbook (from floc-itt-analyser) into a MinRes quotation scope decision for every FLOC and a set of estimation work packages (EWPs) assigned to roles, as an Excel workbook with dashboard, RFI log, inputs tracker, bid programme and validation checks. Use when asked to set what MinRes will price in a tender, regroup FLOCs into estimation packages, assign estimating work, or re-run the Winu scope and EWP workbook after changing delivery-method defaults, EWP groupings, owners or decision overrides.
---

# MinRes quotation scope and EWP workbook

Reads the FLOC workbook, applies the rules and defaults in a JSON config, and writes a workbook that sets scope and organises estimation work. It holds no costs and does not alter the input workbook.

## Files
- `config/winu_ewp_config.json`: everything that can change. Delivery defaults, EWP groupings, owners and reviewers, estimate methods, decision overrides, new bid RFIs, roles and bid dates.
- `scripts/build_ewp_workbook.py`: the generator. Needs `openpyxl`. Run with `python -I`.

## Run
```
python -I scripts/build_ewp_workbook.py \
  --input  output/Winu/Winu_FLOC_Cost_Allocation_Workbook.xlsx \
  --config config/winu_ewp_config.json \
  --output output/Winu/Winu_MinRes_Quotation_Scope_and_EWP.xlsx \
  --carry-forward
```
- Without a flag the script refuses to overwrite an existing output. `--force` overwrites.
- `--carry-forward` rebuilds from the config but keeps what people have typed into the old file: Team names and capacity, EWP status, due dates, planned and actual hours and notes, Inputs_Tracker dates and statuses, RFI owner, status and dates, and reasons for departure.
- The script stops with a list of errors if any priceable leaf FLOC has no EWP or has more than one.

## Changing a default
Edit the config, then re-run with `--carry-forward`.
- Delivery method by discipline: `delivery_by_discipline` (CIV, MIN, CON, STR, MEC, PIP, ELE, ICT, IND, COM). Per-EWP exception: `delivery_by_ewp`. Current defaults: self-perform for civil, mining, concrete, indirects and commercial; subcontract for structural, mechanical, piping, electrical and ICT; TSF liner (EWP-CIV-05) subcontract. All are labelled "Proposed - to confirm" in `delivery_basis`.
- EWP grouping: each entry in `ewps` lists FLOC IDs. An ID matches itself and its children (`WIN-1300-03` covers `WIN-1300-03-01` onwards). Every non-excluded leaf FLOC must match exactly one EWP.
- Owners and reviewers: `owner` and `reviewer` must be role names from `roles`.
- Scope decision for one FLOC: `decision_overrides` (decision, reason, linked RFIs). A decision that differs from the ITT status needs a reason, or Validation fails.
- Rule defaults (In scope to Price, Excluded to Exclude, Provisional to option, no source to Clarify): `decision_rules`.
- New RFIs: `new_rfis`; extra FLOC-to-RFI links: `extra_rfi_links`.
- Bid dates: `bid_programme`. Only enter dates the ITT states; leave others blank.

Decisions, delivery, owners and mapping come from the config. Direct edits to those columns in the workbook are replaced on a re-run, so make those changes in the config.

## Rules
- Do not fabricate quantities, rates, dates, names or scope. Use "Not stated" or "Assumption".
- Keep Source IDs and PDF pages on every row.
- Do not price anything in this workbook.
- British English and dd/mm/yyyy dates.

## After a run
1. Open the workbook in Excel so formulas calculate. No cached values are written by the script.
2. Check the Validation sheet. Due dates are not stated in the ITT, so "EWPs with no due date" fails until they are entered.
3. Report the leaf decision split, the EWP count, and any failing checks.
