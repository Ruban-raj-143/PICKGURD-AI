"""FastAPI REST API router for PickGuard AI agent interaction and human-in-the-loop review."""

import uuid
from typing import Dict
from fastapi import APIRouter, HTTPException, status
from langgraph.types import Command

from backend.app.api.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    HumanReviewRequest,
    HumanReviewResponse,
    AuditResponse,
    SystemStatusResponse,
)
from backend.app.graph.workflow import app_graph
from backend.app.services.llm import get_llm_provider

router = APIRouter(prefix="/api/v1", tags=["PickGuard Agent API"])

# In-memory mapping of run_id -> thread_id
RUN_STORE: Dict[str, str] = {}


def _extract_run_response(run_id: str, thread_id: str) -> AgentRunResponse:
    """Helper to extract AgentRunResponse from LangGraph checkpointer state."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = app_graph.get_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found.")

    state = snapshot.values
    next_nodes = snapshot.next
    is_waiting_review = bool(next_nodes and "human_review_gate" in next_nodes)

    status_str = "WAITING_FOR_HUMAN_REVIEW" if is_waiting_review else "COMPLETED"

    human_payload = None
    if is_waiting_review and snapshot.tasks and len(snapshot.tasks) > 0:
        task = snapshot.tasks[0]
        if task.interrupts and len(task.interrupts) > 0:
            human_payload = task.interrupts[0].value

    return AgentRunResponse(
        run_id=run_id,
        thread_id=thread_id,
        status=status_str,
        exception_type=state.get("exception_type", "UNKNOWN"),
        secondary_exception_types=state.get("secondary_exception_types", []),
        risk_level=state.get("risk_level", "LOW"),
        next_best_action=state.get("next_best_action", "COLLECT_MORE_EVIDENCE"),
        action_type=state.get("action_type", "COLLECT_MORE_EVIDENCE"),
        action_status=state.get("action_status", "RECOMMENDED"),
        requires_human_review=state.get("requires_human_review", False),
        evidence_quality=state.get("evidence_quality", "WEAK"),
        evidence_summary=state.get("evidence_summary", {}),
        reasoning=state.get("reasoning"),
        root_cause=state.get("root_cause"),
        provenance=state.get("provenance", {}),
        human_review_payload=human_payload,
        audit_log=state.get("audit_log", []),
    )


@router.post("/agent/run", response_model=AgentRunResponse, status_code=status.HTTP_201_CREATED)
def run_agent(req: AgentRunRequest):
    """Initiate a new PickGuard pick exception resolution agent workflow run."""
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query string cannot be empty.")

    run_uuid = str(uuid.uuid4())[:8].upper()
    run_id = f"RUN-{run_uuid}"
    thread_id = f"THREAD-{run_uuid}"

    RUN_STORE[run_id] = thread_id

    initial_state = {
        "operator_query": req.query,
        "task_id": req.task_id,
        "item_id": req.item_id,
        "location_id": req.location_id,
        "order_id": req.order_id,
    }

    config = {"configurable": {"thread_id": thread_id}}

    try:
        app_graph.invoke(initial_state, config)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Agent workflow error: {str(e)}")

    return _extract_run_response(run_id, thread_id)


@router.get("/agent/{run_id}", response_model=AgentRunResponse)
def get_run_status(run_id: str):
    """Retrieve the current status, evidence package, recommendation, and audit state of an agent run."""
    thread_id = RUN_STORE.get(run_id)
    if not thread_id:
        # Fallback if run_id was used as thread_id directly
        thread_id = run_id

    return _extract_run_response(run_id, thread_id)


@router.post("/agent/{run_id}/review", response_model=HumanReviewResponse)
def submit_human_review(run_id: str, req: HumanReviewRequest):
    """Submit a human supervisor decision (APPROVE, REJECT, REQUEST_MORE_EVIDENCE, ESCALATE) to resume a paused run."""
    thread_id = RUN_STORE.get(run_id, run_id)
    config = {"configurable": {"thread_id": thread_id}}

    snapshot = app_graph.get_state(config)
    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found.")

    next_nodes = snapshot.next
    if not next_nodes or "human_review_gate" not in next_nodes:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Run '{run_id}' is not currently waiting for human review.")

    review_payload = {
        "decision": req.decision,
        "reviewer_id": req.reviewer_id,
        "reviewer_note": req.reviewer_note,
    }

    try:
        final_state = app_graph.invoke(Command(resume=review_payload), config)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error resuming graph: {str(e)}")

    # Check updated snapshot status
    updated_snapshot = app_graph.get_state(config)
    is_waiting_review = bool(updated_snapshot.next and "human_review_gate" in updated_snapshot.next)
    updated_status = "WAITING_FOR_HUMAN_REVIEW" if is_waiting_review else "COMPLETED"

    return HumanReviewResponse(
        run_id=run_id,
        thread_id=thread_id,
        status=updated_status,
        decision=req.decision,
        action_status=final_state.get("action_status", "RECOMMENDED"),
        final_decision=final_state.get("final_decision"),
        audit_log=final_state.get("audit_log", []),
    )


@router.get("/agent/{run_id}/audit", response_model=AuditResponse)
def get_run_audit(run_id: str):
    """Retrieve the complete timestamped audit trail for a given agent run."""
    thread_id = RUN_STORE.get(run_id, run_id)
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = app_graph.get_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found.")

    return AuditResponse(
        run_id=run_id,
        thread_id=thread_id,
        audit_log=snapshot.values.get("audit_log", []),
    )


@router.get("/system/status", response_model=SystemStatusResponse)
def get_system_status():
    """Retrieve health and configuration metadata for system components."""
    _, meta = get_llm_provider()
    return SystemStatusResponse(
        status="healthy",
        api_status="healthy",
        langgraph_status="healthy",
        rag_status="healthy",
        llm_provider=meta.get("provider", "mimic"),
        model_name=meta.get("model_name", "deterministic-mimic"),
        tools_status="healthy",
    )
