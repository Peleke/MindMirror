"""
Structured logging configuration for MindMirror celery-worker service.

This module provides structured logging with consistent fields for better
searchability in Cloud Logging console and easier debugging.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "celery-worker",
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
        
        # Add structured fields from record
        if hasattr(record, "structured_data"):
            log_entry.update(record.structured_data)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "getMessage", "exc_info", 
                          "exc_text", "stack_info", "structured_data"]:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured formatting."""
    logger = logging.getLogger(name)
    
    # Only add handler if it doesn't already have one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def log_with_context(logger: logging.Logger, level: int, message: str, 
                    **context: Any) -> None:
    """Log a message with structured context data."""
    record = logger.makeRecord(
        logger.name, level, "", 0, message, (), None
    )
    record.structured_data = context
    logger.handle(record)


def log_task_start(logger: logging.Logger, task_type: str, task_id: str, 
                  **context: Any) -> None:
    """Log the start of a task with structured data."""
    log_with_context(
        logger, logging.INFO, f"Task started: {task_type}",
        event_type="task_start",
        task_type=task_type,
        task_id=task_id,
        **context
    )


def log_task_success(logger: logging.Logger, task_type: str, task_id: str,
                    processing_time: float, **context: Any) -> None:
    """Log successful task completion with structured data."""
    log_with_context(
        logger, logging.INFO, f"Task completed successfully: {task_type}",
        event_type="task_success",
        task_type=task_type,
        task_id=task_id,
        processing_time=processing_time,
        **context
    )


def log_task_failure(logger: logging.Logger, task_type: str, task_id: str,
                    error: Exception, processing_time: float, **context: Any) -> None:
    """Log task failure with structured data."""
    log_with_context(
        logger, logging.ERROR, f"Task failed: {task_type}",
        event_type="task_failure",
        task_type=task_type,
        task_id=task_id,
        error_type=type(error).__name__,
        error_message=str(error),
        processing_time=processing_time,
        **context
    )


def log_pubsub_message_received(logger: logging.Logger, topic: str, 
                               message_id: str, **context: Any) -> None:
    """Log received Pub/Sub message with structured data."""
    log_with_context(
        logger, logging.INFO, f"Pub/Sub message received from topic: {topic}",
        event_type="pubsub_message_received",
        topic=topic,
        message_id=message_id,
        **context
    )


def log_pubsub_message_published(logger: logging.Logger, topic: str,
                                message_id: str, **context: Any) -> None:
    """Log published Pub/Sub message with structured data."""
    log_with_context(
        logger, logging.INFO, f"Pub/Sub message published to topic: {topic}",
        event_type="pubsub_message_published",
        topic=topic,
        message_id=message_id,
        **context
    )


def log_journal_indexing(logger: logging.Logger, entry_id: str, user_id: str,
                        tradition: str, success: bool, **context: Any) -> None:
    """Log journal indexing operation with structured data."""
    event_type = "journal_indexing_success" if success else "journal_indexing_failure"
    message = f"Journal indexing {'completed' if success else 'failed'} for entry: {entry_id}"
    
    log_with_context(
        logger, logging.INFO if success else logging.ERROR, message,
        event_type=event_type,
        entry_id=entry_id,
        user_id=user_id,
        tradition=tradition,
        **context
    )


def log_tradition_rebuild(logger: logging.Logger, tradition: str, success: bool,
                         processed_files: int = 0, **context: Any) -> None:
    """Log tradition rebuild operation with structured data."""
    event_type = "tradition_rebuild_success" if success else "tradition_rebuild_failure"
    message = f"Tradition rebuild {'completed' if success else 'failed'} for: {tradition}"
    
    log_with_context(
        logger, logging.INFO if success else logging.ERROR, message,
        event_type=event_type,
        tradition=tradition,
        processed_files=processed_files,
        **context
    )


def log_health_check(logger: logging.Logger, status: str, services: Dict[str, str],
                    **context: Any) -> None:
    """Log health check results with structured data."""
    log_with_context(
        logger, logging.INFO, f"Health check completed with status: {status}",
        event_type="health_check",
        status=status,
        services=services,
        **context
    )


def log_deprecated_usage(logger: logging.Logger, deprecated_feature: str,
                        recommended_alternative: str, **context: Any) -> None:
    """Log deprecated feature usage with structured data."""
    log_with_context(
        logger, logging.WARNING, f"Deprecated feature used: {deprecated_feature}",
        event_type="deprecated_usage",
        deprecated_feature=deprecated_feature,
        recommended_alternative=recommended_alternative,
        **context
    )


def log_performance(logger: logging.Logger, operation: str, duration: float,
                   **context: Any) -> None:
    """Log performance metrics with structured data."""
    log_with_context(
        logger, logging.INFO, f"Performance metric: {operation} took {duration:.3f}s",
        event_type="performance_metric",
        operation=operation,
        duration=duration,
        **context
    )


def log_error_with_context(logger: logging.Logger, error: Exception, 
                          context: str, **extra_context: Any) -> None:
    """Log error with rich context for debugging."""
    log_with_context(
        logger, logging.ERROR, f"Error in {context}: {str(error)}",
        event_type="error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context,
        **extra_context
    )


# Convenience function to generate task IDs
def generate_task_id() -> str:
    """Generate a unique task ID for tracking."""
    return str(uuid4())


# Structured logging decorator
def log_operation(operation_name: str):
    """Decorator to automatically log operation start/success/failure."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            task_id = generate_task_id()
            start_time = datetime.utcnow()
            
            log_task_start(logger, operation_name, task_id)
            
            try:
                result = func(*args, **kwargs)
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                log_task_success(logger, operation_name, task_id, processing_time)
                return result
            except Exception as e:
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                log_task_failure(logger, operation_name, task_id, e, processing_time)
                raise
        
        return wrapper
    return decorator 