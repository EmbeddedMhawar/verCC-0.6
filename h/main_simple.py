from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

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

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:  # Create a copy to avoid modification during iteration
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Store latest readings in memory
latest_readings = {}
readings_history = []

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the real-time dashboard"""
    return HTMLResponse(content=dashboard_html, status_code=200)

@app.post("/api/energy-data")
async def receive_energy_data(reading: Dict[str, Any]):
    """Receive energy data from ESP32"""
    try:
        # Validate required fields
        required_fields = ["device_id", "timestamp", "current", "voltage", "power"]
        for field in required_fields:
            if field not in reading:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Store in memory
        latest_readings[reading["device_id"]] = reading
        readings_history.append(reading)
        
        # Keep only last 1000 readings in memory
        if len(readings_history) > 1000:
            readings_history.pop(0)
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "energy_reading",
            "data": reading
        }))
        
        print(f"📊 Received data from {reading['device_id']}: {reading['power']}W")
        
        return {"status": "success", "message": "Data received and stored"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "devices_connected": len(latest_readings)
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
    total_energy_kwh = reading.get("total_energy_kwh", 0)
    export_mwh = total_energy_kwh / 1000.0 * 0.98  # 98% export efficiency
    
    # Calculate emissions
    baseline_emissions = export_mwh * morocco_ef
    project_emissions = 0  # Solar has zero operational emissions
    emission_reductions = baseline_emissions
    
    carbon_credit_data = {
        "methodology": "GCCM001_v4",
        "reporting_period": reading["timestamp"],
        "project_info": {
            "project_name": f"ESP32 Solar Monitor - {device_id}",
            "project_id": f"VCC-{device_id}",
            "location": "Morocco",
            "capacity_mw": 0.001  # 1kW = 0.001MW
        },
        "monitoring_data": {
            "gross_generation_mwh": total_energy_kwh / 1000.0,
            "net_export_mwh": export_mwh,
            "capacity_factor": (reading.get("ac_power_kw", 0) / 0.001) * 100 if reading.get("ac_power_kw", 0) > 0 else 0,
            "average_irradiance": reading.get("irradiance_w_m2", 0),
            "current_rms": reading.get("current", 0),
            "system_efficiency": reading.get("efficiency", 0)
        },
        "calculations": {
            "baseline_emissions_tco2": baseline_emissions,
            "project_emissions_tco2": project_emissions,
            "emission_reductions_tco2": emission_reductions,
            "carbon_credits_generated": emission_reductions
        }
    }
    
    return carbon_credit_data

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

# Dashboard HTML
dashboard_html = """
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
        .chart-container { 
            position: relative; 
            height: 300px; 
            margin: 20px 0; 
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

        <div class="card">
            <h3>📊 Real-time Power Generation</h3>
            <div class="chart-container">
                <canvas id="powerChart"></canvas>
            </div>
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

        // Chart setup
        const powerCtx = document.getElementById('powerChart').getContext('2d');
        const powerChart = new Chart(powerCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Power (W)',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: 'white' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: 'white' }
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });

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
                updateChart(message.data);
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
            document.getElementById(`${deviceId}-power`).textContent = `${(reading.power || 0).toFixed(1)} W`;
            document.getElementById(`${deviceId}-current`).textContent = `${(reading.current || 0).toFixed(3)} A`;
            document.getElementById(`${deviceId}-energy`).textContent = `${(reading.total_energy_kwh || 0).toFixed(4)} kWh`;
            document.getElementById(`${deviceId}-efficiency`).textContent = `${((reading.efficiency || 0) * 100).toFixed(1)}%`;
            document.getElementById(`${deviceId}-temp`).textContent = `${(reading.ambient_temp_c || 0).toFixed(1)}°C`;
            document.getElementById(`${deviceId}-irradiance`).textContent = `${(reading.irradiance_w_m2 || 0).toFixed(0)} W/m²`;
        }

        function updateChart(reading) {
            const time = new Date(reading.timestamp).toLocaleTimeString();
            
            powerChart.data.labels.push(time);
            powerChart.data.datasets[0].data.push(reading.power || 0);
            
            // Keep only last 20 points
            if (powerChart.data.labels.length > 20) {
                powerChart.data.labels.shift();
                powerChart.data.datasets[0].data.shift();
            }
            
            powerChart.update('none');
        }

        function updateCarbonCredits(reading) {
            // Calculate carbon credits (Morocco emission factor: 0.81 tCO2/MWh)
            const morocco_ef = 0.81;
            const export_mwh = (reading.total_energy_kwh || 0) / 1000.0 * 0.98;
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

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting ESP32 Carbon Credit Backend on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔌 ESP32 endpoint: http://localhost:{port}/api/energy-data")
    uvicorn.run(app, host="0.0.0.0", port=port)