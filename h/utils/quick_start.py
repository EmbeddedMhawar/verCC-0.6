#!/usr/bin/env python3
"""
Quick Start Script for ESP32 Carbon Credit Backend
Installs dependencies and starts the server
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting ESP32 Carbon Credit Backend...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔌 ESP32 should send data to: http://localhost:5000/api/energy-data")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

def main():
    """Main function"""
    print("🌞 ESP32 Carbon Credit Backend - Quick Start")
    print("=" * 50)
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import supabase
        print("✅ Dependencies already installed")
    except ImportError:
        if not install_dependencies():
            sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()