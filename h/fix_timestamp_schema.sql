-- Add new columns to handle timestamp properly
ALTER TABLE energy_readings 
ADD COLUMN IF NOT EXISTS server_received_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS esp32_timestamp TEXT;

-- Update existing records to have server_received_at
UPDATE energy_readings 
SET server_received_at = timestamp 
WHERE server_received_at IS NULL;

-- Create an index on server_received_at for better performance
CREATE INDEX IF NOT EXISTS idx_energy_readings_server_time ON energy_readings(server_received_at);

-- Create a view that shows both timestamps
CREATE OR REPLACE VIEW energy_readings_with_times AS
SELECT 
    *,
    timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'local' as local_timestamp,
    server_received_at AT TIME ZONE 'UTC' AT TIME ZONE 'local' as local_server_time
FROM energy_readings
ORDER BY server_received_at DESC;