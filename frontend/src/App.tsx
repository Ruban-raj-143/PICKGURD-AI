import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DemoButtons } from './components/DemoButtons';
import { OperatorInput } from './components/OperatorInput';
import { ResultHeader } from './components/ResultHeader';
import { EvidencePanel } from './components/EvidencePanel';
import { ReasoningPanel } from './components/ReasoningPanel';
import { ActionPanel } from './components/ActionPanel';
import { HumanReviewModal } from './components/HumanReviewModal';
import { AuditTrail } from './components/AuditTrail';
import { agentApi } from './services/api';
import { AgentRunResponse, SystemStatusResponse } from './types/agent';
import { AlertCircle, RotateCcw } from 'lucide-react';

export const App: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatusResponse | null>(null);
  const [currentResult, setCurrentResult] = useState<AgentRunResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form input state from demo buttons
  const [queryInput, setQueryInput] = useState('');
  const [taskIdInput, setTaskIdInput] = useState('');
  const [itemIdInput, setItemIdInput] = useState('');
  const [locIdInput, setLocIdInput] = useState('');

  useEffect(() => {
    // Fetch system status on load
    agentApi
      .getSystemStatus()
      .then((data) => setSystemStatus(data))
      .catch((err) => console.error('Failed to fetch system status:', err));
  }, []);

  const handleSelectDemo = (query: string, taskId?: string, itemId?: string, locId?: string) => {
    setQueryInput(query);
    setTaskIdInput(taskId || '');
    setItemIdInput(itemId || '');
    setLocIdInput(locId || '');
  };

  const handleSubmitException = async (query: string, taskId?: string, itemId?: string, locId?: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await agentApi.runAgent({
        query,
        task_id: taskId,
        item_id: itemId,
        location_id: locId,
      });
      setCurrentResult(res);
    } catch (err: any) {
      console.error('API execution error:', err);
      setErrorMsg(err.response?.data?.detail || 'PickGuard AI could not complete this request.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitReview = async (
    decision: 'APPROVE' | 'REJECT' | 'REQUEST_MORE_EVIDENCE' | 'ESCALATE',
    note?: string
  ) => {
    if (!currentResult) return;
    setIsSubmittingReview(true);
    setErrorMsg(null);
    try {
      await agentApi.submitHumanReview(currentResult.run_id, {
        decision,
        reviewer_note: note,
        reviewer_id: 'REVIEWER-DEMO-001',
      });
      // Fetch updated status
      const updatedRes = await agentApi.getRunStatus(currentResult.run_id);
      setCurrentResult(updatedRes);
    } catch (err: any) {
      console.error('Human review submission error:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to process human review decision.');
    } finally {
      setIsSubmittingReview(false);
    }
  };

  return (
    <div className="app-root">
      <Header systemStatus={systemStatus} />

      <main className="main-container">
        {/* Preset Demo Scenarios */}
        <DemoButtons onSelectDemo={handleSelectDemo} />

        {/* Operator Query Form */}
        <OperatorInput
          onSubmit={handleSubmitException}
          isLoading={isLoading}
          initialQuery={queryInput}
          initialTaskId={taskIdInput}
          initialItemId={itemIdInput}
          initialLocId={locIdInput}
        />

        {/* Error Alert */}
        {errorMsg && (
          <div className="error-card">
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>{errorMsg}</div>
            <button
              className="btn-ghost"
              onClick={() => setErrorMsg(null)}
              style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
            >
              <RotateCcw size={13} /> Dismiss
            </button>
          </div>
        )}

        {/* Agent Workflow Execution Results */}
        {currentResult && (
          <>
            <ResultHeader result={currentResult} />

            <div className="two-col-grid">
              <ActionPanel result={currentResult} />
              <ReasoningPanel result={currentResult} />
            </div>

            <EvidencePanel result={currentResult} />

            <AuditTrail auditLog={currentResult.audit_log} />
          </>
        )}

        {/* Human-in-the-Loop Review Modal (LangGraph Interrupt Gate) */}
        {currentResult && currentResult.status === 'WAITING_FOR_HUMAN_REVIEW' && (
          <HumanReviewModal
            result={currentResult}
            onSubmitReview={handleSubmitReview}
            isSubmitting={isSubmittingReview}
          />
        )}
      </main>
    </div>
  );
};
