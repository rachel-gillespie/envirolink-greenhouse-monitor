import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from db import connect_db

db = connect_db()
config_collection = db.config

existing = config_collection.find_one({})
if not existing:
    config_collection.insert_one({
    "temp_min": 10,
    "temp_max": 30,
    "humidity_min": 40,
    "humidity_max": 80,
    "ventilation_temp": 24
    })
    print("Config created")
else:
    print("Config already exists")