---
name: sponsor-brief
description: Generate a Concept-stage Sponsor Brief presentation by drafting content slide by slide against the MinRes Concept template
trigger_phrases:
  - create sponsor brief
  - generate sponsor brief
  - build sponsor brief
  - sponsor brief from document
---

# Sponsor Brief Generator (Concept stage)

This skill produces a MinRes **Concept-stage Sponsor Brief**: a 10-slide executive
decision document that leads with the funding ask and closes with an approval block.

It copies the template, then walks you slide by slide, writing finished copy into a
markdown file that you paste into PowerPoint. Content is drafted here; population of the
deck is manual.

**Template:** `.claude/skills/code-review/templates/Sponsor Brief - (Concept).pptx`

## Instructions

When this skill is invoked:

### 1. Gather the project header details

Ask the user for:

- **System / project name** (e.g. "PPE Express")
- **Sponsor** (the approver)
- **System Owner**
- **Category & tier** (e.g. Standard)
- **Delivery approach** (e.g. Hybrid, Waterfall, Agile)
- **Funding stage** being sought (e.g. Define)
- **Ask amount** — accept `[$amount]` if not yet known

Anything not yet known stays in `[square brackets]` and is reported back at the end.

### 2. Copy the template

Create the folder if it doesn't exist, then copy:

```bash
mkdir -p "sponsor brief"
cp ".claude/skills/code-review/templates/Sponsor Brief - (Concept).pptx" "sponsor brief/<ProjectName>-Sponsor-Brief.pptx"
```

Confirm the copy succeeded and tell the user the location. The copy already contains all
10 slides, the title-slide background image, and slide 5's value box and benefits
table — only the text needs replacing.

### 3. Create the content markdown file

Generate `output/Sponsor-Brief-<ProjectName>.md` using the **Output Format** below.
Create `output/` first if needed.

### 4. Draft each slide with the user

Work through the **Slide Guides** in order, slides 1 → 10. For each slide:

- State the purpose and what's needed
- Ask the user for the source material or facts
- Draft the copy within the stated word/bullet budget
- Write the finished copy into the markdown file (final text, not placeholders)
- Show the user the drafted text so they can paste it into PowerPoint

Do not leave `[TO BE COMPLETED]` markers behind — the markdown file is the paste source,
so every section must hold either real copy or an explicit `[N/A]`.

If a source document is available (business case, concept note), convert it first with
the `word-to-text` skill and use it as the input for drafting.

### 5. Export the risk register

Once the risks table in section 7 is populated:

```bash
python .claude/skills/scripts/export_risks_to_excel.py "output/Sponsor-Brief-<ProjectName>.md" "<ProjectName>"
```

This produces `output/Risks-<ProjectName>.xlsx`, sorted Impact H→M→L then Likelihood
H→M→L, with an auto-assigned Risk Category column. Confirm the file was created.

### 6. Summarise

Report:

- Deck path: `sponsor brief/<ProjectName>-Sponsor-Brief.pptx`
- Content path: `output/Sponsor-Brief-<ProjectName>.md`
- Risk register path: `output/Risks-<ProjectName>.xlsx`
- **Every remaining `[bracketed]` item** the user still needs to confirm (ask amount,
  dates, milestone months, links, tier score)

## Deck structure

| # | Slide | Eyebrow | Title |
|---|-------|---------|-------|
| 1 | Title | `SPONSOR BRIEF` | `<Project Name>` |
| 2 | The ask | `DECISION REQUIRED` | `THE ASK & PROJECT SUMMARY` |
| 3 | The case | `THE CASE` | `BUSINESS NEED & PROPOSED APPROACH` |
| 4 | Options | `OPTIONS` | `OPTIONS – <decision being made>` |
| 5 | Value | `VALUE` | `VALUE HYPOTHESIS & BENEFITS` |
| 6 | Alignment & cost | `ALIGNMENT & COST` | `STRATEGIC ALIGNMENT & COST–BENEFIT` |
| 7 | Scope & risk | `SCOPE & RISK` | `SCOPE & KEY RISKS` |
| 8 | Schedule | `SCHEDULE` | `TIMELINE & KEY MILESTONES` |
| 9 | Recommendation | `RECOMMENDATION` | `RECOMMENDATION, APPROVAL & SUPPORTING DOCUMENTS` |
| 10 | Appendix | `APPENDIX` | `<detail topic>` |

Always produce all 10 slides. Never delete or add slides — use `[N/A]` where a section
genuinely does not apply.

## Slide Guides

### Slide 1 — Title

**Placeholders:** Eyebrow (`SPONSOR BRIEF`, leave as-is) · Title · Subtitle · Date line

**Purpose:** Identify the brief and its decision context at a glance.

- **Title:** the system/project name only (2–4 words). Renders 44pt caps white.
- **Subtitle:** one line of context, separated by ` · `:
  `<what it is> · <where> · <decision type> · <stage> · <tier>`
  e.g. `PPE Issue & Fitting System · 18 Hasler Drive Induction Centre · Executive approval · Concept stage · Standard tier`
  Budget: ~20 words.
- **Date line:** `Sponsor: <name> · System Owner: <name> · <Date>` (~10 words)

The background photograph is already in the copied file — leave it.

### Slide 2 — The Ask & Project Summary

**Placeholders:** Left panel `THE ASK` + body · Right panel `PROJECT SUMMARY` + body

**Purpose:** State plainly what decision and what money is being sought. This is the
most important slide — an approver who reads only this should know what they're approving.

**THE ASK** (one paragraph, ~45 words):

- The exact commitment sought: `We are seeking approval to commit [$amount] to fund the <stage> stage…`
- Which tollgate this takes the project through
- What that funding buys (requirements, technology confirmation, option selection, firm estimate)
- What it precedes (e.g. Authority to Execute)

Do not describe the solution here — that's slide 3.

**PROJECT SUMMARY** (7 label:value lines, one per bullet, ~25 words total):

```text
System Name: <name>
Sponsor: <name>
System Owner: <name>
Date: [DD Month YYYY]
Category & tier: <tier>
Delivery approach: <approach>
Funding stage: <stage>
```

**Note on constraints and assumptions:** the new deck has no dedicated slides for them.
Fold anything material into this slide's ask (funding/timing constraints) or into slide 7
risks (assumptions that would hurt if false). Do not silently drop them — if the user
supplies constraints or assumptions, tell them where you placed each one.

### Slide 3 — Business Need & Proposed Approach

**Placeholders:** Left panel `BUSINESS NEED` + body · Right panel `PROPOSED APPROACH` + body

**Purpose:** Establish the problem, then the answer to it. One tight paragraph each.

**BUSINESS NEED** (~88 words, single paragraph):

- How the area operates today — concrete, with metrics or volumes where available
- What is missing or breaking, and the consequence of that gap
- Why it gets worse if untouched (growth, volume, risk exposure)
- Evidence for the problem, not just assertion

Combine current state and problem in one narrative — do not split them.

**PROPOSED APPROACH** (~76 words, single paragraph):

- What will be established, expressed as named modules or components:
  `delivered as three modules: (1) … ; (2) … ; (3) …`
- How each module addresses the need
- Delivery approach and what the solution optimises for

Keep it to this solution. Phasing detail belongs in slide 8 or the appendix.

### Slide 4 — Options

**Placeholders:** Single body placeholder

**Purpose:** Show that alternatives were considered and why the recommendation wins.

**Title:** `OPTIONS – <the specific decision>` (e.g. `OPTIONS – WORKER NOTIFICATION`).
Pick the one genuinely open decision — not every choice in the project.

**Body:** ~152 words across 4 bullets:

1. `Recommended – <option>:` how it works, indicative cost, why it wins (existing
   infrastructure, no hardware, coverage)
2. `<Option 2>:` what it is, its upside, its cost/effort downside, and when you'd
   `Consider if…`
3. `<Option 3>:` same shape — upside, downside, `Consider as…`
4. `Note:` which decision is genuinely open, that the final choice is confirmed in the
   next stage, and whether options are mutually exclusive

Be honest about the downsides of the recommended option — an options slide where the
recommendation has no drawbacks reads as pre-decided.

If there is truly no open option, keep the slide and use the body to state which decision
was closed and why, so the absence of alternatives is explicit rather than implied.

### Slide 5 — Value Hypothesis & Benefits

**Shapes:** `Rectangle 3` (the sandstone value box) and `Table 4` (2-column benefits
table) — both already exist in the copied file. Replace text only; do not redraw them.

**Purpose:** State a testable value hypothesis and give each benefit a measurement point.

**Value hypothesis** → `Rectangle 3`, ~55 words, single `If… then…` sentence:

`If <the capability is established, covering X, Y and Z> then <MinRes gets these outcomes>, while <the secondary benefit>.`

It must be falsifiable. "Improves efficiency" is not a hypothesis; "reduces time from
sizing to bag-ready" is.

**Benefits table** → `Table 4`, header row `BENEFIT` / `HOW IT'S MEASURED`, 3 data rows:

| BENEFIT | HOW IT'S MEASURED |
|---------|-------------------|
| <outcome, not activity> | <one measurement point, with baseline vs target where possible> |

Every benefit needs exactly one measurement point that feeds the later Value Assessment
Report. Prioritise quantifiable benefits; where a benefit is soft (experience,
capability), still name how you'd observe it.

At Standard tier this slide replaces a standalone Value Case.

### Slide 6 — Strategic Alignment & Cost–Benefit

**Placeholders:** Left panel `STRATEGIC ALIGNMENT` + body · Right panel `COST–BENEFIT SUMMARY` + body

**STRATEGIC ALIGNMENT** (2 bullets, ~39 words):

- Which MinRes commitment or value this supports (e.g. the safety commitment, Care) and
  which DTS/business objective it serves
- What capability or improvement it establishes beyond the immediate fix

**COST–BENEFIT SUMMARY** (5 bullets, ~70 words):

- `<Stage>-stage cost (this ask):` broken down by role, days and day rate
  (`BA 6 days @ $1,150 = $6,900`) — the only firm figure on this slide
- `Indicative build (Class 5, ±50% to +100%, to firm up in <next stage>):` per-module
  numbers with the range carried on them
- Cost of the recommended option from slide 4, also ranged
- `Contingency:` amount and the named risks it covers — never a flat percentage
- Where the benefits land (cross-reference the Value slide);
  `detail: see budget estimates [link]`

Keep the ask cost and the indicative build cost visibly separate — approvers are
committing only to the first.

#### Cost estimate discipline

A Concept-stage brief is an **AACE Class 5 estimate**: 0–5% definition maturity, accuracy
range **±50% to +100%**. Every cost statement on this slide must respect that. Full rules:
[.claude/rules/cost_estimate_guidelines.html](../rules/cost_estimate_guidelines.html).

The four that bind this slide:

1. **No single-point build figures.** `Indicative build: $180,000` is false precision at
   Class 5. Write `~$180,000 (Class 5: $90,000–$360,000)`. The ask cost is the exception —
   it is a day-rate calculation for known roles over a known number of days, so it is
   quoted firm.
2. **Contingency is always shown, and always named.** Not "30% buffer" — list the risks
   it covers, drawn from the slide 7 risk table so the two agree:
   `Contingency $45,000 – covers workflow technology unproven at MinRes, requirements
   emergence in Define`.
3. **Say where the number came from.** One clause is enough: `based on <comparable
   project>` or `parametric: <n> modules × ~$<rate>`. "Our estimate" or "based on
   experience" is not a basis.
4. **Don't write "rough".** Use the class: `Class 5 estimate, ±50% to +100%`.

If the user supplies a bare figure with no range, basis or contingency, ask for those
three before drafting the bullet. If they can't supply them, draft
`[$amount – Class 5 range, basis and contingency to confirm]` and carry it into
**Outstanding items** — do not quietly print a naked number.

Where the estimate is broken into baseline, scope emergence allowance, scope change
reserve and contingency, keep those four visibly separate rather than rolled into one
total — approvers need to see which part is scope and which part is risk.

### Slide 7 — Scope & Key Risks

**Placeholders:** Left panel `SCOPE` + body · Right panel `KEY RISKS` + body

**SCOPE** (2 bullets, ~48 words):

- `In scope:` deliverables, systems, boundaries — semicolon-separated within the bullet
- `Out of scope:` explicit exclusions, work handled separately, responsibilities
  staying with the business

Both are required. At least 2–3 items each. Out of scope manages expectations and is
where most approval disputes get prevented.

**KEY RISKS** (3 bullets, ~73 words) — each risk is one prose bullet in this exact form:

`<risk statement> – <Likelihood> / <Impact> – <mitigation>`

- **Likelihood:** Almost certain · Likely · Possible · Unlikely · Rare
- **Impact:** High · Medium · Low
- Mitigation must be an action in this or the next stage, not a hope

Example:
`Workflow solution technology may be new to MinRes – Likely / Medium – confirm technology approach and support model in Define before committing to build.`

Cover the risk types that actually apply: technical/feasibility, requirements stability,
resource availability, schedule dependency, stakeholder buy-in, external/supplier. Focus
on risks within project control, and be honest — a brief with only trivial risks
undermines its own credibility.

**These same risks are also recorded in the markdown `### Risks` table using H/M/L
codes** so the Excel export works. The table is the source of truth; the slide bullets
are its prose rendering. Keep them in step.

### Slide 8 — Timeline & Key Milestones

**Placeholders:** Single body placeholder

**Purpose:** Show the decision path and when the thing actually lands.

4 bullets, `<Milestone>: [Month YYYY]`:

```text
<Stage> Approval: [Month YYYY]
<Next stage> complete / firm estimate: [Month YYYY]
Authority to Execute: [Month YYYY]
System live at <location>: [Month YYYY]
```

Use `[Month YYYY]` brackets for anything unconfirmed. Include the go-live — a timeline
that stops at the next tollgate doesn't answer "when do we get it?".

### Slide 9 — Recommendation, Approval & Supporting Documents

**Placeholders:** Left panel `SPONSOR RECOMMENDATION & APPROVAL` + body · Right panel `SUPPORTING DOCUMENTS` + body

**Left panel** (5 bullets, ~58 words):

```text
Recommendation: I support funding the <stage> stage. <one sentence on why the outcome matters, one on why this stage is low-risk>
Decision: [Approved / Not approved / Deferred]
Approver: <sponsor name>
Date: [DD Month YYYY]
Approval reference: [email / meeting reference]
```

The recommendation is written in the sponsor's voice, first person.

**Right panel** (4 bullets, ~26 words):

```text
Concept scope / module notes: [link]
Budget estimates: [link]
<Options> assessment: [link]
Value: captured on the Value slide (no separate Value Case at <tier> tier)
```

### Slide 10 — Appendix

**Placeholders:** Single body placeholder (taller than other body slides)

**Purpose:** Hold the one piece of operational detail that proves the approach is real.

**Title:** `<TOPIC> – <SCOPE>` (e.g. `WORKFLOW – DAY 1 PPE ISSUE`)

**Body:** ~153 words, grouped process detail:

- **Bold sub-header per stage**, naming the role that owns it:
  `Sizing & order – PPE Assistant`
- Numbered steps beneath each, continuing the sequence across groups (1,2,3 / 4,5,6,7 / 8,9)
- Note explicitly what is *not* captured, where that matters
  (`Worker collection is not recorded.`)

Pick a workflow, data flow, or breakdown that answers the most likely "but how would
that actually work?" question. If there is nothing to add, keep the slide and put the
single most useful supporting detail on it rather than leaving it empty.

## Formatting rules

- **Never override fonts, sizes or colours.** All typography comes from the six slide
  layouts (`1. Title Slide`, `2. Section Divider`, `3. Title and Body`,
  `4. Title and Two Panels`, `5. Title and Grid`, `6. Title and Open Canvas`). Paste
  text into placeholders and let it inherit. If pasting brings formatting with it, use
  paste-as-text or **Home → Clear All Formatting**.
- **Do not change eyebrow or title text** except where a guide says to substitute a
  topic (slides 4 and 10, and the project name on slide 1).
- **En dash `–`** is the separator throughout (`SCOPE & KEY RISKS`, risk bullets,
  `COST–BENEFIT`). Not a hyphen.
- **`·` middle dot** separates items on the slide 1 subtitle and date lines.
- **`[Square brackets]`** mark anything unconfirmed, so it's visibly outstanding.
- **Respect the word budgets.** The layouts have no autofit — overlong text overflows
  its panel rather than shrinking.
- **10 slides always.** `[N/A]` where a section does not apply.
- Brand colours and typography: see
  [.claude/rules/MINRES_Content_Guidelines.html](../rules/MINRES_Content_Guidelines.html).
  Icons: [.claude/rules/Icon_Reference.html](../rules/Icon_Reference.html) — use the
  existing library, don't generate new icons.

## Manual population steps

Open `sponsor brief/<ProjectName>-Sponsor-Brief.pptx` and paste each markdown section
into the matching shape:

| Markdown section | Slide | Target shape |
|------------------|-------|--------------|
| 1. Title Slide | 1 | `Text Placeholder 3` (title), `4` (subtitle), `5` (sponsor/date) |
| 2. The Ask | 2 | `Text Placeholder 4` (left body) |
| 2. Project Summary | 2 | `Text Placeholder 6` (right body) |
| 3. Business Need | 3 | `Text Placeholder 4` |
| 3. Proposed Approach | 3 | `Text Placeholder 6` |
| 4. Options | 4 | `Text Placeholder 3` (body) |
| 5. Value hypothesis | 5 | **`Rectangle 3`** — the sandstone box |
| 5. Benefits table | 5 | **`Table 4`** — replace cell text, add/remove rows as needed |
| 6. Strategic Alignment | 6 | `Text Placeholder 4` |
| 6. Cost–Benefit | 6 | `Text Placeholder 6` |
| 7. Scope | 7 | `Text Placeholder 4` |
| 7. Key Risks (prose form) | 7 | `Text Placeholder 6` |
| 8. Milestones | 8 | `Text Placeholder 3` |
| 9. Recommendation & approval | 9 | `Text Placeholder 4` |
| 9. Supporting Documents | 9 | `Text Placeholder 6` |
| 10. Appendix | 10 | `Text Placeholder 3` |

Slide 1's background image and slide 5's rectangle and table are already present — they
need text replaced, not rebuilding.

To check what's currently in the deck at any point:

```bash
python .claude/skills/scripts/pptx_to_text.py "sponsor brief/<ProjectName>-Sponsor-Brief.pptx"
```

## Output Format

Generate `output/Sponsor-Brief-<ProjectName>.md` with this structure. Sections are in
slide order so the file reads as the deck reads.

```markdown
# Sponsor Brief: [Project Name]

**Stage:** Concept
**Sponsor:** [Name]
**System Owner:** [Name]
**Date:** [DD Month YYYY]

---

## 1. Title Slide

**Title:** [Project Name]

**Subtitle:** [What it is] · [Where] · [Decision type] · Concept stage · [Tier] tier

**Date line:** Sponsor: [Name] · System Owner: [Name] · [DD Month YYYY]

---

## 2. The Ask & Project Summary

### The Ask

[One paragraph, ~45 words. We are seeking approval to commit [$amount] to fund the
[stage] stage, taking the project through the [tollgate] tollgate. This funds ...
ahead of [next gate].]

### Project Summary

- System Name: [Name]
- Sponsor: [Name]
- System Owner: [Name]
- Date: [DD Month YYYY]
- Category & tier: [Tier]
- Delivery approach: [Approach]
- Funding stage: [Stage]

---

## 3. Business Need & Proposed Approach

### Business Need

[One paragraph, ~88 words: how it works today, what's missing, the consequence, why it
worsens untouched.]

### Proposed Approach

[One paragraph, ~76 words: what will be established, as named modules (1) ... (2) ...
(3) ..., plus delivery approach.]

---

## 4. Options – [Decision Being Made]

- **Recommended – [option]:** [how it works, indicative cost, why it wins]
- **[Option 2]:** [what it is, upside, downside]. Consider if [condition].
- **[Option 3]:** [what it is, upside, downside]. Consider as [condition].
- **Note:** [which decision is open, when it's confirmed, whether options are exclusive]

---

## 5. Value Hypothesis & Benefits

### Value Hypothesis

[If [capability is established, covering X, Y and Z] then [outcomes], while [secondary
benefit]. ~55 words, falsifiable.]

### Benefits

| Benefit | How it's measured |
|---------|-------------------|
| [Outcome, not activity] | [One measurement point, baseline vs target] |
| [Outcome] | [Measurement point] |
| [Outcome] | [Measurement point] |

---

## 6. Strategic Alignment & Cost–Benefit

### Strategic Alignment

- [MinRes commitment / value supported, and the business objective served]
- [Capability or improvement established beyond the immediate fix]

### Cost–Benefit Summary

- [Stage]-stage cost (this ask): [Role] [n] days @ $[rate] = $[total]; [Role] [n] days @ $[rate] = $[total]
- Indicative build (Class 5, ±50% to +100%, to firm up in [next stage]): [module] ~$[amount] ($[low]–$[high]); [module] ~$[amount] ($[low]–$[high]); basis: [comparable project / parametric rate]
- [Recommended option]: ~$[amount] ($[low]–$[high]) – [alternatives] higher
- Contingency $[amount] – covers [named risk]; [named risk]
- Benefits are primarily [themes] (see Value slide). Detail: see budget estimates [link]

---

## 7. Scope & Key Risks

### Scope

- **In scope:** [deliverable]; [deliverable]; [deliverable]
- **Out of scope:** [exclusion]; [exclusion]; [exclusion]

### Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk statement] | H/M/L | H/M/L | [Action in this or the next stage] |
| [Risk statement] | H/M/L | H/M/L | [Action] |
| [Risk statement] | H/M/L | H/M/L | [Action] |

### Key Risks — slide text

[Prose rendering of the rows above, one bullet each, for pasting into slide 7:]

- [Risk statement] – [Likelihood] / [Impact] – [mitigation].
- [Risk statement] – [Likelihood] / [Impact] – [mitigation].
- [Risk statement] – [Likelihood] / [Impact] – [mitigation].

---

## 8. Timeline & Key Milestones

- [Stage] Approval: [Month YYYY]
- [Next stage] complete / firm estimate: [Month YYYY]
- Authority to Execute: [Month YYYY]
- System live at [location]: [Month YYYY]

---

## 9. Recommendation, Approval & Supporting Documents

### Sponsor Recommendation & Approval

- Recommendation: I support funding the [stage] stage. [Why the outcome matters.] [Why this stage is low-risk.]
- Decision: [Approved / Not approved / Deferred]
- Approver: [Sponsor name]
- Date: [DD Month YYYY]
- Approval reference: [email / meeting reference]

### Supporting Documents

- Concept scope / module notes: [link]
- Budget estimates: [link]
- [Options] assessment: [link]
- Value: captured on the Value slide (no separate Value Case at [tier] tier)

---

## 10. Appendix – [Topic]

**[Stage group] – [Role]**
1. [Step]
2. [Step]
3. [Step]

**[Stage group] – [Roles]**
4. [Step]
5. [Step]

**[Stage group] – [Role]**
6. [Step]
7. [Step]

[Note what is deliberately not captured, where that matters.]

---

## Outstanding items

- [List every remaining bracketed value the sponsor needs to confirm]

---

*Generated by the Claude Code sponsor-brief skill — Concept stage, MinRes Sponsor Brief template*
```

### Why the `### Risks` table must keep this exact shape

`export_risks_to_excel.py` finds risks by matching the literal heading `### Risks`
followed immediately by a table with columns **Risk | Impact | Likelihood | Mitigation**,
and it only understands `H`/`M`/`L` for the two ratings
(see [export_risks_to_excel.py](scripts/export_risks_to_excel.py)). Keep the heading
text, the column order and the H/M/L codes exactly as shown, or the export finds nothing.
The prose form with full Likelihood words lives in the separate
`### Key Risks — slide text` block below it.

## Error handling

- `sponsor brief/` or `output/` missing → create before writing
- Template copy fails → report the error and the exact path attempted
- Risk export reports "No Risks section found" → the `### Risks` heading or the table's
  column order has drifted; restore the shape shown above
- `python-pptx` missing (only needed for the `pptx_to_text.py` check) → `pip install python-pptx`
- `openpyxl` missing (needed for the risk export) → `pip install openpyxl`
