# sensor.py
# Runs on the Raspberry Pi — reads SenseHAT sensor data every 30 seconds,
# applies CPU temperature calibration, publishes readings to HiveMQ via MQTT,
# and reflects the current greenhouse status on the SenseHAT LED matrix.

import paho.mqtt.client as mqtt
from sense_hat import SenseHat
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()  # reads key-value pairs from a .env file and sets them as environment variables

sense = SenseHat()
time.sleep(10)  # allow the SenseHAT time to initialise before taking readings — important for systemd startup

# LED colours used to indicate greenhouse status at a glance on the SenseHAT matrix
green = (0, 255, 0)   # all readings within safe range
red = (255, 0, 0)     # critical condition (temperature out of range)
yellow = (255, 255, 0) # warning condition (humidity out of range)

def get_readings():
    """
    Read temperature, humidity, and pressure from the SenseHAT.
    Applies a CPU heat correction to the raw temperature reading, as the
    Raspberry Pi's CPU sits close to the SenseHAT and skews readings upward.
    Returns a dictionary of rounded sensor values.
    """
    raw_temp = sense.get_temperature()
    cpu_temp = float(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000  # CPU temp is stored in millidegrees
    corrected_temp = raw_temp - ((cpu_temp - raw_temp) / 5.4)  # 5.4 divisor recommended by the Raspberry Pi community
    return {
        "temperature": round(corrected_temp, 2),
        "humidity": round(sense.get_humidity(), 2),
        "pressure": round(sense.get_pressure(), 2)
    }

def get_led_colour(readings):
    """
    Determine the appropriate LED matrix colour based on current readings.
    Red indicates a critical temperature condition, yellow a humidity warning,
    and green means all values are within the safe operating range.
    """
    if readings["temperature"] < 10 or readings["temperature"] > 30:
        return red
    if readings["humidity"] > 80 or readings["humidity"] < 40:
        return yellow
    return green  # only reached if both temperature and humidity are within range


# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    """Called automatically by paho-mqtt when the broker connection is established or fails."""
    if reason_code == 0:
        print("✅ Connected to HiveMQ")
    else:
        print(f"❌ Connection failed: {reason_code}")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    """Called automatically by paho-mqtt on disconnection — logs unexpected drops for debugging."""
    if reason_code != 0:
        print("⚠️ Unexpected disconnection. Reconnecting...")


# --- MQTT Client Setup ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])  # os.environ returns a dictionary having the user's environmental variable as key and their values as value
client.tls_set()  # enable TLS encryption for the HiveMQ cloud broker connection
client.on_connect = on_connect
client.reconnect_delay_set(min_delay=1, max_delay=60)  # exponential backoff — retries from 1s up to 60s on disconnection
client.on_disconnect = on_disconnect

client.connect(os.environ["MQTT_BROKER"], int(os.environ["MQTT_PORT"]))
client.loop_start()  # runs MQTT network traffic in a background thread so the main loop is not blocked

print("📡 Sensor running — publishing every 30 seconds. Ctrl+C to stop.")

# --- Main Sensor Loop ---
try:
    while True:
        readings = get_readings()
        colour = get_led_colour(readings)
        sense.clear(colour)  # set the entire LED matrix to the status colour
        payload = json.dumps(readings)  # serialise readings dict to JSON string for MQTT transport
        client.publish("envirolink/sensors", payload)
        print(f"Published: {payload}")
        time.sleep(30)  # publish a new reading every 30 seconds
except KeyboardInterrupt:
    # Graceful shutdown — stop the MQTT background thread and cleanly disconnect from the broker
    print("Stopped.")
    client.loop_stop()
    client.disconnect()