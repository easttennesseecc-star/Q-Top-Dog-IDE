"""
Monitoring API Endpoints for AI Marketplace
============================================

Provides REST endpoints for monitoring, health checks, metrics, and alerts.
"""

from fastapi import APIRouter, Response
from typing import Dict, Any
from datetime import datetime
from monitoring import (
    monitoring, 
    MonitoringDashboard, 
    HealthCheckService,
    EventCategory, 
    AlertLevel
)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


# ==================== HEALTH CHECKS ====================

health_service = HealthCheckService(monitoring)


@router.get("/health/live", name="Liveness Probe")
async def liveness() -> Dict[str, Any]:
    """
    Liveness probe - indicates if service is running
    Used by Kubernetes/Docker for restart decisions
    """
    return health_service.get_liveness()


@router.get("/health/ready", name="Readiness Probe")
async def readiness() -> Dict[str, Any]:
    """
    Readiness probe - indicates if service is ready for traffic
    Used by load balancers to route traffic
    """
    return health_service.get_readiness()


@router.get("/health", name="Full Health Check")
async def full_health() -> Dict[str, Any]:
    """
    Complete health check with detailed status
    """
    return {
        **health_service.get_liveness(),
        **health_service.get_readiness(),
        'details': monitoring.get_health_status()
    }


# ==================== METRICS & PERFORMANCE ====================

@router.get("/metrics/performance", name="Performance Metrics")
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance statistics for all tracked operations
    
    Returns min, max, average, p95, p99 response times
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'performance': monitoring.get_performance_stats()
    }


@router.get("/metrics/summary", name="Metrics Summary")
async def get_metrics_summary() -> Dict[str, Any]:
    """
    Get summary of all tracked metrics
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'total_metrics': len(monitoring.metrics),
        'total_events': len(monitoring.events),
        'total_errors': len(monitoring.errors),
        'total_alerts': len(monitoring.alerts),
        'metrics': monitoring.metrics
    }


# ==================== ERRORS & ALERTS ====================

@router.get("/errors/recent", name="Recent Errors")
async def get_recent_errors(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent errors
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'limit': limit,
        'count': len(monitoring.get_recent_errors(limit)),
        'errors': monitoring.get_recent_errors(limit)
    }


@router.get("/alerts/recent", name="Recent Alerts")
async def get_recent_alerts(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent alerts
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'limit': limit,
        'count': len(monitoring.get_recent_alerts(limit)),
        'alerts': monitoring.get_recent_alerts(limit)
    }


@router.get("/alerts/count", name="Alert Count")
async def get_alert_count() -> Dict[str, Any]:
    """
    Get total alert count and severity breakdown
    """
    alerts = monitoring.alerts
    severity_counts = {}
    
    for alert in alerts:
        severity = alert.get('severity', 'unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_alerts': len(alerts),
        'by_severity': severity_counts
    }


# ==================== DASHBOARD ====================

dashboard = MonitoringDashboard(monitoring)


@router.get("/dashboard/text", name="Text Dashboard")
async def get_text_dashboard() -> Dict[str, str]:
    """
    Get ASCII dashboard as text
    """
    return {
        'dashboard': dashboard.generate_summary()
    }


@router.get("/dashboard/json", name="JSON Dashboard")
async def get_json_dashboard() -> Dict[str, Any]:
    """
    Get complete monitoring data as JSON
    """
    return dashboard.export_metrics_json()


# ==================== EVENTS TRACKING ====================

@router.get("/events/recent", name="Recent Events")
async def get_recent_events(limit: int = 20, category: str = None) -> Dict[str, Any]:
    """
    Get recent tracked events
    
    Parameters:
    - limit: Maximum number of events to return
    - category: Filter by event category (optional)
    """
    events = monitoring.events
    
    if category:
        events = [e for e in events if e['category'] == category]
    
    return {
        'timestamp': datetime.now().isoformat(),
        'limit': limit,
        'category_filter': category,
        'count': len(events[-limit:]),
        'events': events[-limit:]
    }


@router.get("/events/summary", name="Events Summary")
async def get_events_summary() -> Dict[str, Any]:
    """
    Get summary of all tracked events by category
    """
    summary = {}
    
    for event in monitoring.events:
        category = event['category']
        summary[category] = summary.get(category, 0) + 1
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_events': len(monitoring.events),
        'by_category': summary
    }


# ==================== STATUS PAGE ====================

@router.get("/status", name="Service Status Page")
async def get_status_page() -> Response:
    """
    Get HTML status page
    """
    health = monitoring.get_health_status()
    perf = monitoring.get_performance_stats()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Marketplace - Status Page</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .status {{ padding: 15px; margin: 10px 0; border-radius: 4px; }}
            .status.healthy {{ background: #d4edda; border-left: 4px solid #28a745; }}
            .status.degraded {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
            .status.error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; margin-top: 30px; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }}
            th {{ background: #f9f9f9; font-weight: bold; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f9f9f9; border-radius: 4px; }}
            .error-item {{ background: #fee; padding: 10px; margin: 5px 0; border-left: 3px solid #d00; }}
            .alert-item {{ background: #ffe; padding: 10px; margin: 5px 0; border-left: 3px solid #ffa500; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 AI Marketplace - Status Page</h1>
            
            <div class="status {health['health_level']}">
                <strong>System Status:</strong> {health['status'].upper()}
                <br><small>Health Level: {health['health_level']} | Error Rate: {health['error_rate']*100:.1f}%</small>
                <br><small>Last Updated: {health['timestamp']}</small>
            </div>
            
            <h2>📊 Metrics</h2>
            <div class="metric">Total Events: {health['total_events']}</div>
            <div class="metric">Total Errors: {health['total_errors']}</div>
            <div class="metric">Total Alerts: {health['total_alerts']}</div>
            
            <h2>⏱️ Performance</h2>
            <table>
                <tr>
                    <th>Operation</th>
                    <th>Avg (ms)</th>
                    <th>P95 (ms)</th>
                    <th>P99 (ms)</th>
                    <th>Count</th>
                </tr>
    """
    
    for operation, stats in sorted(perf.items()):
        html += f"""
                <tr>
                    <td>{operation}</td>
                    <td>{stats['avg_ms']:.1f}</td>
                    <td>{stats['p95_ms']:.1f}</td>
                    <td>{stats['p99_ms']:.1f}</td>
                    <td>{stats['count']}</td>
                </tr>
        """
    
    html += """
            </table>
            
            <h2>🔗 API Endpoints</h2>
            <ul>
                <li><code>GET /api/monitoring/health</code> - Full health check</li>
                <li><code>GET /api/monitoring/health/live</code> - Liveness probe</li>
                <li><code>GET /api/monitoring/health/ready</code> - Readiness probe</li>
                <li><code>GET /api/monitoring/metrics/performance</code> - Performance stats</li>
                <li><code>GET /api/monitoring/errors/recent</code> - Recent errors</li>
                <li><code>GET /api/monitoring/alerts/recent</code> - Recent alerts</li>
                <li><code>GET /api/monitoring/dashboard/json</code> - Full dashboard data</li>
            </ul>
            
            <p style="color: #999; font-size: 12px; margin-top: 40px;">
                Last updated: {datetime.now().isoformat()}
            </p>
        </div>
    </body>
    </html>
    """
    
    return Response(content=html, media_type="text/html")


# ==================== ADMIN ENDPOINTS ====================

@router.post("/admin/clear-history", name="Clear History")
async def clear_monitoring_history() -> Dict[str, str]:
    """
    Clear all monitoring history (development only)
    """
    monitoring.clear_history()
    return {'status': 'cleared', 'timestamp': datetime.now().isoformat()}


@router.get("/admin/config", name="Monitoring Config")
async def get_monitoring_config() -> Dict[str, Any]:
    """
    Get current monitoring configuration
    """
    return {
        'enable_error_tracking': monitoring.config.enable_error_tracking,
        'enable_performance_tracking': monitoring.config.enable_performance_tracking,
        'enable_business_metrics': monitoring.config.enable_business_metrics,
        'alert_on_error_rate': monitoring.config.alert_on_error_rate,
        'alert_on_response_time': monitoring.config.alert_on_response_time,
        'alert_on_db_connection_fail': monitoring.config.alert_on_db_connection_fail,
        'enable_detailed_logging': monitoring.config.enable_detailed_logging
    }
