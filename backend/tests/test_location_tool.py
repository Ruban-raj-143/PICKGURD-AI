import pytest
from backend.app.tools.locations import get_location


def test_existing_location():
    """Test retrieving an existing bin location (A15-B04)."""
    res = get_location("A15-B04")
    assert res["found"] is True
    assert res["location_id"] == "A15-B04"
    assert res["zone"] == "Z01"
    assert res["status"] == "ACTIVE"


def test_missing_location():
    """Test lookup for non-existent location returns found=False structured error."""
    res = get_location("LOC-999_NON_EXISTENT")
    assert res["found"] is False
    assert res["error_code"] == "LOCATION_NOT_FOUND"


def test_neighbouring_locations_returned():
    """Test that neighbouring_locations is returned as a non-empty list for A15-B04."""
    res = get_location("A15-B04")
    assert res["found"] is True
    assert isinstance(res["neighbouring_locations"], list)
    assert "A15-B03" in res["neighbouring_locations"] or "A15-B05" in res["neighbouring_locations"]
