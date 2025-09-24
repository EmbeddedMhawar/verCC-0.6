#!/usr/bin/env python3
"""
Guardian Configuration Manager
Handles Guardian policy selection, submission timing configuration, and device management.
Requirements: 5.2, 5.4
"""

import os
import json
import logging
from datetime import time, datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from guardian_service import GuardianService, GuardianConfig

logger = logging.getLogger(__name__)

class PolicySelectionMode(Enum):
    """Policy selection modes"""
    FIXED = "fixed"  # Use a single fixed policy
    DEVICE_BASED = "device_based"  # Different policies per device
    ENERGY_BASED = "energy_based"  # Select based on energy production
    AUTO = "auto"  # Automatically select best available policy

@dataclass
class PolicyMapping:
    """Policy mapping configuration"""
    device_id: str
    policy_id: str
    tag_name: str = "renewable_energy"
    priority: int = 0  # Higher number = higher priority

@dataclass
class EnergyThreshold:
    """Energy-based policy selection threshold"""
    min_energy_kwh: float
    max_energy_kwh: Optional[float]
    policy_id: str
    tag_name: str = "renewable_energy"

@dataclass
class GuardianPolicyConfig:
    """Guardian policy configuration"""
    # Policy selection
    selection_mode: PolicySelectionMode = PolicySelectionMode.FIXED
    default_policy_id: Optional[str] = None
    default_tag_name: str = "renewable_energy"
    
    # Device-specific mappings
    device_policies: List[PolicyMapping] = None
    
    # Energy-based thresholds
    energy_thresholds: List[EnergyThreshold] = None
    
    # Auto-selection criteria
    auto_selection_enabled: bool = True
    preferred_policy_types: List[str] = None  # e.g., ["VM0042", "ARR"]
    
    def __post_init__(self):
        if self.device_policies is None:
            self.device_policies = []
        if self.energy_thresholds is None:
            self.energy_thresholds = []
        if self.preferred_policy_types is None:
            self.preferred_policy_types = ["VM0042", "ARR"]

@dataclass
class SubmissionTimingConfig:
    """Submission timing configuration"""
    # Daily scheduling
    daily_enabled: bool = True
    daily_time: time = time(hour=1, minute=0)  # 1:00 AM
    
    # Threshold-based triggering
    threshold_enabled: bool = True
    data_completeness_threshold: float = 80.0  # Trigger when 80% complete
    energy_threshold_kwh: float = 1.0  # Trigger when 1 kWh accumulated
    
    # Real-time triggering
    realtime_enabled: bool = False
    realtime_interval_hours: int = 6  # Check every 6 hours
    
    # Batch processing
    batch_enabled: bool = True
    batch_size: int = 10  # Process up to 10 devices at once
    batch_interval_minutes: int = 30  # Process batches every 30 minutes

@dataclass
class DeviceManagementConfig:
    """Device management configuration"""
    # Device filtering
    enabled_devices: Optional[Set[str]] = None  # None = all devices
    excluded_devices: Optional[Set[str]] = None
    
    # Device grouping
    device_groups: Dict[str, List[str]] = None  # Group name -> device list
    group_policies: Dict[str, str] = None  # Group name -> policy ID
    
    # Device priorities
    device_priorities: Dict[str, int] = None  # Device ID -> priority
    
    def __post_init__(self):
        if self.device_groups is None:
            self.device_groups = {}
        if self.group_policies is None:
            self.group_policies = {}
        if self.device_priorities is None:
            self.device_priorities = {}

class GuardianConfigManager:
    """
    Manages Guardian configuration including policy selection and submission timing
    Requirements: 5.2, 5.4
    """
    
    def __init__(self, 
                 guardian_service: GuardianService = None,
                 config_dir: str = None):
        """Initialize the configuration manager"""
        self.guardian_service = guardian_service or GuardianService()
        self.config_dir = Path(config_dir or os.path.join(os.getcwd(), "config"))
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.policy_config_file = self.config_dir / "guardian_policies.json"
        self.timing_config_file = self.config_dir / "submission_timing.json"
        self.device_config_file = self.config_dir / "device_management.json"
        
        # Load configurations
        self.policy_config = self._load_policy_config()
        self.timing_config = self._load_timing_config()
        self.device_config = self._load_device_config()
        
        # Cache for policy information
        self._policy_cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_minutes = 30
        
        logger.info("🔧 GuardianConfigManager initialized")
    
    def get_policy_for_device(self, device_id: str, energy_kwh: float = None) -> Dict[str, str]:
        """
        Get the appropriate Guardian policy for a device
        Requirement 5.2: Create configuration for Guardian policy selection
        """
        try:
            if self.policy_config.selection_mode == PolicySelectionMode.FIXED:
                return self._get_fixed_policy()
            
            elif self.policy_config.selection_mode == PolicySelectionMode.DEVICE_BASED:
                return self._get_device_based_policy(device_id)
            
            elif self.policy_config.selection_mode == PolicySelectionMode.ENERGY_BASED:
                return self._get_energy_based_policy(energy_kwh or 0)
            
            elif self.policy_config.selection_mode == PolicySelectionMode.AUTO:
                return self._get_auto_selected_policy(device_id, energy_kwh)
            
            else:
                logger.warning(f"⚠️ Unknown policy selection mode: {self.policy_config.selection_mode}")
                return self._get_fixed_policy()
                
        except Exception as e:
            logger.error(f"❌ Error getting policy for device {device_id}: {e}")
            return self._get_fixed_policy()
    
    def should_submit_now(self, device_id: str, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine if a submission should be triggered now based on timing configuration
        Requirement 5.4: Create configuration for submission timing
        """
        reasons = []
        should_submit = False
        
        try:
            # Check daily schedule
            if self.timing_config.daily_enabled:
                now = datetime.now().time()
                daily_time = self.timing_config.daily_time
                
                # Check if we're within 30 minutes of daily submission time
                time_diff = abs((now.hour * 60 + now.minute) - (daily_time.hour * 60 + daily_time.minute))
                if time_diff <= 30:  # Within 30 minutes
                    should_submit = True
                    reasons.append(f"Daily schedule: {daily_time}")
            
            # Check threshold-based triggers
            if self.timing_config.threshold_enabled:
                data_completeness = current_data.get("data_completeness_percent", 0)
                energy_kwh = current_data.get("total_energy_kwh", 0)
                
                if data_completeness >= self.timing_config.data_completeness_threshold:
                    should_submit = True
                    reasons.append(f"Data completeness: {data_completeness:.1f}% >= {self.timing_config.data_completeness_threshold}%")
                
                if energy_kwh >= self.timing_config.energy_threshold_kwh:
                    should_submit = True
                    reasons.append(f"Energy threshold: {energy_kwh:.2f} kWh >= {self.timing_config.energy_threshold_kwh} kWh")
            
            # Check real-time triggers
            if self.timing_config.realtime_enabled:
                last_submission = current_data.get("last_submission_time")
                if last_submission:
                    hours_since = (datetime.now() - datetime.fromisoformat(last_submission)).total_seconds() / 3600
                    if hours_since >= self.timing_config.realtime_interval_hours:
                        should_submit = True
                        reasons.append(f"Real-time interval: {hours_since:.1f}h >= {self.timing_config.realtime_interval_hours}h")
                else:
                    # No previous submission, trigger if enabled
                    should_submit = True
                    reasons.append("First submission (real-time enabled)")
            
            return {
                "should_submit": should_submit,
                "reasons": reasons,
                "timing_config": {
                    "daily_enabled": self.timing_config.daily_enabled,
                    "threshold_enabled": self.timing_config.threshold_enabled,
                    "realtime_enabled": self.timing_config.realtime_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking submission timing for {device_id}: {e}")
            return {
                "should_submit": False,
                "reasons": [],
                "error": str(e)
            }
    
    def get_device_priority(self, device_id: str) -> int:
        """Get priority for a device (higher number = higher priority)"""
        # Check device-specific priority
        if device_id in self.device_config.device_priorities:
            return self.device_config.device_priorities[device_id]
        
        # Check group-based priority
        for group_name, devices in self.device_config.device_groups.items():
            if device_id in devices:
                # Use group name hash as priority (consistent but arbitrary)
                return hash(group_name) % 100
        
        # Default priority
        return 0
    
    def is_device_enabled(self, device_id: str) -> bool:
        """Check if device is enabled for Guardian submissions"""
        # Check exclusion list first
        if self.device_config.excluded_devices and device_id in self.device_config.excluded_devices:
            return False
        
        # Check inclusion list (if specified)
        if self.device_config.enabled_devices:
            return device_id in self.device_config.enabled_devices
        
        # Default: all devices enabled
        return True
    
    def get_batch_config(self) -> Dict[str, Any]:
        """Get batch processing configuration"""
        return {
            "enabled": self.timing_config.batch_enabled,
            "batch_size": self.timing_config.batch_size,
            "interval_minutes": self.timing_config.batch_interval_minutes
        }
    
    def update_policy_config(self, **kwargs) -> bool:
        """Update policy configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.policy_config, key):
                    setattr(self.policy_config, key, value)
                else:
                    logger.warning(f"⚠️ Unknown policy config key: {key}")
            
            self._save_policy_config()
            logger.info("✅ Policy configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating policy config: {e}")
            return False
    
    def update_timing_config(self, **kwargs) -> bool:
        """Update timing configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.timing_config, key):
                    # Handle time object conversion
                    if key == "daily_time" and isinstance(value, str):
                        hour, minute = map(int, value.split(":"))
                        value = time(hour=hour, minute=minute)
                    
                    setattr(self.timing_config, key, value)
                else:
                    logger.warning(f"⚠️ Unknown timing config key: {key}")
            
            self._save_timing_config()
            logger.info("✅ Timing configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating timing config: {e}")
            return False
    
    def add_device_policy_mapping(self, device_id: str, policy_id: str, tag_name: str = "renewable_energy", priority: int = 0) -> bool:
        """Add device-specific policy mapping"""
        try:
            # Remove existing mapping for device
            self.policy_config.device_policies = [
                p for p in self.policy_config.device_policies 
                if p.device_id != device_id
            ]
            
            # Add new mapping
            mapping = PolicyMapping(
                device_id=device_id,
                policy_id=policy_id,
                tag_name=tag_name,
                priority=priority
            )
            
            self.policy_config.device_policies.append(mapping)
            self._save_policy_config()
            
            logger.info(f"✅ Added policy mapping: {device_id} -> {policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding device policy mapping: {e}")
            return False
    
    def get_available_policies(self, refresh_cache: bool = False) -> List[Dict[str, Any]]:
        """Get available Guardian policies with caching"""
        try:
            # Check cache validity
            if (not refresh_cache and 
                self._policy_cache and 
                self._cache_timestamp and
                (datetime.now() - self._cache_timestamp).total_seconds() < self._cache_ttl_minutes * 60):
                return self._policy_cache.get("policies", [])
            
            # Fetch from Guardian
            policies = self.guardian_service.get_policies()
            
            # Update cache
            self._policy_cache = {"policies": policies}
            self._cache_timestamp = datetime.now()
            
            logger.info(f"📋 Retrieved {len(policies)} Guardian policies")
            return policies
            
        except Exception as e:
            logger.error(f"❌ Error getting available policies: {e}")
            return []
    
    def validate_policy_exists(self, policy_id: str) -> bool:
        """Validate that a policy exists in Guardian"""
        try:
            policies = self.get_available_policies()
            return any(p.get("id") == policy_id for p in policies)
        except Exception as e:
            logger.error(f"❌ Error validating policy {policy_id}: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of all configurations"""
        return {
            "policy_config": {
                "selection_mode": self.policy_config.selection_mode.value,
                "default_policy_id": self.policy_config.default_policy_id,
                "device_mappings_count": len(self.policy_config.device_policies),
                "energy_thresholds_count": len(self.policy_config.energy_thresholds),
                "auto_selection_enabled": self.policy_config.auto_selection_enabled
            },
            "timing_config": {
                "daily_enabled": self.timing_config.daily_enabled,
                "daily_time": self.timing_config.daily_time.isoformat(),
                "threshold_enabled": self.timing_config.threshold_enabled,
                "realtime_enabled": self.timing_config.realtime_enabled,
                "batch_enabled": self.timing_config.batch_enabled
            },
            "device_config": {
                "enabled_devices_count": len(self.device_config.enabled_devices) if self.device_config.enabled_devices else "all",
                "excluded_devices_count": len(self.device_config.excluded_devices) if self.device_config.excluded_devices else 0,
                "device_groups_count": len(self.device_config.device_groups),
                "device_priorities_count": len(self.device_config.device_priorities)
            }
        }
    
    # Private helper methods
    
    def _get_fixed_policy(self) -> Dict[str, str]:
        """Get fixed policy configuration"""
        return {
            "policy_id": self.policy_config.default_policy_id,
            "tag_name": self.policy_config.default_tag_name,
            "selection_reason": "Fixed policy configuration"
        }
    
    def _get_device_based_policy(self, device_id: str) -> Dict[str, str]:
        """Get device-specific policy"""
        # Find device mapping
        for mapping in self.policy_config.device_policies:
            if mapping.device_id == device_id:
                return {
                    "policy_id": mapping.policy_id,
                    "tag_name": mapping.tag_name,
                    "selection_reason": f"Device-specific mapping (priority: {mapping.priority})"
                }
        
        # Check device groups
        for group_name, devices in self.device_config.device_groups.items():
            if device_id in devices and group_name in self.device_config.group_policies:
                return {
                    "policy_id": self.device_config.group_policies[group_name],
                    "tag_name": self.policy_config.default_tag_name,
                    "selection_reason": f"Device group mapping: {group_name}"
                }
        
        # Fall back to default
        return self._get_fixed_policy()
    
    def _get_energy_based_policy(self, energy_kwh: float) -> Dict[str, str]:
        """Get policy based on energy production"""
        # Sort thresholds by min_energy_kwh
        sorted_thresholds = sorted(self.policy_config.energy_thresholds, key=lambda x: x.min_energy_kwh)
        
        for threshold in sorted_thresholds:
            if (energy_kwh >= threshold.min_energy_kwh and 
                (threshold.max_energy_kwh is None or energy_kwh < threshold.max_energy_kwh)):
                return {
                    "policy_id": threshold.policy_id,
                    "tag_name": threshold.tag_name,
                    "selection_reason": f"Energy threshold: {threshold.min_energy_kwh}-{threshold.max_energy_kwh} kWh"
                }
        
        # Fall back to default
        return self._get_fixed_policy()
    
    def _get_auto_selected_policy(self, device_id: str, energy_kwh: Optional[float]) -> Dict[str, str]:
        """Automatically select best policy"""
        try:
            # Get available policies
            policies = self.get_available_policies()
            
            if not policies:
                return self._get_fixed_policy()
            
            # Filter by preferred types
            preferred_policies = []
            for policy in policies:
                policy_name = policy.get("name", "").upper()
                for preferred_type in self.policy_config.preferred_policy_types:
                    if preferred_type.upper() in policy_name:
                        preferred_policies.append(policy)
                        break
            
            # Use preferred policies if available, otherwise all policies
            candidate_policies = preferred_policies if preferred_policies else policies
            
            # Filter by status (only use published policies)
            active_policies = [p for p in candidate_policies if p.get("status") == "PUBLISH"]
            
            if not active_policies:
                return self._get_fixed_policy()
            
            # Select first active policy (could be enhanced with more sophisticated logic)
            selected_policy = active_policies[0]
            
            return {
                "policy_id": selected_policy.get("id"),
                "tag_name": self.policy_config.default_tag_name,
                "selection_reason": f"Auto-selected: {selected_policy.get('name', 'Unknown')} (status: {selected_policy.get('status')})"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in auto policy selection: {e}")
            return self._get_fixed_policy()
    
    def _load_policy_config(self) -> GuardianPolicyConfig:
        """Load policy configuration from file"""
        try:
            if self.policy_config_file.exists():
                with open(self.policy_config_file, 'r') as f:
                    data = json.load(f)
                
                # Convert data to config object
                config = GuardianPolicyConfig()
                
                if "selection_mode" in data:
                    config.selection_mode = PolicySelectionMode(data["selection_mode"])
                
                config.default_policy_id = data.get("default_policy_id")
                config.default_tag_name = data.get("default_tag_name", "renewable_energy")
                config.auto_selection_enabled = data.get("auto_selection_enabled", True)
                config.preferred_policy_types = data.get("preferred_policy_types", ["VM0042", "ARR"])
                
                # Load device policies
                if "device_policies" in data:
                    config.device_policies = [
                        PolicyMapping(**mapping) for mapping in data["device_policies"]
                    ]
                
                # Load energy thresholds
                if "energy_thresholds" in data:
                    config.energy_thresholds = [
                        EnergyThreshold(**threshold) for threshold in data["energy_thresholds"]
                    ]
                
                logger.info("✅ Loaded policy configuration from file")
                return config
            
        except Exception as e:
            logger.error(f"❌ Error loading policy config: {e}")
        
        # Return default config
        return GuardianPolicyConfig()
    
    def _save_policy_config(self):
        """Save policy configuration to file"""
        try:
            data = {
                "selection_mode": self.policy_config.selection_mode.value,
                "default_policy_id": self.policy_config.default_policy_id,
                "default_tag_name": self.policy_config.default_tag_name,
                "auto_selection_enabled": self.policy_config.auto_selection_enabled,
                "preferred_policy_types": self.policy_config.preferred_policy_types,
                "device_policies": [asdict(mapping) for mapping in self.policy_config.device_policies],
                "energy_thresholds": [asdict(threshold) for threshold in self.policy_config.energy_thresholds]
            }
            
            with open(self.policy_config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving policy config: {e}")
    
    def _load_timing_config(self) -> SubmissionTimingConfig:
        """Load timing configuration from file"""
        try:
            if self.timing_config_file.exists():
                with open(self.timing_config_file, 'r') as f:
                    data = json.load(f)
                
                config = SubmissionTimingConfig()
                
                config.daily_enabled = data.get("daily_enabled", True)
                
                if "daily_time" in data:
                    time_str = data["daily_time"]
                    hour, minute = map(int, time_str.split(":"))
                    config.daily_time = time(hour=hour, minute=minute)
                
                config.threshold_enabled = data.get("threshold_enabled", True)
                config.data_completeness_threshold = data.get("data_completeness_threshold", 80.0)
                config.energy_threshold_kwh = data.get("energy_threshold_kwh", 1.0)
                
                config.realtime_enabled = data.get("realtime_enabled", False)
                config.realtime_interval_hours = data.get("realtime_interval_hours", 6)
                
                config.batch_enabled = data.get("batch_enabled", True)
                config.batch_size = data.get("batch_size", 10)
                config.batch_interval_minutes = data.get("batch_interval_minutes", 30)
                
                logger.info("✅ Loaded timing configuration from file")
                return config
            
        except Exception as e:
            logger.error(f"❌ Error loading timing config: {e}")
        
        return SubmissionTimingConfig()
    
    def _save_timing_config(self):
        """Save timing configuration to file"""
        try:
            data = {
                "daily_enabled": self.timing_config.daily_enabled,
                "daily_time": self.timing_config.daily_time.isoformat(),
                "threshold_enabled": self.timing_config.threshold_enabled,
                "data_completeness_threshold": self.timing_config.data_completeness_threshold,
                "energy_threshold_kwh": self.timing_config.energy_threshold_kwh,
                "realtime_enabled": self.timing_config.realtime_enabled,
                "realtime_interval_hours": self.timing_config.realtime_interval_hours,
                "batch_enabled": self.timing_config.batch_enabled,
                "batch_size": self.timing_config.batch_size,
                "batch_interval_minutes": self.timing_config.batch_interval_minutes
            }
            
            with open(self.timing_config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving timing config: {e}")
    
    def _load_device_config(self) -> DeviceManagementConfig:
        """Load device configuration from file"""
        try:
            if self.device_config_file.exists():
                with open(self.device_config_file, 'r') as f:
                    data = json.load(f)
                
                config = DeviceManagementConfig()
                
                if "enabled_devices" in data:
                    config.enabled_devices = set(data["enabled_devices"])
                
                if "excluded_devices" in data:
                    config.excluded_devices = set(data["excluded_devices"])
                
                config.device_groups = data.get("device_groups", {})
                config.group_policies = data.get("group_policies", {})
                config.device_priorities = data.get("device_priorities", {})
                
                logger.info("✅ Loaded device configuration from file")
                return config
            
        except Exception as e:
            logger.error(f"❌ Error loading device config: {e}")
        
        return DeviceManagementConfig()
    
    def _save_device_config(self):
        """Save device configuration to file"""
        try:
            data = {
                "enabled_devices": list(self.device_config.enabled_devices) if self.device_config.enabled_devices else None,
                "excluded_devices": list(self.device_config.excluded_devices) if self.device_config.excluded_devices else None,
                "device_groups": self.device_config.device_groups,
                "group_policies": self.device_config.group_policies,
                "device_priorities": self.device_config.device_priorities
            }
            
            with open(self.device_config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving device config: {e}")

# Example usage and testing
if __name__ == "__main__":
    from guardian_service import GuardianService, GuardianConfig
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize Guardian service
    guardian_config = GuardianConfig(
        base_url=os.getenv("GUARDIAN_URL", "http://localhost:3000"),
        username=os.getenv("GUARDIAN_USERNAME"),
        password=os.getenv("GUARDIAN_PASSWORD")
    )
    guardian_service = GuardianService(guardian_config)
    
    # Create config manager
    config_manager = GuardianConfigManager(guardian_service)
    
    print("🔍 Testing GuardianConfigManager...")
    
    # Test policy selection
    policy_info = config_manager.get_policy_for_device("ESP32_001", energy_kwh=5.0)
    print(f"📋 Policy for ESP32_001: {policy_info}")
    
    # Test timing check
    timing_info = config_manager.should_submit_now("ESP32_001", {
        "data_completeness_percent": 85.0,
        "total_energy_kwh": 2.5
    })
    print(f"⏰ Timing check: {timing_info}")
    
    # Test configuration summary
    summary = config_manager.get_config_summary()
    print(f"📊 Config summary: {summary}")
    
    print("✅ GuardianConfigManager test complete")