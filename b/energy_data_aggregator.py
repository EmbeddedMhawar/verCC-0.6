#!/usr/bin/env python3
"""
Energy Data Aggregator for Guardian Submission
Handles daily ESP32 sensor data processing and Guardian-compatible report generation
"""

import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class EnergyMetrics:
    """Energy production metrics for a specific period"""
    total_energy_kwh: float
    avg_power_w: float
    max_power_w: float
    min_power_w: float
    peak_to_avg_ratio: float
    capacity_factor: float
    
@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    avg_efficiency: float
    max_efficiency: float
    min_efficiency: float
    avg_power_factor: float
    avg_grid_frequency: float
    
@dataclass
class EnvironmentalMetrics:
    """Environmental condition metrics"""
    avg_irradiance_w_m2: float
    max_irradiance_w_m2: float
    avg_temperature_c: float
    max_temperature_c: float
    min_temperature_c: float
    
@dataclass
class DataQualityMetrics:
    """Data quality and validation metrics"""
    total_readings: int
    valid_readings: int
    missing_readings: int
    data_completeness_percent: float
    outlier_count: int
    measurement_period_hours: float
    
@dataclass
class AggregatedEnergyReport:
    """Comprehensive energy report for Guardian submission"""
    device_id: str
    period_start: datetime
    period_end: datetime
    
    # Energy metrics
    energy_metrics: EnergyMetrics
    
    # Performance metrics
    performance_metrics: PerformanceMetrics
    
    # Environmental metrics
    environmental_metrics: EnvironmentalMetrics
    
    # Data quality
    data_quality: DataQualityMetrics
    
    # Verification and integrity
    verification_hash: str
    data_integrity_score: float
    
    # MENA compliance (Morocco standards)
    grid_voltage_nominal: float = 220.0
    grid_frequency_nominal: float = 50.0
    regional_compliance: Dict[str, Any] = None

class EnergyDataAggregator:
    """
    Aggregates ESP32 sensor readings from Supabase for Guardian submission
    Implements requirements 1.2, 8.1, 8.2
    """
    
    def __init__(self, supabase_client: Client = None):
        """Initialize the aggregator with Supabase client"""
        if supabase_client:
            self.supabase = supabase_client
        else:
            # Initialize Supabase client if not provided
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
            
            self.supabase = create_client(supabase_url, supabase_key)
        
        logger.info("🔧 EnergyDataAggregator initialized")
    
    def aggregate_daily_data(self, device_id: str, target_date: datetime = None) -> AggregatedEnergyReport:
        """
        Aggregate 24-hour ESP32 sensor readings for a specific device and date
        Requirement 1.2: Aggregate 24-hour ESP32 sensor readings from Supabase
        """
        if not device_id or not device_id.strip():
            raise ValueError("Device ID is required for data aggregation")
        
        # Use current date if not specified
        if target_date is None:
            target_date = datetime.now()
        
        # Calculate 24-hour period (start of day to end of day)
        period_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)
        
        logger.info(f"📊 Aggregating daily data for device {device_id} from {period_start} to {period_end}")
        
        # Fetch sensor readings from Supabase
        raw_data = self._fetch_sensor_readings(device_id, period_start, period_end)
        
        if not raw_data:
            raise ValueError(f"No sensor data found for device {device_id} on {target_date.date()}")
        
        # Process and validate data
        validated_data = self._validate_and_clean_data(raw_data)
        
        # Calculate energy metrics
        energy_metrics = self._calculate_energy_metrics(validated_data)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(validated_data)
        
        # Calculate environmental metrics
        environmental_metrics = self._calculate_environmental_metrics(validated_data)
        
        # Calculate data quality metrics
        data_quality = self._calculate_data_quality_metrics(raw_data, validated_data, period_start, period_end)
        
        # Generate verification hash
        verification_hash = self._generate_verification_hash(device_id, validated_data, energy_metrics)
        
        # Calculate data integrity score
        data_integrity_score = self._calculate_data_integrity_score(data_quality, validated_data)
        
        # MENA compliance parameters (Morocco standards)
        regional_compliance = {
            "country": "Morocco",
            "grid_standard": "220V_50Hz",
            "voltage_tolerance": "±10%",
            "frequency_tolerance": "±2%",
            "measurement_standard": "IEC_61724",
            "reporting_timezone": "Africa/Casablanca"
        }
        
        report = AggregatedEnergyReport(
            device_id=device_id,
            period_start=period_start,
            period_end=period_end,
            energy_metrics=energy_metrics,
            performance_metrics=performance_metrics,
            environmental_metrics=environmental_metrics,
            data_quality=data_quality,
            verification_hash=verification_hash,
            data_integrity_score=data_integrity_score,
            grid_voltage_nominal=220.0,  # Morocco standard
            grid_frequency_nominal=50.0,  # Morocco standard
            regional_compliance=regional_compliance
        )
        
        logger.info(f"✅ Daily aggregation complete for {device_id}: {energy_metrics.total_energy_kwh:.2f} kWh, {data_quality.total_readings} readings")
        
        return report
    
    def _validate_and_clean_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean sensor data, removing outliers and invalid readings
        Requirement 8.2: Create data quality validation and verification hash generation
        """
        if not raw_data:
            return []
        
        validated_data = []
        outlier_count = 0
        
        for reading in raw_data:
            # Basic validation checks
            is_valid = True
            
            # Check for required fields
            if not reading.get('power') or reading.get('power') < 0:
                is_valid = False
            
            # Check for reasonable voltage range (Morocco: 220V ±10%)
            voltage = reading.get('voltage', 220.0)
            if voltage < 198 or voltage > 242:  # 220V ±10%
                is_valid = False
            
            # Check for reasonable frequency range (Morocco: 50Hz ±2%)
            frequency = reading.get('grid_frequency_hz', 50.0)
            if frequency < 49 or frequency > 51:  # 50Hz ±2%
                is_valid = False
            
            # Check for reasonable power factor (0.0 to 1.0)
            power_factor = reading.get('power_factor', 0.95)
            if power_factor < 0.0 or power_factor > 1.0:
                is_valid = False
            
            # Check for reasonable efficiency (0.0 to 1.0)
            efficiency = reading.get('efficiency', 0.96)
            if efficiency < 0.0 or efficiency > 1.0:
                is_valid = False
            
            # Check for reasonable temperature range (-10°C to 60°C)
            temp = reading.get('ambient_temp_c', 25.0)
            if temp < -10 or temp > 60:
                is_valid = False
            
            # Check for reasonable irradiance (0 to 1500 W/m²)
            irradiance = reading.get('irradiance_w_m2', 0.0)
            if irradiance < 0 or irradiance > 1500:
                is_valid = False
            
            if is_valid:
                validated_data.append(reading)
            else:
                outlier_count += 1
        
        logger.info(f"🔍 Data validation complete: {len(validated_data)} valid readings, {outlier_count} outliers removed")
        
        return validated_data
    
    def _calculate_energy_metrics(self, data: List[Dict[str, Any]]) -> EnergyMetrics:
        """
        Calculate energy production metrics from validated sensor data
        Requirement 1.2: Implement energy metrics calculation (total kWh, average power, efficiency)
        """
        if not data:
            return EnergyMetrics(0, 0, 0, 0, 0, 0)
        
        # Extract power values (in Watts)
        powers = [reading.get('power', 0) for reading in data]
        powers = [p for p in powers if p > 0]  # Filter out zero/negative values
        
        if not powers:
            return EnergyMetrics(0, 0, 0, 0, 0, 0)
        
        # Calculate basic power statistics
        avg_power_w = sum(powers) / len(powers)
        max_power_w = max(powers)
        min_power_w = min(powers)
        
        # Calculate total energy (kWh) from cumulative energy readings
        energy_readings = [reading.get('total_energy_kwh', 0) for reading in data]
        energy_readings = [e for e in energy_readings if e > 0]
        
        if energy_readings:
            # Use the difference between max and min cumulative energy
            total_energy_kwh = max(energy_readings) - min(energy_readings)
        else:
            # Estimate from average power and time period
            time_hours = len(data) / 60  # Assuming 1-minute intervals
            total_energy_kwh = (avg_power_w * time_hours) / 1000
        
        # Calculate peak-to-average ratio
        peak_to_avg_ratio = max_power_w / avg_power_w if avg_power_w > 0 else 0
        
        # Calculate capacity factor (assuming rated capacity from max observed power)
        # For solar systems, capacity factor = actual energy / (rated capacity × time)
        rated_capacity_kw = max_power_w / 1000  # Assume max observed is rated capacity
        time_hours = len(data) / 60  # Assuming 1-minute intervals
        theoretical_max_energy = rated_capacity_kw * time_hours
        capacity_factor = total_energy_kwh / theoretical_max_energy if theoretical_max_energy > 0 else 0
        
        return EnergyMetrics(
            total_energy_kwh=total_energy_kwh,
            avg_power_w=avg_power_w,
            max_power_w=max_power_w,
            min_power_w=min_power_w,
            peak_to_avg_ratio=peak_to_avg_ratio,
            capacity_factor=min(capacity_factor, 1.0)  # Cap at 100%
        )
    
    def _calculate_performance_metrics(self, data: List[Dict[str, Any]]) -> PerformanceMetrics:
        """Calculate system performance metrics from validated sensor data"""
        if not data:
            return PerformanceMetrics(0, 0, 0, 0, 0)
        
        # Extract efficiency values
        efficiencies = [reading.get('efficiency', 0.96) for reading in data]
        efficiencies = [e for e in efficiencies if 0 <= e <= 1]
        
        # Extract power factor values
        power_factors = [reading.get('power_factor', 0.95) for reading in data]
        power_factors = [pf for pf in power_factors if 0 <= pf <= 1]
        
        # Extract grid frequency values
        frequencies = [reading.get('grid_frequency_hz', 50.0) for reading in data]
        frequencies = [f for f in frequencies if 45 <= f <= 55]  # Reasonable range
        
        return PerformanceMetrics(
            avg_efficiency=sum(efficiencies) / len(efficiencies) if efficiencies else 0.96,
            max_efficiency=max(efficiencies) if efficiencies else 0.96,
            min_efficiency=min(efficiencies) if efficiencies else 0.96,
            avg_power_factor=sum(power_factors) / len(power_factors) if power_factors else 0.95,
            avg_grid_frequency=sum(frequencies) / len(frequencies) if frequencies else 50.0
        )
    
    def _calculate_environmental_metrics(self, data: List[Dict[str, Any]]) -> EnvironmentalMetrics:
        """Calculate environmental condition metrics from validated sensor data"""
        if not data:
            return EnvironmentalMetrics(0, 0, 0, 0, 0)
        
        # Extract irradiance values
        irradiances = [reading.get('irradiance_w_m2', 0) for reading in data]
        irradiances = [i for i in irradiances if 0 <= i <= 1500]
        
        # Extract temperature values
        temperatures = [reading.get('ambient_temp_c', 25.0) for reading in data]
        temperatures = [t for t in temperatures if -10 <= t <= 60]
        
        return EnvironmentalMetrics(
            avg_irradiance_w_m2=sum(irradiances) / len(irradiances) if irradiances else 0,
            max_irradiance_w_m2=max(irradiances) if irradiances else 0,
            avg_temperature_c=sum(temperatures) / len(temperatures) if temperatures else 25.0,
            max_temperature_c=max(temperatures) if temperatures else 25.0,
            min_temperature_c=min(temperatures) if temperatures else 25.0
        )
    
    def _calculate_data_quality_metrics(self, raw_data: List[Dict[str, Any]], 
                                      validated_data: List[Dict[str, Any]], 
                                      period_start: datetime, 
                                      period_end: datetime) -> DataQualityMetrics:
        """
        Calculate data quality and completeness metrics
        Requirement 8.2: Create data quality validation and verification hash generation
        """
        total_readings = len(raw_data)
        valid_readings = len(validated_data)
        missing_readings = total_readings - valid_readings
        
        # Calculate data completeness percentage
        period_hours = (period_end - period_start).total_seconds() / 3600
        expected_readings = period_hours * 60  # Assuming 1-minute intervals
        data_completeness_percent = (total_readings / expected_readings * 100) if expected_readings > 0 else 0
        data_completeness_percent = min(data_completeness_percent, 100.0)  # Cap at 100%
        
        # Count outliers
        outlier_count = total_readings - valid_readings
        
        return DataQualityMetrics(
            total_readings=total_readings,
            valid_readings=valid_readings,
            missing_readings=missing_readings,
            data_completeness_percent=data_completeness_percent,
            outlier_count=outlier_count,
            measurement_period_hours=period_hours
        )
    
    def _generate_verification_hash(self, device_id: str, 
                                  validated_data: List[Dict[str, Any]], 
                                  energy_metrics: EnergyMetrics) -> str:
        """
        Generate cryptographic verification hash for data integrity
        Requirement 8.2: Create data quality validation and verification hash generation
        """
        # Create hash input from key data points
        hash_components = [
            device_id,
            str(len(validated_data)),
            f"{energy_metrics.total_energy_kwh:.6f}",
            f"{energy_metrics.avg_power_w:.2f}",
            f"{energy_metrics.max_power_w:.2f}",
        ]
        
        # Add timestamps from first and last readings
        if validated_data:
            hash_components.extend([
                validated_data[0].get('timestamp', ''),
                validated_data[-1].get('timestamp', '')
            ])
        
        # Add sample of power readings for additional verification
        power_samples = []
        if validated_data:
            step = max(1, len(validated_data) // 10)  # Sample every 10th reading
            for i in range(0, len(validated_data), step):
                power_samples.append(str(validated_data[i].get('power', 0)))
        
        hash_components.extend(power_samples)
        
        # Create SHA-256 hash
        hash_input = "|".join(hash_components)
        verification_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        
        logger.debug(f"🔐 Generated verification hash for {device_id}: {verification_hash[:16]}...")
        
        return verification_hash
    
    def _calculate_data_integrity_score(self, data_quality: DataQualityMetrics, 
                                      validated_data: List[Dict[str, Any]]) -> float:
        """
        Calculate overall data integrity score (0.0 to 1.0)
        Higher score indicates better data quality and reliability
        """
        if not validated_data or data_quality.total_readings == 0:
            return 0.0
        
        # Component scores (each 0.0 to 1.0)
        
        # 1. Data completeness score (40% weight)
        completeness_score = min(data_quality.data_completeness_percent / 100.0, 1.0)
        
        # 2. Data validity score (30% weight)
        validity_score = data_quality.valid_readings / data_quality.total_readings
        
        # 3. Measurement consistency score (20% weight)
        # Check for consistent measurement intervals
        timestamps = [reading.get('timestamp') for reading in validated_data if reading.get('timestamp')]
        consistency_score = 1.0  # Default to perfect if we can't calculate
        
        if len(timestamps) > 1:
            try:
                # Convert timestamps and calculate intervals
                dt_timestamps = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
                intervals = [(dt_timestamps[i+1] - dt_timestamps[i]).total_seconds() 
                           for i in range(len(dt_timestamps)-1)]
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    # Calculate coefficient of variation for intervals
                    interval_variance = sum((interval - avg_interval) ** 2 for interval in intervals) / len(intervals)
                    interval_std = interval_variance ** 0.5
                    cv = interval_std / avg_interval if avg_interval > 0 else 1.0
                    
                    # Lower coefficient of variation = higher consistency score
                    consistency_score = max(0.0, 1.0 - cv)
            except Exception:
                consistency_score = 0.8  # Moderate score if calculation fails
        
        # 4. Value reasonableness score (10% weight)
        # Check if values are within expected ranges
        reasonable_count = 0
        total_checks = 0
        
        for reading in validated_data:
            # Check power values (should be reasonable for solar)
            power = reading.get('power', 0)
            if 0 <= power <= 50000:  # 0 to 50kW reasonable for small solar
                reasonable_count += 1
            total_checks += 1
            
            # Check efficiency values
            efficiency = reading.get('efficiency', 0.96)
            if 0.1 <= efficiency <= 0.99:  # 10% to 99% efficiency
                reasonable_count += 1
            total_checks += 1
        
        reasonableness_score = reasonable_count / total_checks if total_checks > 0 else 1.0
        
        # Calculate weighted overall score
        integrity_score = (
            completeness_score * 0.4 +
            validity_score * 0.3 +
            consistency_score * 0.2 +
            reasonableness_score * 0.1
        )
        
        return min(max(integrity_score, 0.0), 1.0)  # Ensure 0.0 to 1.0 range
    
    def _fetch_sensor_readings(self, device_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Fetch sensor readings from Supabase for the specified period"""
        try:
            result = self.supabase.table("sensor_readings")\
                .select("*")\
                .eq("device_id", device_id)\
                .gte("timestamp", start_time.isoformat())\
                .lt("timestamp", end_time.isoformat())\
                .order("timestamp", desc=False)\
                .execute()
            
            if result.data:
                logger.info(f"📡 Fetched {len(result.data)} sensor readings for device {device_id}")
                return result.data
            else:
                logger.warning(f"⚠️ No sensor readings found for device {device_id} in period {start_time} to {end_time}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch sensor readings: {e}")
            raise RuntimeError(f"Database query failed: {e}")
    
    def aggregate_period_data(self, device_id: str, period_start: datetime, period_end: datetime) -> AggregatedEnergyReport:
        """
        Aggregate ESP32 sensor readings for a custom time period
        Requirement 8.1: Aggregate ESP32 energy data into daily reporting periods
        """
        if not device_id or not device_id.strip():
            raise ValueError("Device ID is required for data aggregation")
        
        if period_end <= period_start:
            raise ValueError("Period end must be after period start")
        
        logger.info(f"📊 Aggregating period data for device {device_id} from {period_start} to {period_end}")
        
        # Fetch sensor readings from Supabase
        raw_data = self._fetch_sensor_readings(device_id, period_start, period_end)
        
        if not raw_data:
            raise ValueError(f"No sensor data found for device {device_id} in period {period_start} to {period_end}")
        
        # Process and validate data
        validated_data = self._validate_and_clean_data(raw_data)
        
        # Calculate all metrics
        energy_metrics = self._calculate_energy_metrics(validated_data)
        performance_metrics = self._calculate_performance_metrics(validated_data)
        environmental_metrics = self._calculate_environmental_metrics(validated_data)
        data_quality = self._calculate_data_quality_metrics(raw_data, validated_data, period_start, period_end)
        
        # Generate verification hash and integrity score
        verification_hash = self._generate_verification_hash(device_id, validated_data, energy_metrics)
        data_integrity_score = self._calculate_data_integrity_score(data_quality, validated_data)
        
        # MENA compliance parameters
        regional_compliance = {
            "country": "Morocco",
            "grid_standard": "220V_50Hz",
            "voltage_tolerance": "±10%",
            "frequency_tolerance": "±2%",
            "measurement_standard": "IEC_61724",
            "reporting_timezone": "Africa/Casablanca"
        }
        
        report = AggregatedEnergyReport(
            device_id=device_id,
            period_start=period_start,
            period_end=period_end,
            energy_metrics=energy_metrics,
            performance_metrics=performance_metrics,
            environmental_metrics=environmental_metrics,
            data_quality=data_quality,
            verification_hash=verification_hash,
            data_integrity_score=data_integrity_score,
            grid_voltage_nominal=220.0,
            grid_frequency_nominal=50.0,
            regional_compliance=regional_compliance
        )
        
        logger.info(f"✅ Period aggregation complete for {device_id}: {energy_metrics.total_energy_kwh:.2f} kWh, {data_quality.total_readings} readings")
        
        return report
    
    def get_device_summary(self, device_id: str, days: int = 7) -> Dict[str, Any]:
        """Get summary statistics for a device over the last N days"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Fetch recent data
            result = self.supabase.table("sensor_readings")\
                .select("*")\
                .eq("device_id", device_id)\
                .gte("timestamp", start_time.isoformat())\
                .order("timestamp", desc=False)\
                .execute()
            
            if not result.data:
                return {
                    "device_id": device_id,
                    "period_days": days,
                    "total_readings": 0,
                    "message": "No data available"
                }
            
            # Calculate summary metrics
            data = result.data
            powers = [r.get('power', 0) for r in data if r.get('power', 0) > 0]
            energies = [r.get('total_energy_kwh', 0) for r in data if r.get('total_energy_kwh', 0) > 0]
            
            summary = {
                "device_id": device_id,
                "period_days": days,
                "period_start": start_time.isoformat(),
                "period_end": end_time.isoformat(),
                "total_readings": len(data),
                "avg_power_w": sum(powers) / len(powers) if powers else 0,
                "max_power_w": max(powers) if powers else 0,
                "total_energy_kwh": max(energies) - min(energies) if len(energies) > 1 else 0,
                "data_availability_percent": (len(data) / (days * 24 * 60)) * 100,  # Assuming 1-min intervals
                "last_reading": data[-1].get('timestamp') if data else None
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get device summary for {device_id}: {e}")
            return {
                "device_id": device_id,
                "error": str(e),
                "message": "Failed to retrieve device summary"
            }
    
    def validate_guardian_readiness(self, device_id: str, target_date: datetime = None) -> Dict[str, Any]:
        """
        Validate if device data is ready for Guardian submission
        Checks data completeness, quality, and compliance requirements
        """
        try:
            # Generate aggregated report
            report = self.aggregate_daily_data(device_id, target_date)
            
            # Define minimum requirements for Guardian submission
            min_data_completeness = 80.0  # 80% data completeness required
            min_integrity_score = 0.7     # 70% data integrity required
            min_readings = 100            # Minimum 100 readings per day
            min_energy = 0.1              # Minimum 0.1 kWh energy production
            
            # Check requirements
            checks = {
                "data_completeness": {
                    "value": report.data_quality.data_completeness_percent,
                    "threshold": min_data_completeness,
                    "passed": report.data_quality.data_completeness_percent >= min_data_completeness
                },
                "data_integrity": {
                    "value": report.data_integrity_score,
                    "threshold": min_integrity_score,
                    "passed": report.data_integrity_score >= min_integrity_score
                },
                "sufficient_readings": {
                    "value": report.data_quality.valid_readings,
                    "threshold": min_readings,
                    "passed": report.data_quality.valid_readings >= min_readings
                },
                "energy_production": {
                    "value": report.energy_metrics.total_energy_kwh,
                    "threshold": min_energy,
                    "passed": report.energy_metrics.total_energy_kwh >= min_energy
                }
            }
            
            # Overall readiness
            all_passed = all(check["passed"] for check in checks.values())
            
            return {
                "device_id": device_id,
                "period": f"{report.period_start.date()} to {report.period_end.date()}",
                "guardian_ready": all_passed,
                "checks": checks,
                "summary": {
                    "total_energy_kwh": report.energy_metrics.total_energy_kwh,
                    "data_integrity_score": report.data_integrity_score,
                    "verification_hash": report.verification_hash
                },
                "report": report
            }
            
        except Exception as e:
            logger.error(f"❌ Guardian readiness validation failed for {device_id}: {e}")
            return {
                "device_id": device_id,
                "guardian_ready": False,
                "error": str(e),
                "message": "Failed to validate Guardian readiness"
            }

# Example usage and testing
if __name__ == "__main__":
    # Test the aggregator
    try:
        aggregator = EnergyDataAggregator()
        
        # Test device summary
        print("🔍 Testing EnergyDataAggregator...")
        
        # Get a sample device (you'll need to replace with actual device ID)
        test_device_id = "ESP32_001"
        
        # Get device summary
        summary = aggregator.get_device_summary(test_device_id, days=1)
        print(f"📊 Device summary: {summary}")
        
        if summary.get("total_readings", 0) > 0:
            # Test daily aggregation
            report = aggregator.aggregate_daily_data(test_device_id)
            print(f"✅ Daily aggregation successful:")
            print(f"   Energy: {report.energy_metrics.total_energy_kwh:.2f} kWh")
            print(f"   Avg Power: {report.energy_metrics.avg_power_w:.1f} W")
            print(f"   Data Quality: {report.data_integrity_score:.2f}")
            print(f"   Verification Hash: {report.verification_hash[:16]}...")
            
            # Test Guardian readiness
            readiness = aggregator.validate_guardian_readiness(test_device_id)
            print(f"🔍 Guardian readiness: {readiness['guardian_ready']}")
            
        else:
            print("⚠️ No test data available. Add some sensor readings first.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")