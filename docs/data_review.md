# PickGuard AI — Data Architecture & Dataset Review

> **Disclaimer:** All data in PickGuard AI is 100% synthetic demo data created for education and capstone demonstration. It does not contain Amazon internal records, customer data, or production operational logs.

---

## Synthetic Data Schema & Data Dictionary

### 1. Locations (`data/synthetic/locations.csv` & SQLite `locations` table)
- `location_id` (TEXT, PK): Fictional bin location identifier (e.g. `A15-B04`, `A20-B02`).
- `zone` (TEXT): Warehouse zone designation (`Z01`, `Z02`, `Z03`).
- `aisle` (TEXT): Aisle number (`A15`, `A20`).
- `shelf` (TEXT): Shelf level (`B04`, `B02`).
- `bin_status` (TEXT): Operational bin state (`ACTIVE`, `MAINTENANCE`, `FULL`).

### 2. Inventory (`data/synthetic/inventory.csv` & SQLite `inventory` table)
- `item_id` (TEXT, PK): Synthetic item SKU code (e.g. `X123`, `X124`, `X125`).
- `location_id` (TEXT, FK): Bin location identifier.
- `quantity` (INTEGER): System record on-hand unit balance.
- `lot_number` (TEXT): Synthetic lot tracking code (`LOT-9001`).
- `barcode` (TEXT): Barcode scanner payload string (`BAR-1001-X123`).

### 3. Pick Tasks (`data/synthetic/pick_tasks.csv` & SQLite `pick_tasks` table)
- `task_id` (TEXT, PK): Unique pick line task identifier (`TASK-1001`, `TASK-1003`).
- `order_id` (TEXT): Synthetic customer order ID (`ORD-5001`).
- `item_id` (TEXT): Item SKU code.
- `location_id` (TEXT): Bin location identifier.
- `quantity_requested` (INTEGER): Target line quantity to pick.
- `status` (TEXT): Task status (`PENDING`, `IN_PROGRESS`, `COMPLETED`).

### 4. Historical Incidents (`data/synthetic/incidents.csv` & SQLite `incidents` table)
- `incident_id` (TEXT, PK): Prior incident record code (`INC-0001`, `INC-0003`).
- `exception_type` (TEXT): Primary exception category.
- `resolution_summary` (TEXT): Historical resolution step executed.
- `outcome` (TEXT): Outcome metric (`RESOLVED`, `ESCALATED`).

### 5. Standard Operating Procedures (ChromaDB Collection `pickguard_sops`)
- 6 Markdown SOP files stored in `data/sops/`:
  - `SOP-MISSING-001.md` (Missing Item SOP)
  - `SOP-QTY-001.md` (Quantity Mismatch SOP)
  - `SOP-WRONG-001.md` (Wrong Item SOP)
  - `SOP-BARCODE-001.md` (Barcode Failure SOP)
  - `SOP-DAMAGED-001.md` (Damaged Item SOP)
  - `SOP-LOC-001.md` (Location Discrepancy SOP)
- Chunked via `RecursiveCharacterTextSplitter` (chunk size 500, overlap 50).
- Embedded using `all-MiniLM-L6-v2` in ChromaDB vector store.
