#!/usr/bin/env python3
"""
Create the correct sensor_readings table that the backend expects
"""

import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sensor_readings_table():
    """Create the sensor_readings table with sample data"""
    
    print("🔧 Creating sensor_readings table...")
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
        
        print("\n📋 Please create this table in Supabase SQL Editor:")
        print("=" * 50)
        
        sql_schema = """
-- Create sensor_readings table (matches backend expectations)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- ESP32 Device Data
    device_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Electrical Measurements
    current REAL NOT NULL DEFAULT 0.0,
    voltage REAL NOT NULL DEFAULT 220.0,
    power REAL NOT NULL DEFAULT 0.0,
    
    -- Power Analysis
    ac_power_kw REAL DEFAULT 0.0,
    total_energy_kwh REAL DEFAULT 0.0,
    grid_frequency_hz REAL DEFAULT 50.0,
    power_factor REAL DEFAULT 0.95,
    
    -- Environmental
    ambient_temp_c REAL DEFAULT 25.0,
    irradiance_w_m2 REAL DEFAULT 0.0,
    
    -- Status
    system_status INTEGER DEFAULT 1,
    efficiency REAL DEFAULT 0.96
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_timestamp ON sensor_readings(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_id ON sensor_readings(device_id);

-- Create guardian_submissions table
CREATE TABLE IF NOT EXISTS guardian_submissions (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Submission Details
    device_id TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    guardian_document_id TEXT,
    
    -- Status Tracking
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'VERIFIED', 'FAILED')),
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ,
    error_message TEXT,
    
    -- Data Period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Aggregated Data
    total_energy_kwh REAL NOT NULL DEFAULT 0.0,
    data_points_count INTEGER NOT NULL DEFAULT 0,
    verification_hash TEXT NOT NULL,
    
    -- Guardian Response
    guardian_response JSONB
);

-- Create indexes for guardian_submissions
CREATE INDEX IF NOT EXISTS idx_guardian_submissions_device_id ON guardian_submissions(device_id);
CREATE INDEX IF NOT EXISTS idx_guardian_submissions_status ON guardian_submissions(status);
CREATE INDEX IF NOT EXISTS idx_guardian_submissions_policy_id ON guardian_submissions(policy_id);

-- Insert sample data for testing
INSERT INTO sensor_readings (
    device_id, timestamp, current, voltage, power, ac_power_kw, 
    total_energy_kwh, grid_frequency_hz, power_factor, 
    ambient_temp_c, irradiance_w_m2, system_status, efficiency
) VALUES 
    ('ESP32_DEMO_001', NOW() - INTERVAL '2 hours', 4.89, 220.0, 1075.8, 1.076, 124.2, 49.9, 0.96, 27.8, 780.0, 1, 0.95),
    ('ESP32_DEMO_001', NOW() - INTERVAL '1 hour', 5.45, 220.0, 1199.0, 1.199, 125.5, 50.0, 0.95, 28.5, 850.0, 1, 0.96),
    ('ESP32_DEMO_001', NOW() - INTERVAL '30 minutes', 6.12, 220.0, 1346.4, 1.346, 126.2, 50.1, 0.94, 29.2, 920.0, 1, 0.97),
    ('ESP32_DEMO_001', NOW() - INTERVAL '15 minutes', 5.78, 220.0, 1271.6, 1.272, 126.8, 50.0, 0.95, 28.9, 865.0, 1, 0.96),
    ('ESP32_DEMO_001', NOW() - INTERVAL '5 minutes', 5.23, 220.0, 1150.6, 1.151, 127.2, 49.8, 0.96, 28.1, 825.0, 1, 0.95)
ON CONFLICT DO NOTHING;

-- Success message
SELECT 'VerifiedCC database schema created successfully!' as message;
"""
        
        print(sql_schema)
        print("=" * 50)
        
        print("\n🌐 Steps to create the tables:")
        print("1. Go to: https://supabase.com/dashboard/project/smemwzfjwhktvtqtdwta")
        print("2. Click 'SQL Editor' in the left sidebar")
        print("3. Paste the SQL above and click 'Run'")
        print("4. Then test with: python test_database_connection.py")
        
        # Try to insert sample data to test if table exists
        print("\n🧪 Testing if table already exists...")
        try:
            sample_data = {
                'device_id': 'ESP32_TEST_CONNECTION',
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
            
            result = supabase.table('sensor_readings').insert(sample_data).execute()
            
            if result.data:
                print("✅ SUCCESS: sensor_readings table already exists and working!")
                print(f"   Inserted test record with ID: {result.data[0]['id']}")
                
                # Clean up test record
                supabase.table('sensor_readings').delete().eq('device_id', 'ESP32_TEST_CONNECTION').execute()
                print("✅ Test record cleaned up")
                return True
            
        except Exception as e:
            if "Could not find the table" in str(e):
                print("❌ Table doesn't exist yet - please create it using the SQL above")
            else:
                print(f"⚠️  Error testing table: {e}")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_sensor_readings_table()