# PickGuard AI — Capstone Rubric Mapping

This document maps the PickGuard AI architecture and implementation features to the 8 evaluation criteria of the Capstone Evaluation Rubric.

| Rubric Criterion | Implementation Evidence in PickGuard AI | Status |
| :--- | :--- | :---: |
| **1. Problem Definition** | Focuses on a narrow, realistic, user-centred bounded task: assisting fulfilment centre pick operators to safely resolve 6 pick exception categories without performing automated WMS inventory mutations. | **PASS** |
| **2. Agent Architecture** | Built on a 13-node LangGraph `StateGraph` with explicit state schemas (`PickExceptionState`), typed transitions, conditional edge routers, and `MemorySaver` checkpointer. | **PASS** |
| **3. Tool Use** | Purposeful, deterministic Python operational tools (`get_inventory`, `get_pick_task`, `get_location`, `search_similar_incidents`, `search_sop`, `create_escalation`) querying synthetic SQLite storage. | **PASS** |
| **4. Human-in-the-Loop** | Real LangGraph `interrupt()` checkpointing for high-risk decisions (`human_review_gate`), `thread_id` state persistence, and `Command(resume=...)` resumption with reviewer accountability. | **PASS** |
| **5. Grounding / RAG** | Synthetic SOP RAG pipeline via ChromaDB (`all-MiniLM-L6-v2`), score thresholding (0.35), explicit source provenance tags, observed facts vs. inference separation, and evidence gap reporting. | **PASS** |
| **6. Evaluation** | 93 automated pytest unit, integration, API, safety, prompt injection, and E2E tests covering normal, edge, high-risk, missing data, and provider failure cases. | **PASS** |
| **7. Responsible AI** | Action boundary policy (`RECOMMENDED` vs `BLOCKED`), zero automated WMS inventory state mutation, prompt injection resistance, secret suppression, and auditability. | **PASS** |
| **8. Presentation & Demo** | React + Vite Operator Dashboard UI with preset demo buttons (Demo 1 Normal, Demo 2 Edge, Demo 3 High-Risk Interrupt), timed pitch scripts, viva Q&As, and comprehensive capstone report. | **PASS** |
