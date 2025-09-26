#!/usr/bin/env python3
"""
Complete System Startup
Launches the integrated ESP32 Dashboard + Guardian Tools system
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_mrv_sender():
    """Start the MRV sender service"""
    print("🚀 Starting MRV Sender...")
    
    try:
        # Start without capturing output so it can run properly
        process = subprocess.Popen(
            [sys.executable, "simple_mrv_sender.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Wait a moment to check if it started
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ MRV Sender started successfully on http://localhost:3005")
            return process
        else:
            print("❌ MRV Sender failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting MRV Sender: {e}")
        return None

def start_dashboard():
    """Start the main ESP32 dashboard with Guardian integration"""
    print("🚀 Starting ESP32 Dashboard with Guardian Tools...")
    
    try:
        # Start without capturing output so it can run properly
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Wait a moment to check if it started
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Dashboard started successfully on http://localhost:5000")
            return process
        else:
            print("❌ Dashboard failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Dashboard: {e}")
        return None

def check_services():
    """Check if services are running"""
    print("\n🔍 Checking services...")
    
    import requests
    
    # Check MRV Sender
    try:
        response = requests.get("http://localhost:3005/health", timeout=5)
        if response.status_code == 200:
            print("✅ MRV Sender: Online")
        else:
            print("⚠️ MRV Sender: Responding but not healthy")
    except:
        print("❌ MRV Sender: Offline")
    
    # Check Dashboard
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard: Online")
        else:
            print("⚠️ Dashboard: Responding but not healthy")
    except:
        print("❌ Dashboard: Offline")

def main():
    print("=" * 60)
    print("🛡️ GUARDIAN TOOLS COMPLETE SYSTEM STARTUP")
    print("=" * 60)
    
    print("\nStarting integrated system:")
    print("- ESP32 Dashboard with Guardian Tools Architecture")
    print("- MRV Sender for Guardian integration")
    print("- Real-time monitoring and processing")
    
    processes = []
    
    try:
        # Start MRV Sender first
        mrv_process = start_mrv_sender()
        if mrv_process:
            processes.append(mrv_process)
        
        # Wait a bit for MRV sender to fully start
        time.sleep(2)
        
        # Start Dashboard
        dashboard_process = start_dashboard()
        if dashboard_process:
            processes.append(dashboard_process)
        
        # Wait for services to start
        time.sleep(5)
        
        # Check services
        check_services()
        
        print("\n" + "=" * 60)
        print("🎉 SYSTEM STARTUP COMPLETE")
        print("=" * 60)
        
        print("\n📋 ACCESS POINTS:")
        print("🌐 ESP32 Dashboard:     http://localhost:5000")
        print("🛡️ Guardian Dashboard:  http://localhost:5000/guardian")
        print("🔧 MRV Sender:          http://localhost:3005")
        print("📊 System Health:       http://localhost:5000/health")
        print("🔗 Guardian Status:     http://localhost:5000/api/guardian/status")
        
        print("\n📡 ESP32 ENDPOINT:")
        print("POST http://localhost:5000/api/energy-data")
        
        print("\n🔄 GUARDIAN TOOLS WORKFLOW:")
        print("1. ESP32 sends data → Tool 10 (Data Source)")
        print("2. System aggregates → Tool 07 (Aggregation)")
        print("3. Creates hash → Tool 03 (Hedera)")
        print("4. Submits MRV → Guardian → Token Minting")
        
        print("\n🧪 TESTING:")
        print("Run: python test_complete_integration.py")
        
        print("\n⚠️ IMPORTANT:")
        print("- Keep this terminal open to maintain services")
        print("- Press Ctrl+C to stop all services")
        print("- Check logs above for any startup errors")
        
        # Keep running
        print("\n🔄 Services running... Press Ctrl+C to stop")
        
        while True:
            time.sleep(10)
            
            # Check if processes are still running
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"⚠️ Process {i} has stopped unexpectedly")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        
        for process in processes:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ All services stopped")
        
    except Exception as e:
        print(f"\n❌ System error: {e}")
        
        # Clean up processes
        for process in processes:
            if process and process.poll() is None:
                process.terminate()

if __name__ == "__main__":
    main()