#!/usr/bin/env python3
"""
Setup script for mrv-sender
Downloads and configures the mrv-sender service
"""

import os
import subprocess
import sys
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MRVSenderSetup:
    """Setup and configuration for mrv-sender"""
    
    def __init__(self):
        self.guardian_repo_url = "https://github.com/hashgraph/guardian.git"
        self.guardian_dir = Path("guardian")
        self.mrv_sender_dir = self.guardian_dir / "mrv-sender"
        
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        required_tools = ["git", "node", "npm"]
        missing_tools = []
        
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], 
                             capture_output=True, check=True)
                logger.info(f"✅ {tool} is installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
                logger.error(f"❌ {tool} is not installed")
        
        if missing_tools:
            logger.error(f"Please install: {', '.join(missing_tools)}")
            return False
        
        return True
    
    def clone_guardian_repo(self) -> bool:
        """Clone the Guardian repository"""
        if self.guardian_dir.exists():
            logger.info("Guardian repository already exists, pulling latest changes...")
            try:
                subprocess.run(["git", "pull"], 
                             cwd=self.guardian_dir, check=True)
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to pull Guardian repo: {e}")
                return False
        else:
            logger.info("Cloning Guardian repository...")
            try:
                subprocess.run(["git", "clone", self.guardian_repo_url], 
                             check=True)
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to clone Guardian repo: {e}")
                return False
    
    def install_dependencies(self) -> bool:
        """Install npm dependencies for mrv-sender"""
        if not self.mrv_sender_dir.exists():
            logger.error("mrv-sender directory not found!")
            return False
        
        logger.info("Installing npm dependencies...")
        try:
            subprocess.run(["npm", "install"], 
                         cwd=self.mrv_sender_dir, check=True)
            logger.info("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def configure_mrv_sender(self) -> bool:
        """Configure mrv-sender with Guardian settings"""
        config_file = self.mrv_sender_dir / "config.json"
        
        # Default configuration
        config = {
            "guardian": {
                "url": "https://guardianservice.app/api/v1",
                "username": "Mhawar",
                "password": "Mhawar2001'",
                "tenantId": "68cc28cc348f53cc0b247ce4",
                "policyId": "68d5ba75152381fe552b1c6d",
                "blockId": "1021939c-b948-4732-bd5f-90cc4ae1cd50"
            },
            "server": {
                "port": 3005,
                "host": "localhost"
            }
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Configuration saved to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def create_start_script(self) -> bool:
        """Create start script for mrv-sender"""
        if os.name == 'nt':  # Windows
            script_content = f"""@echo off
cd /d "{self.mrv_sender_dir.absolute()}"
npm start
pause
"""
            script_file = "start_mrv_sender.bat"
        else:  # Unix-like
            script_content = f"""#!/bin/bash
cd "{self.mrv_sender_dir.absolute()}"
npm start
"""
            script_file = "start_mrv_sender.sh"
        
        try:
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            if os.name != 'nt':
                os.chmod(script_file, 0o755)
            
            logger.info(f"✅ Start script created: {script_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create start script: {e}")
            return False
    
    def setup(self) -> bool:
        """Run complete setup process"""
        logger.info("🚀 Setting up mrv-sender...")
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Cloning Guardian repository", self.clone_guardian_repo),
            ("Installing dependencies", self.install_dependencies),
            ("Configuring mrv-sender", self.configure_mrv_sender),
            ("Creating start script", self.create_start_script)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ {step_name} failed!")
                return False
        
        logger.info("✅ mrv-sender setup completed successfully!")
        return True
    
    def print_usage_instructions(self):
        """Print usage instructions"""
        script_name = "start_mrv_sender.bat" if os.name == 'nt' else "start_mrv_sender.sh"
        
        print("\n" + "=" * 60)
        print("🎉 MRV Sender Setup Complete!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print(f"1. Start mrv-sender: ./{script_name}")
        print("2. Run the Python backend: python python_backend.py")
        print("3. Check Guardian UI for submitted reports")
        print("\n🔧 Manual start (alternative):")
        print(f"   cd {self.mrv_sender_dir}")
        print("   npm start")
        print("\n📁 Files created:")
        print(f"   - {self.mrv_sender_dir}/config.json")
        print(f"   - {script_name}")

def main():
    """Main setup function"""
    setup = MRVSenderSetup()
    
    if setup.setup():
        setup.print_usage_instructions()
        return 0
    else:
        logger.error("Setup failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())