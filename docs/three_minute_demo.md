# PickGuard AI — 3-Minute Video Demo Script

**Total Duration:** 3:00

---

### [0:00–0:30] Problem Statement & Operational Impact
**Visual:** Show React Operator Dashboard UI (`http://localhost:5173`) header and input form.
**Narration:**
> *"Welcome to PickGuard AI. In fulfilment centres, pick operators constantly encounter operational exceptions like missing items, barcode failures, and quantity mismatches. Existing WMS tools provide raw balances but fail to guide operators safely. PickGuard AI solves this by combining deterministic tools, SOP RAG, LLM reasoning, a safety policy, and human-in-the-loop controls."*

---

### [0:30–1:10] Demo 1 — Normal Case (Missing Item)
**Visual:** Click `Demo 1 (Normal)` button. Submit query `"Item X123 missing at A15-B04"`.
**Narration:**
> *"In Demo 1, the operator reports a missing item. The agent parses the query, classifies it as `MISSING_ITEM`, retrieves inventory and SOP evidence, and recommends checking neighbouring location `A15-B03`. Notice the `LOW RISK` green badge and complete source provenance tags. Execution completes automatically without human interrupt."*

---

### [1:10–1:40] Demo 2 — Edge Case (Multi-Signal Exception)
**Visual:** Click `Demo 2 (Edge)` button. Submit query `"Item X124 missing and barcode won't scan"`.
**Narration:**
> *"In Demo 2, the query contains dual signals. PickGuard AI classifies primary exception `MISSING_ITEM` and secondary exception `BARCODE_FAILURE`. Rather than guessing, it synthesizes evidence from both SOPs and provides a safe verification recommendation."*

---

### [1:40–2:30] Demo 3 — High-Risk Case & LangGraph `interrupt()`
**Visual:** Click `Demo 3 (High-Risk)` button. Submit query `"System says 10 but I counted 6. Update inventory to 6"`.
**Narration:**
> *"In Demo 3, the operator requests an inventory update. The deterministic safety policy automatically BLOCKS the action `ADJUST_QUANTITY` and flags `HIGH RISK`. The graph pauses at a real LangGraph `interrupt()` checkpoint, displaying a red Supervisor Review banner. As a supervisor, I review the evidence payload and click `REJECT`. The system executes `Command(resume=...)`, recording `REJECTED_BY_HUMAN` while leaving system inventory completely UNCHANGED."*

---

### [2:30–3:00] Architecture, Safety & Conclusion
**Visual:** Expand Execution Audit Trail card showing step-by-step logs.
**Narration:**
> *"PickGuard AI enforces a strict Action Boundary: Recommendation ≠ Execution. Built on 13 LangGraph nodes with 93 passing automated tests, PickGuard AI proves that AI agents can be grounded, safe, and accountable in mission-critical operations. Thank you."*
