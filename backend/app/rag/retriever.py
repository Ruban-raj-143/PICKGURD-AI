"""RAG Retriever module for PickGuard AI SOP Knowledge Base.

Queries ChromaDB vector store using semantic similarity search with optional exception_type
metadata filtering and minimum relevance score thresholding.
"""

import os
from typing import Any, Dict, Optional
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings

from backend.app.rag.config import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    RAG_MIN_SCORE,
)
from backend.app.rag.schemas import SOPEvidenceChunk, SOPRetrievalResult


class SOPRetriever:
    """Retriever engine querying ChromaDB SOP vector database."""

    def __init__(self, chroma_dir: str = CHROMA_DB_DIR):
        self.chroma_dir = os.path.abspath(chroma_dir)
        self.embedding_fn = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection = None

    def _get_collection(self):
        """Lazy load ChromaDB collection."""
        if self._collection is None:
            if not os.path.exists(self.chroma_dir):
                return None
            self._client = chromadb.PersistentClient(path=self.chroma_dir)
            try:
                self._collection = self._client.get_collection(name=COLLECTION_NAME)
            except Exception:
                return None
        return self._collection

    def search_sop(
        self,
        exception_type: Optional[str] = None,
        query: str = "",
        top_k: int = 5,
        min_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Search SOP knowledge base for relevant procedure chunks.

        Args:
            exception_type: Optional exception classification code (e.g. 'MISSING_ITEM')
            query: Input search query string
            top_k: Maximum number of evidence chunks to return (default 5)
            min_score: Minimum relevance similarity score threshold (default RAG_MIN_SCORE)

        Returns:
            Structured dictionary matching SOPRetrievalResult schema.
        """
        threshold = min_score if min_score is not None else RAG_MIN_SCORE
        clean_query = query.strip() if query and isinstance(query, str) else ""
        clean_exc = exception_type.strip() if exception_type and isinstance(exception_type, str) else None

        if not clean_query and not clean_exc:
            return SOPRetrievalResult(
                found=False,
                query=query,
                exception_type=clean_exc,
                count=0,
                results=[],
                message="No search query or exception type provided.",
            ).model_dump()

        # If query is empty but exception_type provided, use exception_type as query text
        effective_query = clean_query if clean_query else f"{clean_exc} standard operating procedure procedure steps"

        collection = self._get_collection()
        if collection is None or collection.count() == 0:
            return SOPRetrievalResult(
                found=False,
                query=query,
                exception_type=clean_exc,
                count=0,
                results=[],
                message="SOP vector database is empty or not initialized.",
            ).model_dump()

        # Build metadata filter
        where_clause = None
        if clean_exc:
            where_clause = {"exception_type": clean_exc}

        query_embedding = self.embedding_fn.embed_query(effective_query)

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,  # Query extra candidates for threshold filtering
                where=where_clause,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            # Fallback if metadata filter yields no matches
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,
                include=["documents", "metadatas", "distances"],
            )

        if not results or not results["documents"] or not results["documents"][0]:
            return SOPRetrievalResult(
                found=False,
                query=query,
                exception_type=clean_exc,
                count=0,
                results=[],
                message="No relevant SOP evidence was found.",
            ).model_dump()

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0.5] * len(docs)

        evidence_chunks = []
        for doc, meta, dist in zip(docs, metas, distances):
            # Distance to Cosine Similarity conversion: similarity = 1.0 - (dist / 2.0)
            score = round(max(0.0, min(1.0, 1.0 - (dist / 2.0))), 3)

            # Strict relevance thresholding
            if score >= threshold:
                evidence_chunks.append(
                    SOPEvidenceChunk(
                        content=doc,
                        sop_id=str(meta.get("sop_id", "UNKNOWN")),
                        version=str(meta.get("version", "1.0")),
                        source=str(meta.get("source", "unknown.md")),
                        section=str(meta.get("section", "Procedure")),
                        exception_type=str(meta.get("exception_type", "GENERAL")),
                        score=score,
                    )
                )

        # Sort by score descending and take top_k
        evidence_chunks.sort(key=lambda c: c.score, reverse=True)
        top_results = evidence_chunks[:top_k]

        if not top_results:
            return SOPRetrievalResult(
                found=False,
                query=query,
                exception_type=clean_exc,
                count=0,
                results=[],
                message="No sufficiently relevant SOP evidence was found.",
            ).model_dump()

        return SOPRetrievalResult(
            found=True,
            query=query,
            exception_type=clean_exc,
            count=len(top_results),
            results=top_results,
        ).model_dump()


sop_retriever = SOPRetriever()
