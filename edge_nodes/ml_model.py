"""
Local anomaly-detection model for edge nodes.

Design
------
Instead of a black-box sklearn estimator (which is hard to merge via FedAvg),
we maintain a lightweight *statistical model* whose "weights" are:
    [mean_temp, std_temp, mean_vib, std_vib, mean_cur, std_cur, z_threshold, n_samples]

Anomaly = any metric's z-score > z_threshold.

FedAvg = sample-count-weighted average of all numeric weight components.
This gives a clean, serialisable, mergeable representation that is perfect
for peer-to-peer Federated Learning without a central aggregator.
"""
import json
import hashlib
import pickle
import os
from collections import deque

import numpy as np


class AnomalyDetector:
    def __init__(self, window_size: int = 50, z_threshold: float = 3.0):
        self.window_size = window_size

        # Sliding buffers (not exchanged over FL – local history only)
        self._temp_buf = deque(maxlen=window_size)
        self._vib_buf  = deque(maxlen=window_size)
        self._cur_buf  = deque(maxlen=window_size)

        # ── Model weights (exchanged via FL) ─────────────────────────────────
        self.weights: dict = {
            'mean_temp':   40.0,
            'std_temp':    10.0,
            'mean_vib':     1.0,
            'std_vib':      0.5,
            'mean_cur':     5.0,
            'std_cur':      2.0,
            'z_threshold':  z_threshold,
            'n_samples':    0,
        }

    # ── Online update ─────────────────────────────────────────────────────────

    def update(self, temperature: float, vibration: float, current: float) -> None:
        """Feed one new reading into the running statistics."""
        self._temp_buf.append(temperature)
        self._vib_buf.append(vibration)
        self._cur_buf.append(current)

        n = len(self._temp_buf)
        if n >= 10:
            self.weights['mean_temp'] = float(np.mean(self._temp_buf))
            self.weights['std_temp']  = max(float(np.std(self._temp_buf)),  0.01)
            self.weights['mean_vib']  = float(np.mean(self._vib_buf))
            self.weights['std_vib']   = max(float(np.std(self._vib_buf)),   0.001)
            self.weights['mean_cur']  = float(np.mean(self._cur_buf))
            self.weights['std_cur']   = max(float(np.std(self._cur_buf)),   0.01)
            self.weights['n_samples'] = int(self.weights['n_samples']) + 1

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict(self, temperature: float, vibration: float,
                current: float) -> tuple[bool, str, dict]:
        """
        Returns (is_anomaly, reason_string, z_scores_dict).
        """
        w   = self.weights
        thr = w['z_threshold']

        z_temp = abs(temperature - w['mean_temp']) / w['std_temp']
        z_vib  = abs(vibration   - w['mean_vib'])  / w['std_vib']
        z_cur  = abs(current     - w['mean_cur'])  / w['std_cur']

        reasons = []
        if z_temp > thr:
            reasons.append(f'Temp z={z_temp:.2f}>{thr}')
        if z_vib > thr:
            reasons.append(f'Vib z={z_vib:.2f}>{thr}')
        if z_cur > thr:
            reasons.append(f'Cur z={z_cur:.2f}>{thr}')

        return bool(reasons), '; '.join(reasons), {
            'temperature': round(z_temp, 3),
            'vibration':   round(z_vib, 3),
            'current':     round(z_cur, 3),
        }

    # ── FL weight serialisation ───────────────────────────────────────────────

    def get_weights(self) -> dict:
        return dict(self.weights)

    def get_weights_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.weights, sort_keys=True).encode()
        ).hexdigest()

    def apply_fedavg(self, peer_weights: dict) -> None:
        """
        Federated Averaging: sample-count-weighted merge with peer weights.
        """
        own_n  = float(self.weights.get('n_samples', 0))
        peer_n = float(peer_weights.get('n_samples', 0))
        total  = own_n + peer_n

        if total == 0:
            return  # neither node has data yet

        w_own  = own_n  / total
        w_peer = peer_n / total

        for key in ('mean_temp', 'std_temp', 'mean_vib', 'std_vib',
                    'mean_cur', 'std_cur', 'z_threshold'):
            if key in peer_weights:
                self.weights[key] = (
                    w_own  * self.weights.get(key, 0.0) +
                    w_peer * peer_weights[key]
                )

        self.weights['n_samples'] = total
        print(f"  FedAvg applied — own_w={w_own:.3f}  peer_w={w_peer:.3f}")

    def evaluate_accuracy(self, recent_points: list) -> float:
        """
        Proxy accuracy = fraction of recent readings that are NOT flagged.
        (Baseline: healthy operation should be mostly non-anomalous.)
        """
        if not recent_points:
            return round(1.0 - 1.0 / max(self.weights['n_samples'], 1), 4)
        normal = sum(1 for t, v, c in recent_points if not self.predict(t, v, c)[0])
        return normal / len(recent_points)

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> 'AnomalyDetector':
        with open(path, 'rb') as f:
            return pickle.load(f)
