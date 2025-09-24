#!/usr/bin/env python3
"""
Guardian Submission Scheduler
Implements automated Guardian submission workflow with background tasks,
daily energy data aggregation, submission queue, and retry mechanisms.
Requirements: 1.1, 1.2, 5.2, 5.4
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import json
from supabase import Client

from energy_data_aggregator import EnergyDataAggregator, AggregatedEnergyReport
from guardian_document_submitter import GuardianDocumentSubmitter, SubmissionResult, SubmissionStatus
from guardian_submissions_db import GuardianSubmissionsDB
from models import GuardianSubmissionCreate, GuardianSubmissionUpdate, GuardianSubmissionStatus

logger = logging.getLogger(__name__)

class SubmissionTrigger(Enum):
    """Triggers for Guardian submission"""
    DAILY_SCHEDULE = "daily_schedule"
    DATA_THRESHOLD = "data_threshold"
    MANUAL = "manual"
    RETRY = "retry"

@dataclass
class SubmissionConfig:
    """Configuration for automated Guardian submissions"""
    # Scheduling
    daily_submission_time: time = time(hour=1, minute=0)  # 1:00 AM daily
    submission_enabled: bool = True
    
    # Data requirements
    min_data_completeness: float = 80.0  # 80% data completeness required
    min_integrity_score: float = 0.7     # 70% data integrity required
    min_readings_per_day: int = 100      # Minimum readings per day
    min_energy_kwh: float = 0.1          # Minimum energy production
    
    # Guardian policy settings
    default_policy_id: Optional[str] = None
    policy_tag_name: str = "renewable_energy"
    
    # Retry configuration
    max_retry_attempts: int = 3
    retry_delay_hours: int = 2
    retry_exponential_backoff: bool = True
    
    # Queue management
    max_concurrent_submissions: int = 5
    submission_timeout_minutes: int = 30
    
    # Device filtering
    enabled_devices: Optional[Set[str]] = None  # None = all devices
    excluded_devices: Optional[Set[str]] = None

@dataclass
class QueuedSubmission:
    """Queued Guardian submission"""
    device_id: str
    target_date: datetime
    policy_id: str
    trigger: SubmissionTrigger
    priority: int = 0  # Higher number = higher priority
    created_at: datetime = None
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class GuardianSubmissionScheduler:
    """
    Automated Guardian submission scheduler with background tasks
    Implements requirements 1.1, 1.2, 5.2, 5.4
    """
    
    def __init__(self, 
                 supabase_client: Client,
                 config: SubmissionConfig = None):
        """Initialize the submission scheduler"""
        self.supabase = supabase_client
        self.config = config or SubmissionConfig()
        
        # Initialize services
        self.energy_aggregator = EnergyDataAggregator(supabase_client)
        self.document_submitter = GuardianDocumentSubmitter()
        self.submissions_db = GuardianSubmissionsDB(supabase_client)
        
        # Submission queue and tracking
        self.submission_queue: List[QueuedSubmission] = []
        self.active_submissions: Dict[str, QueuedSubmission] = {}
        self.processed_submissions: Set[str] = set()
        
        # Background task control
        self._scheduler_task: Optional[asyncio.Task] = None
        self._queue_processor_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info("🤖 GuardianSubmissionScheduler initialized")
    
    async def start(self):
        """Start the automated submission scheduler"""
        if self._running:
            logger.warning("⚠️ Scheduler is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._scheduler_task = asyncio.create_task(self._daily_scheduler_loop())
        self._queue_processor_task = asyncio.create_task(self._queue_processor_loop())
        
        logger.info("🚀 Guardian submission scheduler started")
        logger.info(f"📅 Daily submission time: {self.config.daily_submission_time}")
        logger.info(f"🔧 Max concurrent submissions: {self.config.max_concurrent_submissions}")
    
    async def stop(self):
        """Stop the automated submission scheduler"""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
            try:
                await self._queue_processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Guardian submission scheduler stopped") 
   
    async def queue_submission(self, 
                             device_id: str, 
                             target_date: datetime = None,
                             policy_id: str = None,
                             trigger: SubmissionTrigger = SubmissionTrigger.MANUAL,
                             priority: int = 0) -> bool:
        """
        Queue a Guardian submission for processing
        Requirement 1.2: Add automatic Guardian submission for completed daily periods
        """
        if not self.config.submission_enabled:
            logger.warning("⚠️ Guardian submissions are disabled")
            return False
        
        # Use current date if not specified
        if target_date is None:
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Use default policy if not specified
        if policy_id is None:
            policy_id = self.config.default_policy_id
        
        if not policy_id:
            logger.error(f"❌ No policy ID specified for {device_id} submission")
            return False
        
        # Check device filtering
        if not self._is_device_enabled(device_id):
            logger.info(f"📵 Device {device_id} is not enabled for submissions")
            return False
        
        # Create submission key for deduplication
        submission_key = f"{device_id}_{target_date.date()}_{policy_id}"
        
        # Check if already processed or queued
        if submission_key in self.processed_submissions:
            logger.info(f"✅ Submission already processed: {submission_key}")
            return True
        
        if submission_key in [f"{q.device_id}_{q.target_date.date()}_{q.policy_id}" for q in self.submission_queue]:
            logger.info(f"⏳ Submission already queued: {submission_key}")
            return True
        
        # Create queued submission
        queued_submission = QueuedSubmission(
            device_id=device_id,
            target_date=target_date,
            policy_id=policy_id,
            trigger=trigger,
            priority=priority
        )
        
        # Add to queue (sorted by priority)
        self.submission_queue.append(queued_submission)
        self.submission_queue.sort(key=lambda x: (-x.priority, x.created_at))
        
        logger.info(f"📋 Queued Guardian submission: {device_id} for {target_date.date()} (trigger: {trigger.value})")
        
        return True
    
    async def process_daily_submissions(self, target_date: datetime = None) -> Dict[str, Any]:
        """
        Process daily Guardian submissions for all eligible devices
        Requirement 1.1: Create background task for daily energy data aggregation
        """
        if target_date is None:
            # Process previous day's data (allow time for data collection to complete)
            target_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"📊 Processing daily Guardian submissions for {target_date.date()}")
        
        # Get active devices from recent sensor readings
        active_devices = await self._get_active_devices(target_date)
        
        results = {
            "target_date": target_date.isoformat(),
            "total_devices": len(active_devices),
            "queued_submissions": 0,
            "skipped_devices": 0,
            "errors": []
        }
        
        for device_id in active_devices:
            try:
                # Check if device meets submission criteria
                readiness = await self._check_submission_readiness(device_id, target_date)
                
                if readiness["ready"]:
                    # Queue submission
                    success = await self.queue_submission(
                        device_id=device_id,
                        target_date=target_date,
                        trigger=SubmissionTrigger.DAILY_SCHEDULE,
                        priority=1  # Daily submissions have priority
                    )
                    
                    if success:
                        results["queued_submissions"] += 1
                    else:
                        results["skipped_devices"] += 1
                        results["errors"].append(f"Failed to queue {device_id}")
                else:
                    results["skipped_devices"] += 1
                    logger.info(f"📵 Skipping {device_id}: {readiness['reason']}")
                    
            except Exception as e:
                results["errors"].append(f"Error processing {device_id}: {str(e)}")
                logger.error(f"❌ Error processing daily submission for {device_id}: {e}")
        
        logger.info(f"✅ Daily submission processing complete: {results['queued_submissions']} queued, {results['skipped_devices']} skipped")
        
        return results
    
    async def retry_failed_submissions(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Retry failed Guardian submissions within the specified age limit
        Requirement 5.4: Implement submission queue and retry mechanism for failed submissions
        """
        logger.info(f"🔄 Checking for failed submissions to retry (max age: {max_age_hours}h)")
        
        # Get failed submissions from database
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        try:
            # Query failed submissions
            from models import GuardianSubmissionQuery
            query = GuardianSubmissionQuery(
                status=GuardianSubmissionStatus.FAILED,
                start_date=cutoff_time,
                limit=100
            )
            
            failed_submissions = await self.submissions_db.query_submissions(query)
            
            results = {
                "total_failed": len(failed_submissions),
                "retry_queued": 0,
                "max_retries_reached": 0,
                "errors": []
            }
            
            for submission in failed_submissions:
                try:
                    # Check if max retries reached (estimate from error message or use default)
                    retry_count = self._extract_retry_count(submission.error_message) or 0
                    
                    if retry_count >= self.config.max_retry_attempts:
                        results["max_retries_reached"] += 1
                        continue
                    
                    # Queue retry with exponential backoff delay
                    delay_hours = self.config.retry_delay_hours
                    if self.config.retry_exponential_backoff:
                        delay_hours *= (2 ** retry_count)
                    
                    # Check if enough time has passed since last attempt
                    if submission.submitted_at:
                        time_since_attempt = datetime.now() - submission.submitted_at
                        if time_since_attempt.total_seconds() < delay_hours * 3600:
                            continue  # Too soon to retry
                    
                    # Queue retry
                    success = await self.queue_submission(
                        device_id=submission.device_id,
                        target_date=submission.period_start,
                        policy_id=submission.policy_id,
                        trigger=SubmissionTrigger.RETRY,
                        priority=2  # Retries have higher priority
                    )
                    
                    if success:
                        results["retry_queued"] += 1
                    else:
                        results["errors"].append(f"Failed to queue retry for {submission.device_id}")
                        
                except Exception as e:
                    results["errors"].append(f"Error processing retry for {submission.device_id}: {str(e)}")
                    logger.error(f"❌ Error processing retry for {submission.device_id}: {e}")
            
            logger.info(f"🔄 Retry processing complete: {results['retry_queued']} queued, {results['max_retries_reached']} max retries reached")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in retry_failed_submissions: {e}")
            return {"error": str(e)}
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current submission queue status"""
        return {
            "queue_length": len(self.submission_queue),
            "active_submissions": len(self.active_submissions),
            "processed_count": len(self.processed_submissions),
            "scheduler_running": self._running,
            "config": {
                "submission_enabled": self.config.submission_enabled,
                "daily_submission_time": self.config.daily_submission_time.isoformat(),
                "max_concurrent": self.config.max_concurrent_submissions,
                "default_policy_id": self.config.default_policy_id
            },
            "queue_items": [
                {
                    "device_id": q.device_id,
                    "target_date": q.target_date.date().isoformat(),
                    "policy_id": q.policy_id,
                    "trigger": q.trigger.value,
                    "priority": q.priority,
                    "retry_count": q.retry_count,
                    "created_at": q.created_at.isoformat()
                }
                for q in self.submission_queue[:10]  # Show first 10 items
            ]
        }
    
    # Private helper methods
    
    async def _daily_scheduler_loop(self):
        """Background task for daily submission scheduling"""
        logger.info("📅 Daily scheduler loop started")
        
        while self._running:
            try:
                now = datetime.now()
                target_time = now.replace(
                    hour=self.config.daily_submission_time.hour,
                    minute=self.config.daily_submission_time.minute,
                    second=0,
                    microsecond=0
                )
                
                # If target time has passed today, schedule for tomorrow
                if now >= target_time:
                    target_time += timedelta(days=1)
                
                # Calculate sleep time
                sleep_seconds = (target_time - now).total_seconds()
                
                logger.info(f"⏰ Next daily submission scheduled for {target_time}")
                
                # Sleep until target time (with periodic wake-ups to check if stopped)
                while sleep_seconds > 0 and self._running:
                    sleep_duration = min(sleep_seconds, 3600)  # Wake up at least every hour
                    await asyncio.sleep(sleep_duration)
                    sleep_seconds -= sleep_duration
                    
                    # Recalculate in case time changed
                    now = datetime.now()
                    sleep_seconds = (target_time - now).total_seconds()
                
                if self._running:
                    # Process daily submissions
                    await self.process_daily_submissions()
                    
                    # Also check for retries
                    await self.retry_failed_submissions()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in daily scheduler loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
        
        logger.info("📅 Daily scheduler loop stopped")
    
    async def _queue_processor_loop(self):
        """Background task for processing submission queue"""
        logger.info("🔄 Queue processor loop started")
        
        while self._running:
            try:
                # Process queue if there are items and capacity
                if (self.submission_queue and 
                    len(self.active_submissions) < self.config.max_concurrent_submissions):
                    
                    # Get next submission from queue
                    queued_submission = self.submission_queue.pop(0)
                    
                    # Start processing
                    task = asyncio.create_task(
                        self._process_queued_submission(queued_submission)
                    )
                    
                    # Track active submission
                    submission_key = f"{queued_submission.device_id}_{queued_submission.target_date.date()}_{queued_submission.policy_id}"
                    self.active_submissions[submission_key] = queued_submission
                    
                    # Don't await - let it run in background
                    task.add_done_callback(
                        lambda t, key=submission_key: self._on_submission_complete(key, t)
                    )
                
                # Sleep before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in queue processor loop: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds before retrying
        
        logger.info("🔄 Queue processor loop stopped")
    
    async def _process_queued_submission(self, queued_submission: QueuedSubmission) -> bool:
        """Process a single queued submission"""
        device_id = queued_submission.device_id
        target_date = queued_submission.target_date
        policy_id = queued_submission.policy_id
        
        logger.info(f"🚀 Processing Guardian submission: {device_id} for {target_date.date()}")
        
        try:
            # Update last attempt time
            queued_submission.last_attempt = datetime.now()
            
            # Aggregate energy data
            aggregated_report = self.energy_aggregator.aggregate_daily_data(device_id, target_date)
            
            # Validate data quality
            readiness = self.energy_aggregator.validate_guardian_readiness(device_id, target_date)
            
            if not readiness["guardian_ready"]:
                error_msg = f"Data quality insufficient: {readiness.get('message', 'Unknown issue')}"
                queued_submission.error_message = error_msg
                logger.warning(f"⚠️ {error_msg}")
                return False
            
            # Create database record
            submission_create = GuardianSubmissionCreate(
                device_id=device_id,
                policy_id=policy_id,
                period_start=aggregated_report.period_start,
                period_end=aggregated_report.period_end,
                total_energy_kwh=aggregated_report.energy_metrics.total_energy_kwh,
                data_points_count=aggregated_report.data_quality.valid_readings,
                verification_hash=aggregated_report.verification_hash,
                guardian_response=None
            )
            
            db_submission = await self.submissions_db.create_submission(submission_create)
            
            # Submit to Guardian
            submission_result = self.document_submitter.submit_energy_report(
                report=aggregated_report,
                policy_id=policy_id,
                tag_name=self.config.policy_tag_name
            )
            
            # Update database record with result
            if submission_result.success:
                update_data = GuardianSubmissionUpdate(
                    guardian_document_id=submission_result.guardian_document_id,
                    status=GuardianSubmissionStatus.PROCESSING,
                    submitted_at=datetime.now(),
                    guardian_response=submission_result.response_data
                )
                
                await self.submissions_db.update_submission(db_submission.id, update_data)
                
                logger.info(f"✅ Guardian submission successful: {device_id} -> {submission_result.guardian_document_id}")
                return True
            else:
                # Update with failure
                update_data = GuardianSubmissionUpdate(
                    status=GuardianSubmissionStatus.FAILED,
                    error_message=submission_result.message,
                    guardian_response=submission_result.response_data
                )
                
                await self.submissions_db.update_submission(db_submission.id, update_data)
                
                queued_submission.error_message = submission_result.message
                queued_submission.retry_count += 1
                
                logger.error(f"❌ Guardian submission failed: {device_id} - {submission_result.message}")
                return False
                
        except Exception as e:
            error_msg = f"Submission processing error: {str(e)}"
            queued_submission.error_message = error_msg
            queued_submission.retry_count += 1
            
            logger.error(f"❌ Error processing submission for {device_id}: {e}")
            return False
    
    def _on_submission_complete(self, submission_key: str, task: asyncio.Task):
        """Callback when submission processing completes"""
        try:
            # Remove from active submissions
            if submission_key in self.active_submissions:
                queued_submission = self.active_submissions.pop(submission_key)
                
                # Mark as processed
                self.processed_submissions.add(submission_key)
                
                # Get task result
                try:
                    success = task.result()
                    if success:
                        logger.info(f"✅ Submission completed successfully: {submission_key}")
                    else:
                        logger.warning(f"⚠️ Submission completed with issues: {submission_key}")
                        
                        # Re-queue for retry if not at max attempts
                        if queued_submission.retry_count < self.config.max_retry_attempts:
                            # Add back to queue with delay
                            queued_submission.priority = 2  # Higher priority for retries
                            self.submission_queue.append(queued_submission)
                            self.submission_queue.sort(key=lambda x: (-x.priority, x.created_at))
                            
                            # Remove from processed so it can be retried
                            self.processed_submissions.discard(submission_key)
                            
                            logger.info(f"🔄 Re-queued for retry: {submission_key} (attempt {queued_submission.retry_count + 1})")
                        
                except Exception as e:
                    logger.error(f"❌ Submission task failed: {submission_key} - {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error in submission completion callback: {e}")
    
    async def _get_active_devices(self, target_date: datetime) -> List[str]:
        """Get list of devices with data for the target date"""
        try:
            # Query devices with readings on target date
            start_time = target_date
            end_time = target_date + timedelta(days=1)
            
            result = self.supabase.table("sensor_readings")\
                .select("device_id")\
                .gte("timestamp", start_time.isoformat())\
                .lt("timestamp", end_time.isoformat())\
                .execute()
            
            if not result.data:
                return []
            
            # Get unique device IDs
            device_ids = list(set([r["device_id"] for r in result.data]))
            
            # Apply device filtering
            filtered_devices = [
                device_id for device_id in device_ids 
                if self._is_device_enabled(device_id)
            ]
            
            logger.info(f"📱 Found {len(filtered_devices)} active devices for {target_date.date()}")
            
            return filtered_devices
            
        except Exception as e:
            logger.error(f"❌ Error getting active devices: {e}")
            return []
    
    async def _check_submission_readiness(self, device_id: str, target_date: datetime) -> Dict[str, Any]:
        """Check if device data meets submission criteria"""
        try:
            # Use energy aggregator to validate readiness
            readiness = self.energy_aggregator.validate_guardian_readiness(device_id, target_date)
            
            # Additional checks based on config
            if readiness["guardian_ready"]:
                checks = readiness.get("checks", {})
                
                # Check against our config thresholds
                data_completeness = checks.get("data_completeness", {}).get("value", 0)
                data_integrity = checks.get("data_integrity", {}).get("value", 0)
                sufficient_readings = checks.get("sufficient_readings", {}).get("value", 0)
                energy_production = checks.get("energy_production", {}).get("value", 0)
                
                if data_completeness < self.config.min_data_completeness:
                    return {"ready": False, "reason": f"Data completeness {data_completeness:.1f}% < {self.config.min_data_completeness}%"}
                
                if data_integrity < self.config.min_integrity_score:
                    return {"ready": False, "reason": f"Data integrity {data_integrity:.2f} < {self.config.min_integrity_score}"}
                
                if sufficient_readings < self.config.min_readings_per_day:
                    return {"ready": False, "reason": f"Readings {sufficient_readings} < {self.config.min_readings_per_day}"}
                
                if energy_production < self.config.min_energy_kwh:
                    return {"ready": False, "reason": f"Energy {energy_production:.2f} kWh < {self.config.min_energy_kwh} kWh"}
                
                return {"ready": True, "reason": "All criteria met"}
            else:
                return {"ready": False, "reason": readiness.get("message", "Guardian readiness check failed")}
                
        except Exception as e:
            logger.error(f"❌ Error checking submission readiness for {device_id}: {e}")
            return {"ready": False, "reason": f"Error: {str(e)}"}
    
    def _is_device_enabled(self, device_id: str) -> bool:
        """Check if device is enabled for submissions"""
        # Check exclusion list first
        if self.config.excluded_devices and device_id in self.config.excluded_devices:
            return False
        
        # Check inclusion list (if specified)
        if self.config.enabled_devices:
            return device_id in self.config.enabled_devices
        
        # Default: all devices enabled
        return True
    
    def _extract_retry_count(self, error_message: str) -> Optional[int]:
        """Extract retry count from error message"""
        if not error_message:
            return None
        
        try:
            # Look for patterns like "attempt 3" or "retry 2"
            import re
            match = re.search(r'(?:attempt|retry)\s+(\d+)', error_message.lower())
            if match:
                return int(match.group(1))
        except:
            pass
        
        return None

# Configuration management functions

def load_submission_config(config_path: str = None) -> SubmissionConfig:
    """Load submission configuration from file or environment variables"""
    config = SubmissionConfig()
    
    # Load from environment variables
    if os.getenv("GUARDIAN_SUBMISSION_ENABLED"):
        config.submission_enabled = os.getenv("GUARDIAN_SUBMISSION_ENABLED").lower() == "true"
    
    if os.getenv("GUARDIAN_DAILY_SUBMISSION_TIME"):
        try:
            time_str = os.getenv("GUARDIAN_DAILY_SUBMISSION_TIME")
            hour, minute = map(int, time_str.split(":"))
            config.daily_submission_time = time(hour=hour, minute=minute)
        except:
            logger.warning("⚠️ Invalid GUARDIAN_DAILY_SUBMISSION_TIME format, using default")
    
    if os.getenv("GUARDIAN_DEFAULT_POLICY_ID"):
        config.default_policy_id = os.getenv("GUARDIAN_DEFAULT_POLICY_ID")
    
    if os.getenv("GUARDIAN_MIN_DATA_COMPLETENESS"):
        try:
            config.min_data_completeness = float(os.getenv("GUARDIAN_MIN_DATA_COMPLETENESS"))
        except:
            logger.warning("⚠️ Invalid GUARDIAN_MIN_DATA_COMPLETENESS, using default")
    
    if os.getenv("GUARDIAN_MAX_CONCURRENT_SUBMISSIONS"):
        try:
            config.max_concurrent_submissions = int(os.getenv("GUARDIAN_MAX_CONCURRENT_SUBMISSIONS"))
        except:
            logger.warning("⚠️ Invalid GUARDIAN_MAX_CONCURRENT_SUBMISSIONS, using default")
    
    # Load from config file if specified
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Update config with file data
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
        except Exception as e:
            logger.error(f"❌ Error loading config file {config_path}: {e}")
    
    return config

def save_submission_config(config: SubmissionConfig, config_path: str):
    """Save submission configuration to file"""
    try:
        config_dict = asdict(config)
        
        # Convert time object to string
        if isinstance(config_dict.get("daily_submission_time"), time):
            config_dict["daily_submission_time"] = config.daily_submission_time.isoformat()
        
        # Convert sets to lists for JSON serialization
        if config_dict.get("enabled_devices"):
            config_dict["enabled_devices"] = list(config.enabled_devices)
        if config_dict.get("excluded_devices"):
            config_dict["excluded_devices"] = list(config.excluded_devices)
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
            
        logger.info(f"✅ Saved submission config to {config_path}")
        
    except Exception as e:
        logger.error(f"❌ Error saving config file {config_path}: {e}")

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from supabase import create_client
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        
        # Create scheduler with test config
        config = SubmissionConfig(
            submission_enabled=True,
            daily_submission_time=time(hour=2, minute=0),  # 2 AM
            default_policy_id=os.getenv("GUARDIAN_DEFAULT_POLICY_ID"),
            min_data_completeness=75.0,  # Lower threshold for testing
            max_concurrent_submissions=3
        )
        
        scheduler = GuardianSubmissionScheduler(supabase, config)
        
        async def test_scheduler():
            print("🔍 Testing GuardianSubmissionScheduler...")
            
            # Test queue status
            status = await scheduler.get_queue_status()
            print(f"📊 Queue status: {status}")
            
            # Test manual submission queueing
            success = await scheduler.queue_submission(
                device_id="ESP32_001",
                trigger=SubmissionTrigger.MANUAL
            )
            print(f"📋 Manual queue result: {success}")
            
            # Test daily submission processing
            results = await scheduler.process_daily_submissions()
            print(f"📅 Daily processing results: {results}")
            
            print("✅ GuardianSubmissionScheduler test complete")
        
        # Run test
        asyncio.run(test_scheduler())
    else:
        print("❌ Set SUPABASE_URL and SUPABASE_KEY environment variables to test")