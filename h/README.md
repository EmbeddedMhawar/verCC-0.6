# ESP32 Carbon Credit Backend & MRV Processing Pipeline

A comprehensive system combining FastAPI-based ESP32 monitoring with complete MRV (Monitoring, Reporting, and Verification) processing pipeline for Guardian integration.

## 📁 Project Structure

```
h/
├── 📄 Core Application
│   ├── main.py                    # Main FastAPI server
│   ├── dashboard_content.py       # VerifiedCC dashboard
│   └── start.py                   # Startup script
├── ⚙️ Configuration
│   ├── .env                       # Environment variables
│   ├── .env.example              # Environment template
│   └── requirements.txt          # Dependencies
├── 🗄️ Database
│   ├── supabase_setup.sql        # Database schema
│   └── setup_supabase.py         # Setup script
├── 🚀 Deployment
│   ├── deploy_to_railway.py      # Railway deployment
│   └── vercel_version/           # Vercel config
├── 🧪 Testing
│   ├── test_complete_system.py   # System tests
│   ├── test_esp32_simulator.py   # ESP32 simulator
│   └── test_supabase_data.py     # Database tests
├── 📚 Documentation
│   ├── README.md                 # Main documentation
│   ├── PROJECT_STRUCTURE.md     # Project guide
│   └── SETUP_GUIDE.md           # Setup instructions
├── 🎨 Assets
│   └── verifiedcc-logo.png      # VerifiedCC logo
├── 🔧 Utilities
│   ├── guardian_integration.py   # Guardian utilities
│   └── quick_start.py           # Quick dev script
└── 🌍 MRV Processing Pipeline
    ├── guardian_client.py        # Guardian API client
    ├── mrv_sender_client.py      # MRV Sender client
    ├── python_backend.py         # Main MRV processor
    ├── setup_mrv_sender.py       # MRV Sender setup
    ├── test_api_endpoints.py     # API testing suite
    ├── run_setup.bat            # Setup automation
    ├── test_endpoints.bat       # Test automation
    ├── run_pipeline.bat         # Pipeline execution
    ├── AMS-I-D.yaml            # Guardian policy config
    └── Steps.md                # MRV workflow guide
```

## 🚀 Quick Start

### ESP32 Dashboard
1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Start the Server**
   ```bash
   python start.py
   ```

4. **Access Dashboard**
   - Open http://localhost:5000 in your browser
   - ESP32 devices should send data to: http://your-ip:5000/api/energy-data

### MRV Processing Pipeline
1. **Setup MRV Pipeline**
   ```bash
   run_setup.bat
   ```

2. **Start MRV Sender**
   ```bash
   start_mrv_sender.bat
   ```

3. **Test Connectivity**
   ```bash
   test_endpoints.bat
   ```

4. **Run MRV Processing**
   ```bash
   run_pipeline.bat
   ```

## 📊 Features

### ESP32 Dashboard
- **Real-time Dashboard**: Live monitoring of ESP32 solar devices
- **Carbon Credit Calculation**: Automatic calculation based on energy generation
- **Guardian Integration**: Export data in Guardian-compatible format
- **Supabase Storage**: Persistent data storage with real-time sync
- **WebSocket Support**: Live updates without page refresh

### MRV Processing Pipeline
- **Complete Guardian Integration**: End-to-end MRV reporting to Guardian
- **MRV Sender Support**: Optional mrv-sender service integration
- **Batch Processing**: Handle multiple monitoring reports
- **Automated Authentication**: Guardian API authentication flow
- **Policy Configuration**: Pre-configured for AMS-I.D renewable energy policy
- **Testing Suite**: Comprehensive API endpoint testing

## 🔧 API Endpoints

### ESP32 Dashboard API
- `GET /` - Dashboard interface
- `POST /api/energy-data` - Receive ESP32 data
- `GET /api/latest-readings` - Get current device readings
- `GET /api/carbon-credits/{device_id}` - Calculate carbon credits
- `GET /health` - System health check

### Guardian MRV API
- `POST /api/v1/accounts/login` - Guardian authentication
- `POST /api/v1/accounts/access-token` - Get access token
- `POST /api/v1/policies/{policyId}/blocks/{blockId}/external` - Submit monitoring report

### MRV Sender API (Local)
- `GET http://localhost:3005/health` - MRV Sender health check
- `POST http://localhost:3005/mrv-generate` - Submit MRV data

## 🌍 Environment Variables

### ESP32 Dashboard
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
PORT=5000
```

### MRV Processing Pipeline
Pre-configured in `guardian_client.py`:
```python
# Guardian Configuration
base_url = "https://guardianservice.app/api/v1"
username = "Mhawar"
tenant_id = "68cc28cc348f53cc0b247ce4"
policy_id = "68d5ba75152381fe552b1c6d"
block_id = "1021939c-b948-4732-bd5f-90cc4ae1cd50"
schema_id = "3b99fd4b-8285-4b91-a84f-99ecec076f4b"
```

## 📱 ESP32 Integration

Your ESP32 should send POST requests to `/api/energy-data` with this format:

```json
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

## 🌍 MRV Data Format

MRV monitoring reports use this Guardian-compatible format:

```json
{
  "field0": "PROJECT_ID",
  "field1": "Grid connected renewable electricity generation",
  "field6": "1450.0",
  "monitoring_period": "2024-01-01 to 2024-12-31",
  "renewable_energy_kwh": "2500000.0",
  "grid_emission_factor": "0.58"
}
```

## 🛠️ Development

### ESP32 Dashboard
- **Testing**: Run tests with `python -m pytest testing/`
- **Database Setup**: Use `python database/setup_supabase.py`
- **Deployment**: Use `python deployment/deploy_to_railway.py`

### MRV Processing Pipeline
- **Setup**: `python setup_mrv_sender.py`
- **Testing**: `python test_api_endpoints.py`
- **Direct Guardian**: `python guardian_client.py`
- **MRV Sender**: `python mrv_sender_client.py`
- **Full Pipeline**: `python python_backend.py`

## 🔄 MRV Workflow

1. **Data Collection**: ESP32 devices send energy data
2. **Processing**: Convert to MRV format with emission calculations
3. **Submission**: Send to Guardian via mrv-sender or direct API
4. **Verification**: Manual approval in Guardian UI
5. **Token Minting**: Automatic carbon credit token generation

## 📄 License

This project is part of the VerifiedCC platform for automated carbon credit generation.