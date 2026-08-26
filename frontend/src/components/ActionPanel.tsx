import React from 'react';
import { AgentRunResponse } from '../types/agent';
import { ShieldCheck, ArrowRight } from 'lucide-react';

interface ActionPanelProps {
  result: AgentRunResponse;
}

export const ActionPanel: React.FC<ActionPanelProps> = ({ result }) => {
  const isBlocked  = result.action_status === 'BLOCKED';
  const isApproved = result.action_status === 'HUMAN_APPROVED_PENDING_EXECUTION';
  const isRejected = result.action_status === 'REJECTED_BY_HUMAN';
  const isEscalated = result.action_status === 'ESCALATED';

  let statusChipClass = 'chip-blue';
  let statusLabel = result.action_status ?? 'RECOMMENDED';
  if (isBlocked)   { statusChipClass = 'chip-red';    }
  if (isApproved)  { statusChipClass = 'chip-green';  }
  if (isRejected)  { statusChipClass = 'chip-red';    }
  if (isEscalated) { statusChipClass = 'chip-amber';  }

  return (
    <div className={`action-card ${isBlocked ? 'action-blocked' : 'action-safe'}`}>
      <div className="card-header">
        <ArrowRight size={16} color={isBlocked ? 'var(--red)' : 'var(--green)'} />
        <span className="card-title">Next Best Action</span>
      </div>

      {/* Recommendation box */}
      <div className={`action-recommendation ${isBlocked ? 'blocked' : ''}`}>
        <div className={`action-text ${isBlocked ? 'blocked' : ''}`}>
          {result.next_best_action}
        </div>
        <div className="action-code-row">
          <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-code)', fontSize: '0.75rem' }}>
            {result.action_type}
          </code>
          <span>·</span>
          <span className={`chip ${statusChipClass}`} style={{ padding: '0.1rem 0.5rem', fontSize: '0.68rem' }}>
            {statusLabel}
          </span>
        </div>
      </div>

      {/* Boundary notice */}
      <div className="action-boundary-notice">
        <ShieldCheck size={14} color="var(--blue)" style={{ flexShrink: 0, marginTop: 1 }} />
        <span>
          <strong style={{ color: 'var(--text-secondary)' }}>Action Boundary Policy:</strong>{' '}
          Recommendations do not auto-execute. PickGuard AI never modifies WMS inventory or order state automatically.
        </span>
      </div>
    </div>
  );
};
