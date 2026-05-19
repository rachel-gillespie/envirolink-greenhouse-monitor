from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from db import connect_db, get_historical_data
import pytz
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import json
from datetime import datetime, timezone
import time
from weather import get_current_weather, get_forecast
import threading

load_dotenv()

ireland = pytz.timezone('Europe/Dublin')
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
socketio = SocketIO(app)
db = connect_db()
readings_collection = db.readings
weather_collection = db.weather
forecast_collection = db.forecast
alerts_collection = db.alerts

def fetch_weather_loop():
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
        time.sleep(10800)
            
weather_thread = threading.Thread(target=fetch_weather_loop, daemon=True)
weather_thread.start()

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
    readings_collection.insert_one(payload)
    irish_time = payload['timestamp'].replace(tzinfo=timezone.utc).astimezone(ireland)
    socketio.emit('new_reading', {
        'temperature': payload['temperature'],
        'humidity': payload['humidity'],
        'pressure': payload['pressure'],
        'timestamp': irish_time.strftime('%H:%M:%S')
    })
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

@app.route('/')
def dashboard():
    sensor_data = db.readings.find_one({}, sort=[("timestamp", -1)])
    sensor_data['timestamp'] = sensor_data['timestamp'].replace(tzinfo=pytz.utc).astimezone(ireland)
    weather_data = db.weather.find_one({}, sort=[("timestamp", -1)])
    alerts_data = db.alerts.find({}, sort=[("timestamp", -1)]).limit(5)
    return render_template('index.html', 
                           title="Dashboard", 
                           sensor_data=sensor_data, 
                           weather_data=weather_data,
                           alerts_data=alerts_data)

@app.route('/api/readings')
def return_readings():
    history = get_historical_data()
    for reading in history:
        reading['_id'] = str(reading['_id'])
    return jsonify(history)

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', port=5000, debug=True)