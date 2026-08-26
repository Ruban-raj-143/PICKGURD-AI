"""Data generator script for PickGuard AI synthetic warehouse datasets.

Generates realistic, internally consistent datasets for locations, inventory,
pick tasks, and historical incidents. Includes specific demo records for capstone scenarios.
"""

import os
import random
import csv
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)

random.seed(42)

# -----------------------------------------------------------------------------
# 1. GENERATE LOCATIONS DATASET (36 locations)
# -----------------------------------------------------------------------------
def generate_locations():
    locations = []
    
    # Specific Demo locations
    demo_locs = [
        {"location_id": "A15-B04", "zone": "Z01", "aisle": "A15", "rack": "R04", "bin": "B04", "status": "ACTIVE", "capacity": 20, "neighbouring_locations": "A15-B03|A15-B05"},
        {"location_id": "A15-B03", "zone": "Z01", "aisle": "A15", "rack": "R04", "bin": "B03", "status": "ACTIVE", "capacity": 20, "neighbouring_locations": "A15-B02|A15-B04"},
        {"location_id": "A15-B05", "zone": "Z01", "aisle": "A15", "rack": "R04", "bin": "B05", "status": "ACTIVE", "capacity": 25, "neighbouring_locations": "A15-B04|A15-B06"},
        {"location_id": "A15-B06", "zone": "Z01", "aisle": "A15", "rack": "R04", "bin": "B06", "status": "ACTIVE", "capacity": 25, "neighbouring_locations": "A15-B05|A15-B07"},
        {"location_id": "A12-B03", "zone": "Z01", "aisle": "A12", "rack": "R03", "bin": "B03", "status": "ACTIVE", "capacity": 15, "neighbouring_locations": "A12-B02|A12-B04"},
        {"location_id": "A12-B02", "zone": "Z01", "aisle": "A12", "rack": "R03", "bin": "B02", "status": "ACTIVE", "capacity": 15, "neighbouring_locations": "A12-B01|A12-B03"},
        {"location_id": "A12-B04", "zone": "Z01", "aisle": "A12", "rack": "R03", "bin": "B04", "status": "ACTIVE", "capacity": 15, "neighbouring_locations": "A12-B03|A12-B05"},
        {"location_id": "A20-B02", "zone": "Z02", "aisle": "A20", "rack": "R02", "bin": "B02", "status": "ACTIVE", "capacity": 30, "neighbouring_locations": "A20-B01|A20-B03"},
        {"location_id": "A20-B01", "zone": "Z02", "aisle": "A20", "rack": "R02", "bin": "B01", "status": "ACTIVE", "capacity": 30, "neighbouring_locations": "A20-B02"},
        {"location_id": "A20-B03", "zone": "Z02", "aisle": "A20", "rack": "R02", "bin": "B03", "status": "ACTIVE", "capacity": 30, "neighbouring_locations": "A20-B02|A20-B04"},
    ]
    
    existing_ids = {loc["location_id"] for loc in demo_locs}
    locations.extend(demo_locs)
    
    # Generate additional locations across Z01, Z02, Z03, Z04
    zones = ["Z01", "Z02", "Z03", "Z04"]
    statuses = ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "BLOCKED", "MAINTENANCE"]
    
    for z in zones:
        for aisle_num in range(1, 10):
            aisle_str = f"A{aisle_num:02d}"
            for rack_num in range(1, 6):
                rack_str = f"R{rack_num:02d}"
                for bin_num in range(1, 6):
                    bin_str = f"B{bin_num:02d}"
                    loc_id = f"{aisle_str}-{bin_str}"
                    if loc_id in existing_ids:
                        continue
                    
                    # Compute neighbors
                    neighbours = []
                    if bin_num > 1:
                        neighbours.append(f"{aisle_str}-B{bin_num-1:02d}")
                    if bin_num < 5:
                        neighbours.append(f"{aisle_str}-B{bin_num+1:02d}")
                    
                    locations.append({
                        "location_id": loc_id,
                        "zone": z,
                        "aisle": aisle_str,
                        "rack": rack_str,
                        "bin": bin_str,
                        "status": random.choice(statuses),
                        "capacity": random.choice([10, 15, 20, 25, 30, 50]),
                        "neighbouring_locations": "|".join(neighbours)
                    })
                    existing_ids.add(loc_id)
                    if len(locations) >= 36:
                        break
                if len(locations) >= 36:
                    break
            if len(locations) >= 36:
                break
        if len(locations) >= 36:
            break

    return locations

# -----------------------------------------------------------------------------
# 2. GENERATE INVENTORY DATASET (60 items)
# -----------------------------------------------------------------------------
PRODUCTS = [
    ("Wireless Ergonomic Mouse", "Electronics", "PERIPHERALS"),
    ("Ultra-Speed USB-C Cable 2m", "Electronics", "CABLES"),
    ("Adjustable Aluminium Laptop Stand", "Office", "ACCESSORIES"),
    ("Mechanical Gaming Keyboard RGB", "Electronics", "PERIPHERALS"),
    ("Shockproof Clear Phone Case", "Accessories", "CASES"),
    ("4K Braided HDMI Cable 3m", "Electronics", "CABLES"),
    ("Portable Bluetooth Speaker", "Electronics", "AUDIO"),
    ("HD Pro Webcam 1080p", "Electronics", "VIDEO"),
    ("65W Fast Power Adapter", "Electronics", "CHARGERS"),
    ("LED Dimmable Desk Lamp", "Office", "LIGHTING"),
    ("Noise-Cancelling Headphones", "Electronics", "AUDIO"),
    ("Ergonomic Desk Chair Cushion", "Office", "FURNITURE"),
    ("Vertical Wireless Mouse", "Electronics", "PERIPHERALS"),
    ("Magnetic Wireless Charger", "Electronics", "CHARGERS"),
    ("Screen Cleaning Kit", "Office", "MAINTENANCE"),
]

def generate_inventory(locations):
    inventory = []
    
    # Specific Demo items
    demo_items = [
        # Demo 1 Item
        {
            "item_id": "X123",
            "sku": "SKU-X123",
            "item_name": "Wireless Ergonomic Mouse",
            "category": "Electronics",
            "location_id": "A15-B04",
            "system_quantity": 3,
            "available_quantity": 3,
            "reserved_quantity": 0,
            "last_scan_timestamp": "2026-08-25T14:30:00Z",
            "last_movement_timestamp": "2026-08-24T09:15:00Z",
            "inventory_status": "AVAILABLE"
        },
        # Demo 1 Overflow / Neighbouring Location Stock
        {
            "item_id": "X123-OVERFLOW",
            "sku": "SKU-X123",  # Same SKU at neighbouring location A15-B05
            "item_name": "Wireless Ergonomic Mouse",
            "category": "Electronics",
            "location_id": "A15-B05",
            "system_quantity": 5,
            "available_quantity": 5,
            "reserved_quantity": 0,
            "last_scan_timestamp": "2026-08-25T15:00:00Z",
            "last_movement_timestamp": "2026-08-24T10:00:00Z",
            "inventory_status": "AVAILABLE"
        },
        # Demo 2 Item
        {
            "item_id": "X124",
            "sku": "SKU-X124",
            "item_name": "Ultra-Speed USB-C Cable 2m",
            "category": "Electronics",
            "location_id": "A12-B03",
            "system_quantity": 5,
            "available_quantity": 4,
            "reserved_quantity": 1,
            "last_scan_timestamp": "2026-08-25T11:20:00Z",
            "last_movement_timestamp": "2026-08-23T16:45:00Z",
            "inventory_status": "AVAILABLE"
        },
        # Demo 3 Item
        {
            "item_id": "X125",
            "sku": "SKU-X125",
            "item_name": "HD Pro Webcam 1080p",
            "category": "Electronics",
            "location_id": "A20-B02",
            "system_quantity": 10,
            "available_quantity": 8,
            "reserved_quantity": 2,
            "last_scan_timestamp": "2026-08-25T08:10:00Z",
            "last_movement_timestamp": "2026-08-22T13:00:00Z",
            "inventory_status": "AVAILABLE"
        }
    ]
    
    inventory.extend(demo_items)
    used_locations = {item["location_id"] for item in demo_items}
    location_list = [loc["location_id"] for loc in locations]
    
    base_time = datetime(2026, 8, 25, 12, 0, 0)
    
    item_counter = 126
    for i in range(56):
        item_id = f"X{item_counter}"
        sku = f"SKU-{item_id}"
        prod_name, cat, _ = PRODUCTS[i % len(PRODUCTS)]
        
        # Select location
        loc_id = location_list[i % len(location_list)]
        
        sys_qty = random.randint(2, 25)
        res_qty = random.randint(0, min(3, sys_qty))
        avail_qty = sys_qty - res_qty
        
        last_scan = (base_time - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%dT%H:%M:%SZ")
        last_move = (base_time - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        inv_status = random.choice(["AVAILABLE", "AVAILABLE", "AVAILABLE", "AVAILABLE", "DAMAGED", "HOLD", "DISCREPANCY"])
        
        inventory.append({
            "item_id": item_id,
            "sku": sku,
            "item_name": prod_name,
            "category": cat,
            "location_id": loc_id,
            "system_quantity": sys_qty,
            "available_quantity": avail_qty,
            "reserved_quantity": res_qty,
            "last_scan_timestamp": last_scan,
            "last_movement_timestamp": last_move,
            "inventory_status": inv_status
        })
        item_counter += 1
        
    return inventory

# -----------------------------------------------------------------------------
# 3. GENERATE PICK TASKS DATASET (45 tasks)
# -----------------------------------------------------------------------------
def generate_pick_tasks(inventory):
    tasks = []
    
    # Specific Demo tasks
    demo_tasks = [
        # Demo 1
        {
            "task_id": "TASK-1001",
            "order_id": "ORD-9001",
            "item_id": "X123",
            "expected_location": "A15-B04",
            "required_quantity": 3,
            "priority": "NORMAL",
            "status": "EXCEPTION",
            "created_at": "2026-08-26T05:00:00Z",
            "assigned_operator": "OP-101"
        },
        # Demo 2
        {
            "task_id": "TASK-1002",
            "order_id": "ORD-9002",
            "item_id": "X124",
            "expected_location": "A12-B03",
            "required_quantity": 1,
            "priority": "URGENT",
            "status": "EXCEPTION",
            "created_at": "2026-08-26T05:15:00Z",
            "assigned_operator": "OP-102"
        },
        # Demo 3
        {
            "task_id": "TASK-1003",
            "order_id": "ORD-9003",
            "item_id": "X125",
            "expected_location": "A20-B02",
            "required_quantity": 10,
            "priority": "HIGH",
            "status": "EXCEPTION",
            "created_at": "2026-08-26T05:30:00Z",
            "assigned_operator": "OP-103"
        }
    ]
    
    tasks.extend(demo_tasks)
    
    operators = ["OP-101", "OP-102", "OP-103", "OP-104", "OP-105", "OP-106"]
    priorities = ["LOW", "NORMAL", "NORMAL", "HIGH", "URGENT"]
    statuses = ["PENDING", "IN_PROGRESS", "EXCEPTION", "COMPLETED"]
    
    base_time = datetime(2026, 8, 26, 4, 0, 0)
    
    task_num = 1004
    order_num = 9004
    
    # Map item_id to location from inventory
    item_loc_map = {inv["item_id"]: (inv["location_id"], inv["system_quantity"]) for inv in inventory}
    item_ids = list(item_loc_map.keys())
    
    for i in range(42):
        task_id = f"TASK-{task_num}"
        order_id = f"ORD-{order_num}"
        item_id = item_ids[i % len(item_ids)]
        expected_loc, sys_qty = item_loc_map[item_id]
        
        req_qty = max(1, min(sys_qty, random.randint(1, 5)))
        prio = random.choice(priorities)
        stat = random.choice(statuses)
        op = random.choice(operators)
        created = (base_time + timedelta(minutes=i * 2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        tasks.append({
            "task_id": task_id,
            "order_id": order_id,
            "item_id": item_id,
            "expected_location": expected_loc,
            "required_quantity": req_qty,
            "priority": prio,
            "status": stat,
            "created_at": created,
            "assigned_operator": op
        })
        
        task_num += 1
        order_num += 1

    return tasks

# -----------------------------------------------------------------------------
# 4. GENERATE INCIDENT HISTORY DATASET (110 incidents)
# -----------------------------------------------------------------------------
def generate_incidents(locations, inventory, pick_tasks):
    incidents = []
    
    # Define exception patterns & resolutions
    EXCEPTION_TYPES = [
        "MISSING_ITEM",
        "QUANTITY_MISMATCH",
        "WRONG_ITEM",
        "BARCODE_FAILURE",
        "DAMAGED_ITEM",
        "LOCATION_DISCREPANCY"
    ]
    
    RESOLUTIONS = {
        "MISSING_ITEM": [
            ("Found item at neighbouring bin location.", "CHECK_NEIGHBOURING_LOCATION", 180),
            ("Item mislaid behind rack divider, returned to active bin.", "CHECK_NEIGHBOURING_LOCATION", 240),
            ("Bin empty, flagged for urgent cycle count refill.", "CYCLE_COUNT_FLAGGED", 300),
            ("Item located in secondary overflow bin.", "LOCATION_CORRECTION_REVIEW", 210)
        ],
        "QUANTITY_MISMATCH": [
            ("Physical count 4 units below system record. Cycle count initiated.", "INVENTORY_VERIFICATION", 300),
            ("Observed count verified with supervisor. Inventory adjusted.", "INVENTORY_VERIFICATION", 420),
            ("Multi-pack unbundled by previous operator causing unit count discrepancy.", "HUMAN_REVIEW_ESCALATED", 360),
            ("Physical quantity verified; system count updated after recount.", "INVENTORY_VERIFICATION", 250)
        ],
        "WRONG_ITEM": [
            ("Similar SKU placed in bin during morning putaway. Corrected SKU retrieved.", "ITEM_REPLACEMENT", 210),
            ("Incorrect item barcode scanned; verified correct item in bin.", "ITEM_REPLACEMENT", 180),
            ("Wrong variant stored in location. Relocated to correct zone.", "LOCATION_CORRECTION_REVIEW", 320)
        ],
        "BARCODE_FAILURE": [
            ("Scanned master carton barcode instead of item barcode. Alternate barcode verified.", "ALTERNATE_BARCODE_VERIFICATION", 120),
            ("Barcode label smudged. Scanned secondary 2D QR code.", "ALTERNATE_BARCODE_VERIFICATION", 90),
            ("Unreadable barcode label; replaced barcode sticker at station.", "ALTERNATE_BARCODE_VERIFICATION", 150)
        ],
        "DAMAGED_ITEM": [
            ("Packaging crushed in storage bin. Moved item to damage hold tote.", "DAMAGE_EXCEPTION", 240),
            ("Torn product seal observed. Product quarantined for inspection.", "DAMAGE_EXCEPTION", 200),
            ("Minor exterior box dent; customer permission granted for pick.", "DAMAGE_EXCEPTION", 180)
        ],
        "LOCATION_DISCREPANCY": [
            ("Item found in aisle A15-B05 instead of system location A15-B04.", "LOCATION_CORRECTION_REVIEW", 210),
            ("Putaway operator logged incorrect bin ID. Location mapping updated.", "LOCATION_CORRECTION_REVIEW", 270),
            ("Item transferred to Zone Z02 without WMS update.", "LOCATION_CORRECTION_REVIEW", 310)
        ]
    }
    
    operators = ["OP-101", "OP-102", "OP-103", "OP-104", "OP-105"]
    base_date = datetime(2026, 8, 1, 8, 0, 0)
    
    # Specific Demo Historical Incidents for Demo 1, Demo 2, Demo 3
    demo_incidents = [
        # Historical match for Demo 1 (MISSING_ITEM at A15-B04 resolved by CHECK_NEIGHBOURING_LOCATION)
        {
            "incident_id": "INC-0001",
            "task_id": "TASK-1001",
            "item_id": "X123",
            "location_id": "A15-B04",
            "exception_type": "MISSING_ITEM",
            "description": "Item X123 not visible in bin A15-B04. Found 3 units in adjacent bin A15-B05.",
            "observed_quantity": 0,
            "expected_quantity": 3,
            "previous_location": "A15-B04",
            "resolution": "Checked neighbouring bin A15-B05 and retrieved required quantity.",
            "resolution_category": "CHECK_NEIGHBOURING_LOCATION",
            "resolution_time_seconds": 195,
            "operator_id": "OP-101",
            "created_at": "2026-08-20T10:15:00Z"
        },
        # Historical match for Demo 2 (BARCODE_FAILURE / MISSING_ITEM at A12-B03)
        {
            "incident_id": "INC-0002",
            "task_id": "TASK-1002",
            "item_id": "X124",
            "location_id": "A12-B03",
            "exception_type": "BARCODE_FAILURE",
            "description": "Barcode label unreadable on SKU-X124. Scanned inner packaging barcode.",
            "observed_quantity": 1,
            "expected_quantity": 1,
            "previous_location": "A12-B03",
            "resolution": "Verified item identity using alternate serial number scanning.",
            "resolution_category": "ALTERNATE_BARCODE_VERIFICATION",
            "resolution_time_seconds": 140,
            "operator_id": "OP-102",
            "created_at": "2026-08-21T11:30:00Z"
        },
        # Historical match for Demo 3 (QUANTITY_MISMATCH at A20-B02)
        {
            "incident_id": "INC-0003",
            "task_id": "TASK-1003",
            "item_id": "X125",
            "location_id": "A20-B02",
            "exception_type": "QUANTITY_MISMATCH",
            "description": "System expected 10 units but physical count in bin was 6 units.",
            "observed_quantity": 6,
            "expected_quantity": 10,
            "previous_location": "A20-B02",
            "resolution": "Escalated to inventory supervisor for cycle count audit.",
            "resolution_category": "HUMAN_REVIEW_ESCALATED",
            "resolution_time_seconds": 450,
            "operator_id": "OP-103",
            "created_at": "2026-08-22T09:45:00Z"
        }
    ]
    
    incidents.extend(demo_incidents)
    
    # Map task/item/location
    task_list = list(pick_tasks)
    
    inc_num = 4
    for i in range(107):
        exc_type = EXCEPTION_TYPES[i % len(EXCEPTION_TYPES)]
        desc_template, res_cat, res_time = RESOLUTIONS[exc_type][i % len(RESOLUTIONS[exc_type])]
        
        task = task_list[i % len(task_list)]
        
        expected_qty = task["required_quantity"]
        if exc_type == "MISSING_ITEM":
            observed_qty = 0
        elif exc_type == "QUANTITY_MISMATCH":
            observed_qty = max(0, expected_qty - random.randint(1, 3))
        else:
            observed_qty = expected_qty
            
        created_dt = base_date + timedelta(days=random.randint(0, 24), hours=random.randint(0, 12), minutes=random.randint(0, 59))
        
        incidents.append({
            "incident_id": f"INC-{inc_num:04d}",
            "task_id": task["task_id"],
            "item_id": task["item_id"],
            "location_id": task["expected_location"],
            "exception_type": exc_type,
            "description": f"{exc_type}: {desc_template}",
            "observed_quantity": observed_qty,
            "expected_quantity": expected_qty,
            "previous_location": task["expected_location"],
            "resolution": f"Resolved via {res_cat.replace('_', ' ').lower()}.",
            "resolution_category": res_cat,
            "resolution_time_seconds": res_time + random.randint(-30, 30),
            "operator_id": random.choice(operators),
            "created_at": created_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        inc_num += 1
        
    return incidents

# -----------------------------------------------------------------------------
# MAIN GENERATION ROUTINE
# -----------------------------------------------------------------------------
def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    locations = generate_locations()
    inventory = generate_inventory(locations)
    pick_tasks = generate_pick_tasks(inventory)
    incidents = generate_incidents(locations, inventory, pick_tasks)
    
    # Save locations.csv
    loc_file = os.path.join(DATA_DIR, "locations.csv")
    with open(loc_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["location_id", "zone", "aisle", "rack", "bin", "status", "capacity", "neighbouring_locations"])
        writer.writeheader()
        writer.writerows(locations)
    print(f"Generated {len(locations)} locations -> {loc_file}")
    
    # Save inventory.csv
    inv_file = os.path.join(DATA_DIR, "inventory.csv")
    with open(inv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item_id", "sku", "item_name", "category", "location_id", "system_quantity", "available_quantity", "reserved_quantity", "last_scan_timestamp", "last_movement_timestamp", "inventory_status"])
        writer.writeheader()
        writer.writerows(inventory)
    print(f"Generated {len(inventory)} inventory records -> {inv_file}")
    
    # Save pick_tasks.csv
    task_file = os.path.join(DATA_DIR, "pick_tasks.csv")
    with open(task_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "order_id", "item_id", "expected_location", "required_quantity", "priority", "status", "created_at", "assigned_operator"])
        writer.writeheader()
        writer.writerows(pick_tasks)
    print(f"Generated {len(pick_tasks)} pick tasks -> {task_file}")
    
    # Save incidents.csv
    inc_file = os.path.join(DATA_DIR, "incidents.csv")
    with open(inc_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["incident_id", "task_id", "item_id", "location_id", "exception_type", "description", "observed_quantity", "expected_quantity", "previous_location", "resolution", "resolution_category", "resolution_time_seconds", "operator_id", "created_at"])
        writer.writeheader()
        writer.writerows(incidents)
    print(f"Generated {len(incidents)} incidents -> {inc_file}")

if __name__ == "__main__":
    main()
