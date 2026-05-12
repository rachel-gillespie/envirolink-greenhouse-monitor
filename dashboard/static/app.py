from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    # In the future, these will come from MongoDB and OpenWeather API
    sensor_data = {"temp": 21.5, "humidity": 45}
    weather_data = {"temp": 12.0, "condition": "Cloudy"}
    
    return render_template('index.njk', 
                           title="Dashboard", 
                           sensor_data=sensor_data, 
                           weather_data=weather_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True