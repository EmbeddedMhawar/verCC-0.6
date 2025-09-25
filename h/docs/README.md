# VerifiedCC ESP32 Carbon Credit Dashboard

A modern, AI-powered platform for ESP32 solar energy monitoring and automated carbon credit generation, built for the Hedera Africa Hackathon 2025.

## 🌟 Features

- **VerifiedCC-Styled Dashboard** - Modern Tailwind CSS interface with real-time updates
- **ESP32 Integration** - Seamless solar energy data collection
- **Carbon Credit Automation** - Automatic calculation using Morocco emission factors
- **Guardian Platform Ready** - API endpoints for official carbon credit verification
- **Real-time Monitoring** - WebSocket-powered live charts and device status
- **Supabase Backend** - Cloud database with real-time synchronization

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Configure your Supabase credentials in .env
   ```

2. **Install & Run**:
   ```bash
   pip install -r requirements.txt
   python start.py
   ```

3. **Access Dashboard**: `http://localhost:5000`

## 📊 Dashboard Features

- **Carbon Credits Hero Section** - Prominent display of total credits generated
- **Device Monitoring** - Compact cards showing ESP32 device metrics
- **Guardian Integration** - One-click carbon credit verification
- **Real-time Charts** - Power generation, energy accumulation, and environmental data
- **Professional Design** - Consistent with VerifiedCC branding

## 🔌 ESP32 Integration

Send data to: `POST /api/energy-data`

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

## 🌍 Carbon Credit Calculation

- **Morocco Emission Factor**: 0.81 tCO2/MWh
- **Export Efficiency**: 98%
- **Guardian Compatible**: MRV data formatting
- **Real-time Updates**: Automatic credit calculation

## 🚀 Deployment

### Railway (Recommended)
```bash
python deploy_to_railway.py
```

### Manual Deployment
Set environment variables and run:
```bash
python main.py
```

## 📁 Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed file organization.

## 🧪 Testing

```bash
# ESP32 Simulator
python test_esp32_simulator.py

# Complete System Test
python test_complete_system.py
```

## 🔧 Environment Variables

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
PORT=5000
```

## 🏆 Built for Hedera Africa Hackathon 2025

This project demonstrates the power of combining IoT devices, AI automation, and blockchain technology to create a transparent, efficient carbon credit marketplace for Africa's green energy revolution.

---

**VerifiedCC** - Automating Carbon Credits with AI and Hedera