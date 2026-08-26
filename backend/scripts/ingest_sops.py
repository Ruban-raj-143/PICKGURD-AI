"""CLI script to ingest synthetic SOP markdown documents into ChromaDB vector store."""

import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.rag.ingest import SOPIngestor


def main():
    print("====================================")
    print("PickGuard AI SOP Ingestion")
    print("")

    ingestor = SOPIngestor()
    result = ingestor.ingest()

    print(f"Documents found: {result['documents_found']}")
    print(f"Documents processed: {result['documents_processed']}")
    print(f"Chunks created: {result['chunks_created']}")
    print(f"Vector store: {result['vector_store']}")
    print(f"Status: {result['status']}")
    print("====================================")

    if result["status"] == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
