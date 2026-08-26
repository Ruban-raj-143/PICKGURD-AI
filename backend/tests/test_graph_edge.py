import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_graph_edge_case():
    """Test DEMO 2 edge case query with dual exception signals (missing item + barcode failure)."""
    app = build_pickguard_graph()
    query = "The item X124 is missing at A12-B03 and the barcode also won't scan."

    thread_config = {"configurable": {"thread_id": "test-edge-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert "BARCODE_FAILURE" in final_state.get("secondary_exception_types", [])

    assert final_state["item_id"] == "X124"
    assert final_state["location_id"] == "A12-B03"

    assert "sop_evidence" in final_state
    assert len(final_state["sop_evidence"]) > 0

    assert "evidence_summary" in final_state
    assert len(final_state["audit_log"]) >= 6
