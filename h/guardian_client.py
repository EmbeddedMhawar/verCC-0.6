#!/usr/bin/env python3
"""
Guardian API Client for MRV Reporting
Handles authentication and API interactions with Guardian service
"""

import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GuardianConfig:
    """Configuration for Guardian API"""
    base_url: str = "https://guardianservice.app/api/v1"
    username: str = "Mhawar"
    password: str = "Mhawar2001'"
    tenant_id: str = "68cc28cc348f53cc0b247ce4"
    policy_id: str = "68d5ba75152381fe552b1c6d"
    block_id: str = "1021939c-b948-4732-bd5f-90cc4ae1cd50"
    schema_id: str = "3b99fd4b-8285-4b91-a84f-99ecec076f4b"

class GuardianClient:
    """Client for interacting with Guardian API"""
    
    def __init__(self, config: GuardianConfig):
        self.config = config
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def login(self) -> bool:
        """Authenticate with Guardian and get refresh token"""
        try:
            login_data = {
                "username": self.config.username,
                "password": self.config.password,
                "tenantId": self.config.tenant_id
            }
            
            response = self.session.post(
                f"{self.config.base_url}/accounts/login",
                headers={"Content-Type": "application/json"},
                json=login_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.refresh_token = result.get("refreshToken")
                logger.info("Successfully logged in to Guardian")
                return True
            else:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def get_access_token(self) -> bool:
        """Get access token using refresh token"""
        if not self.refresh_token:
            logger.error("No refresh token available. Please login first.")
            return False
        
        try:
            token_data = {"refreshToken": self.refresh_token}
            
            response = self.session.post(
                f"{self.config.base_url}/accounts/access-token",
                headers={"Content-Type": "application/json"},
                json=token_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("accessToken")
                logger.info("Successfully obtained access token")
                return True
            else:
                logger.error(f"Access token request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Access token error: {e}")
            return False
    
    def submit_monitoring_report(self, report_data: Dict[str, Any]) -> bool:
        """Submit monitoring report to Guardian"""
        if not self.access_token:
            logger.error("No access token available. Please authenticate first.")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            endpoint = f"{self.config.base_url}/policies/{self.config.policy_id}/blocks/{self.config.block_id}/external"
            
            response = self.session.post(
                endpoint,
                headers=headers,
                json=report_data
            )
            
            if response.status_code in [200, 201]:
                logger.info("Successfully submitted monitoring report")
                logger.info(f"Response: {response.text}")
                return True
            else:
                logger.error(f"Report submission failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Report submission error: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Complete authentication flow"""
        if self.login() and self.get_access_token():
            return True
        return False

if __name__ == "__main__":
    # Test the Guardian client
    config = GuardianConfig()
    client = GuardianClient(config)
    
    if client.authenticate():
        print("✅ Guardian authentication successful!")
        
        # Test data for monitoring report
        test_report = {
            "field0": "TEST_PROJECT_123",
            "field1": "Option A - Grid connected renewable electricity generation",
            "field6": "1000.5"
        }
        
        if client.submit_monitoring_report(test_report):
            print("✅ Test monitoring report submitted successfully!")
        else:
            print("❌ Failed to submit test monitoring report")
    else:
        print("❌ Guardian authentication failed!")