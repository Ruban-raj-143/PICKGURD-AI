"""LangGraph state definition for PickGuard AI pick exception resolution graph."""

from typing import Any, Dict, List, Optional, TypedDict


class PickExceptionState(TypedDict, total=False):
    """Typed state representation for PickGuard AI pick exception resolution workflow.

    Maintains input parameters, extracted entities, exception classification,
    retrieved operational facts, SOP evidence, historical incident evidence,
    evidence package synthesis, evidence fusion, safety policy evaluation,
    next-best-action selection, action boundary enforcement, human-in-the-loop review,
    checkpointing attempts, audit logs, and status errors.
    """

    operator_query: str
    task_id: Optional[str]
    order_id: Optional[str]
    item_id: Optional[str]
    location_id: Optional[str]
    exception_type: str
    secondary_exception_types: List[str]
    operational_data: Dict[str, Any]
    sop_evidence: List[Dict[str, Any]]
    historical_evidence: List[Dict[str, Any]]
    evidence_summary: Dict[str, Any]
    evidence_quality: str
    evidence_conflicts: List[Dict[str, Any]]
    reasoning: str
    root_cause: str
    recommended_action: str
    supported_action: str
    action_type: str
    action_status: str
    next_best_action: str
    confidence: float
    risk_level: str
    risk_reasons: List[str]
    safety_policy_result: Dict[str, Any]
    action_boundary: str
    requires_human_review: bool
    review_reason: Optional[str]
    human_decision: Optional[str]
    final_decision: Optional[str]
    review_attempts: int
    escalation_id: Optional[str]
    provenance: Dict[str, List[str]]
    audit_log: List[str]
    provider: str
    model_name: str
    created_at: str
    updated_at: str
    errors: List[Dict[str, Any]]
