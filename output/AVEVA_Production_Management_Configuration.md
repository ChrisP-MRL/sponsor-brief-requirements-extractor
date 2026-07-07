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
