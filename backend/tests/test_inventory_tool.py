import pytest
from backend.app.tools.inventory import get_inventory


def test_existing_item():
    """Test retrieving an existing inventory item (X123 at A15-B04)."""
    res = get_inventory("X123", "A15-B04")
    assert res["found"] is True
    assert res["item_id"] == "X123"
    assert res["location_id"] == "A15-B04"
    assert res["system_quantity"] == 3
    assert res["inventory_status"] == "AVAILABLE"


def test_missing_item():
    """Test lookup for a non-existent item returns found=False structured error."""
    res = get_inventory("X999_NON_EXISTENT")
    assert res["found"] is False
    assert res["error_code"] == "ITEM_NOT_FOUND"
    assert "No inventory record exists" in res["message"]


def test_correct_quantity():
    """Test that system_quantity equals available_quantity + reserved_quantity."""
    res = get_inventory("X124", "A12-B03")
    assert res["found"] is True
    assert res["system_quantity"] == res["available_quantity"] + res["reserved_quantity"]


def test_invalid_location():
    """Test lookup for existing item but non-matching location returns found=False."""
    res = get_inventory("X123", "Z99-B99_INVALID")
    assert res["found"] is False
    assert res["error_code"] == "ITEM_NOT_FOUND"
