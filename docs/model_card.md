# PickGuard AI — Model Card & LLM Provider Specification

## Model Overview & Specification

- **Model Role:** Evidence-Grounded Reasoning Layer for Fulfilment Centre Pick Exceptions.
- **Primary Provider:** Groq Provider (`llama-3.3-70b-versatile` / `llama3-70b-8192`).
- **Secondary Provider:** Local Ollama Daemon (`llama3.2:latest` / `qwen2.5:latest` at `http://localhost:11434`).
- **Deterministic Fallback:** `MimicProvider` (Rule-based, offline deterministic fallback engine).

---

## Intended Use & Capabilities
- Synthesizes observed operational facts, retrieved SOP chunks, and historical incidents into a structured evidence package.
- Evaluates root causes and identifies candidate verification steps from a controlled action vocabulary.
- Generates natural language explanations ("Why this recommendation?") grounded strictly in evidence.

---

## Operational Boundaries & Limitations
1. **No Autonomous State Mutation:** The model NEVER performs direct SQL queries, WMS inventory alterations, or order cancellations.
2. **Dependence on Grounded Evidence:** Reasoning quality is directly dependent on the completeness of retrieved tool data and SOP chunks.
3. **No Physical World Sensing:** The LLM cannot observe bin contents or physical item conditions; it depends on operator queries and sensor barcodes.
4. **Synthetic Data Context:** Trained and evaluated strictly on synthetic educational warehouse datasets.

---

## Safety & Security Controls
- **Prompt Injection Defense:** Untrusted instructions embedded in operator queries are trapped by exception classification rules and flagged as `HIGH` risk.
- **Deterministic Safety Policy Override:** Candidate actions suggested by the LLM are evaluated by the python safety policy layer before execution. Disallowed actions are automatically `BLOCKED`.
