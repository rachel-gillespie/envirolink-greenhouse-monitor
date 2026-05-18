from flask import Flask, render_template, jsonify
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from db import connect_db, get_historical_data

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = connect_db()

@app.route('/')
def dashboard():
    sensor_data = db.readings.find_one({}, sort=[("timestamp", -1)])
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
    app.run(host='0.0.0.0', port=5000, debug=True)