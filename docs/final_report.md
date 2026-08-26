# PickGuard AI — Capstone Final Project Report

> **Capstone Project:** Evidence-Grounded Pick Exception Resolution Agent for Fulfilment Centre Operations.
> **Disclaimer:** All data, SOP documents, bin locations, SKUs, and historical incidents are synthetic demo/educational data.

---

## 1. Executive Summary
PickGuard AI is an evidence-grounded AI decision support agent designed for fulfilment centre pick operators encountering operational picking exceptions. Built using **LangGraph**, **FastAPI**, **React**, and **ChromaDB**, the system decouples factual operational data retrieval from LLM reasoning. High-risk exception handling is governed by a deterministic safety policy and native LangGraph `interrupt()` checkpointing, guaranteeing zero autonomous warehouse state mutations.

---

## 2. Problem Statement
Pick operators process high pick volumes per hour. When exceptions occur (missing items, quantity discrepancies, unreadable barcodes, damaged packaging), operators face uncertainty. Transactional WMS tools display balances but offer no exception resolution guidance, resulting in unguided decisions, order delays, and inventory inaccuracies.

---

## 3. User
- **Primary User:** Fulfilment Centre Pick Operator.
- **Secondary User:** Line Supervisor / Operations Lead.

---

## 4. Bounded Task
Understand natural language exception descriptions, classify exception categories across 6 supported types (`MISSING_ITEM`, `QUANTITY_MISMATCH`, `WRONG_ITEM`, `BARCODE_FAILURE`, `DAMAGED_ITEM`, `LOCATION_DISCREPANCY`), retrieve operational facts, query SOP procedures, synthesize evidence, and select safe verification recommendations without performing automated WMS state modifications.

---

## 5. System Architecture
Decoupled multi-layer architecture comprising:
- **Frontend Layer:** React 18 + Vite + TypeScript Operator Dashboard.
- **API Layer:** FastAPI REST API service (`/api/v1/agent/run`, `/review`, `/audit`, `/system/status`).
- **Orchestration Layer:** 13-node LangGraph `StateGraph` with `MemorySaver` checkpointer.
- **Data Layer:** Synthetic SQLite database and ChromaDB vector store.

---

## 6. LangGraph Design
State-driven workflow utilizing `PickExceptionState` (29 typed fields). Graph nodes execute linear entity parsing, exception classification, tool fetches, SOP RAG, historical search, reasoning, evidence fusion, conflict detection, action selection, safety evaluation, and human review checkpointing (`human_review_gate`).

---

## 7. Tools
Purposeful, deterministic Python tools:
- `get_inventory(item_id, location_id)`
- `get_pick_task(task_id)`
- `get_location(location_id)`
- `search_similar_incidents(item_id, location_id, exception_type)`
- `create_escalation(task_id, reason)`

---

## 8. RAG
SOP knowledge base stored in ChromaDB vector database using `all-MiniLM-L6-v2` embeddings. Applies score thresholding (0.35) and attaches source provenance metadata tags (`SOP-MISSING-001`, `SOP-QTY-001`).

---

## 9. LLM
LLM reasoning layer supporting multi-provider fallback (`Groq` -> `Ollama` -> `MimicProvider`). The LLM operates strictly as a reasoning engine over pre-fetched evidence packages.

---

## 10. Evidence Grounding
Enforces strict separation between observed facts (verified database records) and inferences (LLM deductions). Outlines identified evidence gaps and warnings in the output payload.

---

## 11. Safety Policy
Deterministic safety policy layer evaluating risk levels (`LOW`, `MEDIUM`, `HIGH`). Automatically `BLOCKS` state-altering actions (`UPDATE_INVENTORY`, `ADJUST_QUANTITY`, `CANCEL_ORDER`) and enforces the Action Boundary statement (Recommendation $\neq$ Execution).

---

## 12. Human-in-the-Loop
Native LangGraph `interrupt()` checkpointing triggered when `requires_human_review == True`. Saves snapshot under `thread_id` using `MemorySaver` checkpointer. Resumes via `Command(resume=payload)` supporting supervisor decisions (`APPROVE`, `REJECT`, `REQUEST_MORE_EVIDENCE`, `ESCALATE`).

---

## 13. Failure Recovery
Comprehensive edge case protocol managing tool failures, RAG threshold misses, provider outages (fallback engine), malformed JSON responses, prompt injections, human rejections, and max review loop limits (`MAX_REVIEW_ATTEMPTS = 2`).

---

## 14. Evaluation
Tested against 93 automated pytest unit, integration, API, safety, prompt injection, and end-to-end integration tests with 100% pass rate.

---

## 15. Responsible AI
Enforces action boundary policies, zero autonomous WMS state changes, secret-free payloads, full audit logging, reviewer accountability, and prompt injection defense.

---

## 16. Limitations
Evaluated on synthetic educational datasets; depends on clarity of natural language inputs; cannot physically inspect physical storage bins.

---

## 17. Future Work
Integration with live WMS REST APIs, multilingual query processing, Cohere RAG re-ranking, and real-time WebSocket supervisor alert streaming.

---

## 18. Conclusion
PickGuard AI demonstrates that agentic AI systems in warehouse operations can be grounded, safe, transparent, and accountable when built on LangGraph stateful orchestration, deterministic tools, and human-in-the-loop safety boundaries.
