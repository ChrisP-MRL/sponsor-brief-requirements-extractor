# Page-by-page extraction brief (Winu ITT pack, WIN-CON-EPC-001) - process control engineer lens

You are a process control engineer extracting every fact needed to construct the processing and product handling facilities, for a FLOC (functional location) / cost-allocation workbook.
Page text is in `build/winu_pages/page_NNNN.txt` (NNNN = PDF page, 1-based, zero-padded). `build/winu_pages/pages.jsonl` has the detected printed page label per PDF page.
Read EVERY page in your range in full (use the Read tool; page files are small). Do not skim, do not use grep as a substitute for reading.
Record the PDF page AS YOU CAPTURE each item - never add page numbers afterwards or from memory.

## Referencing rule (applies to every item)
Every fact, number, tag, rating, capacity and quantity must be traceable to the page it came from. Capture it exactly as stated, with its unit, and with the clause, table, figure, drawing, datasheet or document number that states it.
- Never round, convert units, average, derive or infer a value. If the pack gives a value in one place only, cite that place. If two places differ, emit both as separate items and an `Ambiguity/Risk` item naming both pages.
- Never invent a tag, equipment number, design basis, quantity, rate or page. If a value is not stated, record that it is not stated (`Ambiguity/Risk`); do not fill the gap from experience or from typical plant practice.
- A value that is referenced but sits in a document outside the pack is `Referenced Not Included`: record the document number, revision if given, and what it is said to contain.
- Carry the source basis in `notes`: design value vs nominal vs maximum vs minimum, units, and any stated basis (e.g. dry tonnes, wet tonnes, per hour, per annum, availability).

## What the pack is (so you can place items)
Rio Tinto Projects, Winu copper-gold project (WA). Tender WIN-CON-EPC-001 "Australian Contractor", a CONSTRUCTION contract (an Offshore EPF Contractor does engineering/procurement/fabrication separately). Two Separable Parts:
- SP1 Bulk Earthworks, Concrete and Buried Utilities (bulk earthworks incl. Mine Access Road, surface water mgmt, mine pre-strip, TSF, concrete, buried utilities)
- SP2 Structural, Mechanical, Piping, Electrical, Instrumentation & Comms (Permanent Village, Aerodrome, Mine Services Area, Explosive Facility, site-wide utilities, MPP etc.)
Embedded document ranges (PDF pages): Section A Tender Docs 4-27; Section B Returnables 28-46; Form of Agreement 47-67; General Conditions 68-156; Contract Specification 157-198; Scope of Work (SoW, doc C0007-0000-G-SOW-00005, "n / 125", PDF = n+198) 199-323; Schedules 324-391; Appendices 392-638.

## What to look for (process and product handling construction data)
Work area by area through the processing plant (MPP) and the product handling chain (product stockpile/storage, reclaim, conveying, load-out, and any rail, road or port interface). For each area look for the following and capture each as its own item.

Process and capacity basis
- Throughputs, capacities, design rates, operating hours, availability and utilisation, product tonnages, storage and stockpile capacities, with units and basis.
- Process units and equipment named in the pack (crushing, grinding, flotation, thickening, filtration, concentrate storage, load-out etc.): equipment descriptions, equipment or tag numbers, quantities, sizes, masses, ratings, drives and power, materials of construction.
- Process and utility fluids: raw water, process water, potable water, air (plant/instrument), reagents, fuel, power, with stated flows, pressures, qualities and supply points.
- Tailings and water balance items that tie into the plant (pipelines, pumps, ponds, decant) with stated flows and capacities.

Construction scope on the plant and product handling facilities
- Structural, mechanical, piping, electrical, instrumentation and comms scope by area: what the Contractor erects, installs, terminates, tests and commissions, and the stated quantities (tonnes of steel, metres of pipe, cable lengths, number of items).
- Free-issue, Company-supplied and Offshore EPF supplied equipment and materials, and who unloads, stores, hauls, installs and insures each.
- Pre-assembled and modularised units: sizes, masses, delivery condition, lift and transport constraints.
- Civil and concrete interfaces to plant: foundations, bund and containment, slabs, buried utilities, earthworks pads for each facility.

Control, instrumentation and electrical
- Control philosophy and architecture: DCS/PLC/SCADA scope, control rooms, field instrument and valve counts, I/O counts, protocol and network requirements, interlock and safety instrumented system requirements, fire and gas, CCTV, access control.
- Electrical: MCC and switchroom counts, voltage levels, transformer and generator ratings, power supply and distribution, cable types and quantities, earthing and lightning protection.
- Telecommunications, fibre and radio coverage, and data links between plant, mine, village and remote operations.
- Who supplies, installs, terminates, loop-checks, calibrates, tests and commissions each of these, and where the battery limits sit.

Testing, commissioning and handover
- Pre-commissioning, cold and hot commissioning, performance and reliability tests, acceptance criteria, witness and hold points, inspection and test plans, commissioning spares, vendor representatives, operator training, and handover and as-built documentation requirements.
- Standards, codes, specifications and datasheets that govern the plant (cite the document number and the clause that invokes it).

Cost allocation and boundaries
- Anything that says how plant-related shared or indirect costs are priced, included or allocated (temporary works, cranes and access equipment, commissioning support, spares, vendor attendance, management).
- Pricing schedule lines, provisional sums and options that relate to plant or product handling.

## Laboratory - separate pass (out of scope here)
The Laboratory (site assay, sample preparation, metallurgical or environmental lab, and its equipment, analysers, LIMS and sampling systems) is extracted in its own later pass, so do not extract its detail in this one.
- Emit one `Area/Facility` marker item per page where the Laboratory is referenced, with `suggested_area` exactly "Laboratory (separate pass)", the clause in `section`, and a one-line `evidence` paraphrase. Leave `notes` null unless it gives the page of the main Laboratory scope.
- Do not capture Laboratory quantities, equipment, tags, ratings or commissioning requirements. The later pass will re-read these pages and pick them up.
- Sampling points and sample systems that sit on the process plant or product handling lines (e.g. an on-stream or load-out sampler) stay in this pass, because they are plant scope. Only the Laboratory building and its internal equipment are deferred.
- Because markers carry that exact `suggested_area` string, the later pass can filter on it to find every page to revisit.

## What to capture (one item per distinct fact)
item_type must be one of (these values are consumed by the workbook scripts; do not add or rename):
- "Scope" - an in-scope activity/deliverable/obligation (including construction, installation, termination, testing and commissioning of plant, control, electrical and comms scope)
- "Area/Facility" - a named physical area, facility, pad, pond, road, building, system, process unit or product handling facility (anything that could be a FLOC node)
- "Work Package" - a named work package / separable part / schedule line / pricing line
- "Discipline" - a discipline or trade (civil, structural, mechanical, piping, electrical, instrumentation/control, comms, commissioning) tied to scope
- "Interface" - Owner/Contractor, Contractor/Contractor, Offshore EPF, battery limit, SIMOPS, process/utility tie-in point, control system boundary
- "Exclusion" - excluded / by others / Company-supplied / free-issue
- "Provisional Sum" - provisional sums, allowances, options to be priced, PC items
- "Pricing Structure" - lump sum, schedule of rates, reimbursable, dayworks, milestone payments, pricing schedule line items
- "Commercial Form" - contract form, separable portions, payment, retention, LDs, price adjustment, risk allocation affecting cost
- "Allocation Basis" - anything that tells you how shared/indirect costs (prelims, camp, mob/demob, temporary works, commissioning, spares, management) are priced, included or allocated
- "Programme" - milestones, dates, work fronts, sequencing, commissioning and handover dates
- "Quantity/Rate Stated" - a quantity, rate, price, capacity, rating, throughput, design value or tag/equipment count actually stated (e.g. accommodation A$200/person/day, 175-person camp, a stated plant throughput in t/h)
- "Referenced Not Included" - a drawing, P&ID, datasheet, equipment list, instrument index, I/O list, cable schedule, MTO, specification, appendix, document, model or data file that is referenced but is NOT contained in the pack (or is a blank/NOT USED schedule)
- "Ambiguity/Risk" - an inconsistency, gap, unclear boundary, missing design basis, conflicting value or cost risk worth a tender query

## Output
Write a JSON array to the file path given in your task. Each element exactly:
{
 "pdf_page": <int, the physical PDF page the item appears on>,
 "section": "<clause/section number and heading as printed, e.g. '6.3.2 Detailed Scope' or 'Schedule A.1 Table A.1.1'>",
 "figure_table": "<Figure/Table/Schedule/Drawing number if relevant else null>",
 "item_type": "<one of the types above>",
 "title": "<short name, <=80 chars>",
 "evidence": "<paraphrase, or a verbatim quote of NO MORE THAN 15 words in double quotes>",
 "suggested_area": "<which Winu area/facility this belongs to, free text, e.g. 'Mineral Processing Plant - Flotation', 'Product Handling - Concentrate Load-out', 'Tailings Storage Facility', 'Site-wide / general', or null>",
 "suggested_package": "<SP1 | SP2 | Prelims | Both | Other | null>",
 "disciplines": ["..."],
 "confidence": "High|Medium|Low",   // High = explicit named area/scope/value on that page; Medium = inferred; Low = assumed
 "notes": "<value with unit exactly as stated, its basis, tag/doc/drawing number, cross-refs; keep <=200 chars; null if none>"
}
Rules: never invent quantities/rates/tags/pages. Put every stated number in `notes` (or `evidence` if quoted) with its unit; never omit the unit. If a page is a divider, blank, 'NOT USED', or boilerplate with no cost/scope relevance, emit nothing for it except 'Referenced Not Included' where a schedule is NOT USED. Quote at most 15 words. If you cannot read a page, emit an 'Ambiguity/Risk' item saying so. If a table or figure holds many values (equipment list, I/O count, rating table), emit one item per row or per logical group and cite the table in `figure_table`; do not summarise away individual values. Aim for completeness over brevity on scope/area/exclusion/pricing/allocation/quantity content (many dozens of items per ten pages is normal in the SoW); for boilerplate legal or HSE pages emit only cost-relevant facts (price adjustment, retention, LDs, free-issue, insurance costs, accommodation, audit costs, reporting deliverables with cost, etc.).
Validate your file parses with `python -I -c "import json;json.load(open(PATH))"` before finishing, and confirm every pdf_page is within your range.
Final reply: item count, any pages you could not complete, the 5 most important cost-allocation or scope-boundary findings (one line each, with PDF page), and a list of process, control or product handling data the pack references but does not contain (document number and PDF page of the reference).
