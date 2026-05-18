import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from db import connect_db
import os
import json
from datetime import datetime, timezone
import time
from weather import get_current_weather, get_forecast

load_dotenv()
db = connect_db()
readings_collection = db.readings
weather_collection = db.weather
forecast_collection = db.forecast
alerts_collection = db.alerts

def check_thresholds(readings):
    alerts = []
    if readings["humidity"] > 70:
        alerts.append({"type": "danger", "msg": "High Humidity Detected!"})
        print(f"⚠️ Humidity too high: {readings['humidity']}%")
    if readings["temperature"] > 28:
        alerts.append({"type": "danger", "msg": "Room is getting too warm."})
        print(f"⚠️ Temperature too high: {readings['temperature']}°C")
    return alerts

def rules_engine(payload, latest_weather, latest_forecast):
    alerts = []
    # Rule 1: Frost Prevention Alert
    if latest_weather["temperature"] <= 0 or payload["temperature"] < 10:
        alerts.append({"type": "danger", "msg": "🚨 Frost risk detected — activate heating!"})
        print(f"🚨 CRITICAL: Frost Risk Detected! Outdoor temperature is at freezing or indoor temperature has dropped below 10°C.")
    # Rule 2: Heat Stress Mitigation
    if payload["temperature"] > 30:
        alerts.append({"type": "danger", "msg": "Heat Stress Risk - Activate cooling fans and open vents to lower the temperature!"})
        print(f"⚠️ WARNING: Heat Stress Risk! Greenhouse temperature has exceeded 30°C.")
    # Rule 3: High Humidity & Disease Prevention
    if payload["humidity"] > 80:
        alerts.append({"type": "danger", "msg": "High Humidity Level - Initiate air circulation/de humidification!"})
        print(f"🌧️ NOTICE: High Humidity Level! Internal humidity is above 80%, increasing mold and disease risk.")
    # Rule 4: Low Humidity & Dehydration Warning
    if payload["humidity"] < 40:
        alerts.append({"type": "danger", "msg": "Low Humidity Level - Activate misting system!"})
        print(f"🍂 WARNING: Low Humidity Level! Internal humidity has dropped below 40%. Plants are at risk of drying out.")
    # Rule 5: Smart Ventilation & Irrigation Efficiency
    if latest_weather["temperature"] > payload["temperature"] and payload["temperature"] < 18 or any("rain" in slot["description"] for slot in latest_forecast["forecast"]):
        alerts.append({"type": "system optimisation", "msg": "Outdoor/Indoor temperature balance is optimal for natural ventilation - Open vents!, Heavy rain detected outdoors - Conserve water by pausing watering!"})
        print(f"🔄 SYSTEM OPTIMIZATION: Outdoor/Indoor temperature balance is optimal for natural ventilation. Heavy rain detected outdoors.")
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
    payload["timestamp"] = datetime.now(timezone.utc)
    alerts = check_thresholds(payload)
    readings_collection.insert_one(payload)
    latest_weather = weather_collection.find_one({}, sort=[("timestamp", -1)])
    latest_forecast = forecast_collection.find_one({}, sort=[("timestamp", -1)])
    if latest_weather and latest_forecast:
        rules = rules_engine(payload, latest_weather, latest_forecast)
        for alert in rules:
            alert["timestamp"] = datetime.now(timezone.utc)
            alerts_collection.insert_one(alert)
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
        forecast = get_forecast()
        weather["timestamp"] = datetime.now(timezone.utc)
        forecast_doc = {
            "timestamp": datetime.now(timezone.utc),
            "forecast": forecast
        }
        forecast_collection.insert_one(forecast_doc)
        weather_collection.insert_one(weather)
        print(f"💾 Saved weather and forecast data")
        time.sleep(10800) # 3 hours
except KeyboardInterrupt:
    print("Stopped.")
    client.loop_stop()
    client.disconnect()