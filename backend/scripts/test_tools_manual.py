"""Manual execution test script for PickGuard AI deterministic operational tools.

Runs an end-to-end operational tool execution cycle using synthetic DEMO 1 data
and prints a formatted report.
"""

import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.tools.pick_tasks import get_pick_task
from backend.app.tools.inventory import get_inventory
from backend.app.tools.locations import get_location
from backend.app.tools.incidents import search_similar_incidents
from backend.app.tools.escalation import create_escalation


def main():
    print("========================================")
    print("PickGuard AI Tool Test")
    print("")

    # 1. Test Pick Task
    task_res = get_pick_task("TASK-1001")
    task_status = "✓ TASK-1001 found" if task_res.get("found") else "✗ TASK-1001 failed"
    print("Pick Task")
    print(task_status)
    print("")

    # 2. Test Inventory
    inv_res = get_inventory("X123", "A15-B04")
    inv_status = "✓ X123 found" if inv_res.get("found") else "✗ X123 failed"
    print("Inventory")
    print(inv_status)
    print("")

    # 3. Test Location
    loc_res = get_location("A15-B04")
    loc_status = "✓ A15-B04 found" if loc_res.get("found") else "✗ A15-B04 failed"
    print("Location")
    print(loc_status)
    print("")

    # 4. Test Similar Incidents
    inc_res = search_similar_incidents(item_id="X123", location_id="A15-B04", exception_type="MISSING_ITEM", limit=5)
    inc_count = inc_res.get("count", 0)
    inc_status = f"✓ {inc_count} incidents found" if inc_count > 0 else "✗ 0 incidents found"
    print("Similar Incidents")
    print(inc_status)
    print("")

    # 5. Test Escalation
    esc_res = create_escalation(
        task_id="TASK-1001",
        exception_type="MISSING_ITEM",
        reason="Manual verification test.",
        evidence_summary="Observed 0 units at A15-B04.",
        recommended_action="Check neighbouring bin A15-B05.",
    )
    esc_id = esc_res.get("escalation_id", "")
    esc_status = f"✓ {esc_id} created" if esc_res.get("success") else "✗ Escalation creation failed"
    print("Escalation")
    print(esc_status)
    print("")

    all_passed = (
        task_res.get("found")
        and inv_res.get("found")
        and loc_res.get("found")
        and inc_count > 0
        and esc_res.get("success")
    )

    print("Overall:")
    if all_passed:
        print("TOOLS WORKING")
        sys.exit(0)
    else:
        print("TOOL FAILURE DETECTED")
        sys.exit(1)


if __name__ == "__main__":
    main()
