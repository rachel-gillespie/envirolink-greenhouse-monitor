import paho.mqtt.client as mqtt
from sense_hat import SenseHat
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

sense = SenseHat()
time.sleep(10)

green = (0, 255, 0)
red = (255,0,0)
yellow = (255, 255, 0)

def get_readings():
    raw_temp = sense.get_temperature()
    cpu_temp = float(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000
    corrected_temp = raw_temp - ((cpu_temp - raw_temp) / 5.466)
    return {
        "temperature": round(corrected_temp, 2),
        "humidity": round(sense.get_humidity(), 2),
        "pressure": round(sense.get_pressure(), 2)
    }

def get_led_colour(readings):
    if readings["temperature"] < 10 or readings["temperature"] > 30:
        return red
    if readings["humidity"] > 80 or readings["humidity"] < 40:
        return yellow
    return green

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Connected to HiveMQ")
    else:
        print(f"❌ Connection failed: {reason_code}")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    if reason_code != 0:
        print("⚠️ Unexpected disconnection. Reconnecting...")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])
client.tls_set()
client.on_connect = on_connect
client.reconnect_delay_set(min_delay=1, max_delay=60)
client.on_disconnect = on_disconnect

client.connect(os.environ["MQTT_BROKER"], int(os.environ["MQTT_PORT"]))
client.loop_start()

print("📡 Sensor running — publishing every 30 seconds. Ctrl+C to stop.")

try:
    while True:
        readings = get_readings()
        colour = get_led_colour(readings)
        sense.clear(colour)
        payload = json.dumps(readings)
        client.publish("envirolink/sensors", payload)
        print(f"Published: {payload}")
        time.sleep(30)
except KeyboardInterrupt:
    print("Stopped.")
    client.loop_stop()
    client.disconnect()