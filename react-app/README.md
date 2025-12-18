# React Dashboard - Industrial IoT Predictive Maintenance

Modern React implementation of the Industrial IoT Predictive Maintenance dashboard with real-time data visualization, anomaly detection, and advanced analytics.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at [http://localhost:5173/](http://localhost:5173/)

## 📦 Build Commands

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🏗️ Project Structure

```
react-app/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx       # Main dashboard component
│   │   └── Dashboard.css       # Dashboard styles
│   ├── utils/
│   │   └── dataGenerator.js    # Sensor data simulation utilities
│   ├── App.jsx                 # Root application component
│   ├── App.css                 # Application-level styles
│   ├── index.css               # Global styles
│   └── main.jsx                # Application entry point
├── public/                     # Static assets
├── index.html                  # HTML template
├── package.json                # Dependencies and scripts
└── vite.config.js              # Vite configuration
```

## 🎨 Features

### Core Components

#### Dashboard Component
The main `Dashboard.jsx` component includes:
- **Real-time Sensor Monitoring**: Live temperature, humidity, vibration, and current readings
- **Anomaly Detection**: Multi-parameter threshold analysis with visual alerts
- **Federated Learning Visualization**: Network status and model accuracy tracking
- **Blockchain Ledger**: Immutable transaction log with cryptographic hashes
- **Digital Twin**: Equipment health monitoring and predictive analytics
- **Maintenance Scheduler**: Priority-based maintenance queue

### Data Utilities

#### dataGenerator.js
Provides realistic IoT data simulation:
- `generateSensorData(anomalyMode)` - Creates sensor readings with optional anomaly injection
- `detectAnomalies(data)` - Analyzes sensor data for anomalies
- `generateRandomHash()` - Creates blockchain-style hashes

## 🔧 Customization

### Sensor Thresholds

Edit thresholds in `src/utils/dataGenerator.js`:

```javascript
// Temperature anomaly detection
if (data.temperature > 40 || data.temperature < 15) {
  anomalyScore += 0.4;
  anomalies.push(`Temperature: ${data.temperature.toFixed(1)}°C`);
}

// Vibration anomaly detection
if (data.vibrationMagnitude > 0.1) {
  anomalyScore += 0.5;
  anomalies.push(`High vibration: ${data.vibrationMagnitude.toFixed(3)}g`);
}
```

### Styling

Customize the dashboard appearance in `src/components/Dashboard.css`:

- Grid layout: `.dashboard-grid`
- Card styles: `.card`
- Color scheme: Card headers, status indicators
- Animations: `alertPulse`, `slideIn`

### Chart Configuration

Modify Chart.js settings in `src/components/Dashboard.jsx`:

```javascript
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  // ... customize as needed
};
```

## 📊 State Management

The Dashboard component uses React hooks for state management:

```javascript
const [simulationRunning, setSimulationRunning] = useState(false);
const [sensorData, setSensorData] = useState({ /* sensor values */ });
const [anomalyResult, setAnomalyResult] = useState({ score: 0, anomalies: [] });
const [federatedNodes, setFederatedNodes] = useState([/* nodes */]);
const [blockchainBlocks, setBlockchainBlocks] = useState([/* blocks */]);
const [healthScores, setHealthScores] = useState({ /* health data */ });
const [maintenanceQueue, setMaintenanceQueue] = useState([/* tasks */]);
```

## 🎯 Component Lifecycle

### Simulation Flow

1. **Start Simulation** → Sets `simulationRunning: true`
2. **useEffect Hook** → Creates interval for data updates (2 seconds)
3. **Data Generation** → `generateSensorData()` creates new readings
4. **Anomaly Detection** → `detectAnomalies()` analyzes data
5. **State Updates** → React re-renders with new data
6. **Chart Updates** → Chart.js automatically updates visualizations
7. **Stop Simulation** → Clears interval and resets state

### Anomaly Injection

```javascript
const injectAnomaly = () => {
  const anomalyData = generateSensorData(true);
  setSensorData(anomalyData);
  const result = detectAnomalies(anomalyData);
  setAnomalyResult(result);
  // Triggers alerts and updates health scores
};
```

## 🛠️ Development Tips

### Hot Module Replacement (HMR)

Vite provides instant updates during development:
- Edit `.jsx` files → UI updates instantly
- Edit `.css` files → Styles update without refresh
- State is preserved across most updates

### Debugging

```javascript
// Add console logs in components
useEffect(() => {
  console.log('Sensor data updated:', sensorData);
}, [sensorData]);

// Use React DevTools browser extension for state inspection
```

### Performance Optimization

```javascript
// Memoize expensive calculations
import { useMemo } from 'react';

const processedData = useMemo(() => {
  return heavyComputation(sensorData);
}, [sensorData]);
```

## 📦 Dependencies

### Production Dependencies
- `react` (^18.3.1) - UI framework
- `react-dom` (^18.3.1) - React DOM renderer
- `chart.js` (^4.4.7) - Chart library
- `react-chartjs-2` (^5.3.0) - React wrapper for Chart.js
- `lucide-react` (^0.468.0) - Icon library

### Development Dependencies
- `vite` (^6.0.5) - Build tool
- `@vitejs/plugin-react` (^4.3.4) - React plugin for Vite
- ESLint for code quality

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Deploy to Static Hosting

The built app is static and can be deployed to:

#### Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

#### Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

#### GitHub Pages
```bash
# Add to package.json
"homepage": "https://yourusername.github.io/repo-name",

# Install gh-pages
npm install --save-dev gh-pages

# Add deploy script
"deploy": "npm run build && gh-pages -d dist"

# Deploy
npm run deploy
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
# Build and run
docker build -t iot-dashboard .
docker run -p 8080:80 iot-dashboard
```

## 🔗 Integration with Python Backend

To connect with the Python backend services:

### 1. Update API Endpoints

Edit `src/components/Dashboard.jsx` to fetch from Flask server:

```javascript
// Example: Fetch real sensor data
useEffect(() => {
  const fetchSensorData = async () => {
    try {
      const response = await fetch('http://localhost:5000/data/latest');
      const data = await response.json();
      setSensorData(data);
    } catch (error) {
      console.error('Failed to fetch sensor data:', error);
    }
  };

  const interval = setInterval(fetchSensorData, 2000);
  return () => clearInterval(interval);
}, []);
```

### 2. Enable CORS

Ensure Flask server has CORS enabled (already configured in `../iot/esp32_data_server.py`):

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

### 3. Run Both Servers

```bash
# Terminal 1: Start Python backend
cd iot
python esp32_data_server.py

# Terminal 2: Start React frontend
cd react-app
npm run dev
```

## 📱 Responsive Design

The dashboard is fully responsive with breakpoints:

- **Desktop** (1024px+): 3-column grid layout
- **Tablet** (768px-1024px): 2-column grid layout
- **Mobile** (<768px): Single column layout

Customize breakpoints in `src/components/Dashboard.css`:

```css
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
```

## 🎨 UI Design

### Glassmorphism Effects

```css
.card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### Color Scheme

- **Primary**: `#4ecdc4` (Teal)
- **Warning**: `#ffa726` (Orange)
- **Critical**: `#ff5252` (Red)
- **Background**: Dark gradient

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly: `npm run dev`
5. Lint your code: `npm run lint`
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📄 License

This project is part of the Industrial IoT Predictive Maintenance System and follows the same license as the parent project.

---

**Built with React + Vite for modern web development** ⚛️
