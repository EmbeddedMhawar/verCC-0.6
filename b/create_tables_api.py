#!/usr/bin/env python3
"""
Create Database Tables via Supabase REST API
Alternative approach to create tables programmatically
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables_via_api():
    """Create tables using Supabase REST API"""
    
    print("🔧 Creating Database Tables via API...")
    print("=" * 50)
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Missing Supabase credentials")
        return False
    
    # Extract base URL for SQL execution
    base_url = SUPABASE_URL.replace('/rest/v1', '')
    sql_url = f"{base_url}/rest/v1/rpc/exec_sql"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # SQL to create energy_data table
    create_energy_table_sql = """
    CREATE TABLE IF NOT EXISTS energy_data (
        id BIGSERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        device_id TEXT NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        current REAL NOT NULL DEFAULT 0.0,
        voltage REAL NOT NULL DEFAULT 220.0,
        power REAL NOT NULL DEFAULT 0.0,
        ac_power_kw REAL DEFAULT 0.0,
        total_energy_kwh REAL DEFAULT 0.0,
        grid_frequency_hz REAL DEFAULT 50.0,
        power_factor REAL DEFAULT 0.95,
        ambient_temp_c REAL DEFAULT 25.0,
        irradiance_w_m2 REAL DEFAULT 0.0,
        system_status INTEGER DEFAULT 1,
        efficiency REAL DEFAULT 0.96
    );
    """
    
    try:
        print("📊 Creating energy_data table...")
        response = requests.post(sql_url, json={'sql': create_energy_table_sql}, headers=headers)
        
        if response.status_code == 200:
            print("✓ energy_data table created successfully")
        else:
            print(f"⚠️  API response: {response.status_code} - {response.text}")
            print("   This might be normal if the endpoint doesn't exist")
            
    except Exception as e:
        print(f"⚠️  API method not available: {e}")
    
    print("\n📋 Alternative: Manual Database Setup")
    print("=" * 50)
    print("Since the API approach may not work, please:")
    print()
    print("1. Visit your Supabase dashboard:")
    print(f"   https://supabase.com/dashboard/project/{SUPABASE_URL.split('//')[1].split('.')[0]}")
    print()
    print("2. Go to 'SQL Editor' and run this SQL:")
    print()
    print("-- Create energy_data table")
    print(create_energy_table_sql)
    print()
    print("-- Create guardian_submissions table")
    print("""CREATE TABLE IF NOT EXISTS guardian_submissions (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    device_id TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    guardian_document_id TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ,
    error_message TEXT,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    total_energy_kwh REAL NOT NULL DEFAULT 0.0,
    data_points_count INTEGER NOT NULL DEFAULT 0,
    verification_hash TEXT NOT NULL,
    guardian_response JSONB
);""")
    print()
    print("-- Add sample data")
    print("""INSERT INTO energy_data (device_id, timestamp, current, voltage, power, ac_power_kw, total_energy_kwh, grid_frequency_hz, power_factor, ambient_temp_c, irradiance_w_m2, system_status, efficiency) VALUES 
('ESP32_DEMO_001', NOW(), 5.45, 220.0, 1199.0, 1.199, 125.5, 50.0, 0.95, 28.5, 850.0, 1, 0.96);""")
    
    return True

if __name__ == "__main__":
    create_tables_via_api()