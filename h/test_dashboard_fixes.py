#!/usr/bin/env python3
"""
Test Dashboard Fixes
Test the timestamp and connection status fixes
"""

import requests
import json
import time
from datetime import datetime, timezone

BACKEND_URL = "http://localhost:5000"

def test_timestamp_formats():
    """Test different timestamp formats"""
    
    print("🧪 Testing Timestamp Formats")
    print("=" * 40)
    
    # Test different timestamp formats
    test_readings = [
        {
            "device_id": "TEST-TIMESTAMP",
            "timestamp": datetime.now(timezone.utc).isoformat(),  # ISO format
            "current": 1.0,
            "voltage": 220.0,
            "power": 220.0,
            "ac_power_kw": 0.22,
            "total_energy_kwh": 1.0,
            "grid_frequency_hz": 50.0,
            "power_factor": 0.95,
            "ambient_temp_c": 25.0,
            "irradiance_w_m2": 800.0,
            "system_status": 1,
            "efficiency": 0.96
        },
        {
            "device_id": "TEST-TIMESTAMP",
            "timestamp": "2025-01-20T10:30:00Z",  # Simple ISO format
            "current": 1.5,
            "voltage": 220.0,
            "power": 330.0,
            "ac_power_kw": 0.33,
            "total_energy_kwh": 1.1,
            "grid_frequency_hz": 50.0,
            "power_factor": 0.95,
            "ambient_temp_c": 26.0,
            "irradiance_w_m2": 850.0,
            "system_status": 1,
            "efficiency": 0.96
        },
        {
            "device_id": "TEST-TIMESTAMP",
            "timestamp": "invalid-timestamp",  # Invalid timestamp
            "current": 2.0,
            "voltage": 220.0,
            "power": 440.0,
            "ac_power_kw": 0.44,
            "total_energy_kwh": 1.2,
            "grid_frequency_hz": 50.0,
            "power_factor": 0.95,
            "ambient_temp_c": 27.0,
            "irradiance_w_m2": 900.0,
            "system_status": 1,
            "efficiency": 0.96
        }
    ]
    
    for i, reading in enumerate(test_readings):
        try:
            response = requests.post(f"{BACKEND_URL}/api/energy-data", json=reading, timeout=5)
            if response.status_code == 200:
                print(f"✅ Test {i+1}: {reading['timestamp'][:20]}... - Sent successfully")
            else:
                print(f"❌ Test {i+1}: Failed - {response.status_code}")
        except Exception as e:
            print(f"❌ Test {i+1}: Error - {e}")
        
        time.sleep(2)  # Wait 2 seconds between tests

def test_connection_timeout():
    """Test connection timeout detection"""
    
    print("\n🧪 Testing Connection Timeout")
    print("=" * 40)
    
    # Send data for a test device
    reading = {
        "device_id": "TEST-TIMEOUT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current": 3.0,
        "voltage": 220.0,
        "power": 660.0,
        "ac_power_kw": 0.66,
        "total_energy_kwh": 2.0,
        "grid_frequency_hz": 50.0,
        "power_factor": 0.95,
        "ambient_temp_c": 28.0,
        "irradiance_w_m2": 950.0,
        "system_status": 1,
        "efficiency": 0.96
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/energy-data", json=reading, timeout=5)
        if response.status_code == 200:
            print("✅ Test device data sent")
            
            # Check health endpoint
            health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"📊 Online devices: {health_data.get('online_devices', [])}")
                print(f"📊 Offline devices: {health_data.get('offline_devices', [])}")
                
                print("\n⏳ Waiting 35 seconds to test timeout detection...")
                print("(The device should appear offline after 30 seconds)")
                
                # Wait for timeout
                for i in range(35):
                    print(f"⏱️  {35-i} seconds remaining...", end='\r')
                    time.sleep(1)
                
                print("\n")
                
                # Check health again
                health_response2 = requests.get(f"{BACKEND_URL}/health", timeout=5)
                if health_response2.status_code == 200:
                    health_data2 = health_response2.json()
                    print(f"📊 Online devices: {health_data2.get('online_devices', [])}")
                    print(f"📊 Offline devices: {health_data2.get('offline_devices', [])}")
                    
                    if "TEST-TIMEOUT" in health_data2.get('offline_devices', []):
                        print("✅ Timeout detection working correctly!")
                    else:
                        print("❌ Timeout detection not working")
            
        else:
            print(f"❌ Failed to send test data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection timeout test error: {e}")

def main():
    """Main test function"""
    print("🧪 Dashboard Fixes Test Suite")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding correctly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Please make sure the server is running: python main_with_supabase.py")
        return
    
    # Run tests
    test_timestamp_formats()
    
    # Ask user if they want to test timeout (takes 35 seconds)
    response = input("\n❓ Test connection timeout detection? (takes 35 seconds) (y/N): ")
    if response.lower() == 'y':
        test_connection_timeout()
    
    print("\n🎉 Test completed!")
    print("📊 Check your dashboard at: http://localhost:5000")
    print("💡 The fixes should now show:")
    print("   - Proper timestamps instead of 'Invalid Date'")
    print("   - Device online/offline status")
    print("   - Last seen time for each device")

if __name__ == "__main__":
    main()