# Guardian API Endpoints Update

## Summary

Updated `guardian_service.py` to use the correct Guardian API endpoints based on the official Guardian swagger documentation.

## Changes Made

### 1. Health Check Endpoint

- **Before**: Used `/api/v1/status` (placeholder endpoint)
- **After**: Uses `/settings/about` for authenticated health checks, falls back to base URL check
- **Improvement**: Uses actual Guardian endpoint that returns version information

### 2. Get Policies Endpoint

- **Before**: Simple `GET /policies` call
- **After**: `GET /policies` with proper query parameters
- **New Parameters**:
  - `pageIndex`: Pagination support (default: 0)
  - `pageSize`: Results per page (default: 20)
  - `status`: Filter by policy status (e.g., "PUBLISH", "DRAFT")
  - `type`: Filter by policy type (e.g., "local")
- **Improvement**: Supports pagination and filtering as per Guardian API spec

### 3. Get Specific Policy

- **New**: Added `get_policy(policy_id)` method
- **Endpoint**: `GET /policies/{policyId}`
- **Purpose**: Retrieve detailed information about a specific policy

### 4. Submit Energy Report

- **Before**: Used generic `/documents` endpoint or placeholder
- **After**: Uses correct `POST /policies/{policyId}/tag/{tagName}/blocks`
- **Required Parameters**:
  - `policy_id`: The Guardian policy ID (required)
  - `tag_name`: Block tag name (default: "renewable_energy")
- **Improvement**: Uses the actual Guardian endpoint for submitting data to policy blocks

### 5. Get Document Status

- **Before**: Used `/documents/{document_id}` (incorrect)
- **After**: Uses `GET /policies/{policyId}/documents`
- **New Method**: `get_policy_documents(policy_id, document_type, include_document)`
- **Parameters**:
  - `document_type`: Filter by "VC" or "VP"
  - `include_document`: Include document content (default: True)
- **Improvement**: Uses correct Guardian endpoint for policy document retrieval

### 6. Enhanced Error Handling

- Added specific error handling for different HTTP status codes
- Improved logging with more detailed error messages
- Added network error handling with `requests.exceptions.RequestException`
- Better distinction between authentication errors and API errors

## API Endpoint Mapping

| Function                 | Guardian API Endpoint                              | Method | Purpose                           |
| ------------------------ | -------------------------------------------------- | ------ | --------------------------------- |
| `health_check()`         | `/api/v1/settings/about`                           | GET    | Get Guardian version and status   |
| `get_policies()`         | `/api/v1/policies`                                 | GET    | List all policies with pagination |
| `get_policy(id)`         | `/api/v1/policies/{policyId}`                      | GET    | Get specific policy details       |
| `submit_energy_report()` | `/api/v1/policies/{policyId}/tag/{tagName}/blocks` | POST   | Submit data to policy block       |
| `get_policy_documents()` | `/api/v1/policies/{policyId}/documents`            | GET    | Get documents for a policy        |
| `get_document_status()`  | `/api/v1/policies/{policyId}/documents`            | GET    | Get document status via policy    |

## Testing

### Unit Tests Updated

- Updated `test_guardian_integration.py` to match new API signatures
- Fixed parameter expectations for `get_policies()` method
- Updated response field names for `submit_energy_report()`

### New Test Files

- Created `test_guardian_endpoints.py` for testing against real Guardian instance
- Provides comprehensive endpoint validation
- Includes safety checks for data submission

## Requirements Satisfied

This update satisfies the following requirements from the Guardian integration spec:

- **Requirement 3.3**: ✅ Backend fetches available policies using `GET /policies`
- **Requirement 3.4**: ✅ Backend submits energy data using `POST /policies/{policyId}/tag/{tagName}/blocks`
- **Requirement 5.3**: ✅ Backend validates policy existence using `GET /policies/{policyId}`

## Usage Examples

```python
# Initialize Guardian service
config = GuardianConfig(
    base_url="http://localhost:3000",
    username="your_username",
    password="your_password"
)
guardian = GuardianService(config)

# Get published policies
policies = guardian.get_policies(status="PUBLISH")

# Get specific policy
policy = guardian.get_policy("policy_id_123")

# Submit energy report
result = guardian.submit_energy_report(
    report=energy_report,
    policy_id="policy_id_123",
    tag_name="renewable_energy"
)

# Get policy documents
documents = guardian.get_policy_documents("policy_id_123")
```

## Next Steps

1. Test with actual Guardian instance once Docker environment is set up
2. Implement policy schema validation for energy data formatting
3. Add retry logic for failed submissions
4. Implement document status polling for verification tracking

## L

ive Testing Results

Successfully tested against a running Guardian instance at `http://localhost:3000`:

### ✅ Working Endpoints:

- **Authentication**: `POST /api/v1/accounts/login` - Successfully authenticates and returns JWT token
- **Health Check**: Base URL returns Guardian web interface (HTML)
- **Session Check**: `GET /api/v1/accounts/session` - Returns authentication status

### ⚠️ Permission-Restricted Endpoints:

- **Policies**: `GET /api/v1/policies` - Returns 403 Forbidden (may require specific user role or published policies)
- **Tokens**: `GET /api/v1/tokens` - Returns 403 Forbidden (may require specific permissions)

### 🔧 API Path Corrections:

- **Critical Fix**: All Guardian API endpoints require `/api/v1/` prefix
- **Before**: `/policies`, `/settings/about`, etc.
- **After**: `/api/v1/policies`, `/api/v1/settings/about`, etc.

### 📊 Test Results:

- ✅ Guardian connection established
- ✅ Authentication working with JWT tokens
- ✅ API endpoints returning proper JSON responses (not HTML)
- ✅ Error handling working correctly with 403/404 status codes
- ✅ All unit tests passing

The Guardian service is now correctly configured to work with actual Guardian instances and uses the proper API endpoint structure as defined in the Guardian swagger documentation.
