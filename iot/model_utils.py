"""
Model Utilities
Machine learning utilities for anomaly detection and predictive maintenance
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import pickle
import os


def load_sensor_data_from_file(file_path="sensor_data.jsonl"):
    """
    Load sensor data from JSONL file

    Args:
        file_path: Path to the JSONL file

    Returns:
        pandas DataFrame with sensor data
    """
    import json

    data_list = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    data_list.append(json.loads(line))

    if not data_list:
        raise ValueError(f"No data found in {file_path}")

    df = pd.DataFrame(data_list)
    return df


def preprocess_data(df, features=None, target="Anomaly", test_size=0.2, seed=42):
    """
    Prepare train/test data from a DataFrame

    Args:
        df: pandas DataFrame containing sensor data
        features: list of feature column names (default: Temperature, Humidity, Vibration, Current)
        target: target column name (default: Anomaly)
        test_size: fraction of data for test set (default: 0.2)
        seed: random seed for reproducibility (default: 42)

    Returns:
        X_train, X_test, y_train, y_test
    """
    if features is None:
        features = ["Temperature", "Humidity", "Vibration", "Current"]

    # Check if all features exist
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing features in DataFrame: {missing_features}")

    X = df[features]

    # If target doesn't exist, create placeholder
    if target not in df.columns:
        print(f"Warning: '{target}' column not found. Creating placeholder with all zeros.")
        y = pd.Series([0] * len(df))
    else:
        y = df[target]

    # Check if we have enough samples for stratification
    if len(y.unique()) > 1 and y.value_counts().min() >= 2:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=seed, stratify=y
        )
    else:
        # No stratification if only one class or too few samples
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=seed
        )

    return X_train, X_test, y_train, y_test


def train_local_model(X_train, y_train, n_estimators=100, random_state=42):
    """
    Train a RandomForestClassifier on the given training data

    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of trees in the forest (default: 100)
        random_state: Random seed (default: 42)

    Returns:
        Trained RandomForestClassifier model
    """
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        max_depth=10,
        min_samples_split=5,
        n_jobs=-1  # Use all CPU cores
    )
    model.fit(X_train, y_train)
    return model


def train_isolation_forest(X_train, contamination=0.1, random_state=42):
    """
    Train an Isolation Forest for unsupervised anomaly detection

    Args:
        X_train: Training features
        contamination: Expected proportion of outliers (default: 0.1)
        random_state: Random seed (default: 42)

    Returns:
        Trained IsolationForest model
    """
    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(X_train)
    return model


def evaluate_model(model, X_test, y_test, verbose=True):
    """
    Evaluate the model on test data

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        verbose: Print detailed metrics (default: True)

    Returns:
        Tuple of (accuracy, f1_score)
    """
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="weighted", zero_division=0)

    if verbose:
        precision = precision_score(y_test, preds, average="weighted", zero_division=0)
        recall = recall_score(y_test, preds, average="weighted", zero_division=0)

        print(f"\n📊 Model Evaluation Metrics:")
        print(f"   Accuracy:  {acc:.4f}")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1 Score:  {f1:.4f}")

        # Confusion matrix
        cm = confusion_matrix(y_test, preds)
        print(f"\n   Confusion Matrix:")
        print(f"   {cm}")

    return acc, f1


def get_feature_importance(model, feature_names):
    """
    Get feature importances from trained model

    Args:
        model: Trained RandomForest model
        feature_names: List of feature names

    Returns:
        Dictionary of feature importances
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        feature_importance = dict(zip(feature_names, importances))

        # Sort by importance
        sorted_importance = dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))

        return sorted_importance
    else:
        return {}


def save_model(model, file_path="models/anomaly_model.pkl"):
    """
    Save trained model to disk

    Args:
        model: Trained model
        file_path: Path to save the model (default: models/anomaly_model.pkl)
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        pickle.dump(model, f)

    print(f"✓ Model saved to {file_path}")


def load_model(file_path="models/anomaly_model.pkl"):
    """
    Load trained model from disk

    Args:
        file_path: Path to the model file

    Returns:
        Loaded model
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file not found: {file_path}")

    with open(file_path, "rb") as f:
        model = pickle.load(f)

    print(f"✓ Model loaded from {file_path}")
    return model


def predict_anomaly(model, sensor_reading, features=None):
    """
    Predict if a sensor reading is anomalous

    Args:
        model: Trained model
        sensor_reading: Dictionary or DataFrame with sensor data
        features: List of feature names (default: Temperature, Humidity, Vibration, Current)

    Returns:
        Tuple of (prediction, probability) where prediction is 0 (normal) or 1 (anomaly)
    """
    if features is None:
        features = ["Temperature", "Humidity", "Vibration", "Current"]

    # Convert to DataFrame if dict
    if isinstance(sensor_reading, dict):
        df = pd.DataFrame([sensor_reading])
    else:
        df = sensor_reading

    X = df[features]
    prediction = model.predict(X)[0]

    # Get probability if available
    if hasattr(model, 'predict_proba'):
        probability = model.predict_proba(X)[0]
        return prediction, probability
    else:
        return prediction, None


def calculate_health_score(sensor_data, thresholds=None):
    """
    Calculate equipment health score based on sensor readings

    Args:
        sensor_data: Dictionary with sensor readings
        thresholds: Dictionary with threshold values for each sensor

    Returns:
        Health score (0-100)
    """
    if thresholds is None:
        thresholds = {
            "Temperature": {"min": 15, "max": 40, "optimal": 28},
            "Humidity": {"min": 30, "max": 85, "optimal": 65},
            "Vibration": {"min": 0, "max": 0.1, "optimal": 0.02},
            "Current": {"min": 0.05, "max": 0.3, "optimal": 0.15}
        }

    health_score = 100
    penalties = []

    for sensor, value in sensor_data.items():
        if sensor in thresholds:
            t = thresholds[sensor]

            # Calculate deviation from optimal
            if value < t["min"]:
                penalty = ((t["min"] - value) / t["min"]) * 25
                penalties.append(min(penalty, 25))
            elif value > t["max"]:
                penalty = ((value - t["max"]) / t["max"]) * 25
                penalties.append(min(penalty, 25))
            else:
                # Small penalty for deviation from optimal even if in range
                optimal_penalty = abs(value - t["optimal"]) / t["optimal"] * 5
                penalties.append(min(optimal_penalty, 5))

    # Apply penalties
    health_score -= sum(penalties)
    health_score = max(0, min(100, health_score))  # Clamp between 0 and 100

    return round(health_score, 2)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧠 Model Utilities Test")
    print("="*60)

    # Example usage
    print("\nTesting feature importance calculation...")

    # Create sample data
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=1000, n_features=4, random_state=42)
    feature_names = ["Temperature", "Humidity", "Vibration", "Current"]

    # Convert to DataFrame
    df = pd.DataFrame(X, columns=feature_names)
    df["Anomaly"] = y

    # Split data
    X_train, X_test, y_train, y_test = preprocess_data(df)

    # Train model
    print("\nTraining model...")
    model = train_local_model(X_train, y_train)

    # Evaluate
    evaluate_model(model, X_test, y_test)

    # Feature importance
    print("\n📊 Feature Importance:")
    importance = get_feature_importance(model, feature_names)
    for feature, imp in importance.items():
        print(f"   {feature}: {imp:.4f}")

    print("\n" + "="*60 + "\n")
