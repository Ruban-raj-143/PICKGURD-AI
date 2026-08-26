import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot } from 'lucide-react';

interface OperatorInputProps {
  onSubmit: (query: string, taskId?: string, itemId?: string, locId?: string) => void;
  isLoading: boolean;
  initialQuery?: string;
  initialTaskId?: string;
  initialItemId?: string;
  initialLocId?: string;
}

export const OperatorInput: React.FC<OperatorInputProps> = ({
  onSubmit,
  isLoading,
  initialQuery = '',
  initialTaskId = '',
  initialItemId = '',
  initialLocId = '',
}) => {
  const [query, setQuery]   = useState(initialQuery);
  const [taskId, setTaskId] = useState(initialTaskId);
  const [itemId, setItemId] = useState(initialItemId);
  const [locId, setLocId]   = useState(initialLocId);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setQuery(initialQuery);
    setTaskId(initialTaskId);
    setItemId(initialItemId);
    setLocId(initialLocId);
  }, [initialQuery, initialTaskId, initialItemId, initialLocId]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit(query, taskId || undefined, itemId || undefined, locId || undefined);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div>
      {/* Hero section */}
      <div className="hero-section">
        <div className="hero-tag">
          <Bot size={13} />
          Evidence-Grounded Pick Exception Assistant
        </div>
        <h2 className="hero-title">What happened during your pick?</h2>
        <p className="hero-subtitle">
          Describe the exception in plain language. PickGuard AI will retrieve operational evidence, SOP procedures, and recommend the next best action.
        </p>
      </div>

      {/* Query box */}
      <form onSubmit={handleSubmit}>
        <div className="query-box">
          <textarea
            ref={textareaRef}
            className="query-textarea"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. Item X123 is missing from A15-B04 and the system shows 3 units in stock..."
            rows={3}
            disabled={isLoading}
            aria-label="Exception description"
          />

          <div className="query-footer">
            {/* Optional IDs */}
            <div className="query-meta-fields">
              <input
                className="meta-input"
                type="text"
                placeholder="Task ID"
                value={taskId}
                onChange={(e) => setTaskId(e.target.value)}
                disabled={isLoading}
              />
              <input
                className="meta-input"
                type="text"
                placeholder="Item SKU"
                value={itemId}
                onChange={(e) => setItemId(e.target.value)}
                disabled={isLoading}
              />
              <input
                className="meta-input"
                type="text"
                placeholder="Location ID"
                value={locId}
                onChange={(e) => setLocId(e.target.value)}
                disabled={isLoading}
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading || !query.trim()}
              id="submit-exception-btn"
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="spin" />
                  Analysing…
                </>
              ) : (
                <>
                  <Send size={15} />
                  Analyse Exception
                </>
              )}
            </button>
          </div>
        </div>

        {query.trim() && !isLoading && (
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.5rem', textAlign: 'right' }}>
            Press <kbd style={{ background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)', borderRadius: 4, padding: '1px 5px', fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>⌘ Enter</kbd> to submit
          </div>
        )}
      </form>
    </div>
  );
};
