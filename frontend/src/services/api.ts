import axios from 'axios';
import {
  AgentRunRequest,
  AgentRunResponse,
  HumanReviewRequest,
  HumanReviewResponse,
  SystemStatusResponse,
} from '../types/agent';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const agentApi = {
  runAgent: async (payload: AgentRunRequest): Promise<AgentRunResponse> => {
    const response = await client.post<AgentRunResponse>('/api/v1/agent/run', payload);
    return response.data;
  },

  getRunStatus: async (runId: string): Promise<AgentRunResponse> => {
    const response = await client.get<AgentRunResponse>(`/api/v1/agent/${runId}`);
    return response.data;
  },

  submitHumanReview: async (runId: string, payload: HumanReviewRequest): Promise<HumanReviewResponse> => {
    const response = await client.post<HumanReviewResponse>(`/api/v1/agent/${runId}/review`, payload);
    return response.data;
  },

  getAudit: async (runId: string): Promise<{ run_id: string; audit_log: string[] }> => {
    const response = await client.get<{ run_id: string; audit_log: string[] }>(`/api/v1/agent/${runId}/audit`);
    return response.data;
  },

  getSystemStatus: async (): Promise<SystemStatusResponse> => {
    const response = await client.get<SystemStatusResponse>('/api/v1/system/status');
    return response.data;
  },
};
