# AMS-I.D Automatic Aggregation Tool

This tool automatically aggregates ESP32 solar monitoring data and submits it to Guardian following the AMS-I.D policy workflow for carbon credit generation.

## 🌟 Features

- **Automatic Data Collection**: Continuously collects ESP32 solar monitoring data
- **Smart Aggregation**: Aggregates data over configurable time periods (default: 24 hours)
- **AMS-I.D Compliance**: Follows the official AMS-I.D methodology for renewable energy projects
- **Guardian Integration**: Automatically submits projects and monitoring reports to Guardian
- **Real-time Monitoring**: Provides status updates and logging
- **Configurable**: Easy configuration through JSON file

## 📋 Prerequisites

1. **Guardian Account**: Active Guardian account with proper credentials
2. **AMS-I.D Policy**: Access to the AMS-I.D policy (ID: `68d69341152381fe552b21ec`)
3. **Python 3.7+**: Required for running the aggregation tool
4. **ESP32 Data Source**: Either real ESP32 device or simulated data

## 🚀 Quick Start

### 1. Configuration

Edit `ams_config.json` with your Guardian credentials:

```json
{
  "guardian": {
    "base_url": "https://guardianservice.app/api/v1",
    "username": "your_username",
    "password": "your_password",
    "tenant_id": "your_tenant_id"
  },
  "ams_id_policy": {
    "policy_id": "68d69341152381fe552b21ec",
    "policy_tag": "Tag_1758892814008"
  }
}
```

### 2. Test the System

Run the complete test suite:

```bash
python test_complete_ams_workflow.py
```

This will test:
- ✅ Configuration loading
- ✅ Guardian authentication
- ✅ Policy access
- ✅ Data generation and aggregation
- ✅ Document formatting
- ✅ Guardian submission (optional)

### 3. Start the Aggregator

For production use:
```bash
python start_ams_aggregator.py
```

For testing with faster intervals:
```bash
python start_ams_aggregator.py --test
```

For dry-run (no Guardian submission):
```bash
python start_ams_aggregator.py --dry-run
```

## 📊 How It Works

### Data Flow

1. **ESP32 Data Collection**
   - Collects solar panel measurements every 5 minutes
   - Includes: power, irradiance, temperature, efficiency, energy

2. **Data Aggregation**
   - Aggregates measurements over 24-hour periods
   - Calculates total energy, averages, capacity factor
   - Computes emission reductions using Morocco grid factor (0.81 tCO2/MWh)

3. **Guardian Submission**
   - Creates AMS-I.D compliant project documents
   - Submits monitoring reports with aggregated data
   - Follows proper workflow blocks and schemas

### AMS-I.D Workflow Steps

1. **Project Creation** (`add_project_bnt`)
   - Creates renewable energy project
   - Includes baseline and project emissions calculations

2. **Monitoring Report** (`add_report_bnt`)
   - Submits periodic monitoring data
   - Links to parent project
   - Contains emission reduction calculations

3. **Validation & Verification**
   - Project validation by Standard Registry
   - Report verification by VVB
   - Token minting for verified emission reductions

## 🔧 Configuration Options

### Guardian Settings
- `base_url`: Guardian API endpoint
- `username`: Your Guardian username
- `password`: Your Guardian password
- `tenant_id`: Your Guardian tenant ID

### Policy Settings
- `policy_id`: AMS-I.D policy ID
- `policy_tag`: Policy tag for submissions
- `project_schema_id`: Schema for project documents
- `monitoring_report_schema_id`: Schema for monitoring reports

### Aggregation Settings
- `interval_hours`: How often to aggregate data (default: 24)
- `min_data_points`: Minimum measurements needed for aggregation (default: 10)
- `check_interval_minutes`: How often to check for aggregation (default: 60)

### ESP32 Settings
- `data_interval_seconds`: How often to collect ESP32 data (default: 300)
- `mrv_sender_url`: URL of MRV sender service

## 📁 File Structure

```
h/
├── ams_id_aggregator.py          # Main aggregation logic
├── esp32_ams_integration.py      # ESP32 integration layer
├── guardian_client.py            # Guardian API client
├── mrv_sender_client.py          # MRV sender client
├── ams_config.json               # Configuration file
├── test_complete_ams_workflow.py # Complete test suite
├── start_ams_aggregator.py       # Startup script
└── AMS_ID_AGGREGATOR_README.md   # This file
```

## 🧪 Testing

### Individual Component Tests

Test Guardian authentication:
```bash
python guardian_client.py
```

Test MRV sender:
```bash
python mrv_sender_client.py
```

Test aggregation only:
```bash
python test_ams_id_aggregator.py
```

### Complete Workflow Test

```bash
python test_complete_ams_workflow.py
```

This comprehensive test will:
1. ✅ Load configuration
2. ✅ Authenticate with Guardian
3. ✅ Check policy access
4. ✅ Generate and aggregate test data
5. ✅ Format Guardian documents
6. ✅ Optionally submit to Guardian
7. ✅ Test integration workflow

## 📈 Monitoring

### Log Files
- `ams_aggregator.log`: Main system log
- Console output: Real-time status updates

### Status Information
- Measurements in buffer
- Last measurement timestamp
- Guardian authentication status
- MRV sender availability

### Key Metrics
- Total energy generated (MWh)
- Emission reductions (tCO2e)
- Capacity factor (%)
- Data collection rate

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check Guardian credentials in `ams_config.json`
   - Verify tenant ID is correct
   - Ensure account has proper permissions

2. **Policy Access Denied**
   - Verify policy ID: `68d69341152381fe552b21ec`
   - Check if account has access to AMS-I.D policy
   - Confirm policy is in correct status

3. **Insufficient Data Points**
   - Ensure ESP32 is generating data
   - Check `min_data_points` setting
   - Verify data collection interval

4. **Submission Failures**
   - Check Guardian API status
   - Verify document format compliance
   - Review block IDs and schema IDs

### Debug Mode

Run with verbose logging:
```bash
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" start_ams_aggregator.py
```

## 🔐 Security Notes

- Store Guardian credentials securely
- Use environment variables for production
- Regularly rotate passwords
- Monitor access logs

## 📞 Support

For issues with:
- **Guardian Platform**: Contact Guardian support
- **AMS-I.D Policy**: Refer to policy documentation
- **This Tool**: Check logs and test results

## 🎯 Next Steps

1. Run the complete test suite
2. Configure your Guardian credentials
3. Start with test mode to verify operation
4. Deploy in production mode
5. Monitor logs and status updates
6. Scale to multiple ESP32 devices as needed

---

**Note**: This tool is designed specifically for the AMS-I.D methodology and Guardian platform. Ensure you have proper access and permissions before using in production.