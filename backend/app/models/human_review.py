"""Pydantic schemas for LangGraph human-in-the-loop review decision payload."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_DECISIONS = ["APPROVE", "REJECT", "REQUEST_MORE_EVIDENCE", "ESCALATE"]


class HumanReviewDecision(BaseModel):
    """Structured decision payload submitted by a human supervisor to resume an interrupted graph."""

    decision: str = Field(description="Supervisor decision choice: APPROVE, REJECT, REQUEST_MORE_EVIDENCE, or ESCALATE")
    reviewer_note: Optional[str] = Field(default=None, description="Optional supervisor explanatory note")
    reviewer_id: str = Field(default="REVIEWER-DEMO-001", description="Identifier of the human supervisor")
    timestamp: Optional[str] = Field(default=None, description="Timestamp of the review decision")

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if v_upper not in ALLOWED_DECISIONS:
            raise ValueError(f"Invalid decision '{v}'. Allowed decisions are: {ALLOWED_DECISIONS}")
        return v_upper
