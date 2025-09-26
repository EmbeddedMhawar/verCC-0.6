from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from dashboard_content import dashboard_html
from guardian_integration import guardian_processor
from ams_dashboard_integration import ams_integration

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

# Mount static files directory
app.mount("/static", StaticFiles(directory="assets"), name="static")

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
    """Receive energy data from ESP32 and process through Guardian Tools"""
    try:
        # Validate required fields
        required_fields = ["device_id", "current", "voltage", "power"]
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
        
        # 🔥 NEW: Process through Guardian Tools Architecture
        # Tool 10: Data Source Processing
        try:
            await guardian_processor.process_esp32_data(reading)
            print(f"🔧 Tool 10: Processed {reading['device_id']} data through Guardian pipeline")
        except Exception as e:
            print(f"❌ Guardian Tool 10 error: {e}")
        
        # 🌱 NEW: Process through AMS-I.D Aggregation Pipeline
        try:
            await ams_integration.process_esp32_data(reading)
        except Exception as e:
            print(f"❌ AMS-I.D processing error: {e}")
        
        # Store in Supabase with corrected timestamp
        if supabase:
            try:
                # Create a copy for database with proper timestamp
                db_reading = reading.copy()
                db_reading["timestamp"] = server_time.isoformat()
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
        
        return {
            "status": "success", 
            "message": "Data received, stored, and processed through Guardian Tools", 
            "server_time": server_time.isoformat(),
            "guardian_processed": True
        }
    
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
    """Calculate carbon credits for a device (Legacy endpoint)"""
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

@app.get("/api/guardian/status")
async def get_guardian_status():
    """Get Guardian Tools status summary"""
    return guardian_processor.get_status_summary()

@app.post("/api/guardian/aggregate/{device_id}")
async def trigger_aggregation(device_id: str, hours: int = 1):
    """Tool 07: Trigger data aggregation for a device"""
    try:
        aggregated = guardian_processor.aggregate_data(device_id, hours)
        if aggregated:
            return {
                "success": True,
                "message": f"Aggregated {hours} hours of data for {device_id}",
                "data": aggregated.__dict__
            }
        else:
            return {
                "success": False,
                "message": f"No data found for {device_id} in last {hours} hours"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/guardian/workflow/{device_id}")
async def trigger_complete_workflow(device_id: str):
    """Trigger complete Guardian Tools workflow: Tool 10 → Tool 07 → Tool 03 → Guardian"""
    try:
        result = await guardian_processor.process_complete_workflow(device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/guardian/hedera-records")
async def get_hedera_records():
    """Tool 03: Get all Hedera verification records"""
    return {
        "records": [record.__dict__ for record in guardian_processor.hedera_records],
        "total_records": len(guardian_processor.hedera_records),
        "verified_records": len([r for r in guardian_processor.hedera_records if r.verification_status == "verified"])
    }

@app.get("/api/guardian/aggregated-data")
async def get_aggregated_data():
    """Tool 07: Get all aggregated data reports"""
    return {
        "reports": [data.__dict__ for data in guardian_processor.aggregated_data],
        "total_reports": len(guardian_processor.aggregated_data),
        "total_emission_reductions": sum(a.emission_reductions_tco2 for a in guardian_processor.aggregated_data)
    }

# AMS-I.D Integration Endpoints
@app.get("/api/ams-id/status")
async def get_ams_id_status():
    """Get AMS-I.D integration status"""
    return ams_integration.get_status_summary()

@app.get("/api/ams-id/metrics")
async def get_ams_id_metrics():
    """Get AMS-I.D metrics for dashboard"""
    return ams_integration.get_dashboard_metrics()

@app.post("/api/ams-id/initialize")
async def initialize_ams_id():
    """Initialize AMS-I.D integration"""
    try:
        success = await ams_integration.initialize()
        return {
            "success": success,
            "message": "AMS-I.D integration initialized successfully" if success else "Initialization failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ams-id/aggregate/{device_id}")
async def trigger_ams_aggregation(device_id: str, hours: int = 1):
    """Trigger AMS-I.D aggregation for a device"""
    try:
        result = await ams_integration.trigger_aggregation(device_id, hours)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ams-id/workflow/{device_id}")
async def run_ams_complete_workflow(device_id: str):
    """Run complete AMS-I.D workflow: Aggregate → Submit to Guardian"""
    try:
        result = await ams_integration.run_complete_workflow(device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ams-id/workflow/all")
async def run_ams_workflow_all_devices():
    """Run AMS-I.D workflow for all devices"""
    try:
        result = await ams_integration.run_complete_workflow()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Dashboard HTML is imported from dashboard_content.py

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting ESP32 Carbon Credit Backend with Supabase on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔌 ESP32 endpoint: http://localhost:{port}/api/energy-data")
    print(f"📋 Supabase stats: http://localhost:{port}/api/supabase-stats")
    uvicorn.run(app, host="0.0.0.0", port=port)