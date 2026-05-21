import React, { useState } from 'react';
import Dashboard       from './components/Dashboard';
import BlockchainAudit from './components/BlockchainAudit';
import FLNetworkGraph  from './components/FLNetworkGraph';
import './App.css';

const TABS = [
  { id: 'dashboard',  label: '📊 Dashboard' },
  { id: 'blockchain', label: '⛓️ Blockchain Audit' },
  { id: 'fl',         label: '🤝 FL Network' },
];

export default function App() {
  const [tab, setTab] = useState('dashboard');

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <span className="brand-icon">⚙️</span>
            <div>
              <div className="brand-title">IoT Predictive Maintenance</div>
              <div className="brand-sub">Hybrid Physical + Simulated · Blockchain · Federated Learning</div>
            </div>
          </div>
          <nav className="nav">
            {TABS.map(t => (
              <button
                key={t.id}
                className={`nav-btn ${tab === t.id ? 'active' : ''}`}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="main">
        {tab === 'dashboard'  && <Dashboard />}
        {tab === 'blockchain' && (
          <section>
            <h2 className="section-title">⛓️ Blockchain Audit Log</h2>
            <p className="section-desc">
              Every sensor payload is SHA-256 hashed and linked into an immutable chain.
              Red rows indicate tampered or broken records. Use the Tamper Test button for Phase 5 validation.
            </p>
            <BlockchainAudit />
          </section>
        )}
        {tab === 'fl' && (
          <section>
            <h2 className="section-title">🤝 Federated Learning Network</h2>
            <p className="section-desc">
              Node 1 and Node 2 exchange model weights every {' '}
              <strong style={{ color: '#6366f1' }}>30 seconds</strong>{' '}
              using FedAvg. No central aggregator — all learning is peer-to-peer.
            </p>
            <FLNetworkGraph />
          </section>
        )}
      </main>
    </div>
  );
}
