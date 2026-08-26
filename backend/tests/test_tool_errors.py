import pytest
from backend.app.tools.inventory import get_inventory
from backend.app.tools.pick_tasks import get_pick_task
from backend.app.tools.locations import get_location
from backend.app.tools.incidents import search_similar_incidents


def test_inventory_invalid_inputs():
    """Test error payloads for empty or invalid item IDs."""
    res1 = get_inventory("")
    assert res1["found"] is False
    assert res1["error_code"] == "INVALID_PARAMETER"

    res2 = get_inventory("   ")
    assert res2["found"] is False
    assert res2["error_code"] == "INVALID_PARAMETER"


def test_pick_task_invalid_inputs():
    """Test error payloads for empty task IDs."""
    res = get_pick_task("")
    assert res["found"] is False
    assert res["error_code"] == "INVALID_PARAMETER"


def test_location_invalid_inputs():
    """Test error payloads for empty location IDs."""
    res = get_location("")
    assert res["found"] is False
    assert res["error_code"] == "INVALID_PARAMETER"


def test_incident_empty_query_params():
    """Test error payload when no query parameters are provided to search_similar_incidents."""
    res = search_similar_incidents()
    assert res["count"] == 0
    assert res["error_code"] == "MISSING_QUERY_PARAMS"
