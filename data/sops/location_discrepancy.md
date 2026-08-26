---
sop_id: SOP-LOC-001
title: Standard Operating Procedure for Location Discrepancy Resolution
exception_type: LOCATION_DISCREPANCY
version: 1.0
effective_date: 2026-08-01
status: ACTIVE
source: Synthetic Demo SOP
---

# Standard Operating Procedure for Location Discrepancy Resolution

> [!IMPORTANT]
> **Synthetic / Demo SOP Disclaimer:** This document is a synthetic educational demo procedure created for PickGuard AI capstone project evaluation and does not represent actual Amazon internal systems, SOPs, or operational policies.

## Metadata Header
- **SOP ID:** SOP-LOC-001
- **Exception Type:** LOCATION_DISCREPANCY
- **Version:** 1.0
- **Effective Date:** 2026-08-01
- **Status:** ACTIVE
- **Source:** Synthetic Demo SOP

## Purpose
Establishes standardized procedures when system location records differ from actual physical bin locations where an item is discovered.

## When to Use
Apply this procedure whenever system records specify Location A (e.g. A15-B04), but physical evidence indicates the item is stored at Location B (e.g. A15-B05 or Zone Z02).

## Detection Criteria
- System expects item at Location A, but bin A is mapped to a different zone or bin ID.
- Item found in Location B while picking another task.
- Putaway scan mismatch where physical shelf tag differs from system bin record.

## Verification Steps
1. **Verify Item Identity:** Scan barcode to confirm product SKU matches target task.
2. **Verify Expected Location:** Confirm expected aisle, rack, and bin coordinates on terminal.
3. **Inspect Adjacent & Secondary Overflow Bins:** Check neighbouring bins to determine if item was shifted during restocking.
4. **Compare Operational Evidence:** Check last movement timestamp and putaway operator logs.

## Resolution Steps
1. **Item Found at Discrepant Location:** Scan item barcode at physical location, verify SKU match, and complete pick line.
2. **Log Location Discrepancy Note:** Submit location update flag on scanner terminal specifying actual physical bin ID.
3. **Trigger Bin Mapping Audit:** System dispatches location correction task for inventory controller.

## Escalation Criteria
Escalate to supervisor if:
- Item is found in an unmapped or blocked maintenance zone.
- Systematic location displacement affects an entire aisle row.

## Safety Restrictions
- **Do not silently change location records.** Always log formal location discrepancy report so WMS mapping can be audited.

## Evidence Required
- Expected bin location ID vs actual physical bin location ID.
- Scanned SKU barcode output.
- Location discrepancy report log.

## Example Scenario
Operator assigned to pick item SKU-X123 at expected bin A15-B04 finds bin empty, but discovers SKU-X123 stock in bin A15-B05. Operator scans item at A15-B05, picks required quantity, and logs LOCATION_DISCREPANCY note on terminal.

## Important Notes
- Accurately logging location discrepancies ensures WMS bin mapping stays synchronized across all shift crews.
