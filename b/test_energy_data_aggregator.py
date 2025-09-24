#!/usr/bin/env python3
"""
Test suite for EnergyDataAggregator
Tests data aggregation, validation, and Guardian submission readiness
"""

import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from energy_data_aggregator import (
    EnergyDataAggregator, 
    EnergyMetrics, 
    PerformanceMetrics,
    EnvironmentalMetrics,
    DataQualityMetrics,
    AggregatedEnergyReport
)

class TestEnergyDataAggregator:
    """Test cases for EnergyDataAggregator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Mock Supabase client
        self.mock_supabase = Mock()
        self.aggregator = EnergyDataAggregator(supabase_client=self.mock_supabase)
        
        # Sample sensor data for testing
        self.sample_data = [
            {
                "id": 1,
                "device_id": "ESP32_TEST",
                "timestamp": "2025-01-20T10:00:00Z",
                "power": 1000.0,
                "voltage": 220.0,
                "current": 4.55,
                "ac_power_kw": 1.0,
                "total_energy_kwh": 10.0,
                "grid_frequency_hz": 50.0,
                "power_factor": 0.95,
                "efficiency": 0.96,
                "ambient_temp_c": 25.0,
                "irradiance_w_m2": 800.0,
                "system_status": 1
            },
            {
                "id": 2,
                "device_id": "ESP32_TEST",
                "timestamp": "2025-01-20T10:01:00Z",
                "power": 1200.0,
                "voltage": 220.0,
                "current": 5.45,
                "ac_power_kw": 1.2,
                "total_energy_kwh": 10.02,
                "grid_frequency_hz": 50.0,
                "power_factor": 0.95,
                "efficiency": 0.96,
                "ambient_temp_c": 26.0,
                "irradiance_w_m2": 850.0,
                "system_status": 1
            },
            {
                "id": 3,
                "device_id": "ESP32_TEST",
                "timestamp": "2025-01-20T10:02:00Z",
                "power": 800.0,
                "voltage": 220.0,
                "current": 3.64,
                "ac_power_kw": 0.8,
                "total_energy_kwh": 10.04,
                "grid_frequency_hz": 50.0,
                "power_factor": 0.95,
                "efficiency": 0.96,
                "ambient_temp_c": 24.0,
                "irradiance_w_m2": 750.0,
                "system_status": 1
            }
        ]
    
    def test_initialization_with_mock_client(self):
        """Test aggregator initialization with provided Supabase client"""
        aggregator = EnergyDataAggregator(supabase_client=self.mock_supabase)
        assert aggregator.supabase == self.mock_supabase
    
    @patch.dict(os.environ, {'SUPABASE_URL': 'test_url', 'SUPABASE_KEY': 'test_key'})
    @patch('energy_data_aggregator.create_client')
    def test_initialization_with_env_vars(self, mock_create_client):
        """Test aggregator initialization with environment variables"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        aggregator = EnergyDataAggregator()
        
        mock_create_client.assert_called_once_with('test_url', 'test_key')
        assert aggregator.supabase == mock_client
    
    def test_initialization_without_env_vars(self):
        """Test aggregator initialization fails without environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="SUPABASE_URL and SUPABASE_KEY environment variables are required"):
                EnergyDataAggregator()
    
    def test_validate_and_clean_data(self):
        """Test data validation and cleaning"""
        # Add some invalid data
        invalid_data = self.sample_data + [
            {
                "device_id": "ESP32_TEST",
                "timestamp": "2025-01-20T10:03:00Z",
                "power": -100.0,  # Invalid negative power
                "voltage": 300.0,  # Invalid voltage (outside ±10% of 220V)
                "grid_frequency_hz": 60.0,  # Invalid frequency for Morocco
                "efficiency": 1.5,  # Invalid efficiency > 1.0
                "ambient_temp_c": 70.0,  # Invalid temperature
                "irradiance_w_m2": 2000.0  # Invalid irradiance
            }
        ]
        
        validated_data = self.aggregator._validate_and_clean_data(invalid_data)
        
        # Should filter out the invalid reading
        assert len(validated_data) == 3
        assert all(reading.get('power', 0) >= 0 for reading in validated_data)
    
    def test_calculate_energy_metrics(self):
        """Test energy metrics calculation"""
        metrics = self.aggregator._calculate_energy_metrics(self.sample_data)
        
        assert isinstance(metrics, EnergyMetrics)
        assert metrics.avg_power_w == 1000.0  # (1000 + 1200 + 800) / 3
        assert metrics.max_power_w == 1200.0
        assert metrics.min_power_w == 800.0
        assert abs(metrics.total_energy_kwh - 0.04) < 0.001  # 10.04 - 10.0 (with floating point tolerance)
        assert metrics.peak_to_avg_ratio == 1.2  # 1200 / 1000
    
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation"""
        metrics = self.aggregator._calculate_performance_metrics(self.sample_data)
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.avg_efficiency == 0.96
        assert metrics.max_efficiency == 0.96
        assert metrics.min_efficiency == 0.96
        assert metrics.avg_power_factor == 0.95
        assert metrics.avg_grid_frequency == 50.0
    
    def test_calculate_environmental_metrics(self):
        """Test environmental metrics calculation"""
        metrics = self.aggregator._calculate_environmental_metrics(self.sample_data)
        
        assert isinstance(metrics, EnvironmentalMetrics)
        assert metrics.avg_irradiance_w_m2 == 800.0  # (800 + 850 + 750) / 3
        assert metrics.max_irradiance_w_m2 == 850.0
        assert metrics.avg_temperature_c == 25.0  # (25 + 26 + 24) / 3
        assert metrics.max_temperature_c == 26.0
        assert metrics.min_temperature_c == 24.0
    
    def test_calculate_data_quality_metrics(self):
        """Test data quality metrics calculation"""
        period_start = datetime(2025, 1, 20, 10, 0, 0)
        period_end = datetime(2025, 1, 20, 10, 3, 0)  # 3 minutes
        
        metrics = self.aggregator._calculate_data_quality_metrics(
            self.sample_data, self.sample_data, period_start, period_end
        )
        
        assert isinstance(metrics, DataQualityMetrics)
        assert metrics.total_readings == 3
        assert metrics.valid_readings == 3
        assert metrics.missing_readings == 0
        assert metrics.outlier_count == 0
        assert metrics.measurement_period_hours == 0.05  # 3 minutes = 0.05 hours
    
    def test_generate_verification_hash(self):
        """Test verification hash generation"""
        energy_metrics = EnergyMetrics(
            total_energy_kwh=0.04,
            avg_power_w=1000.0,
            max_power_w=1200.0,
            min_power_w=800.0,
            peak_to_avg_ratio=1.2,
            capacity_factor=0.8
        )
        
        hash1 = self.aggregator._generate_verification_hash("ESP32_TEST", self.sample_data, energy_metrics)
        hash2 = self.aggregator._generate_verification_hash("ESP32_TEST", self.sample_data, energy_metrics)
        
        # Same input should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64-character hex string
        
        # Different device ID should produce different hash
        hash3 = self.aggregator._generate_verification_hash("ESP32_OTHER", self.sample_data, energy_metrics)
        assert hash1 != hash3
    
    def test_calculate_data_integrity_score(self):
        """Test data integrity score calculation"""
        data_quality = DataQualityMetrics(
            total_readings=3,
            valid_readings=3,
            missing_readings=0,
            data_completeness_percent=100.0,
            outlier_count=0,
            measurement_period_hours=0.05
        )
        
        score = self.aggregator._calculate_data_integrity_score(data_quality, self.sample_data)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Should be high for good quality data
    
    def test_fetch_sensor_readings(self):
        """Test sensor readings fetch from Supabase"""
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = self.sample_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
        
        start_time = datetime(2025, 1, 20, 10, 0, 0)
        end_time = datetime(2025, 1, 20, 11, 0, 0)
        
        result = self.aggregator._fetch_sensor_readings("ESP32_TEST", start_time, end_time)
        
        assert result == self.sample_data
        assert len(result) == 3
    
    def test_aggregate_daily_data(self):
        """Test daily data aggregation"""
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = self.sample_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
        
        target_date = datetime(2025, 1, 20)
        report = self.aggregator.aggregate_daily_data("ESP32_TEST", target_date)
        
        assert isinstance(report, AggregatedEnergyReport)
        assert report.device_id == "ESP32_TEST"
        assert report.period_start.date() == target_date.date()
        assert report.energy_metrics.total_energy_kwh == 0.04
        assert report.data_quality.total_readings == 3
        assert len(report.verification_hash) == 64
        assert 0.0 <= report.data_integrity_score <= 1.0
    
    def test_aggregate_period_data(self):
        """Test custom period data aggregation"""
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = self.sample_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
        
        start_time = datetime(2025, 1, 20, 10, 0, 0)
        end_time = datetime(2025, 1, 20, 11, 0, 0)
        
        report = self.aggregator.aggregate_period_data("ESP32_TEST", start_time, end_time)
        
        assert isinstance(report, AggregatedEnergyReport)
        assert report.device_id == "ESP32_TEST"
        assert report.period_start == start_time
        assert report.period_end == end_time
        assert report.regional_compliance["country"] == "Morocco"
    
    def test_validate_guardian_readiness(self):
        """Test Guardian submission readiness validation"""
        # Mock Supabase response with sufficient data
        mock_result = Mock()
        # Create more data points to meet minimum requirements
        extended_data = []
        for i in range(150):  # 150 readings to exceed minimum
            reading = self.sample_data[0].copy()
            reading["id"] = i + 1
            reading["timestamp"] = f"2025-01-20T{10 + i//60:02d}:{i%60:02d}:00Z"
            reading["total_energy_kwh"] = 10.0 + (i * 0.01)  # Increasing energy
            extended_data.append(reading)
        
        mock_result.data = extended_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
        
        readiness = self.aggregator.validate_guardian_readiness("ESP32_TEST")
        
        assert "guardian_ready" in readiness
        assert "checks" in readiness
        assert "data_completeness" in readiness["checks"]
        assert "data_integrity" in readiness["checks"]
        assert "sufficient_readings" in readiness["checks"]
        assert "energy_production" in readiness["checks"]
    
    def test_get_device_summary(self):
        """Test device summary generation"""
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = self.sample_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
        
        summary = self.aggregator.get_device_summary("ESP32_TEST", days=1)
        
        assert summary["device_id"] == "ESP32_TEST"
        assert summary["total_readings"] == 3
        assert summary["avg_power_w"] == 1000.0
        assert summary["max_power_w"] == 1200.0
        assert "data_availability_percent" in summary
    
    def test_error_handling_no_data(self):
        """Test error handling when no data is available"""
        # Mock empty Supabase response
        mock_result = Mock()
        mock_result.data = []
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lt.return_value.order.return_value.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="No sensor data found"):
            self.aggregator.aggregate_daily_data("ESP32_NONEXISTENT")
    
    def test_error_handling_invalid_device_id(self):
        """Test error handling for invalid device ID"""
        with pytest.raises(ValueError, match="Device ID is required"):
            self.aggregator.aggregate_daily_data("")
        
        with pytest.raises(ValueError, match="Device ID is required"):
            self.aggregator.aggregate_daily_data(None)
    
    def test_error_handling_invalid_period(self):
        """Test error handling for invalid time period"""
        start_time = datetime(2025, 1, 20, 11, 0, 0)
        end_time = datetime(2025, 1, 20, 10, 0, 0)  # End before start
        
        with pytest.raises(ValueError, match="Period end must be after period start"):
            self.aggregator.aggregate_period_data("ESP32_TEST", start_time, end_time)

# Integration test (requires actual Supabase connection)
def test_integration_with_real_data():
    """
    Integration test with real Supabase connection
    This test is skipped unless INTEGRATION_TEST environment variable is set
    """
    if not os.getenv("INTEGRATION_TEST"):
        pytest.skip("Integration test skipped - set INTEGRATION_TEST=1 to run")
    
    try:
        aggregator = EnergyDataAggregator()
        
        # Test with a real device (replace with actual device ID)
        test_device = os.getenv("TEST_DEVICE_ID", "ESP32_001")
        
        summary = aggregator.get_device_summary(test_device, days=1)
        assert "device_id" in summary
        
        if summary.get("total_readings", 0) > 0:
            report = aggregator.aggregate_daily_data(test_device)
            assert isinstance(report, AggregatedEnergyReport)
            assert report.device_id == test_device
            
    except Exception as e:
        pytest.fail(f"Integration test failed: {e}")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])