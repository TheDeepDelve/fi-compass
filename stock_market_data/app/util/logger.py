import logging
import structlog
from typing import Any, Dict
import sys
from app.config import settings

def setup_logging():
    """Configure structured logging for the application"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        stream=sys.stdout,
    )
    
    # Reduce noise from Google Cloud libraries
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        return get_logger(self.__class__.__name__)

def log_api_call(method: str, url: str, status_code: int, response_time: float, **kwargs):
    """Log API call details"""
    logger = get_logger("api_calls")
    logger.info(
        "API call completed",
        method=method,
        url=url,
        status_code=status_code,
        response_time_ms=round(response_time * 1000, 2),
        **kwargs
    )

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context"""
    logger = get_logger("errors")
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )