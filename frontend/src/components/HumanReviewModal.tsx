import React, { useState } from 'react';
import { AgentRunResponse } from '../types/agent';
import { ShieldAlert, CheckCircle2, XCircle, Search, AlertOctagon, Loader2 } from 'lucide-react';

interface HumanReviewModalProps {
  result: AgentRunResponse;
  onSubmitReview: (
    decision: 'APPROVE' | 'REJECT' | 'REQUEST_MORE_EVIDENCE' | 'ESCALATE',
    note?: string
  ) => void;
  isSubmitting: boolean;
}

export const HumanReviewModal: React.FC<HumanReviewModalProps> = ({
  result,
  onSubmitReview,
  isSubmitting,
}) => {
  const [view, setView] = useState<'main' | 'approve-confirm' | 'reject-note'>('main');
  const [rejectNote, setRejectNote] = useState('');

  const payload = result.human_review_payload;
  const reason  = payload?.reason || result.reasoning || 'High-risk decision requires supervisor authorisation.';

  return (
    <div className="modal-overlay">
      <div className="modal-dialog" role="dialog" aria-modal aria-labelledby="modal-title">

        {/* Alert bar */}
        <div className="modal-alert-bar">
          <div className="modal-alert-icon">
            <ShieldAlert size={20} color="var(--red)" />
          </div>
          <div>
            <div className="modal-alert-title" id="modal-title">
              Human Supervisor Review Required
            </div>
            <div className="modal-alert-subtitle">
              LangGraph workflow paused · interrupt() checkpoint active
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="modal-body">

          {/* Review reason */}
          <div className="modal-section-label">Review Reason</div>
          <div className="modal-reason-box">{reason}</div>

          {/* Evidence conflicts */}
          {payload?.evidence_conflicts && payload.evidence_conflicts.length > 0 && (
            <>
              <div className="modal-section-label">Active Evidence Discrepancies</div>
              <div className="modal-conflict-box">
                <div className="modal-conflict-title">⚠ Conflicts Detected</div>
                {payload.evidence_conflicts.map((c, idx) => (
                  <div key={idx} className="modal-conflict-item">
                    · {c.description}
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Proposed action */}
          <div className="modal-section-label">Proposed Next Best Action</div>
          <div className="modal-proposed-action">{result.next_best_action}</div>

          {/* ── Main action grid ── */}
          {view === 'main' && (
            <div className="modal-actions-grid">
              <button
                id="btn-approve"
                className="modal-btn modal-btn-approve"
                disabled={isSubmitting}
                onClick={() => setView('approve-confirm')}
              >
                <CheckCircle2 size={15} />
                Approve
              </button>
              <button
                id="btn-reject"
                className="modal-btn modal-btn-reject"
                disabled={isSubmitting}
                onClick={() => setView('reject-note')}
              >
                <XCircle size={15} />
                Reject
              </button>
              <button
                id="btn-more-evidence"
                className="modal-btn modal-btn-evidence"
                disabled={isSubmitting}
                onClick={() => onSubmitReview('REQUEST_MORE_EVIDENCE', 'Requested expanded incident search.')}
              >
                {isSubmitting ? <Loader2 size={14} className="spin" /> : <Search size={15} />}
                More Evidence
              </button>
              <button
                id="btn-escalate"
                className="modal-btn modal-btn-escalate"
                disabled={isSubmitting}
                onClick={() => onSubmitReview('ESCALATE', 'Escalated to WMS operations lead queue.')}
              >
                <AlertOctagon size={15} />
                Escalate
              </button>
            </div>
          )}

          {/* ── Approve confirm ── */}
          {view === 'approve-confirm' && (
            <div className="modal-sub-dialog">
              <div className="modal-sub-title" style={{ color: 'var(--green)' }}>
                ✓ Confirm Supervisor Approval
              </div>
              <div className="modal-sub-warning">
                ⚠ WARNING: Approving authorises the operator to perform physical verification.
                This does NOT automatically modify WMS inventory or order state.
              </div>
              <div className="modal-sub-btns">
                <button
                  className="modal-btn-sm modal-btn-approve"
                  style={{ padding: '0.55rem 1.1rem', borderRadius: 8, border: 'none', fontFamily: 'var(--font-sans)', fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer' }}
                  disabled={isSubmitting}
                  onClick={() => {
                    onSubmitReview('APPROVE', 'Supervisor approved following evidence review.');
                    setView('main');
                  }}
                >
                  {isSubmitting ? <Loader2 size={13} className="spin" /> : <CheckCircle2 size={13} />}
                  Confirm Approval
                </button>
                <button
                  className="modal-btn-sm"
                  style={{ background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', padding: '0.55rem 1rem', borderRadius: 8, fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '0.82rem', cursor: 'pointer' }}
                  onClick={() => setView('main')}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* ── Reject note ── */}
          {view === 'reject-note' && (
            <div className="modal-sub-dialog">
              <div className="modal-sub-title" style={{ color: 'var(--red)' }}>
                Rejection Reason
              </div>
              <input
                className="modal-note-input"
                type="text"
                placeholder="Enter supervisor rejection note (optional)…"
                value={rejectNote}
                onChange={(e) => setRejectNote(e.target.value)}
              />
              <div className="modal-sub-btns">
                <button
                  className="modal-btn-sm"
                  style={{ background: 'var(--gradient-danger)', color: '#fff', padding: '0.55rem 1.1rem', borderRadius: 8, border: 'none', fontFamily: 'var(--font-sans)', fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer' }}
                  disabled={isSubmitting}
                  onClick={() => {
                    onSubmitReview('REJECT', rejectNote || 'Supervisor rejected proposed action.');
                    setView('main');
                  }}
                >
                  {isSubmitting ? <Loader2 size={13} className="spin" /> : <XCircle size={13} />}
                  Confirm Rejection
                </button>
                <button
                  className="modal-btn-sm"
                  style={{ background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', padding: '0.55rem 1rem', borderRadius: 8, fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '0.82rem', cursor: 'pointer' }}
                  onClick={() => setView('main')}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
