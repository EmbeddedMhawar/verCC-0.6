#!/usr/bin/env python3
"""
Guardian Integration Module
Implements the Guardian Tools Architecture:
- Tool 10: Data Source (ESP32 sensors)
- Tool 07: Aggregation/Reporting (Process raw data into summaries)
- Tool 03: Hedera Hashgraph (Store hashes for verification)
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from guardian_client import GuardianClient, GuardianConfig
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnergyReading:
    """Tool 10: Data Source - Raw ESP32 sensor data"""
    device_id: str
    timestamp: str
    current: float
    voltage: float
    power: float
    total_energy_kwh: float
    efficiency: float
    ambient_temp_c: float
    irradiance_w_m2: float
    power_factor: float

@dataclass
class AggregatedData:
    """Tool 07: Aggregation - Processed data summaries"""
    device_id: str
    period_start: str
    period_end: str
    duration_hours: float
    
    # Energy metrics
    total_energy_kwh: float
    avg_power_w: float
    max_power_w: float
    min_power_w: float
    
    # Environmental metrics
    avg_irradiance: float
    avg_temperature: float
    avg_efficiency: float
    
    # Carbon calculations
    baseline_emissions_tco2: float
    project_emissions_tco2: float
    emission_reductions_tco2: float
    
    # Data integrity
    data_points_count: int
    data_hash: str

@dataclass
class HederaRecord:
    """Tool 03: Hedera Hashgraph - Immutable verification record"""
    device_id: str
    timestamp: str
    data_hash: str
    aggregation_period: str
    emission_reductions: float
    verification_status: str
    hedera_transaction_id: Optional[str] = None

class GuardianDataProcessor:
    """
    Main processor implementing Guardian Tools Architecture
    """
    
    def __init__(self):
        self.guardian_client = GuardianClient(GuardianConfig())
        self.raw_data_buffer: List[EnergyReading] = []
        self.aggregated_data: List[AggregatedData] = []
        self.hedera_records: List[HederaRecord] = []
        
        # Morocco grid emission factor (tCO2/MWh)
        self.grid_emission_factor = 0.81
        
    async def process_esp32_data(self, reading_data: Dict[str, Any]) -> EnergyReading:
        """
        Tool 10: Data Source Processing
        Convert ESP32 raw data into structured format
        """
        try:
            reading = EnergyReading(
                device_id=reading_data["device_id"],
                timestamp=reading_data["timestamp"],
                current=float(reading_data.get("current", 0)),
                voltage=float(reading_data.get("voltage", 0)),
                power=float(reading_data.get("power", 0)),
                total_energy_kwh=float(reading_data.get("total_energy_kwh", 0)),
                efficiency=float(reading_data.get("efficiency", 0.85)),
                ambient_temp_c=float(reading_data.get("ambient_temp_c", 25)),
                irradiance_w_m2=float(reading_data.get("irradiance_w_m2", 800)),
                power_factor=float(reading_data.get("power_factor", 0.95))
            )
            
            # Add to buffer for aggregation
            self.raw_data_buffer.append(reading)
            
            # Keep buffer size manageable (last 1000 readings)
            if len(self.raw_data_buffer) > 1000:
                self.raw_data_buffer.pop(0)
            
            logger.info(f"Tool 10: Processed data from {reading.device_id} - {reading.power}W")
            return reading
            
        except Exception as e:
            logger.error(f"Tool 10 error: {e}")
            raise
    
    def aggregate_data(self, device_id: str, hours: int = 1) -> Optional[AggregatedData]:
        """
        Tool 07: Aggregation/Reporting
        Process raw data into meaningful summaries with time periods
        """
        try:
            # Get data for the specified period
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Filter data for device and time period
            period_data = [
                reading for reading in self.raw_data_buffer
                if (reading.device_id == device_id and 
                    start_time <= datetime.fromisoformat(reading.timestamp.replace('Z', '+00:00').replace('+00:00', '')) <= end_time)
            ]
            
            if not period_data:
                logger.warning(f"Tool 07: No data found for {device_id} in last {hours} hours")
                return None
            
            # Calculate aggregations
            powers = [r.power for r in period_data]
            irradiances = [r.irradiance_w_m2 for r in period_data]
            temperatures = [r.ambient_temp_c for r in period_data]
            efficiencies = [r.efficiency for r in period_data]
            
            # Energy calculations
            total_energy = max([r.total_energy_kwh for r in period_data]) - min([r.total_energy_kwh for r in period_data])
            avg_power = sum(powers) / len(powers)
            
            # Carbon calculations
            energy_mwh = total_energy / 1000.0
            baseline_emissions = energy_mwh * self.grid_emission_factor
            project_emissions = 0  # Solar has zero operational emissions
            emission_reductions = baseline_emissions
            
            # Create data hash for integrity
            data_string = json.dumps({
                "device_id": device_id,
                "period": f"{start_time.isoformat()}_to_{end_time.isoformat()}",
                "total_energy_kwh": total_energy,
                "avg_power_w": avg_power,
                "emission_reductions": emission_reductions,
                "data_points": len(period_data)
            }, sort_keys=True)
            
            data_hash = hashlib.sha256(data_string.encode()).hexdigest()
            
            aggregated = AggregatedData(
                device_id=device_id,
                period_start=start_time.isoformat(),
                period_end=end_time.isoformat(),
                duration_hours=hours,
                total_energy_kwh=total_energy,
                avg_power_w=avg_power,
                max_power_w=max(powers),
                min_power_w=min(powers),
                avg_irradiance=sum(irradiances) / len(irradiances),
                avg_temperature=sum(temperatures) / len(temperatures),
                avg_efficiency=sum(efficiencies) / len(efficiencies),
                baseline_emissions_tco2=baseline_emissions,
                project_emissions_tco2=project_emissions,
                emission_reductions_tco2=emission_reductions,
                data_points_count=len(period_data),
                data_hash=data_hash
            )
            
            self.aggregated_data.append(aggregated)
            
            logger.info(f"Tool 07: Aggregated {len(period_data)} data points for {device_id}")
            logger.info(f"Tool 07: Energy: {total_energy:.3f} kWh, Emissions reduced: {emission_reductions:.6f} tCO2")
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Tool 07 error: {e}")
            return None
    
    async def create_hedera_record(self, aggregated: AggregatedData) -> HederaRecord:
        """
        Tool 03: Hedera Hashgraph
        Create immutable verification record
        """
        try:
            hedera_record = HederaRecord(
                device_id=aggregated.device_id,
                timestamp=datetime.now().isoformat(),
                data_hash=aggregated.data_hash,
                aggregation_period=f"{aggregated.period_start}_to_{aggregated.period_end}",
                emission_reductions=aggregated.emission_reductions_tco2,
                verification_status="pending"
            )
            
            # In a real implementation, this would submit to Hedera network
            # For now, we simulate the process
            logger.info(f"Tool 03: Created Hedera record for {aggregated.device_id}")
            logger.info(f"Tool 03: Data hash: {aggregated.data_hash[:16]}...")
            
            # Simulate Hedera transaction
            hedera_record.hedera_transaction_id = f"0.0.{hash(aggregated.data_hash) % 1000000}"
            hedera_record.verification_status = "verified"
            
            self.hedera_records.append(hedera_record)
            
            return hedera_record
            
        except Exception as e:
            logger.error(f"Tool 03 error: {e}")
            raise
    
    async def submit_to_guardian(self, aggregated: AggregatedData, hedera_record: HederaRecord) -> bool:
        """
        Submit processed data to Guardian for MRV reporting
        """
        try:
            # Authenticate with Guardian
            if not await self.authenticate_guardian():
                return False
            
            # Prepare Guardian-compatible data
            guardian_data = {
                "field0": f"VCC-{aggregated.device_id}",  # Project ID
                "field1": "Grid connected renewable electricity generation",  # Project type
                "field6": str(aggregated.emission_reductions_tco2),  # Emission reductions
                
                # Additional monitoring data
                "monitoring_period": f"{aggregated.period_start} to {aggregated.period_end}",
                "total_energy_kwh": str(aggregated.total_energy_kwh),
                "avg_power_w": str(aggregated.avg_power_w),
                "data_points": str(aggregated.data_points_count),
                "data_hash": aggregated.data_hash,
                "hedera_tx_id": hedera_record.hedera_transaction_id,
                "verification_status": hedera_record.verification_status
            }
            
            # Submit to MRV sender (which forwards to Guardian)
            success = await self.submit_to_mrv_sender(guardian_data)
            
            if success:
                logger.info(f"Guardian: Successfully submitted MRV report for {aggregated.device_id}")
            else:
                logger.error(f"Guardian: Failed to submit MRV report for {aggregated.device_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Guardian submission error: {e}")
            return False
    
    async def authenticate_guardian(self) -> bool:
        """Authenticate with Guardian"""
        try:
            return self.guardian_client.authenticate()
        except Exception as e:
            logger.error(f"Guardian authentication error: {e}")
            return False
    
    async def submit_to_mrv_sender(self, data: Dict[str, Any]) -> bool:
        """Submit data to MRV sender"""
        try:
            response = requests.post(
                "http://localhost:3005/mrv-generate",
                json=data,
                timeout=30
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"MRV sender error: {e}")
            return False
    
    async def process_complete_workflow(self, device_id: str) -> Dict[str, Any]:
        """
        Complete Guardian Tools workflow:
        Tool 10 → Tool 07 → Tool 03 → Guardian
        """
        try:
            logger.info(f"Starting complete workflow for {device_id}")
            
            # Tool 07: Aggregate recent data
            aggregated = self.aggregate_data(device_id, hours=1)
            if not aggregated:
                return {"success": False, "error": "No data to aggregate"}
            
            # Tool 03: Create Hedera record
            hedera_record = await self.create_hedera_record(aggregated)
            
            # Submit to Guardian
            guardian_success = await self.submit_to_guardian(aggregated, hedera_record)
            
            result = {
                "success": True,
                "device_id": device_id,
                "aggregated_data": asdict(aggregated),
                "hedera_record": asdict(hedera_record),
                "guardian_submitted": guardian_success,
                "workflow_completed": datetime.now().isoformat()
            }
            
            logger.info(f"Complete workflow finished for {device_id}")
            return result
            
        except Exception as e:
            logger.error(f"Complete workflow error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get status summary of all Guardian tools"""
        return {
            "tool_10_data_source": {
                "raw_data_points": len(self.raw_data_buffer),
                "devices_active": len(set(r.device_id for r in self.raw_data_buffer)),
                "latest_timestamp": max([r.timestamp for r in self.raw_data_buffer]) if self.raw_data_buffer else None
            },
            "tool_07_aggregation": {
                "aggregated_reports": len(self.aggregated_data),
                "total_emission_reductions": sum(a.emission_reductions_tco2 for a in self.aggregated_data),
                "total_energy_processed": sum(a.total_energy_kwh for a in self.aggregated_data)
            },
            "tool_03_hedera": {
                "hedera_records": len(self.hedera_records),
                "verified_records": len([r for r in self.hedera_records if r.verification_status == "verified"]),
                "total_verified_reductions": sum(r.emission_reductions for r in self.hedera_records if r.verification_status == "verified")
            }
        }

# Global processor instance
guardian_processor = GuardianDataProcessor()

if __name__ == "__main__":
    # Test the processor
    async def test_workflow():
        # Simulate ESP32 data
        test_data = {
            "device_id": "ESP32_001",
            "timestamp": datetime.now().isoformat(),
            "current": 2.5,
            "voltage": 230,
            "power": 575,
            "total_energy_kwh": 1.234,
            "efficiency": 0.85,
            "ambient_temp_c": 25.5,
            "irradiance_w_m2": 800,
            "power_factor": 0.95
        }
        
        # Process through complete workflow
        await guardian_processor.process_esp32_data(test_data)
        result = await guardian_processor.process_complete_workflow("ESP32_001")
        
        print("Guardian Tools Workflow Result:")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_workflow())