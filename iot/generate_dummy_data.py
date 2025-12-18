"""
Dummy Data Generator
Generates synthetic sensor data for testing without running the full simulation
"""

import pandas as pd
import numpy as np
import json
import math
from datetime import datetime, timedelta


def generate_sensor_reading(timestamp, anomaly=False, device_id="ESP32_01"):
    """
    Generate a single sensor reading

    Args:
        timestamp: Timestamp for the reading
        anomaly: Whether to inject anomaly
        device_id: Device identifier

    Returns:
        Dictionary with sensor data
    """
    # Base values
    base_temp = 28.0
    base_humidity = 65.0
    base_current = 0.15

    # Noise
    temp_noise = (np.random.random() - 0.5) * 4
    humidity_noise = (np.random.random() - 0.5) * 10
    current_noise = (np.random.random() - 0.5) * 0.05

    # Anomaly factors
    temp_factor = 1.0
    vib_factor = 1.0
    current_factor = 1.0

    if anomaly:
        temp_factor = 1.5 + np.random.random() * 0.5
        vib_factor = 3 + np.random.random() * 2
        current_factor = 2 + np.random.random() * 0.5

    # Calculate values
    temperature = (base_temp + temp_noise) * temp_factor
    humidity = max(0, min(100, base_humidity + humidity_noise))
    current = max(0, (base_current + current_noise) * current_factor)

    # Accelerometer (vibration)
    accel_x = (np.random.random() - 0.5) * 0.1 * vib_factor
    accel_y = (np.random.random() - 0.5) * 0.1 * vib_factor
    accel_z = 0.98 + (np.random.random() - 0.5) * 0.1 * vib_factor

    # Gyroscope
    gyro_x = (np.random.random() - 0.5) * 0.4 * vib_factor
    gyro_y = (np.random.random() - 0.5) * 0.4 * vib_factor
    gyro_z = (np.random.random() - 0.5) * 0.4 * vib_factor

    # Vibration magnitude
    vibration = math.sqrt(accel_x**2 + accel_y**2 + (accel_z - 0.98)**2)

    return {
        "deviceId": device_id,
        "timestamp": int(timestamp.timestamp() * 1000),
        "Temperature": round(temperature, 2),
        "Humidity": round(humidity, 2),
        "Vibration": round(vibration, 4),
        "Current": round(current, 3),
        "accel": {
            "x": round(accel_x, 4),
            "y": round(accel_y, 4),
            "z": round(accel_z, 4)
        },
        "gyro": {
            "x": round(gyro_x, 4),
            "y": round(gyro_y, 4),
            "z": round(gyro_z, 4)
        },
        "Anomaly": 1 if anomaly else 0
    }


def generate_dataset(
    num_samples=5000,
    anomaly_ratio=0.1,
    num_devices=3,
    start_time=None,
    interval_seconds=2
):
    """
    Generate a complete dataset

    Args:
        num_samples: Total number of samples to generate
        anomaly_ratio: Ratio of anomalous samples
        num_devices: Number of simulated devices
        start_time: Start timestamp (default: current time - num_samples * interval)
        interval_seconds: Time interval between readings

    Returns:
        DataFrame with generated data
    """
    if start_time is None:
        start_time = datetime.now() - timedelta(seconds=num_samples * interval_seconds)

    data_list = []
    num_anomalies = int(num_samples * anomaly_ratio)

    # Randomly select which samples will be anomalies
    anomaly_indices = np.random.choice(num_samples, num_anomalies, replace=False)

    print(f"Generating {num_samples} sensor readings...")
    print(f"  Devices: {num_devices}")
    print(f"  Normal samples: {num_samples - num_anomalies}")
    print(f"  Anomalous samples: {num_anomalies}")

    for i in range(num_samples):
        # Select device (round-robin)
        device_id = f"ESP32_{(i % num_devices) + 1:02d}"

        # Current timestamp
        timestamp = start_time + timedelta(seconds=i * interval_seconds)

        # Check if this should be an anomaly
        is_anomaly = i in anomaly_indices

        # Generate reading
        reading = generate_sensor_reading(timestamp, is_anomaly, device_id)
        data_list.append(reading)

        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1}/{num_samples} samples...")

    df = pd.DataFrame(data_list)
    print(f"✓ Dataset generated: {len(df)} samples")

    return df


def save_to_csv(df, filename="data/dummy_sensor_data.csv"):
    """Save dataset to CSV"""
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    df.to_csv(filename, index=False)
    print(f"✓ Saved to CSV: {filename}")


def save_to_jsonl(df, filename="sensor_data.jsonl"):
    """Save dataset to JSONL format"""
    with open(filename, "w") as f:
        for _, row in df.iterrows():
            json.dump(row.to_dict(), f)
            f.write("\n")

    print(f"✓ Saved to JSONL: {filename}")


def print_dataset_summary(df):
    """Print summary statistics of the dataset"""
    print("\n" + "="*60)
    print("📊 Dataset Summary")
    print("="*60)

    print(f"\nTotal samples: {len(df)}")
    print(f"Number of devices: {df['deviceId'].nunique()}")
    print(f"Devices: {df['deviceId'].unique().tolist()}")

    print(f"\n🔴 Anomalies: {df['Anomaly'].sum()} ({df['Anomaly'].sum()/len(df)*100:.1f}%)")
    print(f"🟢 Normal: {len(df) - df['Anomaly'].sum()} ({(len(df)-df['Anomaly'].sum())/len(df)*100:.1f}%)")

    print("\n📈 Feature Statistics:")
    features = ["Temperature", "Humidity", "Vibration", "Current"]

    for feature in features:
        print(f"\n{feature}:")
        print(f"  Mean: {df[feature].mean():.4f}")
        print(f"  Std:  {df[feature].std():.4f}")
        print(f"  Min:  {df[feature].min():.4f}")
        print(f"  Max:  {df[feature].max():.4f}")

    print("\n" + "="*60)


if __name__ == "__main__":
    import sys

    print("\n" + "="*60)
    print("🏭 Dummy Data Generator for IoT Predictive Maintenance")
    print("="*60)

    # Parse command line arguments
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    anomaly_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
    num_devices = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    print(f"\nConfiguration:")
    print(f"  Samples: {num_samples}")
    print(f"  Anomaly ratio: {anomaly_ratio * 100}%")
    print(f"  Devices: {num_devices}")
    print()

    # Generate dataset
    df = generate_dataset(
        num_samples=num_samples,
        anomaly_ratio=anomaly_ratio,
        num_devices=num_devices
    )

    # Print summary
    print_dataset_summary(df)

    # Save to files
    print("\n💾 Saving dataset...")
    save_to_csv(df, f"data/dummy_sensor_data_{num_samples}_with_anomaly.csv")
    save_to_jsonl(df, "sensor_data.jsonl")

    print("\n✅ Dataset generation complete!")
    print("\nYou can now use this data to:")
    print("  1. Train machine learning models")
    print("  2. Run federated learning simulations")
    print("  3. Test the anomaly detection system")
    print()
