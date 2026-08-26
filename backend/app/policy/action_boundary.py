"""Action Boundary module enforcing strict separation between recommendation and execution."""

from typing import Any, Dict


class ActionBoundary:
    """Enforces strict action boundaries to guarantee no consequential warehouse state mutations occur."""

    @staticmethod
    def enforce_boundary(action_type: str, policy_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recommendation and assert that execution is blocked for state-altering actions.

        Args:
            action_type: Action vocabulary identifier.
            policy_evaluation: Dict returned by evaluate_action_policy.

        Returns:
            Dict containing boundary metadata: action_boundary_status, execution_permitted, summary.
        """
        if not policy_evaluation.get("allowed", False):
            return {
                "action_boundary_status": "BLOCKED",
                "execution_permitted": False,
                "summary": f"Execution of '{action_type}' is BLOCKED by safety boundary. State modifications require human review.",
            }

        return {
            "action_boundary_status": "RECOMMENDED",
            "execution_permitted": False,  # Recommendations only; system never executes changes automatically in Phase 7
            "summary": f"Recommendation '{action_type}' is ALLOWED for operator decision support.",
        }
