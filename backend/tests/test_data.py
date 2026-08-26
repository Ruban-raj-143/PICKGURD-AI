import os
import pandas as pd
import pytest

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

VALID_EXCEPTION_TYPES = {
    "MISSING_ITEM",
    "QUANTITY_MISMATCH",
    "WRONG_ITEM",
    "BARCODE_FAILURE",
    "DAMAGED_ITEM",
    "LOCATION_DISCREPANCY",
}


@pytest.fixture
def datasets():
    """Load all datasets as DataFrames."""
    loc_path = os.path.join(DATA_DIR, "locations.csv")
    inv_path = os.path.join(DATA_DIR, "inventory.csv")
    task_path = os.path.join(DATA_DIR, "pick_tasks.csv")
    inc_path = os.path.join(DATA_DIR, "incidents.csv")

    assert os.path.exists(loc_path), "locations.csv does not exist"
    assert os.path.exists(inv_path), "inventory.csv does not exist"
    assert os.path.exists(task_path), "pick_tasks.csv does not exist"
    assert os.path.exists(inc_path), "incidents.csv does not exist"

    return {
        "locations": pd.read_csv(loc_path),
        "inventory": pd.read_csv(inv_path),
        "pick_tasks": pd.read_csv(task_path),
        "incidents": pd.read_csv(inc_path),
    }


def test_required_columns(datasets):
    """Test that all datasets contain required columns."""
    df_loc = datasets["locations"]
    df_inv = datasets["inventory"]
    df_task = datasets["pick_tasks"]
    df_inc = datasets["incidents"]

    req_loc = {"location_id", "zone", "aisle", "rack", "bin", "status", "capacity", "neighbouring_locations"}
    req_inv = {"item_id", "sku", "item_name", "category", "location_id", "system_quantity", "available_quantity", "reserved_quantity", "last_scan_timestamp", "last_movement_timestamp", "inventory_status"}
    req_task = {"task_id", "order_id", "item_id", "expected_location", "required_quantity", "priority", "status", "created_at", "assigned_operator"}
    req_inc = {"incident_id", "task_id", "item_id", "location_id", "exception_type", "description", "observed_quantity", "expected_quantity", "previous_location", "resolution", "resolution_category", "resolution_time_seconds", "operator_id", "created_at"}

    assert req_loc.issubset(df_loc.columns)
    assert req_inv.issubset(df_inv.columns)
    assert req_task.issubset(df_task.columns)
    assert req_inc.issubset(df_inc.columns)


def test_record_counts(datasets):
    """Test minimum record thresholds for each dataset."""
    assert len(datasets["locations"]) >= 30, f"Expected >= 30 locations, got {len(datasets['locations'])}"
    assert len(datasets["inventory"]) >= 50, f"Expected >= 50 inventory records, got {len(datasets['inventory'])}"
    assert len(datasets["pick_tasks"]) >= 40, f"Expected >= 40 pick tasks, got {len(datasets['pick_tasks'])}"
    assert len(datasets["incidents"]) >= 100, f"Expected >= 100 incidents, got {len(datasets['incidents'])}"


def test_foreign_key_references(datasets):
    """Test entity relationships and cross-references."""
    loc_ids = set(datasets["locations"]["location_id"])
    item_ids = set(datasets["inventory"]["item_id"])
    task_ids = set(datasets["pick_tasks"]["task_id"])

    # Inventory -> Location
    inv_locs = set(datasets["inventory"]["location_id"])
    assert inv_locs.issubset(loc_ids), f"Inventory references non-existent locations: {inv_locs - loc_ids}"

    # Pick Tasks -> Item & Location
    task_items = set(datasets["pick_tasks"]["item_id"])
    task_locs = set(datasets["pick_tasks"]["expected_location"])
    assert task_items.issubset(item_ids), f"Pick tasks reference non-existent items: {task_items - item_ids}"
    assert task_locs.issubset(loc_ids), f"Pick tasks reference non-existent locations: {task_locs - loc_ids}"

    # Incidents -> Task, Item & Location
    inc_tasks = set(datasets["incidents"]["task_id"])
    inc_items = set(datasets["incidents"]["item_id"])
    inc_locs = set(datasets["incidents"]["location_id"])
    assert inc_tasks.issubset(task_ids), f"Incidents reference non-existent task_ids: {inc_tasks - task_ids}"
    assert inc_items.issubset(item_ids), f"Incidents reference non-existent item_ids: {inc_items - item_ids}"
    assert inc_locs.issubset(loc_ids), f"Incidents reference non-existent location_ids: {inc_locs - loc_ids}"


def test_quantity_rules(datasets):
    """Test non-negative quantities and availability logic."""
    df_inv = datasets["inventory"]
    df_task = datasets["pick_tasks"]
    df_inc = datasets["incidents"]

    assert (df_inv["system_quantity"] >= 0).all()
    assert (df_inv["available_quantity"] >= 0).all()
    assert (df_inv["reserved_quantity"] >= 0).all()
    assert (df_inv["available_quantity"] <= df_inv["system_quantity"]).all()
    assert (df_inv["reserved_quantity"] <= df_inv["system_quantity"]).all()

    assert (df_task["required_quantity"] >= 0).all()
    assert (df_inc["observed_quantity"] >= 0).all()
    assert (df_inc["expected_quantity"] >= 0).all()


def test_valid_exception_types_and_statuses(datasets):
    """Test that exception types and statuses are within allowed sets."""
    df_inc = datasets["incidents"]
    df_loc = datasets["locations"]
    df_task = datasets["pick_tasks"]

    assert set(df_inc["exception_type"]).issubset(VALID_EXCEPTION_TYPES)

    # Ensure all 6 exception types are represented in incidents dataset
    assert len(set(df_inc["exception_type"])) == 6, "Not all 6 exception types are present in incidents.csv"

    assert set(df_loc["status"]).issubset({"ACTIVE", "BLOCKED", "MAINTENANCE"})
    assert set(df_task["priority"]).issubset({"LOW", "NORMAL", "HIGH", "URGENT"})
    assert set(df_task["status"]).issubset({"PENDING", "IN_PROGRESS", "EXCEPTION", "COMPLETED"})


def test_demo_records_exist(datasets):
    """Test that required demo scenarios exist in datasets."""
    df_task = datasets["pick_tasks"]
    df_inv = datasets["inventory"]
    df_loc = datasets["locations"]

    # Demo 1: TASK-1001, item X123, location A15-B04
    demo1_task = df_task[df_task["task_id"] == "TASK-1001"]
    assert not demo1_task.empty, "Demo 1 task TASK-1001 missing"
    assert demo1_task.iloc[0]["item_id"] == "X123"
    assert demo1_task.iloc[0]["expected_location"] == "A15-B04"
    assert demo1_task.iloc[0]["required_quantity"] == 3

    demo1_inv = df_inv[df_inv["item_id"] == "X123"]
    assert not demo1_inv.empty, "Demo 1 item X123 missing from inventory"
    assert demo1_inv.iloc[0]["location_id"] == "A15-B04"
    assert demo1_inv.iloc[0]["system_quantity"] == 3

    # Demo 2: TASK-1002, item X124, location A12-B03
    demo2_task = df_task[df_task["task_id"] == "TASK-1002"]
    assert not demo2_task.empty, "Demo 2 task TASK-1002 missing"
    assert demo2_task.iloc[0]["item_id"] == "X124"
    assert demo2_task.iloc[0]["expected_location"] == "A12-B03"

    # Demo 3: TASK-1003, item X125, location A20-B02, quantity 10
    demo3_task = df_task[df_task["task_id"] == "TASK-1003"]
    assert not demo3_task.empty, "Demo 3 task TASK-1003 missing"
    assert demo3_task.iloc[0]["item_id"] == "X125"
    assert demo3_task.iloc[0]["expected_location"] == "A20-B02"
    assert demo3_task.iloc[0]["required_quantity"] == 10
