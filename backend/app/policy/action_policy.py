"""Controlled action vocabulary and deterministic safety policy evaluation for PickGuard AI."""

from typing import Any, Dict

ALLOWED_ACTIONS = {
    "CHECK_LOCATION": {"risk_level": "LOW", "requires_human_review": False, "status": "RECOMMENDED"},
    "CHECK_NEIGHBOURING_LOCATION": {"risk_level": "LOW", "requires_human_review": False, "status": "RECOMMENDED"},
    "RE_SCAN_ITEM": {"risk_level": "LOW", "requires_human_review": False, "status": "RECOMMENDED"},
    "VERIFY_ITEM_IDENTITY": {"risk_level": "MEDIUM", "requires_human_review": False, "status": "RECOMMENDED"},
    "RECOUNT_QUANTITY": {"risk_level": "MEDIUM", "requires_human_review": True, "status": "RECOMMENDED"},
    "VERIFY_BARCODE": {"risk_level": "LOW", "requires_human_review": False, "status": "RECOMMENDED"},
    "REVIEW_RECENT_MOVEMENT": {"risk_level": "LOW", "requires_human_review": False, "status": "RECOMMENDED"},
    "REVIEW_SOP": {"risk_level": "LOW", "requires_human_review": False, "status": "RECOMMENDED"},
    "COLLECT_MORE_EVIDENCE": {"risk_level": "MEDIUM", "requires_human_review": True, "status": "RECOMMENDED"},
    "ESCALATE_TO_HUMAN": {"risk_level": "HIGH", "requires_human_review": True, "status": "ESCALATED"},
    "NO_ACTION": {"risk_level": "LOW", "requires_human_review": False, "status": "RECOMMENDED"},
}

DISALLOWED_ACTIONS = {
    "UPDATE_INVENTORY": "Consequential inventory modification is prohibited automatically.",
    "CHANGE_LOCATION": "Consequential WMS location mapping changes require human approval.",
    "CANCEL_ORDER": "Order line cancellation requires supervisor authorization.",
    "MODIFY_ORDER": "Order modifications require supervisor authorization.",
    "ADJUST_QUANTITY": "Inventory quantity adjustments are state-altering and require human review.",
    "DELETE_RECORD": "System record deletion is strictly prohibited.",
    "MARK_ITEM_DAMAGED": "Quarantine hold tagging requires manual inspection.",
}


def evaluate_action_policy(action_type: str) -> Dict[str, Any]:
    """Deterministically evaluate action type against PickGuard AI safety policy.

    Args:
        action_type: Action vocabulary string (e.g. 'CHECK_NEIGHBOURING_LOCATION', 'ADJUST_QUANTITY').

    Returns:
        Dict containing allowed, risk_level, action_status, requires_human_review, and policy reason.
    """
    action_clean = action_type.upper().strip()

    if action_clean in DISALLOWED_ACTIONS:
        return {
            "action_type": action_clean,
            "allowed": False,
            "risk_level": "HIGH",
            "action_status": "BLOCKED",
            "requires_human_review": True,
            "reason": DISALLOWED_ACTIONS[action_clean],
        }

    if action_clean in ALLOWED_ACTIONS:
        cfg = ALLOWED_ACTIONS[action_clean]
        return {
            "action_type": action_clean,
            "allowed": True,
            "risk_level": cfg["risk_level"],
            "action_status": cfg["status"],
            "requires_human_review": cfg["requires_human_review"],
            "reason": f"Action '{action_clean}' is an authorized low-risk verification step.",
        }

    # Unknown or unmapped action vocabulary fallback
    return {
        "action_type": action_clean,
        "allowed": False,
        "risk_level": "HIGH",
        "action_status": "BLOCKED",
        "requires_human_review": True,
        "reason": f"Action '{action_clean}' is not recognized in the authorized action vocabulary.",
    }
