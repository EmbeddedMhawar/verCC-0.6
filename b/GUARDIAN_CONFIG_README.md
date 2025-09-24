# Guardian Configuration Guide

This guide covers Guardian configuration validation and troubleshooting for the VerifiedCC backend.

## Quick Validation

### Run Configuration Validation

```bash
# Basic validation
python validate_guardian_config.py

# Verbose output with details
python validate_guardian_config.py --verbose

# Attempt to fix common issues
python validate_guardian_config.py --fix-config

# Save results to JSON file
python validate_guardian_config.py --output-json guardian_validation.json
```

### Windows Users

```cmd
# Run validation script
validate_guardian.bat

# Or run directly
python validate_guardian_config.py --verbose
```

## Configuration Requirements

### Critical Environment Variables

These variables are **required** for Guardian integration to work:

```bash
# Guardian API Connection
GUARDIAN_URL=http://localhost:3000
GUARDIAN_USERNAME=your_guardian_username
GUARDIAN_PASSWORD=your_guardian_password
```

### Optional Configuration

```bash
# Guardian API Key (optional for local development)
GUARDIAN_API_KEY=

# Submission Configuration
GUARDIAN_SUBMISSION_ENABLED=true
GUARDIAN_DEFAULT_POLICY_ID=your_policy_id
GUARDIAN_DAILY_SUBMISSION_TIME=01:00
GUARDIAN_MIN_DATA_COMPLETENESS=80.0
GUARDIAN_MAX_CONCURRENT_SUBMISSIONS=5

# Connection Settings
GUARDIAN_CONNECTION_TIMEOUT=30
GUARDIAN_MAX_RETRIES=3
GUARDIAN_RETRY_DELAY=1.0

# Policy Configuration
GUARDIAN_POLICY_SELECTION_MODE=fixed
GUARDIAN_PREFERRED_POLICY_TYPES=VM0042,ARR
GUARDIAN_AUTO_POLICY_SELECTION=true
```

## Validation Checks

The validation system performs the following checks:

### Critical Checks (Must Pass)

1. **Environment Variables**: Required variables are set
2. **Guardian Connection**: API is reachable at configured URL
3. **Guardian Authentication**: Username/password work correctly

### Warning Checks (Should Pass)

1. **Guardian Policies**: Policies are available and configured
2. **Configuration Values**: Settings are within valid ranges

### Info Checks (Informational)

1. **Optional Variables**: Optional settings are documented
2. **Configuration Summary**: Current settings overview

## Common Issues and Solutions

### Issue: "Environment variable GUARDIAN_USERNAME is not set"

**Solution**: Add Guardian credentials to your `.env` file:

```bash
GUARDIAN_USERNAME=your_username
GUARDIAN_PASSWORD=your_password
```

### Issue: "Cannot connect to Guardian API"

**Possible Causes**:
1. Guardian is not running
2. Wrong URL in configuration
3. Network connectivity issues

**Solutions**:

1. **Start Guardian Docker containers**:
   ```bash
   cd guardian
   docker compose -f docker-compose-quickstart.yml up -d
   ```

2. **Check Guardian URL**:
   ```bash
   curl http://localhost:3000
   ```

3. **Verify Guardian is running**:
   ```bash
   docker compose -f docker-compose-quickstart.yml ps
   ```

### Issue: "Guardian authentication failed"

**Possible Causes**:
1. Wrong username/password
2. Guardian user account not created
3. Guardian not fully initialized

**Solutions**:

1. **Create Guardian user account**:
   - Open http://localhost:3000
   - Register as Standard Registry
   - Complete profile setup

2. **Verify credentials**:
   ```bash
   curl -X POST http://localhost:3000/api/v1/accounts/login \
     -H "Content-Type: application/json" \
     -d '{"username":"your_username","password":"your_password"}'
   ```

### Issue: "No Guardian policies found"

**Possible Causes**:
1. No policies imported in Guardian
2. Policies not published
3. Authentication issues

**Solutions**:

1. **Import Verra policy templates**:
   - Login to Guardian web interface
   - Go to Policies section
   - Import VM0042 or ARR policy templates
   - Publish the policies

2. **Check policy status**:
   ```bash
   curl http://localhost:5000/api/guardian/policies
   ```

### Issue: "Invalid data completeness threshold"

**Solution**: Update configuration with valid range (0-100):

```bash
GUARDIAN_MIN_DATA_COMPLETENESS=80.0
```

### Issue: "Invalid max concurrent submissions"

**Solution**: Update configuration with valid range (1-50):

```bash
GUARDIAN_MAX_CONCURRENT_SUBMISSIONS=5
```

## Configuration Validation API

The backend provides API endpoints for configuration validation:

### Check Guardian Configuration

```bash
# Get validation results
curl http://localhost:5000/api/guardian/config/validation

# Get environment configuration (masked)
curl http://localhost:5000/api/guardian/config/environment

# Get configuration summary
curl http://localhost:5000/api/guardian/config/summary
```

### Example Validation Response

```json
{
  "overall_status": "passed",
  "can_start": true,
  "timestamp": "2025-01-XX...",
  "summary": {
    "critical": {"passed": 3, "total": 3},
    "warning": {"passed": 2, "total": 2},
    "info": {"passed": 5, "total": 5}
  },
  "results": [...],
  "recommendations": [
    "✅ All validations passed - Guardian integration is ready"
  ]
}
```

## Troubleshooting Steps

### Step 1: Basic Environment Check

```bash
# Check if .env file exists
ls -la .env

# Validate environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('GUARDIAN_URL:', os.getenv('GUARDIAN_URL'))
print('GUARDIAN_USERNAME:', '***' if os.getenv('GUARDIAN_USERNAME') else 'NOT SET')
print('GUARDIAN_PASSWORD:', '***' if os.getenv('GUARDIAN_PASSWORD') else 'NOT SET')
"
```

### Step 2: Guardian Service Check

```bash
# Check if Guardian is running
curl -f http://localhost:3000 || echo "Guardian not accessible"

# Check Guardian Docker containers
docker compose -f guardian/docker-compose-quickstart.yml ps

# View Guardian logs
docker compose -f guardian/docker-compose-quickstart.yml logs guardian-service
```

### Step 3: Authentication Test

```bash
# Test Guardian login
curl -X POST http://localhost:3000/api/v1/accounts/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}' \
  -v
```

### Step 4: Backend Integration Test

```bash
# Start backend
python main.py

# Check Guardian health endpoint
curl http://localhost:5000/api/guardian/health

# Run full validation
python validate_guardian_config.py --verbose
```

## Configuration Templates

### Minimal Configuration (.env)

```bash
# Required for Guardian integration
GUARDIAN_URL=http://localhost:3000
GUARDIAN_USERNAME=your_username
GUARDIAN_PASSWORD=your_password
GUARDIAN_SUBMISSION_ENABLED=true
```

### Full Configuration (.env)

```bash
# Guardian API Connection
GUARDIAN_URL=http://localhost:3000
GUARDIAN_USERNAME=your_username
GUARDIAN_PASSWORD=your_password
GUARDIAN_API_KEY=

# Submission Settings
GUARDIAN_SUBMISSION_ENABLED=true
GUARDIAN_DEFAULT_POLICY_ID=
GUARDIAN_DAILY_SUBMISSION_TIME=01:00
GUARDIAN_MIN_DATA_COMPLETENESS=80.0
GUARDIAN_MAX_CONCURRENT_SUBMISSIONS=5

# Connection Settings
GUARDIAN_CONNECTION_TIMEOUT=30
GUARDIAN_MAX_RETRIES=3
GUARDIAN_RETRY_DELAY=1.0

# Policy Settings
GUARDIAN_POLICY_SELECTION_MODE=fixed
GUARDIAN_PREFERRED_POLICY_TYPES=VM0042,ARR
GUARDIAN_AUTO_POLICY_SELECTION=true

# Docker Settings (for Guardian setup)
GUARDIAN_OPERATOR_ID=0.0.xxxxx
GUARDIAN_OPERATOR_KEY=302e020100...
GUARDIAN_HEDERA_NET=testnet
```

## Monitoring and Maintenance

### Regular Health Checks

```bash
# Daily validation check
python validate_guardian_config.py --output-json daily_check.json

# Monitor Guardian connection
curl http://localhost:5000/api/guardian/health
```

### Log Monitoring

```bash
# Backend logs
tail -f logs/verifiedcc.log

# Guardian logs
docker compose -f guardian/docker-compose-quickstart.yml logs -f guardian-service
```

### Configuration Updates

When updating Guardian configuration:

1. Update `.env` file
2. Run validation: `python validate_guardian_config.py`
3. Restart backend if needed
4. Test integration: `curl http://localhost:5000/api/guardian/health`

## Support

For additional help:

1. **Check logs**: Backend and Guardian service logs
2. **Run validation**: Use the validation script with `--verbose`
3. **Guardian documentation**: See `GUARDIAN_SETUP.md`
4. **API testing**: Use the Guardian health and config endpoints

## Next Steps

After successful validation:

1. **Test submission**: Submit sample energy data
2. **Configure policies**: Set up renewable energy policies
3. **Monitor operations**: Use dashboard and logs
4. **Scale deployment**: Consider production settings