"""Similar incidents operational tool for PickGuard AI.

Provides deterministic priority-ranked search over historical synthetic exception incidents.
"""

from typing import Any, Dict, Optional
from langchain_core.tools import tool
from backend.app.services.data_store import data_store
from backend.app.models.tool_schemas import IncidentItem, IncidentSearchResult


def search_similar_incidents(
    item_id: Optional[str] = None,
    location_id: Optional[str] = None,
    exception_type: Optional[str] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """Search historical synthetic exception incidents matching item_id, location_id, or exception_type.

    Ranking priority:
    1. Exact item + location + exception_type
    2. Exact item + exception_type
    3. Exact location + exception_type
    4. Exact exception_type

    Args:
        item_id: Optional item ID
        location_id: Optional location ID
        exception_type: Optional exception type code
        limit: Max number of incidents to return (default 5)

    Returns:
        Structured dictionary matching IncidentSearchResult schema.
    """
    clean_item = item_id.strip() if item_id and isinstance(item_id, str) and item_id.strip() else None
    clean_loc = location_id.strip() if location_id and isinstance(location_id, str) and location_id.strip() else None
    clean_exc = exception_type.strip() if exception_type and isinstance(exception_type, str) and exception_type.strip() else None

    if not clean_item and not clean_loc and not clean_exc:
        return IncidentSearchResult(
            count=0,
            incidents=[],
            error_code="MISSING_QUERY_PARAMS",
            message="At least one search parameter (item_id, location_id, or exception_type) must be provided.",
        ).model_dump()

    limit = max(1, min(limit, 50))
    raw_results = data_store.search_incidents(
        item_id=clean_item,
        location_id=clean_loc,
        exception_type=clean_exc,
        limit=limit,
    )

    incident_items = [
        IncidentItem(
            incident_id=str(r["incident_id"]),
            task_id=str(r["task_id"]),
            item_id=str(r["item_id"]),
            location_id=str(r["location_id"]),
            exception_type=str(r["exception_type"]),
            description=str(r["description"]),
            observed_quantity=int(r["observed_quantity"]),
            expected_quantity=int(r["expected_quantity"]),
            previous_location=str(r["previous_location"]),
            resolution=str(r["resolution"]),
            resolution_category=str(r["resolution_category"]),
            resolution_time_seconds=int(r["resolution_time_seconds"]),
            operator_id=str(r["operator_id"]),
            created_at=str(r["created_at"]),
        )
        for r in raw_results
    ]

    return IncidentSearchResult(
        count=len(incident_items),
        incidents=incident_items,
    ).model_dump()


@tool("search_similar_incidents")
def search_similar_incidents_tool(
    item_id: Optional[str] = None,
    location_id: Optional[str] = None,
    exception_type: Optional[str] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """Search historical incident resolutions for matching item, location, or exception type."""
    return search_similar_incidents(
        item_id=item_id,
        location_id=location_id,
        exception_type=exception_type,
        limit=limit,
    )
