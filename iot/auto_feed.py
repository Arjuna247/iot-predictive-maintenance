
import time
import sys
from client_sim import ESP32Simulator

def run_auto_feed():
    print("🚀 Starting Auto-Feed Simulation...")
    print("Target: http://localhost:5000")
    
    # Create a device simulator
    sim = ESP32Simulator("ESP32_01", "http://localhost:5000")
    
    # Run indefinitely (or for a long time)
    # interval=1s, anomaly after 60s
    try:
        sim.run(duration=3600, interval=1, inject_anomaly_after=60) 
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    run_auto_feed()
