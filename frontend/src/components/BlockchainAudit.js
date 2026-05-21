import React, { useState, useEffect, useCallback } from 'react';
import { fetchAudit, fetchNodes, tamperRecord } from '../services/api';

const Badge = ({ ok, children }) => (
  <span style={{
    display: 'inline-block',
    padding: '2px 7px',
    borderRadius: 999,
    fontSize: 11,
    fontWeight: 600,
    background: ok ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',
    color: ok ? '#22c55e' : '#ef4444',
    border: `1px solid ${ok ? '#22c55e' : '#ef4444'}`,
  }}>{children}</span>
);

export default function BlockchainAudit() {
  const [audit, setAudit]           = useState(null);
  const [nodes, setNodes]           = useState([]);
  const [filterNode, setFilterNode] = useState('');
  const [loading, setLoading]       = useState(false);
  const [tamperMode, setTamperMode] = useState(false);
  const [tamperMsg, setTamperMsg]   = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [a, n] = await Promise.all([
        fetchAudit(filterNode ? { node_id: filterNode } : {}),
        fetchNodes(),
      ]);
      setAudit(a);
      setNodes(n);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filterNode]);

  useEffect(() => { load(); }, [load]);

  const handleTamper = async (sensorId) => {
    const newTemp = parseFloat(prompt('New temperature value (to corrupt record):', '999'));
    if (isNaN(newTemp)) return;
    try {
      await tamperRecord(sensorId, { temperature: newTemp });
      setTamperMsg(`✅ Record #${sensorId} tampered (temperature → ${newTemp}). Re-run audit to see red.`);
      load();
    } catch (e) {
      setTamperMsg('❌ Tamper failed.');
    }
  };

  const blocks = audit?.blocks ?? [];

  return (
    <div>
      {/* Summary bar */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 16 }}>
        {[
          { label: 'Total Blocks',   value: audit?.total_blocks ?? '—', color: '#e2e8f0' },
          { label: 'Valid Blocks',   value: audit?.valid_blocks ?? '—', color: '#22c55e' },
          { label: 'Invalid Blocks', value: audit?.invalid_blocks ?? '—', color: '#ef4444' },
          { label: 'Integrity',      value: audit ? `${audit.integrity_score}%` : '—',
            color: (audit?.integrity_score ?? 100) >= 100 ? '#22c55e' : '#ef4444' },
        ].map(s => (
          <div key={s.label} style={{
            background: '#1a1d2e', border: '1px solid #2d3148',
            borderRadius: 10, padding: '10px 18px', textAlign: 'center', flex: 1,
          }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 11, color: '#94a3b8' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        <select
          value={filterNode}
          onChange={e => setFilterNode(e.target.value)}
          style={{ background: '#1a1d2e', border: '1px solid #2d3148', color: '#e2e8f0', padding: '6px 10px', borderRadius: 6 }}
        >
          <option value="">All Nodes</option>
          {nodes.map(n => <option key={n.node_id} value={n.node_id}>{n.node_id}</option>)}
        </select>
        <button onClick={load} style={btnStyle('#6366f1')}>
          {loading ? '…' : '🔄 Refresh'}
        </button>
        <button onClick={() => setTamperMode(t => !t)} style={btnStyle(tamperMode ? '#ef4444' : '#64748b')}>
          {tamperMode ? '🔴 Tamper Mode ON' : '⚙️ Enable Tamper Test'}
        </button>
      </div>

      {tamperMsg && (
        <div style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid #6366f1', borderRadius: 8,
          padding: '8px 12px', marginBottom: 12, fontSize: 13 }}>
          {tamperMsg}
        </div>
      )}

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #2d3148', color: '#64748b' }}>
              {['#', 'Node', 'Timestamp', 'Data Hash', 'Block Hash', 'Hash ✓', 'Chain ✓', 'Data ✓', 'Status', tamperMode && 'Tamper'].filter(Boolean).map(h => (
                <th key={h} style={{ padding: '8px 10px', textAlign: 'left', fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {blocks.map((b, i) => (
              <tr key={b._id || b.id || i}
                style={{
                  borderBottom: '1px solid #1e2235',
                  background: b.is_valid ? 'transparent' : 'rgba(239,68,68,0.05)',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = b.is_valid ? '#1e2235' : 'rgba(239,68,68,0.1)'}
                onMouseLeave={e => e.currentTarget.style.background = b.is_valid ? 'transparent' : 'rgba(239,68,68,0.05)'}
              >
                <td style={{ padding: '7px 10px', color: '#94a3b8' }}>{b.block_index}</td>
                <td style={{ padding: '7px 10px' }}>{b.node_id}</td>
                <td style={{ padding: '7px 10px', color: '#94a3b8' }}>{new Date(b.timestamp).toLocaleString()}</td>
                <td style={{ padding: '7px 10px', fontFamily: 'monospace', color: '#64748b', maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                  title={b.data_hash}>{b.data_hash?.slice(0, 12)}…</td>
                <td style={{ padding: '7px 10px', fontFamily: 'monospace', color: '#64748b', maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                  title={b.stored_hash}>{b.stored_hash?.slice(0, 12)}…</td>
                <td style={{ padding: '7px 10px' }}>
                  <Badge ok={b.hash_valid ?? (audit?.integrity_score === 100)}>
                    {b.hash_valid === undefined ? '?' : (b.hash_valid ? '✓' : '✗')}
                  </Badge>
                </td>
                <td style={{ padding: '7px 10px' }}>
                  <Badge ok={b.chain_valid ?? (audit?.integrity_score === 100)}>
                    {b.chain_valid === undefined ? '?' : (b.chain_valid ? '✓' : '✗')}
                  </Badge>
                </td>
                <td style={{ padding: '7px 10px' }}>
                  <Badge ok={b.data_integrity ?? (audit?.integrity_score === 100)}>
                    {b.data_integrity === undefined ? '?' : (b.data_integrity ? '✓' : '✗')}
                  </Badge>
                </td>
                <td style={{ padding: '7px 10px' }}>
                  <Badge ok={b.is_valid ?? (audit?.integrity_score === 100)}>
                    {b.is_valid === undefined ? '✅ Unverified' : (b.is_valid ? '✅ Valid' : '🔴 TAMPERED')}
                  </Badge>
                </td>
                {tamperMode && (
                  <td style={{ padding: '7px 10px' }}>
                    <button onClick={() => handleTamper(b.sensor_data_id || b._id)}
                      style={{ ...btnStyle('#ef4444'), padding: '3px 8px', fontSize: 11 }}>
                      Tamper
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {blocks.length === 0 && (
              <tr><td colSpan={9} style={{ padding: 24, textAlign: 'center', color: '#64748b' }}>
                No blocks yet. Start sending data from edge nodes.
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const btnStyle = color => ({
  background: `${color}22`,
  border: `1px solid ${color}`,
  color,
  padding: '6px 14px',
  borderRadius: 6,
  cursor: 'pointer',
  fontWeight: 600,
  fontSize: 12,
});
