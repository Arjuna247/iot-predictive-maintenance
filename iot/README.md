# 🤖 IoT Backend - Python ML & Blockchain Services

This directory contains the Python backend services for the Industrial IoT Predictive Maintenance System, including federated learning, blockchain ledger, and ML model training.

## 📂 File Structure

```
iot/
├── client_sim.py           # ESP32 IoT device simulator
├── esp32_data_server.py    # Flask server for receiving sensor data
├── model_utils.py          # Machine learning utilities
├── federated_ml.py         # Federated learning implementation
├── ledger.py               # Blockchain ledger for secure logging
├── distill.py              # Knowledge distillation for edge deployment
├── orchestrator.py         # Main orchestration system
├── generate_dummy_data.py  # Generate synthetic test data
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# From the project root directory
pip install -r requirements.txt
```

### 2. Generate Test Data (Optional)

```bash
cd iot
python generate_dummy_data.py 5000 0.1 3
# Args: num_samples anomaly_ratio num_devices
```

### 3. Start the Data Server

```bash
python esp32_data_server.py
```

The server will start on `http://0.0.0.0:5000`

### 4. Run ESP32 Simulators

In a new terminal:

```bash
python client_sim.py
```

Choose option 1 for single device or option 2 for multiple devices.

### 5. Run Federated Learning

After collecting data:

```bash
python federated_ml.py sensor_data.jsonl 5 3
# Args: data_file num_rounds num_clients
```

## 📋 Detailed Component Documentation

### 🔌 client_sim.py - ESP32 Device Simulator

Simulates ESP32 IoT devices sending sensor data to the server.

**Features:**
- Realistic sensor data generation (Temperature, Humidity, Vibration, Current)
- MPU6050-style accelerometer and gyroscope simulation
- Anomaly injection capability
- Multi-device simulation support

**Usage:**

```bash
# Single device
python client_sim.py

# With custom server URL
python client_sim.py http://192.168.1.100:5000
```

**Example Code:**

```python
from client_sim import ESP32Simulator

# Create simulator
simulator = ESP32Simulator("ESP32_01", "http://localhost:5000")

# Run for 60 seconds, inject anomaly after 30 seconds
simulator.run(duration=60, interval=2, inject_anomaly_after=30)
```

---

### 🌐 esp32_data_server.py - Data Collection Server

Flask REST API server for receiving and storing IoT sensor data.

**Endpoints:**

- `GET /` - Health check and API information
- `POST /sensor-data` - Receive sensor data from devices
- `GET /stats` - Get server statistics
- `GET /data` - Get all sensor data (limit: 100)
- `GET /data/latest` - Get latest reading from each device
- `GET /data/device/<device_id>` - Get data for specific device
- `GET /data/anomalies` - Get all anomaly readings
- `POST /clear` - Clear all data (testing only)

**Usage:**

```bash
python esp32_data_server.py
```

**Example API Call:**

```bash
# Get statistics
curl http://localhost:5000/stats

# Get latest readings
curl http://localhost:5000/data/latest

# Send sensor data
curl -X POST http://localhost:5000/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"ESP32_01","Temperature":28.5,"Humidity":65.0,"Vibration":0.02,"Current":0.15,"Anomaly":0}'
```

---

### 🧠 model_utils.py - Machine Learning Utilities

Comprehensive ML utilities for anomaly detection and predictive maintenance.

**Key Functions:**

- `load_sensor_data_from_file(file_path)` - Load data from JSONL
- `preprocess_data(df, features, target)` - Prepare train/test splits
- `train_local_model(X_train, y_train)` - Train Random Forest classifier
- `train_isolation_forest(X_train)` - Unsupervised anomaly detection
- `evaluate_model(model, X_test, y_test)` - Comprehensive evaluation
- `save_model(model, file_path)` - Save trained model
- `load_model(file_path)` - Load trained model
- `predict_anomaly(model, sensor_reading)` - Predict on new data
- `calculate_health_score(sensor_data)` - Calculate equipment health (0-100)

**Usage:**

```python
from model_utils import *

# Load data
df = load_sensor_data_from_file("sensor_data.jsonl")

# Prepare data
X_train, X_test, y_train, y_test = preprocess_data(df)

# Train model
model = train_local_model(X_train, y_train)

# Evaluate
acc, f1 = evaluate_model(model, X_test, y_test)

# Save model
save_model(model, "models/anomaly_model.pkl")

# Predict on new data
reading = {"Temperature": 45.0, "Humidity": 70.0, "Vibration": 0.15, "Current": 0.35}
prediction, probability = predict_anomaly(model, reading)
```

---

### 🔗 federated_ml.py - Federated Learning

Privacy-preserving distributed learning across multiple IoT devices.

**Features:**
- Federated averaging (FedAvg) algorithm
- Blockchain logging of training rounds
- Performance visualization
- Multi-client simulation

**Usage:**

```bash
# Run federated learning
python federated_ml.py sensor_data.jsonl 5 3

# Args:
#   - sensor_data.jsonl: Input data file
#   - 5: Number of training rounds
#   - 3: Number of clients
```

**Example Code:**

```python
from federated_ml import run_federated_learning

results = run_federated_learning(
    data_file="sensor_data.jsonl",
    num_rounds=5,
    num_clients=3,
    save_blockchain=True,
    plot_results=True
)

print(f"Best accuracy: {max(results['global_accuracies']):.4f}")
```

**Output:**
- Trained federated model saved to `models/federated_model.pkl`
- Blockchain ledger saved to `ledger.json`
- Performance plot saved to `federated_learning_results.png`

---

### ⛓️ ledger.py - Blockchain Ledger

Immutable blockchain for logging ML training events and system activities.

**Features:**
- Proof of Authority (PoA) style blockchain
- SHA-256 hash-based block linking
- Chain validation
- JSON export

**Usage:**

```python
from ledger import Blockchain

# Create blockchain
ledger = Blockchain()

# Add blocks
ledger.add_block({
    "event": "Model Training",
    "accuracy": 0.95,
    "timestamp": 1234567890
})

# Verify integrity
ledger.is_chain_valid()

# Save to file
ledger.save_chain("ledger.json")

# Print chain
ledger.print_chain()
```

---

### 🎓 distill.py - Knowledge Distillation

Compress large ensemble models into smaller models for edge deployment on ESP32 devices.

**Features:**
- Teacher-student model training
- Temperature scaling for soft labels
- Model size comparison
- Multiple student architectures (Decision Tree, Small RF, MLP)

**Usage:**

```bash
python distill.py
```

**Example Code:**

```python
from distill import distill_model_for_edge

# Distill teacher model to a small decision tree
student_model, results = distill_model_for_edge(
    teacher_model=large_rf_model,
    X_train=X_train,
    X_test=X_test,
    y_train=y_train,
    y_test=y_test,
    student_type="decision_tree",
    temperature=2.0
)

print(f"Compression ratio: {results['compression_ratio']:.2f}x")
print(f"Accuracy loss: {results['teacher']['accuracy'] - results['student']['accuracy']:.4f}")
```

---

### 📊 generate_dummy_data.py - Data Generator

Generate synthetic sensor data for testing without running live simulators.

**Usage:**

```bash
# Generate 5000 samples with 10% anomalies from 3 devices
python generate_dummy_data.py 5000 0.1 3
```

**Example Code:**

```python
from generate_dummy_data import generate_dataset, save_to_csv

df = generate_dataset(
    num_samples=10000,
    anomaly_ratio=0.15,
    num_devices=5
)

save_to_csv(df, "data/test_data.csv")
```

---

## 🔄 Typical Workflow

### Scenario 1: Real-time Data Collection and Analysis

```bash
# Terminal 1: Start the server
python esp32_data_server.py

# Terminal 2: Run simulators
python client_sim.py
# Choose option 2 for multiple devices

# Terminal 3: After collecting data, run federated learning
python federated_ml.py sensor_data.jsonl 5 3

# Terminal 4: (Optional) Distill model for edge deployment
python distill.py
```

### Scenario 2: Testing with Dummy Data

```bash
# Generate test data
python generate_dummy_data.py 5000 0.1 3

# Train federated model
python federated_ml.py sensor_data.jsonl 5 3

# Distill for edge deployment
python distill.py
```

---

## 📦 Output Files

After running the system, you'll have:

```
iot/
├── sensor_data.jsonl              # Raw sensor readings
├── server_stats.json              # Server statistics
├── ledger.json                    # Blockchain ledger
├── federated_learning_results.png # Performance visualization
├── models/
│   ├── federated_model.pkl       # Federated learning model
│   ├── student_decision_tree.pkl # Distilled model (small)
│   └── student_small_rf.pkl      # Distilled model (medium)
└── data/
    └── dummy_sensor_data_*.csv   # Generated test data
```

---

## 🔧 Configuration

### Sensor Thresholds

Edit in `model_utils.py`:

```python
thresholds = {
    "Temperature": {"min": 15, "max": 40, "optimal": 28},
    "Humidity": {"min": 30, "max": 85, "optimal": 65},
    "Vibration": {"min": 0, "max": 0.1, "optimal": 0.02},
    "Current": {"min": 0.05, "max": 0.3, "optimal": 0.15}
}
```

### Server Settings

Edit in `esp32_data_server.py`:

```python
DATA_FILE = "sensor_data.jsonl"  # Data storage file
STATS_FILE = "server_stats.json"  # Statistics file
PORT = 5000  # Server port
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" when running client simulator

**Solution:**
- Ensure the server is running: `python esp32_data_server.py`
- Check if port 5000 is available
- Verify firewall settings

### Issue: "No data found in sensor_data.jsonl"

**Solution:**
- Run the client simulator first to generate data
- Or generate dummy data: `python generate_dummy_data.py`

### Issue: Import errors

**Solution:**
```bash
pip install -r requirements.txt
```

---

## 📈 Performance Metrics

Expected performance on typical hardware:

- **Data Collection**: 100-1000 readings/second
- **Model Training**: ~1-5 seconds per round (5000 samples)
- **Federated Learning**: ~5-20 seconds per round (3 clients)
- **Inference**: <1ms per prediction (student model)

---

## 🔐 Security Notes

- This is a demonstration system for learning purposes
- In production, add authentication and encryption
- Use HTTPS for API endpoints
- Secure blockchain with proper consensus mechanisms
- Implement proper access control for all endpoints

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Federated Learning Tutorial](https://flower.dev/)
- [Blockchain Basics](https://bitcoin.org/bitcoin.pdf)

---

## 🤝 Contributing

To add new features:

1. Follow the existing code structure
2. Add comprehensive docstrings
3. Test with both real and dummy data
4. Update this README with usage examples

---

Built with ❤️ for Industry 4.0 and IoT innovation
