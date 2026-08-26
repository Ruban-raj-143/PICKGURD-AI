---
sop_id: SOP-MISSING-001
title: Standard Operating Procedure for Missing Item Resolution
exception_type: MISSING_ITEM
version: 1.0
effective_date: 2026-08-01
status: ACTIVE
source: Synthetic Demo SOP
---

# Standard Operating Procedure for Missing Item Resolution

> [!IMPORTANT]
> **Synthetic / Demo SOP Disclaimer:** This document is a synthetic educational demo procedure created for PickGuard AI capstone project evaluation and does not represent actual Amazon internal systems, SOPs, or operational policies.

## Metadata Header
- **SOP ID:** SOP-MISSING-001
- **Exception Type:** MISSING_ITEM
- **Version:** 1.0
- **Effective Date:** 2026-08-01
- **Status:** ACTIVE
- **Source:** Synthetic Demo SOP

## Purpose
Establishes standardized procedures for fulfilment centre operators when an expected item is physically missing from its assigned storage location bin during pick operations.

## When to Use
Apply this procedure whenever a pick task directs an operator to a specific bin location (e.g., A15-B04) and the target item SKU is not found in the bin or the physical stock is insufficient to fulfill the required pick quantity.

## Detection Criteria
- Bin is physically empty.
- Bin contains items, but none match the expected target SKU.
- Bin contains matching SKU, but physical count is less than the required line quantity.

## Verification Steps
1. **Confirm Task & Target Metadata:** Verify task ID, expected item SKU, and exact bin coordinates on scanner unit.
2. **Inspect Primary Storage Bin:** Visually inspect the designated primary bin, checking behind larger packages or box dividers.
3. **Inspect Designated Adjacent/Neighbouring Bins:** Check immediate neighbouring bin locations (e.g., adjacent bins A15-B03 and A15-B05) for overflow or mislaid stock.
4. **Verify Item Identity:** If matching SKU is located in a neighbouring bin, scan the item barcode to verify SKU match before picking.

## Resolution Steps
1. **Neighbouring Stock Found:** If correct SKU is located in an adjacent bin, scan item to confirm match, complete pick line, and log location discrepancy note.
2. **Item Not Found:** If item remains unlocated after checking neighbouring bins, flag pick line as MISSING_ITEM exception on terminal.
3. **Trigger Inventory Count:** Dispatch automated cycle count request for primary bin.

## Escalation Criteria
Escalate to supervisor / area manager if:
- Required pick line priority is `URGENT` or `HIGH` and no neighbouring stock exists.
- Multiple consecutive bins in the aisle report missing items, indicating potential systemic putaway error.

## Safety Restrictions
- Do NOT pick a substitute SKU without authorization.
- Do NOT enter restricted maintenance bins or unassigned storage zones.

## Evidence Required
- Primary bin ID and scanned neighbour bin IDs.
- Scanned SKU barcode or barcode failure observation.
- Physical count observation (e.g., 0 units observed).

## Example Scenario
Operator assigned to TASK-1001 arrives at bin A15-B04 to pick 3 units of Item X123. Bin A15-B04 is empty. Operator checks adjacent bin A15-B05 and discovers 3 units of Item X123. Operator scans barcode to verify SKU match and completes pick.

## Important Notes
- Always log the neighbour bin ID where item was retrieved to maintain audit trail accuracy.
