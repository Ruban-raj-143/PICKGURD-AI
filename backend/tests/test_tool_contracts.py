import pytest
from backend.app.tools.inventory import get_inventory
from backend.app.tools.pick_tasks import get_pick_task
from backend.app.tools.locations import get_location
from backend.app.tools.incidents import search_similar_incidents
from backend.app.tools.sop import search_sop
from backend.app.tools.escalation import create_escalation


def test_tool_contract_structured_outputs():
    """Verify all tool responses conform to expected contract key signatures."""
    inv = get_inventory("X123")
    assert "found" in inv
    assert "item_id" in inv

    task = get_pick_task("TASK-1001")
    assert "found" in task
    assert "task_id" in task

    loc = get_location("A15-B04")
    assert "found" in loc
    assert "neighbouring_locations" in loc

    inc = search_similar_incidents(exception_type="MISSING_ITEM")
    assert "count" in inc
    assert "incidents" in inc

    sop = search_sop("MISSING_ITEM", query="item missing from expected location")
    assert "found" in sop
    assert "results" in sop

    esc = create_escalation(
        task_id="TASK-1001",
        exception_type="MISSING_ITEM",
        reason="Reason text",
        evidence_summary="Evidence summary text",
        recommended_action="Action text",
    )
    assert esc["success"] is True
    assert esc["status"] == "PENDING_HUMAN_REVIEW"


def test_missing_data_does_not_fabricate_values():
    """Verify that querying missing identifiers returns found=False without hallucinated data."""
    inv = get_inventory("FABRICATED_ITEM_9999")
    assert inv["found"] is False
    assert inv.get("sku") is None
    assert inv.get("system_quantity") is None

    task = get_pick_task("FABRICATED_TASK_9999")
    assert task["found"] is False
    assert task.get("order_id") is None

    loc = get_location("FABRICATED_LOC_9999")
    assert loc["found"] is False
    assert loc.get("zone") is None


def test_demo_1_tool_chain_verification():
    """End-to-end tool query chain verification for DEMO 1 (TASK-1001).

    Verifies:
    1. Pick task TASK-1001 exists.
    2. Target item X123 exists.
    3. Expected location A15-B04 exists.
    4. Inventory for X123 at A15-B04 exists.
    5. Similar historical incidents exist.
    6. At least one neighbouring location exists (e.g. A15-B05).
    """
    # 1. Fetch Pick Task
    task_res = get_pick_task("TASK-1001")
    assert task_res["found"] is True
    assert task_res["item_id"] == "X123"
    assert task_res["expected_location"] == "A15-B04"

    # 2. Fetch Item & Location
    item_id = task_res["item_id"]
    loc_id = task_res["expected_location"]

    loc_res = get_location(loc_id)
    assert loc_res["found"] is True
    assert loc_res["location_id"] == "A15-B04"

    # 3. Fetch Inventory
    inv_res = get_inventory(item_id, loc_id)
    assert inv_res["found"] is True
    assert inv_res["item_id"] == "X123"
    assert inv_res["system_quantity"] == 3

    # 4. Fetch Similar Historical Incidents
    inc_res = search_similar_incidents(item_id=item_id, location_id=loc_id, exception_type="MISSING_ITEM")
    assert inc_res["count"] > 0
    top_inc = inc_res["incidents"][0]
    assert top_inc["exception_type"] == "MISSING_ITEM"

    # 5. Check Neighbouring Bins for Overflow Inventory
    neighbours = loc_res["neighbouring_locations"]
    assert len(neighbours) > 0
    assert "A15-B05" in neighbours or "A15-B03" in neighbours
