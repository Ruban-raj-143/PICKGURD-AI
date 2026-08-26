import React from 'react';
import { PlayCircle, ShieldAlert, AlertTriangle, Zap } from 'lucide-react';

interface DemoButtonsProps {
  onSelectDemo: (query: string, taskId?: string, itemId?: string, locId?: string) => void;
}

const SCENARIOS = [
  {
    id: 1,
    icon: <PlayCircle size={15} />,
    risk: 'LOW',
    riskColor: '#34d399',
    label: 'Scenario 1 · Low Risk',
    title: 'Missing Item X123',
    desc: 'Item not found at expected pick location',
    query: 'The item X123 is missing from A15-B04. The system says there are 3 units.',
    taskId: 'TASK-1001',
    itemId: 'X123',
    locId: 'A15-B04',
  },
  {
    id: 2,
    icon: <AlertTriangle size={15} />,
    risk: 'MEDIUM',
    riskColor: '#fbbf24',
    label: 'Scenario 2 · Medium Risk',
    title: 'Missing + Barcode Failure',
    desc: 'Dual exception — missing item and scan failure',
    query: "The item X124 is missing at A12-B03 and the barcode also won't scan.",
    taskId: 'TASK-1002',
    itemId: 'X124',
    locId: 'A12-B03',
  },
  {
    id: 3,
    icon: <ShieldAlert size={15} />,
    risk: 'HIGH',
    riskColor: '#f87171',
    label: 'Scenario 3 · High Risk',
    title: 'Quantity Mismatch',
    desc: 'LangGraph interrupt · supervisor review required',
    query: 'TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6.',
    taskId: 'TASK-1003',
    itemId: 'X125',
    locId: 'A20-B02',
  },
];

export const DemoButtons: React.FC<DemoButtonsProps> = ({ onSelectDemo }) => {
  return (
    <div>
      <div className="scenarios-label">
        <Zap size={12} />
        Quick-load demo scenarios
      </div>
      <div className="scenarios-grid">
        {SCENARIOS.map((s) => (
          <button
            key={s.id}
            className="scenario-card"
            onClick={() => onSelectDemo(s.query, s.taskId, s.itemId, s.locId)}
          >
            <div className="scenario-card-inner">
              <div className="scenario-number" style={{ color: s.riskColor }}>
                <span className="scenario-risk-dot" style={{ background: s.riskColor }} />
                {s.label}
              </div>
              <div className="scenario-title">{s.title}</div>
              <div className="scenario-desc">{s.desc}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
