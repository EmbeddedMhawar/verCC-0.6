#!/usr/bin/env python3
"""
Simple test script to verify Guardian credentials
"""

import os
import sys
from guardian_auth import GuardianAuth, GuardianAuthError

def test_guardian_credentials():
    """Test Guardian authentication with configured credentials"""
    
    # Set credentials from .env file values
    os.environ['GUARDIAN_USERNAME'] = 'VerifiedCC'
    os.environ['GUARDIAN_PASSWORD'] = 'VerifiedCC2025'
    
    username = os.getenv("GUARDIAN_USERNAME")
    password = os.getenv("GUARDIAN_PASSWORD")
    
    if not username or not password:
        print("❌ Guardian credentials not found in environment")
        return False
    
    print(f"🔍 Testing Guardian authentication for user: {username}")
    print(f"🌐 Guardian URL: http://localhost:3000")
    
    try:
        # Initialize Guardian auth
        auth = GuardianAuth(base_url="http://localhost:3000")
        
        # Test login
        print("🔐 Attempting login...")
        token = auth.login(username, password)
        
        if token:
            print(f"✅ Login successful!")
            print(f"👤 Username: {token.username}")
            print(f"🆔 User ID: {token.user_id}")
            print(f"🕒 Token expires: {token.expires_at}")
            print(f"🔑 Token valid: {not token.is_expired()}")
            
            # Test getting user info
            print("\n📋 Getting user information...")
            user_info = auth.get_user_info()
            if user_info:
                print(f"✅ User info retrieved:")
                print(f"   - Username: {user_info.get('username', 'N/A')}")
                print(f"   - Role: {user_info.get('role', 'N/A')}")
                print(f"   - ID: {user_info.get('id', 'N/A')}")
            else:
                print("⚠️ Could not retrieve user info")
            
            # Test logout
            print("\n🔓 Testing logout...")
            logout_success = auth.logout()
            if logout_success:
                print("✅ Logout successful")
            else:
                print("⚠️ Logout had issues but token cleared")
            
            print("\n🎉 All Guardian credential tests passed!")
            return True
            
    except GuardianAuthError as e:
        print(f"❌ Guardian authentication error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_guardian_credentials()
    sys.exit(0 if success else 1)