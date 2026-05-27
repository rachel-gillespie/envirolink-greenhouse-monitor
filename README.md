# 🌱 EnviroLink 🌱 Greenhouse Monitor

## Project overview
EnviroLink is a connected IoT system that monitors greenhouse conditions in real time using a Raspberry Pi with a SenseHAT, and combines live indoor readings with outdoor weather data from the OpenWeather API. It provides users with a unified view of both their indoor environment and outdoor forecast, enabling smarter decisions like opening vents when outdoor conditions are favourable, or alerting when frost is forecast.
The system features 24-hour historical trend charts, a real-time updating dashboard, colour-coded alerts based on a greenhouse rules engine, and visual feedback directly on the SenseHAT LED matrix.

## Architecture
See docs/architecture.svg for the full system diagram.
* Sensor/Edge Layer: Raspberry Pi and SenseHAT take in Temperature, Humidity and Pressure readings. MQTT publishes these readings over TLS. The RPi also shows LED visual alerts.
* Network Layer: HiveMQ Cloud MQTT Broker routes messages to backend
* Processing Layer: Backend Services is subscribed to the MQTT Broker, and the messages are routed through the rules engine, external weather API shows current and 24hr forecast. The readings, weather and alerts are all saved to a MongoDB collection. 
* Application Layer: The Web Dashboard has live weather readings and charts, colour-coded alerts and historical trend graphs. The SenseHAT LED Matrix also shows the colour-coded alerts.

## Features list
* View live indoor temperature, humidity, pressure and the timestamp of when it was last updated.
* View outdoor temperature, humidity, pressure and a description of the current weather conditions.
* Graphs of the last 24 hours of indoor data
* Notifications with warnings
* Raspberry Pi SenseHAT LED matrix provides visual alerts indicating warning severity (green/yellow/red)
* Dashboard alerts are colour-coded by severity
* The dashboard updates in real time without needing to refresh (WebSockets)
* The rules engine cross-references indoor and outdoor data (e.g. frost risk, ventilation suggestions)

## Message schema
### Sensor Reading (MQTT payload / readings collection):
```json
{
  "temperature": 24.4,
  "humidity": 34.07,
  "pressure": 1004.63,
  "timestamp": "2026-05-08T21:35:49.227Z"
}
```
### Weather Document (weather collection):
```json
{
  "city": "Wicklow",
  "temperature": 8.36,
  "feels_like": 5.51,
  "humidity": 79,
  "pressure": 1007,
  "description": "overcast clouds",
  "icon": "04d",
  "timestamp": "2026-05-08T21:35:49.227Z"
}
```
> [!NOTE]
> The city field is returned by the OpenWeather API and may vary depending on your coordinates.

### Alert Document (alerts collection):
```json
{
  "type": "danger",
  "msg": "Low Humidity Level - Activate misting system!",
  "timestamp": "2026-05-18T10:58:59.295Z"
}
```
## Setup instructions

### Prerequisites
* A Raspberry Pi with SenseHAT
* Python 3 installed
* A MongoDB Atlas account — create a free cluster and note your connection string. Add your Raspberry Pi's IP address to the Network Access whitelist.
* A HiveMQ Cloud account — note your broker URL, port, username and password
* An OpenWeather API key (free tier)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rachel-gillespie/connected-devices-app
cd connected-devices-app
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create a .env file in the project root and add the following:
```
MONGO_URI=your_mongodb_connection_string
MQTT_BROKER=your_hivemq_broker_url
MQTT_PORT=8883
MQTT_USERNAME=your_hivemq_username
MQTT_PASSWORD=your_hivemq_password
OPENWEATHER_API_KEY=your_openweather_api_key
OPENWEATHER_LAT=your_latitude
OPENWEATHER_LON=your_longitude
OPENWEATHER_UNITS=metric
SECRET_KEY=any_random_string
```

4. Initialise the default greenhouse thresholds in MongoDB:
```bash
python3 setup_config.py
```
> [!NOTE]
> This creates a `config` document in MongoDB with the default greenhouse thresholds. Only needs to be run once. Thresholds can be updated via the Settings page on the dashboard.

## How to run
In two separate terminals:
```bash
python3 sensor/sensor.py
python3 dashboard/app.py
```
The dashboard will be available at `http://<your-rpi-ip>:5000`

## Demo video link


## Running as a systemd service (optional)
To run EnviroLink automatically on boot, create the following service files:
> [!NOTE]
> Replace rachelgillespie in the User, WorkingDirectory, ExecStart and EnvironmentFile fields with your own username.
> [!NOTE]
> The `After=network-online.target` and `Wants=network-online.target` directives ensure the services wait for a full network connection before starting. This improves reliability on boot and prevents MQTT connection failures.

/etc/systemd/system/envirolink-sensor.service
```ini
[Unit]
Description=EnviroLink Sensor
After=network-online.target
Wants=network-online.target

[Service]
User=rachelgillespie
WorkingDirectory=/home/rachelgillespie/connected-devices-app
ExecStart=/home/rachelgillespie/connected-devices-app/.venv/bin/python sensor/sensor.py
EnvironmentFile=/home/rachelgillespie/connected-devices-app/.env
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

/etc/systemd/system/envirolink-app.service 
```ini
[Unit]
Description=EnviroLink App
After=network-online.target
Wants=network-online.target

[Service]
User=rachelgillespie
WorkingDirectory=/home/rachelgillespie/connected-devices-app
ExecStart=/home/rachelgillespie/connected-devices-app/.venv/bin/python dashboard/app.py
EnvironmentFile=/home/rachelgillespie/connected-devices-app/.env
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable envirolink-sensor envirolink-app
sudo systemctl start envirolink-sensor envirolink-app
```