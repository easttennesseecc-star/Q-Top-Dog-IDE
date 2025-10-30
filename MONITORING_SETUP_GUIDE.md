# Monitoring & Observability Setup Guide

## Overview

The AI Marketplace now includes comprehensive monitoring and observability for 24/7 visibility into system health, performance, and business metrics.

## ✅ Features Implemented

### 1. **Core Monitoring System**
- Real-time error tracking
- Performance monitoring with P95/P99 metrics
- Business event tracking
- Alert generation and management
- Customizable thresholds

### 2. **Health Checks**
- Liveness probe (`/api/monitoring/health/live`)
- Readiness probe (`/api/monitoring/health/ready`)
- Full health check (`/api/monitoring/health`)

### 3. **Metrics Collection**
- Performance statistics (avg, p95, p99, min, max)
- Error rate tracking
- Operation counting
- Custom metric support

### 4. **API Endpoints**

#### Health & Status
```
GET /api/monitoring/health/live       - Liveness probe
GET /api/monitoring/health/ready      - Readiness probe
GET /api/monitoring/health            - Full health check
GET /api/monitoring/status            - HTML status page
```

#### Metrics
```
GET /api/monitoring/metrics/performance   - Performance stats
GET /api/monitoring/metrics/summary       - Metrics summary
```

#### Errors & Alerts
```
GET /api/monitoring/errors/recent        - Recent errors (limit: 10)
GET /api/monitoring/alerts/recent        - Recent alerts (limit: 10)
GET /api/monitoring/alerts/count         - Alert severity breakdown
```

#### Dashboard
```
GET /api/monitoring/dashboard/json       - JSON dashboard data
GET /api/monitoring/dashboard/text       - ASCII text dashboard
```

#### Administration
```
GET /api/monitoring/events/recent        - Recent events
GET /api/monitoring/events/summary       - Events by category
POST /api/monitoring/admin/clear-history - Clear monitoring data
GET /api/monitoring/admin/config         - Monitoring configuration
```

## 📊 Integration with AI Marketplace

### 1. **Add to FastAPI Application**

Update `backend/ai_marketplace_routes.py`:

```python
from fastapi import FastAPI
from monitoring_routes import router as monitoring_router

app = FastAPI()

# Add monitoring routes
app.include_router(monitoring_router)

# Your existing routes...
```

### 2. **Track API Performance**

Use the performance monitoring decorator:

```python
from monitoring import monitor_performance, monitoring, EventCategory

@app.get("/api/search-models")
@monitor_performance(operation_name="search_models")
async def search_models(query: str):
    # Your code here
    
    # Track business events
    monitoring.track_event(
        category=EventCategory.BUSINESS,
        event_name="model_search",
        data={"query": query, "result_count": len(results)}
    )
    
    return results
```

### 3. **Track Errors**

```python
from monitoring import monitoring, AlertLevel

try:
    # Your code
    pass
except Exception as e:
    monitoring.track_error(
        error=e,
        context={"operation": "user_registration"},
        severity=AlertLevel.ERROR
    )
    raise
```

### 4. **Track Custom Metrics**

```python
from monitoring import monitoring, MetricType

# Track user registrations
monitoring.track_metric(
    metric_name="user_registrations",
    value=1,
    metric_type=MetricType.COUNTER,
    tags={"provider": "google"}
)

# Track API availability
monitoring.track_metric(
    metric_name="api_availability",
    value=99.9,
    metric_type=MetricType.GAUGE,
    tags={"endpoint": "/api/search-models"}
)
```

## 🚀 Deployment Monitoring

### Alert Thresholds (Configured)

```
Error Rate Alert:           > 5%
Response Time Alert:        > 2 seconds
Database Connection Fail:   Immediate alert
Critical Errors:            Immediate alert
```

### Health Status Levels

- ✅ **Healthy**: All systems operational, error rate < 5%
- ⚠️ **Degraded**: Error rate > 5% or slow responses
- ❌ **Error**: Critical alerts triggered

## 📈 Monitoring Examples

### Example 1: Check System Health

```bash
curl http://localhost:8000/api/monitoring/health
```

Response:
```json
{
  "status": "alive",
  "ready": true,
  "health_level": "healthy",
  "total_events": 1250,
  "total_errors": 3,
  "error_rate": 0.0024,
  "total_alerts": 0
}
```

### Example 2: Get Performance Metrics

```bash
curl http://localhost:8000/api/monitoring/metrics/performance
```

Response:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "performance": {
    "search_models": {
      "min_ms": 12.5,
      "max_ms": 145.2,
      "avg_ms": 45.3,
      "p95_ms": 120.5,
      "p99_ms": 135.2,
      "count": 847
    },
    "user_registration": {
      "min_ms": 25.1,
      "max_ms": 200.5,
      "avg_ms": 62.3,
      "p95_ms": 180.2,
      "p99_ms": 195.3,
      "count": 523
    }
  }
}
```

### Example 3: Get Recent Errors

```bash
curl http://localhost:8000/api/monitoring/errors/recent?limit=5
```

Response:
```json
{
  "timestamp": "2024-01-15T10:31:22.456Z",
  "limit": 5,
  "count": 2,
  "errors": [
    {
      "timestamp": "2024-01-15T10:25:15.123Z",
      "error_type": "ValueError",
      "error_message": "Invalid complexity level: extreme",
      "severity": "error",
      "context": {"operation": "get_recommendations"}
    }
  ]
}
```

## 🔧 External Monitoring Integration

### Option 1: Sentry (Error Tracking)

```bash
pip install sentry-sdk
```

Add to your FastAPI app:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[
        StarletteIntegration(),
        FastApiIntegration(),
    ],
    traces_sample_rate=0.1,
    environment="production"
)
```

### Option 2: DataDog (Full Observability)

```bash
pip install datadog
```

Add to your code:

```python
from datadog import initialize, api
from monitoring import monitoring

# Forward monitoring data to DataDog
def send_to_datadog():
    stats = monitoring.get_performance_stats()
    for operation, metrics in stats.items():
        api.Metric.send(
            metric=f"marketplace.{operation}.avg_time",
            points=metrics['avg_ms'],
            tags=[f"operation:{operation}"]
        )
```

### Option 3: Prometheus + Grafana

```bash
pip install prometheus-client
```

Add to your FastAPI app:

```python
from prometheus_client import Counter, Histogram

search_counter = Counter('marketplace_searches_total', 'Total searches')
search_time = Histogram('marketplace_search_duration_seconds', 'Search duration')

@app.get("/api/search-models")
async def search_models(query: str):
    with search_time.time():
        # Your code
        search_counter.inc()
        return results
```

## 🎯 Recommended Setup for Staging/Production

### Minimal Setup (Free)
1. Use built-in monitoring
2. Export to CSV/JSON logs
3. Monitor logs with ELK stack (Elasticsearch + Kibana)

### Recommended Setup (Professional)
1. Built-in monitoring + Sentry
2. Prometheus for metrics collection
3. Grafana for dashboards
4. PagerDuty for alert escalation

### Enterprise Setup
1. DataDog for full observability
2. Automated incident management
3. Custom dashboards and alerts
4. 24/7 support and SLA

## 📋 Next Steps

### For Staging Deployment:
1. ✅ Monitoring system created
2. ✅ API endpoints integrated
3. ✅ Health checks configured
4. ⏭️ Deploy to staging server
5. ⏭️ Configure alerts
6. ⏭️ Set up external monitoring

### For Go-Live:
1. Test all monitoring endpoints
2. Configure external error tracking
3. Set up alert notifications (Slack, Email)
4. Create runbooks for common alerts
5. Train team on monitoring dashboard

## 🚨 Critical Alerts Already Configured

The system automatically alerts on:

- **Critical Errors**: Any unhandled exception
- **High Error Rate**: > 5% of requests failing
- **Slow Operations**: Response time > 2 seconds
- **Database Issues**: Connection failures
- **Performance Degradation**: Rapid increase in response times

## 📞 Support

For monitoring integration help:
1. Check `/api/monitoring/status` for HTML dashboard
2. Review `/api/monitoring/dashboard/json` for detailed data
3. Check `logs/marketplace.log` for detailed logs
4. Review `logs/alerts.log` for alert history

---

**Status**: ✅ Monitoring system ready for deployment
**Test the monitoring API**: Navigate to `http://localhost:8000/api/monitoring/status`
