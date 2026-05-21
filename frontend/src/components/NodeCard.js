import React from 'react';

const Stat = ({ label, value, unit, color }) => (
  <div style={{ textAlign: 'center', flex: 1 }}>
    <div style={{ fontSize: 20, fontWeight: 700, color: color || '#e2e8f0' }}>
      {value ?? '—'}{unit}
    </div>
    <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{label}</div>
  </div>
);

export default function NodeCard({ node }) {
  if (!node) return null;
  const { node_id, data_count, last_seen, avg_temperature, avg_vibration, avg_current, anomaly_count } = node;
  const isPhysical = node_id.includes('physical');
  const lastSeenDate = last_seen ? new Date(last_seen) : null;
  const ageMs = lastSeenDate ? Date.now() - lastSeenDate.getTime() : Infinity;
  const online = ageMs < 10000;

  return (
    <div style={{
      background: '#1a1d2e',
      border: `1px solid ${isPhysical ? '#6366f1' : '#22c55e'}`,
      borderRadius: 12,
      padding: '14px 18px',
      flex: 1,
      minWidth: 240,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <span style={{ fontSize: 18 }}>{isPhysical ? '🔌' : '🖥️'}</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15 }}>{node_id}</div>
          <div style={{ fontSize: 11, color: '#94a3b8' }}>
            {isPhysical ? 'Physical ESP32 Proxy' : 'Synthetic Simulator'}
          </div>
        </div>
        <div style={{
          marginLeft: 'auto',
          width: 8, height: 8, borderRadius: '50%',
          background: online ? '#22c55e' : '#ef4444',
          boxShadow: online ? '0 0 6px #22c55e' : 'none',
        }} />
      </div>

      {/* Stats row */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <Stat label="Avg Temp" value={avg_temperature} unit="°C" color="#f59e0b" />
        <Stat label="Avg Vib"  value={avg_vibration}   unit="g"  color="#6366f1" />
        <Stat label="Avg Cur"  value={avg_current}     unit="A"  color="#22c55e" />
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#94a3b8' }}>
        <span>Readings: {data_count ?? 0}</span>
        <span style={{ color: (anomaly_count > 0) ? '#f87171' : '#94a3b8' }}>
          Anomalies: {anomaly_count ?? 0}
        </span>
        <span>{lastSeenDate ? lastSeenDate.toLocaleTimeString() : 'no data'}</span>
      </div>
    </div>
  );
}
