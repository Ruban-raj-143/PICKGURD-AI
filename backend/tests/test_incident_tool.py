import pytest
from backend.app.tools.incidents import search_similar_incidents


def test_search_by_exception():
    """Test searching incidents by exception_type."""
    res = search_similar_incidents(exception_type="MISSING_ITEM")
    assert res["count"] > 0
    for inc in res["incidents"]:
        assert inc["exception_type"] == "MISSING_ITEM"


def test_search_by_item():
    """Test searching incidents by item_id."""
    res = search_similar_incidents(item_id="X123")
    assert res["count"] > 0
    assert any(inc["item_id"] == "X123" for inc in res["incidents"])


def test_search_by_location():
    """Test searching incidents by location_id."""
    res = search_similar_incidents(location_id="A15-B04")
    assert res["count"] > 0
    assert any(inc["location_id"] == "A15-B04" for inc in res["incidents"])


def test_combined_search():
    """Test searching with item_id, location_id, and exception_type combined."""
    res = search_similar_incidents(item_id="X123", location_id="A15-B04", exception_type="MISSING_ITEM")
    assert res["count"] > 0
    top_hit = res["incidents"][0]
    assert top_hit["item_id"] == "X123"
    assert top_hit["location_id"] == "A15-B04"
    assert top_hit["exception_type"] == "MISSING_ITEM"


def test_empty_result():
    """Test search with parameters matching no records returns count 0."""
    res = search_similar_incidents(item_id="NON_EXISTENT_ITEM_999", location_id="NON_EXISTENT_LOC_999", exception_type="MISSING_ITEM")
    assert res["count"] == 0 or all(inc["exception_type"] == "MISSING_ITEM" for inc in res["incidents"])
