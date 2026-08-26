"""Inventory operational tool for PickGuard AI.

Provides deterministic, read-only lookup of inventory records from synthetic warehouse datasets.
Strictly read-only; no modification functions exist.
"""

from typing import Any, Dict, Optional
from langchain_core.tools import tool
from backend.app.services.data_store import data_store
from backend.app.models.tool_schemas import InventoryResult


def get_inventory(item_id: str, location_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve inventory metadata, quantities, and status for a given item_id and optional location_id.

    Args:
        item_id: Unique item identifier (e.g. 'X123')
        location_id: Optional storage bin identifier (e.g. 'A15-B04')

    Returns:
        Structured dictionary matching InventoryResult schema.
    """
    if not item_id or not isinstance(item_id, str) or not item_id.strip():
        return InventoryResult(
            found=False,
            error_code="INVALID_PARAMETER",
            message="Item ID must be a non-empty string.",
        ).model_dump()

    item_id = item_id.strip()
    loc_id = location_id.strip() if location_id and isinstance(location_id, str) else None

    rec = data_store.get_inventory(item_id, loc_id)
    if not rec:
        msg = f"No inventory record exists for item {item_id}"
        if loc_id:
            msg += f" at location {loc_id}"
        return InventoryResult(
            found=False,
            item_id=item_id,
            location_id=loc_id,
            error_code="ITEM_NOT_FOUND",
            message=msg + ".",
        ).model_dump()

    return InventoryResult(
        found=True,
        item_id=str(rec["item_id"]),
        location_id=str(rec["location_id"]),
        sku=str(rec["sku"]),
        item_name=str(rec["item_name"]),
        category=str(rec["category"]),
        system_quantity=int(rec["system_quantity"]),
        available_quantity=int(rec["available_quantity"]),
        reserved_quantity=int(rec["reserved_quantity"]),
        inventory_status=str(rec["inventory_status"]),
        last_scan_timestamp=str(rec["last_scan_timestamp"]),
        last_movement_timestamp=str(rec["last_movement_timestamp"]),
    ).model_dump()


@tool("get_inventory")
def get_inventory_tool(item_id: str, location_id: Optional[str] = None) -> Dict[str, Any]:
    """Look up verified inventory quantities and metadata for an item ID and optional location ID."""
    return get_inventory(item_id, location_id)
