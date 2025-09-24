#!/usr/bin/env python3
"""
Guardian Document Submission Service
Handles document submission to Guardian with status tracking, retry logic, and error handling
"""

import os
import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests

from guardian_auth import GuardianAuth, GuardianAuthError
from guardian_service import GuardianService, GuardianConfig
from energy_data_aggregator import AggregatedEnergyReport

logger = logging.getLogger(__name__)

class SubmissionStatus(Enum):
    """Guardian document submission status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    VERIFIED = "verified"
    FAILED = "failed"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class SubmissionResult:
    """Result of Guardian document submission"""
    success: bool
    submission_id: Optional[str] = None
    guardian_document_id: Optional[str] = None
    policy_id: Optional[str] = None
    tag_name: Optional[str] = None
    status: SubmissionStatus = SubmissionStatus.PENDING
    message: str = ""
    error_code: Optional[str] = None
    retry_count: int = 0
    submitted_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None

@dataclass
class DocumentStatus:
    """Guardian document status information"""
    document_id: str
    policy_id: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    verification_status: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

class GuardianDocumentSubmitter:
    """
    Guardian document submission service with retry logic and status tracking
    Implements requirements 1.3, 1.4, 3.5, 5.4
    """
    
    def __init__(self, guardian_service: GuardianService = None, retry_config: RetryConfig = None):
        """Initialize the document submitter"""
        self.guardian_service = guardian_service or GuardianService()
        self.retry_config = retry_config or RetryConfig()
        
        # Track active submissions
        self._active_submissions: Dict[str, SubmissionResult] = {}
        
        logger.info("🚀 GuardianDocumentSubmitter initialized")
    
    def submit_energy_report(self, report: AggregatedEnergyReport, policy_id: str, 
                           tag_name: str = "renewable_energy") -> SubmissionResult:
        """
        Submit energy production report to Guardian using POST /policies/{policyId}/tag/{tagName}/blocks
        Requirement 1.3: Submit energy data to Guardian for carbon credit generation
        """
        if not report:
            return SubmissionResult(
                success=False,
                error_code="INVALID_INPUT",
                message="Energy report is required for submission"
            )
        
        if not policy_id or not policy_id.strip():
            return SubmissionResult(
                success=False,
                error_code="INVALID_POLICY",
                message="Policy ID is required for Guardian submission"
            )
        
        if not tag_name or not tag_name.strip():
            return SubmissionResult(
                success=False,
                error_code="INVALID_TAG",
                message="Tag name is required for Guardian submission"
            )
        
        # Generate unique submission ID with more precision to avoid collisions
        import uuid
        submission_id = f"{report.device_id}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"📤 Starting Guardian submission for device {report.device_id} to policy {policy_id}")
        
        # Convert report to Guardian-compatible format
        guardian_data = self._format_report_for_guardian(report)
        
        # Attempt submission with retry logic
        result = self._submit_with_retry(
            submission_id=submission_id,
            policy_id=policy_id,
            tag_name=tag_name,
            data=guardian_data,
            report=report
        )
        
        # Track the submission
        self._active_submissions[submission_id] = result
        
        if result.success:
            logger.info(f"✅ Guardian submission successful: {result.guardian_document_id}")
        else:
            logger.error(f"❌ Guardian submission failed: {result.message}")
        
        return result
    
    def get_document_status(self, document_id: str, policy_id: str = None) -> Optional[DocumentStatus]:
        """
        Get Guardian document status using GET /policies/{policyId}/documents
        Requirement 1.4: Track Guardian document status and verification progress
        """
        if not document_id or not document_id.strip():
            logger.error("Document ID is required to get status")
            return None
        
        try:
            # If policy_id is provided, use it directly
            if policy_id:
                return self._get_document_status_by_policy(document_id, policy_id)
            
            # Otherwise, search through active submissions to find the policy
            for submission_result in self._active_submissions.values():
                if submission_result.guardian_document_id == document_id and submission_result.policy_id:
                    return self._get_document_status_by_policy(document_id, submission_result.policy_id)
            
            # If not found in active submissions, we need policy_id to proceed
            logger.warning(f"Cannot get status for document {document_id}: policy_id required")
            return None
            
        except Exception as e:
            logger.error(f"Error getting document status for {document_id}: {e}")
            return None
    
    def track_submission_progress(self, submission_id: str) -> Optional[SubmissionResult]:
        """
        Track the progress of a Guardian submission
        Updates status by checking Guardian API
        """
        if submission_id not in self._active_submissions:
            logger.warning(f"Submission {submission_id} not found in active submissions")
            return None
        
        submission = self._active_submissions[submission_id]
        
        if not submission.guardian_document_id or not submission.policy_id:
            logger.warning(f"Submission {submission_id} missing document or policy ID")
            return submission
        
        try:
            # Get current document status from Guardian
            doc_status = self.get_document_status(submission.guardian_document_id, submission.policy_id)
            
            if doc_status:
                # Update submission status based on Guardian response
                old_status = submission.status
                submission.status = self._map_guardian_status(doc_status.status)
                
                if submission.status != old_status:
                    logger.info(f"📊 Submission {submission_id} status changed: {old_status.value} → {submission.status.value}")
                
                # Update metadata
                if doc_status.metadata:
                    if not submission.response_data:
                        submission.response_data = {}
                    submission.response_data.update(doc_status.metadata)
            
            return submission
            
        except Exception as e:
            logger.error(f"Error tracking submission progress for {submission_id}: {e}")
            return submission
    
    def handle_submission_errors(self, error: Exception, submission_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Guardian API submission errors and determine retry actions
        Requirement 3.5: Implement error handling for Guardian API failures
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "retry_recommended": False,
            "retry_delay": 0,
            "permanent_failure": False
        }
        
        if isinstance(error, GuardianAuthError):
            # Authentication errors - retry with re-authentication
            error_info.update({
                "error_code": "AUTH_ERROR",
                "retry_recommended": True,
                "retry_delay": 5,  # Short delay for auth retry
                "action": "re_authenticate"
            })
            
        elif isinstance(error, requests.exceptions.ConnectionError):
            # Connection errors - retry with exponential backoff
            error_info.update({
                "error_code": "CONNECTION_ERROR",
                "retry_recommended": True,
                "retry_delay": min(self.retry_config.base_delay * (2 ** submission_context.get("retry_count", 0)), 
                                 self.retry_config.max_delay),
                "action": "retry_with_backoff"
            })
            
        elif isinstance(error, requests.exceptions.Timeout):
            # Timeout errors - retry with longer delay
            error_info.update({
                "error_code": "TIMEOUT_ERROR",
                "retry_recommended": True,
                "retry_delay": min(30, self.retry_config.max_delay),
                "action": "retry_with_delay"
            })
            
        elif isinstance(error, requests.exceptions.HTTPError):
            # HTTP errors - analyze status code
            status_code = getattr(error.response, 'status_code', 0) if hasattr(error, 'response') else 0
            
            if status_code == 400:
                # Bad request - permanent failure, don't retry
                error_info.update({
                    "error_code": "BAD_REQUEST",
                    "permanent_failure": True,
                    "action": "fix_data_format"
                })
            elif status_code == 401:
                # Unauthorized - retry with re-authentication
                error_info.update({
                    "error_code": "UNAUTHORIZED",
                    "retry_recommended": True,
                    "retry_delay": 5,
                    "action": "re_authenticate"
                })
            elif status_code == 403:
                # Forbidden - permanent failure
                error_info.update({
                    "error_code": "FORBIDDEN",
                    "permanent_failure": True,
                    "action": "check_permissions"
                })
            elif status_code == 404:
                # Not found - permanent failure
                error_info.update({
                    "error_code": "NOT_FOUND",
                    "permanent_failure": True,
                    "action": "verify_policy_and_tag"
                })
            elif status_code >= 500:
                # Server errors - retry
                error_info.update({
                    "error_code": "SERVER_ERROR",
                    "retry_recommended": True,
                    "retry_delay": min(60, self.retry_config.max_delay),
                    "action": "retry_later"
                })
            else:
                # Other HTTP errors
                error_info.update({
                    "error_code": f"HTTP_{status_code}",
                    "retry_recommended": status_code < 500,
                    "retry_delay": 30
                })
        
        else:
            # Unknown errors - conservative retry
            error_info.update({
                "error_code": "UNKNOWN_ERROR",
                "retry_recommended": True,
                "retry_delay": 30,
                "action": "retry_with_caution"
            })
        
        logger.warning(f"🔧 Error analysis: {error_info}")
        return error_info
    
    def get_submission_history(self, device_id: str = None, limit: int = 50) -> List[SubmissionResult]:
        """Get submission history, optionally filtered by device"""
        submissions = list(self._active_submissions.values())
        
        if device_id:
            # Filter by device_id if available in response_data
            submissions = [
                s for s in submissions 
                if s.response_data and s.response_data.get('guardian_data', {}).get('device_id') == device_id
            ]
        
        # Sort by submission time (most recent first)
        submissions.sort(key=lambda x: x.submitted_at or datetime.min, reverse=True)
        
        return submissions[:limit]
    
    def retry_failed_submission(self, submission_id: str) -> SubmissionResult:
        """Retry a failed Guardian submission"""
        if submission_id not in self._active_submissions:
            return SubmissionResult(
                success=False,
                error_code="SUBMISSION_NOT_FOUND",
                message=f"Submission {submission_id} not found"
            )
        
        original_submission = self._active_submissions[submission_id]
        
        if original_submission.status not in [SubmissionStatus.FAILED, SubmissionStatus.REJECTED]:
            return SubmissionResult(
                success=False,
                error_code="INVALID_STATUS",
                message=f"Cannot retry submission with status {original_submission.status.value}"
            )
        
        # Extract original submission data
        if not original_submission.response_data:
            return SubmissionResult(
                success=False,
                error_code="MISSING_DATA",
                message="Original submission data not available for retry"
            )
        
        # Create new submission with incremented retry count
        new_submission_id = f"{submission_id}_retry_{original_submission.retry_count + 1}"
        
        logger.info(f"🔄 Retrying failed submission {submission_id} as {new_submission_id}")
        
        # Attempt resubmission
        result = self._submit_with_retry(
            submission_id=new_submission_id,
            policy_id=original_submission.policy_id,
            tag_name=original_submission.tag_name,
            data=original_submission.response_data.get('guardian_data', {}),
            report=None,  # We don't have the original report
            base_retry_count=original_submission.retry_count + 1  # Increment base retry count
        )
        
        # Track the new submission
        self._active_submissions[new_submission_id] = result
        
        return result
    
    # Private helper methods
    
    def _submit_with_retry(self, submission_id: str, policy_id: str, tag_name: str, 
                          data: Dict[str, Any], report: AggregatedEnergyReport = None,
                          base_retry_count: int = 0) -> SubmissionResult:
        """Submit data to Guardian with exponential backoff retry logic"""
        retry_count = base_retry_count
        last_error = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                logger.info(f"🔄 Guardian submission attempt {attempt + 1}/{self.retry_config.max_retries + 1}")
                
                # Make the actual Guardian API call
                response = self.guardian_service.submit_energy_report(
                    report=self._create_legacy_energy_report(data, report) if report else None,
                    policy_id=policy_id,
                    tag_name=tag_name
                )
                
                if response.get("success"):
                    return SubmissionResult(
                        success=True,
                        submission_id=submission_id,
                        guardian_document_id=response.get("guardian_document_id"),
                        policy_id=policy_id,
                        tag_name=tag_name,
                        status=SubmissionStatus.SUBMITTED,
                        message=response.get("message", "Submission successful"),
                        retry_count=retry_count,
                        submitted_at=datetime.now(),
                        response_data={
                            "guardian_data": data,
                            "guardian_response": response
                        }
                    )
                else:
                    # Guardian API returned error
                    error_msg = response.get("message", "Unknown Guardian error")
                    last_error = Exception(error_msg)
                    
                    # Check if this is a permanent failure
                    if response.get("error") in ["Bad request", "Not found", "Access forbidden"]:
                        break  # Don't retry permanent failures
                    
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ Submission attempt {attempt + 1} failed: {e}")
            
            # Don't sleep after the last attempt
            if attempt < self.retry_config.max_retries:
                # Calculate delay with exponential backoff
                delay = min(
                    self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
                    self.retry_config.max_delay
                )
                
                # Add jitter to prevent thundering herd
                if self.retry_config.jitter:
                    import random
                    delay *= (0.5 + random.random() * 0.5)
                
                logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                time.sleep(delay)
                retry_count += 1
        
        # All retries failed
        error_info = self.handle_submission_errors(last_error, {"retry_count": retry_count})
        
        return SubmissionResult(
            success=False,
            submission_id=submission_id,
            policy_id=policy_id,
            tag_name=tag_name,
            status=SubmissionStatus.FAILED,
            message=f"Submission failed after {retry_count + 1} attempts: {str(last_error)}",
            error_code=error_info.get("error_code", "UNKNOWN_ERROR"),
            retry_count=retry_count,
            response_data={
                "guardian_data": data,
                "error_info": error_info,
                "last_error": str(last_error)
            }
        )
    
    def _format_report_for_guardian(self, report: AggregatedEnergyReport) -> Dict[str, Any]:
        """Convert AggregatedEnergyReport to Guardian-compatible format"""
        return {
            "type": "renewable_energy_production",
            "device_id": report.device_id,
            "reporting_period": {
                "start": report.period_start.isoformat(),
                "end": report.period_end.isoformat(),
                "duration_hours": (report.period_end - report.period_start).total_seconds() / 3600
            },
            "energy_production": {
                "total_kwh": report.energy_metrics.total_energy_kwh,
                "average_power_w": report.energy_metrics.avg_power_w,
                "peak_power_w": report.energy_metrics.max_power_w,
                "capacity_factor": report.energy_metrics.capacity_factor
            },
            "performance_metrics": {
                "average_efficiency": report.performance_metrics.avg_efficiency,
                "max_efficiency": report.performance_metrics.max_efficiency,
                "average_power_factor": report.performance_metrics.avg_power_factor,
                "grid_frequency_hz": report.performance_metrics.avg_grid_frequency
            },
            "environmental_conditions": {
                "average_irradiance_w_m2": report.environmental_metrics.avg_irradiance_w_m2,
                "peak_irradiance_w_m2": report.environmental_metrics.max_irradiance_w_m2,
                "average_temperature_c": report.environmental_metrics.avg_temperature_c,
                "temperature_range": {
                    "min": report.environmental_metrics.min_temperature_c,
                    "max": report.environmental_metrics.max_temperature_c
                }
            },
            "data_quality": {
                "total_readings": report.data_quality.total_readings,
                "valid_readings": report.data_quality.valid_readings,
                "data_completeness_percent": report.data_quality.data_completeness_percent,
                "integrity_score": report.data_integrity_score,
                "verification_hash": report.verification_hash
            },
            "regional_compliance": {
                "grid_voltage_nominal": report.grid_voltage_nominal,
                "grid_frequency_nominal": report.grid_frequency_nominal,
                "compliance_parameters": report.regional_compliance
            },
            "timestamp": datetime.now().isoformat(),
            "source": "VerifiedCC_ESP32_Network",
            "version": "1.0"
        }
    
    def _get_document_status_by_policy(self, document_id: str, policy_id: str) -> Optional[DocumentStatus]:
        """Get document status from Guardian using policy ID"""
        try:
            # Get all documents for the policy
            documents = self.guardian_service.get_policy_documents(policy_id, include_document=False)
            
            # Find the specific document
            for doc in documents:
                doc_id = doc.get('id') or doc.get('uuid') or doc.get('blockId')
                if doc_id == document_id:
                    return DocumentStatus(
                        document_id=document_id,
                        policy_id=policy_id,
                        status=doc.get('status', 'unknown'),
                        created_at=self._parse_datetime(doc.get('createDate')),
                        updated_at=self._parse_datetime(doc.get('updateDate')),
                        verification_status=doc.get('verificationStatus'),
                        error_message=doc.get('errorMessage'),
                        metadata=doc
                    )
            
            logger.warning(f"Document {document_id} not found in policy {policy_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting document status: {e}")
            return None
    
    def _map_guardian_status(self, guardian_status: str) -> SubmissionStatus:
        """Map Guardian document status to internal submission status"""
        status_mapping = {
            "NEW": SubmissionStatus.SUBMITTED,
            "PENDING": SubmissionStatus.PROCESSING,
            "IN_PROGRESS": SubmissionStatus.PROCESSING,
            "PROCESSING": SubmissionStatus.PROCESSING,
            "VERIFIED": SubmissionStatus.VERIFIED,
            "APPROVED": SubmissionStatus.VERIFIED,
            "REJECTED": SubmissionStatus.REJECTED,
            "FAILED": SubmissionStatus.FAILED,
            "ERROR": SubmissionStatus.FAILED,
            "EXPIRED": SubmissionStatus.EXPIRED
        }
        
        return status_mapping.get(guardian_status.upper(), SubmissionStatus.PENDING)
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Parse datetime string from Guardian API"""
        if not date_str:
            return None
        
        try:
            # Try different datetime formats
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, try ISO format parsing
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
        except Exception:
            logger.warning(f"Could not parse datetime: {date_str}")
            return None
    
    def _create_legacy_energy_report(self, data: Dict[str, Any], report: AggregatedEnergyReport = None):
        """Create legacy EnergyReport object for compatibility with existing guardian_service"""
        from guardian_service import EnergyReport
        
        if report:
            # Use the actual report data
            return EnergyReport(
                device_id=report.device_id,
                period_start=report.period_start,
                period_end=report.period_end,
                total_energy_kwh=report.energy_metrics.total_energy_kwh,
                avg_power_w=report.energy_metrics.avg_power_w,
                max_power_w=report.energy_metrics.max_power_w,
                avg_efficiency=report.performance_metrics.avg_efficiency,
                avg_irradiance=report.environmental_metrics.avg_irradiance_w_m2,
                avg_temperature=report.environmental_metrics.avg_temperature_c,
                data_points=report.data_quality.total_readings,
                verification_hash=report.verification_hash
            )
        else:
            # Create from data dictionary (for retries)
            return EnergyReport(
                device_id=data.get('device_id', 'unknown'),
                period_start=datetime.fromisoformat(data.get('reporting_period', {}).get('start', datetime.now().isoformat())),
                period_end=datetime.fromisoformat(data.get('reporting_period', {}).get('end', datetime.now().isoformat())),
                total_energy_kwh=data.get('energy_production', {}).get('total_kwh', 0),
                avg_power_w=data.get('energy_production', {}).get('average_power_w', 0),
                max_power_w=data.get('energy_production', {}).get('peak_power_w', 0),
                avg_efficiency=data.get('performance_metrics', {}).get('average_efficiency', 0.96),
                avg_irradiance=data.get('environmental_conditions', {}).get('average_irradiance_w_m2', 0),
                avg_temperature=data.get('environmental_conditions', {}).get('average_temperature_c', 25),
                data_points=data.get('data_quality', {}).get('total_readings', 0),
                verification_hash=data.get('data_quality', {}).get('verification_hash', '')
            )

# Example usage and testing
if __name__ == "__main__":
    # Test the document submitter
    try:
        from energy_data_aggregator import EnergyDataAggregator
        
        print("🔍 Testing GuardianDocumentSubmitter...")
        
        # Initialize services
        submitter = GuardianDocumentSubmitter()
        aggregator = EnergyDataAggregator()
        
        # Test with sample data (you'll need actual device data)
        test_device_id = "ESP32_001"
        test_policy_id = "test_policy_id"
        
        print(f"📊 Aggregating test data for device {test_device_id}...")
        
        # This would normally use real data
        # report = aggregator.aggregate_daily_data(test_device_id)
        # result = submitter.submit_energy_report(report, test_policy_id)
        
        print("✅ GuardianDocumentSubmitter test setup complete")
        print("💡 Use with real device data and Guardian policy ID for actual testing")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        print("💡 Ensure Guardian is running and environment variables are set")