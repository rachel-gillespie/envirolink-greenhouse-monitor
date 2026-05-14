fetch('/api/readings')
    .then(response => response.json())
    .then(items => {
        const temperatures = items.map(item => item.temperature);
        const timestamps = items.map(item => new Date(item.timestamp).toLocaleTimeString());
        const ctx = document.getElementById('temperatureChart');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: temperatures
                }]
            }
        })
    });