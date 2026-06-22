---
name: sponsor-brief
description: Generate a comprehensive Sponsor Brief presentation by extracting and structuring content for each section
trigger_phrases:
  - create sponsor brief
  - generate sponsor brief
  - build sponsor brief
  - sponsor brief from document
---

# Sponsor Brief Generator

This skill generates a comprehensive Sponsor Brief presentation by analyzing source documents and structuring content according to the standard Sponsor Brief template. The skill processes each section of the brief separately to ensure thorough coverage.

## Instructions

When this skill is invoked:

1. Ask the user for the project name

2. Create the sponsor brief folder and copy the PowerPoint template:
   - Create folder if it doesn't exist: `Sponsor Brief/`
   - Copy the PowerPoint template: `cp ".claude/skills/code-review/templates/PRJ-Sponsor Brief.pptx" "Sponsor Brief/<ProjectName>-Sponsor-Brief.pptx"`
   - Confirm the file was copied successfully and inform the user of the location

3. Generate a template markdown file in the output format (see below) saved as `Output/Sponsor-Brief-<ProjectName>.md`
   - The markdown file will contain the structure with placeholder sections
   - All sections will be marked as "[TO BE COMPLETED]" for manual population later

4. Present a summary to the user with:
   - Location of the copied PowerPoint template
   - Location of the template markdown file
   - Instructions to manually populate both files using the section focuses as guidance

5. **Prompt for Business Context content (Slide 2):**
   - Ask the user to provide content for the Business Context section
   - Explain what to include (see Focus 1: Business Context below)
   - Once content is provided, summarize it to address the primary objective of the slide
   - **Output requirements:**
     - Maximum 150 words
     - Font: Arial (Body), Black, size 12
     - Focus on establishing current operational state and baseline
   - Save the summarized content to the markdown file under the Business Context section
   - Provide the formatted summary to the user for copying into the PowerPoint slide

6. **Generate Risk Excel Export:**
   - After risks are populated in the markdown file, run the export script:

     ```bash
     python .claude/skills/scripts/export_risks_to_excel.py "Output/Sponsor-Brief-<ProjectName>.md" "<ProjectName>"
     ```

   - The script will:
     - Parse the risk table from the markdown file
     - Automatically categorize risks (Technical, Resource, Schedule, Budget, Stakeholder, External)
     - Sort by Impact (H→M→L) then Likelihood (H→M→L)
     - Create an Excel file at `Output/Risks-<ProjectName>.xlsx` with formatted headers and styling
   - Confirm the Excel file was created successfully and inform the user of the location

## Section Focuses

### Focus 1: Business Context (Slide 2)
**Purpose:** Establish the current operational state and baseline

Extract and document:
- Background information about current operations
- How the business/site currently operates
- Current performance metrics (throughput, capacity, volumes)
- Current organizational structure and responsibilities
- Existing systems, processes, or technology in use
- Recent or ongoing initiatives

**Key Instructions:**
- Focus ONLY on the current state - do not include problems or proposals
- Use concrete examples and specific metrics where available
- Describe "what is" not "what should be"

### Focus 2: Business Problem (Slide 3)
**Purpose:** Define the problem or opportunity that needs to be addressed

Extract and document:
- The core business problem to be solved OR opportunity to be seized
- Type of problem (safety, productivity, cost, compliance, efficiency, etc.)
- Specific features and symptoms the business is experiencing
- Impact of not addressing this problem
- Timeline constraints or opportunity windows
- Evidence or data supporting the problem statement

**Key Instructions:**
- Be specific about the problem - avoid vague statements
- Quantify impacts where possible
- Connect the problem back to business outcomes
- Use the "however..." narrative transition from the context

### Focus 3: Options/Solutions (Slide 4)
**Purpose:** Present the proposed solution and desired outcomes

Extract and document:
- The proposed solution or approach
- How this solution addresses the identified problem
- Scope of the solution (what will be delivered/implemented)
- Expected outcomes and results
- Why this solution was chosen (if multiple options were considered)
- High-level implementation approach

**Key Instructions:**
- Keep focused on THIS solution only - avoid scope creep
- Be clear about what success looks like
- Use "therefore..." narrative to connect solution to problem
- Define measurable outcomes where possible

### Focus 4: High-Level Scope (Slide 5)
**Purpose:** Define clear boundaries for what is and isn't included

Extract and document:

**In Scope:**
- Specific deliverables for the DTS Project Delivery team
- Systems, processes, or areas to be addressed
- Stakeholder groups included
- Geographical or operational boundaries
- Timeline or phases included

**Out of Scope:**
- Explicitly excluded items to manage expectations
- Related work that will be handled separately
- Future enhancements not in current scope
- Responsibilities remaining with business units

**Key Instructions:**
- Be explicit and specific for both in-scope and out-of-scope
- Use bullet points for clarity
- Include at least 2-3 items in each category
- Avoid ambiguous statements

### Focus 5: Business Benefits/Value (Slide 6)
**Purpose:** Quantify the value and benefits of implementing the solution

Extract and document:
- Financial benefits (cost reductions, revenue increases, savings)
- Operational benefits (productivity, efficiency, throughput)
- Safety improvements
- Quality improvements
- Compliance or risk reduction benefits
- Timeline to realize benefits
- Quantifiable metrics and KPIs

**Key Instructions:**
- Prioritize quantifiable benefits with specific numbers
- Use "If we do this, then..." format
- Connect benefits directly to business objectives
- Include both immediate and long-term benefits
- Distinguish between hard and soft benefits

### Focus 6: Risks (Slide 7)
**Purpose:** Identify potential risks that could impact project success

Extract and document:
- Technical risks (feasibility, integration, complexity)
- Resource risks (availability, capability, capacity)
- Schedule risks (dependencies, critical path, delays)
- Budget risks (cost overruns, unforeseen expenses)
- Stakeholder risks (buy-in, change resistance, communication)
- External risks (market, regulatory, supplier)
- Impact and likelihood for each risk
- Mitigation strategies

**Key Instructions:**
- Be honest and comprehensive about risks
- Rate risks by impact and likelihood where possible
- Focus on risks within project control
- Include proposed mitigation approaches

**Excel Export:**

When risks are populated, automatically export them to an Excel file:
- Create file: `Output/Risks-<ProjectName>.xlsx`
- Include columns: Risk, Impact, Likelihood, Mitigation, Risk Category
- Format: Header row with bold text, auto-sized columns
- Sort by Impact (High → Medium → Low), then by Likelihood (High → Medium → Low)

### Focus 7: Constraints (Slide 8)
**Purpose:** Document fixed limitations that must be worked within

Extract and document:
- Budget constraints (fixed budget, funding limitations)
- Timeline constraints (fixed deadlines, seasonal windows)
- Resource constraints (limited personnel, equipment, facilities)
- Technical constraints (system limitations, technology restrictions)
- Regulatory or compliance constraints
- Operational constraints (site access, shutdown windows)
- Organizational constraints (approvals, governance, policies)

**Key Instructions:**
- Distinguish between constraints (fixed) and risks (probabilistic)
- Be specific about the limitation
- Note if the constraint is negotiable or fixed
- Explain impact on project approach if significant

### Focus 8: Assumptions (Slide 9)
**Purpose:** Document key assumptions the project plan depends on

Extract and document:
- Resource availability assumptions
- Budget and funding assumptions
- Stakeholder support and approval assumptions
- Technical feasibility assumptions
- Timeline assumptions (dependencies, durations)
- External factor assumptions (market, supplier, regulatory)
- Organizational support assumptions
- Assumptions about current state or baseline

**Key Instructions:**
- List specific assumptions, not general statements
- Identify assumptions that if proven false would significantly impact the project
- Note which assumptions need validation
- Connect assumptions to specific project elements

## Output Format

Generate a markdown template file with the following structure (all sections marked as TO BE COMPLETED):

```markdown
# Sponsor Brief: [Project Name]

**Sponsor:** [TO BE COMPLETED]  
**Date:** [Current Date]

---

## Business Context

[TO BE COMPLETED - See Focus 1 guidance in .claude/skills/sponsor-brief.md]

**What to include:**
- Background information about current operations
- How the business/site currently operates
- Current performance metrics (throughput, capacity, volumes)
- Current organizational structure and responsibilities
- Existing systems, processes, or technology in use
- Recent or ongoing initiatives

---

## Business Problem

[TO BE COMPLETED - See Focus 2 guidance in .claude/skills/sponsor-brief.md]

**What to include:**
- The core business problem to be solved OR opportunity to be seized
- Type of problem (safety, productivity, cost, compliance, efficiency, etc.)
- Specific features and symptoms the business is experiencing
- Impact of not addressing this problem
- Timeline constraints or opportunity windows

---

## Options/Solutions

[TO BE COMPLETED - See Focus 3 guidance in .claude/skills/sponsor-brief.md]

**What to include:**
- The proposed solution or approach
- How this solution addresses the identified problem
- Scope of the solution (what will be delivered/implemented)
- Expected outcomes and results

---

## High-Level Scope

### In Scope
- [TO BE COMPLETED - Add in-scope items]
- 
- 

### Out of Scope
- [TO BE COMPLETED - Add out-of-scope items]
- 
- 

---

## Business Benefits / Value

[TO BE COMPLETED - See Focus 5 guidance in .claude/skills/sponsor-brief.md]

**What to include:**
- Financial benefits (cost reductions, revenue increases, savings)
- Operational benefits (productivity, efficiency, throughput)
- Safety improvements
- Quality improvements
- Quantifiable metrics and KPIs

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [TO BE COMPLETED] | H/M/L | H/M/L | [Strategy] |
| | | | |
| | | | |

---

## Constraints

- [TO BE COMPLETED - Add constraints]
- 
- 

---

## Assumptions

- [TO BE COMPLETED - Add assumptions]
- 
- 

---

*Generated by Claude Code Sponsor Brief Skill - Template for Manual Population*
```

## Error Handling

- If the `Sponsor Brief/` directory doesn't exist, create it before copying the template
- If the PowerPoint template copy fails, report the error to the user
- If Output directory doesn't exist, create it before generating the template file

## Next Steps After Generation

Once the template files are created, the user should:

1. Open the PowerPoint file at `Sponsor Brief/<ProjectName>-Sponsor-Brief.pptx`
2. Refer to the markdown template at `Output/Sponsor-Brief-<ProjectName>.md` for guidance on each section
3. Use the Section Focuses documented in this skill as detailed guidance for what to include in each slide
4. Manually populate both the PowerPoint and markdown files with project-specific content
