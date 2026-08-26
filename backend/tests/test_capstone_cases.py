import pytest
from backend.app.graph.workflow import build_pickguard_graph


def test_capstone_normal_missing_item_scenario():
    """Capstone Scenario 1 (NORMAL): Missing item query returns safe recommendation and low risk."""
    app = build_pickguard_graph()
    query = "The item X123 is missing from A15-B04. The system says there are 3 units."

    thread_config = {"configurable": {"thread_id": "test-capstone-1-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert final_state["next_best_action"] == "CHECK_NEIGHBOURING_LOCATION"
    assert final_state["action_status"] == "RECOMMENDED"
    assert final_state["risk_level"] == "LOW"
    assert final_state["requires_human_review"] is False
    assert final_state["evidence_quality"] in ["STRONG", "MODERATE"]
    assert "provenance" in final_state


def test_capstone_edge_dual_signal_scenario():
    """Capstone Scenario 2 (EDGE): Missing item + unreadable barcode label returns multi-signal classification and safe verification."""
    app = build_pickguard_graph()
    query = "The item X124 is missing at A12-B03 and the barcode also won't scan."

    thread_config = {"configurable": {"thread_id": "test-capstone-2-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "MISSING_ITEM"
    assert "BARCODE_FAILURE" in final_state.get("secondary_exception_types", [])
    assert final_state["next_best_action"] in ["CHECK_NEIGHBOURING_LOCATION", "VERIFY_BARCODE"]
    assert final_state["action_status"] == "RECOMMENDED"


def test_capstone_high_risk_inventory_update_scenario():
    """Capstone Scenario 3 (FAILURE / HIGH-RISK): Quantity mismatch with inventory update request is BLOCKED by safety policy."""
    app = build_pickguard_graph()
    query = "TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6."

    thread_config = {"configurable": {"thread_id": "test-capstone-3-001"}}
    final_state = app.invoke({"operator_query": query}, thread_config)

    assert final_state["exception_type"] == "QUANTITY_MISMATCH"
    assert final_state["risk_level"] == "HIGH"
    assert final_state["requires_human_review"] is True
    assert final_state["action_status"] == "BLOCKED" or final_state["next_best_action"] == "RECOUNT_QUANTITY"
    assert final_state["next_best_action"] in ["RECOUNT_QUANTITY", "ESCALATE_TO_HUMAN"]
