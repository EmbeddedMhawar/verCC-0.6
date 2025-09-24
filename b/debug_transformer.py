#!/usr/bin/env python3
"""
Debug script for Guardian Data Transformer
"""

from datetime import datetime, timedelta
from guardian_data_transformer import GuardianDataTransformer, GuardianPolicyType
from energy_data_aggregator import (
    AggregatedEnergyReport,
    EnergyMetrics,
    PerformanceMetrics,
    EnvironmentalMetrics,
    DataQualityMetrics
)

def create_test_report():
    """Create a test energy report"""
    period_start = datetime(2024, 1, 15, 0, 0, 0)
    period_end = period_start + timedelta(days=1)
    
    energy_metrics = EnergyMetrics(
        total_energy_kwh=125.75,
        avg_power_w=5239.58,
        max_power_w=8500.0,
        min_power_w=0.0,
        peak_to_avg_ratio=1.62,
        capacity_factor=0.85
    )
    
    performance_metrics = PerformanceMetrics(
        avg_efficiency=0.96,
        max_efficiency=0.98,
        min_efficiency=0.92,
        avg_power_factor=0.95,
        avg_grid_frequency=50.1
    )
    
    environmental_metrics = EnvironmentalMetrics(
        avg_irradiance_w_m2=850.5,
        max_irradiance_w_m2=1200.0,
        avg_temperature_c=28.5,
        max_temperature_c=35.2,
        min_temperature_c=22.1
    )
    
    data_quality = DataQualityMetrics(
        total_readings=1440,
        valid_readings=1380,
        missing_readings=60,
        data_completeness_percent=95.8,
        outlier_count=60,
        measurement_period_hours=24.0
    )
    
    return AggregatedEnergyReport(
        device_id="ESP32_DEBUG_001",
        period_start=period_start,
        period_end=period_end,
        energy_metrics=energy_metrics,
        performance_metrics=performance_metrics,
        environmental_metrics=environmental_metrics,
        data_quality=data_quality,
        verification_hash="debug_hash_123456",
        data_integrity_score=0.92,
        grid_voltage_nominal=220.0,
        grid_frequency_nominal=50.0,
        regional_compliance={"country": "Morocco"}
    )

def main():
    print("🔧 Debugging Guardian Data Transformer...")
    
    transformer = GuardianDataTransformer()
    report = create_test_report()
    
    print(f"📊 Test report created for device: {report.device_id}")
    print(f"   Energy: {report.energy_metrics.total_energy_kwh} kWh")
    print(f"   Power: {report.energy_metrics.avg_power_w} W")
    
    # Test field extraction
    print("\n🔍 Testing field extraction:")
    test_fields = [
        "total_energy_kwh",
        "avg_power_w", 
        "avg_efficiency",
        "avg_irradiance_w_m2",
        "verification_hash"
    ]
    
    for field in test_fields:
        value = transformer._extract_esp32_field_value(report, field)
        print(f"   {field}: {value}")
    
    # Test transformation
    print("\n🔄 Testing transformation:")
    try:
        guardian_doc = transformer.transform_energy_report_to_guardian(
            report, 
            GuardianPolicyType.VM0042
        )
        
        print(f"✅ Document created: {guardian_doc.document_id}")
        print(f"   Types: {guardian_doc.type}")
        
        # Check credential subject
        cs = guardian_doc.credential_subject
        print(f"   Energy Production: {cs.get('energyProduction', {})}")
        
        # Test validation
        print("\n🔍 Testing validation:")
        validation_result = transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        print(f"   Valid: {validation_result['is_valid']}")
        if validation_result['errors']:
            print(f"   Errors: {validation_result['errors']}")
        if validation_result['warnings']:
            print(f"   Warnings: {validation_result['warnings']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()