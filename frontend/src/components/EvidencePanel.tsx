import React, { useState } from 'react';
import { AgentRunResponse } from '../types/agent';
import { Database, FileText, History, Link as LinkIcon, BookOpen, Clock } from 'lucide-react';

interface EvidencePanelProps {
  result: AgentRunResponse;
}

type TabKey = 'op' | 'sop' | 'hist';

interface TabConfig {
  key: TabKey;
  icon: React.ReactNode;
  label: string;
  items: string[] | undefined;
  sourceKey: 'operational' | 'sop' | 'historical';
  itemClass: string;
  sourceIcon: React.ReactNode;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ result }) => {
  const [activeTab, setActiveTab] = useState<TabKey>('op');

  const { evidence_summary, provenance } = result;

  const tabs: TabConfig[] = [
    {
      key: 'op',
      icon: <Database size={13} />,
      label: 'Operational',
      items: evidence_summary?.OBSERVED_FACTS,
      sourceKey: 'operational',
      itemClass: '',
      sourceIcon: <LinkIcon size={10} />,
    },
    {
      key: 'sop',
      icon: <BookOpen size={13} />,
      label: 'SOP Procedures',
      items: evidence_summary?.SOP_EVIDENCE,
      sourceKey: 'sop',
      itemClass: 'sop-item',
      sourceIcon: <FileText size={10} />,
    },
    {
      key: 'hist',
      icon: <Clock size={13} />,
      label: 'Historical',
      items: evidence_summary?.HISTORICAL_EVIDENCE,
      sourceKey: 'historical',
      itemClass: 'hist-item',
      sourceIcon: <History size={10} />,
    },
  ];

  const activeConfig = tabs.find((t) => t.key === activeTab)!;
  const items   = activeConfig.items || [];
  const sources = provenance?.[activeConfig.sourceKey] || [];

  return (
    <div className="card">
      <div className="card-header">
        <Database size={16} color="var(--blue)" />
        <span className="card-title">Grounded Evidence</span>
      </div>

      {/* Tab selector */}
      <div className="evidence-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`ev-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.icon}
            {tab.label}
            <span className="count">{tab.items?.length ?? 0}</span>
          </button>
        ))}
      </div>

      {/* Items */}
      {items.length === 0 ? (
        <div className="empty-state">No {activeConfig.label.toLowerCase()} evidence retrieved.</div>
      ) : (
        items.map((item, idx) => (
          <div key={idx} className={`evidence-item ${activeConfig.itemClass}`}>
            <div className="evidence-text">{item}</div>
            {sources.length > 0 && (
              <div className="evidence-sources">
                {sources.slice(0, 3).map((src, sIdx) => (
                  <span key={sIdx} className="source-tag">
                    {activeConfig.sourceIcon}
                    {src}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};
