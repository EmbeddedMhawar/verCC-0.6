-- Create the energy_readings table in Supabase
CREATE TABLE IF NOT EXISTS energy_readings (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current DECIMAL(10, 6) NOT NULL,
    voltage DECIMAL(10, 2) NOT NULL,
    power DECIMAL(10, 2) NOT NULL,
    ac_power_kw DECIMAL(10, 6) NOT NULL,
    total_energy_kwh DECIMAL(12, 6) NOT NULL,
    grid_frequency_hz DECIMAL(5, 2) NOT NULL,
    power_factor DECIMAL(5, 3) NOT NULL,
    ambient_temp_c DECIMAL(5, 2) NOT NULL,
    irradiance_w_m2 DECIMAL(8, 2) NOT NULL,
    system_status INTEGER NOT NULL,
    efficiency DECIMAL(5, 4) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_energy_readings_device_id ON energy_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp ON energy_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_energy_readings_device_timestamp ON energy_readings(device_id, timestamp);

-- Create a view for latest readings per device
CREATE OR REPLACE VIEW latest_device_readings AS
SELECT DISTINCT ON (device_id) 
    device_id,
    timestamp,
    current,
    voltage,
    power,
    ac_power_kw,
    total_energy_kwh,
    grid_frequency_hz,
    power_factor,
    ambient_temp_c,
    irradiance_w_m2,
    system_status,
    efficiency,
    created_at
FROM energy_readings
ORDER BY device_id, timestamp DESC;

-- Create a function to calculate carbon credits
CREATE OR REPLACE FUNCTION calculate_carbon_credits(
    device_id_param TEXT,
    start_date TIMESTAMPTZ DEFAULT NULL,
    end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
    device_id TEXT,
    total_energy_mwh DECIMAL,
    carbon_credits_tco2 DECIMAL,
    reporting_period_start TIMESTAMPTZ,
    reporting_period_end TIMESTAMPTZ
) AS $$
DECLARE
    morocco_emission_factor DECIMAL := 0.81; -- tCO2/MWh
    export_efficiency DECIMAL := 0.98; -- 98% export efficiency
BEGIN
    -- Set default date range if not provided (last 30 days)
    IF start_date IS NULL THEN
        start_date := NOW() - INTERVAL '30 days';
    END IF;
    
    IF end_date IS NULL THEN
        end_date := NOW();
    END IF;
    
    RETURN QUERY
    SELECT 
        device_id_param,
        (MAX(er.total_energy_kwh) - MIN(er.total_energy_kwh)) / 1000.0 * export_efficiency AS total_energy_mwh,
        ((MAX(er.total_energy_kwh) - MIN(er.total_energy_kwh)) / 1000.0 * export_efficiency * morocco_emission_factor) AS carbon_credits_tco2,
        start_date AS reporting_period_start,
        end_date AS reporting_period_end
    FROM energy_readings er
    WHERE er.device_id = device_id_param
        AND er.timestamp BETWEEN start_date AND end_date
    GROUP BY device_id_param;
END;
$$ LANGUAGE plpgsql;

-- Create RLS (Row Level Security) policies if needed
-- ALTER TABLE energy_readings ENABLE ROW LEVEL SECURITY;

-- Example policy (uncomment if you need user-based access control)
-- CREATE POLICY "Users can view their own device data" ON energy_readings
--     FOR SELECT USING (auth.uid()::text = device_owner_id);

-- Create a materialized view for hourly aggregations (for better performance on large datasets)
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_energy_summary AS
SELECT 
    device_id,
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(current) AS avg_current,
    AVG(voltage) AS avg_voltage,
    AVG(power) AS avg_power,
    MAX(total_energy_kwh) - MIN(total_energy_kwh) AS energy_generated_kwh,
    AVG(grid_frequency_hz) AS avg_frequency,
    AVG(power_factor) AS avg_power_factor,
    AVG(ambient_temp_c) AS avg_temperature,
    AVG(irradiance_w_m2) AS avg_irradiance,
    AVG(efficiency) AS avg_efficiency,
    COUNT(*) AS reading_count
FROM energy_readings
GROUP BY device_id, DATE_TRUNC('hour', timestamp)
ORDER BY device_id, hour;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_hourly_summary_device_hour ON hourly_energy_summary(device_id, hour);

-- Refresh the materialized view (run this periodically)
-- REFRESH MATERIALIZED VIEW hourly_energy_summary;