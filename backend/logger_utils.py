"""
Robust centralized logging utility for Q-IDE TopDog.

Features:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output with rotation
- Full error context capture (stack traces, variables, system info)
- Structured JSON logging for analysis
- Performance metrics tracking
- Request/response logging for API calls
- LLM operation tracking
- Build process monitoring
"""

import logging
import logging.handlers
import json
import traceback
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, TYPE_CHECKING
import threading
from functools import wraps
import time
import platform
import psutil
from contextlib import contextmanager
import os

# Try to import asyncio for async support (optional) with mypy-friendly typing
if TYPE_CHECKING:
    pass  # pragma: no cover
try:
    import asyncio  # type: ignore[no-redef]
except ImportError:  # pragma: no cover - platforms without asyncio
    asyncio = None  # type: ignore[assignment]


class ContextualLogger:
    """Main logger class with context awareness and full error capture."""
    
    def __init__(self, name: str = "q-ide", log_dir: Optional[str] = None, level: int = logging.INFO):
        """
        Initialize the logger.
        
        Args:
            name: Logger name (default: "q-ide")
            log_dir: Directory for log files (default: ./logs)
            level: Default log level
        """
        self.name = name
        self.log_dir = Path(log_dir or "./logs")
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fall back to /tmp when filesystem is read-only
            try:
                self.log_dir = Path("/tmp/logs")
                self.log_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                # As a last resort, proceed without ensuring log dir (stdout-only mode may be enabled)
                pass
        
        # Main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # Context stack for nested operations
        self._context_stack: List[Dict[str, Any]] = []
        self._context_lock = threading.Lock()
        
        # Performance tracking
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self._metrics_lock = threading.Lock()
        
        # Setup handlers
        self._setup_handlers(level)
    
    def _setup_handlers(self, level: int):
        """Setup file and console handlers with rotation."""
        log_to_stdout_only = str(os.getenv("LOG_TO_STDOUT_ONLY", "false")).lower() in ("1", "true", "yes")
        # Console handler - brief format
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        if log_to_stdout_only:
            # Skip file/JSON handlers when stdout-only mode is enabled
            return
        
        # File handler - detailed format with rotation
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG in file
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s [%(threadName)s:%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # JSON handler for structured logging
        json_log_file = self.log_dir / f"{self.name}.json"
        self.json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=3
        )
        self.json_handler.setLevel(logging.INFO)
        json_handler = JSONFormatter()
        self.json_handler.setFormatter(json_handler)
        self.logger.addHandler(self.json_handler)
    
    @contextmanager
    def context(self, **kwargs):
        """
        Context manager for adding nested context to logs.
        
        Usage:
            with logger.context(user_id="123", action="build"):
                logger.info("Building project...")
        """
        with self._context_lock:
            self._context_stack.append(kwargs)
        try:
            yield
        finally:
            with self._context_lock:
                self._context_stack.pop()
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current context stack."""
        with self._context_lock:
            combined = {}
            for ctx in self._context_stack:
                combined.update(ctx)
            return combined
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Capture system information for error reports."""
        try:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "platform": platform.platform(),
                "python_version": sys.version,
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "process_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
            }
        except Exception as e:
            return {"system_info_error": str(e)}
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(f"{message} | {self._format_context()}", extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(f"{message} | {self._format_context()}", extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(f"{message} | {self._format_context()}", extra=kwargs)
    
    def error(self, message: str, error: Optional[BaseException] = None, **kwargs):
        """
        Log error with full context and stack trace.
        
        Args:
            message: Error message
            error: Exception object (uses current exception if None)
            **kwargs: Additional context
        """
        if error is None:
            err_candidate = sys.exc_info()[1]
            if isinstance(err_candidate, BaseException):
                error = err_candidate
        
        # Build comprehensive error report
        error_data = {
            "message": message,
            "error_type": error.__class__.__name__ if error else "Unknown",
            "error_message": str(error) if error else None,
            "stack_trace": traceback.format_exc() if error else None,
            "context": self._get_context(),
            "system_info": self._get_system_info(),
            **kwargs
        }
        
        # Log as structured JSON
        self.logger.error(
            json.dumps(error_data, indent=2, default=str),
            extra={"full_context": error_data}
        )
    
    def critical(self, message: str, error: Optional[BaseException] = None, **kwargs):
        """
        Log critical error with full system state.
        
        Args:
            message: Error message
            error: Exception object
            **kwargs: Additional context
        """
        if error is None:
            err_candidate = sys.exc_info()[1]
            if isinstance(err_candidate, BaseException):
                error = err_candidate
        
        error_data = {
            "message": message,
            "error_type": error.__class__.__name__ if error else "Unknown",
            "error_message": str(error) if error else None,
            "stack_trace": traceback.format_exc() if error else None,
            "context": self._get_context(),
            "system_info": self._get_system_info(),
            "thread_name": threading.current_thread().name,
            **kwargs
        }
        
        self.logger.critical(
            json.dumps(error_data, indent=2, default=str),
            extra={"full_context": error_data}
        )
    
    def track_metric(self, metric_name: str, value: Any, category: str = "general"):
        """Track performance metrics."""
        with self._metrics_lock:
            if category not in self.metrics:
                self.metrics[category] = {}
            if metric_name not in self.metrics[category]:
                self.metrics[category][metric_name] = []
            self.metrics[category][metric_name].append({
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_metrics(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve tracked metrics."""
        with self._metrics_lock:
            if category:
                return self.metrics.get(category, {})
            return self.metrics
    
    def _format_context(self) -> str:
        """Format current context for inline logging."""
        ctx = self._get_context()
        if not ctx:
            return ""
        items = [f"{k}={v}" for k, v in ctx.items()]
        return f"[{'; '.join(items)}]"


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Include extra context if available
        if hasattr(record, "full_context"):
            log_data["context"] = record.full_context
        
        # Include exception info if present
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_type is not None:
                log_data["exception"] = {
                    "type": exc_type.__name__,
                    "value": str(exc_value),
                    "traceback": traceback.format_exception(exc_type, exc_value, exc_tb)
                }
        
        return json.dumps(log_data, default=str)


def log_function_call(logger: ContextualLogger, log_level: str = "INFO"):
    """
    Decorator to automatically log function calls with parameters and results.
    
    Usage:
        @log_function_call(logger)
        def my_function(x, y):
            return x + y
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            # Log function entry
            log_func = getattr(logger, log_level.lower())
            log_func(
                f"Calling {func_name}",
                function=func_name,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                log_func(
                    f"Completed {func_name}",
                    function=func_name,
                    elapsed_seconds=elapsed,
                    result_type=type(result).__name__
                )
                logger.track_metric(f"{func_name}_duration", elapsed, "performance")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Failed in {func_name}",
                    error=e,
                    function=func_name,
                    elapsed_seconds=elapsed
                )
                raise
        
        return wrapper
    return decorator


def log_api_call(logger: ContextualLogger):
    """
    Decorator for logging API calls with request/response details.
    
    Usage:
        @log_api_call(logger)
        async def get_user(user_id: str):
            return await fetch_user(user_id)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _log_api_impl(logger, func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _log_api_impl_sync(logger, func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def _log_api_impl_sync(logger, func, *args, **kwargs):
    """Synchronous API logging implementation."""
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(
            f"API {func.__name__} succeeded",
            function=func.__name__,
            elapsed_seconds=elapsed
        )
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"API {func.__name__} failed",
            error=e,
            function=func.__name__,
            elapsed_seconds=elapsed
        )
        raise


async def _log_api_impl(logger, func, *args, **kwargs):
    """Async API logging implementation."""
    start_time = time.time()
    try:
        result = await func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(
            f"API {func.__name__} succeeded",
            function=func.__name__,
            elapsed_seconds=elapsed
        )
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"API {func.__name__} failed",
            error=e,
            function=func.__name__,
            elapsed_seconds=elapsed
        )
        raise


# Global logger instance
_global_logger: Optional[ContextualLogger] = None


def get_logger(name: str = "q-ide", log_dir: Optional[str] = None) -> ContextualLogger:
    """
    Get or create the global logger instance.
    
    Args:
        name: Logger name
        log_dir: Log directory path
    
    Returns:
        ContextualLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = ContextualLogger(name, log_dir)
    return _global_logger


def configure_logger(
    name: str = "q-ide",
    log_dir: Optional[str] = None,
    level: int = logging.INFO
) -> ContextualLogger:
    """
    Configure and return the global logger instance.
    
    Args:
        name: Logger name
        log_dir: Log directory path
        level: Logging level
    
    Returns:
        Configured ContextualLogger instance
    """
    global _global_logger
    _global_logger = ContextualLogger(name, log_dir, level)
    return _global_logger


if __name__ == "__main__":
    # Example usage
    logger = configure_logger(level=logging.DEBUG)
    
    # Simple logging
    logger.info("Application started")
    
    # Contextual logging
    with logger.context(user_id="user123", action="build"):
        logger.info("Building project...")
        
        try:
            1 / 0
        except Exception as e:
            logger.error("Build failed", error=e)
    
    # Function decorator
    @log_function_call(logger)
    def process_data(data: list):
        time.sleep(0.1)
        return sum(data)
    
    result = process_data([1, 2, 3])
    
    # Metrics tracking
    logger.track_metric("build_time", 2.5, "performance")
    logger.track_metric("build_time", 2.3, "performance")
    
    print("\nMetrics:", json.dumps(logger.get_metrics(), indent=2, default=str))
