"""
Integration examples for the centralized logger in Q-IDE TopDog.

This module shows how to integrate the logger_utils into existing components:
- FastAPI application
- LLM pool detection
- Build monitoring
- Error handling
- Performance tracking
"""

from logger_utils import configure_logger, log_function_call
import logging
from contextlib import contextmanager
import time
from typing import Dict, Any


# Initialize logger early in your application
logger = configure_logger(
    name="q-ide-topdog",
    log_dir="./logs",
    level=logging.INFO
)


# ============================================================================
# EXAMPLE 1: FastAPI Integration
# ============================================================================

"""
Add this to your main.py:

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()
        
        with logger.context(
            request_id=request.headers.get("X-Request-ID", "unknown"),
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown"
        ):
            try:
                response = await call_next(request)
                elapsed = time.time() - start_time
                logger.info(
                    f"Request completed",
                    status_code=response.status_code,
                    elapsed_seconds=elapsed
                )
                return response
            except Exception as e:
                logger.error(
                    f"Request failed",
                    error=e,
                    elapsed_seconds=time.time() - start_time
                )
                raise

app.add_middleware(LoggingMiddleware)
"""


# ============================================================================
# EXAMPLE 2: LLM Pool Detection Logging
# ============================================================================

@log_function_call(logger, log_level="DEBUG")
def detect_llm_with_logging():
    """Enhanced LLM detection with comprehensive logging."""
    with logger.context(operation="llm_detection"):
        try:
            logger.info("Starting LLM pool detection...")
            
            # Your detection code here
            detected = []
            
            logger.info(
                "LLM detection completed",
                count=len(detected),
                models=[m.get("name") for m in detected]
            )
            
            # Track metrics
            for model in detected:
                logger.track_metric(
                    "llm_detected",
                    1,
                    category="llm_discovery"
                )
            
            return detected
            
        except Exception as e:
            logger.error(
                "LLM detection failed",
                error=e,
                critical_operation=True
            )
            raise


# ============================================================================
# EXAMPLE 3: Build Process Monitoring
# ============================================================================

@log_function_call(logger)
def monitor_build(build_id: str, project_name: str):
    """Monitor a build with full logging and metrics."""
    import time
    
    build_start = time.time()
    
    with logger.context(
        build_id=build_id,
        project=project_name,
        operation="build"
    ):
        try:
            logger.info("Build started")
            
            stages = ["setup", "compile", "test", "bundle"]
            for stage in stages:
                stage_start = time.time()
                
                logger.info(f"Starting {stage}...")
                
                try:
                    # Your stage logic here
                    time.sleep(0.1)  # Simulate work
                    
                    elapsed = time.time() - stage_start
                    logger.info(
                        f"Stage {stage} completed",
                        stage=stage,
                        elapsed_seconds=elapsed
                    )
                    logger.track_metric(
                        f"build_{stage}_duration",
                        elapsed,
                        category="build_performance"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Stage {stage} failed",
                        error=e,
                        stage=stage
                    )
                    raise
            
            total_elapsed = time.time() - build_start
            logger.info(
                "Build completed successfully",
                total_seconds=total_elapsed
            )
            return True
            
        except Exception as e:
            logger.critical(
                "Build process failed",
                error=e,
                build_id=build_id
            )
            raise


# ============================================================================
# EXAMPLE 4: API Error Handler Decorator
# ============================================================================

def handle_api_errors(func):
    """Decorator to handle and log API errors gracefully."""
    from functools import wraps
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            logger.error(
                f"Validation error in {func.__name__}",
                error=e,
                error_category="validation"
            )
            return {"error": "Invalid input", "detail": str(e)}, 400
        except KeyError as e:
            logger.error(
                f"Missing key in {func.__name__}",
                error=e,
                error_category="missing_key"
            )
            return {"error": "Missing required field", "detail": str(e)}, 400
        except Exception as e:
            logger.critical(
                f"Unexpected error in {func.__name__}",
                error=e,
                error_category="unexpected"
            )
            return {"error": "Internal server error"}, 500
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(
                f"Validation error in {func.__name__}",
                error=e,
                error_category="validation"
            )
            return {"error": "Invalid input", "detail": str(e)}, 400
        except Exception as e:
            logger.critical(
                f"Unexpected error in {func.__name__}",
                error=e,
                error_category="unexpected"
            )
            return {"error": "Internal server error"}, 500
    
    # Return appropriate wrapper
    import inspect
    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper


# ============================================================================
# EXAMPLE 5: Performance Monitoring Context Manager
# ============================================================================

 


@contextmanager
def monitor_performance(operation_name: str, category: str = "general"):
    """Context manager for monitoring operation performance."""
    start_time = time.time()
    
    with logger.context(operation=operation_name):
        logger.info(f"Starting {operation_name}...")
        
        try:
            yield
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"{operation_name} failed",
                error=e,
                elapsed_seconds=elapsed
            )
            raise
        finally:
            elapsed = time.time() - start_time
            logger.info(
                f"{operation_name} completed",
                elapsed_seconds=elapsed
            )
            logger.track_metric(
                f"{operation_name}_duration",
                elapsed,
                category=f"{category}_performance"
            )


# ============================================================================
# EXAMPLE 6: External Service Logging
# ============================================================================

@log_function_call(logger)
def call_external_service(service_name: str, endpoint: str, payload: Dict[str, Any]):
    """Log external service calls with full context."""
    import requests
    
    with logger.context(
        service=service_name,
        endpoint=endpoint
    ):
        try:
            logger.info(f"Calling {service_name} service...")
            
            response = requests.post(
                endpoint,
                json=payload,
                timeout=10
            )
            
            logger.info(
                f"{service_name} call succeeded",
                status_code=response.status_code,
                response_size=len(response.content)
            )
            
            return response.json()
            
        except requests.Timeout:
            logger.error(
                f"{service_name} call timed out",
                error=TimeoutError("Service call exceeded timeout")
            )
            raise
        except requests.RequestException as e:
            logger.error(
                f"{service_name} call failed",
                error=e,
                service_error=True
            )
            raise


# ============================================================================
# EXAMPLE 7: Database Operation Logging
# ============================================================================

@log_function_call(logger, log_level="DEBUG")
def log_database_operation(operation: str, query: str, params: Dict = None):
    """Log database operations with query details."""
    with logger.context(
        db_operation=operation,
        has_params=params is not None
    ):
        try:
            logger.debug(
                f"Executing database {operation}",
                query=query,
                params_count=len(params) if params else 0
            )
            
            # Your database code here
            
            logger.debug(f"Database {operation} completed")
            
        except Exception as e:
            logger.error(
                f"Database {operation} failed",
                error=e,
                query=query
            )
            raise


# ============================================================================
# EXAMPLE 8: Accessing and Analyzing Logs
# ============================================================================

def analyze_logs():
    """Example: How to access and analyze collected metrics."""
    
    # Get all metrics
    all_metrics = logger.get_metrics()
    
    # Get specific category metrics
    perf_metrics = logger.get_metrics("performance")
    
    # Analyze build performance
    if "build_time" in perf_metrics:
        build_times = [
            m["value"] for m in perf_metrics["build_time"]
        ]
        avg_time = sum(build_times) / len(build_times)
        max_time = max(build_times)
        min_time = min(build_times)
        
        logger.info(
            "Build performance analysis",
            avg_time=avg_time,
            max_time=max_time,
            min_time=min_time,
            total_builds=len(build_times)
        )
    
    return all_metrics


# ============================================================================
# USAGE IN main.py
# ============================================================================

"""
# At the top of main.py:
from logger_utils import configure_logger, get_logger
import logging

# Configure logger
logger = configure_logger(
    name="q-ide-topdog",
    log_dir="./logs",
    level=logging.INFO
)

# Use in endpoints:
@app.get("/llm_pool")
def get_llm_pool():
    \"\"\"Return LLM pool report with logging.\"\"\"
    with logger.context(endpoint="/llm_pool"):
        try:
            logger.info("Fetching LLM pool...")
            from llm_pool import build_llm_report
            report = build_llm_report()
            logger.info(
                "LLM pool fetched",
                available_count=len(report.get("available", []))
            )
            return report
        except Exception as e:
            logger.error("Failed to fetch LLM pool", error=e)
            raise

# Use for monitoring:
@app.post("/build")
def start_build(config: BuildConfig):
    \"\"\"Start a build with full monitoring.\"\"\"
    return monitor_build(config.build_id, config.project_name)
"""


if __name__ == "__main__":
    
    print("Logger integration examples created successfully!")
    print("Check ./logs/ directory for log files:")
    print("  - q-ide-topdog.log (detailed)")
    print("  - q-ide-topdog.json (structured)")
