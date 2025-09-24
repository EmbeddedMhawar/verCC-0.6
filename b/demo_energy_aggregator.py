#!/usr/bin/env python3
"""
Demo script for EnergyDataAggregator
Shows how to use the aggregator for Guardian submission preparation
"""

import os
from datetime import datetime, timedelta
from unittest.mock import Mock
from energy_data_aggregator import EnergyDataAggregator, AggregatedEnergyReport

def create_sample_data():
    """Create sample ESP32 sensor data for demonstration"""
    base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    
    sample_data = []
    for i in range(144):  # 144 readings = 2.4 hours of 1-minute intervals
        timestamp = base_time + timedelta(minutes=i)
        
        # Simulate solar power curve (low in morning/evening, peak at midday)
        hour_of_day = timestamp.hour + timestamp.minute / 60.0
        solar_factor = max(0, 0.8 * (1 - abs(hour_of_day - 12) / 6))  # Peak at noon
        
        reading = {
            "id": i + 1,
            "device_id": "ESP32_DEMO",
            "timestamp": timestamp.isoformat() + "Z",
            "power": 1000 + (500 * solar_factor) + (i % 100),  # Variable power
            "voltage": 220.0,
            "current": 4.5 + (2 * solar_factor),
            "ac_power_kw": (1000 + (500 * solar_factor)) / 1000,
            "total_energy_kwh": 10.0 + (i * 0.02),  # Cumulative energy
            "grid_frequency_hz": 50.0,
            "power_factor": 0.95,
            "efficiency": 0.96 - (0.1 * (1 - solar_factor)),  # Lower efficiency at low power
            "ambient_temp_c": 25.0 + (10 * solar_factor),  # Higher temp at peak
            "irradiance_w_m2": 800 * solar_factor,  # Solar irradiance
            "system_status": 1
        }
        sample_data.append(reading)
    
    return sample_data

def demo_energy_aggregator():
    """Demonstrate EnergyDataAggregator functionality"""
    print("🔍 EnergyDataAggregator Demo")
    print("=" * 50)
    
    # Create mock Supabase client
    mock_supabase = Mock()
    
    # Create sample data
    sample_data = create_sample_data()
    print(f"📊 Created {len(sample_data)} sample sensor readings")
    
    # Mock Supabase response
    mock_result = Mock()
    mock_result.data = sample_data
    mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
    
    # Initialize aggregator with mock client
    aggregator = EnergyDataAggregator(supabase_client=mock_supabase)
    
    # Test daily aggregation
    print("\n📈 Testing Daily Data Aggregation")
    print("-" * 30)
    
    try:
        target_date = datetime.now()
        report = aggregator.aggregate_daily_data("ESP32_DEMO", target_date)
        
        print(f"✅ Aggregation successful for device: {report.device_id}")
        print(f"📅 Period: {report.period_start.date()} to {report.period_end.date()}")
        print(f"⚡ Total Energy: {report.energy_metrics.total_energy_kwh:.2f} kWh")
        print(f"🔋 Average Power: {report.energy_metrics.avg_power_w:.1f} W")
        print(f"📊 Peak Power: {report.energy_metrics.max_power_w:.1f} W")
        print(f"🎯 Capacity Factor: {report.energy_metrics.capacity_factor:.2%}")
        print(f"🌡️ Avg Temperature: {report.environmental_metrics.avg_temperature_c:.1f}°C")
        print(f"☀️ Avg Irradiance: {report.environmental_metrics.avg_irradiance_w_m2:.1f} W/m²")
        print(f"📋 Data Quality: {report.data_quality.valid_readings}/{report.data_quality.total_readings} readings")
        print(f"🔐 Verification Hash: {report.verification_hash[:16]}...")
        print(f"✅ Data Integrity Score: {report.data_integrity_score:.2%}")
        
    except Exception as e:
        print(f"❌ Aggregation failed: {e}")
        return
    
    # Test Guardian readiness validation
    print("\n🔍 Testing Guardian Readiness Validation")
    print("-" * 40)
    
    try:
        readiness = aggregator.validate_guardian_readiness("ESP32_DEMO", target_date)
        
        print(f"🎯 Guardian Ready: {'✅ YES' if readiness['guardian_ready'] else '❌ NO'}")
        print("\n📋 Readiness Checks:")
        
        for check_name, check_data in readiness['checks'].items():
            status = "✅ PASS" if check_data['passed'] else "❌ FAIL"
            print(f"   {check_name}: {status} ({check_data['value']:.2f} >= {check_data['threshold']:.2f})")
        
        print(f"\n📊 Summary:")
        print(f"   Total Energy: {readiness['summary']['total_energy_kwh']:.2f} kWh")
        print(f"   Data Integrity: {readiness['summary']['data_integrity_score']:.2%}")
        print(f"   Verification Hash: {readiness['summary']['verification_hash'][:16]}...")
        
    except Exception as e:
        print(f"❌ Guardian readiness check failed: {e}")
    
    # Test data validation
    print("\n🔍 Testing Data Validation")
    print("-" * 25)
    
    # Add some invalid data to test validation
    invalid_data = sample_data + [
        {
            "device_id": "ESP32_DEMO",
            "timestamp": "2025-01-20T15:00:00Z",
            "power": -100.0,  # Invalid negative power
            "voltage": 300.0,  # Invalid voltage
            "grid_frequency_hz": 60.0,  # Invalid frequency for Morocco
            "efficiency": 1.5,  # Invalid efficiency
            "ambient_temp_c": 70.0,  # Invalid temperature
            "irradiance_w_m2": 2000.0  # Invalid irradiance
        }
    ]
    
    validated_data = aggregator._validate_and_clean_data(invalid_data)
    
    print(f"📊 Original readings: {len(invalid_data)}")
    print(f"✅ Valid readings: {len(validated_data)}")
    print(f"❌ Filtered out: {len(invalid_data) - len(validated_data)} invalid readings")
    
    # Test verification hash consistency
    print("\n🔐 Testing Verification Hash Consistency")
    print("-" * 35)
    
    energy_metrics = report.energy_metrics
    hash1 = aggregator._generate_verification_hash("ESP32_DEMO", validated_data, energy_metrics)
    hash2 = aggregator._generate_verification_hash("ESP32_DEMO", validated_data, energy_metrics)
    hash3 = aggregator._generate_verification_hash("ESP32_OTHER", validated_data, energy_metrics)
    
    print(f"✅ Same input produces same hash: {hash1 == hash2}")
    print(f"✅ Different device produces different hash: {hash1 != hash3}")
    print(f"🔐 Hash length: {len(hash1)} characters (SHA-256)")
    
    print("\n🎉 Demo completed successfully!")
    print("💡 The EnergyDataAggregator is ready for Guardian integration")

if __name__ == "__main__":
    demo_energy_aggregator()