#!/usr/bin/env python3
"""
Complete AMS-I.D Workflow Test
Tests the entire workflow from ESP32 data to Guardian submission
"""

import json
import time
import sys
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ams_id_aggregator import AMSIDAggregator, AMSIDConfig, EnergyMeasurement
from esp32_ams_integration import ESP32AMSIntegration
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AMSWorkflowTester:
    """Comprehensive tester for AMS-I.D workflow"""
    
    def __init__(self):
        self.config = AMSIDConfig.from_file()
        self.aggregator = AMSIDAggregator(self.config)
        self.integration = ESP32AMSIntegration(self.config)
        self.test_results = {}
    
    def print_header(self, title: str):
        """Print formatted test header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str, status: str = ""):
        """Print formatted test step"""
        print(f"\n📋 {step}")
        if status:
            print(f"   {status}")
    
    def test_configuration(self) -> bool:
        """Test configuration loading"""
        self.print_step("Testing Configuration Loading")
        
        try:
            # Test config file loading
            config_from_file = AMSIDConfig.from_file("ams_config.json")
            
            print(f"   ✅ Guardian URL: {config_from_file.guardian_base_url}")
            print(f"   ✅ Policy ID: {config_from_file.policy_id}")
            print(f"   ✅ Username: {config_from_file.username}")
            print(f"   ✅ Tenant ID: {config_from_file.tenant_id}")
            
            self.test_results["configuration"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ Configuration test failed: {e}")
            self.test_results["configuration"] = False
            return False
    
    def test_guardian_authentication(self) -> bool:
        """Test Guardian authentication"""
        self.print_step("Testing Guardian Authentication")
        
        try:
            if self.aggregator.authenticate():
                print("   ✅ Authentication successful!")
                print(f"   ✅ Access token obtained: {self.aggregator.guardian_client.access_token[:20]}...")
                self.test_results["authentication"] = True
                return True
            else:
                print("   ❌ Authentication failed!")
                self.test_results["authentication"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            self.test_results["authentication"] = False
            return False
    
    def test_policy_access(self) -> bool:
        """Test policy access and block retrieval"""
        self.print_step("Testing Policy Access")
        
        try:
            blocks = self.aggregator.get_policy_blocks()
            
            if blocks:
                print(f"   ✅ Retrieved {len(blocks)} policy blocks")
                
                # Check for required blocks
                required_blocks = [
                    self.config.project_creation_block,
                    self.config.report_creation_block
                ]
                
                found_blocks = []
                for block in blocks:
                    if isinstance(block, dict) and 'tag' in block:
                        if block['tag'] in required_blocks:
                            found_blocks.append(block['tag'])
                            print(f"   ✅ Found required block: {block['tag']}")
                
                missing_blocks = set(required_blocks) - set(found_blocks)
                if missing_blocks:
                    print(f"   ⚠️  Missing blocks: {missing_blocks}")
                
                self.test_results["policy_access"] = len(found_blocks) > 0
                return len(found_blocks) > 0
            else:
                print("   ❌ No policy blocks retrieved")
                self.test_results["policy_access"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ Policy access error: {e}")
            self.test_results["policy_access"] = False
            return False
    
    def test_data_generation(self) -> bool:
        """Test ESP32 data generation and conversion"""
        self.print_step("Testing ESP32 Data Generation")
        
        try:
            # Generate test data
            esp32_data = self.integration.simulate_esp32_data()
            
            print(f"   ✅ Generated ESP32 data:")
            print(f"      🔋 Power: {esp32_data['power']:.1f}W")
            print(f"      🌞 Irradiance: {esp32_data['irradiance_w_m2']:.1f}W/m²")
            print(f"      ⚡ Energy: {esp32_data['total_energy_kwh']:.3f}kWh")
            print(f"      🌡️  Temperature: {esp32_data['ambient_temp_c']:.1f}°C")
            
            # Test conversion to measurement
            measurement = self.integration.convert_esp32_to_measurement(esp32_data)
            
            print(f"   ✅ Converted to measurement format:")
            print(f"      📊 Device ID: {measurement.device_id}")
            print(f"      ⏰ Timestamp: {measurement.timestamp}")
            
            self.test_results["data_generation"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ Data generation error: {e}")
            self.test_results["data_generation"] = False
            return False
    
    def test_data_aggregation(self) -> bool:
        """Test data aggregation process"""
        self.print_step("Testing Data Aggregation")
        
        try:
            # Generate 25 hours of test data
            measurements = []
            for i in range(25):
                esp32_data = self.integration.simulate_esp32_data()
                esp32_data["timestamp"] = (datetime.now() - timedelta(hours=i)).isoformat() + "Z"
                measurement = self.integration.convert_esp32_to_measurement(esp32_data)
                measurements.append(measurement)
            
            # Add measurements to aggregator
            for measurement in measurements:
                self.aggregator.add_measurement(measurement)
            
            print(f"   ✅ Added {len(measurements)} measurements to buffer")
            
            # Test aggregation
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            aggregated_report = self.aggregator.aggregate_measurements(start_time, end_time)
            
            if aggregated_report:
                print(f"   ✅ Aggregation successful:")
                print(f"      📈 Total Energy: {aggregated_report.total_energy_mwh:.3f} MWh")
                print(f"      🌱 Emission Reductions: {aggregated_report.emission_reductions_tco2:.3f} tCO2e")
                print(f"      📊 Measurements: {aggregated_report.measurement_count}")
                
                self.test_results["data_aggregation"] = True
                self.test_report = aggregated_report
                return True
            else:
                print("   ❌ Aggregation failed")
                self.test_results["data_aggregation"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ Aggregation error: {e}")
            self.test_results["data_aggregation"] = False
            return False
    
    def test_document_formatting(self) -> bool:
        """Test Guardian document formatting"""
        self.print_step("Testing Document Formatting")
        
        if not hasattr(self, 'test_report'):
            print("   ❌ No test report available")
            return False
        
        try:
            # Test project document
            project_doc = self.aggregator.format_project_document(self.test_report)
            
            if project_doc and 'document' in project_doc:
                print("   ✅ Project document formatted successfully")
                print(f"      📋 Project ID: {project_doc['document']['credentialSubject'][0]['id']}")
                print(f"      🏷️  Policy Tag: {project_doc['policyTag']}")
            else:
                print("   ❌ Project document formatting failed")
                return False
            
            # Test monitoring report document
            report_doc = self.aggregator.format_monitoring_report_document(self.test_report)
            
            if report_doc and 'document' in report_doc:
                print("   ✅ Monitoring report document formatted successfully")
                print(f"      📋 Report ID: {report_doc['document']['credentialSubject'][0]['id']}")
                print(f"      🔗 Project Ref: {report_doc['document']['credentialSubject'][0]['ref']}")
            else:
                print("   ❌ Monitoring report document formatting failed")
                return False
            
            self.test_results["document_formatting"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ Document formatting error: {e}")
            self.test_results["document_formatting"] = False
            return False
    
    def test_guardian_submission(self) -> bool:
        """Test Guardian submission (with user confirmation)"""
        self.print_step("Testing Guardian Submission")
        
        if not hasattr(self, 'test_report'):
            print("   ❌ No test report available")
            return False
        
        # Ask for user confirmation
        print("   ⚠️  This will submit actual data to Guardian!")
        response = input("   Do you want to proceed with Guardian submission? (y/N): ")
        
        if response.lower() != 'y':
            print("   ⏭️  Skipping Guardian submission test")
            self.test_results["guardian_submission"] = "skipped"
            return True
        
        try:
            print("   📤 Submitting project document...")
            project_success = self.aggregator.submit_project(self.test_report)
            
            if project_success:
                print("   ✅ Project submission successful!")
            else:
                print("   ❌ Project submission failed!")
            
            time.sleep(2)  # Wait between submissions
            
            print("   📤 Submitting monitoring report...")
            report_success = self.aggregator.submit_monitoring_report(self.test_report)
            
            if report_success:
                print("   ✅ Monitoring report submission successful!")
            else:
                print("   ❌ Monitoring report submission failed!")
            
            success = project_success and report_success
            self.test_results["guardian_submission"] = success
            return success
            
        except Exception as e:
            print(f"   ❌ Guardian submission error: {e}")
            self.test_results["guardian_submission"] = False
            return False
    
    def test_integration_workflow(self) -> bool:
        """Test complete integration workflow"""
        self.print_step("Testing Complete Integration Workflow")
        
        try:
            # Initialize integration
            if not self.integration.initialize():
                print("   ❌ Integration initialization failed")
                return False
            
            print("   ✅ Integration initialized successfully")
            
            # Test status reporting
            status = self.integration.get_status()
            print(f"   📊 Integration status:")
            print(f"      🔄 Running: {status['running']}")
            print(f"      🔐 Guardian Auth: {status['guardian_authenticated']}")
            print(f"      📡 MRV Sender: {status['mrv_sender_available']}")
            
            self.test_results["integration_workflow"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ Integration workflow error: {e}")
            self.test_results["integration_workflow"] = False
            return False
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        skipped_tests = sum(1 for result in self.test_results.values() if result == "skipped")
        failed_tests = total_tests - passed_tests - skipped_tests
        
        print(f"\n📊 Test Results:")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⏭️  Skipped: {skipped_tests}")
        print(f"   📈 Total: {total_tests}")
        
        print(f"\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            if result is True:
                status = "✅ PASS"
            elif result == "skipped":
                status = "⏭️  SKIP"
            else:
                status = "❌ FAIL"
            
            print(f"   {status} {test_name.replace('_', ' ').title()}")
        
        # Overall result
        if failed_tests == 0:
            print(f"\n🎉 All tests completed successfully!")
            return True
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please check the logs above.")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests in sequence"""
        self.print_header("AMS-I.D Complete Workflow Test Suite")
        
        tests = [
            ("Configuration", self.test_configuration),
            ("Guardian Authentication", self.test_guardian_authentication),
            ("Policy Access", self.test_policy_access),
            ("Data Generation", self.test_data_generation),
            ("Data Aggregation", self.test_data_aggregation),
            ("Document Formatting", self.test_document_formatting),
            ("Guardian Submission", self.test_guardian_submission),
            ("Integration Workflow", self.test_integration_workflow)
        ]
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                if not success and test_name not in ["Guardian Submission"]:
                    print(f"\n⚠️  Critical test '{test_name}' failed. Stopping test suite.")
                    break
            except Exception as e:
                print(f"\n💥 Unexpected error in '{test_name}': {e}")
                self.test_results[test_name.lower().replace(" ", "_")] = False
        
        return self.print_summary()

def main():
    """Main test function"""
    print("🚀 Starting AMS-I.D Complete Workflow Test")
    
    tester = AMSWorkflowTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎊 All tests completed successfully!")
            print("The AMS-I.D aggregation tool is ready for production use.")
            sys.exit(0)
        else:
            print("\n🔧 Some tests failed. Please review and fix issues before production use.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()