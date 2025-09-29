# VerCC Project - Simplified ESP32 Dashboard

## Project Structure

This project provides a clean ESP32 monitoring dashboard with real-time data visualization:

```
├── src/                    # Main application source code
│   ├── main.py            # FastAPI backend server
│   └── dashboard_content.py # Dashboard HTML content
├── hardware/              # Hardware-related files (ESP32 Arduino code)
│   └── enhanced_esp32_scada.ino
├── docs/                  # Documentation files
│   ├── DEPENDENCY_ANALYSIS.md
│   ├── Guardian_API_Complete_Guide.md
│   └── Know_ur_ip.md
├── assets/                # Static assets (logos, images)
│   └── verifiedcc-logo.png
├── database/              # Database setup and migrations
│   ├── README_Guardian_Database.md
│   ├── guardian_api_endpoint.py
│   ├── guardian_credentials_manager.py
│   ├── guardian_credentials_schema.sql
│   ├── setup_guardian_db.py
│   ├── setup_supabase.py
│   └── supabase_setup.sql
├── guardian_api_integration/ # Guardian API integration files
│   └── AMS-I.D.py
├── .vscode/               # VSCode settings
│   ├── c_cpp_properties.json
│   ├── launch.json
│   └── settings.json
├── index.html             # Main HTML file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure your Supabase credentials
3. Run the application: `python src/main.py`
4. Open your browser to `http://localhost:5000`

## Key Features

- **Real-time ESP32 Data Collection**: Receives energy data via `/api/energy-data` endpoint
- **Live Dashboard**: WebSocket-powered real-time updates
- **Supabase Integration**: Automatic data storage and retrieval
- **Device Monitoring**: Multi-device support with health tracking
- **Data Visualization**: Interactive charts for power, energy, and environmental data
- **Carbon Credit Calculation**: Basic carbon footprint estimation

## API Endpoints

### Core Endpoints
- `POST /api/energy-data` - Receive ESP32 sensor data
- `GET /api/latest-readings` - Get latest readings from all devices
- `GET /api/readings-history` - Get historical data
- `GET /health` - System health check
- `GET /` - Dashboard interface
- `GET /debug` - Debug dashboard with detailed logging

### Test/Mock Data Endpoints
- `POST /api/test/send-mock-data` - Send a single mock data point
- `POST /api/test/start-mock-stream` - Start continuous mock data stream (every 5 seconds)
- `POST /api/test/stop-mock-stream` - Stop continuous mock data stream
- `GET /api/test/mock-status` - Get mock data stream status

## ESP32 Integration

The system expects ESP32 devices to send JSON data to `/api/energy-data` with the following format:

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

## Testing with Mock Data

The dashboard includes built-in test controls for development and demonstration:

### Test Control Panel
- **Send Mock Data**: Sends a single realistic test data point
- **Start Stream**: Begins continuous mock data generation every 5 seconds
- **Stop Stream**: Stops the continuous mock data stream

### Mock Data Features
- Simulates realistic solar panel readings
- Follows daily solar irradiance cycles (6 AM - 6 PM peak)
- Includes realistic variations in power, voltage, current
- Automatically stores data in Supabase
- Broadcasts via WebSocket for real-time updates

### Testing Commands
```bash
# Test single mock data point
curl -X POST http://localhost:5000/api/test/send-mock-data

# Start continuous mock stream
curl -X POST http://localhost:5000/api/test/start-mock-stream

# Stop mock stream
curl -X POST http://localhost:5000/api/test/stop-mock-stream

# Check mock status
curl http://localhost:5000/api/test/mock-status
```
