from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta

load_dotenv()

def connect_db():
    client = MongoClient(os.environ["MONGO_URI"])
    return client.envirolink

def get_historical_data(hours=24):
    db = connect_db()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    cursor = db.readings.find({
        "timestamp": {"$gte": cutoff}
    }).sort("timestamp", 1)
    return list(cursor)