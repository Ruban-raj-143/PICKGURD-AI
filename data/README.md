# PickGuard AI — Synthetic Warehouse Datasets

> [!IMPORTANT]
> **Mandatory Data Disclaimer:**
> "These datasets are synthetic educational/demo data and do not represent Amazon internal systems, processes, inventory, or operational records."

---

## 1. Overview & Purpose

The datasets in `data/` simulate fulfilment-centre operational state, storage topography, task queues, and historical exception resolutions for **PickGuard AI**.

They provide a structured, relational baseline that deterministic operational tools will query in Phase 3 to evaluate picking exceptions grounded in empirical warehouse evidence.

---

## 2. Dataset Files & Schema Descriptions

### A. Locations (`data/locations.csv`)
Defines physical storage bins, zones, and aisle topography within the synthetic fulfilment centre.

- **`location_id`**: Primary identifier for storage bin (e.g., `A15-B04`).
- **`zone`**: Functional storage area (`Z01`, `Z02`, `Z03`, `Z04`).
- **`aisle` / `rack` / `bin`**: Physical coordinates within zone.
- **`status`**: Bins state (`ACTIVE`, `BLOCKED`, `MAINTENANCE`).
- **`capacity`**: Maximum unit storage limit.
- **`neighbouring_locations`**: Pipe-separated IDs of adjacent physical bins (e.g., `A15-B03|A15-B05`).

### B. Inventory (`data/inventory.csv`)
Tracks stock levels, SKUs, product metadata, and inventory status per location.

- **`item_id`**: System item identifier (e.g., `X123`).
- **`sku`**: Stock Keeping Unit code (e.g., `SKU-X123`).
- **`item_name` / `category`**: Fictional product description and category.
- **`location_id`**: Foreign key to `locations.csv`.
- **`system_quantity`**: Total unit count recorded in system.
- **`available_quantity`**: Units unreserved and pickable (`available_quantity <= system_quantity`).
- **`reserved_quantity`**: Units allocated to active orders.
- **`inventory_status`**: Stock state (`AVAILABLE`, `DAMAGED`, `HOLD`, `DISCREPANCY`).

### C. Pick Tasks (`data/pick_tasks.csv`)
Represents order line picking assignments dispatched to fulfilment operators.

- **`task_id`**: Pick task primary key (e.g., `TASK-1001`).
- **`order_id`**: Order reference (e.g., `ORD-9001`).
- **`item_id`**: Foreign key to `inventory.csv`.
- **`expected_location`**: Foreign key to `locations.csv`.
- **`required_quantity`**: Target line pick quantity.
- **`priority`**: Task urgency (`LOW`, `NORMAL`, `HIGH`, `URGENT`).
- **`status`**: Execution status (`PENDING`, `IN_PROGRESS`, `EXCEPTION`, `COMPLETED`).
- **`assigned_operator`**: Fictional operator ID (`OP-101`, `OP-102`, etc.).

### D. Incidents History (`data/incidents.csv`)
Historical exception records and operational resolutions used as few-shot evidence and historical context.

- **`incident_id`**: Primary incident key (e.g., `INC-0001`).
- **`task_id` / `item_id` / `location_id`**: Cross-referenced operational entities.
- **`exception_type`**: One of 6 supported types:
  1. `MISSING_ITEM`
  2. `QUANTITY_MISMATCH`
  3. `WRONG_ITEM`
  4. `BARCODE_FAILURE`
  5. `DAMAGED_ITEM`
  6. `LOCATION_DISCREPANCY`
- **`description`**: Ground-truth summary of physical observation.
- **`observed_quantity` / `expected_quantity`**: Empirical count comparison.
- **`resolution` / `resolution_category`**: Standard operational action taken (e.g., `CHECK_NEIGHBOURING_LOCATION`, `INVENTORY_VERIFICATION`, `ALTERNATE_BARCODE_VERIFICATION`, `DAMAGE_EXCEPTION`, `LOCATION_CORRECTION_REVIEW`, `HUMAN_REVIEW_ESCALATED`).

---

## 3. Dataset Relationships Graph

```
locations
  └── stores ──► inventory
                    └── assigned to ──► pick_tasks
                                          └── generates ──► incidents
```

1. **Location** (`locations.csv`): Stores items in physical bin spaces.
2. **Item/Inventory** (`inventory.csv`): Belongs to a location and participates in pick tasks.
3. **Pick Task** (`pick_tasks.csv`): Specifies an item and expected location to pick.
4. **Exception Incident** (`incidents.csv`): Generated when picking encounters an exception; records historical resolution.

---

## 4. Deterministic Demo Scenarios

The datasets contain explicit high-value demo records reserved for final capstone demonstration:

### Demo 1 — Normal Case (`TASK-1001`)
- **Task ID:** `TASK-1001` | **Item ID:** `X123` | **Location:** `A15-B04` | **System Quantity:** `3`
- **Scenario:** Item reported missing from bin `A15-B04`.
- **Evidence Link:** Adjacent bin `A15-B05` contains matching inventory (`X123-OVERFLOW` / `SKU-X123`).
- **Target Resolution:** `CHECK_NEIGHBOURING_LOCATION` (bin `A15-B05`).

### Demo 2 — Edge Case (`TASK-1002`)
- **Task ID:** `TASK-1002` | **Item ID:** `X124` | **Location:** `A12-B03`
- **Scenario:** Item reported missing along with unreadable barcode scanning failures.
- **Target Resolution:** Dual-signal handling (`BARCODE_FAILURE` & `MISSING_ITEM`).

### Demo 3 — High-Risk Case (`TASK-1003`)
- **Task ID:** `TASK-1003` | **Item ID:** `X125` | **Location:** `A20-B02` | **System Quantity:** `10`
- **Scenario:** Observed quantity is `6` (4 units short).
- **Target Resolution:** `QUANTITY_MISMATCH`. Requires human supervisor review; system will **not** modify inventory automatically.

---

## 5. Tool Integration (Phase 3)

In Phase 3, these datasets will be queried deterministically by backend services:
- `LocationService`: Resolves physical coordinates and neighbouring bins.
- `InventoryService`: Checks current stock, reserved quantities, and status.
- `PickTaskService`: Retrieves task context and line requirements.
- `IncidentHistoryService`: Fetches past resolution patterns matching exception types.
