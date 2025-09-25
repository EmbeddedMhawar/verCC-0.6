from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime
import uvicorn
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from guardian_integration import GuardianClient

# Load environment variables
load_dotenv()

app = FastAPI(title="ESP32 Carbon Credit Backend", version="0.6")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "your_supabase_url")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "your_supabase_anon_key")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase connection error: {e}")
    supabase = None

# Data models
class ESP32Reading(BaseModel):
    device_id: str
    timestamp: str
    current: float
    voltage: float
    power: float
    ac_power_kw: float
    total_energy_kwh: float
    grid_frequency_hz: float
    power_factor: float
    ambient_temp_c: float
    irradiance_w_m2: float
    system_status: int
    efficiency: float

class CarbonCreditData(BaseModel):
    methodology: str = "GCCM001_v4"
    reporting_period: str
    project_info: dict
    monitoring_data: dict
    calculations: dict

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Store latest readings in memory
latest_readings = {}
readings_history = []

# Initialize Guardian client
guardian_client = GuardianClient()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the real-time dashboard"""
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            dashboard_html = f.read()
        return HTMLResponse(content=dashboard_html, status_code=200)
    except FileNotFoundError:
        # Fallback to embedded HTML if file not found
        return HTMLResponse(content=embedded_dashboard_html, status_code=200)

@app.post("/api/energy-data")
async def receive_energy_data(reading: ESP32Reading):
    """Receive energy data from ESP32"""
    try:
        # Store in memory
        latest_readings[reading.device_id] = reading.dict()
        readings_history.append(reading.dict())
        
        # Keep only last 1000 readings in memory
        if len(readings_history) > 1000:
            readings_history.pop(0)
        
        # Store in Supabase
        if supabase:
            try:
                result = supabase.table("energy_readings").insert(reading.dict()).execute()
                print(f"Stored in Supabase: {result}")
            except Exception as e:
                print(f"Supabase insert error: {e}")
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "energy_reading",
            "data": reading.dict()
        }))
        
        return {"status": "success", "message": "Data received and stored"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "devices_connected": len(latest_readings),
        "supabase_connected": supabase is not None
    }

@app.get("/api/latest-readings")
async def get_latest_readings():
    """Get latest readings from all devices"""
    return latest_readings

@app.get("/api/readings-history")
async def get_readings_history(limit: int = 100):
    """Get historical readings"""
    return readings_history[-limit:]

@app.get("/api/carbon-credits/{device_id}")
async def calculate_carbon_credits(device_id: str):
    """Calculate carbon credits for a device"""
    if device_id not in latest_readings:
        raise HTTPException(status_code=404, detail="Device not found")
    
    reading = latest_readings[device_id]
    
    # Morocco grid emission factor (tCO2/MWh)
    morocco_ef = 0.81
    
    # Convert kWh to MWh
    export_mwh = reading["total_energy_kwh"] / 1000.0 * 0.98  # 98% export efficiency
    
    # Calculate emissions
    baseline_emissions = export_mwh * morocco_ef
    project_emissions = 0  # Solar has zero operational emissions
    emission_reductions = baseline_emissions
    
    carbon_credit_data = CarbonCreditData(
        reporting_period=reading["timestamp"],
        project_info={
            "project_name": f"ESP32 Solar Monitor - {device_id}",
            "project_id": f"VCC-{device_id}",
            "location": "Morocco",
            "capacity_mw": 0.001  # 1kW = 0.001MW
        },
        monitoring_data={
            "gross_generation_mwh": reading["total_energy_kwh"] / 1000.0,
            "net_export_mwh": export_mwh,
            "capacity_factor": (reading["ac_power_kw"] / 0.001) * 100 if reading["ac_power_kw"] > 0 else 0,
            "average_irradiance": reading["irradiance_w_m2"],
            "current_rms": reading["current"],
            "system_efficiency": reading["efficiency"]
        },
        calculations={
            "baseline_emissions_tco2": baseline_emissions,
            "project_emissions_tco2": project_emissions,
            "emission_reductions_tco2": emission_reductions,
            "carbon_credits_generated": emission_reductions
        }
    )
    
    return carbon_credit_data

@app.post("/api/guardian/submit/{device_id}")
async def submit_to_guardian(device_id: str):
    """Submit device data to Guardian platform"""
    if device_id not in latest_readings:
        raise HTTPException(status_code=404, detail="Device not found")
    
    reading = latest_readings[device_id]
    
    try:
        result = guardian_client.submit_mrv_data(reading)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Guardian submission failed: {str(e)}")

@app.get("/api/guardian/format/{device_id}")
async def get_guardian_format(device_id: str):
    """Get Guardian-formatted data for a device"""
    if device_id not in latest_readings:
        raise HTTPException(status_code=404, detail="Device not found")
    
    reading = latest_readings[device_id]
    
    try:
        formatted_data = guardian_client.format_mrv_data(reading)
        return formatted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Guardian formatting failed: {str(e)}")

@app.get("/api/guardian/policies")
async def get_guardian_policies():
    """Get available Guardian policies"""
    try:
        result = guardian_client.get_policy_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Guardian policies: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await manager.connect(websocket)
    try:
        while True:
            # Send latest readings every 5 seconds
            if latest_readings:
                await websocket.send_text(json.dumps({
                    "type": "latest_readings",
                    "data": latest_readings
                }))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
#
 Embedded dashboard HTML as fallback
embedded_dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Carbon Credit Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .status { 
            display: inline-block; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: bold; 
        }
        .status.online { 
            background: #4CAF50; 
        }
        .status.offline { 
            background: #f44336; 
        }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .card { 
            background: rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(10px); 
            border-radius: 15px; 
            padding: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.2); 
        }
        .card h3 { 
            margin-top: 0; 
            color: #fff; 
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 10px; 
            background: rgba(255, 255, 255, 0.1); 
            border-radius: 8px; 
        }
        .metric-value { 
            font-weight: bold; 
            color: #4CAF50; 
        }
        .carbon-credits { 
            background: linear-gradient(45deg, #4CAF50, #45a049); 
            text-align: center; 
            padding: 30px; 
            border-radius: 15px; 
            margin: 20px 0; 
        }
        .carbon-credits h2 { 
            margin: 0; 
            font-size: 2.5em; 
        }
        .carbon-credits p { 
            margin: 10px 0 0 0; 
            opacity: 0.9; 
        }
        .last-update { 
            text-align: center; 
            opacity: 0.7; 
            margin-top: 20px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌞 ESP32 Carbon Credit Dashboard</h1>
            <p>Real-time monitoring of solar energy generation and carbon credit calculation</p>
            <span id="connectionStatus" class="status offline">Connecting...</span>
        </div>

        <div id="devicesContainer"></div>

        <div class="carbon-credits">
            <h2 id="totalCredits">0.000</h2>
            <p>Total Carbon Credits Generated (tCO2)</p>
        </div>

        <div class="last-update">
            Last updated: <span id="lastUpdate">Never</span>
        </div>
    </div>

    <script>
        // WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connectionStatus = document.getElementById('connectionStatus');
        const devicesContainer = document.getElementById('devicesContainer');
        const totalCreditsElement = document.getElementById('totalCredits');
        const lastUpdateElement = document.getElementById('lastUpdate');

        ws.onopen = function(event) {
            connectionStatus.textContent = 'Connected';
            connectionStatus.className = 'status online';
        };

        ws.onclose = function(event) {
            connectionStatus.textContent = 'Disconnected';
            connectionStatus.className = 'status offline';
        };

        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            
            if (message.type === 'energy_reading') {
                updateDashboard(message.data);
            } else if (message.type === 'latest_readings') {
                Object.values(message.data).forEach(reading => {
                    updateDashboard(reading);
                });
            }
        };

        function updateDashboard(reading) {
            // Update device cards
            let deviceCard = document.getElementById(`device-${reading.device_id}`);
            if (!deviceCard) {
                deviceCard = createDeviceCard(reading.device_id);
                devicesContainer.appendChild(deviceCard);
            }

            // Update metrics
            updateDeviceMetrics(deviceCard, reading);
            
            // Update carbon credits
            updateCarbonCredits(reading);
            
            // Update timestamp
            lastUpdateElement.textContent = new Date(reading.timestamp).toLocaleString();
        }

        function createDeviceCard(deviceId) {
            const card = document.createElement('div');
            card.className = 'card';
            card.id = `device-${deviceId}`;
            card.innerHTML = `
                <h3>📱 Device: ${deviceId}</h3>
                <div class="grid" style="grid-template-columns: 1fr 1fr;">
                    <div class="metric">
                        <span>Power:</span>
                        <span class="metric-value" id="${deviceId}-power">0 W</span>
                    </div>
                    <div class="metric">
                        <span>Current:</span>
                        <span class="metric-value" id="${deviceId}-current">0 A</span>
                    </div>
                    <div class="metric">
                        <span>Energy:</span>
                        <span class="metric-value" id="${deviceId}-energy">0 kWh</span>
                    </div>
                    <div class="metric">
                        <span>Efficiency:</span>
                        <span class="metric-value" id="${deviceId}-efficiency">0%</span>
                    </div>
                    <div class="metric">
                        <span>Temperature:</span>
                        <span class="metric-value" id="${deviceId}-temp">0°C</span>
                    </div>
                    <div class="metric">
                        <span>Irradiance:</span>
                        <span class="metric-value" id="${deviceId}-irradiance">0 W/m²</span>
                    </div>
                </div>
            `;
            return card;
        }

        function updateDeviceMetrics(card, reading) {
            const deviceId = reading.device_id;
            document.getElementById(`${deviceId}-power`).textContent = `${reading.power.toFixed(1)} W`;
            document.getElementById(`${deviceId}-current`).textContent = `${reading.current.toFixed(3)} A`;
            document.getElementById(`${deviceId}-energy`).textContent = `${reading.total_energy_kwh.toFixed(4)} kWh`;
            document.getElementById(`${deviceId}-efficiency`).textContent = `${(reading.efficiency * 100).toFixed(1)}%`;
            document.getElementById(`${deviceId}-temp`).textContent = `${reading.ambient_temp_c.toFixed(1)}°C`;
            document.getElementById(`${deviceId}-irradiance`).textContent = `${reading.irradiance_w_m2.toFixed(0)} W/m²`;
        }

        function updateCarbonCredits(reading) {
            // Calculate carbon credits (Morocco emission factor: 0.81 tCO2/MWh)
            const morocco_ef = 0.81;
            const export_mwh = reading.total_energy_kwh / 1000.0 * 0.98;
            const carbon_credits = export_mwh * morocco_ef;
            
            totalCreditsElement.textContent = carbon_credits.toFixed(6);
        }

        // Fetch initial data
        fetch('/api/latest-readings')
            .then(response => response.json())
            .then(data => {
                Object.values(data).forEach(reading => {
                    updateDashboard(reading);
                });
            })
            .catch(error => console.error('Error fetching initial data:', error));
    </script>
</body>
</html>
"""