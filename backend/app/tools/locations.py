"""Location operational tool for PickGuard AI.

Provides deterministic lookup of bin locations, zones, capacities, and neighbouring bin IDs.
"""

from typing import Any, Dict
from langchain_core.tools import tool
from backend.app.services.data_store import data_store
from backend.app.models.tool_schemas import LocationResult


def get_location(location_id: str) -> Dict[str, Any]:
    """Retrieve location metadata and neighbouring bin locations for a given location_id.

    Args:
        location_id: Unique bin location identifier (e.g. 'A15-B04')

    Returns:
        Structured dictionary matching LocationResult schema.
    """
    if not location_id or not isinstance(location_id, str) or not location_id.strip():
        return LocationResult(
            found=False,
            error_code="INVALID_PARAMETER",
            message="Location ID must be a non-empty string.",
        ).model_dump()

    location_id = location_id.strip()
    rec = data_store.get_location(location_id)
    if not rec:
        return LocationResult(
            found=False,
            location_id=location_id,
            error_code="LOCATION_NOT_FOUND",
            message=f"No location record exists for location {location_id}.",
        ).model_dump()

    # Parse pipe-separated neighbouring locations string into a list
    raw_neighbours = str(rec.get("neighbouring_locations", ""))
    neighbours_list = [n.strip() for n in raw_neighbours.split("|") if n.strip()] if raw_neighbours else []

    return LocationResult(
        found=True,
        location_id=str(rec["location_id"]),
        zone=str(rec["zone"]),
        aisle=str(rec["aisle"]),
        rack=str(rec["rack"]),
        bin=str(rec["bin"]),
        status=str(rec["status"]),
        capacity=int(rec["capacity"]),
        neighbouring_locations=neighbours_list,
    ).model_dump()


@tool("get_location")
def get_location_tool(location_id: str) -> Dict[str, Any]:
    """Look up bin location coordinates, status, capacity, and adjacent bin IDs."""
    return get_location(location_id)
