#!/usr/bin/env python3
"""
MRV Sender Client
Handles communication with the local mrv-sender service
"""

import requests
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MRVSenderClient:
    """Client for interacting with local mrv-sender service"""
    
    def __init__(self, base_url: str = "http://localhost:3005"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_health(self) -> bool:
        """Check if mrv-sender service is running"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def send_mrv_data(self, data: Dict[str, Any]) -> bool:
        """Send MRV data to mrv-sender service"""
        try:
            response = self.session.post(
                f"{self.base_url}/mrv-generate",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info("Successfully sent data to mrv-sender")
                logger.info(f"Response: {response.text}")
                return True
            else:
                logger.error(f"MRV sender request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"MRV sender error: {e}")
            return False

if __name__ == "__main__":
    # Test the MRV sender client
    client = MRVSenderClient()
    
    if client.check_health():
        print("✅ MRV Sender service is running!")
        
        test_data = {
            "field0": "TEST_PROJECT_456",
            "field1": "Grid connected renewable electricity generation",
            "field6": "2500.75"
        }
        
        if client.send_mrv_data(test_data):
            print("✅ Test data sent to MRV Sender successfully!")
        else:
            print("❌ Failed to send test data to MRV Sender")
    else:
        print("❌ MRV Sender service is not running. Please start it first.")