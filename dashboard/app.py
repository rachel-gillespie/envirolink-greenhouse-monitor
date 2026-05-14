from flask import Flask, render_template
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from db import connect_db

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = connect_db()

@app.route('/')
def dashboard():
    # In the future, these will come from MongoDB and OpenWeather API
    sensor_data = db.readings.find_one({}, sort=[("timestamp", -1)])
    weather_data = db.weather.find_one({}, sort=[("timestamp", -1)])
    return render_template('index.html', 
                           title="Dashboard", 
                           sensor_data=sensor_data, 
                           weather_data=weather_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)