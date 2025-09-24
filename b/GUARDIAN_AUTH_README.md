# Guardian Authentication Service

This module provides comprehensive authentication and session management for the Hedera Guardian platform, enabling secure API communication with automatic token refresh and error handling.

## Features

- **Secure Authentication**: Username/password login with bearer token management
- **Automatic Token Refresh**: Seamless token renewal before expiration
- **Session Management**: Persistent authentication state with validation
- **Error Handling**: Comprehensive error recovery and retry logic
- **Integration Ready**: Easy integration with Guardian API services

## Quick Start

### Basic Authentication

```python
from guardian_auth import GuardianAuth, GuardianAuthError

# Initialize authentication service
auth = GuardianAuth(base_url="http://localhost:3000")

try:
    # Login with credentials
    token = auth.login("your_username", "your_password")
    print(f"Authenticated as: {token.username}")
    print(f"Token expires: {token.expires_at}")
    
    # Check if token is valid
    if auth.is_token_valid():
        print("Authentication successful!")
    
    # Logout when done
    auth.logout()
    
except GuardianAuthError as e:
    print(f"Authentication failed: {e}")
```

### Service Integration

```python
from guardian_service import GuardianService, GuardianConfig

# Configure Guardian service with authentication
config = GuardianConfig(
    base_url="http://localhost:3000",
    username="your_username",
    password="your_password"
)

# Initialize service (automatically authenticates)
service = GuardianService(config)

# Check connection and authentication status
health = service.health_check()
print(f"Connected: {health['connected']}")
print(f"Authenticated: {health['authenticated']}")

# Use authenticated API calls
policies = service.get_policies()
tokens = service.get_tokens()
```

## Environment Configuration

Set up your environment variables for seamless authentication:

```bash
# Guardian Configuration
export GUARDIAN_URL=http://localhost:3000
export GUARDIAN_USERNAME=your_guardian_username
export GUARDIAN_PASSWORD=your_guardian_password
```

Or create a `.env` file:

```env
GUARDIAN_URL=http://localhost:3000
GUARDIAN_USERNAME=your_guardian_username
GUARDIAN_PASSWORD=your_guardian_password
```

## API Reference

### GuardianAuth Class

#### Constructor

```python
GuardianAuth(base_url: str = "http://localhost:3000", timeout: int = 30)
```

- `base_url`: Guardian API base URL
- `timeout`: Request timeout in seconds

#### Methods

##### login(username: str, password: str) -> AuthToken

Authenticate with Guardian using username and password.

```python
token = auth.login("username", "password")
```

**Returns**: `AuthToken` object with token details
**Raises**: `GuardianAuthError` on authentication failure

##### logout() -> bool

Logout from Guardian and invalidate current token.

```python
success = auth.logout()
```

**Returns**: `True` if logout successful, `False` otherwise

##### refresh_token() -> Optional[AuthToken]

Refresh the current authentication token.

```python
new_token = auth.refresh_token()
```

**Returns**: New `AuthToken` if successful, `None` otherwise

##### is_token_valid() -> bool

Check if current token is valid and not expired.

```python
if auth.is_token_valid():
    print("Token is valid")
```

**Returns**: `True` if token is valid, `False` otherwise

##### ensure_valid_token(username: str = None, password: str = None) -> bool

Ensure we have a valid token, refreshing or re-authenticating if needed.

```python
if auth.ensure_valid_token("username", "password"):
    # Token is guaranteed to be valid
    pass
```

**Returns**: `True` if valid token is available, `False` otherwise

##### make_authenticated_request(method: str, endpoint: str, **kwargs) -> requests.Response

Make an authenticated request to Guardian API with automatic token refresh.

```python
response = auth.make_authenticated_request('GET', '/policies')
```

**Returns**: `requests.Response` object
**Raises**: `GuardianAuthError` if no valid token available

##### get_auth_headers() -> Dict[str, str]

Get headers with current authentication token.

```python
headers = auth.get_auth_headers()
# Returns: {"Authorization": "Bearer <token>"} or {}
```

##### get_user_info() -> Optional[Dict[str, Any]]

Get current user information from Guardian.

```python
user_info = auth.get_user_info()
if user_info:
    print(f"User: {user_info['username']}")
```

### AuthToken Class

Represents an authentication token with metadata.

#### Properties

- `token: str` - The bearer token
- `expires_at: datetime` - Token expiration time
- `refresh_token: Optional[str]` - Refresh token for renewal
- `user_id: Optional[str]` - User ID
- `username: Optional[str]` - Username

#### Methods

##### is_expired() -> bool

Check if token is expired (with 5-minute buffer).

##### time_until_expiry() -> timedelta

Get time remaining until token expires.

##### to_dict() -> Dict[str, Any]

Convert token to dictionary for serialization.

##### from_dict(data: Dict[str, Any]) -> AuthToken

Create token from dictionary.

## Error Handling

The authentication service provides comprehensive error handling:

### GuardianAuthError

Custom exception for Guardian authentication errors.

```python
try:
    auth.login("username", "password")
except GuardianAuthError as e:
    if "Invalid username or password" in str(e):
        print("Check your credentials")
    elif "Cannot connect" in str(e):
        print("Guardian service is not running")
    elif "timeout" in str(e):
        print("Request timed out")
```

### Common Error Scenarios

1. **Invalid Credentials**: Wrong username/password
2. **Connection Error**: Guardian service not running
3. **Timeout**: Network or service timeout
4. **Token Expired**: Automatic refresh attempted
5. **Forbidden Access**: User lacks required permissions

## Testing

### Unit Tests

Run the comprehensive unit test suite:

```bash
python run_auth_tests.py
```

### Integration Tests

Test with Guardian service integration:

```bash
python test_guardian_integration.py
```

### Demo

Run the interactive demo:

```bash
python demo_guardian_auth.py
```

## Guardian Service Integration

The authentication service is fully integrated with the Guardian service:

```python
from guardian_service import GuardianService, GuardianConfig

# Service automatically handles authentication
config = GuardianConfig(
    base_url="http://localhost:3000",
    username="your_username",
    password="your_password"
)

service = GuardianService(config)

# All API calls are automatically authenticated
policies = service.get_policies()
health = service.health_check()
```

### Automatic Features

- **Login on Initialization**: Automatic authentication when service starts
- **Token Refresh**: Automatic token renewal before expiration
- **Retry Logic**: Automatic retry on authentication failures
- **Error Recovery**: Graceful handling of authentication errors

## Security Considerations

### Token Storage

- Tokens are stored in memory only
- No persistent storage of credentials
- Automatic token cleanup on logout

### Network Security

- HTTPS recommended for production
- Bearer token authentication
- Request timeout protection
- Connection error handling

### Best Practices

1. **Use Environment Variables**: Store credentials securely
2. **Regular Token Refresh**: Tokens automatically refreshed
3. **Proper Logout**: Always logout when done
4. **Error Handling**: Handle authentication errors gracefully
5. **Connection Validation**: Check connection before operations

## Production Deployment

### Environment Setup

```bash
# Production Guardian URL
export GUARDIAN_URL=https://your-guardian-instance.com

# Secure credential storage
export GUARDIAN_USERNAME=production_user
export GUARDIAN_PASSWORD=secure_password
```

### Docker Integration

```yaml
services:
  verifiedcc-backend:
    environment:
      - GUARDIAN_URL=http://guardian-service:3000
      - GUARDIAN_USERNAME=${GUARDIAN_USERNAME}
      - GUARDIAN_PASSWORD=${GUARDIAN_PASSWORD}
    depends_on:
      - guardian-service
```

### Health Monitoring

```python
# Regular health checks
health = service.health_check()
if not health['authenticated']:
    # Alert monitoring system
    logger.error("Guardian authentication failed")
```

## Troubleshooting

### Common Issues

1. **"Cannot connect to Guardian API"**
   - Check if Guardian is running
   - Verify the base URL
   - Check network connectivity

2. **"Invalid username or password"**
   - Verify credentials
   - Check user exists in Guardian
   - Ensure user has required permissions

3. **"Token refresh failed"**
   - Check if refresh token is valid
   - Re-authenticate with username/password
   - Verify Guardian service is running

4. **"Request timeout"**
   - Increase timeout value
   - Check network latency
   - Verify Guardian service performance

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all authentication operations will be logged
auth = GuardianAuth()
```

### Connection Testing

Test Guardian connectivity:

```bash
curl http://localhost:3000/api/v1/status
```

## Requirements

- Python 3.7+
- requests >= 2.31.0
- python-dateutil >= 2.8.2

## License

This module is part of the VerifiedCC project and follows the same licensing terms.