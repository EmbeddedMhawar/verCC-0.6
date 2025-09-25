# ESP32 Carbon Credit Backend - Complete Setup Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Python Dependencies
```bash
cd h
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python start.py
```

### 3. Open Dashboard
Visit: http://localhost:5000

### 4. Test with Simulator
```bash
# In another terminal
python test_esp32_simulator.py
```

You should see real-time data flowing in the dashboard! 🎉

## 📋 Detailed Setup

### Prerequisites
- Python 3.8 or higher
- Internet connection for CDN resources (Chart.js)
- Optional: Supabase account for data persistence

### Step 1: Environment Setup

1. **Clone/Download the files** to your `h` directory
2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn websockets pydantic supabase python-dotenv python-multipart
   ```

### Step 2: Supabase Setup (Optional but Recommended)

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note your Project URL and anon key

2. **Setup Database**:
   - Go to SQL Editor in Supabase
   - Copy and run the SQL from `supabase_setup.sql`

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

### Step 3: ESP32 Configuration

Update your ESP32 code to send data to your backend:

```cpp
// Change this line in your ESP32 code:
const char* serverName = "http://YOUR_COMPUTER_IP:5000/api/energy-data";

// Replace YOUR_COMPUTER_IP with your actual IP address
// Find it with: ipconfig (Windows) or ifconfig (Mac/Linux)
```

### Step 4: Start the Backend

```bash
python main.py
```

Or use the startup script:
```bash
python start.py
```

## 🧪 Testing Without ESP32

Use the simulator to generate test data:

```bash
python test_esp32_simulator.py
```

This simulates realistic solar panel data with:
- Day/night cycles
- Weather variations
- Multiple devices
- Realistic power curves

## 📊 Dashboard Features

### Real-time Monitoring
- **Live Data**: WebSocket updates every 5 seconds
- **Multiple Devices**: Support for multiple ESP32 units
- **Interactive Charts**: Power, energy, and environmental data
- **Carbon Credits**: Real-time calculation

### Key Metrics Displayed
- Current (A)
- Voltage (V) 
- Power (W)
- Energy (kWh)
- Efficiency (%)
- Temperature (°C)
- Solar Irradiance (W/m²)
- Power Factor
- Carbon Credits Generated (tCO2)

## 🛡️ Guardian Integration

### API Endpoints for Guardian
- `GET /api/carbon-credits/{device_id}` - Guardian-formatted carbon credit data
- `POST /api/guardian/submit/{device_id}` - Submit to Guardian platform
- `GET /api/guardian/format/{device_id}` - Get Guardian MRV format
- `GET /api/guardian/policies` - List Guardian policies

### Guardian Data Format
The system automatically formats ESP32 data for Guardian's iREC methodology:

```json
{
  "methodology": "GCCM001_v4",
  "project_info": {
    "project_name": "ESP32 Solar Monitor",
    "location": "Morocco",
    "capacity_mw": 0.001
  },
  "monitoring_data": {
    "gross_generation_mwh": 0.001234,
    "net_export_mwh": 0.001209,
    "capacity_factor": 55.0,
    "average_irradiance": 850.0
  },
  "calculations": {
    "baseline_emissions_tco2": 0.000979,
    "emission_reductions_tco2": 0.000979,
    "carbon_credits_generated": 0.000979
  }
}
```

## 🔧 API Reference

### POST `/api/energy-data`
Receive ESP32 sensor data

**Request:**
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
Get current readings from all devices

### GET `/api/readings-history?limit=100`
Get historical readings

### WebSocket `/ws`
Real-time data stream for dashboard

## 🗄️ Database Schema (Supabase)

### energy_readings table
- `id` - Primary key
- `device_id` - ESP32 device identifier
- `timestamp` - Reading timestamp
- `current` - Current in Amps
- `voltage` - Voltage in Volts
- `power` - Power in Watts
- `ac_power_kw` - AC power in kW
- `total_energy_kwh` - Cumulative energy in kWh
- `grid_frequency_hz` - Grid frequency in Hz
- `power_factor` - Power factor
- `ambient_temp_c` - Temperature in Celsius
- `irradiance_w_m2` - Solar irradiance in W/m²
- `system_status` - System status (0=offline, 1=online)
- `efficiency` - System efficiency

### Views and Functions
- `latest_device_readings` - Latest reading per device
- `hourly_energy_summary` - Hourly aggregated data
- `calculate_carbon_credits()` - Carbon credit calculation function

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **ESP32 not connecting**
   - Check IP address in ESP32 code
   - Ensure both devices on same network
   - Check firewall settings

3. **Supabase connection errors**
   - Verify URL and API key in `.env`
   - Check internet connection
   - Ensure Supabase project is active

4. **Dashboard not updating**
   - Check browser console for WebSocket errors
   - Verify server is running on port 5000
   - Try refreshing the page

5. **Port 5000 already in use**
   ```bash
   # Change port in main.py:
   uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

### Debug Mode
Add debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🌐 Network Configuration

### Finding Your IP Address
**Windows:**
```cmd
ipconfig
```

**Mac/Linux:**
```bash
ifconfig
```

**Python script:**
```python
import socket
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print(f"Your IP: {ip_address}")
```

### Firewall Settings
Ensure port 5000 is open:

**Windows:**
- Windows Defender Firewall → Advanced Settings
- Inbound Rules → New Rule → Port → TCP → 5000

**Mac:**
```bash
sudo pfctl -f /etc/pf.conf
```

**Linux:**
```bash
sudo ufw allow 5000
```

## 📈 Performance Optimization

### For High-Frequency Data
- Increase WebSocket update interval
- Use database connection pooling
- Implement data aggregation
- Consider Redis for caching

### For Multiple Devices
- Implement device-specific WebSocket channels
- Use async database operations
- Add rate limiting
- Monitor memory usage

## 🔒 Security Considerations

### Production Deployment
- Use HTTPS/WSS
- Implement authentication
- Enable Supabase RLS
- Validate all inputs
- Use environment variables for secrets
- Set up proper CORS policies

### Example Production Config
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📦 Deployment Options

### Local Development
```bash
python main.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:5000
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "main.py"]
```

### Cloud Deployment
- **Heroku**: Add `Procfile` with `web: python main.py`
- **Railway**: Direct deployment from GitHub
- **DigitalOcean**: App Platform deployment
- **AWS**: Elastic Beanstalk or Lambda

## 🎯 Next Steps

1. **Connect Real ESP32**: Update ESP32 code with your IP
2. **Setup Supabase**: For data persistence and analytics
3. **Configure Guardian**: For official carbon credit verification
4. **Add Authentication**: For multi-user access
5. **Implement Alerts**: For system monitoring
6. **Create Reports**: For carbon credit documentation

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Review error messages in console
3. Test with the simulator
4. Verify network connectivity
5. Check Supabase logs (if using)

Happy carbon credit monitoring! 🌱⚡