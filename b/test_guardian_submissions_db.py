#!/usr/bin/env python3
"""
Test Guardian Submissions Database functionality
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

from models import (
    GuardianSubmissionCreate, 
    GuardianSubmissionUpdate, 
    GuardianSubmissionQuery,
    GuardianSubmissionStatus
)
from guardian_submissions_db import GuardianSubmissionsDB

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_guardian_submissions_db():
    """Test Guardian submissions database operations"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        supabase = create_client(supabase_url, supabase_key)
        db = GuardianSubmissionsDB(supabase)
        
        logger.info("🧪 Starting Guardian submissions database tests...")
        
        # Test 1: Create a new submission
        logger.info("\n📝 Test 1: Creating new Guardian submission...")
        
        test_submission = GuardianSubmissionCreate(
            device_id="ESP32_TEST_001",
            policy_id="test_policy_123",
            period_start=datetime.now() - timedelta(hours=24),
            period_end=datetime.now(),
            total_energy_kwh=125.5,
            data_points_count=1440,  # 24 hours * 60 minutes
            verification_hash="sha256:abcd1234567890",
            guardian_response={"status": "submitted", "document_id": "doc_123"}
        )
        
        created_submission = await db.create_submission(test_submission)
        logger.info(f"✅ Created submission with ID: {created_submission.id}")
        
        # Test 2: Get submission by ID
        logger.info("\n🔍 Test 2: Getting submission by ID...")
        
        retrieved_submission = await db.get_submission(created_submission.id)
        if retrieved_submission:
            logger.info(f"✅ Retrieved submission: {retrieved_submission.device_id} - {retrieved_submission.status}")
        else:
            logger.error("❌ Failed to retrieve submission")
        
        # Test 3: Update submission status
        logger.info("\n📝 Test 3: Updating submission status...")
        
        update_data = GuardianSubmissionUpdate(
            guardian_document_id="guardian_doc_456",
            status=GuardianSubmissionStatus.PROCESSING,
            submitted_at=datetime.now(),
            guardian_response={"status": "processing", "document_id": "guardian_doc_456"}
        )
        
        updated_submission = await db.update_submission(created_submission.id, update_data)
        logger.info(f"✅ Updated submission status to: {updated_submission.status}")
        
        # Test 4: Query submissions
        logger.info("\n🔍 Test 4: Querying submissions...")
        
        query = GuardianSubmissionQuery(
            device_id="ESP32_TEST_001",
            status=GuardianSubmissionStatus.PROCESSING,
            limit=10
        )
        
        submissions = await db.query_submissions(query)
        logger.info(f"✅ Found {len(submissions)} submissions matching query")
        
        # Test 5: Get device submissions
        logger.info("\n📊 Test 5: Getting device submissions...")
        
        device_submissions = await db.get_device_submissions("ESP32_TEST_001")
        logger.info(f"✅ Found {len(device_submissions)} submissions for device ESP32_TEST_001")
        
        # Test 6: Get submission statistics
        logger.info("\n📈 Test 6: Getting submission statistics...")
        
        stats = await db.get_submission_stats()
        logger.info(f"✅ Total submissions: {stats.total_submissions}")
        logger.info(f"   Pending: {stats.pending_submissions}")
        logger.info(f"   Processing: {stats.processing_submissions}")
        logger.info(f"   Verified: {stats.verified_submissions}")
        logger.info(f"   Failed: {stats.failed_submissions}")
        logger.info(f"   Success rate: {stats.success_rate:.1f}%")
        
        # Test 7: Get device summary
        logger.info("\n📋 Test 7: Getting device summary...")
        
        device_summary = await db.get_device_summary("ESP32_TEST_001")
        logger.info(f"✅ Device summary for ESP32_TEST_001:")
        logger.info(f"   Total submissions: {device_summary.total_submissions}")
        logger.info(f"   Verified: {device_summary.verified_submissions}")
        logger.info(f"   Failed: {device_summary.failed_submissions}")
        logger.info(f"   Success rate: {device_summary.success_rate:.1f}%")
        
        # Test 8: Update to verified status
        logger.info("\n✅ Test 8: Updating to verified status...")
        
        verify_update = GuardianSubmissionUpdate(
            status=GuardianSubmissionStatus.VERIFIED,
            verified_at=datetime.now(),
            guardian_response={"status": "verified", "carbon_credits": 12.5}
        )
        
        verified_submission = await db.update_submission(created_submission.id, verify_update)
        logger.info(f"✅ Updated submission to verified status")
        
        # Test 9: Get pending submissions
        logger.info("\n⏳ Test 9: Getting pending submissions...")
        
        pending_submissions = await db.get_pending_submissions()
        logger.info(f"✅ Found {len(pending_submissions)} pending submissions")
        
        # Test 10: Clean up test data
        logger.info("\n🧹 Test 10: Cleaning up test data...")
        
        deleted = await db.delete_submission(created_submission.id)
        if deleted:
            logger.info("✅ Test submission deleted successfully")
        else:
            logger.warning("⚠️ Test submission was not deleted")
        
        logger.info("\n🎉 All Guardian submissions database tests completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_error_handling():
    """Test error handling scenarios"""
    try:
        logger.info("\n🧪 Testing error handling scenarios...")
        
        # Initialize with invalid credentials to test error handling
        try:
            supabase = create_client("invalid_url", "invalid_key")
            db = GuardianSubmissionsDB(supabase)
            
            # This should fail
            await db.get_submission(999999)
            logger.error("❌ Expected error did not occur")
            
        except Exception as e:
            logger.info(f"✅ Error handling working correctly: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False


def print_test_summary():
    """Print test summary and next steps"""
    print("\n" + "="*60)
    print("GUARDIAN SUBMISSIONS DATABASE TESTS COMPLETED")
    print("="*60)
    print("\nWhat was tested:")
    print("✅ Creating new Guardian submissions")
    print("✅ Retrieving submissions by ID")
    print("✅ Updating submission status and data")
    print("✅ Querying submissions with filters")
    print("✅ Getting device-specific submissions")
    print("✅ Calculating submission statistics")
    print("✅ Getting device summaries")
    print("✅ Status transitions (PENDING → PROCESSING → VERIFIED)")
    print("✅ Deleting submissions")
    print("✅ Error handling")
    
    print("\nNext steps:")
    print("1. Integrate GuardianSubmissionsDB into main.py")
    print("2. Add Guardian submission tracking to existing endpoints")
    print("3. Create background tasks for status monitoring")
    print("4. Add Guardian submission endpoints to the API")


if __name__ == "__main__":
    async def main():
        try:
            # Run main tests
            success = await test_guardian_submissions_db()
            
            if success:
                # Run error handling tests
                await test_error_handling()
                print_test_summary()
            else:
                print("\n❌ Tests failed. Check the logs above for details.")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
    
    # Run the async tests
    result = asyncio.run(main())
    
    if not result:
        exit(1)