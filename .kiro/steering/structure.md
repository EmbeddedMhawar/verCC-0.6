# Project Structure & Organization

## Repository Layout

This is a full-stack renewable energy verification platform with the following structure:

```
/
├── .kiro/                          # Kiro AI assistant configuration
│   └── steering/                   # AI guidance documents
├── .vscode/                        # VS Code configuration
├── b/                              # Backend (Node.js/TypeScript)
│   ├── data/                       # Database and data files
│   ├── node_modules/               # Dependencies
│   ├── .env                        # Environment variables
│   ├── db.ts                       # Database configuration
│   ├── hashDocument.ts             # Document hashing utilities
│   ├── hederaService.ts            # Hedera blockchain integration
│   └── index.ts                    # Main backend server
├── F/                              # Frontend (React/TypeScript)
│   ├── public/                     # Static assets
│   ├── src/                        # React source code
│   ├── energy_data.csv             # Sample data
│   ├── package.json                # Dependencies and scripts
│   ├── vite.config.ts              # Vite build configuration
│   └── tailwind.config.js          # TailwindCSS configuration
├── h/                              # Hardware (ESP32)
│   └── enhanced_esp32_scada.ino    # Arduino firmware
└── 2025 Q3 VerifiedCC Startup Introduction.md  # Business documentation
```

## Component Organization

### Backend (`/b/`)

- **TypeScript/Node.js**: Main API server with Express framework
- **Hedera Integration**: Blockchain service for immutable data records
- **Database Layer**: PostgreSQL/Supabase integration for data persistence
- **Document Hashing**: Cryptographic verification utilities
- **Environment Config**: Secure credential management

### Frontend (`/F/`)

- **React/TypeScript**: Modern web application with Vite build system
- **TailwindCSS**: Utility-first styling framework
- **Data Visualization**: Multiple charting libraries for energy data
- **Real-time Updates**: Live dashboard for energy production monitoring
- **Sample Data**: CSV files for development and testing

### Hardware (`/h/`)

- **ESP32 Firmware**: Arduino sketch for SCADA simulation and real sensor data
- **Embedded Web Server**: Direct HTTP API from microcontroller
- **Modbus-TCP Server**: Industrial protocol support
- **Real Sensor Integration**: SCT-013 current transformer for power measurement
- **SCADA Simulation**: Solar farm parameter simulation for testing

### Configuration

- **VS Code Setup**: Optimized development environment for C++/TypeScript
- **Kiro AI Steering**: Context-aware development assistance
- **Environment Variables**: Secure configuration for all components

## Architecture Patterns

### Data Flow Pipeline

```
ESP32 Hardware → Backend API → Hedera Blockchain → Frontend Dashboard
     ↓              ↓              ↓                    ↓
Real Sensors → Data Processing → Immutable Records → Visualization
SCADA Sim   → Validation      → Carbon Credits   → Monitoring
```

### Component Communication

1. **Hardware Layer**: ESP32 collects real sensor data + SCADA simulation
2. **Protocol Layer**: HTTP REST API + Modbus-TCP for industrial integration
3. **Backend Processing**: Node.js validates, processes, and stores data
4. **Blockchain Layer**: Hedera creates immutable audit trail
5. **Frontend Display**: React dashboard shows real-time energy production

### ESP32 Firmware Architecture

```cpp
void setup() {
    // WiFi connection and sensor calibration
    // HTTP server and Modbus-TCP server initialization
    // LCD display and hardware pin configuration
}

void loop() {
    // Real sensor reading (SCT-013 current transformer)
    // SCADA parameter simulation (solar irradiance, temperature)
    // Data transmission to backend API
    // Modbus register updates for industrial clients
    // Web interface serving for local monitoring
}
```

## Naming Conventions

### Variables & Functions

- **camelCase**: Standard C++ convention for variables (`scadaData`, `lastSendTime`)
- **snake_case**: Used for struct members (`ac_power_kw`, `total_energy_kwh`)
- **Descriptive names**: Clear purpose indication (`noiseFloor`, `calibrationReadings`)

### Constants & Configuration

- **UPPER_CASE**: Hardware pins and calibration values (`SENSOR_PIN`, `CALIBRATION_FACTOR`)
- **Grouped by purpose**: Network, hardware, and simulation constants separated

### Endpoints & Protocols

- **REST API**: `/scada/data` (raw data), `/scada/guardian` (formatted for Guardian)
- **Modbus registers**: 30001-30010 for holding registers, coils 1-8 for status
- **Web interface**: Root path `/` serves embedded SCADA dashboard

## Development Workflow

### Full-Stack Development

```bash
# Backend development (in /b/)
npm install && npm run dev

# Frontend development (in /F/)
npm install && npm run dev

# Hardware development (in /h/)
# Use Arduino IDE or PlatformIO with ESP32 board package
```

### Component Integration

- **API Compatibility**: Consistent JSON payload format across all layers
- **Real-time Sync**: WebSocket connections for live data updates
- **Industrial Standards**: Modbus-TCP compliance for SCADA integration
- **Blockchain Integration**: Hedera Guardian framework for carbon credits

### Testing Strategy

- **Hardware Testing**: Serial monitor for ESP32 debugging and calibration
- **API Testing**: REST endpoint validation and Modbus connectivity
- **Frontend Testing**: Component testing with mock data
- **End-to-End**: Full pipeline from sensor to blockchain verification

## Deployment & Scaling

### Current Status

- **Backend**: Fully implemented Node.js API with Hedera integration
- **Frontend**: React dashboard with data visualization capabilities
- **Hardware**: Production-ready ESP32 firmware with SCADA simulation
- **Integration**: End-to-end pipeline from sensors to blockchain

### Production Readiness

- **Containerization**: Docker support for backend and frontend
- **Cloud Deployment**: Supabase database with scalable infrastructure
- **Security**: TLS encryption ready for industrial environments
- **Monitoring**: Real-time dashboards and alert systems

### Expansion Capabilities

- **Multi-Device Support**: Framework for connecting multiple ESP32 units
- **Protocol Extensions**: Easy addition of new industrial communication protocols
- **Sensor Diversity**: Template for integrating various measurement devices
- **Geographic Scaling**: Multi-region deployment for international markets
