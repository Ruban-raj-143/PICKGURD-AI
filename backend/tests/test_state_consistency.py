import pytest
from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def test_state_consistency_across_interrupt_and_resume():
    """Verify that task_id, item_id, location_id, operational_data, SOP evidence, and audit logs are preserved across interrupt and resume."""
    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "test-thread-consistency-001"}}
    query = "TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6."

    app.invoke({"operator_query": query}, thread_config)

    # Inspect checkpoint snapshot state
    snapshot1 = app.get_state(thread_config)
    state1 = snapshot1.values

    assert state1["task_id"] == "TASK-1003"
    assert state1["item_id"] == "X125"
    assert state1["location_id"] == "A20-B02"
    assert "pick_task" in state1["operational_data"]
    assert len(state1["sop_evidence"]) > 0
    assert len(state1["audit_log"]) >= 9

    # Resume graph
    final_state = app.invoke(Command(resume={"decision": "REJECT"}), thread_config)

    # State fields must remain perfectly intact after resume
    assert final_state["task_id"] == "TASK-1003"
    assert final_state["item_id"] == "X125"
    assert final_state["location_id"] == "A20-B02"
    assert "pick_task" in final_state["operational_data"]
    assert len(final_state["sop_evidence"]) > 0
    assert len(final_state["audit_log"]) >= 10
    assert final_state["human_decision"] == "REJECT"
