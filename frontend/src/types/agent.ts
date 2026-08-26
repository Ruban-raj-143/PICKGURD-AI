export interface AgentRunRequest {
  query: string;
  task_id?: string | null;
  item_id?: string | null;
  location_id?: string | null;
  order_id?: string | null;
}

export interface HumanReviewPayload {
  type: string;
  task_id?: string;
  exception_type?: string;
  risk_level?: string;
  reason?: string;
  recommended_action?: string;
  action_status?: string;
  evidence_quality?: string;
  evidence_conflicts?: Array<{
    type: string;
    description: string;
    severity: string;
  }>;
  supporting_evidence?: Record<string, string[]>;
  review_question?: string;
}

export interface AgentRunResponse {
  run_id: string;
  thread_id: string;
  status: 'COMPLETED' | 'WAITING_FOR_HUMAN_REVIEW' | 'RUNNING' | 'FAILED';
  exception_type: string;
  secondary_exception_types: string[];
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  next_best_action: string;
  action_type: string;
  action_status: 'RECOMMENDED' | 'BLOCKED' | 'HUMAN_APPROVED_PENDING_EXECUTION' | 'REJECTED_BY_HUMAN' | 'ESCALATED' | 'MORE_EVIDENCE_REQUIRED';
  requires_human_review: boolean;
  evidence_quality: 'STRONG' | 'MODERATE' | 'WEAK' | 'INSUFFICIENT';
  evidence_summary: {
    OBSERVED_FACTS?: string[];
    SOP_EVIDENCE?: string[];
    HISTORICAL_EVIDENCE?: string[];
    INFERENCES?: string[];
    EVIDENCE_GAPS?: string[];
  };
  reasoning?: string | null;
  root_cause?: string | null;
  provenance: Record<string, string[]>;
  human_review_payload?: HumanReviewPayload | null;
  audit_log: string[];
}

export interface HumanReviewRequest {
  decision: 'APPROVE' | 'REJECT' | 'REQUEST_MORE_EVIDENCE' | 'ESCALATE';
  reviewer_note?: string;
  reviewer_id?: string;
}

export interface HumanReviewResponse {
  run_id: string;
  thread_id: string;
  status: string;
  decision: string;
  action_status: string;
  final_decision?: string | null;
  audit_log: string[];
}

export interface SystemStatusResponse {
  status: string;
  api_status: string;
  langgraph_status: string;
  rag_status: string;
  llm_provider: string;
  model_name: string;
  tools_status: string;
}
