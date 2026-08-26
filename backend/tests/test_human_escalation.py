import pytest
from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def test_human_escalation_flow():
    """Test that human ESCALATE decision invokes Phase 3 escalation tool and persists escalation_id."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-escalate-001"}}
    query = "TASK-1003 quantity mismatch: System says 10 units but I counted 6. Update inventory to 6."

    app.invoke({"operator_query": query}, thread_config)

    decision_payload = {"decision": "ESCALATE", "reviewer_id": "SUPERVISOR-007", "reviewer_note": "Escalating to warehouse operations lead."}
    final_state = app.invoke(Command(resume=decision_payload), thread_config)

    assert final_state["human_decision"] == "ESCALATE"
    assert final_state["action_status"] == "ESCALATED"
    assert final_state["requires_human_review"] is False
    assert "escalation_id" in final_state
    assert final_state["escalation_id"].startswith("ESC-")
