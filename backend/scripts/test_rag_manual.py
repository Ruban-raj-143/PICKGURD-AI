"""Manual execution test script for PickGuard AI SOP RAG retrieval pipeline."""

import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.rag.retriever import sop_retriever


def main():
    print("====================================")
    print("PickGuard AI — RAG Test")
    print("")

    test_cases = [
        ("The item is missing from A15-B04", "MISSING_ITEM", "SOP-MISSING-001"),
        ("system says 10 but physical count is 6", "QUANTITY_MISMATCH", "SOP-QTY-001"),
        ("barcode won't scan", "BARCODE_FAILURE", "SOP-BARCODE-001"),
        ("wrong product in the bin", "WRONG_ITEM", "SOP-WRONG-001"),
        ("item is physically damaged", "DAMAGED_ITEM", "SOP-DAMAGE-001"),
        ("item is stored in another location", "LOCATION_DISCREPANCY", "SOP-LOC-001"),
    ]

    all_passed = True

    for query, exc_type, expected_sop in test_cases:
        res = sop_retriever.search_sop(exception_type=exc_type, query=query, top_k=1)
        found = res.get("found", False)
        results = res.get("results", [])

        print(f"Query:\n\"{query}\"")
        print("")
        print(f"Exception:\n{exc_type}")
        print("")

        if found and results:
            top_chunk = results[0]
            print(f"Retrieved:\n{top_chunk.get('sop_id', 'N/A')}")
            print("")
            print(f"Section:\n{top_chunk.get('section', 'N/A')}")
            print("")
            print(f"Source:\n{top_chunk.get('source', 'N/A')}")
            print("")
            print(f"Score:\n{top_chunk.get('score', 0.0)}")
            print("")

            if top_chunk.get("sop_id") != expected_sop:
                print(f"WARNING: Expected {expected_sop}, got {top_chunk.get('sop_id')}")
        else:
            print("Retrieved:\nNONE (below threshold)")
            print("")
            all_passed = False

        print("------------------------------------")

    print("====================================")
    if all_passed:
        print("RAG STATUS: PASS")
        sys.exit(0)
    else:
        print("RAG STATUS: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
