#!/usr/bin/env python3
"""
Guardian Authentication Service Demo
Demonstrates the Guardian authentication functionality
"""

import os
import sys
from datetime import datetime, timedelta
from guardian_auth import GuardianAuth, GuardianAuthError
from guardian_service import GuardianService, GuardianConfig

def demo_authentication():
    """Demonstrate Guardian authentication features"""
    print("🔐 Guardian Authentication Service Demo")
    print("=" * 50)
    
    # Initialize Guardian authentication
    auth = GuardianAuth(base_url="http://localhost:3000")
    
    print("1. Guardian Authentication Service initialized")
    print(f"   Base URL: {auth.base_url}")
    print(f"   Timeout: {auth.timeout}s")
    print(f"   Current token: {'None' if not auth.current_token else 'Available'}")
    print()
    
    # Check environment variables
    username = os.getenv("GUARDIAN_USERNAME")
    password = os.getenv("GUARDIAN_PASSWORD")
    
    if not username or not password:
        print("⚠️ Guardian credentials not found in environment variables")
        print("   Set GUARDIAN_USERNAME and GUARDIAN_PASSWORD to test authentication")
        print("   Example:")
        print("   export GUARDIAN_USERNAME=your_username")
        print("   export GUARDIAN_PASSWORD=your_password")
        print()
        return False
    
    try:
        print("2. Attempting Guardian login...")
        token = auth.login(username, password)
        
        print("✅ Login successful!")
        print(f"   Username: {token.username}")
        print(f"   Token: {token.token[:20]}...")
        print(f"   Expires: {token.expires_at.isoformat()}")
        print(f"   Time until expiry: {token.time_until_expiry()}")
        print()
        
        print("3. Testing token validation...")
        print(f"   Token valid: {auth.is_token_valid()}")
        print(f"   Auth headers: {auth.get_auth_headers()}")
        print()
        
        print("4. Testing user info retrieval...")
        user_info = auth.get_user_info()
        if user_info:
            print(f"   User info retrieved: {user_info.get('username', 'unknown')}")
        else:
            print("   User info not available")
        print()
        
        print("5. Testing logout...")
        logout_success = auth.logout()
        print(f"   Logout successful: {logout_success}")
        print(f"   Token after logout: {'None' if not auth.current_token else 'Still available'}")
        print()
        
        return True
        
    except GuardianAuthError as e:
        print(f"❌ Guardian authentication error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def demo_service_integration():
    """Demonstrate Guardian service with authentication"""
    print("🔗 Guardian Service Integration Demo")
    print("=" * 50)
    
    # Get credentials from environment
    username = os.getenv("GUARDIAN_USERNAME")
    password = os.getenv("GUARDIAN_PASSWORD")
    
    if not username or not password:
        print("⚠️ Skipping service demo - no credentials available")
        return False
    
    # Initialize Guardian service with authentication
    config = GuardianConfig(
        base_url="http://localhost:3000",
        username=username,
        password=password
    )
    
    print("1. Initializing Guardian service with authentication...")
    service = GuardianService(config)
    print(f"   Service initialized")
    print(f"   Authentication status: {'Authenticated' if service.auth.is_token_valid() else 'Not authenticated'}")
    print()
    
    print("2. Testing Guardian health check...")
    health = service.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Connected: {health.get('connected', False)}")
    print(f"   Authenticated: {health.get('authenticated', False)}")
    if health.get('user'):
        print(f"   User: {health.get('user')}")
    print()
    
    if health.get('connected') and health.get('authenticated'):
        print("3. Testing Guardian policies retrieval...")
        policies = service.get_policies()
        print(f"   Policies found: {len(policies)}")
        for i, policy in enumerate(policies[:3]):  # Show first 3 policies
            print(f"   - {policy.get('name', 'Unknown')} (ID: {policy.get('id', 'unknown')})")
        print()
        
        print("4. Testing Guardian tokens retrieval...")
        tokens = service.get_tokens()
        print(f"   Tokens found: {len(tokens)}")
        for i, token in enumerate(tokens[:3]):  # Show first 3 tokens
            print(f"   - {token.get('name', 'Unknown')} (ID: {token.get('id', 'unknown')})")
        print()
    else:
        print("3. Skipping API tests - Guardian not connected or not authenticated")
        print()
    
    return True

def main():
    """Main demo function"""
    print("🚀 Guardian Authentication & Service Demo")
    print("=" * 60)
    print()
    
    # Demo authentication
    auth_success = demo_authentication()
    print()
    
    # Demo service integration
    service_success = demo_service_integration()
    print()
    
    print("=" * 60)
    if auth_success or service_success:
        print("✅ Demo completed successfully!")
        print()
        print("💡 Next steps:")
        print("   1. Start Guardian: docker compose -f docker-compose-quickstart.yml up -d")
        print("   2. Set environment variables: GUARDIAN_USERNAME, GUARDIAN_PASSWORD")
        print("   3. Run this demo again to test with real Guardian instance")
    else:
        print("⚠️ Demo completed with limitations")
        print("   Set up Guardian and credentials to see full functionality")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())