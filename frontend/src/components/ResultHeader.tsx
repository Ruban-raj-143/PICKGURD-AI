import React from 'react';
import { AgentRunResponse } from '../types/agent';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface ResultHeaderProps {
  result: AgentRunResponse;
}

const riskConfig: Record<string, { chipClass: string; icon: React.ReactNode; label: string }> = {
  HIGH:   { chipClass: 'chip-red',   icon: <AlertTriangle size={11} />, label: 'HIGH RISK' },
  MEDIUM: { chipClass: 'chip-amber', icon: <AlertTriangle size={11} />, label: 'MEDIUM RISK' },
  LOW:    { chipClass: 'chip-green', icon: <CheckCircle size={11} />,   label: 'LOW RISK' },
};

const statusConfig: Record<string, { chipClass: string; icon: React.ReactNode; label: string }> = {
  WAITING_FOR_HUMAN_REVIEW: { chipClass: 'chip-purple', icon: <Clock size={11} />, label: 'AWAITING REVIEW' },
  COMPLETED:                { chipClass: 'chip-blue',   icon: <CheckCircle size={11} />, label: 'COMPLETED' },
};

export const ResultHeader: React.FC<ResultHeaderProps> = ({ result }) => {
  const risk   = riskConfig[result.risk_level] ?? riskConfig.LOW;
  const status = statusConfig[result.status] ?? { chipClass: 'chip-muted', icon: null, label: result.status };
  const isHigh = result.risk_level === 'HIGH';

  return (
    <div>
      <div className="section-label" style={{ marginBottom: '1rem' }}>
        Analysis result
      </div>

      <div className={`result-hero ${isHigh ? 'risk-high' : ''}`}>
        <div className="result-hero-inner">
          <div>
            <div className="exception-type">{result.exception_type}</div>
            {result.secondary_exception_types && result.secondary_exception_types.length > 0 && (
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
                {result.secondary_exception_types.map((sec) => (
                  <span key={sec} className="chip chip-amber" style={{ fontSize: '0.68rem' }}>+{sec}</span>
                ))}
              </div>
            )}
            <div className="run-meta">
              Run&nbsp;<span>{result.run_id}</span>&nbsp;·&nbsp;Thread&nbsp;<span>{result.thread_id}</span>
            </div>
          </div>

          <div className="result-chips">
            <span className={`chip ${risk.chipClass}`}>
              {risk.icon}{risk.label}
            </span>
            <span className={`chip ${status.chipClass}`}>
              {status.icon}{status.label}
            </span>
            <span className="chip chip-muted">
              Quality: {result.evidence_quality}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
