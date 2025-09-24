-- Quick Setup: ESP32 Sensor Readings Table
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- ESP32 Device Data
    device_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Electrical Measurements
    current REAL NOT NULL DEFAULT 0.0,
    voltage REAL NOT NULL DEFAULT 220.0,
    power REAL NOT NULL,
    
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

-- Essential indexes
CREATE INDEX IF NOT EXISTS idx_device_timestamp ON sensor_readings(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_readings(timestamp DESC);