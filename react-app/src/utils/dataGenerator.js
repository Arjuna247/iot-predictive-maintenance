// Data generation utilities for IoT simulation

export const generateSensorData = (anomalyMode = false) => {
  const baseTemp = 28;
  const baseHumidity = 65;
  const baseCurrent = 0.15;

  const tempNoise = (Math.random() - 0.5) * 4;
  const humidityNoise = (Math.random() - 0.5) * 10;
  const currentNoise = (Math.random() - 0.5) * 0.05;

  let tempFactor = 1;
  let vibrationFactor = 1;
  let currentFactor = 1;

  if (anomalyMode) {
    tempFactor = 1.5 + Math.random() * 0.5;
    vibrationFactor = 3 + Math.random() * 2;
    currentFactor = 2 + Math.random() * 0.5;
  }

  const temperature = (baseTemp + tempNoise) * tempFactor;
  const humidity = Math.max(0, Math.min(100, baseHumidity + humidityNoise));
  const current = Math.max(0, (baseCurrent + currentNoise) * currentFactor);

  const accelX = (Math.random() - 0.5) * 0.1 * vibrationFactor;
  const accelY = (Math.random() - 0.5) * 0.1 * vibrationFactor;
  const accelZ = 0.98 + (Math.random() - 0.5) * 0.1 * vibrationFactor;

  const vibrationMagnitude = Math.sqrt(accelX ** 2 + accelY ** 2 + (accelZ - 0.98) ** 2);

  return {
    deviceId: "sim_esp32_01",
    timestamp: Date.now(),
    temperature: parseFloat(temperature.toFixed(1)),
    humidity: parseFloat(humidity.toFixed(1)),
    vibrationMagnitude: parseFloat(vibrationMagnitude.toFixed(4)),
    current: parseFloat(current.toFixed(3)),
  };
};

export const detectAnomalies = (data) => {
  let anomalyScore = 0;
  const anomalies = [];

  if (data.temperature > 40 || data.temperature < 15) {
    anomalyScore += 0.4;
    anomalies.push(`Temperature: ${data.temperature.toFixed(1)}°C`);
  }

  if (data.vibrationMagnitude > 0.1) {
    anomalyScore += 0.5;
    anomalies.push(`High vibration: ${data.vibrationMagnitude.toFixed(3)}g`);
  }

  if (data.current > 0.3) {
    anomalyScore += 0.3;
    anomalies.push(`High current: ${data.current.toFixed(3)}A`);
  }

  if (data.humidity < 30 || data.humidity > 85) {
    anomalyScore += 0.2;
    anomalies.push(`Humidity: ${data.humidity.toFixed(1)}%`);
  }

  return {
    score: Math.min(anomalyScore, 1),
    anomalies,
  };
};

export const generateRandomHash = () => {
  const chars = '0123456789abcdef';
  let hash = '0x';
  for (let i = 0; i < 8; i++) {
    hash += chars[Math.floor(Math.random() * chars.length)];
  }
  return hash + '...';
};
