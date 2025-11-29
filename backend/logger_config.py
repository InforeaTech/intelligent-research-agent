"""
Logging configuration module for the Intelligent Research Agent.

Provides structured logging with:
- Request correlation IDs
- Performance timing
- JSON formatting
- Configurable log levels
"""

import logging
import json
import time
import functools
from datetime import datetime
from contextvars import ContextVar
from typing import Any, Dict, Optional
import os

# Context variable for request correlation
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class RequestIDFilter(logging.Filter):
    """Filter to add request_id to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to record."""
        record.request_id = request_id_var.get() or 'N/A'
        return True


def setup_logging(log_level: str = None, log_format: str = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ('json' or 'text')
    """
    # Get configuration from environment or use defaults
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
    log_format = log_format or os.getenv('LOG_FORMAT', 'json')
    log_file = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Choose formatter
    if log_format == 'json':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIDFilter())
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.warning(f"Could not create file handler: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """
    Set the request ID for the current context.
    
    Args:
        request_id: Request correlation ID
    """
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """
    Get the current request ID.
    
    Returns:
        Current request ID or None
    """
    return request_id_var.get()


def log_performance(logger: logging.Logger = None):
    """
    Decorator to log function performance.
    
    Args:
        logger: Logger instance (optional, will create one if not provided)
    
    Usage:
        @log_performance()
        def my_function():
            pass
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"{func.__name__} completed successfully",
                    extra={'extra_data': {'duration_ms': round(duration_ms, 2)}}
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed",
                    extra={'extra_data': {'duration_ms': round(duration_ms, 2), 'error': str(e)}},
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


def log_execution_time(func_name: str, duration_ms: float, logger: logging.Logger, **extra):
    """
    Log execution time for a function.
    
    Args:
        func_name: Name of the function
        duration_ms: Duration in milliseconds
        logger: Logger instance
        **extra: Additional data to log
    """
    log_data = {'duration_ms': round(duration_ms, 2)}
    log_data.update(extra)
    logger.info(f"{func_name} completed", extra={'extra_data': log_data})


# Initialize logging on module import
setup_logging()
