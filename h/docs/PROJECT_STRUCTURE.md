# VerifiedCC ESP32 Carbon Credit Dashboard - Project Structure

## Core Files

### Main Application
- `main.py` - Main FastAPI backend server
- `dashboard_content.py` - VerifiedCC-styled dashboard HTML content
- `start.py` - Startup script with dependency checks

### Configuration
- `.env` - Environment variables (Supabase credentials)
- `.env.example` - Template for environment variables
- `requirements.txt` - Python dependencies

### Database & Setup
- `supabase_setup.sql` - Database schema setup
- `setup_supabase.py` - Supabase configuration script

### Deployment
- `deploy_to_railway.py` - Railway deployment script
- `vercel_version/` - Vercel deployment configuration

### Testing & Development
- `test_complete_system.py` - Complete system integration tests
- `test_esp32_simulator.py` - ESP32 device simulator for testing
- `test_supabase_data.py` - Database testing utilities
- `quick_start.py` - Quick development startup script

### Documentation
- `README.md` - Main project documentation
- `SETUP_GUIDE.md` - Detailed setup instructions
- `PROJECT_STRUCTURE.md` - This file

### Assets
- `verifiedcc-logo.png` - VerifiedCC logo for dashboard

### Utilities
- `guardian_integration.py` - Guardian platform integration utilities

## Key Features

✅ **VerifiedCC-Styled Dashboard**
- Modern Tailwind CSS design
- Real-time WebSocket updates
- Interactive charts (Power, Energy, Environmental)
- Carbon credit calculations
- Guardian platform integration

✅ **ESP32 Integration**
- Real-time data collection
- Device connection monitoring
- Automatic timestamp correction

✅ **Supabase Backend**
- Real-time database storage
- Historical data queries
- Statistics and analytics

✅ **Production Ready**
- Railway deployment support
- Environment-based configuration
- Health check endpoints
- CORS enabled for cross-origin requests

## Quick Start

1. Copy `.env.example` to `.env` and configure Supabase credentials
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python start.py`
4. Access dashboard: `http://localhost:5000`

## Architecture

```
ESP32 Device → FastAPI Backend → Supabase Database
                     ↓
            WebSocket Real-time Updates
                     ↓
            VerifiedCC Dashboard (Browser)
```