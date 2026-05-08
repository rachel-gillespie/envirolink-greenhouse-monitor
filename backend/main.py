import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from db import connect_db
import os
import json
from datetime import datetime, timezone

load_dotenv()

db = connect_db()
readings_collection = db["readings"]

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Connected to HiveMQ")
        client.subscribe("envirolink/sensors")
        print("📡 Subscribed to envirolink/sensors")
    else:
        print(f"❌ Connection failed: {reason_code}")

def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode())
    payload["timestamp"] = datetime.now(timezone.utc)
    readings_collection.insert_one(payload)
    print(f"💾 Saved: {payload}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message

client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")))

print("🔄 Backend running — waiting for messages. Ctrl+C to stop.")
client.loop_forever()