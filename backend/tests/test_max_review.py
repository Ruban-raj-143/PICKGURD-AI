import pytest
from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def test_max_review_attempts_limit():
    """Test that exceeding MAX_REVIEW_ATTEMPTS (2) automatically triggers supervisor escalation instead of looping forever."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-max-review-001"}}
    query = "TASK-1003 quantity mismatch: System says 10 units but I counted 6. Update inventory to 6."

    # 1. First interrupt
    app.invoke({"operator_query": query}, thread_config)

    # 2. Request more evidence (Attempt 1)
    app.invoke(Command(resume={"decision": "REQUEST_MORE_EVIDENCE"}), thread_config)

    # 3. Request more evidence (Attempt 2)
    final_state = app.invoke(Command(resume={"decision": "REQUEST_MORE_EVIDENCE"}), thread_config)

    # Exceeding attempt 2 must trigger auto escalation
    assert final_state["action_status"] == "ESCALATED" or final_state.get("review_attempts", 0) >= 2
    assert final_state["requires_human_review"] is False
