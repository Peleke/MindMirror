"""
Message processing utilities for Pub/Sub message handling.

This module provides utilities for processing Pub/Sub messages with
proper error handling, retry logic, and dead letter queue support.
"""

import logging
import time
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator to retry a function on failure with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class MessageProcessor:
    """Base class for processing Pub/Sub messages with error handling."""
    
    def __init__(self, max_retries: int = 3):
        """Initialize the message processor.
        
        Args:
            max_retries: Maximum number of retry attempts for failed processing
        """
        self.max_retries = max_retries
    
    def process_message(
        self,
        message_data: Dict[str, Any],
        processor_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Process a message with retry logic and error handling.
        
        Args:
            message_data: The message data to process
            processor_func: Function to call for processing
            *args: Additional arguments for the processor function
            **kwargs: Additional keyword arguments for the processor function
            
        Returns:
            Dict with processing result and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing message: {message_data.get('task_type', 'unknown')}")
            
            # Apply retry decorator to the processor function
            retry_processor = retry_on_failure(
                max_retries=self.max_retries,
                exceptions=(Exception,)
            )(processor_func)
            
            # Process the message
            result = retry_processor(*args, **kwargs)
            
            processing_time = time.time() - start_time
            
            return {
                "status": "success",
                "result": result,
                "processing_time": processing_time,
                "message_id": message_data.get("message_id"),
                "task_type": message_data.get("task_type")
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            logger.error(
                f"Failed to process message after {self.max_retries + 1} attempts: {e}",
                exc_info=True
            )
            
            return {
                "status": "error",
                "error": str(e),
                "processing_time": processing_time,
                "message_id": message_data.get("message_id"),
                "task_type": message_data.get("task_type"),
                "retry_count": self.max_retries
            }


def should_retry_message(error: Exception, retry_count: int, max_retries: int) -> bool:
    """Determine if a message should be retried based on the error and retry count.
    
    Args:
        error: The exception that occurred
        retry_count: Current number of retry attempts
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if the message should be retried, False otherwise
    """
    if retry_count >= max_retries:
        return False
    
    # Don't retry on certain types of errors
    non_retryable_errors = (
        ValueError,
        TypeError,
        AttributeError,
        KeyError,
        IndexError,
    )
    
    if isinstance(error, non_retryable_errors):
        return False
    
    return True


def log_message_processing(
    message_data: Dict[str, Any],
    result: Dict[str, Any],
    processing_time: float
):
    """Log message processing results.
    
    Args:
        message_data: The original message data
        result: The processing result
        processing_time: Time taken to process the message
    """
    task_type = message_data.get("task_type", "unknown")
    message_id = message_data.get("message_id", "unknown")
    
    if result.get("status") == "success":
        logger.info(
            f"Successfully processed {task_type} message {message_id} "
            f"in {processing_time:.2f}s"
        )
    else:
        logger.error(
            f"Failed to process {task_type} message {message_id} "
            f"in {processing_time:.2f}s: {result.get('error')}"
        ) 