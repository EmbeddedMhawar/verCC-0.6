#!/usr/bin/env python3
"""
ESP32 Data Simulator
Simulates ESP32 sending energy data to the FastAPI backend
"""

import requests
import json
import time
import random
from datetime import datetime, timezone
import math

# Backend URL
BACKEND_URL = "http://localhost:5000/api/energy-data"

def simulate_solar_irradiance():
    """Simulate solar irradiance based on time of day"""
    current_hour = datetime.now().hour
    
    # Solar pattern: 0 at night, peak around noon
    if 6 <= current_hour <= 18:
        # Sine wave pattern for daylight hours
        hour_angle = (current_hour - 6) * math.pi / 12  # 0 to π
        base_irradiance = 1200 * math.sin(hour_angle)
        # Add some randomness
        irradiance = max(0, base_irradiance + random.uniform(-100, 100))
    else:
        irradiance = 0
    
    return irradiance

def simulate_esp32_reading(device_id="ESP32-001"):
    """Generate simulated ESP32 reading"""
    
    # Simulate solar irradiance
    irradiance = simulate_solar_irradiance()
    
    # Calculate power based on irradiance (simplified model)
    # Assume 1kW panel with 20% efficiency
    max_power = 1000  # 1kW
    efficiency = 0.96 + random.uniform(-0.05, 0.05)  # 91-101% efficiency
    power = (irradiance / 1000.0) * max_power * efficiency
    power = max(0, power)
    
    # Calculate current (P = V * I)
    voltage = 220.0 + random.uniform(-5, 5)  # Grid voltage with variation
    current = power / voltage if voltage > 0 else 0
    
    # Simulate accumulated energy (this would normally be persistent)
    if not hasattr(simulate_esp32_reading, 'total_energy'):
        simulate_esp32_reading.total_energy = 0.0
    
    # Add energy (kWh) - assuming 1-second intervals
    energy_increment = (power / 1000.0) / 3600.0  # Convert W to kWh per second
    simulate_esp32_reading.total_energy += energy_increment
    
    # Other parameters
    grid_frequency = 50.0 + random.uniform(-0.1, 0.1)
    power_factor = 0.95 + random.uniform(-0.05, 0.05)
    ambient_temp = 25.0 + random.uniform(-10, 15)  # 15-40°C range
    system_status = 1 if power > 10 else 0  # Online if generating > 10W
    
    reading = {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current": round(current, 6),
        "voltage": round(voltage, 2),
        "power": round(power, 2),
        "ac_power_kw": round(power / 1000.0, 6),
        "total_energy_kwh": round(simulate_esp32_reading.total_energy, 6),
        "grid_frequency_hz": round(grid_frequency, 2),
        "power_factor": round(power_factor, 3),
        "ambient_temp_c": round(ambient_temp, 2),
        "irradiance_w_m2": round(irradiance, 2),
        "system_status": system_status,
        "efficiency": round(efficiency, 4)
    }
    
    return reading

def send_reading(reading):
    """Send reading to backend"""
    try:
        response = requests.post(BACKEND_URL, json=reading, timeout=5)
        if response.status_code == 200:
            print(f"✅ Sent: {reading['device_id']} - {reading['power']:.1f}W - {reading['total_energy_kwh']:.4f}kWh")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

def main():
    """Main simulation loop"""
    print("🌞 ESP32 Solar Data Simulator")
    print(f"📡 Sending data to: {BACKEND_URL}")
    print("🔄 Press Ctrl+C to stop\n")
    
    device_ids = ["ESP32-001", "ESP32-002"]  # Simulate multiple devices
    
    try:
        while True:
            for device_id in device_ids:
                reading = simulate_esp32_reading(device_id)
                send_reading(reading)
            
            time.sleep(5)  # Send every 5 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped")

if __name__ == "__main__":
    main()