"""Data validation script for PickGuard AI synthetic datasets.

Verifies schema compliance, entity integrity, quantity rules, exception types,
and foreign key relationships across locations, inventory, pick tasks, and incidents datasets.
"""

import os
import sys
import pandas as pd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

VALID_EXCEPTION_TYPES = {
    "MISSING_ITEM",
    "QUANTITY_MISMATCH",
    "WRONG_ITEM",
    "BARCODE_FAILURE",
    "DAMAGED_ITEM",
    "LOCATION_DISCREPANCY",
}

VALID_LOCATION_STATUSES = {"ACTIVE", "BLOCKED", "MAINTENANCE"}
VALID_INVENTORY_STATUSES = {"AVAILABLE", "DAMAGED", "HOLD", "DISCREPANCY"}
VALID_TASK_PRIORITIES = {"LOW", "NORMAL", "HIGH", "URGENT"}
VALID_TASK_STATUSES = {"PENDING", "IN_PROGRESS", "EXCEPTION", "COMPLETED"}


def validate_datasets():
    errors = []
    
    # Required files check
    locations_path = os.path.join(DATA_DIR, "locations.csv")
    inventory_path = os.path.join(DATA_DIR, "inventory.csv")
    pick_tasks_path = os.path.join(DATA_DIR, "pick_tasks.csv")
    incidents_path = os.path.join(DATA_DIR, "incidents.csv")
    
    for path, name in [(locations_path, "locations.csv"), (inventory_path, "inventory.csv"), 
                      (pick_tasks_path, "pick_tasks.csv"), (incidents_path, "incidents.csv")]:
        if not os.path.exists(path):
            errors.append(f"File missing: {name}")
            
    if errors:
        print(f"FAILED: Missing files: {errors}")
        sys.exit(1)
        
    df_loc = pd.read_csv(locations_path)
    df_inv = pd.read_csv(inventory_path)
    df_task = pd.read_csv(pick_tasks_path)
    df_inc = pd.read_csv(incidents_path)

    # 1. Required Columns Check
    req_loc_cols = {"location_id", "zone", "aisle", "rack", "bin", "status", "capacity", "neighbouring_locations"}
    req_inv_cols = {"item_id", "sku", "item_name", "category", "location_id", "system_quantity", "available_quantity", "reserved_quantity", "last_scan_timestamp", "last_movement_timestamp", "inventory_status"}
    req_task_cols = {"task_id", "order_id", "item_id", "expected_location", "required_quantity", "priority", "status", "created_at", "assigned_operator"}
    req_inc_cols = {"incident_id", "task_id", "item_id", "location_id", "exception_type", "description", "observed_quantity", "expected_quantity", "previous_location", "resolution", "resolution_category", "resolution_time_seconds", "operator_id", "created_at"}

    if not req_loc_cols.issubset(df_loc.columns):
        errors.append(f"locations.csv missing columns: {req_loc_cols - set(df_loc.columns)}")
    if not req_inv_cols.issubset(df_inv.columns):
        errors.append(f"inventory.csv missing columns: {req_inv_cols - set(df_inv.columns)}")
    if not req_task_cols.issubset(df_task.columns):
        errors.append(f"pick_tasks.csv missing columns: {req_task_cols - set(df_task.columns)}")
    if not req_inc_cols.issubset(df_inc.columns):
        errors.append(f"incidents.csv missing columns: {req_inc_cols - set(df_inc.columns)}")

    # 2. Duplicate Primary Key Check
    if df_loc["location_id"].duplicated().any():
        errors.append(f"Duplicate location_id found in locations.csv: {df_loc[df_loc['location_id'].duplicated()]['location_id'].tolist()}")
    if df_inv["item_id"].duplicated().any():
        errors.append(f"Duplicate item_id found in inventory.csv: {df_inv[df_inv['item_id'].duplicated()]['item_id'].tolist()}")
    if df_task["task_id"].duplicated().any():
        errors.append(f"Duplicate task_id found in pick_tasks.csv: {df_task[df_task['task_id'].duplicated()]['task_id'].tolist()}")
    if df_inc["incident_id"].duplicated().any():
        errors.append(f"Duplicate incident_id found in incidents.csv: {df_inc[df_inc['incident_id'].duplicated()]['incident_id'].tolist()}")

    # Sets for foreign key checks
    all_locations = set(df_loc["location_id"])
    all_items = set(df_inv["item_id"])
    all_tasks = set(df_task["task_id"])

    # 3. Foreign Key Checks
    invalid_inv_locs = set(df_inv["location_id"]) - all_locations
    if invalid_inv_locs:
        errors.append(f"Inventory references non-existent locations: {invalid_inv_locs}")

    invalid_task_items = set(df_task["item_id"]) - all_items
    if invalid_task_items:
        errors.append(f"Pick tasks reference non-existent items: {invalid_task_items}")

    invalid_task_locs = set(df_task["expected_location"]) - all_locations
    if invalid_task_locs:
        errors.append(f"Pick tasks reference non-existent expected locations: {invalid_task_locs}")

    invalid_inc_tasks = set(df_inc["task_id"]) - all_tasks
    if invalid_inc_tasks:
        errors.append(f"Incidents reference non-existent task_ids: {invalid_inc_tasks}")

    invalid_inc_items = set(df_inc["item_id"]) - all_items
    if invalid_inc_items:
        errors.append(f"Incidents reference non-existent item_ids: {invalid_inc_items}")

    invalid_inc_locs = set(df_inc["location_id"]) - all_locations
    if invalid_inc_locs:
        errors.append(f"Incidents reference non-existent location_ids: {invalid_inc_locs}")

    # 4. Quantity Rules Check
    if (df_inv["system_quantity"] < 0).any():
        errors.append("Negative system_quantity found in inventory.csv")
    if (df_inv["available_quantity"] < 0).any():
        errors.append("Negative available_quantity found in inventory.csv")
    if (df_inv["reserved_quantity"] < 0).any():
        errors.append("Negative reserved_quantity found in inventory.csv")
    if (df_inv["available_quantity"] > df_inv["system_quantity"]).any():
        errors.append("available_quantity > system_quantity found in inventory.csv")
    if (df_inv["reserved_quantity"] > df_inv["system_quantity"]).any():
        errors.append("reserved_quantity > system_quantity found in inventory.csv")

    if (df_task["required_quantity"] < 0).any():
        errors.append("Negative required_quantity found in pick_tasks.csv")
    if (df_inc["observed_quantity"] < 0).any():
        errors.append("Negative observed_quantity found in incidents.csv")
    if (df_inc["expected_quantity"] < 0).any():
        errors.append("Negative expected_quantity found in incidents.csv")

    # 5. Exception Types Check
    invalid_exceptions = set(df_inc["exception_type"]) - VALID_EXCEPTION_TYPES
    if invalid_exceptions:
        errors.append(f"Invalid exception types in incidents.csv: {invalid_exceptions}")

    # Summary Report Printing
    print("================================")
    print("PickGuard Dataset Validation")
    print("")
    print(f"Locations: {'FAIL' if any('location' in e for e in errors) else 'PASS'}")
    print(f"Inventory: {'FAIL' if any('inventory' in e for e in errors) else 'PASS'}")
    print(f"Pick Tasks: {'FAIL' if any('task' in e for e in errors) else 'PASS'}")
    print(f"Incidents: {'FAIL' if any('incident' in e or 'exception' in e for e in errors) else 'PASS'}")
    print(f"Cross references: {'FAIL' if any('reference' in e or 'non-existent' in e for e in errors) else 'PASS'}")
    print(f"Quantity rules: {'FAIL' if any('quantity' in e for e in errors) else 'PASS'}")
    print(f"Exception types: {'FAIL' if any('exception types' in e for e in errors) else 'PASS'}")
    print("")
    
    if errors:
        print("Validation ERRORS:")
        for err in errors:
            print(f" - {err}")
        print("")
        print("Overall: FAIL")
        sys.exit(1)
    else:
        print("Overall: PASS")
        sys.exit(0)


if __name__ == "__main__":
    validate_datasets()
