import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from db import connect_db
import os
import json
from datetime import datetime, timezone
import time
from weather import get_current_weather

load_dotenv()
db = connect_db()
readings_collection = db.readings
weather_collection = db.weather

def check_thresholds(readings):
    alerts = []
    if readings["humidity"] > 70:
        alerts.append({"type": "danger", "msg": "High Humidity Detected!"})
        print(f"⚠️ Humidity too high: {readings['humidity']}%")
    if readings["temperature"] > 28:
        alerts.append({"type": "danger", "msg": "Room is getting too warm."})
        print(f"⚠️ Temperature too high: {readings['temperature']}°C")
    return alerts

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Connected to HiveMQ")
        client.subscribe("envirolink/sensors")
        print("📡 Subscribed to envirolink/sensors")
    else:
        print(f"❌ Connection failed: {reason_code}")

def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode())
    alerts = check_thresholds(payload)
    payload["timestamp"] = datetime.now(timezone.utc)
    readings_collection.insert_one(payload)
    print(f"💾 Saved: {payload}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message

client.connect(os.environ["MQTT_BROKER"], int(os.environ["MQTT_PORT"]))
client.loop_start()

print("🔄 Backend running — waiting for messages. Ctrl+C to stop.")

try:
    while True:
        weather = get_current_weather()
        weather["timestamp"] = datetime.now(timezone.utc)
        weather_collection.insert_one(weather)
        print(f"💾 Saved: {weather}")
        time.sleep(10800) # 3 hours
except KeyboardInterrupt:
    print("Stopped.")
    client.loop_stop()
    client.disconnect()