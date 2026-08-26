"""Pydantic API request and response schemas for PickGuard AI FastAPI REST service."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Request payload to initiate a new pick exception resolution run."""

    query: str = Field(description="Operator exception query in natural language", json_schema_extra={"example": "The item X123 is missing from A15-B04"})
    task_id: Optional[str] = Field(default=None, description="Optional Pick Task ID", json_schema_extra={"example": "TASK-1001"})
    item_id: Optional[str] = Field(default=None, description="Optional Item SKU", json_schema_extra={"example": "X123"})
    location_id: Optional[str] = Field(default=None, description="Optional Location ID", json_schema_extra={"example": "A15-B04"})
    order_id: Optional[str] = Field(default=None, description="Optional Order ID", json_schema_extra={"example": "ORD-5001"})


class AgentRunResponse(BaseModel):
    """Response payload returned upon initiating or retrieving an agent run."""

    run_id: str = Field(description="Unique identifier for the agent run")
    thread_id: str = Field(description="LangGraph thread persistence identifier")
    status: str = Field(description="Run status: COMPLETED, WAITING_FOR_HUMAN_REVIEW, RUNNING, or FAILED")
    exception_type: str = Field(description="Primary exception classification")
    secondary_exception_types: List[str] = Field(default_factory=list)
    risk_level: str = Field(description="Safety risk level: LOW, MEDIUM, or HIGH")
    next_best_action: str = Field(description="Recommended next best action")
    action_type: str = Field(description="Action vocabulary code")
    action_status: str = Field(description="Action boundary status: RECOMMENDED, BLOCKED, HUMAN_APPROVED_PENDING_EXECUTION, REJECTED_BY_HUMAN, ESCALATED")
    requires_human_review: bool = Field(description="Flag indicating whether human review is required")
    evidence_quality: str = Field(description="Evidence quality rating: STRONG, MODERATE, WEAK, or INSUFFICIENT")
    evidence_summary: Dict[str, Any] = Field(default_factory=dict, description="Synthesized evidence package")
    reasoning: Optional[str] = Field(default=None, description="Grounded explanation rationale")
    root_cause: Optional[str] = Field(default=None, description="Identified root cause")
    provenance: Dict[str, List[str]] = Field(default_factory=dict, description="Source provenance mapping")
    human_review_payload: Optional[Dict[str, Any]] = Field(default=None, description="Payload for human reviewer if waiting for review")
    audit_log: List[str] = Field(default_factory=list, description="Timestamped audit trail")


class HumanReviewRequest(BaseModel):
    """Request payload to submit a human supervisor decision for a paused run."""

    decision: str = Field(description="Supervisor decision: APPROVE, REJECT, REQUEST_MORE_EVIDENCE, or ESCALATE")
    reviewer_note: Optional[str] = Field(default=None, description="Optional explanatory note from reviewer")
    reviewer_id: str = Field(default="REVIEWER-DEMO-001", description="Identifier of human supervisor")


class HumanReviewResponse(BaseModel):
    """Response payload returned after submitting a human review decision."""

    run_id: str = Field(description="Agent run ID")
    thread_id: str = Field(description="LangGraph thread ID")
    status: str = Field(description="Updated run status")
    decision: str = Field(description="Submitted decision")
    action_status: str = Field(description="Updated action boundary status")
    final_decision: Optional[str] = Field(default=None, description="Final decision summary statement")
    audit_log: List[str] = Field(default_factory=list)


class AuditResponse(BaseModel):
    """Response payload returning complete audit trail for a run."""

    run_id: str = Field(description="Agent run ID")
    thread_id: str = Field(description="LangGraph thread ID")
    audit_log: List[str] = Field(default_factory=list)


class SystemStatusResponse(BaseModel):
    """Response payload detailing system health and component status."""

    status: str = Field(description="Overall system status: healthy or degraded")
    api_status: str = Field(default="healthy")
    langgraph_status: str = Field(default="healthy")
    rag_status: str = Field(default="healthy")
    llm_provider: str = Field(description="Active LLM provider (groq, ollama, or mimic)")
    model_name: str = Field(description="Active model name")
    tools_status: str = Field(default="healthy")
