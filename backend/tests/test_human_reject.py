import pytest
from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def test_human_rejection_flow():
    """Test that human REJECT decision sets action_status to REJECTED_BY_HUMAN."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-reject-001"}}
    query = "TASK-1003 quantity mismatch: System says 10 units but I counted 6. Update inventory to 6."

    app.invoke({"operator_query": query}, thread_config)

    decision_payload = {"decision": "REJECT", "reviewer_id": "SUPERVISOR-007", "reviewer_note": "Reject action."}
    final_state = app.invoke(Command(resume=decision_payload), thread_config)

    assert final_state["human_decision"] == "REJECT"
    assert final_state["action_status"] == "REJECTED_BY_HUMAN"
    assert final_state["requires_human_review"] is False
    assert "REJECTED" in final_state["final_decision"]
