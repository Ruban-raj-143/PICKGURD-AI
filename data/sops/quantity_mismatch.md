---
sop_id: SOP-QTY-001
title: Standard Operating Procedure for Quantity Mismatch Resolution
exception_type: QUANTITY_MISMATCH
version: 1.0
effective_date: 2026-08-01
status: ACTIVE
source: Synthetic Demo SOP
---

# Standard Operating Procedure for Quantity Mismatch Resolution

> [!IMPORTANT]
> **Synthetic / Demo SOP Disclaimer:** This document is a synthetic educational demo procedure created for PickGuard AI capstone project evaluation and does not represent actual Amazon internal systems, SOPs, or operational policies.

## Metadata Header
- **SOP ID:** SOP-QTY-001
- **Exception Type:** QUANTITY_MISMATCH
- **Version:** 1.0
- **Effective Date:** 2026-08-01
- **Status:** ACTIVE
- **Source:** Synthetic Demo SOP

## Purpose
Establishes mandatory procedures for fulfilment centre operators when system recorded inventory quantity differs from physically observed inventory quantity at a pick bin.

## When to Use
Apply this procedure whenever a pick task specifies a required line quantity, but the physical count of units available in the designated bin is greater or less than the expected system record.

## Detection Criteria
- System quantity recorded as N units, but physical count reveals fewer than N units.
- System quantity recorded as N units, but physical count reveals surplus units in bin.
- Partial order line fulfillable due to stock shortage.

## Verification Steps
1. **Confirm Item Identity:** Verify that all units in the bin match the target SKU barcode.
2. **Perform Double Recount:** Conduct a precise manual recount of all physical units present in the bin.
3. **Verify Reserved Stock & Recent Movement:** Check whether units were recently reserved or transferred for concurrent pick tasks.
4. **Record Observed vs System Count:** Note exact physical count observed (e.g., observed 6 units vs expected 10 units).

## Resolution Steps
1. **Partial Pick Execution:** If physical count permits partial fulfillment, pick available verified units for the order line up to required quantity.
2. **Record Exception:** Log physical quantity discrepancy on scanner terminal.
3. **Escalate Discrepancy:** Submit high-risk quantity mismatch report for supervisor review.

## Escalation Criteria
Escalate to supervisor / inventory control area manager if:
- Physical count shortage exceeds 2 units or 20% of line order value.
- Item value tier is high.
- Discrepancy involves reserved order allocations.

## Safety Restrictions
> [!CAUTION]
> **MANDATORY SAFETY RESTRICTION:**
> **Do not directly modify system inventory without required authorization.**
> Operators and automated tools must NOT update WMS inventory master records automatically upon observing a quantity mismatch. All inventory adjustments require formal human supervisor authorization and cycle count verification.

## Evidence Required
- Task ID and expected bin location.
- System expected quantity vs physical observed quantity.
- Photos or terminal count verification log.

## Example Scenario
Operator assigned to TASK-1003 arrives at bin A20-B02 to pick 10 units of Item X125. System quantity indicates 10 units, but physical count reveals only 6 units. Operator picks 6 available units, logs QUANTITY_MISMATCH exception, and escalates to supervisor without altering WMS system inventory balance.

## Important Notes
- Unauthorized inventory adjustments trigger severe audit penalties. Always escalate quantity mismatches to human supervisor review.
