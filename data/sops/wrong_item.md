---
sop_id: SOP-WRONG-001
title: Standard Operating Procedure for Wrong Item Resolution
exception_type: WRONG_ITEM
version: 1.0
effective_date: 2026-08-01
status: ACTIVE
source: Synthetic Demo SOP
---

# Standard Operating Procedure for Wrong Item Resolution

> [!IMPORTANT]
> **Synthetic / Demo SOP Disclaimer:** This document is a synthetic educational demo procedure created for PickGuard AI capstone project evaluation and does not represent actual Amazon internal systems, SOPs, or operational policies.

## Metadata Header
- **SOP ID:** SOP-WRONG-001
- **Exception Type:** WRONG_ITEM
- **Version:** 1.0
- **Effective Date:** 2026-08-01
- **Status:** ACTIVE
- **Source:** Synthetic Demo SOP

## Purpose
Establishes mandatory procedures for fulfilment centre operators when a bin contains an item SKU that differs from the expected target SKU specified by the WMS pick task.

## When to Use
Apply this procedure whenever an operator scans an item located in the expected bin and the scanner registers a WRONG_ITEM barcode mismatch.

## Detection Criteria
- Scanned product barcode does not match expected task SKU.
- Physical product appearance, packaging, or brand differs from task description.
- Incorrect product variant or color stored in bin.

## Verification Steps
1. **Confirm Expected SKU:** Verify expected SKU and barcode sequence displayed on scanner terminal.
2. **Confirm Observed SKU:** Read and verify the physical barcode printed on the observed product packaging.
3. **Check Adjacent Bins & Shelf Dividers:** Inspect adjacent bin slots to determine if items were transposed during morning putaway.
4. **Inspect Inner Packaging:** Check whether outer carton barcode differs from inner unit barcode.

## Resolution Steps
1. **Transposed Item Found:** If correct item is found in adjacent bin slot, scan correct item, complete pick, and flag putaway correction.
2. **Wrong Item Only:** If bin contains only incorrect SKU, do NOT pick the wrong item. Flag WRONG_ITEM exception on terminal.
3. **Quarantine Misplaced Item:** Place wrong item in tote for inventory re-sorting.

## Escalation Criteria
Escalate to supervisor if:
- Entire shelf lot consists of misplaced wrong SKUs.
- High-value electronics variant swap is detected.

## Safety Restrictions
- **Do not pick the wrong item.** Never fulfill an order line with an unverified or alternate SKU without supervisor sign-off.

## Evidence Required
- Expected SKU vs observed SKU barcode scan output.
- Location bin ID.
- Physical photograph of misplaced product.

## Example Scenario
Operator assigned to pick Wireless Mouse (SKU-X123) at bin A15-B04 scans item in bin and scanner reports WRONG_ITEM (USB Cable SKU-X124 scanned). Operator verifies wrong item is stored in bin, checks adjacent slot, and escalates to inventory lead.

## Important Notes
- Picking a wrong item leads directly to customer shipment errors. Strict scanner validation must be enforced.
