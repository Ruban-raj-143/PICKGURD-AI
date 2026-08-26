"""LangGraph StateGraph workflow construction, checkpointer configuration, and compilation for PickGuard AI."""

# pyrefly: ignore [missing-import]
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.app.graph.state import PickExceptionState
from backend.app.graph.nodes import (
    parse_operator_query,
    classify_exception,
    fetch_operational_evidence,
    retrieve_sop_evidence,
    retrieve_historical_evidence,
    build_evidence_package,
    reason_over_evidence,
    fuse_evidence,
    detect_evidence_conflicts,
    select_next_best_action,
    apply_safety_policy,
    human_review_gate,
    collect_additional_evidence,
)
from backend.app.graph.edges import route_after_classification, route_after_human_review

# Global in-memory checkpointer for thread_id persistence and interrupt state recovery
checkpointer = MemorySaver()


def build_pickguard_graph():
    """Construct and compile the PickGuard AI evidence-generation, reasoning, safety policy, and human-in-the-loop workflow graph.

    Returns:
        Compiled StateGraph application with MemorySaver checkpointer.
    """
    workflow = StateGraph(PickExceptionState)

    # Add Nodes
    workflow.add_node("parse_operator_query", parse_operator_query)
    workflow.add_node("classify_exception", classify_exception)
    workflow.add_node("fetch_operational_evidence", fetch_operational_evidence)
    workflow.add_node("retrieve_sop_evidence", retrieve_sop_evidence)
    workflow.add_node("retrieve_historical_evidence", retrieve_historical_evidence)
    workflow.add_node("build_evidence_package", build_evidence_package)
    workflow.add_node("reason_over_evidence", reason_over_evidence)
    workflow.add_node("fuse_evidence", fuse_evidence)
    workflow.add_node("detect_evidence_conflicts", detect_evidence_conflicts)
    workflow.add_node("select_next_best_action", select_next_best_action)
    workflow.add_node("apply_safety_policy", apply_safety_policy)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("collect_additional_evidence", collect_additional_evidence)

    # Linear Edges
    workflow.add_edge(START, "parse_operator_query")
    workflow.add_edge("parse_operator_query", "classify_exception")
    workflow.add_edge("classify_exception", "fetch_operational_evidence")

    # Conditional Routing Edge after operational evidence gathering
    workflow.add_conditional_edges(
        "fetch_operational_evidence",
        route_after_classification,
        {
            "retrieve_sop": "retrieve_sop_evidence",
            "skip_sop": "retrieve_historical_evidence",
        },
    )

    workflow.add_edge("retrieve_sop_evidence", "retrieve_historical_evidence")
    workflow.add_edge("retrieve_historical_evidence", "build_evidence_package")
    workflow.add_edge("build_evidence_package", "reason_over_evidence")
    workflow.add_edge("reason_over_evidence", "fuse_evidence")
    workflow.add_edge("fuse_evidence", "detect_evidence_conflicts")
    workflow.add_edge("detect_evidence_conflicts", "select_next_best_action")
    workflow.add_edge("select_next_best_action", "apply_safety_policy")
    workflow.add_edge("apply_safety_policy", "human_review_gate")

    # Conditional Routing Edge after human review gate (re-query loop or finish)
    workflow.add_conditional_edges(
        "human_review_gate",
        route_after_human_review,
        {
            "collect_more_evidence": "collect_additional_evidence",
            "end_workflow": END,
        },
    )

    workflow.add_edge("collect_additional_evidence", "build_evidence_package")

    # Compile workflow with MemorySaver checkpointer
    return workflow.compile(checkpointer=checkpointer)


# Single compiled graph application instance
app_graph = build_pickguard_graph()
