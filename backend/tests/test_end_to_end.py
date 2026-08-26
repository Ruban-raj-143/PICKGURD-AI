import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_end_to_end_full_pipeline_flow():
    """Complete E2E integration test: Query -> API -> LangGraph -> Tools -> RAG -> LLM -> Safety -> Human Review -> Final Decision."""
    # 1. Submit High-Risk Exception Query
    run_req = {
        "query": "TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6.",
        "task_id": "TASK-1003",
        "item_id": "X125",
        "location_id": "A20-B02",
    }
    run_res = client.post("/api/v1/agent/run", json=run_req)
    assert run_res.status_code == 201
    run_data = run_res.json()

    run_id = run_data["run_id"]
    assert run_data["status"] == "WAITING_FOR_HUMAN_REVIEW"
    assert run_data["exception_type"] == "QUANTITY_MISMATCH"
    assert run_data["risk_level"] == "HIGH"
    assert run_data["action_status"] == "BLOCKED"

    # Verify Evidence Grounding & Provenance
    assert len(run_data["evidence_summary"]["OBSERVED_FACTS"]) > 0
    assert len(run_data["provenance"]["operational"]) > 0

    # 2. Submit Supervisor Approval Decision
    review_req = {
        "decision": "APPROVE",
        "reviewer_id": "SUPERVISOR-E2E-001",
        "reviewer_note": "E2E verification of approval flow.",
    }
    review_res = client.post(f"/api/v1/agent/{run_id}/review", json=review_req)
    assert review_res.status_code == 200
    rev_data = review_res.json()

    assert rev_data["status"] == "COMPLETED"
    assert rev_data["action_status"] == "HUMAN_APPROVED_PENDING_EXECUTION"
    assert "APPROVED" in rev_data["final_decision"]

    # 3. Retrieve Final Run Status & Audit Trail
    status_res = client.get(f"/api/v1/agent/{run_id}")
    assert status_res.status_code == 200
    final_data = status_res.json()

    assert final_data["status"] == "COMPLETED"
    assert any("Human decision = APPROVE" in entry for entry in final_data["audit_log"])
