#!/usr/bin/env python3
"""
Unit tests for Guardian Document Submitter
Tests submission logic, retry mechanisms, status tracking, and error handling
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Import the classes we're testing
from guardian_document_submitter import (
    GuardianDocumentSubmitter, 
    SubmissionResult, 
    DocumentStatus, 
    SubmissionStatus,
    RetryConfig
)
from energy_data_aggregator import (
    AggregatedEnergyReport, 
    EnergyMetrics, 
    PerformanceMetrics, 
    EnvironmentalMetrics, 
    DataQualityMetrics
)
from guardian_service import GuardianService, EnergyReport
from guardian_auth import GuardianAuthError
import requests

class TestGuardianDocumentSubmitter(unittest.TestCase):
    """Test cases for GuardianDocumentSubmitter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock Guardian service
        self.mock_guardian_service = Mock(spec=GuardianService)
        
        # Create submitter with mocked service
        self.submitter = GuardianDocumentSubmitter(
            guardian_service=self.mock_guardian_service,
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)  # Fast retries for testing
        )
        
        # Sample energy report for testing
        self.sample_report = self._create_sample_energy_report()
        
        # Sample policy and tag
        self.test_policy_id = "test_policy_123"
        self.test_tag_name = "renewable_energy"
    
    def _create_sample_energy_report(self) -> AggregatedEnergyReport:
        """Create a sample energy report for testing"""
        return AggregatedEnergyReport(
            device_id="ESP32_TEST_001",
            period_start=datetime(2024, 1, 1, 0, 0, 0),
            period_end=datetime(2024, 1, 2, 0, 0, 0),
            energy_metrics=EnergyMetrics(
                total_energy_kwh=25.5,
                avg_power_w=1062.5,
                max_power_w=2500.0,
                min_power_w=0.0,
                peak_to_avg_ratio=2.35,
                capacity_factor=0.42
            ),
            performance_metrics=PerformanceMetrics(
                avg_efficiency=0.96,
                max_efficiency=0.98,
                min_efficiency=0.94,
                avg_power_factor=0.95,
                avg_grid_frequency=50.0
            ),
            environmental_metrics=EnvironmentalMetrics(
                avg_irradiance_w_m2=450.0,
                max_irradiance_w_m2=1200.0,
                avg_temperature_c=28.5,
                max_temperature_c=35.2,
                min_temperature_c=22.1
            ),
            data_quality=DataQualityMetrics(
                total_readings=1440,
                valid_readings=1425,
                missing_readings=15,
                data_completeness_percent=99.0,
                outlier_count=15,
                measurement_period_hours=24.0
            ),
            verification_hash="abc123def456",
            data_integrity_score=0.95,
            grid_voltage_nominal=220.0,
            grid_frequency_nominal=50.0,
            regional_compliance={
                "country": "Morocco",
                "grid_standard": "220V_50Hz"
            }
        )
    
    def test_submit_energy_report_success(self):
        """Test successful energy report submission"""
        # Mock successful Guardian response
        self.mock_guardian_service.submit_energy_report.return_value = {
            "success": True,
            "guardian_document_id": "doc_123456",
            "policy_id": self.test_policy_id,
            "tag_name": self.test_tag_name,
            "status": "submitted",
            "message": "Energy report submitted successfully"
        }
        
        # Submit the report
        result = self.submitter.submit_energy_report(
            self.sample_report, 
            self.test_policy_id, 
            self.test_tag_name
        )
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.guardian_document_id, "doc_123456")
        self.assertEqual(result.policy_id, self.test_policy_id)
        self.assertEqual(result.tag_name, self.test_tag_name)
        self.assertEqual(result.status, SubmissionStatus.SUBMITTED)
        self.assertIsNotNone(result.submitted_at)
        
        # Verify Guardian service was called correctly
        self.mock_guardian_service.submit_energy_report.assert_called_once()
        call_args = self.mock_guardian_service.submit_energy_report.call_args
        self.assertEqual(call_args[1]['policy_id'], self.test_policy_id)
        self.assertEqual(call_args[1]['tag_name'], self.test_tag_name)
    
    def test_submit_energy_report_invalid_input(self):
        """Test submission with invalid input parameters"""
        # Test with None report
        result = self.submitter.submit_energy_report(None, self.test_policy_id, self.test_tag_name)
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "INVALID_INPUT")
        
        # Test with empty policy ID
        result = self.submitter.submit_energy_report(self.sample_report, "", self.test_tag_name)
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "INVALID_POLICY")
        
        # Test with empty tag name
        result = self.submitter.submit_energy_report(self.sample_report, self.test_policy_id, "")
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "INVALID_TAG")
    
    def test_submit_energy_report_guardian_error(self):
        """Test submission when Guardian returns an error"""
        # Mock Guardian error response
        self.mock_guardian_service.submit_energy_report.return_value = {
            "success": False,
            "error": "Bad request",
            "message": "Invalid data format"
        }
        
        # Submit the report
        result = self.submitter.submit_energy_report(
            self.sample_report, 
            self.test_policy_id, 
            self.test_tag_name
        )
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.status, SubmissionStatus.FAILED)
        self.assertIn("Invalid data format", result.message)
    
    def test_submit_with_retry_success_after_failure(self):
        """Test retry logic - success after initial failure"""
        # Mock Guardian service to fail first, then succeed
        self.mock_guardian_service.submit_energy_report.side_effect = [
            {"success": False, "error": "Connection error", "message": "Network timeout"},
            {"success": True, "guardian_document_id": "doc_retry_123", "message": "Success on retry"}
        ]
        
        # Submit the report
        result = self.submitter.submit_energy_report(
            self.sample_report, 
            self.test_policy_id, 
            self.test_tag_name
        )
        
        # Verify success after retry
        self.assertTrue(result.success)
        self.assertEqual(result.guardian_document_id, "doc_retry_123")
        self.assertEqual(result.retry_count, 1)  # One retry occurred
        
        # Verify Guardian service was called twice
        self.assertEqual(self.mock_guardian_service.submit_energy_report.call_count, 2)
    
    def test_submit_with_retry_max_retries_exceeded(self):
        """Test retry logic when max retries are exceeded"""
        # Mock Guardian service to always fail
        self.mock_guardian_service.submit_energy_report.return_value = {
            "success": False,
            "error": "Server error",
            "message": "Internal server error"
        }
        
        # Submit the report
        result = self.submitter.submit_energy_report(
            self.sample_report, 
            self.test_policy_id, 
            self.test_tag_name
        )
        
        # Verify failure after max retries
        self.assertFalse(result.success)
        self.assertEqual(result.status, SubmissionStatus.FAILED)
        self.assertEqual(result.retry_count, 2)  # Max retries reached
        
        # Verify Guardian service was called max_retries + 1 times
        self.assertEqual(self.mock_guardian_service.submit_energy_report.call_count, 3)
    
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_submit_with_exponential_backoff(self, mock_sleep):
        """Test exponential backoff in retry logic"""
        # Mock Guardian service to always fail
        self.mock_guardian_service.submit_energy_report.side_effect = Exception("Connection error")
        
        # Submit the report
        result = self.submitter.submit_energy_report(
            self.sample_report, 
            self.test_policy_id, 
            self.test_tag_name
        )
        
        # Verify failure
        self.assertFalse(result.success)
        
        # Verify sleep was called with increasing delays
        self.assertEqual(mock_sleep.call_count, 2)  # 2 retries = 2 sleeps
        
        # Check that delays increased (with jitter, so approximate)
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        self.assertGreater(sleep_calls[1], sleep_calls[0])  # Second delay > first delay
    
    def test_get_document_status_success(self):
        """Test successful document status retrieval"""
        # Mock Guardian service response
        mock_documents = [
            {
                "id": "doc_123456",
                "status": "VERIFIED",
                "createDate": "2024-01-01T12:00:00Z",
                "updateDate": "2024-01-01T13:00:00Z",
                "verificationStatus": "APPROVED"
            }
        ]
        self.mock_guardian_service.get_policy_documents.return_value = mock_documents
        
        # Get document status
        status = self.submitter.get_document_status("doc_123456", self.test_policy_id)
        
        # Verify the result
        self.assertIsNotNone(status)
        self.assertEqual(status.document_id, "doc_123456")
        self.assertEqual(status.policy_id, self.test_policy_id)
        self.assertEqual(status.status, "VERIFIED")
        self.assertEqual(status.verification_status, "APPROVED")
        self.assertIsNotNone(status.created_at)
        self.assertIsNotNone(status.updated_at)
    
    def test_get_document_status_not_found(self):
        """Test document status when document is not found"""
        # Mock Guardian service to return empty list
        self.mock_guardian_service.get_policy_documents.return_value = []
        
        # Get document status
        status = self.submitter.get_document_status("nonexistent_doc", self.test_policy_id)
        
        # Verify None is returned
        self.assertIsNone(status)
    
    def test_get_document_status_no_policy_id(self):
        """Test document status retrieval without policy ID"""
        # Get document status without policy ID
        status = self.submitter.get_document_status("doc_123456")
        
        # Should return None since no policy ID provided and no active submissions
        self.assertIsNone(status)
    
    def test_track_submission_progress(self):
        """Test submission progress tracking"""
        # First, create a successful submission
        self.mock_guardian_service.submit_energy_report.return_value = {
            "success": True,
            "guardian_document_id": "doc_progress_123",
            "policy_id": self.test_policy_id,
            "message": "Submitted successfully"
        }
        
        result = self.submitter.submit_energy_report(
            self.sample_report, 
            self.test_policy_id, 
            self.test_tag_name
        )
        
        submission_id = result.submission_id
        
        # Mock updated document status
        mock_documents = [
            {
                "id": "doc_progress_123",
                "status": "PROCESSING",
                "verificationStatus": "IN_PROGRESS"
            }
        ]
        self.mock_guardian_service.get_policy_documents.return_value = mock_documents
        
        # Track progress
        updated_result = self.submitter.track_submission_progress(submission_id)
        
        # Verify status was updated
        self.assertIsNotNone(updated_result)
        self.assertEqual(updated_result.status, SubmissionStatus.PROCESSING)
    
    def test_handle_submission_errors_auth_error(self):
        """Test error handling for authentication errors"""
        auth_error = GuardianAuthError("Invalid credentials")
        error_info = self.submitter.handle_submission_errors(auth_error, {"retry_count": 0})
        
        self.assertEqual(error_info["error_code"], "AUTH_ERROR")
        self.assertTrue(error_info["retry_recommended"])
        self.assertEqual(error_info["action"], "re_authenticate")
    
    def test_handle_submission_errors_connection_error(self):
        """Test error handling for connection errors"""
        conn_error = requests.exceptions.ConnectionError("Cannot connect")
        error_info = self.submitter.handle_submission_errors(conn_error, {"retry_count": 1})
        
        self.assertEqual(error_info["error_code"], "CONNECTION_ERROR")
        self.assertTrue(error_info["retry_recommended"])
        self.assertEqual(error_info["action"], "retry_with_backoff")
        self.assertGreater(error_info["retry_delay"], 0)
    
    def test_handle_submission_errors_http_400(self):
        """Test error handling for HTTP 400 Bad Request"""
        mock_response = Mock()
        mock_response.status_code = 400
        http_error = requests.exceptions.HTTPError("Bad Request")
        http_error.response = mock_response
        
        error_info = self.submitter.handle_submission_errors(http_error, {"retry_count": 0})
        
        self.assertEqual(error_info["error_code"], "BAD_REQUEST")
        self.assertFalse(error_info["retry_recommended"])
        self.assertTrue(error_info["permanent_failure"])
        self.assertEqual(error_info["action"], "fix_data_format")
    
    def test_handle_submission_errors_http_500(self):
        """Test error handling for HTTP 500 Server Error"""
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = requests.exceptions.HTTPError("Internal Server Error")
        http_error.response = mock_response
        
        error_info = self.submitter.handle_submission_errors(http_error, {"retry_count": 0})
        
        self.assertEqual(error_info["error_code"], "SERVER_ERROR")
        self.assertTrue(error_info["retry_recommended"])
        self.assertFalse(error_info["permanent_failure"])
        self.assertEqual(error_info["action"], "retry_later")
    
    def test_format_report_for_guardian(self):
        """Test energy report formatting for Guardian"""
        # Access the private method for testing
        guardian_data = self.submitter._format_report_for_guardian(self.sample_report)
        
        # Verify structure and key fields
        self.assertEqual(guardian_data["type"], "renewable_energy_production")
        self.assertEqual(guardian_data["device_id"], "ESP32_TEST_001")
        self.assertIn("reporting_period", guardian_data)
        self.assertIn("energy_production", guardian_data)
        self.assertIn("performance_metrics", guardian_data)
        self.assertIn("environmental_conditions", guardian_data)
        self.assertIn("data_quality", guardian_data)
        self.assertIn("regional_compliance", guardian_data)
        
        # Verify specific values
        self.assertEqual(guardian_data["energy_production"]["total_kwh"], 25.5)
        self.assertEqual(guardian_data["performance_metrics"]["average_efficiency"], 0.96)
        self.assertEqual(guardian_data["data_quality"]["verification_hash"], "abc123def456")
        self.assertEqual(guardian_data["regional_compliance"]["grid_voltage_nominal"], 220.0)
    
    @patch('time.time')
    def test_get_submission_history(self, mock_time):
        """Test submission history retrieval"""
        # Mock time to ensure unique submission IDs
        mock_time.side_effect = [1000, 2000]  # Different times for each submission
        
        # Create multiple submissions
        self.mock_guardian_service.submit_energy_report.return_value = {
            "success": True,
            "guardian_document_id": "doc_history_1",
            "message": "Success"
        }
        
        # Submit multiple reports
        result1 = self.submitter.submit_energy_report(self.sample_report, "policy_1", "tag_1")
        result2 = self.submitter.submit_energy_report(self.sample_report, "policy_2", "tag_2")
        
        # Get submission history
        history = self.submitter.get_submission_history(limit=10)
        
        # Verify history
        self.assertEqual(len(history), 2)
        self.assertIn(result1, history)
        self.assertIn(result2, history)
    
    def test_retry_failed_submission(self):
        """Test retrying a failed submission"""
        # First, create a failed submission
        self.mock_guardian_service.submit_energy_report.return_value = {
            "success": False,
            "error": "Server error",
            "message": "Temporary failure"
        }
        
        original_result = self.submitter.submit_energy_report(
            self.sample_report, 
            self.test_policy_id, 
            self.test_tag_name
        )
        
        # Verify it failed
        self.assertFalse(original_result.success)
        self.assertEqual(original_result.status, SubmissionStatus.FAILED)
        
        # Mock success for retry
        self.mock_guardian_service.submit_energy_report.return_value = {
            "success": True,
            "guardian_document_id": "doc_retry_success",
            "message": "Retry successful"
        }
        
        # Retry the failed submission
        retry_result = self.submitter.retry_failed_submission(original_result.submission_id)
        
        # Verify retry succeeded
        self.assertTrue(retry_result.success)
        self.assertEqual(retry_result.guardian_document_id, "doc_retry_success")
        self.assertGreater(retry_result.retry_count, original_result.retry_count)
    
    def test_retry_nonexistent_submission(self):
        """Test retrying a submission that doesn't exist"""
        result = self.submitter.retry_failed_submission("nonexistent_submission")
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "SUBMISSION_NOT_FOUND")
    
    def test_map_guardian_status(self):
        """Test Guardian status mapping to internal status"""
        # Test various Guardian statuses
        test_cases = [
            ("NEW", SubmissionStatus.SUBMITTED),
            ("PENDING", SubmissionStatus.PROCESSING),
            ("IN_PROGRESS", SubmissionStatus.PROCESSING),
            ("VERIFIED", SubmissionStatus.VERIFIED),
            ("APPROVED", SubmissionStatus.VERIFIED),
            ("REJECTED", SubmissionStatus.REJECTED),
            ("FAILED", SubmissionStatus.FAILED),
            ("ERROR", SubmissionStatus.FAILED),
            ("EXPIRED", SubmissionStatus.EXPIRED),
            ("UNKNOWN_STATUS", SubmissionStatus.PENDING)  # Default case
        ]
        
        for guardian_status, expected_status in test_cases:
            mapped_status = self.submitter._map_guardian_status(guardian_status)
            self.assertEqual(mapped_status, expected_status, 
                           f"Failed mapping {guardian_status} to {expected_status}")
    
    def test_parse_datetime(self):
        """Test datetime parsing from Guardian API responses"""
        # Test various datetime formats
        test_cases = [
            "2024-01-01T12:00:00.000Z",
            "2024-01-01T12:00:00Z",
            "2024-01-01 12:00:00",
            "2024-01-01T12:00:00+00:00"
        ]
        
        for date_str in test_cases:
            parsed_date = self.submitter._parse_datetime(date_str)
            self.assertIsNotNone(parsed_date, f"Failed to parse {date_str}")
            self.assertIsInstance(parsed_date, datetime)
        
        # Test invalid datetime
        invalid_date = self.submitter._parse_datetime("invalid_date")
        self.assertIsNone(invalid_date)
        
        # Test None input
        none_date = self.submitter._parse_datetime(None)
        self.assertIsNone(none_date)

class TestRetryConfig(unittest.TestCase):
    """Test cases for RetryConfig class"""
    
    def test_default_retry_config(self):
        """Test default retry configuration"""
        config = RetryConfig()
        
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.base_delay, 1.0)
        self.assertEqual(config.max_delay, 60.0)
        self.assertEqual(config.exponential_base, 2.0)
        self.assertTrue(config.jitter)
    
    def test_custom_retry_config(self):
        """Test custom retry configuration"""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=1.5,
            jitter=False
        )
        
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.base_delay, 2.0)
        self.assertEqual(config.max_delay, 120.0)
        self.assertEqual(config.exponential_base, 1.5)
        self.assertFalse(config.jitter)

class TestSubmissionResult(unittest.TestCase):
    """Test cases for SubmissionResult dataclass"""
    
    def test_submission_result_creation(self):
        """Test SubmissionResult creation and attributes"""
        result = SubmissionResult(
            success=True,
            submission_id="test_123",
            guardian_document_id="doc_456",
            policy_id="policy_789",
            tag_name="renewable_energy",
            status=SubmissionStatus.VERIFIED,
            message="Test successful",
            retry_count=1,
            submitted_at=datetime.now()
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.submission_id, "test_123")
        self.assertEqual(result.guardian_document_id, "doc_456")
        self.assertEqual(result.policy_id, "policy_789")
        self.assertEqual(result.tag_name, "renewable_energy")
        self.assertEqual(result.status, SubmissionStatus.VERIFIED)
        self.assertEqual(result.message, "Test successful")
        self.assertEqual(result.retry_count, 1)
        self.assertIsNotNone(result.submitted_at)

class TestDocumentStatus(unittest.TestCase):
    """Test cases for DocumentStatus dataclass"""
    
    def test_document_status_creation(self):
        """Test DocumentStatus creation and attributes"""
        status = DocumentStatus(
            document_id="doc_123",
            policy_id="policy_456",
            status="VERIFIED",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            verification_status="APPROVED",
            error_message=None,
            metadata={"key": "value"}
        )
        
        self.assertEqual(status.document_id, "doc_123")
        self.assertEqual(status.policy_id, "policy_456")
        self.assertEqual(status.status, "VERIFIED")
        self.assertEqual(status.verification_status, "APPROVED")
        self.assertIsNone(status.error_message)
        self.assertEqual(status.metadata["key"], "value")

if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the tests
    unittest.main(verbosity=2)