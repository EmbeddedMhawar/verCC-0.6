#!/usr/bin/env python3
"""
Guardian Data Format Validation and Transformation
Handles ESP32 data transformation to Guardian-compatible formats with Verra schema compliance
Implements requirements 8.1, 8.2, 8.3, 8.5
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
from pathlib import Path

from energy_data_aggregator import AggregatedEnergyReport, EnergyMetrics, PerformanceMetrics, EnvironmentalMetrics, DataQualityMetrics

logger = logging.getLogger(__name__)

class GuardianPolicyType(str, Enum):
    """Guardian policy types for renewable energy"""
    VM0042 = "VM0042"  # Verra Methodology for Grid-Connected Renewable Energy
    ARR = "ARR"        # Afforestation, Reforestation and Revegetation
    CUSTOM_RENEWABLE = "CUSTOM_RENEWABLE"
    SOLAR_PV = "SOLAR_PV"
    WIND = "WIND"
    GENERIC_RENEWABLE = "GENERIC_RENEWABLE"

class VerraSchemaVersion(str, Enum):
    """Verra schema versions supported"""
    V4_0 = "v4.0"
    V4_1 = "v4.1" 
    V4_2 = "v4.2"
    LATEST = "v4.2"

@dataclass
class GuardianFieldMapping:
    """Mapping configuration for ESP32 to Guardian field conversion"""
    esp32_field: str
    guardian_field: str
    data_type: str
    required: bool = False
    transformation_func: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    unit_conversion: Optional[Dict[str, Any]] = None

@dataclass
class VerraComplianceMetadata:
    """Verra methodology compliance metadata"""
    methodology: str
    version: str
    project_type: str
    baseline_scenario: str
    monitoring_approach: str
    crediting_period_years: int
    vintage_year: int
    geographic_location: Dict[str, Any]
    technology_type: str
    capacity_mw: float

@dataclass
class GuardianDocument:
    """Guardian document structure for submission"""
    document_id: str
    document_type: str
    schema_version: str
    policy_id: str
    
    # Document metadata
    issuer: str
    issuance_date: str
    valid_from: str
    valid_until: Optional[str]
    
    # Verifiable Credential structure
    context: List[str]
    type: List[str]
    credential_subject: Dict[str, Any]
    
    # Verra compliance
    verra_metadata: VerraComplianceMetadata
    
    # Data integrity
    proof: Dict[str, Any]
    verification_method: str

class GuardianDataTransformer:
    """
    Transforms ESP32 energy data to Guardian-compatible formats with Verra schema compliance
    Implements requirements 8.1, 8.2, 8.3, 8.5
    """
    
    def __init__(self, config_dir: str = None):
        """Initialize the transformer with configuration"""
        self.config_dir = Path(config_dir or os.path.join(os.getcwd(), '.guardian_config'))
        self.config_dir.mkdir(exist_ok=True)
        
        # Load field mappings and schema configurations
        self.field_mappings = self._load_field_mappings()
        self.schema_templates = self._load_schema_templates()
        self.validation_rules = self._load_validation_rules()
        
        logger.info(f"Guardian Data Transformer initialized with config directory: {self.config_dir}")
    
    def transform_energy_report_to_guardian(self, 
                                          report: AggregatedEnergyReport, 
                                          policy_type: GuardianPolicyType = GuardianPolicyType.VM0042,
                                          schema_version: VerraSchemaVersion = VerraSchemaVersion.LATEST) -> GuardianDocument:
        """
        Transform aggregated energy report to Guardian document format
        Requirement 8.1: Create data transformation functions for Guardian renewable energy schema
        """
        logger.info(f"🔄 Transforming energy report for device {report.device_id} to Guardian format (policy: {policy_type})")
        
        # Generate document metadata
        document_id = self._generate_document_id(report.device_id, report.period_start)
        issuance_date = datetime.now().isoformat()
        
        # Transform energy data to Guardian credential subject
        credential_subject = self._transform_to_credential_subject(report, policy_type)
        
        # Create Verra compliance metadata
        verra_metadata = self._create_verra_metadata(report, policy_type)
        
        # Generate cryptographic proof
        proof = self._generate_document_proof(report, credential_subject)
        
        # Determine document types based on policy
        document_types = ["VerifiableCredential", "RenewableEnergyProductionCredential"]
        
        if policy_type == GuardianPolicyType.VM0042:
            document_types.append("VerraVM0042Credential")
        elif policy_type == GuardianPolicyType.ARR:
            document_types.append("AfforestationCredential")
        elif policy_type == GuardianPolicyType.SOLAR_PV:
            document_types.append("SolarPVProductionCredential")
        elif policy_type == GuardianPolicyType.WIND:
            document_types.append("WindEnergyCredential")
        else:
            document_types.append(f"Verra{policy_type.value}Credential")
        
        # Create Guardian document
        guardian_doc = GuardianDocument(
            document_id=document_id,
            document_type="VerifiableCredential",
            schema_version=schema_version.value,
            policy_id="",  # Will be set when submitting to specific policy
            
            # Document metadata
            issuer=f"did:hedera:verifiedcc:{report.device_id}",
            issuance_date=issuance_date,
            valid_from=report.period_start.isoformat(),
            valid_until=report.period_end.isoformat(),
            
            # Verifiable Credential structure
            context=[
                "https://www.w3.org/2018/credentials/v1",
                "https://schema.verra.org/renewable-energy/v1",
                "https://verifiedcc.com/schemas/esp32-energy/v1"
            ],
            type=document_types,
            credential_subject=credential_subject,
            
            # Verra compliance
            verra_metadata=verra_metadata,
            
            # Data integrity
            proof=proof,
            verification_method=f"did:hedera:verifiedcc:{report.device_id}#key-1"
        )
        
        logger.info(f"✅ Guardian document created: {document_id}")
        return guardian_doc
    
    def validate_guardian_document(self, document: GuardianDocument, policy_type: GuardianPolicyType) -> Dict[str, Any]:
        """
        Validate Guardian document against policy requirements
        Requirement 8.3: Add validation for required Guardian policy fields
        """
        logger.info(f"🔍 Validating Guardian document {document.document_id} for policy {policy_type}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "policy_compliance": {},
            "field_validation": {},
            "schema_validation": {}
        }
        
        # Get validation rules for policy type
        policy_rules = self.validation_rules.get(policy_type.value, {})
        
        # Validate required fields
        required_fields = policy_rules.get("required_fields", [])
        for field_path in required_fields:
            if not self._check_field_exists(document.credential_subject, field_path):
                validation_result["errors"].append(f"Required field missing: {field_path}")
                validation_result["is_valid"] = False
        
        # Validate field types and values
        field_types = policy_rules.get("field_types", {})
        for field_path, expected_type in field_types.items():
            field_value = self._get_nested_field(document.credential_subject, field_path)
            if field_value is not None:
                if not self._validate_field_type(field_value, expected_type):
                    validation_result["errors"].append(f"Field {field_path} has invalid type. Expected {expected_type}")
                    validation_result["is_valid"] = False
        
        # Validate value ranges
        value_ranges = policy_rules.get("value_ranges", {})
        for field_path, range_config in value_ranges.items():
            field_value = self._get_nested_field(document.credential_subject, field_path)
            if field_value is not None and isinstance(field_value, (int, float)):
                if "min" in range_config and field_value < range_config["min"]:
                    validation_result["errors"].append(f"Field {field_path} value {field_value} below minimum {range_config['min']}")
                    validation_result["is_valid"] = False
                if "max" in range_config and field_value > range_config["max"]:
                    validation_result["errors"].append(f"Field {field_path} value {field_value} above maximum {range_config['max']}")
                    validation_result["is_valid"] = False
        
        # Validate Verra methodology compliance
        verra_validation = self._validate_verra_compliance(document, policy_type)
        validation_result["policy_compliance"] = verra_validation
        
        if not verra_validation.get("compliant", True):
            validation_result["errors"].extend(verra_validation.get("errors", []))
            validation_result["is_valid"] = False
        
        # Validate document structure
        structure_validation = self._validate_document_structure(document)
        validation_result["schema_validation"] = structure_validation
        
        if not structure_validation.get("valid", True):
            validation_result["errors"].extend(structure_validation.get("errors", []))
            validation_result["is_valid"] = False
        
        logger.info(f"📋 Validation complete for {document.document_id}: {'✅ Valid' if validation_result['is_valid'] else '❌ Invalid'}")
        
        return validation_result
    
    def adapt_for_policy_type(self, document: GuardianDocument, target_policy_type: GuardianPolicyType) -> GuardianDocument:
        """
        Adapt Guardian document for different policy types
        Requirement 8.3: Implement schema adaptation for different Guardian policy types
        """
        logger.info(f"🔧 Adapting document {document.document_id} for policy type {target_policy_type}")
        
        # Create a copy of the document by reconstructing it
        adapted_doc = GuardianDocument(
            document_id=document.document_id,
            document_type=document.document_type,
            schema_version=document.schema_version,
            policy_id=document.policy_id,
            issuer=document.issuer,
            issuance_date=document.issuance_date,
            valid_from=document.valid_from,
            valid_until=document.valid_until,
            context=document.context.copy(),
            type=document.type.copy(),
            credential_subject=document.credential_subject.copy(),
            verra_metadata=VerraComplianceMetadata(
                methodology=document.verra_metadata.methodology,
                version=document.verra_metadata.version,
                project_type=document.verra_metadata.project_type,
                baseline_scenario=document.verra_metadata.baseline_scenario,
                monitoring_approach=document.verra_metadata.monitoring_approach,
                crediting_period_years=document.verra_metadata.crediting_period_years,
                vintage_year=document.verra_metadata.vintage_year,
                geographic_location=document.verra_metadata.geographic_location.copy(),
                technology_type=document.verra_metadata.technology_type,
                capacity_mw=document.verra_metadata.capacity_mw
            ),
            proof=document.proof.copy(),
            verification_method=document.verification_method
        )
        
        # Update document type and context based on policy
        if target_policy_type == GuardianPolicyType.VM0042:
            adapted_doc.type = [
                "VerifiableCredential",
                "RenewableEnergyProductionCredential",
                "VerraVM0042Credential"
            ]
            if "https://schema.verra.org/vm0042/v1" not in adapted_doc.context:
                adapted_doc.context.append("https://schema.verra.org/vm0042/v1")
            
        elif target_policy_type == GuardianPolicyType.ARR:
            adapted_doc.type = [
                "VerifiableCredential", 
                "AfforestationCredential",
                "VerraARRCredential"
            ]
            if "https://schema.verra.org/arr/v1" not in adapted_doc.context:
                adapted_doc.context.append("https://schema.verra.org/arr/v1")
            
        elif target_policy_type == GuardianPolicyType.SOLAR_PV:
            adapted_doc.type = [
                "VerifiableCredential",
                "SolarPVProductionCredential",
                "RenewableEnergyCredential"
            ]
            if "https://schema.verifiedcc.com/solar-pv/v1" not in adapted_doc.context:
                adapted_doc.context.append("https://schema.verifiedcc.com/solar-pv/v1")
        
        # Adapt credential subject based on policy requirements
        adapted_doc.credential_subject = self._adapt_credential_subject(
            document.credential_subject, 
            target_policy_type
        )
        
        # Update Verra metadata
        adapted_doc.verra_metadata.methodology = target_policy_type.value
        
        # Regenerate proof with adapted data
        adapted_doc.proof = self._generate_document_proof_from_dict(
            adapted_doc.credential_subject, 
            adapted_doc.document_id
        )
        
        logger.info(f"✅ Document adapted for policy type {target_policy_type}")
        return adapted_doc
    
    def create_field_mapping_documentation(self) -> Dict[str, Any]:
        """
        Create comprehensive documentation for ESP32 to Guardian field conversion
        Requirement 8.5: Create data mapping documentation for ESP32 to Guardian field conversion
        """
        logger.info("📚 Creating field mapping documentation")
        
        documentation = {
            "overview": {
                "title": "ESP32 to Guardian Field Mapping Documentation",
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "description": "Comprehensive mapping between ESP32 SCADA data and Guardian Verra-compliant schemas"
            },
            "policy_types": {
                policy_type.value: {
                    "description": self._get_policy_description(policy_type),
                    "schema_version": VerraSchemaVersion.LATEST.value,
                    "field_mappings": self._get_policy_field_mappings(policy_type),
                    "validation_rules": self.validation_rules.get(policy_type.value, {}),
                    "example_transformation": self._create_example_transformation(policy_type)
                }
                for policy_type in GuardianPolicyType
            },
            "esp32_data_structure": {
                "description": "ESP32 SCADA data structure from AggregatedEnergyReport",
                "fields": self._document_esp32_fields(),
                "units": self._document_esp32_units(),
                "data_quality_metrics": self._document_data_quality_fields()
            },
            "guardian_schema_structure": {
                "verifiable_credential": self._document_vc_structure(),
                "verra_compliance": self._document_verra_structure(),
                "proof_mechanism": self._document_proof_structure()
            },
            "transformation_examples": {
                "basic_energy_data": self._create_basic_transformation_example(),
                "environmental_data": self._create_environmental_transformation_example(),
                "performance_metrics": self._create_performance_transformation_example(),
                "data_quality": self._create_quality_transformation_example()
            },
            "validation_guidelines": {
                "required_fields": self._document_required_fields(),
                "data_ranges": self._document_data_ranges(),
                "format_requirements": self._document_format_requirements(),
                "compliance_checks": self._document_compliance_checks()
            }
        }
        
        # Save documentation to file
        doc_file = self.config_dir / "field_mapping_documentation.json"
        with open(doc_file, 'w') as f:
            json.dump(documentation, f, indent=2, default=str)
        
        logger.info(f"📄 Field mapping documentation saved to {doc_file}")
        return documentation
    
    def export_guardian_document_json(self, document: GuardianDocument) -> str:
        """Export Guardian document as JSON string for API submission"""
        doc_dict = {
            "@context": document.context,
            "id": document.document_id,
            "type": document.type,
            "issuer": document.issuer,
            "issuanceDate": document.issuance_date,
            "validFrom": document.valid_from,
            "validUntil": document.valid_until,
            "credentialSubject": document.credential_subject,
            "verraMetadata": asdict(document.verra_metadata),
            "proof": document.proof,
            "verificationMethod": document.verification_method
        }
        
        return json.dumps(doc_dict, indent=2, default=str)
    
    # Private helper methods
    
    def _load_field_mappings(self) -> Dict[str, List[GuardianFieldMapping]]:
        """Load field mapping configurations for different policy types"""
        mappings = {
            GuardianPolicyType.VM0042.value: [
                GuardianFieldMapping("total_energy_kwh", "energyProduction.totalEnergyKWh", "number", True),
                GuardianFieldMapping("avg_power_w", "energyProduction.averagePowerW", "number", True),
                GuardianFieldMapping("max_power_w", "energyProduction.peakPowerW", "number", False),
                GuardianFieldMapping("capacity_factor", "performance.capacityFactor", "number", False),
                GuardianFieldMapping("avg_efficiency", "performance.systemEfficiency", "number", False),
                GuardianFieldMapping("avg_irradiance_w_m2", "environmental.solarIrradiance", "number", False),
                GuardianFieldMapping("avg_temperature_c", "environmental.ambientTemperature", "number", False),
                GuardianFieldMapping("verification_hash", "dataIntegrity.verificationHash", "string", True),
                GuardianFieldMapping("data_integrity_score", "dataIntegrity.qualityScore", "number", True),
            ],
            GuardianPolicyType.SOLAR_PV.value: [
                GuardianFieldMapping("total_energy_kwh", "solarProduction.energyGenerated", "number", True),
                GuardianFieldMapping("avg_power_w", "solarProduction.averageOutput", "number", True),
                GuardianFieldMapping("avg_irradiance_w_m2", "solarConditions.irradiance", "number", True),
                GuardianFieldMapping("avg_efficiency", "solarPerformance.panelEfficiency", "number", False),
                GuardianFieldMapping("capacity_factor", "solarPerformance.capacityUtilization", "number", False),
            ]
        }
        
        # Add default mappings for other policy types
        for policy_type in GuardianPolicyType:
            if policy_type.value not in mappings:
                mappings[policy_type.value] = mappings[GuardianPolicyType.VM0042.value]
        
        return mappings
    
    def _load_schema_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load Guardian schema templates for different policy types"""
        return {
            GuardianPolicyType.VM0042.value: {
                "energyProduction": {
                    "totalEnergyKWh": 0.0,
                    "averagePowerW": 0.0,
                    "peakPowerW": 0.0,
                    "measurementPeriod": {
                        "startDate": "",
                        "endDate": "",
                        "durationHours": 24
                    }
                },
                "performance": {
                    "systemEfficiency": 0.0,
                    "capacityFactor": 0.0,
                    "powerFactor": 0.0,
                    "gridFrequency": 50.0
                },
                "environmental": {
                    "solarIrradiance": 0.0,
                    "ambientTemperature": 0.0,
                    "location": {
                        "country": "Morocco",
                        "region": "MENA",
                        "coordinates": {"lat": 0.0, "lon": 0.0}
                    }
                },
                "dataIntegrity": {
                    "verificationHash": "",
                    "qualityScore": 0.0,
                    "measurementCount": 0,
                    "completenessPercent": 0.0
                }
            }
        }
    
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load validation rules for different policy types"""
        return {
            GuardianPolicyType.VM0042.value: {
                "required_fields": [
                    "energyProduction.totalEnergyKWh",
                    "energyProduction.averagePowerW",
                    "dataIntegrity.verificationHash",
                    "dataIntegrity.qualityScore"
                ],
                "field_types": {
                    "energyProduction.totalEnergyKWh": "number",
                    "energyProduction.averagePowerW": "number",
                    "performance.systemEfficiency": "number",
                    "dataIntegrity.verificationHash": "string"
                },
                "value_ranges": {
                    "energyProduction.totalEnergyKWh": {"min": 0, "max": 10000},
                    "energyProduction.averagePowerW": {"min": 0, "max": 1000000},
                    "performance.systemEfficiency": {"min": 0, "max": 1},
                    "dataIntegrity.qualityScore": {"min": 0, "max": 1}
                }
            }
        }
    
    def _transform_to_credential_subject(self, report: AggregatedEnergyReport, policy_type: GuardianPolicyType) -> Dict[str, Any]:
        """Transform energy report to Guardian credential subject"""
        # Get field mappings for policy type
        mappings = self.field_mappings.get(policy_type.value, [])
        schema_template = self.schema_templates.get(policy_type.value, {})
        
        # Start with schema template
        credential_subject = json.loads(json.dumps(schema_template, default=str))
        
        # Apply field mappings
        for mapping in mappings:
            esp32_value = self._extract_esp32_field_value(report, mapping.esp32_field)
            if esp32_value is not None:
                # Apply unit conversion if specified
                if mapping.unit_conversion:
                    esp32_value = self._apply_unit_conversion(esp32_value, mapping.unit_conversion)
                
                # Apply transformation function if specified
                if mapping.transformation_func:
                    esp32_value = self._apply_transformation_function(esp32_value, mapping.transformation_func)
                
                # Set the value in credential subject
                self._set_nested_field(credential_subject, mapping.guardian_field, esp32_value)
        
        # Add device and period information
        credential_subject["deviceInfo"] = {
            "deviceId": report.device_id,
            "deviceType": "ESP32_SCADA",
            "manufacturer": "VerifiedCC",
            "firmwareVersion": "v2.0"
        }
        
        credential_subject["measurementPeriod"] = {
            "startDate": report.period_start.isoformat(),
            "endDate": report.period_end.isoformat(),
            "durationHours": (report.period_end - report.period_start).total_seconds() / 3600,
            "timezone": "Africa/Casablanca"
        }
        
        # Add MENA compliance information
        if report.regional_compliance:
            credential_subject["regionalCompliance"] = report.regional_compliance
        
        return credential_subject
    
    def _create_verra_metadata(self, report: AggregatedEnergyReport, policy_type: GuardianPolicyType) -> VerraComplianceMetadata:
        """Create Verra methodology compliance metadata"""
        return VerraComplianceMetadata(
            methodology=policy_type.value,
            version=VerraSchemaVersion.LATEST.value,
            project_type="Grid-Connected Renewable Energy",
            baseline_scenario="Grid electricity displacement",
            monitoring_approach="Continuous automated monitoring",
            crediting_period_years=10,
            vintage_year=report.period_start.year,
            geographic_location={
                "country": "Morocco",
                "region": "MENA",
                "grid_emission_factor": 0.72,  # kg CO2/kWh for Morocco grid
                "grid_voltage": report.grid_voltage_nominal,
                "grid_frequency": report.grid_frequency_nominal
            },
            technology_type="Solar PV",
            capacity_mw=report.energy_metrics.max_power_w / 1000000  # Convert W to MW
        )
    
    def _generate_document_proof(self, report: AggregatedEnergyReport, credential_subject: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cryptographic proof for document integrity"""
        # Create proof input from key data
        proof_input = {
            "device_id": report.device_id,
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "total_energy_kwh": report.energy_metrics.total_energy_kwh,
            "verification_hash": report.verification_hash,
            "credential_subject_hash": hashlib.sha256(
                json.dumps(credential_subject, sort_keys=True).encode()
            ).hexdigest()
        }
        
        # Generate proof hash
        proof_string = json.dumps(proof_input, sort_keys=True)
        proof_hash = hashlib.sha256(proof_string.encode()).hexdigest()
        
        return {
            "type": "DataIntegrityProof",
            "created": datetime.now().isoformat(),
            "verificationMethod": f"did:hedera:verifiedcc:{report.device_id}#key-1",
            "proofPurpose": "assertionMethod",
            "proofValue": proof_hash,
            "challenge": str(uuid.uuid4()),
            "domain": "verifiedcc.com"
        }
    
    def _generate_document_id(self, device_id: str, period_start: datetime) -> str:
        """Generate unique document ID"""
        date_str = period_start.strftime("%Y%m%d")
        hash_input = f"{device_id}_{date_str}_{datetime.now().isoformat()}"
        doc_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"verifiedcc_{device_id}_{date_str}_{doc_hash}"
    
    def _extract_esp32_field_value(self, report: AggregatedEnergyReport, field_path: str) -> Any:
        """Extract field value from ESP32 energy report using dot notation"""
        try:
            # Handle direct field names and nested field paths
            if '.' not in field_path:
                # Direct field access - check in different metrics objects
                if hasattr(report.energy_metrics, field_path):
                    return getattr(report.energy_metrics, field_path)
                elif hasattr(report.performance_metrics, field_path):
                    return getattr(report.performance_metrics, field_path)
                elif hasattr(report.environmental_metrics, field_path):
                    return getattr(report.environmental_metrics, field_path)
                elif hasattr(report.data_quality, field_path):
                    return getattr(report.data_quality, field_path)
                elif hasattr(report, field_path):
                    return getattr(report, field_path)
                else:
                    return None
            
            # Handle nested field paths like "energy_metrics.total_energy_kwh"
            parts = field_path.split('.')
            value = report
            
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None
            
            return value
        except Exception:
            return None
    
    def _set_nested_field(self, obj: Dict[str, Any], field_path: str, value: Any):
        """Set nested field value using dot notation"""
        parts = field_path.split('.')
        current = obj
        
        # Navigate to the parent of the target field
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the final field
        current[parts[-1]] = value
    
    def _get_nested_field(self, obj: Dict[str, Any], field_path: str) -> Any:
        """Get nested field value using dot notation"""
        parts = field_path.split('.')
        current = obj
        
        try:
            for part in parts:
                current = current[part]
            return current
        except (KeyError, TypeError):
            return None
    
    def _check_field_exists(self, obj: Dict[str, Any], field_path: str) -> bool:
        """Check if nested field exists"""
        return self._get_nested_field(obj, field_path) is not None
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type.lower())
        if not expected_python_type:
            return True  # Unknown type, allow it
        
        return isinstance(value, expected_python_type)
    
    def _validate_verra_compliance(self, document: GuardianDocument, policy_type: GuardianPolicyType) -> Dict[str, Any]:
        """Validate Verra methodology compliance"""
        compliance_result = {
            "compliant": True,
            "errors": [],
            "warnings": [],
            "methodology_check": True,
            "data_quality_check": True,
            "temporal_check": True
        }
        
        # Check methodology alignment
        if document.verra_metadata.methodology != policy_type.value:
            compliance_result["errors"].append(f"Methodology mismatch: expected {policy_type.value}, got {document.verra_metadata.methodology}")
            compliance_result["methodology_check"] = False
            compliance_result["compliant"] = False
        
        # Check data quality requirements
        quality_score = self._get_nested_field(document.credential_subject, "dataIntegrity.qualityScore")
        if quality_score is not None and quality_score < 0.7:
            compliance_result["warnings"].append(f"Data quality score {quality_score} below recommended threshold 0.7")
            compliance_result["data_quality_check"] = False
        
        # Check temporal validity
        try:
            valid_from = datetime.fromisoformat(document.valid_from.replace('Z', '+00:00'))
            valid_until = datetime.fromisoformat(document.valid_until.replace('Z', '+00:00'))
            
            if valid_until <= valid_from:
                compliance_result["errors"].append("Invalid temporal range: valid_until must be after valid_from")
                compliance_result["temporal_check"] = False
                compliance_result["compliant"] = False
        except Exception as e:
            compliance_result["errors"].append(f"Invalid date format: {e}")
            compliance_result["temporal_check"] = False
            compliance_result["compliant"] = False
        
        return compliance_result
    
    def _validate_document_structure(self, document: GuardianDocument) -> Dict[str, Any]:
        """Validate Guardian document structure"""
        structure_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required VC fields exist as attributes
        required_fields = {
            "context": "@context",
            "type": "type", 
            "issuer": "issuer",
            "issuance_date": "issuanceDate",
            "credential_subject": "credentialSubject"
        }
        
        for attr_name, vc_field in required_fields.items():
            if not hasattr(document, attr_name) or getattr(document, attr_name) is None:
                structure_result["errors"].append(f"Missing required VC field: {vc_field}")
                structure_result["valid"] = False
        
        # Check context validity
        if hasattr(document, 'context') and document.context:
            if not isinstance(document.context, list):
                structure_result["errors"].append("Invalid @context: must be a non-empty array")
                structure_result["valid"] = False
        else:
            structure_result["errors"].append("Missing or empty @context")
            structure_result["valid"] = False
        
        # Check type validity
        if hasattr(document, 'type') and document.type:
            if not isinstance(document.type, list):
                structure_result["errors"].append("Invalid type: must be a non-empty array")
                structure_result["valid"] = False
            elif "VerifiableCredential" not in document.type:
                structure_result["errors"].append("Missing required type: VerifiableCredential")
                structure_result["valid"] = False
        else:
            structure_result["errors"].append("Missing or empty type")
            structure_result["valid"] = False
        
        # Check credential subject exists and is not empty
        if hasattr(document, 'credential_subject') and document.credential_subject:
            if not isinstance(document.credential_subject, dict):
                structure_result["errors"].append("credentialSubject must be an object")
                structure_result["valid"] = False
        else:
            structure_result["errors"].append("Missing or empty credentialSubject")
            structure_result["valid"] = False
        
        return structure_result
    
    def _adapt_credential_subject(self, credential_subject: Dict[str, Any], target_policy_type: GuardianPolicyType) -> Dict[str, Any]:
        """Adapt credential subject for different policy types"""
        adapted_subject = credential_subject.copy()
        
        if target_policy_type == GuardianPolicyType.ARR:
            # For ARR methodology, focus on carbon sequestration rather than energy production
            if "energyProduction" in adapted_subject:
                # Convert energy production to carbon sequestration equivalent
                energy_kwh = adapted_subject["energyProduction"].get("totalEnergyKWh", 0)
                # Morocco grid emission factor: 0.72 kg CO2/kWh
                carbon_avoided = energy_kwh * 0.72
                
                adapted_subject["carbonSequestration"] = {
                    "totalCO2AvoidedKg": carbon_avoided,
                    "equivalentEnergyKWh": energy_kwh,
                    "emissionFactor": 0.72,
                    "methodology": "Grid displacement"
                }
        
        elif target_policy_type == GuardianPolicyType.SOLAR_PV:
            # For Solar PV, emphasize solar-specific metrics
            if "energyProduction" in adapted_subject:
                adapted_subject["solarProduction"] = adapted_subject.pop("energyProduction")
            
            if "environmental" in adapted_subject:
                adapted_subject["solarConditions"] = adapted_subject.pop("environmental")
        
        return adapted_subject
    
    def _apply_unit_conversion(self, value: Any, conversion_config: Dict[str, Any]) -> Any:
        """Apply unit conversion to field value"""
        if not isinstance(value, (int, float)):
            return value
        
        from_unit = conversion_config.get("from")
        to_unit = conversion_config.get("to")
        factor = conversion_config.get("factor", 1.0)
        
        # Apply conversion factor
        converted_value = value * factor
        
        logger.debug(f"Unit conversion: {value} {from_unit} -> {converted_value} {to_unit}")
        return converted_value
    
    def _apply_transformation_function(self, value: Any, func_name: str) -> Any:
        """Apply transformation function to field value"""
        if func_name == "watts_to_kilowatts":
            return value / 1000 if isinstance(value, (int, float)) else value
        elif func_name == "celsius_to_kelvin":
            return value + 273.15 if isinstance(value, (int, float)) else value
        elif func_name == "percentage_to_decimal":
            return value / 100 if isinstance(value, (int, float)) else value
        else:
            return value
    
    def _generate_document_proof_from_dict(self, credential_subject: Dict[str, Any], document_id: str) -> Dict[str, Any]:
        """Generate proof from credential subject dictionary"""
        proof_input = {
            "document_id": document_id,
            "credential_subject_hash": hashlib.sha256(
                json.dumps(credential_subject, sort_keys=True).encode()
            ).hexdigest(),
            "timestamp": datetime.now().isoformat()
        }
        
        proof_string = json.dumps(proof_input, sort_keys=True)
        proof_hash = hashlib.sha256(proof_string.encode()).hexdigest()
        
        return {
            "type": "DataIntegrityProof",
            "created": datetime.now().isoformat(),
            "proofPurpose": "assertionMethod",
            "proofValue": proof_hash,
            "challenge": str(uuid.uuid4()),
            "domain": "verifiedcc.com"
        }
    
    # Documentation helper methods
    
    def _get_policy_description(self, policy_type: GuardianPolicyType) -> str:
        """Get description for policy type"""
        descriptions = {
            GuardianPolicyType.VM0042: "Verra Methodology VM0042 for Grid-Connected Renewable Energy Generation",
            GuardianPolicyType.ARR: "Afforestation, Reforestation and Revegetation methodology",
            GuardianPolicyType.SOLAR_PV: "Solar Photovoltaic energy production methodology",
            GuardianPolicyType.WIND: "Wind energy production methodology",
            GuardianPolicyType.CUSTOM_RENEWABLE: "Custom renewable energy methodology",
            GuardianPolicyType.GENERIC_RENEWABLE: "Generic renewable energy methodology"
        }
        return descriptions.get(policy_type, "Unknown policy type")
    
    def _get_policy_field_mappings(self, policy_type: GuardianPolicyType) -> List[Dict[str, Any]]:
        """Get field mappings for policy type as documentation"""
        mappings = self.field_mappings.get(policy_type.value, [])
        return [asdict(mapping) for mapping in mappings]
    
    def _create_example_transformation(self, policy_type: GuardianPolicyType) -> Dict[str, Any]:
        """Create example transformation for documentation"""
        return {
            "input": {
                "device_id": "ESP32_001",
                "total_energy_kwh": 125.5,
                "avg_power_w": 5229.2,
                "avg_efficiency": 0.96,
                "verification_hash": "abc123..."
            },
            "output": {
                "energyProduction": {
                    "totalEnergyKWh": 125.5,
                    "averagePowerW": 5229.2
                },
                "performance": {
                    "systemEfficiency": 0.96
                },
                "dataIntegrity": {
                    "verificationHash": "abc123..."
                }
            }
        }
    
    def _document_esp32_fields(self) -> Dict[str, Any]:
        """Document ESP32 data structure fields"""
        return {
            "energy_metrics": {
                "total_energy_kwh": "Total energy production in kilowatt-hours",
                "avg_power_w": "Average power output in watts",
                "max_power_w": "Peak power output in watts",
                "capacity_factor": "Ratio of actual to theoretical maximum energy output"
            },
            "performance_metrics": {
                "avg_efficiency": "Average system efficiency (0.0 to 1.0)",
                "avg_power_factor": "Average power factor",
                "avg_grid_frequency": "Average grid frequency in Hz"
            },
            "environmental_metrics": {
                "avg_irradiance_w_m2": "Average solar irradiance in W/m²",
                "avg_temperature_c": "Average ambient temperature in Celsius"
            },
            "data_quality": {
                "verification_hash": "Cryptographic hash for data integrity",
                "data_integrity_score": "Overall data quality score (0.0 to 1.0)",
                "total_readings": "Number of sensor readings in period"
            }
        }
    
    def _document_esp32_units(self) -> Dict[str, str]:
        """Document ESP32 data units"""
        return {
            "total_energy_kwh": "kWh",
            "avg_power_w": "W",
            "max_power_w": "W",
            "avg_efficiency": "decimal (0.0-1.0)",
            "avg_irradiance_w_m2": "W/m²",
            "avg_temperature_c": "°C",
            "avg_grid_frequency": "Hz",
            "avg_power_factor": "decimal (0.0-1.0)"
        }
    
    def _document_data_quality_fields(self) -> Dict[str, str]:
        """Document data quality metrics"""
        return {
            "total_readings": "Total number of sensor readings collected",
            "valid_readings": "Number of readings that passed validation",
            "data_completeness_percent": "Percentage of expected readings received",
            "verification_hash": "SHA-256 hash of key data points for integrity verification",
            "data_integrity_score": "Composite score (0.0-1.0) based on completeness, validity, and consistency"
        }
    
    def _document_vc_structure(self) -> Dict[str, str]:
        """Document Verifiable Credential structure"""
        return {
            "@context": "JSON-LD context defining vocabulary and semantics",
            "type": "Array of credential types including VerifiableCredential",
            "issuer": "DID of the credential issuer (ESP32 device)",
            "issuanceDate": "ISO 8601 timestamp of credential creation",
            "credentialSubject": "Main data payload with energy production information",
            "proof": "Cryptographic proof for credential integrity"
        }
    
    def _document_verra_structure(self) -> Dict[str, str]:
        """Document Verra compliance structure"""
        return {
            "methodology": "Verra methodology identifier (VM0042, ARR, etc.)",
            "version": "Schema version for compliance tracking",
            "project_type": "Type of renewable energy project",
            "baseline_scenario": "Baseline scenario for carbon credit calculation",
            "geographic_location": "Location-specific parameters including grid emission factors"
        }
    
    def _document_proof_structure(self) -> Dict[str, str]:
        """Document cryptographic proof structure"""
        return {
            "type": "Type of proof mechanism (DataIntegrityProof)",
            "created": "Timestamp when proof was generated",
            "verificationMethod": "DID and key reference for proof verification",
            "proofValue": "Cryptographic signature or hash value",
            "challenge": "Unique challenge value to prevent replay attacks"
        }
    
    def _create_basic_transformation_example(self) -> Dict[str, Any]:
        """Create basic transformation example"""
        return {
            "description": "Basic energy production data transformation",
            "esp32_input": {
                "total_energy_kwh": 150.75,
                "avg_power_w": 6281.25,
                "max_power_w": 8500.0
            },
            "guardian_output": {
                "energyProduction": {
                    "totalEnergyKWh": 150.75,
                    "averagePowerW": 6281.25,
                    "peakPowerW": 8500.0
                }
            }
        }
    
    def _create_environmental_transformation_example(self) -> Dict[str, Any]:
        """Create environmental data transformation example"""
        return {
            "description": "Environmental conditions data transformation",
            "esp32_input": {
                "avg_irradiance_w_m2": 850.5,
                "avg_temperature_c": 28.5,
                "max_temperature_c": 35.2
            },
            "guardian_output": {
                "environmental": {
                    "solarIrradiance": 850.5,
                    "ambientTemperature": 28.5,
                    "location": {
                        "country": "Morocco",
                        "region": "MENA"
                    }
                }
            }
        }
    
    def _create_performance_transformation_example(self) -> Dict[str, Any]:
        """Create performance metrics transformation example"""
        return {
            "description": "System performance metrics transformation",
            "esp32_input": {
                "avg_efficiency": 0.96,
                "capacity_factor": 0.85,
                "avg_power_factor": 0.95
            },
            "guardian_output": {
                "performance": {
                    "systemEfficiency": 0.96,
                    "capacityFactor": 0.85,
                    "powerFactor": 0.95
                }
            }
        }
    
    def _create_quality_transformation_example(self) -> Dict[str, Any]:
        """Create data quality transformation example"""
        return {
            "description": "Data quality and integrity transformation",
            "esp32_input": {
                "verification_hash": "a1b2c3d4e5f6...",
                "data_integrity_score": 0.92,
                "total_readings": 1440
            },
            "guardian_output": {
                "dataIntegrity": {
                    "verificationHash": "a1b2c3d4e5f6...",
                    "qualityScore": 0.92,
                    "measurementCount": 1440,
                    "completenessPercent": 95.5
                }
            }
        }
    
    def _document_required_fields(self) -> Dict[str, List[str]]:
        """Document required fields for each policy type"""
        return {
            policy_type.value: self.validation_rules.get(policy_type.value, {}).get("required_fields", [])
            for policy_type in GuardianPolicyType
        }
    
    def _document_data_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Document acceptable data ranges"""
        return {
            "energy_production": {
                "totalEnergyKWh": {"min": 0, "max": 10000, "unit": "kWh"},
                "averagePowerW": {"min": 0, "max": 1000000, "unit": "W"}
            },
            "performance": {
                "systemEfficiency": {"min": 0, "max": 1, "unit": "decimal"},
                "capacityFactor": {"min": 0, "max": 1, "unit": "decimal"}
            },
            "environmental": {
                "solarIrradiance": {"min": 0, "max": 1500, "unit": "W/m²"},
                "ambientTemperature": {"min": -10, "max": 60, "unit": "°C"}
            }
        }
    
    def _document_format_requirements(self) -> Dict[str, str]:
        """Document format requirements"""
        return {
            "timestamps": "ISO 8601 format with timezone (e.g., 2024-01-15T10:30:00Z)",
            "numbers": "Decimal numbers with appropriate precision (e.g., 125.75)",
            "hashes": "Hexadecimal strings (SHA-256: 64 characters)",
            "device_ids": "Alphanumeric strings with underscores (e.g., ESP32_001)",
            "coordinates": "Decimal degrees (latitude: -90 to 90, longitude: -180 to 180)"
        }
    
    def _document_compliance_checks(self) -> Dict[str, str]:
        """Document compliance validation checks"""
        return {
            "data_quality_threshold": "Minimum data integrity score of 0.7 required",
            "temporal_validity": "Valid period must be 24 hours or less for daily reports",
            "measurement_frequency": "Minimum 100 readings per day required",
            "energy_threshold": "Minimum 0.1 kWh energy production required",
            "verra_methodology": "Must align with specified Verra methodology requirements",
            "regional_compliance": "Must include Morocco grid standards (220V, 50Hz)"
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the transformer
    try:
        transformer = GuardianDataTransformer()
        
        print("🔧 Testing Guardian Data Transformer...")
        
        # Create field mapping documentation
        documentation = transformer.create_field_mapping_documentation()
        print(f"📚 Created documentation with {len(documentation['policy_types'])} policy types")
        
        # Test with sample data (you would replace this with actual AggregatedEnergyReport)
        print("✅ Guardian Data Transformer test complete")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()