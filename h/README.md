# ESP32 Carbon Credit Backend

A Python FastAPI backend that receives real-time data from ESP32 SCADA systems, displays it in a beautiful dashboard, and stores it in Supabase for carbon credit calculations.

## Features

- 🚀 **Real-time Dashboard**: WebSocket-powered live updates
- 📊 **Interactive Charts**: Power, energy, and environmental data visualization
- 🌱 **Carbon Credit Calculation**: Automatic calculation based on Morocco emission factors
- 💾 **Supabase Integration**: Real-time data storage and retrieval
- 🔌 **ESP32 Compatible**: Direct integration with your ESP32 SCADA system
- 🛡️ **Guardian Ready**: Formatted data for Guardian platform integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Supabase

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL commands in `supabase_setup.sql` in your Supabase SQL editor
3. Copy your project URL and anon key

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 4. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST `/api/energy-data`
Receive energy data from ESP32

**Request Body:**
```json
{
  "device_id": "ESP32-001",
  "timestamp": "2025-01-20T10:30:00Z",
  "current": 2.5,
  "voltage": 220.0,
  "power": 550.0,
  "ac_power_kw": 0.55,
  "total_energy_kwh": 1.234,
  "grid_frequency_hz": 50.0,
  "power_factor": 0.95,
  "ambient_temp_c": 25.5,
  "irradiance_w_m2": 850.0,
  "system_status": 1,
  "efficiency": 0.96
}
```

### GET `/api/latest-readings`
Get latest readings from all devices

### GET `/api/carbon-credits/{device_id}`
Calculate carbon credits for a specific device

**Response:**
```json
{
  "methodology": "GCCM001_v4",
  "reporting_period": "2025-01-20T10:30:00Z",
  "project_info": {
    "project_name": "ESP32 Solar Monitor - ESP32-001",
    "project_id": "VCC-ESP32-001",
    "location": "Morocco",
    "capacity_mw": 0.001
  },
  "monitoring_data": {
    "gross_generation_mwh": 0.001234,
    "net_export_mwh": 0.001209,
    "capacity_factor": 55.0,
    "average_irradiance": 850.0,
    "current_rms": 2.5,
    "system_efficiency": 0.96
  },
  "calculations": {
    "baseline_emissions_tco2": 0.000979,
    "project_emissions_tco2": 0,
    "emission_reductions_tco2": 0.000979,
    "carbon_credits_generated": 0.000979
  }
}
```

### WebSocket `/ws`
Real-time data streaming for dashboard updates

## ESP32 Integration

Update your ESP32 code to send data to this backend:

```cpp
// In your ESP32 code, change the serverName to:
const char* serverName = "http://192.168.11.101:5000/api/energy-data";

// The JSON payload format is already compatible!
```

## Dashboard Features

- **Real-time Metrics**: Live power, current, energy, and environmental data
- **Interactive Charts**: Power generation, energy accumulation, and environmental conditions
- **Carbon Credit Display**: Real-time calculation of carbon credits generated
- **Guardian Integration**: One-click data formatting for Guardian platform
- **Multi-device Support**: Monitor multiple ESP32 devices simultaneously

## Supabase Database Schema

The system creates the following tables:

- `energy_readings`: Raw sensor data from ESP32 devices
- `latest_device_readings`: View showing latest reading per device
- `hourly_energy_summary`: Materialized view for performance optimization

## Carbon Credit Calculation

The system uses Morocco's grid emission factor (0.81 tCO2/MWh) to calculate carbon credits:

```
Carbon Credits = (Energy Generated in MWh × Export Efficiency × Emission Factor)
```

Where:
- Export Efficiency = 98% (accounting for system losses)
- Morocco Emission Factor = 0.81 tCO2/MWh
- 1 Carbon Credit = 1 tCO2 of emissions avoided

## Guardian Platform Integration

The `/api/carbon-credits/{device_id}` endpoint provides data in Guardian-compatible format for:

- iREC (International Renewable Energy Certificate) methodology
- GCCM001_v4 carbon credit methodology
- Verifiable Credential (VC) document structure

## Development

### Project Structure

```
h/
├── main.py              # FastAPI application
├── dashboard.html       # Real-time dashboard
├── requirements.txt     # Python dependencies
├── supabase_setup.sql   # Database schema
├── .env.example         # Environment template
└── README.md           # This file
```

### Adding New Features

1. **New API Endpoints**: Add them to `main.py`
2. **Dashboard Updates**: Modify `dashboard.html`
3. **Database Changes**: Update `supabase_setup.sql`

## Troubleshooting

### Common Issues

1. **Supabase Connection Error**: Check your URL and API key in `.env`
2. **WebSocket Not Connecting**: Ensure port 5000 is not blocked
3. **ESP32 Not Sending Data**: Verify the IP address in ESP32 code matches your server

### Logs

The server logs all Supabase operations and WebSocket connections to the console.

## Production Deployment

For production deployment:

1. Use a proper WSGI server like Gunicorn
2. Set up SSL/TLS certificates
3. Configure proper CORS origins
4. Enable Supabase RLS (Row Level Security)
5. Set up monitoring and logging

```bash
# Production example
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:5000
```

## License

MIT License - feel free to use this for your carbon credit projects!