#!/usr/bin/env python3
"""
Test Guardian Policy Information
Verify policy exists and find correct endpoints
"""

import requests
import json

def authenticate_guardian():
    """Authenticate with Guardian"""
    print("🔐 Authenticating with Guardian...")
    
    login_url = "https://guardianservice.app/api/v1/accounts/login"
    login_data = {
        "username": "Mhawar",
        "password": "Mhawar2001'",
        "tenantId": "68cc28cc348f53cc0b247ce4"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code != 200:
            return None
        
        refresh_token = response.json().get("refreshToken")
        
        token_url = "https://guardianservice.app/api/v1/accounts/access-token"
        token_data = {"refreshToken": refresh_token}
        
        response = requests.post(token_url, json=token_data)
        if response.status_code not in [200, 201]:
            return None
        
        access_token = response.json().get("accessToken")
        print("✅ Authentication successful")
        return access_token
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def check_policies(access_token):
    """Check available policies"""
    print("\n📋 Checking available policies...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(
            "https://guardianservice.app/api/v1/policies",
            headers=headers
        )
        
        print(f"Policies endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            policies = response.json()
            print(f"Found {len(policies)} policies:")
            
            for policy in policies:
                print(f"  - ID: {policy.get('id', 'N/A')}")
                print(f"    Name: {policy.get('name', 'N/A')}")
                print(f"    Status: {policy.get('status', 'N/A')}")
                print()
                
                # Check if this is our AMS-I.D policy
                if policy.get('id') == "68d5ba75152381fe552b1c6d":
                    print("✅ Found our AMS-I.D policy!")
                    return policy
            
            print("❌ AMS-I.D policy not found in the list")
            return None
        else:
            print(f"❌ Failed to get policies: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking policies: {e}")
        return None

def check_policy_details(access_token, policy_id):
    """Check specific policy details"""
    print(f"\n🔍 Checking policy details for: {policy_id}")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(
            f"https://guardianservice.app/api/v1/policies/{policy_id}",
            headers=headers
        )
        
        print(f"Policy details status: {response.status_code}")
        
        if response.status_code == 200:
            policy = response.json()
            print("✅ Policy details retrieved:")
            print(f"  Name: {policy.get('name', 'N/A')}")
            print(f"  Status: {policy.get('status', 'N/A')}")
            print(f"  Version: {policy.get('version', 'N/A')}")
            return policy
        else:
            print(f"❌ Failed to get policy details: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking policy details: {e}")
        return None

def check_policy_blocks(access_token, policy_id):
    """Check policy blocks/endpoints"""
    print(f"\n🧩 Checking policy blocks for: {policy_id}")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Try different possible endpoints
    endpoints_to_try = [
        f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks",
        f"https://guardianservice.app/api/v1/policies/{policy_id}/dry-run/blocks",
        f"https://guardianservice.app/api/v1/policies/{policy_id}/export/blocks"
    ]
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(endpoint, headers=headers)
            print(f"  {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    ✅ Success: {response.text[:100]}...")
            else:
                print(f"    ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")

def main():
    print("=" * 60)
    print("Guardian Policy Information Test")
    print("=" * 60)
    
    # Authenticate
    access_token = authenticate_guardian()
    if not access_token:
        print("❌ Authentication failed")
        return
    
    # Check policies
    policy = check_policies(access_token)
    
    # Check specific policy details
    policy_id = "68d5ba75152381fe552b1c6d"
    policy_details = check_policy_details(access_token, policy_id)
    
    # Check policy blocks
    check_policy_blocks(access_token, policy_id)
    
    print("\n" + "=" * 60)
    print("Policy Information Check Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()