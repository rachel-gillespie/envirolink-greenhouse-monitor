import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ["OPENWEATHER_API_KEY"]
LAT = os.environ["OPENWEATHER_LAT"]
LON = os.environ["OPENWEATHER_LON"]
UNITS = os.environ["OPENWEATHER_UNITS"]

def get_current_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"
    response = requests.get(url)
    data = response.json()

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
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"
    response = requests.get(url)
    data = response.json()

    forecast = []
    for item in data["list"]:
        forecast.append({
            "time": item["dt_txt"],
            "temperature": item["main"]["temp"],
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"]
        })
    return forecast

if __name__ == "__main__":
    print(get_current_weather())
    print(get_forecast())