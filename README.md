# IoT Predictive Maintenance — Hybrid Physical / Simulated

> **Three sensors · Two nodes · Blockchain integrity · Peer-to-peer Federated Learning**

---

## Architecture at a Glance

```
ESP32 (hardware)
      │  serial
      ▼
physical_node.py (Node 1)          simulated_node.py (Node 2)
  • SHA-256 hashes every payload     • Generates realistic synthetic data
  • Local z-score anomaly detector   • Same hash + ML stack
  • FL peer listener  :5001    ◄────► FL peer listener  :5002
  • FedAvg weight exchange            (offset by interval/2 to avoid collision)
      │                                     │
      └──────────────┬──────────────────────┘
                     ▼
          backend/app.py   (Flask + SocketIO, port 5000)
          • Receives hashed payloads
          • Validates & links blockchain blocks (SQLite / PostgreSQL)
          • /api/audit  – recalculates all hashes
          • /api/fl/*   – logs FL exchanges
          • WebSocket   – pushes live events to frontend
                     │
                     ▼
          frontend/  (React, port 3000)
          • Real-time Recharts for Temperature / Vibration / Current
          • Dual-node side-by-side views
          • Blockchain Audit (🟢 Valid / 🔴 Tampered)
          • FL Network Graph (animated weight-exchange SVG)
          • Anomaly alert banners
```

---

## Quick Start (Windows)

```
start_system.bat
```

That single script opens four console windows for backend, node 1, node 2, and frontend.

---

## Manual Start

### 1 – Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2 – Physical Node (simulation mode, no ESP32 needed)

```bash
cd edge_nodes
pip install -r requirements.txt
python physical_node.py --simulate
```

### 3 – Simulated Node

```bash
cd edge_nodes
python simulated_node.py
```

### 4 – Frontend

```bash
cd frontend
npm install
npm start
```

Visit **http://localhost:3000**

---

## Real ESP32

If you have an ESP32 that sends JSON lines over serial
`{"temp":42.3,"vib":1.24,"cur":6.5}`, run:

```bash
python physical_node.py --port COM3 --baud 115200
```

The script will attempt the serial port and fall back to simulation automatically.

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET  | /api/health | Health check |
| POST | /api/data   | Ingest sensor payload (edge nodes) |
| GET  | /api/data   | Query recent readings (optional `?node_id=`, `?minutes=`, `?limit=`) |
| GET  | /api/audit  | Blockchain audit — recalculates all hashes |
| GET  | /api/nodes  | Node statistics |
| POST | /api/fl/log | Log an FL weight exchange |
| GET  | /api/fl/status | FL exchange history |
| POST | /api/tamper/:id | **Testing only** — corrupt a record to verify tamper detection |

---

## Payload Schema

```json
{
  "node_id":        "node_physical",
  "temperature":    42.35,
  "vibration":      1.2300,
  "current":        6.51,
  "timestamp":      "2024-01-15T10:30:00.000",
  "hash":           "<sha256 of canonical JSON>",
  "is_anomaly":     false,
  "anomaly_reason": ""
}
```

Hash is computed over:
```json
{"node_id": "...", "temperature": 42.35, "vibration": 1.23, "current": 6.51, "timestamp": "..."}
```
(sorted keys, 4 decimal places)

---

## Phase 5 – Tamper Test

1. Open the **Blockchain Audit** tab and click *Enable Tamper Test*.
2. Click **Tamper** next to any block.
3. Enter a fake temperature (e.g. `999`).
4. Click **Refresh** — that block turns **red** because the stored hash no longer matches.

---

## Configuration

Copy `.env.example` to `.env` in `backend/` and `edge_nodes/` and adjust:

| Variable | Default | Notes |
|---|---|---|
| `FL_EXCHANGE_INTERVAL` | 60 | Seconds between weight exchanges |
| `SEND_INTERVAL` | 2.0 | Seconds between sensor readings |
| `ANOMALY_TEMP_MAX` | 80 | Server-side temperature ceiling |
| `ANOMALY_VIBRATION_MAX` | 5.0 | Server-side vibration ceiling |
| `ANOMALY_CURRENT_MAX` | 15.0 | Server-side current ceiling |
| `DATABASE_URL` | SQLite | Set to Postgres URI for production |
