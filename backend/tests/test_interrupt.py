import pytest
from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def test_interrupt_checkpoint_and_command_resume():
    """Test real LangGraph interrupt checkpoint and Command(resume=...) state resumption."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-interrupt-001"}}
    query = "TASK-1003 quantity mismatch: System says 10 units but I counted 6. Update inventory to 6."

    # 1. First invocation should pause at human_review_gate interrupt
    res1 = app.invoke({"operator_query": query}, thread_config)

    snapshot = app.get_state(thread_config)
    assert snapshot.next == ("human_review_gate",)

    # 2. Inspect interrupt payload
    interrupts = snapshot.tasks[0].interrupts
    assert len(interrupts) > 0
    payload = interrupts[0].value

    assert payload["type"] == "human_review_required"
    assert payload["task_id"] == "TASK-1003"
    assert payload["exception_type"] == "QUANTITY_MISMATCH"
    assert payload["risk_level"] == "HIGH"
    assert payload["action_status"] == "BLOCKED"

    # 3. Resume graph using Command(resume=...)
    decision_payload = {"decision": "REJECT", "reviewer_id": "REVIEWER-TEST-001", "reviewer_note": "Test reject note"}
    final_state = app.invoke(Command(resume=decision_payload), thread_config)

    assert final_state["human_decision"] == "REJECT"
    assert final_state["action_status"] == "REJECTED_BY_HUMAN"
    assert final_state["requires_human_review"] is False
    assert any("Human decision = REJECT" in log for log in final_state["audit_log"])
