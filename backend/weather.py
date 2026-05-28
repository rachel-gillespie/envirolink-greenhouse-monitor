# weather.py
# Fetches current weather conditions and short-term forecast from the OpenWeatherMap API.

import requests
from dotenv import load_dotenv
import os

load_dotenv()

# OpenWeatherMap API credentials and location config, loaded from .env
API_KEY = os.environ["OPENWEATHER_API_KEY"]  # os.environ raises a KeyError immediately if the variable is missing — preferable to os.getenv() which silently returns None and causes a harder-to-trace error later
# LAT & LON were more accurate for location than using CITY_NAME
LAT = os.environ["OPENWEATHER_LAT"]
LON = os.environ["OPENWEATHER_LON"]
UNITS = os.environ["OPENWEATHER_UNITS"]  # "metric" for Celsius, "imperial" for Fahrenheit

def get_current_weather():
    """
    Fetch the current weather conditions for the configured location.
    Returns a dictionary of weather data.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"
    response = requests.get(url)
    data = response.json()

    # Extract and return only the fields needed by the dashboard
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }

def get_forecast():
    """
    Fetch a short-term weather forecast for the configured location.
    cnt=8 returns the next 8 x 3-hour intervals (24 hours ahead).
    Returns a list of forecast dictionaries, each representing one time slot.
    """
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}&cnt=8"
    response = requests.get(url)
    data = response.json()

    forecast = []
    for item in data["list"]:
        forecast.append({
            "time": item["dt_txt"],        # human-readable timestamp e.g. "2025-05-01 15:00:00"
            "temperature": item["main"]["temp"],
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"]
        })
    return forecast

if __name__ == "__main__":
    # executed only when this file is run directly (e.g. python weather.py)
    # not executed when weather.py is imported by app.py
    print(get_current_weather())
    print(get_forecast())