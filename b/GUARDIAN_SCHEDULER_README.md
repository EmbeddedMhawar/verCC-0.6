# Guardian Submission Scheduler

This document describes the automated Guardian submission workflow implementation for VerifiedCC, which handles daily energy data aggregation, automatic Guardian submissions, and retry mechanisms for failed submissions.

## Overview

The Guardian Submission Scheduler implements **Requirements 1.1, 1.2, 5.2, and 5.4** by providing:

1. **Background task for daily energy data aggregation** (Requirement 1.1)
2. **Automatic Guardian submission for completed daily periods** (Requirement 1.2)
3. **Configuration for Guardian policy selection and submission timing** (Requirement 5.2)
4. **Submission queue and retry mechanism for failed submissions** (Requirement 5.4)

## Architecture

### Core Components

1. **GuardianSubmissionScheduler** - Main scheduler with background tasks
2. **GuardianConfigManager** - Policy selection and timing configuration
3. **GuardianSubmissionsDB** - Database operations for submission tracking
4. **SubmissionConfig** - Configuration data structures

### Data Flow

```
ESP32 Sensors → Supabase → Energy Aggregator → Scheduler Queue → Guardian API → Blockchain
     ↓              ↓              ↓                ↓              ↓            ↓
Real-time      Persistent     Daily Reports    Queued Tasks   Verification  Carbon Credits
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Guardian Submission Scheduler Configuration
GUARDIAN_SUBMISSION_ENABLED=true
GUARDIAN_DEFAULT_POLICY_ID=your_policy_id_here
GUARDIAN_DAILY_SUBMISSION_TIME=01:00
GUARDIAN_MIN_DATA_COMPLETENESS=80.0
GUARDIAN_MAX_CONCURRENT_SUBMISSIONS=5
```

### Configuration Files

The scheduler creates configuration files in the `config/` directory:

- `guardian_policies.json` - Policy selection configuration
- `submission_timing.json` - Timing and trigger configuration  
- `device_management.json` - Device filtering and grouping

## Features

### 1. Daily Scheduled Submissions

- **Automatic daily processing** at configured time (default: 1:00 AM)
- **Previous day data aggregation** to ensure complete data collection
- **Multi-device support** with concurrent processing limits
- **Data quality validation** before submission

### 2. Policy Selection Modes

#### Fixed Policy Mode
```json
{
  "selection_mode": "fixed",
  "default_policy_id": "your_policy_id",
  "default_tag_name": "renewable_energy"
}
```

#### Device-Based Policy Mode
```json
{
  "selection_mode": "device_based",
  "device_policies": [
    {
      "device_id": "ESP32_001",
      "policy_id": "solar_policy_id",
      "tag_name": "solar_energy",
      "priority": 1
    }
  ]
}
```

#### Energy-Based Policy Mode
```json
{
  "selection_mode": "energy_based",
  "energy_thresholds": [
    {
      "min_energy_kwh": 0.0,
      "max_energy_kwh": 10.0,
      "policy_id": "small_scale_policy",
      "tag_name": "renewable_energy"
    }
  ]
}
```

#### Auto-Selection Mode
```json
{
  "selection_mode": "auto",
  "auto_selection_enabled": true,
  "preferred_policy_types": ["VM0042", "ARR"]
}
```

### 3. Submission Triggers

#### Daily Schedule
- Configurable daily submission time
- Processes all eligible devices automatically

#### Threshold-Based
- Data completeness percentage threshold
- Energy production threshold
- Automatic triggering when thresholds are met

#### Real-Time
- Periodic checks at configured intervals
- Immediate submission when criteria are met

#### Manual
- API endpoint for manual submission queueing
- Priority-based queue processing

### 4. Retry Mechanism

- **Exponential backoff** for failed submissions
- **Configurable retry attempts** (default: 3)
- **Error categorization** and handling
- **Automatic re-queueing** of retryable failures

### 5. Data Quality Validation

Before submission, the scheduler validates:

- **Data completeness** (minimum 80% by default)
- **Data integrity score** (minimum 0.7 by default)
- **Sufficient readings** (minimum 100 per day by default)
- **Energy production** (minimum 0.1 kWh by default)

## API Endpoints

### Scheduler Management

```http
GET /api/guardian/scheduler/status
```
Get current scheduler status and queue information.

```http
POST /api/guardian/scheduler/queue
```
Queue a manual Guardian submission.

```http
POST /api/guardian/scheduler/process-daily
```
Trigger daily submission processing.

```http
POST /api/guardian/scheduler/retry-failed
```
Retry failed submissions.

### Configuration Management

```http
GET /api/guardian/config/summary
```
Get configuration summary.

```http
GET /api/guardian/config/policy/{device_id}
```
Get policy configuration for a device.

```http
POST /api/guardian/config/policy/mapping
```
Add device-specific policy mapping.

```http
GET /api/guardian/config/timing/{device_id}
```
Check submission timing for a device.

### Submission Tracking

```http
GET /api/guardian/submissions
```
Get Guardian submissions with filtering.

```http
GET /api/guardian/submissions/stats
```
Get submission statistics.

```http
GET /api/guardian/submissions/device/{device_id}
```
Get submission summary for a device.

## Usage Examples

### 1. Start the Scheduler

The scheduler starts automatically when the FastAPI application starts:

```python
# In main.py startup event
await guardian_scheduler.start()
```

### 2. Queue Manual Submission

```bash
curl -X POST "http://localhost:5000/api/guardian/scheduler/queue?device_id=ESP32_001&priority=1"
```

### 3. Check Queue Status

```bash
curl "http://localhost:5000/api/guardian/scheduler/status"
```

### 4. Process Daily Submissions

```bash
curl -X POST "http://localhost:5000/api/guardian/scheduler/process-daily"
```

### 5. Add Device Policy Mapping

```bash
curl -X POST "http://localhost:5000/api/guardian/config/policy/mapping" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_001",
    "policy_id": "solar_policy_123",
    "tag_name": "solar_energy",
    "priority": 1
  }'
```

## Testing

Run the test script to verify the scheduler functionality:

```bash
cd b/
python test_guardian_scheduler.py
```

The test script will:
- Test scheduler initialization
- Verify configuration management
- Test policy selection
- Check timing logic
- Test manual queueing
- Validate data processing

## Monitoring and Troubleshooting

### Queue Status Monitoring

Monitor the scheduler queue through the status endpoint:

```json
{
  "queue_length": 3,
  "active_submissions": 1,
  "processed_count": 15,
  "scheduler_running": true,
  "config": {
    "submission_enabled": true,
    "daily_submission_time": "01:00:00",
    "max_concurrent": 5,
    "default_policy_id": "policy_123"
  },
  "queue_items": [
    {
      "device_id": "ESP32_001",
      "target_date": "2025-01-20",
      "policy_id": "policy_123",
      "trigger": "daily_schedule",
      "priority": 1,
      "retry_count": 0,
      "created_at": "2025-01-21T01:00:00"
    }
  ]
}
```

### Common Issues

#### 1. No Default Policy ID
**Error**: "No policy ID specified for device submission"
**Solution**: Set `GUARDIAN_DEFAULT_POLICY_ID` in `.env` file

#### 2. Guardian Connection Failed
**Error**: "Cannot connect to Guardian API"
**Solution**: Ensure Guardian is running and accessible at configured URL

#### 3. Insufficient Data Quality
**Error**: "Data quality insufficient"
**Solution**: Check data completeness and integrity thresholds in configuration

#### 4. Authentication Failures
**Error**: "Guardian authentication failed"
**Solution**: Verify `GUARDIAN_USERNAME` and `GUARDIAN_PASSWORD` in `.env` file

### Logs

The scheduler provides detailed logging:

```
2025-01-21 01:00:00 - INFO - 📅 Daily scheduler loop started
2025-01-21 01:00:00 - INFO - 📊 Aggregating daily data for device ESP32_001
2025-01-21 01:00:01 - INFO - 🚀 Processing Guardian submission: ESP32_001 for 2025-01-20
2025-01-21 01:00:02 - INFO - ✅ Guardian submission successful: ESP32_001 -> doc_456
```

## Database Schema

The scheduler uses the `guardian_submissions` table to track submissions:

```sql
CREATE TABLE guardian_submissions (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    device_id TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    guardian_document_id TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    submitted_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    error_message TEXT,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    total_energy_kwh REAL NOT NULL,
    data_points_count INTEGER NOT NULL,
    verification_hash TEXT NOT NULL,
    guardian_response JSONB
);
```

## Performance Considerations

### Concurrent Processing
- Default: 5 concurrent submissions
- Configurable via `GUARDIAN_MAX_CONCURRENT_SUBMISSIONS`
- Prevents Guardian API overload

### Queue Management
- Priority-based processing (higher number = higher priority)
- Automatic deduplication of submissions
- Retry queue for failed submissions

### Memory Usage
- Processed submissions tracking (in-memory set)
- Policy cache with TTL (30 minutes default)
- Configuration file-based persistence

## Security

### Credentials
- Guardian credentials stored in environment variables
- No hardcoded API keys or passwords
- Secure token management with automatic refresh

### Data Integrity
- Cryptographic hashing of energy data
- Verification hash generation and validation
- Tamper detection for sensor readings

### API Security
- HTTPS for all Guardian API communications
- Request signing for sensitive operations
- Rate limiting to prevent abuse

## Future Enhancements

1. **Advanced Policy Selection**
   - Machine learning-based policy recommendation
   - Dynamic policy switching based on performance
   - Multi-criteria decision making

2. **Enhanced Monitoring**
   - Prometheus metrics integration
   - Grafana dashboards
   - Alert notifications for failures

3. **Scalability Improvements**
   - Distributed queue processing
   - Database connection pooling
   - Horizontal scaling support

4. **Integration Features**
   - Webhook notifications
   - External system integrations
   - Custom trigger plugins

## Support

For issues or questions:

1. Check the logs for detailed error messages
2. Verify Guardian connection and authentication
3. Test with the provided test script
4. Review configuration files for correctness
5. Monitor queue status and submission statistics