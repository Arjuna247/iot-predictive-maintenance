import random
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db.sensor_readings

print("🔌 Connected to MongoDB")

# Generate 300 anomaly records
records = []

for i in range(300):
    record = {
        "deviceId": "ESP32_01",
        "Temperature": random.uniform(60, 100),   # Abnormally high temp
        "Humidity": random.uniform(0, 20),        # Abnormally low humidity
        "Vibration": random.uniform(3, 8),        # High vibration
        "Current": random.uniform(5, 10),         # High current
        "Anomaly": 1,
        "server_timestamp": datetime.utcnow().isoformat()
    }
    records.append(record)

# Insert all at once
collection.insert_many(records)

print("✅ 300 anomaly records inserted successfully!")
