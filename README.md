# PickGuard AI — Evidence-Grounded Pick Exception Resolution Agent

> **Capstone Project:** Evidence-Grounded AI Agent for Fulfilment Centre Pick Exception Resolution.

> [!NOTE]
> **Disclaimer:** All datasets, SOPs, bin locations, SKUs, and historical incidents in this project are strictly synthetic educational/demo data and do not represent Amazon internal systems, processes, inventory, or operational records.

---

## 1. Project Overview & Problem Statement

In high-volume e-commerce fulfilment centres, pick operators frequently encounter picking exceptions:
- Missing items from storage bins
- Physical vs system quantity mismatches
- Unreadable or damaged barcode labels
- Wrong SKUs stored in designated bin slots
- Physical product or packaging damage
- Location mapping discrepancies

**PickGuard AI** provides an evidence-grounded decision support agent built on **LangGraph**, **LangChain**, **FastAPI**, and **React**. The system grounds every recommendation in verified operational facts and Standard Operating Procedures (SOPs), enforcing a strict **Deterministic Safety Policy** and **Human-in-the-Loop `interrupt()` checkpoint** for high-risk decisions.

---

## 2. Key Architectural Principles

1. **Deterministic Operational Fact Layer:** The LLM does NOT retrieve raw facts. verified operational data is retrieved via deterministic Python tools (`get_inventory`, `get_pick_task`, `get_location`, `search_similar_incidents`).
2. **SOP RAG Retrieval:** Standard Operating Procedures are retrieved from ChromaDB vector store (`all-MiniLM-L6-v2`) with complete source provenance metadata.
3. **Controlled Provider Abstraction:** Multi-level fallback hierarchy (`Groq` -> `Ollama` -> `MimicProvider`).
4. **Deterministic Safety Policy & Action Boundary:** Safety risk classification (`LOW`, `MEDIUM`, `HIGH`) and execution boundaries (`RECOMMENDED` vs `BLOCKED`) are governed by deterministic rules. State-altering warehouse modifications (e.g. `UPDATE_INVENTORY`, `ADJUST_QUANTITY`) are automatically `BLOCKED`.
5. **Real LangGraph `interrupt()` Checkpoint:** High-risk decisions pause graph execution via LangGraph `interrupt()`, saving state with `MemorySaver` checkpointer and `thread_id`. Resumption occurs via `Command(resume=...)`.

---

## 3. Technology Stack

- **Backend:** Python 3.12, FastAPI, LangGraph, LangChain, Pydantic, SQLite, ChromaDB, HuggingFace Transformers
- **Frontend:** React 18, Vite, TypeScript, Lucide Icons, Vanilla CSS Design System
- **Testing:** Pytest (93 automated unit, contract, safety, API, and E2E tests passing)

---

## 4. How to Run the Application

### Environment Setup
Ensure the Python 3.12 virtual environment is activated:
```bash
source .venv/bin/activate
```

### 1. Run Backend Tests
Execute the full pytest suite:
```bash
.venv/bin/python -m pytest backend/tests
```

### 2. Start FastAPI Backend Server
Launch the backend server on port 8000:
```bash
.venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 3. Start React Operator Dashboard UI
In a separate terminal tab:
```bash
cd frontend
npm install
npm run dev
```
- Operator Dashboard UI: `http://localhost:5173`

---

## 5. End-to-End Capstone Demo Scenarios

The Operator UI includes 3 preset demo scenario buttons:
- **Demo 1 (Normal):** Missing item `X123` at `A15-B04`. Low risk recommendation (`CHECK_NEIGHBOURING_LOCATION`), completes automatically without human interrupt.
- **Demo 2 (Edge):** Missing item + unreadable barcode label at `A12-B03`. Multi-signal exception classification and safe verification recommendation.
- **Demo 3 (High Risk):** Quantity mismatch + inventory update request (`"System says 10 but I counted 6. Update inventory to 6."`). Triggers safety policy block (`ADJUST_QUANTITY` `BLOCKED`), pauses execution at real LangGraph `interrupt()` checkpoint, presents Human Review modal, and resumes upon supervisor approval/rejection without modifying inventory.
