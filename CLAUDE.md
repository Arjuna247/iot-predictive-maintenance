# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Hybrid Physical/Simulated IoT Predictive Maintenance** system. It ingests three sensor metrics — Temperature, Vibration, and Current — from two parallel nodes: a physical ESP32 node (proxied via a local PC/Pi script) and a simulated Python node. Data integrity is enforced via a blockchain, and anomaly detection models are improved through decentralized (node-to-node) Federated Learning.

The full plan lives in `iotnewplan.md`.

## Architecture

```
ESP32 (hardware)
     │
     ▼
Node 1 – Physical Proxy (Python)  ◄──► Node 2 – Simulated Node (Python)
  - SHA-256 hashes payload              - Generates synthetic sensor data
  - Trains local ML model               - Trains local ML model
  - Peer-to-peer FL weight exchange ◄──► Peer-to-peer FL weight exchange
     │                                         │
     └──────────────┬───────────────────────────┘
                    ▼
          Backend API (Flask or FastAPI)
          - Validates + links blockchain blocks
          - Stores to SQLite (dev) / PostgreSQL (prod)
          - Exposes REST endpoints for dashboard & audit
                    │
                    ▼
          React Frontend
          - Dual-node real-time charts (Chart.js / Recharts)
          - Anomaly / drastic-change alert banners
          - Blockchain audit log view (Green = valid, Red = tampered)
          - FL Network Graph (node connections, accuracy)
```

## Key Design Decisions

- **Three metrics only:** Temperature, Vibration, Current. Every sensor payload must include these plus `node_id` and a `hash`.
- **Blockchain is lightweight and embedded:** Each backend insert links to the previous block's hash. No external chain. The `/api/audit` endpoint recalculates all hashes to detect tampering.
- **Federated Learning is peer-to-peer (no central aggregator):** Node 1 and Node 2 exchange model weights directly (ZeroMQ, WebSockets, or lightweight Flask servers on each edge node) and each performs local FedAvg.
- **Database:** SQLite for development/MVP; PostgreSQL for production. Two main tables: `SensorData` and `BlockchainLedger`.

## Planned Tech Stack

| Layer | Technology |
|---|---|
| Edge nodes | Python (physical proxy + simulator) |
| ML models | scikit-learn (`.pkl`) or similar lightweight library |
| P2P FL transport | ZeroMQ, WebSockets, or Flask-on-edge |
| Backend API | Flask or FastAPI |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Frontend | React |
| Charts | Chart.js or Recharts |

## Implementation Phases (from `iotnewplan.md`)

1. **Phase 1 – Ingestion & DB Setup:** Define `SensorData` and `BlockchainLedger` schemas; build REST API to receive `(node_id, temperature, vibration, current, hash)` payloads; adapt ESP32 proxy.
2. **Phase 2 – Blockchain Integrity:** Hashing utility on edge nodes; chain-link logic on backend; `/api/audit` endpoint.
3. **Phase 3 – Simulated Node & P2P FL:** `simulated_node.py` with realistic synthetic data; peer listeners for weight exchange; local FedAvg merging.
4. **Phase 4 – React Dashboard:** Real-time charts for 3 metrics per node; blockchain audit UI; FL network graph.
5. **Phase 5 – Testing:** End-to-end ESP32 flow; tamper detection via manual DB alteration; FL convergence verification.

## Conventions to Follow

- Edge node scripts should be self-contained Python files (`physical_node.py`, `simulated_node.py`).
- The backend API must be stateless with respect to ML — models live on edge nodes, not the server.
- Hash computation: SHA-256 over the canonical JSON of `{node_id, temperature, vibration, current, timestamp}` before POSTing.
- Anomaly thresholds and FL exchange intervals should be configurable via environment variables or a config file, not hard-coded.

