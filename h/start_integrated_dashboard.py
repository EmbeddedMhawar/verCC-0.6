#!/usr/bin/env python3
"""
Start Integrated Dashboard
Starts the dashboard with AMS-I.D integration
"""

import os
import sys
import uvicorn
from main import app

def main():
    """Start the integrated dashboard"""
    print("🌱 Starting VerifiedCC Dashboard with AMS-I.D Integration")
    print("=" * 60)
    print("🔧 Features:")
    print("   ✅ ESP32 Real-time Monitoring")
    print("   ✅ Guardian Tools Architecture")
    print("   ✅ AMS-I.D Automatic Aggregation")
    print("   ✅ Carbon Credit Generation")
    print("   ✅ Supabase Data Storage")
    print()
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 5000))
    
    print(f"🚀 Dashboard URL: http://localhost:{port}")
    print(f"📊 ESP32 Endpoint: http://localhost:{port}/api/energy-data")
    print(f"🌱 AMS-I.D Status: http://localhost:{port}/api/ams-id/status")
    print(f"📋 Health Check: http://localhost:{port}/health")
    print()
    print("🎯 AMS-I.D Integration Features:")
    print("   • Automatic data aggregation every 24 hours")
    print("   • Guardian policy compliance (AMS-I.D)")
    print("   • Real-time carbon credit calculation")
    print("   • Manual workflow triggers via dashboard")
    print("   • Activity logging and status monitoring")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()