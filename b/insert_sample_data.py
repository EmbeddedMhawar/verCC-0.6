#!/usr/bin/env python3
"""
Insert Sample Data to Test Database Connection
This will help verify if the database is working
"""

import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def insert_sample_data():
    """Insert sample data to test database connection"""
    
    print("📊 Testing Database with Sample Data...")
    print("=" * 50)
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Missing Supabase credentials")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Connected to Supabase")
        
        # Sample energy data
        sample_data = {
            'device_id': 'ESP32_TEST_001',
            'timestamp': datetime.now().isoformat(),
            'current': 5.45,
            'voltage': 220.0,
            'power': 1199.0,
            'ac_power_kw': 1.199,
            'total_energy_kwh': 125.5,
            'grid_frequency_hz': 50.0,
            'power_factor': 0.95,
            'ambient_temp_c': 28.5,
            'irradiance_w_m2': 850.0,
            'system_status': 1,
            'efficiency': 0.96
        }
        
        print("\n📝 Attempting to insert sample data...")
        
        # Try to insert data - this will fail if table doesn't exist
        result = supabase.table('energy_data').insert(sample_data).execute()
        
        if result.data:
            print("✅ SUCCESS: Sample data inserted successfully!")
            print(f"   Record ID: {result.data[0]['id']}")
            print("   This means the energy_data table exists and is working")
            
            # Try to read it back
            print("\n📖 Reading data back...")
            read_result = supabase.table('energy_data').select('*').eq('device_id', 'ESP32_TEST_001').execute()
            
            if read_result.data:
                print(f"✅ Successfully read {len(read_result.data)} records")
                latest = read_result.data[0]
                print(f"   Device: {latest['device_id']}")
                print(f"   Power: {latest['power']}W")
                print(f"   Energy: {latest['total_energy_kwh']}kWh")
            
            return True
        else:
            print("⚠️  Insert returned no data")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Database test failed: {error_msg}")
        
        if "Could not find the table" in error_msg:
            print("\n🔧 SOLUTION: The energy_data table doesn't exist yet.")
            print("Please create it manually in Supabase:")
            print()
            print("1. Go to: https://supabase.com/dashboard")
            print("2. Select your project")
            print("3. Go to 'SQL Editor'")
            print("4. Run this SQL:")
            print()
            print("CREATE TABLE energy_data (")
            print("    id BIGSERIAL PRIMARY KEY,")
            print("    created_at TIMESTAMPTZ DEFAULT NOW(),")
            print("    device_id TEXT NOT NULL,")
            print("    timestamp TIMESTAMPTZ NOT NULL,")
            print("    current REAL NOT NULL DEFAULT 0.0,")
            print("    voltage REAL NOT NULL DEFAULT 220.0,")
            print("    power REAL NOT NULL DEFAULT 0.0,")
            print("    ac_power_kw REAL DEFAULT 0.0,")
            print("    total_energy_kwh REAL DEFAULT 0.0,")
            print("    grid_frequency_hz REAL DEFAULT 50.0,")
            print("    power_factor REAL DEFAULT 0.95,")
            print("    ambient_temp_c REAL DEFAULT 25.0,")
            print("    irradiance_w_m2 REAL DEFAULT 0.0,")
            print("    system_status INTEGER DEFAULT 1,")
            print("    efficiency REAL DEFAULT 0.96")
            print(");")
            
        return False

if __name__ == "__main__":
    success = insert_sample_data()
    if success:
        print("\n🎉 Database is working correctly!")
    else:
        print("\n⚠️  Database needs setup - follow the instructions above")