import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';

const METRIC_META = {
  temperature: { label: 'Temperature (°C)', color1: '#f59e0b', color2: '#fcd34d', unit: '°C' },
  vibration:   { label: 'Vibration (g)',     color1: '#6366f1', color2: '#818cf8', unit: 'g'  },
  current:     { label: 'Current (A)',        color1: '#22c55e', color2: '#86efac', unit: 'A'  },
};

const CustomTooltip = ({ active, payload, label, unit }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#1a1d2e', border: '1px solid #2d3148',
      borderRadius: 8, padding: '8px 12px', fontSize: 12,
    }}>
      <p style={{ color: '#94a3b8', marginBottom: 4 }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color, marginBottom: 2 }}>
          {p.name}: <strong>{p.value?.toFixed(3)}{unit}</strong>
        </p>
      ))}
    </div>
  );
};

export default function SensorChart({ data, metric, thresholds = {} }) {
  const meta = METRIC_META[metric];
  if (!meta) return null;

  // 1. Sort data chronologically (oldest first) for Recharts
  const sortedData = [...(data || [])].sort((a, b) => 
    new Date(a.timestamp) - new Date(b.timestamp)
  );

  // 2. Identify nodes dynamically or fallback to common prefixes
  const nodeIds = [...new Set(sortedData.map(d => d.node_id))];
  const physId = nodeIds.find(id => id.includes('physical') || id.includes('ESP32')) || nodeIds[0];
  const simId  = nodeIds.find(id => id.includes('simulated') && id !== physId) || nodeIds[1];

  const physData = sortedData.filter(d => d.node_id === physId).slice(-60);
  const simData  = sortedData.filter(d => d.node_id === simId).slice(-60);

  // 3. Merge into unified time-indexed array
  const timeMap = new Map();
  sortedData.forEach(d => {
    if (!d.timestamp) return;
    // Force UTC parsing by appending 'Z' if missing, then toLocaleTimeString converts to current local timing
    const dateObj = new Date(d.timestamp.endsWith('Z') ? d.timestamp : d.timestamp + 'Z');
    const timeKey = dateObj.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    if (!timeMap.has(timeKey)) {
      timeMap.set(timeKey, { time: timeKey, timeMs: dateObj.getTime() });
    }
    const entry = timeMap.get(timeKey);
    
    if (d.node_id === physId) entry.physical = d[metric];
    if (d.node_id === simId) entry.simulated = d[metric];
  });

  const merged = Array.from(timeMap.values())
    .sort((a, b) => a.timeMs - b.timeMs)
    .slice(-60); // Keep latest 60 time buckets

  return (
    <div style={{
      background: '#1a1d2e',
      border: '1px solid #2d3148',
      borderRadius: 12,
      padding: '14px 16px',
    }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, color: '#94a3b8', marginBottom: 10 }}>
        {meta.label}
      </h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={merged} margin={{ top: 4, right: 8, bottom: 0, left: -10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3148" vertical={false} />
          <XAxis
            dataKey="time"
            tick={{ fill: '#64748b', fontSize: 9 }}
            interval="preserveStartEnd"
            minTickGap={40}
            axisLine={{ stroke: '#2d3148' }}
            tickLine={false}
          />
          <YAxis 
            tick={{ fill: '#64748b', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={35}
          />
          <Tooltip content={<CustomTooltip unit={meta.unit} />} />
          <Legend
            wrapperStyle={{ fontSize: 10, paddingTop: 8 }}
            formatter={v => v === 'physical' ? 'Physical' : 'Simulated'}
          />
          {thresholds.max && (
            <ReferenceLine y={thresholds.max} stroke="#ef4444" strokeDasharray="4 2"
              label={{ value: 'max', fill: '#ef4444', fontSize: 10 }} />
          )}
          {thresholds.min && (
            <ReferenceLine y={thresholds.min} stroke="#f59e0b" strokeDasharray="4 2"
              label={{ value: 'min', fill: '#f59e0b', fontSize: 10 }} />
          )}
          <Line
            type="monotone"
            dataKey="physical"
            stroke={meta.color1}
            dot={false}
            strokeWidth={2}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="simulated"
            stroke={meta.color2}
            dot={false}
            strokeWidth={2}
            strokeDasharray="5 3"
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
