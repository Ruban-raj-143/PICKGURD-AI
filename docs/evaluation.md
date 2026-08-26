# PickGuard AI — Test Evaluation Matrix

This document reports empirical test execution results derived directly from pytest runs across 9 core test categories.

| Test Category | Expected Result | Actual Result | Pass? | Notes & Improvements |
| :--- | :--- | :--- | :---: | :--- |
| **Normal Case** | Safe recommendation (`CHECK_NEIGHBOURING_LOCATION`), `LOW` risk, no human interrupt. | `exception_type = MISSING_ITEM`, `risk_level = LOW`, `next_best_action = CHECK_NEIGHBOURING_LOCATION`, `status = COMPLETED`. | **YES** | Passes `test_graph_normal.py` and `test_capstone_cases.py`. |
| **Edge Case** | Multi-signal detection (`MISSING_ITEM` + `BARCODE_FAILURE`), safe verification action. | `primary = MISSING_ITEM`, `secondary = ['BARCODE_FAILURE']`, `next_best_action = CHECK_NEIGHBOURING_LOCATION`. | **YES** | Passes `test_graph_edge.py` and `test_capstone_cases.py`. |
| **Failure / High-Risk Case** | Action `BLOCKED`, `HIGH` risk, LangGraph `interrupt()` pause, human review payload. | `action_status = BLOCKED`, `risk_level = HIGH`, `requires_human_review = True`, status `WAITING_FOR_HUMAN_REVIEW`. | **YES** | Passes `test_safety_override.py`, `test_interrupt.py`, and `test_capstone_cases.py`. |
| **Unknown Exception** | No forced classification, fallback to `UNKNOWN`, skip category SOP, execute historical search. | `exception_type = UNKNOWN`, `secondary = []`, historical incidents searched. | **YES** | Passes `test_graph_unknown.py`. |
| **Missing Operational Data** | No hallucinated items/locations, error recorded in state, safe fallback recommendation. | `item_id = X9999`, error recorded in `state.errors`, safe fallback recommendation. | **YES** | Passes `test_graph_missing_data.py`. |
| **Prompt Injection Attack** | Untrusted instructions ignored, classified as `HIGH` risk, action blocked. | Prompt injection attempt trapped, `risk_level = HIGH`, `requires_human_review = True`. | **YES** | Passes `test_prompt_injection.py`. |
| **LLM Provider Failure** | Multi-tier provider fallback (`groq` -> `ollama` -> `mimic`), safe response generated. | Provider fallback triggers `MimicProvider`, completing reasoning deterministically. | **YES** | Passes `test_provider.py`. |
| **Human Rejection** | Resume via `Command(resume=...)`, set `REJECTED_BY_HUMAN`, zero state mutation. | Graph resumes, `action_status = REJECTED_BY_HUMAN`, audit trail updated, inventory unchanged. | **YES** | Passes `test_human_reject.py`. |
| **More Evidence Request** | Re-route to `collect_additional_evidence`, increment attempt count, re-evaluate. | Graph routes to evidence collector, `review_attempts` incremented, state re-evaluated. | **YES** | Passes `test_more_evidence.py`. |

---

## Pytest Suite Summary Statistics
- **Total Tests Executed:** 93
- **Passed:** 93
- **Failed:** 0
- **Execution Time:** 9.08s
