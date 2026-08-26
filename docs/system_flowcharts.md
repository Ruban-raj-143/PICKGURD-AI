# PickGuard AI - Comprehensive System Flowcharts & Diagrams

This document provides visual diagrams and flowcharts explaining the end-to-end architecture, LangGraph execution graph, LLM fallback routing, and Human-in-the-Loop (HITL) safety workflows for PickGuard AI.

---

## 1. End-to-End System Architecture

This flowchart outlines the macro-architecture: from the operator frontend to the FastAPI router, LangGraph agent orchestration, RAG knowledge stores, multi-tier LLM providers, and operational databases.

```mermaid
flowchart TD
    subgraph Client ["Client Layer"]
        User(["👷 Warehouse Operator / Supervisor"])
        UI["💻 React + Vite Frontend Dashboard"]
    end

    subgraph API ["Backend API Layer (FastAPI)"]
        Router["REST Endpoints\n/api/v1/agent/run\n/api/v1/agent/review\n/api/v1/agent/audit"]
        Checkpointer[("MemorySaver Checkpointer\n(Thread ID & State Snapshot)")]
    end

    subgraph Graph ["LangGraph Agent Engine"]
        LG["13-Node StateGraph Workflow\n(Evidence Synthesis & Policy Evaluation)"]
    end

    subgraph Providers ["Multi-Tier LLM Provider Factory"]
        Groq["Tier 1: Groq Cloud API\n(openai/gpt-oss-120b)"]
        Ollama["Tier 2: Local Ollama\n(llama3)"]
        Mimic["Tier 3: Deterministic\nMimic Fallback"]
    end

    subgraph Data ["Data & RAG Retrieval Layer"]
        DB[("SQLite Database\n(Tasks, Inventory, Incidents)")]
        VectorStore[("ChromaDB Vector Store\n(SOP Rules & HuggingFace Embeddings)")]
    end

    User -->|Inputs Query or Scans Barcode| UI
    UI -->|HTTP POST Request| Router
    Router -->|Initialize & Resume Session| Checkpointer
    Router --> LG
    LG <-->|Structured JSON Reasoning| Providers
    LG <-->|Query Operational Facts| DB
    LG <-->|Semantic SOP Retrieval| VectorStore
    Providers -.->|Fallback on error / rate limit| Ollama
    Ollama -.->|Fallback on offline daemon| Mimic
    LG -->|Audit Logs & Next-Best Action| Router
    Router -->|JSON Response| UI
    UI -->|Render Root Cause & Resolution| User
```

---

## 2. LangGraph 13-Node StateGraph Workflow

This diagram represents the step-by-step execution path of the compiled `StateGraph(PickExceptionState)` located in `backend/app/graph/workflow.py`.

```mermaid
flowchart TD
    START(["▶ START"]) --> N1["1. parse_operator_query\n(Extract TASK, SKU, Bin IDs)"]
    N1 --> N2["2. classify_exception\n(MISSING_ITEM, QUANTITY_MISMATCH, etc.)"]
    N2 --> N3["3. fetch_operational_evidence\n(Query DB for Task & Inventory Records)"]

    N3 --> C1{"Route After\nClassification"}

    %% Conditional Branches
    C1 -->|Standard Exception| N4["4. retrieve_sop_evidence\n(ChromaDB Semantic Search)"]
    C1 -->|Historical Incident| N5["5. retrieve_historical_evidence\n(Query Past Resolutions)"]
    C1 -->|Missing Data / Unknown| N13["13. collect_additional_evidence\n(Request Recount / Photo Scan)"]

    N4 --> N6["6. build_evidence_package\n(Synthesize Facts, SOPs, Gaps)"]
    N5 --> N6
    N13 --> N6

    N6 --> N7["7. reason_over_evidence\n(LLM Structured AgentOutput)"]
    N7 --> N8["8. fuse_evidence\n(Merge Facts with LLM Inferences)"]
    N8 --> N9["9. detect_evidence_conflicts\n(Cross-Check Bin vs System Counts)"]
    N9 --> N10["10. select_next_best_action\n(Pick Action: RECOUNT, ESCALATE, etc.)"]
    N10 --> N11["11. apply_safety_policy\n(Deterministic ActionBoundary Checks)"]

    N11 --> C2{"Requires Human\nReview?"}

    C2 -->|Yes (High Risk / Policy Violation)| N12["12. human_review_gate\n(LangGraph interrupt() & HITL)"]
    C2 -->|No (Safe & High Confidence)| END_NODE(["⏹ END (Execution Complete)"])

    N12 --> C3{"Supervisor\nDecision"}
    C3 -->|APPROVE / MODIFY| END_NODE
    C3 -->|COLLECT_MORE_DATA| N13
    C3 -->|REJECT / ABORT| END_NODE
```

---

## 3. Multi-Tier LLM Provider & Automatic Failover Logic

The LLM provider factory (`backend/app/services/llm.py`) guarantees 100% uptime with graceful degradation across cloud, local edge, and deterministic fallbacks.

```mermaid
flowchart TD
    Req(["Invoke LLM Reasoning"]) --> CheckGroq{"GROQ_API_KEY\nConfigured & Valid?"}

    CheckGroq -->|Yes| TryGroq["Attempt Groq Cloud API\n(Model: openai/gpt-oss-120b)"]
    CheckGroq -->|No| CheckOllama

    TryGroq --> GroqSuccess{"Groq Response\nSuccess?"}
    GroqSuccess -->|Yes| ReturnGroq["✅ Return Groq AgentOutput\n(Real-time Cloud Reasoning)"]
    GroqSuccess -->|No / Rate Limit| CheckOllama{"Local Ollama\nService Active? (Port 11434)"}

    CheckOllama -->|Yes| TryOllama["Attempt Local Ollama\n(Model: llama3)"]
    CheckOllama -->|No| UseMimic

    TryOllama --> OllamaSuccess{"Ollama Response\nSuccess?"}
    OllamaSuccess -->|Yes| ReturnOllama["✅ Return Ollama AgentOutput\n(Local Edge Reasoning)"]
    OllamaSuccess -->|No| UseMimic["Fallback to MimicProvider\n(Deterministic Rule-Based Reasoning)"]

    UseMimic --> ReturnMimic["⚠️ Return Safe Fallback AgentOutput\n(Confidence: 0.0, Flags Supervisor Review)"]
```

---

## 4. Human-in-the-Loop (HITL) Interrupt & Resume Lifecycle

Demonstrates how risky actions are halted using LangGraph checkpoint interrupts and safely resumed by warehouse supervisors.

```mermaid
sequenceDiagram
    autonumber
    actor Operator as 👷 Picker Operator
    participant API as 🚀 FastAPI Server
    participant Graph as 🧠 LangGraph StateGraph
    participant Checkpoint as 💾 MemorySaver Checkpointer
    actor Supervisor as 🧑‍💼 Warehouse Supervisor

    Operator->>API: POST /api/v1/agent/run (Query: Quantity mismatch at bin)
    API->>Graph: invoke(initial_state, thread_id)
    Graph->>Graph: Evidence Synthesis & Reasoning
    Graph->>Graph: Evaluate Safety Policy (Risk = HIGH)
    Note over Graph: Safety Policy violation triggers human_review_gate
    Graph->>Checkpoint: Persist State Snapshot & Call interrupt()
    Graph-->>API: Yield Run Status: WAITING_FOR_HUMAN_REVIEW
    API-->>Operator: 201 Created (run_id, requires_human_review: true)

    Supervisor->>API: GET /api/v1/agent/status/{run_id}
    API-->>Supervisor: Review Payload (Observed Facts, Recommended Action, Risk Factors)

    Supervisor->>API: POST /api/v1/agent/review (Decision: APPROVE, notes: "Recount confirmed")
    API->>Graph: Command(resume={"decision": "APPROVE"}) with thread_id
    Graph->>Checkpoint: Restore Snapshot & Resume after human_review_gate
    Graph->>Graph: Finalize Action & Append Audit Trail
    Graph-->>API: Execution Finished (status: COMPLETED)
    API-->>Supervisor: 200 OK (Action Executed & Logged)
```

---

## 5. Safety Policy & Action Boundary Enforcement

How deterministic warehouse safety rules prevent unauthorized inventory adjustments or invalid picks before any action is approved.

```mermaid
flowchart TD
    ActionIn(["Generated Action Proposal\nfrom reason_over_evidence"]) --> CheckBoundary{"Is Action within\nAutonomous Boundary?"}

    CheckBoundary -->|AUTO_CONFIRM_PICK / SAFE_REROUTE| CheckConfidence{"LLM Confidence\n>= 0.70 Threshold?"}
    CheckBoundary -->|FORCE_ADJUST_STOCK / OVERRIDE_SAFETY| TriggerViolation["❌ Boundary Violation:\nUnauthorized Action"]

    CheckConfidence -->|Yes (High Confidence)| CheckConflicts{"Evidence Conflicts\nDetected?"}
    CheckConfidence -->|No (Low Confidence)| FlagReview["⚠️ Flag for Supervisor Review"]

    CheckConflicts -->|None Detected| ApproveAction["✅ Action Approved\n(Status: EXECUTED)"]
    CheckConflicts -->|Conflicting Facts| FlagReview

    TriggerViolation --> SetHighRisk["Set Risk Level = HIGH\nrequires_human_review = True"]
    FlagReview --> SetHighRisk
    SetHighRisk --> RouteToGate["Route to human_review_gate"]
```

---

## 6. RAG Retrieval & Grounding Data Flow

Shows how standard operating procedures (SOPs) and historical warehouse incidents are retrieved via vector search to ground agent decisions in verified facts.

```mermaid
flowchart LR
    subgraph Ingestion ["Knowledge Ingestion"]
        SOP_Files["📄 SOP Markdown Docs\n(SOP-MIS-001, SOP-QTY-001, etc.)"]
        Chunker["Text Splitter / Chunker"]
        Embedder["HuggingFace Embeddings\n(all-MiniLM-L6-v2)"]
        ChromaStore[("ChromaDB Vector Store\n(data/chroma/)")]
        
        SOP_Files --> Chunker --> Embedder --> ChromaStore
    end

    subgraph QueryFlow ["Runtime Retrieval & Grounding"]
        ExcType["Classified Exception\n& Extracted Entities"]
        Retriever["Vector Similarity Search\n(Threshold: 0.40)"]
        EvidenceSummary["Synthesized Evidence Package\n(OBSERVED_FACTS + SOP_EVIDENCE)"]
        
        ExcType --> Retriever
        ChromaStore --> Retriever
        Retriever --> EvidenceSummary
    end
```
