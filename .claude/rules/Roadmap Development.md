# Claude Rule File: Enterprise Roadmap Development Using TOGAF ADM Phases E & F

```yaml
rule_name: "Enterprise Roadmap Development Framework"
rule_version: "1.0"
rule_id: "TOGAF-ROADMAP-E-F-001"
created_date: "2026-08-14"
classification: "Enterprise Architecture | Roadmap Development | TOGAF ADM"
priority: "CRITICAL"
status: "ACTIVE"

rule_metadata:
  framework_stack: "TOGAF ADM (Phases E-F) + Capability-Based Planning + MoP/MSP + PRINCE2/SAFe"
  applicable_contexts:
    - Enterprise architecture roadmapping
    - Business transformation planning
    - IT portfolio management
    - Programme/project portfolio governance
    - Strategic capability gap closure
  
  key_principle: |
    "TOGAF Phases E and F are native roadmapping engines. When solid Business/Data 
    Architectures exist (Phases A-D), use Phase E gap analysis + Capability-Based Planning 
    to define work packages and Transition Architectures. Use Phase F to sequence by value, 
    risk, and dependency. Layer MoP/MSP for governance above. Use PRINCE2/SAFe for execution 
    below. Do NOT use external roadmapping tools bolted on outside the framework; the 
    roadmap emerges natively from integrated frameworks."

---

## SECTION 1: DIAGNOSTIC PHASE
## (Determine whether to proceed with Phase E/F roadmapping)

diagnostic_phase:
  
  purpose: |
    Before proposing any roadmapping approach, conduct diagnostic assessment to 
    determine starting point, maturity, scope, and applicable frameworks.
  
  diagnostic_questions:
    
    q1_architecture_maturity:
      question: "What architecture work is complete?"
      context: "TOGAF Phases A-D are prerequisites for Phase E/F roadmapping"
      sub_questions:
        - "Is Phase A Architecture Vision complete with business drivers and scope?"
        - "Is Phase B Business Architecture complete with capability maps?"
        - "Is Phase B current-state and target-state capability maturity assessed?"
        - "Are Phases C (Data/Application) and D (Technology) complete?"
        - "Is gap analysis (baseline vs. target) available from Phases B-D?"
      
      if_incomplete_response: |
        "Architecture maturity is insufficient for Phase E/F roadmapping. 
        RECOMMENDATION: Complete Phase B Business Architecture first, particularly:
        - Business capability map (location of capabilities in org structure)
        - Current-state capability maturity assessment (1-5 scale)
        - Target-state capability maturity assessment
        - Capability gap analysis (target maturity - current maturity)
        
        Once Phase B is complete with capability assessments, Phase E/F roadmapping 
        can proceed with high confidence."
      
      if_complete_response: |
        "Architecture foundation is sufficient. Proceed to Phase E/F roadmapping 
        using Capability-Based Planning as the native technique."
    
    q2_architecture_quality:
      question: "Is the architecture quality sufficient to extract valid gaps and sequencing?"
      context: "Poor architecture quality renders Phase E/F roadmapping unreliable"
      assessment_criteria:
        - "Architecture is reviewed and approved by Architecture Review Board (ARB)"
        - "Gap analysis is quantified (not vague or subjective)"
        - "Dependencies between gaps are identified"
        - "Capability increments can be clearly defined from gaps"
        - "Business drivers are explicitly traceable to architectural decisions"
      
      if_quality_poor_response: |
        "Architecture quality is insufficient. RECOMMENDATION: 
        - Conduct architecture quality review with ARB
        - Remediate gaps in traceability, completeness, or rigor
        - Re-assess in 2-4 weeks; do not proceed with roadmapping until quality improved"
      
      if_quality_sufficient_response: |
        "Architecture quality is sufficient. Proceed with Phase E/F roadmapping."
    
    q3_delivery_model:
      question: "What is the delivery model (stage-gated, agile, hybrid)?"
      context: "Delivery model determines execution framework (PRINCE2 vs. SAFe)"
      options:
        - option: "Stage-gated/waterfall"
          description: "Sequential project phases with formal gates and sign-offs"
          recommended_execution: "PRINCE2 projects"
          roadmap_style: "Discrete, sequenced Transition Architectures"
        
        - option: "Agile/iterative"
          description: "Rolling-wave sprints, Program Increments, continuous delivery"
          recommended_execution: "SAFe Agile Release Trains (ARTs)"
          roadmap_style: "Rolling-wave roadmap mapped to PI (Program Increment) cycles"
        
        - option: "Hybrid"
          description: "Foundation phases stage-gated, then agile execution"
          recommended_execution: "PRINCE2 for foundation + SAFe for continuous delivery"
          roadmap_style: "Hybrid: initial gate to Transition Architecture, then SAFe PI planning"
    
    q4_scope_definition:
      question: "What is the roadmap scope?"
      context: "Scope determines framework complexity and governance requirements"
      scope_types:
        - scope: "Full enterprise transformation"
          domain_count: "Multiple (business, data, applications, technology)"
          timespan: "2-5 years"
          recommended_approach: "Full TOGAF Phase E/F + MSP or MoP"
        
        - scope: "Single business domain or capability stream"
          domain_count: "Single or closely related"
          timespan: "1-2 years"
          recommended_approach: "TOGAF Phase E/F (simplified) + PRINCE2 or SAFe"
        
        - scope: "Narrow technology initiative (e.g., infrastructure modernization)"
          domain_count: "Technology only"
          timespan: "6-18 months"
          recommended_approach: "Simplified TOGAF Phase E/F or Gartner approach"
    
    q5_programme_structure:
      question: "Will the roadmap produce one coordinated programme or multiple independent initiatives?"
      context: "Programme structure determines governance layer (MSP vs. MoP)"
      
      if_single_coordinated_programme: |
        "One coordinated programme delivering a unified blueprint.
        GOVERNANCE LAYER: Use MSP (Managing Successful Programmes)
        - Organize work packages into Tranches aligned to Transition Architectures
        - Establish Programme Board for governance
        - Plan benefits realization across the programme"
      
      if_multiple_independent_initiatives: |
        "Multiple semi-independent initiatives competing for resources.
        GOVERNANCE LAYER: Use MoP (Management of Portfolios)
        - Use weighted scoring to prioritize work packages
        - Make go/no-go funding decisions
        - Establish Portfolio Board for governance"
      
      if_mix_of_both: |
        "Mix of multiple programmes + portfolio-level prioritization.
        GOVERNANCE LAYER: Use both MoP (portfolio level) + MSP (programme level)"
    
    q6_governance_requirements:
      question: "What level of governance and oversight is required?"
      context: "Governance requirements determine framework rigor"
      options:
        - level: "Simple project delivery"
          description: "Single project, clear sponsor, defined constraints"
          governance_approach: "PRINCE2 only; skip portfolio/programme layer"
        
        - level: "Programme governance"
          description: "Multiple related projects delivering coordinated blueprint"
          governance_approach: "MSP programme governance + PRINCE2 project execution"
        
        - level: "Portfolio governance"
          description: "Multiple competing programmes/projects for shared resources"
          governance_approach: "MoP portfolio prioritization + MSP/PRINCE2 below"
        
        - level: "Full governance stack"
          description: "Enterprise-wide transformation with centralized resource/funding control"
          governance_approach: "TOGAF Phase E/F + MoP + MSP + PRINCE2"
    
    q7_sourcing_strategy:
      question: "Is technology/capability sourcing strategy (build vs. buy vs. outsource) strategically important?"
      context: "Sourcing strategy importance determines whether to overlay Wardley Mapping"
      
      if_sourcing_critical: |
        "Sourcing strategy is a key decision factor.
        RECOMMENDATION: Overlay WARDLEY MAPPING on top of TOGAF roadmap to visualize:
        - Component lifecycle stage (Genesis → Custom-Built → Product → Commodity)
        - Build vs. buy vs. outsource decisions at each stage
        - Strategic differentiation vs. cost optimization trade-offs"
      
      if_sourcing_not_critical: |
        "Sourcing strategy is not a primary concern; proceed without Wardley overlay."

---

## SECTION 2: NATIVE TOGAF PATH (PHASE E)
## (Gap analysis, capability increments, work packages, Transition Architectures)

phase_e_activities:
  
  phase_title: "Phase E: Opportunities & Solutions"
  phase_purpose: |
    "Identify opportunities for change, define work packages, and propose Transition 
    Architectures that bridge from Baseline to Target Architecture. Phase E outputs an 
    initial (Version 0.1) Architecture Roadmap that sequences capability increments."
  
  phase_inputs:
    - "Baseline Architecture (as-is) from Phases B-D"
    - "Target Architecture (to-be) from Phases B-D"
    - "Architecture Vision and business drivers from Phase A"
    - "Approved domain architectures (Business, Data, Application, Technology)"
  
  # ACTIVITY 1: CONSOLIDATE GAP ANALYSIS
  activity_1_consolidate_gaps:
    
    title: "Consolidate Gap Analysis Across All Domains"
    
    purpose: |
      "Organize baseline vs. target architectural gaps from Phases B-D (Business, Data, 
      Application, Technology) into a unified Consolidated Gaps, Solutions, and 
      Dependencies Matrix."
    
    inputs:
      - gap_sources:
          - "Business Architecture gap analysis (Phase B)"
          - "Data Architecture gap analysis (Phase C)"
          - "Application Architecture gap analysis (Phase C)"
          - "Technology Architecture gap analysis (Phase D)"
    
    process_steps:
      - step: 1
        action: "Collect gap analysis results from each domain architecture"
        detail: "From Phase B-D work, extract gaps documented in each domain's gap analysis matrix"
        output: "Raw list of baseline vs. target discrepancies per domain"
      
      - step: 2
        action: "Normalize and categorize gaps"
        detail: |
          "Organize gaps into categories:
          - CAPABILITY GAPS: Business capabilities missing or immature in baseline
          - PROCESS GAPS: Business processes requiring re-engineering
          - DATA GAPS: Data structures, quality, governance changes
          - APPLICATION GAPS: Applications to retire/replace/upgrade
          - TECHNOLOGY GAPS: Infrastructure, platform, or tooling changes
          - INTEGRATION GAPS: New interfaces or integration patterns required
          - GOVERNANCE GAPS: Organizational structure, roles, policies changes"
        output: "Categorized gap inventory"
      
      - step: 3
        action: "Document solutions for each gap"
        detail: |
          "For each gap, identify potential solution(s):
          - Technical solution (e.g., new application platform, infrastructure upgrade)
          - Process solution (e.g., re-engineering, automation)
          - Organizational solution (e.g., new role, governance model)
          - Hybrid/phased solution (combinations of above)
          Note: Multiple solutions per gap are normal; Phase E identifies candidates"
        output: "Gap-to-solution mapping"
      
      - step: 4
        action: "Identify dependencies"
        detail: |
          "For each gap/solution pair, identify:
          - TECHNICAL DEPENDENCIES: What other gaps must be resolved first?
          - ORGANIZATIONAL DEPENDENCIES: What organizational changes must precede?
          - REGULATORY DEPENDENCIES: What compliance requirements apply?
          - VENDOR/MARKET DEPENDENCIES: What market availability or vendor roadmap issues exist?
          - SKILLS DEPENDENCIES: What skills must be acquired or trained?"
        output: "Dependency matrix showing gap interdependencies"
      
      - step: 5
        action: "Create Consolidated Gaps, Solutions, and Dependencies Matrix"
        detail: |
          "Matrix structure:
          
          | Gap ID | Domain | Gap Description | Current State | Target State | 
          | Solution(s) | Dependencies | Priority (initial) | Affected Stakeholders |
          
          Example row:
          | GAP-001 | Business | Customer data governance maturity | Ad-hoc ownership | 
          | Centralized governance office | Requires data governance platform (APP-005), 
          | org restructuring | Medium | Data stewards, IT, Privacy officer |
          
          This matrix becomes the primary input for all Phase E/F decisions."
        output: "Consolidated Gaps, Solutions, and Dependencies Matrix"
      
      - step: 6
        action: "Review and validate with stakeholders"
        detail: "Present consolidated matrix to Architecture Review Board and domain architects; address questions and conflicts"
        output: "Approved Consolidated Matrix"
    
    quality_checks:
      - "Every gap is traceable to a specific baseline vs. target discrepancy"
      - "Every gap has at least one proposed solution"
      - "All identified dependencies are explicitly documented"
      - "Matrix is complete for all domain architectures (B, C, D)"
      - "No capability gaps are missing from Phase B business capability map"
    
    outputs:
      - "Consolidated Gaps, Solutions, and Dependencies Matrix"
      - "Gap inventory by domain (for impact analysis)"
      - "Dependency network diagram (optional visualization)"
  
  # ACTIVITY 2: IDENTIFY CAPABILITY GAPS AND INCREMENTS
  activity_2_capability_increments:
    
    title: "Identify Capability Gaps and Define Capability Increments"
    
    purpose: |
      "Using Capability-Based Planning (the recommended TOGAF technique), assess which 
      business capabilities must advance from their current maturity to target maturity, 
      and decompose capability gaps into measurable capability increments that will form 
      the basis for Transition Architectures."
    
    theory:
      capability_based_planning_foundation: |
        "Capability-Based Planning links business capabilities directly to roadmap sequencing:
        1. Identify target capabilities and their desired maturity level (1-5 scale)
        2. Assess current capability maturity for each capability
        3. Calculate gap = target maturity - current maturity
        4. Define capability increments (discrete maturity advancements)
        5. Sequence capability increments by dependency, value, risk, resource
        6. Each increment becomes a Transition Architecture with specific deliverables
        
        Key principle: Every capability increment is a Transition Architecture that 
        provides measurable business value and can be executed as a discrete change unit."
    
    inputs:
      - "Business Architecture from Phase B (business capability map)"
      - "Current-state and target-state capability maturity assessments"
      - "Business drivers and strategic objectives from Phase A"
      - "Consolidated Gaps, Solutions, and Dependencies Matrix"
    
    process_steps:
      - step: 1
        action: "Re-assess target business capabilities and maturity targets"
        detail: |
          "Review Phase B Target Architecture capability map and for each critical capability:
          - Confirm target capability definition (what the capability should do)
          - Define target maturity level (1-5 scale):
            * Level 1 (Immature): Manual, ad-hoc, undocumented
            * Level 2 (Repeatable): Documented, some standards
            * Level 3 (Defined): Standardized, documented, monitored
            * Level 4 (Optimized): Automated, continuously improving
            * Level 5 (Mature): Industry best practice, strategic differentiator
          - Document business justification for target maturity (not all capabilities need Level 5)"
        output: "Target capability map with maturity targets (1-5) for each"
      
      - step: 2
        action: "Assess current-state capability maturity"
        detail: |
          "For each critical capability, conduct current maturity assessment:
          - Review existing processes, tools, people, governance
          - Assess using same 1-5 scale:
            * Immature (1): Reactive, undocumented, inconsistent
            * Repeatable (2): Documented procedures, some training
            * Defined (3): Standard processes, governance, monitoring
            * Optimized (4): Automated workflows, continuous improvement
            * Mature (5): Industry best practice
          - Method: Expert interviews, process observation, metrics analysis, surveys
          - Document evidence (e.g., 'Evidence: Process documented in wiki; training quarterly')"
        output: "Current-state capability maturity map (1-5) with supporting evidence"
      
      - step: 3
        action: "Calculate capability gaps"
        detail: |
          "For each capability:
          Gap = Target Maturity - Current Maturity
          
          Example:
          - Customer Data Governance capability: Target 4, Current 1 → Gap = 3
          - This capability must advance 3 maturity levels
          
          Gaps of 0 (target already achieved) are excluded from roadmap.
          Gaps typically range from 1-4 levels (larger gaps suggest capability not yet defined)."
        output: "Capability gap inventory (capability name, current maturity, target maturity, gap size)"
      
      - step: 4
        action: "Prioritize capabilities by gap size and strategic importance"
        detail: |
          "Prioritization scoring (preliminary; will be refined in Phase F):
          
          CRITERIA:
          - Strategic Importance (High/Medium/Low): Does this capability directly support business drivers?
          - Gap Size (1-4): How many maturity levels must be advanced? (larger = more complex)
          - Dependencies (High/Medium/Low): How many other capabilities depend on this one?
          
          SCORING EXAMPLE:
          Capability A: Strategic High (10 pts) + Gap 3 (6 pts) + Dependencies High (10 pts) = 26 total
          Capability B: Strategic Medium (5 pts) + Gap 2 (4 pts) + Dependencies Low (2 pts) = 11 total
          
          INITIAL SEQUENCING LOGIC (refined in Phase F):
          - Strategic Foundation Capabilities: Schedule early even if lower value (enable others)
          - Quick Wins: High value, low dependency, small gap → Schedule early for momentum
          - Complex Capabilities: Larger gaps, more dependencies → Schedule after foundations
          
          This is PRELIMINARY prioritization; Phase F will refine with cost/risk/value data."
        output: "Prioritized capability gap list with scoring rationale"
      
      - step: 5
        action: "Define capability increments for each gap"
        detail: |
          "For each capability gap > 0, decompose into capability increments.
          
          Definition: A capability increment is a discrete step forward in capability maturity 
          that provides measurable business value and can be delivered as a unit.
          
          DECOMPOSITION APPROACH:
          For Gap Size = 3 (e.g., Customer Data Governance from Level 1 → Level 4):
          
          Capability Increment 1 (Level 1 → Level 2):
            - Objective: Document current processes and establish governance office
            - Deliverables: Data governance policy, roles/responsibilities, steering committee
            - Timeline: 3-6 months
            - Resources: 0.5 FTE governance lead + 0.5 FTE data stewards
            - Business Value: Establishes foundation for data management
          
          Capability Increment 2 (Level 2 → Level 3):
            - Objective: Standardize data management processes and implement data quality monitoring
            - Deliverables: Standard data management procedures, data quality metrics, training
            - Timeline: 6-9 months (after Increment 1)
            - Resources: 1 FTE governance lead + 2 FTE data engineers
            - Business Value: Improves data quality and reduces errors by 30%
          
          Capability Increment 3 (Level 3 → Level 4):
            - Objective: Automate data governance and implement self-service analytics
            - Deliverables: Data governance automation platform, self-service reporting
            - Timeline: 9-12 months (after Increment 2)
            - Resources: 2 FTE architects + 2 FTE engineers + vendor support
            - Business Value: Reduces data access time from days to minutes; enables analytics
          
          Key principle: Each increment is a Transition Architecture with specific, measurable 
          objectives and deliverables. Not all increments need to be executed; they can be 
          deferred or cancelled based on Phase F prioritization."
        output: "Capability increments for each gap with objectives, deliverables, timeline estimates"
      
      - step: 6
        action: "Validate capability increments with business stakeholders"
        detail: |
          "Present capability increments to business sponsors and process owners:
          - Does each increment represent realistic business value?
          - Are sequencing dependencies correct?
          - Are timeline and resource estimates reasonable?
          - Are there alternative decompositions to consider?
          Refine based on feedback."
        output: "Validated capability increment library (becomes basis for Transition Architectures)"
    
    quality_checks:
      - "Every strategic capability with current maturity < target maturity is represented"
      - "Each capability increment has clear, measurable objectives"
      - "Capability increments are sequenced to reflect dependencies"
      - "Business value of each increment is articulated"
      - "Resource estimates (effort, duration) are provided"
      - "No orphan increments (all increments are on a path from current to target maturity)"
    
    outputs:
      - "Capability gap inventory (capability, current maturity, target maturity, gap size)"
      - "Prioritized capability list (preliminary scoring)"
      - "Capability increments library (each with objectives, deliverables, timeline, resources)"
      - "Capability increment dependency network (which increments must precede others)"
  
  # ACTIVITY 3: DEFINE TRANSITION ARCHITECTURES
  activity_3_transition_architectures:
    
    title: "Define Transition Architectures Aligned to Capability Increments"
    
    purpose: |
      "For each capability increment, define the corresponding Transition Architecture—
      the intermediate architectural state that enables the capability advancement. This 
      ensures that every roadmap entry corresponds to both a business capability milestone 
      and an architectural state."
    
    theory:
      transition_architecture_concept: |
        "Transition Architecture = Intermediate architecture that represents progress from 
        Baseline Architecture toward Target Architecture, enabling a specific capability 
        increment with continuous business value.
        
        Key characteristics:
        1. Each Transition Architecture is a snapshot of the architecture at a point in time
        2. Multiple Transition Architectures form a sequence from Baseline → Target
        3. Each Transition Architecture maps to one or more capability increments
        4. Each Transition Architecture is executable as a discrete change unit
        5. Progression through Transition Architectures is planned to avoid 'big bang' 
           deployment and allow continuous value realization"
    
    inputs:
      - "Capability increments library from Activity 2"
      - "Target Architecture (from Phase B-D)"
      - "Baseline Architecture (from Phase B-D)"
      - "Domain architectures (Business, Data, Application, Technology)"
    
    process_steps:
      - step: 1
        action: "Map capability increments to architectural changes"
        detail: |
          "For each capability increment, identify what architectural changes are required:
          
          CAPABILITY INCREMENT EXAMPLE:
          Capability: Data Governance (Level 1 → Level 2)
          
          REQUIRED ARCHITECTURAL CHANGES:
          - Business Architecture: Define Data Governance office in org structure
          - Data Architecture: Define data ownership map, stewardship model
          - Application Architecture: No significant application changes (process-driven)
          - Technology Architecture: Data governance platform (selection, not implementation)
          
          - Infrastructure: Governance platform sizing and deployment model
          - Integration: No significant integration changes
          - Security/Compliance: Policy documentation, RACI matrix
          
          For each change, document:
          - Which domain architecture is affected
          - What baseline elements are modified/added/removed
          - What target elements are established
          - What architectural decisions are materialized (from Phase D Decision Log)"
        output: "Capability increment → architectural changes mapping"
      
      - step: 2
        action: "Define Transition Architecture for each capability increment"
        detail: |
          "Create a Transition Architecture definition document for each capability increment.
          
          TEMPLATE:
          
          TRANSITION ARCHITECTURE ID: TA-001
          TRANSITION TITLE: Data Governance Foundation
          CAPABILITY INCREMENT: Data Governance Level 1 → Level 2
          SEQUENCE: First transition (from Baseline)
          
          ARCHITECTURAL CHANGES:
          
          Business Architecture Changes:
          - ADD: Data Governance Office role in IT organization
          - ADD: Chief Data Officer position (reports to CTO/CIO)
          - ADD: Data Stewardship model (by business domain)
          - ADD: Data Governance steering committee (monthly meetings)
          
          Data Architecture Changes:
          - ADD: Data ownership map (identifies steward for each data entity)
          - ADD: Master data governance policy (data quality, lineage, retention)
          - ADD: Data glossary (business definitions for critical data elements)
          - MODIFY: Data quality KPIs (establish baseline metrics)
          
          Application Architecture Changes:
          - No application changes (policy-driven in this increment)
          
          Technology Architecture Changes:
          - SELECT: Data governance platform (e.g., Collibra, Informatica, Alation)
          - NO IMPLEMENTATION in this transition (selection only; deployment in TA-003)
          
          WORK PACKAGES REQUIRED:
          - Governance Model Development (2 months, 1 FTE architect)
          - Data Ownership Mapping (1 month, 0.5 FTE data analyst)
          - Policy Documentation (1 month, 0.5 FTE governance lead)
          - Governance Platform Selection (1 month, 1 FTE architect + vendor evaluation)
          - Organizational Change (2 months, 0.5 FTE change manager, org communication)
          
          BUSINESS VALUE:
          - Establishes clear data ownership and accountability
          - Provides foundation for data quality initiatives
          - Reduces confusion about data definitions (30% reduction in data-related incidents)
          - Enables Phase 2 data quality improvements
          
          DEPENDENCIES:
          - No prior transitions required
          - Enables: Data Quality Improvement (TA-002), Master Data Management (TA-004)
          
          STAKEHOLDERS:
          - Sponsor: Chief Information Officer
          - Business Owners: Marketing, Finance, HR (data stewards)
          - Technical Leads: Data Architecture, Integration, Security
          
          RISK ASSESSMENT:
          - Risk: Executive turnover (Chief Data Officer not retained)
            Mitigation: Governance embedded in charter; succession planning
          - Risk: Business stakeholders resist stewardship model
            Mitigation: Clear business benefits communicated; training program
          
          SUCCESS CRITERIA:
          - Data Governance Office established with defined charter
          - 100% of critical data entities have identified stewards
          - Data governance policy approved by steering committee
          - Data governance platform vendor selected and contract executed"
        output: "Transition Architecture definition documents (one per capability increment)"
      
      - step: 3
        action: "Sequence Transition Architectures"
        detail: |
          "Establish sequence/ordering of Transition Architectures:
          
          SEQUENCING FACTORS:
          1. DEPENDENCY ORDER: Some TAs must precede others
             Example: Data Governance TA must precede Data Quality TA (because governance 
             establishes the framework for quality management)
          
          2. ENABLER PRIORITY: TAs that enable multiple downstream increments should be 
             scheduled early
             Example: Application Platform TA enables application modernization TA
          
          3. VALUE REALIZATION: Early value-generating TAs should be scheduled first 
             (for momentum and stakeholder confidence)
             Example: Cost savings from consolidated infrastructure early in roadmap
          
          4. RISK MITIGATION: High-risk TAs may be scheduled early to allow learning 
             and course correction
             Example: New technology TA scheduled early to prove concept before large investment
          
          5. RESOURCE AVAILABILITY: TAs are sequenced to match available resources 
             and avoid resource conflicts
             Example: If limited data architects, TAs requiring data architect are scheduled serially
          
          SEQUENCING ALGORITHM:
          - Start with TAs with zero dependencies (can execute immediately)
          - For each TA with dependencies, schedule only after all dependencies complete
          - Apply priority logic to order independent TAs (value, risk, resource)
          - Validate total timeline and resource utilization (avoid peaks/valleys if possible)"
        output: "Transition Architecture sequence/roadmap (TA-001, TA-002, TA-003, ... TA-N)"
      
      - step: 4
        action: "Verify architectural continuity"
        detail: |
          "For each pair of consecutive Transition Architectures, verify continuity:
          
          VERIFICATION CHECKLIST:
          - Outputs of TA-N are inputs to TA-(N+1)? (e.g., Data Governance Office exists before 
            Master Data Management implementation)
          - No conflicting architectural decisions? (e.g., TA-N doesn't undo TA-(N-1))
          - Stakeholder roles consistent? (e.g., Data Steward role defined in TA-001 still 
            relevant in TA-002)
          - Technology stack coherent? (e.g., If TA-N chooses platform X, TA-(N+1) doesn't 
            assume platform Y)
          - Organizational structure transitions logically? (e.g., No sudden elimination of 
            established roles)"
        output: "Verified Transition Architecture sequence with continuity confirmed"
    
    quality_checks:
      - "Every capability increment has a corresponding Transition Architecture"
      - "Every Transition Architecture maps to specific architectural domain changes"
      - "Transition Architecture sequence respects dependencies"
      - "No capability gaps are left without a TA"
      - "TA sequencing is optimized for value, risk, and resource constraints"
      - "TA definitions are specific enough to inform Phase F prioritization"
    
    outputs:
      - "Transition Architecture definitions (one per capability increment)"
      - "Transition Architecture sequence diagram"
      - "TA-to-capability-increment mapping matrix"
  
  # ACTIVITY 4: IDENTIFY WORK PACKAGES
  activity_4_work_packages:
    
    title: "Identify and Group Changes into Work Packages"
    
    purpose: |
      "Organize work required to implement each Transition Architecture into logical 
      work packages that can be managed and sequenced. Work packages are the building 
      blocks of the roadmap and will be prioritized in Phase F."
    
    theory:
      work_package_concept: |
        "Work Package = A logical grouping of related activities that deliver a specific 
        architectural or capability outcome. Characteristics:
        
        1. Discrete and manageable (can be planned, estimated, executed as a unit)
        2. Produces clear, measurable deliverables
        3. Has defined start/end points and dependencies
        4. Requires specific resources and skills
        5. Can be assigned to a single project or program increment
        6. Maps to one or more capabilities on the roadmap"
    
    inputs:
      - "Transition Architecture definitions"
      - "Consolidated Gaps, Solutions, and Dependencies Matrix"
      - "Business drivers and strategic constraints"
      - "Organizational structure and change capacity"
    
    process_steps:
      - step: 1
        action: "Decompose each Transition Architecture into work packages"
        detail: |
          "For each Transition Architecture, identify work packages required to deliver it.
          
          DECOMPOSITION APPROACH:
          For Transition Architecture (TA-001: Data Governance Foundation), identify:
          
          WORK PACKAGES:
          
          WP-001: Data Governance Model Development
          - Objectives: Design data governance organizational structure, roles, processes
          - Deliverables: 
            * Governance model documentation
            * RACI matrix (roles and responsibilities)
            * Governance charter
            * Steering committee terms of reference
          - Effort: 2 months
          - Skills required: Enterprise architect, governance specialist
          - Budget: Internal staff (no vendor cost)
          - Dependencies: None (can start immediately)
          
          WP-002: Data Ownership Mapping
          - Objectives: Identify steward for each critical data entity
          - Deliverables:
            * Data ownership registry (all business and IT data entities)
            * Steward contact matrix
            * Communication plan
          - Effort: 1 month
          - Skills required: Data analyst, business analyst
          - Dependencies: After WP-001 (roles defined)
          
          WP-003: Data Governance Policy Documentation
          - Objectives: Establish policies for data quality, lineage, retention, privacy
          - Deliverables:
            * Master data governance policy document
            * Data quality standards
            * Data retention policy
            * Privacy and compliance requirements
          - Effort: 2 months
          - Skills required: Policy writer, compliance specialist, governance lead
          - Dependencies: Parallel to WP-001, then depends on stewardship model
          
          WP-004: Data Glossary Development
          - Objectives: Create common business glossary for critical data elements
          - Deliverables:
            * Glossary document (200+ business terms)
            * Definitions and lineage for each term
            * Technical metadata links
          - Effort: 1 month
          - Skills required: Business analyst, data architect
          - Dependencies: Parallel to WP-002
          
          WP-005: Data Governance Platform Selection
          - Objectives: Evaluate and select data governance platform
          - Deliverables:
            * Platform evaluation matrix
            * Vendor RFP and responses
            * Platform selection decision
            * Contract executed
          - Effort: 1 month (selection phase; implementation in future TA)
          - Skills required: Enterprise architect, procurement specialist
          - Dependencies: After WP-001 (requirements defined)
          
          WP-006: Organizational Change and Communication
          - Objectives: Prepare organization for governance model, communicate changes
          - Deliverables:
            * Change management plan
            * Stakeholder communication materials
            * Training program (governance model, roles, processes)
            * Executive briefings
          - Effort: 2 months (ongoing throughout WP-001 through WP-005)
          - Skills required: Change manager, communications specialist
          - Dependencies: Parallel to all technical work packages
          
          KEY PRINCIPLE: Work packages are groupings of related activities that make 
          sense from project management, resource allocation, and organizational change 
          perspectives. They balance between 'too small' (1000s of tiny packages) and 
          'too large' (single monolithic package)."
        output: "Work package inventory for each Transition Architecture"
      
      - step: 2
        action: "Document work package details"
        detail: |
          "For each work package, create a detailed definition:
          
          WORK PACKAGE TEMPLATE:
          
          ID: WP-001
          NAME: Data Governance Model Development
          TRANSITION ARCHITECTURE: TA-001 (Data Governance Foundation)
          
          BUSINESS OBJECTIVE:
          Design and establish data governance organizational structure, roles, and 
          decision-making processes to provide foundation for improved data management.
          
          ARCHITECTURAL OUTCOMES:
          - Business Architecture: CDO role, data stewardship model defined
          - Data Architecture: Data governance policies established
          - Organizational: Governance office structure and staffing plan
          
          DELIVERABLES:
          1. Governance Model Document (roles, organizational structure, reporting lines)
          2. RACI Matrix (roles and responsibilities for data management decisions)
          3. Governance Charter (authority, scope, decision rights)
          4. Steering Committee Charter (membership, meeting cadence, decision authority)
          5. Governance Operating Model (processes, escalation paths, issue resolution)
          
          SUCCESS CRITERIA:
          - Governance model approved by executive steering committee
          - All stakeholder questions addressed
          - Executive sponsor confident in structure
          - Ready to announce organization changes
          
          EFFORT ESTIMATE:
          - Duration: 8 weeks (2 months)
          - Full-Time Equivalent: 1.0 FTE enterprise architect + 0.5 FTE governance specialist
          - Person-months: 3
          
          RESOURCE REQUIREMENTS:
          - Enterprise Architect (full-time, 8 weeks)
          - Governance Specialist (part-time, 4 weeks)
          - Executive sponsor time (4 hours per week steering meetings)
          - IT leadership time (2 hours per week for interviews/feedback)
          
          BUDGET ESTIMATE:
          - Internal staff: ~$60K (based on average cost per person-month)
          - Travel: $2K
          - Facilities: Included in existing overhead
          - Total: $62K
          
          DEPENDENCIES:
          - Predecessor: None (can start immediately)
          - Parallel: WP-003 (Policy), WP-006 (Change Management)
          - Successor: WP-002 (Ownership Mapping), WP-004 (Glossary)
          
          RISKS:
          - Risk: Executive turnover disrupts governance model
            Probability: Low | Impact: High
            Mitigation: Governance embedded in organization structure; succession plan
          
          - Risk: Governance model too complex (too many committees/approvals)
            Probability: Medium | Impact: Medium
            Mitigation: Simplification workshop; feedback from business users
          
          - Risk: Conflicting views on roles and authority
            Probability: Medium | Impact: Low
            Mitigation: Escalation to executive steering committee
          
          ASSUMPTIONS:
          - Executive sponsor available for weekly feedback
          - Access to IT leadership for interviews
          - No major organizational restructuring in parallel
          - No competing enterprise architecture work
          
          CONSTRAINTS:
          - Must complete before WP-002 (Ownership Mapping) can fully execute
          - Must not conflict with existing HR organizational initiatives
          - Budget limited to $62K
          
          STAKEHOLDERS:
          - Sponsor: Chief Information Officer
          - Business Owners: All department heads
          - Governance Leads: Data, IT, IT Security, Privacy officer
          - IT Leadership: Infrastructure, Applications, Data teams
          
          QUALITY ASSURANCE:
          - Review by Architecture Review Board
          - Validation by business stakeholder group
          - Legal/compliance review (authority, decision rights)
          - Executive sponsor sign-off"
        output: "Detailed work package definitions (templates completed for all WPs)"
      
      - step: 3
        action: "Identify work package dependencies and critical path"
        detail: |
          "For the set of work packages (across all TAs), identify:
          
          DEPENDENCY TYPES:
          1. FINISH-TO-START: WP-A must finish before WP-B can start
             Example: WP-001 (Governance Model) must finish before WP-002 (Ownership Mapping)
          
          2. START-TO-START: WP-A must start before WP-B can start
             Example: WP-001 and WP-006 both start at same time (governance definition + change comms)
          
          3. FINISH-TO-FINISH: WP-A must finish before WP-B can finish
             Example: WP-006 (Change Management) must finish same time as WP-005 (Platform Selection)
          
          4. PARALLEL (independent): WP-A and WP-B can execute simultaneously
             Example: WP-003 (Policy) and WP-004 (Glossary) are independent
          
          DEPENDENCY ANALYSIS TASKS:
          - Create dependency matrix (rows = work packages, columns = predecessors)
          - Identify critical path (longest sequence of dependent WPs)
          - Calculate project duration (critical path length)
          - Identify float/slack (non-critical WPs that can be delayed without affecting total timeline)
          - Identify resource conflicts (two WPs requiring same resource at same time)
          
          EXAMPLE DEPENDENCY LOGIC:
          TA-001 Timeline Analysis:
          - Start: Week 1
          - WP-001 (8 weeks) → Critical path starts
          - WP-001 completes → WP-002 (4 weeks) can start
          - WP-002 completes → TA-001 ready for pilot (Week 12)
          - WP-006 (8 weeks, parallel) → Organizational readiness ready at Week 8
          - Critical Path: WP-001 → WP-002 (12 weeks total)
          - TA-001 duration: ~12 weeks from start to completion"
        output: "Work package dependency matrix and critical path analysis"
      
      - step: 4
        action: "Validate work package sizing and grouping"
        detail: |
          "Review work packages for consistency and appropriateness:
          
          VALIDATION QUESTIONS:
          - Is each WP bounded and discrete? (Not a vague 'implementation' WP)
          - Are WP timelines realistic? (1-4 months typical for Phase E estimate)
          - Are WP effort estimates reasonable? (0.5-2 FTE typical)
          - Are dependencies correctly identified? (No circular dependencies?)
          - Are WPs sized consistently? (Some WPs 2 weeks vs. others 6 months → group/split)
          - Do WPs map clearly to capabilities? (Every WP contributes to a capability increment)
          - Are organizational/change WPs included? (Not just technical WPs)
          
          COMMON ISSUES TO AVOID:
          - TOO SMALL: 'Update documentation file' is not a work package (combine with other docs)
          - TOO LARGE: 'Enterprise data platform implementation' (12+ months) should be split
          - VAGUE: 'Optimization work' is not a work package (specify what is being optimized)
          - ISOLATED: WP maps to no business capability or TA (question its inclusion)
          - UNRESOURCED: WP requiring expertise not available in organization (plan hiring/training)"
        output: "Validated work package inventory"
    
    quality_checks:
      - "Every work package maps to a Transition Architecture"
      - "Every Transition Architecture is decomposed into at least 2-3 work packages"
      - "Work packages are bounded (not too small or too large)"
      - "All dependencies are explicitly documented"
      - "No circular dependencies"
      - "Work package effort and duration estimates are provided"
      - "Organizational and change management work packages are included"
      - "Critical path can be identified"
    
    outputs:
      - "Work package inventory (100-200+ WPs typical for enterprise transformation)"
      - "Detailed work package definitions (effort, budget, skills, dependencies)"
      - "Work package dependency matrix"
      - "Critical path analysis"
  
  # ACTIVITY 5: IDENTIFY IMPLEMENTATION FACTORS
  activity_5_implementation_factors:
    
    title: "Identify Implementation Factors and Constraints"
    
    purpose: |
      "Document factors that will enable or constrain implementation, including 
      organizational readiness, skills gaps, budget availability, regulatory requirements, 
      and market/vendor dependencies. These factors will be used in Phase F to refine 
      sequencing and identify risk mitigation strategies."
    
    inputs:
      - "Work package inventory"
      - "Consolidated Gaps, Solutions, and Dependencies Matrix"
      - "Business drivers and strategic constraints"
      - "Current organizational capabilities and maturity"
    
    process_steps:
      - step: 1
        action: "Document organizational change factors"
        detail: |
          "For each significant change, identify organizational factors:
          
          ORGANIZATIONAL CHANGE ASSESSMENT:
          
          FACTOR: Process Re-engineering Complexity
          - Element: Customer Data Governance process redesign
          - Current State: Manual, disconnected governance; no central coordination
          - Target State: Centralized governance office with defined processes
          - Complexity Level: MEDIUM
          - Rationale: Requires new roles, process changes, but no fundamental business model change
          - Implementation Factor: 2-3 months for organizational change absorption capacity
          - Mitigation: Phased rollout, training program, communication campaign
          
          FACTOR: Stakeholder Resistance Risk
          - Element: Data stewardship model requiring business unit participation
          - Resistance Sources: Business users perceive as 'more process,' additional work
          - Resistance Level: MEDIUM-HIGH
          - Rationale: Stewardship requires ongoing governance effort from business
          - Implementation Factor: May delay adoption; impacts benefit realization timeline
          - Mitigation: Clear business case showing data quality benefits; executive endorsement
          
          FACTOR: Organizational Restructuring
          - Element: Creation of Chief Data Officer role and data governance office
          - Change Magnitude: NEW role, NEW office, NEW reporting lines
          - Change Level: MEDIUM
          - Rationale: Significant but not enterprise-wide reorganization
          - Implementation Factor: Hiring/recruiting lead time; organizational approval cycles
          - Mitigation: Expedited recruiting; executive authorization pre-approved
          
          FACTOR: Governance Model Adoption
          - Element: New governance office steering committee; monthly reviews
          - Current State: Ad-hoc governance; no formal structure
          - Target State: Formal governance with regular cadence and escalation paths
          - Adoption Complexity: LOW-MEDIUM
          - Rationale: Steering committee is familiar governance pattern; main challenge is enforcement
          - Implementation Factor: Executive commitment to attend meetings; timely decisions
          - Mitigation: Executive calendar holds; escalation to CFO/CIO if delayed decisions"
        output: "Organizational change factors assessment"
      
      - step: 2
        action: "Document skills and resource availability"
        detail: |
          "Assess skills required vs. skills available:
          
          SKILLS GAP ASSESSMENT:
          
          REQUIRED SKILL: Enterprise Architecture (Data Governance specialty)
          - Required Level: EXPERT (10+ years enterprise architecture experience)
          - FTE Required: 1.0 FTE for 8 weeks
          - Current Availability: 1.5 FTE enterprise architects in IT
          - Skill Gap: NONE (have available expertise)
          - Action: Allocate 1.0 FTE from available pool
          - Timeline Impact: NONE
          
          REQUIRED SKILL: Data Governance Specialty
          - Required Level: INTERMEDIATE (5+ years data governance experience)
          - FTE Required: 0.5 FTE for 12 weeks
          - Current Availability: 0 (no data governance specialists in organization)
          - Skill Gap: CRITICAL
          - Action: Hire external consultant or conduct training program
          - Timeline Impact: 4-6 weeks recruiting/onboarding delay if external hire
          - Mitigation: Hire consultant immediately (6-week project delay acceptable vs. training)
          
          REQUIRED SKILL: Change Management
          - Required Level: INTERMEDIATE (change management certification preferred)
          - FTE Required: 0.5 FTE for 8 weeks
          - Current Availability: 1 FTE change manager available
          - Skill Gap: NONE (have available expertise)
          - Action: Allocate 0.5 FTE from available pool
          - Timeline Impact: NONE
          
          REQUIRED SKILL: Policy Writing/Legal Compliance
          - Required Level: INTERMEDIATE (compliance and policy experience)
          - FTE Required: 0.5 FTE for 8 weeks
          - Current Availability: 0 (Compliance/Legal department, not available full-time)
          - Skill Gap: MEDIUM
          - Action: Allocate 0.25 FTE from Compliance department; consider external consultant for complex policy
          - Timeline Impact: 2-3 weeks delay (compliance reviews are bottleneck)
          - Mitigation: Engage compliance team early; parallel path with external policy consultant
          
          RESOURCE CONFLICT ANALYSIS:
          - Enterprise architects are also supporting Current Project X (platform migration)
          - Current Project X: 0.5 FTE architect required through Q4
          - Available EA capacity for Data Governance: 1.0 FTE (no conflict)
          - Action: Confirm EA prioritization with IT leadership; get written commitment"
        output: "Skills gap assessment and resource availability analysis"
      
      - step: 3
        action: "Document budget and financial constraints"
        detail: |
          "Assess financial factors affecting roadmap:
          
          BUDGET ANALYSIS:
          
          FACTOR: Overall Transformation Budget Availability
          - Current Budget Allocation: $10M over 3 years (from CFO approved strategic plan)
          - Current Commitments: $6M (existing approved projects)
          - Available for New Initiatives: $4M
          - Data Governance TA-001 Estimated Cost: $0.5M (consulting + implementation)
          - Data Governance TA-002 Estimated Cost: $1.5M (platform + implementation)
          - Data Governance TA-003 Estimated Cost: $2.0M (advanced analytics platform)
          - Total Data Governance Roadmap: $4.0M
          - Risk: Data Governance roadmap consumes entire available budget
          - Mitigation: Prioritize TA-001 and TA-002; defer TA-003 if budget pressure
          
          FACTOR: Vendor License Costs
          - Data Governance Platform annual license: $150K (years 1-3, then $200K/year)
          - Infrastructure platform cloud costs: $50K/month (operational, ongoing)
          - Risk: Ongoing operational costs not budgeted
          - Mitigation: Move cloud costs to operational budget (separate from transformation budget)
          
          FACTOR: Capital vs. Operational Budget Split
          - Transformation projects typically funded from capital budget (one-time)
          - Ongoing platform operations funded from operational budget (recurring)
          - Risk: Transformation completes but ongoing costs not budgeted
          - Mitigation: Define transition point when platform moves from capital to operational budget
          
          FACTOR: Funding Release Schedule
          - Corporate budget cycle: Annual (June approval, July funding release)
          - TA-001 start: January (6-month delay if waiting for annual budget cycle)
          - Option 1: Request early funding release from CFO (emergency/strategic priority)
          - Option 2: Defer start to July (aligned with budget cycle)
          - Recommendation: Request early release if business driver is urgent"
        output: "Budget and financial constraints assessment"
      
      - step: 4
        action: "Document regulatory, compliance, and market dependencies"
        detail: |
          "Assess external factors affecting implementation:
          
          REGULATORY/COMPLIANCE FACTORS:
          
          FACTOR: Data Privacy Regulation (GDPR, CCPA)
          - Requirement: Data governance and data privacy controls required by regulation
          - Current Status: Compliance gap identified
          - Implementation Deadline: 2026 Q2 audit (8 months away)
          - Roadmap Impact: Data Governance TA-001 must complete by Q2 2026
          - Risk: Regulatory penalty ($1M+) if not compliant
          - Mitigation: Schedule TA-001 to complete Q1 2026 (safety margin)
          
          FACTOR: Industry Standard (ISO 27001 Information Security)
          - Requirement: Information security governance required for certification
          - Current Status: Pursuing certification (competitive requirement)
          - Implementation Target: 2026 Q4 certification
          - Roadmap Impact: Information governance TA-001 must support ISO 27001 requirements
          - Risk: Failure to certify loses competitive advantage
          - Mitigation: Align governance model with ISO 27001 requirements
          
          MARKET/VENDOR DEPENDENCY FACTORS:
          
          FACTOR: Data Governance Platform Vendor Maturity
          - Current Platform Landscape: 3-4 mature vendors (Collibra, Informatica, Alation)
          - Evaluation Timeline: 2-3 months typical
          - Risk: Selected vendor discontinues product or acquired
          - Mitigation: Choose vendor with strong market position; contract portability clause
          
          FACTOR: Cloud Infrastructure Provider Commitment
          - Deployment Model: Cloud-based data governance platform
          - Risk: Cloud provider outage; provider pricing increases; provider sunset service
          - Mitigation: Multi-cloud strategy; contract price guarantees; redundancy planning
          
          FACTOR: Enterprise Data Platform Ecosystem
          - Dependency: Data governance platform must integrate with current data warehouse, BI tools
          - Current Tools: Snowflake data warehouse, Tableau BI
          - Ecosystem Maturity: Strong (both vendors support all major governance platforms)
          - Risk: LOW
          - Mitigation: Verify integration testing as part of platform selection"
        output: "Regulatory, compliance, and market dependency assessment"
      
      - step: 5
        action: "Create Implementation Factor Assessment and Deduction Matrix"
        detail: |
          "Consolidate all implementation factors into a matrix:
          
          TEMPLATE:
          
          | Factor ID | Factor Category | Factor Description | Current State | 
          | Target State | Maturity Level | Implementation Impact | Mitigation Strategy | 
          | Owner | Timeline |
          
          EXAMPLE ROWS:
          
          | IF-001 | Organizational | Data Governance office exists? | NO | YES | 
          | Low (need to create) | Medium (2-3 mo delay) | Expedited recruiting; executive approval | 
          | CIO | Q1 2026 |
          
          | IF-002 | Skills | Data governance expertise available? | NO | YES (hire consultant) | 
          | Low (no internal expertise) | Low (4-6 wk delay) | External consultant contract executed | 
          | HR/CIO | Q4 2025 |
          
          | IF-003 | Budget | $4M available for data governance roadmap? | $4M available | $4M needed | 
          | Medium (tight but sufficient) | Low (no delay if approved) | Funding approval memo signed | 
          | CFO/CIO | Q3 2025 |
          
          | IF-004 | Regulatory | GDPR compliance by Q2 2026? | Non-compliant | Compliant | 
          | Low (audit gap) | High (regulatory deadline) | TA-001 scheduled Q1 2026 | 
          | Chief Legal Officer | Q1 2026 |
          
          | IF-005 | Stakeholder | Business stewardship model resistance? | High | Medium (post-comms) | 
          | Medium (resistance expected) | Medium (3-4 mo adoption) | Communication campaign; exec sponsorship | 
          | Change Manager | Q4 2025-Q2 2026 |
          
          MATRIX SUMMARY:
          - Total Factors Identified: 12
          - Low Impact Factors: 5 (no material timeline change)
          - Medium Impact Factors: 5 (2-4 week timeline impact each)
          - High Impact Factors: 2 (regulatory deadline, skills gap)
          - Total Timeline Risk: -4 to -8 weeks (medium risk)
          - Mitigation Actions: 12 specific actions identified with owners and deadlines
          - Overall Recommendation: Roadmap feasible with timely mitigation actions"
        output: "Implementation Factor Assessment and Deduction Matrix"
    
    quality_checks:
      - "All work packages have implementation factors identified"
      - "Organizational change factors are explicitly addressed"
      - "Skills gaps are quantified (FTE, level, mitigation)"
      - "Budget constraints are documented with contingency options"
      - "Regulatory and compliance requirements are identified with deadlines"
      - "Market and vendor dependencies are assessed for risk"
      - "Mitigation strategies are specific and assigned to owners"
    
    outputs:
      - "Implementation Factor Assessment and Deduction Matrix"
      - "Organizational change factors assessment"
      - "Skills gap analysis with hiring/training plans"
      - "Budget constraints and financial risk assessment"
      - "Regulatory/compliance/market dependency assessment"

---

phase_e_outputs:
  
  title: "Phase E Outputs – Version 0.1 Architecture Roadmap and Implementation & Migration Plan"
  
  output_1_architecture_roadmap_v01:
    artifact_name: "Architecture Roadmap (Version 0.1)"
    description: |
      "A prioritized list of Transition Architectures and work packages, organized 
      by capability increment, showing progression from Baseline to Target Architecture. 
      This is an INITIAL roadmap; Phase F will refine and sequence."
    
    structure: |
      "
      ARCHITECTURE ROADMAP - VERSION 0.1
      
      Executive Summary:
      [1-page summary of roadmap scope, key transitions, timeline estimate, resource estimate, 
      key risks and mitigation]
      
      Roadmap by Transition Architecture:
      
      TRANSITION ARCHITECTURE 1: Data Governance Foundation (Capability: Data Governance L1→L2)
      - Estimated Start: Q4 2025
      - Estimated Duration: 12 weeks
      - Work Packages: WP-001 through WP-006 (6 packages)
      - Estimated Effort: 8 person-months
      - Estimated Budget: $500K
      - Key Resources: Enterprise architect, governance specialist, change manager
      - Dependencies: None (can start immediately)
      - Business Value: Establishes governance foundation; reduces data incidents 30%; enables downstream work
      - Key Risks: (5 risks identified) → Mitigation: (5 mitigations planned)
      - Success Criteria: Governance office operational, stewards appointed, policies approved
      - Stakeholders: CIO, Business unit heads, Data office leadership
      
      TRANSITION ARCHITECTURE 2: Data Quality Improvement (Capability: Data Quality L1→L3)
      - Estimated Start: Q1 2026 (after TA-001)
      - Estimated Duration: 20 weeks
      - Work Packages: WP-007 through WP-012 (6 packages)
      - Estimated Effort: 12 person-months
      - Estimated Budget: $750K
      - Key Resources: Data engineers, data stewards, BI developers
      - Dependencies: TA-001 (governance foundation must precede)
      - Business Value: Improves data quality metrics; reduces ETL failures; improves analytics reliability
      - Key Risks: (4 risks identified)
      - Success Criteria: Data quality KPIs show 50% improvement; 95% data accuracy
      - Stakeholders: Data office, BI/Analytics team, business users
      
      ... [Remaining TAs follow similar structure]
      
      TRANSITION ARCHITECTURE N: [Final TA in sequence]
      
      Roadmap Timeline (Gantt-style):
      
      2025 Q4 | 2026 Q1 | 2026 Q2 | 2026 Q3 | 2026 Q4 |
      TA-001  |   TA-002    |   TA-003        |   TA-004...
      
      Cumulative Budget by Quarter:
      
      2025 Q4: $0.5M
      2026 Q1: $0.5M + $0.75M = $1.25M (cumulative)
      2026 Q2: $1.25M + $1.0M = $2.25M (cumulative)
      ... Total: $4.0M over 3 years
      
      Work Package Dependency Network:
      [Diagram or matrix showing which work packages depend on others]
      
      Capability Maturity Progression:
      
      CAPABILITY: Customer Data Governance
      Current: L1 (Immature)
      After TA-001: L2 (Repeatable)
      After TA-002: L3 (Defined)
      Target: L4 (Optimized) [deferred to future roadmap cycle]
      
      ... [Similar progression for other capabilities]
      
      Implementation Factors and Risks:
      [Summary of major implementation factors and risk mitigation strategies from Activity 5]
      "
    
    approval_required: "YES – Architecture Review Board must approve Version 0.1 roadmap before Phase F"
  
  output_2_implementation_migration_plan_v01:
    artifact_name: "Implementation and Migration Plan (Version 0.1)"
    description: |
      "Detailed plan for executing the Architecture Roadmap, including activities, 
      timelines, resources, and organizational change approach. Phase E produces 
      initial plan; Phase F refines and integrates with enterprise change activity."
    
    structure: |
      "
      IMPLEMENTATION AND MIGRATION PLAN - VERSION 0.1
      
      Executive Summary:
      [1-page summary of migration approach, key phases, resource plan, budget, risks]
      
      Part 1: Migration Strategy and Approach
      
      Overall Migration Approach: EVOLUTIONARY
      Rationale: No 'big bang' replacement; incremental capability advancement allows 
      continuous value realization and risk mitigation.
      
      Strategic Implementation Parameters:
      - Timeframe: 3 years (2025 Q4 - 2028 Q3)
      - Scope: Data governance, data quality, master data management, advanced analytics
      - Strategic Initiative: Become 'data-driven' organization with centralized governance
      - Key Success Factor: Executive commitment and organizational change management
      
      Phase 1: Foundation (Q4 2025 - Q1 2026)
        Focus: Establish governance office and foundational processes
        Key Milestones: Governance office operational, stewards appointed, policies approved
      
      Phase 2: Core Implementation (Q1 2026 - Q3 2026)
        Focus: Deploy data governance platform, implement data quality processes
        Key Milestones: Platform go-live, data quality KPIs established
      
      Phase 3: Advanced Analytics (Q3 2026 - Q1 2027)
        Focus: Master data management, advanced analytics capabilities
        Key Milestones: MDM deployed, analytics self-service available
      
      Phase 4: Optimization (Q1 2027 - Q3 2027)
        Focus: Continuous improvement, process refinement, technology optimization
        Key Milestones: Operational excellence achieved, innovation enabled
      
      Part 2: Detailed Activity Plan
      
      For each Transition Architecture and Work Package:
      - Activities (sub-tasks that make up the work package)
      - Timeline and sequencing
      - Responsible parties and resource allocation
      - Deliverables and success criteria
      - Risk and mitigation for this specific WP
      
      WORK PACKAGE ACTIVITY EXAMPLE:
      
      WP-001: Data Governance Model Development
      
      Activity 1: Stakeholder Engagement and Requirements Gathering (Weeks 1-2)
        - Conduct interviews with IT leadership, business unit heads, governance stakeholders
        - Define data governance scope and objectives
        - Identify governance decision types (strategic, tactical, operational)
        Responsible: Enterprise Architect
        Duration: 2 weeks
        Resources: 1.0 FTE architect, 4 hours/week executive time
        Deliverable: Governance requirements document
      
      Activity 2: Governance Model Design (Weeks 2-4)
        - Design organizational structure (roles, committee structure)
        - Create RACI matrix (roles and responsibilities)
        - Define governance processes (decision-making, escalation)
        Responsible: Enterprise Architect
        Duration: 3 weeks
        Resources: 1.0 FTE architect, 2 hours/week stakeholder review
        Deliverable: Governance model design document
      
      Activity 3: Executive Review and Approval (Weeks 4-5)
        - Present to executive steering committee
        - Address questions and concerns
        - Obtain executive sign-off
        Responsible: CIO/Executive Sponsor
        Duration: 2 weeks
        Resources: Executive steering committee
        Deliverable: Approved governance model
      
      Activity 4: Charter and Policy Documentation (Weeks 5-8)
        - Write governance charter (authority, scope, decision rights)
        - Document steering committee terms of reference
        - Create governance operating manual (processes, guidelines)
        Responsible: Governance Specialist
        Duration: 4 weeks
        Resources: 0.5 FTE governance specialist, legal review
        Deliverable: Governance charter, committee charter, operating manual
      
      Activity 5: Organizational Change Communication (Weeks 1-8, ongoing)
        - Develop communication plan
        - Create executive briefings for leaders
        - Prepare FAQs and messaging for employees
        - Conduct townhalls/listening sessions
        Responsible: Change Manager
        Duration: 8 weeks (parallel to technical activities)
        Resources: 0.5 FTE change manager, communications support
        Deliverable: Communication materials, feedback from stakeholders
      
      Part 3: Resource Plan
      
      Staffing Model:
      - Program Manager: 1.0 FTE (overall roadmap execution)
      - Enterprise Architects: 2.0 FTE (technical architecture decisions)
      - Data Governance Specialists: 2.0 FTE (governance process design/implementation)
      - Change Managers: 1.0 FTE (organizational change, stakeholder engagement)
      - BI/Data Engineers: 4.0 FTE (Phase 2-4, data platform implementation)
      - Project Managers: 1.0 FTE (project execution oversight)
      - Quality Assurance: 0.5 FTE (quality and testing)
      
      Total Permanent Staffing: 11.5 FTE (core team for 3-year roadmap)
      Additional Consultants/Contractors: 3-5 FTE (specialized skills, temporary support)
      
      Skills/Training Needs:
      - 10 managers requiring change leadership training (2 days each)
      - 100 employees requiring data governance training (4 hours each)
      - 20 data stewards requiring ongoing training (quarterly, 2 hours each)
      - 50 data users requiring self-service analytics training (4 hours each)
      
      Budget Allocation:
      
      Year 1 (2025 Q4 - 2026 Q3): $1.5M
        - Staffing: $800K (8-10 FTE)
        - Vendor consulting: $400K (governance model, change management)
        - Software licenses: $200K (data governance platform)
        - Training and materials: $100K
      
      Year 2 (2026 Q4 - 2027 Q3): $1.8M
        - Staffing: $1.0M (10-12 FTE)
        - Software licenses and implementation: $600K (platform implementation, integration)
        - Infrastructure: $150K (cloud costs)
        - Training: $50K
      
      Year 3 (2027 Q4 - 2028 Q3): $0.7M
        - Staffing: $400K (4-5 FTE, core team)
        - Software licenses: $200K (platform operations)
        - Infrastructure: $100K (ongoing cloud costs)
        - Training and optimization: $50K
      
      Total 3-Year Budget: $4.0M
      
      Part 4: Organizational Change Management Plan
      
      Change Management Approach:
      - Executive sponsorship (CIO is primary sponsor, CFO is secondary)
      - Stakeholder engagement (monthly steering meetings, quarterly townhalls)
      - Communication (executive briefings, regular updates, FAQs)
      - Training (governance model training, platform training, process training)
      - Incentives (performance metrics tied to governance compliance, data quality)
      
      Resistance Management:
      - Identify potential resistors (resistance assessment workshops)
      - Address concerns through executive communication and business case
      - Engage resistors early in design process (co-creation of governance model)
      - Monitor adoption metrics and intervene if adoption lagging
      
      Part 5: Risk and Mitigation
      
      Major Risks and Mitigation Strategies:
      [Summary of key risks from Phase E work, with specific mitigation actions and owners]
      
      Part 6: Success Criteria and Benefits Realization
      
      Success Criteria by Transition Architecture:
      - TA-001: Governance office operational, 100% stewards appointed, policies approved
      - TA-002: Data quality KPIs improved 50%, platform go-live on schedule
      - TA-003: MDM deployed, 80% customer records matched, analytics adoption at 60%
      - TA-004: Regulatory compliance achieved, audit clean opinion
      
      Benefits Realization Tracking:
      - Data quality: Current 60% accurate → Target 95% accurate
      - Time to insight: Current 3 days → Target 1 day
      - Data incident costs: Current $500K/year → Target $100K/year
      - Decision speed: Current weeks → Target days
      
      Benefit Realization Plan:
      - Baseline measurements taken pre-TA-001
      - Quarterly measurement and tracking throughout roadmap
      - Formal benefit realization review at end of each TA
      - Continuous improvement based on benefits realized
      "
    
    approval_required: "YES – Phase F will refine and integrate with enterprise change activity"

---

## SECTION 3: PHASE F ACTIVITIES (Sequencing and finalization)

phase_f_activities:
  
  phase_title: "Phase F: Migration Planning"
  phase_purpose: |
    "Sequence and prioritize work packages identified in Phase E. Integrate the 
    Architecture Roadmap with the enterprise's other change activity. Produce the 
    final Architecture Roadmap and detailed Implementation & Migration Plan."
  
  phase_inputs:
    - "Architecture Roadmap Version 0.1 from Phase E"
    - "Work package inventory and estimates from Phase E"
    - "Implementation Factor Assessment and Deduction Matrix from Phase E"
    - "Enterprise project portfolio and resource availability"
    - "Current change initiatives and resource commitments"
  
  activity_1_sequence_by_value_risk_dependency:
    
    title: "Sequence Work Packages by Business Value, Risk, Dependency, and Cost"
    
    purpose: |
      "Apply prioritization logic to order work packages and Transition Architectures 
      in the final roadmap. Phase E identified work packages but did not definitively 
      sequence them; Phase F provides the final, executive-approved sequence."
    
    process_steps:
      - step: 1
        action: "Calculate business value for each work package"
        detail: |
          "For each work package, quantify business value:
          
          VALUE SCORING APPROACH:
          
          Work Package: WP-001 (Data Governance Model)
          
          STRATEGIC ALIGNMENT SCORE (0-10 points):
          - Supports business driver 'Become data-driven organization' (Full alignment = 10 points)
          Score: 10 points
          
          DIRECT FINANCIAL BENEFIT (0-10 points):
          - Reduces data incidents from $500K/year to $400K/year = $100K/year savings
          - Data incident prevention = $100K annual value
          - Normalize to 3-year value: $100K × 3 = $300K
          - Scale: $0-500K benefit = 0-5 points; $500K-1M = 5-7 points; $1M+ = 8-10 points
          - $300K benefit = 3 points
          Score: 3 points
          
          STRATEGIC CAPABILITY ENABLER (0-10 points):
          - Enables 5 downstream Transition Architectures (data quality, MDM, analytics, compliance)
          - High enabler (enables 4+ downstream work) = 10 points
          Score: 10 points
          
          STAKEHOLDER PRIORITY (0-10 points):
          - Governance is stated executive priority (Board directive, CEO emphasis)
          - High stakeholder priority = 8-10 points
          Score: 9 points
          
          TOTAL VALUE SCORE: 10 + 3 + 10 + 9 = 32 points (on 0-40 scale)
          
          INTERPRETATION: 32/40 = High value work package; priority for execution
          
          [Calculate scores for all work packages to create prioritized list]"
      
      - step: 2
        action: "Calculate risk for each work package"
        detail: |
          "Quantify implementation and execution risk:
          
          RISK SCORING APPROACH:
          
          Work Package: WP-001 (Data Governance Model)
          
          TECHNICAL RISK (0-10, where 10 = highest risk):
          - Is technology proven? Data governance model design is well-established (Low risk)
          - Are skills available? Need to hire external specialist (Medium risk)
          - Are vendors/partners reliable? N/A for this work package
          - Technical Risk Score: 2 (Low)
          
          ORGANIZATIONAL RISK (0-10):
          - Will stakeholders support? Executive-sponsored; high support (Low risk)
          - Will organizational change succeed? Major change to how governance operates (Medium risk)
          - Is executive commitment sustained? CIO is executive sponsor (Low risk)
          - Organizational Risk Score: 4 (Medium-Low)
          
          SCHEDULE RISK (0-10):
          - Is timeline realistic? 12 weeks for governance model is standard timeline (Low risk)
          - Resource dependencies resolved? Architect available, consulting can be procured (Medium risk)
          - Are external dependencies manageable? Few external dependencies (Low risk)
          - Schedule Risk Score: 2 (Low)
          
          FINANCIAL RISK (0-10):
          - Is budget adequate? $500K budget for TA-001 appears adequate (Low risk)
          - Are cost overruns likely? Consulting + staff, low complexity = Low risk
          - Budget contingency: 15% ($75K) included in estimate
          - Financial Risk Score: 2 (Low)
          
          TOTAL RISK SCORE: (2 + 4 + 2 + 2) / 4 = 2.5 (Low risk, on 0-10 scale)
          
          RISK INTERPRETATION: Low risk work package; good candidate for early execution
          
          RISK MITIGATION: Even for low-risk WP, document mitigations:
          - Technical Risk (2): Mitigate by hiring experienced consultant (known entity)
          - Organizational Risk (4): Mitigate by strong executive sponsorship + change mgmt plan
          - Schedule Risk (2): Mitigate by locking in architect resource commitment
          
          [Calculate risk scores for all work packages]"
      
      - step: 3
        action: "Map dependencies and identify critical path"
        detail: |
          "Create dependency sequencing logic:
          
          DEPENDENCY MAPPING:
          
          WP-001 (Data Governance Model) → WP-002 (Ownership Mapping)
            Dependency Type: Finish-to-Start (governance model must complete before mapping)
            Dependency Strength: HARD (cannot start WP-002 until WP-001 delivers governance roles)
          
          WP-001 → WP-004 (Glossary Development)
            Dependency Type: Start-to-Start (can begin glossary work once governance model starts)
            Dependency Strength: SOFT (glossary can begin with preliminary governance assumptions)
          
          WP-006 (Change Management) → all other WPs
            Dependency Type: Start-to-Start (change comms must begin when technical work starts)
            Dependency Strength: PARALLEL (change work runs parallel to technical work, not sequential)
          
          CRITICAL PATH CALCULATION:
          Critical Path = longest sequence of dependent work packages
          
          Path 1: WP-001 (8w) → WP-002 (4w) → TA-001 complete (12 weeks)
          Path 2: WP-001 (8w) → WP-003 (8w) → TA-001 complete (16 weeks)
          Path 3: WP-001 (8w) → WP-004 (4w) → TA-001 complete (12 weeks)
          
          Critical Path: WP-001 → WP-003 (16 weeks = 4 months)
          
          Float/Slack: WP-002 has 4-week slack (can be delayed without impacting TA-001 completion)
          
          SEQUENCING IMPLICATION: 
          - Focus management attention on WP-001 and WP-003 (critical path items)
          - WP-002 and WP-004 can be deferred if resources constrained (not on critical path)
          - Focus resource protection on WP-003 (policy documentation is bottleneck)
          
          [Repeat for all Transition Architectures to identify cross-TA critical path]"
      
      - step: 4
        action: "Calculate cost for each work package"
        detail: |
          "Quantify resource and budget requirements:
          
          COST ESTIMATION APPROACH:
          
          Work Package: WP-001 (Data Governance Model)
          
          STAFFING COSTS:
          - Enterprise Architect: 1.0 FTE × 8 weeks × $200/hour (avg cost/hr) = $64K
          - Governance Specialist: 0.5 FTE × 4 weeks × $175/hour = $14K
          - Change Manager: 0.5 FTE × 8 weeks × $150/hour = $12K
          
          Total Staffing: $90K
          
          VENDOR/CONSULTING COSTS:
          - External governance consultant (expert input): $50K
          
          Total Vendor: $50K
          
          EQUIPMENT/SOFTWARE COSTS:
          - Collaboration tools, documentation software: $5K
          - No major software licenses in WP-001
          
          Total Equipment: $5K
          
          OTHER COSTS (travel, training, contingency):
          - Travel for workshops: $2K
          - Contingency (15% of subtotal): $25K
          
          Total Other: $27K
          
          TOTAL WP-001 COST: $90K + $50K + $5K + $27K = $172K
          
          Compare to Phase E estimate: $500K for entire TA-001
          Breakdown:
          - WP-001: $172K (34% of TA budget)
          - WP-002: $120K (24% of TA budget)
          - WP-003: $130K (26% of TA budget)
          - WP-004: $50K (10% of TA budget)
          - WP-005: $18K (4% of TA budget)
          - WP-006: $10K (2% of TA budget) - mostly internal change management costs
          Total: $500K (Phase F can refine with detailed estimates)
          
          [Repeat for all work packages to build bottom-up budget]"
      
      - step: 5
        action: "Apply prioritization matrix to sequence work packages"
        detail: |
          "Combine value, risk, dependency, cost into prioritization matrix:
          
          PRIORITIZATION MATRIX (4-QUADRANT):
          
          Value (High/Low) vs. Risk (Low/High):
          
          QUADRANT 1: HIGH VALUE + LOW RISK ('QUICK WINS')
          - Priority: EXECUTE IMMEDIATELY
          - Examples: WP-001 (Governance Model = Value 32, Risk 2.5)
          - Rationale: Maximum ROI with manageable risk
          
          QUADRANT 2: HIGH VALUE + HIGH RISK ('STRATEGIC INITIATIVES')
          - Priority: EXECUTE AFTER FOUNDATIONS, WITH RISK MITIGATION
          - Examples: WP-007 (Data Quality Platform Implementation = Value 28, Risk 6)
          - Rationale: Strategic importance justifies risk, but mitigate first
          
          QUADRANT 3: LOW VALUE + LOW RISK ('OPTIONAL NICE-TO-HAVES')
          - Priority: DEFER OR ELIMINATE
          - Examples: WP-010 (Advanced Metadata = Value 12, Risk 2)
          - Rationale: Can be cut without major impact; low risk is not sufficient
          
          QUADRANT 4: LOW VALUE + HIGH RISK ('AVOID')
          - Priority: ELIMINATE
          - Examples: WP-015 (Experimental AI Governance = Value 8, Risk 8)
          - Rationale: Neither value nor risk justifies inclusion
          
          SEQUENCING LOGIC:
          1. START: Execute Quadrant 1 (High Value + Low Risk) immediately for momentum
          2. THEN: Execute Quadrant 2 (High Value + High Risk) after foundations (Q1 dependencies clear)
          3. DEFER: Quadrant 3 (Low Value + Low Risk) → execute if slack time/resources
          4. ELIMINATE: Quadrant 4 (Low Value + High Risk) → remove from roadmap
          
          APPLY DEPENDENCY CONSTRAINTS:
          - Even if WP-007 (High Value) needed immediately, if it depends on WP-001 (foundation),
            start WP-001 first
          - Identify 'enabler work packages' (WP-001, WP-005) that don't have high direct value
            but enable many downstream WPs (schedule early despite lower direct value)
          
          APPLY RESOURCE CONSTRAINTS:
          - Enterprise Architect is bottleneck (2.0 FTE max available, 12 WPs need architect input)
          - Sequence WP-001, WP-005, WP-008 (require architect) serially with 2-week padding
          - Parallel: WP-002, WP-003, WP-006 (don't require architect)
          
          FINAL SEQUENCING:
          
          2025 Q4:
          - WP-001 (Weeks 1-8): Data Governance Model (High Value, Low Risk, Critical Path)
          - WP-006 (Weeks 1-8, parallel): Change Management begins immediately
          - WP-004 (Weeks 1-4): Glossary Development begins (soft dependency with WP-001)
          
          2026 Q1:
          - WP-002 (Weeks 9-12): Ownership Mapping (Hard dependency on WP-001)
          - WP-003 (Weeks 1-8): Policy Documentation (parallel to Q4 work)
          - WP-005 (Weeks 1-4): Platform Selection (High Value Enabler)
          
          2026 Q2 onwards: TA-002, TA-003, ... based on similar logic
          
          ROADMAP RESULT: Sequenced, prioritized work packages with clear rationale"
    
    outputs:
      - "Prioritized work package list (ranked by Value/Risk/Dependency/Cost)"
      - "Sequenced work packages (quarter by quarter, showing order and dependencies)"
      - "Critical path analysis (which WPs impact timeline if delayed)"
      - "Resource conflict analysis (where bottlenecks exist)"
  
  activity_2_integrate_with_enterprise_activity:
    
    title: "Integrate Architecture Roadmap with Enterprise Portfolio and Change Activity"
    
    purpose: |
      "Ensure the Architecture Roadmap is coordinated with:
      - Current enterprise projects and initiatives
      - Resource availability and capacity constraints
      - Organizational change management capacity
      - Strategic priorities and budget allocation
      This prevents roadmap from being isolated from organizational reality."
    
    process_steps:
      - step: 1
        action: "Map Architecture Roadmap to current enterprise portfolio"
        detail: |
          "Assess overlap and conflicts with existing projects:
          
          CURRENT ENTERPRISE PROJECTS:
          
          Project 1: ERP Platform Migration
          - Status: In-progress (started Jan 2025, ends Dec 2026)
          - Resource Requirement: 5 FTE IT staff (ERP specialists)
          - Budget: $3.0M (already committed)
          - Risk Impact: ERP project consumes IT resources Q1-Q4 2026
          - Conflict with Architecture Roadmap: TA-002 (Data Quality) scheduled Q1 2026
          
          ASSESSMENT: Resource conflict in Q1 2026
          - Data Quality work (TA-002) needs 3-4 data engineers
          - ERP migration needs 5 IT staff
          - Total capacity needed: 8-9 resources
          - Available IT/data resources: 8 total
          - RECOMMENDATION: Sequence TA-002 to Q2 2026 (after ERP phase 1 completes)
          
          Project 2: Data Warehouse Refresh
          - Status: Planned for Q4 2025
          - Resource Requirement: 2-3 FTE data engineers
          - Budget: $400K
          - Conflict with Architecture Roadmap: Overlaps with TA-001 (Q4 2025)
          
          ASSESSMENT: Timing conflict but not catastrophic
          - Data Warehouse Refresh is technical infrastructure work (needed for data governance platform)
          - TA-001 is governance model + processes (can run parallel if resources available)
          - RECOMMENDATION: Coordinate start dates; ensure Data Warehouse work completes before 
            TA-002 platform implementation (Q2 2026)
          
          [Similar analysis for all current projects]
          
          PORTFOLIO INTEGRATION RESULT:
          - Architecture Roadmap sequencing adjusted to fit with current projects
          - No catastrophic conflicts; some sequencing adjustments needed
          - Resource conflicts identified and alternatives proposed"
      
      - step: 2
        action: "Validate resource availability and capacity"
        detail: |
          "Confirm that planned staffing matches available resources:
          
          RESOURCE AVAILABILITY ANALYSIS:
          
          RESOURCE TYPE: Enterprise Architects
          - Current headcount: 2.0 FTE
          - Current commitments: 0.5 FTE (ERP governance support)
          - Available capacity: 1.5 FTE
          - Architecture Roadmap requirement:
            * TA-001: 1.0 FTE (8 weeks)
            * TA-002: 1.0 FTE (12 weeks)
            * TA-003: 0.5 FTE (8 weeks)
          - Sequencing: TA-001 (Q4), then TA-002 (Q1-Q2), then TA-003 (Q2-Q3)
          - ASSESSMENT: Capacity available; no hiring needed
          
          RESOURCE TYPE: Data Governance Specialists
          - Current headcount: 0 FTE (no expertise in organization)
          - Current commitments: 0 FTE
          - Available capacity: 0
          - Architecture Roadmap requirement: 2.0 FTE starting Q4 2025
          - GAP: Need to hire or contract 2 specialists
          - OPTION 1: Hire 2 full-time governance specialists (4-6 week recruiting)
          - OPTION 2: Contract external consulting firm for Phases 1-2 (immediate availability)
          - OPTION 3: Hybrid (hire 1 FTE + contract 1 FTE = faster ramp)
          - RECOMMENDATION: Hybrid approach (hire 1 specialist, contract 1 consultant)
            * Hire 1 FTE permanent (recruitment starts Sept 2025)
            * Contract consultant for Q4 2025 - Q1 2026 (immediate availability)
            * Transition to permanent-only staffing in Q2 2026
          - Timeline Impact: Minimal (consultant available for Q4 start)
          
          [Repeat for all resource types: Data Engineers, BI Developers, Project Managers, etc.]
          
          RESOURCE CAPACITY PLAN:
          - Hiring needed: 2-3 positions (data governance, data engineer)
          - Consulting/contractors needed: 3-5 FTE for phases 1-3
          - Training needed: Internal staff upskilling on data governance, platforms
          - Recommendation: Begin recruiting immediately (Sept-Oct 2025 for Q4 start)"
      
      - step: 3
        action: "Assess organizational change capacity"
        detail: |
          "Determine if organization can absorb proposed changes:
          
          ORGANIZATIONAL CHANGE CAPACITY ASSESSMENT:
          
          FACTORS INDICATING CAPACITY:
          - Executive sponsorship: Strong (CIO + CFO sponsoring data initiative)
          - Prior transformation experience: ERP implementation in progress (positive precedent)
          - Employee readiness: Survey shows 60% ready for change (median)
          - Governance maturity: Organization has governance committees for various initiatives
          
          FACTORS INDICATING CONSTRAINTS:
          - Change fatigue: ERP implementation ongoing (staff already experiencing change)
          - Skills availability: Data governance expertise low (training required)
          - Organizational structure: Siloed departments (data governance requires cross-silo collaboration)
          - Budget constraints: Capital budget tight ($4M available for all new initiatives)
          
          CHANGE CAPACITY CALCULATION:
          Current change capacity score: 6/10 (Medium capacity)
          - Positive factors: +3 (executive sponsorship, prior experience)
          - Negative factors: -3 (change fatigue, silos)
          - Neutral baseline: 6
          
          IMPLICATION:
          - Organization can absorb 1 major transformation at a time (capacity = 1)
          - Current capacity consumed by: ERP implementation (100% of capacity)
          - Available capacity for Architecture Roadmap: 0 additional capacity
          - ISSUE: ERP implementation and Architecture Roadmap both need organizational change energy
          
          MITIGATION OPTIONS:
          Option 1: Defer Architecture Roadmap until ERP completes (Dec 2026)
            - Advantage: No change conflict; full focus on ERP
            - Disadvantage: Delays data governance roadmap; misses regulatory deadline
          
          Option 2: Sequence Architecture Roadmap phases to align with ERP phases
            - TA-001 (Foundation): Q4 2025 (before ERP heaviest phase, low change impact)
            - TA-002 (Implementation): Q2 2026 (ERP nearing completion, change capacity available)
            - TA-003+: 2027 (ERP complete, full change capacity available)
            - Advantage: Moderate change load in each phase
            - Disadvantage: TA-001 in isolation delivers limited value until platforms deployed
          
          Option 3: Accelerate ERP project to complete by Q2 2026
            - Advantage: Frees change capacity for TA-002 in Q3 2026
            - Disadvantage: May compromise ERP quality or outcomes
          
          RECOMMENDATION: Option 2 (sequence phases)
          - Keep TA-001 in Q4 2025 (foundation work, low organizational impact)
          - Defer TA-002 (platform implementation) to Q3 2026 (ERP complete by then)
          - Adjust timeline: Roadmap now extends 3.5 years instead of 3 years
          - Regulatory deadline check: GDPR compliance still achievable (Q1 2027 vs. Q2 2026 deadline)
          
          CHANGE CAPACITY PLAN:
          - Phase 1 (Q4 2025): Change capacity = 30% of TA-001 (foundation work)
          - Phase 2 (Q1-Q2 2026): Change capacity = 10% (ERP at peak; minimal new change)
          - Phase 3 (Q3 2026+): Change capacity = 50% (ERP complete; significant capacity available)"
      
      - step: 4
        action: "Create integrated roadmap incorporating portfolio constraints"
        detail: |
          "Produce final roadmap reflecting portfolio and organizational constraints:
          
          INTEGRATED ROADMAP:
          
          2025 Q4: Data Governance Foundation Phase
          - TA-001 Work Packages: WP-001 through WP-006
          - Parallel: ERP Phase 2 in progress (no conflict; governance is process-based)
          - Resource allocation: 2 FTE governance specialists (1 hire + 1 consultant), 1 FTE architect
          - Change capacity consumed: ~30% (moderate, compatible with ERP context)
          - Budget: $500K from approved Architecture Roadmap budget
          - Deliverables: Governance office operational, policies approved
          - Business value: Foundation for Phase 2
          
          2026 Q1-Q2: ERP Peak + Foundation Implementation Phase
          - TA-001 Completion: WP-006 concluding (change management wrap-up)
          - TA-002 Deferred: Platform implementation pushed to Q3 (resource conflict with ERP)
          - Interim work: Begin TA-002 planning, vendor evaluation, requirements finalization
          - Resource allocation: Governance specialists focus on change adoption; architects support ERP
          - Change capacity consumed: ~10% for Architecture work (ERP consuming 90%)
          - Budget: $100K (planning/evaluation only; implementation budget held for Q3)
          - Deliverables: TA-001 fully operational; TA-002 requirements finalized, vendor selected
          - Business value: Governance processes embedded; foundation stable for next phase
          
          2026 Q3-Q4: ERP Completion + Data Quality Platform Deployment
          - TA-002 Execution: Platform deployment, data quality implementation
          - ERP project closing (Dec 2026)
          - Resource allocation: Full governance + data engineer team on TA-002
          - Change capacity consumed: ~50% (ERP winding down; TA-002 ramping up)
          - Budget: $750K (platform + implementation)
          - Deliverables: Data quality platform go-live; data quality metrics established
          - Business value: 50% improvement in data quality metrics
          
          2027 Q1-Q2: Data Quality + Master Data Management
          - TA-003 Execution: Master data management, MDM implementation
          - TA-002 foundation stable (data quality processes operational)
          - Resource allocation: Full team on TA-003
          - Change capacity consumed: ~50% (ongoing transformation energy)
          - Budget: $1.0M (MDM platform + integration)
          - Deliverables: MDM platform go-live, customer master record consolidated
          - Business value: Single customer view; reduced data redundancy
          
          2027 Q3-Q4: MDM + Advanced Analytics
          - TA-004 Execution: Advanced analytics platform, self-service BI
          - TA-003 foundation operational (MDM processes stable)
          - Resource allocation: Team transitions from deployment to optimization
          - Change capacity consumed: ~30% (transformation maturing; moving to optimization)
          - Budget: $0.75M (analytics platform + training)
          - Deliverables: Self-service BI available; analytics user adoption at 60%
          - Business value: Time-to-insight reduced from 3 days to 1 day
          
          2028 Q1+: Continuous Optimization
          - TA-005+: Capability refinement, process optimization, innovation
          - All platforms operational; team focuses on optimization and new capabilities
          - Resource allocation: 4-5 FTE (core team only; temporary staff released)
          - Change capacity consumed: ~10% (transformation complete; normal operations)
          - Budget: $0.3M/year (ongoing licenses + minor enhancements)
          - Business value: Sustained benefits; continuous improvement cycle
          
          ADJUSTED TIMELINE:
          Original Plan: 3 years (2025 Q4 - 2028 Q3)
          Integrated Plan: 3.25 years (2025 Q4 - 2028 Q4)
          - Added 1 quarter due to ERP portfolio conflict
          - Still meets regulatory deadline (GDPR compliance by 2027 Q1)
          - Strategic priority sequence preserved (foundation → implementation → optimization)
          
          ADJUSTED BUDGET:
          Original: $4.0M (2025-2028)
          Integrated: $4.0M (same budget, just extended timeline)
          - Q4 2025: $500K
          - Q1-Q2 2026: $100K (minimal spending, focus on planning)
          - Q3-Q4 2026: $850K
          - 2027 Q1-Q4: $1.75M (TA-003 + TA-004)
          - 2028+: $0.8M (TA-005 optimization + ongoing ops)
          
          RESOURCE ADJUSTMENTS:
          - Add 1 quarter for ERP resource availability
          - Begin recruiting Q3 2025 (vs. Q2 originally planned)
          - Extend contractor engagement to Q2 2026 (vs. Q1 originally planned)
          - No increase to total FTE (timeline extension absorbs resource conflicts)"
    
    outputs:
      - "Portfolio integration assessment (conflicts identified and resolved)"
      - "Resource capacity analysis and hiring/contracting plan"
      - "Organizational change capacity assessment"
      - "Integrated roadmap reflecting portfolio and organizational constraints"
  
  activity_3_finalize_architecture_roadmap:
    
    title: "Finalize Architecture Roadmap (Version 2.0)"
    
    purpose: |
      "Produce the final, executive-approved Architecture Roadmap that reflects 
      Phase E and Phase F analysis, sequencing decisions, and integration with 
      enterprise portfolio."
    
    outputs_included:
      - "Architecture Roadmap Version 2.0 (final)"
      - "Implementation and Migration Plan (final, detailed)"
      - "Resource and budget allocation plan"
      - "Executive summary and business case for approval"
    
    outputs:
      - "Final Architecture Roadmap (Version 2.0)"
      - "Final Implementation and Migration Plan"
      - "Resource plan (hiring, recruiting, consulting)"
      - "Budget allocation by quarter and work package"
      - "Executive presentation for steering committee approval"

---

## SECTION 4: GOVERNANCE LAYER DECISION (MoP vs. MSP)

governance_layer_selection:
  
  title: "Governance Layer Selection – MoP or MSP"
  purpose: |
    "The Architecture Roadmap (from Phase E/F) becomes the input to portfolio 
    or programme governance. Select the appropriate framework based on programme structure."
  
  decision_tree:
    
    question: "Is the Architecture Roadmap a single coordinated programme or multiple independent initiatives?"
    
    path_1_single_programme_msp:
      condition: "Single coordinated programme delivering unified blueprint"
      governance_framework: "MSP (Managing Successful Programmes)"
      
      msp_activities:
        - "Define programme blueprint (maps to Target Architecture)"
        - "Organize work packages into Tranches (maps to Transition Architectures)"
        - "Establish Programme Board (governance authority)"
        - "Plan benefits realization (business value tracking)"
        - "Manage organizational change (stakeholder engagement, adoption)"
        - "Control constituent projects (quality, scope, schedule)"
      
      example_scenario: |
        "Architecture Roadmap identifies 4 Transition Architectures for enterprise-wide 
        data transformation (Data Governance → Data Quality → Master Data Management → 
        Advanced Analytics). These TAs are tightly interdependent and deliver a unified 
        'data-driven enterprise' blueprint. All work packages are related and must be 
        coordinated through a single Programme Board.
        
        MSP Application:
        - Programme Blueprint = Target Architecture (data-driven enterprise)
        - Tranche 1 = TA-001 (Data Governance Foundation)
        - Tranche 2 = TA-002 (Data Quality Implementation)
        - Tranche 3 = TA-003 (Master Data Management)
        - Tranche 4 = TA-004 (Advanced Analytics)
        - Constituent projects within each tranche deliver specific work packages"
      
      governance_structure: |
        "
        PROGRAMME GOVERNANCE HIERARCHY:
        
        Executive Steering Committee
              ↓
        Programme Board (Senior Responsible Owner, Programme Director)
              ↓
        Tranche Planning Team (for each Tranche)
              ↓
        Constituent Projects (PRINCE2 projects within each tranche)
        
        MSP Programme Board authority:
        - Approve benefits definition and realization plan
        - Allocate budget and resources across tranches
        - Make trade-off decisions (scope, schedule, cost, quality)
        - Manage inter-project dependencies and interfaces
        - Escalate risks and issues
        - Monitor benefits realization
        "
    
    path_2_multiple_initiatives_mop:
      condition: "Multiple independent or loosely coupled initiatives competing for resources"
      governance_framework: "MoP (Management of Portfolios)"
      
      mop_activities:
        - "Define portfolio strategy aligned to business strategy"
        - "Prioritize initiatives based on weighted scoring"
        - "Allocate budget and resources across portfolio"
        - "Establish Portfolio Board (governance authority)"
        - "Monitor portfolio balance (strategic alignment, risk, value)"
        - "Manage benefits across portfolio"
        - "Manage programme/project interdependencies"
      
      example_scenario: |
        "Architecture Roadmap identifies 3 independent capability streams:
        1. Data Governance Capability (TA-001 through TA-003)
        2. Customer Experience Modernization (separate architecture roadmap)
        3. Infrastructure Cost Optimization (separate architecture roadmap)
        
        These streams have minimal interdependencies but compete for shared resources 
        (architecture team, budget) and executive attention. Portfolio prioritization 
        determines which streams proceed first and how resources are allocated.
        
        MoP Application:
        - Portfolio Strategy = Enterprise digital transformation across all capabilities
        - Data Governance Stream = Programme 1 (MSP governance within programme)
        - Customer Experience Stream = Programme 2 (MSP governance within programme)
        - Infrastructure Stream = Programme 3 (MSP governance within programme)
        - Portfolio Board prioritizes across these 3 programmes"
      
      governance_structure: |
        "
        PORTFOLIO GOVERNANCE HIERARCHY:
        
        Executive Steering Committee
              ↓
        Portfolio Board (Portfolio Director, CFO)
              ↓
        Programme/Project Prioritization Forum
              ↓
        Individual Programmes (MSP) or Projects (PRINCE2)
        
        MoP Portfolio Board authority:
        - Align portfolio strategy to business strategy
        - Prioritize and balance initiatives
        - Allocate shared budget and resources
        - Make go/no-go funding decisions
        - Monitor portfolio balance and strategic alignment
        - Manage portfolio-level risks and interdependencies
        "

---

## SECTION 5: EXECUTION LAYER SELECTION (PRINCE2 or SAFe)

execution_layer_selection:
  
  title: "Execution Layer Selection – PRINCE2 or SAFe"
  purpose: |
    "Architecture Roadmap (and MSP/MoP governance) feeds into project execution. 
    Select execution framework based on delivery model."
  
  decision_tree:
    
    question: "What is the project delivery model (stage-gated or agile)?"
    
    path_1_stage_gated_prince2:
      condition: "Stage-gated, waterfall-style delivery"
      execution_framework: "PRINCE2"
      
      prince2_phases:
        - "Project Initiation: Create Project Initiation Document (PID) based on roadmap work package definition"
        - "Project Planning: Decompose work package into activities, timelines, resource allocation"
        - "Project Execution: Deliver against planned activities; manage changes through formal change control"
        - "Project Monitoring and Control: Track progress against baseline; manage risks and issues"
        - "Project Closure: Close project; measure and report realized benefits against roadmap expectations"
      
      example_scenario: |
        "Work Package WP-001 (Data Governance Model Development) from TA-001 becomes a PRINCE2 project:
        
        Project Initiation:
        - PID created from roadmap WP-001 definition
        - Project manager appointed
        - Stakeholders identified
        - Quality standards defined
        
        Project Planning:
        - 8 weeks decomposed into 12 activities
        - Each activity assigned to team member with effort estimate
        - Resource calendar created (1.0 FTE architect, 0.5 FTE specialist)
        - Budget allocated ($172K per Phase E estimate)
        - Gantt chart created
        
        Project Execution:
        - Team executes activities per plan
        - Weekly status meetings
        - Deliverables reviewed for quality
        - Changes evaluated for scope/schedule/cost impact
        
        Project Closure:
        - Project delivered on schedule, within budget
        - Governance model approved by steering committee
        - Benefits (foundation established) realized
        - Project formally closed; team released to next project"
    
    path_2_agile_safe:
      condition: "Agile/iterative delivery with rolling-wave planning"
      execution_framework: "SAFe (Scaled Agile Framework)"
      
      safe_approach:
        - "Map Architecture Roadmap Transition Architectures to SAFe Program Increments (PIs)"
        - "Each PI is an 8-12 week delivery cycle aligned to one or more TAs"
        - "PI Planning event aligns team to shared mission and plan"
        - "Agile Release Train (ART) executes sprints within PI"
        - "Continuous feedback from delivery informs roadmap adjustments"
      
      example_scenario: |
        "TA-001 (Data Governance Foundation) becomes 2 Program Increments under SAFe:
        
        SAFE ROADMAP:
        PI 1 (Oct 2025 - Nov 2025, 8 weeks):
          Epics: Governance Model Design, Change Management Planning
          Stories: 
            - Design governance organizational structure
            - Create RACI matrix
            - Plan stakeholder communication
            - Develop training curriculum
          Teams: Enterprise Architecture, Change Management, HR
          Business Value: Governance model defined, organization prepared
        
        PI 2 (Dec 2025 - Jan 2026, 8 weeks):
          Epics: Governance Execution, Policy Implementation
          Stories:
            - Governance office operational
            - Data stewards appointed
            - Policies approved
            - Training delivered
          Teams: Data Governance Office, IT Leadership
          Business Value: Governance model deployed and operational
        
        SAFe PI PLANNING (for PI 1):
        - Stakeholders (business, IT, governance teams) gather for 2-day PI Planning
        - Define PI objectives: 'Governance model designed and stakeholder-approved'
        - Break down epics into user stories and tasks
        - Identify dependencies between teams
        - Make team commitments (what can be delivered in 8 weeks)
        - Identify risks and mitigation
        
        SAFe EXECUTION (PI 1):
        - 4 sprints of 2 weeks each
        - Sprint 1: Governance model draft + initial RACI
        - Sprint 2: Governance model refined + stakeholder feedback incorporated
        - Sprint 3: RACI complete + change plan detailed
        - Sprint 4: Final governance model + change plan ready for executive review
        
        SAFe INSPECT & ADAPT (after PI 1):
        - System demo to stakeholders (governance model demo, process walkthroughs)
        - Retrospective (what worked, what didn't, improvements for PI 2)
        - Release plan updated based on learning from PI 1
        
        TA-001 VALUE DELIVERED: Incremental governance model advancement from sprint 1 → sprint 4,
        with continuous feedback and adaptation"
    
    path_3_hybrid_prince2_safe:
      condition: "Hybrid – initial foundation phase (stage-gated), then agile execution"
      execution_framework: "PRINCE2 for foundation phase + SAFe for continuous delivery"
      
      hybrid_approach: |
        "Phase 1 (Foundation, 3-6 months): PRINCE2 project
        - Governance model design, organizational change preparation
        - Stage-gated delivery with executive gates
        - Foundation must be solid before moving to Phase 2
        
        Phase 2-4 (Implementation/Evolution, ongoing): SAFe Release Trains
        - Platform implementation, process deployment, optimization
        - Rolling-wave PI Planning every 8-12 weeks
        - Continuous delivery and feedback
        
        Transition point: After foundation is solid (PRINCE2 closure), organization 
        transitions to SAFe ARTs for ongoing delivery"

---

## SECTION 6: OPTIONAL OVERLAYS

optional_overlays:
  
  overlay_1_wardley_mapping:
    
    title: "Optional Overlay: Wardley Mapping (Sourcing and Maturity Strategy)"
    
    when_to_apply: |
      "Use Wardley Mapping if:
      - Roadmap spans multiple years and sourcing strategy (build vs. buy vs. outsource) is important
      - Technology or capability maturity evolution should be visualized
      - Make vs. buy decisions need strategic justification
      - Cost optimization through appropriate sourcing is a goal"
    
    integration_example: |
      "CAPABILITY: Data Governance
      
      WARDLEY MAP OVERLAY:
      
      Y-axis (User Value): How critical is this capability to business?
      X-axis (Maturity/Evolution): Genesis → Custom-Built → Product → Commodity
      
      Current State (2025):
      - Data Governance maturity: Genesis/Custom-Built (early stage, immature)
      - Sourcing: Internal build + consulting (expensive, inconsistent)
      - User value: High (CEO priority)
      
      Evolution Path:
      
      TA-001 (2025): Genesis → Custom-Built
      - Build custom governance model (in-house, with consulting)
      - Cost: $500K + 2 FTE (high cost, custom solution)
      - Sourcing decision: MAKE (internal build, high strategic control)
      - Rationale: Competitive differentiator; organization must understand governance
      
      TA-002 (2026): Custom-Built → Product
      - Adopt data governance platform (commercial product selection)
      - Cost: $200K software + $300K implementation
      - Sourcing decision: BUY (data governance platform as commercial product)
      - Rationale: Platform commoditized; buying cheaper than building; platforms meet 80% of need
      
      TA-003 (2027): Product → Commodity
      - Integrate with cloud data governance as a service
      - Cost: $150K/year SaaS (lower than product on-premise)
      - Sourcing decision: OUTSOURCE (SaaS model; reduce operational burden)
      - Rationale: Governance moved to commodity status; cloud service is cost-effective
      
      STRATEGIC INSIGHT FROM WARDLEY MAP:
      - Maturity journey: Custom → Product → Commodity reflects realistic evolution
      - Cost trajectory: $500K (custom) → $500K (product) → $150K/year (SaaS)
      - Sourcing justification: Each increment has strategic rationale based on maturity
      - Roadmap communicates not just 'what' (capabilities) but 'how' (sourcing strategy)
      
      STAKEHOLDER VALUE:
      - CFO understands cost trajectory and cost optimization strategy
      - Business understands strategic vs. commodity positioning
      - IT understands when to control (Genesis/Custom) vs. when to outsource (Commodity)"
  
  overlay_2_gartner_approach:
    
    title: "Optional Overlay: Gartner IT Roadmap Approach (Technology-Focused Only)"
    
    when_to_apply: |
      "Use Gartner's approach if:
      - Scope is narrowly technology-focused (e.g., infrastructure, platforms, tools)
      - Not a full enterprise capability roadmap
      - Speed of roadmap production is critical
      - Peer benchmarking data adds stakeholder credibility
      - Less TOGAF rigor is acceptable for narrower scope"
    
    note: |
      "Gartner approach is supplementary to TOGAF Phase E/F, not a replacement. 
      Use for technology domain only; use full TOGAF for enterprise-wide roadmapping."

---

## SECTION 7: DELIVERABLE CHECKLIST

roadmap_deliverable_checklist:
  
  title: "Deliverables Checklist – Confirming Phase E/F Completeness"
  
  phase_e_deliverables:
    - "[✓] Consolidated Gaps, Solutions, and Dependencies Matrix"
    - "[✓] Capability gap inventory (current maturity vs. target maturity)"
    - "[✓] Capability increments library (with objectives, deliverables, timeline)"
    - "[✓] Transition Architecture definitions (aligned to capability increments)"
    - "[✓] Work package inventory (100+ packages, detailed definitions)"
    - "[✓] Work package dependency matrix"
    - "[✓] Implementation Factor Assessment and Deduction Matrix"
    - "[✓] Architecture Roadmap Version 0.1 (initial, unsquenced)"
    - "[✓] Implementation and Migration Plan Version 0.1 (initial)"
  
  phase_f_deliverables:
    - "[✓] Work package prioritization matrix (value/risk/cost/dependency)"
    - "[✓] Sequenced work packages (ranked order for execution)"
    - "[✓] Critical path analysis (dependencies impacting timeline)"
    - "[✓] Portfolio integration assessment (conflicts resolved)"
    - "[✓] Resource capacity analysis and hiring plan"
    - "[✓] Organizational change capacity assessment"
    - "[✓] Integrated Architecture Roadmap (incorporating constraints)"
    - "[✓] Architecture Roadmap Version 2.0 (final, executive-approved)"
    - "[✓] Implementation and Migration Plan (final, detailed)"
    - "[✓] Resource plan (FTE allocation, hiring, recruiting)"
    - "[✓] Budget plan (by quarter, by work package)"
    - "[✓] Executive presentation and business case for steering committee approval"
  
  governance_layer_deliverables:
    - "[✓] Governance framework selection (MSP or MoP)"
    - "[✓] Programme/Portfolio Board charter"
    - "[✓] Benefits definition and realization plan"
    - "[✓] Tranche plan (if MSP) or Priority list (if MoP)"
  
  execution_layer_deliverables:
    - "[✓] Project Initiation Documents (one per project/work package)"
    - "[✓] Project plans (activities, resources, schedule)"
    - "[✓] SAFe Program roadmap (if agile delivery)"
    - "[✓] Quality standards and acceptance criteria"

---

## SECTION 8: DECISION FLOWCHART

final_decision_flowchart:
  
  title: "Claude Rule Flowchart – Decision Tree for Roadmap Development"
  
  flowchart: |
    "
    START: Developing an Enterprise Roadmap?
    │
    ├─ Q1: Is solid TOGAF Phase A-D architecture available?
    │   ├─ NO → STOP: Complete Phase B Business Architecture first
    │   └─ YES → Continue to Q2
    │
    ├─ Q2: What delivery model?
    │   ├─ Stage-gated (Waterfall) → Use PRINCE2 (record for Q9)
    │   ├─ Agile/Iterative → Use SAFe (record for Q9)
    │   └─ Hybrid → Use both (record for Q9)
    │
    ├─ Q3: Programme structure?
    │   ├─ One coordinated programme → Use MSP (record for Q8)
    │   ├─ Multiple independent initiatives → Use MoP (record for Q8)
    │   └─ Mix of both → Use MoP + MSP (record for Q8)
    │
    ├─ Q4: Execute TOGAF Phase E Activities:
    │   ├─ Consolidate Gap Analysis
    │   ├─ Identify Capability Increments (Capability-Based Planning)
    │   ├─ Define Transition Architectures
    │   ├─ Identify Work Packages
    │   └─ Identify Implementation Factors
    │   → Output: Architecture Roadmap Version 0.1 + Implementation Plan 0.1
    │
    ├─ Q5: Execute TOGAF Phase F Activities:
    │   ├─ Sequence work packages by value/risk/dependency/cost
    │   ├─ Integrate with enterprise portfolio
    │   ├─ Validate resource availability
    │   ├─ Assess organizational change capacity
    │   └─ Finalize Architecture Roadmap Version 2.0
    │   → Output: Final Roadmap + Implementation Plan + Resource Plan + Budget Plan
    │
    ├─ Q6: Apply Governance Layer (MSP or MoP):
    │   ├─ If MSP: Establish Programme Board, define tranches, benefits plan
    │   ├─ If MoP: Establish Portfolio Board, prioritize initiatives, allocate resources
    │   └─ Output: Programme/Portfolio Charter + Benefits Definition
    │
    ├─ Q7: (Optional) Apply Wardley Mapping Overlay:
    │   ├─ If sourcing strategy important: Create Wardley map (technology maturity journey)
    │   └─ If not critical: Skip
    │
    ├─ Q8: (Optional) Apply Gartner Overlay (if technology-only roadmap):
    │   ├─ If narrow scope, fast timeline needed: Use Gartner for that domain only
    │   └─ If full enterprise roadmap: Stick with TOGAF
    │
    ├─ Q9: Apply Execution Layer (PRINCE2 or SAFe):
    │   ├─ If PRINCE2: Create Project Initiation Documents, project plans
    │   ├─ If SAFe: Map roadmap to Program Increments, conduct PI Planning
    │   └─ If Hybrid: PRINCE2 for foundation phase, SAFe for ongoing delivery
    │
    ├─ Q10: Obtain Approval:
    │   ├─ Architecture Review Board approves Phase E/F roadmap
    │   ├─ Steering Committee/Portfolio Board approves governance and funding
    │   └─ Proceed to execution
    │
    └─ END: Roadmap approved and ready for execution
    "

---

## SECTION 9: QUICK REFERENCE SUMMARY

quick_reference:
  
  title: "Claude Rule Quick Reference – When to Use What"
  
  framework_selection_guide:
    
    scenario_1: |
      SCENARIO: "I have solid architecture but no roadmap"
      APPROACH: "Use TOGAF Phase E/F + Capability-Based Planning natively"
      FRAMEWORKS: "TOGAF only (no external tools needed)"
      TIMELINE: "4-6 months to final roadmap"
      KEY ACTIVITY: "Gap analysis → Capability increments → Transition Architectures → Work packages → Sequencing"
    
    scenario_2: |
      SCENARIO: "I have multiple programmes competing for resources"
      APPROACH: "Use TOGAF Phase E/F roadmap as input to MoP"
      FRAMEWORKS: "TOGAF E/F → MoP → PRINCE2"
      TIMELINE: "5-7 months to approved portfolio"
      KEY ACTIVITY: "Prioritize initiatives, allocate shared resources, establish Portfolio Board"
    
    scenario_3: |
      SCENARIO: "I have one coordinated enterprise transformation"
      APPROACH: "Use TOGAF Phase E/F roadmap as input to MSP"
      FRAMEWORKS: "TOGAF E/F → MSP → PRINCE2"
      TIMELINE: "4-6 months to approved programme blueprint"
      KEY ACTIVITY: "Define tranches, establish Programme Board, plan benefits realization"
    
    scenario_4: |
      SCENARIO: "I need agile/iterative delivery, not waterfall"
      APPROACH: "Use TOGAF Phase E/F roadmap mapped to SAFe Program Increments"
      FRAMEWORKS: "TOGAF E/F → SAFe → Agile projects"
      TIMELINE: "4-6 months to first PI planning"
      KEY ACTIVITY: "Map Transition Architectures to PIs, conduct PI Planning, execute sprints"
    
    scenario_5: |
      SCENARIO: "Sourcing strategy (build vs. buy vs. outsource) is important"
      APPROACH: "Use TOGAF Phase E/F + overlay Wardley Mapping"
      FRAMEWORKS: "TOGAF E/F + Wardley Mapping"
      TIMELINE: "5-7 months (roadmap + Wardley strategic analysis)"
      KEY ACTIVITY: "Visualize technology/capability maturity evolution, sourcing decisions"
    
    scenario_6: |
      SCENARIO: "Narrow technology roadmap, need fast turnaround"
      APPROACH: "Use simplified TOGAF Phase E/F or Gartner approach"
      FRAMEWORKS: "Simplified TOGAF or Gartner"
      TIMELINE: "2-3 months (simplified approach)"
      KEY ACTIVITY: "Technology adoption curves, peer benchmarking, practical deployment"

---

## SECTION 10: COMMON PITFALLS AND HOW TO AVOID THEM

common_pitfalls:
  
  pitfall_1: |
    PITFALL: "Attempting Phase E/F roadmapping without solid Phase B Business Architecture"
    IMPACT: "Roadmap disconnected from business strategy; cannot prioritize effectively"
    MITIGATION: "Complete Phase B Business Architecture with capability maps and maturity assessments BEFORE Phase E/F"
  
  pitfall_2: |
    PITFALL: "Treating Phase F Architecture Roadmap as detailed project plan"
    IMPACT: "Unnecessary rework; project planning too abstract"
    MITIGATION: "Understand hierarchy: Roadmap (high-level) → Programme Tranches (medium-level) → Project Plans (low-level)"
  
  pitfall_3: |
    PITFALL: "Ignoring organizational change and skills gaps in roadmap"
    IMPACT: "Missed timelines, poor adoption, benefits not realized"
    MITIGATION: "Use Implementation Factor Assessment Matrix; include change work packages alongside technical work"
  
  pitfall_4: |
    PITFALL: "Creating static 3-year roadmap, not updating it"
    IMPACT: "Roadmap becomes irrelevant; stakeholder confidence erodes"
    MITIGATION: "Annual strategic refresh, quarterly portfolio review, continuous Phase H change management"
  
  pitfall_5: |
    PITFALL: "Not validating work package estimates with stakeholders"
    IMPACT: "Estimates wildly inaccurate; schedule slips; budget overruns"
    MITIGATION: "Review Phase E estimates with ARB; conduct three-point estimation (optimistic/likely/pessimistic)"
  
  pitfall_6: |
    PITFALL: "Sequencing work packages by dependency only, not by value/risk"
    IMPACT: "High-risk, low-value work gets scheduled before quick wins"
    MITIGATION: "Use prioritization matrix (value vs. risk); schedule quick wins early for momentum"
  
  pitfall_7: |
    PITFALL: "Not integrating roadmap with current enterprise projects"
    IMPACT: "Resource conflicts; organizational chaos; projects compete for same people"
    MITIGATION: "Phase F explicitly integrates with portfolio (Activity 2)"
  
  pitfall_8: |
    PITFALL: "Skipping governance layer (MoP/MSP) and going straight to project execution"
    IMPACT: "No prioritization mechanism; all work packages treated equally; no programme coherence"
    MITIGATION: "Establish MSP or MoP governance based on programme structure; allocate resources through formal board"

---

## SECTION 11: SUCCESS METRICS FOR ROADMAP DEVELOPMENT

success_metrics:
  
  phase_e_success_metrics:
    - "All business capability gaps (current → target maturity) identified and quantified"
    - "Capability increments define measurable maturity advancement (e.g., Level 1 → Level 2)"
    - "Transition Architectures map 1:1 to capability increments"
    - "Work packages are specific and estimatable (effort, cost, duration provided)"
    - "Dependencies clearly documented (no 'soft' or vague dependencies)"
    - "Implementation factors identified for cost, resource, schedule, risk"
    - "Architecture Review Board approves roadmap quality"
  
  phase_f_success_metrics:
    - "Work packages prioritized by value/risk/dependency/cost (not just dependency order)"
    - "Critical path identified and resource bottlenecks surfaced"
    - "Integrated with enterprise portfolio (conflicts resolved, not ignored)"
    - "Resource availability confirmed (hiring/recruiting plan if gaps exist)"
    - "Organizational change capacity assessed (timeline adjusted if needed)"
    - "Steering committee approves final roadmap and budget allocation"
    - "Clear executive sponsorship and governance structure in place"
  
  governance_layer_success_metrics:
    - "MSP or MoP framework selected based on programme structure"
    - "Board charter approved (authority, decision rights, escalation)"
    - "Benefits definition and realization plan documented"
    - "Tranche/portfolio plan communicated to all stakeholders"
  
  execution_layer_success_metrics:
    - "Project Initiation Documents created for first phase work packages"
    - "Resource commitment confirmed (FTE allocated, names assigned)"
    - "First project/PI on track and delivering as planned"
    - "Feedback from execution informing roadmap refinement"

---

## END OF CLAUDE RULE FILE

rule_status: "ACTIVE"
rule_version: "1.0"
last_updated: "2026-08-14"
rule_authority: "Enterprise Architecture Framework Integration"
rule_confidence: "HIGH (based on comprehensive TOGAF ADM and AXELOS framework analysis)"
```

---

# Usage Instructions for Claude

**When a user asks about developing an enterprise roadmap:**

1. **Reference this rule file** to provide consistent, framework-based guidance
2. **Use the diagnostic phase** (Section 1) to assess the user's starting point
3. **Guide through native TOGAF path** (Section 2: Phase E) if architecture is solid
4. **Guide through Phase F sequencing** (Section 3) to produce final roadmap
5. **Recommend governance layer** (Section 4: MoP or MSP) based on programme structure
6. **Recommend execution layer** (Section 5: PRINCE2 or SAFe) based on delivery model
7. **Suggest optional overlays** (Section 6: Wardley, Gartner) if applicable
8. **Check deliverables** (Section 7) to confirm completeness
9. **Reference quick reference** (Section 9) for scenario-specific guidance
10. **Warn about pitfalls** (Section 10) relevant to user's situation

This rule ensures that all roadmap development guidance is **framework-aligned, traceable, and integrated** rather than ad-hoc or tool-dependent.