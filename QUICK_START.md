# ⚡ Quick Start Guide

Get started with the Industrial IoT Predictive Maintenance System in 5 minutes!

## 🎯 What You Can Do

1. **Frontend Dashboard** - View real-time IoT simulation in your browser
2. **Python Backend** - Run real IoT device simulators and ML training

---

## 🖥️ Option 1: Frontend Only (Easiest - 30 seconds!)

The dashboard works standalone with simulated data in the browser.

### Steps:

1. **Open the dashboard:**
   ```bash
   open index.html
   ```
   Or double-click `index.html` in Finder

2. **Use the dashboard:**
   - Click "Start Simulation" to begin
   - Click "Inject Anomaly" to test alerts
   - Watch real-time charts and metrics

**That's it!** The frontend runs completely in your browser.

---

## 🐍 Option 2: Full Python Backend (Advanced - 5 minutes)

Run real ESP32 simulators and machine learning models.

### Step 1: Install Dependencies

**On macOS** (use `python3` and `pip3`):
```bash
./install_dependencies.sh
```

Or manually:
```bash
pip3 install --user flask flask-cors pandas numpy scikit-learn matplotlib requests
```

### Step 2: Start the Data Server

```bash
cd iot
python3 esp32_data_server.py
```

Keep this terminal open. You should see:
```
🏭 ESP32 IoT Data Server
📡 Server starting on http://0.0.0.0:5000
```

### Step 3: Run Device Simulators

**In a new terminal:**
```bash
cd iot
python3 client_sim.py
```

Choose option 2 for multiple devices, then:
- Duration: `120` (2 minutes)
- Interval: `2` (readings every 2 seconds)

Watch the data being sent to the server!

### Step 4: Train ML Model (After Data Collection)

**In a new terminal:**
```bash
cd iot
python3 federated_ml.py sensor_data.jsonl 5 3
```

This will:
- Train a federated learning model
- Create a blockchain ledger
- Save performance plots

---

## 📝 Common Commands

### Generate Test Data (No Simulator Needed)
```bash
cd iot
python3 generate_dummy_data.py 5000 0.1 3
```

### Check Server Stats
```bash
curl http://localhost:5000/stats
```

### View Latest Readings
```bash
curl http://localhost:5000/data/latest
```

---

## 🐛 Troubleshooting

### "pip: command not found"
Use `pip3` instead of `pip` on macOS:
```bash
pip3 install -r requirements.txt --user
```

### "Address already in use (Port 5000)"
Kill the process:
```bash
lsof -i :5000
kill -9 <PID>
```

### "No data found"
Make sure you:
1. Started the server first
2. Ran the client simulator
3. Or generated dummy data

---

##  🎓 Learn More

- **Full Setup Guide:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Main README:** [README.md](README.md)
- **Backend Docs:** [iot/README.md](iot/README.md)

---

## 🚀 What's Next?

After you're comfortable with the basics:

1. **Customize thresholds** in `scripts/app.js`
2. **Train your own models** with collected data
3. **Deploy models to edge devices** using distillation
4. **Explore the blockchain ledger** in `ledger.json`

---

**Enjoy exploring Industry 4.0! 🏭✨**
