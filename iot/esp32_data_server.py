"""
ESP32 Data Server
Flask server that receives and stores sensor data from IoT devices
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
import time

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
    """Receive sensor data from IoT devices"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Validate required fields
        required_fields = ["deviceId", "Temperature", "Humidity", "Vibration", "Current"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Add server timestamp
        data["server_timestamp"] = datetime.now().isoformat()

        # Store in memory
        sensor_data_list.append(data)

        # Append to file (one JSON per line)
        with open(DATA_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")

        # Update statistics
        update_stats(data.get("deviceId", "unknown"))

        return jsonify({
            "status": "ok",
            "message": "Data received successfully",
            "device_id": data.get("deviceId"),
            "timestamp": data.get("timestamp")
        }), 200

    except Exception as e:
        print(f"Error receiving data: {e}")
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
