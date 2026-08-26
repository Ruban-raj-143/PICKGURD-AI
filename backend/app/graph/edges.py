"""Conditional routing functions for PickGuard AI LangGraph workflow."""

from backend.app.graph.state import PickExceptionState


def route_after_classification(state: PickExceptionState) -> str:
    """Route workflow conditionally after exception classification.

    If exception_type is UNKNOWN, skip category-specific SOP retrieval
    and route directly to retrieve_historical_evidence.
    Otherwise, proceed to retrieve_sop_evidence.
    """
    exc_type = state.get("exception_type", "UNKNOWN")
    if exc_type == "UNKNOWN":
        return "skip_sop"
    return "retrieve_sop"


def route_after_human_review(state: PickExceptionState) -> str:
    """Route workflow conditionally after human review gate.

    If human reviewer requested more evidence (action_status == 'MORE_EVIDENCE_REQUIRED'),
    route to collect_additional_evidence.
    Otherwise, complete execution at END.
    """
    status = state.get("action_status")
    if status == "MORE_EVIDENCE_REQUIRED":
        return "collect_more_evidence"
    return "end_workflow"
