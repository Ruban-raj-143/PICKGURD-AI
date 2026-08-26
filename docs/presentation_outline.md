# PickGuard AI — Capstone Presentation Outline (10 Slides)

## Slide 1 — Title Slide
- **Title:** PickGuard AI: Evidence-Grounded Pick Centre Operator Assistant
- **Subtitle:** An Evidence-Grounded LangGraph Agent for Fulfilment Centre Exception Resolution
- **Presenter / Team:** Senior AI Architect & Engineering Lead

---

## Slide 2 — Problem Statement & Operational Impact
- **Operational Reality:** Fulfilment centre pick operators frequently encounter missing items, quantity mismatches, unreadable barcodes, wrong SKUs, and damaged products.
- **Pain Point:** Standard WMS interfaces provide transactional data but lack grounded exception resolution guidance, forcing operators to guess or make risky inventory edits.
- **Goal:** Build an evidence-grounded AI assistant that guides pick operators safely without performing unauthorized warehouse state mutations.

---

## Slide 3 — User & Bounded Task
- **Target User:** Fulfilment Centre Pick Operator & Line Supervisor.
- **Bounded Task:** Understand natural language exception queries, retrieve operational and SOP evidence, select safe verification actions, and trigger human review for high-risk requests.
- **Non-Goal:** PickGuard AI does NOT perform automated WMS inventory alterations or order cancellations.

---

## Slide 4 — System Solution Overview
- **Operator Interface:** React + Vite Operator Dashboard UI (`http://localhost:5173`).
- **REST API:** FastAPI Backend Server (`http://localhost:8000`).
- **Graph Workflow:** 13-Node LangGraph `StateGraph` with `MemorySaver` checkpointer.
- **Evidence Layers:** Deterministic Tools (SQLite), SOP RAG (ChromaDB), Historical Incident Search.

---

## Slide 5 — LangGraph Architecture & Nodes
- **State Schema:** `PickExceptionState` (29 typed fields).
- **Core Workflow Nodes:** `parse_operator_query` -> `classify_exception` -> `fetch_operational_evidence` -> `retrieve_sop_evidence` -> `retrieve_historical_evidence` -> `build_evidence_package` -> `reason_over_evidence` -> `fuse_evidence` -> `detect_evidence_conflicts` -> `select_next_best_action` -> `apply_safety_policy` -> `human_review_gate`.
- **Interrupt Mechanism:** Real LangGraph `interrupt()` checkpoint with `Command(resume=...)`.

---

## Slide 6 — Evidence Grounding & Provenance
- **Fact vs. Inference:** Observed operational facts (e.g. system balance: 10, physical count: 6) are strictly separated from LLM reasoning inferences.
- **Source Provenance:** Every recommendation lists explicit source tags (`Inventory Tool`, `Pick Task Tool`, `SOP-QTY-001`, `INC-0003`).
- **Evidence Gap Reporting:** Identifies missing data context and flags warnings.

---

## Slide 7 — Safety Policy & Action Boundary
- **Controlled Action Vocabulary:** Authorized recommendations (`CHECK_NEIGHBOURING_LOCATION`, `RECOUNT_QUANTITY`, `VERIFY_BARCODE`).
- **Disallowed Consequential Actions:** `UPDATE_INVENTORY`, `ADJUST_QUANTITY`, `CANCEL_ORDER` automatically `BLOCKED`.
- **Action Boundary:** Recommendation $\neq$ Execution. PickGuard AI outputs guidance; physical verification remains in human hands.

---

## Slide 8 — End-to-End Capstone Demo
- **Demo 1 (Normal):** Missing Item `X123` -> Low Risk -> `CHECK_NEIGHBOURING_LOCATION` -> Auto Completed.
- **Demo 2 (Edge):** Missing Item + Barcode Failure -> Multi-Signal Detection -> Safe Verification.
- **Demo 3 (High-Risk):** Quantity Mismatch + Update Inventory Request -> `BLOCKED` -> LangGraph `interrupt()` -> Human Rejection -> Resumed cleanly with `REJECTED_BY_HUMAN`.

---

## Slide 9 — Empirical Evaluation & Test Results
- **Automated Test Suite:** 93 passed in 9.08s across 36 test modules.
- **Frontend Build:** 100% clean TypeScript production bundle.
- **API Latency:** Tool latency 0.29 ms, RAG latency 1.15 s, End-to-end API latency 16.53 ms.

---

## Slide 10 — Reflection & Future Improvements
- **What We Would Build With 1 Additional Week:**
  1. Real WMS API integration with OAuth2 role-based authorization.
  2. Multilingual operator query support (Spanish, French, German).
  3. Advanced RAG re-ranking engine (Cohere Rerank / BGE-Reranker).
  4. Real-time WebSocket streaming for audit logs and supervisor review notifications.
