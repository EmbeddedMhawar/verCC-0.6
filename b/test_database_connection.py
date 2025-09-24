#!/usr/bin/env python3
"""
Database Connection Test Script
Tests Supabase connection and basic operations
"""

import os
import sys
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test Supabase database connection and basic operations"""
    
    print("🔍 Testing VerifiedCC Database Connection...")
    print("=" * 50)
    
    # Get Supabase credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Missing Supabase credentials")
        print("   SUPABASE_URL:", "✓ Set" if SUPABASE_URL else "❌ Missing")
        print("   SUPABASE_KEY:", "✓ Set" if SUPABASE_KEY else "❌ Missing")
        return False
    
    print("✓ Environment variables loaded")
    print(f"  SUPABASE_URL: {SUPABASE_URL}")
    print(f"  SUPABASE_KEY: {SUPABASE_KEY[:20]}...")
    
    try:
        # Initialize Supabase client
        print("\n🔗 Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client initialized")
        
        # Test 1: Check if sensor_readings table exists and get schema
        print("\n📊 Testing sensor_readings table...")
        try:
            # Try to get table info by querying with limit 0
            result = supabase.table('sensor_readings').select('*').limit(0).execute()
            print("✓ sensor_readings table exists and is accessible")
        except Exception as e:
            print(f"❌ sensor_readings table error: {e}")
            return False
        
        # Test 2: Get recent sensor data
        print("\n📈 Checking recent sensor data...")
        try:
            recent_data = supabase.table('sensor_readings').select('*').order('created_at', desc=True).limit(5).execute()
            
            if recent_data.data:
                print(f"✓ Found {len(recent_data.data)} recent records")
                latest = recent_data.data[0]
                print(f"  Latest record: Device {latest.get('device_id', 'Unknown')} at {latest.get('timestamp', 'Unknown time')}")
                print(f"  Power: {latest.get('power', 0):.2f}W, Energy: {latest.get('total_energy_kwh', 0):.3f}kWh")
            else:
                print("⚠️  No sensor data found in database")
                print("   This is normal if ESP32 hasn't sent data yet")
        except Exception as e:
            print(f"❌ Error reading sensor data: {e}")
            return False
        
        # Test 3: Check guardian_submissions table
        print("\n🛡️  Testing guardian_submissions table...")
        try:
            guardian_result = supabase.table('guardian_submissions').select('*').limit(0).execute()
            print("✓ guardian_submissions table exists and is accessible")
            
            # Get submission count
            submissions = supabase.table('guardian_submissions').select('*').limit(5).execute()
            if submissions.data:
                print(f"✓ Found {len(submissions.data)} Guardian submissions")
            else:
                print("ℹ️  No Guardian submissions yet (normal for new setup)")
                
        except Exception as e:
            print(f"❌ guardian_submissions table error: {e}")
            print("   You may need to run the migration script")
            return False
        
        # Test 4: Test write permissions (insert a test record)
        print("\n✍️  Testing write permissions...")
        try:
            test_data = {
                'device_id': 'TEST_CONNECTION',
                'timestamp': datetime.now().isoformat(),
                'current': 0.0,
                'voltage': 220.0,
                'power': 0.0,
                'ac_power_kw': 0.0,
                'total_energy_kwh': 0.0,
                'grid_frequency_hz': 50.0,
                'power_factor': 1.0,
                'ambient_temp_c': 25.0,
                'irradiance_w_m2': 0.0,
                'system_status': 1,
                'efficiency': 0.0
            }
            
            # Insert test record
            insert_result = supabase.table('sensor_readings').insert(test_data).execute()
            
            if insert_result.data:
                print("✓ Write permissions working - test record inserted")
                
                # Clean up - delete the test record
                test_id = insert_result.data[0]['id']
                supabase.table('sensor_readings').delete().eq('id', test_id).execute()
                print("✓ Test record cleaned up")
            else:
                print("⚠️  Insert returned no data")
                
        except Exception as e:
            print(f"❌ Write permission test failed: {e}")
            return False
        
        # Test 5: Check database statistics
        print("\n📊 Database Statistics:")
        try:
            # Count total records
            total_sensor = supabase.table('sensor_readings').select('id', count='exact').execute()
            total_submissions = supabase.table('guardian_submissions').select('id', count='exact').execute()
            
            print(f"  Total sensor records: {total_sensor.count}")
            print(f"  Total Guardian submissions: {total_submissions.count}")
            
        except Exception as e:
            print(f"⚠️  Could not get statistics: {e}")
        
        print("\n🎉 Database Connection Test PASSED!")
        print("   All tests completed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Database Connection Test FAILED!")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)