# Page-by-page extraction pass

Goal: every captured fact carries its PDF page from the moment it is recorded.

1. Read each `page_NNNN.txt` in full, in order. Do not search and skim as a substitute for reading.
2. For each distinct fact write one JSON element:
   `pdf_page` (int), `section` (clause/heading as printed), `figure_table` (Figure/Table/Schedule/Drawing no. or null), `item_type`, `title` (<=80 chars), `evidence` (paraphrase or quote of <=15 words), `suggested_area`, `suggested_package`, `disciplines[]`, `confidence` (High = explicit named area/scope; Medium = inferred; Low = assumed), `notes` (amounts, quantities, cross-refs; <=200 chars).
3. Capture, as separate items: scope and boundaries; work packages and separable parts; physical areas/facilities; disciplines; interfaces (Owner/Contractor, contractor/contractor, offshore/onshore, battery limits, SIMOPS); exclusions and Company-supplied items; provisional sums and options to be priced; pricing structure and commercial form (lump sum, schedule of rates, reimbursable, dayworks, milestones); anything that says how shared or indirect costs are priced or allocated; programme/work fronts; stated quantities, rates and capacities.
4. Referenced items that are not in the PDF (drawings, MTOs, pricing templates, schedules marked NOT USED) are `Referenced Not Included` items. Do not guess their content or page.
5. If a page has no text layer or is an image, emit an `Ambiguity/Risk` item and flag it for visual reading.
6. Validate the JSON parses and all pages are within the assigned range. Parallel owners write to separate files.

The full brief used on the Winu pack is in `references/extraction_brief.md`.
