"""
ESP32 Data Server
Flask server that receives and stores sensor data from IoT devices
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from db import sensor_collection 
import threading
import time
import joblib
import numpy as np

# -----------------------------
# Load Trained ML Model
# -----------------------------
MODEL_PATH = "models/federated_model.pkl"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ ML model loaded successfully")
else:
    model = None
    print("⚠ ML model not found. Anomaly detection disabled.")


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Configuration
DATA_FILE = "sensor_data.jsonl"
STATS_FILE = "server_stats.json"

# In-memory storage
sensor_data_list = []
device_stats = {}


def initialize_storage():
    """Initialize storage files if they don't exist"""
    if not os.path.exists(DATA_FILE):
        open(DATA_FILE, "w").close()
        print(f"✓ Created {DATA_FILE}")

    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({"total_readings": 0, "devices": {}}, f)
        print(f"✓ Created {STATS_FILE}")


def update_stats(device_id):
    """Update statistics for device"""
    if device_id not in device_stats:
        device_stats[device_id] = {
            "count": 0,
            "first_seen": datetime.now().isoformat(),
            "last_seen": None
        }

    device_stats[device_id]["count"] += 1
    device_stats[device_id]["last_seen"] = datetime.now().isoformat()


def save_stats_periodically():
    """Background task to save stats every 30 seconds"""
    while True:
        time.sleep(30)
        try:
            with open(STATS_FILE, "w") as f:
                json.dump({
                    "total_readings": len(sensor_data_list),
                    "devices": device_stats,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")


@app.route("/", methods=["GET"])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "service": "ESP32 Data Server",
        "version": "1.0.0",
        "endpoints": {
            "/sensor-data": "POST - Receive sensor data",
            "/stats": "GET - Get server statistics",
            "/data": "GET - Get all sensor data",
            "/data/latest": "GET - Get latest readings",
            "/data/device/<device_id>": "GET - Get data for specific device"
        }
    }), 200


@app.route("/sensor-data", methods=["POST"])
def receive_data():
    try:
        data = request.get_json()
        print("Received data:", data)
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Required fields from ESP32
        required_fields = [
            "device_id",
            "temperature",
            "humidity",
            "ax",
            "ay",
            "az",
            "current_voltage"
        ]

        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing fields: {', '.join(missing)}"
            }), 400
        if data["temperature"] is None or data["humidity"] is None:
            return jsonify({
                "status": "error",
                "message": "Missing fields"
            }), 400

        # ---- Normalize for ML ----
        normalized = {
            "deviceId": data["device_id"],
            "Temperature": float(data["temperature"]),
            "Humidity": float(data["humidity"]),
            "Vibration": (data["ax"]**2 + data["ay"]**2 + data["az"]**2) ** 0.5,
            "Current": float(data["current_voltage"]),
            #"Anomaly": 0,  # default (ML will update later)
            "server_timestamp": datetime.now().isoformat()
        }
        if model is not None:
            try:
                features = np.array([[
                    normalized["Temperature"],
                    normalized["Humidity"],
                    normalized["Vibration"],
                    normalized["Current"]
                ]])

                prediction = model.predict(features)
                normalized["Anomaly"] = int(prediction[0])

                if normalized["Anomaly"] == 1:
                    print("🚨 ANOMALY DETECTED 🚨")
                else:
                    print("✅ Normal Reading")

            except Exception as e:
                print("Prediction error:", e)
                normalized["Anomaly"] = 0
        else:
            normalized["Anomaly"] = 0
        
        # Save to MongoDB
        try:
            sensor_collection.insert_one(dict(normalized))
        except Exception as e:
            print(f"MongoDB error: {e}")

        # Save in memory
        sensor_data_list.append(normalized)

        # Save to file (JSONL)
        with open(DATA_FILE, "a") as f:
            f.write(json.dumps(normalized) + "\n")

        # Update stats
        update_stats(normalized["deviceId"])

        return jsonify({
            "status": "ok",
            "device_id": normalized["deviceId"]
        }), 200

    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route("/stats", methods=["GET"])
def get_stats():
    """Get server statistics"""
    return jsonify({
        "total_readings": len(sensor_data_list),
        "devices": device_stats,
        "data_file": DATA_FILE,
        "file_size_kb": os.path.getsize(DATA_FILE) / 1024 if os.path.exists(DATA_FILE) else 0
    }), 200


@app.route("/data", methods=["GET"])
def get_all_data():
    """Get all sensor data"""
    limit = request.args.get("limit", type=int, default=100)
    return jsonify({
        "count": len(sensor_data_list),
        "data": sensor_data_list[-limit:]  # Return last N readings
    }), 200


@app.route("/data/latest", methods=["GET"])
def get_latest():
    """Get latest readings for each device"""
    latest_by_device = {}

    # Get latest reading for each device
    for data in reversed(sensor_data_list):
        device_id = data.get("deviceId", "unknown")
        if device_id not in latest_by_device:
            latest_by_device[device_id] = data

    return jsonify({
        "count": len(latest_by_device),
        "data": latest_by_device
    }), 200


@app.route("/data/device/<device_id>", methods=["GET"])
def get_device_data(device_id):
    """Get data for a specific device"""
    device_data = [d for d in sensor_data_list if d.get("deviceId") == device_id]
    limit = request.args.get("limit", type=int, default=100)

    return jsonify({
        "device_id": device_id,
        "count": len(device_data),
        "data": device_data[-limit:]
    }), 200


@app.route("/data/anomalies", methods=["GET"])
def get_anomalies():
    """Get all anomaly readings"""
    anomalies = [d for d in sensor_data_list if d.get("Anomaly", 0) == 1]

    return jsonify({
        "count": len(anomalies),
        "data": anomalies
    }), 200


@app.route("/clear", methods=["POST"])
def clear_data():
    """Clear all data (for testing purposes)"""
    global sensor_data_list, device_stats

    sensor_data_list = []
    device_stats = {}

    # Clear file
    with open(DATA_FILE, "w") as f:
        f.write("")

    return jsonify({
        "status": "ok",
        "message": "All data cleared"
    }), 200


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏭 ESP32 IoT Data Server")
    print("="*60)

    # Initialize storage
    initialize_storage()

    # Start background stats saver
    stats_thread = threading.Thread(target=save_stats_periodically, daemon=True)
    stats_thread.start()
    print("✓ Background stats saver started")

    print(f"\n📡 Server starting on http://0.0.0.0:5000")
    print(f"📊 Data file: {DATA_FILE}")
    print(f"📈 Stats file: {STATS_FILE}")
    print("\nEndpoints:")
    print("  POST /sensor-data     - Receive sensor data")
    print("  GET  /stats           - View statistics")
    print("  GET  /data            - Get all data")
    print("  GET  /data/latest     - Get latest readings")
    print("  GET  /data/anomalies  - Get anomaly readings")
    print("\n" + "="*60 + "\n")

    # Run Flask server
    app.run(host="0.0.0.0", port=5000, debug=False)
