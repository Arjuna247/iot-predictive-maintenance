"""
Hashing utilities shared by both edge nodes.
Must produce identical output to backend/blockchain.py :: compute_payload_hash.
"""
import hashlib
import json
from datetime import datetime, timezone


def compute_payload_hash(node_id: str, temperature: float,
                         vibration: float, current: float,
                         timestamp: str) -> str:
    """
    SHA-256 of the canonical (sort_keys) sensor payload JSON.
    Values are rounded to 4 dp so floating-point drift can't break the chain.
    """
    payload = {
        'node_id': node_id,
        'temperature': round(temperature, 4),
        'vibration': round(vibration, 4),
        'current': round(current, 4),
        'timestamp': timestamp,
    }
    canonical = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def get_utc_timestamp() -> str:
    """Current UTC time as an ISO-8601 string (microseconds stripped to ms)."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
