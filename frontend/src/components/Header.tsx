import React from 'react';
import { Shield } from 'lucide-react';
import { SystemStatusResponse } from '../types/agent';

interface HeaderProps {
  systemStatus?: SystemStatusResponse | null;
}

const STATUS_ITEMS = [
  { key: 'api',      label: 'API' },
  { key: 'langgraph', label: 'LangGraph' },
  { key: 'rag',      label: 'RAG' },
  { key: 'tools',    label: 'Tools' },
];

export const Header: React.FC<HeaderProps> = ({ systemStatus }) => {
  const llm = systemStatus?.llm_provider || 'mimic';

  return (
    <header className="app-header">
      {/* Brand */}
      <div className="brand">
        <div className="brand-icon">
          <Shield size={18} color="#fff" strokeWidth={2.5} />
        </div>
        <div className="brand-text">
          <h1>PickGuard AI</h1>
          <p>Pick Exception Assistant</p>
        </div>
      </div>

      {/* Status Pills */}
      <div className="status-bar">
        {STATUS_ITEMS.map((item) => (
          <div key={item.key} className="status-pill active">
            <span className="status-dot" />
            {item.label}
          </div>
        ))}
        <div className="status-pill" style={{ color: '#7dd3fc', borderColor: 'rgba(125, 211, 252, 0.25)', background: 'rgba(125, 211, 252, 0.07)' }}>
          <span className="status-dot" style={{ background: '#7dd3fc' }} />
          LLM: {llm}
        </div>
      </div>
    </header>
  );
};
