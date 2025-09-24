#!/usr/bin/env python3
"""
Hedera Guardian API Integration Service
Handles communication with Guardian platform for carbon credit verification
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from guardian_auth import GuardianAuth, GuardianAuthError
from guardian_error_handler import (
    GuardianErrorHandler, 
    ErrorContext, 
    RetryStrategy,
    RateLimitConfig,
    GuardianRateLimiter,
    get_guardian_error_handler
)

logger = logging.getLogger('guardian.service')

@dataclass
class GuardianConfig:
    """Guardian API configuration"""
    base_url: str = "http://localhost:3000"
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None  # Deprecated: use username/password instead
    timeout: int = 30

@dataclass
class EnergyReport:
    """Energy production report for Guardian submission"""
    device_id: str
    period_start: datetime
    period_end: datetime
    total_energy_kwh: float
    avg_power_w: float
    max_power_w: float
    avg_efficiency: float
    avg_irradiance: float
    avg_temperature: float
    data_points: int
    verification_hash: str

class GuardianService:
    """Service for interacting with Hedera Guardian API"""
    
    def __init__(self, config: GuardianConfig = None):
        self.config = config or GuardianConfig()
        self.auth = GuardianAuth(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        
        # Initialize error handler with custom configuration
        retry_strategy = RetryStrategy(
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0
        )
        
        rate_limit_config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            burst_limit=10
        )
        
        self.error_handler = GuardianErrorHandler(
            retry_strategy=retry_strategy,
            rate_limiter=GuardianRateLimiter(rate_limit_config),
            logger=logger
        )
        
        # Attempt authentication if credentials are provided
        if self.config.username and self.config.password:
            try:
                self.auth.login(self.config.username, self.config.password)
                logger.info("✅ Guardian authentication successful",
                           extra={'guardian_operation': 'init', 'authenticated': True})
            except GuardianAuthError as e:
                logger.warning(f"⚠️ Guardian authentication failed: {e}",
                              extra={'guardian_operation': 'init', 'authenticated': False})
            except Exception as e:
                logger.warning(f"⚠️ Guardian authentication failed: {e}",
                              extra={'guardian_operation': 'init', 'authenticated': False})
        elif self.config.api_key:
            # Legacy API key support (deprecated)
            logger.warning("⚠️ Using deprecated API key authentication. Please use username/password instead.",
                          extra={'guardian_operation': 'init', 'auth_method': 'api_key'})
            self.auth.session.headers.update({
                'Authorization': f'Bearer {self.config.api_key}'
            })
    
    def health_check(self) -> Dict[str, Any]:
        """Check Guardian API health status"""
        try:
            # Try to get Guardian version info using the /settings/about endpoint
            if self.auth.is_token_valid():
                try:
                    response = self.auth.make_authenticated_request('GET', '/api/v1/settings/about')
                    if response.status_code == 200:
                        about_data = response.json()
                        result = {
                            "status": "healthy",
                            "guardian_version": about_data.get("version", "unknown"),
                            "connected": True,
                            "authenticated": True
                        }
                        
                        if self.auth.current_token:
                            result["user"] = self.auth.current_token.username
                            result["token_expires"] = self.auth.current_token.expires_at.isoformat()
                        
                        return result
                except GuardianAuthError:
                    # Fall back to unauthenticated check
                    pass
            
            # Try a simple unauthenticated request to check if Guardian is running
            # Use the base URL to check if Guardian web interface is accessible
            response = self.auth.session.get(
                f"{self.config.base_url}",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "guardian_version": "unknown (not authenticated)",
                    "connected": True,
                    "authenticated": self.auth.is_token_valid()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "connected": False,
                    "authenticated": False
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "unreachable",
                "error": "Cannot connect to Guardian API",
                "connected": False,
                "authenticated": False
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "connected": False,
                "authenticated": False
            }
    
    def get_policies(self, status: str = None, policy_type: str = None, page_index: int = 0, page_size: int = 20) -> List[Dict[str, Any]]:
        """Get available Guardian policies using GET /policies endpoint"""
        try:
            # Ensure we have valid authentication
            if not self.auth.ensure_valid_token(self.config.username, self.config.password):
                logger.error("Cannot get policies: No valid authentication")
                return []
            
            # Build query parameters
            params = {
                'pageIndex': page_index,
                'pageSize': page_size
            }
            if status:
                params['status'] = status  # e.g., PUBLISH, DRAFT, DRY_RUN
            if policy_type:
                params['type'] = policy_type  # e.g., local
            
            # Use the correct Guardian API endpoint for policies (requirement 3.3)
            response = self.auth.make_authenticated_request('GET', '/api/v1/policies', params=params)
            
            if response.status_code == 200:
                policies_data = response.json()
                
                # Handle both array response and paginated response formats
                if isinstance(policies_data, dict) and 'body' in policies_data:
                    # Paginated response format
                    policies_list = policies_data.get('body', [])
                    total_count = policies_data.get('totalCount', len(policies_list))
                elif isinstance(policies_data, list):
                    # Direct array response
                    policies_list = policies_data
                    total_count = response.headers.get('X-Total-Count', len(policies_list))
                else:
                    logger.warning(f"Unexpected policies response format: {type(policies_data)}")
                    policies_list = []
                    total_count = 0
                
                logger.info(f"Successfully retrieved {len(policies_list)} policies from Guardian (total: {total_count})")
                return policies_list
            elif response.status_code == 401:
                logger.error("Guardian authentication failed - invalid credentials or expired token")
                return []
            elif response.status_code == 403:
                logger.error("Guardian access forbidden - insufficient permissions to view policies")
                return []
            elif response.status_code == 404:
                logger.error("Guardian policies endpoint not found - check Guardian version and API paths")
                return []
            else:
                logger.error(f"Failed to get policies: HTTP {response.status_code} - {response.text}")
                return []
            
        except GuardianAuthError as e:
            logger.error(f"Guardian authentication error getting policies: {e}")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Guardian API: {e}")
            return []
        except requests.exceptions.Timeout as e:
            logger.error(f"Guardian API request timeout: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Guardian policies: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Guardian policies endpoint: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting Guardian policies: {e}")
            return []
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Guardian policy by ID using GET /policies/{policyId}"""
        try:
            if not policy_id or not policy_id.strip():
                logger.error("Cannot get policy: Policy ID is required")
                return None
                
            # Ensure we have valid authentication
            if not self.auth.ensure_valid_token(self.config.username, self.config.password):
                logger.error("Cannot get policy: No valid authentication")
                return None
            
            # Use the correct Guardian API endpoint for a specific policy (requirement 3.3)
            response = self.auth.make_authenticated_request('GET', f'/api/v1/policies/{policy_id}')
            
            if response.status_code == 200:
                policy_data = response.json()
                logger.info(f"Successfully retrieved policy {policy_id} from Guardian")
                return policy_data
            elif response.status_code == 401:
                logger.error(f"Guardian authentication failed getting policy {policy_id}")
                return None
            elif response.status_code == 403:
                logger.error(f"Access forbidden to policy {policy_id} - insufficient permissions")
                return None
            elif response.status_code == 404:
                logger.warning(f"Policy {policy_id} not found in Guardian")
                return None
            else:
                logger.error(f"Failed to get policy {policy_id}: HTTP {response.status_code} - {response.text}")
                return None
            
        except GuardianAuthError as e:
            logger.error(f"Guardian authentication error getting policy {policy_id}: {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Guardian API for policy {policy_id}: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"Guardian API timeout getting policy {policy_id}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Guardian policy {policy_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Guardian for policy {policy_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Guardian policy {policy_id}: {e}")
            return None
    
    def submit_energy_report(self, report: EnergyReport, policy_id: str, tag_name: str = "renewable_energy") -> Dict[str, Any]:
        """Submit energy production report to Guardian using POST /policies/{policyId}/tag/{tagName}/blocks (requirement 3.4)"""
        
        # Validate input parameters
        if not policy_id or not policy_id.strip():
            return {
                "success": False,
                "error": "Missing policy_id",
                "message": "Policy ID is required for Guardian submission"
            }
        
        if not tag_name or not tag_name.strip():
            return {
                "success": False,
                "error": "Missing tag_name",
                "message": "Tag name is required for Guardian submission"
            }
        
        if not report:
            return {
                "success": False,
                "error": "Missing report",
                "message": "Energy report is required for Guardian submission"
            }
        
        try:
            # Ensure we have valid authentication
            if not self.auth.ensure_valid_token(self.config.username, self.config.password):
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "message": "Cannot submit report: No valid authentication"
                }
            
            # Convert report to Guardian-compatible format
            guardian_data = {
                "type": "renewable_energy_production",
                "device_id": report.device_id,
                "reporting_period": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat()
                },
                "energy_production": {
                    "total_kwh": report.total_energy_kwh,
                    "average_power_w": report.avg_power_w,
                    "peak_power_w": report.max_power_w
                },
                "performance_metrics": {
                    "average_efficiency": report.avg_efficiency,
                    "average_irradiance_w_m2": report.avg_irradiance,
                    "average_temperature_c": report.avg_temperature
                },
                "data_quality": {
                    "total_data_points": report.data_points,
                    "verification_hash": report.verification_hash
                },
                "timestamp": datetime.now().isoformat(),
                "source": "VerifiedCC_ESP32_Network"
            }
            
            # Use the correct Guardian API endpoint for block data submission (requirement 3.4)
            endpoint = f"/api/v1/policies/{policy_id}/tag/{tag_name}/blocks"
            
            response = self.auth.make_authenticated_request(
                'POST',
                endpoint,
                json=guardian_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                document_id = result.get("id") or result.get("uuid") or result.get("blockId")
                logger.info(f"Successfully submitted energy report to Guardian policy {policy_id}: {document_id}")
                return {
                    "success": True,
                    "guardian_document_id": document_id,
                    "policy_id": policy_id,
                    "tag_name": tag_name,
                    "status": result.get("status", "submitted"),
                    "message": "Energy report submitted to Guardian successfully",
                    "response_data": result
                }
            elif response.status_code == 400:
                logger.error(f"Guardian submission failed - bad request: {response.text}")
                return {
                    "success": False,
                    "error": "Bad request",
                    "message": f"Invalid data format or missing required fields: {response.text}",
                    "policy_id": policy_id,
                    "tag_name": tag_name
                }
            elif response.status_code == 401:
                logger.error("Guardian submission failed - authentication error")
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "message": "Guardian authentication expired or invalid",
                    "policy_id": policy_id,
                    "tag_name": tag_name
                }
            elif response.status_code == 403:
                logger.error(f"Guardian submission failed - access forbidden to policy {policy_id}")
                return {
                    "success": False,
                    "error": "Access forbidden",
                    "message": f"Insufficient permissions to submit to policy {policy_id}",
                    "policy_id": policy_id,
                    "tag_name": tag_name
                }
            elif response.status_code == 404:
                logger.error(f"Guardian submission failed - policy or tag not found: {policy_id}/{tag_name}")
                return {
                    "success": False,
                    "error": "Not found",
                    "message": f"Policy {policy_id} or tag {tag_name} not found in Guardian",
                    "policy_id": policy_id,
                    "tag_name": tag_name
                }
            else:
                logger.error(f"Guardian submission failed: HTTP {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "policy_id": policy_id,
                    "tag_name": tag_name
                }
                
        except GuardianAuthError as e:
            logger.error(f"Guardian authentication error during submission: {e}")
            return {
                "success": False,
                "error": "Authentication error",
                "message": str(e)
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Guardian API during submission: {e}")
            return {
                "success": False,
                "error": "Connection error",
                "message": f"Cannot connect to Guardian API: {str(e)}"
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"Guardian API timeout during submission: {e}")
            return {
                "success": False,
                "error": "Timeout error",
                "message": f"Guardian API request timeout: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error submitting to Guardian: {e}")
            return {
                "success": False,
                "error": "Network error",
                "message": str(e)
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Guardian submission: {e}")
            return {
                "success": False,
                "error": "Invalid response",
                "message": f"Guardian returned invalid JSON response: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error submitting energy report to Guardian: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to communicate with Guardian API"
            }
    
    def get_policy_documents(self, policy_id: str, document_type: str = None, include_document: bool = True) -> List[Dict[str, Any]]:
        """Get documents for a specific policy using GET /policies/{policyId}/documents (requirement 3.5)"""
        try:
            if not policy_id or not policy_id.strip():
                logger.error("Cannot get policy documents: Policy ID is required")
                return []
                
            # Ensure we have valid authentication
            if not self.auth.ensure_valid_token(self.config.username, self.config.password):
                logger.error("Cannot get policy documents: No valid authentication")
                return []
            
            # Build query parameters
            params = {}
            if document_type:
                params['type'] = document_type  # VC or VP
            if include_document is not None:
                params['includeDocument'] = str(include_document).lower()
            
            # Use the correct Guardian API endpoint for policy documents (requirement 3.5)
            endpoint = f"/api/v1/policies/{policy_id}/documents"
            
            response = self.auth.make_authenticated_request('GET', endpoint, params=params)
            
            if response.status_code == 200:
                documents_data = response.json()
                
                # Handle different response formats
                if isinstance(documents_data, list):
                    documents = documents_data
                elif isinstance(documents_data, dict) and 'body' in documents_data:
                    documents = documents_data.get('body', [])
                elif isinstance(documents_data, dict) and 'documents' in documents_data:
                    documents = documents_data.get('documents', [])
                else:
                    logger.warning(f"Unexpected documents response format for policy {policy_id}: {type(documents_data)}")
                    documents = []
                
                logger.info(f"Successfully retrieved {len(documents)} documents for policy {policy_id}")
                return documents
            elif response.status_code == 401:
                logger.error(f"Guardian authentication failed getting documents for policy {policy_id}")
                return []
            elif response.status_code == 403:
                logger.error(f"Access forbidden to documents for policy {policy_id}")
                return []
            elif response.status_code == 404:
                logger.warning(f"Policy {policy_id} not found or has no documents")
                return []
            else:
                logger.error(f"Failed to get policy documents: HTTP {response.status_code} - {response.text}")
                return []
            
        except GuardianAuthError as e:
            logger.error(f"Guardian authentication error getting policy documents: {e}")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Guardian API for policy documents: {e}")
            return []
        except requests.exceptions.Timeout as e:
            logger.error(f"Guardian API timeout getting policy documents: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting policy documents: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Guardian documents endpoint: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting policy documents: {e}")
            return []
    
    def get_document_status(self, policy_id: str, document_id: str = None) -> Dict[str, Any]:
        """Get status of documents in a policy using GET /policies/{policyId}/documents (requirement 3.5)"""
        try:
            if not policy_id or not policy_id.strip():
                return {
                    "success": False,
                    "error": "Missing policy_id",
                    "message": "Policy ID is required to get document status"
                }
            
            # Get all documents for the policy
            documents = self.get_policy_documents(policy_id, include_document=False)
            
            if document_id:
                # Find specific document
                document_id = document_id.strip()
                for doc in documents:
                    doc_id = doc.get('id') or doc.get('uuid') or doc.get('blockId')
                    if doc_id == document_id:
                        return {
                            "success": True,
                            "document": doc,
                            "status": doc.get("status", "unknown"),
                            "policy_id": policy_id,
                            "document_id": document_id
                        }
                
                return {
                    "success": False,
                    "error": "Document not found",
                    "message": f"Document {document_id} not found in policy {policy_id}",
                    "policy_id": policy_id,
                    "document_id": document_id
                }
            else:
                # Return all documents status
                return {
                    "success": True,
                    "documents": documents,
                    "policy_id": policy_id,
                    "total_count": len(documents)
                }
            
        except Exception as e:
            logger.error(f"Failed to get document status from Guardian: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get document status",
                "policy_id": policy_id
            }
    
    def get_tokens(self) -> List[Dict[str, Any]]:
        """Get available tokens (carbon credits) from Guardian"""
        try:
            # Ensure we have valid authentication
            if not self.auth.ensure_valid_token(self.config.username, self.config.password):
                logger.error("Cannot get tokens: No valid authentication")
                return []
            
            response = self.auth.make_authenticated_request('GET', '/api/v1/tokens')
            
            if response.status_code == 200:
                tokens_data = response.json()
                
                # Handle different response formats
                if isinstance(tokens_data, list):
                    tokens = tokens_data
                elif isinstance(tokens_data, dict) and 'body' in tokens_data:
                    tokens = tokens_data.get('body', [])
                elif isinstance(tokens_data, dict) and 'tokens' in tokens_data:
                    tokens = tokens_data.get('tokens', [])
                else:
                    logger.warning(f"Unexpected tokens response format: {type(tokens_data)}")
                    tokens = []
                
                logger.info(f"Successfully retrieved {len(tokens)} tokens from Guardian")
                return tokens
            elif response.status_code == 401:
                logger.error("Guardian authentication failed getting tokens")
                return []
            elif response.status_code == 403:
                logger.error("Access forbidden to Guardian tokens")
                return []
            else:
                logger.error(f"Failed to get tokens: HTTP {response.status_code} - {response.text}")
                return []
            
        except GuardianAuthError as e:
            logger.error(f"Guardian authentication error getting tokens: {e}")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Guardian API for tokens: {e}")
            return []
        except requests.exceptions.Timeout as e:
            logger.error(f"Guardian API timeout getting tokens: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Guardian tokens: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Guardian tokens endpoint: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get tokens from Guardian: {e}")
            return []
    
    def validate_policy_exists(self, policy_id: str) -> Dict[str, Any]:
        """Validate that a Guardian policy exists and is accessible (requirement 5.3)"""
        try:
            if not policy_id or not policy_id.strip():
                return {
                    "valid": False,
                    "error": "Missing policy_id",
                    "message": "Policy ID is required for validation"
                }
            
            policy = self.get_policy(policy_id)
            
            if policy:
                policy_status = policy.get('status', 'unknown')
                policy_name = policy.get('name', 'Unknown')
                
                # Check if policy is in a usable state
                if policy_status in ['PUBLISH', 'DRY_RUN']:
                    return {
                        "valid": True,
                        "policy": policy,
                        "status": policy_status,
                        "name": policy_name,
                        "message": f"Policy {policy_id} is valid and accessible"
                    }
                else:
                    return {
                        "valid": False,
                        "policy": policy,
                        "status": policy_status,
                        "name": policy_name,
                        "error": "Policy not in usable state",
                        "message": f"Policy {policy_id} has status '{policy_status}' - only PUBLISH or DRY_RUN policies can be used"
                    }
            else:
                return {
                    "valid": False,
                    "error": "Policy not found",
                    "message": f"Policy {policy_id} not found or not accessible"
                }
                
        except Exception as e:
            logger.error(f"Error validating policy {policy_id}: {e}")
            return {
                "valid": False,
                "error": str(e),
                "message": f"Failed to validate policy {policy_id}"
            }

def create_energy_report_from_data(device_data: List[Dict], device_id: str) -> EnergyReport:
    """Create an EnergyReport from sensor data"""
    if not device_data:
        raise ValueError("No data provided for energy report")
    
    # Sort data by timestamp
    sorted_data = sorted(device_data, key=lambda x: x['timestamp'])
    
    # Calculate aggregated metrics
    total_energy = max([d.get('total_energy_kwh', 0) for d in sorted_data])
    powers = [d.get('power', 0) for d in sorted_data if d.get('power')]
    efficiencies = [d.get('efficiency', 0) for d in sorted_data if d.get('efficiency')]
    irradiances = [d.get('irradiance_w_m2', 0) for d in sorted_data if d.get('irradiance_w_m2')]
    temperatures = [d.get('ambient_temp_c', 0) for d in sorted_data if d.get('ambient_temp_c')]
    
    # Create verification hash (simple hash of key metrics)
    import hashlib
    hash_data = f"{device_id}_{len(sorted_data)}_{total_energy}_{sum(powers)}"
    verification_hash = hashlib.sha256(hash_data.encode()).hexdigest()[:16]
    
    return EnergyReport(
        device_id=device_id,
        period_start=datetime.fromisoformat(sorted_data[0]['timestamp'].replace('Z', '+00:00')),
        period_end=datetime.fromisoformat(sorted_data[-1]['timestamp'].replace('Z', '+00:00')),
        total_energy_kwh=total_energy,
        avg_power_w=sum(powers) / len(powers) if powers else 0,
        max_power_w=max(powers) if powers else 0,
        avg_efficiency=sum(efficiencies) / len(efficiencies) if efficiencies else 0,
        avg_irradiance=sum(irradiances) / len(irradiances) if irradiances else 0,
        avg_temperature=sum(temperatures) / len(temperatures) if temperatures else 0,
        data_points=len(sorted_data),
        verification_hash=verification_hash
    )

# Example usage and testing
if __name__ == "__main__":
    # Test Guardian connection
    guardian = GuardianService()
    
    print("🔍 Testing Guardian connection...")
    health = guardian.health_check()
    print(f"Guardian Status: {health}")
    
    if health.get("connected"):
        print("✅ Guardian is accessible")
        
        # Get available policies
        policies = guardian.get_policies(status="PUBLISH")  # Only get published policies
        print(f"📋 Available published policies: {len(policies)}")
        
        if policies:
            # Show first policy details
            first_policy = policies[0]
            print(f"First policy: {first_policy.get('name', 'Unknown')} (ID: {first_policy.get('id', 'Unknown')})")
            
            # Test getting specific policy
            policy_id = first_policy.get('id')
            if policy_id:
                policy_details = guardian.get_policy(policy_id)
                if policy_details:
                    print(f"✅ Successfully retrieved policy details for {policy_id}")
                
                # Test getting policy documents
                documents = guardian.get_policy_documents(policy_id)
                print(f"📄 Policy documents: {len(documents)}")
        
        # Get available tokens
        tokens = guardian.get_tokens()
        print(f"🪙 Available tokens: {len(tokens)}")
        
    else:
        print("❌ Guardian is not accessible")
        print("💡 Make sure Guardian is running: docker compose -f docker-compose-quickstart.yml up -d")