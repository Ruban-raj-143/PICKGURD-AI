"""Pydantic schema for PickGuard AI final decision object."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DecisionResult(BaseModel):
    """Structured decision output produced by PickGuard AI safety and fusion pipeline."""

    exception_type: str = Field(description="Primary exception classification code")
    root_cause: str = Field(description="Identified operational root cause")
    evidence_quality: str = Field(description="Evidence quality rating: STRONG, MODERATE, WEAK, or INSUFFICIENT")
    evidence_conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Detected evidence conflicts")
    next_best_action: str = Field(description="Recommended or required next operational step")
    action_type: str = Field(description="Action vocabulary code (e.g. CHECK_NEIGHBOURING_LOCATION, RECOUNT_QUANTITY)")
    action_status: str = Field(description="Action boundary status: RECOMMENDED, BLOCKED, or ESCALATED")
    risk_level: str = Field(description="Safety risk classification: LOW, MEDIUM, or HIGH")
    risk_reasons: List[str] = Field(default_factory=list, description="List of reasons triggering the risk classification")
    requires_human_review: bool = Field(default=False, description="Flag indicating human supervisor review requirement")
    review_reason: Optional[str] = Field(default=None, description="Detailed explanation why human review is required")
    reason: str = Field(description="Rationale explaining the decision and next best action")
    provenance: Dict[str, List[str]] = Field(default_factory=dict, description="Source provenance mapping for all facts")
