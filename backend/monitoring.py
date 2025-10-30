"""
AI Marketplace Monitoring & Observability Module
================================================

Provides comprehensive monitoring, logging, and error tracking for the AI Marketplace.
Integrates with multiple monitoring backends for 24/7 visibility.

Features:
- Error tracking and reporting
- Performance monitoring  
- Custom event tracking
- Alert configuration
- Dashboard generation
- Health checks
- Metrics collection
"""

import logging
import time
import functools
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/marketplace.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class MetricType(str, Enum):
    """Types of metrics to track"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class EventCategory(str, Enum):
    """Categories of events to track"""
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    ERROR = "error"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    SECURITY = "security"


class MonitoringConfig:
    """Configuration for monitoring system"""
    
    def __init__(
        self,
        enable_error_tracking: bool = True,
        enable_performance_tracking: bool = True,
        enable_business_metrics: bool = True,
        alert_on_error_rate: float = 0.05,  # 5%
        alert_on_response_time: float = 2.0,  # 2 seconds
        alert_on_db_connection_fail: bool = True,
        enable_detailed_logging: bool = True,
    ):
        self.enable_error_tracking = enable_error_tracking
        self.enable_performance_tracking = enable_performance_tracking
        self.enable_business_metrics = enable_business_metrics
        self.alert_on_error_rate = alert_on_error_rate
        self.alert_on_response_time = alert_on_response_time
        self.alert_on_db_connection_fail = alert_on_db_connection_fail
        self.enable_detailed_logging = enable_detailed_logging


class MonitoringSystem:
    """Central monitoring and observability system"""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.metrics: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.performance_data: Dict[str, List[float]] = {}
        
        logger.info("Monitoring system initialized")
    
    def track_event(
        self,
        category: EventCategory,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
        level: AlertLevel = AlertLevel.INFO
    ) -> None:
        """Track a business event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'category': category.value,
            'event_name': event_name,
            'data': data or {},
            'level': level.value
        }
        self.events.append(event)
        
        if self.config.enable_detailed_logging:
            logger.info(f"Event tracked: {event_name}", extra={'event': event})
    
    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: AlertLevel = AlertLevel.ERROR
    ) -> None:
        """Track an error with full context"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'severity': severity.value
        }
        self.errors.append(error_data)
        
        logger.error(
            f"Error tracked: {error_data['error_type']}: {error_data['error_message']}",
            extra={'error': error_data}
        )
        
        # Check if alert should be triggered
        if severity == AlertLevel.CRITICAL:
            self._trigger_alert(
                title=f"Critical Error: {error_data['error_type']}",
                message=error_data['error_message'],
                severity=severity,
                context=error_data
            )
    
    def track_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Track a performance or business metric"""
        metric_data = {
            'timestamp': datetime.now().isoformat(),
            'name': metric_name,
            'value': value,
            'type': metric_type.value,
            'tags': tags or {}
        }
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append(metric_data)
        
        if self.config.enable_detailed_logging:
            logger.debug(f"Metric: {metric_name}={value}")
    
    def track_performance(
        self,
        operation_name: str,
        duration_ms: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track operation performance"""
        if operation_name not in self.performance_data:
            self.performance_data[operation_name] = []
        
        self.performance_data[operation_name].append(duration_ms)
        
        # Check for performance alerts
        if self.config.enable_performance_tracking:
            if duration_ms > self.config.alert_on_response_time * 1000:
                self._trigger_alert(
                    title=f"Slow Operation: {operation_name}",
                    message=f"Operation took {duration_ms:.0f}ms (threshold: {self.config.alert_on_response_time*1000:.0f}ms)",
                    severity=AlertLevel.WARNING,
                    context={
                        'operation': operation_name,
                        'duration_ms': duration_ms,
                        'threshold_ms': self.config.alert_on_response_time * 1000,
                        'metadata': metadata
                    }
                )
        
        logger.debug(f"Performance: {operation_name} took {duration_ms:.2f}ms (success={success})")
    
    def _trigger_alert(
        self,
        title: str,
        message: str,
        severity: AlertLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Trigger an alert for critical issues"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'severity': severity.value,
            'context': context or {}
        }
        self.alerts.append(alert)
        
        logger.warning(f"ALERT: {title} - {message}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        total_events = len(self.events)
        total_errors = len(self.errors)
        total_alerts = len(self.alerts)
        
        error_rate = total_errors / max(total_events, 1)
        
        health_status = AlertLevel.INFO
        if error_rate > self.config.alert_on_error_rate:
            health_status = AlertLevel.WARNING
        if total_alerts > 0:
            health_status = AlertLevel.ERROR
        
        return {
            'status': 'healthy' if health_status == AlertLevel.INFO else 'degraded',
            'health_level': health_status.value,
            'total_events': total_events,
            'total_errors': total_errors,
            'error_rate': error_rate,
            'total_alerts': total_alerts,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for all tracked operations"""
        stats = {}
        
        for operation, durations in self.performance_data.items():
            if durations:
                stats[operation] = {
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'avg_ms': sum(durations) / len(durations),
                    'p95_ms': sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 0 else 0,
                    'p99_ms': sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 0 else 0,
                    'count': len(durations)
                }
        
        return stats
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors"""
        return self.errors[-limit:]
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alerts[-limit:]
    
    def clear_history(self) -> None:
        """Clear all collected data (for testing)"""
        self.events.clear()
        self.errors.clear()
        self.alerts.clear()
        self.performance_data.clear()


def monitor_performance(operation_name: Optional[str] = None):
    """Decorator to automatically monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                monitoring.track_performance(name, duration_ms, success=True)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                monitoring.track_performance(name, duration_ms, success=False)
                monitoring.track_error(e, context={'operation': name})
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                monitoring.track_performance(name, duration_ms, success=True)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                monitoring.track_performance(name, duration_ms, success=False)
                monitoring.track_error(e, context={'operation': name})
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Global monitoring instance
monitoring = MonitoringSystem(config=MonitoringConfig())


# ==================== ALERT HANDLERS ====================

class AlertHandler:
    """Base class for alert handlers"""
    
    def handle_alert(self, alert: Dict[str, Any]) -> None:
        """Handle an alert"""
        raise NotImplementedError


class ConsoleAlertHandler(AlertHandler):
    """Logs alerts to console"""
    
    def handle_alert(self, alert: Dict[str, Any]) -> None:
        severity = alert['severity'].upper()
        timestamp = alert['timestamp']
        title = alert['title']
        message = alert['message']
        print(f"\n{'='*60}")
        print(f"[{severity}] {timestamp}")
        print(f"{title}")
        print(f"{message}")
        print(f"{'='*60}\n")


class LogFileAlertHandler(AlertHandler):
    """Logs alerts to file"""
    
    def __init__(self, filename: str = 'logs/alerts.log'):
        self.filename = filename
    
    def handle_alert(self, alert: Dict[str, Any]) -> None:
        with open(self.filename, 'a') as f:
            f.write(f"\n[{alert['severity'].upper()}] {alert['timestamp']}\n")
            f.write(f"{alert['title']}\n")
            f.write(f"{alert['message']}\n")
            f.write(f"{'-'*60}\n")


class EmailAlertHandler(AlertHandler):
    """Sends critical alerts via email"""
    
    def __init__(self, smtp_config: Dict[str, str]):
        self.smtp_config = smtp_config
    
    def handle_alert(self, alert: Dict[str, Any]) -> None:
        # Only send critical alerts
        if alert['severity'] == AlertLevel.CRITICAL.value:
            logger.warning(f"Email alert would be sent (not implemented): {alert['title']}")


# ==================== DASHBOARD & REPORTING ====================

class MonitoringDashboard:
    """Generates monitoring dashboards and reports"""
    
    def __init__(self, monitoring_system: MonitoringSystem):
        self.monitoring = monitoring_system
    
    def generate_summary(self) -> str:
        """Generate a summary dashboard"""
        health = self.monitoring.get_health_status()
        perf = self.monitoring.get_performance_stats()
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           AI MARKETPLACE MONITORING DASHBOARD               ║
╚══════════════════════════════════════════════════════════════╝

┌─ System Health ─────────────────────────────────────────────┐
│ Status: {health['status'].upper():20} ({health['health_level']})
│ Timestamp: {health['timestamp']}
│ Error Rate: {health['error_rate']*100:.1f}% (threshold: {self.monitoring.config.alert_on_error_rate*100:.1f}%)
│ Total Events: {health['total_events']}
│ Total Errors: {health['total_errors']}
│ Total Alerts: {health['total_alerts']}
└─────────────────────────────────────────────────────────────┘

┌─ Performance Metrics ───────────────────────────────────────┐
"""
        
        if perf:
            for operation, stats in sorted(perf.items()):
                summary += f"\n│ {operation}\n"
                summary += f"│   Avg: {stats['avg_ms']:.1f}ms | P95: {stats['p95_ms']:.1f}ms | P99: {stats['p99_ms']:.1f}ms\n"
                summary += f"│   Count: {stats['count']} | Min: {stats['min_ms']:.1f}ms | Max: {stats['max_ms']:.1f}ms\n"
        else:
            summary += "│ No performance data yet\n"
        
        summary += "└─────────────────────────────────────────────────────────────┘\n"
        
        recent_errors = self.monitoring.get_recent_errors(5)
        if recent_errors:
            summary += "\n┌─ Recent Errors (Last 5) ───────────────────────────────────┐\n"
            for error in recent_errors:
                summary += f"│ [{error['severity'].upper()}] {error['error_type']}\n"
                summary += f"│    {error['error_message'][:50]}\n"
            summary += "└─────────────────────────────────────────────────────────────┘\n"
        
        recent_alerts = self.monitoring.get_recent_alerts(5)
        if recent_alerts:
            summary += "\n┌─ Recent Alerts (Last 5) ────────────────────────────────────┐\n"
            for alert in recent_alerts:
                summary += f"│ [{alert['severity'].upper()}] {alert['title']}\n"
                summary += f"│    {alert['message'][:45]}\n"
            summary += "└─────────────────────────────────────────────────────────────┘\n"
        
        return summary
    
    def export_metrics_json(self) -> Dict[str, Any]:
        """Export all metrics as JSON"""
        return {
            'timestamp': datetime.now().isoformat(),
            'health': self.monitoring.get_health_status(),
            'performance': self.monitoring.get_performance_stats(),
            'recent_errors': self.monitoring.get_recent_errors(20),
            'recent_alerts': self.monitoring.get_recent_alerts(20),
            'total_events': len(self.monitoring.events),
            'total_metrics': len(self.monitoring.metrics)
        }


# ==================== HEALTH CHECK ENDPOINTS ====================

class HealthCheckService:
    """Service for health checks and liveness/readiness probes"""
    
    def __init__(self, monitoring_system: MonitoringSystem):
        self.monitoring = monitoring_system
    
    def get_liveness(self) -> Dict[str, Any]:
        """Check if service is alive"""
        return {
            'status': 'alive',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_readiness(self) -> Dict[str, Any]:
        """Check if service is ready to accept traffic"""
        health = self.monitoring.get_health_status()
        is_ready = health['health_level'] != 'degraded' and len(self.monitoring.get_recent_alerts(1)) == 0
        
        return {
            'status': 'ready' if is_ready else 'not_ready',
            'ready': is_ready,
            'health_level': health['health_level'],
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    # Example usage
    print("Monitoring system initialized successfully")
    print("\nAvailable components:")
    print("  - MonitoringSystem: Core monitoring")
    print("  - MonitoringDashboard: Dashboard generation")
    print("  - HealthCheckService: Health probes")
    print("  - monitor_performance: Performance decorator")
