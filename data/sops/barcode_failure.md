---
sop_id: SOP-BARCODE-001
title: Standard Operating Procedure for Barcode Failure Resolution
exception_type: BARCODE_FAILURE
version: 1.0
effective_date: 2026-08-01
status: ACTIVE
source: Synthetic Demo SOP
---

# Standard Operating Procedure for Barcode Failure Resolution

> [!IMPORTANT]
> **Synthetic / Demo SOP Disclaimer:** This document is a synthetic educational demo procedure created for PickGuard AI capstone project evaluation and does not represent actual Amazon internal systems, SOPs, or operational policies.

## Metadata Header
- **SOP ID:** SOP-BARCODE-001
- **Exception Type:** BARCODE_FAILURE
- **Version:** 1.0
- **Effective Date:** 2026-08-01
- **Status:** ACTIVE
- **Source:** Synthetic Demo SOP

## Purpose
Establishes standard procedures when an item barcode is unreadable, damaged, missing, or fails scanner validation during picking operations.

## When to Use
Apply this procedure whenever a handheld scanner fails to register an item scan due to physical label degradation, smudging, missing barcode stickers, or scanner laser rejection.

## Detection Criteria
- Scanner emits failure beep or error message upon scanning.
- Barcode sticker is torn, defaced, smudged, or missing.
- Barcode label present but unreadable by optical lens.

## Verification Steps
1. **Inspect Physical Barcode:** Clean optical lens and smooth out wrinkled label.
2. **Reposition Scanner:** Re-angle scanner lens 4 to 8 inches from barcode label and retry scan.
3. **Check Alternate Identifiers:** Look for secondary 2D DataMatrix code, master carton barcode, or product serial number printed on inner packaging.
4. **Compare Against Expected SKU:** Cross-reference item brand, model number, and description against expected task SKU.

## Resolution Steps
1. **Alternate Barcode Scan:** Scan verified secondary 2D DataMatrix or master carton barcode if authorized by terminal.
2. **Manual Key Entry:** If authorized, enter verified 12-digit UPC/EAN code manually into scanner terminal.
3. **Relabel Item:** If item identity is confirmed but barcode is unreadable, transport unit to problem solve station for barcode relabeling.

## Escalation Criteria
Escalate to supervisor if:
- Item identity cannot be verified with 100% certainty.
- Multiple items in bin have unreadable barcodes.

## Safety Restrictions
- **Do not assume identity from physical appearance alone.** Always verify SKU via secondary barcode or serial number scan.

## Evidence Required
- Scanned location bin ID.
- Observed barcode condition note.
- Scanned secondary barcode or manual key entry log.

## Example Scenario
Operator assigned to TASK-1002 attempts to scan USB Cable SKU-X124 at bin A12-B03. Primary barcode label is smudged. Operator scans secondary 2D DataMatrix barcode on inner box, verifying SKU match and completing pick task.

## Important Notes
- Unverified manual entries create inventory discrepancies. Always double-check alternate barcode identifiers.
