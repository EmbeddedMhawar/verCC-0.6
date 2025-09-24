#!/usr/bin/env python3
"""
Guardian Configuration Validation Script
Standalone script to validate Guardian configuration and connection.
Requirements: 7.1, 7.2, 7.3, 7.5

Usage:
    python validate_guardian_config.py
    python validate_guardian_config.py --verbose
    python validate_guardian_config.py --fix-config
"""

import os
import sys
import argparse
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guardian_connection_validator import GuardianConnectionValidator, ValidationLevel
from guardian_service import GuardianService, GuardianConfig

def print_banner():
    """Print validation banner"""
    print("=" * 60)
    print("🔍 Guardian Configuration Validation")
    print("   VerifiedCC Backend - Guardian Integration")
    print("=" * 60)

def print_validation_result(result, verbose=False):
    """Print a single validation result"""
    level_icons = {
        ValidationLevel.CRITICAL: "🚨",
        ValidationLevel.WARNING: "⚠️",
        ValidationLevel.INFO: "ℹ️"
    }
    
    status_icon = "✅" if result.passed else "❌"
    level_icon = level_icons.get(result.level, "❓")
    
    print(f"{status_icon} {level_icon} {result.check_name}: {result.message}")
    
    if verbose and result.details:
        for key, value in result.details.items():
            print(f"    {key}: {value}")

def print_summary(summary):
    """Print validation summary"""
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    overall_status = summary["overall_status"]
    can_start = summary["can_start"]
    
    # Overall status
    if overall_status == "passed":
        print("✅ Overall Status: PASSED")
    elif overall_status == "warning":
        print("⚠️ Overall Status: WARNING")
    else:
        print("❌ Overall Status: FAILED")
    
    print(f"🚀 Can Start System: {'YES' if can_start else 'NO'}")
    
    # Statistics
    stats = summary["summary"]
    print(f"\n📈 Check Statistics:")
    print(f"   Critical: {stats['critical']['passed']}/{stats['critical']['total']}")
    print(f"   Warning:  {stats['warning']['passed']}/{stats['warning']['total']}")
    print(f"   Info:     {stats['info']['passed']}/{stats['info']['total']}")
    
    # Recommendations
    if summary["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"   {rec}")

def create_sample_env_file():
    """Create a sample .env file with Guardian configuration"""
    env_content = """# VerifiedCC Backend Configuration
PORT=5000
FRONTEND_URL=http://localhost:5173

# Supabase Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Guardian Configuration
GUARDIAN_URL=http://localhost:3000
GUARDIAN_USERNAME=your_guardian_username
GUARDIAN_PASSWORD=your_guardian_password
GUARDIAN_API_KEY=
# Note: Guardian API key is optional for local development

# Guardian Submission Scheduler Configuration
GUARDIAN_SUBMISSION_ENABLED=true
GUARDIAN_DEFAULT_POLICY_ID=
GUARDIAN_DAILY_SUBMISSION_TIME=01:00
GUARDIAN_MIN_DATA_COMPLETENESS=80.0
GUARDIAN_MAX_CONCURRENT_SUBMISSIONS=5

# Guardian Docker Configuration (for local setup)
GUARDIAN_OPERATOR_ID=0.0.xxxxx
GUARDIAN_OPERATOR_KEY=302e020100...
GUARDIAN_HEDERA_NET=testnet
GUARDIAN_PREUSED_HEDERA_NET=testnet

# Guardian Policy Configuration
GUARDIAN_POLICY_SELECTION_MODE=fixed
GUARDIAN_PREFERRED_POLICY_TYPES=VM0042,ARR
GUARDIAN_AUTO_POLICY_SELECTION=true

# Guardian Connection Settings
GUARDIAN_CONNECTION_TIMEOUT=30
GUARDIAN_MAX_RETRIES=3
GUARDIAN_RETRY_DELAY=1.0
"""
    
    env_file = Path(".env.sample")
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created sample environment file: {env_file}")
    print("💡 Copy this to .env and update with your actual values")

def fix_common_config_issues():
    """Attempt to fix common configuration issues"""
    print("🔧 Attempting to fix common configuration issues...")
    
    fixes_applied = []
    
    # Check if .env file exists
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("📋 Copying .env.example to .env...")
            import shutil
            shutil.copy(".env.example", ".env")
            fixes_applied.append("Created .env file from .env.example")
        else:
            create_sample_env_file()
            fixes_applied.append("Created sample .env file")
    
    # Load current environment
    load_dotenv()
    
    # Check for missing critical variables
    critical_vars = {
        "GUARDIAN_URL": "http://localhost:3000",
        "GUARDIAN_USERNAME": "",
        "GUARDIAN_PASSWORD": ""
    }
    
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        updated = False
        for var, default in critical_vars.items():
            if f"{var}=" not in env_content:
                env_content += f"\n{var}={default}"
                updated = True
                fixes_applied.append(f"Added missing {var} variable")
        
        if updated:
            with open(env_file, 'w') as f:
                f.write(env_content)
    
    if fixes_applied:
        print("✅ Applied fixes:")
        for fix in fixes_applied:
            print(f"   • {fix}")
        print("💡 Please update the .env file with your actual Guardian credentials")
    else:
        print("ℹ️ No automatic fixes available - manual configuration required")

async def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description="Validate Guardian configuration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix-config", "-f", action="store_true", help="Attempt to fix common configuration issues")
    parser.add_argument("--output-json", "-j", help="Output results to JSON file")
    parser.add_argument("--env-file", "-e", default=".env", help="Environment file to load (default: .env)")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Fix configuration if requested
    if args.fix_config:
        fix_common_config_issues()
        print()
    
    # Load environment variables
    if Path(args.env_file).exists():
        load_dotenv(args.env_file)
        print(f"📁 Loaded environment from: {args.env_file}")
    else:
        print(f"⚠️ Environment file not found: {args.env_file}")
        if args.env_file == ".env":
            print("💡 Run with --fix-config to create a sample .env file")
    
    print()
    
    # Create Guardian service
    try:
        config = GuardianConfig(
            base_url=os.getenv("GUARDIAN_URL", "http://localhost:3000"),
            username=os.getenv("GUARDIAN_USERNAME"),
            password=os.getenv("GUARDIAN_PASSWORD"),
            timeout=int(os.getenv("GUARDIAN_CONNECTION_TIMEOUT", "30"))
        )
        guardian_service = GuardianService(config)
    except Exception as e:
        print(f"❌ Failed to create Guardian service: {e}")
        return 1
    
    # Run validation
    try:
        validator = GuardianConnectionValidator(guardian_service)
        summary = await validator.validate_all()
        
        # Print individual results
        if args.verbose:
            print("📋 DETAILED VALIDATION RESULTS")
            print("-" * 60)
            for result_data in summary["results"]:
                # Convert back to ValidationResult for printing
                from guardian_connection_validator import ValidationResult
                result = ValidationResult(
                    check_name=result_data["check_name"],
                    level=ValidationLevel(result_data["level"]),
                    passed=result_data["passed"],
                    message=result_data["message"],
                    details=result_data["details"]
                )
                print_validation_result(result, verbose=True)
            print()
        
        # Print summary
        print_summary(summary)
        
        # Output JSON if requested
        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n💾 Results saved to: {args.output_json}")
        
        # Return appropriate exit code
        if summary["can_start"]:
            if summary["overall_status"] == "passed":
                print("\n🎉 Guardian configuration is ready!")
                return 0
            else:
                print("\n⚠️ Guardian configuration has warnings but system can start")
                return 0
        else:
            print("\n🛑 Guardian configuration has critical issues - fix before starting")
            return 1
            
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Validation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)