#!/usr/bin/env python3
"""
Quick Integration Test Runner
Simplified test runner for Guardian integration tests that can be executed directly
"""

import sys
import os
import traceback
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_quick_tests():
    """Run a subset of integration tests quickly"""
    print("🚀 Running Quick Guardian Integration Tests")
    print("=" * 50)
    
    try:
        # Import test classes
        from test_guardian_integration import TestGuardianIntegrationWorkflow, TestGuardianIntegrationErrorScenarios
        
        # Initialize test instances
        workflow_tests = TestGuardianIntegrationWorkflow()
        error_tests = TestGuardianIntegrationErrorScenarios()
        
        # Set up test fixtures manually (without pytest)
        workflow_tests.test_config = {
            "guardian_url": "http://localhost:3000",
            "username": "test_user",
            "password": "test_password",
            "policy_id": "test_policy_123",
            "device_id": "ESP32_INTEGRATION_TEST",
            "tag_name": "renewable_energy"
        }
        
        # Mock Supabase client
        from unittest.mock import Mock
        workflow_tests.mock_supabase = Mock()
        
        # Initialize components
        from guardian_auth import GuardianAuth
        from guardian_service import GuardianService
        from guardian_policy_manager import GuardianPolicyManager
        from guardian_document_submitter import GuardianDocumentSubmitter, RetryConfig
        from energy_data_aggregator import EnergyDataAggregator
        from guardian_submissions_db import GuardianSubmissionsDB
        
        workflow_tests.guardian_auth = GuardianAuth(base_url=workflow_tests.test_config["guardian_url"])
        workflow_tests.guardian_service = GuardianService()
        workflow_tests.policy_manager = GuardianPolicyManager(workflow_tests.guardian_service)
        workflow_tests.document_submitter = GuardianDocumentSubmitter(
            workflow_tests.guardian_service,
            RetryConfig(max_retries=2, base_delay=0.1)
        )
        workflow_tests.energy_aggregator = EnergyDataAggregator(supabase_client=workflow_tests.mock_supabase)
        workflow_tests.submissions_db = GuardianSubmissionsDB(supabase_client=workflow_tests.mock_supabase)
        
        # Create sample data
        workflow_tests.sample_energy_data = workflow_tests._create_sample_energy_data()
        workflow_tests.sample_aggregated_report = workflow_tests._create_sample_aggregated_report()
        
        # Set up error tests
        error_tests.guardian_auth = GuardianAuth(base_url="http://localhost:3000")
        error_tests.document_submitter = GuardianDocumentSubmitter()
        
        test_results = []
        
        # Test 1: Authentication Flow
        print("\n🔐 Test 1: Guardian Authentication Flow")
        try:
            workflow_tests.test_guardian_authentication_flow()
            test_results.append(("Authentication Flow", "PASSED"))
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            test_results.append(("Authentication Flow", "FAILED"))
        
        # Test 2: Energy Data Aggregation
        print("\n📊 Test 2: Energy Data Aggregation Pipeline")
        try:
            workflow_tests.test_energy_data_aggregation_pipeline()
            test_results.append(("Energy Data Aggregation", "PASSED"))
        except Exception as e:
            print(f"❌ Energy aggregation test failed: {e}")
            test_results.append(("Energy Data Aggregation", "FAILED"))
        
        # Test 3: Policy Discovery
        print("\n📋 Test 3: Policy Discovery and Validation")
        try:
            workflow_tests.test_policy_discovery_and_validation()
            test_results.append(("Policy Discovery", "PASSED"))
        except Exception as e:
            print(f"❌ Policy discovery test failed: {e}")
            test_results.append(("Policy Discovery", "FAILED"))
        
        # Test 4: Document Submission
        print("\n📤 Test 4: Document Submission and Tracking")
        try:
            workflow_tests.test_document_submission_and_tracking()
            test_results.append(("Document Submission", "PASSED"))
        except Exception as e:
            print(f"❌ Document submission test failed: {e}")
            test_results.append(("Document Submission", "FAILED"))
        
        # Test 5: Error Handling
        print("\n🔧 Test 5: Error Handling and Retry Mechanisms")
        try:
            workflow_tests.test_error_handling_and_retry_mechanisms()
            test_results.append(("Error Handling", "PASSED"))
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            test_results.append(("Error Handling", "FAILED"))
        
        # Test 6: Data Integrity
        print("\n🔒 Test 6: Data Integrity Verification")
        try:
            workflow_tests.test_data_integrity_verification()
            test_results.append(("Data Integrity", "PASSED"))
        except Exception as e:
            print(f"❌ Data integrity test failed: {e}")
            test_results.append(("Data Integrity", "FAILED"))
        
        # Test 7: Regional Compliance
        print("\n🌍 Test 7: Regional Compliance Validation")
        try:
            workflow_tests.test_regional_compliance_validation()
            test_results.append(("Regional Compliance", "PASSED"))
        except Exception as e:
            print(f"❌ Regional compliance test failed: {e}")
            test_results.append(("Regional Compliance", "FAILED"))
        
        # Test 8: Error Scenarios
        print("\n⚠️ Test 8: Error Scenarios")
        try:
            error_tests.test_guardian_service_unavailable()
            error_tests.test_malformed_energy_data()
            test_results.append(("Error Scenarios", "PASSED"))
        except Exception as e:
            print(f"❌ Error scenarios test failed: {e}")
            test_results.append(("Error Scenarios", "FAILED"))
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed_count = 0
        failed_count = 0
        
        for test_name, result in test_results:
            status_icon = "✅" if result == "PASSED" else "❌"
            print(f"{status_icon} {test_name}: {result}")
            
            if result == "PASSED":
                passed_count += 1
            else:
                failed_count += 1
        
        print(f"\nTotal Tests: {len(test_results)}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        print(f"Success Rate: {(passed_count/len(test_results)*100):.1f}%")
        
        if failed_count == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️ {failed_count} test(s) failed")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        print("Make sure all Guardian integration components are available")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during test execution: {e}")
        traceback.print_exc()
        return False

def check_environment():
    """Check basic environment setup"""
    print("🔍 Checking Environment...")
    
    # Check for required files
    required_files = [
        'guardian_auth.py',
        'guardian_service.py', 
        'guardian_policy_manager.py',
        'guardian_document_submitter.py',
        'energy_data_aggregator.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files found")
    
    # Check environment variables
    env_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {missing_vars}")
        print("Some tests may use mock data instead of real database connections")
    else:
        print("✅ Database environment variables configured")
    
    return True

def main():
    """Main function"""
    print(f"Guardian Integration Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_environment():
        print("❌ Environment check failed")
        return 1
    
    success = run_quick_tests()
    
    if success:
        print("\n🎉 Quick integration tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())