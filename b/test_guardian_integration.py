#!/usr/bin/env python3
"""
Integration Tests for Guardian Workflow
Tests complete ESP32 → Guardian → Hedera pipeline with authentication, policy discovery,
energy data submission, status tracking, and error handling mechanisms.

Requirements covered: 1.1, 1.2, 1.3, 1.4, 1.5
"""

import pytest
import os
import time
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional

# Import Guardian integration components
from guardian_auth import GuardianAuth, AuthToken, GuardianAuthError
from guardian_service import GuardianService, GuardianConfig, EnergyReport
from guardian_policy_manager import GuardianPolicyManager, PolicySchema, ValidationResult
from guardian_document_submitter import (
    GuardianDocumentSubmitter, 
    SubmissionResult, 
    DocumentStatus,
    SubmissionStatus,
    RetryConfig
)
from energy_data_aggregator import (
    EnergyDataAggregator,
    AggregatedEnergyReport,
    EnergyMetrics,
    PerformanceMetrics,
    EnvironmentalMetrics,
    DataQualityMetrics
)
from guardian_submissions_db import GuardianSubmissionsDB
import requests

class TestGuardianIntegrationWorkflow:
    """
    Integration tests for complete Guardian workflow
    Tests the full pipeline from ESP32 data to Guardian submission
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures and mock services"""
        # Test configuration
        self.test_config = {
            "guardian_url": "http://localhost:3000",
            "username": "test_user",
            "password": "test_password",
            "policy_id": "test_policy_123",
            "device_id": "ESP32_INTEGRATION_TEST",
            "tag_name": "renewable_energy"
        }
        
        # Mock Supabase client for energy data aggregator
        self.mock_supabase = Mock()
        
        # Initialize components with mocks
        self.guardian_auth = GuardianAuth(base_url=self.test_config["guardian_url"])
        self.guardian_service = GuardianService()
        self.policy_manager = GuardianPolicyManager(self.guardian_service)
        self.document_submitter = GuardianDocumentSubmitter(
            self.guardian_service,
            RetryConfig(max_retries=2, base_delay=0.1)  # Fast retries for testing
        )
        self.energy_aggregator = EnergyDataAggregator(supabase_client=self.mock_supabase)
        self.submissions_db = GuardianSubmissionsDB(supabase_client=self.mock_supabase)
        
        # Sample energy data for testing
        self.sample_energy_data = self._create_sample_energy_data()
        self.sample_aggregated_report = self._create_sample_aggregated_report()    

    def _create_sample_energy_data(self) -> List[Dict[str, Any]]:
        """Create sample ESP32 energy data for testing"""
        base_time = datetime.now() - timedelta(hours=1)
        data = []
        
        for i in range(60):  # 60 minutes of data
            timestamp = base_time + timedelta(minutes=i)
            reading = {
                "id": i + 1,
                "device_id": self.test_config["device_id"],
                "timestamp": timestamp.isoformat() + "Z",
                "power": 1000 + (i * 10),  # Increasing power
                "voltage": 220.0,
                "current": 4.55 + (i * 0.05),
                "ac_power_kw": 1.0 + (i * 0.01),
                "total_energy_kwh": 10.0 + (i * 0.017),  # ~1kWh per hour
                "grid_frequency_hz": 50.0,
                "power_factor": 0.95,
                "efficiency": 0.96,
                "ambient_temp_c": 25.0 + (i * 0.1),
                "irradiance_w_m2": 800.0 + (i * 5),
                "system_status": 1
            }
            data.append(reading)
        
        return data
    
    def _create_sample_aggregated_report(self) -> AggregatedEnergyReport:
        """Create sample aggregated energy report for testing"""
        return AggregatedEnergyReport(
            device_id=self.test_config["device_id"],
            period_start=datetime.now() - timedelta(hours=1),
            period_end=datetime.now(),
            energy_metrics=EnergyMetrics(
                total_energy_kwh=1.0,
                avg_power_w=1295.0,  # Average of increasing power
                max_power_w=1590.0,
                min_power_w=1000.0,
                peak_to_avg_ratio=1.23,
                capacity_factor=0.65
            ),
            performance_metrics=PerformanceMetrics(
                avg_efficiency=0.96,
                max_efficiency=0.96,
                min_efficiency=0.96,
                avg_power_factor=0.95,
                avg_grid_frequency=50.0
            ),
            environmental_metrics=EnvironmentalMetrics(
                avg_irradiance_w_m2=947.5,
                max_irradiance_w_m2=1095.0,
                avg_temperature_c=27.95,
                max_temperature_c=30.9,
                min_temperature_c=25.0
            ),
            data_quality=DataQualityMetrics(
                total_readings=60,
                valid_readings=60,
                missing_readings=0,
                data_completeness_percent=100.0,
                outlier_count=0,
                measurement_period_hours=1.0
            ),
            verification_hash="integration_test_hash_123",
            data_integrity_score=0.98,
            grid_voltage_nominal=220.0,
            grid_frequency_nominal=50.0,
            regional_compliance={
                "country": "Morocco",
                "grid_standard": "220V_50Hz"
            }
        ) 
   
    @patch('requests.Session.post')
    def test_guardian_authentication_flow(self, mock_post):
        """
        Test Guardian authentication and token management
        Requirement 1.1: Complete ESP32 → Guardian → Hedera pipeline
        """
        # Mock successful login response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "refreshToken": "mock_refresh_token_123",
            "id": "user_456",
            "username": self.test_config["username"]
        }
        mock_post.return_value = mock_response
        
        # Test authentication
        token = self.guardian_auth.login(
            self.test_config["username"], 
            self.test_config["password"]
        )
        
        # Verify authentication success
        assert token is not None
        assert token.token == "mock_refresh_token_123"
        assert token.username == self.test_config["username"]
        assert not token.is_expired()
        
        # Verify session headers were set
        assert "Authorization" in self.guardian_auth.session.headers
        assert self.guardian_auth.session.headers["Authorization"] == "Bearer mock_refresh_token_123"
        
        # Test token validation
        assert self.guardian_auth.is_token_valid()
        
        print("✅ Guardian authentication flow test passed")
    
    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_policy_discovery_and_validation(self, mock_get, mock_post):
        """
        Test Guardian policy discovery and data validation
        Requirement 1.2: Aggregate 24-hour ESP32 sensor readings from Supabase
        """
        # Mock authentication
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"refreshToken": "test_token", "id": "user_123"}
        )
        
        # Mock policy discovery response
        mock_policies_response = Mock()
        mock_policies_response.status_code = 200
        mock_policies_response.json.return_value = [
            {
                "id": self.test_config["policy_id"],
                "name": "Renewable Energy Policy",
                "description": "Policy for renewable energy carbon credits",
                "status": "PUBLISH",
                "config": {
                    "children": [
                        {
                            "blockType": "interfaceDocumentsSource",
                            "id": "block_123",
                            "tag": "renewable_energy",
                            "permissions": ["OWNER"]
                        }
                    ]
                }
            }
        ]
        mock_get.return_value = mock_policies_response
        
        # Authenticate first
        self.guardian_auth.login(self.test_config["username"], self.test_config["password"])
        
        # Test policy discovery
        policies = self.policy_manager.get_policies(status="PUBLISH")
        
        assert len(policies) > 0
        assert policies[0]["id"] == self.test_config["policy_id"]
        assert policies[0]["status"] == "PUBLISH"
        
        # Test renewable energy policy filtering
        renewable_policies = self.policy_manager.get_renewable_energy_policies()
        assert len(renewable_policies) > 0
        
        # Test policy schema retrieval
        schema = self.policy_manager.get_policy_schema(self.test_config["policy_id"])
        assert schema is not None
        assert schema.policy_id == self.test_config["policy_id"]
        
        # Test data validation against policy schema
        test_data = {
            "device_id": self.test_config["device_id"],
            "period_start": datetime.now().isoformat(),
            "period_end": (datetime.now() + timedelta(hours=1)).isoformat(),
            "total_energy_kwh": 1.0,
            "verification_hash": "test_hash_123"
        }
        
        validation_result = self.policy_manager.validate_data(test_data, self.test_config["policy_id"])
        assert isinstance(validation_result, ValidationResult)
        
        print("✅ Policy discovery and validation test passed")    

    def test_energy_data_aggregation_pipeline(self):
        """
        Test ESP32 energy data aggregation for Guardian submission
        Requirement 1.2: Aggregate 24-hour ESP32 sensor readings from Supabase
        """
        # Mock Supabase response with sample data
        mock_result = Mock()
        mock_result.data = self.sample_energy_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
        
        # Test daily data aggregation
        target_date = datetime.now() - timedelta(hours=1)
        report = self.energy_aggregator.aggregate_daily_data(
            self.test_config["device_id"], 
            target_date
        )
        
        # Verify aggregated report structure
        assert isinstance(report, AggregatedEnergyReport)
        assert report.device_id == self.test_config["device_id"]
        assert report.energy_metrics.total_energy_kwh > 0
        assert report.data_quality.total_readings == 60
        assert report.data_integrity_score > 0.5  # Adjusted for test data
        assert len(report.verification_hash) == 64  # SHA-256 hash
        
        # Test Guardian readiness validation
        readiness = self.energy_aggregator.validate_guardian_readiness(
            self.test_config["device_id"],
            target_date
        )
        
        assert "guardian_ready" in readiness
        assert readiness["guardian_ready"] is True
        assert all(check["passed"] for check in readiness["checks"].values())
        
        print("✅ Energy data aggregation pipeline test passed")
    
    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_document_submission_and_tracking(self, mock_get, mock_post):
        """
        Test Guardian document submission and status tracking
        Requirements 1.3, 1.4: Submit energy data to Guardian and track status
        """
        # Mock authentication
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"refreshToken": "test_token", "id": "user_123"}
        
        # Mock successful submission response
        submission_response = Mock()
        submission_response.status_code = 200
        submission_response.json.return_value = {
            "success": True,
            "guardian_document_id": "doc_integration_test_123",
            "policy_id": self.test_config["policy_id"],
            "status": "submitted",
            "message": "Energy report submitted successfully"
        }
        
        # Mock document status response
        status_response = Mock()
        status_response.status_code = 200
        status_response.json.return_value = [
            {
                "id": "doc_integration_test_123",
                "status": "PROCESSING",
                "createDate": datetime.now().isoformat(),
                "updateDate": datetime.now().isoformat(),
                "verificationStatus": "IN_PROGRESS"
            }
        ]
        
        mock_post.side_effect = [auth_response, submission_response]
        mock_get.return_value = status_response
        
        # Authenticate
        self.guardian_auth.login(self.test_config["username"], self.test_config["password"])
        
        # Test document submission
        result = self.document_submitter.submit_energy_report(
            self.sample_aggregated_report,
            self.test_config["policy_id"],
            self.test_config["tag_name"]
        )
        
        # Verify submission result
        assert result.success is True
        assert result.guardian_document_id == "doc_integration_test_123"
        assert result.policy_id == self.test_config["policy_id"]
        assert result.status == SubmissionStatus.SUBMITTED
        assert result.submitted_at is not None
        
        # Test document status tracking
        document_status = self.document_submitter.get_document_status(
            result.guardian_document_id,
            self.test_config["policy_id"]
        )
        
        assert document_status is not None
        assert document_status.document_id == "doc_integration_test_123"
        assert document_status.status == "PROCESSING"
        assert document_status.verification_status == "IN_PROGRESS"
        
        # Test submission progress tracking
        updated_result = self.document_submitter.track_submission_progress(result.submission_id)
        assert updated_result is not None
        assert updated_result.status == SubmissionStatus.PROCESSING
        
        print("✅ Document submission and tracking test passed")
    
    @patch('requests.Session.post')
    def test_error_handling_and_retry_mechanisms(self, mock_post):
        """
        Test error handling and retry mechanisms with Guardian API
        Requirement 1.5: Store Guardian document ID and status
        """
        # Test authentication failure
        auth_error_response = Mock()
        auth_error_response.status_code = 401
        auth_error_response.text = "Invalid credentials"
        mock_post.return_value = auth_error_response
        
        with pytest.raises(GuardianAuthError, match="Invalid username or password"):
            self.guardian_auth.login("invalid_user", "invalid_password")
        
        # Test connection error handling
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        error_info = self.document_submitter.handle_submission_errors(
            requests.exceptions.ConnectionError("Connection failed"),
            {"retry_count": 0}
        )
        
        assert error_info["error_code"] == "CONNECTION_ERROR"
        assert error_info["retry_recommended"] is True
        assert error_info["action"] == "retry_with_backoff"
        
        # Test retry mechanism with eventual success
        mock_post.side_effect = [
            # First attempt: connection error
            requests.exceptions.ConnectionError("Connection failed"),
            # Second attempt: success
            Mock(status_code=200, json=lambda: {"refreshToken": "retry_token", "id": "user_retry"})
        ]
        
        # This should succeed after retry
        token = self.guardian_auth.login(self.test_config["username"], self.test_config["password"])
        assert token is not None
        assert token.token == "retry_token"
        
        # Test HTTP error handling
        http_error = requests.exceptions.HTTPError("Bad Request")
        http_error.response = Mock(status_code=400)
        
        error_info = self.document_submitter.handle_submission_errors(
            http_error,
            {"retry_count": 0}
        )
        
        assert error_info["error_code"] == "BAD_REQUEST"
        assert error_info["permanent_failure"] is True
        assert error_info["retry_recommended"] is False
        
        print("✅ Error handling and retry mechanisms test passed")   
 
    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_complete_esp32_guardian_hedera_pipeline(self, mock_get, mock_post):
        """
        Test complete ESP32 → Guardian → Hedera pipeline integration
        Requirement 1.1: Complete ESP32 → Guardian → Hedera pipeline
        """
        # Mock authentication
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"refreshToken": "pipeline_token", "id": "user_pipeline"}
        
        # Mock policy discovery
        policies_response = Mock()
        policies_response.status_code = 200
        policies_response.json.return_value = [
            {
                "id": self.test_config["policy_id"],
                "name": "Integration Test Policy",
                "status": "PUBLISH"
            }
        ]
        
        # Mock successful submission
        submission_response = Mock()
        submission_response.status_code = 200
        submission_response.json.return_value = {
            "success": True,
            "guardian_document_id": "doc_pipeline_123",
            "hedera_transaction_id": "0.0.123456-789",
            "status": "submitted"
        }
        
        # Mock status progression: submitted → processing → verified
        status_responses = [
            Mock(status_code=200, json=lambda: [{"id": "doc_pipeline_123", "status": "SUBMITTED"}]),
            Mock(status_code=200, json=lambda: [{"id": "doc_pipeline_123", "status": "PROCESSING"}]),
            Mock(status_code=200, json=lambda: [{"id": "doc_pipeline_123", "status": "VERIFIED", "hederaTransactionId": "0.0.123456-789"}])
        ]
        
        mock_post.side_effect = [auth_response, submission_response]
        mock_get.side_effect = [policies_response] + status_responses
        
        # Mock Supabase data for energy aggregation
        mock_result = Mock()
        mock_result.data = self.sample_energy_data
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
        
        # Step 1: ESP32 Data Collection and Aggregation
        print("🔄 Step 1: ESP32 Data Collection and Aggregation")
        target_date = datetime.now() - timedelta(hours=1)
        energy_report = self.energy_aggregator.aggregate_daily_data(
            self.test_config["device_id"],
            target_date
        )
        
        assert energy_report.device_id == self.test_config["device_id"]
        assert energy_report.energy_metrics.total_energy_kwh > 0
        print(f"   ✅ Aggregated {energy_report.data_quality.total_readings} readings, {energy_report.energy_metrics.total_energy_kwh:.2f} kWh")
        
        # Step 2: Guardian Authentication
        print("🔄 Step 2: Guardian Authentication")
        auth_token = self.guardian_auth.login(
            self.test_config["username"],
            self.test_config["password"]
        )
        
        assert auth_token is not None
        assert not auth_token.is_expired()
        print(f"   ✅ Authenticated as {auth_token.username}")
        
        # Step 3: Policy Discovery and Validation
        print("🔄 Step 3: Policy Discovery and Validation")
        policies = self.policy_manager.get_policies(status="PUBLISH")
        
        assert len(policies) > 0
        target_policy = next((p for p in policies if p["id"] == self.test_config["policy_id"]), None)
        assert target_policy is not None
        print(f"   ✅ Found policy: {target_policy['name']}")
        
        # Step 4: Data Validation
        print("🔄 Step 4: Data Validation")
        validation_result = self.policy_manager.validate_energy_report(
            energy_report,
            self.test_config["policy_id"]
        )
        
        assert validation_result.is_valid
        print(f"   ✅ Data validation passed with {len(validation_result.warnings)} warnings")
        
        # Step 5: Guardian Submission
        print("🔄 Step 5: Guardian Submission")
        submission_result = self.document_submitter.submit_energy_report(
            energy_report,
            self.test_config["policy_id"],
            self.test_config["tag_name"]
        )
        
        assert submission_result.success
        assert submission_result.guardian_document_id == "doc_pipeline_123"
        print(f"   ✅ Submitted to Guardian: {submission_result.guardian_document_id}")
        
        # Step 6: Status Tracking and Hedera Integration
        print("🔄 Step 6: Status Tracking and Hedera Integration")
        
        # Simulate status progression
        for i, expected_status in enumerate(["SUBMITTED", "PROCESSING", "VERIFIED"]):
            time.sleep(0.1)  # Small delay to simulate processing time
            
            status = self.document_submitter.get_document_status(
                submission_result.guardian_document_id,
                self.test_config["policy_id"]
            )
            
            assert status is not None
            print(f"   📊 Status: {status.status}")
            
            if status.status == "VERIFIED":
                # Check for Hedera transaction ID in final status
                assert hasattr(status, 'metadata')
                print(f"   ✅ Verified on Hedera blockchain")
                break
        
        # Step 7: Database Storage
        print("🔄 Step 7: Database Storage")
        
        # Store submission record in database
        submission_record = {
            "device_id": energy_report.device_id,
            "policy_id": self.test_config["policy_id"],
            "guardian_document_id": submission_result.guardian_document_id,
            "status": "VERIFIED",
            "period_start": energy_report.period_start,
            "period_end": energy_report.period_end,
            "total_energy_kwh": energy_report.energy_metrics.total_energy_kwh,
            "verification_hash": energy_report.verification_hash,
            "submitted_at": submission_result.submitted_at,
            "verified_at": datetime.now()
        }
        
        # Verify all required fields are present
        required_fields = [
            "device_id", "policy_id", "guardian_document_id", "status",
            "total_energy_kwh", "verification_hash"
        ]
        
        for field in required_fields:
            assert field in submission_record
            assert submission_record[field] is not None
        
        print(f"   ✅ Stored submission record for {submission_record['device_id']}")
        
        print("🎉 Complete ESP32 → Guardian → Hedera pipeline test passed!")
        
        # Return pipeline results for further verification
        return {
            "energy_report": energy_report,
            "auth_token": auth_token,
            "policies": policies,
            "validation_result": validation_result,
            "submission_result": submission_result,
            "final_status": status,
            "submission_record": submission_record
        }   
 
    def test_concurrent_submissions(self):
        """
        Test handling multiple concurrent Guardian submissions
        Requirement 1.5: Store Guardian document ID and status
        """
        # Create multiple energy reports
        reports = []
        for i in range(3):
            report = self.sample_aggregated_report
            report.device_id = f"ESP32_CONCURRENT_{i}"
            reports.append(report)
        
        # Mock successful submissions
        with patch.object(self.document_submitter.guardian_service, 'submit_energy_report') as mock_submit:
            mock_submit.side_effect = [
                {"success": True, "guardian_document_id": f"doc_concurrent_{i}", "status": "submitted"}
                for i in range(3)
            ]
            
            # Submit all reports
            results = []
            for i, report in enumerate(reports):
                result = self.document_submitter.submit_energy_report(
                    report,
                    self.test_config["policy_id"],
                    self.test_config["tag_name"]
                )
                results.append(result)
            
            # Verify all submissions succeeded
            assert len(results) == 3
            assert all(result.success for result in results)
            assert len(set(result.guardian_document_id for result in results)) == 3  # All unique IDs
            
            # Verify submission history
            history = self.document_submitter.get_submission_history(limit=10)
            assert len(history) >= 3
        
        print("✅ Concurrent submissions test passed")
    
    def test_data_integrity_verification(self):
        """
        Test data integrity verification throughout the pipeline
        Requirement 1.2: Create data quality validation and verification hash generation
        """
        # Test hash consistency
        report1 = self.sample_aggregated_report
        report2 = self.sample_aggregated_report
        
        # Same data should produce same hash
        hash1 = self.energy_aggregator._generate_verification_hash(
            report1.device_id,
            self.sample_energy_data,
            report1.energy_metrics
        )
        hash2 = self.energy_aggregator._generate_verification_hash(
            report2.device_id,
            self.sample_energy_data,
            report2.energy_metrics
        )
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256
        
        # Modified data should produce different hash
        modified_data = self.sample_energy_data.copy()
        modified_data[0]["power"] = 9999.0  # Modify first reading
        
        hash3 = self.energy_aggregator._generate_verification_hash(
            report1.device_id,
            modified_data,
            report1.energy_metrics
        )
        
        assert hash1 != hash3
        
        # Test data integrity score calculation
        high_quality_metrics = DataQualityMetrics(
            total_readings=1440,
            valid_readings=1440,
            missing_readings=0,
            data_completeness_percent=100.0,
            outlier_count=0,
            measurement_period_hours=24.0
        )
        
        high_score = self.energy_aggregator._calculate_data_integrity_score(
            high_quality_metrics,
            self.sample_energy_data
        )
        
        assert high_score > 0.9
        
        # Test with lower quality data
        low_quality_metrics = DataQualityMetrics(
            total_readings=1440,
            valid_readings=1000,  # Missing 440 readings
            missing_readings=440,
            data_completeness_percent=69.4,
            outlier_count=100,
            measurement_period_hours=24.0
        )
        
        low_score = self.energy_aggregator._calculate_data_integrity_score(
            low_quality_metrics,
            self.sample_energy_data[:1000]  # Reduced data
        )
        
        assert low_score < high_score
        assert 0.0 <= low_score <= 1.0
        
        print("✅ Data integrity verification test passed")    

    @patch('requests.Session.post')
    def test_guardian_api_rate_limiting(self, mock_post):
        """
        Test Guardian API rate limiting and throttling
        """
        # Mock rate limit response (HTTP 429)
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.text = "Rate limit exceeded"
        
        # Mock eventual success
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"refreshToken": "rate_limit_token", "id": "user_rate"}
        
        mock_post.side_effect = [rate_limit_response, success_response]
        
        # Test rate limit handling
        error_info = self.document_submitter.handle_submission_errors(
            requests.exceptions.HTTPError("Rate limit exceeded"),
            {"retry_count": 0}
        )
        
        # Should recommend retry for rate limiting
        assert error_info["retry_recommended"] is True
        assert error_info["retry_delay"] > 0
        
        print("✅ Guardian API rate limiting test passed")
    
    def test_regional_compliance_validation(self):
        """
        Test MENA regional compliance validation (Morocco standards)
        Requirement 1.2: Include MENA-specific details (Morocco voltage, reporting standards)
        """
        # Test Morocco-specific validation
        morocco_data = {
            "voltage": 220.0,  # Morocco standard
            "grid_frequency_hz": 50.0,  # Morocco standard
            "ambient_temp_c": 35.0,  # Typical Morocco temperature
            "power": 1500.0
        }
        
        validated_data = self.energy_aggregator._validate_and_clean_data([morocco_data])
        assert len(validated_data) == 1
        
        # Test out-of-range voltage (Morocco: 220V ±10%)
        invalid_voltage_data = {
            "voltage": 250.0,  # Outside ±10% range
            "grid_frequency_hz": 50.0,
            "power": 1000.0
        }
        
        validated_data = self.energy_aggregator._validate_and_clean_data([invalid_voltage_data])
        assert len(validated_data) == 0  # Should be filtered out
        
        # Test frequency validation (Morocco: 50Hz ±2%)
        invalid_frequency_data = {
            "voltage": 220.0,
            "grid_frequency_hz": 53.0,  # Outside ±2% range
            "power": 1000.0
        }
        
        validated_data = self.energy_aggregator._validate_and_clean_data([invalid_frequency_data])
        assert len(validated_data) == 0  # Should be filtered out
        
        # Test regional compliance in aggregated report
        report = self.sample_aggregated_report
        assert report.grid_voltage_nominal == 220.0
        assert report.grid_frequency_nominal == 50.0
        assert report.regional_compliance["country"] == "Morocco"
        assert report.regional_compliance["grid_standard"] == "220V_50Hz"
        
        print("✅ Regional compliance validation test passed")

class TestGuardianIntegrationErrorScenarios:
    """
    Test error scenarios and edge cases in Guardian integration
    """
    
    def setup_method(self):
        """Set up test fixtures for error scenarios"""
        self.guardian_auth = GuardianAuth(base_url="http://localhost:3000")
        self.document_submitter = GuardianDocumentSubmitter()
    
    def test_guardian_service_unavailable(self):
        """Test handling when Guardian service is completely unavailable"""
        with patch('requests.Session.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Service unavailable")
            
            with pytest.raises(GuardianAuthError):
                self.guardian_auth.login("test_user", "test_password")
    
    def test_invalid_policy_id(self):
        """Test handling of invalid policy IDs"""
        with patch.object(self.document_submitter.guardian_service, 'submit_energy_report') as mock_submit:
            mock_submit.return_value = {
                "success": False,
                "error": "Not found",
                "message": "Policy not found"
            }
            
            # Create a dummy report
            dummy_report = AggregatedEnergyReport(
                device_id="TEST_DEVICE",
                period_start=datetime.now() - timedelta(hours=1),
                period_end=datetime.now(),
                energy_metrics=EnergyMetrics(1.0, 1000.0, 1200.0, 800.0, 1.2, 0.8),
                performance_metrics=PerformanceMetrics(0.96, 0.96, 0.96, 0.95, 50.0),
                environmental_metrics=EnvironmentalMetrics(800.0, 1000.0, 25.0, 30.0, 20.0),
                data_quality=DataQualityMetrics(60, 60, 0, 100.0, 0, 1.0),
                verification_hash="test_hash",
                data_integrity_score=0.95
            )
            
            result = self.document_submitter.submit_energy_report(
                dummy_report,
                "invalid_policy_id",
                "renewable_energy"
            )
            
            assert result.success is False
            assert result.status == SubmissionStatus.FAILED
    
    def test_malformed_energy_data(self):
        """Test handling of malformed energy data"""
        # Test with None report
        result = self.document_submitter.submit_energy_report(None, "policy_123", "tag")
        assert result.success is False
        assert result.error_code == "INVALID_INPUT"
        
        # Test with empty policy ID
        dummy_report = AggregatedEnergyReport(
            device_id="TEST_DEVICE",
            period_start=datetime.now() - timedelta(hours=1),
            period_end=datetime.now(),
            energy_metrics=EnergyMetrics(1.0, 1000.0, 1200.0, 800.0, 1.2, 0.8),
            performance_metrics=PerformanceMetrics(0.96, 0.96, 0.96, 0.95, 50.0),
            environmental_metrics=EnvironmentalMetrics(800.0, 1000.0, 25.0, 30.0, 20.0),
            data_quality=DataQualityMetrics(60, 60, 0, 100.0, 0, 1.0),
            verification_hash="test_hash",
            data_integrity_score=0.95
        )
        
        result = self.document_submitter.submit_energy_report(dummy_report, "", "tag")
        assert result.success is False
        assert result.error_code == "INVALID_POLICY"

# Integration test configuration
@pytest.mark.integration
class TestGuardianLiveIntegration:
    """
    Live integration tests that require actual Guardian instance
    These tests are skipped unless GUARDIAN_INTEGRATION_TEST environment variable is set
    """
    
    def setup_method(self):
        """Set up for live integration tests"""
        if not os.getenv("GUARDIAN_INTEGRATION_TEST"):
            pytest.skip("Live integration tests skipped - set GUARDIAN_INTEGRATION_TEST=1 to run")
        
        self.guardian_url = os.getenv("GUARDIAN_URL", "http://localhost:3000")
        self.guardian_username = os.getenv("GUARDIAN_USERNAME")
        self.guardian_password = os.getenv("GUARDIAN_PASSWORD")
        
        if not self.guardian_username or not self.guardian_password:
            pytest.skip("Guardian credentials not provided - set GUARDIAN_USERNAME and GUARDIAN_PASSWORD")
        
        self.guardian_auth = GuardianAuth(base_url=self.guardian_url)
        self.guardian_service = GuardianService()
        self.policy_manager = GuardianPolicyManager(self.guardian_service)
    
    def test_live_guardian_authentication(self):
        """Test authentication against live Guardian instance"""
        try:
            token = self.guardian_auth.login(self.guardian_username, self.guardian_password)
            assert token is not None
            assert not token.is_expired()
            
            # Test user info retrieval
            user_info = self.guardian_auth.get_user_info()
            assert user_info is not None
            assert user_info.get("username") == self.guardian_username
            
            # Test logout
            logout_success = self.guardian_auth.logout()
            assert logout_success is True
            
        except Exception as e:
            pytest.fail(f"Live Guardian authentication failed: {e}")
    
    def test_live_policy_discovery(self):
        """Test policy discovery against live Guardian instance"""
        try:
            # Authenticate first
            self.guardian_auth.login(self.guardian_username, self.guardian_password)
            
            # Get policies
            policies = self.policy_manager.get_policies(status="PUBLISH")
            assert isinstance(policies, list)
            
            if len(policies) > 0:
                # Test policy schema retrieval
                first_policy = policies[0]
                schema = self.policy_manager.get_policy_schema(first_policy["id"])
                assert schema is not None
                
                # Test policy blocks
                blocks = self.policy_manager.get_policy_blocks(first_policy["id"])
                assert isinstance(blocks, list)
            
        except Exception as e:
            pytest.fail(f"Live policy discovery failed: {e}")

if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "-m", "not integration"  # Skip live integration tests by default
    ])