import React, { useState } from 'react';
import { ListTree, ChevronDown, ChevronUp, History } from 'lucide-react';

interface AuditTrailProps {
  auditLog: string[];
}

export const AuditTrail: React.FC<AuditTrailProps> = ({ auditLog }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!auditLog || auditLog.length === 0) return null;

  return (
    <div className="card">
      <div
        className="audit-toggle"
        onClick={() => setIsOpen(!isOpen)}
        role="button"
        tabIndex={0}
        aria-expanded={isOpen}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <History size={16} color="var(--blue)" />
          <span className="card-title">Execution Audit Trail</span>
          <span className="chip chip-muted" style={{ fontSize: '0.68rem', padding: '0.1rem 0.5rem' }}>
            {auditLog.length} events
          </span>
        </div>
        <div style={{ color: 'var(--text-secondary)' }}>
          {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </div>

      {isOpen && (
        <div className="timeline">
          {auditLog.map((log, idx) => (
            <div key={idx} className="timeline-item">
              <div className="timeline-idx">STEP {String(idx + 1).padStart(2, '0')}</div>
              <div className="timeline-content">{log}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
