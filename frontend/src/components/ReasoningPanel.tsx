import React from 'react';
import { AgentRunResponse } from '../types/agent';
import { Sparkles, AlertCircle, Triangle } from 'lucide-react';

interface ReasoningPanelProps {
  result: AgentRunResponse;
}

export const ReasoningPanel: React.FC<ReasoningPanelProps> = ({ result }) => {
  const rationale =
    result.reasoning ||
    result.evidence_summary?.INFERENCES?.[0] ||
    'Operational facts and SOP procedures support this verification step.';

  const gaps = result.evidence_summary?.EVIDENCE_GAPS || [];

  return (
    <div className="card">
      <div className="card-header">
        <Sparkles size={16} color="var(--purple)" />
        <span className="card-title">AI Reasoning</span>
      </div>

      {/* Rationale */}
      <div className="card-label">Grounded Rationale</div>
      <div className="reasoning-box">{rationale}</div>

      {/* Root cause */}
      {result.root_cause && (
        <>
          <div className="card-label">Identified Root Cause</div>
          <div className="root-cause-box">
            <Triangle size={14} style={{ flexShrink: 0, marginTop: 2 }} />
            {result.root_cause}
          </div>
        </>
      )}

      {/* Evidence gaps */}
      {gaps.length > 0 && (
        <>
          <div
            className="card-label"
            style={{ color: 'var(--amber)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <AlertCircle size={11} />
            Evidence Gaps & Warnings
          </div>
          <div>
            {gaps.map((gap, idx) => (
              <div key={idx} className="gap-item">
                <span style={{ color: 'var(--amber)', flexShrink: 0 }}>·</span>
                {gap}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
