---
sop_id: SOP-DAMAGE-001
title: Standard Operating Procedure for Damaged Item Resolution
exception_type: DAMAGED_ITEM
version: 1.0
effective_date: 2026-08-01
status: ACTIVE
source: Synthetic Demo SOP
---

# Standard Operating Procedure for Damaged Item Resolution

> [!IMPORTANT]
> **Synthetic / Demo SOP Disclaimer:** This document is a synthetic educational demo procedure created for PickGuard AI capstone project evaluation and does not represent actual Amazon internal systems, SOPs, or operational policies.

## Metadata Header
- **SOP ID:** SOP-DAMAGE-001
- **Exception Type:** DAMAGED_ITEM
- **Version:** 1.0
- **Effective Date:** 2026-08-01
- **Status:** ACTIVE
- **Source:** Synthetic Demo SOP

## Purpose
Establishes mandatory procedures for handling physically damaged product units or compromised packaging discovered during pick execution.

## When to Use
Apply this procedure whenever an operator observes physical product crush, liquid leakage, torn factory seals, broken glass/plastic, or severe packaging deformation prior to picking.

## Detection Criteria
- Crushed, punctured, or severely dented exterior packaging.
- Broken factory security seal or opened retail box.
- Visible product crack, spill, leakage, or internal component rattle.

## Verification Steps
1. **Halt Pick Flow:** Immediately stop normal pick flow for the affected damaged unit.
2. **Verify Item Identity:** Scan barcode to confirm item identity before moving item.
3. **Assess Damage Severity Category:** Categorize damage as Packaging Minor, Packaging Severe, or Product Functional Damage.
4. **Check Bin for Undamaged Units:** Check if undamaged units of identical SKU exist in the same bin.

## Resolution Steps
1. **Undamaged Unit Available:** If another unit in bin is pristine, pick the undamaged unit, and place damaged unit in designated RED damage hold tote.
2. **All Units Damaged:** Flag DAMAGED_ITEM exception on terminal, place unit in damage tote, and request stock replenishment.
3. **Log Damage Hold:** Transport damage tote to QA quarantine area at end of aisle pick run.

## Escalation Criteria
Escalate to safety lead / supervisor if:
- Liquid spill or hazardous chemical leak is observed.
- Damage indicates broad pallet drop or structural rack failure.

## Safety Restrictions
- Do not pack or ship damaged items to customers under any circumstances.
- Do not automatically change system inventory status without supervisor authorization.

## Evidence Required
- Scanned SKU and bin location ID.
- Damage category code.
- Photo of damaged packaging/unit.

## Example Scenario
Operator picking Keyboard SKU-X126 discovers crushed box corner and broken security tape. Operator inspects bin, finds a second pristine unit of SKU-X126, picks pristine unit, and places damaged unit in RED damage hold tote.

## Important Notes
- Shipping damaged items severely harms customer trust. Always quarantine damaged units immediately.
