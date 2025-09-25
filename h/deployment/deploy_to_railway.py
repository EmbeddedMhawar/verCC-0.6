#!/usr/bin/env python3
"""
Railway Deployment Script for ESP32 Carbon Credit Backend
Automated deployment with Supabase integration
"""

import subprocess
import sys
import os
import time

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI")
        print("Please install manually: npm install -g @railway/cli")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js first")
        return False

def railway_login():
    """Login to Railway"""
    try:
        result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Already logged in to Railway: {result.stdout.strip()}")
            return True
        else:
            print("🔐 Please login to Railway...")
            subprocess.run(['railway', 'login'], check=True)
            return True
    except subprocess.CalledProcessError:
        print("❌ Railway login failed")
        return False

def create_railway_project():
    """Create or initialize Railway project"""
    print("🚂 Initializing Railway project...")
    try:
        # Check if already initialized
        if os.path.exists('.railway'):
            print("✅ Railway project already initialized")
            return True
        
        # Initialize new project
        subprocess.run(['railway', 'init'], check=True)
        print("✅ Railway project initialized")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to initialize Railway project")
        return False

def set_environment_variables():
    """Set environment variables in Railway"""
    print("🔑 Setting environment variables...")
    
    # Your Supabase credentials
    env_vars = {
        'SUPABASE_URL': 'https://smemwzfjwhktvtqtdwta.supabase.co',
        'SUPABASE_ANON_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNtZW13emZqd2hrdHZ0cXRkd3RhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NDc1NjAsImV4cCI6MjA3NDIyMzU2MH0.aH_a78ryFXc7SvNhrGpXQTr93Ss4JnDF7yNWmpbhQT0',
        'GUARDIAN_API_URL': 'http://localhost:3000/api/v1'
    }
    
    try:
        for key, value in env_vars.items():
            subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
            print(f"✅ Set {key}")
        
        print("✅ All environment variables set")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set environment variables: {e}")
        return False

def deploy_to_railway():
    """Deploy the application to Railway"""
    print("🚀 Deploying to Railway...")
    try:
        # Deploy with detached mode
        result = subprocess.run(['railway', 'up', '--detach'], capture_output=True, text=True, check=True)
        print("✅ Deployment initiated successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print(e.stderr)
        return False

def get_deployment_url():
    """Get the deployment URL"""
    print("🌐 Getting deployment URL...")
    try:
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True, check=True)
        print("📊 Deployment status:")
        print(result.stdout)
        
        # Try to get the URL
        url_result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if url_result.returncode == 0 and url_result.stdout.strip():
            url = url_result.stdout.strip()
            print(f"🌐 Your app is deployed at: {url}")
            return url
        else:
            print("⏳ URL will be available once deployment completes")
            return None
    except subprocess.CalledProcessError:
        print("❌ Failed to get deployment status")
        return None

def monitor_deployment():
    """Monitor deployment logs"""
    print("📝 Monitoring deployment (press Ctrl+C to stop)...")
    try:
        subprocess.run(['railway', 'logs', '--follow'])
    except KeyboardInterrupt:
        print("\n✅ Stopped monitoring logs")

def main():
    """Main deployment function"""
    print("🚂 ESP32 Carbon Credit Backend - Railway Deployment")
    print("=" * 60)
    print("🌞 Deploying your ESP32 carbon credit monitoring system...")
    print("")
    
    # Check and install Railway CLI
    if not check_railway_cli():
        if not install_railway_cli():
            sys.exit(1)
    
    # Login to Railway
    if not railway_login():
        sys.exit(1)
    
    # Create project
    if not create_railway_project():
        sys.exit(1)
    
    # Set environment variables
    if not set_environment_variables():
        sys.exit(1)
    
    # Deploy
    if not deploy_to_railway():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Deployment completed successfully!")
    
    # Get URL
    url = get_deployment_url()
    
    print("\n📋 Next steps:")
    print("1. ✅ Your backend is deployed and running")
    print("2. 🔧 Setup Supabase database: python setup_supabase.py")
    print("3. 🧪 Test your deployment: python test_complete_system.py")
    print("4. 📱 Update ESP32 code with your Railway URL")
    
    if url:
        print(f"\n🔌 ESP32 Configuration:")
        print(f'const char* serverName = "{url}/api/energy-data";')
        print(f"\n📊 Dashboard: {url}")
        print(f"🔍 Health Check: {url}/health")
    
    print("\n🚂 Railway Commands:")
    print("- View logs: railway logs")
    print("- Check status: railway status")
    print("- Open dashboard: railway open")
    print("- Redeploy: railway up")
    
    # Ask if user wants to monitor logs
    response = input("\n❓ Monitor deployment logs? (y/N): ")
    if response.lower() == 'y':
        monitor_deployment()
    
    print("\n🌱 Your ESP32 carbon credit system is now live on Railway!")
    print("Happy monitoring! ⚡🌞")

if __name__ == "__main__":
    main()