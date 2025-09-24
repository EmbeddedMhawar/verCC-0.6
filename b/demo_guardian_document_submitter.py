#!/usr/bin/env python3
"""
Demo script for Guardian Document Submitter
Shows how to use the GuardianDocumentSubmitter with real energy data
"""

import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our classes
from guardian_document_submitter import GuardianDocumentSubmitter, RetryConfig
from energy_data_aggregator import EnergyDataAggregator
from guardian_service import GuardianService, GuardianConfig

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_guardian_document_submission():
    """Demonstrate Guardian document submission workflow"""
    
    print("🚀 Guardian Document Submitter Demo")
    print("=" * 50)
    
    try:
        # 1. Initialize Guardian configuration
        guardian_config = GuardianConfig(
            base_url=os.getenv("GUARDIAN_URL", "http://localhost:3000"),
            username=os.getenv("GUARDIAN_USERNAME"),
            password=os.getenv("GUARDIAN_PASSWORD"),
            timeout=30
        )
        
        print(f"📡 Guardian URL: {guardian_config.base_url}")
        print(f"👤 Guardian User: {guardian_config.username}")
        
        # 2. Initialize services
        guardian_service = GuardianService(guardian_config)
        
        # Configure retry logic for demo (faster retries)
        retry_config = RetryConfig(
            max_retries=2,
            base_delay=1.0,
            max_delay=10.0,
            exponential_base=2.0,
            jitter=True
        )
        
        submitter = GuardianDocumentSubmitter(
            guardian_service=guardian_service,
            retry_config=retry_config
        )
        
        print("✅ Guardian Document Submitter initialized")
        
        # 3. Check Guardian health
        print("\n🔍 Checking Guardian health...")
        health = guardian_service.health_check()
        print(f"Guardian Status: {health.get('status', 'unknown')}")
        print(f"Connected: {health.get('connected', False)}")
        print(f"Authenticated: {health.get('authenticated', False)}")
        
        if not health.get('connected'):
            print("❌ Cannot connect to Guardian. Please ensure Guardian is running.")
            return
        
        # 4. Get available policies
        print("\n📋 Getting available Guardian policies...")
        policies = guardian_service.get_policies(status="PUBLISH")
        
        if not policies:
            print("⚠️ No published policies found. Please create a policy in Guardian first.")
            print("💡 You can use the Guardian web interface at http://localhost:3000")
            return
        
        print(f"Found {len(policies)} published policies:")
        for i, policy in enumerate(policies[:3]):  # Show first 3
            print(f"  {i+1}. {policy.get('name', 'Unnamed')} (ID: {policy.get('id', 'unknown')})")
        
        # Use the first policy for demo
        demo_policy_id = policies[0].get('id')
        demo_policy_name = policies[0].get('name', 'Unknown Policy')
        print(f"\n🎯 Using policy: {demo_policy_name} ({demo_policy_id})")
        
        # 5. Create sample energy data (simulating ESP32 aggregated data)
        print("\n📊 Creating sample energy report...")
        
        # Initialize energy data aggregator
        try:
            aggregator = EnergyDataAggregator()
            
            # Try to get real device data
            test_device_id = "ESP32_001"  # Replace with actual device ID
            
            print(f"🔍 Checking for real data from device: {test_device_id}")
            device_summary = aggregator.get_device_summary(test_device_id, days=1)
            
            if device_summary.get('total_readings', 0) > 0:
                print(f"✅ Found real data: {device_summary['total_readings']} readings")
                
                # Use real data
                yesterday = datetime.now() - timedelta(days=1)
                energy_report = aggregator.aggregate_daily_data(test_device_id, yesterday)
                
            else:
                print("⚠️ No real device data found, creating simulated report...")
                # Create simulated energy report for demo
                energy_report = create_simulated_energy_report()
                
        except Exception as e:
            print(f"⚠️ Could not access database: {e}")
            print("📝 Creating simulated energy report for demo...")
            energy_report = create_simulated_energy_report()
        
        print(f"📈 Energy Report Summary:")
        print(f"  Device: {energy_report.device_id}")
        print(f"  Period: {energy_report.period_start.date()} to {energy_report.period_end.date()}")
        print(f"  Total Energy: {energy_report.energy_metrics.total_energy_kwh:.2f} kWh")
        print(f"  Avg Power: {energy_report.energy_metrics.avg_power_w:.1f} W")
        print(f"  Data Quality: {energy_report.data_integrity_score:.1%}")
        print(f"  Verification Hash: {energy_report.verification_hash[:16]}...")
        
        # 6. Submit energy report to Guardian
        print(f"\n📤 Submitting energy report to Guardian policy {demo_policy_id}...")
        
        submission_result = submitter.submit_energy_report(
            report=energy_report,
            policy_id=demo_policy_id,
            tag_name="renewable_energy"
        )
        
        # 7. Display submission results
        print(f"\n📋 Submission Results:")
        print(f"  Success: {submission_result.success}")
        print(f"  Submission ID: {submission_result.submission_id}")
        
        if submission_result.success:
            print(f"  Guardian Document ID: {submission_result.guardian_document_id}")
            print(f"  Status: {submission_result.status.value}")
            print(f"  Message: {submission_result.message}")
            print(f"  Retry Count: {submission_result.retry_count}")
            print(f"  Submitted At: {submission_result.submitted_at}")
            
            # 8. Track submission progress
            print(f"\n🔄 Tracking submission progress...")
            
            import time
            time.sleep(2)  # Wait a moment for Guardian to process
            
            updated_result = submitter.track_submission_progress(submission_result.submission_id)
            if updated_result:
                print(f"  Updated Status: {updated_result.status.value}")
                
                # Get detailed document status
                if updated_result.guardian_document_id:
                    doc_status = submitter.get_document_status(
                        updated_result.guardian_document_id, 
                        demo_policy_id
                    )
                    if doc_status:
                        print(f"  Guardian Status: {doc_status.status}")
                        print(f"  Verification Status: {doc_status.verification_status}")
            
        else:
            print(f"  Error Code: {submission_result.error_code}")
            print(f"  Error Message: {submission_result.message}")
            print(f"  Retry Count: {submission_result.retry_count}")
            
            # Show error handling information
            if submission_result.response_data and 'error_info' in submission_result.response_data:
                error_info = submission_result.response_data['error_info']
                print(f"  Error Analysis:")
                print(f"    Type: {error_info.get('error_type')}")
                print(f"    Retry Recommended: {error_info.get('retry_recommended')}")
                print(f"    Action: {error_info.get('action')}")
        
        # 9. Show submission history
        print(f"\n📚 Submission History:")
        history = submitter.get_submission_history(limit=5)
        
        if history:
            for i, submission in enumerate(history, 1):
                print(f"  {i}. {submission.submission_id}")
                print(f"     Status: {submission.status.value}")
                print(f"     Policy: {submission.policy_id}")
                if submission.submitted_at:
                    print(f"     Time: {submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("  No submission history available")
        
        print(f"\n✅ Guardian Document Submitter demo completed!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure Guardian is running and environment variables are set")

def create_simulated_energy_report():
    """Create a simulated energy report for demo purposes"""
    from energy_data_aggregator import (
        AggregatedEnergyReport, EnergyMetrics, PerformanceMetrics, 
        EnvironmentalMetrics, DataQualityMetrics
    )
    
    # Simulate a day of solar energy production
    now = datetime.now()
    period_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    period_end = period_start + timedelta(days=1)
    
    return AggregatedEnergyReport(
        device_id="ESP32_DEMO_001",
        period_start=period_start,
        period_end=period_end,
        energy_metrics=EnergyMetrics(
            total_energy_kwh=28.5,  # 28.5 kWh for the day
            avg_power_w=1187.5,     # Average 1.2 kW
            max_power_w=3200.0,     # Peak 3.2 kW
            min_power_w=0.0,        # Night time
            peak_to_avg_ratio=2.69,
            capacity_factor=0.37    # 37% capacity factor
        ),
        performance_metrics=PerformanceMetrics(
            avg_efficiency=0.96,
            max_efficiency=0.98,
            min_efficiency=0.92,
            avg_power_factor=0.95,
            avg_grid_frequency=50.0
        ),
        environmental_metrics=EnvironmentalMetrics(
            avg_irradiance_w_m2=520.0,
            max_irradiance_w_m2=1150.0,
            avg_temperature_c=29.2,
            max_temperature_c=38.5,
            min_temperature_c=21.8
        ),
        data_quality=DataQualityMetrics(
            total_readings=1440,      # 1 reading per minute
            valid_readings=1432,      # 99.4% valid
            missing_readings=8,
            data_completeness_percent=99.4,
            outlier_count=8,
            measurement_period_hours=24.0
        ),
        verification_hash="demo_hash_" + str(int(now.timestamp())),
        data_integrity_score=0.97,
        grid_voltage_nominal=220.0,
        grid_frequency_nominal=50.0,
        regional_compliance={
            "country": "Morocco",
            "grid_standard": "220V_50Hz",
            "voltage_tolerance": "±10%",
            "frequency_tolerance": "±2%",
            "measurement_standard": "IEC_61724",
            "reporting_timezone": "Africa/Casablanca"
        }
    )

if __name__ == "__main__":
    # Check environment variables
    required_vars = ["GUARDIAN_USERNAME", "GUARDIAN_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please set these variables in your .env file:")
        print("   GUARDIAN_USERNAME=your_guardian_username")
        print("   GUARDIAN_PASSWORD=your_guardian_password")
        print("   GUARDIAN_URL=http://localhost:3000  # Optional, defaults to localhost")
    else:
        demo_guardian_document_submission()