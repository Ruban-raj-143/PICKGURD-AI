import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_graph_end_to_end_integration():
    """End-to-end integration test verifying complete START to END graph execution."""
    app = build_pickguard_graph()
    query = "TASK-1003 has a quantity mismatch at A20-B02 for X125. System says 10 but physical count is 6."

    thread_config = {"configurable": {"thread_id": "test-integration-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    # Verify execution output fields
    assert final_state["exception_type"] == "QUANTITY_MISMATCH"
    assert final_state["task_id"] == "TASK-1003"
    assert final_state["item_id"] == "X125"
    assert final_state["location_id"] == "A20-B02"

    assert "operational_data" in final_state
    assert "sop_evidence" in final_state
    assert "historical_evidence" in final_state
    assert "evidence_summary" in final_state
    assert "audit_log" in final_state

    # Verify Audit Trail
    audit = final_state["audit_log"]
    assert any("Query parsed" in log for log in audit)
    assert any("Exception classified" in log for log in audit)
    assert any("Operational evidence fetched" in log for log in audit)
    assert any("SOP evidence" in log for log in audit)
    assert any("Historical evidence" in log for log in audit)
    assert any("Evidence package synthesized" in log for log in audit)

    # Provider metadata check
    assert final_state["provider"] in ["mimic", "groq", "ollama"]
    assert final_state["model_name"] in ["deterministic-mimic", "llama3", "llama-3.3-70b-versatile"]
