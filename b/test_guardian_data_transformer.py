#!/usr/bin/env python3
"""
Test suite for Guardian Data Format Validation and Transformation
Tests requirements 8.1, 8.2, 8.3, 8.5
"""

import unittest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from guardian_data_transformer import (
    GuardianDataTransformer, 
    GuardianPolicyType, 
    VerraSchemaVersion,
    GuardianDocument,
    VerraComplianceMetadata
)
from energy_data_aggregator import (
    AggregatedEnergyReport,
    EnergyMetrics,
    PerformanceMetrics,
    EnvironmentalMetrics,
    DataQualityMetrics
)

class TestGuardianDataTransformer(unittest.TestCase):
    """Test Guardian data transformation and validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.transformer = GuardianDataTransformer()
        
        # Create sample energy report
        self.sample_report = self._create_sample_energy_report()
    
    def _create_sample_energy_report(self) -> AggregatedEnergyReport:
        """Create sample aggregated energy report for testing"""
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
        
        regional_compliance = {
            "country": "Morocco",
            "grid_standard": "220V_50Hz",
            "voltage_tolerance": "±10%",
            "frequency_tolerance": "±2%",
            "measurement_standard": "IEC_61724",
            "reporting_timezone": "Africa/Casablanca"
        }
        
        return AggregatedEnergyReport(
            device_id="ESP32_TEST_001",
            period_start=period_start,
            period_end=period_end,
            energy_metrics=energy_metrics,
            performance_metrics=performance_metrics,
            environmental_metrics=environmental_metrics,
            data_quality=data_quality,
            verification_hash="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            data_integrity_score=0.92,
            grid_voltage_nominal=220.0,
            grid_frequency_nominal=50.0,
            regional_compliance=regional_compliance
        )
    
    def test_transform_energy_report_to_guardian_vm0042(self):
        """Test transformation to Guardian VM0042 format"""
        # Test requirement 8.1: Create data transformation functions for Guardian renewable energy schema
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042,
            VerraSchemaVersion.LATEST
        )
        
        # Verify document structure
        self.assertIsInstance(guardian_doc, GuardianDocument)
        self.assertEqual(guardian_doc.document_type, "VerifiableCredential")
        self.assertEqual(guardian_doc.schema_version, VerraSchemaVersion.LATEST.value)
        
        # Verify Verifiable Credential structure
        self.assertIn("https://www.w3.org/2018/credentials/v1", guardian_doc.context)
        self.assertIn("VerifiableCredential", guardian_doc.type)
        self.assertIn("VerraVM0042Credential", guardian_doc.type)
        
        # Verify credential subject contains transformed data
        credential_subject = guardian_doc.credential_subject
        self.assertIn("energyProduction", credential_subject)
        self.assertIn("performance", credential_subject)
        self.assertIn("environmental", credential_subject)
        self.assertIn("dataIntegrity", credential_subject)
        
        # Verify energy production data
        energy_prod = credential_subject["energyProduction"]
        self.assertEqual(energy_prod["totalEnergyKWh"], 125.75)
        self.assertEqual(energy_prod["averagePowerW"], 5239.58)
        self.assertEqual(energy_prod["peakPowerW"], 8500.0)
        
        # Verify performance data
        performance = credential_subject["performance"]
        self.assertEqual(performance["systemEfficiency"], 0.96)
        self.assertEqual(performance["capacityFactor"], 0.85)
        
        # Verify environmental data
        environmental = credential_subject["environmental"]
        self.assertEqual(environmental["solarIrradiance"], 850.5)
        self.assertEqual(environmental["ambientTemperature"], 28.5)
        
        # Verify data integrity
        data_integrity = credential_subject["dataIntegrity"]
        self.assertEqual(data_integrity["verificationHash"], self.sample_report.verification_hash)
        self.assertEqual(data_integrity["qualityScore"], 0.92)
        
        # Verify device info
        device_info = credential_subject["deviceInfo"]
        self.assertEqual(device_info["deviceId"], "ESP32_TEST_001")
        self.assertEqual(device_info["deviceType"], "ESP32_SCADA")
        
        # Verify measurement period
        measurement_period = credential_subject["measurementPeriod"]
        self.assertEqual(measurement_period["durationHours"], 24.0)
        self.assertEqual(measurement_period["timezone"], "Africa/Casablanca")
        
        print("✅ VM0042 transformation test passed")
    
    def test_transform_energy_report_to_guardian_solar_pv(self):
        """Test transformation to Guardian Solar PV format"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.SOLAR_PV,
            VerraSchemaVersion.LATEST
        )
        
        # Verify Solar PV specific structure
        self.assertIn("SolarPVProductionCredential", guardian_doc.type)
        
        # Verify credential subject has solar-specific fields
        credential_subject = guardian_doc.credential_subject
        # Note: Solar PV uses different field structure
        self.assertIn("solarProduction", credential_subject)
        
        print("✅ Solar PV transformation test passed")
    
    def test_validate_guardian_document_valid(self):
        """Test validation of valid Guardian document"""
        # Test requirement 8.3: Add validation for required Guardian policy fields
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        # Verify validation passes
        self.assertTrue(validation_result["is_valid"])
        self.assertEqual(len(validation_result["errors"]), 0)
        
        # Verify policy compliance
        self.assertTrue(validation_result["policy_compliance"]["compliant"])
        
        # Verify schema validation
        self.assertTrue(validation_result["schema_validation"]["valid"])
        
        print("✅ Valid document validation test passed")
    
    def test_validate_guardian_document_invalid(self):
        """Test validation of invalid Guardian document"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        # Make document invalid by removing required field
        del guardian_doc.credential_subject["energyProduction"]["totalEnergyKWh"]
        
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        # Verify validation fails
        self.assertFalse(validation_result["is_valid"])
        self.assertGreater(len(validation_result["errors"]), 0)
        
        # Check for specific error about missing field
        error_messages = " ".join(validation_result["errors"])
        self.assertIn("totalEnergyKWh", error_messages)
        
        print("✅ Invalid document validation test passed")
    
    def test_adapt_for_policy_type(self):
        """Test schema adaptation for different policy types"""
        # Test requirement 8.3: Implement schema adaptation for different Guardian policy types
        
        # Start with VM0042 document
        vm0042_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        # Adapt to ARR policy
        arr_doc = self.transformer.adapt_for_policy_type(
            vm0042_doc,
            GuardianPolicyType.ARR
        )
        
        # Verify adaptation
        self.assertIn("VerraARRCredential", arr_doc.type)
        self.assertEqual(arr_doc.verra_metadata.methodology, GuardianPolicyType.ARR.value)
        
        # Verify ARR-specific fields
        if "carbonSequestration" in arr_doc.credential_subject:
            carbon_seq = arr_doc.credential_subject["carbonSequestration"]
            self.assertIn("totalCO2AvoidedKg", carbon_seq)
            self.assertIn("emissionFactor", carbon_seq)
        
        # Adapt to Solar PV policy
        solar_doc = self.transformer.adapt_for_policy_type(
            vm0042_doc,
            GuardianPolicyType.SOLAR_PV
        )
        
        # Verify Solar PV adaptation
        self.assertIn("SolarPVProductionCredential", solar_doc.type)
        
        print("✅ Policy type adaptation test passed")
    
    def test_field_mapping_documentation(self):
        """Test field mapping documentation generation"""
        # Test requirement 8.5: Create data mapping documentation for ESP32 to Guardian field conversion
        
        documentation = self.transformer.create_field_mapping_documentation()
        
        # Verify documentation structure
        self.assertIn("overview", documentation)
        self.assertIn("policy_types", documentation)
        self.assertIn("esp32_data_structure", documentation)
        self.assertIn("guardian_schema_structure", documentation)
        self.assertIn("transformation_examples", documentation)
        self.assertIn("validation_guidelines", documentation)
        
        # Verify policy types are documented
        policy_types = documentation["policy_types"]
        self.assertIn(GuardianPolicyType.VM0042.value, policy_types)
        self.assertIn(GuardianPolicyType.SOLAR_PV.value, policy_types)
        
        # Verify each policy type has required sections
        for policy_type, policy_doc in policy_types.items():
            self.assertIn("description", policy_doc)
            self.assertIn("field_mappings", policy_doc)
            self.assertIn("validation_rules", policy_doc)
            self.assertIn("example_transformation", policy_doc)
        
        # Verify ESP32 data structure documentation
        esp32_structure = documentation["esp32_data_structure"]
        self.assertIn("fields", esp32_structure)
        self.assertIn("units", esp32_structure)
        self.assertIn("data_quality_metrics", esp32_structure)
        
        # Verify Guardian schema documentation
        guardian_structure = documentation["guardian_schema_structure"]
        self.assertIn("verifiable_credential", guardian_structure)
        self.assertIn("verra_compliance", guardian_structure)
        self.assertIn("proof_mechanism", guardian_structure)
        
        # Verify transformation examples
        examples = documentation["transformation_examples"]
        self.assertIn("basic_energy_data", examples)
        self.assertIn("environmental_data", examples)
        self.assertIn("performance_metrics", examples)
        self.assertIn("data_quality", examples)
        
        # Verify validation guidelines
        guidelines = documentation["validation_guidelines"]
        self.assertIn("required_fields", guidelines)
        self.assertIn("data_ranges", guidelines)
        self.assertIn("format_requirements", guidelines)
        self.assertIn("compliance_checks", guidelines)
        
        print("✅ Field mapping documentation test passed")
    
    def test_export_guardian_document_json(self):
        """Test JSON export of Guardian document"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        json_output = self.transformer.export_guardian_document_json(guardian_doc)
        
        # Verify JSON is valid
        parsed_json = json.loads(json_output)
        
        # Verify required VC fields
        self.assertIn("@context", parsed_json)
        self.assertIn("type", parsed_json)
        self.assertIn("issuer", parsed_json)
        self.assertIn("issuanceDate", parsed_json)
        self.assertIn("credentialSubject", parsed_json)
        self.assertIn("proof", parsed_json)
        
        # Verify Verra metadata
        self.assertIn("verraMetadata", parsed_json)
        verra_metadata = parsed_json["verraMetadata"]
        self.assertEqual(verra_metadata["methodology"], GuardianPolicyType.VM0042.value)
        
        print("✅ JSON export test passed")
    
    def test_data_quality_validation(self):
        """Test data quality validation requirements"""
        # Test requirement 8.2: Add validation for required Guardian policy fields
        
        # Test with high quality data
        high_quality_report = self.sample_report
        high_quality_report.data_integrity_score = 0.95
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            high_quality_report,
            GuardianPolicyType.VM0042
        )
        
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertTrue(validation_result["is_valid"])
        
        # Test with low quality data
        low_quality_report = self.sample_report
        low_quality_report.data_integrity_score = 0.5
        
        guardian_doc_low = self.transformer.transform_energy_report_to_guardian(
            low_quality_report,
            GuardianPolicyType.VM0042
        )
        
        validation_result_low = self.transformer.validate_guardian_document(
            guardian_doc_low,
            GuardianPolicyType.VM0042
        )
        
        # Should still be valid but with warnings
        self.assertTrue(validation_result_low["is_valid"])
        # Check if warnings are generated (they should be in policy_compliance)
        policy_warnings = validation_result_low.get("policy_compliance", {}).get("warnings", [])
        general_warnings = validation_result_low.get("warnings", [])
        total_warnings = len(policy_warnings) + len(general_warnings)
        self.assertGreater(total_warnings, 0)
        
        print("✅ Data quality validation test passed")
    
    def test_verra_compliance_validation(self):
        """Test Verra methodology compliance validation"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        # Test with correct methodology
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertTrue(validation_result["policy_compliance"]["compliant"])
        self.assertTrue(validation_result["policy_compliance"]["methodology_check"])
        
        # Test with incorrect methodology
        guardian_doc.verra_metadata.methodology = "WRONG_METHODOLOGY"
        
        validation_result_wrong = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertFalse(validation_result_wrong["policy_compliance"]["compliant"])
        self.assertFalse(validation_result_wrong["policy_compliance"]["methodology_check"])
        
        print("✅ Verra compliance validation test passed")
    
    def test_temporal_validation(self):
        """Test temporal validity validation"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        # Test with valid temporal range
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertTrue(validation_result["policy_compliance"]["temporal_check"])
        
        # Test with invalid temporal range (end before start)
        guardian_doc.valid_until = guardian_doc.valid_from
        
        validation_result_invalid = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertFalse(validation_result_invalid["policy_compliance"]["temporal_check"])
        
        print("✅ Temporal validation test passed")
    
    def test_field_type_validation(self):
        """Test field type validation"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        # Test with correct types
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertTrue(validation_result["is_valid"])
        
        # Test with incorrect type (string instead of number)
        guardian_doc.credential_subject["energyProduction"]["totalEnergyKWh"] = "not_a_number"
        
        validation_result_invalid = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertFalse(validation_result_invalid["is_valid"])
        error_messages = " ".join(validation_result_invalid["errors"])
        self.assertIn("invalid type", error_messages.lower())
        
        print("✅ Field type validation test passed")
    
    def test_value_range_validation(self):
        """Test value range validation"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        # Test with values in valid range
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertTrue(validation_result["is_valid"])
        
        # Test with value out of range (negative energy)
        guardian_doc.credential_subject["energyProduction"]["totalEnergyKWh"] = -100
        
        validation_result_invalid = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertFalse(validation_result_invalid["is_valid"])
        error_messages = " ".join(validation_result_invalid["errors"])
        self.assertIn("below minimum", error_messages)
        
        print("✅ Value range validation test passed")
    
    def test_mena_compliance_integration(self):
        """Test MENA region compliance integration"""
        
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            self.sample_report,
            GuardianPolicyType.VM0042
        )
        
        # Verify MENA compliance data is included
        credential_subject = guardian_doc.credential_subject
        
        # Check regional compliance
        if "regionalCompliance" in credential_subject:
            regional = credential_subject["regionalCompliance"]
            self.assertEqual(regional["country"], "Morocco")
            self.assertEqual(regional["grid_standard"], "220V_50Hz")
        
        # Check Verra metadata geographic location
        geo_location = guardian_doc.verra_metadata.geographic_location
        self.assertEqual(geo_location["country"], "Morocco")
        self.assertEqual(geo_location["region"], "MENA")
        self.assertEqual(geo_location["grid_voltage"], 220.0)
        self.assertEqual(geo_location["grid_frequency"], 50.0)
        
        print("✅ MENA compliance integration test passed")


class TestGuardianDataTransformerIntegration(unittest.TestCase):
    """Integration tests for Guardian data transformer"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.transformer = GuardianDataTransformer()
    
    def test_end_to_end_transformation_workflow(self):
        """Test complete end-to-end transformation workflow"""
        
        # Create sample energy report
        period_start = datetime(2024, 1, 15, 0, 0, 0)
        period_end = period_start + timedelta(days=1)
        
        energy_metrics = EnergyMetrics(
            total_energy_kwh=200.5,
            avg_power_w=8354.17,
            max_power_w=12000.0,
            min_power_w=0.0,
            peak_to_avg_ratio=1.44,
            capacity_factor=0.78
        )
        
        performance_metrics = PerformanceMetrics(
            avg_efficiency=0.94,
            max_efficiency=0.97,
            min_efficiency=0.89,
            avg_power_factor=0.93,
            avg_grid_frequency=49.9
        )
        
        environmental_metrics = EnvironmentalMetrics(
            avg_irradiance_w_m2=920.3,
            max_irradiance_w_m2=1350.0,
            avg_temperature_c=31.2,
            max_temperature_c=38.5,
            min_temperature_c=24.8
        )
        
        data_quality = DataQualityMetrics(
            total_readings=1440,
            valid_readings=1425,
            missing_readings=15,
            data_completeness_percent=99.0,
            outlier_count=15,
            measurement_period_hours=24.0
        )
        
        energy_report = AggregatedEnergyReport(
            device_id="ESP32_INTEGRATION_001",
            period_start=period_start,
            period_end=period_end,
            energy_metrics=energy_metrics,
            performance_metrics=performance_metrics,
            environmental_metrics=environmental_metrics,
            data_quality=data_quality,
            verification_hash="integration_test_hash_123456789abcdef",
            data_integrity_score=0.98,
            grid_voltage_nominal=220.0,
            grid_frequency_nominal=50.0,
            regional_compliance={
                "country": "Morocco",
                "grid_standard": "220V_50Hz"
            }
        )
        
        # Step 1: Transform to Guardian format
        guardian_doc = self.transformer.transform_energy_report_to_guardian(
            energy_report,
            GuardianPolicyType.VM0042
        )
        
        # Step 2: Validate the document
        validation_result = self.transformer.validate_guardian_document(
            guardian_doc,
            GuardianPolicyType.VM0042
        )
        
        self.assertTrue(validation_result["is_valid"])
        
        # Step 3: Adapt for different policy type
        solar_doc = self.transformer.adapt_for_policy_type(
            guardian_doc,
            GuardianPolicyType.SOLAR_PV
        )
        
        # Step 4: Validate adapted document
        solar_validation = self.transformer.validate_guardian_document(
            solar_doc,
            GuardianPolicyType.SOLAR_PV
        )
        
        self.assertTrue(solar_validation["is_valid"])
        
        # Step 5: Export to JSON
        json_output = self.transformer.export_guardian_document_json(guardian_doc)
        parsed_json = json.loads(json_output)
        
        # Verify complete workflow
        self.assertIn("@context", parsed_json)
        self.assertIn("credentialSubject", parsed_json)
        self.assertIn("verraMetadata", parsed_json)
        
        print("✅ End-to-end transformation workflow test passed")
    
    def test_multiple_policy_type_support(self):
        """Test support for multiple policy types"""
        
        # Create base energy report
        energy_report = self._create_test_energy_report()
        
        # Test all supported policy types
        policy_types = [
            GuardianPolicyType.VM0042,
            GuardianPolicyType.ARR,
            GuardianPolicyType.SOLAR_PV,
            GuardianPolicyType.GENERIC_RENEWABLE
        ]
        
        for policy_type in policy_types:
            with self.subTest(policy_type=policy_type):
                # Transform to Guardian format
                guardian_doc = self.transformer.transform_energy_report_to_guardian(
                    energy_report,
                    policy_type
                )
                
                # Validate document
                validation_result = self.transformer.validate_guardian_document(
                    guardian_doc,
                    policy_type
                )
                
                # Should be valid for all policy types
                self.assertTrue(validation_result["is_valid"], 
                              f"Validation failed for policy type {policy_type}")
                
                # Verify policy-specific type is included
                expected_type = f"Verra{policy_type.value}Credential"
                if policy_type == GuardianPolicyType.SOLAR_PV:
                    expected_type = "SolarPVProductionCredential"
                elif policy_type == GuardianPolicyType.ARR:
                    expected_type = "AfforestationCredential"
                
                if expected_type != f"Verra{GuardianPolicyType.GENERIC_RENEWABLE.value}Credential":
                    self.assertIn(expected_type, guardian_doc.type)
        
        print("✅ Multiple policy type support test passed")
    
    def _create_test_energy_report(self) -> AggregatedEnergyReport:
        """Create test energy report for integration tests"""
        period_start = datetime(2024, 1, 20, 0, 0, 0)
        period_end = period_start + timedelta(days=1)
        
        return AggregatedEnergyReport(
            device_id="ESP32_MULTI_TEST",
            period_start=period_start,
            period_end=period_end,
            energy_metrics=EnergyMetrics(150.0, 6250.0, 9000.0, 0.0, 1.44, 0.80),
            performance_metrics=PerformanceMetrics(0.95, 0.98, 0.90, 0.94, 50.0),
            environmental_metrics=EnvironmentalMetrics(875.0, 1250.0, 29.5, 36.0, 23.0),
            data_quality=DataQualityMetrics(1440, 1420, 20, 98.6, 20, 24.0),
            verification_hash="multi_test_hash_abcdef123456",
            data_integrity_score=0.95,
            grid_voltage_nominal=220.0,
            grid_frequency_nominal=50.0,
            regional_compliance={"country": "Morocco", "grid_standard": "220V_50Hz"}
        )


if __name__ == "__main__":
    # Run the tests
    print("🧪 Running Guardian Data Transformer Tests...")
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(loader.loadTestsFromTestCase(TestGuardianDataTransformer))
    test_suite.addTests(loader.loadTestsFromTestCase(TestGuardianDataTransformerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\n🎉 All Guardian Data Transformer tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")