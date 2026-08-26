import pytest
from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def test_human_approval_flow():
    """Test that human APPROVE decision sets action_status to HUMAN_APPROVED_PENDING_EXECUTION without modifying WMS."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-approve-001"}}
    query = "TASK-1003 quantity mismatch: System says 10 units but I counted 6. Update inventory to 6."

    app.invoke({"operator_query": query}, thread_config)

    decision_payload = {"decision": "APPROVE", "reviewer_id": "SUPERVISOR-007", "reviewer_note": "Approved recount recommendation."}
    final_state = app.invoke(Command(resume=decision_payload), thread_config)

    assert final_state["human_decision"] == "APPROVE"
    assert final_state["action_status"] == "HUMAN_APPROVED_PENDING_EXECUTION"
    assert final_state["requires_human_review"] is False
    assert "APPROVED" in final_state["final_decision"]
