#!/usr/bin/env python3
"""
VerifiedCC Python Backend
Receives ESP32 data and stores it in Supabase
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
from guardian_service import GuardianService, GuardianConfig, create_energy_report_from_data
from energy_data_aggregator import EnergyDataAggregator, AggregatedEnergyReport
from guardian_submission_scheduler import GuardianSubmissionScheduler, SubmissionConfig, SubmissionTrigger
from guardian_config_manager import GuardianConfigManager
from guardian_submissions_db import GuardianSubmissionsDB
from guardian_connection_validator import validate_guardian_on_startup

# Load environment variables
load_dotenv()

# Configure comprehensive Guardian logging
from guardian_logging_config import setup_guardian_logging, get_logging_health_status
from guardian_error_handler import get_guardian_error_handler

# Setup Guardian logging with environment-based configuration
logging_config = setup_guardian_logging()
logger = logging.getLogger('guardian.main')

# Initialize FastAPI app
app = FastAPI(
    title="VerifiedCC Backend",
    description="Python backend for ESP32 energy data collection and Supabase storage",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ SUPABASE_URL and SUPABASE_KEY environment variables are required")
    raise RuntimeError("Missing Supabase configuration")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logger.info("🔧 Supabase client initialized")

# Initialize Guardian service
guardian_config = GuardianConfig(
    base_url=os.getenv("GUARDIAN_URL", "http://localhost:3000"),
    username=os.getenv("GUARDIAN_USERNAME"),
    password=os.getenv("GUARDIAN_PASSWORD"),
    api_key=os.getenv("GUARDIAN_API_KEY")  # Legacy support
)
guardian_service = GuardianService(guardian_config)
logger.info("🔧 Guardian service initialized")

# Initialize Energy Data Aggregator
energy_aggregator = EnergyDataAggregator(supabase_client=supabase)
logger.info("🔧 Energy Data Aggregator initialized")

# Initialize Guardian Configuration Manager
guardian_config_manager = GuardianConfigManager(guardian_service)
logger.info("🔧 Guardian Configuration Manager initialized")

# Initialize Guardian Submissions Database
guardian_submissions_db = GuardianSubmissionsDB(supabase)
logger.info("🔧 Guardian Submissions Database initialized")

# Initialize Guardian Submission Scheduler
submission_config = SubmissionConfig(
    submission_enabled=os.getenv("GUARDIAN_SUBMISSION_ENABLED", "true").lower() == "true",
    default_policy_id=os.getenv("GUARDIAN_DEFAULT_POLICY_ID"),
    min_data_completeness=float(os.getenv("GUARDIAN_MIN_DATA_COMPLETENESS", "80.0")),
    max_concurrent_submissions=int(os.getenv("GUARDIAN_MAX_CONCURRENT_SUBMISSIONS", "5"))
)
guardian_scheduler = GuardianSubmissionScheduler(supabase, submission_config)
logger.info("🔧 Guardian Submission Scheduler initialized")
logger.info(f"📍 Database URL: {SUPABASE_URL}")

# Data models
class ESP32Data(BaseModel):
    device_id: str
    timestamp: str
    current: float = 0.0
    voltage: float = 220.0
    power: float
    # SCADA simulation data
    ac_power_kw: Optional[float] = None
    total_energy_kwh: Optional[float] = 0.0
    grid_frequency_hz: Optional[float] = 50.0
    power_factor: Optional[float] = 0.95
    ambient_temp_c: Optional[float] = 25.0
    irradiance_w_m2: Optional[float] = 0.0
    system_status: Optional[int] = 1
    efficiency: Optional[float] = 0.96

class HealthResponse(BaseModel):
    status: str
    message: str
    database: str
    timestamp: str
    total_records: int

class DeviceStats(BaseModel):
    device_id: str
    total_readings: int
    max_power: float
    total_energy: float
    last_seen: str

class DeviceStatsResponse(BaseModel):
    devices: List[DeviceStats]
    total_devices: int
    total_readings: int

# ------------------------
# Health Check & Database Connection Test
# ------------------------
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with database connection test"""
    try:
        # Test Supabase connection
        result = supabase.table("sensor_readings").select("*", count="exact").execute()
        
        total_records = result.count if result.count is not None else 0
        
        return HealthResponse(
            status="healthy",
            message="Backend and database connected successfully",
            database="Supabase PostgreSQL",
            timestamp=datetime.now().isoformat(),
            total_records=total_records
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": "Server health check failed"}
        )

# ------------------------
# ESP32 Data Ingestion Endpoint
# ------------------------
@app.post("/api/energy-data")
async def receive_energy_data(esp32_data: ESP32Data):
    """Receive and store ESP32 energy data in Supabase"""
    try:
        logger.info(f"📡 Received ESP32 data: {esp32_data.model_dump()}")
        
        # Prepare data for insertion
        insert_data = {
            "device_id": esp32_data.device_id,
            "timestamp": esp32_data.timestamp,
            "current": esp32_data.current,
            "voltage": esp32_data.voltage,
            "power": esp32_data.power,
            "ac_power_kw": esp32_data.ac_power_kw or esp32_data.power / 1000,
            "total_energy_kwh": esp32_data.total_energy_kwh,
            "grid_frequency_hz": esp32_data.grid_frequency_hz,
            "power_factor": esp32_data.power_factor,
            "ambient_temp_c": esp32_data.ambient_temp_c,
            "irradiance_w_m2": esp32_data.irradiance_w_m2,
            "system_status": esp32_data.system_status,
            "efficiency": esp32_data.efficiency
        }
        
        # Store in Supabase
        result = supabase.table("sensor_readings").insert(insert_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Database insertion failed")
        
        stored_data = result.data[0]
        logger.info(f"✅ Data successfully stored in Supabase: {stored_data}")
        
        # Convert datetime objects to strings for JSON serialization
        if stored_data and 'timestamp' in stored_data:
            stored_data['timestamp'] = str(stored_data['timestamp'])
        if stored_data and 'created_at' in stored_data:
            stored_data['created_at'] = str(stored_data['created_at'])
        
        return {
            "success": True,
            "message": "Data received and stored in database",
            "data": stored_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        logger.error(f"❌ Invalid timestamp format: {e}")
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    except Exception as e:
        logger.error(f"❌ Unexpected error in /api/energy-data: {e}")
        raise HTTPException(status_code=500, detail="Server error")

# ------------------------
# Get Latest Energy Data for Frontend
# ------------------------
@app.get("/api/energy-data/latest")
async def get_latest_energy_data():
    """Get the most recent energy data reading"""
    try:
        result = supabase.table("sensor_readings")\
            .select("*")\
            .order("id", desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="No data available")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in /api/energy-data/latest: {e}")
        raise HTTPException(status_code=500, detail="Server error")

# ------------------------
# Get Historical Data for Charts
# ------------------------
@app.get("/api/energy-data/history")
async def get_energy_data_history(
    period: str = Query("today", description="Time period: hour, today, week, month"),
    limit: int = Query(100, description="Maximum number of records to return")
):
    """Get historical energy data for specified time period"""
    try:
        now = datetime.now()
        
        # Calculate start time based on period
        if period == "hour":
            start_time = now - timedelta(hours=1)
        elif period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_time = now - timedelta(days=7)
        elif period == "month":
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = supabase.table("sensor_readings")\
            .select("*")\
            .gte("timestamp", start_time.isoformat())\
            .lte("timestamp", now.isoformat())\
            .order("timestamp", desc=False)\
            .limit(limit)\
            .execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"❌ Error in /api/energy-data/history: {e}")
        raise HTTPException(status_code=500, detail="Server error")

# ------------------------
# Get Device Statistics
# ------------------------
@app.get("/api/devices/stats", response_model=DeviceStatsResponse)
async def get_device_stats():
    """Get statistics for all devices"""
    try:
        result = supabase.table("sensor_readings")\
            .select("device_id, power, total_energy_kwh, timestamp")\
            .order("timestamp", desc=True)\
            .execute()
        
        if not result.data:
            return DeviceStatsResponse(devices=[], total_devices=0, total_readings=0)
        
        # Calculate statistics
        devices_dict: Dict[str, Dict[str, Any]] = {}
        
        for reading in result.data:
            device_id = reading["device_id"]
            
            if device_id not in devices_dict:
                devices_dict[device_id] = {
                    "device_id": device_id,
                    "total_readings": 0,
                    "max_power": 0.0,
                    "total_energy": 0.0,
                    "last_seen": reading["timestamp"]
                }
            
            devices_dict[device_id]["total_readings"] += 1
            devices_dict[device_id]["max_power"] = max(
                devices_dict[device_id]["max_power"], 
                reading["power"] or 0.0
            )
            devices_dict[device_id]["total_energy"] = max(
                devices_dict[device_id]["total_energy"], 
                reading["total_energy_kwh"] or 0.0
            )
        
        devices = [DeviceStats(**device_data) for device_data in devices_dict.values()]
        
        return DeviceStatsResponse(
            devices=devices,
            total_devices=len(devices),
            total_readings=len(result.data)
        )
        
    except Exception as e:
        logger.error(f"❌ Error in /api/devices/stats: {e}")
        raise HTTPException(status_code=500, detail="Server error")

# ------------------------
# Startup event
# ------------------------
@app.on_event("startup")
async def startup_event():
    """Test database connection and start Guardian scheduler on startup"""
    try:
        logger.info("🔍 Testing Supabase connection...")
        result = supabase.table("sensor_readings").select("*", count="exact").execute()
        logger.info("✅ Supabase connection successful")
        
        # Start Guardian submission scheduler
        if submission_config.submission_enabled:
            await guardian_scheduler.start()
            logger.info("🤖 Guardian submission scheduler started")
        else:
            logger.info("📵 Guardian submission scheduler disabled")
        
        logger.info("🚀 VerifiedCC Python Backend started successfully")
        logger.info("📊 Health check: http://localhost:5000/api/health")
        logger.info("📡 ESP32 endpoint: http://localhost:5000/api/energy-data")
        logger.info("📈 Latest data: http://localhost:5000/api/energy-data/latest")
        logger.info("📋 Device stats: http://localhost:5000/api/devices/stats")
        logger.info("🔄 Energy aggregation: http://localhost:5000/api/energy-data/aggregate/{device_id}")
        logger.info("✅ Guardian readiness: http://localhost:5000/api/energy-data/guardian-readiness/{device_id}")
        logger.info("🤖 Guardian scheduler: http://localhost:5000/api/guardian/scheduler/status")
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        logger.warning("⚠️  Server starting anyway, but database operations may fail")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop Guardian scheduler on shutdown"""
    try:
        if guardian_scheduler:
            await guardian_scheduler.stop()
            logger.info("🛑 Guardian submission scheduler stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping Guardian scheduler: {e}")

# ------------------------
# Guardian Integration Endpoints
# ------------------------

class GuardianSubmissionRequest(BaseModel):
    device_id: str
    period_hours: int = Field(default=24, description="Period in hours to aggregate data")
    policy_id: Optional[str] = Field(default=None, description="Guardian policy ID")

@app.get("/api/guardian/health")
async def guardian_health_check():
    """Check Guardian API connection status"""
    try:
        health = guardian_service.health_check()
        return health
    except Exception as e:
        logger.error(f"❌ Guardian health check failed: {e}")
        raise HTTPException(status_code=500, detail="Guardian health check failed")

@app.get("/api/guardian/policies")
async def get_guardian_policies():
    """Get available Guardian policies"""
    try:
        policies = guardian_service.get_policies()
        return {"policies": policies, "count": len(policies)}
    except Exception as e:
        logger.error(f"❌ Failed to get Guardian policies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Guardian policies")

@app.get("/api/guardian/tokens")
async def get_guardian_tokens():
    """Get available Guardian tokens (carbon credits)"""
    try:
        tokens = guardian_service.get_tokens()
        return {"tokens": tokens, "count": len(tokens)}
    except Exception as e:
        logger.error(f"❌ Failed to get Guardian tokens: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Guardian tokens")

@app.get("/api/energy-data/aggregate/{device_id}")
async def get_aggregated_energy_data(
    device_id: str,
    target_date: str = Query(None, description="Target date in YYYY-MM-DD format (default: today)"),
    period_hours: int = Query(24, description="Period in hours for aggregation")
):
    """Get aggregated energy data for a device using EnergyDataAggregator"""
    try:
        if target_date:
            # Parse target date
            target_datetime = datetime.fromisoformat(target_date)
        else:
            target_datetime = datetime.now()
        
        if period_hours == 24:
            # Use daily aggregation
            report = energy_aggregator.aggregate_daily_data(device_id, target_datetime)
        else:
            # Use custom period aggregation
            end_time = target_datetime
            start_time = end_time - timedelta(hours=period_hours)
            report = energy_aggregator.aggregate_period_data(device_id, start_time, end_time)
        
        # Convert report to JSON-serializable format
        return {
            "device_id": report.device_id,
            "period": {
                "start": report.period_start.isoformat(),
                "end": report.period_end.isoformat(),
                "hours": (report.period_end - report.period_start).total_seconds() / 3600
            },
            "energy_metrics": {
                "total_energy_kwh": report.energy_metrics.total_energy_kwh,
                "avg_power_w": report.energy_metrics.avg_power_w,
                "max_power_w": report.energy_metrics.max_power_w,
                "min_power_w": report.energy_metrics.min_power_w,
                "peak_to_avg_ratio": report.energy_metrics.peak_to_avg_ratio,
                "capacity_factor": report.energy_metrics.capacity_factor
            },
            "performance_metrics": {
                "avg_efficiency": report.performance_metrics.avg_efficiency,
                "max_efficiency": report.performance_metrics.max_efficiency,
                "min_efficiency": report.performance_metrics.min_efficiency,
                "avg_power_factor": report.performance_metrics.avg_power_factor,
                "avg_grid_frequency": report.performance_metrics.avg_grid_frequency
            },
            "environmental_metrics": {
                "avg_irradiance_w_m2": report.environmental_metrics.avg_irradiance_w_m2,
                "max_irradiance_w_m2": report.environmental_metrics.max_irradiance_w_m2,
                "avg_temperature_c": report.environmental_metrics.avg_temperature_c,
                "max_temperature_c": report.environmental_metrics.max_temperature_c,
                "min_temperature_c": report.environmental_metrics.min_temperature_c
            },
            "data_quality": {
                "total_readings": report.data_quality.total_readings,
                "valid_readings": report.data_quality.valid_readings,
                "missing_readings": report.data_quality.missing_readings,
                "data_completeness_percent": report.data_quality.data_completeness_percent,
                "outlier_count": report.data_quality.outlier_count,
                "measurement_period_hours": report.data_quality.measurement_period_hours
            },
            "verification": {
                "hash": report.verification_hash,
                "data_integrity_score": report.data_integrity_score
            },
            "regional_compliance": report.regional_compliance
        }
        
    except ValueError as e:
        logger.error(f"❌ Aggregation error for {device_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error aggregating data for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Data aggregation failed")

@app.get("/api/energy-data/guardian-readiness/{device_id}")
async def check_guardian_readiness(
    device_id: str,
    target_date: str = Query(None, description="Target date in YYYY-MM-DD format (default: today)")
):
    """Check if device data is ready for Guardian submission"""
    try:
        if target_date:
            target_datetime = datetime.fromisoformat(target_date)
        else:
            target_datetime = datetime.now()
        
        readiness = energy_aggregator.validate_guardian_readiness(device_id, target_datetime)
        
        return readiness
        
    except Exception as e:
        logger.error(f"❌ Error checking Guardian readiness for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Guardian readiness check failed")

@app.post("/api/guardian/submit")
async def submit_to_guardian(request: GuardianSubmissionRequest):
    """Submit aggregated energy data to Guardian for carbon credit verification"""
    try:
        # Use EnergyDataAggregator for improved data processing
        if request.period_hours == 24:
            # Daily aggregation
            aggregated_report = energy_aggregator.aggregate_daily_data(request.device_id)
        else:
            # Custom period aggregation
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=request.period_hours)
            aggregated_report = energy_aggregator.aggregate_period_data(request.device_id, start_time, end_time)
        
        # Convert AggregatedEnergyReport to legacy EnergyReport format for Guardian submission
        from guardian_service import EnergyReport
        
        legacy_report = EnergyReport(
            device_id=aggregated_report.device_id,
            period_start=aggregated_report.period_start,
            period_end=aggregated_report.period_end,
            total_energy_kwh=aggregated_report.energy_metrics.total_energy_kwh,
            avg_power_w=aggregated_report.energy_metrics.avg_power_w,
            max_power_w=aggregated_report.energy_metrics.max_power_w,
            avg_efficiency=aggregated_report.performance_metrics.avg_efficiency,
            avg_irradiance=aggregated_report.environmental_metrics.avg_irradiance_w_m2,
            avg_temperature=aggregated_report.environmental_metrics.avg_temperature_c,
            data_points=aggregated_report.data_quality.valid_readings,
            verification_hash=aggregated_report.verification_hash
        )
        
        # Submit to Guardian
        submission_result = guardian_service.submit_energy_report(
            legacy_report, 
            request.policy_id
        )
        
        if submission_result.get("success"):
            logger.info(f"✅ Successfully submitted {request.device_id} data to Guardian")
            
            return {
                "success": True,
                "message": "Energy data submitted to Guardian successfully",
                "guardian_submission": submission_result,
                "energy_report": {
                    "device_id": aggregated_report.device_id,
                    "period": f"{aggregated_report.period_start.isoformat()} to {aggregated_report.period_end.isoformat()}",
                    "total_energy_kwh": aggregated_report.energy_metrics.total_energy_kwh,
                    "avg_power_w": aggregated_report.energy_metrics.avg_power_w,
                    "data_points": aggregated_report.data_quality.valid_readings,
                    "verification_hash": aggregated_report.verification_hash,
                    "data_integrity_score": aggregated_report.data_integrity_score
                },
                "data_quality": {
                    "completeness_percent": aggregated_report.data_quality.data_completeness_percent,
                    "integrity_score": aggregated_report.data_integrity_score,
                    "outlier_count": aggregated_report.data_quality.outlier_count
                }
            }
        else:
            logger.error(f"❌ Failed to submit {request.device_id} data to Guardian: {submission_result}")
            raise HTTPException(
                status_code=500,
                detail=f"Guardian submission failed: {submission_result.get('message', 'Unknown error')}"
            )
            
    except ValueError as e:
        logger.error(f"❌ Data aggregation error for {request.device_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in Guardian submission: {e}")
        raise HTTPException(status_code=500, detail="Guardian submission failed")

@app.get("/api/guardian/documents/{id}/status")
async def get_guardian_document_status(
    id: str,
    policy_id: str = Query(..., description="Guardian policy ID")
):
    """Get status of a document submitted to Guardian (requirement 3.5)"""
    try:
        status = guardian_service.get_document_status(policy_id, id)
        return status
    except Exception as e:
        logger.error(f"❌ Failed to get Guardian document status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document status")

# ------------------------
# Guardian Scheduler Endpoints
# ------------------------

@app.get("/api/guardian/scheduler/status")
async def get_scheduler_status():
    """Get Guardian submission scheduler status"""
    try:
        status = await guardian_scheduler.get_queue_status()
        return status
    except Exception as e:
        logger.error(f"❌ Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")

@app.post("/api/guardian/scheduler/queue")
async def queue_guardian_submission(
    device_id: str,
    target_date: str = Query(None, description="Target date in YYYY-MM-DD format (default: yesterday)"),
    policy_id: str = Query(None, description="Guardian policy ID (uses default if not specified)"),
    priority: int = Query(0, description="Submission priority (higher = more urgent)")
):
    """Queue a Guardian submission for processing"""
    try:
        # Parse target date
        if target_date:
            target_datetime = datetime.fromisoformat(target_date)
        else:
            # Default to yesterday (allow time for data collection)
            target_datetime = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Queue submission
        success = await guardian_scheduler.queue_submission(
            device_id=device_id,
            target_date=target_datetime,
            policy_id=policy_id,
            trigger=SubmissionTrigger.MANUAL,
            priority=priority
        )
        
        if success:
            return {
                "success": True,
                "message": f"Guardian submission queued for {device_id}",
                "device_id": device_id,
                "target_date": target_datetime.date().isoformat(),
                "policy_id": policy_id or submission_config.default_policy_id,
                "priority": priority
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to queue Guardian submission")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"❌ Error queueing Guardian submission: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue submission")

@app.post("/api/guardian/scheduler/process-daily")
async def trigger_daily_submissions(
    target_date: str = Query(None, description="Target date in YYYY-MM-DD format (default: yesterday)")
):
    """Trigger daily Guardian submissions for all eligible devices"""
    try:
        # Parse target date
        if target_date:
            target_datetime = datetime.fromisoformat(target_date)
        else:
            # Default to yesterday
            target_datetime = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Process daily submissions
        results = await guardian_scheduler.process_daily_submissions(target_datetime)
        
        return {
            "success": True,
            "message": "Daily submissions processed",
            "results": results
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"❌ Error processing daily submissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to process daily submissions")

@app.post("/api/guardian/scheduler/retry-failed")
async def retry_failed_submissions(
    max_age_hours: int = Query(24, description="Maximum age of failed submissions to retry (hours)")
):
    """Retry failed Guardian submissions"""
    try:
        results = await guardian_scheduler.retry_failed_submissions(max_age_hours)
        
        return {
            "success": True,
            "message": "Failed submissions retry processed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrying failed submissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retry submissions")

# ------------------------
# Guardian Configuration Endpoints
# ------------------------

@app.get("/api/guardian/config/summary")
async def get_guardian_config_summary():
    """Get Guardian configuration summary"""
    try:
        summary = guardian_config_manager.get_config_summary()
        return summary
    except Exception as e:
        logger.error(f"❌ Failed to get config summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configuration summary")

@app.get("/api/guardian/config/policy/{device_id}")
async def get_device_policy(
    device_id: str,
    energy_kwh: float = Query(None, description="Energy production for policy selection")
):
    """Get Guardian policy configuration for a specific device"""
    try:
        policy_info = guardian_config_manager.get_policy_for_device(device_id, energy_kwh)
        return policy_info
    except Exception as e:
        logger.error(f"❌ Failed to get device policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to get device policy")

@app.get("/api/guardian/config/validation")
async def validate_guardian_configuration():
    """Validate Guardian configuration and connection (requirement 7.5)"""
    try:
        validation_result = await validate_guardian_on_startup(guardian_service)
        return validation_result
    except Exception as e:
        logger.error(f"❌ Guardian configuration validation failed: {e}")
        raise HTTPException(status_code=500, detail="Guardian configuration validation failed")

@app.get("/api/guardian/config/environment")
async def get_guardian_environment_config():
    """Get Guardian environment configuration (masked sensitive values)"""
    try:
        config = {
            "guardian_url": os.getenv("GUARDIAN_URL", "http://localhost:3000"),
            "guardian_username": os.getenv("GUARDIAN_USERNAME", "").replace(os.getenv("GUARDIAN_USERNAME", ""), "***" if os.getenv("GUARDIAN_USERNAME") else ""),
            "guardian_password_set": bool(os.getenv("GUARDIAN_PASSWORD")),
            "guardian_api_key_set": bool(os.getenv("GUARDIAN_API_KEY")),
            "submission_enabled": os.getenv("GUARDIAN_SUBMISSION_ENABLED", "true").lower() == "true",
            "default_policy_id": os.getenv("GUARDIAN_DEFAULT_POLICY_ID"),
            "daily_submission_time": os.getenv("GUARDIAN_DAILY_SUBMISSION_TIME", "01:00"),
            "min_data_completeness": float(os.getenv("GUARDIAN_MIN_DATA_COMPLETENESS", "80.0")),
            "max_concurrent_submissions": int(os.getenv("GUARDIAN_MAX_CONCURRENT_SUBMISSIONS", "5")),
            "connection_timeout": int(os.getenv("GUARDIAN_CONNECTION_TIMEOUT", "30")),
            "max_retries": int(os.getenv("GUARDIAN_MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("GUARDIAN_RETRY_DELAY", "1.0"))
        }
        
        # Mask username for security
        if config["guardian_username"] != "***":
            username = os.getenv("GUARDIAN_USERNAME", "")
            if len(username) > 3:
                config["guardian_username"] = username[:2] + "***" + username[-1:]
            elif username:
                config["guardian_username"] = "***"
        
        return {
            "configuration": config,
            "timestamp": datetime.now().isoformat(),
            "note": "Sensitive values are masked for security"
        }
    except Exception as e:
        logger.error(f"❌ Failed to get Guardian environment config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Guardian environment configuration")

@app.post("/api/guardian/config/policy/mapping")
async def add_device_policy_mapping(
    device_id: str,
    policy_id: str,
    tag_name: str = "renewable_energy",
    priority: int = 0
):
    """Add device-specific policy mapping"""
    try:
        success = guardian_config_manager.add_device_policy_mapping(
            device_id=device_id,
            policy_id=policy_id,
            tag_name=tag_name,
            priority=priority
        )
        
        if success:
            return {
                "success": True,
                "message": f"Policy mapping added for {device_id}",
                "device_id": device_id,
                "policy_id": policy_id,
                "tag_name": tag_name,
                "priority": priority
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add policy mapping")
            
    except Exception as e:
        logger.error(f"❌ Error adding policy mapping: {e}")
        raise HTTPException(status_code=500, detail="Failed to add policy mapping")

@app.get("/api/guardian/config/timing/{device_id}")
async def check_submission_timing(
    device_id: str,
    data_completeness_percent: float = Query(0, description="Current data completeness percentage"),
    total_energy_kwh: float = Query(0, description="Current total energy production"),
    last_submission_time: str = Query(None, description="Last submission timestamp")
):
    """Check if device should submit now based on timing configuration"""
    try:
        current_data = {
            "data_completeness_percent": data_completeness_percent,
            "total_energy_kwh": total_energy_kwh,
            "last_submission_time": last_submission_time
        }
        
        timing_info = guardian_config_manager.should_submit_now(device_id, current_data)
        return timing_info
        
    except Exception as e:
        logger.error(f"❌ Error checking submission timing: {e}")
        raise HTTPException(status_code=500, detail="Failed to check submission timing")

# ------------------------
# Guardian Submissions Database Endpoints
# ------------------------

@app.get("/api/guardian/submissions")
async def get_guardian_submissions(
    device_id: str = Query(None, description="Filter by device ID"),
    policy_id: str = Query(None, description="Filter by policy ID"),
    status: str = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get Guardian submissions with optional filtering"""
    try:
        from models import GuardianSubmissionQuery, GuardianSubmissionStatus
        
        # Build query
        query = GuardianSubmissionQuery(
            device_id=device_id,
            policy_id=policy_id,
            status=GuardianSubmissionStatus(status) if status else None,
            limit=limit,
            offset=offset
        )
        
        submissions = await guardian_submissions_db.query_submissions(query)
        
        # Convert to JSON-serializable format
        submissions_data = []
        for submission in submissions:
            submission_dict = submission.dict()
            # Convert datetime objects to ISO strings
            for key, value in submission_dict.items():
                if isinstance(value, datetime):
                    submission_dict[key] = value.isoformat()
            submissions_data.append(submission_dict)
        
        return {
            "submissions": submissions_data,
            "count": len(submissions_data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting Guardian submissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get submissions")

@app.get("/api/guardian/submissions/stats")
async def get_guardian_submission_stats(
    device_id: str = Query(None, description="Get stats for specific device")
):
    """Get Guardian submission statistics"""
    try:
        stats = await guardian_submissions_db.get_submission_stats(device_id)
        
        # Convert to JSON-serializable format
        stats_dict = stats.dict()
        return stats_dict
        
    except Exception as e:
        logger.error(f"❌ Error getting submission stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get submission statistics")

@app.get("/api/guardian/submissions/device/{device_id}")
async def get_device_submission_summary(device_id: str):
    """Get Guardian submission summary for a specific device"""
    try:
        summary = await guardian_submissions_db.get_device_summary(device_id)
        
        # Convert to JSON-serializable format
        summary_dict = summary.dict()
        for key, value in summary_dict.items():
            if isinstance(value, datetime):
                summary_dict[key] = value.isoformat()
        
        return summary_dict
        
    except Exception as e:
        logger.error(f"❌ Error getting device submission summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get device summary")

# ------------------------
# Auto-submission based on thresholds
# ------------------------

async def check_auto_submission():
    """Check if any devices meet criteria for automatic Guardian submission"""
    try:
        # Get devices with recent activity
        recent_time = datetime.now() - timedelta(hours=1)
        result = supabase.table("sensor_readings")\
            .select("device_id")\
            .gte("timestamp", recent_time.isoformat())\
            .execute()
        
        if not result.data:
            return
        
        # Get unique device IDs
        device_ids = list(set([r["device_id"] for r in result.data]))
        
        for device_id in device_ids:
            # Check if device has enough data for submission (e.g., 24 hours worth)
            day_ago = datetime.now() - timedelta(hours=24)
            device_result = supabase.table("sensor_readings")\
                .select("*", count="exact")\
                .eq("device_id", device_id)\
                .gte("timestamp", day_ago.isoformat())\
                .execute()
            
            # Auto-submit if device has sufficient data (e.g., >100 readings in 24h)
            if device_result.count and device_result.count > 100:
                logger.info(f"🤖 Auto-submitting {device_id} to Guardian (sufficient data: {device_result.count} readings)")
                
                # Create and submit energy report
                energy_report = create_energy_report_from_data(device_result.data, device_id)
                submission_result = guardian_service.submit_energy_report(energy_report)
                
                if submission_result.get("success"):
                    logger.info(f"✅ Auto-submission successful for {device_id}")
                else:
                    logger.error(f"❌ Auto-submission failed for {device_id}: {submission_result}")
                    
    except Exception as e:
        logger.error(f"❌ Auto-submission check failed: {e}")

        logger.info("📈 Latest data: http://localhost:5000/api/energy-data/latest")
        logger.info("📋 Device stats: http://localhost:5000/api/devices/stats")
        
        # Validate Guardian connection and configuration
        logger.info("🔍 Validating Guardian connection and configuration...")
        guardian_validation = await validate_guardian_on_startup(guardian_service)
        
        if guardian_validation["can_start"]:
            if guardian_validation["overall_status"] == "passed":
                logger.info("✅ Guardian validation passed - all systems ready")
                logger.info("🔗 Guardian endpoints available:")
                logger.info("   📊 Guardian health: http://localhost:5000/api/guardian/health")
                logger.info("   📋 Guardian policies: http://localhost:5000/api/guardian/policies")
                logger.info("   🪙 Guardian tokens: http://localhost:5000/api/guardian/tokens")
                logger.info("   📤 Submit to Guardian: POST http://localhost:5000/api/guardian/submit")
            else:
                logger.warning("⚠️ Guardian validation completed with warnings - some features may not work optimally")
                logger.info("🔗 Guardian endpoints available (with limitations):")
                logger.info("   📊 Guardian health: http://localhost:5000/api/guardian/health")
        else:
            logger.error("❌ Guardian validation failed - Guardian features disabled")
            logger.info("💡 To enable Guardian features:")
            logger.info("💡 1. Check environment variables in .env file")
            logger.info("💡 2. Start Guardian: docker compose -f docker-compose-quickstart.yml up -d")
            logger.info("💡 3. See GUARDIAN_SETUP.md for detailed setup instructions")
            
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        logger.warning("⚠️  Server starting anyway, but database operations may fail")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)