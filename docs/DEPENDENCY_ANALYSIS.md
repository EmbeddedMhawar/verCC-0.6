# Dependency Analysis Report

## Overview

This document analyzes all dependencies in the codebase starting from the main entry points and identifies files that can be safely removed while keeping core functionality intact.

## Main Entry Points Analysis

### 1. Primary Entry Point: `src/main.py`

**Status**: KEEP - Core application
**Dependencies**:

- `dashboard_content.py` - KEEP (provides HTML dashboard)
- FastAPI, uvicorn, supabase - KEEP (core web framework)
- Environment variables (.env) - KEEP

**Functionality**:

- FastAPI web server
- WebSocket connections for real-time data
- Supabase database integration
- Energy data API endpoints
- Dashboard serving

### 2. Dashboard Integration: `src/ams_dashboard_integration.py`

**Status**: REMOVE - AMS-ID specific
**Dependencies**:

- `ams_id_aggregator.py` - REMOVE
- `esp32_ams_integration.py` - REMOVE

**Issues Found**:

- This is causing the 404 errors for `/api/ams-id/metrics`
- Imports AMS-ID components that aren't used in main.py

## Dependency Chain Analysis

### AMS-ID Related Files (REMOVE ALL)

1. `src/ams_dashboard_integration.py` - AMS-ID dashboard integration
2. `src/ams_id_aggregator.py` - AMS-ID aggregation logic
3. `src/esp32_ams_integration.py` - ESP32 to AMS-ID bridge
4. `config/ams_config.json` - AMS-ID configuration

### Guardian Related Files (REMOVE ALL)

1. `src/guardian_integration.py` - Guardian Tools architecture
2. `src/guardian_client.py` - Empty file, Guardian API client
3. `src/mrv_sender_client.py` - MRV sender client
4. `src/simple_mrv_sender.py` - Python MRV sender implementation

### System Startup Files (REMOVE)

1. `src/start_complete_system.py` - Starts multiple services including AMS-ID

## Core Files to Keep

### Essential Application Files

- `src/main.py` - Main FastAPI application ✅
- `src/dashboard_content.py` - Dashboard HTML content ✅
- `requirements.txt` - Python dependencies ✅
- `.env` / `.env.example` - Environment configuration ✅
- `README.md` - Project documentation ✅

### Database Files (KEEP as requested)

- `database/setup_supabase.py` ✅
- `database/supabase_setup.sql` ✅

### Assets (KEEP as requested)

- `assets/verifiedcc-logo.png` ✅

### Hardware Files (KEEP)

- `hardware/enhanced_esp32_scada.ino` ✅

## Files to Remove

### AMS-ID Components

- `src/ams_dashboard_integration.py`
- `src/ams_id_aggregator.py`
- `src/esp32_ams_integration.py`
- `config/ams_config.json`

### Guardian Components

- `src/guardian_integration.py`
- `src/guardian_client.py`
- `src/mrv_sender_client.py`
- `src/simple_mrv_sender.py`

### System Files

- `src/start_complete_system.py`

## Impact Analysis

### Removing AMS-ID Components

**Benefits**:

- Eliminates 404 errors for `/api/ams-id/metrics`
- Removes complex Guardian API dependencies
- Simplifies codebase significantly
- Removes authentication issues with Guardian service

**Functionality Lost**:

- Automatic carbon credit aggregation
- Guardian Tools integration
- AMS-I.D policy workflow
- MRV reporting to Guardian

### Removing Guardian Components

**Benefits**:

- Eliminates external service dependencies
- Removes authentication complexity
- Simplifies deployment
- Removes network-dependent features

**Functionality Lost**:

- Guardian blockchain integration
- Hedera Hashgraph verification
- MRV (Measurement, Reporting, Verification) automation

## Recommended Cleanup Actions

### Phase 1: Remove AMS-ID Integration

1. Delete AMS-ID related files
2. Remove AMS-ID imports from any remaining files
3. Clean up any AMS-ID API endpoints

### Phase 2: Remove Guardian Integration

1. Delete Guardian related files
2. Remove Guardian imports
3. Clean up MRV sender components

### Phase 3: Update Main Application

1. Remove any references to removed components
2. Update requirements.txt if needed
3. Update README.md to reflect simplified architecture

## Simplified Architecture After Cleanup

```
├── src/
│   ├── main.py              # Core FastAPI application
│   └── dashboard_content.py # Dashboard HTML
├── hardware/
│   └── enhanced_esp32_scada.ino
├── database/
│   ├── setup_supabase.py
│   └── supabase_setup.sql
├── assets/
│   └── verifiedcc-logo.png
├── .env / .env.example
├── requirements.txt
└── README.md
```

## Core Functionality Retained

- ESP32 data collection via `/api/energy-data`
- Real-time dashboard with WebSocket updates
- Supabase database storage
- Device monitoring and health checks
- Power, energy, and environmental data visualization
- Basic carbon credit calculation (can be simplified)

## Error Resolution

The 404 errors for `/api/ams-id/metrics` will be resolved by removing the AMS-ID integration components that are trying to access non-existent endpoints.

## C

leanup Results

### Files Successfully Removed

✅ **AMS-ID Components**:

- `src/ams_dashboard_integration.py` - Removed (was causing 404 errors)
- `src/ams_id_aggregator.py` - Removed
- `src/esp32_ams_integration.py` - Removed
- `config/ams_config.json` - Removed
- `config/` directory - Removed (empty)

✅ **Guardian Components**:

- `src/guardian_integration.py` - Removed
- `src/guardian_client.py` - Removed (was empty)
- `src/mrv_sender_client.py` - Removed
- `src/simple_mrv_sender.py` - Removed

✅ **System Files**:

- `src/start_complete_system.py` - Removed

### Code Cleanup Completed

✅ **main.py**:

- Removed Guardian-related response messages
- Fixed static files path for assets directory

✅ **dashboard_content.py**:

- Removed entire AMS-I.D Integration Section from HTML
- Removed all Guardian and AMS-ID JavaScript functions
- Cleaned up references to removed components
- Updated page title and descriptions

✅ **README.md**:

- Updated to reflect simplified architecture
- Removed references to Guardian and AMS-ID components
- Added clear API documentation
- Updated project structure documentation

### Final Architecture

The application now has a clean, simplified structure:

```
├── src/
│   ├── main.py              # Core FastAPI application
│   └── dashboard_content.py # Clean dashboard HTML
├── hardware/
│   └── enhanced_esp32_scada.ino
├── database/
│   ├── setup_supabase.py
│   └── supabase_setup.sql
├── assets/
│   └── verifiedcc-logo.png
├── docs/
│   └── DEPENDENCY_ANALYSIS.md
├── .env / .env.example
├── requirements.txt
└── README.md
```

### Issues Resolved

✅ **404 Errors Fixed**: The `/api/ams-id/metrics` 404 errors are now resolved since the AMS-ID integration components have been removed.

✅ **Simplified Codebase**: Removed ~2000+ lines of complex integration code that wasn't contributing to core functionality.

✅ **No External Dependencies**: Eliminated dependencies on Guardian API, MRV services, and complex authentication systems.

✅ **Clean Startup**: Application now starts successfully without errors and connects to Supabase.

### Core Functionality Retained

- ✅ ESP32 data collection via `/api/energy-data`
- ✅ Real-time WebSocket dashboard updates
- ✅ Supabase database integration
- ✅ Multi-device monitoring
- ✅ Interactive data visualization charts
- ✅ Basic carbon credit calculations
- ✅ Health monitoring endpoints

The application is now much simpler, more maintainable, and free from the complex external integrations that were causing issues.
