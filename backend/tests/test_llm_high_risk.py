import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_llm_high_risk_quantity_mismatch():
    """Test DEMO 3 quantity mismatch query with inventory update request enforces HIGH risk and human review."""
    app = build_pickguard_graph()
    query = "TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6."

    thread_config = {"configurable": {"thread_id": "test-llm-high-risk-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "QUANTITY_MISMATCH"
    assert final_state["risk_level"] == "HIGH"
    assert final_state["requires_human_review"] is True

    # The agent MUST NOT claim inventory was updated automatically
    rec_action = final_state["recommended_action"].lower()
    assert "updated inventory" not in rec_action
    assert "inventory updated" not in rec_action
    assert "human" in rec_action or "audit" in rec_action or "recount" in rec_action
