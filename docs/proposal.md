# EnviroLink — Home Environment & Weather Integration Monitor
#### Student Name: Rachel Gillespie   Student ID: 20118715

## Introduction

EnviroLink is a connected IoT system that monitors the indoor home environment using a Raspberry Pi with a SenseHAT, and combines this live local data with real-time outdoor weather forecasts from an external API. The goal is to give users a unified view of both their indoor conditions and the outside world, enabling smarter decisions like ventilating a stuffy room when the weather is ideal, or flagging when indoor humidity is rising while rain is forecast outside.

The system follows a four-layer IoT architecture: the Raspberry Pi acts as the **sensor/edge node**, a Python backend handles **processing and logic**, **MQTT** is used for lightweight messaging between components, and a **web dashboard** provides the **application layer** with live readings, historical trends, and weather-aware alerts.

This project extends and integrates the weather web application developed in the previous semester, adding a real physical data source and a proper IoT communication layer.

## Architecture Overview

```
[Raspberry Pi / SenseHAT]
  Temperature, Humidity, Pressure
         |
       MQTT Publish
         |
  [MQTT Broker (Mosquitto)]
         |
       MQTT Subscribe
         |
  [Python Backend Service]
  - Threshold checks & alerting
  - Fetches outdoor weather [Open Weather](https://openweathermap.org/api)
  - Stores readings to NoSQL database (MongoDB)
         |
     HTTP / WebSocket
         |
  [Web Dashboard]
  - Live indoor readings
  - Historical charts (indoor trends)
  - Current outdoor weather & forecast
  - Weather-aware alerts (e.g. "Open a window, it's cooler outside")
```

## Features & Processing Logic

- **Data collection** - SenseHAT readings (temperature, humidity, pressure) published to MQTT every 30 seconds as JSON messages.
- **Threshold checks** - backend flags readings outside acceptable ranges (e.g. humidity > 70%, temperature > 27°C).
- **Outdoor weather integration** - backend polls the [Open Weather](https://openweathermap.org/api) free weather API for current conditions and short-term forecast at the user's location.
- **Weather-aware rules engine** - simple rules cross-reference indoor and outdoor data:
  - *"Indoor temp high + outdoor temp lower → suggest ventilation"*
  - *"Rain forecast + laundry alert active → notify user"*
- **Historical logging** - all readings stored as documents in a MongoDB collection; dashboard displays trend charts for the past 24 hours.
- **Alerts/notifications** - dashboard displays colour-coded alerts; stretch goal: email notification via SMTP.

## Tools, Technologies and Equipment

| Category | Item |
|---|---|
| **Hardware** | Raspberry Pi (with SenseHAT) |
| **Programming Language** | Python 3 |
| **Networking Protocol** | MQTT (publish/subscribe messaging) |
| **MQTT Broker** | Eclipse Mosquitto (local) |
| **External API** | Open Weather API (free, no key required) |
| **Backend** | Python (`paho-mqtt`, `requests`, `pymongo`, `flask`) |
| **Database** | MongoDB (via `pymongo`) |
| **Frontend / Dashboard** | Flask + Nunjucks templates + Bulma CSS + Chart.js (for graphs) |
| **IDE** | VS Code with SSH Remote (for RPi development) |
| **Version Control** | Git + GitHub |
| **Data Format** | JSON (MQTT message payloads) |

## Cross-Module Integration

This project draws on knowledge from across all four modules studied this year, directly satisfying the "combined knowledge" criteria in the grading rubric:

| Module | Knowledge Applied |
|---|---|
| **Computer Systems & Networks** | Raspberry Pi setup, Linux/Bash scripting, MQTT networking, IP/transport layer communication |
| **Database** | MongoDB document storage for sensor readings, querying historical data by time range |
| **Web Development** | Nunjucks templating, Bulma CSS framework, HTML/CSS/JavaScript dashboard, Chart.js for trend graphs |
| **Programming** | Python backend logic, MQTT client, REST API integration, rules engine for weather-aware alerts |

## Potential Stretch Goals

The following are self-acquired technologies beyond module content that I am considering incorporating, time permitting:

- **WebSockets** (Flask-SocketIO) - push live sensor updates to the dashboard in real time as MQTT messages arrive, rather than relying on periodic polling.
- **MongoDB Atlas** - deploy the database to the cloud (free tier) rather than running it locally, enabling remote access and aligning with the cloud deployment expectations of a Release 4 submission.
- **Docker / Docker Compose** - containerise the backend and MQTT broker so the full stack can be launched with a single command, demonstrating DevOps awareness and making the project easier to reproduce.
- **MQTT reconnect / retry logic** - implement backoff and reconnection handling in the sensor client to make the system more robust against network interruptions.

## Project Repository

The repository will include:
- `sensor/` — RPi data collection script (SenseHAT or simulator)
- `backend/` — MQTT subscriber, weather API integration, database handler
- `dashboard/` — Flask web app and frontend templates
- `docs/` — Architecture diagram, setup notes
- `README.md` — Project overview, installation guide, and demo link
