#!/usr/bin/env python3
"""
Guardian Connection Validator
Validates Guardian connection and configuration on backend startup.
Requirements: 7.1, 7.2, 7.3, 7.5
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from guardian_service import GuardianService, GuardianConfig, GuardianAuthError

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"  # Must pass for system to start
    WARNING = "warning"   # Should pass but system can continue
    INFO = "info"         # Informational only

@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_name: str
    level: ValidationLevel
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class GuardianConnectionValidator:
    """
    Validates Guardian connection and configuration on startup
    Requirements: 7.1, 7.2, 7.3, 7.5
    """
    
    def __init__(self, guardian_service: GuardianService = None):
        """Initialize the validator"""
        self.guardian_service = guardian_service
        self.validation_results: List[ValidationResult] = []
        
        # Configuration from environment
        self.guardian_url = os.getenv("GUARDIAN_URL", "http://localhost:3000")
        self.guardian_username = os.getenv("GUARDIAN_USERNAME")
        self.guardian_password = os.getenv("GUARDIAN_PASSWORD")
        self.connection_timeout = int(os.getenv("GUARDIAN_CONNECTION_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("GUARDIAN_MAX_RETRIES", "3"))
        
        logger.info("🔧 GuardianConnectionValidator initialized")
    
    async def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation checks
        Requirement 7.5: Add Guardian configuration validation and error reporting
        """
        logger.info("🔍 Starting Guardian connection validation...")
        self.validation_results.clear()
        
        # Run validation checks
        await self._validate_environment_variables()
        await self._validate_guardian_connection()
        await self._validate_guardian_authentication()
        await self._validate_guardian_policies()
        await self._validate_guardian_configuration()
        
        # Analyze results
        summary = self._generate_validation_summary()
        
        # Log results
        self._log_validation_results(summary)
        
        return summary
    
    async def _validate_environment_variables(self):
        """Validate required environment variables are set"""
        logger.info("📋 Validating environment variables...")
        
        # Critical environment variables
        critical_vars = {
            "GUARDIAN_URL": self.guardian_url,
            "GUARDIAN_USERNAME": self.guardian_username,
            "GUARDIAN_PASSWORD": self.guardian_password
        }
        
        for var_name, var_value in critical_vars.items():
            if not var_value:
                self.validation_results.append(ValidationResult(
                    check_name=f"env_var_{var_name.lower()}",
                    level=ValidationLevel.CRITICAL,
                    passed=False,
                    message=f"Environment variable {var_name} is not set",
                    details={"variable": var_name, "required": True}
                ))
            else:
                self.validation_results.append(ValidationResult(
                    check_name=f"env_var_{var_name.lower()}",
                    level=ValidationLevel.INFO,
                    passed=True,
                    message=f"Environment variable {var_name} is configured",
                    details={"variable": var_name, "value_length": len(str(var_value))}
                ))
        
        # Optional environment variables
        optional_vars = {
            "GUARDIAN_API_KEY": os.getenv("GUARDIAN_API_KEY"),
            "GUARDIAN_DEFAULT_POLICY_ID": os.getenv("GUARDIAN_DEFAULT_POLICY_ID"),
            "GUARDIAN_SUBMISSION_ENABLED": os.getenv("GUARDIAN_SUBMISSION_ENABLED", "true")
        }
        
        for var_name, var_value in optional_vars.items():
            if var_value:
                self.validation_results.append(ValidationResult(
                    check_name=f"env_var_{var_name.lower()}",
                    level=ValidationLevel.INFO,
                    passed=True,
                    message=f"Optional environment variable {var_name} is configured",
                    details={"variable": var_name, "value": str(var_value)}
                ))
    
    async def _validate_guardian_connection(self):
        """Validate Guardian API connection"""
        logger.info("🌐 Validating Guardian connection...")
        
        if not self.guardian_service:
            # Create Guardian service for validation
            config = GuardianConfig(
                base_url=self.guardian_url,
                username=self.guardian_username,
                password=self.guardian_password,
                timeout=self.connection_timeout
            )
            self.guardian_service = GuardianService(config)
        
        try:
            # Test basic connectivity
            health = self.guardian_service.health_check()
            
            if health.get("connected"):
                self.validation_results.append(ValidationResult(
                    check_name="guardian_connection",
                    level=ValidationLevel.CRITICAL,
                    passed=True,
                    message=f"Guardian API is reachable at {self.guardian_url}",
                    details={
                        "url": self.guardian_url,
                        "status": health.get("status"),
                        "version": health.get("guardian_version", "unknown")
                    }
                ))
            else:
                self.validation_results.append(ValidationResult(
                    check_name="guardian_connection",
                    level=ValidationLevel.CRITICAL,
                    passed=False,
                    message=f"Cannot connect to Guardian API at {self.guardian_url}",
                    details={
                        "url": self.guardian_url,
                        "error": health.get("error", "Unknown connection error"),
                        "status": health.get("status", "unknown")
                    }
                ))
                
        except Exception as e:
            self.validation_results.append(ValidationResult(
                check_name="guardian_connection",
                level=ValidationLevel.CRITICAL,
                passed=False,
                message=f"Guardian connection test failed: {str(e)}",
                details={"url": self.guardian_url, "exception": str(e)}
            ))
    
    async def _validate_guardian_authentication(self):
        """Validate Guardian authentication"""
        logger.info("🔐 Validating Guardian authentication...")
        
        if not self.guardian_service:
            self.validation_results.append(ValidationResult(
                check_name="guardian_authentication",
                level=ValidationLevel.CRITICAL,
                passed=False,
                message="Guardian service not available for authentication test",
                details={"reason": "connection_failed"}
            ))
            return
        
        try:
            # Test authentication
            health = self.guardian_service.health_check()
            
            if health.get("authenticated"):
                self.validation_results.append(ValidationResult(
                    check_name="guardian_authentication",
                    level=ValidationLevel.CRITICAL,
                    passed=True,
                    message="Guardian authentication successful",
                    details={
                        "username": health.get("user", "unknown"),
                        "token_expires": health.get("token_expires"),
                        "authenticated": True
                    }
                ))
            else:
                # Try to authenticate
                try:
                    success = self.guardian_service.auth.login()
                    if success:
                        self.validation_results.append(ValidationResult(
                            check_name="guardian_authentication",
                            level=ValidationLevel.CRITICAL,
                            passed=True,
                            message="Guardian authentication successful after login",
                            details={"username": self.guardian_username, "login_required": True}
                        ))
                    else:
                        self.validation_results.append(ValidationResult(
                            check_name="guardian_authentication",
                            level=ValidationLevel.CRITICAL,
                            passed=False,
                            message="Guardian authentication failed",
                            details={"username": self.guardian_username, "reason": "login_failed"}
                        ))
                except GuardianAuthError as e:
                    self.validation_results.append(ValidationResult(
                        check_name="guardian_authentication",
                        level=ValidationLevel.CRITICAL,
                        passed=False,
                        message=f"Guardian authentication error: {str(e)}",
                        details={"username": self.guardian_username, "error": str(e)}
                    ))
                    
        except Exception as e:
            self.validation_results.append(ValidationResult(
                check_name="guardian_authentication",
                level=ValidationLevel.CRITICAL,
                passed=False,
                message=f"Guardian authentication test failed: {str(e)}",
                details={"username": self.guardian_username, "exception": str(e)}
            ))
    
    async def _validate_guardian_policies(self):
        """Validate Guardian policies are available"""
        logger.info("📋 Validating Guardian policies...")
        
        if not self.guardian_service:
            self.validation_results.append(ValidationResult(
                check_name="guardian_policies",
                level=ValidationLevel.WARNING,
                passed=False,
                message="Guardian service not available for policy validation",
                details={"reason": "connection_failed"}
            ))
            return
        
        try:
            policies = self.guardian_service.get_policies()
            
            if policies:
                # Check for renewable energy policies
                renewable_policies = []
                for policy in policies:
                    policy_name = policy.get("name", "").lower()
                    if any(keyword in policy_name for keyword in ["renewable", "energy", "vm0042", "arr"]):
                        renewable_policies.append(policy)
                
                self.validation_results.append(ValidationResult(
                    check_name="guardian_policies",
                    level=ValidationLevel.WARNING,
                    passed=True,
                    message=f"Found {len(policies)} Guardian policies ({len(renewable_policies)} renewable energy related)",
                    details={
                        "total_policies": len(policies),
                        "renewable_policies": len(renewable_policies),
                        "policy_names": [p.get("name", "unnamed") for p in policies[:5]]  # First 5 names
                    }
                ))
                
                # Validate default policy if specified
                default_policy_id = os.getenv("GUARDIAN_DEFAULT_POLICY_ID")
                if default_policy_id:
                    policy_exists = any(p.get("id") == default_policy_id for p in policies)
                    if policy_exists:
                        self.validation_results.append(ValidationResult(
                            check_name="guardian_default_policy",
                            level=ValidationLevel.WARNING,
                            passed=True,
                            message=f"Default policy {default_policy_id} exists in Guardian",
                            details={"policy_id": default_policy_id}
                        ))
                    else:
                        self.validation_results.append(ValidationResult(
                            check_name="guardian_default_policy",
                            level=ValidationLevel.WARNING,
                            passed=False,
                            message=f"Default policy {default_policy_id} not found in Guardian",
                            details={"policy_id": default_policy_id, "available_policies": len(policies)}
                        ))
            else:
                self.validation_results.append(ValidationResult(
                    check_name="guardian_policies",
                    level=ValidationLevel.WARNING,
                    passed=False,
                    message="No Guardian policies found - policies may need to be imported",
                    details={"total_policies": 0, "suggestion": "Import Verra policy templates"}
                ))
                
        except Exception as e:
            self.validation_results.append(ValidationResult(
                check_name="guardian_policies",
                level=ValidationLevel.WARNING,
                passed=False,
                message=f"Guardian policy validation failed: {str(e)}",
                details={"exception": str(e)}
            ))
    
    async def _validate_guardian_configuration(self):
        """Validate Guardian configuration settings"""
        logger.info("⚙️ Validating Guardian configuration...")
        
        # Validate submission configuration
        submission_enabled = os.getenv("GUARDIAN_SUBMISSION_ENABLED", "true").lower() == "true"
        min_completeness = float(os.getenv("GUARDIAN_MIN_DATA_COMPLETENESS", "80.0"))
        max_concurrent = int(os.getenv("GUARDIAN_MAX_CONCURRENT_SUBMISSIONS", "5"))
        
        # Check submission settings
        if submission_enabled:
            self.validation_results.append(ValidationResult(
                check_name="guardian_submission_config",
                level=ValidationLevel.INFO,
                passed=True,
                message="Guardian submission is enabled",
                details={
                    "enabled": submission_enabled,
                    "min_completeness": min_completeness,
                    "max_concurrent": max_concurrent
                }
            ))
        else:
            self.validation_results.append(ValidationResult(
                check_name="guardian_submission_config",
                level=ValidationLevel.WARNING,
                passed=True,
                message="Guardian submission is disabled",
                details={"enabled": submission_enabled, "note": "Enable with GUARDIAN_SUBMISSION_ENABLED=true"}
            ))
        
        # Validate configuration ranges
        if min_completeness < 0 or min_completeness > 100:
            self.validation_results.append(ValidationResult(
                check_name="guardian_config_validation",
                level=ValidationLevel.WARNING,
                passed=False,
                message=f"Invalid data completeness threshold: {min_completeness}% (should be 0-100)",
                details={"min_completeness": min_completeness, "valid_range": "0-100"}
            ))
        
        if max_concurrent < 1 or max_concurrent > 50:
            self.validation_results.append(ValidationResult(
                check_name="guardian_config_validation",
                level=ValidationLevel.WARNING,
                passed=False,
                message=f"Invalid max concurrent submissions: {max_concurrent} (should be 1-50)",
                details={"max_concurrent": max_concurrent, "valid_range": "1-50"}
            ))
    
    def _generate_validation_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        critical_passed = sum(1 for r in self.validation_results if r.level == ValidationLevel.CRITICAL and r.passed)
        critical_total = sum(1 for r in self.validation_results if r.level == ValidationLevel.CRITICAL)
        
        warning_passed = sum(1 for r in self.validation_results if r.level == ValidationLevel.WARNING and r.passed)
        warning_total = sum(1 for r in self.validation_results if r.level == ValidationLevel.WARNING)
        
        info_passed = sum(1 for r in self.validation_results if r.level == ValidationLevel.INFO and r.passed)
        info_total = sum(1 for r in self.validation_results if r.level == ValidationLevel.INFO)
        
        # Determine overall status
        if critical_total > 0 and critical_passed < critical_total:
            overall_status = "failed"
            can_start = False
        elif warning_total > 0 and warning_passed < warning_total:
            overall_status = "warning"
            can_start = True
        else:
            overall_status = "passed"
            can_start = True
        
        return {
            "overall_status": overall_status,
            "can_start": can_start,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "critical": {"passed": critical_passed, "total": critical_total},
                "warning": {"passed": warning_passed, "total": warning_total},
                "info": {"passed": info_passed, "total": info_total}
            },
            "results": [
                {
                    "check_name": r.check_name,
                    "level": r.level.value,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.validation_results
            ],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Check for critical failures
        critical_failures = [r for r in self.validation_results if r.level == ValidationLevel.CRITICAL and not r.passed]
        
        if critical_failures:
            recommendations.append("🚨 Critical issues found - Guardian integration will not work properly")
            
            for failure in critical_failures:
                if "env_var" in failure.check_name:
                    recommendations.append(f"   • Set environment variable: {failure.details.get('variable', 'unknown')}")
                elif "connection" in failure.check_name:
                    recommendations.append("   • Start Guardian Docker containers: docker compose -f docker-compose-quickstart.yml up -d")
                elif "authentication" in failure.check_name:
                    recommendations.append("   • Verify Guardian username and password in .env file")
        
        # Check for warnings
        warning_failures = [r for r in self.validation_results if r.level == ValidationLevel.WARNING and not r.passed]
        
        if warning_failures:
            recommendations.append("⚠️ Warning issues found - some features may not work optimally")
            
            for warning in warning_failures:
                if "policies" in warning.check_name:
                    recommendations.append("   • Import Verra policy templates in Guardian web interface")
                elif "config" in warning.check_name:
                    recommendations.append("   • Review Guardian configuration settings in .env file")
        
        # Add general recommendations
        if not critical_failures and not warning_failures:
            recommendations.append("✅ All validations passed - Guardian integration is ready")
        
        recommendations.append("📖 See GUARDIAN_SETUP.md for detailed setup instructions")
        
        return recommendations
    
    def _log_validation_results(self, summary: Dict[str, Any]):
        """Log validation results"""
        overall_status = summary["overall_status"]
        can_start = summary["can_start"]
        
        if overall_status == "passed":
            logger.info("✅ Guardian validation passed - all checks successful")
        elif overall_status == "warning":
            logger.warning("⚠️ Guardian validation completed with warnings - system can start but some features may not work optimally")
        else:
            logger.error("❌ Guardian validation failed - critical issues found")
        
        # Log summary
        summary_stats = summary["summary"]
        logger.info(f"📊 Validation summary: Critical {summary_stats['critical']['passed']}/{summary_stats['critical']['total']}, "
                   f"Warning {summary_stats['warning']['passed']}/{summary_stats['warning']['total']}, "
                   f"Info {summary_stats['info']['passed']}/{summary_stats['info']['total']}")
        
        # Log recommendations
        for recommendation in summary["recommendations"]:
            if recommendation.startswith("🚨"):
                logger.error(recommendation)
            elif recommendation.startswith("⚠️"):
                logger.warning(recommendation)
            else:
                logger.info(recommendation)
        
        # Log startup decision
        if can_start:
            logger.info("🚀 Guardian validation allows system startup")
        else:
            logger.error("🛑 Guardian validation prevents system startup - fix critical issues first")

# Async helper function for integration with FastAPI startup
async def validate_guardian_on_startup(guardian_service: GuardianService = None) -> Dict[str, Any]:
    """
    Validate Guardian connection on startup
    Requirements: 7.1, 7.2, 7.3, 7.5
    """
    validator = GuardianConnectionValidator(guardian_service)
    return await validator.validate_all()

# Example usage and testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_validation():
        print("🔍 Testing Guardian Connection Validator...")
        
        # Create Guardian service
        config = GuardianConfig(
            base_url=os.getenv("GUARDIAN_URL", "http://localhost:3000"),
            username=os.getenv("GUARDIAN_USERNAME"),
            password=os.getenv("GUARDIAN_PASSWORD")
        )
        guardian_service = GuardianService(config)
        
        # Run validation
        validator = GuardianConnectionValidator(guardian_service)
        summary = await validator.validate_all()
        
        print(f"\n📊 Validation Summary:")
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Can Start: {summary['can_start']}")
        print(f"Critical: {summary['summary']['critical']['passed']}/{summary['summary']['critical']['total']}")
        print(f"Warning: {summary['summary']['warning']['passed']}/{summary['summary']['warning']['total']}")
        print(f"Info: {summary['summary']['info']['passed']}/{summary['summary']['info']['total']}")
        
        print(f"\n📋 Recommendations:")
        for rec in summary['recommendations']:
            print(f"  {rec}")
        
        print("\n✅ Guardian Connection Validator test complete")
    
    # Run the test
    asyncio.run(test_validation())