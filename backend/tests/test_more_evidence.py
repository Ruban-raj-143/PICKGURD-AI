import pytest
from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def test_request_more_evidence_flow():
    """Test that human REQUEST_MORE_EVIDENCE decision routes to collect_additional_evidence node and re-evaluates."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-more-evidence-001"}}
    query = "TASK-1003 quantity mismatch: System says 10 units but I counted 6. Update inventory to 6."

    app.invoke({"operator_query": query}, thread_config)

    decision_payload = {"decision": "REQUEST_MORE_EVIDENCE", "reviewer_id": "SUPERVISOR-007", "reviewer_note": "Need more logs."}

    # Resuming with REQUEST_MORE_EVIDENCE routes to collect_additional_evidence -> build_evidence_package -> ... -> human_review_gate
    res2 = app.invoke(Command(resume=decision_payload), thread_config)

    # State should reflect review attempt increment
    snapshot = app.get_state(thread_config)
    state = snapshot.values

    assert state.get("review_attempts") == 1
    assert any("REQUEST_MORE_EVIDENCE" in log for log in state.get("audit_log", []))
