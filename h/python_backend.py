#!/usr/bin/env python3
"""
Python Backend for MRV Data Processing
Main application that processes MRV data and sends it through the pipeline
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging
from dataclasses import dataclass, asdict

from guardian_client import GuardianClient, GuardianConfig
from mrv_sender_client import MRVSenderClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MRVReport:
    """Data structure for MRV monitoring reports"""
    project_id: str
    project_type: str
    baseline_emissions: float
    project_emissions: float
    emission_reductions: float
    monitoring_period_start: str
    monitoring_period_end: str
    renewable_energy_generated: float  # kWh
    grid_emission_factor: float  # tCO2/MWh
    
    def to_guardian_format(self) -> Dict[str, Any]:
        """Convert to Guardian API format"""
        return {
            "field0": self.project_id,
            "field1": self.project_type,
            "field6": str(self.emission_reductions),
            "monitoring_period": f"{self.monitoring_period_start} to {self.monitoring_period_end}",
            "renewable_energy_kwh": str(self.renewable_energy_generated),
            "grid_emission_factor": str(self.grid_emission_factor)
        }

class MRVProcessor:
    """Main processor for MRV data pipeline"""
    
    def __init__(self, use_mrv_sender: bool = True):
        self.guardian_config = GuardianConfig()
        self.guardian_client = GuardianClient(self.guardian_config)
        self.mrv_sender_client = MRVSenderClient() if use_mrv_sender else None
        self.use_mrv_sender = use_mrv_sender
    
    def authenticate_guardian(self) -> bool:
        """Authenticate with Guardian service"""
        logger.info("Authenticating with Guardian...")
        return self.guardian_client.authenticate()
    
    def check_mrv_sender(self) -> bool:
        """Check if MRV sender is available"""
        if not self.use_mrv_sender:
            return True
        
        logger.info("Checking MRV Sender service...")
        return self.mrv_sender_client.check_health()
    
    def process_report(self, report: MRVReport) -> bool:
        """Process a single MRV report through the pipeline"""
        logger.info(f"Processing MRV report for project: {report.project_id}")
        
        # Convert to Guardian format
        guardian_data = report.to_guardian_format()
        
        if self.use_mrv_sender and self.mrv_sender_client:
            # Send through mrv-sender
            logger.info("Sending data through mrv-sender...")
            return self.mrv_sender_client.send_mrv_data(guardian_data)
        else:
            # Send directly to Guardian
            logger.info("Sending data directly to Guardian...")
            return self.guardian_client.submit_monitoring_report(guardian_data)
    
    def process_batch(self, reports: List[MRVReport]) -> Dict[str, int]:
        """Process multiple MRV reports"""
        results = {"success": 0, "failed": 0}
        
        for i, report in enumerate(reports, 1):
            logger.info(f"Processing report {i}/{len(reports)}")
            
            if self.process_report(report):
                results["success"] += 1
                logger.info(f"✅ Report {i} processed successfully")
            else:
                results["failed"] += 1
                logger.error(f"❌ Report {i} failed to process")
            
            # Add delay between requests to avoid rate limiting
            if i < len(reports):
                time.sleep(2)
        
        return results

def create_sample_reports() -> List[MRVReport]:
    """Create sample MRV reports for testing"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    reports = [
        MRVReport(
            project_id="SOLAR_FARM_001",
            project_type="Grid connected renewable electricity generation",
            baseline_emissions=1500.0,
            project_emissions=50.0,
            emission_reductions=1450.0,
            monitoring_period_start="2024-01-01",
            monitoring_period_end="2024-12-31",
            renewable_energy_generated=2500000.0,  # 2.5 GWh
            grid_emission_factor=0.58  # tCO2/MWh
        ),
        MRVReport(
            project_id="WIND_FARM_002",
            project_type="Grid connected renewable electricity generation",
            baseline_emissions=2200.0,
            project_emissions=75.0,
            emission_reductions=2125.0,
            monitoring_period_start="2024-01-01",
            monitoring_period_end="2024-12-31",
            renewable_energy_generated=3800000.0,  # 3.8 GWh
            grid_emission_factor=0.58  # tCO2/MWh
        ),
        MRVReport(
            project_id="HYDRO_PLANT_003",
            project_type="Grid connected renewable electricity generation",
            baseline_emissions=1800.0,
            project_emissions=30.0,
            emission_reductions=1770.0,
            monitoring_period_start="2024-01-01",
            monitoring_period_end="2024-12-31",
            renewable_energy_generated=3200000.0,  # 3.2 GWh
            grid_emission_factor=0.58  # tCO2/MWh
        )
    ]
    
    return reports

def main():
    """Main application entry point"""
    print("🚀 Starting MRV Processing Pipeline")
    print("=" * 50)
    
    # Initialize processor
    processor = MRVProcessor(use_mrv_sender=True)
    
    # Check services
    print("🔍 Checking services...")
    
    if not processor.authenticate_guardian():
        print("❌ Guardian authentication failed!")
        return
    
    if not processor.check_mrv_sender():
        print("⚠️  MRV Sender not available, will send directly to Guardian")
        processor.use_mrv_sender = False
    
    print("✅ Services ready!")
    print()
    
    # Create and process sample reports
    print("📊 Creating sample MRV reports...")
    reports = create_sample_reports()
    print(f"Created {len(reports)} sample reports")
    print()
    
    # Process reports
    print("🔄 Processing reports...")
    results = processor.process_batch(reports)
    
    # Summary
    print()
    print("📈 Processing Summary:")
    print(f"✅ Successful: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📊 Total: {results['success'] + results['failed']}")
    
    if results['success'] > 0:
        print()
        print("🎉 MRV reports have been submitted to Guardian!")
        print("👀 Check the Guardian UI for approval and token minting.")

if __name__ == "__main__":
    main()