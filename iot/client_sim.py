"""
ESP32 IoT Client Simulator
Simulates ESP32 devices sending sensor data to the server
"""

import requests
import json
import time
import random
import math
from datetime import datetime


class ESP32Simulator:
    """Simulates an ESP32 device with multiple sensors"""

    def __init__(self, device_id, server_url="http://localhost:5000"):
        self.device_id = device_id
        self.server_url = server_url
        self.running = False
        self.anomaly_mode = False

    def generate_sensor_data(self):
        """Generate realistic sensor data similar to the frontend"""
        timestamp = int(time.time() * 1000)  # milliseconds

        # Base values
        base_temp = 28.0  # Celsius
        base_humidity = 65.0  # Percentage
        base_current = 0.15  # Amperes

        # Add realistic noise
        temp_noise = (random.random() - 0.5) * 4
        humidity_noise = (random.random() - 0.5) * 10
        current_noise = (random.random() - 0.5) * 0.05

        # Anomaly factors
        temp_factor = 1.0
        vibration_factor = 1.0
        current_factor = 1.0

        if self.anomaly_mode:
            temp_factor = 1.5 + random.random() * 0.5  # 50-100% increase
            vibration_factor = 3 + random.random() * 2  # 300-500% increase
            current_factor = 2 + random.random() * 0.5  # 200-250% increase

        # Calculate sensor values
        temperature = (base_temp + temp_noise) * temp_factor
        humidity = max(0, min(100, base_humidity + humidity_noise))
        current = max(0, (base_current + current_noise) * current_factor)

        # MPU6050-style accelerometer data (simulating vibration)
        accel_x = (random.random() - 0.5) * 0.1 * vibration_factor
        accel_y = (random.random() - 0.5) * 0.1 * vibration_factor
        accel_z = 0.98 + (random.random() - 0.5) * 0.1 * vibration_factor

        # Gyroscope data
        gyro_x = (random.random() - 0.5) * 0.4 * vibration_factor
        gyro_y = (random.random() - 0.5) * 0.4 * vibration_factor
        gyro_z = (random.random() - 0.5) * 0.4 * vibration_factor

        # Calculate vibration magnitude
        vibration = math.sqrt(accel_x**2 + accel_y**2 + (accel_z - 0.98)**2)

        return {
            "deviceId": self.device_id,
            "timestamp": timestamp,
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
            "Anomaly": 1 if self.anomaly_mode else 0
        }

    def send_data(self, data):
        """Send data to the server"""
        try:
            response = requests.post(
                f"{self.server_url}/sensor-data",
                json=data,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✓ [{self.device_id}] Data sent: Temp={data['Temperature']:.1f}°C, "
                      f"Vib={data['Vibration']:.3f}g")
                return True
            else:
                print(f"✗ [{self.device_id}] Server error: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"✗ [{self.device_id}] Connection failed. Is the server running?")
            return False
        except Exception as e:
            print(f"✗ [{self.device_id}] Error: {e}")
            return False

    def run(self, duration=60, interval=1, inject_anomaly_after=30):
        """
        Run the simulator

        Args:
            duration: Total runtime in seconds
            interval: Time between readings in seconds
            inject_anomaly_after: Inject anomaly after this many seconds (0 = no anomaly)
        """
        self.running = True
        start_time = time.time()
        iteration = 0

        print(f"\n🚀 Starting {self.device_id} simulator...")
        print(f"   Duration: {duration}s | Interval: {interval}s | Server: {self.server_url}")

        try:
            while self.running and (time.time() - start_time) < duration:
                # Check if we should inject anomaly
                if inject_anomaly_after > 0 and (time.time() - start_time) > inject_anomaly_after:
                    if not self.anomaly_mode:
                        self.anomaly_mode = True
                        print(f"\n⚠️  [{self.device_id}] ANOMALY INJECTED\n")

                # Generate and send data
                data = self.generate_sensor_data()
                self.send_data(data)

                iteration += 1
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n🛑 [{self.device_id}] Stopped by user")

        self.running = False
        print(f"\n✅ [{self.device_id}] Simulation completed. Sent {iteration} readings.")

    def stop(self):
        """Stop the simulator"""
        self.running = False


def simulate_multiple_devices(num_devices=3, duration=60, interval=2):
    """Simulate multiple ESP32 devices"""
    import threading

    simulators = []
    threads = []

    print(f"\n{'='*60}")
    print(f"🏭 Starting {num_devices} ESP32 Device Simulators")
    print(f"{'='*60}")

    # Create simulators
    for i in range(1, num_devices + 1):
        device_id = f"ESP32_{i:02d}"
        simulator = ESP32Simulator(device_id)
        simulators.append(simulator)

        # Different anomaly injection times for each device
        anomaly_time = 0 if i == 1 else (20 + i * 10)

        # Create thread for each simulator
        thread = threading.Thread(
            target=simulator.run,
            args=(duration, interval, anomaly_time)
        )
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()
        time.sleep(0.5)  # Stagger the starts slightly

    # Wait for all to complete
    for thread in threads:
        thread.join()

    print(f"\n{'='*60}")
    print(f"✅ All simulators completed")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys

    # Check if server URL is provided
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

    print("\n" + "="*60)
    print("🔌 ESP32 IoT Device Simulator")
    print("="*60)
    print("\nOptions:")
    print("1. Single device simulation")
    print("2. Multiple devices (3 devices)")
    print("3. Exit")

    choice = input("\nSelect option (1-3): ").strip()

    if choice == "1":
        device_id = input("Enter device ID (default: ESP32_01): ").strip() or "ESP32_01"
        duration = int(input("Duration in seconds (default: 60): ").strip() or "60")
        interval = float(input("Interval between readings (default: 2): ").strip() or "2")
        anomaly_after = int(input("Inject anomaly after seconds (0=no anomaly, default: 30): ").strip() or "30")

        simulator = ESP32Simulator(device_id, server_url)
        simulator.run(duration, interval, anomaly_after)

    elif choice == "2":
        duration = int(input("Duration in seconds (default: 60): ").strip() or "60")
        interval = float(input("Interval between readings (default: 2): ").strip() or "2")

        simulate_multiple_devices(num_devices=3, duration=duration, interval=interval)

    else:
        print("Exiting...")
