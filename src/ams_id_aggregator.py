#!/usr/bin/env python3
"""
AMS-I.D Automatic Aggregation Tool
Follows the AMS-I.D policy workflow for automatic data aggregation and submission
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging
from guardian_client import GuardianClient, GuardianConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AMSIDConfig:
    """Configuration for AMS-I.D policy workflow"""
    # Guardian API Configuration
    guardian_base_url: str = "https://guardianservice.app/api/v1"
    username: str = "Mhawar"
    password: str = "Mhawar2001'"
    tenant_id: str = "68cc28cc348f53cc0b247ce4"
    
    # AMS-I.D Policy Configuration (from AMS-I.D.json)
    policy_id: str = "68d69341152381fe552b21ec"
    policy_tag: str = "Tag_1758892814008"
    
    # Block IDs for different workflow steps
    project_creation_block: str = "add_project_bnt"
    report_creation_block: str = "add_report_bnt"
    project_validation_block: str = "sr_validate_project_btn"
    report_verification_block: str = "approve_report_btn"
    
    # Schema IDs
    project_schema_id: str = "#161f2947-f16c-4601-9c4c-3545f286a55c"
    monitoring_report_schema_id: str = "#4259e321-7b95-4f10-9c10-29ac60bb6612"
    
    # Aggregation settings
    aggregation_interval_hours: int = 24
    min_data_points: int = 10
    
    @classmethod
    def from_file(cls, config_file: str = "ams_config.json") -> "AMSIDConfig":
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            return cls(
                guardian_base_url=config_data["guardian"]["base_url"],
                username=config_data["guardian"]["username"],
                password=config_data["guardian"]["password"],
                tenant_id=config_data["guardian"]["tenant_id"],
                policy_id=config_data["ams_id_policy"]["policy_id"],
                policy_tag=config_data["ams_id_policy"]["policy_tag"],
                project_creation_block=config_data["workflow_blocks"]["project_creation"],
                report_creation_block=config_data["workflow_blocks"]["report_creation"],
                project_validation_block=config_data["workflow_blocks"]["project_validation"],
                report_verification_block=config_data["workflow_blocks"]["report_verification"],
                project_schema_id=config_data["ams_id_policy"]["project_schema_id"],
                monitoring_report_schema_id=config_data["ams_id_policy"]["monitoring_report_schema_id"],
                aggregation_interval_hours=config_data["aggregation"]["interval_hours"],
                min_data_points=config_data["aggregation"]["min_data_points"]
            )
        except Exception as e:
            logger.warning(f"Failed to load config from {config_file}: {e}. Using defaults.")
            return cls()

@dataclass
class EnergyMeasurement:
    """Single energy measurement from ESP32"""
    timestamp: str
    device_id: str
    total_energy_kwh: float
    irradiance_w_m2: float
    ambient_temp_c: float
    efficiency: float
    power: float
    current: float
    voltage: float
    power_factor: float

@dataclass
class AggregatedReport:
    """Aggregated monitoring report for AMS-I.D submission"""
    reporting_period_start: str
    reporting_period_end: str
    project_id: str
    total_energy_mwh: float
    average_irradiance: float
    average_temperature: float
    average_efficiency: float
    capacity_factor: float
    baseline_emissions_tco2: float
    project_emissions_tco2: float
    emission_reductions_tco2: float
    measurement_count: int

class AMSIDAggregator:
    """Main aggregation tool for AMS-I.D policy workflow"""
    
    def __init__(self, config: AMSIDConfig):
        self.config = config
        self.guardian_client = GuardianClient(GuardianConfig(
            base_url=config.guardian_base_url,
            username=config.username,
            password=config.password,
            tenant_id=config.tenant_id,
            policy_id=config.policy_id
        ))
        self.session = requests.Session()
        self.measurements_buffer: List[EnergyMeasurement] = []
    
    def authenticate(self) -> bool:
        """Authenticate with Guardian"""
        return self.guardian_client.authenticate()
    
    def add_measurement(self, measurement: EnergyMeasurement) -> None:
        """Add a new measurement to the buffer"""
        self.measurements_buffer.append(measurement)
        logger.info(f"Added measurement from device {measurement.device_id} at {measurement.timestamp}")
    
    def aggregate_measurements(self, start_time: datetime, end_time: datetime) -> Optional[AggregatedReport]:
        """Aggregate measurements for the specified time period"""
        # Filter measurements within the time period
        period_measurements = []
        for measurement in self.measurements_buffer:
            measurement_time = datetime.fromisoformat(measurement.timestamp.replace('Z', '+00:00'))
            if start_time <= measurement_time <= end_time:
                period_measurements.append(measurement)
        
        if len(period_measurements) < self.config.min_data_points:
            logger.warning(f"Insufficient data points: {len(period_measurements)} < {self.config.min_data_points}")
            return None
        
        # Calculate aggregated values
        total_energy_kwh = sum(m.total_energy_kwh for m in period_measurements)
        avg_irradiance = sum(m.irradiance_w_m2 for m in period_measurements) / len(period_measurements)
        avg_temperature = sum(m.ambient_temp_c for m in period_measurements) / len(period_measurements)
        avg_efficiency = sum(m.efficiency for m in period_measurements) / len(period_measurements)
        
        # Convert to MWh
        total_energy_mwh = total_energy_kwh / 1000.0
        
        # Calculate capacity factor (assuming 1kW nominal capacity)
        nominal_capacity_kw = 1.0
        hours_in_period = (end_time - start_time).total_seconds() / 3600
        theoretical_max_kwh = nominal_capacity_kw * hours_in_period
        capacity_factor = (total_energy_kwh / theoretical_max_kwh) * 100 if theoretical_max_kwh > 0 else 0
        
        # Calculate emissions (Morocco grid emission factor: 0.81 tCO2/MWh)
        morocco_emission_factor = 0.81  # tCO2/MWh
        baseline_emissions = total_energy_mwh * morocco_emission_factor
        project_emissions = 0.0  # Renewable energy has zero direct emissions
        emission_reductions = baseline_emissions - project_emissions
        
        # Get project ID from first measurement
        project_id = f"ESP32-SOLAR-{period_measurements[0].device_id}"
        
        return AggregatedReport(
            reporting_period_start=start_time.isoformat() + "Z",
            reporting_period_end=end_time.isoformat() + "Z",
            project_id=project_id,
            total_energy_mwh=total_energy_mwh,
            average_irradiance=avg_irradiance,
            average_temperature=avg_temperature,
            average_efficiency=avg_efficiency,
            capacity_factor=capacity_factor,
            baseline_emissions_tco2=baseline_emissions,
            project_emissions_tco2=project_emissions,
            emission_reductions_tco2=emission_reductions,
            measurement_count=len(period_measurements)
        )
    
    def format_project_document(self, report: AggregatedReport) -> Dict[str, Any]:
        """Format project document for AMS-I.D policy"""
        return {
            "document": {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1"
                ],
                "id": f"project-{report.project_id}-{int(time.time())}",
                "type": ["VerifiableCredential"],
                "issuer": f"did:hedera:testnet:{report.project_id}",
                "issuanceDate": datetime.now().isoformat() + "Z",
                "credentialSubject": [{
                    "type": "project_schema",
                    "id": report.project_id,
                    "field0": {
                        "field0": f"Solar PV Project - {report.project_id}",
                        "field1": "Renewable energy project",
                        "field2": f"ESP32-based solar monitoring system for device {report.project_id.split('-')[-1]}"
                    },
                    "H33": {
                        "H35": "Greenfield power plants.",
                        "H40": report.baseline_emissions_tco2
                    },
                    "H81": {
                        "H82": "Renewable energy project activities.",
                        "H85": report.project_emissions_tco2
                    },
                    "H113": {
                        "H114": report.emission_reductions_tco2,
                        "H115": report.baseline_emissions_tco2,
                        "H116": report.project_emissions_tco2,
                        "H117": 0.0
                    }
                }]
            },
            "owner": f"did:hedera:testnet:{report.project_id}",
            "policyTag": self.config.policy_tag
        }
    
    def format_monitoring_report_document(self, report: AggregatedReport) -> Dict[str, Any]:
        """Format monitoring report document for AMS-I.D policy"""
        return {
            "document": {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1"
                ],
                "id": f"report-{report.project_id}-{int(time.time())}",
                "type": ["VerifiableCredential"],
                "issuer": f"did:hedera:testnet:{report.project_id}",
                "issuanceDate": datetime.now().isoformat() + "Z",
                "credentialSubject": [{
                    "type": "monitoring_report_schema",
                    "id": f"report-{report.project_id}-{int(time.time())}",
                    "ref": report.project_id,
                    "field0": {
                        "field0": f"Monitoring Report - {report.project_id}",
                        "field1": f"Period: {report.reporting_period_start} to {report.reporting_period_end}"
                    },
                    "field1": "Option A - Grid connected renewable electricity generation",
                    "field6": str(report.total_energy_mwh),
                    "field17": str(report.baseline_emissions_tco2),
                    "field21": str(report.project_emissions_tco2),
                    "field22": str(report.emission_reductions_tco2),
                    "field26": str(report.total_energy_mwh * 1000),  # Convert back to kWh for this field
                    "field27": "3.6",  # Conversion factor MJ/kWh
                    "field28": {
                        "field1": str(report.average_irradiance),
                        "field2": str(report.average_temperature),
                        "field3": str(report.average_efficiency)
                    }
                }]
            },
            "owner": f"did:hedera:testnet:{report.project_id}",
            "policyTag": self.config.policy_tag
        }
    
    def submit_project(self, report: AggregatedReport) -> bool:
        """Submit project to Guardian following AMS-I.D workflow"""
        try:
            project_doc = self.format_project_document(report)
            
            # Submit to external API with specific policy and block tag
            endpoint = f"{self.config.guardian_base_url}/external/{self.config.policy_id}/{self.config.project_creation_block}"
            
            headers = {
                "Authorization": f"Bearer {self.guardian_client.access_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(endpoint, headers=headers, json=project_doc)
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully submitted project for {report.project_id}")
                return True
            else:
                logger.error(f"Project submission failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Project submission error: {e}")
            return False
    
    def submit_monitoring_report(self, report: AggregatedReport) -> bool:
        """Submit monitoring report to Guardian following AMS-I.D workflow"""
        try:
            report_doc = self.format_monitoring_report_document(report)
            
            # Submit to external API with specific policy and block tag
            endpoint = f"{self.config.guardian_base_url}/external/{self.config.policy_id}/{self.config.report_creation_block}"
            
            headers = {
                "Authorization": f"Bearer {self.guardian_client.access_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(endpoint, headers=headers, json=report_doc)
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully submitted monitoring report for {report.project_id}")
                return True
            else:
                logger.error(f"Monitoring report submission failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Monitoring report submission error: {e}")
            return False
    
    def get_policy_blocks(self) -> Dict[str, Any]:
        """Get policy blocks information for debugging"""
        try:
            endpoint = f"{self.config.guardian_base_url}/policies/{self.config.policy_id}/blocks"
            
            headers = {
                "Authorization": f"Bearer {self.guardian_client.access_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get policy blocks: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting policy blocks: {e}")
            return {}
    
    def process_aggregation_cycle(self) -> bool:
        """Process one complete aggregation cycle"""
        try:
            # Calculate time period for aggregation (timezone-aware)
            from datetime import timezone
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=self.config.aggregation_interval_hours)
            
            logger.info(f"Processing aggregation cycle for period: {start_time} to {end_time}")
            
            # Aggregate measurements
            aggregated_report = self.aggregate_measurements(start_time, end_time)
            
            if not aggregated_report:
                logger.warning("No aggregated report generated - insufficient data")
                return False
            
            logger.info(f"Generated aggregated report: {aggregated_report.measurement_count} measurements, "
                       f"{aggregated_report.total_energy_mwh:.3f} MWh, "
                       f"{aggregated_report.emission_reductions_tco2:.3f} tCO2e")
            
            # Submit project (if not already exists)
            project_success = self.submit_project(aggregated_report)
            
            # Submit monitoring report
            report_success = self.submit_monitoring_report(aggregated_report)
            
            # Clear processed measurements from buffer
            cutoff_time = start_time
            self.measurements_buffer = [
                m for m in self.measurements_buffer 
                if datetime.fromisoformat(m.timestamp.replace('Z', '+00:00')) > cutoff_time
            ]
            
            return project_success and report_success
            
        except Exception as e:
            logger.error(f"Error in aggregation cycle: {e}")
            return False
    
    def run_continuous_aggregation(self, check_interval_minutes: int = 60) -> None:
        """Run continuous aggregation process"""
        logger.info(f"Starting continuous aggregation with {check_interval_minutes} minute intervals")
        
        last_aggregation = datetime.now() - timedelta(hours=self.config.aggregation_interval_hours)
        
        while True:
            try:
                current_time = datetime.now()
                
                # Check if it's time for next aggregation
                if (current_time - last_aggregation).total_seconds() >= (self.config.aggregation_interval_hours * 3600):
                    logger.info("Starting aggregation cycle...")
                    
                    if self.process_aggregation_cycle():
                        logger.info("✅ Aggregation cycle completed successfully")
                        last_aggregation = current_time
                    else:
                        logger.warning("❌ Aggregation cycle failed")
                
                # Wait before next check
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous aggregation...")
                break
            except Exception as e:
                logger.error(f"Error in continuous aggregation: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function for testing"""
    config = AMSIDConfig()
    aggregator = AMSIDAggregator(config)
    
    # Authenticate
    if not aggregator.authenticate():
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    
    # Test with sample measurements
    sample_measurements = [
        EnergyMeasurement(
            timestamp=(datetime.now() - timedelta(hours=i)).isoformat() + "Z",
            device_id="ESP32_001",
            total_energy_kwh=0.5 + (i * 0.1),
            irradiance_w_m2=800 + (i * 10),
            ambient_temp_c=25 + (i * 0.5),
            efficiency=0.85 + (i * 0.01),
            power=400 + (i * 5),
            current=2.0 + (i * 0.1),
            voltage=220,
            power_factor=0.95
        )
        for i in range(25)  # 25 hours of data
    ]
    
    # Add measurements to aggregator
    for measurement in sample_measurements:
        aggregator.add_measurement(measurement)
    
    print(f"✅ Added {len(sample_measurements)} sample measurements")
    
    # Test aggregation
    if aggregator.process_aggregation_cycle():
        print("✅ Test aggregation cycle completed successfully!")
    else:
        print("❌ Test aggregation cycle failed!")

if __name__ == "__main__":
    main()