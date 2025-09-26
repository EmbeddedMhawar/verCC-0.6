#!/usr/bin/env python3
"""
Step 3: Setup and Run mrv-sender on Your PC
Following Steps.md workflow exactly:
1. git clone https://github.com/hashgraph/guardian.git
2. cd guardian/mrv-sender
3. npm install
4. npm start
"""

import os
import subprocess
import sys
from pathlib import Path
import time

def check_prerequisites():
    """Check if git, node, and npm are installed"""
    print("🔍 Checking prerequisites...")
    
    tools = ["git", "node", "npm"]
    for tool in tools:
        try:
            result = subprocess.run([tool, "--version"], 
                                  capture_output=True, text=True, check=True, shell=True)
            print(f"✅ {tool}: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool} not found! Please install {tool}")
            return False
    return True

def clone_guardian_repo():
    """Step 3a: git clone https://github.com/hashgraph/guardian.git"""
    print("\n📥 Step 3a: Cloning Guardian repository...")
    
    guardian_dir = Path("guardian")
    
    if guardian_dir.exists():
        print("Guardian directory already exists. Checking mrv-sender...")
        mrv_sender_dir = guardian_dir / "mrv-sender"
        if mrv_sender_dir.exists():
            print("✅ Guardian repository with mrv-sender already available")
            return True
        else:
            print("Guardian exists but mrv-sender missing. Will try sparse checkout...")
    
    # Try sparse checkout to get only mrv-sender
    try:
        if not guardian_dir.exists():
            print("Initializing sparse checkout for mrv-sender only...")
            subprocess.run(["git", "clone", "--filter=blob:none", "--sparse", 
                          "https://github.com/hashgraph/guardian.git"], 
                         capture_output=True, text=True, check=True, shell=True)
        
        # Set sparse checkout to only include mrv-sender
        subprocess.run(["git", "sparse-checkout", "set", "mrv-sender"], 
                     cwd=guardian_dir, capture_output=True, text=True, check=True, shell=True)
        
        print("✅ Guardian repository (mrv-sender) cloned successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Sparse checkout failed: {e.stderr}")
        print("Trying alternative approach...")
        
        # Alternative: Download just the mrv-sender folder
        return download_mrv_sender_only()

def download_mrv_sender_only():
    """Alternative: Download only mrv-sender files"""
    print("📦 Downloading mrv-sender files directly...")
    
    import requests
    import zipfile
    import io
    
    try:
        # Download the repository as zip
        url = "https://github.com/hashgraph/guardian/archive/refs/heads/main.zip"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Extract only mrv-sender folder
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # Find mrv-sender files
                mrv_files = [f for f in zip_file.namelist() if 'mrv-sender/' in f]
                
                if mrv_files:
                    guardian_dir = Path("guardian")
                    guardian_dir.mkdir(exist_ok=True)
                    
                    for file_path in mrv_files:
                        # Remove the guardian-main/ prefix and extract
                        local_path = file_path.replace('guardian-main/', '')
                        if local_path.startswith('mrv-sender/'):
                            target_path = guardian_dir / local_path
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            if not file_path.endswith('/'):  # It's a file, not directory
                                with zip_file.open(file_path) as source:
                                    with open(target_path, 'wb') as target:
                                        target.write(source.read())
                    
                    print("✅ mrv-sender downloaded successfully")
                    return True
                else:
                    print("❌ mrv-sender not found in repository")
                    return False
        else:
            print(f"❌ Failed to download repository: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def check_mrv_sender_exists():
    """Step 3b: Check if guardian/mrv-sender exists"""
    print("\n📁 Step 3b: Checking mrv-sender directory...")
    
    mrv_sender_dir = Path("guardian/mrv-sender")
    
    if mrv_sender_dir.exists():
        print("✅ mrv-sender directory found")
        return True
    else:
        print("❌ mrv-sender directory not found!")
        print("The Guardian repository structure might have changed.")
        return False

def install_mrv_dependencies():
    """Step 3c: npm install in guardian/mrv-sender"""
    print("\n📦 Step 3c: Installing npm dependencies...")
    
    mrv_sender_dir = Path("guardian/mrv-sender")
    
    try:
        print("Running: npm install")
        result = subprocess.run(["npm", "install"], 
                              cwd=mrv_sender_dir,
                              capture_output=True, text=True, check=True, shell=True)
        print("✅ Dependencies installed successfully")
        print(f"Output: {result.stdout[:200]}...")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e.stderr}")
        return False

def test_mrv_start():
    """Step 3d: Test if we can start mrv-sender (just check, don't run)"""
    print("\n🚀 Step 3d: Checking if mrv-sender can start...")
    
    mrv_sender_dir = Path("guardian/mrv-sender")
    package_json = mrv_sender_dir / "package.json"
    
    if package_json.exists():
        print("✅ package.json found")
        try:
            with open(package_json, 'r') as f:
                import json
                pkg_data = json.load(f)
                scripts = pkg_data.get('scripts', {})
                if 'start' in scripts:
                    print(f"✅ Start script found: {scripts['start']}")
                    return True
                else:
                    print("❌ No start script found in package.json")
                    return False
        except Exception as e:
            print(f"❌ Error reading package.json: {e}")
            return False
    else:
        print("❌ package.json not found")
        return False

def create_start_script():
    """Create a start script for mrv-sender"""
    print("\n📝 Creating start script...")
    
    mrv_sender_dir = Path("guardian/mrv-sender").absolute()
    
    if os.name == 'nt':  # Windows
        script_content = f"""@echo off
echo Starting MRV Sender...
cd /d "{mrv_sender_dir}"
npm start
pause
"""
        script_file = "start_mrv_sender.bat"
    else:  # Unix-like
        script_content = f"""#!/bin/bash
echo "Starting MRV Sender..."
cd "{mrv_sender_dir}"
npm start
"""
        script_file = "start_mrv_sender.sh"
    
    try:
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        if os.name != 'nt':
            os.chmod(script_file, 0o755)
        
        print(f"✅ Start script created: {script_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create start script: {e}")
        return False

def main():
    print("=" * 60)
    print("Step 3: Setup mrv-sender on Your PC")
    print("=" * 60)
    
    steps = [
        ("Prerequisites check", check_prerequisites),
        ("Clone Guardian repository", clone_guardian_repo),
        ("Check mrv-sender directory", check_mrv_sender_exists),
        ("Install npm dependencies", install_mrv_dependencies),
        ("Test mrv-sender setup", test_mrv_start),
        ("Create start script", create_start_script)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"\n❌ Step 3 failed at: {step_name}")
            return False
        time.sleep(1)  # Brief pause between steps
    
    print("\n" + "=" * 60)
    print("✅ Step 3 Complete - mrv-sender setup successful!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Start mrv-sender: ./start_mrv_sender.bat")
    print("2. Test mrv-sender connectivity (Step 4)")
    print("3. Send test data to mrv-sender")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)