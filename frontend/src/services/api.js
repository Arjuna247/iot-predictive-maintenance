import axios from 'axios';
import { io } from 'socket.io-client';

const BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

// ── REST helpers ──────────────────────────────────────────────────────────────

export const fetchSensorData = (params = {}) =>
  axios.get(`${BASE}/api/data`, { params }).then(r => r.data);

export const fetchNodes = () =>
  axios.get(`${BASE}/api/nodes`).then(r => {
    // Map _id to node_id for MongoDB aggregation results
    return (r.data || []).map(n => ({
      ...n,
      node_id: n.node_id || n._id
    }));
  });

export const fetchAudit = (params = {}) =>
  axios.get(`${BASE}/api/audit`, { params }).then(r => r.data);

export const fetchFLStatus = (params = {}) =>
  axios.get(`${BASE}/api/fl/status`, { params })
    .then(r => r.data)
    .catch(err => {
      console.warn('FL Status endpoint not available:', err.message);
      return []; // Return empty array if endpoint is commented out in backend
    });

export const tamperRecord = (id, body) =>
  axios.post(`${BASE}/api/tamper/${id}`, body)
    .then(r => r.data)
    .catch(err => {
      console.error('Tamper failed:', err.message);
      throw err;
    });

// ── WebSocket ─────────────────────────────────────────────────────────────────

let _socket = null;

export const getSocket = () => {
  if (!_socket) {
    _socket = io(BASE, { transports: ['websocket', 'polling'] });
  }
  return _socket;
};
