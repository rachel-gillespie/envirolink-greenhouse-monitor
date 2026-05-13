import paho.mqtt.client as mqtt
from sense_hat import SenseHat
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

sense = SenseHat()

def get_readings():
    raw_temp = sense.get_temperature()
    cpu_temp = float(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000
    corrected_temp = raw_temp - ((cpu_temp - raw_temp) / 1.5)
    
    return {
        "temperature": round(corrected_temp, 2),
        "humidity": round(sense.get_humidity(), 2),
        "pressure": round(sense.get_pressure(), 2)
    }

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Connected to HiveMQ")
    else:
        print(f"❌ Connection failed: {reason_code}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
client.tls_set()
client.on_connect = on_connect

client.connect(os.environ["MQTT_BROKER"], int(os.environ["MQTT_PORT"]))
client.loop_start()

print("📡 Sensor running — publishing every 30 seconds. Ctrl+C to stop.")

try:
    while True:
        readings = get_readings()
        payload = json.dumps(readings)
        client.publish("envirolink/sensors", payload)
        print(f"Published: {payload}")
        time.sleep(30)
except KeyboardInterrupt:
    print("Stopped.")
    client.loop_stop()
    client.disconnect()