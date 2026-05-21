"""
Node 1 – Physical Gateway Node
================================
Proxies live data from an ESP32 (via serial OR Wi-Fi) to the backend API.
Falls back to **simulation mode** automatically when no serial port is given
or when pyserial is not installed.

Usage
-----
  python physical_node.py                      # full simulation (no ESP32)
  python physical_node.py --port COM3          # use real ESP32 on COM3
  python physical_node.py --port /dev/ttyUSB0 --baud 115200
  python physical_node.py --esp32-wifi         # accept live data over Wi-Fi (HTTP POST)

Environment variables
---------------------
  BACKEND_URL          (default: http://localhost:5000)
  PEER_FL_URL          (default: http://localhost:5002)
  FL_LISTEN_PORT       (default: 5001)
  FL_EXCHANGE_INTERVAL (default: 30)    seconds
  SEND_INTERVAL        (default: 2.0)   seconds between readings
  NODE_ID              (default: node_physical)
  MODEL_PATH           (default: models/node_physical.pkl)
  ESP32_WIFI_PORT      (default: 5005)  port for ESP32 Wi-Fi data endpoint

ESP32 Wi-Fi usage (--esp32-wifi)
---------------------------------
  POST JSON to  http://<PC_IP>:5005/esp32/data
  Body:  { "temperature": 45.2, "vibration": 1.05, "current": 6.8 }
  See claude_plan.md §1 for the full Arduino/PlatformIO sketch snippet.
"""
import argparse
import math
import os
import random
import sys
import threading
import time

import requests

from hashing_utils import compute_payload_hash, get_utc_timestamp
from ml_model import AnomalyDetector
from fl_peer import FLPeer

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL          = os.environ.get('BACKEND_URL',          'http://localhost:5000')
PEER_FL_URL          = os.environ.get('PEER_FL_URL',          'http://localhost:5002')
FL_LISTEN_PORT       = int(os.environ.get('FL_LISTEN_PORT',   '5001'))
FL_EXCHANGE_INTERVAL = int(os.environ.get('FL_EXCHANGE_INTERVAL', '30'))
SEND_INTERVAL        = float(os.environ.get('SEND_INTERVAL',  '2.0'))
NODE_ID              = os.environ.get('NODE_ID',              'node_physical')
MODEL_PATH           = os.environ.get('MODEL_PATH',           f'models/{NODE_ID}.pkl')
ESP32_WIFI_PORT      = int(os.environ.get('ESP32_WIFI_PORT',  '5005'))

# Try pyserial
try:
    import serial
    _SERIAL_OK = True
except ImportError:
    _SERIAL_OK = False


class PhysicalNode:
    def __init__(self, serial_port=None, baud_rate=115200, simulate=False, esp32_wifi=False):
        self.node_id      = NODE_ID
        self.serial_port  = serial_port
        self.baud_rate    = baud_rate
        self.simulate     = simulate or (not _SERIAL_OK) or (serial_port is None)
        self.ser          = None
        self._t           = 0

        # Wi-Fi (ESP32 HTTP POST) state
        self._esp32_wifi   = esp32_wifi
        self._wifi_lock    = threading.Lock()
        self._wifi_reading = None   # most-recent reading received over Wi-Fi

        # Simulation baseline (mimics a real machine)
        self._base_temp = 42.0
        self._base_vib  =  1.2
        self._base_cur  =  6.5

        # ML model
        os.makedirs('models', exist_ok=True)
        if os.path.exists(MODEL_PATH):
            self.model = AnomalyDetector.load(MODEL_PATH)
            print(f"  Loaded model from {MODEL_PATH}")
        else:
            self.model = AnomalyDetector(window_size=50, z_threshold=3.0)
            print("  Initialised fresh anomaly detector")

        # FL peer
        self.fl_peer = FLPeer(
            node_id=self.node_id,
            peer_url=PEER_FL_URL,
            backend_url=BACKEND_URL,
            listen_port=FL_LISTEN_PORT,
            exchange_interval=FL_EXCHANGE_INTERVAL,
        )
        self.fl_peer.model = self.model

        if esp32_wifi:
            mode = f'wifi  (listening on 0.0.0.0:{ESP32_WIFI_PORT})'
        elif not self.simulate:
            mode = f'serial:{serial_port}'
        else:
            mode = 'simulation'

        print(f"\n{'='*55}")
        print(f"  Node ID  : {self.node_id}")
        print(f"  Mode     : {mode}")
        print(f"  Backend  : {BACKEND_URL}")
        print(f"  FL peer  : {PEER_FL_URL}")
        print(f"{'='*55}\n")

    # ── Wi-Fi Listener (ESP32 HTTP POST) ──────────────────────────────────────

    def _start_wifi_listener(self):
        """Start a minimal Flask server on a background daemon thread.

        The ESP32 should POST JSON to:
            http://<HOST_IP>:{ESP32_WIFI_PORT}/esp32/data

        Payload:
            { "temperature": 45.2, "vibration": 1.05, "current": 6.8 }

        A GET /health endpoint is also available for connectivity checks.
        """
        from flask import Flask as _WifiFlask, request as _wifi_req, jsonify as _wifi_json
        import logging

        app = _WifiFlask(__name__ + '_wifi')

        # Silence Werkzeug per-request logs; they clutter the node's output
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

        node_ref = self   # closure reference

        @app.route('/esp32/data', methods=['POST'])
        def receive_esp32():
            data = _wifi_req.get_json(force=True, silent=True)
            if not data:
                return _wifi_json({'error': 'Expected a JSON body'}), 400
            try:
                reading = {
                    'temperature': float(data.get('temperature', 0)),
                    'vibration':   float(data.get('vibration',   0)),
                    'current':     float(data.get('current',     0)),
                }
            except (TypeError, ValueError) as exc:
                return _wifi_json({'error': str(exc)}), 400

            with node_ref._wifi_lock:
                node_ref._wifi_reading = reading

            print(f"  📡 ESP32→Wi-Fi  "
                  f"T:{reading['temperature']}°C  "
                  f"V:{reading['vibration']}g  "
                  f"I:{reading['current']}A")
            return _wifi_json({'status': 'ok', 'node_id': node_ref.node_id}), 200

        @app.route('/health', methods=['GET'])
        def health():
            return _wifi_json({'status': 'up', 'node_id': node_ref.node_id}), 200

        t = threading.Thread(
            target=lambda: app.run(
                host='0.0.0.0',
                port=ESP32_WIFI_PORT,
                debug=False,
                use_reloader=False,
            ),
            daemon=True,
            name='esp32-wifi-listener',
        )
        t.start()
        print(f"  📡 ESP32 Wi-Fi listener → http://0.0.0.0:{ESP32_WIFI_PORT}/esp32/data")
        print(f"     POST  {{ \"temperature\": 45.2, \"vibration\": 1.05, \"current\": 6.8 }}")
        print(f"     GET   http://0.0.0.0:{ESP32_WIFI_PORT}/health   (connectivity check)")

    # ── Serial ────────────────────────────────────────────────────────────────

    def _connect_serial(self) -> bool:
        if not _SERIAL_OK:
            return False
        try:
            import serial as _serial
            self.ser = _serial.Serial(self.serial_port, self.baud_rate, timeout=2)
            time.sleep(2)
            print(f"  Connected to ESP32 on {self.serial_port}")
            return True
        except Exception as exc:
            print(f"  Serial connection failed ({exc}), falling back to simulation.")
            self.simulate = True
            return False

    def _read_serial(self):
        try:
            line = self.ser.readline().decode('utf-8').strip()
            if line.startswith('{'):
                import json
                d = json.loads(line)
                return {
                    'temperature': float(d.get('temp', d.get('temperature', 0))),
                    'vibration':   float(d.get('vib',  d.get('vibration', 0))),
                    'current':     float(d.get('cur',  d.get('current', 0))),
                }
        except Exception:
            pass
        return None

    # ── Simulation ────────────────────────────────────────────────────────────

    def _simulate(self) -> dict:
        self._t += 1
        t = self._t

        temp = (self._base_temp
                + 3.0  * math.sin(t / 20)
                + random.gauss(0, 0.5))
        vib  = (self._base_vib
                + 0.3  * math.sin(t / 10 + 1)
                + random.gauss(0, 0.05))
        cur  = (self._base_cur
                + 1.0  * math.sin(t / 15 + 2)
                + random.gauss(0, 0.2))

        # Inject occasional anomaly spike
        if t % 200 == 0:
            atype = random.choice(['temp', 'vib', 'cur'])
            if atype == 'temp': temp += random.uniform(30, 50)
            elif atype == 'vib': vib += random.uniform(3, 6)
            else:                cur += random.uniform(8, 12)

        return {
            'temperature': round(temp, 2),
            'vibration':   round(max(vib, 0), 4),
            'current':     round(max(cur, 0), 2),
        }

    def _get_reading(self) -> dict:
        # Priority 1 – live ESP32 data received over Wi-Fi
        if self._esp32_wifi:
            with self._wifi_lock:
                r = self._wifi_reading
                self._wifi_reading = None   # consume; next tick will get next POST
            if r:
                return r

        # Priority 2 – serial (physical cable)
        if not self.simulate and self.ser:
            r = self._read_serial()
            if r:
                return r

        # Priority 3 – synthetic simulation fallback
        return self._simulate()

    # ── Send ──────────────────────────────────────────────────────────────────

    def _send(self, reading: dict):
        ts = get_utc_timestamp()
        ph = compute_payload_hash(
            self.node_id,
            reading['temperature'],
            reading['vibration'],
            reading['current'],
            ts,
        )

        self.model.update(reading['temperature'], reading['vibration'], reading['current'])
        is_anom, reason, _ = self.model.predict(
            reading['temperature'], reading['vibration'], reading['current']
        )

        payload = {
            'device_id':      self.node_id,
            'temperature':    reading['temperature'],
            'ax':             reading['vibration'],
            'ay':             0,
            'az':             0,
            'current_voltage': reading['current'],
            'humidity':       50.0, # dummy value
            'timestamp':      ts,
        }

        try:
            resp = requests.post(f'{BACKEND_URL}/sensor-data', json=payload, timeout=5)
            if resp.status_code == 201:
                result = resp.json()
                flag   = '🚨 ANOMALY' if is_anom else '✅ OK'
                print(f"[{self.node_id}] {ts} | "
                      f"T:{reading['temperature']:5.1f}°C  "
                      f"V:{reading['vibration']:.4f}g  "
                      f"I:{reading['current']:5.2f}A | "
                      f"{flag}  Block#{result.get('block_index', '?')}")
            else:
                print(f"  Backend {resp.status_code}: {resp.text[:80]}")
        except requests.exceptions.ConnectionError:
            print(f"  [!] Cannot reach backend {BACKEND_URL}")
        except Exception as exc:
            print(f"  [!] Send error: {exc}")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        # Start Wi-Fi listener first so the ESP32 can connect immediately
        if self._esp32_wifi:
            self._start_wifi_listener()

        self.fl_peer.start_listener()
        time.sleep(0.5)
        self.fl_peer.start_exchange_scheduler()

        if not self.simulate and self.serial_port:
            self._connect_serial()

        print(f"🚀  {self.node_id} running — interval={SEND_INTERVAL}s\n")

        try:
            while True:
                reading = self._get_reading()
                self._send(reading)
                if self._t % 100 == 0:
                    self.model.save(MODEL_PATH)
                time.sleep(SEND_INTERVAL)
        except KeyboardInterrupt:
            print('\n  Shutting down physical node …')
            self.model.save(MODEL_PATH)
            if self.ser:
                self.ser.close()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='IoT Physical Gateway Node')
    p.add_argument('--port',       default=None,
                   help='Serial port (COM3, /dev/ttyUSB0, …)')
    p.add_argument('--baud',       type=int, default=115200,
                   help='Serial baud rate (default: 115200)')
    p.add_argument('--simulate',   action='store_true',
                   help='Force simulation mode even if a port is specified')
    p.add_argument('--esp32-wifi', action='store_true', dest='esp32_wifi',
                   help=f'Accept live sensor data from ESP32 over Wi-Fi '
                        f'(HTTP POST on port {ESP32_WIFI_PORT}). '
                        f'Falls back to simulation when no POST arrives.')
    args = p.parse_args()

    PhysicalNode(
        serial_port=args.port,
        baud_rate=args.baud,
        # Force simulation when neither serial port nor Wi-Fi mode is given
        simulate=args.simulate or (args.port is None and not args.esp32_wifi),
        esp32_wifi=args.esp32_wifi,
    ).run()


if __name__ == '__main__':
    main()
