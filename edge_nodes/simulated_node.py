"""
Node 2 – Simulated Node
========================
Generates realistic synthetic sensor data with gradual machine-degradation
patterns and participates in peer-to-peer Federated Learning with Node 1.

The simulation has a distinct operating baseline from Node 1 so the two
nodes bring genuinely different distribution knowledge to FedAvg.

Environment variables
---------------------
  BACKEND_URL          (default: http://localhost:5000)
  PEER_FL_URL          (default: http://localhost:5001)
  FL_LISTEN_PORT       (default: 5002)
  FL_EXCHANGE_INTERVAL (default: 30)
  SEND_INTERVAL        (default: 2.0)
  NODE_ID              (default: node_simulated)
  MODEL_PATH           (default: models/node_simulated.pkl)
  SIM_BASE_TEMP        (default: 38.0)
  SIM_BASE_VIB         (default: 0.9)
  SIM_BASE_CUR         (default: 5.8)
"""
import math
import os
import random
import time

import requests

from hashing_utils import compute_payload_hash, get_utc_timestamp
from ml_model import AnomalyDetector
from fl_peer import FLPeer

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL          = os.environ.get('BACKEND_URL',          'http://localhost:5000')
PEER_FL_URL          = os.environ.get('PEER_FL_URL',          'http://localhost:5001')
FL_LISTEN_PORT       = int(os.environ.get('FL_LISTEN_PORT',   '5002'))
FL_EXCHANGE_INTERVAL = int(os.environ.get('FL_EXCHANGE_INTERVAL', '30'))
SEND_INTERVAL        = float(os.environ.get('SEND_INTERVAL',  '2.0'))
NODE_ID              = os.environ.get('NODE_ID',              'node_simulated')
MODEL_PATH           = os.environ.get('MODEL_PATH',           f'models/{NODE_ID}.pkl')

SIM_BASE_TEMP = float(os.environ.get('SIM_BASE_TEMP', '38.0'))
SIM_BASE_VIB  = float(os.environ.get('SIM_BASE_VIB',  '0.9'))
SIM_BASE_CUR  = float(os.environ.get('SIM_BASE_CUR',  '5.8'))


class SimulatedNode:
    def __init__(self):
        self.node_id = NODE_ID
        self._t      = 0

        # Operating baseline (different from physical node)
        self._base_temp = SIM_BASE_TEMP
        self._base_vib  = SIM_BASE_VIB
        self._base_cur  = SIM_BASE_CUR

        # Degradation state
        self._degrading       = False
        self._degrad_rate     = 0.0
        self._degrad_start_t  = 0

        # ML model
        os.makedirs('models', exist_ok=True)
        if os.path.exists(MODEL_PATH):
            self.model = AnomalyDetector.load(MODEL_PATH)
            print(f"  Loaded model from {MODEL_PATH}")
        else:
            self.model = AnomalyDetector(window_size=50, z_threshold=3.0)
            print("  Initialised fresh anomaly detector")

        # FL peer (offset scheduler so the two nodes don't collide)
        self.fl_peer = FLPeer(
            node_id=self.node_id,
            peer_url=PEER_FL_URL,
            backend_url=BACKEND_URL,
            listen_port=FL_LISTEN_PORT,
            exchange_interval=FL_EXCHANGE_INTERVAL,
        )
        self.fl_peer.model = self.model

        print(f"\n{'='*55}")
        print(f"  Node ID  : {self.node_id}")
        print(f"  Mode     : synthetic simulation")
        print(f"  Backend  : {BACKEND_URL}")
        print(f"  FL peer  : {PEER_FL_URL}")
        print(f"{'='*55}\n")

    # ── Data generation ───────────────────────────────────────────────────────

    def _toggle_degradation(self):
        if self._degrading:
            self._degrading   = False
            self._degrad_rate = 0.0
            print('\n  ✅  Machine returned to normal operation')
        else:
            self._degrading      = True
            self._degrad_rate    = random.uniform(0.015, 0.04)
            self._degrad_start_t = self._t
            print(f'\n  ⚠️   Machine degradation started (rate={self._degrad_rate:.4f}/step)')

    def _generate(self) -> dict:
        self._t += 1
        t = self._t

        # Toggle degradation every ~500 readings
        if t % 500 == 0:
            self._toggle_degradation()

        degrad_steps = (t - self._degrad_start_t) if self._degrading else 0
        d = self._degrad_rate * degrad_steps

        temp = (self._base_temp
                + d * 8.0
                + 4.0 * math.sin(t / 25)
                + 2.0 * math.sin(t / 7 + 0.5)
                + random.gauss(0, 0.4))

        vib  = (self._base_vib
                + d * 1.5
                + 0.2 * math.sin(t / 12)
                + 0.1 * math.sin(t / 4 + 1)
                + random.gauss(0, 0.04))

        cur  = (self._base_cur
                + d * 2.5
                + 0.8 * math.sin(t / 18 + 2)
                + random.gauss(0, 0.15))

        # Low-probability random spike
        if random.random() < 0.005:
            spike = random.choice(['temp', 'vib', 'cur'])
            if spike == 'temp': temp += random.uniform(25, 45)
            elif spike == 'vib': vib += random.uniform(2, 5)
            else:                cur += random.uniform(6, 10)

        return {
            'temperature': round(temp, 2),
            'vibration':   round(max(vib, 0), 4),
            'current':     round(max(cur, 0), 2),
        }

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
                      f"{flag}  Block#{result.get('block_index','?')}")
            else:
                print(f"  Backend {resp.status_code}: {resp.text[:80]}")
        except requests.exceptions.ConnectionError:
            print(f"  [!] Cannot reach backend {BACKEND_URL}")
        except Exception as exc:
            print(f"  [!] Send error: {exc}")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        self.fl_peer.start_listener()
        time.sleep(0.5)
        # Offset by half the interval so Node 2 exchanges when Node 1 is idle
        self.fl_peer.start_exchange_scheduler(
            initial_delay=FL_EXCHANGE_INTERVAL / 2
        )

        print(f"🚀  {self.node_id} running — interval={SEND_INTERVAL}s\n")

        try:
            while True:
                reading = self._generate()
                self._send(reading)
                if self._t % 100 == 0:
                    self.model.save(MODEL_PATH)
                time.sleep(SEND_INTERVAL)
        except KeyboardInterrupt:
            print('\n  Shutting down simulated node …')
            self.model.save(MODEL_PATH)


if __name__ == '__main__':
    SimulatedNode().run()
