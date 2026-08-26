import pytest
from backend.app.tools.pick_tasks import get_pick_task


def test_existing_pick_task():
    """Test retrieving an existing pick task (TASK-1001)."""
    res = get_pick_task("TASK-1001")
    assert res["found"] is True
    assert res["task_id"] == "TASK-1001"
    assert res["order_id"] == "ORD-9001"
    assert res["item_id"] == "X123"
    assert res["expected_location"] == "A15-B04"
    assert res["required_quantity"] == 3


def test_missing_pick_task():
    """Test lookup for non-existent task returns found=False structured error."""
    res = get_pick_task("TASK-9999_NON_EXISTENT")
    assert res["found"] is False
    assert res["error_code"] == "TASK_NOT_FOUND"


def test_returned_item_matches_dataset():
    """Test that returned pick task item fields match dataset expectation."""
    res = get_pick_task("TASK-1003")
    assert res["found"] is True
    assert res["item_id"] == "X125"
    assert res["expected_location"] == "A20-B02"
    assert res["required_quantity"] == 10
