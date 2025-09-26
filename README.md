# VerCC Project

## Project Structure

This project has been reorganized for better maintainability and clarity:

```
├── src/                    # Main application source code
│   ├── main.py            # FastAPI backend server
│   ├── guardian_*.py      # Guardian Tools integration
│   ├── ams_*.py          # AMS-I.D integration components
│   ├── esp32_*.py        # ESP32 integration
│   └── mrv_*.py          # MRV sender components
├── hardware/              # Hardware-related files (ESP32 Arduino code)
├── docs/                  # All documentation files
│   ├── API Guideline.md
│   ├── Demo guides
│   └── DEPENDENCY_ANALYSIS.md
├── config/                # Configuration files
│   └── ams_config.json
├── assets/                # Static assets (logos, images)
├── database/              # Database setup and migrations
│   ├── setup_supabase.py
│   └── supabase_setup.sql
├── .env                   # Environment variables
├── .env.example          # Environment template
└── requirements.txt      # Python dependencies
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run the application: `python src/main.py`

## Key Components

- **FastAPI Backend**: Main application server in `src/main.py`
- **Guardian Integration**: Guardian Tools architecture implementation
- **AMS-I.D Integration**: Asset Management System integration
- **ESP32 Bridge**: Hardware integration for IoT devices
- **MRV Sender**: Measurement, Reporting, and Verification components
