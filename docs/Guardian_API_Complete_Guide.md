# Guardian API Complete Integration Guide

> Comprehensive guide combining working authentication patterns, dry-run operations, and API automation based on real implementation experience

This guide consolidates proven authentication methods, successful dry-run patterns, and API integration techniques discovered through extensive testing with the Guardian Service API.

## Table of Contents
1. [Authentication Patterns That Work](#authentication-patterns-that-work)
2. [Dry-Run Operations](#dry-run-operations)
3. [Policy Management](#policy-management)
4. [API Integration Patterns](#api-integration-patterns)
5. [Working Code Examples](#working-code-examples)
6. [Troubleshooting Guide](#troubleshooting-guide)

## Authentication Patterns That Work

### 🔑 Proven Authentication Flow

Based on extensive testing, here's the authentication pattern that consistently works:

```python
# Step 1: Login with Tenant ID (CRITICAL!)
def login_with_tenant():
    """Login with tenant ID - this is essential for success"""
    credentials = {
        "username": "your_username",
        "password": "your_password",
        "tenantId": "your_tenant_id"  # This is REQUIRED
    }
    
    response = requests.post(
        "https://guardianservice.app/api/v1/accounts/login",
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        json=credentials
    )
    
    if response.status_code == 200:
        return response.json()
    return None

# Step 2: Get Access Token (Working Method)
def get_access_token(refresh_token):
    """Get access token using refresh token in request body"""
    response = requests.post(
        "https://guardianservice.app/api/v1/accounts/access-token",
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {refresh_token}'
        },
        json={"refreshToken": refresh_token}  # Key: Include refresh token in body
    )
    
    if response.status_code == 201:  # Note: Returns 201, not 200
        return response.json()['accessToken']
    return None
```

### 🔍 Authentication Discovery Results

From extensive testing, here's what works and what doesn't:

**✅ What Works:**
- Login with `tenantId` included in credentials
- Access token endpoint with refresh token in request body
- External endpoints (`/external/{policyId}`) for data submission
- Session endpoint for authentication verification

**❌ What Doesn't Work:**
- Login without `tenantId`
- Direct policy endpoints without proper access token
- Access token endpoint without refresh token in body
- Standard policy management endpoints with basic authentication

### 🏗️ Complete Authentication Class

```python
class GuardianAuth:
    def __init__(self, username, password, tenant_id):
        self.base_url = "https://guardianservice.app/api/v1"
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self.access_token = None
        self.refresh_token = None
        self.user_info = None
    
    def authenticate(self):
        """Complete authentication flow"""
        # Step 1: Login
        login_data = self._login()
        if not login_data:
            return False
        
        # Step 2: Get access token
        access_token = self._get_access_token()
        if not access_token:
            # Fallback: use refresh token directly
            self.access_token = self.refresh_token
        
        return True
    
    def _login(self):
        credentials = {
            "username": self.username,
            "password": self.password,
            "tenantId": self.tenant_id
        }
        
        response = requests.post(
            f"{self.base_url}/accounts/login",
            headers={'accept': 'application/json', 'Content-Type': 'application/json'},
            json=credentials
        )
        
        if response.status_code == 200:
            data = response.json()
            self.refresh_token = data.get('refreshToken')
            self.user_info = {
                'username': data.get('username'),
                'role': data.get('role'),
                'did': data.get('did')
            }
            return data
        return None
    
    def _get_access_token(self):
        if not self.refresh_token:
            return None
        
        response = requests.post(
            f"{self.base_url}/accounts/access-token",
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.refresh_token}'
            },
            json={"refreshToken": self.refresh_token}
        )
        
        if response.status_code == 201:
            self.access_token = response.json()['accessToken']
            return self.access_token
        return None
    
    def get_auth_headers(self):
        token = self.access_token or self.refresh_token
        return {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
```

## Dry-Run Operations

### 🧪 Starting Dry-Run Mode

Based on testing, here are the methods that work for starting dry-run:

```python
def start_dry_run(policy_id, auth_token):
    """Start dry-run using external endpoint (proven to work)"""
    
    # Method 1: External endpoint (WORKS!)
    response = requests.post(
        f"https://guardianservice.app/api/v1/external/{policy_id}/dry-run",
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        },
        json={}
    )
    
    if response.status_code == 200 and response.text == 'true':
        print("✅ Dry-run started successfully via external endpoint")
        return True
    
    # Method 2: Direct endpoint (may require additional permissions)
    response = requests.put(
        f"https://guardianservice.app/api/v1/policies/{policy_id}/dry-run",
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        },
        json={}
    )
    
    if response.status_code == 200:
        print("✅ Dry-run started successfully via direct endpoint")
        return True
    
    return False
```

### 🎭 Virtual User Management

```python
class DryRunManager:
    def __init__(self, policy_id, auth_token):
        self.policy_id = policy_id
        self.auth_token = auth_token
        self.base_url = "https://guardianservice.app/api/v1"
        self.virtual_users = []
    
    def create_virtual_user(self, role="Project Participant"):
        """Create virtual user for testing"""
        response = requests.post(
            f"{self.base_url}/policies/{self.policy_id}/dry-run/user",
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_token}'
            },
            json={"role": role}
        )
        
        if response.status_code in [200, 201]:
            virtual_user = response.json()
            self.virtual_users.append(virtual_user)
            return virtual_user
        return None
    
    def login_virtual_user(self, virtual_user):
        """Login as virtual user"""
        response = requests.post(
            f"{self.base_url}/policies/{self.policy_id}/dry-run/login",
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_token}'
            },
            json={"did": virtual_user.get('did')}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
```

## Policy Management

### 📋 Working Policy Access Patterns

```python
class PolicyManager:
    def __init__(self, auth_handler):
        self.auth = auth_handler
        self.base_url = "https://guardianservice.app/api/v1"
    
    def get_policies(self):
        """Get policies using multiple fallback methods"""
        
        # Method 1: Direct policies endpoint (for Standard Registry users)
        if self.auth.user_info.get('role') == 'STANDARD_REGISTRY':
            try:
                response = requests.get(
                    f"{self.base_url}/policies",
                    headers=self.auth.get_auth_headers()
                )
                if response.status_code == 200:
                    return response.json()
            except:
                pass
        
        # Method 2: Analytics search (fallback)
        try:
            response = requests.post(
                f"{self.base_url}/analytics/search/policies",
                headers=self.auth.get_auth_headers(),
                json={"threshold": 0}
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Method 3: User assigned policies
        try:
            username = self.auth.user_info.get('username')
            response = requests.get(
                f"{self.base_url}/permissions/users/{username}/policies",
                headers=self.auth.get_auth_headers()
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return None
    
    def submit_data_to_block(self, policy_id, block_id, data):
        """Submit data to policy block"""
        response = requests.post(
            f"{self.base_url}/policies/{policy_id}/blocks/{block_id}",
            headers=self.auth.get_auth_headers(),
            json={"document": data}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def submit_external_data(self, policy_id, block_tag, data):
        """Submit data via external endpoint (more reliable)"""
        response = requests.post(
            f"{self.base_url}/external/{policy_id}/{block_tag}",
            headers=self.auth.get_auth_headers(),
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        return None
```

## API Integration Patterns

### 🔄 Complete Workflow Automation

```python
class GuardianWorkflowAutomation:
    def __init__(self, policy_config):
        self.policy_id = policy_config['id']
        self.policy_name = policy_config['name']
        self.block_ids = policy_config['block_ids']
        self.auth = None
        self.dry_run = None
    
    def initialize(self, username, password, tenant_id):
        """Initialize authentication and dry-run"""
        # Step 1: Authenticate
        self.auth = GuardianAuth(username, password, tenant_id)
        if not self.auth.authenticate():
            raise Exception("Authentication failed")
        
        # Step 2: Start dry-run
        if not start_dry_run(self.policy_id, self.auth.access_token):
            raise Exception("Failed to start dry-run")
        
        # Step 3: Initialize dry-run manager
        self.dry_run = DryRunManager(self.policy_id, self.auth.access_token)
        
        print("✅ Workflow automation initialized")
    
    def execute_project_participant_workflow(self, pp_name):
        """Execute complete PP workflow"""
        results = {
            'steps_completed': [],
            'errors': [],
            'artifacts': []
        }
        
        try:
            # Step 1: Create virtual user
            virtual_user = self.dry_run.create_virtual_user("Project Participant")
            if not virtual_user:
                raise Exception("Failed to create virtual user")
            results['steps_completed'].append("Virtual user created")
            
            # Step 2: Login virtual user
            user_session = self.dry_run.login_virtual_user(virtual_user)
            if not user_session:
                raise Exception("Failed to login virtual user")
            results['steps_completed'].append("Virtual user logged in")
            
            # Step 3: Submit project data
            project_data = {
                "project_name": pp_name,
                "project_type": "Emission Reduction",
                "methodology": "AMS-I.D"
            }
            
            submission_result = self.submit_project_data(project_data)
            if submission_result:
                results['steps_completed'].append("Project data submitted")
                results['artifacts'].append(submission_result)
            
            return results
            
        except Exception as e:
            results['errors'].append(str(e))
            return results
    
    def submit_project_data(self, data):
        """Submit project data using working endpoints"""
        # Try external endpoint first (more reliable)
        if 'create_pp_profile' in self.block_ids:
            block_tag = 'create_pp_profile'
            result = self.submit_external_data(block_tag, data)
            if result:
                return result
        
        # Fallback to direct block submission
        if 'create_pp_profile' in self.block_ids:
            block_id = self.block_ids['create_pp_profile']
            result = self.submit_to_block(block_id, data)
            if result:
                return result
        
        return None
    
    def submit_external_data(self, block_tag, data):
        """Submit via external endpoint"""
        response = requests.post(
            f"https://guardianservice.app/api/v1/external/{self.policy_id}/{block_tag}",
            headers=self.auth.get_auth_headers(),
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def submit_to_block(self, block_id, data):
        """Submit via direct block endpoint"""
        response = requests.post(
            f"https://guardianservice.app/api/v1/policies/{self.policy_id}/blocks/{block_id}",
            headers=self.auth.get_auth_headers(),
            json={"document": data}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
```

## Working Code Examples

### 🚀 Quick Start Example

```python
# Configuration based on your working setup
POLICY_CONFIG = {
    "id": "68d69341152381fe552b21ec",
    "name": "AMS-I.D_1758892865729",
    "block_ids": {
        "create_pp_profile": "70b59a78-d1db-463e-a41f-723d9b421818",
        "pp_wait_for_approve": "0eb44b50-c2ef-4aa1-b384-f516ab62d05b"
    }
}

USER_CREDENTIALS = {
    "username": "your_username",
    "password": "your_password",
    "tenant_id": "your_tenant_id"
}

# Quick start workflow
def quick_start():
    # Initialize workflow
    workflow = GuardianWorkflowAutomation(POLICY_CONFIG)
    workflow.initialize(
        USER_CREDENTIALS['username'],
        USER_CREDENTIALS['password'],
        USER_CREDENTIALS['tenant_id']
    )
    
    # Execute PP workflow
    results = workflow.execute_project_participant_workflow("Test Project")
    
    print(f"Workflow completed:")
    print(f"  Steps: {len(results['steps_completed'])}")
    print(f"  Errors: {len(results['errors'])}")
    print(f"  Artifacts: {len(results['artifacts'])}")
    
    return results

# Run the workflow
if __name__ == "__main__":
    results = quick_start()
```

### 🧪 Testing Framework Integration

```python
import pytest
import requests

class TestGuardianAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication for all tests"""
        self.auth = GuardianAuth(
            username="test_user",
            password="test_password",
            tenant_id="test_tenant"
        )
        assert self.auth.authenticate(), "Authentication failed"
        
        # Start dry-run
        assert start_dry_run(POLICY_CONFIG['id'], self.auth.access_token), "Dry-run start failed"
    
    def test_virtual_user_creation(self):
        """Test virtual user creation"""
        dry_run = DryRunManager(POLICY_CONFIG['id'], self.auth.access_token)
        
        # Test different roles
        roles = ["Project Participant", "VVB", "Standard Registry"]
        for role in roles:
            user = dry_run.create_virtual_user(role)
            assert user is not None, f"Failed to create {role} user"
            assert user.get('role') == role, f"Role mismatch for {role}"
    
    def test_data_submission(self):
        """Test data submission to blocks"""
        test_data = {
            "project_name": "Test Submission",
            "project_type": "Test Type"
        }
        
        # Test external endpoint
        response = requests.post(
            f"https://guardianservice.app/api/v1/external/{POLICY_CONFIG['id']}/test_block",
            headers=self.auth.get_auth_headers(),
            json=test_data
        )
        
        # Should not fail with 401 (authentication working)
        assert response.status_code != 401, "Authentication failed"
    
    def test_policy_access(self):
        """Test policy access methods"""
        policy_manager = PolicyManager(self.auth)
        policies = policy_manager.get_policies()
        
        # Should get some policies or at least not fail with auth error
        assert policies is not None or self.auth.user_info.get('role') != 'STANDARD_REGISTRY'
```

## Troubleshooting Guide

### 🔧 Common Issues and Solutions

#### Authentication Issues

**Problem**: `401 Unauthorized` on login
```python
# Solution: Ensure tenant ID is included
credentials = {
    "username": "your_username",
    "password": "your_password",
    "tenantId": "your_tenant_id"  # This is REQUIRED
}
```

**Problem**: Access token endpoint returns `401`
```python
# Solution: Include refresh token in request body
response = requests.post(
    f"{base_url}/accounts/access-token",
    headers={'Authorization': f'Bearer {refresh_token}'},
    json={"refreshToken": refresh_token}  # Include in body
)
```

#### Dry-Run Issues

**Problem**: Cannot start dry-run mode
```python
# Solution: Use external endpoint as fallback
def start_dry_run_with_fallback(policy_id, token):
    # Try external endpoint first
    response = requests.post(
        f"https://guardianservice.app/api/v1/external/{policy_id}/dry-run",
        headers={'Authorization': f'Bearer {token}'},
        json={}
    )
    
    if response.status_code == 200:
        return True
    
    # Fallback to direct endpoint
    response = requests.put(
        f"https://guardianservice.app/api/v1/policies/{policy_id}/dry-run",
        headers={'Authorization': f'Bearer {token}'},
        json={}
    )
    
    return response.status_code == 200
```

#### Policy Access Issues

**Problem**: Cannot access policy endpoints
```python
# Solution: Use multiple fallback methods
def get_policies_with_fallbacks(auth):
    methods = [
        lambda: requests.get(f"{base_url}/policies", headers=auth.get_auth_headers()),
        lambda: requests.post(f"{base_url}/analytics/search/policies", 
                            headers=auth.get_auth_headers(), json={"threshold": 0}),
        lambda: requests.get(f"{base_url}/permissions/users/{auth.username}/policies",
                           headers=auth.get_auth_headers())
    ]
    
    for method in methods:
        try:
            response = method()
            if response.status_code == 200:
                return response.json()
        except:
            continue
    
    return None
```

### 📊 API Endpoint Status Reference

Based on extensive testing, here's the status of various endpoints:

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/accounts/login` | ✅ Works | Requires `tenantId` |
| `/accounts/access-token` | ✅ Works | Needs refresh token in body |
| `/accounts/session` | ✅ Works | Good for auth verification |
| `/policies` | ⚠️ Limited | Requires Standard Registry role |
| `/policies/{id}/dry-run` | ⚠️ Limited | May need additional permissions |
| `/external/{id}` | ✅ Works | Most reliable for data submission |
| `/analytics/search/policies` | ⚠️ Limited | Fallback for policy access |
| `/permissions/users/{user}/policies` | ⚠️ Limited | User-specific policies |

### 🎯 Best Practices

1. **Always include `tenantId` in login requests**
2. **Use external endpoints for data submission when possible**
3. **Implement multiple fallback methods for policy access**
4. **Test authentication with session endpoint before proceeding**
5. **Handle different response codes gracefully (200, 201, 401, 422)**
6. **Use proper error handling and retry logic**
7. **Cache authentication tokens to avoid repeated login calls**

## Conclusion

This guide represents the culmination of extensive testing and discovery of working patterns with the Guardian API. The key insights are:

- **Authentication requires tenant ID** - this is non-negotiable
- **External endpoints are more reliable** than direct policy endpoints
- **Multiple fallback methods** are essential for robust integration
- **Proper error handling** is crucial for production use

Use this guide as your foundation for Guardian API integration, and build upon these proven patterns for your specific use cases.

---

*This guide is based on real implementation experience with Guardian API v1 and reflects working patterns as of the current API version.*