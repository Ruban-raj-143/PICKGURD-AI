"""Pick task operational tool for PickGuard AI.

Provides deterministic lookup of pick task line assignments from synthetic warehouse datasets.
"""

from typing import Any, Dict
from langchain_core.tools import tool
from backend.app.services.data_store import data_store
from backend.app.models.tool_schemas import PickTaskResult


def get_pick_task(task_id: str) -> Dict[str, Any]:
    """Retrieve pick task details for a given task_id.

    Args:
        task_id: Unique task identifier (e.g. 'TASK-1001')

    Returns:
        Structured dictionary matching PickTaskResult schema.
    """
    if not task_id or not isinstance(task_id, str) or not task_id.strip():
        return PickTaskResult(
            found=False,
            error_code="INVALID_PARAMETER",
            message="Task ID must be a non-empty string.",
        ).model_dump()

    task_id = task_id.strip()
    rec = data_store.get_pick_task(task_id)
    if not rec:
        return PickTaskResult(
            found=False,
            task_id=task_id,
            error_code="TASK_NOT_FOUND",
            message=f"No pick task exists with ID {task_id}.",
        ).model_dump()

    return PickTaskResult(
        found=True,
        task_id=str(rec["task_id"]),
        order_id=str(rec["order_id"]),
        item_id=str(rec["item_id"]),
        expected_location=str(rec["expected_location"]),
        required_quantity=int(rec["required_quantity"]),
        priority=str(rec["priority"]),
        status=str(rec["status"]),
        created_at=str(rec["created_at"]),
        assigned_operator=str(rec["assigned_operator"]),
    ).model_dump()


@tool("get_pick_task")
def get_pick_task_tool(task_id: str) -> Dict[str, Any]:
    """Look up pick task line order details and required quantities for a task ID."""
    return get_pick_task(task_id)
