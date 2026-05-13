from flask import Flask, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def dashboard():
    # In the future, these will come from MongoDB and OpenWeather API
    sensor_data = {"temperature": 21.50, "humidity": 45.06, "pressure": 56.21}
    weather_data = {"temperature": 12, "humidity": 30, "pressure": 20, "description": "Cloudy"}
    
    return render_template('index.html', 
                           title="Dashboard", 
                           sensor_data=sensor_data, 
                           weather_data=weather_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)