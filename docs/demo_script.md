# PickGuard AI — Capstone Demo Script

> **Disclaimer:** All warehouse data, SOP documents, bin locations, SKUs, and historical incidents in this project are strictly synthetic demo/educational data and do not represent Amazon internal systems or operational records.

---

## Demo Introduction

**Speaker:**
> *"PickGuard AI is an evidence-grounded AI assistant for fulfilment-centre pick exceptions. Instead of simply generating an unverified answer, it combines deterministic warehouse tools, SOP retrieval, historical evidence, LLM reasoning, a safety policy, and human review for high-risk cases."*

---

## DEMO 1 — Normal Case (Missing Item)

### Scenario Setup
- **Operator Input:** `"The item X123 is missing from A15-B04. The system says there are 3 units."`
- **Optional Identifiers:** `Task ID: TASK-1001`, `SKU: X123`, `Bin: A15-B04`

### Agent Processing Walkthrough
> *"The agent first classifies the exception as `MISSING_ITEM`, retrieves operational inventory and location facts via deterministic tools, retrieves the relevant Missing Item SOP (`SOP-MISSING-001`), checks historical incidents, and recommends the safest next step."*

### UI Display Results
- **Exception Type:** `MISSING_ITEM`
- **Risk Level:** `LOW RISK` (Green Badge)
- **Evidence Quality:** `STRONG`
- **Recommended Action:** `CHECK_NEIGHBOURING_LOCATION`
- **Action Status:** `RECOMMENDED`
- **Human Review Required:** `False`
- **Final Status:** `COMPLETED`
- **Provenance Tags:** `Inventory Tool`, `Pick Task Tool`, `SOP-MISSING-001`, `INC-0001`

---

## DEMO 2 — Edge Case (Combined Exceptions)

### Scenario Setup
- **Operator Input:** `"The item X124 is missing at A12-B03 and the barcode also won't scan."`

### Agent Processing Walkthrough
> *"This demonstrates that the agent can handle multiple signals instead of treating every problem as a single predefined category."*

### UI Display Results
- **Primary Exception:** `MISSING_ITEM`
- **Secondary Exception:** `BARCODE_FAILURE`
- **Risk Level:** `LOW RISK`
- **Evidence Quality:** `STRONG`
- **Recommended Action:** `CHECK_NEIGHBOURING_LOCATION` (or `VERIFY_BARCODE`)
- **Action Status:** `RECOMMENDED`
- **Human Review Required:** `False`

---

## DEMO 3 — High-Risk Case (Quantity Mismatch & Interrupt Checkpoint)

### Scenario Setup
- **Operator Input:** `"TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6."`

### Agent Processing Walkthrough
> *"Here the operator explicitly asks the system to change inventory. The LLM may understand the request, but it cannot bypass the deterministic safety policy."*

### Graph Execution & Interrupt Gate
> *"The graph is now paused at a real LangGraph `interrupt()` checkpoint."*

### UI Display Results (Before Resume)
- **Exception Type:** `QUANTITY_MISMATCH`
- **Risk Level:** `HIGH RISK` (Red Banner)
- **Action:** `ADJUST_QUANTITY` `BLOCKED`
- **Action Status:** `BLOCKED`
- **Human Review Required:** `True`
- **Run Status:** `WAITING_FOR_HUMAN_REVIEW`
- **Review Reason:** *"Consequential action 'ADJUST_QUANTITY' is BLOCKED automatically.; Evidence conflicts detected (1 active conflicts)."*

### Human Supervisor Decision
1. Supervisor inspects review payload.
2. Supervisor selects **`REJECT`** and submits note: *"Supervisor rejected inventory modification request pending physical recount."*
3. System invokes `Command(resume={"decision": "REJECT"})`.

> *"The human decision is recorded and the graph resumes from the checkpoint rather than starting again."*

### UI Display Results (After Resume)
- **Human Decision:** `REJECT`
- **Action Status:** `REJECTED_BY_HUMAN`
- **Final Summary:** *"Human reviewer REJECTED the proposed action. Pick exception remains unapproved."*
- **Inventory State:** **UNCHANGED** (System quantity remains 10 units).
