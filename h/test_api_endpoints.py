#!/usr/bin/env python3
"""
Test script for Guardian API endpoints
Tests authentication and API connectivity
"""

import requests
import json
from guardian_client import GuardianClient, GuardianConfig

def test_guardian_endpoints():
    """Test all Guardian API endpoints"""
    print("🧪 Testing Guardian API Endpoints")
    print("=" * 50)
    
    config = GuardianConfig()
    client = GuardianClient(config)
    
    # Test 1: Login
    print("1️⃣ Testing login endpoint...")
    if client.login():
        print("✅ Login successful")
        print(f"   Refresh token: {client.refresh_token[:20]}...")
    else:
        print("❌ Login failed")
        return False
    
    # Test 2: Access token
    print("\n2️⃣ Testing access token endpoint...")
    if client.get_access_token():
        print("✅ Access token obtained")
        print(f"   Access token: {client.access_token[:20]}...")
    else:
        print("❌ Access token failed")
        return False
    
    # Test 3: Policy info (optional)
    print("\n3️⃣ Testing policy info endpoint...")
    try:
        headers = {"Authorization": f"Bearer {client.access_token}"}
        response = requests.get(
            f"{config.base_url}/policies/{config.policy_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            policy_info = response.json()
            print("✅ Policy info retrieved")
            print(f"   Policy name: {policy_info.get('name', 'N/A')}")
            print(f"   Policy status: {policy_info.get('status', 'N/A')}")
        else:
            print(f"⚠️  Policy info request failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Policy info error: {e}")
    
    # Test 4: Submit test report
    print("\n4️⃣ Testing monitoring report submission...")
    test_data = {
        "field0": "API_TEST_PROJECT",
        "field1": "Grid connected renewable electricity generation",
        "field6": "999.99"
    }
    
    if client.submit_monitoring_report(test_data):
        print("✅ Test report submitted successfully")
    else:
        print("❌ Test report submission failed")
        return False
    
    print("\n🎉 All API tests completed successfully!")
    return True

def test_mrv_sender_connectivity():
    """Test mrv-sender connectivity"""
    print("\n🧪 Testing MRV Sender Connectivity")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3005/health", timeout=5)
        if response.status_code == 200:
            print("✅ MRV Sender is running and accessible")
            return True
        else:
            print(f"⚠️  MRV Sender responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ MRV Sender is not running or not accessible")
        print("   Please start mrv-sender first: ./start_mrv_sender.bat")
        return False
    except Exception as e:
        print(f"❌ MRV Sender connectivity error: {e}")
        return False

def main():
    """Main test function"""
    print("🔬 API Endpoint Testing Suite")
    print("=" * 60)
    
    # Test Guardian API
    guardian_ok = test_guardian_endpoints()
    
    # Test MRV Sender
    mrv_sender_ok = test_mrv_sender_connectivity()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"Guardian API: {'✅ PASS' if guardian_ok else '❌ FAIL'}")
    print(f"MRV Sender:   {'✅ PASS' if mrv_sender_ok else '❌ FAIL'}")
    
    if guardian_ok and mrv_sender_ok:
        print("\n🎉 All systems are ready for MRV processing!")
    elif guardian_ok:
        print("\n⚠️  Guardian is ready, but MRV Sender needs to be started")
        print("   You can still run the backend in direct mode")
    else:
        print("\n❌ Please check your Guardian credentials and network connectivity")

if __name__ == "__main__":
    main()