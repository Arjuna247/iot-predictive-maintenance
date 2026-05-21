import React, { useEffect, useState } from 'react';
import { fetchFLStatus, getSocket } from '../services/api';

// ── Helpers ───────────────────────────────────────────────────────────────────

const getAccColor = acc => {
  if (acc == null) return '#64748b';
  if (acc >= 0.9)  return '#22c55e';
  if (acc >= 0.7)  return '#f59e0b';
  return '#ef4444';
};

const getStatusLabel = acc => {
  if (acc == null) return 'No data';
  if (acc >= 0.9)  return '● Active';
  if (acc >= 0.7)  return '◐ Training';
  return '○ Low';
};

const fmtAcc  = acc => (acc != null ? `${(acc * 100).toFixed(1)}%` : '—');
const fmtTime = ts  => (ts ? new Date(ts).toLocaleTimeString() : '—');

// ── Sub-components ────────────────────────────────────────────────────────────

const AccBadge = ({ acc }) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center', gap: 4,
    padding: '3px 10px', borderRadius: 999, fontSize: 11, fontWeight: 700,
    background: `${getAccColor(acc)}22`,
    color: getAccColor(acc),
    border: `1px solid ${getAccColor(acc)}66`,
  }}>
    {getStatusLabel(acc)}
  </span>
);

const DeltaBadge = ({ before, after }) => {
  if (before == null || after == null) return null;
  const delta = ((after - before) * 100).toFixed(1);
  const pos   = after >= before;
  return (
    <span style={{
      fontSize: 11,
      fontWeight: 700,
      color: pos ? '#22c55e' : '#ef4444',
    }}>
      {pos ? '▲' : '▼'} {Math.abs(delta)}%
    </span>
  );
};

// ── Node Status Card ──────────────────────────────────────────────────────────

function NodeStatusCard({ nodeId, acc, lastExchange }) {
  const isPhysical  = nodeId?.includes('physical');
  const icon        = isPhysical ? '🔌' : '🖥️';
  const label       = nodeId?.replace('node_', '') ?? nodeId;
  const accentColor = isPhysical ? '#6366f1' : '#22c55e';

  return (
    <div style={{
      flex: '1 1 200px',
      background: '#1a1d2e',
      border: `1px solid ${accentColor}44`,
      borderLeft: `3px solid ${accentColor}`,
      borderRadius: 10,
      padding: '14px 16px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <span style={{ fontSize: 22 }}>{icon}</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: 13, color: '#e2e8f0' }}>{label}</div>
          <div style={{ fontSize: 11, color: '#64748b' }}>{nodeId}</div>
        </div>
      </div>

      {/* Accuracy value */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
        <span style={{ fontSize: 11, color: '#94a3b8' }}>Model Accuracy</span>
        <span style={{ fontSize: 18, fontWeight: 700, color: getAccColor(acc) }}>
          {fmtAcc(acc)}
        </span>
      </div>

      {/* Progress bar */}
      <div style={{
        background: '#0f1120', borderRadius: 4,
        overflow: 'hidden', height: 5, marginBottom: 12,
      }}>
        <div style={{
          height: '100%',
          width: acc != null ? `${(acc * 100).toFixed(1)}%` : '0%',
          background: `linear-gradient(90deg, ${getAccColor(acc)}, ${getAccColor(acc)}88)`,
          transition: 'width 0.6s ease',
          borderRadius: 4,
        }} />
      </div>

      {/* Footer: badge + last exchange */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 6 }}>
        <AccBadge acc={acc} />
        <span style={{ fontSize: 10, color: '#475569' }}>
          {lastExchange ? `Last: ${fmtTime(lastExchange)}` : 'No exchange yet'}
        </span>
      </div>
    </div>
  );
}

// ── Exchange Timeline Row ─────────────────────────────────────────────────────

function ExchangeRow({ ex, highlight }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: 12,
      padding: '10px 0',
      borderBottom: '1px solid #1e2235',
      animation: highlight ? 'fl-fade-in 0.4s ease' : 'none',
    }}>
      {/* Timeline dot */}
      <div style={{ paddingTop: 4, flexShrink: 0 }}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          background: highlight ? '#6366f1' : '#2d3148',
          border: `2px solid ${highlight ? '#6366f1' : '#3d4168'}`,
          boxShadow: highlight ? '0 0 6px #6366f1' : 'none',
          transition: 'all 0.3s ease',
        }} />
      </div>

      {/* Exchange detail */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 3 }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: '#a5b4fc' }}>
            {ex.from_node?.replace('node_', '') ?? ex.from_node}
          </span>
          <span style={{ fontSize: 13, color: '#4b5563' }}>→</span>
          <span style={{ fontSize: 12, fontWeight: 700, color: '#86efac' }}>
            {ex.to_node?.replace('node_', '') ?? ex.to_node}
          </span>

          {ex.accuracy_before != null && ex.accuracy_after != null && (
            <>
              <span style={{ fontSize: 11, color: '#64748b' }}>
                {fmtAcc(ex.accuracy_before)}
                <span style={{ margin: '0 4px', color: '#4b5563' }}>→</span>
                {fmtAcc(ex.accuracy_after)}
              </span>
              <DeltaBadge before={ex.accuracy_before} after={ex.accuracy_after} />
            </>
          )}
        </div>
        <div style={{ fontSize: 10, color: '#475569' }}>
          {ex.timestamp ? new Date(ex.timestamp).toLocaleString() : '—'}
        </div>
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export default function FLNetworkGraph({ nodeStats }) {
  const [exchanges, setExchanges] = useState([]);
  const [newestId,  setNewestId]  = useState(null);
  const [loading,   setLoading]   = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchFLStatus({ limit: 30 });
      setExchanges(data);
    } catch (e) {
      console.error('FL status load error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const sock = getSocket();

    sock.on('fl_exchange', ev => {
      setExchanges(prev => [ev, ...prev].slice(0, 30));
      setNewestId(ev.id ?? `ts-${ev.timestamp}`);
    });

    return () => sock.off('fl_exchange');
  }, []);

  // Derive per-node accuracy and last exchange time from exchange log
  const accByNode          = {};
  const lastExchangeByNode = {};

  exchanges.forEach(ex => {
    if (accByNode[ex.from_node] == null) {
      accByNode[ex.from_node]          = ex.accuracy_after;
      lastExchangeByNode[ex.from_node] = ex.timestamp;
    }
    if (accByNode[ex.to_node] == null) {
      accByNode[ex.to_node]          = ex.accuracy_after;
      lastExchangeByNode[ex.to_node] = ex.timestamp;
    }
  });

  // Unique node IDs from stats prop + exchange log
  const nodeIds = [...new Set([
    ...(nodeStats || []).map(n => n.node_id),
    ...exchanges.flatMap(e => [e.from_node, e.to_node]),
  ])].filter(Boolean);

  // Overall average accuracy
  const accValues  = Object.values(accByNode).filter(a => a != null);
  const overallAcc = accValues.length > 0
    ? accValues.reduce((a, b) => a + b, 0) / accValues.length
    : null;

  return (
    <div>
      {/* ── Summary stats bar ──────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16 }}>
        {[
          { label: 'Total Exchanges',  value: exchanges.length,          color: '#6366f1' },
          { label: 'Active Nodes',     value: nodeIds.length,            color: '#22c55e' },
          { label: 'Avg Accuracy',     value: fmtAcc(overallAcc),        color: getAccColor(overallAcc) },
          { label: 'Last Exchange',    value: exchanges[0]?.timestamp
              ? fmtTime(exchanges[0].timestamp) : '—',                   color: '#94a3b8' },
        ].map(s => (
          <div key={s.label} style={{
            flex: '1 1 110px',
            background: '#1a1d2e', border: '1px solid #2d3148',
            borderRadius: 8, padding: '10px 14px', textAlign: 'center',
          }}>
            <div style={{ fontSize: 18, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* ── Node Status Cards ───────────────────────────────────────────────── */}
      {nodeIds.length > 0 ? (
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
          {nodeIds.map(nid => (
            <NodeStatusCard
              key={nid}
              nodeId={nid}
              acc={accByNode[nid]}
              lastExchange={lastExchangeByNode[nid]}
            />
          ))}
        </div>
      ) : (
        <div style={{
          background: '#1a1d2e', border: '1px dashed #2d3148',
          borderRadius: 10, padding: '28px', textAlign: 'center',
          color: '#64748b', fontSize: 13, marginBottom: 20,
        }}>
          🤝 No FL data yet — nodes will exchange weights every{' '}
          <strong style={{ color: '#6366f1' }}>
            {process.env.REACT_APP_FL_INTERVAL || 30}s
          </strong>
        </div>
      )}

      {/* ── Exchange Timeline ───────────────────────────────────────────────── */}
      <div style={{
        background: '#1a1d2e', border: '1px solid #2d3148',
        borderRadius: 12, padding: 16,
      }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', marginBottom: 12,
        }}>
          <h3 style={{ margin: 0, fontSize: 13, fontWeight: 600, color: '#94a3b8' }}>
            Weight Exchange Timeline
          </h3>
          <button
            onClick={load}
            disabled={loading}
            style={{
              background: 'none', border: '1px solid #2d3148',
              color: '#6366f1', cursor: 'pointer',
              fontSize: 12, borderRadius: 6, padding: '4px 10px',
              opacity: loading ? 0.5 : 1,
            }}
          >
            {loading ? '…' : '🔄 Refresh'}
          </button>
        </div>

        {exchanges.length === 0 ? (
          <p style={{ color: '#64748b', fontSize: 12, margin: 0 }}>
            No weight exchanges recorded yet. Waiting for first FedAvg round…
          </p>
        ) : (
          exchanges.map((ex, i) => {
            const rowId = ex.id ?? `ts-${ex.timestamp}-${i}`;
            return (
              <ExchangeRow
                key={rowId}
                ex={ex}
                highlight={i === 0 && rowId === newestId}
              />
            );
          })
        )}
      </div>

      {/* Keyframe for new-exchange highlight */}
      <style>{`
        @keyframes fl-fade-in {
          from { opacity: 0; transform: translateY(-5px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
