#!/usr/bin/env python3
"""
Complete System Test
Tests the entire ESP32 Carbon Credit Backend with real Supabase integration
"""

import requests
import json
import time
import random
from datetime import datetime, timezone
import math

# Your backend URL (update this after Railway deployment)
BACKEND_URL = "http://localhost:5000"

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

def generate_esp32_reading(device_id="ESP32-001"):
    """Generate realistic ESP32 reading"""
    
    # Simulate solar irradiance
    irradiance = simulate_solar_irradiance()
    
    # Calculate power based on irradiance (simplified model)
    max_power = 1000  # 1kW panel
    efficiency = 0.96 + random.uniform(-0.05, 0.05)  # 91-101% efficiency
    power = (irradiance / 1000.0) * max_power * efficiency
    power = max(0, power)
    
    # Calculate current (P = V * I)
    voltage = 220.0 + random.uniform(-5, 5)  # Grid voltage with variation
    current = power / voltage if voltage > 0 else 0
    
    # Simulate accumulated energy
    if not hasattr(generate_esp32_reading, 'total_energy'):
        generate_esp32_reading.total_energy = random.uniform(0, 10)  # Start with some energy
    
    # Add energy increment
    energy_increment = (power / 1000.0) / 3600.0  # Convert W to kWh per second
    generate_esp32_reading.total_energy += energy_increment
    
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
        "total_energy_kwh": round(generate_esp32_reading.total_energy, 6),
        "grid_frequency_hz": round(grid_frequency, 2),
        "power_factor": round(power_factor, 3),
        "ambient_temp_c": round(ambient_temp, 2),
        "irradiance_w_m2": round(irradiance, 2),
        "system_status": system_status,
        "efficiency": round(efficiency, 4)
    }
    
    return reading

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"   Devices: {data['devices_connected']}")
            print(f"   Supabase: {'Connected' if data['supabase_connected'] else 'Disconnected'}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_energy_data_endpoint():
    """Test sending energy data"""
    print("\n📊 Testing energy data endpoint...")
    
    reading = generate_esp32_reading("TEST-ESP32")
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/energy-data", json=reading, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Data sent: {result['message']}")
            print(f"   Power: {reading['power']}W")
            print(f"   Energy: {reading['total_energy_kwh']}kWh")
            return True
        else:
            print(f"❌ Failed to send data: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return False

def test_carbon_credits():
    """Test carbon credit calculation"""
    print("\n🌱 Testing carbon credit calculation...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/carbon-credits/TEST-ESP32", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Carbon credits calculated:")
            print(f"   Methodology: {data['methodology']}")
            print(f"   Energy Generated: {data['monitoring_data']['gross_generation_mwh']:.6f} MWh")
            print(f"   Carbon Credits: {data['calculations']['carbon_credits_generated']:.6f} tCO2")
            return True
        else:
            print(f"❌ Carbon credit calculation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Carbon credit error: {e}")
        return False

def test_guardian_integration():
    """Test Guardian integration"""
    print("\n🛡️ Testing Guardian integration...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/guardian/format/TEST-ESP32", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Guardian format generated:")
            print(f"   Document ID: {data['document']['id']}")
            print(f"   Owner: {data['owner']}")
            print(f"   Policy Tag: {data['policyTag']}")
            return True
        else:
            print(f"❌ Guardian format failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Guardian error: {e}")
        return False

def test_dashboard():
    """Test dashboard access"""
    print("\n📊 Testing dashboard...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard accessible")
            print(f"   URL: {BACKEND_URL}")
            return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def run_continuous_test(duration_minutes=5):
    """Run continuous data sending test"""
    print(f"\n🔄 Running continuous test for {duration_minutes} minutes...")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    count = 0
    
    while time.time() < end_time:
        reading = generate_esp32_reading("CONTINUOUS-TEST")
        
        try:
            response = requests.post(f"{BACKEND_URL}/api/energy-data", json=reading, timeout=5)
            if response.status_code == 200:
                count += 1
                print(f"📈 Sent #{count}: {reading['power']:.1f}W, {reading['total_energy_kwh']:.4f}kWh")
            else:
                print(f"❌ Failed to send data: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(5)  # Send every 5 seconds
    
    print(f"✅ Continuous test completed: {count} readings sent")

def main():
    """Main test function"""
    print("🧪 ESP32 Carbon Credit Backend - Complete System Test")
    print("=" * 60)
    print(f"🎯 Testing backend at: {BACKEND_URL}")
    print("")
    
    # Test all endpoints
    tests = [
        ("Health Check", test_health_check),
        ("Energy Data", test_energy_data_endpoint),
        ("Carbon Credits", test_carbon_credits),
        ("Guardian Integration", test_guardian_integration),
        ("Dashboard", test_dashboard)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready for production.")
        
        # Ask if user wants to run continuous test
        response = input("\n❓ Run continuous test? (y/N): ")
        if response.lower() == 'y':
            run_continuous_test()
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    print("\n🌐 Next steps:")
    print("1. Deploy to Railway using the deployment guide")
    print("2. Update ESP32 code with your Railway URL")
    print("3. Setup Supabase database using setup_supabase.py")
    print("4. Monitor your carbon credit generation!")

if __name__ == "__main__":
    main()