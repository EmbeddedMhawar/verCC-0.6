#!/usr/bin/env python3
"""
Step 3 Extended: Build and Test mrv-sender
"""

import subprocess
import time
from pathlib import Path

def build_mrv_sender():
    """Build the TypeScript code"""
    print("🔨 Building mrv-sender TypeScript code...")
    
    mrv_sender_dir = Path("guardian/mrv-sender")
    
    try:
        result = subprocess.run(["npm", "run", "build"], 
                              cwd=mrv_sender_dir,
                              capture_output=True, text=True, check=True, shell=True)
        print("✅ Build successful!")
        
        # Check if dist folder was created
        dist_dir = mrv_sender_dir / "dist"
        if dist_dir.exists():
            print(f"✅ dist folder created with files:")
            for file in dist_dir.iterdir():
                print(f"   - {file.name}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e.stderr}")
        return False

def test_mrv_start_briefly():
    """Test if mrv-sender can start (run for a few seconds then stop)"""
    print("\n🚀 Testing mrv-sender startup...")
    
    mrv_sender_dir = Path("guardian/mrv-sender")
    
    try:
        # Start the process
        process = subprocess.Popen(["npm", "start"], 
                                 cwd=mrv_sender_dir,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True, shell=True)
        
        # Wait a few seconds to see if it starts properly
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ mrv-sender started successfully!")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            print("✅ mrv-sender stopped cleanly")
            return True
        else:
            # Process already terminated, check output
            stdout, stderr = process.communicate()
            print(f"❌ mrv-sender failed to start:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing mrv-sender: {e}")
        return False

def main():
    print("=" * 60)
    print("Step 3 Extended: Build and Test mrv-sender")
    print("=" * 60)
    
    # Build first
    if not build_mrv_sender():
        print("❌ Build failed - cannot proceed")
        return False
    
    # Test startup
    if not test_mrv_start_briefly():
        print("❌ Startup test failed")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Step 3 Extended Complete!")
    print("✅ mrv-sender is built and ready to run")
    print("=" * 60)
    print("\n📋 Ready for Step 4: Test mrv-sender connectivity")
    
    return True

if __name__ == "__main__":
    main()