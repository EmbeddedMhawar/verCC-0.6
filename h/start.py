#!/usr/bin/env python3
"""
Startup script for ESP32 Carbon Credit Backend
"""

import subprocess
import sys
import os
import time

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import supabase
        import pydantic
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ Environment file found")
        return True
    else:
        print("⚠️  No .env file found")
        print("📝 Please copy .env.example to .env and configure your Supabase credentials")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting ESP32 Carbon Credit Backend...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔌 ESP32 should send data to: http://your-ip:5000/api/energy-data")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    try:
        # Start the server
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server error: {e}")

def main():
    """Main startup function"""
    print("🌞 ESP32 Carbon Credit Backend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    env_ok = check_env_file()
    
    if not env_ok:
        response = input("\n❓ Continue without Supabase? (y/N): ")
        if response.lower() != 'y':
            print("👋 Setup your .env file and try again")
            sys.exit(1)
        print("⚠️  Running without Supabase - data will only be stored in memory")
    
    print("\n" + "=" * 50)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()