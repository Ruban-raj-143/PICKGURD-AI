import pytest
from backend.app.graph.nodes import (
    parse_operator_query,
    classify_exception,
    fetch_operational_evidence,
    retrieve_sop_evidence,
    retrieve_historical_evidence,
    build_evidence_package,
)


def test_parse_operator_query_node():
    """Test parse_operator_query node extracts task_id, item_id, location_id."""
    state = {"operator_query": "Item X123 is missing from A15-B04 in task TASK-1001"}
    res = parse_operator_query(state)

    assert res["item_id"] == "X123"
    assert res["location_id"] == "A15-B04"
    assert res["task_id"] == "TASK-1001"
    assert len(res["audit_log"]) > 0


def test_classify_exception_node():
    """Test classify_exception node maps query to primary and secondary exceptions."""
    state = {"operator_query": "Item X123 missing and barcode label is unreadable"}
    res = classify_exception(state)

    assert res["exception_type"] == "MISSING_ITEM"
    assert "BARCODE_FAILURE" in res["secondary_exception_types"]


def test_fetch_operational_evidence_node():
    """Test fetch_operational_evidence node calls deterministic tools."""
    state = {"task_id": "TASK-1001", "item_id": "X123", "location_id": "A15-B04", "audit_log": []}
    res = fetch_operational_evidence(state)

    op_data = res["operational_data"]
    assert "pick_task" in op_data
    assert "inventory" in op_data
    assert "location" in op_data


def test_retrieve_sop_evidence_node():
    """Test retrieve_sop_evidence node retrieves SOP chunks."""
    state = {"exception_type": "MISSING_ITEM", "operator_query": "item missing from expected bin", "audit_log": []}
    res = retrieve_sop_evidence(state)

    assert isinstance(res["sop_evidence"], list)
    assert len(res["sop_evidence"]) > 0


def test_retrieve_historical_evidence_node():
    """Test retrieve_historical_evidence node retrieves past incidents."""
    state = {"item_id": "X123", "location_id": "A15-B04", "exception_type": "MISSING_ITEM", "audit_log": []}
    res = retrieve_historical_evidence(state)

    assert isinstance(res["historical_evidence"], list)
    assert len(res["historical_evidence"]) > 0


def test_build_evidence_package_node():
    """Test build_evidence_package node synthesizes structured evidence sections."""
    state = {
        "exception_type": "MISSING_ITEM",
        "operational_data": {
            "inventory": {"item_id": "X123", "location_id": "A15-B04", "system_quantity": 3, "item_name": "Wireless Ergonomic Mouse", "inventory_status": "AVAILABLE"},
            "location": {"location_id": "A15-B04", "zone": "Z01", "neighbouring_locations": ["A15-B03", "A15-B05"]},
        },
        "sop_evidence": [{"sop_id": "SOP-MISSING-001", "version": "1.0", "section": "Verification Steps", "content": "Check neighbouring bins."}],
        "historical_evidence": [{"incident_id": "INC-0001", "exception_type": "MISSING_ITEM", "resolution_category": "CHECK_NEIGHBOURING_LOCATION", "resolution": "Checked A15-B05."}],
        "audit_log": [],
    }

    res = build_evidence_package(state)
    summary = res["evidence_summary"]

    assert "OBSERVED_FACTS" in summary
    assert "SOP_EVIDENCE" in summary
    assert "HISTORICAL_EVIDENCE" in summary
    assert "INFERENCES" in summary
    assert "EVIDENCE_GAPS" in summary
    assert res["provider"] == "deterministic"
    assert res["model_name"] == "rule-based-classifier"
