import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_llm_edge_case():
    """Test DEMO 2 dual exception query (missing item + barcode failure) through LLM reasoning node."""
    app = build_pickguard_graph()
    query = "The item X124 is missing at A12-B03 and the barcode also won't scan."

    thread_config = {"configurable": {"thread_id": "test-llm-edge-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert "BARCODE_FAILURE" in final_state.get("secondary_exception_types", [])

    assert "recommended_action" in final_state
    assert len(final_state["recommended_action"]) > 0
    assert final_state["risk_level"] in ["LOW", "MEDIUM"]
