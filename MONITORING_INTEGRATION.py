"""
Integration instructions for adding Monitoring to the AI Marketplace API
=========================================================================

Follow these steps to integrate monitoring into your FastAPI application.
"""

# STEP 1: Update requirements.txt
# Add these dependencies (already included):
# - fastapi (already installed)
# - uvicorn (already installed)
# - python-dotenv (already installed)

# STEP 2: Import monitoring in your main FastAPI application

from fastapi import FastAPI
from monitoring_routes import router as monitoring_router

app = FastAPI(title="AI Marketplace API")

# Add monitoring routes
app.include_router(monitoring_router)

# Your other routes...


# STEP 3: Example integration in API endpoints

from monitoring import monitor_performance, monitoring, EventCategory, AlertLevel, MetricType

# Example 1: Add performance monitoring to an endpoint
@app.get("/api/search-models")
@monitor_performance(operation_name="search_models_api")
async def search_models_api(query: str, limit: int = 10):
    """Search for AI models - automatically monitored"""
    try:
        # Your search logic here
        results = []  # placeholder
        
        # Track business event
        monitoring.track_event(
            category=EventCategory.BUSINESS,
            event_name="model_search_performed",
            data={
                "query": query,
                "limit": limit,
                "result_count": len(results),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Track metric
        monitoring.track_metric(
            metric_name="searches_total",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={"endpoint": "search_models", "query_length": str(len(query))}
        )
        
        return {"query": query, "results": results, "count": len(results)}
    
    except Exception as e:
        # Errors are automatically tracked by the decorator
        # But you can add context
        monitoring.track_error(
            error=e,
            context={
                "operation": "search_models_api",
                "query": query
            },
            severity=AlertLevel.ERROR
        )
        raise


# Example 2: Manual performance tracking
@app.post("/api/users/register")
async def register_user(email: str, password: str):
    """User registration with explicit monitoring"""
    import time
    start_time = time.time()
    
    try:
        # Your registration logic here
        user = {}  # placeholder
        
        # Track success
        duration_ms = (time.time() - start_time) * 1000
        monitoring.track_performance(
            operation_name="user_registration",
            duration_ms=duration_ms,
            success=True,
            metadata={"email": email}
        )
        
        # Track event
        monitoring.track_event(
            category=EventCategory.USER_ACTION,
            event_name="user_registered",
            data={"email": email}
        )
        
        return {"status": "success", "user": user}
    
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        monitoring.track_performance(
            operation_name="user_registration",
            duration_ms=duration_ms,
            success=False,
            metadata={"email": email}
        )
        
        monitoring.track_error(
            error=e,
            context={"operation": "register_user", "email": email},
            severity=AlertLevel.ERROR
        )
        raise


# Example 3: Custom metrics tracking
@app.post("/api/models/use")
async def use_model(model_id: str, tokens: int):
    """Track model usage with business metrics"""
    try:
        # Your model usage logic
        cost = tokens * 0.0001  # Example cost calculation
        
        # Track multiple metrics
        monitoring.track_metric(
            metric_name="model_usage_count",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={"model_id": model_id}
        )
        
        monitoring.track_metric(
            metric_name="tokens_consumed",
            value=tokens,
            metric_type=MetricType.COUNTER,
            tags={"model_id": model_id}
        )
        
        monitoring.track_metric(
            metric_name="revenue_generated",
            value=cost,
            metric_type=MetricType.COUNTER,
            tags={"model_id": model_id}
        )
        
        # Track as business event
        monitoring.track_event(
            category=EventCategory.BUSINESS,
            event_name="model_usage",
            data={
                "model_id": model_id,
                "tokens": tokens,
                "cost": cost
            }
        )
        
        return {"status": "success", "tokens_used": tokens, "cost": cost}
    
    except Exception as e:
        monitoring.track_error(e, context={"operation": "use_model", "model_id": model_id})
        raise


# STEP 4: Complete main.py integration example

"""
# Add to top of main.py:

from monitoring_routes import router as monitoring_router
from monitoring import monitoring, EventCategory, AlertLevel, monitor_performance

# After app = FastAPI(...):

app.include_router(monitoring_router)

# Add middleware to track all requests
from fastapi import Request
import time

@app.middleware("http")
async def track_all_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        # Track performance for all endpoints
        monitoring.track_performance(
            operation_name=f"{request.method} {request.url.path}",
            duration_ms=duration_ms,
            success=response.status_code < 400,
            metadata={"status_code": response.status_code}
        )
        
        # Track business events for important endpoints
        if "/api/users" in request.url.path:
            monitoring.track_event(
                category=EventCategory.USER_ACTION,
                event_name=f"user_{request.method.lower()}",
                data={"endpoint": request.url.path}
            )
        
        return response
    
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        monitoring.track_performance(
            operation_name=f"{request.method} {request.url.path}",
            duration_ms=duration_ms,
            success=False
        )
        
        monitoring.track_error(
            error=e,
            context={"method": request.method, "path": request.url.path},
            severity=AlertLevel.ERROR
        )
        raise
"""


# STEP 5: Testing monitoring integration

"""
# Test in a new Python file:

import asyncio
from monitoring import monitoring, EventCategory, AlertLevel, MonitoringDashboard

# Simulate some operations
monitoring.track_event(
    category=EventCategory.BUSINESS,
    event_name="test_event",
    data={"test": "data"}
)

monitoring.track_metric(
    metric_name="test_metric",
    value=42
)

monitoring.track_performance(
    operation_name="test_operation",
    duration_ms=150.5,
    success=True
)

# Generate dashboard
dashboard = MonitoringDashboard(monitoring)
print(dashboard.generate_summary())

# Check health
health = monitoring.get_health_status()
print(f"Health Status: {health}")
"""


# STEP 6: Verify monitoring is working

"""
curl http://localhost:8000/api/monitoring/health
curl http://localhost:8000/api/monitoring/status
curl http://localhost:8000/api/monitoring/metrics/performance
"""


if __name__ == "__main__":
    print("""
    ✅ Monitoring Integration Guide Ready
    
    Steps to integrate:
    1. Add 'from monitoring_routes import router as monitoring_router' to main.py
    2. Add 'app.include_router(monitoring_router)' after app creation
    3. Use @monitor_performance decorator on endpoints
    4. Use monitoring.track_event() for business events
    5. Use monitoring.track_error() for exception handling
    6. Test endpoints at http://localhost:8000/api/monitoring/
    
    Available endpoints:
    - GET  /api/monitoring/health           - Full health check
    - GET  /api/monitoring/health/live      - Liveness probe
    - GET  /api/monitoring/health/ready     - Readiness probe
    - GET  /api/monitoring/status           - HTML status page
    - GET  /api/monitoring/metrics/performance - Performance stats
    - GET  /api/monitoring/errors/recent    - Recent errors
    - GET  /api/monitoring/alerts/recent    - Recent alerts
    - GET  /api/monitoring/dashboard/json   - Full dashboard
    - POST /api/monitoring/admin/clear-history - Clear data
    
    Documentation:
    - See MONITORING_SETUP_GUIDE.md for complete guide
    - See monitoring.py for API documentation
    - See monitoring_routes.py for endpoint implementations
    """)
