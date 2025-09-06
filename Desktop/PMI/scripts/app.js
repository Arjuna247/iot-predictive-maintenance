// Global variables
let simulationRunning = false;
let simulationInterval;
let anomalyInjected = false;
let sensorChart, anomalyChart, predictiveChart;
let sensorData = [];
let anomalyData = [];
let predictiveData = [];
let blockHeight = 1247;
let flCountdown = 45;

// Initialize charts
function initCharts() {
    // Sensor Chart
    const sensorCtx = document.getElementById('sensorChart').getContext('2d');
    sensorChart = new Chart(sensorCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature',
                data: [],
                borderColor: '#ff6b6b',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                tension: 0.4
            }, {
                label: 'Vibration',
                data: [],
                borderColor: '#4ecdc4',
                backgroundColor: 'rgba(78, 205, 196, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });

    // Anomaly Chart
    const anomalyCtx = document.getElementById('anomalyChart').getContext('2d');
    anomalyChart = new Chart(anomalyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Anomaly Score',
                data: [],
                borderColor: '#ffa726',
                backgroundColor: 'rgba(255, 167, 38, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    min: 0,
                    max: 1,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });

    // Predictive Chart
    const predictiveCtx = document.getElementById('predictiveChart').getContext('2d');
    predictiveChart = new Chart(predictiveCtx, {
        type: 'line',
        data: {
            labels: ['Now', '2h', '4h', '6h', '8h', '10h', '12h'],
            datasets: [{
                label: 'Health Prediction',
                data: [82, 79, 75, 70, 65, 58, 52],
                borderColor: '#4ecdc4',
                backgroundColor: 'rgba(78, 205, 196, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });
}

// Generate realistic sensor data
function generateSensorData() {
    const now = Date.now();
    const baseTemp = 28;
    const baseHumidity = 65;
    const baseCurrent = 0.15;
    
    // Add some noise and trends
    const tempNoise = (Math.random() - 0.5) * 4;
    const humidityNoise = (Math.random() - 0.5) * 10;
    const currentNoise = (Math.random() - 0.5) * 0.05;
    
    // Simulate anomaly injection
    let tempAnomalyFactor = 1;
    let vibrationAnomalyFactor = 1;
    let currentAnomalyFactor = 1;
    
    if (anomalyInjected) {
        tempAnomalyFactor = 1.5 + Math.random() * 0.5; // 50-100% increase
        vibrationAnomalyFactor = 3 + Math.random() * 2; // 300-500% increase
        currentAnomalyFactor = 2 + Math.random() * 0.5; // 200-250% increase
    }
    
    const temperature = (baseTemp + tempNoise) * tempAnomalyFactor;
    const humidity = Math.max(0, Math.min(100, baseHumidity + humidityNoise));
    const current = Math.max(0, (baseCurrent + currentNoise) * currentAnomalyFactor);
    
    // Simulate MPU6050-like accelerometer data
    const accel = {
        x: (Math.random() - 0.5) * 0.1 * vibrationAnomalyFactor,
        y: (Math.random() - 0.5) * 0.1 * vibrationAnomalyFactor,
        z: 0.98 + (Math.random() - 0.5) * 0.1 * vibrationAnomalyFactor
    };
    
    const gyro = {
        x: (Math.random() - 0.5) * 0.4 * vibrationAnomalyFactor,
        y: (Math.random() - 0.5) * 0.4 * vibrationAnomalyFactor,
        z: (Math.random() - 0.5) * 0.4 * vibrationAnomalyFactor
    };
    
    const vibrationMagnitude = Math.sqrt(accel.x**2 + accel.y**2 + (accel.z-0.98)**2);
    
    return {
        deviceId: "sim_esp32_01",
        timestamp: now,
        temperature: temperature,
        humidity: humidity,
        accel: accel,
        gyro: gyro,
        current: current,
        vibrationMagnitude: vibrationMagnitude
    };
}

// Update sensor displays
function updateSensorDisplay(data) {
    document.getElementById('temp-value').textContent = data.temperature.toFixed(1) + '°C';
    document.getElementById('humidity-value').textContent = data.humidity.toFixed(1) + '%';
    document.getElementById('vibration-value').textContent = data.vibrationMagnitude.toFixed(3) + 'g';
    document.getElementById('current-value').textContent = data.current.toFixed(3) + 'A';
}

// Anomaly detection algorithm
function detectAnomalies(data) {
    let anomalyScore = 0;
    let anomalies = [];
    
    // Temperature anomaly (> 40°C or < 15°C)
    if (data.temperature > 40 || data.temperature < 15) {
        anomalyScore += 0.4;
        anomalies.push(`Temperature: ${data.temperature.toFixed(1)}°C`);
    }
    
    // Vibration anomaly (> 0.1g)
    if (data.vibrationMagnitude > 0.1) {
        anomalyScore += 0.5;
        anomalies.push(`High vibration: ${data.vibrationMagnitude.toFixed(3)}g`);
    }
    
    // Current anomaly (> 0.3A)
    if (data.current > 0.3) {
        anomalyScore += 0.3;
        anomalies.push(`High current: ${data.current.toFixed(3)}A`);
    }
    
    // Humidity anomaly (< 30% or > 85%)
    if (data.humidity < 30 || data.humidity > 85) {
        anomalyScore += 0.2;
        anomalies.push(`Humidity: ${data.humidity.toFixed(1)}%`);
    }
    
    return { score: Math.min(anomalyScore, 1), anomalies };
}

// Update anomaly detection display
function updateAnomalyDisplay(anomalyResult) {
    const statusIndicator = document.getElementById('ai-status');
    const statusText = document.getElementById('ai-status-text');
    const alertsContainer = document.getElementById('anomaly-alerts');
    const confidenceLevel = document.getElementById('confidence-level');
    const confidenceBar = document.getElementById('confidence-bar');
    
    // Update status based on anomaly score
    if (anomalyResult.score > 0.7) {
        statusIndicator.className = 'status-indicator status-critical';
        statusText.textContent = 'Critical Anomaly Detected';
    } else if (anomalyResult.score > 0.3) {
        statusIndicator.className = 'status-indicator status-warning';
        statusText.textContent = 'Warning: Anomaly Detected';
    } else {
        statusIndicator.className = 'status-indicator status-normal';
        statusText.textContent = 'System Normal';
    }
    
    // Update confidence level (inverse of anomaly score)
    const confidence = Math.round((1 - anomalyResult.score) * 100);
    confidenceLevel.textContent = confidence + '%';
    confidenceBar.style.width = confidence + '%';
    
    // Show/hide alerts
    alertsContainer.innerHTML = '';
    if (anomalyResult.anomalies.length > 0) {
        anomalyResult.anomalies.forEach(anomaly => {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert show';
            alertDiv.innerHTML = `⚠️ ${anomaly}`;
            alertsContainer.appendChild(alertDiv);
        });
    }
}

// Update charts
function updateCharts(data, anomalyResult) {
    const timeLabel = new Date(data.timestamp).toLocaleTimeString();
    
    // Update sensor chart
    sensorChart.data.labels.push(timeLabel);
    sensorChart.data.datasets[0].data.push(data.temperature);
    sensorChart.data.datasets[1].data.push(data.vibrationMagnitude * 100); // Scale for visibility
    
    // Keep only last 20 points
    if (sensorChart.data.labels.length > 20) {
        sensorChart.data.labels.shift();
        sensorChart.data.datasets[0].data.shift();
        sensorChart.data.datasets[1].data.shift();
    }
    
    sensorChart.update('none');
    
    // Update anomaly chart
    anomalyChart.data.labels.push(timeLabel);
    anomalyChart.data.datasets[0].data.push(anomalyResult.score);
    
    if (anomalyChart.data.labels.length > 20) {
        anomalyChart.data.labels.shift();
        anomalyChart.data.datasets[0].data.shift();
    }
    
    anomalyChart.update('none');
}

// Simulate federated learning updates
function updateFederatedLearning() {
    const node1Acc = document.getElementById('node1-acc');
    const node2Acc = document.getElementById('node2-acc');
    const node3Acc = document.getElementById('node3-acc');
    const globalAcc = document.getElementById('global-accuracy');
    
    // Simulate accuracy improvements over time
    let acc1 = parseFloat(node1Acc.textContent);
    let acc2 = parseFloat(node2Acc.textContent);
    let acc3 = parseFloat(node3Acc.textContent);
    
    // Random small improvements
    acc1 += (Math.random() - 0.4) * 2; // Slight bias toward improvement
    acc2 += (Math.random() - 0.4) * 2;
    acc3 += (Math.random() - 0.4) * 2;
    
    // Keep within realistic bounds
    acc1 = Math.max(75, Math.min(95, acc1));
    acc2 = Math.max(75, Math.min(95, acc2));
    acc3 = Math.max(75, Math.min(95, acc3));
    
    node1Acc.textContent = acc1.toFixed(0) + '%';
    node2Acc.textContent = acc2.toFixed(0) + '%';
    node3Acc.textContent = acc3.toFixed(0) + '%';
    
    // Calculate and update global accuracy
    const globalAccuracy = (acc1 + acc2 + acc3) / 3;
    globalAcc.textContent = globalAccuracy.toFixed(0) + '%';
    
    // Update accuracy bars
    const accuracyBars = document.querySelectorAll('.federated-node .accuracy-fill');
    accuracyBars[0].style.width = acc1 + '%';
    accuracyBars[1].style.width = acc2 + '%';
    accuracyBars[2].style.width = acc3 + '%';
}

// Add new blockchain block
function addBlockchainBlock(data, anomalyResult) {
    const blocksContainer = document.getElementById('blockchain-blocks');
    const blockHeightElement = document.getElementById('block-height');
    
    // Only add block if there's significant activity
    if (anomalyResult.score > 0.3 || Math.random() < 0.1) {
        blockHeight++;
        blockHeightElement.textContent = blockHeight.toLocaleString();
        
        const blockDiv = document.createElement('div');
        blockDiv.className = 'blockchain-block';
        
        const blockType = anomalyResult.score > 0.3 ? 'Anomaly Alert' : 'FL Update';
        const hash = generateRandomHash();
        
        blockDiv.innerHTML = `
            <div>Block #${blockHeight}</div>
            <div class="block-hash">Hash: ${hash}</div>
            <div>${blockType}: ${data.deviceId}</div>
            <div style="font-size: 0.7rem; opacity: 0.6;">Just now</div>
        `;
        
        blocksContainer.insertBefore(blockDiv, blocksContainer.firstChild);
        
        // Keep only last 3 blocks visible
        if (blocksContainer.children.length > 3) {
            blocksContainer.removeChild(blocksContainer.lastChild);
        }
    }
}

// Generate random hash for blockchain simulation
function generateRandomHash() {
    const chars = '0123456789abcdef';
    let hash = '0x';
    for (let i = 0; i < 8; i++) {
        hash += chars[Math.floor(Math.random() * chars.length)];
    }
    return hash + '...';
}

// Update digital twin health scores
function updateDigitalTwin(anomalyResult) {
    const motorHealth = document.getElementById('motor-health');
    const bearingHealth = document.getElementById('bearing-health');
    const tempHealth = document.getElementById('temp-health');
    const overallHealth = document.getElementById('overall-health');
    
    // Decrease health based on anomaly score
    let motorScore = parseFloat(motorHealth.textContent);
    let bearingScore = parseFloat(bearingHealth.textContent);
    let tempScore = parseFloat(tempHealth.textContent);
    
    if (anomalyResult.score > 0.5) {
        motorScore -= Math.random() * 3;
        bearingScore -= Math.random() * 5;
        tempScore -= Math.random() * 4;
    } else {
        // Gradual degradation over time
        motorScore -= Math.random() * 0.5;
        bearingScore -= Math.random() * 0.8;
        tempScore -= Math.random() * 0.6;
    }
    
    // Keep within bounds
    motorScore = Math.max(30, Math.min(100, motorScore));
    bearingScore = Math.max(30, Math.min(100, bearingScore));
    tempScore = Math.max(30, Math.min(100, tempScore));
    
    motorHealth.textContent = Math.round(motorScore);
    bearingHealth.textContent = Math.round(bearingScore);
    tempHealth.textContent = Math.round(tempScore);
    
    // Update overall health
    const overall = (motorScore + bearingScore + tempScore) / 3;
    overallHealth.textContent = Math.round(overall);
    
    // Update health score colors
    updateHealthColor(motorHealth, motorScore);
    updateHealthColor(bearingHealth, bearingScore);
    updateHealthColor(tempHealth, tempScore);
    updateHealthColor(overallHealth, overall);
}

function updateHealthColor(element, score) {
    element.className = 'health-score';
    if (score >= 80) element.classList.add('health-excellent');
    else if (score >= 65) element.classList.add('health-good');
    else if (score >= 50) element.classList.add('health-warning');
    else element.classList.add('health-critical');
}

// Main simulation loop
function runSimulation() {
    if (!simulationRunning) return;
    
    // Generate new sensor data
    const data = generateSensorData();
    updateSensorDisplay(data);
    
    // Run anomaly detection
    const anomalyResult = detectAnomalies(data);
    updateAnomalyDisplay(anomalyResult);
    
    // Update charts
    updateCharts(data, anomalyResult);
    
    // Update digital twin
    updateDigitalTwin(anomalyResult);
    
    // Add blockchain block occasionally
    addBlockchainBlock(data, anomalyResult);
    
    // Reset anomaly injection after some time
    if (anomalyInjected && Math.random() < 0.1) {
        anomalyInjected = false;
    }
}

// Federated learning countdown and updates
function federatedLearningLoop() {
    const countdown = document.getElementById('fl-countdown');
    flCountdown--;
    
    if (flCountdown <= 0) {
        updateFederatedLearning();
        flCountdown = 60 + Math.random() * 30; // 60-90 seconds
    }
    
    countdown.textContent = flCountdown + 's';
}

// Control functions
function toggleSimulation() {
    const button = event.target;
    
    if (!simulationRunning) {
        simulationRunning = true;
        button.textContent = 'Stop Simulation';
        button.style.background = 'linear-gradient(45deg, #ff5252, #f44336)';
        
        // Start simulation intervals
        simulationInterval = setInterval(runSimulation, 1000); // Every second
        setInterval(federatedLearningLoop, 1000); // Countdown every second
        
        // Initialize with some data
        runSimulation();
    } else {
        simulationRunning = false;
        button.textContent = 'Start Simulation';
        button.style.background = 'linear-gradient(45deg, #4ecdc4, #45b7aa)';
        
        clearInterval(simulationInterval);
    }
}

function injectAnomaly() {
    if (simulationRunning) {
        anomalyInjected = true;
        
        // Show temporary feedback
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = 'Anomaly Injected!';
        button.style.background = 'linear-gradient(45deg, #ff5252, #f44336)';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = 'linear-gradient(45deg, #4ecdc4, #45b7aa)';
        }, 2000);
    }
}

// Real-time data streaming simulation
function simulateDataStream() {
    if (!simulationRunning) return;
    
    // Add visual feedback for data updates
    const sensorValues = document.querySelectorAll('.sensor-value');
    sensorValues.forEach(sv => {
        sv.classList.add('updating');
        setTimeout(() => sv.classList.remove('updating'), 300);
    });
}

// System health monitoring
function systemHealthCheck() {
    const nodes = document.querySelectorAll('.federated-node .status-indicator');
    
    nodes.forEach((node, index) => {
        // Simulate occasional node issues
        if (Math.random() < 0.05) { // 5% chance
            node.className = 'status-indicator status-warning';
        } else if (Math.random() < 0.02) { // 2% chance
            node.className = 'status-indicator status-critical';
        } else {
            node.className = 'status-indicator status-normal';
        }
    });
}

// Add tooltips for better UX
function addTooltips() {
    const tooltipElements = [
        {selector: '.sensor-value', text: 'Real-time sensor readings from IoT devices'},
        {selector: '.federated-node', text: 'Federated learning node with local model training'},
        {selector: '.blockchain-block', text: 'Immutable record of system events and model updates'},
        {selector: '.twin-component', text: 'Digital twin component health prediction'}
    ];

    tooltipElements.forEach(({selector, text}) => {
        document.querySelectorAll(selector).forEach(el => {
            el.title = text;
        });
    });
}

// Initialize everything when page loads
window.addEventListener('load', function() {
    initCharts();
    
    // Start federated learning countdown
    setInterval(federatedLearningLoop, 1000);
    
    // Add system health monitoring
    setInterval(systemHealthCheck, 10000); // Every 10 seconds
    setInterval(simulateDataStream, 1000); // Every second
    
    // Initialize tooltips
    setTimeout(addTooltips, 1000);
    
    // Add some initial blockchain blocks
    setTimeout(() => {
        addBlockchainBlock({deviceId: 'sim_esp32_02'}, {score: 0.1});
    }, 2000);
    
    setTimeout(() => {
        addBlockchainBlock({deviceId: 'sim_esp32_03'}, {score: 0.6});
    }, 4000);
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        toggleSimulation();
    }
    if (e.ctrlKey && e.key === 'a') {
        e.preventDefault();
        injectAnomaly();
    }
});

console.log('🏭 Industrial IoT Predictive Maintenance System Initialized');
console.log('💡 Press Ctrl+S to start/stop simulation');
console.log('⚠️ Press Ctrl+A to inject anomaly');