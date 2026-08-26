import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_llm_no_evidence_case():
    """Test query referencing non-existent task/item/location results in evidence gaps and human review."""
    app = build_pickguard_graph()
    query = "The item X9999 is missing from bin A99-B99 in task TASK-9999."

    thread_config = {"configurable": {"thread_id": "test-llm-no-ev-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["requires_human_review"] is True
    assert len(final_state["errors"]) > 0

    ev_summary = final_state.get("evidence_summary", {})
    assert len(ev_summary.get("EVIDENCE_GAPS", [])) > 0

    # Verify no fabricated inventory or location facts exist in observed facts
    observed = " ".join(ev_summary.get("OBSERVED_FACTS", []))
    assert "No verified operational facts" in observed or "not found" in observed.lower()
