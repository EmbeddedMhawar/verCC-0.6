# VerifiedCC Integrated Dashboard with AMS-I.D

This is the complete integrated dashboard that combines ESP32 monitoring, Guardian Tools Architecture, and AMS-I.D automatic aggregation for carbon credit generation.

## 🌟 Features

### Core Monitoring

- **Real-time ESP32 Data**: Live monitoring of solar panel performance
- **WebSocket Updates**: Real-time dashboard updates
- **Supabase Storage**: Persistent data storage
- **Interactive Charts**: Power, energy, and environmental data visualization

### Guardian Tools Architecture

- **Tool 10**: Data Source Processing (ESP32 sensors)
- **Tool 07**: Data Aggregation and Processing
- **Tool 03**: Hedera Verification and Recording
- **Complete Workflow**: Automated MRV pipeline

### AMS-I.D Integration

- **Automatic Aggregation**: 24-hour data aggregation cycles
- **Guardian Submission**: Automatic project and report submission
- **Carbon Credit Calculation**: Real-time tCO2e calculations
- **Policy Compliance**: Full AMS-I.D methodology compliance
- **Manual Controls**: Dashboard triggers for testing and management

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Python dependencies
pip install fastapi uvicorn websockets supabase python-dotenv

# Configure environment variables
cp .env.example .env
# Edit .env with your Supabase and Guardian credentials
```

### 2. Configuration

Edit `h/ams_config.json` with your Guardian credentials:

```json
{
  "guardian": {
    "base_url": "https://guardianservice.app/api/v1",
    "username": "your_username",
    "password": "your_password",
    "tenant_id": "your_tenant_id"
  }
}
```

### 3. Start the Dashboard

```bash
# Start the integrated dashboard
python h/start_integrated_dashboard.py

# Or use the main script
python h/main.py
```

### 4. Access the Dashboard

- **Dashboard**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **AMS-I.D Status**: http://localhost:5000/api/ams-id/status

## 📊 Dashboard Sections

### 1. Carbon Credits Hero

- **Total Credits**: Real-time carbon credit accumulation
- **AMS-I.D Generated**: Credits from AMS-I.D workflow
- **Visual Impact**: Animated display with leaf icon

### 2. AMS-I.D Integration Panel

- **System Status**: Online/offline indicators
- **Data Processing**: Measurements and buffer status
- **Guardian Submissions**: Projects and reports submitted
- **Carbon Credits**: Detailed breakdown of generated credits
- **Workflow Controls**: Manual triggers and management
- **Activity Log**: Real-time activity monitoring

### 3. Guardian Tools Architecture

- **Tool 10**: ESP32 data source monitoring
- **Tool 07**: Aggregation processing status
- **Tool 03**: Hedera verification records
- **Workflow Diagram**: Visual pipeline representation
- **Manual Controls**: Individual tool triggers

### 4. Device Monitoring

- **Real-time Readings**: Live ESP32 data
- **Device Status**: Online/offline indicators
- **Performance Metrics**: Power, energy, efficiency
- **Environmental Data**: Temperature, irradiance

### 5. Interactive Charts

- **Power Generation**: Real-time power output
- **Energy Accumulation**: Cumulative energy production
- **Environmental Conditions**: Temperature and irradiance trends

## 🔧 API Endpoints

### ESP32 Data

- `POST /api/energy-data` - Receive ESP32 readings
- `GET /api/latest-readings` - Get latest device readings
- `GET /api/readings-history` - Get historical data

### AMS-I.D Integration

- `GET /api/ams-id/status` - Get AMS-I.D system status
- `GET /api/ams-id/metrics` - Get dashboard metrics
- `POST /api/ams-id/initialize` - Initialize AMS-I.D system
- `POST /api/ams-id/aggregate/{device_id}` - Trigger aggregation
- `POST /api/ams-id/workflow/{device_id}` - Run complete workflow
- `POST /api/ams-id/workflow/all` - Run workflow for all devices

### Guardian Tools

- `GET /api/guardian/status` - Get Guardian tools status
- `POST /api/guardian/aggregate/{device_id}` - Trigger aggregation
- `POST /api/guardian/workflow/{device_id}` - Run complete workflow
- `GET /api/guardian/hedera-records` - Get Hedera records
- `GET /api/guardian/aggregated-data` - Get aggregated reports

### Legacy Endpoints

- `GET /api/carbon-credits/{device_id}` - Calculate carbon credits
- `GET /api/supabase-stats` - Get Supabase statistics
- `GET /health` - System health check

## 🎯 AMS-I.D Workflow

### Automatic Process

1. **Data Collection**: ESP32 sends readings every 5 minutes
2. **Buffer Management**: Measurements stored in memory buffer
3. **Aggregation Trigger**: Every 24 hours (configurable)
4. **Guardian Submission**: Automatic project and report submission
5. **Carbon Credit Generation**: Real-time tCO2e calculation

### Manual Controls

- **Initialize**: Set up AMS-I.D system connection
- **Trigger Aggregation**: Force aggregation for testing
- **Run Complete Workflow**: Execute full pipeline manually
- **Refresh Status**: Update dashboard metrics

### Data Flow

```
ESP32 → Dashboard → AMS-I.D Buffer → Aggregation → Guardian → Carbon Credits
```

## 📈 Monitoring and Logging

### Real-time Status

- **System Health**: Connection status indicators
- **Data Flow**: Measurement processing rates
- **Guardian Status**: Authentication and submission status
- **Buffer Status**: Current measurements in buffer

### Activity Logs

- **AMS-I.D Log**: Aggregation and submission activities
- **Guardian Log**: Tools workflow activities
- **System Log**: General system events and errors

### Metrics Tracking

- **Measurements Processed**: Total ESP32 readings processed
- **Projects Submitted**: Guardian project submissions
- **Reports Submitted**: Guardian monitoring reports
- **Carbon Credits**: Total tCO2e generated
- **Energy Generated**: Total MWh produced

## 🔍 Troubleshooting

### Common Issues

1. **AMS-I.D Initialization Failed**

   - Check Guardian credentials in `ams_config.json`
   - Verify network connectivity to Guardian API
   - Ensure policy access permissions

2. **Insufficient Data for Aggregation**

   - Check ESP32 data flow
   - Verify minimum data points setting (default: 10)
   - Review aggregation interval (default: 24 hours)

3. **Guardian Submission Errors**

   - Verify Guardian authentication
   - Check policy ID and block tags
   - Review Guardian API status

4. **Dashboard Not Loading**
   - Check port availability (default: 5000)
   - Verify all dependencies installed
   - Review server logs for errors

### Debug Mode

```bash
# Run with debug logging
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" h/main.py
```

### Health Checks

```bash
# Check system health
curl http://localhost:5000/health

# Check AMS-I.D status
curl http://localhost:5000/api/ams-id/status

# Check Guardian status
curl http://localhost:5000/api/guardian/status
```

## 🔐 Security

- Store Guardian credentials securely
- Use environment variables for production
- Regularly rotate API keys
- Monitor access logs
- Implement rate limiting for production use

## 📞 Support

For issues with:

- **Dashboard**: Check logs and health endpoints
- **AMS-I.D Integration**: Review activity logs and status
- **Guardian Tools**: Verify authentication and permissions
- **ESP32 Data**: Check device connectivity and data format

## 🎊 Success Indicators

When everything is working correctly, you should see:

✅ **Dashboard**: Real-time data updates and charts
✅ **AMS-I.D**: Green status indicators and activity logs
✅ **Guardian**: Successful authentication and submissions
✅ **Carbon Credits**: Increasing credit totals
✅ **ESP32**: Regular data flow from devices

---

**The integrated dashboard provides a complete solution for ESP32 monitoring, Guardian Tools processing, and AMS-I.D carbon credit generation in one unified interface!** 🌱
