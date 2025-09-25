#!/usr/bin/env python3
"""
Test Timestamp Fix
Verify that timestamps are now correct in the database
"""

import requests
import json
from datetime import datetime, timezone
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKEND_URL = "http://localhost:5000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def test_timestamp_fix():
    """Test that timestamps are now correct"""
    
    print("🧪 Testing Timestamp Fix")
    print("=" * 40)
    
    # Get current local time
    local_time = datetime.now()
    print(f"🕐 Current local time: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Send test data
    test_reading = {
        "device_id": "TEST-TIMESTAMP-FIX",
        "timestamp": "2025-01-20T00:02:11Z",  # This is the fake ESP32 timestamp
        "current": 2.5,
        "voltage": 220.0,
        "power": 550.0,
        "ac_power_kw": 0.55,
        "total_energy_kwh": 1.234,
        "grid_frequency_hz": 50.0,
        "power_factor": 0.95,
        "ambient_temp_c": 25.5,
        "irradiance_w_m2": 850.0,
        "system_status": 1,
        "efficiency": 0.96
    }
    
    try:
        print(f"📤 Sending test data with fake timestamp: {test_reading['timestamp']}")
        response = requests.post(f"{BACKEND_URL}/api/energy-data", json=test_reading, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            server_time = result.get("server_time", "")
            print(f"✅ Data sent successfully")
            print(f"🕐 Server corrected timestamp: {server_time}")
            
            # Check what's in Supabase
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Get the latest record for our test device
            db_result = supabase.table("energy_readings").select("*").eq("device_id", "TEST-TIMESTAMP-FIX").order("timestamp", desc=True).limit(1).execute()
            
            if db_result.data:
                record = db_result.data[0]
                db_timestamp = record.get("timestamp", "")
                esp32_timestamp = record.get("esp32_timestamp", "")
                server_received_at = record.get("server_received_at", "")
                
                print(f"\n📊 Database Record:")
                print(f"   Database timestamp: {db_timestamp}")
                print(f"   ESP32 timestamp: {esp32_timestamp}")
                print(f"   Server received at: {server_received_at}")
                
                # Parse and display in local time
                try:
                    db_time = datetime.fromisoformat(db_timestamp.replace('Z', '+00:00'))
                    local_db_time = db_time.astimezone()
                    print(f"   Local time: {local_db_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    
                    # Check if timestamp is reasonable (within last minute)
                    time_diff = abs((local_time - local_db_time.replace(tzinfo=None)).total_seconds())
                    if time_diff < 60:
                        print(f"✅ Timestamp is correct! (within {time_diff:.1f} seconds)")
                    else:
                        print(f"❌ Timestamp is off by {time_diff:.1f} seconds")
                        
                except Exception as e:
                    print(f"❌ Error parsing timestamp: {e}")
            else:
                print("❌ No record found in database")
                
            # Clean up test data
            supabase.table("energy_readings").delete().eq("device_id", "TEST-TIMESTAMP-FIX").execute()
            print("🧹 Cleaned up test data")
            
        else:
            print(f"❌ Failed to send data: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

def check_recent_data():
    """Check recent ESP32-001 data timestamps"""
    
    print("\n🔍 Checking Recent ESP32-001 Data")
    print("=" * 40)
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get latest 5 records
        result = supabase.table("energy_readings").select("*").eq("device_id", "ESP32-001").order("timestamp", desc=True).limit(5).execute()
        
        if result.data:
            print("📊 Latest 5 ESP32-001 records:")
            print("-" * 60)
            print(f"{'Timestamp':<20} {'Power':<8} {'Local Time':<20}")
            print("-" * 60)
            
            for record in result.data:
                timestamp = record.get("timestamp", "")
                power = record.get("power", 0)
                
                try:
                    # Convert to local time
                    db_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    local_time = db_time.astimezone()
                    local_str = local_time.strftime('%H:%M:%S')
                    
                    print(f"{timestamp[:19]:<20} {power:<8.1f} {local_str:<20}")
                except:
                    print(f"{timestamp[:19]:<20} {power:<8.1f} {'Parse Error':<20}")
        else:
            print("No ESP32-001 data found")
            
    except Exception as e:
        print(f"❌ Error checking data: {e}")

def main():
    """Main test function"""
    print("🕐 Timestamp Fix Test Suite")
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
    test_timestamp_fix()
    check_recent_data()
    
    print("\n🎉 Timestamp fix test completed!")
    print("📊 Check your dashboard at: http://localhost:5000")
    print("💡 Timestamps should now show your local time correctly")

if __name__ == "__main__":
    main()