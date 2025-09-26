#!/usr/bin/env python3
"""
AMS-I.D Aggregator Startup Script
Easy way to start the complete AMS-I.D aggregation system
"""

import sys
import time
import argparse
from esp32_ams_integration import ESP32AMSIntegration
from ams_id_aggregator import AMSIDConfig
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ams_aggregator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='AMS-I.D Aggregation System')
    parser.add_argument('--config', default='ams_config.json', help='Configuration file path')
    parser.add_argument('--test', action='store_true', help='Run in test mode with faster intervals')
    parser.add_argument('--dry-run', action='store_true', help='Run without submitting to Guardian')
    
    args = parser.parse_args()
    
    print("🌱 AMS-I.D Automatic Aggregation System")
    print("=" * 50)
    
    try:
        # Load configuration
        config = AMSIDConfig.from_file(args.config)
        
        # Adjust intervals for test mode
        if args.test:
            print("🧪 Running in TEST MODE with faster intervals")
            config.aggregation_interval_hours = 1  # 1 hour instead of 24
            esp32_interval = 60  # 1 minute instead of 5 minutes
        else:
            esp32_interval = 300  # 5 minutes
        
        # Create integration instance
        integration = ESP32AMSIntegration(
            ams_config=config,
            esp32_data_interval=esp32_interval
        )
        
        # Initialize system
        print("🔧 Initializing system...")
        if not integration.initialize():
            print("❌ System initialization failed!")
            sys.exit(1)
        
        print("✅ System initialized successfully!")
        
        # Display configuration
        print(f"\n📋 Configuration:")
        print(f"   Guardian URL: {config.guardian_base_url}")
        print(f"   Policy ID: {config.policy_id}")
        print(f"   Aggregation Interval: {config.aggregation_interval_hours} hours")
        print(f"   ESP32 Data Interval: {esp32_interval} seconds")
        print(f"   Minimum Data Points: {config.min_data_points}")
        
        if args.dry_run:
            print("   🔒 DRY RUN MODE: No data will be submitted to Guardian")
        
        # Start the system
        print("\n🚀 Starting AMS-I.D aggregation system...")
        integration.start()
        
        print("✅ System started successfully!")
        print("\n📊 System Status:")
        print("   - Collecting ESP32 data continuously")
        print("   - Aggregating data every hour" if args.test else "   - Aggregating data every 24 hours")
        print("   - Submitting to Guardian automatically")
        print("\nPress Ctrl+C to stop the system")
        
        # Monitor system
        try:
            while True:
                time.sleep(60)  # Check every minute
                
                status = integration.get_status()
                
                # Print status update every 10 minutes
                if int(time.time()) % 600 == 0:
                    print(f"\n📈 Status Update ({time.strftime('%H:%M:%S')}):")
                    print(f"   Running: {'✅' if status['running'] else '❌'}")
                    print(f"   Measurements in buffer: {status['measurements_in_buffer']}")
                    print(f"   Guardian authenticated: {'✅' if status['guardian_authenticated'] else '❌'}")
                    
                    if status['last_measurement_time']:
                        print(f"   Last measurement: {status['last_measurement_time']}")
                
                # Force aggregation in test mode when we have enough data
                if args.test and status['measurements_in_buffer'] >= 5:
                    print("\n🔄 Forcing aggregation cycle (test mode)...")
                    if integration.force_aggregation():
                        print("✅ Aggregation successful!")
                    else:
                        print("❌ Aggregation failed!")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down system...")
            integration.stop()
            print("✅ System stopped successfully!")
            
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"💥 System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()