#!/usr/bin/env python3
"""
Step 4: Test Python Backend Sends Data to mrv-sender
Following Steps.md exactly:
- Start mrv-sender
- Send test data to http://localhost:3005/mrv-generate
- Verify response
"""

import subprocess
import time
import requests
import json
from pathlib import Path
import threading
import sys

class MRVSenderManager:
    """Manage mrv-sender process"""
    
    def __init__(self):
        self.process = None
        self.mrv_sender_dir = Path("guardian/mrv-sender")
        
    def start(self):
        """Start mrv-sender in background"""
        print("🚀 Starting mrv-sender...")
        
        try:
            self.process = subprocess.Popen(
                ["npm", "start"], 
                cwd=self.mrv_sender_dir,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True, shell=True
            )
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Check if it's running
            if self.process.poll() is None:
                print("✅ mrv-sender started successfully")
                return True
            else:
                stdout, stderr = self.process.communicate()
                print(f"❌ mrv-sender failed to start:")
                print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting mrv-sender: {e}")
            return False
    
    def stop(self):
        """Stop mrv-sender"""
        if self.process:
            print("🛑 Stopping mrv-sender...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✅ mrv-sender stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("✅ mrv-sender force stopped")

def test_mrv_health():
    """Test if mrv-sender is responding"""
    print("🔍 Testing mrv-sender health...")
    
    try:
        response = requests.get("http://localhost:3005/health", timeout=5)
        if response.status_code == 200:
            print("✅ mrv-sender health check passed")
            return True
        else:
            print(f"⚠️  mrv-sender health check returned: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to mrv-sender (not running?)")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_send_mrv_data():
    """Step 4: Send test data to mrv-sender as per Steps.md"""
    print("\n📤 Step 4: Sending test data to mrv-sender...")
    
    # Test data as specified in Steps.md
    data = {
        "field0": "ProjectID123",  # Map to schema
        "field1": "Grid connected renewable electricity generation",
        "field6": "1500.75"  # Emission reductions
    }
    
    print(f"Sending data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:3005/mrv-generate", 
            json=data,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Data sent to mrv-sender successfully!")
            return True
        else:
            print(f"❌ mrv-sender returned error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to mrv-sender")
        return False
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return False

def main():
    print("=" * 60)
    print("Step 4: Python Backend → mrv-sender Test")
    print("=" * 60)
    
    # Start mrv-sender
    mrv_manager = MRVSenderManager()
    
    try:
        if not mrv_manager.start():
            print("❌ Cannot start mrv-sender")
            return False
        
        # Wait a bit more for full startup
        print("⏳ Waiting for mrv-sender to fully initialize...")
        time.sleep(5)
        
        # Test health
        if not test_mrv_health():
            print("❌ mrv-sender health check failed")
            return False
        
        # Test sending data
        if not test_send_mrv_data():
            print("❌ Data sending failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Step 4 Complete!")
        print("✅ Python → mrv-sender communication working!")
        print("=" * 60)
        print("\n📋 Ready for Step 5: mrv-sender → Guardian")
        
        return True
        
    finally:
        # Always stop mrv-sender
        mrv_manager.stop()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)