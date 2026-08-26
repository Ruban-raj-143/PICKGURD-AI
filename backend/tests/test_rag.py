import pytest
from backend.app.rag.retriever import sop_retriever
from backend.app.tools.sop import search_sop


def test_rag_missing_item_query():
    """Test 1: Query 'item missing from expected location' retrieves MISSING_ITEM SOP."""
    res = search_sop(exception_type="MISSING_ITEM", query="item missing from expected location")
    assert res["found"] is True
    assert res["count"] > 0
    top = res["results"][0]
    assert top["sop_id"] == "SOP-MISSING-001"
    assert top["exception_type"] == "MISSING_ITEM"


def test_rag_quantity_mismatch_query():
    """Test 2: Query 'system says 10 but physical count is 6' retrieves QUANTITY_MISMATCH SOP."""
    res = search_sop(exception_type="QUANTITY_MISMATCH", query="system says 10 but physical count is 6")
    assert res["found"] is True
    assert res["count"] > 0
    top = res["results"][0]
    assert top["sop_id"] == "SOP-QTY-001"
    assert top["exception_type"] == "QUANTITY_MISMATCH"


def test_rag_barcode_failure_query():
    """Test 3: Query 'barcode won't scan' retrieves BARCODE_FAILURE SOP."""
    res = search_sop(exception_type="BARCODE_FAILURE", query="barcode won't scan")
    assert res["found"] is True
    assert res["count"] > 0
    top = res["results"][0]
    assert top["sop_id"] == "SOP-BARCODE-001"
    assert top["exception_type"] == "BARCODE_FAILURE"


def test_rag_wrong_item_query():
    """Test 4: Query 'wrong product in the bin' retrieves WRONG_ITEM SOP."""
    res = search_sop(exception_type="WRONG_ITEM", query="wrong product in the bin")
    assert res["found"] is True
    assert res["count"] > 0
    top = res["results"][0]
    assert top["sop_id"] == "SOP-WRONG-001"
    assert top["exception_type"] == "WRONG_ITEM"


def test_rag_damaged_item_query():
    """Test 5: Query 'item is physically damaged' retrieves DAMAGED_ITEM SOP."""
    res = search_sop(exception_type="DAMAGED_ITEM", query="item is physically damaged")
    assert res["found"] is True
    assert res["count"] > 0
    top = res["results"][0]
    assert top["sop_id"] == "SOP-DAMAGE-001"
    assert top["exception_type"] == "DAMAGED_ITEM"


def test_rag_location_discrepancy_query():
    """Test 6: Query 'item is stored in another location' retrieves LOCATION_DISCREPANCY SOP."""
    res = search_sop(exception_type="LOCATION_DISCREPANCY", query="item is stored in another location")
    assert res["found"] is True
    assert res["count"] > 0
    top = res["results"][0]
    assert top["sop_id"] == "SOP-LOC-001"
    assert top["exception_type"] == "LOCATION_DISCREPANCY"


def test_cross_category_ranking():
    """Test that a quantity mismatch query does NOT rank missing item SOP as top result."""
    res = search_sop(query="system count is 10 but observed count is 6 quantity mismatch")
    assert res["found"] is True
    top = res["results"][0]
    assert top["sop_id"] != "SOP-MISSING-001"
    assert top["sop_id"] == "SOP-QTY-001"


def test_provenance_metadata():
    """Test that every retrieved result retains complete provenance metadata."""
    res = search_sop(query="inspect damaged package torn tape")
    assert res["found"] is True
    for chunk in res["results"]:
        assert chunk["sop_id"] is not None and len(chunk["sop_id"]) > 0
        assert chunk["version"] is not None and len(chunk["version"]) > 0
        assert chunk["source"] is not None and len(chunk["source"]) > 0
        assert chunk["section"] is not None and len(chunk["section"]) > 0
        assert chunk["content"] is not None and len(chunk["content"]) > 0
        assert 0.0 <= chunk["score"] <= 1.0


def test_no_hallucination_unrelated_query():
    """Test that unrelated queries return found=False with no fake SOP results."""
    res = sop_retriever.search_sop(query="How do I make chocolate cake?", min_score=0.35)
    assert res["found"] is False
    assert res["count"] == 0
    assert "No sufficiently relevant SOP evidence was found" in res.get("message", "")
