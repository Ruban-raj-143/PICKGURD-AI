"""Script to measure empirical latency of API endpoints, tools, RAG retriever, and LangGraph workflow."""

import os
import sys
import time
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.tools.inventory import get_inventory
from backend.app.rag.retriever import sop_retriever
from backend.app.graph.workflow import build_pickguard_graph
from backend.app.api.router import run_agent, AgentRunRequest


def measure():
    print("========================================")
    print("PickGuard AI — Empirical Performance Measurement")
    print("========================================")

    # 1. Measure Tool Latency
    t0 = time.perf_counter()
    inv = get_inventory("X123", "A15-B04")
    t1 = time.perf_counter()
    tool_ms = (t1 - t0) * 1000.0
    print(f"Tool Latency (get_inventory): {tool_ms:.2f} ms")

    # 2. Measure RAG Retriever Latency
    t0 = time.perf_counter()
    res_rag = sop_retriever.search_sop(exception_type="MISSING_ITEM", query="item missing from bin")
    t1 = time.perf_counter()
    rag_ms = (t1 - t0) * 1000.0
    print(f"RAG Latency (ChromaDB query): {rag_ms:.2f} ms ({res_rag.get('total_chunks', 0)} chunks)")

    # 3. Measure Full LangGraph Workflow Latency (Mimic Provider)
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "perf-test-001"}}
    query = "The item X123 is missing from A15-B04."

    t0 = time.perf_counter()
    res = app.invoke({"operator_query": query}, thread_config)
    t1 = time.perf_counter()
    graph_ms = (t1 - t0) * 1000.0
    print(f"LangGraph Workflow Latency (End-to-End): {graph_ms:.2f} ms")

    # 4. Measure API Endpoint Latency (POST /api/v1/agent/run)
    req = AgentRunRequest(query="The item X123 is missing from A15-B04.", task_id="TASK-1001", item_id="X123", location_id="A15-B04")
    t0 = time.perf_counter()
    api_res = run_agent(req)
    t1 = time.perf_counter()
    api_ms = (t1 - t0) * 1000.0
    print(f"API Endpoint Latency (run_agent): {api_ms:.2f} ms")

    perf_data = {
        "tool_latency_ms": round(tool_ms, 2),
        "rag_latency_ms": round(rag_ms, 2),
        "graph_latency_ms": round(graph_ms, 2),
        "api_latency_ms": round(api_ms, 2),
    }

    with open("docs/perf_results.json", "w") as f:
        json.dump(perf_data, f, indent=2)

    print("\nSaved empirical measurements to docs/perf_results.json")


if __name__ == "__main__":
    measure()
