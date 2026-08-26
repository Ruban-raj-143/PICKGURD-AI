import pytest
from backend.app.policy.action_policy import evaluate_action_policy, ALLOWED_ACTIONS, DISALLOWED_ACTIONS


def test_allowed_actions():
    """Test all authorized low-risk action vocabulary items return allowed=True."""
    for action in ALLOWED_ACTIONS.keys():
        res = evaluate_action_policy(action)
        assert res["allowed"] is True
        assert res["action_status"] in ["RECOMMENDED", "ESCALATED"]


def test_disallowed_actions():
    """Test all state-altering consequential actions return allowed=False and status=BLOCKED."""
    for action in DISALLOWED_ACTIONS.keys():
        res = evaluate_action_policy(action)
        assert res["allowed"] is False
        assert res["action_status"] == "BLOCKED"
        assert res["risk_level"] == "HIGH"
        assert res["requires_human_review"] is True


def test_unrecognized_action():
    """Test unrecognized action string returns allowed=False and status=BLOCKED."""
    res = evaluate_action_policy("UNAUTHORIZED_EXTERNAL_WMS_CALL")
    assert res["allowed"] is False
    assert res["action_status"] == "BLOCKED"
    assert res["risk_level"] == "HIGH"
    assert res["requires_human_review"] is True
