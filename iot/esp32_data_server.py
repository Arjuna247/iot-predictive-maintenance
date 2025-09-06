from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
sensor_data_list = []  # still keep in memory
DATA_FILE = "sensor_data.jsonl"  # file to save readings

@app.route("/sensor-data", methods=["POST"])
def receive_data():
    data = request.get_json()
    
    # append to memory
    sensor_data_list.append(data)
    
    # append to file (one JSON per line)
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
    
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # optional: create empty file if doesn't exist
    if not os.path.exists(DATA_FILE):
        open(DATA_FILE, "w").close()
    
    app.run(host="0.0.0.0", port=5000)
