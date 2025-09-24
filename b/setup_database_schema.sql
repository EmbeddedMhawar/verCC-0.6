-- VerifiedCC Database Schema Setup
-- Run this in your Supabase SQL Editor to create all required tables

-- 1. Energy Data Table (matches backend expectations)
CREATE TABLE IF NOT EXISTS energy_data (
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

-- 2. Guardian Submissions Table
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

-- 3. Create Essential Indexes
CREATE INDEX IF NOT EXISTS idx_energy_data_device_timestamp ON energy_data(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_energy_data_timestamp ON energy_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_energy_data_device_id ON energy_data(device_id);

CREATE INDEX IF NOT EXISTS idx_guardian_submissions_device_id ON guardian_submissions(device_id);
CREATE INDEX IF NOT EXISTS idx_guardian_submissions_status ON guardian_submissions(status);
CREATE INDEX IF NOT EXISTS idx_guardian_submissions_policy_id ON guardian_submissions(policy_id);
CREATE INDEX IF NOT EXISTS idx_guardian_submissions_period ON guardian_submissions(period_start, period_end);

-- 4. Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE energy_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE guardian_submissions ENABLE ROW LEVEL SECURITY;

-- 5. Create policies for authenticated access (adjust as needed)
CREATE POLICY "Enable read access for authenticated users" ON energy_data
    FOR SELECT USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable insert access for authenticated users" ON energy_data
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable read access for authenticated users" ON guardian_submissions
    FOR SELECT USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable insert access for authenticated users" ON guardian_submissions
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable update access for authenticated users" ON guardian_submissions
    FOR UPDATE USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

-- 6. Insert some sample data for testing (optional)
INSERT INTO energy_data (
    device_id, timestamp, current, voltage, power, ac_power_kw, 
    total_energy_kwh, grid_frequency_hz, power_factor, 
    ambient_temp_c, irradiance_w_m2, system_status, efficiency
) VALUES 
    ('ESP32_DEMO_001', NOW() - INTERVAL '1 hour', 5.45, 220.0, 1199.0, 1.199, 
     125.5, 50.0, 0.95, 28.5, 850.0, 1, 0.96),
    ('ESP32_DEMO_001', NOW() - INTERVAL '30 minutes', 6.12, 220.0, 1346.4, 1.346, 
     126.2, 50.1, 0.94, 29.2, 920.0, 1, 0.97),
    ('ESP32_DEMO_001', NOW() - INTERVAL '15 minutes', 4.89, 220.0, 1075.8, 1.076, 
     126.8, 49.9, 0.96, 27.8, 780.0, 1, 0.95)
ON CONFLICT DO NOTHING;

-- Success message
SELECT 'VerifiedCC database schema created successfully!' as message;