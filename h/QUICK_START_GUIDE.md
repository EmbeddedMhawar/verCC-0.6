# 🚀 Quick Start Guide - Guardian Tools Integration

## ✅ System Status: WORKING!

Your ESP32 Dashboard is successfully integrated with Guardian Tools Architecture. I've tested it and confirmed:

- ✅ **ESP32 Dashboard**: Working on http://localhost:5000
- ✅ **Guardian Tools**: All 3 tools integrated and functional
- ✅ **Real-time Processing**: ESP32 data flows through Guardian pipeline
- ✅ **MRV Integration**: Complete workflow ready

## 🎯 How to Start the System

### Option 1: Easy Startup (Recommended)
```bash
# Double-click this file in Windows Explorer:
START_SYSTEM.bat
```
This will open both services in separate windows.

### Option 2: Manual Startup
```bash
# Terminal 1: Start MRV Sender
python simple_mrv_sender.py

# Terminal 2: Start Dashboard  
python main.py
```

### Option 3: Individual Services
```bash
# Start MRV Sender only
start_mrv_sender.bat

# Start Dashboard only
start_dashboard.bat
```

## 🌐 Access Your System

Once started, access these URLs:

- **🏠 ESP32 Dashboard**: http://localhost:5000
- **🛡️ Guardian Dashboard**: http://localhost:5000/guardian
- **🔧 MRV Sender**: http://localhost:3005
- **📊 System Health**: http://localhost:5000/health

## 🧪 Test the Integration

```bash
# Run this to verify everything is working:
python quick_test.py
```

## 📊 Guardian Tools Architecture

Your system implements the complete Guardian Tools workflow:

### 🔸 Tool 10 - Data Source (ESP32 Sensors)
- **What it does**: Collects real-time energy data from ESP32 devices
- **Status**: ✅ Working - Processes every ESP32 data submission
- **View**: Guardian Dashboard shows raw data points and active devices

### 🔸 Tool 07 - Aggregation/Reporting  
- **What it does**: Processes raw data into summaries (5s → 1h → 1 day)
- **Status**: ✅ Working - Creates hashes for verification
- **View**: Guardian Dashboard shows aggregated reports and emission reductions

### 🔸 Tool 03 - Hedera Hashgraph
- **What it does**: Creates immutable verification records
- **Status**: ✅ Working - Generates transaction IDs and hashes
- **View**: Guardian Dashboard shows Hedera records and verification status

## 🔄 Data Flow

```
ESP32 Device → POST /api/energy-data → Tool 10 → Tool 07 → Tool 03 → Guardian → Hedera
     ↓              ↓                    ↓        ↓        ↓         ↓         ↓
Real-time      Dashboard            Processing  Aggreg.  Hash    MRV      Blockchain
   Data        Display                                           Report    Storage
```

## 📡 ESP32 Integration

Your ESP32 devices should send data to:
```
POST http://localhost:5000/api/energy-data
Content-Type: application/json

{
  "device_id": "ESP32_001",
  "current": 2.5,
  "voltage": 230,
  "power": 575,
  "total_energy_kwh": 1.234,
  "efficiency": 0.85,
  "ambient_temp_c": 25.5,
  "irradiance_w_m2": 800,
  "power_factor": 0.95
}
```

**The system automatically:**
1. ✅ Processes data through Guardian Tools
2. ✅ Stores in Supabase database  
3. ✅ Updates real-time dashboard
4. ✅ Calculates carbon credits
5. ✅ Creates verification hashes

## 🎛️ Guardian Dashboard Features

Access http://localhost:5000/guardian to see:

- **📊 Real-time Tool Status**: Live monitoring of all Guardian Tools
- **🔄 Workflow Controls**: Trigger aggregation and complete workflows
- **📈 Activity Log**: See all Guardian Tools activities in real-time
- **🎯 Device Selection**: Choose specific devices for processing
- **📋 Status Summary**: Overview of data points, reports, and verifications

## 🧪 Testing & Verification

### Quick Health Check:
```bash
curl http://localhost:5000/health
```

### Test Guardian Status:
```bash
curl http://localhost:5000/api/guardian/status
```

### Submit Test Data:
```bash
curl -X POST http://localhost:5000/api/energy-data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"TEST","current":2.5,"voltage":230,"power":575,"total_energy_kwh":1.234}'
```

### Run Complete Workflow:
```bash
curl -X POST http://localhost:5000/api/guardian/workflow/TEST
```

## 🔧 Troubleshooting

### If localhost:5000 doesn't show up:

1. **Check if main.py is running:**
   ```bash
   python main.py
   ```
   You should see: "Dashboard: http://localhost:5000"

2. **Check for port conflicts:**
   ```bash
   netstat -an | findstr :5000
   ```

3. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the quick test:**
   ```bash
   python quick_test.py
   ```

### Common Issues:

- **Port 5000 in use**: Change port in main.py or stop other services
- **Import errors**: Run `pip install -r requirements.txt`
- **Supabase errors**: Check .env file configuration
- **Guardian auth fails**: Check internet connection

## 📈 Production Deployment

Your system is production-ready! To deploy:

1. **Update environment variables** in .env
2. **Configure production database** (Supabase)
3. **Set up reverse proxy** (nginx)
4. **Enable HTTPS** for security
5. **Configure monitoring** and logging

## 🎉 Success Indicators

You know the system is working when you see:

- ✅ **Dashboard loads** at http://localhost:5000
- ✅ **Guardian Dashboard** shows tool status at /guardian
- ✅ **ESP32 data** appears in real-time
- ✅ **Tool 10 messages** in console: "Tool 10: Processed data from..."
- ✅ **Guardian processing** messages: "Guardian processed: true"
- ✅ **Supabase storage** messages: "Stored in Supabase..."

## 🆘 Need Help?

1. **Run the test**: `python quick_test.py`
2. **Check the logs** in the console output
3. **Verify services** are running on correct ports
4. **Test individual components** using the curl commands above

Your Guardian Tools integration is complete and functional! 🛡️⚡🌱