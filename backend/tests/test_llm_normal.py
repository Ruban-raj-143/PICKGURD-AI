import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_llm_normal_case():
    """Test normal DEMO 1 missing item query workflow execution through LLM reasoning node."""
    app = build_pickguard_graph()
    query = "The item X123 is missing from A15-B04. The system says there are 3 units."

    thread_config = {"configurable": {"thread_id": "test-llm-normal-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert final_state["item_id"] == "X123"
    assert final_state["location_id"] == "A15-B04"

    # LLM Reasoning Output Fields
    assert "reasoning" in final_state
    assert "root_cause" in final_state
    assert "recommended_action" in final_state
    assert "A15-B05" in final_state["recommended_action"] or "neighbouring" in final_state["recommended_action"]
    assert final_state["confidence"] > 0.5
    assert final_state["risk_level"] == "LOW"
    assert final_state["requires_human_review"] is False

    # Provider Metadata
    assert final_state["provider"] in ["mimic", "groq", "ollama"]
    assert "model_name" in final_state
