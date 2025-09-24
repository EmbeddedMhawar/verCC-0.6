-- Guardian Submissions Database Migration (Alternative with Devices Table)
-- This version creates a devices table to maintain referential integrity

-- First, create a devices table to store unique device information
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    device_name TEXT,
    device_type TEXT DEFAULT 'ESP32',
    location TEXT,
    capacity_kw REAL,
    status TEXT DEFAULT 'ACTIVE'
);

-- Insert existing devices from sensor_readings
INSERT INTO devices (device_id)
SELECT DISTINCT device_id 
FROM sensor_readings 
WHERE device_id NOT IN (SELECT device_id FROM devices)
ON CONFLICT (device_id) DO NOTHING;

-- Guardian submissions tracking table
CREATE TABLE IF NOT EXISTS guardian_submissions (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Submission details
    device_id TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    guardian_document_id TEXT,
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'PENDING',
    submitted_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    error_message TEXT,
    
    -- Energy data reference
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    total_energy_kwh REAL NOT NULL,
    data_points_count INTEGER NOT NULL,
    verification_hash TEXT NOT NULL,
    
    -- Guardian response data
    guardian_response JSONB,
    
    -- Foreign key constraint (references devices table)
    CONSTRAINT fk_guardian_submissions_device 
        FOREIGN KEY (device_id) 
        REFERENCES devices(device_id) 
        ON DELETE CASCADE
);

-- Indexes for optimal query performance
CREATE INDEX IF NOT EXISTS idx_guardian_submissions_device_status 
    ON guardian_submissions(device_id, status);

CREATE INDEX IF NOT EXISTS idx_guardian_submissions_policy 
    ON guardian_submissions(policy_id, submitted_at DESC);

CREATE INDEX IF NOT EXISTS idx_guardian_submissions_status 
    ON guardian_submissions(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_guardian_submissions_period 
    ON guardian_submissions(period_start, period_end);

-- Add comments for documentation
COMMENT ON TABLE devices IS 'Master table of ESP32 devices';
COMMENT ON TABLE guardian_submissions IS 'Tracks Guardian blockchain submissions for energy data verification';
COMMENT ON COLUMN guardian_submissions.device_id IS 'ESP32 device identifier from devices table';
COMMENT ON COLUMN guardian_submissions.policy_id IS 'Guardian policy ID used for verification';
COMMENT ON COLUMN guardian_submissions.guardian_document_id IS 'Guardian-assigned document ID for tracking';
COMMENT ON COLUMN guardian_submissions.status IS 'Submission status: PENDING, PROCESSING, VERIFIED, FAILED';
COMMENT ON COLUMN guardian_submissions.verification_hash IS 'Cryptographic hash of submitted energy data';
COMMENT ON COLUMN guardian_submissions.guardian_response IS 'Full Guardian API response data in JSON format';