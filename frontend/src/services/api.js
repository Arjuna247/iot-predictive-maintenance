import axios from 'axios';
import { io } from 'socket.io-client';

const BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

// ── REST helpers ──────────────────────────────────────────────────────────────

export const fetchSensorData = (params = {}) =>
  axios.get(`${BASE}/api/data`, { params }).then(r => r.data);

export const fetchNodes = () =>
  axios.get(`${BASE}/api/nodes`).then(r => r.data);

export const fetchAudit = (params = {}) =>
  axios.get(`${BASE}/api/audit`, { params }).then(r => r.data);

export const fetchFLStatus = (params = {}) =>
  axios.get(`${BASE}/api/fl/status`, { params }).then(r => r.data);

export const tamperRecord = (id, body) =>
  axios.post(`${BASE}/api/tamper/${id}`, body).then(r => r.data);

// ── WebSocket ─────────────────────────────────────────────────────────────────

let _socket = null;

export const getSocket = () => {
  if (!_socket) {
    _socket = io(BASE, { transports: ['websocket', 'polling'] });
  }
  return _socket;
};
