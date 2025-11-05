# 📊 Centralized Logging System - Top Dog TopDog

## Overview

A robust, production-grade centralized logging utility that captures errors with full context, system information, performance metrics, and structured logging for analysis.

## Features

✅ **Multi-level logging** - DEBUG, INFO, WARNING, ERROR, CRITICAL
✅ **File rotation** - Automatic log rotation with 5 backups (10 MB each)
✅ **Console & file output** - Real-time console + detailed file logs
✅ **JSON structured logging** - Machine-readable logs for analysis
✅ **Full error context** - Stack traces, system info, thread details
✅ **Performance metrics** - Track operation durations, success rates
✅ **Contextual logging** - Nested context for complex operations
✅ **Decorators** - Easy integration with functions and APIs
✅ **Thread-safe** - Locks for multi-threaded environments

## Architecture

```
logger_utils.py
├── ContextualLogger (main class)
│   ├── Multi-handler setup (console, file, JSON)
│   ├── Context stack for nested operations
│   ├── Metrics tracking with categories
│   └── Full error reporting
├── JSONFormatter (structured logging)
├── Decorators
│   ├── @log_function_call
│   └── @log_api_call (async support)
└── Global logger instance
```

## Files

### 1. `backend/logger_utils.py`
Main logging utility module with full implementation.

**Key Classes:**
- `ContextualLogger` - Main logger with context management
- `JSONFormatter` - Structured JSON formatting

**Key Functions:**
- `configure_logger()` - Initialize logger
- `get_logger()` - Get global logger instance
- `log_function_call()` - Decorator for function logging
- `log_api_call()` - Decorator for API logging

### 2. `backend/logger_integration.py`
Integration examples for different components.

**Includes:**
- FastAPI middleware example
- LLM pool detection logging
- Build process monitoring
- Error handling decorators
- Performance monitoring
- External service calls
- Database operations

## Quick Start

### Basic Setup

```python
from logger_utils import configure_logger
import logging

# Initialize logger
logger = configure_logger(
    name="my-app",
    log_dir="./logs",
    level=logging.INFO
)

# Simple logging
logger.info("Application started")
logger.warning("Deprecation notice")
logger.error("Operation failed", error=exception_obj)
```

### With Context

```python
# Add context to all logs within this block
with logger.context(user_id="123", action="deploy"):
    logger.info("Starting deployment...")
    try:
        deploy_app()
        logger.info("Deployment succeeded")
    except Exception as e:
        logger.error("Deployment failed", error=e)
```

### Function Decorators

```python
from logger_utils import log_function_call

@log_function_call(logger, log_level="INFO")
def process_data(data: list):
    """Automatically logs function entry, exit, duration, and errors."""
    return sum(data)
```

### Performance Monitoring

```python
from logger_utils import get_logger

logger = get_logger()

# Track custom metrics
logger.track_metric("build_duration", 2.5, category="performance")
logger.track_metric("api_response_time", 0.125, category="api")

# Retrieve metrics
metrics = logger.get_metrics("performance")
api_metrics = logger.get_metrics("api")
```

## Log Output Examples

### Console Output (Brief)
```
2025-10-26 08:05:25 [INFO] Top Dog: Application started | [user_id=123; action=build]
2025-10-26 08:05:25 [ERROR] Top Dog: Build failed | [user_id=123; action=build]
```

### File Output (Detailed)
```
2025-10-26 08:05:25 [INFO] Top Dog [Thread-1:process_data:145] Processing data | [user_id=123]
2025-10-26 08:05:26 [ERROR] Top Dog [MainThread:main:156] Unexpected error | [user_id=123]
  File "./app.py", line 156, in main
    result = process_data(items)
```

### JSON Log Output (Structured)
```json
{
  "timestamp": "2025-10-26T12:05:25.123456",
  "level": "ERROR",
  "logger": "Top Dog",
  "message": "Build failed",
  "module": "build",
  "function": "execute_build",
  "line": 145,
  "context": {
    "user_id": "123",
    "action": "build",
    "project": "topdog"
  },
  "exception": {
    "type": "RuntimeError",
    "value": "Compilation failed",
    "traceback": ["...full traceback..."]
  },
  "system_info": {
    "timestamp": "2025-10-26T12:05:25.123456",
    "platform": "Windows-10-10.0.26100",
    "python_version": "3.11.9",
    "cpu_percent": 45.2,
    "memory_percent": 62.5,
    "process_memory_mb": 125.5
  }
}
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from logger_utils import configure_logger

app = FastAPI()
logger = configure_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        with logger.context(
            request_id=request.headers.get("X-Request-ID"),
            method=request.method,
            path=request.url.path
        ):
            response = await call_next(request)
            return response

app.add_middleware(LoggingMiddleware)
```

### Build Monitoring

```python
@log_function_call(logger)
def build_project(project_id: str):
    with logger.context(project_id=project_id, operation="build"):
        logger.info("Build started")
        
        try:
            compile_stage()
            test_stage()
            bundle_stage()
            
            logger.info("Build completed successfully")
        except Exception as e:
            logger.critical("Build failed", error=e)
            raise
```

### Error Handling

```python
def handle_endpoint_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            logger.error("Validation failed", error=e)
            return {"error": "Invalid input"}, 400
        except Exception as e:
            logger.critical("Unexpected error", error=e)
            return {"error": "Server error"}, 500
    return wrapper

@app.post("/api/process")
@handle_endpoint_errors
async def process_request(data: dict):
    return {"result": process_data(data)}
```

## Log Files Location

All logs are stored in `./logs/` directory:

```
logs/
├── Top Dog-topdog.log          # Detailed rotating log (10 MB max, 5 backups)
├── Top Dog-topdog.log.1        # Rotated backups
├── Top Dog-topdog.log.2
├── Top Dog-topdog.json         # Structured JSON logs
└── Top Dog-topdog.json.1       # JSON backups
```

## Performance Tracking

Track and analyze metrics across your application:

```python
# Track metric
logger.track_metric("api_response_time", 0.245, category="api")
logger.track_metric("build_duration", 2.5, category="builds")

# Get all metrics
all_metrics = logger.get_metrics()

# Analyze
builds = logger.get_metrics("builds")
for metric in builds["build_duration"]:
    print(f"Build took {metric['value']} seconds")
```

## Context Management

Nested contexts are merged automatically:

```python
with logger.context(user="alice"):
    logger.info("User context")  # [user=alice]
    
    with logger.context(action="build"):
        logger.info("Build context")  # [user=alice; action=build]
        
        with logger.context(stage="compile"):
            logger.info("Compile context")  # [user=alice; action=build; stage=compile]
```

## System Information Captured

Each error log includes:

- **Timestamp** - UTC timestamp
- **Platform** - OS and version
- **Python Version** - Runtime version
- **CPU Percent** - Current CPU usage
- **Memory Percent** - System memory usage
- **Process Memory** - App memory in MB
- **Stack Trace** - Full exception traceback
- **Thread Info** - Thread name and details

## Best Practices

### ✅ DO:

1. **Initialize early** - Configure logger at app startup
2. **Use context** - Wrap related operations with context
3. **Log levels** - Use appropriate levels (DEBUG < INFO < WARNING < ERROR < CRITICAL)
4. **Include metadata** - Pass relevant context to logs
5. **Track metrics** - Monitor key operations
6. **Use decorators** - For automatic function logging
7. **Thread-safe** - Logger handles threading automatically

### ❌ DON'T:

1. **Create multiple instances** - Use `get_logger()` for global instance
2. **Log sensitive data** - Be careful with passwords, tokens, API keys
3. **Over-log** - Too much logging reduces performance
4. **Ignore errors** - Always log before re-raising
5. **Hardcode log levels** - Use environment variables

## Performance Considerations

- **Console logging** - Minimal overhead, async-safe
- **File rotation** - Automatic when files reach 10 MB
- **JSON logging** - Slightly slower but worth it for analysis
- **Metrics** - Thread-safe, minimal memory impact
- **Context stack** - Per-thread, minimal overhead

## Troubleshooting

### Logs not appearing?
```python
# Ensure logger is initialized
logger = configure_logger(level=logging.DEBUG)

# Check log directory exists
import os
print(os.path.exists("./logs"))
```

### Too many log files?
```python
# Logs rotate automatically at 10 MB with 5 backups
# Clean old logs: python -c "
import os, glob
for f in glob.glob('logs/*.log.*'):
    os.remove(f)
"
```

### Performance issues?
```python
# Reduce console logging level
logger = configure_logger(level=logging.WARNING)

# Or disable specific handlers
# (Advanced: modify _setup_handlers method)
```

## API Reference

### ContextualLogger Methods

```python
# Basic logging
logger.debug(message, **kwargs)
logger.info(message, **kwargs)
logger.warning(message, **kwargs)
logger.error(message, error=None, **kwargs)
logger.critical(message, error=None, **kwargs)

# Context management
with logger.context(**context_dict):
    logger.info("message")

# Metrics
logger.track_metric(name, value, category="general")
metrics = logger.get_metrics(category=None)
```

### Decorators

```python
@log_function_call(logger, log_level="INFO")
def my_function():
    pass

@log_api_call(logger)
async def my_api():
    pass
```

## Future Enhancements

- [ ] Sentry/Rollbar integration
- [ ] Elasticsearch export
- [ ] Custom formatters
- [ ] Log filtering rules
- [ ] Remote syslog support
- [ ] Distributed tracing (OpenTelemetry)

---

**Status**: ✅ Production Ready  
**Last Updated**: 2025-10-26  
**Version**: 1.0.0
