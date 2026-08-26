"""Pydantic schemas for PickGuard AI LLM reasoning agent output."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Structured reasoning output produced by the LLM agent from evidence package."""

    exception_type: str = Field(description="Primary exception classification code")
    root_cause: str = Field(description="Identified operational root cause")
    observed_facts: List[str] = Field(default_factory=list, description="Verified facts directly retrieved from tools")
    inferences: List[str] = Field(default_factory=list, description="Derived logical inferences from facts")
    evidence_gaps: List[str] = Field(default_factory=list, description="Missing or unverified operational information")
    recommended_action: str = Field(description="Evidence-grounded next best verification step")
    reason: str = Field(description="Rationale explaining why the action was recommended")
    fallback_action: str = Field(description="Conservative fallback step if primary action fails")
    confidence: float = Field(default=0.8, description="Qualitative confidence estimate (0.0 to 1.0)")
    risk_level: str = Field(default="LOW", description="Safety risk classification: LOW, MEDIUM, or HIGH")
    requires_human_review: bool = Field(default=False, description="Whether human supervisor review is required")
    supporting_evidence: List[str] = Field(default_factory=list, description="List of supporting evidence source names")
