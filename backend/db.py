# db.py
# Handles MongoDB connection and data retrieval for EnviroLink sensor readings.

from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta

load_dotenv()  # Load environment variables from .env file

def connect_db():
    """Connect to MongoDB and return the envirolink database."""
    client = MongoClient(os.environ["MONGO_URI"])  # os.environ returns a dictionary having the user's environmental variable as key and their values as value
    return client.envirolink

def get_historical_data(hours=24):
    """
    Retrieve sensor readings from the past `hours` hours, sorted oldest-first.
    Defaults to the last 24 hours if no argument is provided.
    """
    db = connect_db()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)  # stored timestamps are timezone-aware
    cursor = db.readings.find({
        "timestamp": {"$gte": cutoff}  # $gte = greater than or equal to — cutoff must be timezone-aware to match stored timestamps; mixing aware and naive datetimes causes a TypeError
    }).sort("timestamp", 1)  # 1 = ascending (oldest first)
    return list(cursor)