import pytest
from backend.app.graph.nodes import select_next_best_action


def test_select_action_missing_item():
    """Test select_next_best_action selects CHECK_NEIGHBOURING_LOCATION for MISSING_ITEM."""
    state = {"exception_type": "MISSING_ITEM", "operator_query": "Item missing from bin", "audit_log": []}
    res = select_next_best_action(state)
    assert res["next_best_action"] == "CHECK_NEIGHBOURING_LOCATION"


def test_select_action_quantity_mismatch():
    """Test select_next_best_action selects RECOUNT_QUANTITY for QUANTITY_MISMATCH."""
    state = {"exception_type": "QUANTITY_MISMATCH", "operator_query": "Count mismatch", "audit_log": []}
    res = select_next_best_action(state)
    assert res["next_best_action"] == "RECOUNT_QUANTITY"


def test_select_action_barcode_failure():
    """Test select_next_best_action selects VERIFY_BARCODE for BARCODE_FAILURE."""
    state = {"exception_type": "BARCODE_FAILURE", "operator_query": "Barcode won't scan", "audit_log": []}
    res = select_next_best_action(state)
    assert res["next_best_action"] == "VERIFY_BARCODE"


def test_select_action_wrong_item():
    """Test select_next_best_action selects VERIFY_ITEM_IDENTITY for WRONG_ITEM."""
    state = {"exception_type": "WRONG_ITEM", "operator_query": "Different SKU in bin", "audit_log": []}
    res = select_next_best_action(state)
    assert res["next_best_action"] == "VERIFY_ITEM_IDENTITY"


def test_select_action_damaged_item():
    """Test select_next_best_action selects REVIEW_SOP for DAMAGED_ITEM."""
    state = {"exception_type": "DAMAGED_ITEM", "operator_query": "Packaging dented", "audit_log": []}
    res = select_next_best_action(state)
    assert res["next_best_action"] == "REVIEW_SOP"


def test_select_action_location_discrepancy():
    """Test select_next_best_action selects CHECK_LOCATION for LOCATION_DISCREPANCY."""
    state = {"exception_type": "LOCATION_DISCREPANCY", "operator_query": "Wrong location bin", "audit_log": []}
    res = select_next_best_action(state)
    assert res["next_best_action"] == "CHECK_LOCATION"


def test_select_action_unknown():
    """Test select_next_best_action selects COLLECT_MORE_EVIDENCE for UNKNOWN."""
    state = {"exception_type": "UNKNOWN", "operator_query": "Unclassified issue", "audit_log": []}
    res = select_next_best_action(state)
    assert res["next_best_action"] == "COLLECT_MORE_EVIDENCE"
