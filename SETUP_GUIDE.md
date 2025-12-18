# 🚀 Complete Setup & Usage Guide

## Industrial IoT Predictive Maintenance System

This guide will help you set up and run the complete Industrial IoT Predictive Maintenance System with both frontend and backend components.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Running the Frontend Dashboard](#running-the-frontend-dashboard)
4. [Running the Python Backend](#running-the-python-backend)
5. [Complete System Workflow](#complete-system-workflow)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### For Frontend (Dashboard):
- Web browser (Chrome, Firefox, Safari, Edge)
- VS Code (recommended) with Live Server extension

### For Backend (Python ML Services):
- Python 3.8 or higher
- pip (Python package manager)

---

## 📦 Installation

### Step 1: Clone or Download the Project

```bash
cd "/Users/arjuna247/IoT v2/iot-predictive-maintenance"
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask & Flask-CORS (Web server)
- Pandas & NumPy (Data processing)
- Scikit-learn (Machine learning)
- Matplotlib (Visualization)
- Requests (HTTP client)

### Step 3: Verify Installation

```bash
python --version  # Should show Python 3.8+
pip list | grep Flask  # Should show Flask installed
```

---

## 🎨 Running the Frontend Dashboard

The frontend is a pure HTML/CSS/JavaScript dashboard that runs in your browser.

### Option 1: Using VS Code Live Server (Recommended)

1. Open the project in VS Code:
   ```bash
   code .
   ```

2. Install the "Live Server" extension if not already installed:
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows)
   - Search for "Live Server"
   - Click Install

3. Open `index.html` in VS Code

4. Right-click on `index.html` and select "Open with Live Server"

5. Your browser will open at `http://127.0.0.1:5500` with the dashboard

### Option 2: Direct Browser Open

1. Navigate to the project directory
2. Double-click `index.html`
3. The dashboard will open in your default browser

**Note:** The frontend dashboard runs independently with simulated data in the browser. The Python backend is for real IoT device simulation and ML training.

---

## 🐍 Running the Python Backend

The backend consists of multiple components that work together.

### Component 1: Data Server

The server receives and stores sensor data from IoT devices.

```bash
cd iot
python esp32_data_server.py
```

**Expected Output:**
```
============================================================
🏭 ESP32 IoT Data Server
============================================================
✓ Created sensor_data.jsonl
✓ Created server_stats.json
✓ Background stats saver started

📡 Server starting on http://0.0.0.0:5000
============================================================
```

**Keep this terminal running.**

---

### Component 2: ESP32 Device Simulators

In a **new terminal**, run the IoT device simulator:

```bash
cd iot
python client_sim.py
```

**Interactive Menu:**
```
============================================================
🔌 ESP32 IoT Device Simulator
============================================================

Options:
1. Single device simulation
2. Multiple devices (3 devices)
3. Exit

Select option (1-3):
```

**Example Single Device:**
- Choose option 1
- Device ID: `ESP32_01` (or press Enter for default)
- Duration: `120` (2 minutes)
- Interval: `2` (2 seconds between readings)
- Anomaly after: `60` (inject anomaly after 60 seconds)

**Example Multiple Devices:**
- Choose option 2
- Duration: `120`
- Interval: `2`

**Expected Output:**
```
🚀 Starting ESP32_01 simulator...
   Duration: 120s | Interval: 2s | Server: http://localhost:5000

✓ [ESP32_01] Data sent: Temp=28.3°C, Vib=0.021g
✓ [ESP32_01] Data sent: Temp=29.1°C, Vib=0.018g
...
⚠️  [ESP32_01] ANOMALY INJECTED

✓ [ESP32_01] Data sent: Temp=42.5°C, Vib=0.234g  ← Anomalous
```

**Keep this running until you have enough data (at least 100+ readings).**

---

### Component 3: Federated Learning

Once you have collected sensor data, train a federated learning model.

In a **new terminal** (or wait for simulators to finish):

```bash
cd iot
python federated_ml.py sensor_data.jsonl 5 3
```

**Arguments:**
- `sensor_data.jsonl` - Input data file
- `5` - Number of training rounds
- `3` - Number of clients/nodes

**Expected Output:**
```
============================================================
🌐 Federated Learning for IoT Predictive Maintenance
============================================================
✓ Blockchain initialized
✓ Loaded 250 sensor readings
✓ Data split among 3 clients

============================================================
🔄 Federated Learning Round 1
============================================================

📱 Training Client 1...
   ✓ Accuracy: 0.9200, F1: 0.9150

📱 Training Client 2...
   ✓ Accuracy: 0.9100, F1: 0.9050

📱 Training Client 3...
   ✓ Accuracy: 0.8900, F1: 0.8850

🌍 Global Model Performance:
   Accuracy: 0.9067
   F1 Score: 0.9017
   ⛓️  Block #2 added to blockchain
...
✅ Blockchain saved to ledger.json
✅ Model saved to models/federated_model.pkl
```

**Output Files:**
- `ledger.json` - Blockchain ledger with training history
- `models/federated_model.pkl` - Trained ML model
- `federated_learning_results.png` - Performance visualization

---

### Component 4: Model Distillation (Optional)

Compress the model for edge deployment on resource-constrained devices.

```bash
cd iot
python distill.py
```

**Expected Output:**
```
============================================================
🧠 Knowledge Distillation for Edge Deployment
============================================================

👨‍🏫 Training Teacher Model (Large Random Forest)...
   ✓ Teacher model trained

============================================================
Distilling to: decision_tree
============================================================

🎓 Starting Knowledge Distillation...
   Teacher: RandomForestClassifier
   Student: DecisionTreeClassifier
   Temperature: 2.0
   ✓ Distillation complete!

📊 Model Comparison:
============================================================

👨‍🏫 Teacher Model:
   Accuracy:  0.9200
   F1 Score:  0.9150

🎓 Student Model:
   Accuracy:  0.8850
   F1 Score:  0.8800

📦 Model Size Comparison:
   Teacher size: ~245.32 KB
   Student size: ~12.45 KB
   Compression ratio: 19.70x

✅ Student model saved to: models/student_decision_tree.pkl
```

---

## 🔄 Complete System Workflow

### Scenario A: Full Real-Time System

```bash
# Terminal 1: Start the data server
cd iot && python esp32_data_server.py

# Terminal 2: Run device simulators
cd iot && python client_sim.py
# → Choose option 2 for multiple devices
# → Duration: 300 (5 minutes)
# → Interval: 2

# Wait for data collection to complete...

# Terminal 3: Train federated model
cd iot && python federated_ml.py sensor_data.jsonl 5 3

# Terminal 4: Distill model for edge deployment
cd iot && python distill.py

# Open the frontend dashboard in browser
# → Open index.html with Live Server or directly in browser
```

### Scenario B: Quick Testing with Dummy Data

```bash
# Generate test data
cd iot
python generate_dummy_data.py 5000 0.1 3

# Train federated model
python federated_ml.py sensor_data.jsonl 5 3

# Distill model
python distill.py

# Open dashboard
# → Open index.html in browser
```

---

## 🌐 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FRONTEND DASHBOARD                      │
│            (index.html + CSS + JavaScript)               │
│                                                          │
│  📊 Real-time Charts  🤖 Anomaly Detection              │
│  🔗 Federated Learning  ⛓️ Blockchain Visualization     │
│  🔮 Digital Twin  📱 Responsive Design                  │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                  PYTHON BACKEND (iot/)                   │
├─────────────────────────────────────────────────────────┤
│  📡 esp32_data_server.py  ← Flask REST API              │
│  🔌 client_sim.py         ← ESP32 Simulator             │
│  🧠 model_utils.py        ← ML Utilities                │
│  🔗 federated_ml.py       ← Federated Learning          │
│  ⛓️ ledger.py             ← Blockchain Ledger           │
│  🎓 distill.py            ← Model Compression           │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    DATA & MODELS                         │
├─────────────────────────────────────────────────────────┤
│  📄 sensor_data.jsonl    ← Raw sensor readings          │
│  ⛓️ ledger.json          ← Blockchain ledger            │
│  🧠 models/*.pkl         ← Trained ML models            │
│  📊 *.png                ← Visualization plots          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features Demonstration

### 1. Anomaly Detection
- Open the dashboard
- Click "Start Simulation"
- Click "Inject Anomaly"
- Watch the alerts and charts respond in real-time

### 2. Federated Learning
- Run multiple ESP32 simulators
- Execute federated learning script
- View the blockchain ledger and performance plots

### 3. Digital Twin
- Monitor health scores in the dashboard
- See degradation prediction
- View maintenance scheduling

### 4. Blockchain Security
- View immutable transaction logs in the dashboard
- Check `ledger.json` for cryptographic hashes
- Verify blockchain integrity

---

## 🐛 Troubleshooting

### Issue: "Address already in use" (Port 5000)

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
# Edit esp32_data_server.py, change: app.run(host="0.0.0.0", port=5001)
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall requirements
pip install -r requirements.txt

# Or install individually
pip install flask flask-cors pandas numpy scikit-learn matplotlib requests
```

### Issue: "No data found in sensor_data.jsonl"

**Solution:**
1. Make sure the data server is running first
2. Run the client simulator to generate data
3. Or generate dummy data: `python generate_dummy_data.py`

### Issue: Frontend not connecting to backend

**Note:** The frontend dashboard runs independently with its own simulation. It doesn't need the Python backend to function. The Python backend is for:
- Real IoT device simulation
- Machine learning training
- Federated learning
- Model deployment

---

## 📊 Sample Data Format

**sensor_data.jsonl format:**
```json
{"deviceId": "ESP32_01", "timestamp": 1699564800000, "Temperature": 28.5, "Humidity": 65.2, "Vibration": 0.021, "Current": 0.15, "Anomaly": 0}
{"deviceId": "ESP32_01", "timestamp": 1699564802000, "Temperature": 42.3, "Humidity": 68.1, "Vibration": 0.234, "Current": 0.32, "Anomaly": 1}
```

---

## 📈 Expected Performance

On a typical development machine:

- **Frontend Dashboard**: Instant load, 60 FPS animations
- **Data Collection**: 100-1000 readings/second
- **Model Training**: 1-5 seconds per round (5000 samples)
- **Federated Learning**: 5-20 seconds per round (3 clients)
- **Model Inference**: <1ms per prediction

---

## 🎓 Learning Path

1. **Start Simple**: Open the frontend dashboard and explore the UI
2. **Add Data**: Run the ESP32 simulator to generate real data
3. **Train Models**: Execute federated learning
4. **Optimize**: Use distillation for edge deployment
5. **Experiment**: Modify thresholds, add features, customize visualizations

---

## 📚 Additional Documentation

- Frontend details: See [README.md](README.md)
- Backend details: See [iot/README.md](iot/README.md)
- Python APIs: Check docstrings in each `.py` file

---

## 🤝 Support

For issues or questions:
1. Check this guide thoroughly
2. Review the troubleshooting section
3. Check the browser console for frontend errors
4. Check terminal output for backend errors

---

## 🎉 You're All Set!

The system is now ready to demonstrate:
- ✅ Real-time IoT data collection
- ✅ Edge AI anomaly detection
- ✅ Federated learning across devices
- ✅ Blockchain security and transparency
- ✅ Digital twin technology
- ✅ Predictive maintenance scheduling

**Enjoy exploring the future of Industry 4.0! 🏭🚀**
