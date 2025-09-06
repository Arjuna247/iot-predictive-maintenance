# 🏭 Industrial IoT Predictive Maintenance System

A comprehensive Edge AI-powered predictive maintenance dashboard featuring real-time IoT data simulation, anomaly detection, federated learning, blockchain security, and digital twin technology.

## 🚀 Features

### 📡 **Real-time IoT Simulation**
- Simulates ESP32-based sensor data (Temperature, Humidity, Vibration, Current)
- MPU6050-style accelerometer and gyroscope data
- JSON format data streaming with realistic patterns

### 🤖 **Edge AI Anomaly Detection**
- Real-time fault detection algorithms
- Multi-parameter threshold analysis
- Dynamic confidence scoring
- Visual alert system with color-coded indicators

### 🔗 **Federated Learning Network**
- Multi-node ESP32 simulation
- Distributed model training
- Global model accuracy aggregation
- Privacy-preserving learning (only model updates shared)

### ⛓️ **Blockchain Security**
- Private Proof of Authority (PoA) network simulation
- Immutable logging of system events
- Real-time block generation
- Cryptographic hash simulation

### 🔮 **Digital Twin & Predictive Analytics**
- Virtual equipment modeling
- Component health prediction (Motor, Bearing, Temperature Control)
- 12-hour degradation forecasting
- Proactive maintenance scheduling

### 📊 **Interactive Dashboard**
- Real-time charts and visualizations
- Responsive design for all devices
- Live data streaming with Chart.js
- Modern glassmorphism UI design

## 🛠️ Installation & Setup

### Prerequisites
- Web browser (Chrome, Firefox, Safari, Edge)
- VS Code (recommended)
- Live Server extension for VS Code

### Quick Start

1. **Clone or download** the project files
2. **Open in VS Code**
3. **Install Live Server extension** (if not already installed)
4. **Right-click on `index.html`** → "Open with Live Server"
5. **Start simulation** and begin monitoring!

### Project Structure
```
iot-predictive-maintenance/
│
├── index.html              # Main HTML file
├── styles/
│   └── main.css            # All CSS styles
├── scripts/
│   └── app.js              # JavaScript functionality
├── assets/                 # Images and other assets
└── README.md              # This file
```

## 🎮 Usage

### Starting the System
1. Click **"Start Simulation"** to begin real-time data streaming
2. Watch the dashboard come alive with sensor data, charts, and analytics
3. Monitor the federated learning network as nodes update their models
4. Observe blockchain blocks being added as events occur

### Testing Anomalies
1. Click **"Inject Anomaly"** to simulate equipment failure
2. Watch the AI detection system respond with alerts
3. See how the digital twin health scores degrade
4. Notice new blockchain blocks recording the anomaly events

### Keyboard Shortcuts
- **Ctrl + S**: Start/Stop simulation
- **Ctrl + A**: Inject anomaly

## 🔧 Customization

### Sensor Data Configuration
Modify the `generateSensorData()` function in `scripts/app.js`:
```javascript
const baseTemp = 28;        // Base temperature
const baseHumidity = 65;    // Base humidity
const baseCurrent = 0.15;   // Base current
```

### Anomaly Thresholds
Adjust detection thresholds in `detectAnomalies()` function:
```javascript
if (data.temperature > 40 || data.temperature < 15) {
    // Temperature anomaly threshold
}
if (data.vibrationMagnitude > 0.1) {
    // Vibration anomaly threshold
}
```

### UI Styling
Customize colors and styles in `styles/main.css`:
```css
:root {
    --primary-color: #4ecdc4;
    --warning-color: #ffa726;
    --critical-color: #ff5252;
}
```

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- 🖥️ Desktop computers
- 💻 Laptops
- 📱 Tablets
- 📱 Mobile phones

## 🌐 Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## 🚀 Deployment Options

### Local Development
- Use VS Code Live Server for instant development
- No build process required - pure HTML/CSS/JS

### Web Hosting
- Upload files to any web hosting service
- Works with GitHub Pages, Netlify, Vercel, etc.
- No server-side requirements

### Docker (Optional)
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
```

## 🔍 Technical Details

### Technologies Used
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js 3.9.1
- **Styling**: CSS Grid, Flexbox, CSS Variables
- **Animation**: CSS Keyframes, Transitions
- **Architecture**: Modular JavaScript, Event-driven

### Data Format
The system uses JSON format for IoT data:
```json
{
  "deviceId": "sim_esp32_01",
  "timestamp": 1690000000000,
  "temperature": 29.5,
  "humidity": 67.8,
  "accel": {"x": 0.02, "y": -0.05, "z": 0.88},
  "gyro": {"x": 0.18, "y": 0.16, "z": -0.10},
  "current": 0.12,
  "vibrationMagnitude": 0.094
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the browser console for error messages
- Ensure all files are properly linked

## 🎯 Future Enhancements

- [ ] Real ESP32 hardware integration
- [ ] MongoDB data persistence
- [ ] Advanced ML models with TensorFlow.js
- [ ] Real blockchain integration
- [ ] Multi-tenant support
- [ ] Advanced security features
- [ ] Mobile app companion

---

**Built with ❤️ for Industry 4.0 and IoT innovation**
