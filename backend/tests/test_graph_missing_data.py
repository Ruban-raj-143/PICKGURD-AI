import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_graph_missing_data_case():
    """Test query referencing non-existent task, item, and location IDs handles errors safely."""
    app = build_pickguard_graph()
    query = "The item X9999 is missing from A99-B99 in task TASK-9999."

    thread_config = {"configurable": {"thread_id": "test-missing-data-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert final_state["item_id"] == "X9999"
    assert final_state["location_id"] == "A99-B99"
    assert final_state["task_id"] == "TASK-9999"

    # Tool failures should be captured in errors list without crashing graph
    assert len(final_state["errors"]) > 0
    error_codes = [err.get("error_code") for err in final_state["errors"] if "error_code" in err]
    assert "ITEM_NOT_FOUND" in error_codes or "TASK_NOT_FOUND" in error_codes or "LOCATION_NOT_FOUND" in error_codes

    # Evidence package contains recorded evidence gaps
    assert "evidence_summary" in final_state
    pkg = final_state["evidence_summary"]
    assert len(pkg.get("EVIDENCE_GAPS", [])) > 0

    # Graph completes safely
    assert len(final_state["audit_log"]) >= 6
