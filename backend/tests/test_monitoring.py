"""
Test monitoring system to verify all components are working correctly
"""

import pytest
from datetime import datetime
from monitoring import (
    monitoring,
    MonitoringSystem,
    MonitoringConfig,
    MonitoringDashboard,
    HealthCheckService,
    EventCategory,
    AlertLevel,
    MetricType,
    monitor_performance
)


class TestMonitoringCore:
    """Test core monitoring functionality"""
    
    def setup_method(self):
        """Clear monitoring state before each test"""
        monitoring.clear_history()
    
    def test_event_tracking(self):
        """Test event tracking"""
        monitoring.track_event(
            category=EventCategory.BUSINESS,
            event_name="test_event",
            data={"key": "value"}
        )
        
        assert len(monitoring.events) == 1
        assert monitoring.events[0]['event_name'] == 'test_event'
        assert monitoring.events[0]['data']['key'] == 'value'
    
    def test_error_tracking(self):
        """Test error tracking"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            monitoring.track_error(e, context={"operation": "test"})
        
        assert len(monitoring.errors) == 1
        assert monitoring.errors[0]['error_type'] == 'ValueError'
        assert monitoring.errors[0]['error_message'] == 'Test error'
    
    def test_metric_tracking(self):
        """Test metric tracking"""
        monitoring.track_metric(
            metric_name="test_metric",
            value=42.5,
            metric_type=MetricType.GAUGE,
            tags={"env": "test"}
        )
        
        assert 'test_metric' in monitoring.metrics
        assert len(monitoring.metrics['test_metric']) == 1
        assert monitoring.metrics['test_metric'][0]['value'] == 42.5
    
    def test_performance_tracking(self):
        """Test performance tracking"""
        monitoring.track_performance(
            operation_name="test_operation",
            duration_ms=123.4,
            success=True
        )
        
        assert 'test_operation' in monitoring.performance_data
        assert len(monitoring.performance_data['test_operation']) == 1
        assert monitoring.performance_data['test_operation'][0] == 123.4
    
    def test_health_status(self):
        """Test health status calculation"""
        # Add some events and errors
        for i in range(10):
            monitoring.track_event(
                category=EventCategory.BUSINESS,
                event_name=f"event_{i}",
                data={}
            )
        
        # Add one error
        try:
            raise RuntimeError("test error")
        except RuntimeError as e:
            monitoring.track_error(e)
        
        health = monitoring.get_health_status()
        
        assert health['total_events'] == 10
        assert health['total_errors'] == 1
        assert health['error_rate'] == pytest.approx(0.1, rel=0.01)
    
    def test_alert_triggering(self):
        """Test alert triggering"""
        monitoring._trigger_alert(
            title="Test Alert",
            message="This is a test",
            severity=AlertLevel.WARNING
        )
        
        assert len(monitoring.alerts) == 1
        assert monitoring.alerts[0]['title'] == 'Test Alert'
    
    def test_performance_alert_threshold(self):
        """Test that slow operations trigger alerts"""
        # Track a slow operation (> 2000ms threshold)
        monitoring.track_performance(
            operation_name="slow_op",
            duration_ms=3000,
            success=True
        )
        
        # Should have triggered alert
        assert len(monitoring.alerts) > 0
        assert any('Slow Operation' in str(a.get('title', '')) for a in monitoring.alerts)
    
    def test_clear_history(self):
        """Test clearing monitoring history"""
        monitoring.track_event(
            category=EventCategory.BUSINESS,
            event_name="test",
            data={}
        )
        
        assert len(monitoring.events) == 1
        
        monitoring.clear_history()
        
        assert len(monitoring.events) == 0
        assert len(monitoring.errors) == 0
        assert len(monitoring.alerts) == 0


class TestMonitoringDashboard:
    """Test dashboard generation"""
    
    def setup_method(self):
        monitoring.clear_history()
    
    def test_dashboard_generation(self):
        """Test dashboard summary generation"""
        # Add some data
        monitoring.track_event(
            category=EventCategory.BUSINESS,
            event_name="test",
            data={}
        )
        
        monitoring.track_performance(
            operation_name="test_op",
            duration_ms=100,
            success=True
        )
        
        dashboard = MonitoringDashboard(monitoring)
        summary = dashboard.generate_summary()
        
        assert "MONITORING DASHBOARD" in summary
        assert "System Health" in summary
        assert "test_op" in summary
    
    def test_metrics_json_export(self):
        """Test JSON export"""
        monitoring.track_metric(
            metric_name="test",
            value=42
        )
        
        dashboard = MonitoringDashboard(monitoring)
        metrics_json = dashboard.export_metrics_json()
        
        assert 'timestamp' in metrics_json
        assert 'health' in metrics_json
        assert 'performance' in metrics_json


class TestHealthCheck:
    """Test health check service"""
    
    def setup_method(self):
        monitoring.clear_history()
    
    def test_liveness(self):
        """Test liveness probe"""
        health_service = HealthCheckService(monitoring)
        liveness = health_service.get_liveness()
        
        assert liveness['status'] == 'alive'
        assert 'timestamp' in liveness
    
    def test_readiness_healthy(self):
        """Test readiness when healthy"""
        health_service = HealthCheckService(monitoring)
        readiness = health_service.get_readiness()
        
        assert readiness['status'] == 'ready'
        assert readiness['ready'] is True
    
    def test_readiness_degraded(self):
        """Test readiness when alerts present"""
        health_service = HealthCheckService(monitoring)
        
        # Trigger an alert
        monitoring._trigger_alert(
            title="Test",
            message="Alert",
            severity=AlertLevel.CRITICAL
        )
        
        readiness = health_service.get_readiness()
        
        assert readiness['ready'] is False


class TestPerformanceDecorator:
    """Test performance monitoring decorator"""
    
    def setup_method(self):
        monitoring.clear_history()
    
    def test_sync_function_monitoring(self):
        """Test monitoring of synchronous functions"""
        
        @monitor_performance(operation_name="test_sync")
        def test_function():
            return "result"
        
        result = test_function()
        
        assert result == "result"
        assert 'test_sync' in monitoring.performance_data
        assert len(monitoring.performance_data['test_sync']) == 1
    
    def test_sync_function_error_monitoring(self):
        """Test error monitoring in decorated functions"""
        
        @monitor_performance(operation_name="test_error")
        def failing_function():
            raise ValueError("test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        assert 'test_error' in monitoring.performance_data
        assert len(monitoring.errors) == 1


class TestMonitoringConfig:
    """Test monitoring configuration"""
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = MonitoringConfig(
            alert_on_error_rate=0.10,
            alert_on_response_time=5.0
        )
        
        assert config.alert_on_error_rate == 0.10
        assert config.alert_on_response_time == 5.0
    
    def test_config_applied(self):
        """Test that config is applied to system"""
        config = MonitoringConfig(
            enable_detailed_logging=False
        )
        
        monitoring_system = MonitoringSystem(config=config)
        
        assert monitoring_system.config.enable_detailed_logging is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
