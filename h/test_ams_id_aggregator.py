#!/usr/bin/env python3
"""
Test script for AMS-I.D Aggregation Tool
Tests all components and workflow steps
"""

import json
import time
from datetime import datetime, timedelta
from ams_id_aggregator import AMSIDAggregator, AMSIDConfig, EnergyMeasurement
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_authentication():
    """Test Guardian authentication"""
    print("\n🔐 Testing Guardian Authentication...")
    
    config = AMSIDConfig()
    aggregator = AMSIDAggregator(config)
    
    if aggregator.authenticate():
        print("✅ Authentication successful!")
        return aggregator
    else:
        print("❌ Authentication failed!")
        return None

def test_policy_blocks(aggregator):
    """Test policy blocks retrieval"""
    print("\n📋 Testing Policy Blocks Retrieval...")
    
    blocks = aggregator.get_policy_blocks()
    
    if blocks:
        print(f"✅ Retrieved policy blocks: {len(blocks)} blocks found")
        
        # Look for our target blocks
        target_blocks = [
            aggregator.config.project_creation_block,
            aggregator.config.report_creation_block
        ]
        
        for block_tag in target_blocks:
            found = any(block.get('tag') == block_tag for block in blocks if isinstance(block, dict))
            status = "✅" if found else "❌"
            print(f"{status} Block '{block_tag}': {'Found' if found else 'Not found'}")
        
        return True
    else:
        print("❌ Failed to retrieve policy blocks")
        return False

def generate_test_measurements(device_id="ESP32_001", hours=25):
    """Generate test measurements for the specified number of hours"""
    measurements = []
    
    for i in range(hours):
        # Simulate realistic solar data with daily cycle
        hour_of_day = (datetime.now().hour - i) % 24
        
        # Solar irradiance follows a bell curve during day
        if 6 <= hour_of_day <= 18:
            base_irradiance = 800 * (1 - abs(hour_of_day - 12) / 6)
        else:
            base_irradiance = 0
        
        # Add some randomness
        import random
        irradiance = max(0, base_irradiance + random.uniform(-50, 50))
        
        # Power is proportional to irradiance
        power = irradiance * 0.5  # Assuming 0.5W per W/m²
        
        # Energy accumulates over time
        energy = power * 1 / 1000  # Convert to kWh (1 hour intervals)
        
        measurement = EnergyMeasurement(
            timestamp=(datetime.now() - timedelta(hours=i)).isoformat() + "Z",
            device_id=device_id,
            total_energy_kwh=energy,
            irradiance_w_m2=irradiance,
            ambient_temp_c=25 + random.uniform(-5, 10),
            efficiency=0.85 + random.uniform(-0.05, 0.05),
            power=power,
            current=power / 220 if power > 0 else 0,
            voltage=220,
            power_factor=0.95
        )
        
        measurements.append(measurement)
    
    return measurements

def test_measurement_aggregation(aggregator):
    """Test measurement aggregation"""
    print("\n📊 Testing Measurement Aggregation...")
    
    # Generate test measurements
    measurements = generate_test_measurements(hours=25)
    
    # Add measurements to aggregator
    for measurement in measurements:
        aggregator.add_measurement(measurement)
    
    print(f"✅ Added {len(measurements)} test measurements")
    
    # Test aggregation
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    aggregated_report = aggregator.aggregate_measurements(start_time, end_time)
    
    if aggregated_report:
        print("✅ Aggregation successful!")
        print(f"   📈 Total Energy: {aggregated_report.total_energy_mwh:.3f} MWh")
        print(f"   🌞 Average Irradiance: {aggregated_report.average_irradiance:.1f} W/m²")
        print(f"   🌡️  Average Temperature: {aggregated_report.average_temperature:.1f}°C")
        print(f"   ⚡ Capacity Factor: {aggregated_report.capacity_factor:.1f}%")
        print(f"   🌱 Emission Reductions: {aggregated_report.emission_reductions_tco2:.3f} tCO2e")
        print(f"   📊 Measurement Count: {aggregated_report.measurement_count}")
        return aggregated_report
    else:
        print("❌ Aggregation failed!")
        return None

def test_document_formatting(aggregator, report):
    """Test document formatting for Guardian"""
    print("\n📄 Testing Document Formatting...")
    
    # Test project document formatting
    project_doc = aggregator.format_project_document(report)
    
    if project_doc and 'document' in project_doc:
        print("✅ Project document formatted successfully!")
        print(f"   📋 Project ID: {project_doc['document']['credentialSubject'][0]['id']}")
        print(f"   🏷️  Policy Tag: {project_doc['policyTag']}")
    else:
        print("❌ Project document formatting failed!")
        return False
    
    # Test monitoring report document formatting
    report_doc = aggregator.format_monitoring_report_document(report)
    
    if report_doc and 'document' in report_doc:
        print("✅ Monitoring report document formatted successfully!")
        print(f"   📋 Report ID: {report_doc['document']['credentialSubject'][0]['id']}")
        print(f"   🔗 Project Reference: {report_doc['document']['credentialSubject'][0]['ref']}")
    else:
        print("❌ Monitoring report document formatting failed!")
        return False
    
    return True

def test_guardian_submission(aggregator, report):
    """Test submission to Guardian (with user confirmation)"""
    print("\n🚀 Testing Guardian Submission...")
    
    # Ask user for confirmation before submitting
    response = input("Do you want to test actual submission to Guardian? (y/N): ")
    
    if response.lower() != 'y':
        print("⏭️  Skipping actual Guardian submission")
        return True
    
    print("📤 Submitting project to Guardian...")
    project_success = aggregator.submit_project(report)
    
    if project_success:
        print("✅ Project submission successful!")
    else:
        print("❌ Project submission failed!")
    
    # Wait a bit before submitting report
    time.sleep(2)
    
    print("📤 Submitting monitoring report to Guardian...")
    report_success = aggregator.submit_monitoring_report(report)
    
    if report_success:
        print("✅ Monitoring report submission successful!")
    else:
        print("❌ Monitoring report submission failed!")
    
    return project_success and report_success

def test_full_aggregation_cycle(aggregator):
    """Test complete aggregation cycle"""
    print("\n🔄 Testing Full Aggregation Cycle...")
    
    # Generate fresh test data
    measurements = generate_test_measurements(hours=25)
    
    # Clear existing buffer and add new measurements
    aggregator.measurements_buffer = []
    for measurement in measurements:
        aggregator.add_measurement(measurement)
    
    # Run aggregation cycle
    success = aggregator.process_aggregation_cycle()
    
    if success:
        print("✅ Full aggregation cycle completed successfully!")
    else:
        print("❌ Full aggregation cycle failed!")
    
    return success

def main():
    """Main test function"""
    print("🧪 AMS-I.D Aggregation Tool Test Suite")
    print("=" * 50)
    
    # Test 1: Authentication
    aggregator = test_authentication()
    if not aggregator:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Test 2: Policy blocks
    if not test_policy_blocks(aggregator):
        print("\n⚠️  Policy blocks test failed, but continuing...")
    
    # Test 3: Measurement aggregation
    report = test_measurement_aggregation(aggregator)
    if not report:
        print("\n❌ Cannot proceed without successful aggregation")
        return
    
    # Test 4: Document formatting
    if not test_document_formatting(aggregator, report):
        print("\n❌ Document formatting failed")
        return
    
    # Test 5: Guardian submission (optional)
    test_guardian_submission(aggregator, report)
    
    # Test 6: Full aggregation cycle
    test_full_aggregation_cycle(aggregator)
    
    print("\n🎉 Test Suite Completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()