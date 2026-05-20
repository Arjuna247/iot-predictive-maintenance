# Industrial IoT Predictive Maintenance System

An Edge AI-powered predictive maintenance platform featuring real-time IoT sensor simulation, anomaly detection, federated learning, blockchain audit logging, and digital twin modeling.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Configuration](#configuration)
- [Technical Reference](#technical-reference)
- [Browser Compatibility](#browser-compatibility)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This system provides a browser-based dashboard for monitoring industrial equipment health in real time. It simulates ESP32-based sensor nodes, applies edge AI anomaly detection, and models equipment degradation using digital twin technology — all without requiring a backend server.

---

## Features

**Real-Time IoT Simulation**
Simulates ESP32 sensor nodes streaming temperature, humidity, vibration, and current data in JSON format, including MPU6050-style accelerometer and gyroscope readings.

**Edge AI Anomaly Detection**
Detects faults in real time using multi-parameter threshold analysis with dynamic confidence scoring and color-coded visual alerts.

**Federated Learning Network**
Simulates a multi-node distributed training environment where only model updates are shared between nodes, preserving data privacy while aggregating a global model.

**Blockchain Audit Logging**
Logs system events to a simulated Proof of Authority (PoA) blockchain with immutable records, real-time block generation, and cryptographic hash simulation.

**Digital Twin & Predictive Analytics**
Models virtual equipment components (motor, bearing, temperature control), forecasts degradation over a 12-hour window, and schedules proactive maintenance alerts.

**Interactive Dashboard**
Responsive, real-time visualizations built with Chart.js, CSS Grid, and a glassmorphism UI — compatible with desktop, tablet, and mobile devices.

---

## Prerequisites

- A modern web browser (see [Browser Compatibility](#browser-compatibility))
- [Visual Studio Code](https://code.visualstudio.com/) *(recommended)*
- [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) VS Code extension

---

## Installation

1. Clone or download the repository.
2. Open the project folder in VS Code.
3. Install the Live Server extension if not already present.
4. Right-click `index.html` and select **Open with Live Server**.
5. The dashboard will open in your default browser.

---

## Project Structure

```
iot-predictive-maintenance/
├── index.html              # Application entry point
├── styles/
│   └── main.css            # Global styles and CSS variables
├── scripts/
│   └── app.js              # Core application logic
├── assets/                 # Static assets (images, icons)
└── README.md
```

---

## Usage

**Starting the system**
Click **Start Simulation** to begin real-time data streaming. Sensor readings, chart updates, federated learning activity, and blockchain events will begin immediately.

**Injecting anomalies**
Click **Inject Anomaly** to simulate an equipment fault. The anomaly detection engine will trigger alerts, digital twin health scores will degrade, and the event will be recorded on the blockchain.

**Keyboard shortcuts**

| Shortcut | Action |
|----------|--------|
| `Ctrl + S` | Start / Stop simulation |
| `Ctrl + A` | Inject anomaly |

---

## Configuration

**Sensor baseline values** — edit `generateSensorData()` in `scripts/app.js`:

```javascript
const baseTemp      = 28;    // Degrees Celsius
const baseHumidity  = 65;    // Percentage
const baseCurrent   = 0.15;  // Amperes
```

**Anomaly thresholds** — edit `detectAnomalies()` in `scripts/app.js`:

```javascript
if (data.temperature > 40 || data.temperature < 15) { /* temperature fault */ }
if (data.vibrationMagnitude > 0.1)                  { /* vibration fault */   }
```

**UI theme** — edit CSS variables in `styles/main.css`:

```css
:root {
    --primary-color:  #4ecdc4;
    --warning-color:  #ffa726;
    --critical-color: #ff5252;
}
```

---

## Technical Reference

**Technologies**

| Layer | Technology |
|-------|------------|
| Markup | HTML5 |
| Styling | CSS3 — Grid, Flexbox, CSS Variables, Keyframe Animations |
| Logic | JavaScript ES6+ (modular, event-driven) |
| Charts | Chart.js 3.9.1 |

**IoT Data Format**

```json
{
  "deviceId": "sim_esp32_01",
  "timestamp": 1690000000000,
  "temperature": 29.5,
  "humidity": 67.8,
  "accel": { "x": 0.02, "y": -0.05, "z": 0.88 },
  "gyro":  { "x": 0.18, "y": 0.16,  "z": -0.10 },
  "current": 0.12,
  "vibrationMagnitude": 0.094
}
```

---

## Browser Compatibility

| Browser | Minimum Version |
|---------|----------------|
| Chrome  | 80+ |
| Firefox | 75+ |
| Safari  | 13+ |
| Edge    | 80+ |

---

## Deployment

**Local development**
Use VS Code Live Server. No build step or server-side dependencies are required.

**Static web hosting**
Upload all project files to any static hosting provider. The following platforms are compatible out of the box: GitHub Pages, Netlify, Vercel.

**Docker**

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
```

---

## Roadmap

- [ ] Real ESP32 hardware integration
- [ ] MongoDB time-series data persistence
- [ ] Advanced ML inference with TensorFlow.js
- [ ] Production blockchain integration
- [ ] Multi-tenant architecture
- [ ] Companion mobile application
- [ ] Role-based access control

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes with clear, descriptive messages.
4. Open a pull request describing the change and its motivation.

Please ensure all changes are tested across supported browsers before submitting.

---

## License

This project is released under the [MIT License](LICENSE).

---

*Built for Industry 4.0 and the Industrial Internet of Things.*
