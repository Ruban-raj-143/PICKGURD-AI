"""RAG configuration settings for PickGuard AI SOP Retrieval System."""

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")
SOPS_DIR = os.path.join(BASE_DIR, "data", "sops")
COLLECTION_NAME = "pickguard_sops"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Configurable minimum similarity score threshold (0.0 to 1.0)
RAG_MIN_SCORE = 0.35

# Chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
