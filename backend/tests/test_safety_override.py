import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_safety_override_inventory_update_attempt():
    """Test safety policy overrides inventory update requests to BLOCKED and forces human review."""
    app = build_pickguard_graph()
    query = "System says 10 units but I counted 6. Update inventory to 6 immediately."

    thread_config = {"configurable": {"thread_id": "test-safety-override-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["action_status"] == "BLOCKED" or final_state["requires_human_review"] is True
    assert final_state["risk_level"] == "HIGH"
    assert final_state["requires_human_review"] is True
    assert final_state["next_best_action"] in ["RECOUNT_QUANTITY", "ESCALATE_TO_HUMAN"]
