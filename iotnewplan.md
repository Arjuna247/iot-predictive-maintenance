# Hybrid Physical/Simulated IoT Predictive Maintenance Plan

## 1. Objective
To build a secure, intelligent web application for IoT predictive maintenance. The system will ingest three specific metrics (Temperature, Vibration, Current) from an existing physical ESP32 setup and a parallel simulated node. It will ensure data immutability via Blockchain and employ Decentralized (Node-to-Node) Federated Learning to improve anomaly detection models without centralized training.

## 2. Core Architecture & Workflow

### 2.1. The Edge Nodes
*   **Node 1 (Physical Gateway):** A local script (e.g., running on a PC or Raspberry Pi on the same network as the ESP32) that acts as a proxy. It receives live readings from the physical ESP32.
*   **Node 2 (Simulated Node):** A Python script generating synthetic readings matching the ESP32's format.
*   **Edge Responsibilities:** 
    *   **Hashing:** Both nodes cryptographically hash their sensor payloads (SHA-256) before transmission to create the foundational blocks for the Blockchain.
    *   **Local ML:** Both nodes maintain local predictive maintenance models and train them on their respective data streams.

### 2.2. Node-to-Node Federated Learning (Decentralized FL)
Instead of a central server aggregating weights, Node 1 and Node 2 will establish direct peer-to-peer communication (or use a lightweight broker). 
*   They will periodically exchange their model weights (`.pkl` files or arrays).
*   Each node will perform local Federated Averaging (`FedAvg`) to merge its peer's knowledge into its own model, achieving consensus without a central coordinator.

### 2.3. Central Server & Database Layer
*   **API Gateway (Flask/FastAPI):** Receives the hashed data blocks from both nodes.
*   **Blockchain Verification:** The server validates the hashes and links them into an immutable chain.
*   **Database:** A robust database (e.g., SQLite for MVP, PostgreSQL for production) will replace the `JSONL` files to store the sensor readings, hash signatures, and anomaly flags securely.

### 2.4. Presentation Layer (React Web App)
*   **Dual-Node Real-time Dashboard:** Visualizes live streams of Temperature, Vibration, and Current. The UI must explicitly distinguish and display side-by-side (or overlaid) charts for both the physical ESP32 node and the simulated node.
*   **Drastic Change / Anomaly Alerts:** A prominent alerting system (visual notifications/banners) that triggers immediately when either node experiences drastic reading changes 
(identified via thresholds or the local ML model), indicating that the monitored machine requires maintenance attention.
*   **Blockchain Audit Log:** A view to verify data integrity, flagging any records in the DB where the hash does not match the data (tampering detection).
*   **FL Network Graph:** A visual representation of the nodes, showing when weight exchanges occur and the current accuracy of the distributed models.

## 3. Implementation Phases

### Phase 1: Ingestion & Database Setup
1.  Initialize a relational Database (SQLite/PostgreSQL) with tables for `SensorData` and `BlockchainLedger`.
2.  Create the backend REST API to receive JSON payloads containing `(node_id, temperature, vibration, current, hash)`.
3.  Adapt the physical ESP32 (or write a Python proxy script) to POST data to this API.

### Phase 2: Blockchain Data Integrity
1.  Implement a hashing utility on the Edge Nodes (Python proxy for ESP32, and the Sim script).
2.  Implement the chain logic on the Backend: When inserting into the DB, calculate the `previous_hash` link and verify the incoming block.
3.  Create an audit endpoint `/api/audit` that recalculates all hashes in the DB to prove immutability.

### Phase 3: Simulated Node & Node-to-Node FL
1.  Build `simulated_node.py` to generate realistic synthetic data and post to the backend.
2.  Implement Peer-to-Peer FL: 
    *   Expose a lightweight listener on Node 1 and Node 2 (e.g., via ZeroMQ, WebSockets, or simple Flask servers on the edge).
    *   Write the logic for them to send weights to each other every *X* minutes, average them, and update their local models.

### Phase 4: React Dashboard Development
1.  Connect the React frontend to the Database via the Backend API.
2.  Build the real-time charts (Chart.js/Recharts) for the 3 sensor metrics.
3.  Build the Blockchain validation UI (Green = Valid, Red = Tampered).

### Phase 5: Testing & Validation
1.  Verify the physical ESP32 data flows correctly into the DB.
2.  Manually alter a database record and verify the React dashboard catches the broken Blockchain hash.
3.  Observe the Node-to-Node FL exchange and verify anomaly detection improves.
