# AVEVA Production Management System Configuration Analysis

**Document Version:** 2.0  
**Date:** 7 July 2026  
**System:** AVEVA Production Management 2020 U2  
**Organization:** CSI Mining Services

---

## 1. Executive Summary

This document provides a comprehensive technical analysis of the AVEVA Production Management 2020 U2 system as configured and deployed across CSI Mining Services operations. The analysis is based on system screenshots, database schema documentation, and the Time Usage Model (TUM) specification document PRC-OPS-COR-SPC-0001.

**Key Findings:**

- **Multi-Site Deployment**: The system is configured to support 14 distinct mining sites across Australia, encompassing crushing circuits, processing plants, haulage operations, and marine facilities.
- **Comprehensive TUM Framework**: A standardized 4-level Time Usage Model hierarchy governs downtime tracking, delay classification, and performance metrics across all operations.
- **Integrated Reporting**: SQL Server Reporting Services (SSRS) integration provides daily site reports, email summaries, and production dashboards with safety, production, and delay tracking.
- **Planning & Scheduling Capability**: The PLRP (Planning) module supports long-range activity scheduling with Gantt chart visualization spanning multiple years.
- **Flexible Data Model**: The underlying database schema uses custom field arrays (Field0001-0021 for downtime, Field0001-0035 for metrics) enabling site-specific data capture without schema changes.

The system supports crushing & fixed plant operations, haulage, and marine activities with standardized performance measurement enabling consistent benchmarking and continuous improvement across the CSI Mining Services portfolio.

---

## 2. System Overview

### 2.1 Application Details

- **Application Name:** AVEVA Production Management
- **Version:** 2020 U2
- **Application Type:** Web-based enterprise production management system
- **Access Method:** Browser-based interface (Report Server Web Portal for reports)
- **User Authentication:** Domain-based (PIHA-CSI\chris.pavlinovich visible in screenshots)

### 2.2 Core Functional Modules

From screenshot evidence, the system implements three primary functional modules:

1. **Downtime Module** - Equipment downtime event tracking with cause/effect classification
2. **Knowledge Module** - Knowledge capture and documentation functionality
3. **Metrics Module** - Production metrics and KPI tracking
4. **Planning Module** - Long-range planning and scheduling (PLRP - Planning)

### 2.3 Key System Features

- Hierarchical organizational navigation with expandable site/location tree
- Real-time and historical downtime event tracking
- Time-period filtering (e.g., "Current Hour" filter visible)
- Multiple visualization options: Gantt charts, Pareto charts, Pie charts
- Data grid with inline editing capabilities
- Event splitting for concurrent downtime causes
- Confirmation workflow (IsConfirmed flags in data model)
- SQL Server Reporting Services integration for formatted reports
- Email summary report generation and distribution
- Multi-year planning with activity tracking

---

## 3. Organizational Hierarchy

### 3.1 Site Structure

From the navigation hierarchy visible in AVEVA_Screenshot.png, the system is configured with the following 14 top-level sites:

| Site Code | Site Name | Sub-Components Visible |
|-----------|-----------|------------------------|
| CSI | CSI (Parent) | Crushing Circuit, Processing Plant, Haulage, Reports |
| Bald Hill | Bald Hill | Crushing Circuit, Processing Plant, Reports |
| Carina | Carina | Crushing Circuit, Train Loadout, Reports |
| GRUYERE | GRUYERE | Crushing Circuit, Email Summary, Reports |
| Hope Downs4 | Hope Downs4 | Crushing Circuit, Reclaim-TLO, Daily Report, Email Summary |
| Iron Valley | Iron Valley | Crushing Circuit, Reports, Email Summary Report |
| KGSM | Koolyanobbing | Main Plant, North Plant Mt C Backfill Circuit, Reports |
| Mount Marion | Mount Marion | Crushing Circuit 2, Processing Plant, Reports, Email Daily Summary |
| Mount Whaleback | Mount Whaleback | Crushing Circuit, Email Daily Summary, Reports |
| Red Ore | Red Ore | Crushing Circuit, Email Summary, MTD Employee, Reports |
| Roy Hill | Roy Hill | Crushing Circuit, DSO, Daily Report, Email Summary |
| Sanjiv Ridge | Sanjiv Ridge | Crushing Circuit, Daily Sample Report, Email Summary Report, Reports |
| West Angelas | West Angelas | Plant 1, Reports |
| Wodgina | Wodgina | Crushing Circuit, Email Summary, Reports |
| Wonmunna | Wonmunna | Crushing Circuit, Email Summary, Reports |

**Note:** The screenshot shows "Haulage" visible under CSI parent, and the planning screenshot references "CSI Haulage.PLRP" indicating haulage operations are tracked as separate reporting points.

### 3.2 Hierarchical Structure

The organizational model follows a three-tier hierarchy:

1. **Site Level** - Top-level mining site (e.g., "Roy Hill")
2. **Location Level** - Specific operational areas (e.g., "Crushing Circuit", "Processing Plant", "Haulage")
3. **Equipment/Reporting Point Level** - Individual equipment or reporting points within each location

This structure is reinforced by the database schema where `items` table has self-referential `ParentID` enabling unlimited hierarchical depth, and `reportingpoint` table links items to operational tracking points.

---

## 4. Downtime Tracking Functionality

### 4.1 Core Downtime Features

The Downtime module visible in AVEVA_Screenshot.png demonstrates the following capabilities:

**Data Grid Columns:**
- Is Clipped (checkbox indicator for events extending beyond view window)
- Last Modified timestamp
- Last... (additional timestamp field)
- Start Time
- End Time  
- Duration (calculated in hours, showing values like 10.95, 1.9)
- Location (CSI Roy Hill references visible)
- Equipment identifier
- Eff... (likely Efficiency or Effect classification)
- Location... (additional location reference)
- Cause... (downtime cause classification)
- Cause (downtime cause description)
- Eff... (effect/classification)

**Filtering & Time Selection:**
- Period filter showing "Filtered to only show records where Sample Period is Current Hour"
- Date picker showing 7/07/2026
- Count indicator showing "Count: 2" with total duration "12.85" hours

**Visualization Options:**
A dropdown menu provides chart options:
- Gantt chart (radio button selected)
- Pareto chart
- Pie chart
- No chart

### 4.2 Time Usage Model Classification

According to the TUM specification document (PRC-OPS-COR-SPC-0001), downtime events are classified into a 4-level hierarchy:

**Level 0: Calendar Time (CT)**
- Total available time (24 hours/day, 8760 hours/year)

**Level 1: Available Time vs. Downtime**
- **Available Time (AT)** - Time equipment can operate
- **Downtime (DT)** - Time equipment is unavailable:
  - Scheduled Maintenance (SM) - Planned maintenance activities
  - Unscheduled Maintenance (UM) - Breakdown events
  - Non-Maintainable Downtime (NMD) - Non-preventable events (accidents, weather)

**Level 2: Utilization Breakdown**
- **Utilised Time (UT)** - Equipment being used for production
- **Standby (SB)** - Available but not utilized:
  - Operating Standby (OSB) - Management decision
  - External Standby (ESB) - External factors beyond control

**Level 3: Operating Time Breakdown**
- **Operating Time (OT)** - Actual production time
- **Non-Productive Time (NPT)** - Activities not contributing to production (refueling, training)
- **Operating Delay (OD)** - Temporary stoppages

**Level 4: Production Rate**
- **Full Rate Production (FRP)** - Operating at or above target rate
- **Reduced Rate Production (RRP)** - Operating below target rate

### 4.3 Event Capture Requirements

From the TUM specification, each downtime event must capture:

| Data Field | Description |
|------------|-------------|
| Production Unit | Highest level of asset hierarchy (e.g., Crushing Train 1) |
| Plant Component | Component where event occurred (e.g., Conveyor) |
| Equipment ID | ID number of component (e.g., 3210CV101) |
| Equipment Type | Specific equipment type (e.g., Belt) |
| Event Start Time | Start timestamp (to the second) |
| Event End Time | End timestamp (to the second) |
| Cause | Root cause from site cause/effect matrix |
| Effect | Effect classification (No Production, Reduced Rate) |
| Classification | TUM classification code (SM, UM, NMD, OSB, ESB, OD, NPT) |
| Comment | Free-text explanation where required |

---

## 5. User Interface Components

### 5.1 Navigation Panel

**Location:** Left side panel  
**Features:**
- Hierarchical tree view labeled "Navigation" and "Hierarchy"
- Location dropdown filter at top
- Expandable/collapsible nodes with [+]/[-] icons
- Color-coded icons:
  - Orange gear icons for equipment/circuits
  - Yellow folder icons for report categories
  - Site identifiers with checkbox indicators

### 5.2 Toolbar

**Top Navigation Bar:**
- Back/Forward navigation arrows
- Home button
- Refresh button
- Filter button (funnel icon)
- Additional view controls (grid icon, list icon)
- Chart/graph button
- User profile icon (top right)
- Settings icon (gear)
- Help icon (question mark)
- Notifications icon (bell)
- User display: "PIHA-CSI\chris.pavlinovich"

### 5.3 Data Grid

**Features:**
- Multi-column sortable grid
- Checkbox column for row selection
- Color-coded rows (beige/tan highlighting visible in screenshot)
- Horizontal and vertical scrolling
- Status bar showing count and totals
- Inline editing capability implied by structure

**Grid Footer Toolbar:**
- Multiple action buttons for data manipulation
- Chart selection dropdown (visible on right)
- Export and print icons visible

### 5.4 Module Tabs

**Bottom of Navigation Panel:**
Three module tabs visible:
1. Downtime (clock icon)
2. Knowledge (book icon)
3. Metrics (gauge/chart icon)

These tabs switch between the three primary data collection modules.

---

## 6. Reporting Framework

### 6.1 SQL Server Reporting Services Integration

From AVEVA_Reporting.png and AVEVA_email_summary.png, the system integrates with **SQL Server Reporting Services** to deliver formatted reports.

**SSRS Portal Features:**
- Navigation: "SQL Server Reporting Services" breadcrumb
- Report folders: Favorites, Browse
- Reporting Date parameter with date picker (06/07/2026 17:00:00)
- NULL checkbox option
- Page navigation controls (1 of 1)
- Zoom control (100% dropdown)
- Refresh, back, print, and export buttons
- Comments toggle
- View Report button
- User context: Chris Pavlinovich

### 6.2 Daily Site Report Format

**Report:** Bald Hill Daily Site Report  
**Date:** 06/07/2026  
**Branding:** CSI Mining Services logo

**Report Sections:**

**1. Safety & Training**
Table with Day and MTD columns:
- Take Times: 52 (Day), 66 (MTD)
- Field Interactions: 16 (Day), 25 (MTD)
- Hazards: Gas bottle in laydown yard (Day), Hazards Reported: 1 (Day), 3 (MTD)
- Incidents: Nil, Incidents Reported: 0 (Day), 0 (MTD)
- PSI Topic: Hand Injuries
- Safety Discussion: CRM's for Crusher shut and quality inspections

**2. Production Summary**
Table with columns: D/S, N/S, Day, Target, Variance, MTD, MTD Target, Variance

| Metric | D/S | N/S | Day | Target | Variance | MTD | MTD Target | Variance |
|--------|-----|-----|-----|--------|----------|-----|------------|----------|
| Total Tonnes Crushed | 0 | 0 | 0 | 2,100 | -2,100 | 9,951 | 16,100 | -6,149 |
| Run Hours | 0.0 | 0.0 | 0.0 | 6.0 | -6.0 | 37.3 | 46.0 | -8.7 |
| Rate (tph) | 0 | 0 | 0 | 350 | -350 | 267 | 350 | -83 |
| Availability | 0.0% | 0.0% | 0.0% | 50.0% | -50.0% | 75.5% | 71.9% | 3.6% |
| Utilisation | 0.0% | 0.0% | 0.0% | 50.0% | -50.0% | 59.4% | 66.3% | -6.9% |
| Overall Utilisation | 0.0% | 0.0% | 0.0% | 25.0% | -25.0% | 47.1% | 42.2% | 5.0% |

**Note:** Report continues with additional sections (Delay Summary visible at bottom edge)

### 6.3 Email Summary Report Format

**Report:** GRA_EMAIL_SUMMARY (Granites Email Summary Report)  
**Date:** 06/07/2026 04:31:00  
**Title:** EMAIL SUMMARY- GRANITES  
**Branding:** CSI Mining Services logo

**Report Content:**

**Header:** Granites Daily Production Report  
**Date:** Monday, 06 July 2026

**Production Table:**
| Metric | Value |
|--------|-------|
| Daily Tonnes Target | 0 |
| Daily Tonnes Actual | 0 |
| MTD Target | 7,362 |
| MTD Actual | 0 |
| Comments | Scheduled shutdown |

**Safety Sections:**
- **Safety Focus:** Area awareness
- **Safety Discussion:** Discussed fatigue management and to check on your work mates

**Distribution:** Email delivery via SSRS subscription mechanism

### 6.4 Report Distribution

The presence of "Email Summary" and "Email Daily Summary" report nodes under multiple sites indicates automated email distribution configured for:
- Daily production reports
- Site-specific summary reports
- Targeted stakeholder distribution

---

## 7. Equipment and Process Monitoring

### 7.1 Equipment Types Tracked

From the organizational hierarchy and TUM specification, the system tracks the following equipment and process types:

**Crushing & Fixed Plant Operations:**
- Crushing Circuits (Primary, Secondary, Tertiary)
- Conveyors
- Screens
- Feeders
- Processing Plants
- Train Loadout facilities
- Reclaim operations

**Haulage Operations:**
- Haulage equipment and activities
- Tracked as separate reporting points under sites

**Marine Operations:**
- Port and marine loading facilities (referenced in TUM scope)

**Supporting Equipment:**
- Referenced in data capture requirements (belts, motors, electrical systems)

### 7.2 Performance Metrics Tracked

According to the TUM specification (PRC-OPS-COR-SPC-0001), the system calculates and reports the following metrics:

**Level 1 Metrics (Primary KPIs):**
- **Availability (%)** = Available Time / Calendar Time
- **Utilisation (%)** = Utilised Time / Calendar Time
- **Overall Utilisation (%)** = Operating Time / Calendar Time
- **Mean Time Between Failure (MTBF)** = Utilised Time / Count of UM Events
- **Mean Time to Repair (MTTR)** = Downtime / Count of Downtime Events

**Level 2 Metrics (Detailed Analysis):**
- **Mean Time Between Stoppages (MTBS)** = Operating Time / Count of (OD + NPT) Events
- **Utilisation of Available Time (%)** = Utilised Time / Available Time
- **Operating Efficiency (%)** = Operating Time / Utilised Time
- **Standby Rate (%)** = Standby Time / Calendar Time
- **Standby Ratio (%)** = Standby Time / Available Time
- **Non-Productive Time Ratio (%)** = NPT / Utilised Time
- **Operating Delay Ratio (%)** = Operating Delay / Utilised Time
- **Production Efficiency (%)** = Full Rate Production Time / Operating Time

**Level 3 Metrics (Maintenance Focus):**
- **Scheduled Maintenance Rate (%)** = SM / Calendar Time
- **Unscheduled Maintenance Rate (%)** = UM / Calendar Time
- **Non-Maintainable Downtime Rate (%)** = NMD / Calendar Time
- **Scheduled Maintenance Efficiency (%)** = SM / Downtime
- **Unscheduled Maintenance Ratio (%)** = UM / Downtime
- **Non-Maintainable Downtime Ratio (%)** = NMD / Downtime

---

## 8. Data Management and Analysis

### 8.1 Time-Based Features

**Time Granularity:**
- Minimum 1-minute granularity for event capture (per TUM specification)
- Timestamp precision to the second in database schema
- Duration calculations in hours with decimal precision (10.95 hours visible in screenshot)

**Time Period Filters:**
- Current Hour (visible in screenshot filter)
- Date range selection via date picker
- Shift-based reporting (D/S, N/S visible in daily report - Day Shift, Night Shift)

**Calendar Integration:**
- 24-hour operations (Calendar Time = 24 hours/day)
- 8760 hours/year baseline
- Multi-year planning capability (2023-2028 visible in planning Gantt chart)

### 8.2 Data Confirmation Workflow

The database schema includes `IsConfirmed` boolean fields in:
- **downtimedataset** table
- **metricsdataset** table
- **knowledgedataset** table

This indicates a two-stage data entry process:
1. **Initial Entry** - Events entered by operators (IsConfirmed = False)
2. **Confirmation** - Events reviewed and confirmed by supervisors/managers (IsConfirmed = True)

### 8.3 Data Audit and Integrity

**Audit Trail Fields:**
- **CreatedBy** (string) - User who created the record
- **LastModified** - Timestamp of last modification (visible in grid column)
- **IsDeleted** (string) - Soft delete flag for maintaining history

**Data Integrity Mechanisms:**
- **IsSplit** (boolean) - Indicates downtime event has been split across multiple causes
- **downtimedatasetsplit** table - Manages split event relationships with RootSetId, NextId, PreviousId
- **MaskedById** (int) - Tracks overlapping or superseded events
- **PercentDowntime** (double) - For partial downtime allocation

---

## 9. System Configuration Insights

### 9.1 Standardization Strategy

The deployment demonstrates a **centralized standardization** approach:

**Standardized Elements:**
- Common TUM classification hierarchy (4 levels)
- Standard performance metrics calculations
- Consistent reporting formats (daily reports, email summaries)
- Shared database schema across all sites
- Common user interface and navigation patterns

**Site-Specific Flexibility:**
- Custom field arrays (Field0001-0021 for downtime, Field0001-0035 for metrics)
- Site-specific cause/effect matrices
- Configurable reporting hierarchies
- Location-specific equipment types and reporting points

### 9.2 Scalability Features

**Multi-Site Architecture:**
- 14 sites currently configured
- Hierarchical data model supports unlimited site addition
- Centralized reporting with site-level filtering
- Common authentication and access control

**Data Model Flexibility:**
- Generic custom field arrays avoid schema changes for new data points
- Hierarchical items structure supports any organizational depth
- Type-based item classification (itemtypes table with TypeFullName, AssemblyFullName)

### 9.3 Integration Architecture

**Database Integration:**
- SQL Server backend (evident from SSRS integration)
- Relational data model with referential integrity
- Foreign key relationships between items, reporting points, and datasets

**Reporting Integration:**
- SQL Server Reporting Services for formatted reports
- Email delivery mechanism for automated distribution
- Web-based report portal access

**Change Data Capture:**
- **_cdc_type** field in downtimedatasetsplit table suggests CDC (Change Data Capture) enabled
- Supports real-time or near-real-time data replication and integration

---

## 10. Functional Capabilities Summary

### 10.1 Core Capabilities

1. **Downtime Event Management**
   - Real-time downtime event capture
   - Multi-level cause/effect classification
   - Event splitting for concurrent causes
   - Duration calculation and tracking
   - Historical event query and analysis

2. **Performance Measurement**
   - Automated metric calculations (24+ standard metrics)
   - Availability, utilization, and efficiency tracking
   - MTBF, MTTR, MTBS analysis
   - Maintenance effectiveness metrics

3. **Reporting & Analytics**
   - Daily site reports with safety, production, and variance tracking
   - Email summary distribution
   - Visualization options (Gantt, Pareto, Pie charts)
   - Shift-based reporting (Day/Night shift breakdown)
   - MTD (Month-to-Date) aggregations

4. **Planning & Scheduling**
   - Long-range planning (multi-year Gantt charts)
   - Activity scheduling with planned vs. actual tracking
   - Resource and location assignment
   - Activity state management (Available, Planned, Actual)

5. **Knowledge Management**
   - Knowledge capture module (separate from downtime)
   - Sample-based data collection (SampleDateTime in knowledgedataset)
   - Structured knowledge retention

6. **Metrics Tracking**
   - Production metrics dataset
   - Period-based aggregation (hourly, shift, daily)
   - 35 custom metric fields per reporting point

### 10.2 User Roles and Workflows

From the TUM specification document, the system supports the following organizational roles:

**1. Chief Operating Officer**
- TUM and metrics definition and change management
- Enterprise-wide standardization governance

**2. General Managers & Operations Managers**
- Target setting for sites
- Performance monitoring and variance investigation
- Corrective action implementation

**3. Site Managers**
- Daily performance monitoring and reporting
- Downtime event validation
- Non-compliance identification
- Site-specific cause/effect matrix management

**4. Operators (Implied)**
- Real-time event entry
- Initial data capture
- Equipment status updates

**5. Supervisors (Implied)**
- Data confirmation and validation
- Event classification review
- Comment and context addition

---

## 11. Integration Points

### 11.1 External System Integration

**SQL Server Reporting Services**
- Report rendering and distribution
- Email subscription mechanism
- PDF/Excel export capabilities (implied by SSRS standard features)

**Active Directory / Domain Authentication**
- User authentication (PIHA-CSI domain visible)
- Role-based access control (implied by CreatedBy tracking)

**Corporate Email System**
- Automated email report distribution
- Subscription-based delivery to stakeholders

### 11.2 Data Flow Architecture

**Input Layer:**
- Manual data entry via web interface
- Operator event creation
- Supervisor confirmation workflow

**Processing Layer:**
- TUM classification engine
- Metric calculation engine
- Duration and aggregation calculations
- Data validation and integrity checks

**Storage Layer:**
- SQL Server relational database
- Hierarchical item structure
- Time-series event datasets (downtime, metrics, knowledge)
- Audit trail and change tracking

**Output Layer:**
- Web-based data grids and visualizations
- SSRS formatted reports
- Email distribution
- Chart generation (Gantt, Pareto, Pie)

### 11.3 Data Model Integration

The database schema demonstrates a well-integrated relational model:

**Core Hierarchy:**
- `items` → Self-referential hierarchy (ParentID)
- `itemtypes` → Item type definitions
- `reportingpoint` → Links items to operational tracking

**Event Datasets:**
- `downtimedataset` → Links to reportingpoint (FK: ReportingPointId)
- `metricsdataset` → Links to reportingpoint (FK: ReportingPointId)
- `knowledgedataset` → Links to reportingpoint (FK: ReportingPointId)

**Supporting Structures:**
- `downtimedatasetsplit` → Manages split events with linked list structure (RootSetId, NextId, PreviousId)

---

## 12. Observations and Recommendations

### 12.1 System Strengths

1. **Comprehensive TUM Framework**
   - Well-documented 4-level classification system
   - Clear definitions and calculations for 24+ metrics
   - Standardized across entire organization

2. **Multi-Site Scalability**
   - 14 sites successfully deployed
   - Consistent user interface and experience
   - Centralized reporting with site-specific detail

3. **Flexible Data Model**
   - Custom field arrays avoid schema changes
   - Hierarchical structure supports any organizational model
   - Audit trail and data integrity features built-in

4. **Integrated Reporting**
   - SSRS integration provides professional report formatting
   - Automated email distribution reduces manual effort
   - Multiple visualization options for different audiences

5. **Planning Capability**
   - Multi-year planning with visual Gantt charts
   - Planned vs. actual tracking enables schedule adherence monitoring

### 12.2 Potential Use Cases for Enhancement

1. **Real-Time Dashboards**
   - Current interface shows data grids; opportunity for live KPI dashboards
   - Real-time availability and utilization gauges
   - Live production rate monitoring

2. **Mobile Data Entry**
   - Web interface suggests desktop/laptop usage
   - Mobile-optimized interface could improve data capture timeliness
   - Offline data entry with synchronization

3. **Advanced Analytics**
   - Historical data enables predictive maintenance modeling
   - Trend analysis and forecasting
   - Pareto analysis of downtime causes across sites

4. **Integration Opportunities**
   - SCADA/DCS integration for automatic event detection
   - Maintenance management system integration (work order linkage)
   - ERP integration for cost tracking and analysis

5. **Performance Benchmarking**
   - Cross-site performance comparison reports
   - Industry benchmark tracking
   - Best practice identification and sharing

---

## 13. Technical Specifications

### 13.1 Database Schema Summary

The system utilizes a SQL Server database with the following core tables:

#### items
**Purpose:** Hierarchical item/location structure

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| ID | string | PK | Unique item identifier |
| ParentID | string | FK | Self-referential parent item |
| TypeID | string | FK | Links to itemtypes |
| Name | string | | Display name |
| DisplayOrder | bigint | | Sort order for display |

#### itemtypes
**Purpose:** Item type definitions

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| ID | string | PK | Type identifier |
| TypeFullName | string | | Full type name |
| AssemblyFullName | string | | Assembly reference |

#### reportingpoint
**Purpose:** Links items to operational tracking points

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| ReportingPointId | int | PK | Unique reporting point ID |
| ItemId | string | FK | Links to items table |
| ItemFullName | string | | Full hierarchical name |
| SiteId | bigint | | Site identifier |
| LocationIdentifier | string | | Location code |

#### downtimedataset
**Purpose:** Downtime event records

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| Id | int | PK | Event ID |
| ReportingPointId | int | FK | Links to reportingpoint |
| StartDateTime | timestamp | | Event start time |
| EndDateTime | timestamp | | Event end time |
| Duration | int | | Duration in minutes |
| Cause | int | | Cause code |
| Classification | int | | TUM classification code |
| IsSplit | boolean | | Indicates split event |
| IsConfirmed | boolean | | Confirmation status |
| PercentDowntime | double | | Partial downtime percentage |
| CreatedBy | string | | User who created record |
| Field0001-Field0021 | string | | Custom fields (21 fields) |
| MaskedById | int | | Overlapping event reference |
| IsDeleted | string | | Soft delete flag |

#### metricsdataset
**Purpose:** Production metrics records

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| Id | int | PK | Metric record ID |
| ReportingPointId | int | FK | Links to reportingpoint |
| StartDateTime | timestamp | | Period start time |
| EndDateTime | timestamp | | Period end time |
| Duration | int | | Period duration |
| Period | string | | Period type (Hour, Shift, Day) |
| IsConfirmed | boolean | | Confirmation status |
| CreatedBy | string | | User who created record |
| Field0001-Field0035 | string | | Custom fields (35 fields) |
| IsDeleted | string | | Soft delete flag |

#### knowledgedataset
**Purpose:** Knowledge capture records

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| Id | int | PK | Knowledge record ID |
| ReportingPointId | int | FK | Links to reportingpoint |
| SampleDateTime | timestamp | | Sample time |
| Duration | int | | Duration |
| IsConfirmed | boolean | | Confirmation status |
| CreatedBy | string | | User who created record |
| IsDeleted | string | | Soft delete flag |

#### downtimedatasetsplit
**Purpose:** Split downtime event management

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| SetId | int | PK | Split set identifier |
| RootSetId | int | FK | Original event reference |
| NextId | int | | Next split event in chain |
| PreviousId | int | | Previous split event in chain |
| _cdc_type | string | | Change data capture type |

### 13.2 System Architecture

**Presentation Layer:**
- Web-based interface (HTML/JavaScript)
- SSRS Report Portal
- Browser-based access (no client installation required)

**Application Layer:**
- AVEVA Production Management 2020 U2 application server
- Business logic and calculation engine
- TUM classification engine
- Metric calculation services

**Data Layer:**
- SQL Server relational database
- Stored procedures for calculations (implied)
- Change Data Capture enabled
- Referential integrity enforced

**Integration Layer:**
- SQL Server Reporting Services
- Email delivery services
- Authentication services (Active Directory)

---

## 14. Planning and Scheduling Module

### 14.1 PLRP Module Overview

From AVEVA_schedule.png, the Planning module (PLRP - Planning) provides comprehensive long-range scheduling capabilities.

**Module Features:**
- **View:** PLRP - Schedule (dropdown selector visible)
- **Reporting Point:** CSI Haulage.PLRP (navigation hierarchy shows "Planning - CSI Haulage.PLRP")
- **Filter:** "Filtered to only show records where Sample Period is Current Hour"
- **Record Count:** 35 activities visible

### 14.2 Planning Data Grid

**Grid Columns:**

| Column | Type | Description |
|--------|------|-------------|
| Is Clipped | Checkbox | Indicates event extends beyond visible window |
| LastMo... (Last Modified) | Timestamp | Last modification date/time |
| Last... | Timestamp | Additional timestamp field |
| Plann... (Planned Start) | Date | Planned start date (format: 2/07/20..., showing dates in 2020s) |
| Planne... (Planned End) | Date | Planned end date |
| Planne... (Planned Duration) | Duration | Planned duration value (format: 31/07/2... visible) |
| Actual... (Actual Start) | Time | Actual start time (format: 00:00:00 visible) |
| Actual... (Actual End) | Time | Actual end time |
| Actual... (Actual Duration) | Time | Actual duration (format: 00:00:00) |
| Location | String | Location identifier (CSI Ha... visible) |
| ActivityId | String | Activity identifier (WL2343, WL2342, WL2341, WL2288, WL2272, WL2226, WL2192, EX1167, EX1050, GS3329_IV, etc.) |
| Parent... (Parent Activity) | String | Parent activity reference |
| State | String | Activity state (showing "Available") |
| Product | String | Product type (visible in grid) |
| Locatio... (Location Id) | String | Location identifier code (CSI_H... visible) |
| Require... (Required Equipment) | String | Equipment requirements |
| Require... (Required Resources) | String | Resource requirements |
| Comment | String | Free-text comments |
| Operati... (Operations) | String | Operations details |
| Operati... (Operations Details) | String | Extended operations info |
| Equip... (Equipment) | String | Equipment assignment |

### 14.3 Gantt Chart Visualization

**Timeline Features:**
- **Date Range:** Jan 29, 2023 - Dec 1, 2028 (5+ year planning horizon)
- **Timeline Granularity:** Quarterly breakdown (Q1, Q2, Q3, Q4) with year labels (2023, 2024, 2025, 2026, 2027, 2028)
- **Bar Color:** Red Gantt bars indicating scheduled activities
- **Activity Count:** 35 activities shown in left grid with corresponding Gantt bars

**Activity Identifiers Visible:**
- WL-series activities (WL2343, WL2342, WL2341, WL2288, WL2272, WL2226, WL2192, WL2324, WL2323)
- EX-series activities (EX1167, EX1050)
- GS-series activities (GS3329_IV)

**Activity Pattern:**
Most activities show bars spanning 1-2 years across 2025-2027 period, indicating long-range campaign or project planning.

### 14.4 Planning Module Actions

**Actions Panel (Right Side):**
- **Save Changes** button
- **Cancel Changes** button
- **Display options:**
  - Location (radio button)
  - ActivityId (radio button)
  - Parent Activity (radio button)
  - State (radio button)
  - Product (radio button)
  - Location Id (radio button)
  - Required Equipment (radio button)
  - Required Resources (radio button)
  - Operations (radio button)
  - Equipment (radio button)
  - SiteRef (radio button - appears at bottom)

These display options suggest the Gantt chart can be colored/grouped by different dimensions for visual analysis.

### 14.5 Planning Workflow

The Planning module supports the following workflow:

1. **Activity Definition**
   - Create activity with unique ActivityId
   - Assign to Location (e.g., CSI Haulage)
   - Define product, equipment, and resource requirements
   - Set planned start/end dates and duration

2. **Schedule Visualization**
   - View activities on multi-year Gantt chart
   - Identify resource conflicts and scheduling gaps
   - Adjust activity timing via drag-and-drop (implied by interface)

3. **State Management**
   - Track activity state (Available, Planned, Actual visible as options)
   - Transition activities through lifecycle stages

4. **Actual Tracking**
   - Record actual start/end times
   - Calculate actual duration
   - Compare planned vs. actual for variance analysis

5. **Save and Confirm**
   - Save Changes commits updates to database
   - Cancel Changes reverts unsaved modifications

### 14.6 Planning Data Integration

The Planning module likely uses the same `reportingpoint` and custom dataset structure:

**Potential Table:** A planning-specific dataset table (not visible in ERD excerpt but following same pattern):
- Links to `reportingpoint` (FK: ReportingPointId)
- Planned Start/End/Duration fields
- Actual Start/End/Duration fields
- ActivityId, State, Product, Location fields
- Custom Field0001-0035 array for flexible attributes
- IsConfirmed and CreatedBy for workflow

**Integration with Operations:**
- Planned activities define maintenance windows (Scheduled Maintenance in TUM)
- Actual execution feeds into downtime and metrics tracking
- Variance between planned and actual drives continuous improvement

---

## 15. Conclusion

The AVEVA Production Management 2020 U2 system as deployed by CSI Mining Services represents a comprehensive, enterprise-scale production management solution with the following characteristics:

**Scope and Scale:**
- 14-site deployment across diverse mining operations
- Standardized Time Usage Model with 4-level classification hierarchy
- 24+ standard performance metrics automatically calculated
- Multi-year planning and scheduling capability

**Technical Architecture:**
- SQL Server-based relational database with robust schema
- Web-based user interface accessible via standard browsers
- SSRS integration for professional reporting and email distribution
- Flexible data model with custom field arrays avoiding schema changes

**Functional Coverage:**
- Real-time downtime event tracking with cause/effect classification
- Automated availability, utilization, and efficiency calculations
- Daily site reporting with safety, production, and variance tracking
- Knowledge capture and retention
- Long-range planning with Gantt chart visualization
- Multi-dimensional data confirmation workflow

**Operational Benefits:**
- Consistent performance measurement across all CSI operations
- Standardized reporting enabling cross-site benchmarking
- Automated metric calculations reducing manual effort
- Hierarchical data model supporting any organizational structure
- Audit trail and data integrity features ensuring reliable analytics

**Strategic Advantages:**
- Common TUM framework enables consistent communication across organization
- Detailed downtime classification supports targeted improvement initiatives
- Historical data accumulation enables trend analysis and predictive modeling
- Integration architecture supports expansion to additional sites and data sources

The system provides CSI Mining Services with enterprise-class production management capabilities aligned with industry best practices and positioned to support continuous operational improvement across the organization's portfolio of mining operations.

---

**Document End**

*Analysis based on AVEVA Production Management 2020 U2 system screenshots, database schema (AMPLA_ERD.drawio), and Time Usage Model Specification PRC-OPS-COR-SPC-0001 revision 00 dated 21/01/2026.*

*Version 2.0 - 7 July 2026*
