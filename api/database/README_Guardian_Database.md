# Guardian Verifiable Credentials Database System

A comprehensive database system for storing and managing Guardian API verifiable credentials for renewable energy projects and carbon credit tracking.

## Overview

This system extends your existing energy monitoring database with full support for Guardian verifiable credentials, including:

- Complete credential storage with normalized relational structure
- Project participant profiles and metadata
- Crediting and monitoring periods tracking
- Electricity system information and power units
- Emissions data and calculations
- Geographic location indexing
- RESTful API endpoints for credential management

## Database Schema

### Core Tables

1. **verifiable_credentials** - Main credential metadata
2. **project_participants** - Project details and participant profiles
3. **crediting_periods** - Carbon credit periods
4. **monitoring_periods** - Monitoring and reporting periods
5. **electricity_systems** - Power system information
6. **power_units** - Individual power generation units
7. **emissions_data** - Emission factors and calculations

### Key Features

- **JSONB Support**: Raw credential storage for complete data preservation
- **Geographic Indexing**: Efficient location-based queries
- **Relational Normalization**: Structured data for complex queries
- **Automatic Functions**: Built-in insertion and retrieval functions
- **Performance Optimized**: Comprehensive indexing strategy

## Setup Instructions

### 1. Database Schema Setup

Run the SQL schema in your Supabase project:

```bash
# Copy the contents of guardian_credentials_schema.sql
# Paste into Supabase SQL Editor and execute
```

### 2. Python Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables in .env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
```

### 3. Initialize and Test

```bash
# Run the setup script
python database/setup_guardian_db.py

# Test the system
python database/guardian_credentials_manager.py
```

## Usage Examples

### Python API

```python
from guardian_credentials_manager import GuardianCredentialsManager

# Initialize manager
manager = GuardianCredentialsManager()

# Store a credential
credential_uuid = manager.insert_credential(your_credential_json)

# Retrieve credential
credential = manager.get_credential_by_id("urn:uuid:your-credential-id")

# Search credentials
results = manager.search_credentials(
    organization_name="Green Energy",
    project_type="Wind",
    country="Morocco"
)

# Get location-based results
nearby = manager.get_credentials_by_location(
    lat_min=30.0, lat_max=35.0,
    lon_min=-10.0, lon_max=-5.0
)

# Get summary statistics
summary = manager.get_emission_reductions_summary()
```

### REST API

Start the API server:

```bash
python database/guardian_api_endpoint.py
```

#### API Endpoints

**Store Credential**

```bash
POST /api/credentials
Content-Type: application/json

{
  "id": "urn:uuid:project-participant-uuid",
  "type": ["VerifiableCredential"],
  "issuer": "did:hedera:testnet:issuer-id",
  # ... complete credential JSON
}
```

**List Credentials**

```bash
GET /api/credentials?limit=10&organization=Green%20Energy&project_type=Wind
```

**Get Specific Credential**

```bash
GET /api/credentials/urn:uuid:project-participant-uuid
```

**Search by Location**

```bash
GET /api/credentials/location?lat_min=30&lat_max=35&lon_min=-10&lon_max=-5
```

**Get Summary Statistics**

```bash
GET /api/summary
```

**Health Check**

```bash
GET /health
```

## Data Structure Support

The system fully supports the Guardian credential structure you provided:

```json
{
  "id": "urn:uuid:project-participant-uuid",
  "type": ["VerifiableCredential"],
  "issuer": "did:hedera:testnet:issuer-id",
  "issuanceDate": "2025-09-29T10:57:00.000Z",
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "credentialSubject": [
    {
      "participant_profile": {
        "summaryDescription": "Renewable power plant for grid decarbonization",
        "sectoralScope": "Energy",
        "projectType": "Wind",
        "locationLatitude": 33.5731,
        "locationLongitude": -7.5898,
        "organizationName": "Green Energy Morocco Ltd",
        "emissionReductions": 10000,
        "creditingPeriods": [{ "start": "2025-01-01", "end": "2030-12-31" }],
        "tool_07": {
          "electricitySystemInfo": "National interconnected system",
          "buildMargin": {
            "powerUnits": [{ "type": "Wind", "capacity": 70 }]
          }
        }
        // ... all other fields supported
      }
    }
  ],
  "proof": {
    "type": "Ed25519Signature2018",
    "verificationMethod": "did:hedera:testnet:issuer-id#did-root-key"
  }
}
```

## Key Features

### 1. Complete Data Preservation

- Raw JSON storage in `raw_credential` field
- Normalized relational structure for queries
- No data loss during storage

### 2. Advanced Querying

- Search by organization, project type, country
- Geographic bounding box queries
- Date range filtering on periods
- Emission reduction aggregations

### 3. Performance Optimized

- Strategic indexing on frequently queried fields
- Materialized views for complex aggregations
- Efficient JSON operations

### 4. Integration Ready

- RESTful API with CORS support
- Python SDK for direct integration
- Compatible with existing energy monitoring system

### 5. Validation & Error Handling

- Credential structure validation
- Comprehensive error handling
- Detailed logging and monitoring

## Database Functions

### insert_guardian_credential(credential_json)

Inserts a complete credential with all related data in a single transaction.

### get_credential_details(credential_id)

Retrieves complete credential data with all related tables joined.

## Views

### credential_summary

Provides a flattened view of credentials with key participant information for efficient listing and searching.

## Monitoring & Maintenance

### Performance Monitoring

```sql
-- Check credential counts
SELECT COUNT(*) FROM verifiable_credentials;

-- Monitor emission reductions
SELECT
  SUM(emission_reductions) as total_reductions,
  COUNT(*) as project_count,
  project_type
FROM project_participants
GROUP BY project_type;

-- Geographic distribution
SELECT
  country,
  COUNT(*) as project_count,
  AVG(emission_reductions) as avg_reductions
FROM project_participants
GROUP BY country;
```

### Maintenance Tasks

```sql
-- Refresh materialized views (if any)
REFRESH MATERIALIZED VIEW hourly_energy_summary;

-- Update statistics
ANALYZE verifiable_credentials;
ANALYZE project_participants;
```

## Security Considerations

- Row Level Security (RLS) ready
- Environment variable configuration
- Input validation and sanitization
- SQL injection protection via parameterized queries

## Integration with Existing System

This Guardian credentials system integrates seamlessly with your existing energy monitoring database:

1. **Shared Infrastructure**: Uses same Supabase instance
2. **Complementary Data**: Links energy readings with credential projects
3. **Unified API**: Can be combined with existing FastAPI endpoints
4. **Common Patterns**: Follows same database design principles

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check SUPABASE_URL and SUPABASE_ANON_KEY in .env
2. **Schema Errors**: Ensure guardian_credentials_schema.sql was executed
3. **Permission Errors**: Verify Supabase project permissions
4. **JSON Validation**: Check credential structure matches expected format

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Real-time credential verification
- Blockchain integration for proof validation
- Advanced analytics and reporting
- Multi-tenant support
- Automated compliance checking

## Support

For issues or questions:

1. Check the logs for detailed error messages
2. Verify database schema is properly installed
3. Test with the provided sample credentials
4. Review API endpoint responses for error details
