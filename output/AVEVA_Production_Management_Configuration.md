# AVEVA Production Management System Configuration Analysis

**Document Version:** 1.0  
**Date:** 7 July 2026  
**System Version:** AVEVA Production Management 2020 U2  
**User:** PIHA-CS\chris.pavlinovich

---

## 1. Executive Summary

This document provides a detailed analysis of the configured functionality within the AVEVA Production Management 2020 U2 system, based on screenshot evidence captured from the production environment. The system is configured to track downtime events across multiple mining sites and processing facilities, with comprehensive hierarchical organization and reporting capabilities.

---

## 2. System Overview

### 2.1 Application Details
- **Product Name:** AVEVA Production Management 2020 U2
- **Primary Function:** Downtime tracking and production monitoring
- **Current View:** Downtime - CSI Roy Hill.Crushing Circuit.DRP
- **Filter Context:** Records filtered to show "Sample Period is Current Hour"

### 2.2 Key Features Identified
- Hierarchical site/equipment navigation
- Real-time downtime event tracking
- Multi-site support across mining operations
- Comprehensive reporting framework
- Time-based event recording with duration tracking
- Equipment-specific monitoring

---

## 3. Organizational Hierarchy

### 3.1 Site Structure

The system is configured with a comprehensive multi-site hierarchy representing various mining and processing operations:

#### **CSI (Roy Hill)**
- Crushing Circuit
- Processing Plant
- Reports

#### **Carina**
- Crushing Circuit
- Train Loadout
- Reports

#### **GRUYERE**
- Crushing Circuit
- Email Summary
- Reports

#### **Hopes Downs4**
- Crushing Circuit
- Reclaim-TLO
- Daily Report
- Email Daily Summary
- Reports

#### **Iron Valley**
- Crushing Circuit
- Reports
- Email Summary Report

#### **Koolyanobbing**
- Main Plant
- North Plant Mt C Backfill Circuit
- Reports

#### **Mount Marion**
- Crushing Circuit 2
- Processing Plant
- Reports
- Email Daily Summary

#### **Mount Whaleback**
- Crushing Circuit
- Email Daily Summary
- Reports

#### **Reed**
- Crushing Circuit
- Email Summary
- MTD Employee
- Reports

#### **Ripidian**
- Crushing Circuit
- DSO
- Daily Report
- Email Summary
- Reports

#### **Shire**
- Crushing Circuit
- Daily Sample Report
- Email Summary Report
- Reports

#### **Utah Point**
- Wondinlas
- Plant 1
- Reports

#### **Wodgina**
- Crushing Circuit
- Email Summary
- Reports

#### **Wonmunna**
- Crushing Circuit
- Email Summary
- Reports

### 3.2 Hierarchy Characteristics

**Multi-Level Structure:**
1. **Site Level** - Geographic location/operation (e.g., CSI, Carina, GRUYERE)
2. **Equipment/Area Level** - Specific processing areas (e.g., Crushing Circuit, Processing Plant)
3. **Reporting Level** - Reports and communication outputs

**Standardized Components:**
- Most sites include a "Crushing Circuit" module
- "Reports" folders are standard across all sites
- Email notification systems (Email Summary, Email Daily Summary) are configured for multiple sites
- Some sites have specialized equipment tracking (Train Loadout, Reclaim-TLO, DSO)

---

## 4. Downtime Tracking Functionality

### 4.1 Downtime Record Structure

The system displays downtime events in a tabular format with the following data fields:

| Field | Description | Example Value |
|-------|-------------|---------------|
| **Sample Period** | Recording period indicator | Current Hour |
| **Is Clipped** | Event clipping status indicator | Checkbox (visual indicators) |
| **Last Modified** | Timestamp of last record update | 7/07/20... |
| **Last...** | Additional timestamp field | 7/07/20... |
| **Start Time** | Downtime event start | 7/07/20... |
| **End Time** | Downtime event end | 7/07/20... |
| **Duration** | Length of downtime | 10.95 (hours), 1.9 (hours) |
| **Location** | Equipment location code | CSI Ro... |
| **Equipment** | Specific equipment identifier | 10.95 CSI_R... |
| **Eff...** | Efficiency/effectiveness metric | (Partial view) |
| **Locatio...** | Extended location details | CSI_R... |
| **Cause...** | Cause category | CSI.Ro... |
| **Cause** | Specific cause description | CSI.Ro... |
| **Eff** | Efficiency rating | (Partial view) |

### 4.2 Event Tracking Details

**Visible Records:**
- Count: 2 downtime events displayed in current view
- Total Duration: 12.85 hours (10.95 + 1.9 hours)
- Location: CSI Roy Hill (CSI Ro...)
- Date: 7/07/2026 (filtered to current hour)

**Visual Indicators:**
- Color-coded rows (tan/beige highlighting on second record)
- Checkbox indicators for clipping status
- Three-state checkboxes (white, beige, blue squares) for event status tracking

### 4.3 Filtering Capabilities

**Active Filter:**
- Filter Type: Time-based
- Filter Rule: "Sample Period is Current Hour"
- Filter applies to: CSI Roy Hill.Crushing Circuit.DRP

**Filter Display:**
- Prominently shown at top of data grid
- Applied to the specific equipment hierarchy path
- Results count displayed at bottom of grid

---

## 5. User Interface Components

### 5.1 Navigation Panel (Left Sidebar)

**Primary Navigation Tabs:**
1. **Downtime** - Currently active, displaying downtime tracking interface
2. **Knowledge** - Access to knowledge base/documentation
3. **Metrics** - Performance metrics and KPI dashboard

**Hierarchy Browser:**
- Expandable/collapsible tree structure
- Visual indicators (+ / - icons) for node expansion
- Icon types:
  - Site icons (organizational level)
  - Equipment icons (operational level)
  - Report icons (document level)
- Currently viewing: Ripidian > Crushing Circuit (highlighted in blue)

### 5.2 Top Navigation Bar

**Navigation Controls (Left to Right):**
1. Back arrow (navigation history)
2. Forward arrow (navigation history)
3. Home icon (return to home view)
4. Refresh icon (reload current view)
5. Filter icon (data filtering)
6. Additional view options
7. Grid view icon (switch to grid display)
8. Chart view icon (switch to chart display)

**Right-Side Controls:**
1. Star icon (favorites/bookmarks)
2. Settings/configuration gear icon
3. Help/information icon
4. Notifications bell icon
5. User profile (PIHA-CS\chris.pavlinovich)

### 5.3 Data Grid Interface

**Grid Features:**
- Multi-column sortable table
- Horizontal scrolling for additional columns
- Resizable columns
- Status bar showing record count ("Count: 2") and total duration ("12.85")
- Horizontal scroll indicator
- Navigation arrows for moving between records

**Toolbar (Bottom of Grid):**
- Standard data manipulation icons
- Export functionality
- Print options
- Chart generation tools
- Copy/paste capabilities
- Data import/export buttons
- Refresh data button
- Additional analysis tools

### 5.4 Chart Selection Panel (Right Sidebar)

**Available Chart Types:**
1. **Gantt chart** - Timeline visualization (radio button)
2. **Pareto chart** - Pareto analysis visualization (radio button)
3. **Pie chart** - Distribution pie chart (radio button, currently selected)
4. **No chart** - Disable chart view (radio button)

**Current State:**
- Pie chart option selected
- Chart area displays "No Data Available" message
- Chart panel remains visible but empty due to filtered dataset

---

## 6. Reporting Framework

### 6.1 Report Types Configured

Based on the navigation hierarchy, the following report types are configured across sites:

#### **Daily Reports**
- Daily Report (Hopes Downs4, Ripidian)
- Daily Sample Report (Shire)
- Email Daily Summary (multiple sites)

#### **Email Notifications**
- Email Summary (GRUYERE, Iron Valley, Mount Marion, Reed, Wodgina, Wonmunna)
- Email Daily Summary (Hopes Downs4, Mount Whaleback, Ripidian)
- Email Summary Report (Iron Valley, Shire)

#### **Specialized Reports**
- MTD Employee (Reed) - Month-to-Date employee reporting
- DSO (Ripidian) - Direct Shipping Ore reporting
- Reclaim-TLO (Hopes Downs4) - Reclaim and Train Load Out
- North Plant Mt C Backfill Circuit (Koolyanobbing) - Specialized circuit reporting

### 6.2 Report Distribution

**Standardization:**
- All 14 sites have a "Reports" folder
- 10 sites have email notification systems configured
- 3 sites have daily reporting mechanisms
- Multiple sites share similar report templates

---

## 7. Equipment and Process Monitoring

### 7.1 Equipment Types Tracked

**Primary Processing Equipment:**

1. **Crushing Circuits** - Present at 14 sites
   - CSI, Carina, GRUYERE, Hopes Downs4, Iron Valley, Koolyanobbing (Main Plant), Mount Marion, Mount Whaleback, Reed, Ripidian, Shire, Wodgina, Wonmunna
   - Most common equipment type across all operations

2. **Processing Plants**
   - CSI - Processing Plant
   - Mount Marion - Processing Plant
   - Koolyanobbing - Main Plant, North Plant Mt C Backfill Circuit
   - Utah Point - Plant 1

3. **Material Handling**
   - Carina - Train Loadout
   - Hopes Downs4 - Reclaim-TLO (Train Load Out)

4. **Specialized Operations**
   - Ripidian - DSO (Direct Shipping Ore)
   - Utah Point - Wondinlas
   - Koolyanobbing - North Plant Mt C Backfill Circuit

### 7.2 Monitoring Scope

**Site Coverage:**
- 14 distinct mining/processing sites
- Geographic spread across multiple operations
- Mix of iron ore and lithium operations (Mount Marion, Wodgina, Mount Whaleback)

**Equipment Hierarchy:**
- Site → Equipment Area → Reports structure
- Equipment areas represent major process steps
- Consistent naming conventions across sites

---

## 8. Data Management and Analysis

### 8.1 Time-Based Features

**Temporal Filtering:**
- Current Hour filtering capability
- Sample Period tracking
- Start Time and End Time recording
- Duration calculation (automatic)
- Last Modified timestamp tracking

**Time Aggregation:**
- Hourly tracking
- Daily reporting (Daily Report, Email Daily Summary)
- Month-to-Date (MTD) reporting available

### 8.2 Cause and Effect Tracking

**Data Fields:**
- **Cause Category** - High-level categorization of downtime reasons
- **Cause** - Specific cause description
- **Location** - Equipment location identification
- **Equipment** - Specific equipment identifier
- **Efficiency** - Performance effectiveness metrics

**Event Classification:**
- Is Clipped indicator for partial events
- Visual status indicators (color coding)
- Multiple cause fields for detailed root cause analysis

### 8.3 Analytical Capabilities

**Visualization Options:**
1. **Gantt Chart** - Timeline-based analysis for event sequences
2. **Pareto Chart** - Identify major downtime contributors (80/20 analysis)
3. **Pie Chart** - Distribution analysis of downtime by category
4. **Grid View** - Detailed tabular data

**Export Capabilities:**
- Toolbar suggests export functionality
- Print capabilities
- Data manipulation tools
- Import/export buttons visible

---

## 9. System Configuration Insights

### 9.1 Standardization Strategy

**Common Configuration Patterns:**

1. **Equipment Naming:**
   - "Crushing Circuit" used as standard terminology across 14 sites
   - Consistent hierarchy: Site > Equipment > Reports

2. **Reporting Structure:**
   - Standard "Reports" folder at each site
   - Email notification systems widely deployed
   - Mix of automated daily summaries and on-demand reports

3. **User Interface:**
   - Consistent navigation across all sites
   - Standardized toolbar and controls
   - Uniform data grid layout

### 9.2 Site-Specific Customizations

**Unique Configurations:**
- Reed: MTD Employee reporting (employee-focused metrics)
- Ripidian: DSO (Direct Shipping Ore) tracking
- Hopes Downs4: Reclaim-TLO specialized reporting
- Koolyanobbing: Backfill circuit monitoring
- Utah Point: Multiple plant configuration (Wondinlas, Plant 1)

### 9.3 Operational Characteristics

**Current State (from screenshot):**
- System actively in use (user logged in)
- Real-time data entry (current hour filtering)
- 2 downtime events recorded for CSI Roy Hill
- Total downtime: 12.85 hours tracked
- Data spans 7/07/2026 (current day)

**Access Control:**
- User identification: PIHA-CS\chris.pavlinovich
- Domain-based authentication (PIHA-CS domain)
- User-specific session tracking

---

## 10. Functional Capabilities Summary

### 10.1 Core Functions

1. **Downtime Tracking**
   - Real-time event recording
   - Duration tracking with automatic calculation
   - Multi-site simultaneous monitoring
   - Equipment-specific attribution

2. **Cause Analysis**
   - Detailed cause categorization
   - Root cause tracking
   - Location-based analysis
   - Equipment efficiency metrics

3. **Reporting**
   - Automated daily summaries
   - Email distribution system
   - Multiple report formats
   - Customizable report templates

4. **Data Visualization**
   - Multiple chart types (Gantt, Pareto, Pie)
   - Grid-based detailed views
   - Real-time data refresh
   - Export capabilities

5. **Multi-Site Management**
   - 14 operational sites configured
   - Hierarchical organization structure
   - Consistent data model across sites
   - Site-specific customization support

### 10.2 User Interaction Patterns

**Navigation:**
- Tree-based hierarchy browsing
- Favorites/bookmark system
- Navigation history (back/forward)
- Quick home return

**Data Entry:**
- Grid-based data input
- Status indicators (checkboxes, color coding)
- Time-based filtering
- Multi-field event recording

**Analysis:**
- On-demand chart generation
- Filtering and sorting capabilities
- Data aggregation (count, duration totals)
- Export for external analysis

---

## 11. Integration Points

### 11.1 External Systems

**Email Integration:**
- Automated email reports configured for 10 sites
- Daily summary distribution
- Event-based notifications

**Data Export:**
- Standard export functionality visible in toolbar
- Support for external analysis tools
- Report generation for distribution

### 11.2 Data Flow

**Input:**
- Manual data entry (downtime events)
- Real-time event recording
- Equipment status updates

**Processing:**
- Duration calculations
- Aggregation (hourly, daily, MTD)
- Efficiency metrics computation

**Output:**
- Email notifications
- Reports (daily, summary, specialized)
- Charts and visualizations
- Data exports

---

## 12. Observations and Recommendations

### 12.1 Strengths

1. **Comprehensive Coverage** - 14 sites with consistent configuration
2. **Standardization** - Common equipment terminology and hierarchy
3. **Flexibility** - Site-specific customization while maintaining standards
4. **Reporting** - Robust automated reporting framework
5. **User Interface** - Intuitive navigation and data entry
6. **Multi-Modal Analysis** - Grid and chart views for different needs

### 12.2 Evident Use Cases

1. **Real-Time Monitoring** - Current hour filtering for active shift monitoring
2. **Historical Analysis** - Comprehensive data fields for trend analysis
3. **Root Cause Analysis** - Detailed cause tracking capabilities
4. **Management Reporting** - Automated daily summaries for leadership
5. **Cross-Site Comparison** - Consistent data structure enables benchmarking

### 12.3 Configuration Maturity

**Indicators of Mature Configuration:**
- 14 sites fully configured
- Consistent naming conventions
- Comprehensive reporting framework
- Multiple visualization options
- Automated notification systems
- Standardized data model

**Areas of Specialization:**
- Custom reports for specific sites (MTD Employee, DSO, Reclaim-TLO)
- Site-specific equipment tracking (Backfill Circuit, Train Loadout)
- Varied reporting frequencies (hourly, daily, MTD)

---

## 13. Technical Specifications

### 13.1 System Information

- **Product:** AVEVA Production Management
- **Version:** 2020 U2
- **Platform:** Windows-based application
- **Authentication:** Domain-based (PIHA-CS)
- **User Interface:** Desktop application with rich client interface

### 13.2 Data Model

**Key Entities:**
1. Site (top-level organizational unit)
2. Equipment/Area (processing location)
3. Downtime Event (tracked occurrence)
4. Cause (reason categorization)
5. Report (output document)

**Relationships:**
- Site → Equipment → Downtime Events
- Downtime Events → Causes
- Equipment → Reports

---

## 14. Conclusion

The AVEVA Production Management 2020 U2 system as configured demonstrates a comprehensive, enterprise-scale implementation for tracking downtime and production events across 14 mining and processing sites. The configuration exhibits:

- **Standardization** across sites for consistency
- **Flexibility** for site-specific requirements
- **Comprehensive reporting** for various stakeholders
- **User-friendly interface** for efficient data entry and analysis
- **Real-time capabilities** for operational decision-making
- **Historical analysis** support for continuous improvement

The system serves as a central repository for downtime tracking, enabling both real-time operational response and longer-term trend analysis across the entire operation portfolio.

---

**Document End**
