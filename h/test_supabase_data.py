#!/usr/bin/env python3
"""
Test Supabase Data
Verify that ESP32 data is being stored in Supabase
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def test_supabase_data():
    """Test Supabase data storage and retrieval"""
    
    print("🧪 Testing Supabase Data Storage")
    print("=" * 50)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Get total count
        result = supabase.table("energy_readings").select("*", count="exact").execute()
        total_count = result.count
        print(f"📊 Total readings in database: {total_count}")
        
        # Get unique devices
        devices_result = supabase.table("energy_readings").select("device_id").execute()
        unique_devices = list(set([row["device_id"] for row in devices_result.data]))
        print(f"📱 Unique devices: {unique_devices}")
        
        # Get latest 10 readings
        latest_result = supabase.table("energy_readings").select("*").order("timestamp", desc=True).limit(10).execute()
        print(f"\n📋 Latest 10 readings:")
        print("-" * 80)
        print(f"{'Timestamp':<20} {'Device':<12} {'Power':<8} {'Current':<8} {'Energy':<10}")
        print("-" * 80)
        
        for reading in latest_result.data:
            timestamp = reading.get("timestamp", "")[:19]  # Truncate timestamp
            device_id = reading.get("device_id", "")
            power = reading.get("power", 0)
            current = reading.get("current", 0)
            energy = reading.get("total_energy_kwh", 0)
            
            print(f"{timestamp:<20} {device_id:<12} {power:<8.1f} {current:<8.3f} {energy:<10.4f}")
        
        # Get readings for ESP32-001 specifically
        esp32_result = supabase.table("energy_readings").select("*").eq("device_id", "ESP32-001").order("timestamp", desc=True).limit(5).execute()
        print(f"\n🔌 Latest 5 readings from ESP32-001:")
        print("-" * 80)
        
        for reading in esp32_result.data:
            timestamp = reading.get("timestamp", "")[:19]
            power = reading.get("power", 0)
            current = reading.get("current", 0)
            energy = reading.get("total_energy_kwh", 0)
            irradiance = reading.get("irradiance_w_m2", 0)
            
            print(f"⚡ {timestamp} | {power:6.1f}W | {current:6.3f}A | {energy:8.4f}kWh | {irradiance:4.0f}W/m²")
        
        # Calculate some statistics
        if esp32_result.data:
            powers = [r.get("power", 0) for r in esp32_result.data]
            avg_power = sum(powers) / len(powers)
            max_power = max(powers)
            min_power = min(powers)
            
            print(f"\n📈 ESP32-001 Statistics (last 5 readings):")
            print(f"   Average Power: {avg_power:.1f}W")
            print(f"   Maximum Power: {max_power:.1f}W")
            print(f"   Minimum Power: {min_power:.1f}W")
        
        # Test carbon credit calculation
        if esp32_result.data:
            latest_reading = esp32_result.data[0]
            energy_kwh = latest_reading.get("total_energy_kwh", 0)
            
            # Morocco emission factor
            morocco_ef = 0.81  # tCO2/MWh
            export_mwh = energy_kwh / 1000.0 * 0.98  # 98% export efficiency
            carbon_credits = export_mwh * morocco_ef
            
            print(f"\n🌱 Carbon Credit Calculation:")
            print(f"   Total Energy: {energy_kwh:.4f} kWh")
            print(f"   Export Energy: {export_mwh:.6f} MWh")
            print(f"   Carbon Credits: {carbon_credits:.6f} tCO2")
        
        print(f"\n✅ Supabase integration is working perfectly!")
        print(f"🌐 View your data: https://supabase.com/dashboard/project/smemwzfjwhktvtqtdwta/editor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Supabase: {e}")
        return False

if __name__ == "__main__":
    test_supabase_data()