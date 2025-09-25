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
from supabase import create_client, Client

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
    print(f"✅ Connected to Supabase: {SUPABASE_URL}")
except Exception as e:
    print(f"❌ Supabase connection error: {e}")
    supabase = None

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
device_last_seen = {}

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the real-time dashboard"""
    return HTMLResponse(content=dashboard_html, status_code=200)

@app.post("/api/energy-data")
async def receive_energy_data(reading: Dict[str, Any]):
    """Receive energy data from ESP32"""
    try:
        # Validate required fields
        required_fields = ["device_id", "current", "voltage", "power"]  # Removed timestamp as required
        for field in required_fields:
            if field not in reading:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Fix timestamp - use server time instead of ESP32's fake timestamp
        server_time = datetime.now()
        reading["timestamp"] = server_time.isoformat()
        reading["server_received_at"] = server_time.isoformat()
        
        # Store in memory
        latest_readings[reading["device_id"]] = reading
        readings_history.append(reading)
        device_last_seen[reading["device_id"]] = server_time
        
        # Keep only last 1000 readings in memory
        if len(readings_history) > 1000:
            readings_history.pop(0)
        
        # Store in Supabase with corrected timestamp
        if supabase:
            try:
                # Create a copy for database with proper timestamp (remove esp32_timestamp for now)
                db_reading = reading.copy()
                db_reading["timestamp"] = server_time.isoformat()
                # Remove any fields that don't exist in the database
                db_reading.pop("server_received_at", None)
                
                result = supabase.table("energy_readings").insert(db_reading).execute()
                current_time = server_time.strftime("%H:%M:%S")
                print(f"📊 [{current_time}] Stored in Supabase: {reading['device_id']} - {reading['power']}W")
            except Exception as e:
                print(f"❌ Supabase insert error: {e}")
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "energy_reading",
            "data": reading
        }))
        
        current_time = server_time.strftime("%H:%M:%S")
        print(f"📊 [{current_time}] Received data from {reading['device_id']}: {reading['power']}W")
        
        return {"status": "success", "message": "Data received and stored", "server_time": server_time.isoformat()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check which devices are online (received data in last 30 seconds)
    now = datetime.now()
    online_devices = []
    offline_devices = []
    
    for device_id, last_seen in device_last_seen.items():
        time_diff = (now - last_seen).total_seconds()
        if time_diff <= 30:  # 30 seconds timeout
            online_devices.append(device_id)
        else:
            offline_devices.append(device_id)
    
    return {
        "status": "healthy",
        "timestamp": now.isoformat(),
        "total_devices": len(device_last_seen),
        "online_devices": online_devices,
        "offline_devices": offline_devices,
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

@app.get("/api/supabase-data/{device_id}")
async def get_supabase_data(device_id: str, limit: int = 10):
    """Get data from Supabase for a specific device"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not connected")
    
    try:
        result = supabase.table("energy_readings").select("*").eq("device_id", device_id).order("timestamp", desc=True).limit(limit).execute()
        return {
            "device_id": device_id,
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase query error: {str(e)}")

@app.get("/api/supabase-stats")
async def get_supabase_stats():
    """Get statistics from Supabase"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not connected")
    
    try:
        # Get total count
        result = supabase.table("energy_readings").select("*", count="exact").execute()
        total_count = result.count
        
        # Get unique devices
        devices_result = supabase.table("energy_readings").select("device_id").execute()
        unique_devices = list(set([row["device_id"] for row in devices_result.data]))
        
        # Get latest readings per device
        latest_per_device = {}
        for device in unique_devices:
            latest = supabase.table("energy_readings").select("*").eq("device_id", device).order("timestamp", desc=True).limit(1).execute()
            if latest.data:
                latest_per_device[device] = latest.data[0]
        
        return {
            "total_readings": total_count,
            "unique_devices": len(unique_devices),
            "devices": unique_devices,
            "latest_per_device": latest_per_device
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase stats error: {str(e)}")

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

# Enhanced Dashboard HTML with Supabase integration
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
        .supabase-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }
        .supabase-button {
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .supabase-button:hover {
            background: #1976D2;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .device-offline {
            opacity: 0.6;
            border: 2px solid #f44336 !important;
        }
        .device-online {
            border: 2px solid #4CAF50 !important;
        }
        .status {
            font-size: 10px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌞 ESP32 Carbon Credit Dashboard</h1>
            <p>Real-time monitoring with Supabase integration</p>
            <span id="connectionStatus" class="status offline">Connecting...</span>
        </div>

        <div class="supabase-section">
            <h3>📊 Supabase Database Status</h3>
            <div class="stats-grid" id="supabaseStats">
                <div class="metric">
                    <span>Total Readings:</span>
                    <span class="metric-value" id="totalReadings">Loading...</span>
                </div>
                <div class="metric">
                    <span>Unique Devices:</span>
                    <span class="metric-value" id="uniqueDevices">Loading...</span>
                </div>
                <div class="metric">
                    <span>Database Status:</span>
                    <span class="metric-value" id="dbStatus">Loading...</span>
                </div>
            </div>
            <button class="supabase-button" onclick="refreshSupabaseStats()">🔄 Refresh Stats</button>
            <button class="supabase-button" onclick="viewSupabaseData()">📋 View Data</button>
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
            
            // Update timestamp - fix invalid date issue
            try {
                const timestamp = new Date(reading.timestamp);
                if (isNaN(timestamp.getTime())) {
                    // If timestamp is invalid, use current time
                    lastUpdateElement.textContent = new Date().toLocaleString();
                } else {
                    lastUpdateElement.textContent = timestamp.toLocaleString();
                }
            } catch (e) {
                lastUpdateElement.textContent = new Date().toLocaleString();
            }
            
            // Update device last seen time and connection status
            updateDeviceStatus(reading.device_id, reading.timestamp);
        }

        function createDeviceCard(deviceId) {
            const card = document.createElement('div');
            card.className = 'card';
            card.id = `device-${deviceId}`;
            card.innerHTML = `
                <h3>📱 Device: ${deviceId} <span class="status online" id="${deviceId}-status">Online</span></h3>
                <div class="metric">
                    <span>Last Seen:</span>
                    <span class="metric-value" id="${deviceId}-lastseen">Never</span>
                </div>
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
            try {
                const timestamp = new Date(reading.timestamp);
                const time = isNaN(timestamp.getTime()) ? 
                    new Date().toLocaleTimeString() : 
                    timestamp.toLocaleTimeString();
                
                powerChart.data.labels.push(time);
                powerChart.data.datasets[0].data.push(reading.power || 0);
                
                // Keep only last 20 points
                if (powerChart.data.labels.length > 20) {
                    powerChart.data.labels.shift();
                    powerChart.data.datasets[0].data.shift();
                }
                
                powerChart.update('none');
            } catch (e) {
                console.error('Error updating chart:', e);
            }
        }

        function updateCarbonCredits(reading) {
            // Calculate carbon credits (Morocco emission factor: 0.81 tCO2/MWh)
            const morocco_ef = 0.81;
            const export_mwh = (reading.total_energy_kwh || 0) / 1000.0 * 0.98;
            const carbon_credits = export_mwh * morocco_ef;
            
            totalCreditsElement.textContent = carbon_credits.toFixed(6);
        }

        function refreshSupabaseStats() {
            fetch('/api/supabase-stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('totalReadings').textContent = data.total_readings;
                    document.getElementById('uniqueDevices').textContent = data.unique_devices;
                    document.getElementById('dbStatus').textContent = 'Connected ✅';
                    console.log('Supabase stats:', data);
                })
                .catch(error => {
                    document.getElementById('dbStatus').textContent = 'Error ❌';
                    console.error('Supabase stats error:', error);
                });
        }

        function viewSupabaseData() {
            const deviceIds = Object.keys(latest_readings);
            if (deviceIds.length === 0) {
                alert('No devices available');
                return;
            }
            
            const deviceId = deviceIds[0];
            window.open(`/api/supabase-data/${deviceId}`, '_blank');
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

        // Device status tracking
        let deviceLastSeen = {};
        const DEVICE_TIMEOUT = 30000; // 30 seconds timeout

        function updateDeviceStatus(deviceId, timestamp) {
            try {
                const lastSeenTime = new Date(timestamp);
                if (isNaN(lastSeenTime.getTime())) {
                    // If timestamp is invalid, use current time
                    deviceLastSeen[deviceId] = new Date();
                } else {
                    deviceLastSeen[deviceId] = lastSeenTime;
                }
                
                // Update last seen display
                const lastSeenElement = document.getElementById(`${deviceId}-lastseen`);
                if (lastSeenElement) {
                    lastSeenElement.textContent = deviceLastSeen[deviceId].toLocaleTimeString();
                }
                
                // Update status to online
                const statusElement = document.getElementById(`${deviceId}-status`);
                if (statusElement) {
                    statusElement.textContent = 'Online';
                    statusElement.className = 'status online';
                }
            } catch (e) {
                console.error('Error updating device status:', e);
            }
        }

        function checkDeviceConnections() {
            const now = new Date();
            
            Object.keys(deviceLastSeen).forEach(deviceId => {
                const lastSeen = deviceLastSeen[deviceId];
                const timeDiff = now - lastSeen;
                
                const statusElement = document.getElementById(`${deviceId}-status`);
                const deviceCard = document.getElementById(`device-${deviceId}`);
                
                if (statusElement && deviceCard) {
                    if (timeDiff > DEVICE_TIMEOUT) {
                        statusElement.textContent = 'Offline';
                        statusElement.className = 'status offline';
                        deviceCard.className = 'card device-offline';
                    } else {
                        statusElement.textContent = 'Online';
                        statusElement.className = 'status online';
                        deviceCard.className = 'card device-online';
                    }
                }
            });
        }

        function formatTimestamp(timestamp) {
            try {
                const date = new Date(timestamp);
                if (isNaN(date.getTime())) {
                    return 'Invalid Date';
                }
                // Format with local timezone
                return date.toLocaleString(undefined, {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                });
            } catch (e) {
                return 'Invalid Date';
            }
        }

        // Load Supabase stats on page load
        refreshSupabaseStats();
        
        // Refresh Supabase stats every 30 seconds
        setInterval(refreshSupabaseStats, 30000);
        
        // Check device connections every 5 seconds
        setInterval(checkDeviceConnections, 5000);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting ESP32 Carbon Credit Backend with Supabase on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔌 ESP32 endpoint: http://localhost:{port}/api/energy-data")
    print(f"📋 Supabase stats: http://localhost:{port}/api/supabase-stats")
    uvicorn.run(app, host="0.0.0.0", port=port)