#!/usr/bin/env python3
"""
Test Guardian Roles and Policy Access
Check available roles and try to access as Project Participant
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

def check_policy_roles(access_token):
    """Check available roles in the policy"""
    print("👥 Checking policy roles...")
    
    policy_id = "68d5ba75152381fe552b1c6d"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Try to get policy groups/roles
        response = requests.get(
            f"https://guardianservice.app/api/v1/policies/{policy_id}/groups",
            headers=headers
        )
        
        print(f"Policy groups status: {response.status_code}")
        if response.status_code == 200:
            groups = response.json()
            print("✅ Available groups/roles:")
            for group in groups:
                print(f"   - {group}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking roles: {e}")

def try_role_selection(access_token):
    """Try to select Project Participant role"""
    print("\n🎭 Trying to select Project Participant role...")
    
    policy_id = "68d5ba75152381fe552b1c6d"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Try different role selection methods
    role_data_options = [
        {"role": "Project Participant"},
        {"group": "Project Participant"},
        {"policyRole": "Project Participant"},
        "Project Participant"
    ]
    
    for i, role_data in enumerate(role_data_options, 1):
        print(f"\n{i}️⃣ Trying role data format: {role_data}")
        
        try:
            response = requests.post(
                f"https://guardianservice.app/api/v1/policies/{policy_id}/groups",
                headers=headers,
                json=role_data
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code in [200, 201]:
                print("   ✅ Role selection might have worked!")
                return True
                
        except Exception as e:
            print(f"   Error: {e}")
    
    return False

def check_blocks_after_role_change(access_token):
    """Check if blocks are accessible after role change"""
    print("\n🧩 Checking blocks after role change...")
    
    policy_id = "68d5ba75152381fe552b1c6d"
    block_id = "1021939c-b948-4732-bd5f-90cc4ae1cd50"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Try to access the specific block
        response = requests.get(
            f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks/{block_id}",
            headers=headers
        )
        
        print(f"Block access status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Block is now accessible!")
            return True
        else:
            print("❌ Block still not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error checking block: {e}")
        return False

def try_document_submission(access_token):
    """Try submitting a document/report"""
    print("\n📤 Trying document submission...")
    
    policy_id = "68d5ba75152381fe552b1c6d"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Try different document submission endpoints
    endpoints = [
        f"https://guardianservice.app/api/v1/policies/{policy_id}/tag/add_report_bnt",
        f"https://guardianservice.app/api/v1/policies/{policy_id}/tag/addreportbnt",
        f"https://guardianservice.app/api/v1/policies/{policy_id}/dry-run/user/1021939c-b948-4732-bd5f-90cc4ae1cd50"
    ]
    
    report_data = {
        "field0": "ProjectID123",
        "field1": "Grid connected renewable electricity generation", 
        "field6": "1500.75"
    }
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"\n{i}️⃣ Trying endpoint: {endpoint}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=report_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code in [200, 201]:
                print("   ✅ Submission successful!")
                return True
                
        except Exception as e:
            print(f"   Error: {e}")
    
    return False

def main():
    print("=" * 60)
    print("Guardian Roles and Policy Access Test")
    print("=" * 60)
    
    access_token = authenticate_guardian()
    if not access_token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Check available roles
    check_policy_roles(access_token)
    
    # Try to select Project Participant role
    role_changed = try_role_selection(access_token)
    
    # Check blocks after role change
    if role_changed:
        check_blocks_after_role_change(access_token)
    
    # Try document submission
    try_document_submission(access_token)
    
    print("\n" + "=" * 60)
    print("Roles and Access Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()