import React, { useEffect, useState, useCallback, useRef } from 'react';
import SensorChart from './SensorChart';
import NodeCard    from './NodeCard';
import AlertBanner from './AlertBanner';
import { fetchSensorData, fetchNodes, getSocket } from '../services/api';

const POLL_MS    = 5000;
const MAX_POINTS = 120;

const METRICS = [
  { id: 'temperature', label: '🌡️ Temperature', unit: '°C' },
  { id: 'vibration',   label: '📳 Vibration',   unit: 'g'  },
  { id: 'current',     label: '⚡ Current',      unit: 'A'  },
];

const THRESHOLDS = {
  temperature: { min: 20, max: 80 },
  vibration:   { max: 5 },
  current:     { max: 15 },
};

// ── Node Summary Bar ──────────────────────────────────────────────────────────

function NodeSummaryBar({ nodeStats, sensorData, connected, totalBuffered }) {
  return (
    <div style={{
      background: '#1a1d2e', border: '1px solid #2d3148',
      borderRadius: 10, padding: '9px 14px',
      display: 'flex', alignItems: 'center', gap: 12,
      flexWrap: 'wrap', marginBottom: 14,
    }}>
      {/* WebSocket status pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5, flexShrink: 0 }}>
        <div style={{
          width: 7, height: 7, borderRadius: '50%',
          background: connected ? '#22c55e' : '#ef4444',
          boxShadow: connected ? '0 0 6px #22c55e' : 'none',
        }} />
        <span style={{ fontSize: 11, color: '#64748b' }}>
          {connected ? 'Live' : 'Polling'}
        </span>
      </div>

      <div style={{ width: 1, height: 24, background: '#2d3148', flexShrink: 0 }} />

      {/* Per-node metrics */}
      {nodeStats.length === 0 ? (
        <span style={{ fontSize: 12, color: '#64748b' }}>
          ⏳ Waiting for nodes to connect…
        </span>
      ) : (
        nodeStats.map((n, idx) => {
          const latest = [...sensorData]
            .filter(d => d?.node_id === n?.node_id)
            .slice(-1)[0] || {};
          const isPhysical = (n?.node_id || '').includes('physical');

          return (
            <React.Fragment key={n.node_id}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <span style={{
                  fontSize: 12, fontWeight: 700,
                  color: isPhysical ? '#818cf8' : '#4ade80',
                  whiteSpace: 'nowrap',
                }}>
                  {isPhysical ? '🔌' : '🖥️'} {(n?.node_id || 'unknown').replace('node_', '')}
                </span>
                <span style={{ fontSize: 11, color: '#fcd34d', whiteSpace: 'nowrap' }}>
                  🌡️ {latest.temperature != null ? `${latest.temperature.toFixed(1)}°C` : '—'}
                </span>
                <span style={{ fontSize: 11, color: '#a5b4fc', whiteSpace: 'nowrap' }}>
                  📳 {latest.vibration != null ? `${latest.vibration.toFixed(3)}g` : '—'}
                </span>
                <span style={{ fontSize: 11, color: '#86efac', whiteSpace: 'nowrap' }}>
                  ⚡ {latest.current != null ? `${latest.current.toFixed(2)}A` : '—'}
                </span>
                {n.anomaly_count > 0 && (
                  <span style={{ fontSize: 10, color: '#f87171', whiteSpace: 'nowrap' }}>
                    ⚠ {n.anomaly_count} anom.
                  </span>
                )}
              </div>
              {idx < nodeStats.length - 1 && (
                <div style={{ width: 1, height: 20, background: '#2d3148', flexShrink: 0 }} />
              )}
            </React.Fragment>
          );
        })
      )}

      {/* Buffer count */}
      <span style={{ marginLeft: 'auto', fontSize: 11, color: '#475569', flexShrink: 0 }}>
        {totalBuffered} pts
      </span>
    </div>
  );
}

// ── Metric Tab Switcher ───────────────────────────────────────────────────────

function MetricTabs({ active, onChange }) {
  return (
    <div style={{
      display: 'inline-flex', gap: 3,
      background: '#1a1d2e', border: '1px solid #2d3148',
      borderRadius: 10, padding: 4, marginBottom: 14,
    }}>
      {METRICS.map(m => (
        <button
          key={m.id}
          onClick={() => onChange(m.id)}
          style={{
            padding: '7px 18px',
            borderRadius: 7,
            border: 'none',
            cursor: 'pointer',
            fontSize: 13,
            fontWeight: active === m.id ? 700 : 400,
            background: active === m.id ? '#6366f1' : 'transparent',
            color: active === m.id ? '#fff' : '#64748b',
            transition: 'background 0.15s ease, color 0.15s ease',
          }}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}

// ── Anomaly Sidebar ───────────────────────────────────────────────────────────

function AnomalySidebar({ anomalies }) {
  return (
    <div style={{
      background: '#1a1d2e', border: '1px solid #2d3148',
      borderRadius: 10, overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '10px 14px',
        borderBottom: '1px solid #2d3148',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#94a3b8' }}>
          🚨 Recent Anomalies
        </span>
        <span style={{
          background: anomalies.length > 0 ? 'rgba(239,68,68,0.15)' : 'rgba(34,197,94,0.15)',
          color: anomalies.length > 0 ? '#ef4444' : '#22c55e',
          border: `1px solid ${anomalies.length > 0 ? '#ef4444' : '#22c55e'}55`,
          fontSize: 11, fontWeight: 700,
          padding: '2px 8px', borderRadius: 999,
        }}>
          {anomalies.length}
        </span>
      </div>

      {/* Body */}
      {anomalies.length === 0 ? (
        <div style={{ padding: '20px 14px', textAlign: 'center', color: '#64748b', fontSize: 12 }}>
          ✅ No anomalies detected
        </div>
      ) : (
        <div style={{ maxHeight: 440, overflowY: 'auto' }}>
          {[...anomalies].slice(-20).reverse().map(d => (
            <div key={d.id} style={{
              padding: '9px 14px',
              borderBottom: '1px solid #1e2235',
              background: 'rgba(239,68,68,0.03)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: '#f87171' }}>
                  {d.node_id}
                </span>
                <span style={{ fontSize: 10, color: '#64748b' }}>
                  {new Date(d.timestamp.endsWith('Z') ? d.timestamp : d.timestamp + 'Z').toLocaleTimeString()}
                </span>
              </div>
              <div
                style={{
                  fontSize: 11, color: '#fca5a5', marginBottom: 3,
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                }}
                title={d.anomaly_reason}
              >
                {d.anomaly_reason}
              </div>
              <div style={{ fontSize: 10, color: '#64748b' }}>
                T:{d.temperature?.toFixed(1)}°C · V:{d.vibration?.toFixed(3)}g · I:{d.current?.toFixed(2)}A
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export default function Dashboard() {
  const [sensorData,   setSensorData]   = useState([]);
  const [nodeStats,    setNodeStats]    = useState([]);
  const [alerts,       setAlerts]       = useState([]);
  const [connected,    setConnected]    = useState(false);
  const pollRef = useRef(null);

  // ── Data loading ──────────────────────────────────────────────────────────
  const loadData = useCallback(async () => {
    try {
      const [data, nodes] = await Promise.all([
        fetchSensorData({ limit: MAX_POINTS, minutes: 30 }),
        fetchNodes(),
      ]);
      setSensorData(data);
      setNodeStats(nodes);
    } catch (e) { /* backend may not be up yet */ }
  }, []);

  useEffect(() => {
    loadData();
    pollRef.current = setInterval(loadData, POLL_MS);
    return () => clearInterval(pollRef.current);
  }, [loadData]);

  // ── WebSocket ─────────────────────────────────────────────────────────────
  useEffect(() => {
    const sock = getSocket();

    sock.on('connect',    () => setConnected(true));
    sock.on('disconnect', () => setConnected(false));

    sock.on('new_sensor_data', point => {
      setSensorData(prev => {
        // Prepend newest point to match loadData's sort order (newest-first)
        const next = [point, ...prev];
        return next.length > MAX_POINTS ? next.slice(0, MAX_POINTS) : next;
      });
    });

    sock.on('anomaly_alert', alert => {
      setAlerts(prev => [...prev, alert]);
    });

    return () => {
      sock.off('connect');
      sock.off('disconnect');
      sock.off('new_sensor_data');
      sock.off('anomaly_alert');
    };
  }, []);

  const anomalies = sensorData.filter(d => d.is_anomaly);

  return (
    <div>
      {/* ── Node Summary Bar (full-width) ───────────────────────────────── */}
      <NodeSummaryBar
        nodeStats={nodeStats}
        sensorData={sensorData}
        connected={connected}
        totalBuffered={sensorData.length}
      />

      {/* ── Top Section: Three Real-time Charts ─────────────────────────── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: 16,
        marginBottom: 20
      }}>
        {METRICS.map(m => (
          <SensorChart
            key={m.id}
            data={sensorData}
            metric={m.id}
            thresholds={THRESHOLDS[m.id]}
          />
        ))}
      </div>

      {/* ── Bottom Section: Detail Cards + Sidebar ─────────────────────── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 300px',
        gap: 16,
        alignItems: 'start',
      }}>

        {/* ── LEFT: Node status details ─────────────────────────────────── */}
        <div>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: '#94a3b8' }}>
            🛰️ Active Edge Nodes
          </h2>
          {nodeStats.length > 0 ? (
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {nodeStats.map(n => (
                <NodeCard key={n.node_id} node={n} />
              ))}
            </div>
          ) : (
            <div style={{ padding: 40, textAlign: 'center', background: '#1a1d2e', borderRadius: 12, border: '1px dashed #2d3148', color: '#64748b' }}>
              Waiting for node data...
            </div>
          )}
        </div>

        {/* ── RIGHT: Sidebar ─────────────────────────────────────────────── */}
        <div style={{
          display: 'flex', flexDirection: 'column', gap: 12,
          position: 'sticky', top: 16,
        }}>
          {/* Alert banners (live WebSocket anomalies) */}
          <AlertBanner alerts={alerts} />

          {/* Scrollable anomaly log */}
          <AnomalySidebar anomalies={anomalies} />
        </div>
      </div>
    </div>
  );
}
