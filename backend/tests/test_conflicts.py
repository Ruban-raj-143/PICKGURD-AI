import pytest
from backend.app.graph.nodes import detect_evidence_conflicts


def test_detect_quantity_conflict():
    """Test detect_evidence_conflicts flags QUANTITY_CONFLICT when system reports count difference."""
    state = {
        "operator_query": "System says 10 units but physical count is 6.",
        "exception_type": "QUANTITY_MISMATCH",
        "operational_data": {"inventory": {"system_quantity": 10}},
        "audit_log": [],
    }
    res = detect_evidence_conflicts(state)

    conflicts = res["evidence_conflicts"]
    assert len(conflicts) > 0
    assert any(c["type"] == "QUANTITY_CONFLICT" for c in conflicts)


def test_detect_location_conflict():
    """Test detect_evidence_conflicts flags LOCATION_CONFLICT when item is in another bin."""
    state = {
        "operator_query": "Item found in another bin location.",
        "exception_type": "LOCATION_DISCREPANCY",
        "operational_data": {"pick_task": {"expected_location": "A15-B04"}},
        "audit_log": [],
    }
    res = detect_evidence_conflicts(state)

    conflicts = res["evidence_conflicts"]
    assert len(conflicts) > 0
    assert any(c["type"] == "LOCATION_CONFLICT" for c in conflicts)
