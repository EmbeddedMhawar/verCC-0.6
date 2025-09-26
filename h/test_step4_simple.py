#!/usr/bin/env python3
"""
Simple Step 4 Test: Test MRV Communication
Run this while simple_mrv_sender.py is running in another terminal
"""

import requests
import json

def test_mrv_health():
    """Test MRV sender health"""
    print("Testing MRV Sender health...")
    
    try:
        response = requests.get("http://localhost:3005/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("MRV Sender health check passed")
            print(f"Status: {health_data.get('status')}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to MRV Sender")
        print("Make sure to run: python simple_mrv_sender.py")
        return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_mrv_data():
    """Test sending MRV data"""
    print("\nTesting MRV data submission...")
    
    # Test data from Steps.md
    data = {
        "field0": "ProjectID123",
        "field1": "Grid connected renewable electricity generation",
        "field6": "1500.75"
    }
    
    print(f"Sending: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:3005/mrv-generate",
            json=data,
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print("MRV data submission successful!")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return True
        else:
            print(f"MRV submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending MRV data: {e}")
        return False

def main():
    print("=" * 60)
    print("Step 4: Python Backend -> MRV Sender Test")
    print("=" * 60)
    
    # Test health
    if not test_mrv_health():
        return False
    
    # Test data submission
    if not test_mrv_data():
        return False
    
    print("\n" + "=" * 60)
    print("Step 4 Complete!")
    print("Python -> MRV Sender communication working!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main()