"""
Peer-to-Peer Federated Learning transport.

Each node runs a tiny Flask server that:
  GET  /fl/weights  – return own weights (pull interface)
  POST /fl/receive  – accept weights from peer (push interface)
  GET  /fl/status   – diagnostics

A background scheduler fires every FL_EXCHANGE_INTERVAL seconds to
push the local weights to the configured peer URL.
"""
import threading
import time
import requests
from flask import Flask, request, jsonify


class FLPeer:
    def __init__(self, node_id: str, peer_url: str, backend_url: str,
                 listen_port: int, exchange_interval: int = 60):
        self.node_id           = node_id
        self.peer_url          = peer_url        # e.g. http://localhost:5002
        self.backend_url       = backend_url
        self.listen_port       = listen_port
        self.exchange_interval = exchange_interval

        self.model          = None   # set by the owning node before start_listener()
        self.last_exchange  = None
        self.exchange_count = 0

        self._app = Flask(f'fl_peer_{node_id}')
        self._setup_routes()

    # ── Flask routes ─────────────────────────────────────────────────────────

    def _setup_routes(self):
        app = self._app

        @app.route('/fl/weights', methods=['GET'])
        def get_weights():
            if self.model is None:
                return jsonify({'error': 'model not ready'}), 503
            return jsonify({
                'node_id':      self.node_id,
                'weights':      self.model.get_weights(),
                'weights_hash': self.model.get_weights_hash(),
            })

        @app.route('/fl/receive', methods=['POST'])
        def receive_weights():
            data         = request.get_json(force=True)
            peer_weights = data.get('weights', {})
            from_node    = data.get('node_id', 'unknown')

            if self.model is None:
                return jsonify({'error': 'model not ready'}), 503

            acc_before = self.model.evaluate_accuracy([])
            self.model.apply_fedavg(peer_weights)
            acc_after  = self.model.evaluate_accuracy([])

            self._log_to_backend(from_node, self.node_id,
                                 acc_before, acc_after,
                                 data.get('weights_hash'))

            return jsonify({
                'success':          True,
                'accuracy_before':  acc_before,
                'accuracy_after':   acc_after,
            })

        @app.route('/fl/status', methods=['GET'])
        def status():
            return jsonify({
                'node_id':        self.node_id,
                'exchange_count': self.exchange_count,
                'last_exchange':  self.last_exchange,
                'weights':        self.model.get_weights() if self.model else None,
            })

    # ── Logging helper ────────────────────────────────────────────────────────

    def _log_to_backend(self, from_node, to_node, acc_before, acc_after, weights_hash):
        try:
            requests.post(
                f'{self.backend_url}/api/fl/log',
                json={
                    'from_node':       from_node,
                    'to_node':         to_node,
                    'accuracy_before': acc_before,
                    'accuracy_after':  acc_after,
                    'weights_hash':    weights_hash,
                },
                timeout=5,
            )
        except Exception as e:
            print(f"  [FL] Backend log failed: {e}")

    # ── Push weights to peer ──────────────────────────────────────────────────

    def push_weights_to_peer(self) -> bool:
        if self.model is None:
            return False
        try:
            weights      = self.model.get_weights()
            weights_hash = self.model.get_weights_hash()
            acc_before   = self.model.evaluate_accuracy([])

            resp = requests.post(
                f'{self.peer_url}/fl/receive',
                json={
                    'node_id':      self.node_id,
                    'weights':      weights,
                    'weights_hash': weights_hash,
                },
                timeout=10,
            )

            if resp.status_code == 200:
                self.exchange_count += 1
                self.last_exchange   = time.strftime('%Y-%m-%dT%H:%M:%S')
                result               = resp.json()
                print(f"  [FL] ✓ Exchange #{self.exchange_count}: "
                      f"{self.node_id} → peer  "
                      f"acc_after={result.get('accuracy_after', '?')}")
                self._log_to_backend(
                    self.node_id, 'peer',
                    acc_before, result.get('accuracy_after'),
                    weights_hash,
                )
                return True

        except requests.exceptions.ConnectionError:
            print(f"  [FL] Peer not reachable at {self.peer_url}")
        except Exception as e:
            print(f"  [FL] Exchange error: {e}")

        return False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start_listener(self):
        """Start the Flask listener in a daemon thread."""
        def _run():
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            self._app.run(host='0.0.0.0', port=self.listen_port,
                          debug=False, use_reloader=False)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        print(f"  [FL] Listener started on port {self.listen_port}")

    def start_exchange_scheduler(self, initial_delay: float = 0):
        """Periodically push weights to peer."""
        def _scheduler():
            if initial_delay:
                time.sleep(initial_delay)
            while True:
                time.sleep(self.exchange_interval)
                print(f"\n  [FL] Initiating scheduled exchange from {self.node_id} …")
                self.push_weights_to_peer()

        t = threading.Thread(target=_scheduler, daemon=True)
        t.start()
        print(f"  [FL] Scheduler started (interval={self.exchange_interval}s, "
              f"delay={initial_delay}s)")
