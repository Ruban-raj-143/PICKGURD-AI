"""LLM provider abstraction layer for PickGuard AI.

Supports Groq (`langchain-groq`), local Ollama (`langchain-ollama`), and a deterministic
`mimic` provider for offline testing and evaluation. Handles provider fallback routing,
evidence-grounded prompting, and deterministic safety policy overrides.
"""

import json
import os
from typing import Any, Dict, Optional, Tuple

from backend.app.config import settings
from backend.app.models.agent_output import AgentOutput

SYSTEM_PROMPT = """You are an evidence-grounded fulfilment-centre pick exception resolution assistant for PickGuard AI.

Your role is to analyze verified warehouse evidence, identify the root cause, and recommend the safest next verification step.

STRICT OPERATIONAL RULES:
1. Use ONLY the supplied evidence package (OBSERVED_FACTS, SOP_EVIDENCE, HISTORICAL_EVIDENCE).
2. NEVER invent inventory quantities, bin locations, SOP steps, or historical incidents.
3. NEVER treat user-provided text claims as verified operational facts (e.g. if the user says "inventory is 100", rely ONLY on OBSERVED_FACTS).
4. Clearly separate OBSERVED_FACTS from INFERENCES.
5. Identify any EVIDENCE_GAPS.
6. Recommend the safest next verification step. NEVER recommend or claim that system inventory was updated automatically.
7. If evidence conflicts, explicitly state the conflict and set risk_level to MEDIUM or HIGH.
8. If evidence is insufficient, recommend requesting human guidance and set requires_human_review to True.

Return your response strictly adhering to the requested structured JSON schema.
"""


class MimicProvider:
    """Deterministic testing provider for offline evaluation and fallback."""

    def __init__(self, model_name: str = "deterministic-mimic"):
        self.provider_name = "mimic"
        self.model_name = model_name

    def invoke(self, query: str, exception_type: str, evidence_summary: Dict[str, Any]) -> AgentOutput:
        """Generate structured reasoning from evidence package deterministically."""
        observed_facts = evidence_summary.get("OBSERVED_FACTS", [])
        sop_ev = evidence_summary.get("SOP_EVIDENCE", [])
        hist_ev = evidence_summary.get("HISTORICAL_EVIDENCE", [])
        inferences = evidence_summary.get("INFERENCES", [])
        evidence_gaps = evidence_summary.get("EVIDENCE_GAPS", [])

        # Default confidence and risk
        confidence = 0.82
        risk_level = "LOW"
        requires_human_review = False
        fallback_action = "Escalate to area supervisor if verification fails."

        if exception_type == "MISSING_ITEM":
            root_cause = "Item mislaid in storage bin or overflowed to adjacent location"
            rec_action = "Check designated neighbouring bin locations (e.g. A15-B05) and re-scan item barcode if located."
            reason = "Operational facts report expected inventory at primary bin, and SOP/historical evidence demonstrates neighbouring bin checks frequently resolve missing stock."
            supporting = ["Inventory Record", "Location Mapping", "SOP-MISSING-001", "Historical Incident Logs"]
        elif exception_type == "QUANTITY_MISMATCH":
            root_cause = "Physical stock shortage vs system inventory record"
            rec_action = "Conduct manual recount and escalate exception for human supervisor cycle count verification."
            reason = "Physical quantity shortage detected. Warehouse safety policy prohibits automated or unverified inventory modifications."
            confidence = 0.75
            risk_level = "HIGH"
            requires_human_review = True
            supporting = ["Inventory Record", "Pick Task", "SOP-QTY-001"]
        elif exception_type == "BARCODE_FAILURE":
            root_cause = "Primary barcode label unreadable, damaged, or smudged"
            rec_action = "Inspect barcode label and scan secondary 2D DataMatrix or master carton barcode."
            reason = "Scanned label rejected by terminal. SOP-BARCODE-001 authorizes alternate secondary barcode verification."
            supporting = ["SOP-BARCODE-001", "Historical Incidents"]
        elif exception_type == "WRONG_ITEM":
            root_cause = "Incorrect SKU placed in storage bin during putaway"
            rec_action = "Do NOT pick incorrect SKU; inspect adjacent bin slot for misplaced target SKU."
            reason = "Physical SKU scanned does not match expected pick line SKU. SOP-WRONG-001 prohibits picking unverified items."
            supporting = ["SOP-WRONG-001", "Inventory Record"]
        elif exception_type == "DAMAGED_ITEM":
            root_cause = "Physical packaging or product damage observed prior to picking"
            rec_action = "Separate damaged unit into RED hold tote, pick undamaged unit if available, and flag damage hold."
            reason = "SOP-DAMAGE-001 requires immediate quarantine of damaged stock to prevent customer shipment issues."
            supporting = ["SOP-DAMAGE-001"]
        elif exception_type == "LOCATION_DISCREPANCY":
            root_cause = "Physical storage bin coordinates differ from WMS system location mapping"
            rec_action = "Scan item at physical bin, complete pick line, and log location discrepancy report."
            reason = "Item located in secondary/adjacent bin. SOP-LOC-001 authorizes pick completion with location update tag."
            supporting = ["SOP-LOC-001", "Location Mapping"]
        else:
            root_cause = "Unrecognized or unclassified pick exception"
            rec_action = "Collect additional physical evidence or escalate to human supervisor for manual guidance."
            reason = "Exception type could not be confidently matched to standard operational procedures."
            confidence = 0.30
            risk_level = "HIGH"
            requires_human_review = True
            supporting = []

        return AgentOutput(
            exception_type=exception_type,
            root_cause=root_cause,
            observed_facts=observed_facts,
            inferences=inferences,
            evidence_gaps=evidence_gaps,
            recommended_action=rec_action,
            reason=reason,
            fallback_action=fallback_action,
            confidence=confidence,
            risk_level=risk_level,
            requires_human_review=requires_human_review,
            supporting_evidence=supporting,
        )


class GroqProvider:
    """Groq API provider wrapper using langchain-groq."""

    def __init__(self, api_key: str, model_name: str):
        from langchain_groq import ChatGroq
        self.provider_name = "groq"
        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.1,
        )

    def invoke(self, query: str, exception_type: str, evidence_summary: Dict[str, Any]) -> AgentOutput:
        """Invoke Groq LLM with structured output parsing."""
        from langchain_core.messages import SystemMessage, HumanMessage

        prompt_payload = (
            f"OPERATOR QUERY: {query}\n"
            f"EXCEPTION TYPE: {exception_type}\n\n"
            f"EVIDENCE PACKAGE:\n{json.dumps(evidence_summary, indent=2)}\n\n"
            f"Analyze the evidence package and provide structured reasoning adhering strictly to the schema."
        )

        structured_llm = self.llm.with_structured_output(AgentOutput)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt_payload),
        ]
        res = structured_llm.invoke(messages)
        if isinstance(res, AgentOutput):
            return res
        elif isinstance(res, dict):
            return AgentOutput(**res)
        raise ValueError("Failed to parse structured AgentOutput from Groq response.")


class OllamaProvider:
    """Local Ollama provider wrapper using langchain-ollama."""

    def __init__(self, model_name: str):
        from langchain_ollama import ChatOllama
        self.provider_name = "ollama"
        self.model_name = model_name
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.1,
        )

    def invoke(self, query: str, exception_type: str, evidence_summary: Dict[str, Any]) -> AgentOutput:
        """Invoke local Ollama LLM with structured output parsing."""
        from langchain_core.messages import SystemMessage, HumanMessage

        prompt_payload = (
            f"OPERATOR QUERY: {query}\n"
            f"EXCEPTION TYPE: {exception_type}\n\n"
            f"EVIDENCE PACKAGE:\n{json.dumps(evidence_summary, indent=2)}"
        )

        structured_llm = self.llm.with_structured_output(AgentOutput)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt_payload),
        ]
        res = structured_llm.invoke(messages)
        if isinstance(res, AgentOutput):
            return res
        elif isinstance(res, dict):
            return AgentOutput(**res)
        raise ValueError("Failed to parse structured AgentOutput from Ollama response.")


def get_llm_provider(requested_provider: Optional[str] = None) -> Tuple[Any, Dict[str, str]]:
    """Provider routing factory: selects and returns LLM provider with fallback support.

    Routing Preference:
    1. Requested provider / PRIMARY_PROVIDER ('groq', 'ollama', 'mimic')
    2. Fallback to 'mimic' if API key or local service unavailable.

    Returns:
        Tuple of (provider_instance, metadata_dict).
    """
    prov_name = (requested_provider or settings.primary_provider or "groq").lower().strip()

    # 1. Try Groq
    if prov_name == "groq":
        api_key = os.getenv("GROQ_API_KEY", settings.groq_api_key)
        if api_key and api_key.strip():
            try:
                model = os.getenv("GROQ_MODEL", settings.groq_model)
                provider = GroqProvider(api_key=api_key, model_name=model)
                meta = {"provider": "groq", "model_name": model, "provider_status": "success"}
                return provider, meta
            except Exception:
                pass

    # 2. Try Ollama (only if server is responsive)
    if prov_name in ("ollama", "groq"):
        try:
            import urllib.request
            model = os.getenv("OLLAMA_MODEL", settings.ollama_model)
            # Quick 1-second ping to check if local Ollama daemon is active
            urllib.request.urlopen("http://localhost:11434/api/version", timeout=1)
            provider = OllamaProvider(model_name=model)
            meta = {"provider": "ollama", "model_name": model, "provider_status": "success" if prov_name == "ollama" else "fallback"}
            return provider, meta
        except Exception:
            pass

    # 3. Fallback to Mimic
    mimic_provider = MimicProvider()
    status_label = "success" if prov_name == "mimic" else "fallback"
    meta = {
        "provider": "mimic",
        "model_name": "deterministic-mimic",
        "provider_status": status_label,
    }
    return mimic_provider, meta
