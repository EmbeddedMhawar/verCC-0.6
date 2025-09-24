#!/usr/bin/env python3
"""
Guardian Error Handler and Logging Enhancement
Comprehensive error handling, logging, retry logic, and rate limiting for Guardian API interactions
"""

import os
import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import requests
from functools import wraps
import threading
from collections import defaultdict, deque

# Configure structured logging for Guardian operations
class GuardianLogFormatter(logging.Formatter):
    """Custom formatter for Guardian API interactions"""
    
    def format(self, record):
        # Add Guardian-specific context
        if hasattr(record, 'guardian_operation'):
            record.msg = f"[{record.guardian_operation}] {record.msg}"
        
        if hasattr(record, 'guardian_policy_id'):
            record.msg = f"{record.msg} (Policy: {record.guardian_policy_id})"
        
        if hasattr(record, 'guardian_document_id'):
            record.msg = f"{record.msg} (Doc: {record.guardian_document_id})"
        
        return super().format(record)

class ErrorSeverity(Enum):
    """Error severity levels for Guardian operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categories of Guardian API errors"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """Context information for error handling"""
    operation: str
    policy_id: Optional[str] = None
    document_id: Optional[str] = None
    device_id: Optional[str] = None
    attempt_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetryStrategy:
    """Configuration for retry behavior"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    backoff_multiplier: float = 1.5
    retry_on_errors: List[ErrorCategory] = field(default_factory=lambda: [
        ErrorCategory.NETWORK,
        ErrorCategory.TIMEOUT,
        ErrorCategory.RATE_LIMIT,
        ErrorCategory.SERVER_ERROR
    ])

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    cooldown_period: float = 60.0

class GuardianRateLimiter:
    """Rate limiter for Guardian API requests"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.request_times = deque()
        self.hourly_requests = deque()
        self.burst_requests = deque()
        self.lock = threading.Lock()
        self.cooldown_until = None
    
    def can_make_request(self) -> bool:
        """Check if a request can be made without exceeding limits"""
        with self.lock:
            now = time.time()
            
            # Check cooldown period
            if self.cooldown_until and now < self.cooldown_until:
                return False
            
            # Clean old requests
            self._clean_old_requests(now)
            
            # Check burst limit (last 10 seconds)
            burst_window = now - 10
            recent_burst = sum(1 for t in self.burst_requests if t > burst_window)
            if recent_burst >= self.config.burst_limit:
                return False
            
            # Check per-minute limit
            minute_window = now - 60
            recent_minute = sum(1 for t in self.request_times if t > minute_window)
            if recent_minute >= self.config.requests_per_minute:
                return False
            
            # Check per-hour limit
            hour_window = now - 3600
            recent_hour = sum(1 for t in self.hourly_requests if t > hour_window)
            if recent_hour >= self.config.requests_per_hour:
                return False
            
            return True
    
    def record_request(self):
        """Record a successful request"""
        with self.lock:
            now = time.time()
            self.request_times.append(now)
            self.hourly_requests.append(now)
            self.burst_requests.append(now)
            self._clean_old_requests(now)
    
    def record_rate_limit_hit(self):
        """Record that we hit a rate limit"""
        with self.lock:
            self.cooldown_until = time.time() + self.config.cooldown_period
    
    def get_wait_time(self) -> float:
        """Get recommended wait time before next request"""
        with self.lock:
            now = time.time()
            
            # Check cooldown
            if self.cooldown_until and now < self.cooldown_until:
                return self.cooldown_until - now
            
            self._clean_old_requests(now)
            
            # Calculate wait time based on limits
            wait_times = []
            
            # Burst limit wait time
            if len(self.burst_requests) >= self.config.burst_limit:
                oldest_burst = min(self.burst_requests)
                wait_times.append(10 - (now - oldest_burst))
            
            # Per-minute limit wait time
            if len(self.request_times) >= self.config.requests_per_minute:
                oldest_minute = min(self.request_times)
                wait_times.append(60 - (now - oldest_minute))
            
            # Per-hour limit wait time
            if len(self.hourly_requests) >= self.config.requests_per_hour:
                oldest_hour = min(self.hourly_requests)
                wait_times.append(3600 - (now - oldest_hour))
            
            return max(wait_times) if wait_times else 0
    
    def _clean_old_requests(self, now: float):
        """Remove old request timestamps"""
        # Clean burst requests (10 seconds)
        while self.burst_requests and self.burst_requests[0] <= now - 10:
            self.burst_requests.popleft()
        
        # Clean minute requests (60 seconds)
        while self.request_times and self.request_times[0] <= now - 60:
            self.request_times.popleft()
        
        # Clean hour requests (3600 seconds)
        while self.hourly_requests and self.hourly_requests[0] <= now - 3600:
            self.hourly_requests.popleft()

class GuardianErrorHandler:
    """Comprehensive error handler for Guardian API operations"""
    
    def __init__(self, 
                 retry_strategy: RetryStrategy = None,
                 rate_limiter: GuardianRateLimiter = None,
                 logger: logging.Logger = None):
        self.retry_strategy = retry_strategy or RetryStrategy()
        self.rate_limiter = rate_limiter or GuardianRateLimiter(RateLimitConfig())
        self.logger = logger or self._setup_logger()
        
        # Error statistics
        self.error_stats = defaultdict(int)
        self.recovery_stats = defaultdict(int)
        self.operation_metrics = defaultdict(list)
        self._start_time = datetime.now()
        self._last_error_times = defaultdict(datetime)
        
        # Enhanced monitoring
        self._circuit_breaker_states = defaultdict(lambda: {'failures': 0, 'last_failure': None, 'state': 'CLOSED'})
        self._performance_alerts = []
    
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging for Guardian operations"""
        logger = logging.getLogger('guardian_error_handler')
        
        if not logger.handlers:
            # Console handler with custom formatter
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = GuardianLogFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # File handler for detailed logs
            log_dir = os.path.join(os.getcwd(), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(
                os.path.join(log_dir, 'guardian_operations.log')
            )
            file_handler.setLevel(logging.DEBUG)
            
            detailed_formatter = GuardianLogFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
            
            logger.setLevel(logging.DEBUG)
        
        return logger
    
    def categorize_error(self, error: Exception, response: requests.Response = None) -> ErrorCategory:
        """Categorize error for appropriate handling"""
        if isinstance(error, requests.exceptions.ConnectionError):
            return ErrorCategory.NETWORK
        elif isinstance(error, requests.exceptions.Timeout):
            return ErrorCategory.TIMEOUT
        elif hasattr(error, 'response') and error.response:
            status_code = error.response.status_code
            if status_code == 401:
                return ErrorCategory.AUTHENTICATION
            elif status_code == 403:
                return ErrorCategory.AUTHORIZATION
            elif status_code == 429:
                return ErrorCategory.RATE_LIMIT
            elif status_code >= 500:
                return ErrorCategory.SERVER_ERROR
            elif status_code == 400:
                return ErrorCategory.VALIDATION
        elif response and response.status_code:
            if response.status_code == 429:
                return ErrorCategory.RATE_LIMIT
            elif response.status_code >= 500:
                return ErrorCategory.SERVER_ERROR
        
        return ErrorCategory.UNKNOWN
    
    def get_error_severity(self, error_category: ErrorCategory, attempt_count: int) -> ErrorSeverity:
        """Determine error severity based on category and attempt count"""
        if error_category == ErrorCategory.AUTHENTICATION and attempt_count > 2:
            return ErrorSeverity.CRITICAL
        elif error_category == ErrorCategory.AUTHORIZATION:
            return ErrorSeverity.HIGH
        elif error_category in [ErrorCategory.NETWORK, ErrorCategory.TIMEOUT] and attempt_count > 3:
            return ErrorSeverity.HIGH
        elif error_category == ErrorCategory.RATE_LIMIT:
            return ErrorSeverity.MEDIUM
        elif attempt_count > 5:
            return ErrorSeverity.HIGH
        else:
            return ErrorSeverity.LOW
    
    def should_retry(self, error_category: ErrorCategory, attempt_count: int) -> bool:
        """Determine if operation should be retried"""
        if attempt_count >= self.retry_strategy.max_retries:
            return False
        
        if error_category not in self.retry_strategy.retry_on_errors:
            return False
        
        # Don't retry authorization errors
        if error_category == ErrorCategory.AUTHORIZATION:
            return False
        
        return True
    
    def calculate_delay(self, attempt_count: int, error_category: ErrorCategory) -> float:
        """Calculate delay before retry with exponential backoff"""
        base_delay = self.retry_strategy.base_delay
        
        # Adjust base delay based on error category
        if error_category == ErrorCategory.RATE_LIMIT:
            base_delay = max(base_delay, self.rate_limiter.get_wait_time())
        elif error_category == ErrorCategory.SERVER_ERROR:
            base_delay *= 2  # Longer delays for server errors
        
        # Exponential backoff
        delay = min(
            base_delay * (self.retry_strategy.exponential_base ** attempt_count),
            self.retry_strategy.max_delay
        )
        
        # Add jitter to prevent thundering herd
        if self.retry_strategy.jitter:
            import random
            jitter_factor = 0.1 + random.random() * 0.1  # 10-20% jitter
            delay *= (1 + jitter_factor)
        
        return delay
    
    def log_error(self, error: Exception, context: ErrorContext, severity: ErrorSeverity):
        """Log error with structured information"""
        error_category = self.categorize_error(error)
        
        # Create log record with Guardian context
        extra = {
            'guardian_operation': context.operation,
            'guardian_policy_id': context.policy_id,
            'guardian_document_id': context.document_id,
            'error_category': error_category.value,
            'error_severity': severity.value,
            'attempt_count': context.attempt_count,
            'duration_ms': (datetime.now() - context.start_time).total_seconds() * 1000
        }
        
        # Update error statistics
        self.error_stats[f"{error_category.value}_{severity.value}"] += 1
        
        # Log based on severity
        error_msg = f"Guardian API error: {str(error)}"
        
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(error_msg, extra=extra, exc_info=True)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(error_msg, extra=extra, exc_info=True)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(error_msg, extra=extra)
        else:
            self.logger.info(error_msg, extra=extra)
    
    def log_success(self, context: ErrorContext, response_data: Dict[str, Any] = None):
        """Log successful operation"""
        duration_ms = (datetime.now() - context.start_time).total_seconds() * 1000
        
        extra = {
            'guardian_operation': context.operation,
            'guardian_policy_id': context.policy_id,
            'guardian_document_id': context.document_id,
            'attempt_count': context.attempt_count,
            'duration_ms': duration_ms
        }
        
        # Record operation metrics
        self.operation_metrics[context.operation].append(duration_ms)
        
        # Log recovery if this was after failures
        if context.attempt_count > 0:
            self.recovery_stats[context.operation] += 1
            self.logger.info(f"Guardian operation recovered after {context.attempt_count} retries", extra=extra)
        else:
            self.logger.debug(f"Guardian operation successful", extra=extra)
    
    def log_rate_limit(self, context: ErrorContext, wait_time: float):
        """Log rate limiting events"""
        extra = {
            'guardian_operation': context.operation,
            'guardian_policy_id': context.policy_id,
            'wait_time_seconds': wait_time
        }
        
        self.logger.warning(f"Guardian API rate limit hit, waiting {wait_time:.1f}s", extra=extra)
        self.rate_limiter.record_rate_limit_hit()
    
    def with_error_handling(self, operation: str, policy_id: str = None, document_id: str = None):
        """Decorator for Guardian API operations with comprehensive error handling, circuit breaker, and performance monitoring"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check circuit breaker
                if not self.check_circuit_breaker(operation):
                    raise Exception(f"Circuit breaker is OPEN for operation '{operation}' - too many recent failures")
                
                context = ErrorContext(
                    operation=operation,
                    policy_id=policy_id,
                    document_id=document_id
                )
                
                operation_start_time = time.time()
                
                for attempt in range(self.retry_strategy.max_retries + 1):
                    context.attempt_count = attempt
                    
                    try:
                        # Check rate limits before making request
                        if not self.rate_limiter.can_make_request():
                            wait_time = self.rate_limiter.get_wait_time()
                            self.log_rate_limit(context, wait_time)
                            time.sleep(wait_time)
                        
                        # Execute the operation
                        result = func(*args, **kwargs)
                        
                        # Calculate operation duration
                        operation_duration = (time.time() - operation_start_time) * 1000
                        
                        # Record successful request
                        self.rate_limiter.record_request()
                        self.record_circuit_breaker_success(operation)
                        self.log_success(context, result if isinstance(result, dict) else None)
                        
                        # Performance monitoring
                        if operation_duration > 10000:  # 10 seconds threshold
                            self.add_performance_alert(operation, 'response_time_ms', operation_duration, 10000)
                        
                        return result
                        
                    except Exception as error:
                        error_category = self.categorize_error(error)
                        severity = self.get_error_severity(error_category, attempt)
                        
                        self.log_error(error, context, severity)
                        self.record_circuit_breaker_failure(operation)
                        
                        # Check if we should retry
                        if not self.should_retry(error_category, attempt):
                            raise error
                        
                        # Calculate delay and wait
                        if attempt < self.retry_strategy.max_retries:
                            delay = self.calculate_delay(attempt, error_category)
                            self.logger.info(f"Retrying Guardian operation in {delay:.1f}s (attempt {attempt + 2}/{self.retry_strategy.max_retries + 1})")
                            time.sleep(delay)
                
                # All retries exhausted
                raise Exception(f"Guardian operation '{operation}' failed after {self.retry_strategy.max_retries + 1} attempts")
            
            return wrapper
        return decorator
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error and recovery statistics with health metrics"""
        total_errors = sum(self.error_stats.values())
        total_recoveries = sum(self.recovery_stats.values())
        
        # Calculate average response times
        avg_response_times = {}
        for operation, times in self.operation_metrics.items():
            if times:
                avg_response_times[operation] = {
                    'avg_ms': sum(times) / len(times),
                    'min_ms': min(times),
                    'max_ms': max(times),
                    'count': len(times),
                    'p95_ms': sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else max(times),
                    'p99_ms': sorted(times)[int(len(times) * 0.99)] if len(times) > 100 else max(times)
                }
        
        # Calculate error rates by category
        error_rates = {}
        for error_key, count in self.error_stats.items():
            category = error_key.split('_')[0]
            if category not in error_rates:
                error_rates[category] = 0
            error_rates[category] += count
        
        # Health score calculation (0-100)
        health_score = 100
        if total_errors > 0:
            error_rate = total_errors / (total_errors + total_recoveries + 1)
            health_score = max(0, 100 - (error_rate * 100))
        
        # Rate limiter detailed status
        now = time.time()
        rate_limiter_status = {
            'requests_in_last_minute': len([t for t in self.rate_limiter.request_times if t > now - 60]),
            'requests_in_last_hour': len([t for t in self.rate_limiter.hourly_requests if t > now - 3600]),
            'burst_requests_last_10s': len([t for t in self.rate_limiter.burst_requests if t > now - 10]),
            'cooldown_active': self.rate_limiter.cooldown_until and now < self.rate_limiter.cooldown_until,
            'cooldown_remaining_seconds': max(0, self.rate_limiter.cooldown_until - now) if self.rate_limiter.cooldown_until else 0,
            'next_request_allowed_in_seconds': self.rate_limiter.get_wait_time(),
            'limits': {
                'requests_per_minute': self.rate_limiter.config.requests_per_minute,
                'requests_per_hour': self.rate_limiter.config.requests_per_hour,
                'burst_limit': self.rate_limiter.config.burst_limit
            }
        }
        
        return {
            'error_counts': dict(self.error_stats),
            'recovery_counts': dict(self.recovery_stats),
            'error_rates_by_category': error_rates,
            'total_errors': total_errors,
            'total_recoveries': total_recoveries,
            'recovery_rate_percent': (total_recoveries / total_errors * 100) if total_errors > 0 else 100,
            'health_score': health_score,
            'operation_metrics': avg_response_times,
            'rate_limiter_status': rate_limiter_status,
            'uptime_seconds': (datetime.now() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0,
            'last_error_time': max([datetime.now() - timedelta(seconds=60)] + [datetime.now()]) if total_errors > 0 else None
        }
    
    def reset_statistics(self):
        """Reset error and recovery statistics"""
        self.error_stats.clear()
        self.recovery_stats.clear()
        self.operation_metrics.clear()
        self._last_error_times.clear()
        self._circuit_breaker_states.clear()
        self._performance_alerts.clear()
        self._start_time = datetime.now()
    
    def check_circuit_breaker(self, operation: str) -> bool:
        """Check if circuit breaker allows operation to proceed"""
        breaker = self._circuit_breaker_states[operation]
        now = datetime.now()
        
        if breaker['state'] == 'OPEN':
            # Check if we should try to close the circuit
            if breaker['last_failure'] and (now - breaker['last_failure']).total_seconds() > 60:
                breaker['state'] = 'HALF_OPEN'
                self.logger.info(f"🔄 Circuit breaker for {operation} moved to HALF_OPEN state")
                return True
            return False
        
        return True
    
    def record_circuit_breaker_success(self, operation: str):
        """Record successful operation for circuit breaker"""
        breaker = self._circuit_breaker_states[operation]
        if breaker['state'] == 'HALF_OPEN':
            breaker['state'] = 'CLOSED'
            breaker['failures'] = 0
            self.logger.info(f"✅ Circuit breaker for {operation} closed after successful operation")
    
    def record_circuit_breaker_failure(self, operation: str):
        """Record failed operation for circuit breaker"""
        breaker = self._circuit_breaker_states[operation]
        breaker['failures'] += 1
        breaker['last_failure'] = datetime.now()
        
        # Open circuit if too many failures
        if breaker['failures'] >= 5 and breaker['state'] != 'OPEN':
            breaker['state'] = 'OPEN'
            self.logger.error(f"🚨 Circuit breaker for {operation} opened due to {breaker['failures']} consecutive failures")
    
    def add_performance_alert(self, operation: str, metric: str, value: float, threshold: float):
        """Add performance alert for monitoring"""
        alert = {
            'timestamp': datetime.now(),
            'operation': operation,
            'metric': metric,
            'value': value,
            'threshold': threshold,
            'severity': 'HIGH' if value > threshold * 2 else 'MEDIUM'
        }
        
        self._performance_alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self._performance_alerts) > 100:
            self._performance_alerts = self._performance_alerts[-100:]
        
        self.logger.warning(f"⚠️ Performance alert: {operation} {metric} = {value:.2f} (threshold: {threshold:.2f})")
    
    def get_performance_alerts(self, last_hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance alerts from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=last_hours)
        return [
            {
                'timestamp': alert['timestamp'].isoformat(),
                'operation': alert['operation'],
                'metric': alert['metric'],
                'value': alert['value'],
                'threshold': alert['threshold'],
                'severity': alert['severity']
            }
            for alert in self._performance_alerts
            if alert['timestamp'] > cutoff_time
        ]

# Global error handler instance
_global_error_handler = None

def get_guardian_error_handler() -> GuardianErrorHandler:
    """Get or create global Guardian error handler"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = GuardianErrorHandler()
    return _global_error_handler

def configure_guardian_logging(log_level: str = "INFO", log_file: str = None):
    """Configure Guardian logging globally with enhanced structured logging"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger for Guardian operations
    guardian_logger = logging.getLogger('guardian')
    guardian_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in guardian_logger.handlers[:]:
        guardian_logger.removeHandler(handler)
    
    # Console handler with enhanced formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    formatter = GuardianLogFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    guardian_logger.addHandler(console_handler)
    
    # File handler with rotation for production use
    if log_file:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        detailed_formatter = GuardianLogFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(detailed_formatter)
        guardian_logger.addHandler(file_handler)
    
    # Add JSON structured logging for production monitoring
    if os.getenv("GUARDIAN_JSON_LOGGING", "false").lower() == "true":
        import json
        
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add Guardian-specific context
                if hasattr(record, 'guardian_operation'):
                    log_entry['guardian_operation'] = record.guardian_operation
                if hasattr(record, 'guardian_policy_id'):
                    log_entry['guardian_policy_id'] = record.guardian_policy_id
                if hasattr(record, 'guardian_document_id'):
                    log_entry['guardian_document_id'] = record.guardian_document_id
                if hasattr(record, 'error_category'):
                    log_entry['error_category'] = record.error_category
                if hasattr(record, 'retry_count'):
                    log_entry['retry_count'] = record.retry_count
                if hasattr(record, 'duration_ms'):
                    log_entry['duration_ms'] = record.duration_ms
                
                return json.dumps(log_entry)
        
        json_handler = logging.StreamHandler()
        json_handler.setFormatter(JSONFormatter())
        json_handler.setLevel(logging.INFO)
        guardian_logger.addHandler(json_handler)

# Example usage and testing
if __name__ == "__main__":
    # Test the error handler
    error_handler = GuardianErrorHandler()
    
    @error_handler.with_error_handling("test_operation", policy_id="test_policy")
    def test_function():
        # Simulate various errors for testing
        import random
        error_type = random.choice(['success', 'network', 'auth', 'rate_limit'])
        
        if error_type == 'network':
            raise requests.exceptions.ConnectionError("Network error")
        elif error_type == 'auth':
            raise requests.exceptions.HTTPError("401 Unauthorized")
        elif error_type == 'rate_limit':
            response = requests.Response()
            response.status_code = 429
            raise requests.exceptions.HTTPError("429 Too Many Requests", response=response)
        else:
            return {"success": True, "data": "test"}
    
    # Test the function
    try:
        result = test_function()
        print(f"✅ Test successful: {result}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Print statistics
    stats = error_handler.get_error_statistics()
    print(f"📊 Error statistics: {json.dumps(stats, indent=2)}")