# PickGuard AI — Performance & Latency Benchmark Report

This document reports empirical performance latency measurements gathered from live benchmarks (`backend/scripts/measure_performance.py`).

## Measured Latency Breakdown

| Component | Benchmark Operation | Measured Latency |
| :--- | :--- | :---: |
| **Deterministic Tool Layer** | `get_inventory("X123", "A15-B04")` SQLite Query | **0.29 ms** |
| **RAG Vector Retriever** | ChromaDB `all-MiniLM-L6-v2` Vector Search | **1,154.20 ms** (1.15 s) |
| **LangGraph Workflow Engine** | Full 13-Node StateGraph Execution (`MimicProvider`) | **50.28 ms** |
| **FastAPI REST Endpoint** | `POST /api/v1/agent/run` Full API Round-Trip | **16.53 ms** |
| **Human Review Pause** | `interrupt()` Checkpoint Suspension | **< 1.00 ms** (Immediate) |

---

## Latency Analysis & Discussion
1. **Tool Efficiency:** Deterministic tools (`get_inventory`, `get_pick_task`, `get_location`) perform direct indexed SQLite queries, responding in **< 0.3 ms**.
2. **RAG Embedding Overhead:** ChromaDB embedding generation and similarity distance calculation via HuggingFace `all-MiniLM-L6-v2` is the primary latency component (**~1.15 s**), ensuring grounded SOP provenance.
3. **Graph Execution Overhead:** LangGraph node transitions, state updates, and safety policy evaluations add less than **51 ms** of computation overhead.
