#!/usr/bin/env python3
"""
Step 4 Alternative: Direct Guardian API Submission
Following Steps.md workflow:
1. Authenticate with Guardian (Step 2)
2. Send monitoring report directly to Guardian API (Step 5)
"""

import requests
import json

def authenticate_guardian():
    """Step 2: Authenticate with Guardian"""
    print("🔐 Authenticating with Guardian...")
    
    # Step 2a: Login
    login_url = "https://guardianservice.app/api/v1/accounts/login"
    login_data = {
        "username": "Mhawar",
        "password": "Mhawar2001'",
        "tenantId": "68cc28cc348f53cc0b247ce4"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return None
        
        refresh_token = response.json().get("refreshToken")
        print("✅ Login successful")
        
        # Step 2b: Get access token
        token_url = "https://guardianservice.app/api/v1/accounts/access-token"
        token_data = {"refreshToken": refresh_token}
        
        response = requests.post(token_url, json=token_data)
        if response.status_code not in [200, 201]:
            print(f"❌ Access token failed: {response.text}")
            return None
        
        access_token = response.json().get("accessToken")
        print("✅ Access token obtained")
        return access_token
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def submit_monitoring_report_direct(access_token):
    """Step 5: Submit monitoring report directly to Guardian"""
    print("\n📤 Step 4/5: Submitting monitoring report to Guardian...")
    
    # Guardian configuration from AMS-I-D.yaml
    policy_id = "68d5ba75152381fe552b1c6d"
    block_id = "1021939c-b948-4732-bd5f-90cc4ae1cd50"
    
    # Test data matching the schema
    report_data = {
        "field0": "ProjectID123",  # Project identifier
        "field1": "Grid connected renewable electricity generation",  # Project type
        "field6": "1500.75"  # Emission reductions
    }
    
    print(f"Sending report data: {json.dumps(report_data, indent=2)}")
    
    # Guardian API endpoint
    url = f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks/{block_id}/external"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=report_data)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Monitoring report submitted successfully to Guardian!")
            return True
        else:
            print(f"❌ Guardian API returned error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting to Guardian: {e}")
        return False

def main():
    print("=" * 60)
    print("Step 4 Alternative: Direct Guardian API Submission")
    print("=" * 60)
    
    # Authenticate
    access_token = authenticate_guardian()
    if not access_token:
        print("❌ Authentication failed")
        return False
    
    # Submit report
    if not submit_monitoring_report_direct(access_token):
        print("❌ Report submission failed")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Step 4 Alternative Complete!")
    print("✅ Python → Guardian API working!")
    print("=" * 60)
    print("\n📋 Next: Check Guardian UI for the submitted report")
    print("📋 Login to Guardian and check AMS-I.D policy monitoring reports")
    
    return True

if __name__ == "__main__":
    main()