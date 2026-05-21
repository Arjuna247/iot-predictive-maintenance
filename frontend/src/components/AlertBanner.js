import React, { useEffect, useState } from 'react';

const MAX_ALERTS = 5;

export default function AlertBanner({ alerts }) {
  const [visible, setVisible] = useState([]);

  useEffect(() => {
    if (!alerts || alerts.length === 0) return;
    setVisible(prev => [alerts[alerts.length - 1], ...prev].slice(0, MAX_ALERTS));
  }, [alerts]);

  const dismiss = idx => setVisible(v => v.filter((_, i) => i !== idx));

  if (visible.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
      {visible.map((a, i) => (
        <div key={i} style={{
          background: 'rgba(239,68,68,0.15)',
          border: '1px solid #ef4444',
          borderRadius: 8,
          padding: '10px 14px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: 10,
        }}>
          <span style={{ fontSize: 18 }}>🚨</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, color: '#f87171', marginBottom: 2 }}>
              Anomaly — {a.node_id}
            </div>
            <div style={{ color: '#fca5a5', fontSize: 13 }}>{a.reason}</div>
            <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 2 }}>
              T:{a.temperature?.toFixed(1)}°C  V:{a.vibration?.toFixed(3)}g  I:{a.current?.toFixed(2)}A
              &nbsp;·&nbsp; {new Date(a.timestamp.endsWith('Z') ? a.timestamp : a.timestamp + 'Z').toLocaleTimeString()}
            </div>
          </div>
          <button onClick={() => dismiss(i)} style={{
            background: 'none', border: 'none', color: '#94a3b8',
            cursor: 'pointer', fontSize: 16, lineHeight: 1,
          }}>×</button>
        </div>
      ))}
    </div>
  );
}
