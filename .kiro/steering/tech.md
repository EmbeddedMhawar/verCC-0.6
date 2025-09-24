# Technology Stack & Development Environment

## Core Technology Stack

### Blockchain Infrastructure
- **Hedera Hashgraph**: Immutable ledger for energy production records
- **Hedera Guardian**: Automated carbon credit verification workflows
- **Guardian Policy Engine**: Multi-stakeholder verification (Project Participants, VVBs, System Owners)
- **Smart Contracts**: Automated compliance and payment processing

### Backend Stack (`/b/`)
- **Node.js 18+**: Runtime environment with ES modules support
- **TypeScript**: Type-safe development with strict configuration
- **Express.js**: RESTful API framework with middleware support
- **Supabase**: PostgreSQL cloud database with real-time subscriptions
- **Hedera SDK**: Direct blockchain integration for data submission

### Frontend Stack (`/F/`)
- **React 18**: Modern UI framework with hooks and concurrent features
- **TypeScript**: Full type safety across components and APIs
- **Vite**: Fast build tool with HMR and optimized bundling
- **TailwindCSS**: Utility-first CSS framework for responsive design
- **Chart.js + Recharts**: Multiple visualization libraries for energy data

### Hardware Platform (`/h/`)
- **ESP32**: Dual-core microcontroller with WiFi and Bluetooth
- **Arduino Framework**: C++ development with extensive library ecosystem
- **SCT-013**: Non-invasive current transformer for AC measurement
- **EmonLib**: Energy monitoring calculations and calibration
- **LiquidCrystal_I2C**: 16x2 LCD for local status display

### Industrial Integration
- **Modbus-TCP**: Standard SCADA communication protocol (port 502)
- **HTTP REST API**: Modern web-based data access endpoints
- **JSON Payloads**: Structured data format for cross-platform compatibility
- **TLS Security**: Production-ready encryption for industrial networks

## Development Environment Setup

### Backend Development (`/b/`)
```bash
# Node.js dependencies
npm install express typescript @types/node
npm install @hashgraph/sdk supabase dotenv

# Development tools
npm install -D nodemon ts-node @types/express

# Environment variables required
HEDERA_ACCOUNT_ID=your_account_id
HEDERA_PRIVATE_KEY=your_private_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
```

### Frontend Development (`/F/`)
```bash
# React + TypeScript + Vite setup
npm create vite@latest . --template react-ts
npm install tailwindcss postcss autoprefixer
npm install chart.js react-chartjs-2 recharts

# Development server
npm run dev  # Starts on http://localhost:5173
```

### Hardware Development (`/h/`)
```cpp
// Arduino IDE Libraries (install via Library Manager)
#include <WiFi.h>           // ESP32 built-in
#include <HTTPClient.h>     // ESP32 built-in
#include <ArduinoJson.h>    // JSON parsing and generation
#include <EmonLib.h>        // Energy monitoring calculations
#include <LiquidCrystal_I2C.h>  // I2C LCD display
#include <ModbusIP_ESP32.h> // Modbus-TCP server (emelianov)

// Hardware connections
#define SENSOR_PIN A0       // SCT-013 current transformer
#define LCD_ADDRESS 0x27    // I2C LCD address
```

### Network Configuration
- **WiFi Setup**: SSID and password configuration in ESP32 firmware
- **Port Allocation**: HTTP server (80), Modbus-TCP (502), Backend API (3000)
- **IP Management**: Static IP recommended for industrial environments
- **Firewall Rules**: Open ports 80 and 502 for SCADA access

## Development Commands

### Backend Operations (`/b/`)
```bash
# Development server with auto-reload
npm run dev

# Production build and start
npm run build && npm start

# Database operations
# Use Supabase dashboard for schema management
# Real-time subscriptions handled automatically
```

### Frontend Operations (`/F/`)
```bash
# Development server with HMR
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Linting and formatting
npm run lint
```

### Hardware Development (`/h/`)
```bash
# Arduino IDE workflow
# 1. Select "ESP32 Dev Module" board
# 2. Set upload speed to 921600 baud
# 3. Select correct COM port
# 4. Compile and upload firmware

# Serial monitoring for debugging
# Baud rate: 115200
# Monitor calibration process and data transmission
```

### Testing & Validation
```bash
# Test ESP32 endpoints
curl http://[ESP32_IP]/scada/data
curl http://[ESP32_IP]/scada/guardian
curl http://[ESP32_IP]/  # Web interface

# Test Modbus connectivity
# Use ModbusPoll, QModMaster, or similar tools
# Connect to [ESP32_IP]:502
# Read holding registers 30001-30010

# Backend API testing
curl http://localhost:3000/api/energy-data
curl -X POST http://localhost:3000/api/submit-data
```

## System Architecture & Data Flow

### Production Pipeline
```
ESP32 Sensors → Backend API → Supabase DB → Hedera Blockchain → React Dashboard
     ↓              ↓             ↓              ↓                    ↓
Real Power    → Validation → Persistence → Immutable Record → Visualization
SCADA Sim     → Processing → Real-time   → Carbon Credits  → Monitoring
Modbus-TCP    → Formatting → Sync        → Audit Trail     → Alerts
```

### Version Evolution
- **v1.0**: Full-stack implementation with real sensor integration
- **v1.1**: Hedera Guardian framework for automated carbon credit workflows
- **v1.2**: Multi-device support and industrial SCADA integration
- **v2.0**: Production deployment with TLS security and cloud scaling

### Security Architecture
- **Transport Layer**: TLS 1.3 encryption for all network communications
- **Authentication**: API key management and certificate-based device auth
- **Data Integrity**: Cryptographic hashing before blockchain submission
- **Industrial Security**: Modbus-TCP Security (RFC 8502) compliance
- **Audit Trail**: Immutable blockchain records for regulatory compliance

### Calibration & Measurement
- **Startup Calibration**: 2-minute noise floor measurement for accuracy
- **Real-time Correction**: Automatic offset adjustment for environmental drift
- **Power Calculations**: True RMS with 220V grid voltage (Morocco standard)
- **Data Validation**: Range checking and anomaly detection before transmission
- **Simulation Mode**: Realistic solar farm parameters for testing and demos