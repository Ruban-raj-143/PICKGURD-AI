# PickGuard AI — System Architecture

## Overview
**PickGuard AI** is an Evidence-Grounded Pick Exception Resolution Agent designed for fulfilment centre pick operators.

> [!NOTE]
> **Phase 9 Status:** Phase 1 (Core App), Phase 2 (Datasets), Phase 3 (Tools), Phase 4 (SOP RAG), Phase 5 (StateGraph), Phase 6 (LLM Reasoning), Phase 7 (Evidence Fusion), Phase 8 (Human-in-the-Loop `interrupt()`), and Phase 9 (FastAPI REST API + React Operator UI) are fully implemented. Final evaluation belongs to Phase 10.

---

## End-to-End System Architecture

```
React Operator UI (http://localhost:5173)
         │
         ▼ (HTTP / REST API)
FastAPI Backend (http://localhost:8000/api/v1/)
         │
         ▼
LangGraph Compiled StateGraph (13 Nodes + MemorySaver Checkpointer)
         │
         ├──► 1. parse_operator_query (Regex entity parsing)
         ├──► 2. classify_exception (Keyword rules classifier)
         ├──► 3. fetch_operational_evidence (Phase 3 Tools: get_inventory, get_pick_task, get_location)
         ├──► 4. retrieve_sop_evidence (Phase 4 ChromaDB Vector RAG)
         ├──► 5. retrieve_historical_evidence (Phase 3 search_similar_incidents Tool)
         ├──► 6. build_evidence_package (Observed facts, SOP chunks, Historical logs synthesis)
         ├──► 7. reason_over_evidence (LLM Provider: Groq / Ollama / MimicProvider)
         ├──► 8. fuse_evidence (Quality scoring: STRONG, MODERATE, WEAK, INSUFFICIENT)
         ├──► 9. detect_evidence_conflicts (Quantity, Location, SKU discrepancy detection)
         ├──► 10. select_next_best_action (Action vocabulary selection)
         ├──► 11. apply_safety_policy (Deterministic safety rules & action boundary enforcement)
         ├──► 12. human_review_gate (LangGraph interrupt() checkpoint when requires_human_review == True)
         └──► 13. collect_additional_evidence (Re-query loop upon supervisor evidence request)
```

---

## API Layer & Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Basic system health check. |
| `GET` | `/api/v1/system/status` | Component health metrics (API, LangGraph, RAG, LLM provider, tools). |
| `POST` | `/api/v1/agent/run` | Initiates exception resolution workflow; returns `run_id`, `thread_id`, and status. |
| `GET` | `/api/v1/agent/{run_id}` | Fetches current run status, evidence package, recommendation, and review state. |
| `POST` | `/api/v1/agent/{run_id}/review` | Submits supervisor decision (`APPROVE`, `REJECT`, `REQUEST_MORE_EVIDENCE`, `ESCALATE`) via `Command(resume=...)`. |
| `GET` | `/api/v1/agent/{run_id}/audit` | Returns complete timestamped audit log. |

---

## Action Boundary & Safety Policy

- **Allowed Recommendations (`RECOMMENDED`):** `CHECK_LOCATION`, `CHECK_NEIGHBOURING_LOCATION`, `RE_SCAN_ITEM`, `VERIFY_ITEM_IDENTITY`, `RECOUNT_QUANTITY`, `VERIFY_BARCODE`, `REVIEW_RECENT_MOVEMENT`, `REVIEW_SOP`, `COLLECT_MORE_EVIDENCE`, `ESCALATE_TO_HUMAN`, `NO_ACTION`.
- **Disallowed Consequential Actions (`BLOCKED`):** `UPDATE_INVENTORY`, `CHANGE_LOCATION`, `CANCEL_ORDER`, `MODIFY_ORDER`, `ADJUST_QUANTITY`, `DELETE_RECORD`, `MARK_ITEM_DAMAGED`.
- **Recommendation $\neq$ Execution:** System outputs decision recommendations for pick operator guidance; automated WMS state mutations are strictly prohibited.
