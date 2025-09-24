#!/usr/bin/env python3
"""
Guardian Logging Configuration
Centralized logging configuration for all Guardian integration components
"""

import os
import sys
import logging
import logging.config
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def setup_guardian_logging(
    log_level: str = None,
    log_dir: str = None,
    enable_json_logging: bool = None,
    enable_file_logging: bool = None,
    max_log_size_mb: int = 10,
    backup_count: int = 5
) -> Dict[str, Any]:
    """
    Setup comprehensive logging configuration for Guardian integration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_json_logging: Enable structured JSON logging
        enable_file_logging: Enable file logging
        max_log_size_mb: Maximum size of log files in MB
        backup_count: Number of backup log files to keep
    
    Returns:
        Dictionary with logging configuration details
    """
    
    # Get configuration from environment variables with defaults
    log_level = log_level or os.getenv("GUARDIAN_LOG_LEVEL", "INFO")
    log_dir = log_dir or os.getenv("GUARDIAN_LOG_DIR", os.path.join(os.getcwd(), "logs"))
    enable_json_logging = enable_json_logging if enable_json_logging is not None else os.getenv("GUARDIAN_JSON_LOGGING", "false").lower() == "true"
    enable_file_logging = enable_file_logging if enable_file_logging is not None else os.getenv("GUARDIAN_FILE_LOGGING", "true").lower() == "true"
    
    # Create log directory
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Define log file paths
    log_files = {
        'guardian_operations': log_dir_path / 'guardian_operations.log',
        'guardian_errors': log_dir_path / 'guardian_errors.log',
        'guardian_performance': log_dir_path / 'guardian_performance.log',
        'guardian_auth': log_dir_path / 'guardian_auth.log',
        'guardian_submissions': log_dir_path / 'guardian_submissions.log'
    }
    
    # Logging configuration dictionary
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'guardian_context': {
                '()': 'guardian_error_handler.GuardianLogFormatter',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'guardian_context',
                'stream': sys.stdout
            }
        },
        'loggers': {
            'guardian': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'guardian.auth': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'guardian.service': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'guardian.policy': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'guardian.submissions': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'guardian.scheduler': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'guardian.error_handler': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    }
    
    # Add file handlers if enabled
    if enable_file_logging:
        # Operations log (all Guardian operations)
        config['handlers']['operations_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': str(log_files['guardian_operations']),
            'maxBytes': max_log_size_mb * 1024 * 1024,
            'backupCount': backup_count,
            'encoding': 'utf-8'
        }
        
        # Error log (errors and warnings only)
        config['handlers']['error_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'WARNING',
            'formatter': 'detailed',
            'filename': str(log_files['guardian_errors']),
            'maxBytes': max_log_size_mb * 1024 * 1024,
            'backupCount': backup_count,
            'encoding': 'utf-8'
        }
        
        # Performance log (performance metrics and alerts)
        config['handlers']['performance_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': str(log_files['guardian_performance']),
            'maxBytes': max_log_size_mb * 1024 * 1024,
            'backupCount': backup_count,
            'encoding': 'utf-8'
        }
        
        # Add file handlers to all Guardian loggers
        for logger_name in config['loggers']:
            if logger_name.startswith('guardian'):
                config['loggers'][logger_name]['handlers'].extend([
                    'operations_file', 'error_file'
                ])
    
    # Add JSON logging if enabled
    if enable_json_logging:
        config['formatters']['json'] = {
            '()': 'guardian_logging_config.JSONFormatter'
        }
        
        config['handlers']['json_console'] = {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'json',
            'stream': sys.stdout
        }
        
        # Add JSON handler to Guardian loggers
        for logger_name in config['loggers']:
            if logger_name.startswith('guardian'):
                config['loggers'][logger_name]['handlers'].append('json_console')
    
    # Apply the configuration
    logging.config.dictConfig(config)
    
    # Log configuration summary
    logger = logging.getLogger('guardian.config')
    logger.info("🔧 Guardian logging configuration applied")
    logger.info(f"📊 Log level: {log_level}")
    logger.info(f"📁 Log directory: {log_dir}")
    logger.info(f"📄 File logging: {'enabled' if enable_file_logging else 'disabled'}")
    logger.info(f"🔍 JSON logging: {'enabled' if enable_json_logging else 'disabled'}")
    
    return {
        'log_level': log_level,
        'log_dir': str(log_dir_path),
        'file_logging_enabled': enable_file_logging,
        'json_logging_enabled': enable_json_logging,
        'log_files': {k: str(v) for k, v in log_files.items()},
        'max_log_size_mb': max_log_size_mb,
        'backup_count': backup_count
    }


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        import json
        
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add Guardian-specific context
        guardian_fields = [
            'guardian_operation', 'guardian_policy_id', 'guardian_document_id',
            'error_category', 'error_severity', 'retry_count', 'duration_ms',
            'device_id', 'submission_id', 'rate_limit_hit'
        ]
        
        for field in guardian_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info) if record.exc_info else None
            }
        
        return json.dumps(log_entry, default=str)


class GuardianLogFilter(logging.Filter):
    """Custom filter for Guardian logs"""
    
    def __init__(self, operation_filter: str = None, min_duration_ms: float = None):
        super().__init__()
        self.operation_filter = operation_filter
        self.min_duration_ms = min_duration_ms
    
    def filter(self, record):
        # Filter by operation if specified
        if self.operation_filter:
            operation = getattr(record, 'guardian_operation', '')
            if self.operation_filter not in operation:
                return False
        
        # Filter by minimum duration if specified
        if self.min_duration_ms:
            duration = getattr(record, 'duration_ms', 0)
            if duration < self.min_duration_ms:
                return False
        
        return True


def create_performance_logger(name: str = 'guardian.performance') -> logging.Logger:
    """Create a specialized logger for performance metrics"""
    logger = logging.getLogger(name)
    
    # Add performance-specific handler if not already present
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) and 'performance' in h.baseFilename 
               for h in logger.handlers):
        
        log_dir = Path(os.getenv("GUARDIAN_LOG_DIR", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            log_dir / 'guardian_performance.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - PERF - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_guardian_operation_metrics(operation: str, duration_ms: float, success: bool, 
                                 policy_id: str = None, error_category: str = None):
    """Log operation metrics for monitoring and analysis"""
    perf_logger = create_performance_logger()
    
    metrics = {
        'operation': operation,
        'duration_ms': duration_ms,
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if policy_id:
        metrics['policy_id'] = policy_id
    if error_category:
        metrics['error_category'] = error_category
    
    import json
    perf_logger.info(json.dumps(metrics))


def get_logging_health_status() -> Dict[str, Any]:
    """Get health status of logging system"""
    log_dir = Path(os.getenv("GUARDIAN_LOG_DIR", "logs"))
    
    health = {
        'status': 'healthy',
        'log_directory_exists': log_dir.exists(),
        'log_directory_writable': os.access(log_dir, os.W_OK) if log_dir.exists() else False,
        'active_loggers': [],
        'log_files': {}
    }
    
    # Check active Guardian loggers
    for name in logging.Logger.manager.loggerDict:
        if isinstance(logging.Logger.manager.loggerDict[name], logging.Logger) and name.startswith('guardian'):
            logger = logging.getLogger(name)
            health['active_loggers'].append({
                'name': name,
                'level': logging.getLevelName(logger.level),
                'handlers': len(logger.handlers),
                'disabled': logger.disabled
            })
    
    # Check log files
    if log_dir.exists():
        for log_file in log_dir.glob('guardian_*.log'):
            try:
                stat = log_file.stat()
                health['log_files'][log_file.name] = {
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'readable': os.access(log_file, os.R_OK),
                    'writable': os.access(log_file, os.W_OK)
                }
            except Exception as e:
                health['log_files'][log_file.name] = {'error': str(e)}
    
    # Determine overall health
    if not health['log_directory_exists'] or not health['log_directory_writable']:
        health['status'] = 'degraded'
    
    if not health['active_loggers']:
        health['status'] = 'warning'
    
    return health


# Initialize logging when module is imported
if __name__ != "__main__":
    # Only setup logging if not running as main script
    try:
        setup_guardian_logging()
    except Exception as e:
        print(f"Warning: Failed to setup Guardian logging: {e}")


if __name__ == "__main__":
    # Test logging configuration
    print("🔍 Testing Guardian logging configuration...")
    
    config = setup_guardian_logging(log_level="DEBUG", enable_json_logging=True)
    print(f"✅ Logging configured: {config}")
    
    # Test different loggers
    loggers = [
        'guardian.auth',
        'guardian.service', 
        'guardian.policy',
        'guardian.submissions',
        'guardian.error_handler'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.info(f"Testing {logger_name} logger")
        logger.warning(f"Warning from {logger_name}")
        logger.error(f"Error from {logger_name}")
    
    # Test performance logging
    log_guardian_operation_metrics('test_operation', 1500.0, True, 'test_policy')
    
    # Test health status
    health = get_logging_health_status()
    print(f"📊 Logging health: {health}")
    
    print("✅ Guardian logging test complete")