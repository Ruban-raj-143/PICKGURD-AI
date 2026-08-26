"""Pydantic schemas for RAG retrieval outputs and provenance metadata."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SOPEvidenceChunk(BaseModel):
    """Retrieved SOP evidence chunk with complete source provenance."""

    content: str = Field(description="Text content of the retrieved SOP section chunk")
    sop_id: str = Field(description="SOP document ID (e.g. SOP-MISSING-001)")
    version: str = Field(description="SOP document version (e.g. 1.0)")
    source: str = Field(description="Source markdown filename (e.g. missing_item.md)")
    section: str = Field(description="Heading section title (e.g. Verification Steps)")
    exception_type: str = Field(description="Associated exception type code")
    score: float = Field(description="Relevance similarity score (0.0 to 1.0)")


class SOPRetrievalResult(BaseModel):
    """Structured RAG response payload returned to operational tools and agent."""

    found: bool = Field(description="Whether relevant SOP evidence was found above score threshold")
    query: str = Field(description="Input search query string")
    exception_type: Optional[str] = Field(default=None, description="Exception type filter if applied")
    count: int = Field(default=0, description="Number of evidence chunks returned")
    results: List[SOPEvidenceChunk] = Field(default_factory=list, description="List of evidence chunks")
    message: Optional[str] = Field(default=None, description="Status or no-result message")
