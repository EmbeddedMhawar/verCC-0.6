#!/usr/bin/env python3
"""
AMS-I.D Dashboard Integration
Integrates the AMS-I.D aggregation tool with the existing dashboard
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ams_id_aggregator import AMSIDAggregator, AMSIDConfig, EnergyMeasurement, AggregatedReport
from esp32_ams_integration import ESP32AMSIntegration

logger = logging.getLogger(__name__)

class AMSDashboardIntegration:
    """Integration layer between AMS-I.D aggregator and dashboard"""
    
    def __init__(self):
        self.config = AMSIDConfig.from_file()
        self.aggregator = AMSIDAggregator(self.config)
        self.integration = ESP32AMSIntegration(self.config)
        
        # Status tracking
        self.is_initialized = False
        self.is_running = False
        self.last_aggregation = None
        self.total_carbon_credits = 0.0
        self.activity_log = []
        
        # Statistics
        self.stats = {
            "total_measurements": 0,
            "total_projects": 0,
            "total_reports": 0,
            "total_energy_mwh": 0.0,
            "total_emission_reductions": 0.0,
            "devices_processed": set(),
            "last_submission": None,
            "guardian_authenticated": False
        }
    
    async def initialize(self) -> bool:
        """Initialize the AMS-I.D integration"""
        try:
            self.log_activity("🔧 Initializing AMS-I.D integration...")
            
            # Initialize the ESP32 integration
            if not self.integration.initialize():
                self.log_activity("❌ Failed to initialize ESP32 integration")
                return False
            
            self.is_initialized = True
            self.stats["guardian_authenticated"] = True
            self.log_activity("✅ AMS-I.D integration initialized successfully")
            return True
            
        except Exception as e:
            self.log_activity(f"❌ Initialization error: {e}")
            logger.error(f"AMS integration initialization error: {e}")
            return False
    
    def log_activity(self, message: str):
        """Add activity to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "datetime": datetime.now().isoformat()
        }
        self.activity_log.append(log_entry)
        
        # Keep only last 50 entries
        if len(self.activity_log) > 50:
            self.activity_log.pop(0)
        
        logger.info(f"[{timestamp}] {message}")
    
    async def process_esp32_data(self, reading: Dict[str, Any]) -> bool:
        """Process ESP32 data through AMS-I.D pipeline"""
        try:
            # Convert to EnergyMeasurement format
            measurement = EnergyMeasurement(
                timestamp=reading.get("timestamp", datetime.now().isoformat() + "Z"),
                device_id=reading.get("device_id", "ESP32_001"),
                total_energy_kwh=float(reading.get("total_energy_kwh", 0)),
                irradiance_w_m2=float(reading.get("irradiance_w_m2", 0)),
                ambient_temp_c=float(reading.get("ambient_temp_c", 25)),
                efficiency=float(reading.get("efficiency", 0.85)),
                power=float(reading.get("power", 0)),
                current=float(reading.get("current", 0)),
                voltage=float(reading.get("voltage", 220)),
                power_factor=float(reading.get("power_factor", 0.95))
            )
            
            # Add to aggregator
            self.aggregator.add_measurement(measurement)
            
            # Update statistics
            self.stats["total_measurements"] += 1
            self.stats["devices_processed"].add(measurement.device_id)
            
            # Log activity periodically (every 10 measurements)
            if self.stats["total_measurements"] % 10 == 0:
                self.log_activity(f"📊 Processed {self.stats['total_measurements']} measurements from {len(self.stats['devices_processed'])} devices")
            
            return True
            
        except Exception as e:
            self.log_activity(f"❌ Error processing ESP32 data: {e}")
            logger.error(f"ESP32 data processing error: {e}")
            return False
    
    async def trigger_aggregation(self, device_id: str = None, hours: int = 1) -> Dict[str, Any]:
        """Trigger manual aggregation for testing"""
        try:
            self.log_activity(f"🔄 Triggering aggregation for {device_id or 'all devices'} ({hours}h)")
            
            # Calculate time period
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Get measurements for the period
            measurements_count = len([
                m for m in self.aggregator.measurements_buffer
                if datetime.fromisoformat(m.timestamp.replace('Z', '+00:00')) >= start_time.replace(tzinfo=end_time.tzinfo)
            ])
            
            if measurements_count < self.config.min_data_points:
                message = f"Insufficient data: {measurements_count} < {self.config.min_data_points} required"
                self.log_activity(f"⚠️ {message}")
                return {
                    "success": False,
                    "message": message,
                    "measurements_found": measurements_count,
                    "required": self.config.min_data_points
                }
            
            # Perform aggregation
            aggregated_report = self.aggregator.aggregate_measurements(start_time, end_time)
            
            if aggregated_report:
                # Update statistics
                self.stats["total_energy_mwh"] += aggregated_report.total_energy_mwh
                self.stats["total_emission_reductions"] += aggregated_report.emission_reductions_tco2
                self.total_carbon_credits += aggregated_report.emission_reductions_tco2
                self.last_aggregation = datetime.now()
                
                self.log_activity(f"✅ Aggregation successful: {aggregated_report.total_energy_mwh:.3f} MWh, {aggregated_report.emission_reductions_tco2:.3f} tCO2e")
                
                return {
                    "success": True,
                    "message": "Aggregation completed successfully",
                    "report": {
                        "project_id": aggregated_report.project_id,
                        "total_energy_mwh": aggregated_report.total_energy_mwh,
                        "emission_reductions_tco2": aggregated_report.emission_reductions_tco2,
                        "measurement_count": aggregated_report.measurement_count,
                        "capacity_factor": aggregated_report.capacity_factor,
                        "period_start": aggregated_report.reporting_period_start,
                        "period_end": aggregated_report.reporting_period_end
                    }
                }
            else:
                self.log_activity("❌ Aggregation failed")
                return {
                    "success": False,
                    "message": "Aggregation failed - no report generated"
                }
                
        except Exception as e:
            error_msg = f"Aggregation error: {e}"
            self.log_activity(f"❌ {error_msg}")
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
    
    async def run_complete_workflow(self, device_id: str = None) -> Dict[str, Any]:
        """Run complete AMS-I.D workflow: Aggregate → Submit to Guardian"""
        try:
            self.log_activity(f"🚀 Starting complete AMS-I.D workflow for {device_id or 'all devices'}")
            
            # Step 1: Trigger aggregation
            aggregation_result = await self.trigger_aggregation(device_id, hours=24)
            
            if not aggregation_result["success"]:
                return aggregation_result
            
            # Step 2: Submit to Guardian
            success = self.aggregator.process_aggregation_cycle()
            
            if success:
                # Update statistics
                self.stats["total_projects"] += 1
                self.stats["total_reports"] += 1
                self.stats["last_submission"] = datetime.now().isoformat()
                
                self.log_activity("✅ Complete workflow successful - submitted to Guardian!")
                
                return {
                    "success": True,
                    "message": "Complete AMS-I.D workflow executed successfully",
                    "steps_completed": [
                        "Data aggregation",
                        "Project submission to Guardian",
                        "Monitoring report submission to Guardian"
                    ],
                    "aggregation": aggregation_result["report"]
                }
            else:
                self.log_activity("❌ Guardian submission failed")
                return {
                    "success": False,
                    "message": "Aggregation successful but Guardian submission failed",
                    "aggregation": aggregation_result["report"]
                }
                
        except Exception as e:
            error_msg = f"Complete workflow error: {e}"
            self.log_activity(f"❌ {error_msg}")
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary for dashboard"""
        return {
            "ams_id": {
                "initialized": self.is_initialized,
                "running": self.is_running,
                "guardian_authenticated": self.stats["guardian_authenticated"],
                "last_aggregation": self.last_aggregation.isoformat() if self.last_aggregation else None,
                "total_carbon_credits": self.total_carbon_credits,
                "config": {
                    "policy_id": self.config.policy_id,
                    "aggregation_interval_hours": self.config.aggregation_interval_hours,
                    "min_data_points": self.config.min_data_points
                }
            },
            "statistics": {
                **self.stats,
                "devices_processed": list(self.stats["devices_processed"])
            },
            "activity_log": self.activity_log[-10:],  # Last 10 entries
            "measurements_buffer": {
                "count": len(self.aggregator.measurements_buffer),
                "oldest": (
                    self.aggregator.measurements_buffer[0].timestamp 
                    if self.aggregator.measurements_buffer 
                    else None
                ),
                "newest": (
                    self.aggregator.measurements_buffer[-1].timestamp 
                    if self.aggregator.measurements_buffer 
                    else None
                )
            }
        }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get metrics specifically formatted for dashboard display"""
        buffer_count = len(self.aggregator.measurements_buffer)
        
        return {
            "ams_id_status": "online" if self.is_initialized else "offline",
            "total_carbon_credits": round(self.total_carbon_credits, 6),
            "measurements_processed": self.stats["total_measurements"],
            "projects_submitted": self.stats["total_projects"],
            "reports_submitted": self.stats["total_reports"],
            "total_energy_mwh": round(self.stats["total_energy_mwh"], 3),
            "total_emission_reductions": round(self.stats["total_emission_reductions"], 6),
            "devices_count": len(self.stats["devices_processed"]),
            "buffer_count": buffer_count,
            "guardian_status": "authenticated" if self.stats["guardian_authenticated"] else "disconnected",
            "last_activity": self.activity_log[-1]["message"] if self.activity_log else "No activity",
            "last_submission": self.stats["last_submission"]
        }
    
    async def start_background_processing(self):
        """Start background processing (for future use)"""
        self.is_running = True
        self.log_activity("🔄 Background AMS-I.D processing started")
        
        # This could be expanded to run periodic aggregations
        # For now, we'll keep it simple and rely on manual triggers
    
    def stop_background_processing(self):
        """Stop background processing"""
        self.is_running = False
        self.log_activity("⏹️ Background AMS-I.D processing stopped")

# Global instance for the dashboard
ams_integration = AMSDashboardIntegration()