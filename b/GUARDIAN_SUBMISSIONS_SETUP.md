# Guardian Submissions Database Setup

This document explains how to set up the Guardian submissions database table for tracking Guardian blockchain submissions.

## Quick Setup

### Step 1: Run the Database Migration

Since Supabase doesn't support automatic SQL execution via the Python client, you need to run the migration manually:

1. **Open your Supabase Dashboard**
   - Go to [supabase.com](https://supabase.com)
   - Navigate to your project dashboard

2. **Open the SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy and Paste the Migration SQL**
   - Copy the entire contents of `guardian_submissions_migration.sql`
   - Paste it into the SQL Editor
   - Click "Run" to execute the migration

4. **Verify the Migration**
   - Go to "Table Editor" in the left sidebar
   - You should see the new `guardian_submissions` table
   - Check that it has all the expected columns and indexes

### Step 2: Test the Database Integration

Run the test script to verify everything is working:

```bash
python test_guardian_submissions_db.py
```

This will test all the database operations and confirm the integration is working correctly.

## What Gets Created

The migration creates:

### Tables
- **`guardian_submissions`**: Main table for tracking Guardian submissions

### Indexes
- `idx_guardian_submissions_device_status`: For device + status queries
- `idx_guardian_submissions_policy`: For policy-based queries
- `idx_guardian_submissions_status`: For status-based queries  
- `idx_guardian_submissions_period`: For time period queries

### Foreign Key Constraints
- Links `device_id` to the existing `sensor_readings` table

## Database Schema

```sql
guardian_submissions (
    id                    BIGSERIAL PRIMARY KEY,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    device_id            TEXT NOT NULL,
    policy_id            TEXT NOT NULL,
    guardian_document_id TEXT,
    status               TEXT NOT NULL DEFAULT 'PENDING',
    submitted_at         TIMESTAMPTZ,
    verified_at          TIMESTAMPTZ,
    error_message        TEXT,
    period_start         TIMESTAMPTZ NOT NULL,
    period_end           TIMESTAMPTZ NOT NULL,
    total_energy_kwh     REAL NOT NULL,
    data_points_count    INTEGER NOT NULL,
    verification_hash    TEXT NOT NULL,
    guardian_response    JSONB
)
```

## Status Values

| Status | Description |
|--------|-------------|
| `PENDING` | Submission created, waiting to be sent to Guardian |
| `PROCESSING` | Submitted to Guardian, verification in progress |
| `VERIFIED` | Successfully verified by Guardian, carbon credits issued |
| `FAILED` | Submission failed, check error_message for details |

## Usage Examples

### Creating a Submission

```python
from guardian_submissions_db import GuardianSubmissionsDB
from models import GuardianSubmissionCreate

# Create submission
submission_data = GuardianSubmissionCreate(
    device_id="ESP32_001",
    policy_id="renewable_energy_policy",
    period_start=datetime.now() - timedelta(hours=24),
    period_end=datetime.now(),
    total_energy_kwh=125.5,
    data_points_count=1440,
    verification_hash="sha256:abcd1234567890"
)

db = GuardianSubmissionsDB(supabase_client)
submission = await db.create_submission(submission_data)
```

### Updating Submission Status

```python
from models import GuardianSubmissionUpdate, GuardianSubmissionStatus

# Update to processing
update_data = GuardianSubmissionUpdate(
    guardian_document_id="guardian_doc_123",
    status=GuardianSubmissionStatus.PROCESSING,
    submitted_at=datetime.now()
)

updated = await db.update_submission(submission.id, update_data)
```

### Querying Submissions

```python
from models import GuardianSubmissionQuery

# Get device submissions
device_submissions = await db.get_device_submissions("ESP32_001")

# Get pending submissions
pending = await db.get_pending_submissions()

# Get statistics
stats = await db.get_submission_stats()
```

## Integration with Main Application

The Guardian submissions database is designed to integrate with the existing VerifiedCC backend:

1. **Automatic Submission Tracking**: When energy data is submitted to Guardian, create a record in `guardian_submissions`
2. **Status Monitoring**: Background tasks can check Guardian API for status updates
3. **Dashboard Integration**: Frontend can display submission history and verification status
4. **Audit Trail**: Complete history of all Guardian interactions for compliance

## Troubleshooting

### Table Not Found Error
- Verify the migration was run successfully in Supabase SQL Editor
- Check that the table appears in the Table Editor
- Ensure your Supabase credentials are correct

### Foreign Key Constraint Error
- Make sure the `sensor_readings` table exists
- Verify that device_id values exist in sensor_readings before creating submissions

### Permission Errors
- Check that your Supabase service key has the necessary permissions
- Consider enabling Row Level Security (RLS) if needed

## Next Steps

After setting up the database:

1. **Integrate with Guardian Service**: Update `guardian_service.py` to create submission records
2. **Add API Endpoints**: Create REST endpoints for Guardian submission management
3. **Background Tasks**: Implement status monitoring and automatic updates
4. **Frontend Integration**: Add Guardian submission views to the dashboard

## Files Created

- `guardian_submissions_migration.sql`: Database migration script
- `models.py`: Pydantic models for Guardian submissions
- `guardian_submissions_db.py`: Database service class
- `test_guardian_submissions_db.py`: Test suite
- `run_migration.py`: Automated migration script (for reference)
- `GUARDIAN_SUBMISSIONS_SETUP.md`: This setup guide