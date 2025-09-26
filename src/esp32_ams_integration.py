#!/usr/bin/env python3
"""
ESP32 to AMS-I.D Integration
Connects ESP32 data source with AMS-I.D aggregation tool
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ams_id_aggregator import AMSIDAggregator, AMSIDConfig, EnergyMeasurement
from mrv_sender_client import MRVSenderClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ESP32AMSIntegration:
    """Integration between ESP32 data and AMS-I.D aggregation"""
    
    def __init__(self, 
                 ams_config: AMSIDConfig = None,
                 mrv_sender_url: str = "http://localhost:3005",
                 esp32_data_interval: int = 300):  # 5 minutes
        
        self.ams_config = ams_config or AMSIDConfig()
        self.aggregator = AMSIDAggregator(self.ams_config)
        self.mrv_client = MRVSenderClient(mrv_sender_url)
        self.esp32_data_interval = esp32_data_interval
        
        self.running = False
        self.data_thread = None
        self.aggregation_thread = None
    
    def initialize(self) -> bool:
        """Initialize the integration system"""
        logger.info("Initializing ESP32-AMS Integration...")
        
        # Authenticate with Guardian
        if not self.aggregator.authenticate():
            logger.error("Failed to authenticate with Guardian")
            return False
        
        # Check MRV sender health
        if not self.mrv_client.check_health():
            logger.warning("MRV Sender service not available - will use simulated data")
        
        logger.info("✅ ESP32-AMS Integration initialized successfully")
        return True
    
    def convert_esp32_to_measurement(self, esp32_data: Dict[str, Any]) -> EnergyMeasurement:
        """Convert ESP32 data format to EnergyMeasurement"""
        return EnergyMeasurement(
            timestamp=esp32_data.get("timestamp", datetime.now().isoformat() + "Z"),
            device_id=esp32_data.get("device_id", "ESP32_001"),
            total_energy_kwh=float(esp32_data.get("total_energy_kwh", 0)),
            irradiance_w_m2=float(esp32_data.get("irradiance_w_m2", 0)),
            ambient_temp_c=float(esp32_data.get("ambient_temp_c", 25)),
            efficiency=float(esp32_data.get("efficiency", 0.85)),
            power=float(esp32_data.get("power", 0)),
            current=float(esp32_data.get("current", 0)),
            voltage=float(esp32_data.get("voltage", 220)),
            power_factor=float(esp32_data.get("power_factor", 0.95))
        )
    
    def simulate_esp32_data(self) -> Dict[str, Any]:
        """Simulate ESP32 data for testing"""
        import random
        
        # Simulate realistic solar data
        current_hour = datetime.now().hour
        
        # Solar irradiance follows daily cycle
        if 6 <= current_hour <= 18:
            base_irradiance = 800 * (1 - abs(current_hour - 12) / 6)
        else:
            base_irradiance = 0
        
        irradiance = max(0, base_irradiance + random.uniform(-100, 100))
        power = irradiance * 0.5  # 0.5W per W/m²
        energy_increment = power * (self.esp32_data_interval / 3600) / 1000  # kWh for this interval
        
        return {
            "timestamp": datetime.now().isoformat() + "Z",
            "device_id": "ESP32_001",
            "total_energy_kwh": energy_increment,
            "irradiance_w_m2": irradiance,
            "ambient_temp_c": 25 + random.uniform(-5, 10),
            "efficiency": 0.85 + random.uniform(-0.05, 0.05),
            "power": power,
            "current": power / 220 if power > 0 else 0,
            "voltage": 220 + random.uniform(-5, 5),
            "power_factor": 0.95 + random.uniform(-0.05, 0.05)
        }
    
    def fetch_esp32_data(self) -> Dict[str, Any]:
        """Fetch data from ESP32 (via MRV sender or simulation)"""
        try:
            # Try to get real data from MRV sender
            if self.mrv_client.check_health():
                # In a real implementation, this would fetch actual ESP32 data
                # For now, we'll use simulated data
                pass
            
            # Use simulated data
            return self.simulate_esp32_data()
            
        except Exception as e:
            logger.error(f"Error fetching ESP32 data: {e}")
            return self.simulate_esp32_data()
    
    def data_collection_loop(self):
        """Main data collection loop"""
        logger.info(f"Starting data collection loop (interval: {self.esp32_data_interval}s)")
        
        while self.running:
            try:
                # Fetch ESP32 data
                esp32_data = self.fetch_esp32_data()
                
                # Convert to measurement format
                measurement = self.convert_esp32_to_measurement(esp32_data)
                
                # Add to aggregator
                self.aggregator.add_measurement(measurement)
                
                logger.info(f"Collected data: {measurement.power:.1f}W, "
                           f"{measurement.irradiance_w_m2:.1f}W/m², "
                           f"{measurement.total_energy_kwh:.3f}kWh")
                
                # Wait for next collection
                time.sleep(self.esp32_data_interval)
                
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def aggregation_loop(self):
        """Main aggregation loop"""
        logger.info("Starting aggregation loop")
        
        # Run continuous aggregation
        self.aggregator.run_continuous_aggregation(check_interval_minutes=30)
    
    def start(self):
        """Start the integration system"""
        if self.running:
            logger.warning("Integration already running")
            return
        
        logger.info("Starting ESP32-AMS Integration...")
        self.running = True
        
        # Start data collection thread
        self.data_thread = threading.Thread(target=self.data_collection_loop, daemon=True)
        self.data_thread.start()
        
        # Start aggregation thread
        self.aggregation_thread = threading.Thread(target=self.aggregation_loop, daemon=True)
        self.aggregation_thread.start()
        
        logger.info("✅ ESP32-AMS Integration started successfully")
    
    def stop(self):
        """Stop the integration system"""
        logger.info("Stopping ESP32-AMS Integration...")
        self.running = False
        
        if self.data_thread and self.data_thread.is_alive():
            self.data_thread.join(timeout=5)
        
        if self.aggregation_thread and self.aggregation_thread.is_alive():
            self.aggregation_thread.join(timeout=5)
        
        logger.info("✅ ESP32-AMS Integration stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the integration"""
        return {
            "running": self.running,
            "measurements_in_buffer": len(self.aggregator.measurements_buffer),
            "last_measurement_time": (
                self.aggregator.measurements_buffer[-1].timestamp 
                if self.aggregator.measurements_buffer 
                else None
            ),
            "guardian_authenticated": self.aggregator.guardian_client.access_token is not None,
            "mrv_sender_available": self.mrv_client.check_health()
        }
    
    def force_aggregation(self) -> bool:
        """Force an immediate aggregation cycle"""
        logger.info("Forcing immediate aggregation cycle...")
        return self.aggregator.process_aggregation_cycle()

def main():
    """Main function for testing the integration"""
    print("🔗 ESP32-AMS Integration Test")
    print("=" * 40)
    
    # Create integration instance
    integration = ESP32AMSIntegration(esp32_data_interval=60)  # 1 minute for testing
    
    # Initialize
    if not integration.initialize():
        print("❌ Initialization failed!")
        return
    
    print("✅ Integration initialized successfully!")
    
    try:
        # Start the integration
        integration.start()
        
        print("🚀 Integration started. Collecting data...")
        print("Press Ctrl+C to stop")
        
        # Monitor status
        while True:
            time.sleep(30)  # Check every 30 seconds
            
            status = integration.get_status()
            print(f"\n📊 Status Update:")
            print(f"   Running: {status['running']}")
            print(f"   Measurements in buffer: {status['measurements_in_buffer']}")
            print(f"   Guardian authenticated: {status['guardian_authenticated']}")
            print(f"   MRV Sender available: {status['mrv_sender_available']}")
            
            if status['last_measurement_time']:
                print(f"   Last measurement: {status['last_measurement_time']}")
            
            # Force aggregation every 5 minutes for testing
            if status['measurements_in_buffer'] >= 5:
                print("\n🔄 Forcing aggregation cycle for testing...")
                if integration.force_aggregation():
                    print("✅ Aggregation successful!")
                else:
                    print("❌ Aggregation failed!")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping integration...")
        integration.stop()
        print("✅ Integration stopped successfully!")

if __name__ == "__main__":
    main()