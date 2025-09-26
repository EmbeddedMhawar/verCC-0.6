#!/usr/bin/env python3
"""
Test Dashboard Integration
Tests the AMS-I.D dashboard integration
"""

import asyncio
import json
from datetime import datetime
from ams_dashboard_integration import ams_integration

async def test_dashboard_integration():
    """Test the dashboard integration"""
    print("🧪 Testing AMS-I.D Dashboard Integration")
    print("=" * 50)
    
    # Test 1: Initialize
    print("\n1️⃣ Testing Initialization...")
    success = await ams_integration.initialize()
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 2: Process sample ESP32 data
    print("\n2️⃣ Testing ESP32 Data Processing...")
    sample_reading = {
        "device_id": "ESP32_001",
        "timestamp": datetime.now().isoformat() + "Z",
        "total_energy_kwh": 0.5,
        "irradiance_w_m2": 800,
        "ambient_temp_c": 25,
        "efficiency": 0.85,
        "power": 400,
        "current": 2.0,
        "voltage": 220,
        "power_factor": 0.95
    }
    
    success = await ams_integration.process_esp32_data(sample_reading)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: Get status summary
    print("\n3️⃣ Testing Status Summary...")
    status = ams_integration.get_status_summary()
    print(f"   Initialized: {status['ams_id']['initialized']}")
    print(f"   Guardian Auth: {status['ams_id']['guardian_authenticated']}")
    print(f"   Measurements: {status['statistics']['total_measurements']}")
    
    # Test 4: Get dashboard metrics
    print("\n4️⃣ Testing Dashboard Metrics...")
    metrics = ams_integration.get_dashboard_metrics()
    print(f"   Status: {metrics['ams_id_status']}")
    print(f"   Carbon Credits: {metrics['total_carbon_credits']}")
    print(f"   Buffer Count: {metrics['buffer_count']}")
    
    # Test 5: Trigger aggregation (if enough data)
    print("\n5️⃣ Testing Aggregation...")
    
    # Add more sample data
    for i in range(15):  # Add 15 more measurements
        sample_reading["timestamp"] = datetime.now().isoformat() + "Z"
        sample_reading["power"] = 400 + (i * 10)
        await ams_integration.process_esp32_data(sample_reading)
    
    result = await ams_integration.trigger_aggregation("ESP32_001", hours=1)
    print(f"   Result: {'✅ Success' if result['success'] else '❌ Failed'}")
    if result['success']:
        report = result['report']
        print(f"   Energy: {report['total_energy_mwh']:.3f} MWh")
        print(f"   Emissions: {report['emission_reductions_tco2']:.6f} tCO2e")
    else:
        print(f"   Message: {result['message']}")
    
    # Test 6: Activity log
    print("\n6️⃣ Testing Activity Log...")
    activity_log = ams_integration.activity_log[-5:]  # Last 5 entries
    for entry in activity_log:
        print(f"   [{entry['timestamp']}] {entry['message']}")
    
    print(f"\n✅ Dashboard Integration Test Complete!")
    print(f"📊 Final Stats:")
    final_metrics = ams_integration.get_dashboard_metrics()
    print(f"   - Measurements Processed: {final_metrics['measurements_processed']}")
    print(f"   - Buffer Count: {final_metrics['buffer_count']}")
    print(f"   - Carbon Credits: {final_metrics['total_carbon_credits']:.6f} tCO2e")

if __name__ == "__main__":
    asyncio.run(test_dashboard_integration())