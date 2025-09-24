# Database Schema for ESP32 Energy Data

## Quick Setup

### 1. Create Table in Supabase

Copy and paste this SQL into your Supabase SQL Editor:

```sql
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
```

## Table Structure

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `id` | BIGSERIAL | AUTO | Primary key |
| `created_at` | TIMESTAMPTZ | NOW() | Record creation time |
| `device_id` | TEXT | - | ESP32 device identifier |
| `timestamp` | TIMESTAMPTZ | - | Measurement timestamp |
| `current` | REAL | 0.0 | Current in Amperes |
| `voltage` | REAL | 220.0 | Voltage in Volts |
| `power` | REAL | - | Power in Watts (required) |
| `ac_power_kw` | REAL | 0.0 | AC Power in Kilowatts |
| `total_energy_kwh` | REAL | 0.0 | Cumulative energy in kWh |
| `grid_frequency_hz` | REAL | 50.0 | Grid frequency in Hz |
| `power_factor` | REAL | 0.95 | Power factor (0.0-1.0) |
| `ambient_temp_c` | REAL | 25.0 | Ambient temperature in °C |
| `irradiance_w_m2` | REAL | 0.0 | Solar irradiance in W/m² |
| `system_status` | INTEGER | 1 | System status (1=OK, 0=Error) |
| `efficiency` | REAL | 0.96 | System efficiency (0.0-1.0) |

## ESP32 Data Format

Your ESP32 should send JSON data in this format:

```json
{
  "device_id": "ESP32_001",
  "timestamp": "2025-01-20T10:30:00Z",
  "current": 5.2,
  "voltage": 220.0,
  "power": 1144.0,
  "ac_power_kw": 1.144,
  "total_energy_kwh": 25.6,
  "grid_frequency_hz": 50.0,
  "power_factor": 0.95,
  "ambient_temp_c": 28.5,
  "irradiance_w_m2": 850.0,
  "system_status": 1,
  "efficiency": 0.96
}
```

### Required Fields
- `device_id` - Unique identifier for your ESP32
- `timestamp` - ISO 8601 timestamp
- `power` - Power measurement in Watts

### Optional Fields
All other fields have default values and are optional.

## API Endpoint

Send ESP32 data to:
```
POST http://localhost:5000/api/energy-data
Content-Type: application/json
```

## Database Queries

### Get Latest Reading
```sql
SELECT * FROM sensor_readings 
ORDER BY timestamp DESC 
LIMIT 1;
```

### Get Device History
```sql
SELECT * FROM sensor_readings 
WHERE device_id = 'ESP32_001' 
ORDER BY timestamp DESC 
LIMIT 100;
```

### Daily Energy Summary
```sql
SELECT 
    device_id,
    DATE(timestamp) as date,
    COUNT(*) as readings,
    AVG(power) as avg_power,
    MAX(total_energy_kwh) - MIN(total_energy_kwh) as daily_energy
FROM sensor_readings 
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY device_id, DATE(timestamp)
ORDER BY date DESC;
```

## Indexes

The table includes these indexes for optimal performance:

1. **Primary Key**: `id` (automatic)
2. **Device + Timestamp**: `(device_id, timestamp DESC)` - for device history queries
3. **Timestamp**: `(timestamp DESC)` - for latest data queries

## Data Types Explained

### REAL vs NUMERIC
- **REAL**: 4-byte floating point, sufficient for sensor data
- **TIMESTAMPTZ**: Timezone-aware timestamp (recommended)
- **TEXT**: Variable-length string for device IDs
- **INTEGER**: 4-byte integer for status codes

### Default Values
- **Voltage**: 220V (Morocco electrical standard)
- **Frequency**: 50Hz (Morocco electrical standard)
- **Power Factor**: 0.95 (typical for solar installations)
- **Efficiency**: 0.96 (typical solar panel efficiency)
- **Temperature**: 25°C (room temperature baseline)

## Troubleshooting

### Common Issues

1. **Table doesn't exist**
   ```
   Run: create_table.sql in Supabase SQL Editor
   ```

2. **Permission denied**
   ```
   Check: Supabase service key has table access
   ```

3. **Invalid timestamp format**
   ```
   Use: ISO 8601 format (2025-01-20T10:30:00Z)
   ```

4. **Missing required fields**
   ```
   Required: device_id, timestamp, power
   ```

### Test Commands

```bash
# Test database connection
python test_database.py

# Test API endpoint
curl -X POST http://localhost:5000/api/energy-data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_TEST","timestamp":"2025-01-20T10:30:00Z","power":1000}'
```

## Migration from Existing Data

If you have existing data in a different format, create a migration script:

```python
# Example migration script
from supabase import create_client
import pandas as pd

# Read existing data
df = pd.read_csv('old_data.csv')

# Transform to new format
new_data = []
for _, row in df.iterrows():
    new_data.append({
        'device_id': row['device'],
        'timestamp': row['time'],
        'power': row['watts'],
        # ... map other fields
    })

# Insert into new table
supabase.table('sensor_readings').insert(new_data).execute()
```

## Performance Considerations

### For High-Frequency Data (>1 reading/second)
- Consider batching inserts
- Use connection pooling
- Monitor index performance

### For Long-Term Storage
- Implement data archiving strategy
- Consider partitioning by date
- Regular VACUUM and ANALYZE

## Guardian Submissions Table

### Guardian Integration Schema

The `guardian_submissions` table tracks Guardian blockchain submissions for carbon credit verification:

```sql
CREATE TABLE guardian_submissions (
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
    
    FOREIGN KEY (device_id) REFERENCES sensor_readings(device_id)
);
```

### Guardian Submission Status Values

| Status | Description |
|--------|-------------|
| `PENDING` | Submission created, waiting to be sent to Guardian |
| `PROCESSING` | Submitted to Guardian, verification in progress |
| `VERIFIED` | Successfully verified by Guardian, carbon credits issued |
| `FAILED` | Submission failed, check error_message for details |

### Guardian Submission Queries

#### Get Device Submission History
```sql
SELECT 
    gs.*,
    sr.device_id
FROM guardian_submissions gs
JOIN sensor_readings sr ON gs.device_id = sr.device_id
WHERE gs.device_id = 'ESP32_001'
ORDER BY gs.created_at DESC;
```

#### Get Submission Statistics
```sql
SELECT 
    status,
    COUNT(*) as count,
    SUM(total_energy_kwh) as total_energy,
    AVG(total_energy_kwh) as avg_energy
FROM guardian_submissions
GROUP BY status;
```

#### Get Processing Time Analysis
```sql
SELECT 
    device_id,
    AVG(EXTRACT(EPOCH FROM (verified_at - submitted_at))/3600) as avg_processing_hours
FROM guardian_submissions
WHERE status = 'VERIFIED' 
  AND submitted_at IS NOT NULL 
  AND verified_at IS NOT NULL
GROUP BY device_id;
```

### Migration Instructions

To add the Guardian submissions table to your existing database:

1. **Automatic Migration**:
   ```bash
   python run_migration.py
   ```

2. **Manual Migration**:
   - Copy the SQL from `guardian_submissions_migration.sql`
   - Paste into Supabase SQL Editor
   - Execute the migration

3. **Verify Migration**:
   ```bash
   python test_guardian_submissions_db.py
   ```

## Security

### Recommended Practices
- Use service key for backend API only
- Implement Row Level Security (RLS) if needed
- Validate all input data
- Use prepared statements (handled by Supabase client)

### Example RLS Policy
```sql
-- Enable RLS
ALTER TABLE sensor_readings ENABLE ROW LEVEL SECURITY;

-- Allow read access to authenticated users
CREATE POLICY "Allow read access" ON sensor_readings
    FOR SELECT USING (auth.role() = 'authenticated');

-- Guardian submissions RLS
ALTER TABLE guardian_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow guardian submissions access" ON guardian_submissions
    FOR ALL USING (auth.role() = 'authenticated');
```