# IoT Predictive Maintenance: Implementation Guide & Claude Instructions

This document outlines the execution plan for Claude Code to implement ESP32 hardware integration, backend migration to MongoDB, and simplification of the Federated Learning (FL) visualization and Dashboard UI.

## 1. Clean Up & Simplification
- **Remove `node_wifi_test`**: Completely delete `node_wifi_test` from the project (e.g., `frontend/models/node_wifi_test.pkl` and any related references).
- **Remove Unused Code**: Scan for and remove any other dead or unused code across the directory to reduce complications and simplify the project.
- **Constraint**: **Do not make any changes to `node_simulated` (including `edge_nodes/simulated_node.py` and its models).**

## 2. Backend Migration: SQL to MongoDB
The backend code (`@backend/app.py`, `@backend/blockchain.py`, `@backend/config.py`) has been updated and a decision was made to use MongoDB instead of SQL.
- **Change the SQL schema to Mongo**: Replace SQLAlchemy (`db.Model`) in `@backend/models.py` with MongoDB schemas (e.g., using `flask_pymongo`, `mongoengine`, or raw `pymongo`).
- **Update Project Structure**: Refactor the database connections and models to fully support MongoDB. Remove SQLite/SQLAlchemy specific configurations and folders like `instance/`.
- **Refactor Logic**: Update all queries and insertions in `app.py` and `blockchain.py` to match the new MongoDB document structure.

## 3. ESP32 Physical Integration (REST API Path)
Instead of relying solely on Serial or Simulation, add a dedicated HTTP listener to the Physical Node Proxy.
- **Proxy Side Implementation (`physical_node.py`)**:
  - Add a lightweight Flask server on a background thread (e.g., port `5005`).
  - Add Endpoint: `POST /esp32/data`
  - Logic: Received data bypasses simulation and is treated as the primary sensor reading, following the standard pipeline (ML Anomaly Detection -> Hashing -> Backend Submission).
- **ESP32 Side Instructions**:
  - Provide a README or pseudo-code showing how to `WiFi.begin(...)` and send a JSON POST (`{"temperature": 45.2, "vibration": 1.05, "current": 6.8}`) to the Proxy's IP on port 5005.

## 4. Federated Learning (FL) Simplification
The current SVG-based network graph is complex and hard to read. Replace it with a simplified metrics panel.
- **Remove Complex Graphs**: Delete the SVG and D3 logic from `FLNetworkGraph.js` or related components.
- **Simplified Metrics Panel**: Set hardcoded/simulated metrics or configure the system to display:
  - **Last Sync Time**: Display "2 secs ago".
  - **Avg Accuracy**: Display "88%".
  - **Active Nodes**: Display "2".
- **Local Exchanges Realtime**: Ensure the local FL exchanges happen in real-time, specifically every 30 seconds.

## 5. Dashboard Streamlining
Reorganize the dashboard into a "Command Center" layout to reduce clutter.
- **Tabbed Chart View (`Dashboard.js`)**: Instead of showing 3 large charts vertically, implement a tab switcher: `[ Temperature | Vibration | Current ]`. This keeps the most relevant chart in focus.
- **Unified Sidebar**: Move the "Recent Anomalies" table and "Alert Banners" into a right-side scrollable panel.
- **Node Summary Bar**: Keep a slim horizontal bar at the top showing connectivity status and average metrics for both Physical and Simulated nodes.

## Execution Checklist for Claude Code
1.  **Cleanup**: Delete `node_wifi_test` and any unused code. Leave `node_simulated` alone.
2.  **Database Migration**: Refactor `backend/models.py`, `backend/app.py`, `backend/config.py`, and `backend/blockchain.py` for MongoDB. Update project structure.
3.  **Physical Proxy**: Update `physical_node.py` to include a Flask listener for ESP32 POST requests.
4.  **FL Dashboard**: Remove D3/SVGs. Implement the simplified FL metrics (2 secs last exchange, 88% avg accuracy, 2 active nodes, 30s local exchange).
5.  **Main Dashboard**: Implement the tabbed chart view and sidebar layout in `Dashboard.js`.