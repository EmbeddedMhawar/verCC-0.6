# 🌞 ESP32 Carbon Credit Backend - Complete System

A production-ready Python FastAPI backend that receives real-time data from ESP32 SCADA systems, displays it in a beautiful dashboard, stores it in Supabase, and formats it for Guardian platform carbon credit verification.

## 🎯 **Your System is Ready!**

✅ **Supabase Configured**: `smemwzfjwhktvtqtdwta.supabase.co`  
✅ **Real-time Dashboard**: WebSocket-powered live updates  
✅ **Guardian Integration**: Carbon credit calculation ready  
✅ **Railway Deployment**: Production-ready configuration  
✅ **ESP32 Compatible**: Direct integration with your SCADA system  

## 🚀 **Quick Deploy to Railway**

### Option 1: Automated Script
```bash
python deploy_to_railway.py
```

### Option 2: Manual Commands
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Your environment variables are already configured!

## 🗄️ **Setup Supabase Database**

1. **Run the setup script**:
   ```bash
   python setup_supabase.py
   ```

2. **Or manually in Supabase**:
   - Go to: https://supabase.com/dashboard/project/smemwzfjwhktvtqtdwta/sql
   - Copy and paste contents of `supabase_setup.sql`
   - Run the SQL commands

## 🧪 **Test Your System**

### Local Testing
```bash
# Start local server
python main.py

# Test all endpoints
python test_complete_system.py

# Simulate ESP32 data
python test_esp32_simulator.py
```

### Production Testing
```bash
# Update BACKEND_URL in test_complete_system.py to your Railway URL
python test_complete_system.py
```

## 📱 **ESP32 Integration**

Update your ESP32 code with your Railway URL:
```cpp
// Replace with your actual Railway URL
const char* serverName = "https://your-app.up.railway.app/api/energy-data";
```

Your ESP32 JSON format is already compatible!

## 📊 **Dashboard Features**

- **Real-time Monitoring**: Live WebSocket updates every 5 seconds
- **Multi-device Support**: Monitor multiple ESP32 units
- **Interactive Charts**: Power, energy, and environmental data
- **Carbon Credit Display**: Real-time calculation using Morocco emission factors
- **Guardian Integration**: One-click data formatting for verification

## 🛡️ **Guardian Platform Integration**

### API Endpoints
- `GET /api/carbon-credits/{device_id}` - Guardian-formatted carbon credit data
- `POST /api/guardian/submit/{device_id}` - Submit to Guardian platform
- `GET /api/guardian/format/{device_id}` - Get Guardian MRV format

### Carbon Credit Calculation
```javascript
// Morocco emission factor: 0.81 tCO2/MWh
Carbon Credits = (Energy Generated in MWh × 0.98 export efficiency × 0.81 tCO2/MWh)
```

## 🔧 **API Reference**

### Core Endpoints
- `POST /api/energy-data` - Receive ESP32 sensor data
- `GET /api/latest-readings` - Get current readings from all devices
- `GET /api/readings-history?limit=100` - Get historical readings
- `GET /health` - Health check for Railway monitoring
- `WebSocket /ws` - Real-time data stream

### Data Format (ESP32 → Backend)
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

## 🗄️ **Database Schema (Supabase)**

### Main Table: `energy_readings`
- Real-time ESP32 sensor data storage
- Optimized indexes for performance
- Automatic timestamps

### Views & Functions
- `latest_device_readings` - Latest reading per device
- `hourly_energy_summary` - Aggregated hourly data
- `calculate_carbon_credits()` - Carbon credit calculation function

## 📁 **Project Structure**

```
h/
├── main.py                    # FastAPI application
├── dashboard.html             # Real-time dashboard
├── guardian_integration.py    # Guardian platform integration
├── supabase_setup.sql        # Database schema
├── .env                      # Your Supabase credentials
├── requirements.txt          # Python dependencies
├── Procfile                  # Railway deployment
├── railway.toml              # Railway configuration
├── deploy_to_railway.py      # Automated deployment
├── setup_supabase.py         # Database setup
├── test_complete_system.py   # System testing
├── test_esp32_simulator.py   # ESP32 data simulator
└── README_COMPLETE.md        # This file
```

## 🌐 **Production URLs (After Railway Deployment)**

- **Dashboard**: `https://your-app.up.railway.app/`
- **API**: `https://your-app.up.railway.app/api/energy-data`
- **Health Check**: `https://your-app.up.railway.app/health`
- **Carbon Credits**: `https://your-app.up.railway.app/api/carbon-credits/ESP32-001`

## 🚨 **Troubleshooting**

### Common Issues

1. **Supabase Connection Error**
   - Check your credentials in `.env`
   - Ensure database tables are created
   - Run `python setup_supabase.py`

2. **Railway Deployment Failed**
   - Check Railway logs: `railway logs`
   - Verify environment variables: `railway variables`
   - Redeploy: `railway up`

3. **ESP32 Not Connecting**
   - Verify Railway URL in ESP32 code
   - Check network connectivity
   - Test with simulator first

4. **Dashboard Not Updating**
   - Check WebSocket connection in browser console
   - Verify server is running
   - Test health endpoint

### Debug Commands
```bash
# Railway
railway logs              # View deployment logs
railway status            # Check deployment status
railway open              # Open Railway dashboard

# Local
python main.py            # Start local server
python test_complete_system.py  # Test all endpoints
```

## 🔒 **Security & Production**

### Environment Variables (Already Set)
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anonymous key
- `GUARDIAN_API_URL` - Guardian platform URL (optional)

### Production Considerations
- ✅ CORS configured for development
- ✅ Health checks enabled
- ✅ Error handling implemented
- ✅ Environment variables secured
- ⚠️ Consider rate limiting for production
- ⚠️ Add authentication for sensitive endpoints

## 📈 **Monitoring & Analytics**

### Railway Dashboard
- CPU and memory usage
- Request logs and metrics
- Error tracking
- Automatic scaling

### Supabase Dashboard
- Database performance
- Query analytics
- Real-time subscriptions
- Storage usage

## 🎯 **Next Steps**

1. **Deploy to Railway**: `python deploy_to_railway.py`
2. **Setup Database**: `python setup_supabase.py`
3. **Test System**: `python test_complete_system.py`
4. **Update ESP32**: Use your Railway URL
5. **Monitor Data**: Watch real-time dashboard
6. **Generate Credits**: Submit to Guardian platform

## 🌟 **Advanced Features**

### Custom Domains
```bash
railway domain add yourdomain.com
```

### Multiple Environments
```bash
railway environment create staging
railway up --environment staging
```

### Database Backups
- Automatic backups in Supabase
- Point-in-time recovery available
- Export data via Supabase dashboard

## 💰 **Cost Estimation**

### Railway (Free Tier)
- $5 credit per month
- Automatic sleep after inactivity
- Perfect for development and testing

### Supabase (Free Tier)
- 500MB database
- 2GB bandwidth
- 50MB file storage
- Sufficient for ESP32 monitoring

### Production Scaling
- Railway Pro: $20/month
- Supabase Pro: $25/month
- Handles thousands of ESP32 devices

## 🎉 **You're Ready!**

Your ESP32 Carbon Credit Backend is now:

✅ **Production-ready** with Railway deployment  
✅ **Database-connected** with Supabase integration  
✅ **Real-time enabled** with WebSocket dashboard  
✅ **Guardian-compatible** for carbon credit verification  
✅ **Fully tested** with comprehensive test suite  
✅ **Scalable** for multiple ESP32 devices  

## 📞 **Support & Resources**

- **Railway Docs**: https://docs.railway.app
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Guardian Platform**: https://github.com/hashgraph/guardian

Happy carbon credit monitoring! 🌱⚡🚂