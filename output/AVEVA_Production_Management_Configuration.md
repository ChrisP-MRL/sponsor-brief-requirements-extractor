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
