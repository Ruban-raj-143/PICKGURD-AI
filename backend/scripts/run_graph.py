"""CLI runner script for PickGuard AI evidence-generation, LLM reasoning, and safety policy LangGraph workflow."""

import json
import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.graph.workflow import build_pickguard_graph


def main():
    print("========================================")
    print("PickGuard AI — LangGraph Decision & Safety Policy Run")
    print("")

    query = "The item X123 is missing from A15-B04. The system says there are 3 units."
    print(f"Operator Query:\n\"{query}\"")
    print("")

    app = build_pickguard_graph()
    initial_state = {"operator_query": query}

    final_state = app.invoke(initial_state)

    print(f"Exception:\n{final_state.get('exception_type')}")
    print(f"Secondary Exceptions:\n{final_state.get('secondary_exception_types', [])}")
    print("")

    print("Provider Metadata:")
    print(f" - Provider: {final_state.get('provider')}")
    print(f" - Model Name: {final_state.get('model_name')}")
    print("")

    print("Evidence Fusion & Quality:")
    print(f" - Quality Rating: {final_state.get('evidence_quality')}")
    print(f" - Active Conflicts: {len(final_state.get('evidence_conflicts', []))}")
    print("")

    print("Source Provenance:")
    prov = final_state.get("provenance", {})
    for key, sources in prov.items():
        print(f" - {key.capitalize()}: {sources}")
    print("")

    print("Safety Policy & Next-Best Action:")
    print(f" - Action Type: {final_state.get('action_type')}")
    print(f" - Action Status: {final_state.get('action_status')}")
    print(f" - Next Best Action: {final_state.get('next_best_action')}")
    print(f" - Risk Level: {final_state.get('risk_level')}")
    print(f" - Requires Human Review: {final_state.get('requires_human_review')}")
    if final_state.get("review_reason"):
        print(f" - Review Reason: {final_state.get('review_reason')}")
    print(f" - Action Boundary Summary: {final_state.get('action_boundary')}")
    print("")

    print("Audit Log:")
    for log_entry in final_state.get("audit_log", []):
        print(f" -> {log_entry}")
    print("")

    print("Graph Status:")
    if final_state.get("next_best_action"):
        print("SUCCESS")
        sys.exit(0)
    else:
        print("FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
