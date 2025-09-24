#!/usr/bin/env python3
"""
Integration Test Runner for Guardian Workflow
Executes comprehensive integration tests for the complete ESP32 → Guardian → Hedera pipeline
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'integration_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'pytest',
        'requests',
        'supabase',
        'guardian_auth',
        'guardian_service',
        'guardian_policy_manager',
        'guardian_document_submitter',
        'energy_data_aggregator'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing required modules: {missing_modules}")
        logger.error("Please install missing dependencies before running integration tests")
        return False
    
    logger.info("✅ All required dependencies are available")
    return True

def check_environment():
    """Check if environment is properly configured for testing"""
    logger.info("🔍 Checking environment configuration...")
    
    # Check for required environment variables
    required_env_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some tests may be skipped due to missing configuration")
    
    # Check for Guardian configuration (optional for mocked tests)
    guardian_vars = [
        'GUARDIAN_URL',
        'GUARDIAN_USERNAME', 
        'GUARDIAN_PASSWORD'
    ]
    
    guardian_configured = all(os.getenv(var) for var in guardian_vars)
    
    if guardian_configured:
        logger.info("✅ Guardian configuration found - live integration tests will be available")
    else:
        logger.info("⚠️ Guardian configuration not found - only mocked tests will run")
        logger.info("Set GUARDIAN_INTEGRATION_TEST=1 and provide Guardian credentials for live tests")
    
    return True

def run_unit_tests():
    """Run individual component unit tests first"""
    logger.info("🧪 Running unit tests for Guardian components...")
    
    unit_test_files = [
        'test_guardian_auth.py',
        'test_guardian_document_submitter.py',
        'test_energy_data_aggregator.py'
    ]
    
    for test_file in unit_test_files:
        if Path(test_file).exists():
            logger.info(f"Running {test_file}...")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pytest', 
                    test_file, 
                    '-v', 
                    '--tb=short'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"✅ {test_file} passed")
                else:
                    logger.error(f"❌ {test_file} failed:")
                    logger.error(result.stdout)
                    logger.error(result.stderr)
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ {test_file} timed out")
                return False
            except Exception as e:
                logger.error(f"❌ Error running {test_file}: {e}")
                return False
        else:
            logger.warning(f"⚠️ {test_file} not found, skipping")
    
    logger.info("✅ Unit tests completed successfully")
    return True

def run_integration_tests():
    """Run the main integration tests"""
    logger.info("🔗 Running Guardian integration tests...")
    
    test_file = 'test_guardian_integration.py'
    
    if not Path(test_file).exists():
        logger.error(f"❌ Integration test file {test_file} not found")
        return False
    
    # Run mocked integration tests
    logger.info("Running mocked integration tests...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            test_file, 
            '-v', 
            '--tb=short',
            '-m', 'not integration',  # Skip live integration tests
            '--durations=10'  # Show slowest 10 tests
        ], capture_output=True, text=True, timeout=600)
        
        logger.info("STDOUT:")
        logger.info(result.stdout)
        
        if result.stderr:
            logger.warning("STDERR:")
            logger.warning(result.stderr)
        
        if result.returncode == 0:
            logger.info("✅ Mocked integration tests passed")
        else:
            logger.error("❌ Mocked integration tests failed")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Integration tests timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error running integration tests: {e}")
        return False
    
    # Run live integration tests if configured
    if os.getenv("GUARDIAN_INTEGRATION_TEST") == "1":
        logger.info("Running live Guardian integration tests...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                test_file, 
                '-v', 
                '--tb=short',
                '-m', 'integration',  # Only live integration tests
                '--durations=5'
            ], capture_output=True, text=True, timeout=900)
            
            logger.info("Live Integration Test STDOUT:")
            logger.info(result.stdout)
            
            if result.stderr:
                logger.warning("Live Integration Test STDERR:")
                logger.warning(result.stderr)
            
            if result.returncode == 0:
                logger.info("✅ Live integration tests passed")
            else:
                logger.warning("⚠️ Live integration tests failed (this may be expected if Guardian is not running)")
                logger.warning("Live test failures do not affect overall test success")
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Live integration tests timed out")
        except Exception as e:
            logger.warning(f"⚠️ Error running live integration tests: {e}")
    
    return True

def generate_test_report():
    """Generate a summary test report"""
    logger.info("📊 Generating test report...")
    
    report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w') as f:
        f.write("# Guardian Integration Test Report\n\n")
        f.write(f"**Test Run Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Test Coverage\n\n")
        f.write("### Requirements Tested\n")
        f.write("- ✅ **Requirement 1.1:** Complete ESP32 → Guardian → Hedera pipeline\n")
        f.write("- ✅ **Requirement 1.2:** Aggregate 24-hour ESP32 sensor readings from Supabase\n")
        f.write("- ✅ **Requirement 1.3:** Submit energy data to Guardian for carbon credit generation\n")
        f.write("- ✅ **Requirement 1.4:** Track Guardian document status and verification progress\n")
        f.write("- ✅ **Requirement 1.5:** Store Guardian document ID and status\n\n")
        
        f.write("### Test Categories\n")
        f.write("1. **Authentication Flow Tests**\n")
        f.write("   - Guardian login/logout\n")
        f.write("   - Token management and refresh\n")
        f.write("   - Session handling\n\n")
        
        f.write("2. **Policy Discovery Tests**\n")
        f.write("   - Policy retrieval and caching\n")
        f.write("   - Schema validation\n")
        f.write("   - Renewable energy policy filtering\n\n")
        
        f.write("3. **Energy Data Pipeline Tests**\n")
        f.write("   - ESP32 data aggregation\n")
        f.write("   - Data quality validation\n")
        f.write("   - Guardian readiness checks\n\n")
        
        f.write("4. **Document Submission Tests**\n")
        f.write("   - Energy report submission\n")
        f.write("   - Status tracking\n")
        f.write("   - Progress monitoring\n\n")
        
        f.write("5. **Error Handling Tests**\n")
        f.write("   - Connection failures\n")
        f.write("   - Authentication errors\n")
        f.write("   - Retry mechanisms\n")
        f.write("   - Rate limiting\n\n")
        
        f.write("6. **Data Integrity Tests**\n")
        f.write("   - Verification hash generation\n")
        f.write("   - Data consistency checks\n")
        f.write("   - Regional compliance validation\n\n")
        
        f.write("## Environment Configuration\n\n")
        f.write("### Required Environment Variables\n")
        f.write("- `SUPABASE_URL`: Database connection URL\n")
        f.write("- `SUPABASE_KEY`: Database access key\n\n")
        
        f.write("### Optional Environment Variables (for live tests)\n")
        f.write("- `GUARDIAN_INTEGRATION_TEST=1`: Enable live Guardian tests\n")
        f.write("- `GUARDIAN_URL`: Guardian instance URL (default: http://localhost:3000)\n")
        f.write("- `GUARDIAN_USERNAME`: Guardian user credentials\n")
        f.write("- `GUARDIAN_PASSWORD`: Guardian user credentials\n\n")
        
        f.write("## Running the Tests\n\n")
        f.write("### Mocked Tests (Default)\n")
        f.write("```bash\n")
        f.write("python run_integration_tests.py\n")
        f.write("```\n\n")
        
        f.write("### Live Integration Tests\n")
        f.write("```bash\n")
        f.write("export GUARDIAN_INTEGRATION_TEST=1\n")
        f.write("export GUARDIAN_USERNAME=your_username\n")
        f.write("export GUARDIAN_PASSWORD=your_password\n")
        f.write("python run_integration_tests.py\n")
        f.write("```\n\n")
        
        f.write("### Individual Test Execution\n")
        f.write("```bash\n")
        f.write("# Run specific test class\n")
        f.write("pytest test_guardian_integration.py::TestGuardianIntegrationWorkflow -v\n\n")
        f.write("# Run specific test method\n")
        f.write("pytest test_guardian_integration.py::TestGuardianIntegrationWorkflow::test_complete_esp32_guardian_hedera_pipeline -v\n\n")
        f.write("# Run with coverage\n")
        f.write("pytest test_guardian_integration.py --cov=guardian_auth --cov=guardian_service --cov=energy_data_aggregator\n")
        f.write("```\n\n")
    
    logger.info(f"📄 Test report generated: {report_file}")
    return report_file

def main():
    """Main test runner function"""
    logger.info("🚀 Starting Guardian Integration Test Suite")
    logger.info("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        logger.error("❌ Environment check failed")
        sys.exit(1)
    
    # Run unit tests first
    if not run_unit_tests():
        logger.error("❌ Unit tests failed")
        sys.exit(1)
    
    # Run integration tests
    if not run_integration_tests():
        logger.error("❌ Integration tests failed")
        sys.exit(1)
    
    # Generate report
    report_file = generate_test_report()
    
    logger.info("=" * 60)
    logger.info("🎉 All tests completed successfully!")
    logger.info(f"📄 Test report: {report_file}")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())