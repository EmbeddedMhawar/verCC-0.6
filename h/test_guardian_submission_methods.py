#!/usr/bin/env python3
"""
Test Different Guardian Submission Methods
Try various ways to submit monitoring reports
"""

import requests
import json

def authenticate_guardian():
    """Authenticate with Guardian"""
    login_url = "https://guardianservice.app/api/v1/accounts/login"
    login_data = {
        "username": "Mhawar",
        "password": "Mhawar2001'",
        "tenantId": "68cc28cc348f53cc0b247ce4"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        refresh_token = response.json().get("refreshToken")
        
        token_url = "https://guardianservice.app/api/v1/accounts/access-token"
        token_data = {"refreshToken": refresh_token}
        
        response = requests.post(token_url, json=token_data)
        access_token = response.json().get("accessToken")
        return access_token
    except:
        return None

def try_submission_methods(access_token):
    """Try different submission methods"""
    print("🧪 Testing different submission methods...")
    
    policy_id = "68d5ba75152381fe552b1c6d"
    block_id = "1021939c-b948-4732-bd5f-90cc4ae1cd50"
    
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    report_data = {
        "field0": "ProjectID123",
        "field1": "Grid connected renewable electricity generation",
        "field6": "1500.75"
    }
    
    # Method 1: External endpoint (from Steps.md)
    print("\n1️⃣ Trying /external endpoint...")
    url1 = f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks/{block_id}/external"
    try:
        response = requests.post(url1, headers=headers, json=report_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 2: Direct block endpoint
    print("\n2️⃣ Trying direct block endpoint...")
    url2 = f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks/{block_id}"
    try:
        response = requests.post(url2, headers=headers, json=report_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 3: Documents endpoint
    print("\n3️⃣ Trying documents endpoint...")
    url3 = f"https://guardianservice.app/api/v1/policies/{policy_id}/documents"
    try:
        response = requests.post(url3, headers=headers, json=report_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 4: Check what endpoints are available
    print("\n4️⃣ Checking available endpoints...")
    base_url = f"https://guardianservice.app/api/v1/policies/{policy_id}"
    
    endpoints_to_check = [
        "",
        "/documents",
        "/dry-run",
        "/export",
        "/import",
        "/validate",
        "/publish",
        "/blocks",
        f"/blocks/{block_id}",
        f"/blocks/{block_id}/data",
        f"/blocks/{block_id}/documents"
    ]
    
    for endpoint in endpoints_to_check:
        url = base_url + endpoint
        try:
            # Try GET first
            response = requests.get(url, headers=headers)
            if response.status_code != 404:
                print(f"   GET {endpoint}: {response.status_code}")
                
            # Try POST for some endpoints
            if endpoint in ["/documents", f"/blocks/{block_id}", f"/blocks/{block_id}/data"]:
                response = requests.post(url, headers=headers, json=report_data)
                if response.status_code != 404:
                    print(f"   POST {endpoint}: {response.status_code} - {response.text[:100]}...")
                    
        except Exception as e:
            pass  # Skip errors for this exploration

def main():
    print("=" * 60)
    print("Guardian Submission Methods Test")
    print("=" * 60)
    
    access_token = authenticate_guardian()
    if not access_token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    try_submission_methods(access_token)
    
    print("\n" + "=" * 60)
    print("Submission Methods Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()