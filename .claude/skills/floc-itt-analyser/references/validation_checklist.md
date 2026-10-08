# Validation checklist (mirrors the Validation sheet)

Automated by `scripts/validate.py` (run inside `build_workbook.py`):
- [ ] FLOCs with no Source ID: zero, or explicitly marked "No source - Assumption" and listed in Gaps_and_RFIs
- [ ] Source IDs that point to no FLOC (orphan evidence, possibly missing scope): scope-type items must be zero
- [ ] Page numbers outside the document's page count
- [ ] PDF page entered where printed page is expected, or the reverse (offset check against the config parts)
- [ ] Primary reference missing, or more than one Primary per FLOC
- [ ] Parent page range covers every child's pages
- [ ] Duplicate FLOC IDs, orphan nodes, hierarchy level gaps, unmapped scope items
- [ ] Hyperlink target page parameter equals the stated PDF page and the file exists
- [ ] Spot-check: 10% of FLOC references re-read against the page text (automated text match; 'REVIEW' rows are read by a person)

Manual before issue:
- [ ] Read the REVIEW rows and a further sample against the PDF itself (not the extracted text)
- [ ] Open three hyperlinks per part of the pack and confirm they land on the stated page; note the viewer used
- [ ] Every referenced-but-missing document or schedule appears in Gaps_and_RFIs
- [ ] No quantities, rates or amounts in the cost model other than ones the pack states
- [ ] Each allocation rule cites a Source ID or is labelled Assumption
- [ ] MECE read-through: no scope item could reasonably sit under two sibling FLOCs
- [ ] Dates dd/mm/yyyy, currency AUD, British English
