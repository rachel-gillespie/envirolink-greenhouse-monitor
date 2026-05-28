// dashboard.js
// Handles chart rendering, live sensor updates via Socket.IO, and alert display.

// --- Historical Charts ---
// Fetch the last 24 hours of readings from the Flask API and render three Chart.js line graphs.
fetch('/api/readings') // relative path always requests from whatever server served the page, regardless of IP address
    .then(response => response.json()) // parse the JSON response body into a JavaScript array of objects
    .then(items => {
        // Extract each metric into its own array for use as Chart.js datasets
        const temperatures = items.map(item => item.temperature);
        const humidities = items.map(item => item.humidity);
        const pressures = items.map(item => item.pressure);
        const timestamps = items.map(item => new Date(item.timestamp).toLocaleTimeString()); // format UTC timestamp to local time string for chart labels

        // Get the canvas elements that Chart.js will render into
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
        });

        new Chart(humidityCtx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Humidity (%)',
                    data: humidities
                }]
            }
        });

        new Chart(pressureCtx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Pressure (hPa)',
                    data: pressures
                }]
            }
        });
    });


// --- Live Readings via Socket.IO ---
const socket = io(); // connect to the Flask-SocketIO server

// When the backend publishes a new MQTT reading, update the live display values on the dashboard
socket.on('new_reading', function(data) {
    document.querySelector('.indoor-temperature').textContent = data.temperature + '°C';
    document.querySelector('.indoor-humidity').textContent = data.humidity + '%';
    document.querySelector('.indoor-pressure').textContent = data.pressure + 'hPa';
    document.querySelector('.indoor-timestamp').textContent = data.timestamp;
});


// --- Alerts ---
function loadAlerts() {
    // Fetch the current list of active alerts from the backend and re-render the alerts container
    fetch('/api/alerts')
        .then(response => response.json())
        .then(alerts => {
            const container = document.getElementById('alerts-container');
            container.innerHTML = ''; // clear existing alerts before re-rendering

            alerts.forEach(alert => {
                // Use Bulma's is-danger (red) or is-warning (yellow) class depending on alert severity
                const div = document.createElement('div');
                div.className = `notification ${alert.type === 'danger' ? 'is-danger' : 'is-warning'}`;
                div.innerHTML = `<button class="delete"></button>${alert.msg}`;
                container.appendChild(div);
            });

            // Reattach delete button listeners (needed because innerHTML was cleared above)
            container.querySelectorAll('.delete').forEach(button => {
                button.addEventListener('click', () => button.parentElement.remove());
            });
        });
}

loadAlerts(); // run once on page load
setInterval(loadAlerts, 30000); // then refresh every 30 seconds to stay in sync with new MQTT readings