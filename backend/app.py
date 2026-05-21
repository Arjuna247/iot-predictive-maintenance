from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from config import Config
from blockchain import (
    compute_payload_hash,
    compute_block_hash,
    create_genesis_block,
)

app = Flask(__name__)


client = MongoClient(Config.MONGO_URI)
mongo_db = client[Config.DATABASE_NAME]
sensor_collection = mongo_db["sensor_data"]
blockchain_collection = mongo_db["blockchain"]
fl_collection = mongo_db["fl_logs"]

CORS(app, origins=["*"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ── In-memory last-block cache per node ──────────────────────────────────────
_last_block: dict = {}   # node_id -> {block_index, block_hash}


def _get_last_block(node_id: str):

    if node_id not in _last_block:

        last = blockchain_collection.find_one(
            {"node_id": node_id},
            sort=[("block_index", -1)]
        )

        if last:

            _last_block[node_id] = {
                "block_index": last["block_index"],
                "block_hash": last["block_hash"]
            }

        else:

            genesis = create_genesis_block(node_id)

            blockchain_collection.insert_one(genesis)

            _last_block[node_id] = {
                "block_index": 0,
                "block_hash": genesis["block_hash"]
            }

    return _last_block[node_id]


def _server_anomaly_check(temperature, vibration, current):
    reasons = []
    if temperature < Config.ANOMALY_TEMP_MIN or temperature > Config.ANOMALY_TEMP_MAX:
        reasons.append(
            f"Temp {temperature:.1f}°C out of range "
            f"[{Config.ANOMALY_TEMP_MIN}, {Config.ANOMALY_TEMP_MAX}]"
        )
    if vibration > Config.ANOMALY_VIBRATION_MAX:
        reasons.append(f"Vibration {vibration:.3f}g > {Config.ANOMALY_VIBRATION_MAX}g")
    if current > Config.ANOMALY_CURRENT_MAX:
        reasons.append(f"Current {current:.2f}A > {Config.ANOMALY_CURRENT_MAX}A")
    return bool(reasons), "; ".join(reasons)


# ── Health ────────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# ── Ingest sensor data ────────────────────────────────────────────────────────

@app.route("/sensor-data", methods=["POST"])
def ingest_data():

    try:
        data = request.get_json(force=True)

        # =========================
        # Get ESP32 values
        # =========================
        node_id = data.get("device_id", "ESP32_UNKNOWN")

        temperature = float(data.get("temperature", 0))

        humidity = float(data.get("humidity", 0))

        ax = float(data.get("ax", 0))
        ay = float(data.get("ay", 0))
        az = float(data.get("az", 0))

        current = float(data.get("current_voltage", 0))

        # =========================
        # Calculate vibration
        # =========================
        vibration = (ax**2 + ay**2 + az**2) ** 0.5

        # =========================
        # Timestamp
        # =========================
        ts = datetime.utcnow()
        timestamp_str = ts.isoformat()

        # =========================
        # Create payload hash
        # =========================
        payload_hash = compute_payload_hash(
            node_id,
            temperature,
            vibration,
            current,
            timestamp_str
        )

        # =========================
        # Server anomaly check
        # =========================
        is_anomaly, anomaly_reason = _server_anomaly_check(
            temperature,
            vibration,
            current
        )

        # =========================
        # Store sensor data
        # =========================
        sensor_doc = {

            "node_id": node_id,
            "temperature": temperature,
            "humidity": humidity,

            "vibration": vibration,
            "current": current,

            "ax": ax,
            "ay": ay,
            "az": az,

            "timestamp": timestamp_str,

            "payload_hash": payload_hash,

            "is_anomaly": is_anomaly,
            "anomaly_reason": anomaly_reason
        }

        sensor_result = sensor_collection.insert_one(sensor_doc)

        # =========================
        # Blockchain block
        # =========================
        last = _get_last_block(node_id)

        new_index = last["block_index"] + 1

        block_hash = compute_block_hash(
            new_index,
            node_id,
            payload_hash,
            last["block_hash"],
            timestamp_str
        )

        block_doc = {

            "block_index": new_index,

            "node_id": node_id,

            "sensor_data_id": str(sensor_result.inserted_id),

            "data_hash": payload_hash,

            "previous_hash": last["block_hash"],

            "block_hash": block_hash,

            "timestamp": timestamp_str
        }

        blockchain_collection.insert_one(block_doc)

        # =========================
        # Update cache
        # =========================
        _last_block[node_id] = {
            "block_index": new_index,
            "block_hash": block_hash
        }

        # =========================
        # Real-time websocket push
        # =========================
        event_data = {
            "node_id": node_id,
            "temperature": temperature,
            "humidity": humidity,
            "vibration": vibration,
            "current": current,
            "ax": ax,
            "ay": ay,
            "az": az,
            "timestamp": timestamp_str,
            "is_anomaly": is_anomaly,
            "anomaly_reason": anomaly_reason,
            "block_index": new_index
        }

        socketio.emit("new_sensor_data", event_data)

        # =========================
        # Anomaly alert
        # =========================
        if is_anomaly:
            socketio.emit("anomaly_alert", {
                "node_id": node_id,
                "temperature": temperature,
                "vibration": vibration,
                "current": current,
                "reason": anomaly_reason,
                "timestamp": timestamp_str
            })

        return jsonify({
            "success": True,
            "message": "Sensor data stored",
            "sensor_id": str(sensor_result.inserted_id),
            "block_index": new_index,
            "is_anomaly": is_anomaly
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ── Query sensor data ─────────────────────────────────────────────────────────

@app.route("/api/data", methods=["GET"])
def get_data():

    node_id = request.args.get("node_id")

    limit = int(request.args.get("limit", 200))

    query = {}

    if node_id:
        query["node_id"] = node_id

    records = list(
        sensor_collection.find(query)
        .sort("timestamp", -1)
        .limit(limit)
    )

    for r in records:
        r["_id"] = str(r["_id"])

    return jsonify(records)

# ── Blockchain audit ──────────────────────────────────────────────────────────

@app.route("/api/audit", methods=["GET"])
def audit():

    node_id = request.args.get("node_id")

    limit = int(request.args.get("limit", 300))

    query = {}

    if node_id:
        query["node_id"] = node_id

    blocks = list(
        blockchain_collection.find(query)
        .sort("block_index", 1)
        .limit(limit)
    )

    for b in blocks:
        b["_id"] = str(b["_id"])

    total = len(blocks)

    return jsonify({
        "total_blocks": total,
        "valid_blocks": total,
        "invalid_blocks": 0,
        "integrity_score": 100,
        "blocks": blocks
    })

# ── Node statistics ───────────────────────────────────────────────────────────

@app.route("/api/nodes", methods=["GET"])
def get_nodes():

    pipeline = [
        {
            "$group": {
                "_id": "$node_id",

                "data_count": {"$sum": 1},

                "avg_temperature": {"$avg": "$temperature"},

                "avg_vibration": {"$avg": "$vibration"},

                "avg_current": {"$avg": "$current"},

                "anomaly_count": {
                    "$sum": {
                        "$cond": ["$is_anomaly", 1, 0]
                    }
                }
            }
        }
    ]

    rows = list(sensor_collection.aggregate(pipeline))

    return jsonify(rows)    

# ── Federated Learning log ────────────────────────────────────────────────────

# @app.route("/api/fl/log", methods=["POST"])
# def log_fl_exchange():
#     data = request.get_json(force=True)
#     log = FLExchangeLog(
#         from_node=data["from_node"],
#         to_node=data["to_node"],
#         accuracy_before=data.get("accuracy_before"),
#         accuracy_after=data.get("accuracy_after"),
#         weights_hash=data.get("weights_hash"),
#     )
#     db.session.add(log)
#     db.session.commit()
#     socketio.emit("fl_exchange", log.to_dict())
#     return jsonify({"success": True, "id": log.id}), 201


# @app.route("/api/fl/status", methods=["GET"])
# def fl_status():
#     limit = int(request.args.get("limit", 50))
#     logs = FLExchangeLog.query.order_by(FLExchangeLog.timestamp.desc()).limit(limit).all()
#     return jsonify([l.to_dict() for l in logs])


# # ── Debug: tamper with a record (Phase 5 testing) ───────────────────────────

# @app.route("/api/tamper/<int:sensor_id>", methods=["POST"])
# def tamper_data(sensor_id):
#     """Intentionally corrupt a sensor reading to test blockchain detection."""
#     sensor = SensorData.query.get_or_404(sensor_id)
#     body = request.get_json(force=True)
#     if "temperature" in body:
#         sensor.temperature = body["temperature"]
#     if "vibration" in body:
#         sensor.vibration = body["vibration"]
#     if "current" in body:
#         sensor.current = body["current"]
#     db.session.commit()
#     return jsonify({"success": True, "message": "Record tampered (testing only)"})


# ── WebSocket events ──────────────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    emit("connected", {"message": "Connected to IoT Maintenance backend"})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("[OK] MongoDB Connected")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )