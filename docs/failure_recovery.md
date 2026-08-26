# PickGuard AI — Failure Recovery & Edge Case Protocol

## Matrix of System Failure & Recovery Strategies

| Failure Mode | Detection Mechanism | System Recovery Strategy | Operator & Graph Impact |
| :--- | :--- | :--- | :--- |
| **Tool Failure / DB Error** | Exception caught in `fetch_operational_evidence` node function. | Appends error string to `state.errors` dictionary; continues workflow with available evidence. | Operational evidence marked incomplete; evidence quality reduced to `WEAK`. |
| **RAG Threshold Miss** | Retrieval similarity score below threshold (0.35). | Returns empty chunk list; appends warning to `evidence_summary.EVIDENCE_GAPS`. | SOP evidence omitted; relies on general safety rules and historical incidents. |
| **LLM Provider Offline** | `GroqProvider` / `OllamaProvider` ping fails or throws network timeout. | Triggers fallback router (`groq` -> `ollama` -> `MimicProvider`). | Seamless fallback to deterministic `MimicProvider`; workflow continues without crash. |
| **Malformed LLM Output** | Pydantic validation fails on LLM response. | Fallback parser extracts action or defaults to `COLLECT_MORE_EVIDENCE`. | Safe default recommendation selected; error logged in audit trail. |
| **Conflicting Evidence** | `detect_evidence_conflicts` node identifies quantity/location mismatch. | Flags conflict in state (`evidence_conflicts`); upgrades risk to `HIGH`. | Does not silently resolve conflict; forces `requires_human_review = True`. |
| **Human Rejection** | Supervisor submits `REJECT` via `Command(resume=...)`. | Graph resumes, updates `action_status = REJECTED_BY_HUMAN`. | Decision canceled; inventory state remains completely unchanged. |
| **Request More Evidence** | Supervisor submits `REQUEST_MORE_EVIDENCE`. | Routes to `collect_additional_evidence`, fetches expanded incident logs, re-evaluates. | Workflow loops back to evidence synthesis; review attempt counter incremented. |
| **Max Review Loop Limit** | `review_attempts >= MAX_REVIEW_ATTEMPTS` (2). | Automatically invokes `create_escalation()` tool; sets `action_status = ESCALATED`. | Prevents infinite review request loops; escalates to WMS supervisor queue. |
