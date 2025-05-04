let timelineChart = null;

async function updateDashboard() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        // Update status panel
        const statusPanel = document.getElementById('userStatuses');
        let statusHtml = '';
        
        data.users.forEach(user => {
            const userData = data[user];
            statusHtml += `
                <div class="status-card ${userData.current_status}">
                    <h3>${user}</h3>
                    <div class="status-indicator"></div>
                    <p>${userData.current_status.toUpperCase()}</p>
                    ${userData.last_seen ? 
                        `<small>Last seen: ${new Date(userData.last_seen).toLocaleString()}</small>` : ''}
                </div>
            `;
        });
        statusPanel.innerHTML = statusHtml;

        // Update timeline chart
        if (data.users.length > 0) {
            updateTimelineChart(data.users[0]); // Show first user by default
        }
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

async function updateTimelineChart(username) {
    try {
        const response = await fetch(`/history/${username}`);
        const history = await response.json().history;

        const chartData = {
            datasets: [{
                label: `${username} Status`,
                data: history.map(event => ({
                    x: luxon.DateTime.fromISO(event.timestamp).toJSDate(),
                    y: event.status === 'online' ? 1 : 0
                })),
                borderColor: '#00ffcc',
                backgroundColor: 'rgba(0, 255, 204, 0.2)',
                fill: true,
                stepped: 'after'
            }]
        };

        if (timelineChart) {
            timelineChart.data = chartData;
            timelineChart.update();
        } else {
            const ctx = document.getElementById('timelineChart').getContext('2d');
            timelineChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    scales: {
                        x: { type: 'time', time: { tooltipFormat: 'DD T' } },
                        y: { ticks: { callback: v => v ? 'Online' : 'Offline' } }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

// Initial load
updateDashboard();
// Update every 3 seconds
setInterval(updateDashboard, 3000);