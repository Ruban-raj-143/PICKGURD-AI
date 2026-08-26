# PickGuard AI — Grounding & Fact vs. Inference Distinction

## Concrete Example

### 1. Observed Facts (Verified Data)
- **Fact 1:** `"Inventory system reports 3 units of X123 at location A15-B04."` (Source: Inventory Tool)
- **Fact 2:** `"Pick Task TASK-1001 requires 1 unit of X123 at location A15-B04."` (Source: Pick Task Tool)
- **Fact 3:** `"Operator physically observed 0 units at bin A15-B04."` (Source: Operator Query)

### 2. Evidence-Grounded Inferences (LLM Reasoning Output)
- **Inference 1:** *"The required item X123 may be physically misplaced in an adjacent storage bin (e.g. A15-B03 or A15-B05) due to recent stocking activity."*
- **Inference 2:** *"A inventory count discrepancy exists between system stock (3) and bin contents (0)."*

### 3. Evidence Gaps & Missing Context
- **Gap 1:** *"No recent bin transfer log available for bin A15-B04 within the last 2 hours."*
- **Gap 2:** *"Reserve storage bin locations for SKU X123 were not checked."*

---

## Why This Distinction Matters in Fulfilment Operations

1. **Hallucination Prevention:** Presenting an inference as an observed fact (e.g. telling the operator *"The item is in bin A15-B03"*) causes wasted operator walk time and pick line delays if false.
2. **Safety & Audit Compliance:** Warehouse auditors require clear distinction between system inventory balances and physical observations before authorizing recounts or adjustments.
3. **Evidence-Backed Recommendations:** Operators trust decision support tools when recommendations cite explicit operational facts and SOP rules rather than opaque AI claims.
