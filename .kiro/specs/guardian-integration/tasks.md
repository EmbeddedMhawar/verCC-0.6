# Implementation Plan

- [x] 1. Set up Guardian Docker environment with testnet configuration

  - Configure Guardian Docker Compose with Hedera testnet credentials
  - Create .env file with HEDERA_NET=testnet and test account credentials
  - Start Guardian services and verify web interface accessibility at localhost:3000
  - Test Guardian API endpoints using Swagger UI at localhost:3000/api-docs
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 7.1, 7.4_

- [x] 2. Implement Guardian authentication service

  - Create GuardianAuth class with login/logout functionality using /accounts/login endpoint
  - Implement bearer token storage and automatic refresh logic
  - Add token validation and expiration handling
  - Write unit tests for authentication flows with mock Guardian responses
  - _Requirements: 3.1, 3.2, 5.5, 7.2_

- [x] 3. Update Guardian service with proper API endpoints

  - Modify existing guardian_service.py to use correct Guardian API endpoints
  - Replace placeholder endpoints with actual Guardian REST API paths
  - Implement GET /policies endpoint for policy discovery
  - Add proper error handling for Guardian API responses
  - _Requirements: 3.3, 3.4, 5.3_

- [x] 4. Create Guardian policy manager component

  - Implement GuardianPolicyManager class for policy discovery and validation
  - Add policy schema fetching and caching functionality
  - Create data validation methods for Guardian policy requirements
  - Write tests for policy schema validation with sample Guardian policies
  - _Requirements: 5.1, 5.2, 8.3, 8.4_

- [x] 5. Implement energy data aggregation for Guardian submission

  - Create EnergyDataAggregator class for daily data processing
  - Add methods to aggregate 24-hour ESP32 sensor readings from Supabase
  - Implement energy metrics calculation (total kWh, average power, efficiency)
  - Create data quality validation and verification hash generation
  - _Requirements: 1.2, 8.1, 8.2_

-

- [x] 6. Create Guardian document submission service

  - Implement GuardianDocumentSubmitter class using POST /policies/{policyId}/tag/{tagName}/blocks
  - Add document status tracking using GET /policies/{policyId}/documents
  - Create submission retry logic with exponential backoff
  - Implement error handling for Guardian API failures
  - _Requirements: 1.3, 1.4, 3.5, 5.4_

- [x] 7. Add Guardian submissions database table

  - Create guardian_submissions table with submission tracking fields
  - Add indexes for device_id, policy_id, and status queries
  - Implement database models for GuardianSubmission records
  - Create migration script for existing database schema
  - _Requirements: 1.5, 6.1, 6.2, 6.3_

- [x] 8. Integrate Guardian endpoints into FastAPI backend

  - Add Guardian health check endpoint GET /api/guardian/health
  - Implement Guardian policies endpoint GET /api/guardian/policies
  - Create Guardian submission endpoint POST /api/guardian/submit
  - Add Guardian document status endpoint GET /api/guardian/documents/{id}/status
  - _Requirements: 3.1, 3.3, 3.4, 3.5_

- [x] 9. Implement automated Guardian submission workflow

  - Create background task for daily energy data aggregation
  - Add automatic Guardian submission for completed daily periods
  - Implement submission queue and retry mechanism for failed submissions
  - Create configuration for Guardian policy selection and submission timing
  - _Requirements: 1.1, 1.2, 5.2, 5.4_

- [x] 10. Add Guardian integration to frontend dashboard

  - Update dashboard to display Guardian connection status
  - Add Guardian submission history view for each device
  - Implement carbon credit verification status display
  - Create Guardian policy selection interface for manual submissions
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 11. Create Guardian configuration and environment setup


  - Add Guardian configuration to .env.example with testnet settings
  - Create Guardian setup documentation with Docker installation steps
  - Implement Guardian connection validation on backend startup
  - Add Guardian configuration validation and error reporting
  - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [-] 12. Implement comprehensive error handling and logging







  - Add detailed logging for all Guardian API interactions
  - Implement retry logic for Guardian connection failures
  - Create error recovery mechanisms for authentication failures
  - Add Guardian API rate limiting and request throttling
  - _Requirements: 5.5, 6.4, 7.5_

- [x] 13. Write integration tests for Guardian workflow






  - Create tests for complete ESP32 → Guardian → Hedera pipeline
  - Test Guardian authentication and policy discovery
  - Validate energy data submission and status tracking
  - Test error handling and retry mechanisms with Guardian API
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
-

- [x] 14. Create Guardian deployment and testing documentation





  - Write step-by-step Guardian Docker setup guide
  - Document Guardian policy configuration for renewable energy
  - Create troubleshooting guide for common Guardian integration issues
  - Add Guardian API testing examples and validation procedures
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [-] 15. Implement Guardian data format validation and transformation







  - Create data transformation functions for Guardian renewable energy schema
  - Add validation for required Guardian policy fields
  - Implement schema adaptation for different Guardian policy types
  - Create data mapping documentation for ESP32 to Guardian field conversion
  - _Requirements: 8.1, 8.2, 8.3, 8.5_
