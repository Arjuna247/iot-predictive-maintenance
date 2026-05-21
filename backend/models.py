"""
MongoDB database layer.
Replaces SQLAlchemy – call init_db(app) once at startup,
then call get_db() anywhere to get the PyMongo Database object.

Collections
-----------
  sensor_data        – one doc per sensor reading
  blockchain_ledger  – one doc per blockchain block
  fl_exchange_log    – one doc per federated-learning weight exchange
"""
from pymongo import MongoClient, ASCENDING, DESCENDING

_client: MongoClient | None = None
_db = None


def init_db(app) -> None:
    """Connect to MongoDB and ensure indexes exist."""
    global _client, _db
    _client = MongoClient(app.config['MONGO_URI'])
    # get_default_database() reads the DB name from the URI path
    _db = _client.get_default_database()

    # Indexes ─────────────────────────────────────────────────────────────────
    _db.sensor_data.create_index(
        [('timestamp', ASCENDING)],
    )
    _db.sensor_data.create_index(
        [('node_id', ASCENDING), ('timestamp', ASCENDING)],
    )
    _db.blockchain_ledger.create_index(
        [('node_id', ASCENDING), ('block_index', ASCENDING)],
        unique=True,
    )
    _db.blockchain_ledger.create_index(
        [('block_index', ASCENDING)],
    )
    _db.fl_exchange_log.create_index(
        [('timestamp', DESCENDING)],
    )

    print("[OK] MongoDB connected — collections & indexes ready.")


def get_db():
    """Return the MongoDB Database instance (set by init_db)."""
    return _db
