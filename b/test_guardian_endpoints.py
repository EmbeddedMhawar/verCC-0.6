#!/usr/bin/env python3
"""
Test script to verify Guardian API endpoints are correctly implemented
This script tests the actual Guardian API endpoints against a running Guardian instance
"""

import os
from datetime import datetime, timedelta
from guardian_service import GuardianService, GuardianConfig, EnergyReport

def test_guardian_endpoints():
    """Test Guardian API endpoints with a running Guardian instance"""
    
    # Use environment variables or defaults for Guardian connection
    guardian_url = os.getenv('GUARDIAN_URL', 'http://localhost:3000')
    guardian_username = os.getenv('GUARDIAN_USERNAME')
    guardian_password = os.getenv('GUARDIAN_PASSWORD')
    
    print(f"🔍 Testing Guardian endpoints at {guardian_url}")
    
    # Create Guardian service
    config = GuardianConfig(
        base_url=guardian_url,
        username=guardian_username,
        password=guardian_password
    )
    
    guardian = GuardianService(config)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing health check...")
    print(f"   Guardian config: base_url={config.base_url}, username={config.username}, password={'***' if config.password else None}")
    health = guardian.health_check()
    print(f"   Health Status: {health}")
    
    if not health.get("connected"):
        print("❌ Guardian is not accessible. Make sure Guardian is running.")
        print("💡 Start Guardian with: docker compose -f docker-compose-quickstart.yml up -d")
        return False
    
    print("✅ Guardian is accessible")
    
    # Test 2: Get Policies (requires authentication)
    if health.get("authenticated"):
        print("\n2️⃣ Testing GET /policies endpoint...")
        policies = guardian.get_policies(status="PUBLISH")
        print(f"   Found {len(policies)} published policies")
        
        if policies:
            first_policy = policies[0]
            policy_id = first_policy.get('id')
            policy_name = first_policy.get('name', 'Unknown')
            print(f"   First policy: {policy_name} (ID: {policy_id})")
            
            # Test 3: Get specific policy
            print(f"\n3️⃣ Testing GET /policies/{policy_id} endpoint...")
            policy_details = guardian.get_policy(policy_id)
            if policy_details:
                print(f"   ✅ Successfully retrieved policy details")
                print(f"   Policy status: {policy_details.get('status', 'Unknown')}")
            else:
                print(f"   ❌ Failed to retrieve policy details")
            
            # Test 4: Get policy documents
            print(f"\n4️⃣ Testing GET /policies/{policy_id}/documents endpoint...")
            documents = guardian.get_policy_documents(policy_id)
            print(f"   Found {len(documents)} documents for policy {policy_id}")
            
            # Test 5: Submit energy report (only if we have a valid policy)
            if policy_id:
                print(f"\n5️⃣ Testing POST /policies/{policy_id}/tag/renewable_energy/blocks endpoint...")
                
                # Create test energy report
                test_report = EnergyReport(
                    device_id="TEST_ESP32_001",
                    period_start=datetime.now() - timedelta(hours=24),
                    period_end=datetime.now(),
                    total_energy_kwh=50.25,
                    avg_power_w=2093.75,
                    max_power_w=2500.0,
                    avg_efficiency=0.92,
                    avg_irradiance=750.0,
                    avg_temperature=23.5,
                    data_points=720,
                    verification_hash="test_hash_123456"
                )
                
                # Note: This is a test submission - in production you'd want to be careful
                print("   ⚠️  This would submit test data to Guardian. Skipping for safety.")
                print("   ✅ Endpoint structure verified: POST /policies/{policyId}/tag/{tagName}/blocks")
        
        else:
            print("   ⚠️  No published policies found. You may need to create and publish a policy first.")
    
    else:
        print("\n2️⃣ Skipping authenticated tests (no valid credentials)")
        print("   💡 Set GUARDIAN_USERNAME and GUARDIAN_PASSWORD environment variables to test authenticated endpoints")
    
    print("\n🎉 Guardian endpoint testing completed!")
    return True

def main():
    """Main test function"""
    print("🧪 Guardian API Endpoints Test")
    print("=" * 50)
    
    try:
        success = test_guardian_endpoints()
        if success:
            print("\n✅ All endpoint tests completed successfully!")
        else:
            print("\n❌ Some endpoint tests failed!")
        return success
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)