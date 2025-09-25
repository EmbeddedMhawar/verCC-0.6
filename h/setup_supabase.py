#!/usr/bin/env python3
"""
Supabase Database Setup Script
Creates the necessary tables and functions for ESP32 Carbon Credit Backend
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def setup_database():
    """Setup Supabase database with required tables and functions"""
    
    print("🔧 Setting up Supabase database...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Read the SQL setup file
        with open("supabase_setup.sql", "r") as f:
            sql_commands = f.read()
        
        # Note: Supabase Python client doesn't support raw SQL execution
        # You need to run the SQL commands manually in Supabase SQL Editor
        
        print("📋 Database setup instructions:")
        print("1. Go to your Supabase project: https://supabase.com/dashboard/project/smemwzfjwhktvtqtdwta")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of 'supabase_setup.sql'")
        print("4. Run the SQL commands")
        print("")
        print("🔗 Direct link: https://supabase.com/dashboard/project/smemwzfjwhktvtqtdwta/sql")
        print("")
        print("✅ After running the SQL, your database will have:")
        print("   - energy_readings table")
        print("   - latest_device_readings view")
        print("   - hourly_energy_summary materialized view")
        print("   - calculate_carbon_credits() function")
        print("   - Optimized indexes for performance")
        
        # Test the connection by trying to access a table
        try:
            result = supabase.table("energy_readings").select("*").limit(1).execute()
            print("✅ Database tables are ready!")
            return True
        except Exception as e:
            if "relation \"energy_readings\" does not exist" in str(e):
                print("⚠️  Please run the SQL setup first (see instructions above)")
                return False
            else:
                print(f"❌ Database error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

def test_database():
    """Test database connection and functionality"""
    
    print("\n🧪 Testing database connection...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test insert
        test_data = {
            "device_id": "TEST-001",
            "timestamp": "2025-01-20T10:30:00Z",
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
        
        result = supabase.table("energy_readings").insert(test_data).execute()
        print("✅ Test data inserted successfully")
        
        # Test select
        result = supabase.table("energy_readings").select("*").eq("device_id", "TEST-001").execute()
        if result.data:
            print("✅ Test data retrieved successfully")
            
            # Clean up test data
            supabase.table("energy_readings").delete().eq("device_id", "TEST-001").execute()
            print("✅ Test data cleaned up")
            
            return True
        else:
            print("❌ Failed to retrieve test data")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🌞 ESP32 Carbon Credit Backend - Supabase Setup")
    print("=" * 60)
    
    # Check environment variables
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    print(f"📊 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 API Key: {SUPABASE_KEY[:20]}...")
    print("")
    
    # Setup database
    if setup_database():
        print("\n" + "=" * 60)
        
        # Test database
        if test_database():
            print("\n🎉 Supabase setup completed successfully!")
            print("🚀 Your backend is ready to receive ESP32 data")
        else:
            print("\n⚠️  Database setup incomplete - please run the SQL commands manually")
    else:
        print("\n❌ Setup failed - please check your credentials and try again")

if __name__ == "__main__":
    main()