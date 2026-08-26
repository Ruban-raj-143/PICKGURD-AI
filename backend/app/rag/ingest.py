"""Document ingestion pipeline for PickGuard AI SOP Knowledge Base.

Loads synthetic SOP markdown files, extracts YAML/header metadata, splits text into
section-aware chunks, generates HuggingFace embeddings, and persists vectors in ChromaDB.
Implements idempotent stable chunk IDs to prevent duplicate record explosion.
"""

import os
import re
import yaml
from typing import Any, Dict, List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb

from backend.app.rag.config import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    SOPS_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


class SOPIngestor:
    """Ingests synthetic SOP markdown documents into ChromaDB vector store."""

    def __init__(self, sops_dir: str = SOPS_DIR, chroma_dir: str = CHROMA_DB_DIR):
        self.sops_dir = os.path.abspath(sops_dir)
        self.chroma_dir = os.path.abspath(chroma_dir)
        self.embedding_fn = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "],
        )

    def _parse_frontmatter(self, file_path: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter and body text from markdown file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                except Exception:
                    pass

        filename = os.path.basename(file_path)
        metadata.setdefault("source", filename)

        return metadata, body

    def _split_into_sections(self, body: str) -> List[Tuple[str, str]]:
        """Split body text by markdown level-2 headers (## Section Name)."""
        sections = []
        pattern = r"(^|\n)##\s+(.+)"
        splits = re.split(pattern, body)

        current_section = "Overview"
        i = 0
        if splits[0].strip():
            sections.append((current_section, splits[0].strip()))
            i = 1

        while i < len(splits):
            if i + 2 < len(splits):
                section_title = splits[i + 1].strip() if splits[i + 1].strip() else "Procedure"
                section_content = splits[i + 2].strip() if i + 2 < len(splits) else ""
                sections.append((section_title, section_content))
                i += 3
            else:
                break

        if not sections:
            sections.append(("General Procedure", body))

        return sections

    def ingest(self) -> Dict[str, Any]:
        """Discover SOP markdown files, parse, chunk, embed, and upsert to ChromaDB."""
        if not os.path.exists(self.sops_dir):
            raise FileNotFoundError(f"SOPs directory not found: {self.sops_dir}")

        sop_files = [
            os.path.join(self.sops_dir, f)
            for f in os.listdir(self.sops_dir)
            if f.endswith(".md") and not f.startswith(".")
        ]

        if not sop_files:
            return {"documents_found": 0, "documents_processed": 0, "chunks_created": 0, "status": "NO_FILES"}

        os.makedirs(self.chroma_dir, exist_ok=True)
        client = chromadb.PersistentClient(path=self.chroma_dir)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "PickGuard AI Synthetic SOP Knowledge Base"},
        )

        all_ids = []
        all_documents = []
        all_metadatas = []

        total_chunks = 0

        for file_path in sorted(sop_files):
            meta, body = self._parse_frontmatter(file_path)
            sop_id = str(meta.get("sop_id", "SOP-UNKNOWN"))
            version = str(meta.get("version", "1.0"))
            source_file = os.path.basename(file_path)
            exc_type = str(meta.get("exception_type", "GENERAL"))

            sections = self._split_into_sections(body)

            doc_chunk_counter = 0

            for section_title, section_text in sections:
                if not section_text.strip():
                    continue

                chunks = self.text_splitter.split_text(section_text)
                sec_slug = re.sub(r"[^\w]+", "_", section_title.lower()).strip("_")
                if not sec_slug:
                    sec_slug = "section"

                for idx, chunk_text in enumerate(chunks):
                    doc_chunk_counter += 1
                    chunk_id = f"{sop_id}_{sec_slug}_{doc_chunk_counter}"

                    formatted_content = f"SOP {sop_id} [{exc_type}] - {section_title}:\n{chunk_text}"

                    chunk_meta = {
                        "sop_id": sop_id,
                        "version": version,
                        "source": source_file,
                        "exception_type": exc_type,
                        "section": section_title,
                    }

                    all_ids.append(chunk_id)
                    all_documents.append(formatted_content)
                    all_metadatas.append(chunk_meta)
                    total_chunks += 1

        if all_documents:
            embeddings = self.embedding_fn.embed_documents(all_documents)
            collection.upsert(
                ids=all_ids,
                documents=all_documents,
                embeddings=embeddings,
                metadatas=all_metadatas,
            )

        return {
            "documents_found": len(sop_files),
            "documents_processed": len(sop_files),
            "chunks_created": total_chunks,
            "vector_store": self.chroma_dir,
            "status": "SUCCESS",
        }
