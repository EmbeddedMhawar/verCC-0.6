#!/usr/bin/env python3
"""
Test Guardian Integration
Quick test to verify Guardian credentials functionality
"""

import requests
import json
from datetime import datetime

def test_guardian_endpoints():
    """Test Guardian API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Guardian Integration")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Main server health check passed")
        else:
            print("❌ Main server health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Landing page (Become Our Partner)
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Landing page (Become Our Partner) accessible")
        else:
            print("❌ Landing page failed")
    except Exception as e:
        print(f"❌ Landing page error: {e}")
    
    # Test 3: Energy dashboard
    try:
        response = requests.get(f"{base_url}/energy")
        if response.status_code == 200:
            print("✅ Energy dashboard accessible")
        else:
            print("❌ Energy dashboard failed")
    except Exception as e:
        print(f"❌ Energy dashboard error: {e}")
    
    # Test 4: Guardian dashboard (should redirect without auth)
    try:
        response = requests.get(f"{base_url}/dashboard", allow_redirects=False)
        if response.status_code == 302:
            print("✅ Guardian dashboard properly protected (redirects)")
        else:
            print("❌ Guardian dashboard protection failed")
    except Exception as e:
        print(f"❌ Guardian dashboard error: {e}")
    
    # Test 4: Guardian API summary
    try:
        response = requests.get(f"{base_url}/api/guardian/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Guardian summary API works: {data}")
        else:
            print(f"❌ Guardian summary API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Guardian summary API error: {e}")
    
    # Test 5: Add test credential
    test_credential = {
        "id": f"urn:uuid:test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "type": ["VerifiableCredential"],
        "issuer": "did:hedera:testnet:test-issuer",
        "issuanceDate": datetime.now().isoformat() + "Z",
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "schema:guardian-policy-v1"
        ],
        "credentialSubject": [{
            "participant_profile": {
                "summaryDescription": "Test renewable energy project",
                "sectoralScope": "Energy",
                "projectType": "Wind",
                "typeOfActivity": "Installation",
                "projectScale": "Large",
                "locationLatitude": 33.5731,
                "locationLongitude": -7.5898,
                "organizationName": "Test Energy Morocco",
                "country": "Morocco",
                "emissionReductions": 5000,
                "startDate": "2025-01-01",
                "creditingPeriods": [{"start": "2025-01-01", "end": "2030-12-31"}],
                "monitoringPeriods": [{"start": "2025-01-01", "end": "2025-12-31"}],
                "policyId": "test-policy-id",
                "guardianVersion": "3.3.0-test"
            }
        }],
        "proof": {
            "type": "Ed25519Signature2018",
            "created": datetime.now().isoformat() + "Z",
            "verificationMethod": "did:hedera:testnet:test-issuer#did-root-key",
            "proofPurpose": "assertionMethod",
            "jws": "test-signature"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/guardian/credentials",
            json=test_credential,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test credential added: {data.get('credential_uuid', 'Unknown')}")
        else:
            print(f"❌ Test credential failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Test credential error: {e}")
    
    # Test 6: List credentials
    try:
        response = requests.get(f"{base_url}/api/guardian/credentials")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Credentials list works: {data.get('count', 0)} credentials found")
        else:
            print(f"❌ Credentials list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Credentials list error: {e}")
    
    print("\n🎉 Guardian integration test completed!")
    print("📝 Next steps:")
    print("   1. Visit http://localhost:5000 for 'Become Our Partner' landing page")
    print("   2. Click 'Try Demo Account' button or sign in with password 'verifiedcc'")
    print("   3. Visit http://localhost:5000/energy for energy monitoring dashboard")
    print("   4. Visit http://localhost:5000/dashboard for Guardian credentials (after auth)")
    print("   5. Visit http://localhost:5000/demo for direct demo access")

if __name__ == "__main__":
    test_guardian_endpoints()