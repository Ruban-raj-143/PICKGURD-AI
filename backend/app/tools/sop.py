"""SOP operational tool for PickGuard AI.

Connects the operational tool interface directly to the SOP RAG retriever module.
Queries ChromaDB vector store for evidence-grounded procedure chunks.
Does NOT call an LLM.
"""

from typing import Any, Dict, Optional
from langchain_core.tools import tool
from backend.app.rag.retriever import sop_retriever


def search_sop(
    exception_type: Optional[str] = None,
    query: str = "",
    top_k: int = 5,
) -> Dict[str, Any]:
    """Retrieve Standard Operating Procedure (SOP) guidance chunks matching exception_type or query.

    Args:
        exception_type: Optional exception classification code (e.g. 'MISSING_ITEM')
        query: Search query string (e.g. 'item missing from expected bin')
        top_k: Max evidence chunks to return (default 5)

    Returns:
        Structured dictionary matching SOPRetrievalResult schema.
    """
    return sop_retriever.search_sop(
        exception_type=exception_type,
        query=query,
        top_k=top_k,
    )


@tool("search_sop")
def search_sop_tool(
    exception_type: Optional[str] = None,
    query: str = "",
    top_k: int = 5,
) -> Dict[str, Any]:
    """Search SOP Knowledge Base for evidence-grounded procedure steps and verification criteria."""
    return search_sop(
        exception_type=exception_type,
        query=query,
        top_k=top_k,
    )
