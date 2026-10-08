# Page-by-page extraction brief (Winu ITT pack, WIN-CON-EPC-001)

You are doing the page-by-page extraction pass for a FLOC (functional location) / cost-allocation workbook.
Page text is in `build/winu_pages/page_NNNN.txt` (NNNN = PDF page, 1-based, zero-padded). `build/winu_pages/pages.jsonl` has the detected printed page label per PDF page.
Read EVERY page in your range in full (use the Read tool; page files are small). Do not skim, do not use grep as a substitute for reading.
Record the PDF page AS YOU CAPTURE each item - never add page numbers afterwards or from memory.

## What the pack is (so you can place items)
Rio Tinto Projects, Winu copper-gold project (WA). Tender WIN-CON-EPC-001 "Australian Contractor", a CONSTRUCTION contract (an Offshore EPF Contractor does engineering/procurement/fabrication separately). Two Separable Parts:
- SP1 Bulk Earthworks, Concrete and Buried Utilities (bulk earthworks incl. Mine Access Road, surface water mgmt, mine pre-strip, TSF, concrete, buried utilities)
- SP2 Structural, Mechanical, Piping, Electrical, Instrumentation & Comms (Permanent Village, Aerodrome, Mine Services Area, Explosive Facility, site-wide utilities, MPP etc.)
Embedded document ranges (PDF pages): Section A Tender Docs 4-27; Section B Returnables 28-46; Form of Agreement 47-67; General Conditions 68-156; Contract Specification 157-198; Scope of Work (SoW, doc C0007-0000-G-SOW-00005, "n / 125", PDF = n+198) 199-323; Schedules 324-391; Appendices 392-638.

## What to capture (one item per distinct fact)
item_type must be one of:
- "Scope" - an in-scope activity/deliverable/obligation
- "Area/Facility" - a named physical area, facility, pad, pond, road, building, system (anything that could be a FLOC node)
- "Work Package" - a named work package / separable part / schedule line / pricing line
- "Discipline" - a discipline or trade (civil, structural, mechanical, piping, E&I, etc.) tied to scope
- "Interface" - Owner/Contractor, Contractor/Contractor, Offshore EPF, battery limit, SIMOPS
- "Exclusion" - excluded / by others / Company-supplied / free-issue
- "Provisional Sum" - provisional sums, allowances, options to be priced, PC items
- "Pricing Structure" - lump sum, schedule of rates, reimbursable, dayworks, milestone payments, pricing schedule line items
- "Commercial Form" - contract form, separable portions, payment, retention, LDs, price adjustment, risk allocation affecting cost
- "Allocation Basis" - anything that tells you how shared/indirect costs (prelims, camp, mob/demob, temporary works, commissioning, spares, management) are priced, included or allocated
- "Programme" - milestones, dates, work fronts, sequencing
- "Quantity/Rate Stated" - a quantity, rate, price or capacity actually stated (e.g. accommodation A$200/person/day, 175-person camp)
- "Referenced Not Included" - a drawing, schedule, appendix, document, model, MTO or data file that is referenced but is NOT contained in the pack (or is a blank/NOT USED schedule)
- "Ambiguity/Risk" - an inconsistency, gap, unclear boundary or cost risk worth a tender query

## Output
Write a JSON array to the file path given in your task. Each element exactly:
{
 "pdf_page": <int, the physical PDF page the item appears on>,
 "section": "<clause/section number and heading as printed, e.g. '6.3.2 Detailed Scope' or 'Schedule A.1 Table A.1.1'>",
 "figure_table": "<Figure/Table/Schedule/Drawing number if relevant else null>",
 "item_type": "<one of the types above>",
 "title": "<short name, <=80 chars>",
 "evidence": "<paraphrase, or a verbatim quote of NO MORE THAN 15 words in double quotes>",
 "suggested_area": "<which Winu area/facility this belongs to, free text, e.g. 'Tailings Storage Facility', 'Permanent Village', 'Site-wide / general', or null>",
 "suggested_package": "<SP1 | SP2 | Prelims | Both | Other | null>",
 "disciplines": ["..."],
 "confidence": "High|Medium|Low",   // High = explicit named area/scope on that page; Medium = inferred; Low = assumed
 "notes": "<anything a QS needs: amounts, quantities, cross-refs; keep <=200 chars; null if none>"
}
Rules: never invent quantities/rates/pages. If a page is a divider, blank, 'NOT USED', or boilerplate with no cost/scope relevance, emit nothing for it except 'Referenced Not Included' where a schedule is NOT USED. Quote at most 15 words. If you cannot read a page, emit an 'Ambiguity/Risk' item saying so. Aim for completeness over brevity on scope/area/exclusion/pricing/allocation content (many dozens of items per ten pages is normal in the SoW); for boilerplate legal or HSE pages emit only cost-relevant facts (price adjustment, retention, LDs, free-issue, insurance costs, accommodation, audit costs, reporting deliverables with cost, etc.).
Validate your file parses with `python -I -c "import json;json.load(open(PATH))"` before finishing, and confirm every pdf_page is within your range.
Final reply: item count, any pages you could not complete, and the 5 most important cost-allocation or scope-boundary findings (one line each, with PDF page).
