# Managed Guardian Service (MGS) API Guide

## Overview
The Managed Guardian Service (MGS) API enables applications to mint emissions and carbon offset tokens without managing complex blockchain infrastructure. This guide covers the essential workflows and endpoints for integrating with the MGS platform.

## Base Configuration
- **Base URL**: `{server}/api/v1`
- **Authentication**: Bearer token required for most endpoints
- **Content-Type**: `application/json`
- **API Version**: 3.3.0-rc

## Getting Started

### 1. User Registration & Authentication

#### Register a New User
```http
POST /accounts/register
Content-Type: application/json

{
  "username": "your_username",
  "email": "user@example.com",
  "password": "secure_password",
  "role": "USER"
}
```

#### Login
```http
POST /accounts/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "secure_password"
}
```

#### Get Access Token
```http
POST /accounts/access-token
Authorization: Bearer {session_token}
```

### 2. Profile Setup

#### Configure Hedera Credentials
```http
PUT /profiles/{username}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "hederaAccountId": "0.0.123456",
  "hederaAccountKey": "your_private_key"
}
```

#### Check Account Balance
```http
GET /accounts/balance
Authorization: Bearer {access_token}
```

## Core Workflows

### Working with Policies

#### 1. Create a New Policy
```http
POST /policies
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Carbon Credit Policy",
  "description": "Policy for managing carbon credits",
  "version": "1.0.0",
  "policyTag": "carbon_credit_v1"
}
```

#### 2. Import Existing Policy
```http
POST /policies/import/message
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "messageId": "hedera_message_id"
}
```

#### 3. Validate Policy
```http
POST /policies/validate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "policy": {policy_configuration}
}
```

#### 4. Publish Policy
```http
PUT /policies/{policyId}/publish
Authorization: Bearer {access_token}
```

#### 5. Dry Run Testing
```http
PUT /policies/{policyId}/dry-run
Authorization: Bearer {access_token}
```

### Working with Schemas

#### 1. Create Schema
```http
POST /schemas/{topicId}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Emission Data Schema",
  "description": "Schema for emission reporting",
  "entity": "VC",
  "document": {
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "type": "object",
    "properties": {
      "emissionAmount": {"type": "number"},
      "emissionType": {"type": "string"},
      "reportingPeriod": {"type": "string"}
    }
  }
}
```

#### 2. Publish Schema
```http
PUT /schemas/{schemaId}/publish
Authorization: Bearer {access_token}
```

### Token Management

#### 1. Create Token
```http
POST /tokens
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "tokenName": "Carbon Credit Token",
  "tokenSymbol": "CCT",
  "tokenType": "NON_FUNGIBLE_UNIQUE",
  "decimals": 0,
  "initialSupply": "0",
  "enableAdmin": true,
  "enableKYC": true,
  "enableFreeze": true,
  "enableWipe": true
}
```

#### 2. Associate Token with User
```http
PUT /tokens/{tokenId}/associate
Authorization: Bearer {access_token}
```

#### 3. Grant KYC
```http
PUT /tokens/{tokenId}/{username}/grant-kyc
Authorization: Bearer {access_token}
```

## Advanced Features

### Dry Run Mode

#### Create Virtual Users
```http
POST /policies/{policyId}/dry-run/user
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "test_user",
  "role": "USER"
}
```

#### Switch Virtual User
```http
POST /policies/{policyId}/dry-run/login
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "test_user"
}
```

#### Create Savepoint
```http
POST /policies/{policyId}/savepoint/create
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "checkpoint_1"
}
```

### External Data Integration

#### Send External Data
```http
POST /external/{policyId}/{blockTag}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "data": {
    "sensorReading": 150.5,
    "timestamp": "2024-01-15T10:30:00Z",
    "location": "Facility A"
  }
}
```

### Contract Operations

#### Retire Tokens
```http
POST /contracts/retire/pools/{poolId}/retire
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "tokenId": "0.0.123456",
  "amount": "100",
  "reason": "Carbon offset retirement"
}
```

## Data Submission Workflow

### 1. Policy Block Interaction
```http
GET /policies/{policyId}/blocks
Authorization: Bearer {access_token}
```

### 2. Submit Data to Block
```http
POST /policies/{policyId}/blocks/{blockId}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "document": {
    "type": "emission_report",
    "data": {
      "co2Emissions": 1500,
      "reportingPeriod": "2024-Q1",
      "facility": "Manufacturing Plant A"
    }
  }
}
```

### 3. Submit via Tag
```http
POST /policies/{policyId}/tag/{tagName}/blocks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "document": {emission_data}
}
```

## Monitoring & Analytics

### Get Policy Documents
```http
GET /policies/{policyId}/documents
Authorization: Bearer {access_token}
```

### Search Documents with Filters
```http
GET /policies/{policyId}/search-documents?type=VC&status=VERIFIED
Authorization: Bearer {access_token}
```

### Trust Chain Verification
```http
GET /trust-chains/{documentHash}
Authorization: Bearer {access_token}
```

### Get Policy Statistics
```http
GET /policy-statistics/{definitionId}/assessment
Authorization: Bearer {access_token}
```

## Error Handling

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `451` - Unavailable for Legal Reasons
- `500` - Internal Server Error
- `503` - Service Unavailable

Example error response:
```json
{
  "error": "ValidationError",
  "message": "Invalid schema format",
  "details": {
    "field": "document.properties",
    "issue": "Missing required property"
  }
}
```

## Best Practices

### Authentication
- Store access tokens securely
- Refresh tokens before expiration
- Use HTTPS for all requests
- Implement proper session management

### Policy Development
- Always validate policies before publishing
- Use dry-run mode for testing
- Create savepoints during development
- Test with multiple user roles

### Data Submission
- Validate data against schemas before submission
- Handle async operations properly
- Implement retry logic for failed requests
- Monitor transaction status

### Performance
- Use pagination for large datasets
- Cache frequently accessed data
- Batch operations when possible
- Monitor API rate limits

## Integration Examples

### Python Integration
```python
import requests

class MGSClient:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def create_policy(self, policy_data):
        response = requests.post(
            f'{self.base_url}/policies',
            json=policy_data,
            headers=self.headers
        )
        return response.json()
    
    def submit_emission_data(self, policy_id, block_id, data):
        response = requests.post(
            f'{self.base_url}/policies/{policy_id}/blocks/{block_id}',
            json={'document': data},
            headers=self.headers
        )
        return response.json()
```

### JavaScript Integration
```javascript
class MGSClient {
    constructor(baseUrl, accessToken) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async createPolicy(policyData) {
        const response = await fetch(`${this.baseUrl}/policies`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(policyData)
        });
        return response.json();
    }
    
    async submitEmissionData(policyId, blockId, data) {
        const response = await fetch(
            `${this.baseUrl}/policies/${policyId}/blocks/${blockId}`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({ document: data })
            }
        );
        return response.json();
    }
}
```

## Conclusion

The MGS API provides comprehensive functionality for carbon credit and environmental token management. Start with user authentication, set up your policies and schemas, then integrate data submission workflows. Use dry-run mode extensively during development and implement proper error handling for production deployments.

For detailed schema definitions and response formats, refer to the complete API documentation and OpenAPI specification.