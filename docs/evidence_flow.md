# PickGuard AI — Evidence Flow & Separation of Responsibilities

## Architectural Responsibilities Summary

```
Operator Query
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ 1. FACT & EVIDENCE RETRIEVAL LAYER (Deterministic Tools & RAG) │
│ • Operational Facts: SQLite database via Python tools  │
│ • SOP Procedures: ChromaDB vector store embeddings     │
│ • Historical Incidents: Prior resolution logs          │
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ 2. REASONING LAYER (LLM Provider)                      │
│ • Synthesizes evidence package                         │
│ • Identifies root cause and infers candidate actions   │
│ • DOES NOT invent warehouse facts or modify state      │
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ 3. DETERMINISTIC SAFETY CONTROL LAYER (Action Policy)   │
│ • Evaluates candidate action against risk rules        │
│ • Automatically BLOCKS state-altering modifications    │
│ • Enforces action boundary (RECOMMENDED vs BLOCKED)    │
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ 4. HUMAN ACCOUNTABILITY LAYER (LangGraph interrupt)    │
│ • Pauses execution for high-risk decisions             │
│ • Exposes secret-free structured evidence payload      │
│ • Supervisor approves/rejects via Command(resume=...)  │
└────────────────────────────────────────────────────────┘
      │
      ▼
Final Recommended Action (Zero Automated WMS Mutation)
```

### Key Principles
- **LLM = Reasoning Layer:** Interprets collected evidence; never source of warehouse truth.
- **Tools & RAG = Verified Operational Facts:** Retrieves verified inventory, location, and procedure data.
- **Safety Policy = Deterministic Control:** Authoritative boundary blocking dangerous state changes.
- **Human = Accountability:** Authorizes physical verification steps for high-risk exceptions.
