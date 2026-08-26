"""Interactive CLI demo script demonstrating real LangGraph interrupt checkpoint and Command resume."""

import json
import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from langgraph.types import Command
from backend.app.graph.workflow import build_pickguard_graph


def run_demo(simulated_decision: str = "REJECT"):
    print("========================================")
    print("PickGuard AI — LangGraph Human-in-the-Loop Demo")
    print("========================================")
    print("")

    query = "TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6."
    print(f"Operator Query:\n\"{query}\"\n")

    app = build_pickguard_graph()
    thread_config = {"configurable": {"thread_id": "demo-task-1003"}}

    print("Step 1: Invoking graph with initial state...")
    state_res = app.invoke({"operator_query": query}, thread_config)

    # Check if graph paused at interrupt
    snapshot = app.get_state(thread_config)
    next_nodes = snapshot.next

    if next_nodes and "human_review_gate" in next_nodes:
        print("\n>>> GRAPH INTERRUPTED AT HUMAN REVIEW GATE <<<\n")
        interrupt_tasks = snapshot.tasks
        if interrupt_tasks and len(interrupt_tasks) > 0 and len(interrupt_tasks[0].interrupts) > 0:
            payload = interrupt_tasks[0].interrupts[0].value
            print("========================================")
            print("HUMAN REVIEW REQUIRED")
            print("========================================")
            print(f"Task ID:             {payload.get('task_id')}")
            print(f"Exception Type:      {payload.get('exception_type')}")
            print(f"Risk Level:          {payload.get('risk_level')}")
            print(f"Requested Action:    {payload.get('recommended_action')}")
            print(f"Action Status:       {payload.get('action_status')}")
            print(f"Review Reason:       {payload.get('reason')}")
            print(f"Evidence Quality:    {payload.get('evidence_quality')}")
            print(f"Evidence Conflicts:  {len(payload.get('evidence_conflicts', []))} active conflicts")
            print("========================================\n")

            print(f"Simulating Human Decision: '{simulated_decision}'")
            print("Step 2: Resuming graph execution with Command(resume=...)...")
            human_decision_payload = {
                "decision": simulated_decision,
                "reviewer_id": "REVIEWER-DEMO-001",
                "reviewer_note": f"Supervisor review decision '{simulated_decision}' submitted via demo script.",
            }

            final_state = app.invoke(Command(resume=human_decision_payload), thread_config)

            print("\n========================================")
            print("FINAL DECISION AFTER RESUME")
            print("========================================")
            print(f"Human Decision:       {final_state.get('human_decision')}")
            print(f"Action Status:        {final_state.get('action_status')}")
            print(f"Next Best Action:     {final_state.get('next_best_action')}")
            print(f"Requires Human Review: {final_state.get('requires_human_review')}")
            print(f"Final Summary:        {final_state.get('final_decision')}")
            print("========================================\n")

            print("Audit Trail:")
            for entry in final_state.get("audit_log", []):
                print(f" -> {entry}")
            print("\nGraph Status: SUCCESS")
            return 0
    else:
        print("Graph completed without interrupt.")
        print(f"Final Action Status: {state_res.get('action_status')}")
        return 0


def main():
    decision = sys.argv[1] if len(sys.argv) > 1 else "REJECT"
    sys.exit(run_demo(decision))


if __name__ == "__main__":
    main()
