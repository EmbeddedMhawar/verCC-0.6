# Requirements Document

## Introduction

This feature transforms the current system from Guardian-based blockchain verification to a streamlined real-time data pipeline. ESP32 devices will send energy production data directly to Supabase, which will then provide real-time updates to a modern React dashboard. This eliminates blockchain complexity while maintaining data integrity and providing immediate visibility into energy production metrics.

## Requirements

### Requirement 1

**User Story:** As an energy facility operator, I want ESP32 sensors to send data directly to Supabase in real-time, so that I can monitor energy production without blockchain delays or complexity.

#### Acceptance Criteria

1. WHEN ESP32 collects sensor data THEN the system SHALL transmit data to Supabase within 5 seconds
2. WHEN data is transmitted THEN Supabase SHALL store the data with timestamp and device identification
3. WHEN network connectivity is lost THEN ESP32 SHALL buffer data locally and retry transmission
4. IF transmission fails THEN ESP32 SHALL implement exponential backoff retry logic

### Requirement 2

**User Story:** As a facility manager, I want a real-time dashboard that shows current energy production, so that I can monitor system performance instantly.

#### Acceptance Criteria

1. WHEN new data arrives in Supabase THEN the dashboard SHALL update within 2 seconds
2. WHEN displaying data THEN the dashboard SHALL show current power output, total energy produced, and device status
3. WHEN data is older than 30 seconds THEN the dashboard SHALL indicate potential connectivity issues
4. IF no data is received for 5 minutes THEN the dashboard SHALL display an alert

### Requirement 3

**User Story:** As a system administrator, I want to view historical energy data and trends, so that I can analyze performance patterns and identify issues.

#### Acceptance Criteria

1. WHEN accessing historical data THEN the dashboard SHALL display data for selectable time ranges (hour, day, week, month)
2. WHEN viewing trends THEN the system SHALL provide interactive charts with zoom and pan capabilities
3. WHEN analyzing data THEN the dashboard SHALL calculate and display average power, peak power, and total energy metrics
4. IF data gaps exist THEN the dashboard SHALL clearly indicate missing data periods

### Requirement 4

**User Story:** As a maintenance technician, I want to see device health and connectivity status, so that I can proactively address hardware issues.

#### Acceptance Criteria

1. WHEN ESP32 devices are online THEN the dashboard SHALL show green status indicators
2. WHEN devices haven't reported for over 5 minutes THEN the dashboard SHALL show red status indicators
3. WHEN viewing device details THEN the dashboard SHALL display last seen time, signal strength, and error counts
4. IF device errors exceed threshold THEN the system SHALL generate maintenance alerts

### Requirement 5

**User Story:** As a developer, I want the ESP32 firmware to be configurable via web interface, so that I can adjust settings without reflashing firmware.

#### Acceptance Criteria

1. WHEN accessing ESP32 web interface THEN the system SHALL provide configuration forms for WiFi, Supabase credentials, and sampling rates
2. WHEN configuration is updated THEN ESP32 SHALL apply changes without requiring restart
3. WHEN invalid configuration is provided THEN the system SHALL validate inputs and show error messages
4. IF configuration fails THEN ESP32 SHALL revert to previous working configuration

### Requirement 6

**User Story:** As a data analyst, I want to export energy production data, so that I can perform detailed analysis in external tools.

#### Acceptance Criteria

1. WHEN requesting data export THEN the dashboard SHALL provide CSV and JSON format options
2. WHEN exporting data THEN the system SHALL include all relevant fields (timestamp, power, energy, device_id, status)
3. WHEN large datasets are requested THEN the system SHALL implement pagination or streaming export
4. IF export fails THEN the system SHALL provide clear error messages and retry options