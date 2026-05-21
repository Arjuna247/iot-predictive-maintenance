import os


class Config:

    # =========================
    # MongoDB
    # =========================
    MONGO_URI = os.environ.get(
        "MONGO_URI",
        "mongodb+srv://harivisu06:hariharan123@cluster0.2fbexgr.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0"
    )

    DATABASE_NAME = os.environ.get(
        "DATABASE_NAME",
        "iot_predictive_maintenance"
    )

    # =========================
    # Flask Secret
    # =========================
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "iot-predictive-maintenance-secret-2024"
    )

    # =========================
    # CORS
    # =========================
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000"
    ).split(",")

    # =========================
    # Anomaly Thresholds
    # =========================
    ANOMALY_TEMP_MIN = float(
        os.environ.get("ANOMALY_TEMP_MIN", "20.0")
    )

    ANOMALY_TEMP_MAX = float(
        os.environ.get("ANOMALY_TEMP_MAX", "80.0")
    )

    ANOMALY_VIBRATION_MAX = float(
        os.environ.get("ANOMALY_VIBRATION_MAX", "5.0")
    )

    ANOMALY_CURRENT_MAX = float(
        os.environ.get("ANOMALY_CURRENT_MAX", "15.0")
    )

    # =========================
    # Federated Learning
    # =========================
    FL_EXCHANGE_INTERVAL = int(
        os.environ.get("FL_EXCHANGE_INTERVAL", "60")
    )