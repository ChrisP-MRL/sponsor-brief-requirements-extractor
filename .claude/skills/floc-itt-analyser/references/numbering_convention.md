# FLOC numbering convention (adjustable per project in the config `numbering` block)

| Level | Meaning | Pattern | Example |
|---|---|---|---|
| 1 | Project | `{PREFIX}` | `WIN` |
| 2 | Area / precinct or scope stream | `{PREFIX}-{4 digits, step 100}` | `WIN-1000`, `WIN-1100` |
| 3 | System / facility | `{parent}-{2 digits}` | `WIN-1000-01` |
| 4 | Sub-system / work package | `{parent}-{2 digits}` | `WIN-1000-01-02` |
| 5 | Equipment / cost object (only where the pack names discrete items) | `{parent}-{3 digits}` | `WIN-1000-01-02-003` |

Rules
- Codes are generated in tree order by `resolve_spec.py`; the step of 100 at Level 2 leaves room to insert areas between releases without renumbering.
- Never reuse a retired code. If a node is deleted, keep the number unassigned in the change log.
- Siblings must be mutually exclusive and collectively exhaustive (MECE): each scope item maps to exactly one FLOC. Cross-cutting items (preliminaries, camp, mobilisation, commissioning support, temporary works) get their own L2 "Site-wide / shared" branch and are allocated to physical FLOCs by Allocation_Rules, not duplicated.
- A parent's description is a grouping, never a cost object that also carries its own cost; costs sit on leaves and roll up.
- Standards alignment: FLOC (asset/maintenance register style) for the tree; WBS for the project control view; CBS for cost elements; PBS for the physical breakdown. Map to the owner's own FLOC standard if one is issued (record the mapping in the notes column).
