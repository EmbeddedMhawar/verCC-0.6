-- Guardian Submissions Database Migration
-- Add Guardian submissions tracking table to existing schema

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
    guardian_response JSONB
    
    -- Note: No foreign key constraint to sensor_readings.device_id
    -- because device_id is not unique in sensor_readings (one device has many readings)
    -- The relationship is maintained logically through application code
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
COMMENT ON TABLE guardian_submissions IS 'Tracks Guardian blockchain submissions for energy data verification';
COMMENT ON COLUMN guardian_submissions.device_id IS 'ESP32 device identifier from sensor_readings table';
COMMENT ON COLUMN guardian_submissions.policy_id IS 'Guardian policy ID used for verification';
COMMENT ON COLUMN guardian_submissions.guardian_document_id IS 'Guardian-assigned document ID for tracking';
COMMENT ON COLUMN guardian_submissions.status IS 'Submission status: PENDING, PROCESSING, VERIFIED, FAILED';
COMMENT ON COLUMN guardian_submissions.verification_hash IS 'Cryptographic hash of submitted energy data';
COMMENT ON COLUMN guardian_submissions.guardian_response IS 'Full Guardian API response data in JSON format';