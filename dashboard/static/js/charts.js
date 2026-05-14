fetch('/api/readings')
    .then(response => response.json())
    .then(items => {
        const temperatures = items.map(item => item.temperature);
        const humiditys = items.map(item => item.humidity);
        const pressures = items.map(item => item.pressure);
        const timestamps = items.map(item => new Date(item.timestamp).toLocaleTimeString());
        const tempCtx = document.getElementById('temperatureChart');
        const humidityCtx = document.getElementById('humidityChart');
        const pressureCtx = document.getElementById('pressureChart');
        new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: temperatures
                }]
            }
        })
        new Chart(humidityCtx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Humidity (%)',
                    data: humiditys
                }]
            }
        })
        new Chart(pressureCtx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Pressure (hPa)',
                    data: pressures
                }]
            }
        })
    });