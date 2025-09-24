#!/usr/bin/env python3
"""
Guardian Policy Manager
Handles policy discovery, validation, schema fetching, and data validation for Guardian policies
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import hashlib

from guardian_service import GuardianService, GuardianConfig, EnergyReport

logger = logging.getLogger(__name__)

@dataclass
class PolicySchema:
    """Guardian policy schema definition"""
    policy_id: str
    schema_id: str
    schema_type: str  # VC, VP, etc.
    required_fields: List[str]
    optional_fields: List[str]
    field_types: Dict[str, str]
    validation_rules: Dict[str, Any]
    last_updated: datetime

@dataclass
class ValidationResult:
    """Result of data validation against policy schema"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_fields: List[str]
    invalid_fields: Dict[str, str]
    schema_id: str
    validated_data: Optional[Dict[str, Any]] = None

@dataclass
class PolicyBlock:
    """Guardian policy block definition"""
    block_id: str
    block_type: str
    tag: str
    permissions: List[str]
    schema_requirements: Optional[PolicySchema] = None

class GuardianPolicyManager:
    """
    Manages Guardian policies, schemas, and data validation
    Implements requirements 5.1, 5.2, 8.3, 8.4
    """
    
    def __init__(self, guardian_service: GuardianService = None, cache_dir: str = None):
        self.guardian_service = guardian_service or GuardianService()
        self.cache_dir = Path(cache_dir or os.path.join(os.getcwd(), '.guardian_cache'))
        self.cache_dir.mkdir(exist_ok=True)
        
        # In-memory cache for frequently accessed policies and schemas
        self._policy_cache: Dict[str, Dict[str, Any]] = {}
        self._schema_cache: Dict[str, PolicySchema] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self.cache_duration = timedelta(hours=1)  # Cache policies for 1 hour
        
        logger.info(f"Guardian Policy Manager initialized with cache directory: {self.cache_dir}")
    
    def get_policies(self, status: str = "PUBLISH", refresh_cache: bool = False) -> List[Dict[str, Any]]:
        """
        Get available Guardian policies with caching
        Requirement 5.1: Policy discovery and validation
        """
        cache_key = f"policies_{status}"
        
        # Check cache first unless refresh is requested
        if not refresh_cache and self._is_cache_valid(cache_key):
            logger.debug(f"Returning cached policies for status: {status}")
            return self._policy_cache.get(cache_key, [])
        
        try:
            # Fetch policies from Guardian
            policies = self.guardian_service.get_policies(status=status, page_size=100)
            
            if policies:
                # Update cache
                self._policy_cache[cache_key] = policies
                self._cache_expiry[cache_key] = datetime.now() + self.cache_duration
                
                # Save to disk cache
                self._save_to_disk_cache(f"policies_{status}.json", policies)
                
                logger.info(f"Retrieved and cached {len(policies)} policies with status '{status}'")
                return policies
            else:
                # Try to load from disk cache if Guardian is unavailable
                cached_policies = self._load_from_disk_cache(f"policies_{status}.json")
                if cached_policies:
                    logger.warning(f"Guardian unavailable, using disk cache for policies ({len(cached_policies)} policies)")
                    return cached_policies
                
                logger.warning(f"No policies found with status '{status}' and no cache available")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching policies: {e}")
            
            # Fallback to disk cache
            cached_policies = self._load_from_disk_cache(f"policies_{status}.json")
            if cached_policies:
                logger.warning(f"Using disk cache due to error ({len(cached_policies)} policies)")
                return cached_policies
            
            return []
    
    def get_policy_schema(self, policy_id: str, refresh_cache: bool = False) -> Optional[PolicySchema]:
        """
        Get policy schema with caching
        Requirement 5.2: Policy schema fetching and caching functionality
        """
        if not policy_id or not policy_id.strip():
            logger.error("Policy ID is required to get schema")
            return None
        
        cache_key = f"schema_{policy_id}"
        
        # Check cache first unless refresh is requested
        if not refresh_cache and cache_key in self._schema_cache:
            if self._is_cache_valid(cache_key):
                logger.debug(f"Returning cached schema for policy: {policy_id}")
                return self._schema_cache[cache_key]
        
        try:
            # Fetch policy details from Guardian
            policy = self.guardian_service.get_policy(policy_id)
            
            if not policy:
                logger.warning(f"Policy {policy_id} not found")
                return None
            
            # Extract schema information from policy
            schema = self._extract_policy_schema(policy)
            
            if schema:
                # Update cache
                self._schema_cache[cache_key] = schema
                self._cache_expiry[cache_key] = datetime.now() + self.cache_duration
                
                # Save to disk cache
                schema_data = {
                    'policy_id': schema.policy_id,
                    'schema_id': schema.schema_id,
                    'schema_type': schema.schema_type,
                    'required_fields': schema.required_fields,
                    'optional_fields': schema.optional_fields,
                    'field_types': schema.field_types,
                    'validation_rules': schema.validation_rules,
                    'last_updated': schema.last_updated.isoformat()
                }
                self._save_to_disk_cache(f"schema_{policy_id}.json", schema_data)
                
                logger.info(f"Retrieved and cached schema for policy {policy_id}")
                return schema
            else:
                logger.warning(f"Could not extract schema from policy {policy_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching schema for policy {policy_id}: {e}")
            
            # Try to load from disk cache
            cached_schema_data = self._load_from_disk_cache(f"schema_{policy_id}.json")
            if cached_schema_data:
                try:
                    schema = PolicySchema(
                        policy_id=cached_schema_data['policy_id'],
                        schema_id=cached_schema_data['schema_id'],
                        schema_type=cached_schema_data['schema_type'],
                        required_fields=cached_schema_data['required_fields'],
                        optional_fields=cached_schema_data['optional_fields'],
                        field_types=cached_schema_data['field_types'],
                        validation_rules=cached_schema_data['validation_rules'],
                        last_updated=datetime.fromisoformat(cached_schema_data['last_updated'])
                    )
                    logger.warning(f"Using cached schema for policy {policy_id} due to error")
                    return schema
                except Exception as cache_error:
                    logger.error(f"Error loading cached schema: {cache_error}")
            
            return None
    
    def validate_data(self, data: Dict[str, Any], policy_id: str) -> ValidationResult:
        """
        Validate energy data against Guardian policy schema
        Requirement 8.3, 8.4: Data validation methods for Guardian policy requirements
        """
        if not data:
            return ValidationResult(
                is_valid=False,
                errors=["No data provided for validation"],
                warnings=[],
                missing_fields=[],
                invalid_fields={},
                schema_id="unknown"
            )
        
        # Get policy schema
        schema = self.get_policy_schema(policy_id)
        if not schema:
            return ValidationResult(
                is_valid=False,
                errors=[f"Could not retrieve schema for policy {policy_id}"],
                warnings=[],
                missing_fields=[],
                invalid_fields={},
                schema_id="unknown"
            )
        
        errors = []
        warnings = []
        missing_fields = []
        invalid_fields = {}
        validated_data = data.copy()
        
        # Check required fields
        for field in schema.required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
                errors.append(f"Required field '{field}' is missing")
        
        # Validate field types and values
        for field, value in data.items():
            if field in schema.field_types:
                expected_type = schema.field_types[field]
                
                # Type validation
                if not self._validate_field_type(value, expected_type):
                    invalid_fields[field] = f"Expected {expected_type}, got {type(value).__name__}"
                    errors.append(f"Field '{field}' has invalid type: {invalid_fields[field]}")
                
                # Custom validation rules
                if field in schema.validation_rules:
                    validation_error = self._validate_field_rules(field, value, schema.validation_rules[field])
                    if validation_error:
                        invalid_fields[field] = validation_error
                        errors.append(f"Field '{field}' validation failed: {validation_error}")
        
        # Check for unexpected fields (warnings only)
        all_allowed_fields = set(schema.required_fields + schema.optional_fields)
        for field in data.keys():
            if field not in all_allowed_fields:
                warnings.append(f"Unexpected field '{field}' not defined in schema")
        
        # Transform data for Guardian compatibility if needed
        if not errors:
            validated_data = self._transform_data_for_guardian(data, schema)
        
        is_valid = len(errors) == 0 and len(missing_fields) == 0
        
        result = ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
            schema_id=schema.schema_id,
            validated_data=validated_data if is_valid else None
        )
        
        if is_valid:
            logger.info(f"Data validation successful for policy {policy_id}")
        else:
            logger.warning(f"Data validation failed for policy {policy_id}: {len(errors)} errors, {len(missing_fields)} missing fields")
        
        return result
    
    def get_policy_blocks(self, policy_id: str) -> List[PolicyBlock]:
        """
        Get policy blocks for a specific policy
        Used to understand submission endpoints and requirements
        """
        try:
            policy = self.guardian_service.get_policy(policy_id)
            if not policy:
                logger.warning(f"Policy {policy_id} not found")
                return []
            
            blocks = []
            policy_config = policy.get('config', {})
            
            # Extract blocks from policy configuration
            if 'children' in policy_config:
                blocks.extend(self._extract_blocks_recursive(policy_config['children']))
            
            logger.info(f"Found {len(blocks)} blocks in policy {policy_id}")
            return blocks
            
        except Exception as e:
            logger.error(f"Error getting policy blocks for {policy_id}: {e}")
            return []
    
    def validate_energy_report(self, report: EnergyReport, policy_id: str) -> ValidationResult:
        """
        Validate an EnergyReport against a specific Guardian policy
        Convenience method for energy data validation
        """
        # Convert EnergyReport to dictionary format
        report_data = {
            "device_id": report.device_id,
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "total_energy_kwh": report.total_energy_kwh,
            "avg_power_w": report.avg_power_w,
            "max_power_w": report.max_power_w,
            "avg_efficiency": report.avg_efficiency,
            "avg_irradiance": report.avg_irradiance,
            "avg_temperature": report.avg_temperature,
            "data_points": report.data_points,
            "verification_hash": report.verification_hash,
            "timestamp": datetime.now().isoformat(),
            "source": "VerifiedCC_ESP32_Network"
        }
        
        return self.validate_data(report_data, policy_id)
    
    def get_renewable_energy_policies(self) -> List[Dict[str, Any]]:
        """
        Get policies specifically for renewable energy projects
        Filters policies by name/description keywords
        """
        all_policies = self.get_policies(status="PUBLISH")
        
        renewable_keywords = [
            "renewable", "energy", "solar", "wind", "vm0042", "arr",
            "carbon", "credit", "emission", "verra", "clean"
        ]
        
        renewable_policies = []
        for policy in all_policies:
            policy_name = policy.get('name', '').lower()
            policy_desc = policy.get('description', '').lower()
            
            # Check if policy contains renewable energy keywords
            if any(keyword in policy_name or keyword in policy_desc for keyword in renewable_keywords):
                renewable_policies.append(policy)
        
        logger.info(f"Found {len(renewable_policies)} renewable energy policies out of {len(all_policies)} total policies")
        return renewable_policies
    
    def clear_cache(self, policy_id: str = None):
        """Clear policy and schema cache"""
        if policy_id:
            # Clear specific policy cache
            cache_keys_to_remove = [key for key in self._policy_cache.keys() if policy_id in key]
            for key in cache_keys_to_remove:
                self._policy_cache.pop(key, None)
                self._cache_expiry.pop(key, None)
            
            schema_key = f"schema_{policy_id}"
            self._schema_cache.pop(schema_key, None)
            self._cache_expiry.pop(schema_key, None)
            
            logger.info(f"Cleared cache for policy {policy_id}")
        else:
            # Clear all cache
            self._policy_cache.clear()
            self._schema_cache.clear()
            self._cache_expiry.clear()
            logger.info("Cleared all policy and schema cache")
    
    # Private helper methods
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self._cache_expiry:
            return False
        return datetime.now() < self._cache_expiry[cache_key]
    
    def _save_to_disk_cache(self, filename: str, data: Any):
        """Save data to disk cache"""
        try:
            cache_file = self.cache_dir / filename
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save to disk cache {filename}: {e}")
    
    def _load_from_disk_cache(self, filename: str) -> Optional[Any]:
        """Load data from disk cache"""
        try:
            cache_file = self.cache_dir / filename
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load from disk cache {filename}: {e}")
        return None
    
    def _extract_policy_schema(self, policy: Dict[str, Any]) -> Optional[PolicySchema]:
        """Extract schema information from Guardian policy"""
        try:
            # Guardian policies contain schema information in various formats
            # This is a simplified extraction - real implementation would need
            # to handle Guardian's specific schema format
            
            policy_id = policy.get('id', '')
            policy_name = policy.get('name', '')
            
            # Default schema for renewable energy data
            # This would be extracted from actual Guardian policy schema
            required_fields = [
                "device_id", "period_start", "period_end", 
                "total_energy_kwh", "verification_hash"
            ]
            
            optional_fields = [
                "avg_power_w", "max_power_w", "avg_efficiency",
                "avg_irradiance", "avg_temperature", "data_points",
                "timestamp", "source"
            ]
            
            field_types = {
                "device_id": "string",
                "period_start": "datetime",
                "period_end": "datetime",
                "total_energy_kwh": "number",
                "avg_power_w": "number",
                "max_power_w": "number",
                "avg_efficiency": "number",
                "avg_irradiance": "number",
                "avg_temperature": "number",
                "data_points": "integer",
                "verification_hash": "string",
                "timestamp": "datetime",
                "source": "string"
            }
            
            validation_rules = {
                "total_energy_kwh": {"min": 0, "max": 10000},
                "avg_power_w": {"min": 0, "max": 1000000},
                "max_power_w": {"min": 0, "max": 1000000},
                "avg_efficiency": {"min": 0, "max": 1},
                "data_points": {"min": 1}
            }
            
            return PolicySchema(
                policy_id=policy_id,
                schema_id=f"{policy_id}_renewable_energy_schema",
                schema_type="VC",  # Verifiable Credential
                required_fields=required_fields,
                optional_fields=optional_fields,
                field_types=field_types,
                validation_rules=validation_rules,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error extracting schema from policy: {e}")
            return None
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type"""
        if value is None:
            return True  # None is allowed for optional fields
        
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "datetime": str,  # ISO format string
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type.lower())
        if not expected_python_type:
            return True  # Unknown type, allow it
        
        return isinstance(value, expected_python_type)
    
    def _validate_field_rules(self, field_name: str, value: Any, rules: Dict[str, Any]) -> Optional[str]:
        """Validate field against custom rules"""
        try:
            if "min" in rules and isinstance(value, (int, float)):
                if value < rules["min"]:
                    return f"Value {value} is below minimum {rules['min']}"
            
            if "max" in rules and isinstance(value, (int, float)):
                if value > rules["max"]:
                    return f"Value {value} is above maximum {rules['max']}"
            
            if "pattern" in rules and isinstance(value, str):
                import re
                if not re.match(rules["pattern"], value):
                    return f"Value does not match required pattern"
            
            if "enum" in rules:
                if value not in rules["enum"]:
                    return f"Value must be one of: {rules['enum']}"
            
            return None
            
        except Exception as e:
            return f"Validation rule error: {str(e)}"
    
    def _transform_data_for_guardian(self, data: Dict[str, Any], schema: PolicySchema) -> Dict[str, Any]:
        """Transform data to Guardian-compatible format"""
        transformed = data.copy()
        
        # Add Guardian-specific metadata
        transformed.update({
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": ["VerifiableCredential", "RenewableEnergyProduction"],
            "issuer": "VerifiedCC_ESP32_Network",
            "issuanceDate": datetime.now().isoformat(),
            "credentialSubject": {
                "id": f"did:hedera:{data.get('device_id', 'unknown')}",
                "energyProduction": data
            }
        })
        
        return transformed
    
    def _extract_blocks_recursive(self, children: List[Dict[str, Any]]) -> List[PolicyBlock]:
        """Recursively extract blocks from policy configuration"""
        blocks = []
        
        for child in children:
            block_type = child.get('blockType', '')
            if block_type in ['interfaceDocumentsSource', 'sendToGuardian', 'externalData']:
                block = PolicyBlock(
                    block_id=child.get('id', ''),
                    block_type=block_type,
                    tag=child.get('tag', ''),
                    permissions=child.get('permissions', [])
                )
                blocks.append(block)
            
            # Recursively process nested children
            if 'children' in child:
                blocks.extend(self._extract_blocks_recursive(child['children']))
        
        return blocks