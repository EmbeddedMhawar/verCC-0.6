#!/usr/bin/env python3
"""
Test script for Guardian Submission Scheduler
Tests the automated Guardian submission workflow implementation
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta, time
from supabase import create_client
from dotenv import load_dotenv

from guardian_submission_scheduler import GuardianSubmissionScheduler, SubmissionConfig, SubmissionTrigger
from guardian_config_manager import GuardianConfigManager
from guardian_service import GuardianService, GuardianConfig
from energy_data_aggregator import EnergyDataAggregator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_guardian_scheduler():
    """Test the Guardian submission scheduler functionality"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL and SUPABASE_KEY environment variables are required")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    logger.info("✅ Supabase client initialized")
    
    # Initialize Guardian service
    guardian_config = GuardianConfig(
        base_url=os.getenv("GUARDIAN_URL", "http://localhost:3000"),
        username=os.getenv("GUARDIAN_USERNAME"),
        password=os.getenv("GUARDIAN_PASSWORD")
    )
    guardian_service = GuardianService(guardian_config)
    logger.info("✅ Guardian service initialized")
    
    # Test Guardian connection
    health = guardian_service.health_check()
    if not health.get("connected"):
        logger.warning("⚠️ Guardian is not connected - some tests may fail")
    else:
        logger.info("✅ Guardian connection verified")
    
    # Initialize configuration manager
    config_manager = GuardianConfigManager(guardian_service)
    logger.info("✅ Guardian config manager initialized")
    
    # Create test submission configuration
    submission_config = SubmissionConfig(
        submission_enabled=True,
        daily_submission_time=time(hour=2, minute=0),  # 2 AM for testing
        default_policy_id=os.getenv("GUARDIAN_DEFAULT_POLICY_ID"),
        min_data_completeness=75.0,  # Lower threshold for testing
        min_integrity_score=0.6,     # Lower threshold for testing
        min_readings_per_day=50,     # Lower threshold for testing
        min_energy_kwh=0.05,         # Lower threshold for testing
        max_concurrent_submissions=3,
        max_retry_attempts=2
    )
    
    # Initialize scheduler
    scheduler = GuardianSubmissionScheduler(supabase, submission_config)
    logger.info("✅ Guardian scheduler initialized")
    
    print("\n" + "="*60)
    print("🔍 TESTING GUARDIAN SUBMISSION SCHEDULER")
    print("="*60)
    
    # Test 1: Queue Status
    print("\n📊 Test 1: Queue Status")
    try:
        status = await scheduler.get_queue_status()
        print(f"✅ Queue status retrieved:")
        print(f"   - Queue length: {status['queue_length']}")
        print(f"   - Active submissions: {status['active_submissions']}")
        print(f"   - Scheduler running: {status['scheduler_running']}")
        print(f"   - Submission enabled: {status['config']['submission_enabled']}")
    except Exception as e:
        print(f"❌ Queue status test failed: {e}")
    
    # Test 2: Configuration Summary
    print("\n🔧 Test 2: Configuration Summary")
    try:
        summary = config_manager.get_config_summary()
        print(f"✅ Configuration summary:")
        print(f"   - Policy selection mode: {summary['policy_config']['selection_mode']}")
        print(f"   - Default policy ID: {summary['policy_config']['default_policy_id']}")
        print(f"   - Daily submissions: {summary['timing_config']['daily_enabled']}")
        print(f"   - Daily time: {summary['timing_config']['daily_time']}")
    except Exception as e:
        print(f"❌ Configuration summary test failed: {e}")
    
    # Test 3: Policy Selection
    print("\n📋 Test 3: Policy Selection")
    try:
        test_device = "ESP32_TEST_001"
        policy_info = config_manager.get_policy_for_device(test_device, energy_kwh=2.5)
        print(f"✅ Policy for {test_device}:")
        print(f"   - Policy ID: {policy_info.get('policy_id')}")
        print(f"   - Tag name: {policy_info.get('tag_name')}")
        print(f"   - Selection reason: {policy_info.get('selection_reason')}")
    except Exception as e:
        print(f"❌ Policy selection test failed: {e}")
    
    # Test 4: Timing Check
    print("\n⏰ Test 4: Timing Check")
    try:
        timing_info = config_manager.should_submit_now(test_device, {
            "data_completeness_percent": 85.0,
            "total_energy_kwh": 1.5,
            "last_submission_time": None
        })
        print(f"✅ Timing check for {test_device}:")
        print(f"   - Should submit: {timing_info['should_submit']}")
        print(f"   - Reasons: {timing_info['reasons']}")
    except Exception as e:
        print(f"❌ Timing check test failed: {e}")
    
    # Test 5: Manual Queue Submission
    print("\n📋 Test 5: Manual Queue Submission")
    try:
        # Use yesterday's date for testing
        target_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        success = await scheduler.queue_submission(
            device_id=test_device,
            target_date=target_date,
            trigger=SubmissionTrigger.MANUAL,
            priority=1
        )
        
        if success:
            print(f"✅ Successfully queued submission for {test_device}")
            
            # Check queue status again
            status = await scheduler.get_queue_status()
            print(f"   - Queue length after queueing: {status['queue_length']}")
            
            if status['queue_items']:
                item = status['queue_items'][0]
                print(f"   - Queued item: {item['device_id']} for {item['target_date']} (trigger: {item['trigger']})")
        else:
            print(f"❌ Failed to queue submission for {test_device}")
            
    except Exception as e:
        print(f"❌ Manual queue submission test failed: {e}")
    
    # Test 6: Get Active Devices (if data exists)
    print("\n📱 Test 6: Active Devices Check")
    try:
        # Check for devices with recent data
        yesterday = datetime.now() - timedelta(days=1)
        result = supabase.table("sensor_readings")\
            .select("device_id")\
            .gte("timestamp", yesterday.isoformat())\
            .limit(5)\
            .execute()
        
        if result.data:
            device_ids = list(set([r["device_id"] for r in result.data]))
            print(f"✅ Found {len(device_ids)} devices with recent data:")
            for device_id in device_ids[:3]:  # Show first 3
                print(f"   - {device_id}")
                
                # Test readiness for first device
                if device_ids:
                    aggregator = EnergyDataAggregator(supabase)
                    try:
                        readiness = aggregator.validate_guardian_readiness(device_ids[0], yesterday)
                        print(f"   - Guardian readiness for {device_ids[0]}: {readiness['guardian_ready']}")
                    except Exception as e:
                        print(f"   - Readiness check failed for {device_ids[0]}: {e}")
        else:
            print("⚠️ No devices found with recent data")
            
    except Exception as e:
        print(f"❌ Active devices check failed: {e}")
    
    # Test 7: Daily Submission Processing (dry run)
    print("\n📅 Test 7: Daily Submission Processing (Dry Run)")
    try:
        # Process submissions for yesterday
        target_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        results = await scheduler.process_daily_submissions(target_date)
        print(f"✅ Daily submission processing results:")
        print(f"   - Target date: {results['target_date']}")
        print(f"   - Total devices: {results['total_devices']}")
        print(f"   - Queued submissions: {results['queued_submissions']}")
        print(f"   - Skipped devices: {results['skipped_devices']}")
        
        if results['errors']:
            print(f"   - Errors: {len(results['errors'])}")
            for error in results['errors'][:3]:  # Show first 3 errors
                print(f"     * {error}")
                
    except Exception as e:
        print(f"❌ Daily submission processing test failed: {e}")
    
    # Test 8: Available Policies
    print("\n📋 Test 8: Available Guardian Policies")
    try:
        policies = config_manager.get_available_policies()
        print(f"✅ Found {len(policies)} Guardian policies:")
        
        for policy in policies[:3]:  # Show first 3 policies
            print(f"   - {policy.get('name', 'Unknown')} (ID: {policy.get('id', 'N/A')}, Status: {policy.get('status', 'N/A')})")
            
        if not policies:
            print("⚠️ No Guardian policies found - check Guardian connection and authentication")
            
    except Exception as e:
        print(f"❌ Available policies test failed: {e}")
    
    print("\n" + "="*60)
    print("✅ GUARDIAN SCHEDULER TESTING COMPLETE")
    print("="*60)
    
    # Final queue status
    try:
        final_status = await scheduler.get_queue_status()
        print(f"\n📊 Final Queue Status:")
        print(f"   - Queue length: {final_status['queue_length']}")
        print(f"   - Active submissions: {final_status['active_submissions']}")
        print(f"   - Processed count: {final_status['processed_count']}")
    except Exception as e:
        print(f"❌ Final status check failed: {e}")
    
    print("\n💡 Next Steps:")
    print("   1. Ensure Guardian is running and accessible")
    print("   2. Set GUARDIAN_DEFAULT_POLICY_ID in .env file")
    print("   3. Add some test sensor data to the database")
    print("   4. Start the FastAPI server to test the full workflow")
    print("   5. Use the scheduler endpoints to monitor and control submissions")

if __name__ == "__main__":
    asyncio.run(test_guardian_scheduler())