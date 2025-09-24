#!/usr/bin/env python3
"""
Unit tests for Guardian Policy Manager
Tests policy schema validation with sample Guardian policies
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from guardian_policy_manager import (
    GuardianPolicyManager, PolicySchema, ValidationResult, PolicyBlock
)
from guardian_service import GuardianService, EnergyReport

class TestGuardianPolicyManager(unittest.TestCase):
    """Test cases for Guardian Policy Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary cache directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock Guardian service
        self.mock_guardian_service = Mock(spec=GuardianService)
        
        # Create policy manager with mocked service
        self.policy_manager = GuardianPolicyManager(
            guardian_service=self.mock_guardian_service,
            cache_dir=self.temp_dir
        )
        
        # Sample policy data
        self.sample_policy = {
            "id": "test_policy_123",
            "name": "Renewable Energy VM0042 Policy",
            "description": "Verra VM0042 methodology for renewable energy projects",
            "status": "PUBLISH",
            "config": {
                "children": [
                    {
                        "id": "block_1",
                        "blockType": "interfaceDocumentsSource",
                        "tag": "renewable_energy",
                        "permissions": ["read", "write"]
                    }
                ]
            }
        }
        
        # Sample energy report
        self.sample_energy_report = EnergyReport(
            device_id="ESP32_001",
            period_start=datetime(2024, 1, 1, 0, 0, 0),
            period_end=datetime(2024, 1, 1, 23, 59, 59),
            total_energy_kwh=25.5,
            avg_power_w=1062.5,
            max_power_w=1500.0,
            avg_efficiency=0.85,
            avg_irradiance=800.0,
            avg_temperature=25.0,
            data_points=1440,
            verification_hash="abc123def456"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_get_policies_success(self):
        """Test successful policy retrieval"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policies.return_value = [self.sample_policy]
        
        # Get policies
        policies = self.policy_manager.get_policies(status="PUBLISH")
        
        # Verify results
        self.assertEqual(len(policies), 1)
        self.assertEqual(policies[0]["id"], "test_policy_123")
        self.assertEqual(policies[0]["name"], "Renewable Energy VM0042 Policy")
        
        # Verify Guardian service was called correctly
        self.mock_guardian_service.get_policies.assert_called_once_with(
            status="PUBLISH", page_size=100
        )
    
    def test_get_policies_with_cache(self):
        """Test policy retrieval with caching"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policies.return_value = [self.sample_policy]
        
        # First call - should hit Guardian service
        policies1 = self.policy_manager.get_policies(status="PUBLISH")
        
        # Second call - should use cache
        policies2 = self.policy_manager.get_policies(status="PUBLISH")
        
        # Verify both calls return same data
        self.assertEqual(policies1, policies2)
        
        # Verify Guardian service was only called once
        self.mock_guardian_service.get_policies.assert_called_once()
    
    def test_get_policies_fallback_to_cache(self):
        """Test fallback to disk cache when Guardian is unavailable"""
        # First, populate cache
        self.mock_guardian_service.get_policies.return_value = [self.sample_policy]
        self.policy_manager.get_policies(status="PUBLISH")
        
        # Then simulate Guardian failure
        self.mock_guardian_service.get_policies.return_value = []
        
        # Should still return cached data
        policies = self.policy_manager.get_policies(status="PUBLISH", refresh_cache=True)
        self.assertEqual(len(policies), 1)
        self.assertEqual(policies[0]["id"], "test_policy_123")
    
    def test_get_policy_schema_success(self):
        """Test successful policy schema retrieval"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Get policy schema
        schema = self.policy_manager.get_policy_schema("test_policy_123")
        
        # Verify schema structure
        self.assertIsInstance(schema, PolicySchema)
        self.assertEqual(schema.policy_id, "test_policy_123")
        self.assertIn("device_id", schema.required_fields)
        self.assertIn("total_energy_kwh", schema.required_fields)
        self.assertIn("avg_power_w", schema.optional_fields)
        
        # Verify Guardian service was called
        self.mock_guardian_service.get_policy.assert_called_once_with("test_policy_123")
    
    def test_get_policy_schema_not_found(self):
        """Test policy schema retrieval when policy not found"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policy.return_value = None
        
        # Get policy schema
        schema = self.policy_manager.get_policy_schema("nonexistent_policy")
        
        # Verify no schema returned
        self.assertIsNone(schema)
    
    def test_validate_data_success(self):
        """Test successful data validation"""
        # Mock policy schema
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Valid data
        valid_data = {
            "device_id": "ESP32_001",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-01T23:59:59",
            "total_energy_kwh": 25.5,
            "verification_hash": "abc123def456"
        }
        
        # Validate data
        result = self.policy_manager.validate_data(valid_data, "test_policy_123")
        
        # Verify validation success
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.missing_fields), 0)
        self.assertIsNotNone(result.validated_data)
    
    def test_validate_data_missing_required_fields(self):
        """Test data validation with missing required fields"""
        # Mock policy schema
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Invalid data - missing required fields
        invalid_data = {
            "device_id": "ESP32_001",
            # Missing period_start, period_end, total_energy_kwh, verification_hash
        }
        
        # Validate data
        result = self.policy_manager.validate_data(invalid_data, "test_policy_123")
        
        # Verify validation failure
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertGreater(len(result.missing_fields), 0)
        self.assertIn("period_start", result.missing_fields)
        self.assertIn("total_energy_kwh", result.missing_fields)
    
    def test_validate_data_invalid_types(self):
        """Test data validation with invalid field types"""
        # Mock policy schema
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Invalid data - wrong types
        invalid_data = {
            "device_id": "ESP32_001",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-01T23:59:59",
            "total_energy_kwh": "not_a_number",  # Should be number
            "verification_hash": "abc123def456"
        }
        
        # Validate data
        result = self.policy_manager.validate_data(invalid_data, "test_policy_123")
        
        # Verify validation failure
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("total_energy_kwh", result.invalid_fields)
    
    def test_validate_data_out_of_range_values(self):
        """Test data validation with out-of-range values"""
        # Mock policy schema
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Invalid data - values out of range
        invalid_data = {
            "device_id": "ESP32_001",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-01T23:59:59",
            "total_energy_kwh": -5.0,  # Negative energy (invalid)
            "verification_hash": "abc123def456"
        }
        
        # Validate data
        result = self.policy_manager.validate_data(invalid_data, "test_policy_123")
        
        # Verify validation failure
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("total_energy_kwh", result.invalid_fields)
    
    def test_validate_energy_report(self):
        """Test energy report validation"""
        # Mock policy schema
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Validate energy report
        result = self.policy_manager.validate_energy_report(
            self.sample_energy_report, "test_policy_123"
        )
        
        # Verify validation success
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertIsNotNone(result.validated_data)
    
    def test_get_policy_blocks(self):
        """Test policy blocks extraction"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Get policy blocks
        blocks = self.policy_manager.get_policy_blocks("test_policy_123")
        
        # Verify blocks
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], PolicyBlock)
        self.assertEqual(blocks[0].block_id, "block_1")
        self.assertEqual(blocks[0].block_type, "interfaceDocumentsSource")
        self.assertEqual(blocks[0].tag, "renewable_energy")
    
    def test_get_renewable_energy_policies(self):
        """Test filtering renewable energy policies"""
        # Mock policies with different names
        policies = [
            {
                "id": "policy_1",
                "name": "Renewable Energy Solar VM0042",
                "description": "Solar energy policy",
                "status": "PUBLISH"
            },
            {
                "id": "policy_2", 
                "name": "Industrial Process Policy",
                "description": "Manufacturing process policy",
                "status": "PUBLISH"
            },
            {
                "id": "policy_3",
                "name": "Wind Energy ARR Policy",
                "description": "Wind farm carbon credits",
                "status": "PUBLISH"
            }
        ]
        
        self.mock_guardian_service.get_policies.return_value = policies
        
        # Get renewable energy policies
        renewable_policies = self.policy_manager.get_renewable_energy_policies()
        
        # Verify filtering
        self.assertEqual(len(renewable_policies), 2)  # Should exclude industrial policy
        policy_ids = [p["id"] for p in renewable_policies]
        self.assertIn("policy_1", policy_ids)
        self.assertIn("policy_3", policy_ids)
        self.assertNotIn("policy_2", policy_ids)
    
    def test_cache_expiry(self):
        """Test cache expiration functionality"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policies.return_value = [self.sample_policy]
        
        # Set very short cache duration for testing
        self.policy_manager.cache_duration = timedelta(milliseconds=1)
        
        # First call
        policies1 = self.policy_manager.get_policies(status="PUBLISH")
        
        # Wait for cache to expire
        import time
        time.sleep(0.002)
        
        # Second call should hit Guardian service again
        policies2 = self.policy_manager.get_policies(status="PUBLISH")
        
        # Verify Guardian service was called twice
        self.assertEqual(self.mock_guardian_service.get_policies.call_count, 2)
    
    def test_clear_cache(self):
        """Test cache clearing functionality"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policies.return_value = [self.sample_policy]
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Populate cache
        self.policy_manager.get_policies(status="PUBLISH")
        self.policy_manager.get_policy_schema("test_policy_123")
        
        # Verify cache is populated
        self.assertGreater(len(self.policy_manager._policy_cache), 0)
        self.assertGreater(len(self.policy_manager._schema_cache), 0)
        
        # Clear cache
        self.policy_manager.clear_cache()
        
        # Verify cache is empty
        self.assertEqual(len(self.policy_manager._policy_cache), 0)
        self.assertEqual(len(self.policy_manager._schema_cache), 0)
    
    def test_clear_specific_policy_cache(self):
        """Test clearing cache for specific policy"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policies.return_value = [self.sample_policy]
        self.mock_guardian_service.get_policy.return_value = self.sample_policy
        
        # Populate cache
        self.policy_manager.get_policies(status="PUBLISH")
        self.policy_manager.get_policy_schema("test_policy_123")
        
        # Clear specific policy cache
        self.policy_manager.clear_cache("test_policy_123")
        
        # Verify specific policy cache is cleared but general cache remains
        self.assertGreater(len(self.policy_manager._policy_cache), 0)  # General policies cache
        self.assertEqual(len(self.policy_manager._schema_cache), 0)    # Specific schema cache cleared
    
    def test_disk_cache_persistence(self):
        """Test disk cache save and load functionality"""
        # Mock Guardian service response
        self.mock_guardian_service.get_policies.return_value = [self.sample_policy]
        
        # Get policies (should save to disk cache)
        policies = self.policy_manager.get_policies(status="PUBLISH")
        
        # Verify disk cache file exists
        cache_file = Path(self.temp_dir) / "policies_PUBLISH.json"
        self.assertTrue(cache_file.exists())
        
        # Verify cache content
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)
        
        self.assertEqual(len(cached_data), 1)
        self.assertEqual(cached_data[0]["id"], "test_policy_123")

if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main()