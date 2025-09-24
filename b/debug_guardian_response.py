#!/usr/bin/env python3
"""
Debug script to examine Guardian API response format
"""

import requests
import json

def debug_guardian_login():
    """Debug Guardian login response format"""
    
    url = "http://localhost:3000/api/v1/accounts/login"
    credentials = {
        "username": "VerifiedCC",
        "password": "VerifiedCC2025"
    }
    
    print(f"🔍 Making request to: {url}")
    print(f"📝 Credentials: {credentials}")
    
    try:
        response = requests.post(url, json=credentials, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"\n✅ Response Data:")
            print(json.dumps(response_data, indent=2))
            
            print(f"\n🔍 Available fields:")
            for key, value in response_data.items():
                print(f"   - {key}: {type(value).__name__} = {str(value)[:100]}...")
                
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_guardian_login()