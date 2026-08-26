import pytest
from backend.app.services.llm import get_llm_provider, MimicProvider


def test_mimic_provider_direct():
    """Test direct invocation of MimicProvider."""
    provider = MimicProvider()
    evidence = {
        "OBSERVED_FACTS": ["System inventory records 3 units at A15-B04."],
        "SOP_EVIDENCE": ["Check neighbouring bin A15-B05."],
        "HISTORICAL_EVIDENCE": ["Incident resolved via CHECK_NEIGHBOURING_LOCATION."],
    }
    output = provider.invoke("Missing item X123", "MISSING_ITEM", evidence)

    assert output.exception_type == "MISSING_ITEM"
    assert "A15-B05" in output.recommended_action
    assert output.confidence > 0.5
    assert output.risk_level == "LOW"


def test_get_llm_provider_mimic():
    """Test get_llm_provider with explicit 'mimic' request."""
    provider, meta = get_llm_provider("mimic")

    assert meta["provider"] == "mimic"
    assert meta["model_name"] == "deterministic-mimic"
    assert meta["provider_status"] == "success"


def test_get_llm_provider_fallback_without_groq_key(monkeypatch):
    """Test that requesting 'groq' without GROQ_API_KEY falls back cleanly to mimic."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    provider, meta = get_llm_provider("groq")

    assert meta["provider"] == "mimic"
    assert meta["provider_status"] == "fallback"


def test_get_llm_provider_invalid_name():
    """Test that requesting an invalid provider name falls back to mimic."""
    provider, meta = get_llm_provider("invalid_provider_999")

    assert meta["provider"] == "mimic"
    assert meta["provider_status"] == "fallback"
