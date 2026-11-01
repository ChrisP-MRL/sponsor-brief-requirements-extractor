# AVEVA Production Management Replacement - Knowledge Gaps Analysis

**Document Version:** 1.0
**Date:** 7 July 2026
**Author:** Solution Architecture Team
**Purpose:** Identify critical knowledge gaps required for developing requirements for a bespoke replacement system

---

## Executive Summary

This document identifies major gaps in documented knowledge about the AVEVA Production Management 2020 U2 system that must be understood before developing requirements for a replacement system. While the configuration analysis provides excellent structural understanding (sites, equipment hierarchy, UI components), it lacks the operational intelligence and business logic necessary to build a replacement system.

**Critical Finding:** The existing documentation describes **WHAT** is configured but not **HOW** it's used, **WHY** decisions are made, or **WHAT** the underlying business rules are.

---

## 1. Business Process & Workflow Gaps

### 1.1 Downtime Event Lifecycle

**Unknown:**

- How are downtime events initiated?
- What is the complete workflow from event detection to closure?
- Who has authority to create, modify, or delete events?
- What validation occurs at each stage?
- Are there approval gates for specific event types or durations?
- How are disputed or challenged events resolved?

**Why Critical:**
Without understanding the event lifecycle, the replacement system may introduce workflow breaks or bypass critical control points.

**Discovery Method:**

- Process mapping workshops with operators and supervisors
- Shadow observation during actual shift operations
- Review of event amendment logs (if available)

### 1.2 Data Entry Workflows

**Unknown:**

- When is data entered (real-time during event, end of shift, retrospectively)?
- What prompts trigger data entry?
- What validation rules exist (mandatory fields, logical checks, range validations)?
- How are partial or incomplete events handled?
- What happens when operators disagree on cause codes?
- Are there shift handover protocols fo
- r in-progress events?

**Why Critical:**
Data entry timing and validation directly impacts data quality and operational decision-making.

**Discovery Method:**

- User observation during multiple shifts across different sites
- Interview operators about pain points and workarounds
- Review training materials and SOPs

### 1.3 Correction and Amendment Processes

**Unknown:**

- Can historical records be modified? By whom?
- What audit trail is maintained for changes?
- Are corrections made in-place or via offsetting entries?
- Who approves historical corrections?
- What time window exists for corrections (24 hours, 7 days, unlimited)?
- How are corrections reflected in historical reports?

**Why Critical:**
Audit trail and data immutability requirements impact database design and security model.

**Discovery Method:**

- Review audit log records
- Interview data governance team
- Check compliance and regulatory requirements

### 1.4 Escalation and Exception Handling

**Unknown:**

- What conditions trigger management alerts?
- Who is notified when escalation thresholds are breached?
- What constitutes a "critical" downtime event?
- How are emergency situations handled differently?
- What override capabilities exist for supervisors vs. operators?
- Are there SLAs for responding to specific event types?

**Why Critical:**
Escalation logic ensures the right people are informed at the right time for critical events.

**Discovery Method:**

- Interview management and shift supervisors
- Review notification logs and alert configurations
- Document recent critical incidents and response patterns

---

## 2. Data Model & Integration Gaps

### 2.1 Cause Taxonomy and Hierarchy

**Unknown:**

- Complete list of all cause categories and subcategories
- Hierarchical relationship between cause levels (if any)
- Definitions, examples, and selection criteria for each cause code
- Which causes are standardized across all sites vs. site-specific
- How cause codes map to financial impact categories
- Who maintains the cause code master list?
- How often are new cause codes added or deprecated?
- Are there mandatory vs. optional cause fields?

**Why Critical:**
Cause taxonomy is the foundation for root cause analysis, trending, and improvement initiatives. Incomplete understanding will lead to incompatible or unusable categorization.

**Discovery Method:**

- Export complete cause code tables from AVEVA database
- Interview reliability engineers and site engineers
- Review RCA (Root Cause Analysis) documentation
- Map cause codes to maintenance planning categories

### 2.2 Equipment Master Data

**Unknown:**

- Complete equipment hierarchy (full depth beyond 2-3 levels shown)
- Equipment naming conventions and ID structures
- Integration with CMMS/EAM systems (SAP, Maximo, etc.)
- Equipment criticality classification
- Equipment grouping for analysis purposes
- Relationship between equipment and maintenance plans
- How new equipment is commissioned into the system
- Decommissioning and retirement processes
- Equipment parent-child relationships (is a pump part of a circuit?)

**Why Critical:**
Equipment master data integrity is essential for accurate tracking and integration with maintenance systems.

**Discovery Method:**

- Export complete equipment hierarchy from AVEVA
- Cross-reference with CMMS system
- Interview asset management team
- Document equipment registration workflow

### 2.3 Location vs. Equipment Distinction

**Unknown:**

- What defines a "Location" vs. "Equipment"?
- Can a location contain multiple equipment items?
- How does location relate to physical geography vs. process area?
- Are locations tied to cost centers or organizational units?
- Can equipment move between locations?

**Why Critical:**
Confusion between location and equipment will create data quality issues and incorrect reporting.

**Discovery Method:**

- Analyze sample data showing location/equipment combinations
- Interview site engineers about the distinction
- Map locations to organizational hierarchy

### 2.4 "Is Clipped" Field Logic

**Unknown:**

- What does "Is Clipped" mean in operational terms?
- Under what conditions is an event clipped?
- Does clipping affect duration calculations or KPIs?
- Are clipped events reported differently?
- Can operators manually clip events, or is it automatic?

**Why Critical:**
Unknown business rule that likely affects calculations and reporting accuracy.

**Discovery Method:**

- Review AVEVA system documentation
- Analyze data samples with clipped vs. unclipped events
- Interview power users or system administrators

### 2.5 Source System Integration

**Unknown:**

- Does AVEVA receive automated data feeds from SCADA, DCS, or PLC systems?
- What events are automatically detected vs. manually entered?
- How is time synchronized across systems and sites?
- What happens when source systems are offline?
- Are there automated triggers that create downtime events?
- How does production rate data integrate with downtime tracking?
- Is there integration with weighbridges, samplers, or quality systems?

**Why Critical:**
Understanding automation level determines development complexity and integration architecture.

**Discovery Method:**

- Interview OT (Operational Technology) team
- Review integration architecture diagrams
- Identify all systems that exchange data with AVEVA
- Document data flows and transformation logic

---

## 3. Metrics & KPIs Gaps

### 3.1 Efficiency Calculation Logic

**Unknown:**

- What does the "Eff" (efficiency/effectiveness) field represent?
- What is the formula for calculating efficiency?
- What are the input variables?
- How are planned vs. actual production rates factored in?
- Are efficiency metrics normalized for ore grade or feed characteristics?
- What constitutes 100% efficiency?
- How is efficiency aggregated from equipment to site to enterprise?

**Why Critical:**
Efficiency is a key performance metric. Incorrect calculation will undermine management confidence.

**Discovery Method:**

- Review calculation logic in AVEVA or documentation
- Interview production engineers
- Validate calculations against manual spreadsheets
- Document edge cases and rounding rules

### 3.2 OEE and Availability Metrics

**Unknown:**

- Is OEE (Overall Equipment Effectiveness) calculated within AVEVA?
- What are the Availability, Performance, and Quality components?
- How are planned vs. unplanned stops distinguished?
- What constitutes "available time" vs. "scheduled time"?
- How are startup/shutdown periods handled?
- Are there different OEE standards for different equipment types?

**Why Critical:**
OEE is a standard mining industry metric. Replacement system must support industry benchmarking.

**Discovery Method:**

- Review OEE definitions used in the organization
- Compare AVEVA output to corporate KPI reports
- Interview continuous improvement team
- Document any deviations from standard OEE definitions

### 3.3 Aggregation and Roll-Up Rules

**Unknown:**

- How are site-level metrics aggregated to enterprise level?
- Are metrics time-weighted or volume-weighted?
- How are sites of different sizes normalized for comparison?
- What events are excluded from certain KPIs?
- How are overlapping events handled in duration calculations?
- What rounding rules apply at different aggregation levels?
- How are partial periods (month-to-date, quarter-to-date) calculated?

**Why Critical:**
Incorrect aggregation creates reconciliation nightmares and management mistrust.

**Discovery Method:**

- Trace a specific metric from raw event through to executive dashboard
- Interview BI/reporting team
- Document all exclusions and adjustments
- Validate aggregations against manual calculations

### 3.4 Performance Baselines and Targets

**Unknown:**

- Where are performance targets defined and stored?
- How are targets set (nameplate capacity, historical average, budgeted)?
- Do targets vary by time period (seasonal adjustments)?
- How often are targets reviewed and updated?
- Are there different targets for different operating conditions?
- How is "target" vs. "actual" calculated in reports?

**Why Critical:**
Without baseline and target data, performance metrics lack context and meaning.

**Discovery Method:**

- Interview planning and budgeting team
- Review business planning documentation
- Determine if targets are stored in AVEVA or external system
- Document target-setting methodology

---

## 4. Reporting & Analytics Gaps

### 4.1 Report Content and Layout

**Known from Sample Reports:**

From analysis of actual report examples (Granites Email Summary and Bald Hill Daily Report), the following structure is confirmed:

**Email Summary Report Structure (e.g., Granites):**
- Site-specific title (e.g., "EMAIL SUMMARY - GRANITES")
- Report generation date/time
- Tabular format including:
  - Daily Tonnes Target vs. Actual
  - MTD (Month-to-Date) Target vs. Actual
  - Comments field (free text for shift notes, e.g., "Scheduled shutdown")
  - Safety Focus area
  - Safety Discussion narrative

**Daily Report Structure (e.g., Bald Hill):**
- Site-specific title (e.g., "DAILY REPORT - Bald Hill")
- Report metadata: Supervisor names, Weather conditions, Date
- **Safety & Training Section:**
  - Take Times (Day and MTD)
  - Field Interactions (Day and MTD)
  - Hazards identified with descriptions
  - Incidents with descriptions
  - PSI Topic
  - Safety Discussion narrative
  - Hazards Reported count (Day and MTD)
  - Incidents Reported count (Day and MTD)
- **Production Summary Section:**
  - Multiple time views: D/S (Day Shift), N/S (Night Shift), Day (combined), with Target, Variance, MTD, MTD Target, Variance columns
  - Total Tonnes Crushed
  - Run Hours
  - Rate (tph - tonnes per hour)
  - Availability percentage
  - Utilisation percentage
  - Overall Utilisation percentage
  - Variance calculations shown (negative values appear to be highlighted in red)
- **Delay Summary Section** (structure partially visible in sample)

**Report Technology:**
- Generated via SQL Server Reporting Services (SSRS)
- Web-based report portal interface
- Appears to be HTML/web format with tabular layouts
- Navigation hierarchy on left side shows all sites and report types

**Still Unknown:**

- Complete structure of "Delay Summary" section in Daily Reports
- Exact variance calculation formulas and color-coding thresholds (when does variance turn red?)
- Whether charts/graphs appear in any reports (samples show tables only)
- Complete list of all report variants across 14 sites
- Drill-down capabilities from summary to detail views
- How "Email Summary" differs from "Email Daily Summary"
- Whether operators can modify report templates or only view standard templates
- Export format options (PDF, Excel, CSV)
- How safety metrics (Take Times, Field Interactions) integrate with downtime data
- Relationship between shift-level data (D/S, N/S) and day-level aggregation

**Why Critical:**
Reports are the primary system output. The discovered structure shows that reports integrate safety, production, and downtime data in a single view. Replacement must match or exceed this integrated reporting functionality, particularly the variance-highlighting and multi-timeframe views (shift, day, MTD).

**Discovery Method:**

- ✓ Collected examples of Email Summary and Daily Report formats
- Collect remaining report types from all sites (Reclaim-TLO, DSO, MTD Employee, etc.)
- Document variance calculation formulas and threshold rules
- Interview report recipients about usefulness and gaps
- Identify any manual post-processing of reports
- Determine if Delay Summary includes Pareto analysis or other visualizations
- Understand how safety metrics feed into these reports

### 4.2 Report Distribution and Scheduling

**Unknown:**

- Who receives each report type?
- When are reports generated (exact times)?
- Are reports on-demand, scheduled, or event-triggered?
- How are distribution lists maintained?
- Can users subscribe/unsubscribe?
- What happens when report generation fails?
- Are reports archived? For how long?

**Why Critical:**
Report distribution SLAs may be contractually or operationally critical.

**Discovery Method:**

- Export report scheduling configuration
- Interview IT team about email system integration
- Document distribution lists for each report
- Identify VIPs who must receive reports

### 4.3 Analytical Usage Patterns

**Unknown:**

- How are Pareto charts actually used in decision-making?
- What analysis do users perform with Gantt charts?
- What data exports are most common?
- What ad-hoc queries do power users run?
- How is AVEVA data combined with data from other systems?
- What Excel templates or tools consume AVEVA exports?

**Why Critical:**
Understanding actual usage patterns identifies true requirements vs. rarely-used features.

**Discovery Method:**

- Interview business analysts and engineers
- Review export logs (if available)
- Shadow users performing analysis tasks
- Identify downstream tools and integration points

### 4.4 Specialized Report Details

**Unknown:**

#### MTD Employee Report (Reed):

- What employee metrics are tracked?
- How does employee time relate to equipment downtime?
- Is this a utilization report, attendance report, or productivity report?
- How does this integrate with HR or timekeeping systems?

#### DSO Report (Ripidian):

- What unique attributes of Direct Shipping Ore require tracking?
- How does DSO differ from standard crushing circuit tracking?
- Are there quality or grade considerations?
- How does this relate to customer commitments or contracts?

#### Reclaim-TLO Report (Hope Downs 4):

- What aspects of reclaim and train load-out are tracked?
- How does rail logistics integrate with production downtime?
- Are there demurrage or contract considerations?
- What unique downtime causes exist for train loading?

**Why Critical:**
Site-specific reports indicate unique business requirements that must be preserved.

**Discovery Method:**

- Obtain copies of specialized reports
- Interview site management at specialized sites
- Document unique workflows and business drivers
- Identify integration with logistics or customer systems

---

## 5. Technical Architecture Gaps

### 5.1 System Integration Architecture

**Unknown:**

- Complete list of systems that integrate with AVEVA (both inbound and outbound)
- Integration methods (APIs, file transfers, database links, message queues)
- Real-time vs. batch integration patterns
- Data transformation and mapping logic
- Error handling and recovery procedures
- Integration monitoring and alerting
- Authentication and authorization mechanisms

**Why Critical:**
Integration architecture is a major cost and risk driver for replacement system.

**Discovery Method:**

- Interview IT architecture team
- Review integration documentation and diagrams
- Analyze interface specifications
- Document data flows with sequence diagrams
- Identify integration technologies in use

### 5.2 Database Schema and Data Model

**Unknown:**

- Complete entity-relationship diagram
- Table structures, keys, and indexes
- Referential integrity constraints
- Stored procedures and business logic in database
- Database platform and version
- Data volumes (row counts, growth rates)
- Partitioning or archiving strategies

**Why Critical:**
Understanding current data model accelerates replacement system design and data migration.

**Discovery Method:**

- Export database schema
- Generate ER diagram from database
- Analyze table relationships and cardinality
- Document business rules encoded in database
- Estimate data migration complexity

### 5.3 Performance and Scalability

**Unknown:**

- Current data volumes (events per day/month/year per site)
- Number of concurrent users by site and role
- Peak usage times and load patterns
- Current system response times (baseline)
- Acceptable response time thresholds
- Network bandwidth between sites and central system
- Database size and growth rate

**Why Critical:**
Non-functional requirements (performance, scalability) drive technology choices.

**Discovery Method:**

- Analyze system usage logs
- Query database for event counts and growth trends
- Interview users about performance pain points
- Document peak periods (shift changes, month-end)
- Measure current response times

### 5.4 Current Technical Debt and Limitations

**Unknown:**

- Known bugs or limitations in current system
- Workarounds users have developed
- Features that should be automated but are manual
- Data quality issues (common errors, inconsistencies)
- Integration failures or gaps
- Reporting limitations (can't get certain views)
- Performance bottlenecks

**Why Critical:**
Understanding pain points ensures replacement system solves real problems, not just replicates current state.

**Discovery Method:**

- Review IT helpdesk tickets and issues
- Interview support team
- Conduct user satisfaction survey
- Document wishlist items from users
- Identify "shadow IT" (Excel tools, Access databases, scripts)

---

## 6. Mobile & Offline Capabilities

### 6.1 Remote Access Requirements

**Unknown:**

- Do operators access AVEVA from tablets or mobile devices?
- What operations must be performed in the field vs. control room?
- Are there remote/rural sites with limited connectivity?
- What happens during network outages?
- Can data be entered offline and synchronized later?
- What mobile device types are used (rugged tablets, phones)?

**Why Critical:**
Mobile and offline requirements fundamentally change application architecture.

**Discovery Method:**

- Survey users about mobile usage needs
- Visit remote sites to assess connectivity
- Interview IT about network infrastructure
- Document offline scenarios and workarounds

---

## 7. Site-Specific Customization Logic

### 7.1 Configuration Variability

**Unknown:**

- Which data fields are standard vs. site-specific?
- Do different sites have different cause code lists?
- Are validation rules consistent across sites or customized?
- How are site-specific business rules implemented?
- What level of autonomy do sites have for configuration changes?
- Is there a central configuration management process?

**Why Critical:**
Understanding customization requirements determines whether replacement needs multi-tenancy or configuration management.

**Discovery Method:**

- Compare configurations across multiple sites
- Interview site engineers about local customizations
- Document configuration change control process
- Identify governance model (centralized vs. federated)

### 7.2 Specialized Process Requirements

**Unknown:**

#### Train Loadout (Carina, Hope Downs 4):

- How does rail logistics create unique downtime patterns?
- Are train delays tracked as production downtime?
- How does scheduling interact with production tracking?
- What integration exists with rail operators or logistics systems?

#### Backfill Circuit (Koolyanobbing):

- What unique process characteristics require special tracking?
- How does backfill differ from standard crushing?
- Are there environmental or regulatory considerations?

#### Multiple Plants (Utah Point - Wondinlas, Plant 1):

- How are multiple plants at one site differentiated?
- Can downtime at one plant affect another?
- How is capacity allocated across plants?

**Why Critical:**
Site-specific processes may reveal requirements applicable to future expansions or acquisitions.

**Discovery Method:**

- Visit specialized sites
- Interview process engineers
- Document unique equipment or process flows
- Identify generalizable patterns

---

## 8. Operational Context Gaps

### 8.1 Downtime Classification Business Rules

**Unknown:**

- How is planned vs. unplanned downtime distinguished?
- What constitutes scheduled maintenance vs. breakdown?
- How are weather delays categorized?
- Are startup/shutdown periods considered downtime?
- How is standby time tracked (ready but not running)?
- How are external factors (power outage, supply shortage) handled?
- Can multiple concurrent causes exist for one event?
- How is primary vs. contributing cause determined?

**Why Critical:**
Downtime classification directly impacts KPIs and management reporting.

**Discovery Method:**

- Review downtime classification standards
- Interview planning and maintenance teams
- Analyze edge cases in historical data
- Document decision trees for classification

### 8.2 Concurrent and Overlapping Events

**Unknown:**

- Can one equipment item have multiple simultaneous downtime events?
- How are overlapping events handled in duration calculations?
- If downtime starts for one reason and continues for another, how is it recorded?
- Can parent and child equipment both have downtime events?
- How are cascading failures tracked?

**Why Critical:**
Concurrent event logic affects data model design and calculation accuracy.

**Discovery Method:**

- Analyze data for overlapping events
- Interview users about how they handle concurrent issues
- Test system behavior with overlapping entries
- Document business rules for event precedence

### 8.3 Decision Support Usage

**Unknown:**

- What real-time alerts exist (thresholds, conditions)?
- How is AVEVA data used in shift handover meetings?
- What questions does management ask that require AVEVA data?
- How is downtime data used in capital planning or improvement projects?
- Are there predictive or forecasting capabilities?
- Can users perform what-if analysis?
- How is AVEVA data used in operational meetings?

**Why Critical:**
Understanding decision-making context ensures replacement system supports critical business processes.

**Discovery Method:**

- Attend operational meetings where AVEVA data is reviewed
- Interview management about how they use the data
- Document questions that can't be answered with current system
- Identify analytical gaps

---

## 9. Compliance & Audit Gaps

### 9.1 Regulatory Requirements

**Unknown:**

- Are there regulatory reports generated from AVEVA data?
- What audit trail requirements exist (SOX, ISO, mining regulations)?
- How long must data be retained for compliance?
- Are there data residency requirements (where data must be stored)?
- What access controls are required for compliance?
- Are there external audit requirements?

**Why Critical:**
Compliance requirements are non-negotiable and may dictate architecture choices.

**Discovery Method:**

- Interview legal and compliance teams
- Review regulatory obligations
- Understand audit requirements
- Document data retention policies

### 9.2 Audit Trail and Data Governance

**Unknown:**

- What changes are logged in audit trail?
- Who can view audit history?
- Can records be deleted or only amended?
- How are deletions justified and approved?
- What reconciliation exists with other systems (finance, maintenance)?
- How is data quality measured and monitored?
- What data quality reports exist?

**Why Critical:**
Audit trail requirements impact database design and security model.

**Discovery Method:**

- Review audit log samples
- Interview data governance team
- Document data quality KPIs
- Understand reconciliation processes

---

## 10. User Experience & Training Gaps

### 10.1 Usability and Pain Points

**Unknown:**

- What do users find most frustrating about current system?
- Which features are rarely or never used?
- What unofficial workarounds have users developed?
- How long does it take to train a new operator?
- What common errors do new users make?
- What features do users wish existed?
- How much time do users spend in the system per shift?

**Why Critical:**
User satisfaction and productivity gains are key benefits of a replacement system.

**Discovery Method:**

- Conduct user satisfaction surveys
- Interview new users about learning curve
- Shadow users to observe pain points
- Review training materials and duration
- Facilitate wishlist workshops

### 10.2 Feature Utilization

**Unknown:**

- Which AVEVA features are heavily used vs. ignored?
- What percentage of users use chart views vs. grid only?
- How often are filters used?
- What export formats are most common?
- Do users leverage favorites/bookmarks?
- What navigation patterns are most common?

**Why Critical:**
Feature usage analysis helps prioritize development and avoid building unused functionality.

**Discovery Method:**

- Analyze usage logs if available
- Survey users about feature usage
- Identify features to deprecate or enhance
- Focus development on high-value features

---

## 11. Notification & Communication Gaps

### 11.1 Email System Configuration

**Unknown:**

- What specific events trigger each email type?
- What content is included in each email (data fields, formatting)?
- When exactly are emails sent (times, frequencies)?
- Who is on each distribution list?
- How are distribution lists maintained?
- Can users self-subscribe to reports?
- What happens when email delivery fails?
- Are emails sent via SMTP, Exchange, or other mechanism?

**Why Critical:**
Email notifications may be contractually required or operationally critical.

**Discovery Method:**

- Export email configuration from AVEVA
- Collect examples of all email types
- Document distribution lists
- Interview recipients about email usefulness
- Identify integration with email system

### 11.2 Real-Time Alerting

**Unknown:**

- What conditions trigger real-time alerts?
- Who receives alerts (roles vs. individuals)?
- What alert channels exist (email, SMS, dashboard)?
- What escalation logic exists?
- Can users acknowledge or snooze alerts?
- How are alert thresholds configured and maintained?

**Why Critical:**
Real-time alerting may be essential for operational response to critical events.

**Discovery Method:**

- Review alert configuration
- Interview operations management
- Document alert response procedures
- Test current alert functionality

---

## 12. Data Migration and Transition

### 12.1 Historical Data Requirements

**Unknown:**

- How much historical data must be migrated?
- What is the minimum historical period required (1 year, 5 years)?
- Can old data be archived read-only or must it remain editable?
- Are there specific historical reports that must be reproducible?
- What data quality issues exist in historical data?
- How will data be validated after migration?

**Why Critical:**
Data migration is often the highest-risk element of system replacement.

**Discovery Method:**

- Define data retention requirements
- Assess historical data quality
- Estimate migration complexity
- Plan for parallel running period

### 12.2 Cutover and Transition

**Unknown:**

- Can cutover be site-by-site or must be big-bang?
- What is acceptable downtime for cutover?
- What parallel running is required?
- How will users be trained on new system?
- What fallback plan exists if cutover fails?
- What operational disruption is acceptable?

**Why Critical:**
Transition strategy impacts risk and project timeline.

**Discovery Method:**

- Develop transition strategy options
- Assess operational constraints
- Plan training approach
- Define success criteria for cutover

---

## Priority Knowledge Acquisition Roadmap

### Phase 1: Critical Business Understanding (Weeks 1-3)

#### Week 1: Process & Workflow

- **Activity:** Conduct business process workshops at 3 representative sites (large, medium, small)
- **Participants:** Operators, shift supervisors, site engineers
- **Deliverable:** Process flow diagrams for event lifecycle, data entry, corrections, escalations
- **Key Questions:** How does downtime get recorded from detection to closure?

#### Week 2: Data Model & Taxonomy

- **Activity:** Extract and document complete data model
- **Participants:** Database administrators, system administrators, reliability engineers
- **Deliverable:**
  - Complete cause code taxonomy with definitions
  - Equipment master data structure
  - ER diagram from database schema
- **Key Questions:** What does each cause code mean? How is equipment hierarchy structured?

#### Week 3: Metrics & Calculations

- **Activity:** Document all KPI and metric calculations
- **Participants:** Production engineers, continuous improvement team, BI analysts
- **Deliverable:**
  - Efficiency calculation formulas
  - OEE calculation methodology
  - Aggregation and roll-up rules
- **Key Questions:** How are efficiency and availability calculated? What gets excluded from KPIs?

### Phase 2: Technical Architecture (Weeks 4-6)

#### Week 4: Integration Architecture

- **Activity:** Map all system integrations
- **Participants:** IT architecture team, OT team, integration developers
- **Deliverable:**
  - Integration architecture diagram
  - Interface specifications for all integrations
  - Data flow documentation
- **Key Questions:** What systems exchange data with AVEVA? Real-time or batch?

#### Week 5: Performance & Scale

- **Activity:** Analyze performance requirements and current limitations
- **Participants:** IT operations, database administrators, end users
- **Deliverable:**
  - Data volume analysis
  - Concurrent user load patterns
  - Performance benchmarks and requirements
  - Technical debt documentation
- **Key Questions:** How many events per day? What are performance pain points?

#### Week 6: Database Deep Dive

- **Activity:** Extract and analyze database schema and business logic
- **Participants:** Database administrators, senior developers
- **Deliverable:**
  - Complete database schema documentation
  - Business rules encoded in database
  - Data quality assessment
  - Migration complexity estimate
- **Key Questions:** What business logic lives in the database? What's data quality like?

### Phase 3: Reporting & Analytics (Weeks 7-8)

#### Week 7: Report Inventory

- **Activity:** Collect and document all reports
- **Participants:** Report recipients at all sites, BI team
- **Deliverable:**
  - Complete report inventory with examples
  - Distribution lists and schedules
  - Report usage and satisfaction assessment
- **Key Questions:** What reports exist? Who uses them? Are they valuable?

#### Week 8: Analytical Usage

- **Activity:** Understand how users analyze data
- **Participants:** Business analysts, engineers, management
- **Deliverable:**
  - User analysis workflow documentation
  - Downstream tool integration mapping
  - Analytical gaps identification
- **Key Questions:** How is AVEVA data actually used in decision-making?

### Phase 4: Site-Specific & Edge Cases (Weeks 9-10)

#### Week 9: Specialized Sites

- **Activity:** Visit and document specialized site requirements
- **Participants:** Site engineers at Reed, Ripidian, Hope Downs 4, Koolyanobbing, Utah Point
- **Deliverable:**
  - Specialized process documentation
  - Site-specific requirement capture
  - Configuration variability analysis
- **Key Questions:** What makes these sites different? Can requirements be generalized?

#### Week 10: Operational Context

- **Activity:** Document business rules and decision support usage
- **Participants:** Operations management, planning team
- **Deliverable:**
  - Downtime classification decision trees
  - Concurrent event handling rules
  - Decision support usage patterns
- **Key Questions:** How are edge cases handled? How is data used in decisions?

### Phase 5: Compliance & User Experience (Weeks 11-12)

#### Week 11: Compliance & Audit

- **Activity:** Document regulatory and audit requirements
- **Participants:** Legal, compliance, internal audit, data governance
- **Deliverable:**
  - Compliance requirements matrix
  - Audit trail specifications
  - Data retention policies
- **Key Questions:** What are regulatory obligations? What audit capabilities are required?

#### Week 12: User Experience & Training

- **Activity:** Assess usability and training needs
- **Participants:** End users, trainers, support team
- **Deliverable:**
  - User satisfaction survey results
  - Pain points and wishlist compilation
  - Feature utilization analysis
  - Training requirements
- **Key Questions:** What frustrates users? What do they wish existed?

---

## Discovery Activity Details

### 1. System Database Schema Export

**Method:** Direct database access with schema export tools
**Deliverable:** Complete ER diagram, table definitions, relationships, constraints
**Estimated Effort:** 2-3 days
**Owner:** Database Administrator

### 2. Report Template Extraction

**Method:** Export report definitions from AVEVA configuration
**Deliverable:** All report templates, SQL queries, formatting specifications
**Estimated Effort:** 3-5 days
**Owner:** BI Analyst / AVEVA System Administrator

### 3. User Interviews (Stratified by Role)

**Roles to Interview:**

- Operators (2-3 per site at 5 sites) - 10-15 interviews
- Shift Supervisors (1-2 per site at 5 sites) - 5-10 interviews
- Site Engineers (1 per site at all sites) - 14 interviews
- Central Reporting Team - 2-3 interviews
- IT Support Team - 2-3 interviews
- Management (site and corporate) - 5-8 interviews

**Interview Duration:** 60-90 minutes each
**Estimated Effort:** 40-50 interviews × 1.5 hours = 60-75 hours
**Owner:** Business Analyst team

### 4. Process Observation (Job Shadowing)

**Sites:** 3 representative sites
**Shifts:** At least 2 shifts per site (day and night)
**Duration:** Full shift (12 hours typical)
**Estimated Effort:** 6 shifts × 12 hours = 72 hours observation + 24 hours documentation
**Owner:** Business Analyst team

### 5. Integration Documentation Review

**Method:** Review existing integration specifications, interview integration developers
**Deliverable:** Integration architecture diagram, interface specs, data flow diagrams
**Estimated Effort:** 5-10 days
**Owner:** Solution Architect / Integration Architect

### 6. Analytics Deep-Dive Workshop

**Participants:** Business analysts, engineers, BI team
**Duration:** 1 day workshop
**Deliverable:** Understanding of how Pareto, Gantt, and other analytics are used
**Estimated Effort:** 1 day workshop + 2 days documentation
**Owner:** Business Analyst

### 7. Pain Point Workshop

**Method:** Facilitated workshop with users from multiple sites
**Duration:** Half-day workshop
**Deliverable:** Prioritized list of pain points and improvement opportunities
**Estimated Effort:** 0.5 day workshop + 1 day analysis
**Owner:** Business Analyst / Change Manager

### 8. Data Quality Assessment

**Method:** Statistical analysis of actual AVEVA data
**Analyses:**

- Completeness (null/missing values)
- Consistency (referential integrity violations)
- Accuracy (outliers, impossible values)
- Timeliness (lag between event and recording)
- Duplication (duplicate events)

**Estimated Effort:** 5-7 days
**Owner:** Data Analyst

### 9. Site Visits

**Sites to Visit:** All 14 sites (prioritize 5-7 for detailed observation)
**Duration:** 1-2 days per site
**Activities:**

- Observe control room operations
- Interview site personnel
- Document physical layout and equipment
- Review site-specific configurations
- Assess network connectivity

**Estimated Effort:** 14-28 days travel + observation
**Owner:** Solution Architect + Business Analyst

### 10. Configuration Comparison Analysis

**Method:** Export configurations from multiple sites, compare systematically
**Deliverable:** Configuration variance matrix, common vs. custom elements
**Estimated Effort:** 3-5 days
**Owner:** System Administrator + Solution Architect

---

## Risk Assessment

### High-Risk Knowledge Gaps (Must Resolve Before Requirements)

1. **Business Process Workflows** - Risk: Building wrong workflows into system
2. **Cause Code Taxonomy** - Risk: Incompatible categorization breaks trending
3. **KPI Calculation Logic** - Risk: Incorrect metrics undermine management trust
4. **Integration Architecture** - Risk: Missing integrations break operational processes
5. **Compliance Requirements** - Risk: Non-compliance creates legal exposure

### Medium-Risk Knowledge Gaps (Resolve During Requirements Phase)

6. **Report Content Details** - Risk: Missing key reports frustrates users
7. **Data Entry Validation Rules** - Risk: Poor data quality
8. **Site-Specific Customizations** - Risk: Loss of critical functionality at specific sites
9. **Mobile/Offline Requirements** - Risk: Unusable in field conditions
10. **Performance Requirements** - Risk: Slow system impacts operations

### Lower-Risk Knowledge Gaps (Can Resolve During Design)

11. **Chart Usage Patterns** - Risk: Sub-optimal analytics capability
12. **User Experience Preferences** - Risk: Lower user satisfaction
13. **Training Requirements** - Risk: Longer adoption period
14. **Feature Utilization** - Risk: Building unused features

---

## Success Criteria for Knowledge Acquisition

### Objective Evidence of Sufficient Understanding

**You have sufficient knowledge when:**

1. **Process Understanding:** You can draw the complete workflow from event detection through closure with all decision points and approvals
2. **Data Model Clarity:** You have a complete ER diagram and can explain every entity, relationship, and key field
3. **Calculation Transparency:** You can reproduce any KPI calculation from raw events and get the same result as AVEVA
4. **Integration Completeness:** You have documented every system that exchanges data with AVEVA, with interface specs
5. **Report Verification:** You can generate sample output for every report type and verify it matches AVEVA output
6. **Rule Documentation:** You have documented business rules as executable decision trees or pseudocode
7. **User Validation:** Users review your process maps and say "yes, that's how it works"
8. **Confidence Test:** A developer could build a replacement system from your documentation without asking further questions

---

## Estimated Timeline and Effort

### Knowledge Acquisition Phase Summary

| Phase                    | Duration           | Effort (Person-Days)   | Key Deliverables                                                |
| ------------------------ | ------------------ | ---------------------- | --------------------------------------------------------------- |
| Phase 1: Business        | 3 weeks            | 30-40                  | Process flows, cause taxonomy, KPI formulas                     |
| Phase 2: Technical       | 3 weeks            | 30-40                  | Integration architecture, database schema, performance baseline |
| Phase 3: Reporting       | 2 weeks            | 15-20                  | Report inventory, analytical workflows                          |
| Phase 4: Site-Specific   | 2 weeks            | 20-30                  | Specialized requirements, edge cases                            |
| Phase 5: Compliance & UX | 2 weeks            | 15-20                  | Compliance matrix, user feedback                                |
| **Total**          | **12 weeks** | **110-150 days** | **Complete requirements foundation**                      |

### Team Composition

- **Solution Architect:** 50% allocation (30 days)
- **Business Analysts (2-3):** 100% allocation (120-180 days combined)
- **Technical Architect:** 30% allocation (18 days)
- **Data Analyst:** 50% allocation (30 days)
- **AVEVA System Administrator:** 20% allocation (12 days)
- **Database Administrator:** 10% allocation (6 days)

**Total Team Effort:** 216-276 person-days over 12 weeks

---

## Critical Success Factors

### Prerequisites for Success

1. **Executive Sponsorship:** Senior leadership must mandate cooperation and prioritize knowledge transfer
2. **User Availability:** Operational staff must be released for interviews and observation
3. **System Access:** Full access to AVEVA database, configuration, and logs required
4. **Documentation Access:** All existing documentation, procedures, training materials
5. **Cross-Functional Participation:** IT, Operations, Finance, Compliance all engaged
6. **Transparent Communication:** Honest assessment of current system limitations and workarounds

### Red Flags (Indicators of Insufficient Knowledge)

- **"That's just how AVEVA works"** - Indicates business rule is not understood
- **"We'll figure that out during development"** - Defers critical decisions too late
- **"It's too complex to explain"** - Lack of process understanding
- **"We have workarounds for that"** - Hidden requirements
- **Reluctance to share pain points** - Cultural barrier to improvement
- **No one knows why it's configured that way** - Lost institutional knowledge

---

## Next Steps

### Immediate Actions (Week 1)

1. **Secure Executive Sponsorship:** Present this analysis to steering committee, obtain mandate
2. **Assemble Core Team:** Recruit solution architect, business analysts, technical architect
3. **Develop Detailed Discovery Plan:** Expand this roadmap into detailed work breakdown structure
4. **Schedule Site Visits:** Coordinate with site management for access and interviews
5. **Request System Access:** Obtain credentials and permissions for AVEVA database and configuration
6. **Kickoff Meeting:** Align stakeholders on discovery approach and timeline

### Quick Wins (Weeks 1-2)

1. **Database Schema Export:** Low-effort, high-value activity to start immediately
2. **Report Collection:** Gather examples of all report types from all sites
3. **User Survey:** Deploy online survey to gather initial feedback from broad user base
4. **Integration Inventory:** Interview IT to list all systems that integrate with AVEVA
5. **Cause Code Export:** Extract complete cause code list from database

### Foundation Building (Weeks 3-6)

1. **Process Workshops:** Facilitate detailed process mapping with operational staff
2. **Site Visits:** Visit 5-7 priority sites for observation and interviews
3. **Technical Deep Dive:** Analyze database, integration architecture, performance data
4. **Calculation Validation:** Reverse-engineer and document all KPI formulas

---

## Appendices

### Appendix A: Interview Question Templates

*(To be developed - tailored question sets for each role)*

**Operator Interview Questions**
**Shift Supervisor Interview Questions**
**Site Engineer Interview Questions**
**Management Interview Questions**
**IT/System Administrator Interview Questions**

### Appendix B: Data Collection Templates

*(To be developed - standardized templates for capturing information)*

**Process Flow Template**
**Business Rule Documentation Template**
**Integration Specification Template**
**Report Inventory Template**
**Configuration Variance Matrix**

### Appendix C: Risk Register

*(To be developed - detailed risk tracking)*

**Knowledge Gap Risk Register**
**Mitigation Strategies**
**Contingency Plans**

### Appendix D: Stakeholder Matrix

*(To be developed - comprehensive stakeholder map)*

**Stakeholder Analysis**
**Communication Plan**
**Engagement Strategy**

---

## Document Control

**Version History:**

| Version | Date        | Author                     | Changes          |
| ------- | ----------- | -------------------------- | ---------------- |
| 1.0     | 7 July 2026 | Solution Architecture Team | Initial analysis |

**Approval:**

| Role                    | Name | Signature | Date |
| ----------------------- | ---- | --------- | ---- |
| Solution Architect Lead |      |           |      |
| Program Manager         |      |           |      |
| Business Owner          |      |           |      |

**Distribution:**

- Steering Committee
- Project Team
- Site Management
- IT Leadership

---

**Document End**
