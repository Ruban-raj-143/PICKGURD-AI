import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_graph_unknown_case():
    """Test query with unknown exception type routes safely without crash or forced SOP."""
    app = build_pickguard_graph()
    query = "I need help with something unusual."

    thread_config = {"configurable": {"thread_id": "test-unknown-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "UNKNOWN"
    assert final_state["secondary_exception_types"] == []

    # Category SOP retrieval should be bypassed
    assert final_state.get("sop_evidence", []) == []

    # Evidence gaps should record UNKNOWN classification
    assert "evidence_summary" in final_state
    pkg = final_state["evidence_summary"]
    assert any("UNKNOWN" in gap for gap in pkg.get("EVIDENCE_GAPS", []))

    # Graph completes safely
    assert len(final_state["audit_log"]) >= 4
