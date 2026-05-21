# Project Documentation

Date: 2026-05-21

## Summary

This repository implements a Hybrid Physical/Simulated IoT Predictive Maintenance system. It ingests three sensor metrics — Temperature, Vibration, and Current — from two parallel nodes: a physical ESP32 proxy node and a simulated Python node. Data integrity is enforced via an embedded blockchain; model improvements are coordinated via peer-to-peer Federated Learning (FL). The system includes edge node scripts, a backend API, and a React frontend dashboard.

## High-level architecture

- Edge nodes (two):
  - Physical proxy node: collects data from ESP32 (proxied) and posts to backend.
  - Simulated node: generates synthetic sensor data for testing and FL.
- Peer-to-peer FL: edge nodes exchange model weights directly and perform local FedAvg.
- Backend API: receives sensor payloads, verifies blockchain linkage, persists data (SQLite for dev), and exposes audit endpoints.
- Frontend: React app showing real-time charts, blockchain audit view, FL network graph, and alerts.

## Project structure

```
d:/iot
├─ backend/
│  ├─ app.py
│  ├─ blockchain.py
│  ├─ config.py
│  ├─ models.py
│  ├─ requirements.txt
│  └─ instance/
├─ edge_nodes/
│  ├─ fl_peer.py
│  ├─ hashing_utils.py
│  ├─ ml_model.py
│  ├─ physical_node.py
│  ├─ requirements.txt
│  ├─ simulated_node.py
│  └─ models/
├─ frontend/
│  ├─ package.json
│  └─ src/
│     ├─ App.js
│     ├─ App.css
│     ├─ index.js
│     ├─ index.css
│     └─ components/
│        ├─ AlertBanner.js
│        ├─ BlockchainAudit.js
│        ├─ Dashboard.js
│        ├─ FLNetworkGraph.js
│        ├─ NodeCard.js
│        └─ SensorChart.js
├─ CLAUDE.md
├─ iotnewplan.md
├─ README.md
├─ start_system.bat
└─ PROJECT_DOCUMENTATION.md
```

## Key folders and files (detailed)

- backend/
  - app.py: FastAPI or Flask-based HTTP API server. Implements endpoints to receive sensor payloads (POST), to run blockchain audits (GET), and to expose data for the frontend. Responsible for validating payload structure and chaining incoming blocks.
  - blockchain.py: Lightweight blockchain utilities used by the backend to link blocks by hashing canonical payloads. Provides functions to create ledger entries, validate chain integrity, and recompute hashes for audit.
  - config.py: Central configuration (DB path, secret keys, thresholds, FL settings). Environment-aware: development vs production flags.
  - models.py: Database models (SQLite during development). Contains `SensorData` and `BlockchainLedger` table definitions and helpers to persist/retrieve records.
  - requirements.txt: Python dependencies required by backend (Flask/FastAPI, SQLAlchemy, uvicorn/gunicorn, etc.).
  - instance/: runtime-created folder for SQLite DB and local instance data.

- edge_nodes/
  - physical_node.py: Proxy script that interfaces with an ESP32 (or a proxied feed) to collect raw sensor readings. It constructs canonical JSON payloads containing `node_id`, `temperature`, `vibration`, `current`, `timestamp`, computes a SHA-256 `hash`, and POSTs to the backend endpoint.
  - simulated_node.py: Standalone simulator generating realistic synthetic streams for the same three metrics. Used for testing dashboards and FL behavior.
  - fl_peer.py: Implements the peer-to-peer Federated Learning logic. Handles weight serialization, transport (ZeroMQ/WebSockets/HTTP peer), and FedAvg merging logic. Runs on each edge node to periodically exchange and merge model weights.
  - hashing_utils.py: Canonical JSON hashing utilities used by all nodes to ensure consistent hash computation for blockchain linking.
  - ml_model.py: Lightweight ML model implementation (scikit-learn or similar) for local anomaly detection or predictive maintenance. Exposes `train()`, `predict()`, `serialize()` and `deserialize()` helpers.
  - requirements.txt: Python dependencies for edge node scripts (numpy, scikit-learn, requests, pyzmq or websockets).
  - models/: optional directory for saved model artifacts (pickled `.pkl`) created by edge nodes.

- frontend/
  - package.json: Node package manifest for the React app.
  - public/index.html: HTML entry for the single-page app.
  - src/index.js: React bootstrap.
  - src/App.js, App.css: Main application shell and styles.
  - src/components/:
    - AlertBanner.js: UI component that shows anomaly or drastic-change alerts.
    - BlockchainAudit.js: UI for running/reviewing blockchain audit; shows green/red entries depending on tamper detection.
    - Dashboard.js: Layout for per-node real-time charts and status.
    - FLNetworkGraph.js: Visualization of FL peer connections and node accuracies over time.
    - NodeCard.js: Compact per-node summary card (latest metrics, last-seen, model accuracy).
    - SensorChart.js: Chart component (Chart.js or Recharts) for plotting time series per metric.
  - src/services/api.js: Client-side functions for calling backend endpoints (ingest, audit, live data websocket or polling).

- Root files
  - README.md: Project overview and quickstart (author-maintained). Review for run instructions.
  - iotnewplan.md: Longer-term plan and phased roadmap for the project (phases 1–5).
  - CLAUDE.md: Design notes and key decisions (mirrors many of the items documented here).
  - start_system.bat: Windows convenience script to start components for local dev (may invoke backend and frontend servers and/or simulators).

## Data model & payload format

All sensor payloads must include the following canonical fields before hashing and sending:

- node_id: unique identifier for the edge node (string)
- temperature: numeric
- vibration: numeric
- current: numeric
- timestamp: ISO 8601 UTC timestamp (string)
- hash: SHA-256 hex digest of the canonical JSON of the above fields (excluding the hash itself)

Hash computation rules (consistent across nodes):
1. Create an ordered (canonical) JSON object containing exactly `{node_id, temperature, vibration, current, timestamp}` (sorted keys consistently).
2. UTF-8 encode the JSON string (no extra whitespace) and compute the SHA-256 hex digest.
3. Include that digest as the `hash` field in the POST payload.

Example payload (conceptual):

```json
{
  "node_id": "node-1",
  "temperature": 36.7,
  "vibration": 0.004,
  "current": 0.12,
  "timestamp": "2026-05-21T12:34:56Z",
  "hash": "<sha256-hex>"
}
```

## Blockchain ledger behavior

- Each persisted record in `BlockchainLedger` includes: id, payload_hash, previous_hash, timestamp, and metadata.
- When a new sensor payload arrives, the backend computes the new block's `payload_hash` (verifying the provided `hash` matches) and sets `previous_hash` to the last ledger entry's `payload_hash`.
- The `/api/audit` endpoint recomputes hashes across the ledger to detect any tampering (mismatched recomputed hash → tampered record).

## Federated Learning (FL) approach

- Peer-to-peer: No central aggregator. Edge nodes connect (ZeroMQ, WebSockets, or simple HTTP endpoints) to exchange model weights.
- Exchange frequency and FedAvg parameters are configurable via environment variables.
- Each node trains locally using its collected data, serializes weights, exchanges with peers, and merges via weighted-average (FedAvg).
- Models remain on edge nodes; the backend is stateless with regard to ML models.

## Development & run instructions (local)

1. Backend (Python)

- Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

- Run the backend (example using uvicorn for FastAPI):

```powershell
cd backend
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

2. Edge nodes (simulator and physical proxy)

- Create a separate virtualenv and install edge requirements:

```powershell
python -m venv .venv-edge
.\.venv-edge\Scripts\Activate.ps1
pip install -r edge_nodes/requirements.txt
```

- Start simulated node:

```powershell
python edge_nodes/simulated_node.py
```

- Start physical proxy (if used):

```powershell
python edge_nodes/physical_node.py
```

3. Frontend (React)

```powershell
cd frontend
npm install
npm start
```

- The frontend expects the backend at the configured API base URL in `src/services/api.js`.

## Configuration & environment variables

- Backend config examples in `backend/config.py` include:
  - `DATABASE_URL` (default: SQLite file path in `instance/`)
  - `API_HOST`, `API_PORT`
  - `FL_EXCHANGE_INTERVAL` (seconds)
  - `ANOMALY_THRESHOLD` values used by edge models
- Edge nodes accept env vars or CLI args for `NODE_ID`, `BACKEND_URL`, and FL parameters.

## Conventions & design decisions

- Three metrics only: Temperature, Vibration, Current.
- Canonical JSON hashing must be identical on all nodes to ensure consistent blockchain behavior.
- The blockchain is intentionally lightweight and embedded in the backend database to support tamper-evidence and audits, not for decentralization.
- FL remains peer-to-peer and fully on-edge; backend does not store model weights.

## Testing & verification

- Manual tamper test: modify a row in the `BlockchainLedger` SQLite DB and call `/api/audit` to verify a tamper-detection (mismatched recomputed hash).
- FL convergence: run simulated node and physical node, enable FL exchange, and monitor model metrics in `FLNetworkGraph`.
- Unit tests: add tests for `hashing_utils`, `blockchain` validation, and backend endpoints.

## Next steps & suggestions

- Add automated integration tests for ingestion → storage → audit path.
- Add containerization (Dockerfiles) for backend and edge components for reproducible dev environments.
- Harden security (HTTPS, API auth) before exposing any endpoints beyond local dev.
- Add a recorded example dataset and a short script to seed the DB with representative data for demo purposes.

## Where to look in the code

- Backend entry point and API: [backend/app.py](backend/app.py)
- Ledger and blockchain logic: [backend/blockchain.py](backend/blockchain.py)
- Edge FL peer code: [edge_nodes/fl_peer.py](edge_nodes/fl_peer.py)
- Hash utilities: [edge_nodes/hashing_utils.py](edge_nodes/hashing_utils.py)
- Simulator: [edge_nodes/simulated_node.py](edge_nodes/simulated_node.py)
- Physical proxy: [edge_nodes/physical_node.py](edge_nodes/physical_node.py)
- Frontend app and components: [frontend/src/App.js](frontend/src/App.js) and [frontend/src/components/](frontend/src/components/)

---

This file was generated on 2026-05-21 to provide a single-source reference for the repository layout, data flows, and developer-oriented run instructions. If you want, I can:

- Add more granular file-by-file descriptions (function summaries and key lines).
- Create example payloads or a Postman collection for the API.
- Containerize services with Dockerfiles and a `docker-compose.yml`.

Tell me which next step you'd like. 
