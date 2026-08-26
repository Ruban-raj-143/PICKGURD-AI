"""LangGraph node implementations for PickGuard AI pick exception workflow."""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from langgraph.types import interrupt

from backend.app.graph.state import PickExceptionState
from backend.app.models.human_review import ALLOWED_DECISIONS, HumanReviewDecision
from backend.app.policy.action_boundary import ActionBoundary
from backend.app.policy.action_policy import evaluate_action_policy
from backend.app.services.llm import get_llm_provider
from backend.app.tools.escalation import create_escalation
from backend.app.tools.inventory import get_inventory
from backend.app.tools.pick_tasks import get_pick_task
from backend.app.tools.locations import get_location
from backend.app.tools.incidents import search_similar_incidents
from backend.app.tools.sop import search_sop

MAX_REVIEW_ATTEMPTS = 2


# -----------------------------------------------------------------------------
# NODE 1: PARSE OPERATOR QUERY
# -----------------------------------------------------------------------------
def parse_operator_query(state: PickExceptionState) -> Dict[str, Any]:
    """Parse operator query text to extract task_id, item_id, location_id, and order_id."""
    query = state.get("operator_query", "") or ""
    audit_log = list(state.get("audit_log", []))
    errors = list(state.get("errors", []))

    # Regex patterns for deterministic identifier extraction
    task_match = re.search(r"\bTASK-\d+\b", query, re.IGNORECASE)
    order_match = re.search(r"\bORD-\d+\b", query, re.IGNORECASE)
    item_match = re.search(r"\bX\d+\b", query, re.IGNORECASE)
    loc_match = re.search(r"\b[A-Z]\d+-[A-Z]\d+\b", query, re.IGNORECASE)

    extracted_task = task_match.group(0).upper() if task_match else state.get("task_id")
    extracted_order = order_match.group(0).upper() if order_match else state.get("order_id")
    extracted_item = item_match.group(0).upper() if item_match else state.get("item_id")
    extracted_loc = loc_match.group(0).upper() if loc_match else state.get("location_id")

    audit_entry = (
        f"Query parsed: task_id={extracted_task}, item_id={extracted_item}, "
        f"location_id={extracted_loc}, order_id={extracted_order}"
    )
    audit_log.append(audit_entry)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "task_id": extracted_task,
        "order_id": extracted_order,
        "item_id": extracted_item,
        "location_id": extracted_loc,
        "audit_log": audit_log,
        "updated_at": now_str,
        "created_at": state.get("created_at") or now_str,
        "errors": errors,
    }


# -----------------------------------------------------------------------------
# NODE 2: CLASSIFY EXCEPTION
# -----------------------------------------------------------------------------
def classify_exception(state: PickExceptionState) -> Dict[str, Any]:
    """Classify the primary and secondary exception types using deterministic keyword logic."""
    query = (state.get("operator_query") or "").lower()
    audit_log = list(state.get("audit_log", []))

    keyword_patterns = {
        "MISSING_ITEM": ["missing", "empty", "not in bin", "cannot find", "can't find", "not present", "no item", "zero units", "absent"],
        "QUANTITY_MISMATCH": ["quantity mismatch", "count", "quantity", "units short", "mismatch", "expected 10", "says 10", "difference", "system quantity", "physical count"],
        "WRONG_ITEM": ["wrong item", "wrong product", "different sku", "incorrect sku", "scanned item mismatch", "wrong sku"],
        "BARCODE_FAILURE": ["barcode", "won't scan", "unreadable", "can't scan", "label damaged", "scanner failure", "scanning problem", "scan failure"],
        "DAMAGED_ITEM": ["damaged", "crushed", "broken", "leaking", "torn seal", "packaging dent", "dent", "leaking package"],
        "LOCATION_DISCREPANCY": ["wrong location", "another bin", "stored in", "aisle discrepancy", "location mismatch", "found in bin", "different bin"],
    }

    matched_categories = []
    for cat, keywords in keyword_patterns.items():
        if any(kw in query for kw in keywords):
            matched_categories.append(cat)

    if not matched_categories:
        primary_exc = "UNKNOWN"
        secondary_excs = []
    else:
        primary_exc = matched_categories[0]
        secondary_excs = matched_categories[1:]

    audit_entry = f"Exception classified: primary={primary_exc}, secondary={secondary_excs}"
    audit_log.append(audit_entry)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "exception_type": primary_exc,
        "secondary_exception_types": secondary_excs,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 3: FETCH OPERATIONAL EVIDENCE
# -----------------------------------------------------------------------------
def fetch_operational_evidence(state: PickExceptionState) -> Dict[str, Any]:
    """Fetch verified operational facts using Phase 3 deterministic tools."""
    task_id = state.get("task_id")
    item_id = state.get("item_id")
    location_id = state.get("location_id")
    audit_log = list(state.get("audit_log", []))
    errors = list(state.get("errors", []))

    operational_data: Dict[str, Any] = {}

    # 1. Fetch Pick Task
    if task_id:
        task_res = get_pick_task(task_id)
        if task_res.get("found"):
            operational_data["pick_task"] = task_res
            if not item_id and task_res.get("item_id"):
                item_id = task_res["item_id"]
            if not location_id and task_res.get("expected_location"):
                location_id = task_res["expected_location"]
        else:
            errors.append({"tool": "get_pick_task", "task_id": task_id, "error_code": task_res.get("error_code"), "message": task_res.get("message")})

    # 2. Fetch Inventory
    if item_id:
        inv_res = get_inventory(item_id, location_id)
        if inv_res.get("found"):
            operational_data["inventory"] = inv_res
            if not location_id and inv_res.get("location_id"):
                location_id = inv_res["location_id"]
        else:
            errors.append({"tool": "get_inventory", "item_id": item_id, "location_id": location_id, "error_code": inv_res.get("error_code"), "message": inv_res.get("message")})

    # 3. Fetch Location
    if location_id:
        loc_res = get_location(location_id)
        if loc_res.get("found"):
            operational_data["location"] = loc_res
        else:
            errors.append({"tool": "get_location", "location_id": location_id, "error_code": loc_res.get("error_code"), "message": loc_res.get("message")})

    audit_entry = f"Operational evidence fetched: keys={list(operational_data.keys())}, errors_count={len(errors)}"
    audit_log.append(audit_entry)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "item_id": item_id,
        "location_id": location_id,
        "operational_data": operational_data,
        "errors": errors,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 4: RETRIEVE SOP EVIDENCE
# -----------------------------------------------------------------------------
def retrieve_sop_evidence(state: PickExceptionState) -> Dict[str, Any]:
    """Retrieve procedural SOP evidence from RAG vector store."""
    exc_type = state.get("exception_type", "UNKNOWN")
    query = state.get("operator_query", "") or ""
    audit_log = list(state.get("audit_log", []))
    errors = list(state.get("errors", []))

    sop_evidence = []

    if exc_type == "UNKNOWN":
        audit_entry = "SOP retrieval skipped: exception_type is UNKNOWN"
        audit_log.append(audit_entry)
        return {
            "sop_evidence": [],
            "audit_log": audit_log,
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    try:
        rag_res = search_sop(exception_type=exc_type, query=query, top_k=5)
        if rag_res.get("found") and rag_res.get("results"):
            sop_evidence = rag_res["results"]
            audit_entry = f"SOP evidence retrieved: {len(sop_evidence)} chunks for {exc_type}"
        else:
            audit_entry = f"SOP evidence gap: no chunks found for {exc_type} above threshold"
            errors.append({"step": "retrieve_sop_evidence", "exception_type": exc_type, "message": rag_res.get("message")})
    except Exception as e:
        audit_entry = f"SOP retrieval error: {str(e)}"
        errors.append({"step": "retrieve_sop_evidence", "exception_type": exc_type, "error": str(e)})

    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "sop_evidence": sop_evidence,
        "errors": errors,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 5: RETRIEVE HISTORICAL EVIDENCE
# -----------------------------------------------------------------------------
def retrieve_historical_evidence(state: PickExceptionState) -> Dict[str, Any]:
    """Retrieve historical synthetic incident resolutions for similar exceptions."""
    item_id = state.get("item_id")
    location_id = state.get("location_id")
    exc_type = state.get("exception_type", "UNKNOWN")
    audit_log = list(state.get("audit_log", []))

    historical_evidence = []

    inc_res = search_similar_incidents(item_id=item_id, location_id=location_id, exception_type=exc_type, limit=5)
    if inc_res.get("count", 0) > 0:
        historical_evidence = inc_res.get("incidents", [])
        audit_entry = f"Historical evidence retrieved: {len(historical_evidence)} incidents"
    else:
        audit_entry = "Historical evidence gap: no past incidents found matching criteria"

    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "historical_evidence": historical_evidence,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 6: BUILD EVIDENCE PACKAGE
# -----------------------------------------------------------------------------
def build_evidence_package(state: PickExceptionState) -> Dict[str, Any]:
    """Synthesize operational facts, SOP chunks, and historical incidents into an evidence package."""
    op_data = state.get("operational_data", {})
    sop_ev = state.get("sop_evidence", [])
    hist_ev = state.get("historical_evidence", [])
    exc_type = state.get("exception_type", "UNKNOWN")
    errors = state.get("errors", [])
    audit_log = list(state.get("audit_log", []))

    # 1. OBSERVED FACTS
    observed_facts = []
    if "pick_task" in op_data:
        pt = op_data["pick_task"]
        observed_facts.append(f"Pick Task {pt.get('task_id')} requires item {pt.get('item_id')} at bin {pt.get('expected_location')} (required qty: {pt.get('required_quantity')}).")
    if "inventory" in op_data:
        inv = op_data["inventory"]
        observed_facts.append(f"System inventory records {inv.get('system_quantity')} units of {inv.get('item_name')} ({inv.get('item_id')}) at location {inv.get('location_id')} (status: {inv.get('inventory_status')}).")
    if "location" in op_data:
        loc = op_data["location"]
        neighbours = ", ".join(loc.get("neighbouring_locations", []))
        observed_facts.append(f"Storage bin {loc.get('location_id')} is in zone {loc.get('zone')}. Neighbouring bins: [{neighbours}].")
    if not observed_facts:
        observed_facts.append("No verified operational facts were retrieved from inventory or pick task databases.")

    # 2. SOP EVIDENCE
    sop_facts = []
    for chunk in sop_ev:
        sop_facts.append(f"[{chunk.get('sop_id')} v{chunk.get('version')} Section '{chunk.get('section')}']: {chunk.get('content')}")
    if not sop_facts:
        sop_facts.append("No SOP evidence retrieved above similarity score threshold.")

    # 3. HISTORICAL EVIDENCE
    hist_facts = []
    for inc in hist_ev:
        hist_facts.append(f"Incident {inc.get('incident_id')} ({inc.get('exception_type')}) resolved via {inc.get('resolution_category')}: '{inc.get('resolution')}'.")
    if not hist_facts:
        hist_facts.append("No matching historical incident logs found.")

    # 4. INFERENCES
    inferences = []
    if exc_type == "MISSING_ITEM" and "location" in op_data:
        neighbours = op_data["location"].get("neighbouring_locations", [])
        if neighbours:
            inferences.append(f"Stock for missing item may have overflowed or been mislaid into neighbouring bin(s): {neighbours}.")
    elif exc_type == "QUANTITY_MISMATCH":
        inferences.append("Physical shortage detected. System stock should be audited via supervisor cycle count rather than modified automatically.")
    elif exc_type == "BARCODE_FAILURE":
        inferences.append("Primary barcode unreadable. Secondary 2D DataMatrix or master carton barcode should be verified.")

    # 5. EVIDENCE GAPS
    evidence_gaps = []
    if exc_type == "UNKNOWN":
        evidence_gaps.append("Exception type could not be confidently classified (UNKNOWN).")
    if errors:
        for err in errors:
            evidence_gaps.append(f"Data lookup error: {err.get('message') or err.get('error_code')}")

    evidence_summary = {
        "OBSERVED_FACTS": observed_facts,
        "SOP_EVIDENCE": sop_facts,
        "HISTORICAL_EVIDENCE": hist_facts,
        "INFERENCES": inferences,
        "EVIDENCE_GAPS": evidence_gaps,
    }

    audit_entry = "Evidence package synthesized successfully"
    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "evidence_summary": evidence_summary,
        "provider": "deterministic",
        "model_name": "rule-based-classifier",
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 7: REASON OVER EVIDENCE (LLM REASONING NODE)
# -----------------------------------------------------------------------------
def reason_over_evidence(state: PickExceptionState) -> Dict[str, Any]:
    """Execute evidence-grounded LLM reasoning over the synthesized evidence package."""
    query = state.get("operator_query", "") or ""
    exc_type = state.get("exception_type", "UNKNOWN")
    ev_summary = state.get("evidence_summary", {})
    errors = list(state.get("errors", []))
    audit_log = list(state.get("audit_log", []))

    # Obtain LLM provider
    provider_inst, meta = get_llm_provider()

    try:
        agent_out = provider_inst.invoke(query, exc_type, ev_summary)
    except Exception as e:
        # LLM Provider Failure Fallback
        meta["provider_status"] = "failed"
        errors.append({"step": "reason_over_evidence", "error": str(e)})

        # Conservative Fallback AgentOutput
        agent_out = get_llm_provider("mimic")[0].invoke(query, exc_type, ev_summary)
        agent_out.confidence = 0.0
        agent_out.risk_level = "HIGH"
        agent_out.requires_human_review = True
        agent_out.recommended_action = "Human review required because automated reasoning is unavailable"
        agent_out.reason = f"Provider failure ({meta['provider']}): {str(e)}"

    # -------------------------------------------------------------------------
    # DETERMINISTIC SAFETY POLICY OVERRIDES
    # -------------------------------------------------------------------------
    query_lower = query.lower()

    # Rule 1: Prompt Injection / Inventory Alteration Request Protection
    if any(kw in query_lower for kw in ["update", "change quantity", "set count", "ignore", "override", "pretend", "bypass"]):
        agent_out.risk_level = "HIGH"
        agent_out.requires_human_review = True
        agent_out.recommended_action = "Escalate for human supervisor review and cycle count audit."
        agent_out.reason = "Warehouse safety policy strictly prohibits automated inventory modifications or unverified quantity adjustments."
        if any(kw in query_lower for kw in ["ignore", "pretend", "override", "bypass"]):
            agent_out.inferences.append("User prompt injection attempt detected and rejected; relying strictly on tool evidence.")

    # Rule 2: Quantity Mismatch Mandatory High-Risk Policy
    if exc_type == "QUANTITY_MISMATCH":
        agent_out.risk_level = "HIGH"
        agent_out.requires_human_review = True
        if "update inventory" in agent_out.recommended_action.lower():
            agent_out.recommended_action = "Conduct physical recount and submit exception for human supervisor cycle count audit."

    # Rule 3: Missing Data or Data Errors Policy
    if errors or exc_type == "UNKNOWN":
        agent_out.requires_human_review = True
        if agent_out.confidence > 0.5:
            agent_out.confidence = 0.40

    audit_entry = (
        f"Reasoning completed via provider={meta['provider']} (model={meta['model_name']}, "
        f"status={meta['provider_status']}, risk={agent_out.risk_level}, human_review={agent_out.requires_human_review})"
    )
    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "reasoning": agent_out.reason,
        "root_cause": agent_out.root_cause,
        "recommended_action": agent_out.recommended_action,
        "confidence": agent_out.confidence,
        "risk_level": agent_out.risk_level,
        "requires_human_review": agent_out.requires_human_review,
        "provider": meta["provider"],
        "model_name": meta["model_name"],
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 8: FUSE EVIDENCE
# -----------------------------------------------------------------------------
def fuse_evidence(state: PickExceptionState) -> Dict[str, Any]:
    """Evaluate evidence quality and assemble source provenance mapping."""
    op_data = state.get("operational_data", {})
    sop_ev = state.get("sop_evidence", [])
    hist_ev = state.get("historical_evidence", [])
    errors = state.get("errors", [])
    audit_log = list(state.get("audit_log", []))

    has_op = bool(op_data and len(op_data) > 0)
    has_sop = bool(sop_ev and len(sop_ev) > 0)
    has_hist = bool(hist_ev and len(hist_ev) > 0)

    # 1. Calculate Evidence Quality
    if errors and not (has_op or has_sop):
        quality = "INSUFFICIENT"
    elif has_op and has_sop and has_hist:
        quality = "STRONG"
    elif (has_op and has_sop) or (has_sop and has_hist) or (has_op and has_hist):
        quality = "STRONG"
    elif has_op and has_sop:
        quality = "MODERATE"
    elif has_op or has_sop or has_hist:
        quality = "WEAK"
    else:
        quality = "INSUFFICIENT"

    # 2. Build Provenance Mapping
    provenance = {
        "operational": [],
        "sop": [],
        "historical": [],
    }

    if "pick_task" in op_data:
        provenance["operational"].append(f"Pick Task: {op_data['pick_task'].get('task_id')}")
    if "inventory" in op_data:
        inv = op_data["inventory"]
        provenance["operational"].append(f"Inventory: {inv.get('item_id')} @ {inv.get('location_id')} ({inv.get('system_quantity')} units)")
    if "location" in op_data:
        loc = op_data["location"]
        provenance["operational"].append(f"Location Mapping: {loc.get('location_id')} (Zone {loc.get('zone')})")

    for chunk in sop_ev:
        provenance["sop"].append(f"{chunk.get('sop_id')} v{chunk.get('version')} Section '{chunk.get('section')}'")

    for inc in hist_ev:
        provenance["historical"].append(f"Incident {inc.get('incident_id')} ({inc.get('resolution_category')})")

    audit_entry = f"Evidence fused: quality={quality}, op_sources={len(provenance['operational'])}, sop_sources={len(provenance['sop'])}, hist_sources={len(provenance['historical'])}"
    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "evidence_quality": quality,
        "provenance": provenance,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 9: DETECT EVIDENCE CONFLICTS
# -----------------------------------------------------------------------------
def detect_evidence_conflicts(state: PickExceptionState) -> Dict[str, Any]:
    """Detect discrepancies between system records, operator query observations, and SOP expectations."""
    query = (state.get("operator_query") or "").lower()
    op_data = state.get("operational_data", {})
    exc_type = state.get("exception_type", "UNKNOWN")
    audit_log = list(state.get("audit_log", []))

    conflicts: List[Dict[str, Any]] = []

    # 1. Quantity Conflict Detection
    if exc_type == "QUANTITY_MISMATCH" or "count" in query or "says 10" in query:
        inv = op_data.get("inventory", {})
        sys_qty = inv.get("system_quantity")
        conflicts.append({
            "type": "QUANTITY_CONFLICT",
            "description": f"Physical observation differs from system inventory record (system reports {sys_qty} units).",
            "severity": "HIGH",
        })

    # 2. Location Conflict Detection
    if exc_type == "LOCATION_DISCREPANCY" or "another bin" in query or "different location" in query:
        pt = op_data.get("pick_task", {})
        exp_loc = pt.get("expected_location") or state.get("location_id")
        conflicts.append({
            "type": "LOCATION_CONFLICT",
            "description": f"Physical item location differs from system bin assignment ({exp_loc}).",
            "severity": "MEDIUM",
        })

    # 3. SKU / Wrong Item Conflict Detection
    if exc_type == "WRONG_ITEM" or "different sku" in query or "wrong item" in query:
        pt = op_data.get("pick_task", {})
        exp_sku = pt.get("item_id") or state.get("item_id")
        conflicts.append({
            "type": "SKU_CONFLICT",
            "description": f"Scanned/observed physical item SKU differs from expected pick line SKU ({exp_sku}).",
            "severity": "HIGH",
        })

    audit_entry = f"Evidence conflicts detected: count={len(conflicts)}"
    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "evidence_conflicts": conflicts,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 10: SELECT NEXT BEST ACTION
# -----------------------------------------------------------------------------
def select_next_best_action(state: PickExceptionState) -> Dict[str, Any]:
    """Deterministically select the next best verification step from authorized action vocabulary."""
    exc_type = state.get("exception_type", "UNKNOWN")
    query = (state.get("operator_query") or "").lower()
    audit_log = list(state.get("audit_log", []))

    # Priority Action Selection Rules
    if any(kw in query for kw in ["update", "change quantity", "set count", "ignore", "override"]):
        action_type = "ADJUST_QUANTITY"  # Will be evaluated and BLOCKED by safety policy
        next_best = "RECOUNT_QUANTITY"
    elif exc_type == "MISSING_ITEM":
        action_type = "CHECK_NEIGHBOURING_LOCATION"
        next_best = "CHECK_NEIGHBOURING_LOCATION"
    elif exc_type == "QUANTITY_MISMATCH":
        action_type = "RECOUNT_QUANTITY"
        next_best = "RECOUNT_QUANTITY"
    elif exc_type == "BARCODE_FAILURE":
        action_type = "VERIFY_BARCODE"
        next_best = "VERIFY_BARCODE"
    elif exc_type == "WRONG_ITEM":
        action_type = "VERIFY_ITEM_IDENTITY"
        next_best = "VERIFY_ITEM_IDENTITY"
    elif exc_type == "DAMAGED_ITEM":
        action_type = "REVIEW_SOP"
        next_best = "REVIEW_SOP"
    elif exc_type == "LOCATION_DISCREPANCY":
        action_type = "CHECK_LOCATION"
        next_best = "CHECK_LOCATION"
    else:
        action_type = "COLLECT_MORE_EVIDENCE"
        next_best = "COLLECT_MORE_EVIDENCE"

    audit_entry = f"Next-best action selected: action_type={action_type}, next_best_action={next_best}"
    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "action_type": action_type,
        "next_best_action": next_best,
        "supported_action": next_best,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 11: APPLY SAFETY POLICY
# -----------------------------------------------------------------------------
def apply_safety_policy(state: PickExceptionState) -> Dict[str, Any]:
    """Evaluate candidate action against deterministic safety policy and enforce explicit action boundary."""
    action_type = state.get("action_type", "COLLECT_MORE_EVIDENCE")
    next_best = state.get("next_best_action", "COLLECT_MORE_EVIDENCE")
    ev_quality = state.get("evidence_quality", "WEAK")
    conflicts = state.get("evidence_conflicts", [])
    errors = state.get("errors", [])
    exc_type = state.get("exception_type", "UNKNOWN")
    audit_log = list(state.get("audit_log", []))

    # Evaluate deterministic action policy
    policy_res = evaluate_action_policy(action_type)
    boundary_res = ActionBoundary.enforce_boundary(action_type, policy_res)

    risk_reasons = []
    requires_human_review = policy_res.get("requires_human_review", False)
    risk_level = policy_res.get("risk_level", "LOW")
    action_status = boundary_res.get("action_boundary_status", "RECOMMENDED")

    # Risk Escalation Rules
    if not policy_res.get("allowed", False):
        risk_level = "HIGH"
        requires_human_review = True
        risk_reasons.append(f"Consequential action '{action_type}' is BLOCKED automatically.")
        # Override proposed blocked action to safe verification step
        next_best = "RECOUNT_QUANTITY" if exc_type == "QUANTITY_MISMATCH" else "ESCALATE_TO_HUMAN"

    if conflicts:
        risk_level = "HIGH" if any(c.get("severity") == "HIGH" for c in conflicts) else "MEDIUM"
        requires_human_review = True
        risk_reasons.append(f"Evidence conflicts detected ({len(conflicts)} active conflicts).")

    if ev_quality in ("WEAK", "INSUFFICIENT"):
        requires_human_review = True
        risk_reasons.append(f"Evidence quality is {ev_quality}.")

    if errors:
        requires_human_review = True
        risk_reasons.append("Tool data lookup errors occurred.")

    review_reason = "; ".join(risk_reasons) if requires_human_review else None

    if action_status == "BLOCKED":
        audit_entry = f"Safety policy evaluated: action={action_type} BLOCKED -> next_best={next_best}, risk=HIGH, human_review=True"
    else:
        audit_entry = f"Safety policy evaluated: action={action_type} ALLOWED -> status={action_status}, risk={risk_level}, human_review={requires_human_review}"

    audit_log.append(audit_entry)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "action_type": action_type,
        "action_status": action_status,
        "next_best_action": next_best,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "safety_policy_result": policy_res,
        "action_boundary": boundary_res.get("summary", ""),
        "requires_human_review": requires_human_review,
        "review_reason": review_reason,
        "audit_log": audit_log,
        "updated_at": now_str,
    }


# -----------------------------------------------------------------------------
# NODE 12: HUMAN REVIEW GATE (LANGGRAPH INTERRUPT CHECKPOINT)
# -----------------------------------------------------------------------------
def human_review_gate(state: PickExceptionState) -> Dict[str, Any]:
    """LangGraph interrupt checkpoint pausing high-risk decisions for human supervisor review."""
    requires_review = state.get("requires_human_review", False)
    audit_log = list(state.get("audit_log", []))
    attempts = state.get("review_attempts", 0)

    # If low risk / review not required, pass through normally
    if not requires_review:
        return {"audit_log": audit_log, "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

    # Max Review Attempts Enforced -> Auto Escalate
    if attempts >= MAX_REVIEW_ATTEMPTS:
        esc_res = create_escalation(
            task_id=state.get("task_id", "N/A"),
            exception_type=state.get("exception_type", "UNKNOWN"),
            reason=f"Exceeded maximum human review attempts ({MAX_REVIEW_ATTEMPTS}). Automatic escalation triggered.",
            evidence_summary="Multiple review cycles completed without resolution.",
            recommended_action=state.get("next_best_action", "ESCALATE_TO_HUMAN"),
        )
        audit_log.append(f"Max review attempts ({MAX_REVIEW_ATTEMPTS}) reached -> Auto escalated to supervisor queue (Escalation ID: {esc_res.get('escalation_id')})")
        return {
            "action_type": "ESCALATE_TO_HUMAN",
            "action_status": "ESCALATED",
            "requires_human_review": False,
            "escalation_id": esc_res.get("escalation_id"),
            "final_decision": f"Maximum review attempts reached. Escalated to supervisor (ID: {esc_res.get('escalation_id')}).",
            "audit_log": audit_log,
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    # Build interrupt payload with full decision context
    payload = {
        "type": "human_review_required",
        "task_id": state.get("task_id", "N/A"),
        "exception_type": state.get("exception_type", "UNKNOWN"),
        "risk_level": state.get("risk_level", "HIGH"),
        "reason": state.get("review_reason") or state.get("reasoning", "High-risk pick exception requires human review."),
        "recommended_action": state.get("next_best_action") or state.get("recommended_action", "N/A"),
        "action_status": state.get("action_status", "BLOCKED"),
        "evidence_quality": state.get("evidence_quality", "WEAK"),
        "evidence_conflicts": state.get("evidence_conflicts", []),
        "supporting_evidence": state.get("provenance", {}),
        "review_question": "Approve recommendation, reject, request more evidence, or escalate?",
    }

    audit_log.append(f"LangGraph interrupt checkpoint reached (review attempt {attempts + 1}): pausing execution for human review")

    # REAL LANGGRAPH INTERRUPT CALL
    human_res = interrupt(payload)

    # Resume handling when graph is invoked with Command(resume=...)
    if isinstance(human_res, str):
        decision_val = human_res.upper().strip()
        reviewer_id = "REVIEWER-DEMO-001"
        note = None
    elif isinstance(human_res, dict):
        decision_val = (human_res.get("decision") or "REJECT").upper().strip()
        reviewer_id = human_res.get("reviewer_id", "REVIEWER-DEMO-001")
        note = human_res.get("reviewer_note")
    else:
        decision_val = "REJECT"
        reviewer_id = "REVIEWER-DEMO-001"
        note = None

    if decision_val not in ALLOWED_DECISIONS:
        raise ValueError(f"Invalid human decision '{decision_val}'. Allowed values: {ALLOWED_DECISIONS}")

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if decision_val == "APPROVE":
        audit_log.append(f"Human decision = APPROVE (reviewer={reviewer_id}, note={note})")
        return {
            "human_decision": "APPROVE",
            "action_status": "HUMAN_APPROVED_PENDING_EXECUTION",
            "requires_human_review": False,
            "final_decision": "Human supervisor APPROVED recommendation. Pending operational execution by pick operator.",
            "audit_log": audit_log,
            "updated_at": now_str,
        }
    elif decision_val == "REJECT":
        audit_log.append(f"Human decision = REJECT (reviewer={reviewer_id}, note={note})")
        return {
            "human_decision": "REJECT",
            "action_status": "REJECTED_BY_HUMAN",
            "requires_human_review": False,
            "final_decision": "Human reviewer REJECTED the proposed action. Pick exception remains unapproved.",
            "audit_log": audit_log,
            "updated_at": now_str,
        }
    elif decision_val == "REQUEST_MORE_EVIDENCE":
        new_attempts = attempts + 1
        audit_log.append(f"Human decision = REQUEST_MORE_EVIDENCE (reviewer={reviewer_id}, attempt={new_attempts})")
        return {
            "human_decision": "REQUEST_MORE_EVIDENCE",
            "action_status": "MORE_EVIDENCE_REQUIRED",
            "review_attempts": new_attempts,
            "requires_human_review": True,
            "audit_log": audit_log,
            "updated_at": now_str,
        }
    elif decision_val == "ESCALATE":
        esc_res = create_escalation(
            task_id=state.get("task_id", "N/A"),
            exception_type=state.get("exception_type", "UNKNOWN"),
            reason=note or "Human supervisor requested formal exception escalation.",
            evidence_summary=state.get("reasoning", ""),
            recommended_action=state.get("next_best_action", "ESCALATE_TO_HUMAN"),
        )
        escalation_id = esc_res.get("escalation_id")
        audit_log.append(f"Human decision = ESCALATE (reviewer={reviewer_id}, escalation_id={escalation_id})")
        return {
            "human_decision": "ESCALATE",
            "action_status": "ESCALATED",
            "requires_human_review": False,
            "escalation_id": escalation_id,
            "final_decision": f"Escalated to supervisor queue (Escalation ID: {escalation_id}).",
            "audit_log": audit_log,
            "updated_at": now_str,
        }

    return {"audit_log": audit_log, "updated_at": now_str}


# -----------------------------------------------------------------------------
# NODE 13: COLLECT ADDITIONAL EVIDENCE
# -----------------------------------------------------------------------------
def collect_additional_evidence(state: PickExceptionState) -> Dict[str, Any]:
    """Gather additional evidence when requested by a human reviewer."""
    audit_log = list(state.get("audit_log", []))
    item_id = state.get("item_id")
    location_id = state.get("location_id")
    exc_type = state.get("exception_type", "UNKNOWN")

    # Perform expanded incident lookup
    additional_incidents = []
    inc_res = search_similar_incidents(item_id=item_id, location_id=location_id, exception_type=exc_type, limit=10)
    if inc_res.get("count", 0) > 0:
        additional_incidents = inc_res.get("incidents", [])

    historical_ev = list(state.get("historical_evidence", [])) + additional_incidents

    audit_log.append("Additional evidence gathered upon human reviewer request")
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "historical_evidence": historical_ev,
        "audit_log": audit_log,
        "updated_at": now_str,
    }
