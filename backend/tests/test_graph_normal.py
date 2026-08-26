import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_graph_normal_case():
    """Test normal DEMO 1 missing item query workflow execution."""
    app = build_pickguard_graph()
    query = "The item X123 is missing from A15-B04. The system says there are 3 units."

    thread_config = {"configurable": {"thread_id": "test-normal-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert final_state["item_id"] == "X123"
    assert final_state["location_id"] == "A15-B04"

    # Operational Evidence
    assert "operational_data" in final_state
    assert "inventory" in final_state["operational_data"]
    assert final_state["operational_data"]["inventory"]["system_quantity"] == 3

    # SOP Evidence
    assert "sop_evidence" in final_state
    assert len(final_state["sop_evidence"]) > 0
    assert final_state["sop_evidence"][0]["sop_id"] == "SOP-MISSING-001"

    # Historical Evidence
    assert "historical_evidence" in final_state
    assert isinstance(final_state["historical_evidence"], list)

    # Evidence Package
    assert "evidence_summary" in final_state
    pkg = final_state["evidence_summary"]
    assert len(pkg["OBSERVED_FACTS"]) > 0
    assert len(pkg["SOP_EVIDENCE"]) > 0
    assert len(pkg["INFERENCES"]) > 0

    # Audit Log
    assert len(final_state["audit_log"]) >= 6
