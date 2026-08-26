import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_low_risk_no_interrupt():
    """Test that low-risk queries complete execution from START to END without interrupting."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-low-risk-001"}}
    query = "The item X123 is missing from A15-B04. The system says there are 3 units."

    final_state = app.invoke({"operator_query": query}, thread_config)

    # Graph should reach END without pausing
    snapshot = app.get_state(thread_config)
    assert snapshot.next == ()

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert final_state["next_best_action"] == "CHECK_NEIGHBOURING_LOCATION"
    assert final_state["risk_level"] == "LOW"
    assert final_state["requires_human_review"] is False
