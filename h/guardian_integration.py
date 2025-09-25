"""
Guardian Platform Integration Module
Handles communication with Guardian API for carbon credit verification
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class GuardianClient:
    """Client for Guardian API integration"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("GUARDIAN_API_URL", "http://localhost:3000/api/v1")
        self.api_key = api_key or os.getenv("GUARDIAN_API_KEY")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def format_mrv_data(self, esp32_reading: Dict[str, Any]) -> Dict[str, Any]:
        """Format ESP32 reading for Guardian MRV submission"""
        
        # Generate unique measurement ID
        measurement_id = f"esp32-{esp32_reading['device_id']}-{int(datetime.now().timestamp())}"
        
        # Create Guardian-compatible VC document
        vc_document = {
            "id": measurement_id,
            "type": ["VerifiableCredential"],
            "issuer": f"did:hedera:testnet:esp32-{esp32_reading['device_id']}",
            "issuanceDate": esp32_reading["timestamp"],
            "@context": [
                "https://www.w3.org/2018/credentials/v1"
            ],
            "credentialSubject": [{
                "type": "energy_measurement_schema",
                "field0": str(esp32_reading["total_energy_kwh"]),  # Energy generated (kWh)
                "field1": str(esp32_reading["irradiance_w_m2"]),   # Irradiance (W/m²)
                "field2": str(esp32_reading["ambient_temp_c"]),    # Temperature (°C)
                "field3": str(esp32_reading["efficiency"]),        # Efficiency
                "field4": str(esp32_reading["power"]),             # Power (W)
                "field5": str(esp32_reading["current"]),           # Current (A)
                "field6": str(esp32_reading["voltage"]),           # Voltage (V)
                "field7": str(esp32_reading["power_factor"]),      # Power Factor
                "policyId": "esp32_solar_policy",
                "accountId": esp32_reading["device_id"]
            }]
        }
        
        return {
            "document": vc_document,
            "owner": f"did:hedera:testnet:esp32-{esp32_reading['device_id']}",
            "policyTag": "ESP32_SOLAR_MONITORING"
        }
    
    def submit_mrv_data(self, esp32_reading: Dict[str, Any]) -> Dict[str, Any]:
        """Submit MRV data to Guardian"""
        try:
            mrv_data = self.format_mrv_data(esp32_reading)
            
            response = self.session.post(
                f"{self.base_url}/external",
                json=mrv_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "MRV data submitted successfully",
                    "guardian_response": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Guardian API error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": "Connection error",
                "details": str(e)
            }
    
    def create_issue_request(self, device_id: str, energy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an issue request for carbon credits"""
        
        # Calculate reporting period (last 24 hours for demo)
        end_time = datetime.now()
        start_time = datetime.fromtimestamp(end_time.timestamp() - 86400)  # 24 hours ago
        
        # Morocco emission factor
        morocco_ef = 0.81  # tCO2/MWh
        export_efficiency = 0.98
        
        # Convert energy to MWh and calculate carbon credits
        total_energy_mwh = energy_data["total_energy_kwh"] / 1000.0
        net_export_mwh = total_energy_mwh * export_efficiency
        carbon_credits = net_export_mwh * morocco_ef
        
        issue_request = {
            "reporting_period_start": start_time.isoformat() + "Z",
            "reporting_period_end": end_time.isoformat() + "Z",
            "project_id": f"ESP32-SOLAR-{device_id}",
            "project_name": f"ESP32 Solar Monitor - {device_id}",
            "total_energy_mwh": total_energy_mwh,
            "net_export_mwh": net_export_mwh,
            "capacity_factor": (energy_data["ac_power_kw"] / 0.001) * 100 if energy_data["ac_power_kw"] > 0 else 0,
            "average_irradiance": energy_data["irradiance_w_m2"],
            "baseline_emissions_tco2": carbon_credits,
            "project_emissions_tco2": 0,
            "emission_reductions_tco2": carbon_credits,
            "carbon_credits_requested": carbon_credits
        }
        
        return issue_request
    
    def get_policy_list(self) -> Dict[str, Any]:
        """Get list of available policies"""
        try:
            response = self.session.get(f"{self.base_url}/policies")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "policies": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get policies: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_token_history(self, policy_id: str) -> Dict[str, Any]:
        """Get token history for a policy"""
        try:
            response = self.session.get(f"{self.base_url}/policies/{policy_id}/tokens")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "tokens": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get token history: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

# Example usage functions
def demo_guardian_integration():
    """Demo function showing Guardian integration"""
    
    # Sample ESP32 reading
    sample_reading = {
        "device_id": "ESP32-001",
        "timestamp": datetime.now().isoformat() + "Z",
        "current": 2.5,
        "voltage": 220.0,
        "power": 550.0,
        "ac_power_kw": 0.55,
        "total_energy_kwh": 1.234,
        "grid_frequency_hz": 50.0,
        "power_factor": 0.95,
        "ambient_temp_c": 25.5,
        "irradiance_w_m2": 850.0,
        "system_status": 1,
        "efficiency": 0.96
    }
    
    # Initialize Guardian client
    guardian = GuardianClient()
    
    # Format MRV data
    mrv_data = guardian.format_mrv_data(sample_reading)
    print("MRV Data formatted for Guardian:")
    print(json.dumps(mrv_data, indent=2))
    
    # Create issue request
    issue_request = guardian.create_issue_request("ESP32-001", sample_reading)
    print("\nIssue Request:")
    print(json.dumps(issue_request, indent=2))

if __name__ == "__main__":
    demo_guardian_integration()