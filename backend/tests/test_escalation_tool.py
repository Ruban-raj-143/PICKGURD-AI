import pytest
import sqlite3
import os
from backend.app.tools.escalation import create_escalation, DB_FILE
from backend.app.tools.inventory import get_inventory


def test_escalation_creation():
    """Test creating an escalation record and verifying returned payload."""
    res = create_escalation(
        task_id="TASK-1003",
        exception_type="QUANTITY_MISMATCH",
        reason="Physical count 6 is 4 units less than system count 10.",
        evidence_summary="Observed quantity 6 vs System quantity 10 at location A20-B02.",
        recommended_action="Flag for human supervisor cycle count audit.",
    )

    assert res["success"] is True
    assert res["escalation_id"].startswith("ESC-")
    assert res["status"] == "PENDING_HUMAN_REVIEW"
    assert res["task_id"] == "TASK-1003"
    assert res["exception_type"] == "QUANTITY_MISMATCH"


def test_escalation_persisted_in_sqlite():
    """Test that escalation record is correctly persisted in SQLite database."""
    res = create_escalation(
        task_id="TASK-1003",
        exception_type="QUANTITY_MISMATCH",
        reason="Test escalation persistence.",
        evidence_summary="Test evidence.",
        recommended_action="Test action.",
    )

    esc_id = res["escalation_id"]
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, task_id FROM escalations WHERE escalation_id = ?", (esc_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "PENDING_HUMAN_REVIEW"
        assert row[1] == "TASK-1003"


def test_no_warehouse_data_modified():
    """Test that creating an escalation does not modify inventory stock numbers."""
    inv_before = get_inventory("X125", "A20-B02")
    
    create_escalation(
        task_id="TASK-1003",
        exception_type="QUANTITY_MISMATCH",
        reason="Audit check.",
        evidence_summary="Evidence.",
        recommended_action="Action.",
    )

    inv_after = get_inventory("X125", "A20-B02")
    assert inv_before["system_quantity"] == inv_after["system_quantity"]
    assert inv_before["available_quantity"] == inv_after["available_quantity"]
