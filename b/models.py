"""
Database models for VerifiedCC Guardian integration
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GuardianSubmissionStatus(str, Enum):
    """Guardian submission status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class GuardianSubmission(BaseModel):
    """Guardian submission database model"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Submission details
    device_id: str = Field(..., description="ESP32 device identifier")
    policy_id: str = Field(..., description="Guardian policy ID")
    guardian_document_id: Optional[str] = Field(None, description="Guardian-assigned document ID")
    
    # Status tracking
    status: GuardianSubmissionStatus = Field(default=GuardianSubmissionStatus.PENDING)
    submitted_at: Optional[datetime] = Field(None, description="Timestamp when submitted to Guardian")
    verified_at: Optional[datetime] = Field(None, description="Timestamp when verification completed")
    error_message: Optional[str] = Field(None, description="Error message if submission failed")
    
    # Energy data reference
    period_start: datetime = Field(..., description="Start of energy data period")
    period_end: datetime = Field(..., description="End of energy data period")
    total_energy_kwh: float = Field(..., description="Total energy in kWh for the period")
    data_points_count: int = Field(..., description="Number of sensor readings included")
    verification_hash: str = Field(..., description="Cryptographic hash of energy data")
    
    # Guardian response data
    guardian_response: Optional[Dict[str, Any]] = Field(None, description="Full Guardian API response")
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class GuardianSubmissionCreate(BaseModel):
    """Model for creating new Guardian submissions"""
    device_id: str
    policy_id: str
    period_start: datetime
    period_end: datetime
    total_energy_kwh: float
    data_points_count: int
    verification_hash: str
    guardian_response: Optional[Dict[str, Any]] = None


class GuardianSubmissionUpdate(BaseModel):
    """Model for updating Guardian submissions"""
    guardian_document_id: Optional[str] = None
    status: Optional[GuardianSubmissionStatus] = None
    submitted_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    error_message: Optional[str] = None
    guardian_response: Optional[Dict[str, Any]] = None


class GuardianSubmissionQuery(BaseModel):
    """Model for querying Guardian submissions"""
    device_id: Optional[str] = None
    policy_id: Optional[str] = None
    status: Optional[GuardianSubmissionStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class GuardianSubmissionStats(BaseModel):
    """Statistics for Guardian submissions"""
    total_submissions: int
    pending_submissions: int
    processing_submissions: int
    verified_submissions: int
    failed_submissions: int
    total_energy_kwh: float
    success_rate: float
    avg_processing_time_hours: Optional[float] = None


class DeviceSubmissionSummary(BaseModel):
    """Summary of Guardian submissions for a specific device"""
    device_id: str
    total_submissions: int
    verified_submissions: int
    failed_submissions: int
    total_verified_energy_kwh: float
    last_submission_date: Optional[datetime] = None
    last_verification_date: Optional[datetime] = None
    success_rate: float