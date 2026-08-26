# PickGuard AI — Final System Architecture

## End-to-End Control & Evidence Flow

```
                                      OPERATOR
                                         │
                                         ▼
                            React Operator Dashboard UI
                               (http://localhost:5173)
                                         │
                                         ▼ (HTTP REST API)
                             FastAPI Backend Service
                               (http://localhost:8000)
                                         │
                                         ▼
                         LangGraph Compiled StateGraph
                           (MemorySaver Checkpointer)
                                         │
    ┌────────────────────────────────────┴────────────────────────────────────┐
    │                                                                         │
    ▼                                                                         ▼
1. parse_operator_query                                             13. collect_additional_evidence
    │                                                                         ▲
    ▼                                                                         │
2. classify_exception                                                         │
    │                                                                         │
    ▼                                                                         │
3. fetch_operational_evidence (Tools)                                         │
    │                                                                         │
    ├──► 4. retrieve_sop_evidence (RAG)                                       │
    │                                                                         │
    ▼                                                                         │
5. retrieve_historical_evidence (Incidents Tool)                             │
    │                                                                         │
    ▼                                                                         │
6. build_evidence_package                                                     │
    │                                                                         │
    ▼                                                                         │
7. reason_over_evidence (LLM)                                                 │
    │                                                                         │
    ▼                                                                         │
8. fuse_evidence & 9. detect_evidence_conflicts                               │
    │                                                                         │
    ▼                                                                         │
10. select_next_best_action & 11. apply_safety_policy                         │
    │                                                                         │
    ▼                                                                         │
12. human_review_gate                                                         │
    │                                                                         │
    ├────────────────────────────────────┬────────────────────────────────────┤
    │ (requires_human_review == False)   │ (requires_human_review == True)    │
    ▼                                    ▼                                    │
   END                         interrupt() Checkpoint Paused                  │
                                         │                                    │
                                Command(resume=payload)                       │
                                         │                                    │
                  ┌──────────────────────┼──────────────────────┐             │
                  ▼                      ▼                      ▼             │
               APPROVE                REJECT                 ESCALATE  REQUEST_MORE_EVIDENCE
                  │                      │                      │             │
                  ▼                      ▼                      ▼             └─────────┘
  HUMAN_APPROVED_PENDING_EXECUTION  REJECTED_BY_HUMAN       ESCALATED
                  │                      │                      │
                  └──────────────────────┼──────────────────────┘
                                         ▼
                                      END Log
```
