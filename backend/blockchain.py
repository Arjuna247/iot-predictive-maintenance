"""
Blockchain utility functions.
Hashing is SHA-256 over canonical (sort_keys) JSON of block fields.
The exact same compute_payload_hash must be used on edge nodes.
"""
import hashlib
import json
from datetime import datetime


# ── Payload hash ────────────────────────────────────────────────────────────

def compute_payload_hash(node_id: str, temperature: float,
                         vibration: float, current: float,
                         timestamp: str) -> str:
    """
    SHA-256 of the canonical sensor payload.
    Must mirror hashing_utils.compute_payload_hash on edge nodes.
    """
    payload = {
        'node_id': node_id,
        'temperature': round(temperature, 4),
        'vibration': round(vibration, 4),
        'current': round(current, 4),
        'timestamp': timestamp,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()


# ── Block hash ───────────────────────────────────────────────────────────────

def compute_block_hash(block_index: int, node_id: str,
                       data_hash: str, previous_hash: str,
                       timestamp: str) -> str:
    """SHA-256 of the canonical block header fields."""
    block_data = {
        'block_index': block_index,
        'node_id': node_id,
        'data_hash': data_hash,
        'previous_hash': previous_hash,
        'timestamp': timestamp,
    }
    return hashlib.sha256(
        json.dumps(block_data, sort_keys=True).encode()
    ).hexdigest()


# ── Genesis block ─────────────────────────────────────────────────────────────

def create_genesis_block(node_id: str) -> dict:
    ts = datetime.utcnow().isoformat()
    previous_hash = '0' * 64
    data_hash = 'GENESIS'
    block_hash = compute_block_hash(0, node_id, data_hash, previous_hash, ts)
    return {
        'block_index': 0,
        'node_id': node_id,
        'data_hash': data_hash,
        'previous_hash': previous_hash,
        'block_hash': block_hash,
        'timestamp': ts,
    }


# ── Chain validation ──────────────────────────────────────────────────────────

def validate_chain(blocks) -> list:
    """
    Walk the chain recalculating every block hash and checking linkage.
    Linkage is validated *per node* — each node has its own independent chain.
    Returns a list of per-block validation dicts.
    """
    results = []
    # Track the last block hash seen FOR EACH NODE independently
    prev_hash_by_node: dict = {}

    # Sort by node + block_index so linkage checks are in order
    sorted_blocks = sorted(blocks, key=lambda b: (b.node_id, b.block_index))

    for block in sorted_blocks:
        expected_hash = compute_block_hash(
            block.block_index,
            block.node_id,
            block.data_hash,
            block.previous_hash,
            block.timestamp.isoformat(),
        )

        hash_valid = expected_hash == block.block_hash

        # Check linkage within this node's chain
        prev_hash = prev_hash_by_node.get(block.node_id)
        if prev_hash is not None:
            chain_valid = block.previous_hash == prev_hash
        else:
            chain_valid = True  # first block we've seen for this node

        # Verify the payload hash against current DB values (tamper detection)
        data_integrity = True
        if hasattr(block, 'sensor_data') and block.sensor_data:
            sd = block.sensor_data
            # Use the original timestamp string stored at ingest time.
            # Fallback to .isoformat() for older rows without timestamp_raw.
            ts_for_hash = getattr(sd, 'timestamp_raw', None) or sd.timestamp.isoformat()
            recalc = compute_payload_hash(
                sd.node_id, sd.temperature, sd.vibration,
                sd.current, ts_for_hash
            )
            data_integrity = recalc == block.data_hash

        results.append({
            'id': block.id,
            'block_index': block.block_index,
            'node_id': block.node_id,
            'timestamp': block.timestamp.isoformat(),
            'data_hash': block.data_hash,
            'stored_hash': block.block_hash,
            'expected_hash': expected_hash,
            'previous_hash': block.previous_hash,
            'hash_valid': hash_valid,
            'chain_valid': chain_valid,
            'data_integrity': data_integrity,
            'is_valid': hash_valid and chain_valid and data_integrity,
        })

        prev_hash_by_node[block.node_id] = block.block_hash

    return results