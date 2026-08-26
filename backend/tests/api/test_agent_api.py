import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test GET /health health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_system_status_endpoint():
    """Test GET /api/v1/system/status endpoint."""
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "llm_provider" in data
    assert "model_name" in data


def test_run_agent_normal_endpoint():
    """Test POST /api/v1/agent/run for normal missing item query."""
    payload = {
        "query": "The item X123 is missing from A15-B04. The system says there are 3 units.",
        "task_id": "TASK-1001",
        "item_id": "X123",
        "location_id": "A15-B04",
    }
    response = client.post("/api/v1/agent/run", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["run_id"].startswith("RUN-")
    assert data["status"] == "COMPLETED"
    assert data["exception_type"] == "MISSING_ITEM"
    assert data["risk_level"] == "LOW"
    assert data["requires_human_review"] is False
    assert len(data["audit_log"]) > 0


def test_run_agent_high_risk_endpoint():
    """Test POST /api/v1/agent/run for high-risk quantity mismatch query pauses at WAITING_FOR_HUMAN_REVIEW."""
    payload = {
        "query": "TASK-1003 quantity mismatch: System says 10 units but I counted 6. Update inventory to 6.",
        "task_id": "TASK-1003",
        "item_id": "X125",
        "location_id": "A20-B02",
    }
    response = client.post("/api/v1/agent/run", json=payload)
    assert response.status_code == 201
    data = response.json()

    run_id = data["run_id"]
    assert data["status"] == "WAITING_FOR_HUMAN_REVIEW"
    assert data["risk_level"] == "HIGH"
    assert data["requires_human_review"] is True
    assert data["human_review_payload"] is not None

    # Test GET /api/v1/agent/{run_id}
    get_res = client.get(f"/api/v1/agent/{run_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "WAITING_FOR_HUMAN_REVIEW"

    # Test POST /api/v1/agent/{run_id}/review with REJECT decision
    review_payload = {
        "decision": "REJECT",
        "reviewer_id": "API-REVIEWER-001",
        "reviewer_note": "API test reject decision",
    }
    review_res = client.post(f"/api/v1/agent/{run_id}/review", json=review_payload)
    assert review_res.status_code == 200
    rev_data = review_res.json()

    assert rev_data["status"] == "COMPLETED"
    assert rev_data["action_status"] == "REJECTED_BY_HUMAN"

    # Test GET /api/v1/agent/{run_id}/audit
    audit_res = client.get(f"/api/v1/agent/{run_id}/audit")
    assert audit_res.status_code == 200
    assert len(audit_res.json()["audit_log"]) >= 10
