"""
Database service for Guardian submissions
Handles CRUD operations for guardian_submissions table
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from supabase import Client
from models import (
    GuardianSubmission, 
    GuardianSubmissionCreate, 
    GuardianSubmissionUpdate,
    GuardianSubmissionQuery,
    GuardianSubmissionStats,
    DeviceSubmissionSummary,
    GuardianSubmissionStatus
)

logger = logging.getLogger(__name__)


class GuardianSubmissionsDB:
    """Database service for Guardian submissions"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = "guardian_submissions"
    
    async def create_submission(self, submission_data: GuardianSubmissionCreate) -> GuardianSubmission:
        """Create a new Guardian submission record"""
        try:
            # Validate that device_id exists in sensor_readings
            device_check = self.supabase.table("sensor_readings")\
                .select("device_id")\
                .eq("device_id", submission_data.device_id)\
                .limit(1)\
                .execute()
            
            if not device_check.data:
                raise ValueError(f"Device {submission_data.device_id} not found in sensor_readings")
            
            # Prepare data for insertion
            insert_data = {
                "device_id": submission_data.device_id,
                "policy_id": submission_data.policy_id,
                "period_start": submission_data.period_start.isoformat(),
                "period_end": submission_data.period_end.isoformat(),
                "total_energy_kwh": submission_data.total_energy_kwh,
                "data_points_count": submission_data.data_points_count,
                "verification_hash": submission_data.verification_hash,
                "guardian_response": submission_data.guardian_response,
                "status": GuardianSubmissionStatus.PENDING.value
            }
            
            result = self.supabase.table(self.table_name).insert(insert_data).execute()
            
            if not result.data:
                raise ValueError("Failed to create Guardian submission record")
            
            created_record = result.data[0]
            logger.info(f"✅ Created Guardian submission record: {created_record['id']}")
            
            return GuardianSubmission(**created_record)
            
        except Exception as e:
            logger.error(f"❌ Failed to create Guardian submission: {e}")
            raise
    
    async def update_submission(self, submission_id: int, update_data: GuardianSubmissionUpdate) -> GuardianSubmission:
        """Update an existing Guardian submission record"""
        try:
            # Prepare update data (only include non-None values)
            update_dict = {}
            
            if update_data.guardian_document_id is not None:
                update_dict["guardian_document_id"] = update_data.guardian_document_id
            
            if update_data.status is not None:
                update_dict["status"] = update_data.status.value
            
            if update_data.submitted_at is not None:
                update_dict["submitted_at"] = update_data.submitted_at.isoformat()
            
            if update_data.verified_at is not None:
                update_dict["verified_at"] = update_data.verified_at.isoformat()
            
            if update_data.error_message is not None:
                update_dict["error_message"] = update_data.error_message
            
            if update_data.guardian_response is not None:
                update_dict["guardian_response"] = update_data.guardian_response
            
            if not update_dict:
                raise ValueError("No update data provided")
            
            result = self.supabase.table(self.table_name)\
                .update(update_dict)\
                .eq("id", submission_id)\
                .execute()
            
            if not result.data:
                raise ValueError(f"Guardian submission {submission_id} not found")
            
            updated_record = result.data[0]
            logger.info(f"✅ Updated Guardian submission {submission_id}: status={updated_record.get('status')}")
            
            return GuardianSubmission(**updated_record)
            
        except Exception as e:
            logger.error(f"❌ Failed to update Guardian submission {submission_id}: {e}")
            raise
    
    async def get_submission(self, submission_id: int) -> Optional[GuardianSubmission]:
        """Get a Guardian submission by ID"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("id", submission_id)\
                .execute()
            
            if not result.data:
                return None
            
            return GuardianSubmission(**result.data[0])
            
        except Exception as e:
            logger.error(f"❌ Failed to get Guardian submission {submission_id}: {e}")
            raise
    
    async def get_submission_by_document_id(self, guardian_document_id: str) -> Optional[GuardianSubmission]:
        """Get a Guardian submission by Guardian document ID"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("guardian_document_id", guardian_document_id)\
                .execute()
            
            if not result.data:
                return None
            
            return GuardianSubmission(**result.data[0])
            
        except Exception as e:
            logger.error(f"❌ Failed to get Guardian submission by document ID {guardian_document_id}: {e}")
            raise
    
    async def query_submissions(self, query: GuardianSubmissionQuery) -> List[GuardianSubmission]:
        """Query Guardian submissions with filters"""
        try:
            # Build query
            supabase_query = self.supabase.table(self.table_name).select("*")
            
            # Apply filters
            if query.device_id:
                supabase_query = supabase_query.eq("device_id", query.device_id)
            
            if query.policy_id:
                supabase_query = supabase_query.eq("policy_id", query.policy_id)
            
            if query.status:
                supabase_query = supabase_query.eq("status", query.status.value)
            
            if query.start_date:
                supabase_query = supabase_query.gte("created_at", query.start_date.isoformat())
            
            if query.end_date:
                supabase_query = supabase_query.lte("created_at", query.end_date.isoformat())
            
            # Apply ordering, limit, and offset
            supabase_query = supabase_query\
                .order("created_at", desc=True)\
                .range(query.offset, query.offset + query.limit - 1)
            
            result = supabase_query.execute()
            
            return [GuardianSubmission(**record) for record in result.data or []]
            
        except Exception as e:
            logger.error(f"❌ Failed to query Guardian submissions: {e}")
            raise
    
    async def get_device_submissions(self, device_id: str, limit: int = 50) -> List[GuardianSubmission]:
        """Get Guardian submissions for a specific device"""
        query = GuardianSubmissionQuery(device_id=device_id, limit=limit)
        return await self.query_submissions(query)
    
    async def get_pending_submissions(self, limit: int = 100) -> List[GuardianSubmission]:
        """Get all pending Guardian submissions"""
        query = GuardianSubmissionQuery(status=GuardianSubmissionStatus.PENDING, limit=limit)
        return await self.query_submissions(query)
    
    async def get_processing_submissions(self, limit: int = 100) -> List[GuardianSubmission]:
        """Get all processing Guardian submissions"""
        query = GuardianSubmissionQuery(status=GuardianSubmissionStatus.PROCESSING, limit=limit)
        return await self.query_submissions(query)
    
    async def get_submission_stats(self, device_id: Optional[str] = None) -> GuardianSubmissionStats:
        """Get Guardian submission statistics"""
        try:
            # Build base query
            base_query = self.supabase.table(self.table_name).select("*")
            
            if device_id:
                base_query = base_query.eq("device_id", device_id)
            
            result = base_query.execute()
            submissions = result.data or []
            
            if not submissions:
                return GuardianSubmissionStats(
                    total_submissions=0,
                    pending_submissions=0,
                    processing_submissions=0,
                    verified_submissions=0,
                    failed_submissions=0,
                    total_energy_kwh=0.0,
                    success_rate=0.0
                )
            
            # Calculate statistics
            total_submissions = len(submissions)
            pending_count = sum(1 for s in submissions if s["status"] == "PENDING")
            processing_count = sum(1 for s in submissions if s["status"] == "PROCESSING")
            verified_count = sum(1 for s in submissions if s["status"] == "VERIFIED")
            failed_count = sum(1 for s in submissions if s["status"] == "FAILED")
            
            total_energy = sum(s["total_energy_kwh"] or 0.0 for s in submissions)
            success_rate = (verified_count / total_submissions * 100) if total_submissions > 0 else 0.0
            
            # Calculate average processing time for verified submissions
            avg_processing_time = None
            verified_submissions = [s for s in submissions if s["status"] == "VERIFIED" and s["submitted_at"] and s["verified_at"]]
            
            if verified_submissions:
                processing_times = []
                for s in verified_submissions:
                    submitted = datetime.fromisoformat(s["submitted_at"].replace('Z', '+00:00'))
                    verified = datetime.fromisoformat(s["verified_at"].replace('Z', '+00:00'))
                    processing_times.append((verified - submitted).total_seconds() / 3600)  # Convert to hours
                
                avg_processing_time = sum(processing_times) / len(processing_times)
            
            return GuardianSubmissionStats(
                total_submissions=total_submissions,
                pending_submissions=pending_count,
                processing_submissions=processing_count,
                verified_submissions=verified_count,
                failed_submissions=failed_count,
                total_energy_kwh=total_energy,
                success_rate=success_rate,
                avg_processing_time_hours=avg_processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get Guardian submission stats: {e}")
            raise
    
    async def get_device_summary(self, device_id: str) -> DeviceSubmissionSummary:
        """Get submission summary for a specific device"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("device_id", device_id)\
                .order("created_at", desc=True)\
                .execute()
            
            submissions = result.data or []
            
            if not submissions:
                return DeviceSubmissionSummary(
                    device_id=device_id,
                    total_submissions=0,
                    verified_submissions=0,
                    failed_submissions=0,
                    total_verified_energy_kwh=0.0,
                    success_rate=0.0
                )
            
            total_submissions = len(submissions)
            verified_submissions = [s for s in submissions if s["status"] == "VERIFIED"]
            failed_submissions = [s for s in submissions if s["status"] == "FAILED"]
            
            verified_count = len(verified_submissions)
            failed_count = len(failed_submissions)
            
            total_verified_energy = sum(s["total_energy_kwh"] or 0.0 for s in verified_submissions)
            success_rate = (verified_count / total_submissions * 100) if total_submissions > 0 else 0.0
            
            # Get latest dates
            last_submission_date = None
            last_verification_date = None
            
            if submissions:
                last_submission_date = datetime.fromisoformat(submissions[0]["created_at"].replace('Z', '+00:00'))
            
            if verified_submissions:
                latest_verified = max(verified_submissions, key=lambda x: x["verified_at"] or "")
                if latest_verified["verified_at"]:
                    last_verification_date = datetime.fromisoformat(latest_verified["verified_at"].replace('Z', '+00:00'))
            
            return DeviceSubmissionSummary(
                device_id=device_id,
                total_submissions=total_submissions,
                verified_submissions=verified_count,
                failed_submissions=failed_count,
                total_verified_energy_kwh=total_verified_energy,
                last_submission_date=last_submission_date,
                last_verification_date=last_verification_date,
                success_rate=success_rate
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get device submission summary for {device_id}: {e}")
            raise
    
    async def delete_submission(self, submission_id: int) -> bool:
        """Delete a Guardian submission record"""
        try:
            result = self.supabase.table(self.table_name)\
                .delete()\
                .eq("id", submission_id)\
                .execute()
            
            success = bool(result.data)
            if success:
                logger.info(f"✅ Deleted Guardian submission {submission_id}")
            else:
                logger.warning(f"⚠️ Guardian submission {submission_id} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to delete Guardian submission {submission_id}: {e}")
            raise
    
    async def cleanup_old_submissions(self, days_old: int = 90) -> int:
        """Clean up old Guardian submissions (older than specified days)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            result = self.supabase.table(self.table_name)\
                .delete()\
                .lt("created_at", cutoff_date.isoformat())\
                .execute()
            
            deleted_count = len(result.data or [])
            logger.info(f"✅ Cleaned up {deleted_count} old Guardian submissions (older than {days_old} days)")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old Guardian submissions: {e}")
            raise