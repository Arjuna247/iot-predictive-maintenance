import { useState, useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Play, Pause, AlertTriangle, RefreshCw } from 'lucide-react';
import { generateSensorData, detectAnomalies, generateRandomHash } from '../utils/dataGenerator';
import { fetchLatestData } from '../services/api';
import './Dashboard.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function Dashboard() {
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [anomalyInjected, setAnomalyInjected] = useState(false);
  const [sensorData, setSensorData] = useState({
    temperature: 0,
    humidity: 0,
    vibrationMagnitude: 0,
    current: 0,
    deviceId: 'Waiting...'
  });
  const [anomalyResult, setAnomalyResult] = useState({ score: 0, anomalies: [] });
  const [sensorHistory, setSensorHistory] = useState([]);
  const [anomalyHistory, setAnomalyHistory] = useState([]);
  const [blockHeight, setBlockHeight] = useState(1247);
  const [blocks, setBlocks] = useState([
    { id: 1247, hash: '0x5f7a2b8c...', event: 'FL Update: Node_01 → Node_02', time: '2 mins ago' },
    { id: 1246, hash: '0x3e9d1f4a...', event: 'Anomaly Alert: ESP32_03', time: '5 mins ago' }
  ]);
  const [healthScores, setHealthScores] = useState({
    motor: 94,
    bearing: 78,
    temperature: 65,
    overall: 82
  });
  const [flAccuracies, setFlAccuracies] = useState({
    node1: 87,
    node2: 91,
    node3: 83,
    global: 89
  });
  const [flCountdown, setFlCountdown] = useState(45);

  // Simulation / Data Polling loop
  useEffect(() => {
    let interval;
    if (simulationRunning) {
      interval = setInterval(async () => {
        // Attempt to fetch real data
        const response = await fetchLatestData();

        let data;
        let result;

        if (response && response.count > 0) {
          // Use the first available device or a specific one
          const deviceKeys = Object.keys(response.data);
          const rawData = response.data[deviceKeys[0]]; // Pick first device

          // Map backend data to frontend format
          data = {
            deviceId: rawData.deviceId,
            timestamp: rawData.timestamp || Date.now(),
            temperature: rawData.Temperature || 0,
            humidity: rawData.Humidity || 0,
            vibrationMagnitude: rawData.Vibration || 0,
            current: rawData.Current || 0,
            // If backend sends anomaly flag, use it, otherwise detect locally
          };

          // Use backend anomaly flag if present, else use local detection
          if (rawData.Anomaly !== undefined) {
            const isAnomaly = rawData.Anomaly === 1;

            result = {
              score: isAnomaly ? 1 : 0,
              anomalies: isAnomaly ? ["🚨 ML Detected Anomaly"] : []
            };
          } else {
            result = {
              score: 0,
              anomalies: []
            };
          }

        } else {
          // Fallback to mock if API fails or no data (optional, or just wait)
          // For now, let's just wait effectively acting as "no data"
          // Or we could keep the mock as a fallback? 
          // The user asked to LINK it, so let's stick to trying to get real data.
          // If we fail, we just don't update.
          return;
        }

        setSensorData(data);
        setAnomalyResult(result);

        // Update histories
        const timeLabel = new Date().toLocaleTimeString();
        setSensorHistory(prev => {
          const newHistory = [...prev, { time: timeLabel, ...data }];
          return newHistory.slice(-20);
        });

        setAnomalyHistory(prev => {
          const newHistory = [...prev, { time: timeLabel, score: result.score }];
          return newHistory.slice(-20);
        });

        // Update health scores based on anomalies
        if (result.score > 0.5) {
          setHealthScores(prev => ({
            motor: Math.max(30, prev.motor - Math.random() * 3),
            bearing: Math.max(30, prev.bearing - Math.random() * 5),
            temperature: Math.max(30, prev.temperature - Math.random() * 4),
            overall: Math.max(30, prev.overall - Math.random() * 3)
          }));
        } else {
          setHealthScores(prev => ({
            motor: Math.max(30, prev.motor - Math.random() * 0.5),
            bearing: Math.max(30, prev.bearing - Math.random() * 0.8),
            temperature: Math.max(30, prev.temperature - Math.random() * 0.6),
            overall: Math.max(30, prev.overall - Math.random() * 0.5)
          }));
        }

        // Add blockchain blocks
        if (result.score > 0.3 || Math.random() < 0.1) {
          setBlockHeight(prev => prev + 1);
          setBlocks(prev => {
            const newBlock = {
              id: blockHeight + 1,
              hash: generateRandomHash(),
              event: result.score > 0.3 ? `Anomaly Alert: ${data.deviceId}` : `FL Update: ${data.deviceId}`,
              time: 'Just now'
            };
            return [newBlock, ...prev].slice(0, 3);
          });
        }

        // Auto-reset anomaly (only for UI state, doesn't affect backend)
        if (anomalyInjected && Math.random() < 0.1) {
          setAnomalyInjected(false);
        }
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [simulationRunning, anomalyInjected, blockHeight]);

  // FL countdown
  useEffect(() => {
    let interval;
    if (simulationRunning) {
      interval = setInterval(() => {
        setFlCountdown(prev => {
          if (prev <= 0) {
            // Update FL accuracies
            setFlAccuracies({
              node1: Math.max(75, Math.min(95, flAccuracies.node1 + (Math.random() - 0.4) * 2)),
              node2: Math.max(75, Math.min(95, flAccuracies.node2 + (Math.random() - 0.4) * 2)),
              node3: Math.max(75, Math.min(95, flAccuracies.node3 + (Math.random() - 0.4) * 2)),
              global: 0
            });
            setFlAccuracies(prev => ({
              ...prev,
              global: (prev.node1 + prev.node2 + prev.node3) / 3
            }));
            return 60 + Math.random() * 30;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [simulationRunning, flAccuracies]);

  const toggleSimulation = () => {
    setSimulationRunning(!simulationRunning);
  };

  const injectAnomaly = () => {
    if (simulationRunning) {
      setAnomalyInjected(true);
    }
  };

  // Chart data
  const sensorChartData = {
    labels: sensorHistory.map(d => d.time),
    datasets: [
      {
        label: 'Temperature',
        data: sensorHistory.map(d => d.temperature),
        borderColor: '#ff6b6b',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        tension: 0.4
      },
      {
        label: 'Vibration',
        data: sensorHistory.map(d => d.vibrationMagnitude * 100),
        borderColor: '#4ecdc4',
        backgroundColor: 'rgba(78, 205, 196, 0.1)',
        tension: 0.4
      }
    ]
  };

  const anomalyChartData = {
    labels: anomalyHistory.map(d => d.time),
    datasets: [
      {
        label: 'Anomaly Score',
        data: anomalyHistory.map(d => d.score),
        borderColor: '#ffa726',
        backgroundColor: 'rgba(255, 167, 38, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
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
  };

  const getHealthColor = (score) => {
    if (score >= 80) return '#4ecdc4';
    if (score >= 65) return '#66bb6a';
    if (score >= 50) return '#ffa726';
    return '#ff5252';
  };

  const getStatusClass = (score) => {
    if (score === 1) return 'status-critical';
    return 'status-normal';
  };

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {/* Sensor Card */}
        <div className="card">
          <h2>📡 Edge Node - {sensorData.deviceId}</h2>
          <div className="controls">
            <button onClick={toggleSimulation}>
              {simulationRunning ? <><Pause size={16} /> Stop Monitoring</> : <><Play size={16} /> Start Monitoring</>}
            </button>
            <button onClick={injectAnomaly} className="btn-danger">
              <AlertTriangle size={16} /> Inject Anomaly
            </button>
          </div>

          <div className="sensor-grid">
            <div className="sensor-value">
              <div className="label">Temperature</div>
              <div className="value">{sensorData.temperature.toFixed(1)}°C</div>
            </div>
            <div className="sensor-value">
              <div className="label">Humidity</div>
              <div className="value">{sensorData.humidity.toFixed(1)}%</div>
            </div>
            <div className="sensor-value">
              <div className="label">Vibration</div>
              <div className="value">{sensorData.vibrationMagnitude.toFixed(3)}g</div>
            </div>
            <div className="sensor-value">
              <div className="label">Current</div>
              <div className="value">{sensorData.current.toFixed(3)}A</div>
            </div>
          </div>

          <div className="chart-container">
            <Line data={sensorChartData} options={chartOptions} />
          </div>
        </div>

        {/* Anomaly Detection Card */}
        <div className="card">
          <h2>🤖 Edge AI Anomaly Detection</h2>
          <div style={{ marginBottom: '1rem' }}>
            <span className={`status-indicator ${getStatusClass(anomalyResult.score)}`}></span>
            <span>
              {anomalyResult.score > 0.7 ? 'Critical Anomaly Detected' :
                anomalyResult.score > 0.3 ? 'Warning: Anomaly Detected' :
                  'System Normal'}
            </span>
          </div>

          <div className="anomaly-alerts">
            {anomalyResult.anomalies.map((anomaly, idx) => (
              <div key={idx} className="alert show">
                ⚠️ {anomaly}
              </div>
            ))}
          </div>

          <div className="chart-container">
            <Line data={anomalyChartData} options={{ ...chartOptions, scales: { ...chartOptions.scales, y: { ...chartOptions.scales.y, min: 0, max: 1 } } }} />
          </div>

          <div style={{ marginTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>Confidence Level:</span>
              <span>{Math.round((1 - anomalyResult.score) * 100)}%</span>
            </div>
            <div className="accuracy-bar">
              <div className="accuracy-fill" style={{ width: `${(1 - anomalyResult.score) * 100}%` }}></div>
            </div>
          </div>
        </div>

        {/* Federated Learning Card */}
        <div className="card">
          <h2>🔗 Federated Learning Network</h2>
          {[
            { name: 'Node ESP32_01', accuracy: flAccuracies.node1, status: 'normal' },
            { name: 'Node ESP32_02', accuracy: flAccuracies.node2, status: 'normal' },
            { name: 'Node ESP32_03', accuracy: flAccuracies.node3, status: 'warning' }
          ].map((node, idx) => (
            <div key={idx} className="federated-node">
              <div className="node-status">
                <span>{node.name}</span>
                <span className={`status-indicator status-${node.status}`}></span>
              </div>
              <div>Accuracy: <span>{node.accuracy.toFixed(0)}%</span></div>
              <div className="accuracy-bar">
                <div className="accuracy-fill" style={{ width: `${node.accuracy}%` }}></div>
              </div>
            </div>
          ))}
          <div style={{ marginTop: '1rem', textAlign: 'center' }}>
            <div>Global Model Accuracy: <strong>{flAccuracies.global.toFixed(0)}%</strong></div>
            <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Next FL Round: <span>{flCountdown}s</span></div>
          </div>
        </div>

        {/* Blockchain Card */}
        <div className="card">
          <h2>⛓️ Blockchain Security</h2>
          <div style={{ marginBottom: '1rem' }}>
            <div>Network: <strong>Private PoA</strong></div>
            <div>Nodes: <strong>5 Active</strong></div>
            <div>Block Height: <strong>{blockHeight.toLocaleString()}</strong></div>
          </div>
          <div className="blockchain-blocks">
            {blocks.map((block) => (
              <div key={block.id} className="blockchain-block">
                <div>Block #{block.id}</div>
                <div className="block-hash">Hash: {block.hash}</div>
                <div>{block.event}</div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6 }}>{block.time}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Digital Twin Card */}
        <div className="card digital-twin">
          <h2>🔮 Digital Twin & Predictive Analytics</h2>
          <div className="twin-status">
            {[
              { name: 'Motor Health', score: healthScores.motor, expected: '2.3 days' },
              { name: 'Bearing Status', score: healthScores.bearing, expected: '12 hours' },
              { name: 'Temperature Control', score: healthScores.temperature, expected: '6 hours' },
              { name: 'Overall System', score: healthScores.overall, expected: '8 hours' }
            ].map((component, idx) => (
              <div key={idx} className="twin-component">
                <div>{component.name}</div>
                <div className="health-score" style={{ color: getHealthColor(component.score) }}>
                  {Math.round(component.score)}
                </div>
                <div style={{ fontSize: '0.8rem' }}>Expected: {component.expected}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Maintenance Card */}
        <div className="card">
          <h2>🔧 Maintenance Scheduler</h2>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>🔴 Critical</span>
              <span>2 items</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>🟡 Warning</span>
              <span>5 items</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>🟢 Scheduled</span>
              <span>12 items</span>
            </div>
          </div>
          <div className="maintenance-queue">
            <div className="maintenance-item critical">
              <div><strong>ESP32_03 Bearing Replacement</strong></div>
              <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Due: 6 hours</div>
            </div>
            <div className="maintenance-item warning">
              <div><strong>Temperature Sensor Calibration</strong></div>
              <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Due: 1 day</div>
            </div>
            <div className="maintenance-item scheduled">
              <div><strong>Routine Motor Inspection</strong></div>
              <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Due: 3 days</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
