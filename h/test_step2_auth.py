#!/usr/bin/env python3
"""
Step 2: Test Guardian API Authentication
Following Steps.md workflow exactly
"""

import requests
import json

def test_guardian_login():
    """Test Step 2a: Login to get refresh token"""
    print("🔐 Step 2a: Testing Guardian Login...")
    
    login_url = "https://guardianservice.app/api/v1/accounts/login"
    login_data = {
        "username": "Mhawar",
        "password": "Mhawar2001'",
        "tenantId": "68cc28cc348f53cc0b247ce4"
    }
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(login_url, headers=headers, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            refresh_token = result.get("refreshToken")
            print("✅ Login successful!")
            print(f"Refresh Token: {refresh_token[:20]}...")
            return refresh_token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_access_token(refresh_token):
    """Test Step 2b: Get access token"""
    print("\n🎫 Step 2b: Testing Access Token...")
    
    if not refresh_token:
        print("❌ No refresh token available")
        return None
    
    token_url = "https://guardianservice.app/api/v1/accounts/access-token"
    token_data = {"refreshToken": refresh_token}
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(token_url, headers=headers, json=token_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            access_token = result.get("accessToken")
            print("✅ Access token obtained!")
            print(f"Access Token: {access_token[:20]}...")
            return access_token
        else:
            print(f"❌ Access token failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Access token error: {e}")
        return None

def main():
    print("=" * 60)
    print("Step 2: Guardian API Authentication Test")
    print("=" * 60)
    
    # Step 2a: Login
    refresh_token = test_guardian_login()
    
    # Step 2b: Get Access Token
    access_token = test_access_token(refresh_token)
    
    # Summary
    print("\n" + "=" * 60)
    print("Step 2 Summary:")
    if refresh_token and access_token:
        print("✅ Authentication successful - Ready for Step 3!")
        return True
    else:
        print("❌ Authentication failed - Check credentials")
        return False

if __name__ == "__main__":
    main()