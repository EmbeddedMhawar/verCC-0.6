# ESP32 Carbon Credit Backend

A FastAPI-based backend system for monitoring ESP32 solar energy devices and calculating carbon credits.

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
└── 🔧 Utilities
    ├── guardian_integration.py   # Guardian utilities
    └── quick_start.py           # Quick dev script
```

## 🚀 Quick Start

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

## 📊 Features

- **Real-time Dashboard**: Live monitoring of ESP32 solar devices
- **Carbon Credit Calculation**: Automatic calculation based on energy generation
- **Guardian Integration**: Export data in Guardian-compatible format
- **Supabase Storage**: Persistent data storage with real-time sync
- **WebSocket Support**: Live updates without page refresh

## 🔧 API Endpoints

- `GET /` - Dashboard interface
- `POST /api/energy-data` - Receive ESP32 data
- `GET /api/latest-readings` - Get current device readings
- `GET /api/carbon-credits/{device_id}` - Calculate carbon credits
- `GET /health` - System health check

## 🌍 Environment Variables

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
PORT=5000
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

## 🛠️ Development

- **Testing**: Run tests with `python -m pytest testing/`
- **Database Setup**: Use `python database/setup_supabase.py`
- **Deployment**: Use `python deployment/deploy_to_railway.py`

## 📄 License

This project is part of the VerifiedCC platform for automated carbon credit generation.