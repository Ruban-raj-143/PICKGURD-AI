import pytest
from backend.app.graph.nodes import fuse_evidence


def test_fuse_evidence_strong_quality():
    """Test fuse_evidence rates quality as STRONG when operational facts, SOP, and historical evidence exist."""
    state = {
        "operational_data": {"inventory": {"item_id": "X123", "location_id": "A15-B04", "system_quantity": 3}},
        "sop_evidence": [{"sop_id": "SOP-MISSING-001", "version": "1.0", "section": "Verification Steps"}],
        "historical_evidence": [{"incident_id": "INC-0001", "resolution_category": "CHECK_NEIGHBOURING_LOCATION"}],
        "errors": [],
        "audit_log": [],
    }
    res = fuse_evidence(state)

    assert res["evidence_quality"] == "STRONG"
    assert len(res["provenance"]["operational"]) > 0
    assert len(res["provenance"]["sop"]) > 0
    assert len(res["provenance"]["historical"]) > 0


def test_fuse_evidence_moderate_quality():
    """Test fuse_evidence rates quality as MODERATE when operational data and SOP exist."""
    state = {
        "operational_data": {"inventory": {"item_id": "X123", "location_id": "A15-B04", "system_quantity": 3}},
        "sop_evidence": [{"sop_id": "SOP-MISSING-001", "version": "1.0", "section": "Verification Steps"}],
        "historical_evidence": [],
        "errors": [],
        "audit_log": [],
    }
    res = fuse_evidence(state)

    assert res["evidence_quality"] == "STRONG" or res["evidence_quality"] == "MODERATE"


def test_fuse_evidence_insufficient_quality():
    """Test fuse_evidence rates quality as INSUFFICIENT when errors occur and no evidence is retrieved."""
    state = {
        "operational_data": {},
        "sop_evidence": [],
        "historical_evidence": [],
        "errors": [{"error": "DATA_NOT_FOUND"}],
        "audit_log": [],
    }
    res = fuse_evidence(state)

    assert res["evidence_quality"] == "INSUFFICIENT"
