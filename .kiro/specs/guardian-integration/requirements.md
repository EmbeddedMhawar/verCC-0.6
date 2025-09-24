# Requirements Document

## Introduction

This feature integrates the Hedera Guardian platform with the VerifiedCC Python backend to enable automated, Verra-compliant carbon credit verification workflows. The integration will allow ESP32 energy data to be submitted to Guardian using Verra open-source policy templates (VM0042, ARR) for blockchain-based verification and carbon credit generation, creating an end-to-end "Trust as a Service" platform for renewable energy producers in MENA regions.

The system will implement a complete multi-stakeholder workflow supporting Project Proponents (renewable plant operators), Validation/Verification Bodies (VVBs), and Standard Registry roles, with specific compliance for Morocco electrical standards (220V grid) and MENA market requirements.

## Requirements

### Requirement 1

**User Story:** As a renewable energy producer, I want to automatically submit my verified energy production data to Guardian for carbon credit generation, so that I can monetize my green energy production without manual verification processes.

#### Acceptance Criteria

1. WHEN ESP32 energy data is received by the Python backend THEN the system SHALL store the data in Supabase database
2. WHEN sufficient energy data is accumulated (24-hour periods) THEN the system SHALL automatically format and submit the data to Guardian
3. WHEN Guardian receives the energy data THEN it SHALL process it through the configured carbon credit policy
4. IF the Guardian submission is successful THEN the system SHALL store the Guardian document ID and status
5. WHEN Guardian completes verification THEN the system SHALL update the local database with the final carbon credit status

### Requirement 2

**User Story:** As a system administrator, I want to deploy Guardian locally using Docker with Standard Registry setup, so that I can have a complete Verra-compliant carbon credit verification environment for development and testing.

#### Acceptance Criteria

1. WHEN I run the Guardian Docker setup THEN Guardian SHALL start all required services (MongoDB, NATS, Redis, etc.)
2. WHEN Guardian is running THEN it SHALL be accessible at http://localhost:3000 for the web interface
3. WHEN Guardian is running THEN it SHALL provide API access at http://localhost:3000/api-docs
4. WHEN Guardian starts THEN it SHALL connect to Hedera testnet using provided credentials
5. WHEN Guardian is initialized THEN it SHALL allow Standard Registry account registration with organizational profile setup
6. WHEN Standard Registry profile is complete THEN it SHALL initialize core identities (DID, Verifiable Credential)
7. WHEN Verra policy templates are imported THEN the system SHALL support VM0042 and ARR methodologies
8. IF Guardian fails to start THEN the system SHALL provide clear error messages and troubleshooting steps

### Requirement 3

**User Story:** As a developer, I want the Python backend to authenticate with Guardian and communicate through REST APIs, so that energy data can be submitted and carbon credit status can be tracked.

#### Acceptance Criteria

1. WHEN the Python backend starts THEN it SHALL authenticate with Guardian using login credentials
2. WHEN Guardian authentication succeeds THEN the backend SHALL store the bearer token for API requests
3. WHEN Guardian policies are requested THEN the backend SHALL fetch available policies using GET /policies
4. WHEN energy data is submitted to Guardian THEN the backend SHALL use POST /policies/{policyId}/tag/{tagName}/blocks endpoint
5. WHEN Guardian document status is requested THEN the backend SHALL fetch status using GET /policies/{policyId}/documents

### Requirement 4

**User Story:** As a renewable energy producer, I want to view my carbon credit verification status in the dashboard, so that I can track the progress of my submissions and see generated credits.

#### Acceptance Criteria

1. WHEN I access the frontend dashboard THEN it SHALL display Guardian connection status
2. WHEN I view device statistics THEN it SHALL show Guardian submission history for each device
3. WHEN Guardian documents are processing THEN the dashboard SHALL show "Pending Verification" status
4. WHEN Guardian completes verification THEN the dashboard SHALL show "Verified" status with carbon credit details
5. IF Guardian verification fails THEN the dashboard SHALL show error details and retry options

### Requirement 5

**User Story:** As a system operator, I want automated Guardian submissions with Verra-compliant policies and multi-stakeholder workflows, so that different types of renewable energy installations can use appropriate verification workflows with proper role assignments.

#### Acceptance Criteria

1. WHEN the system is configured THEN it SHALL support Guardian user registration with role-based access (Standard Registry, Project Proponent, VVB)
2. WHEN user profiles are created THEN the system SHALL assign appropriate roles (operator, validator, registry) in Guardian's registry role management
3. WHEN VVBs are registered THEN the system SHALL approve stakeholders in Guardian's registry role management view
4. WHEN auto-submission is enabled THEN the system SHALL automatically submit daily energy summaries to Guardian policy blocks using Verra methodology templates
5. WHEN a Guardian policy is selected THEN the system SHALL validate that the policy exists and matches Verra compliance requirements
6. WHEN energy data doesn't meet Verra policy schema requirements THEN the system SHALL log validation errors and retry later
7. WHEN Guardian authentication expires THEN the system SHALL automatically re-authenticate and retry submissions
8. WHEN "Dry Run" mode is enabled THEN the system SHALL test policy workflows before enabling live transactions

### Requirement 6

**User Story:** As a compliance officer, I want immutable audit trails of all Guardian submissions, so that I can provide regulatory proof of carbon credit verification processes.

#### Acceptance Criteria

1. WHEN energy data is submitted to Guardian THEN the system SHALL log the submission with timestamp and data hash
2. WHEN Guardian responds THEN the system SHALL log the response including document ID and initial status
3. WHEN Guardian status changes THEN the system SHALL log all status updates with timestamps
4. WHEN audit reports are requested THEN the system SHALL provide complete submission and verification history
5. WHEN data integrity is questioned THEN the system SHALL provide cryptographic proof of data authenticity

### Requirement 7

**User Story:** As a system administrator, I want to configure Guardian credentials and connection settings, so that the system can connect to different Guardian instances (local, testnet, mainnet).

#### Acceptance Criteria

1. WHEN Guardian is deployed locally THEN the system SHALL connect to http://localhost:3000 by default
2. WHEN Guardian credentials are provided THEN the system SHALL authenticate using POST /accounts/login endpoint
3. WHEN Guardian environment variables are set THEN the system SHALL use custom Guardian URL and credentials
4. WHEN Guardian Docker containers are started THEN the system SHALL wait for Guardian to be ready before attempting connection
5. WHEN Guardian connection fails THEN the system SHALL provide clear error messages and retry logic

### Requirement 8

**User Story:** As a renewable energy producer, I want my ESP32 data to be automatically formatted for Verra-compliant Guardian policy schemas with MENA-specific parameters, so that it meets international carbon credit verification requirements.

#### Acceptance Criteria

1. WHEN ESP32 energy data is received THEN the system SHALL aggregate it into daily reporting periods with Morocco grid standards (220V)
2. WHEN daily data is complete THEN the system SHALL format it according to Verra renewable energy schema (VM0042/ARR)
3. WHEN Guardian policy requires specific MRV fields THEN the system SHALL map ESP32 SCADA data to required Verra methodology fields
4. WHEN regional parameters are needed THEN the system SHALL include MENA-specific details (Morocco voltage, reporting standards)
5. WHEN data validation fails THEN the system SHALL log specific field errors and Verra schema requirements
6. WHEN Guardian schema changes THEN the system SHALL adapt data formatting to new Verra methodology requirements
7. WHEN SCADA data is processed THEN the system SHALL ensure cryptographic hashing and secure TLS transmission for industrial compliance
#
## Requirement 9

**User Story:** As a project proponent, I want to register renewable energy projects in Guardian with proper validation workflows, so that I can progress through Verra-compliant verification steps for carbon credit generation.

#### Acceptance Criteria

1. WHEN using the "New Project" function THEN the system SHALL input SCADA-driven energy and emissions data with regional details
2. WHEN project registration is submitted THEN the system SHALL include Morocco standards and MENA market parameters
3. WHEN validation is required THEN VVBs SHALL review and verify submitted MRV data through Guardian workflows
4. WHEN monitoring reports are created THEN the system SHALL use SCADA-backed, hashed measurement uploads
5. WHEN verification is complete THEN the system SHALL ensure real-time, cryptographically secured, and auditable records
6. WHEN project data is insufficient THEN the system SHALL provide clear guidance on required Verra methodology fields

### Requirement 10

**User Story:** As a Standard Registry operator, I want to mint Verra-compliant carbon credit tokens after verification, so that verified energy output can be converted to tradeable carbon credits with full auditability.

#### Acceptance Criteria

1. WHEN monitoring reports are verified by VVBs THEN the Standard Registry SHALL be able to mint Verra-compliant carbon credit tokens
2. WHEN carbon credits are minted THEN they SHALL be mapped directly to validated energy output from ESP32 SCADA data
3. WHEN tokens are created THEN the system SHALL provide access to TrustChain for transparent auditability
4. WHEN audit trails are requested THEN the system SHALL provide Token History sections for dispute resolution
5. WHEN regulatory reporting is needed THEN the system SHALL make records available to producers, auditors, and buyers
6. WHEN carbon credits are issued THEN the system SHALL maintain immutable blockchain records on Hedera

### Requirement 11

**User Story:** As a compliance officer, I want automated VVB assignment and notification workflows, so that verification processes can scale efficiently across multiple renewable energy projects.

#### Acceptance Criteria

1. WHEN projects require verification THEN the system SHALL automatically assign appropriate VVBs based on project type and region
2. WHEN VVB assignment occurs THEN the system SHALL send notifications to assigned verification bodies
3. WHEN verification workflows are active THEN the system SHALL track progress through multi-stakeholder approval processes
4. WHEN VVB capacity is reached THEN the system SHALL redistribute assignments to available verification bodies
5. WHEN verification is delayed THEN the system SHALL escalate notifications and provide status updates to project proponents
6. WHEN scaling requirements increase THEN the system SHALL support automated assignment processes for platform growth