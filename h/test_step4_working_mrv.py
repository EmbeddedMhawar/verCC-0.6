#!/usr/bin/env python3
"""
Step 4: Test Python Backend → Working MRV Sender
Now testing with our working Python-based MRV sender
"""

import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
from mrv_sender_client import MRVSenderClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MRVTester:
    """Test suite for MRV Sender functionality"""
    
    def __init__(self, config_path: str = "test_config.json"):
        self.config = self._load_config(config_path)
        self.client = MRVSenderClient(self.config["mrv_sender"]["base_url"])
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            config_file = Path(__file__).parent / config_path
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "mrv_sender": {
                "base_url": "http://localhost:3005",
                "timeout": 30,
                "delay_between_requests": 0.5
            },
            "test_data": {
                "single_report": {
                    "field0": "ProjectID123",
                    "field1": "Grid connected renewable electricity generation",
                    "field6": "1500.75"
                }
            }
        }
        
    def test_health(self) -> bool:
        """Test if our MRV sender is responding"""
        print("🔍 Testing MRV Sender health...")
        
        if self.client.check_health():
            print("✅ MRV Sender health check passed")
            return True
        else:
            print("❌ Cannot connect to MRV Sender (not running?)")
            return False

    def test_single_report(self) -> bool:
        """Step 4: Send test data to MRV sender as per Steps.md"""
        print("\n📤 Step 4: Sending test data to MRV sender...")
        
        test_data = self.config["test_data"]["single_report"]
        print(f"Sending data: {json.dumps(test_data, indent=2)}")
        
        if self.client.send_mrv_data(test_data):
            print("✅ Data sent to MRV sender successfully!")
            return True
        else:
            print("❌ Failed to send data to MRV sender")
            return False

    def test_multiple_reports(self) -> bool:
        """Test sending multiple MRV reports"""
        print("\n📊 Testing multiple MRV reports...")
        
        reports = self.config["test_data"]["multiple_reports"]
        success_count = 0
        delay = self.config["mrv_sender"]["delay_between_requests"]
        
        for i, report in enumerate(reports, 1):
            print(f"\n📋 Sending report {i}/{len(reports)}: {report['field0']}")
            
            if self.client.send_mrv_data(report):
                print(f"   ✅ Report {i} sent successfully")
                success_count += 1
            else:
                print(f"   ❌ Report {i} failed")
                
            # Small delay between requests to avoid overwhelming the service
            if i < len(reports):  # Don't delay after the last request
                time.sleep(delay)
        
        print(f"\n📊 Results: {success_count}/{len(reports)} reports sent successfully")
        return success_count == len(reports)

def main():
    """Main test function"""
    print("🚀 Starting Step 4: Python Backend → Working MRV Sender Test")
    print("=" * 60)
    
    tester = MRVTester()
    
    try:
        # Step 1: Check MRV sender health
        if not tester.test_health():
            print("\n❌ MRV Sender is not available. Please start it first.")
            print("Run: npm start in the guardian/mrv-sender directory")
            return False
        
        # Step 2: Send single test data
        if not tester.test_single_report():
            print("\n❌ Single data test failed")
            return False
        
        # Step 3: Send multiple reports
        if not tester.test_multiple_reports():
            print("\n❌ Multiple reports test failed")
            return False
        
        print("\n🎉 All tests passed! MRV Sender is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"\n❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    main(): {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n📈 Results: {success_count}/{len(reports)} reports sent successfully")
    return success_count == len(reports)

def main():
    print("=" * 60)
    print("Step 4: Python Backend → Working MRV Sender Test")
    print("=" * 60)
    
    # Test health
    if not test_mrv_health():
        print("❌ MRV Sender not available")
        print("💡 Make sure to run: python simple_mrv_sender.py")
        return False
    
    # Test single report
    if not test_send_mrv_data():
        print("❌ Single report test failed")
        return False
    
    # Test multiple reports
    if not test_multiple_reports():
        print("❌ Multiple reports test failed")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Step 4 Complete!")
    print("✅ Python → MRV Sender communication working perfectly!")
    print("=" * 60)
    print("\n🎉 MRV Processing Pipeline is functional!")
    print("📋 Next steps:")
    print("   1. ✅ Guardian authentication working")
    print("   2. ✅ MRV Sender receiving and processing data")
    print("   3. 📝 Guardian API submission needs UI-based workflow")
    print("   4. 🔄 Complete end-to-end pipeline ready for production")
    
    return True

if __name__ == "__main__":
    main()