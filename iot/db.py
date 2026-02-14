from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client=MongoClient(os.getenv("MONGO_URI"))
db=client[os.getenv("DB_NAME")]
sensor_collection=db.sensor_readings
stats_collection=db.server_stats



