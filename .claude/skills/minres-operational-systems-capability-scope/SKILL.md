---
name: minres-operational-systems-capability-scope
description: Classify the operational systems capabilities in a tender (ITT) on ISA-95 levels and Mining, Processing, Waste Handling and Logistics domains, decide which are within MinRes scope, and link each to the FLOCs and EWPs of the MinRes quotation scope workbook, as an Excel workbook with dashboard, interface register, EWP impact, RFI log and validation checks. Use when asked which systems, controls, FMS, communications or data capabilities fall in the MinRes quote, to scope or re-scope them for the Lead Estimator, or to re-run the Winu operational systems capability workbook after changing capabilities, interfaces, RFIs or proposed EWPs.
---

# MinRes operational systems capability scope (ISA-95)

Reads the quotation scope/EWP workbook (FLOCs, EWPs, RFIs) and the FLOC workbook (Source_Register), applies the capability content in a JSON config, and writes a new workbook. It holds no prices and does not alter the inputs.

## Files
- `config/winu_ops_config.json`: everything that can change. `capabilities` (position, level, domain, activity model, delivery type, Source IDs, FLOCs, extra EWPs, proposed EWPs, interfaces, RFIs, risk, estimation inputs), `interfaces`, `rfis` (new OPS RFIs), `assumptions`, `proposed_ewps`, `framework` (ISA-95 tables and mining adaptations), `lists`.
- `scripts/build_ops_capability_workbook.py`: the generator. Needs `openpyxl`. Run with `python -I`.

## Run (from the repository root)
```
python -I .claude/skills/minres-operational-systems-capability-scope/scripts/build_ops_capability_workbook.py \
  --config .claude/skills/minres-operational-systems-capability-scope/config/winu_ops_config.json \
  --scope-workbook output/Winu/Winu_MinRes_Quotation_Scope_and_EWP.xlsx \
  --floc-workbook  output/Winu/Winu_FLOC_Cost_Allocation_Workbook.xlsx \
  --output output/Winu/Winu_MinRes_Operational_Systems_Capability_Scope.xlsx \
  --force
```
- Without `--force` the script refuses to overwrite an existing output.
- Inputs are copied to a temp folder before reading, so an input open in Excel is not a problem.
- The script stops with a list of errors if the config names a Source ID, FLOC, EWP, RFI, interface or proposed EWP that does not exist.
- The workbook is written with formulas and no cached values. Open it in Excel (it recalculates on open).

## Changing content
Edit the config, then re-run. Edits made directly in the workbook are replaced.
- Scope position or delivery type of a capability: `position` (`pos`) and `dt` in `capabilities`. Allowed values are in `lists`. Owner, third-party and Not in ITT rows must use delivery type `None (not MinRes)`.
- FLOC and EWP links: `floc` lists FLOC IDs; EWPs are derived from the input workbook's FLOC-to-EWP mapping, plus any in `ewp`. `prop` lists proposed EWP IDs from `proposed_ewps`.
- Every capability that is not Not in ITT needs at least one Source ID in `src`. Page numbers come from the Source_Register, so do not type pages.
- New questions: add to `rfis` (ID `OPS-RFI-nn`, source, owner role from the Team sheet) and reference the ID in a capability's `rfi`. Clarify capabilities must have an RFI.
- Interfaces: `interfaces`. Use `Unassigned` as `responsible` only where the ITT does not say; it will show as a Validation failure by design.
- ISA-95 adaptations and architecture items not stated: `framework`.

## Rules
- Do not fabricate scope, standards, protocols, vendors, quantities, rates or page numbers. Use "Not stated" or "Assumption".
- Do not claim the ITT requires ISA-95. It is a classification framework only.
- Mark a capability the ITT does not support as Not in ITT and record the search basis in `note`.
- Keep Source IDs and PDF pages on every row. Do not price anything.
- Check the Validation sheet after each run. Failures on the unassigned-interface check reflect genuine ITT gaps, not build errors.
