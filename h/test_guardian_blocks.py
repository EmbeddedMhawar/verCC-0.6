#!/usr/bin/env python3
"""
Test Guardian Policy Blocks
Find available blocks and their structure
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

def explore_policy_blocks(access_token):
    """Explore the policy block structure"""
    print("🧩 Exploring policy blocks...")
    
    policy_id = "68d5ba75152381fe552b1c6d"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(
            f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks",
            headers=headers
        )
        
        if response.status_code == 200:
            blocks_data = response.json()
            print("✅ Policy blocks retrieved")
            
            # Save to file for inspection
            with open('policy_blocks.json', 'w') as f:
                json.dump(blocks_data, f, indent=2)
            print("📁 Blocks data saved to policy_blocks.json")
            
            # Look for monitoring report related blocks
            find_monitoring_blocks(blocks_data)
            
        else:
            print(f"❌ Failed to get blocks: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting blocks: {e}")

def find_monitoring_blocks(blocks_data, level=0):
    """Recursively find monitoring report blocks"""
    indent = "  " * level
    
    if isinstance(blocks_data, dict):
        block_type = blocks_data.get('blockType', '')
        block_id = blocks_data.get('id', '')
        tag = blocks_data.get('tag', '')
        
        # Look for monitoring report related blocks
        if any(keyword in str(blocks_data).lower() for keyword in ['monitoring', 'report', 'mrv', 'add']):
            print(f"{indent}🎯 Found relevant block:")
            print(f"{indent}   ID: {block_id}")
            print(f"{indent}   Type: {block_type}")
            print(f"{indent}   Tag: {tag}")
            
            # Check if this is our target block
            if block_id == "1021939c-b948-4732-bd5f-90cc4ae1cd50":
                print(f"{indent}   ✅ This is our target block!")
                print(f"{indent}   Full block data:")
                print(json.dumps(blocks_data, indent=level+2)[:500] + "...")
        
        # Recurse into children
        if 'children' in blocks_data:
            for child in blocks_data['children']:
                find_monitoring_blocks(child, level + 1)
                
    elif isinstance(blocks_data, list):
        for item in blocks_data:
            find_monitoring_blocks(item, level)

def check_user_role(access_token):
    """Check current user role and permissions"""
    print("\n👤 Checking user role and permissions...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Try to get user profile
        response = requests.get(
            "https://guardianservice.app/api/v1/accounts/session",
            headers=headers
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User session data:")
            print(f"   Username: {user_data.get('username', 'N/A')}")
            print(f"   Role: {user_data.get('role', 'N/A')}")
            print(f"   DID: {user_data.get('did', 'N/A')}")
            
        else:
            print(f"❌ Failed to get user session: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking user role: {e}")

def main():
    print("=" * 60)
    print("Guardian Policy Blocks Explorer")
    print("=" * 60)
    
    access_token = authenticate_guardian()
    if not access_token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Check user role
    check_user_role(access_token)
    
    # Explore blocks
    explore_policy_blocks(access_token)
    
    print("\n" + "=" * 60)
    print("Policy Blocks Exploration Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()