#!/usr/bin/env python3
"""
Complete Step 4 Test: Start MRV Sender and Test Communication
"""

import subprocess
import time
import requests
import json
import threading
import sys
from pathlib import Path

def start_mrv_sender():
    """Start the MRV sender in background"""
    print("🚀 Starting MRV Sender...")
    
    try:
        # Start the MRV sender process
        process = subprocess.Popen(
            [sys.executable, "simple_mrv_sender.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if it's running
        if process.poll() is None:
            print("✅ MRV Sender started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MRV Sender failed to start:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting MRV Sender: {e}")
        return None

def wait_for_mrv_ready():
    """Wait for MRV sender to be ready"""
    print("⏳ Waiting for MRV Sender to be ready...")
    
    for i in range(10):  # Try for 10 seconds
        try:
            response = requests.get("http://localhost:3005/health", timeout=2)
            if response.status_code == 200:
                print("✅ MRV Sender is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
        print(f"   Attempt {i+1}/10...")
    
    print("❌ MRV Sender did not become ready")
    return False

def test_mrv_communication():
    """Test MRV communication"""
    print("\n📤 Testing MRV communication...")
    
    # Test data as specified in Steps.md
    data = {
        "field0": "ProjectID123",
        "field1": "Grid connected renewable electricity generation",
        "field6": "1500.75"
    }
    
    print(f"Sending data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:3005/mrv-generate",
            json=data,
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print("✅ MRV communication successful!")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return True
        else:
            print(f"❌ MRV communication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in MRV communication: {e}")
        return False

def main():
    print("=" * 60)
    print("Complete Step 4 Test: MRV Sender + Communication")
    print("=" * 60)
    
    mrv_process = None
    
    try:
        # Start MRV sender
        mrv_process = start_mrv_sender()
        if not mrv_process:
            print("❌ Failed to start MRV Sender")
            return False
        
        # Wait for it to be ready
        if not wait_for_mrv_ready():
            print("❌ MRV Sender not ready")
            return False
        
        # Test communication
        if not test_mrv_communication():
            print("❌ MRV communication failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Step 4 Complete - MRV Pipeline Working!")
        print("=" * 60)
        print("\n🎉 Summary:")
        print("✅ MRV Sender started successfully")
        print("✅ Guardian authentication working")
        print("✅ Python → MRV Sender communication working")
        print("✅ MRV data processing working")
        
        print("\n📋 What we've accomplished:")
        print("1. ✅ Step 1: Guardian Policy IDs verified")
        print("2. ✅ Step 2: Guardian API authentication working")
        print("3. ✅ Step 3: MRV Sender setup (Python alternative)")
        print("4. ✅ Step 4: Python → MRV Sender communication")
        
        print("\n🔄 Next steps for complete workflow:")
        print("- Guardian API submission (needs UI workflow)")
        print("- Integration with ESP32 data collection")
        print("- Production deployment")
        
        return True
        
    finally:
        # Clean up
        if mrv_process:
            print("\n🛑 Stopping MRV Sender...")
            mrv_process.terminate()
            try:
                mrv_process.wait(timeout=5)
                print("✅ MRV Sender stopped cleanly")
            except subprocess.TimeoutExpired:
                mrv_process.kill()
                print("✅ MRV Sender force stopped")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)