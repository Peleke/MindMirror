"""
Tracing decorators for monitoring and debugging.

This module provides decorators for tracing function execution,
performance monitoring, and error tracking.
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union
import uuid

logger = logging.getLogger(__name__)


def trace_function(
    operation_name: str,
    tags: Optional[List[str]] = None,
    capture_args: bool = True,
    capture_result: bool = False,
    log_level: str = "INFO"
):
    """
    Decorator to trace function execution with timing and metadata.
    
    Args:
        operation_name: Name of the operation being traced
        tags: List of tags to associate with the trace
        capture_args: Whether to capture function arguments
        capture_result: Whether to capture function result
        log_level: Logging level for trace messages
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Prepare trace metadata
            trace_data = {
                "trace_id": trace_id,
                "operation": operation_name,
                "function": f"{func.__module__}.{func.__name__}",
                "tags": tags or [],
                "start_time": start_time,
            }
            
            if capture_args:
                trace_data["args"] = str(args)
                trace_data["kwargs"] = str(kwargs)
            
            # Log start of execution
            log_message = f"TRACE_START [{trace_id}] {operation_name}"
            if tags:
                log_message += f" [tags: {', '.join(tags)}]"
            
            getattr(logger, log_level.lower())(log_message)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                trace_data["execution_time"] = execution_time
                trace_data["status"] = "success"
                
                if capture_result:
                    trace_data["result"] = str(result)
                
                # Log successful completion
                log_message = f"TRACE_SUCCESS [{trace_id}] {operation_name} completed in {execution_time:.3f}s"
                getattr(logger, log_level.lower())(log_message)
                
                return result
                
            except Exception as e:
                # Calculate execution time
                execution_time = time.time() - start_time
                trace_data["execution_time"] = execution_time
                trace_data["status"] = "error"
                trace_data["error"] = str(e)
                trace_data["error_type"] = type(e).__name__
                
                # Log error
                log_message = f"TRACE_ERROR [{trace_id}] {operation_name} failed after {execution_time:.3f}s: {e}"
                getattr(logger, log_level.lower())(log_message)
                
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Prepare trace metadata
            trace_data = {
                "trace_id": trace_id,
                "operation": operation_name,
                "function": f"{func.__module__}.{func.__name__}",
                "tags": tags or [],
                "start_time": start_time,
                "async": True,
            }
            
            if capture_args:
                trace_data["args"] = str(args)
                trace_data["kwargs"] = str(kwargs)
            
            # Log start of execution
            log_message = f"TRACE_START [{trace_id}] {operation_name} (async)"
            if tags:
                log_message += f" [tags: {', '.join(tags)}]"
            
            getattr(logger, log_level.lower())(log_message)
            
            try:
                # Execute the async function
                result = await func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                trace_data["execution_time"] = execution_time
                trace_data["status"] = "success"
                
                if capture_result:
                    trace_data["result"] = str(result)
                
                # Log successful completion
                log_message = f"TRACE_SUCCESS [{trace_id}] {operation_name} (async) completed in {execution_time:.3f}s"
                getattr(logger, log_level.lower())(log_message)
                
                return result
                
            except Exception as e:
                # Calculate execution time
                execution_time = time.time() - start_time
                trace_data["execution_time"] = execution_time
                trace_data["status"] = "error"
                trace_data["error"] = str(e)
                trace_data["error_type"] = type(e).__name__
                
                # Log error
                log_message = f"TRACE_ERROR [{trace_id}] {operation_name} (async) failed after {execution_time:.3f}s: {e}"
                getattr(logger, log_level.lower())(log_message)
                
                raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return wrapper
    
    return decorator


def trace_performance(threshold_ms: float = 1000.0):
    """
    Decorator to trace function performance and warn on slow execution.
    
    Args:
        threshold_ms: Threshold in milliseconds to trigger performance warning
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                if execution_time_ms > threshold_ms:
                    logger.warning(
                        f"PERFORMANCE_WARNING: {func.__name__} took {execution_time_ms:.2f}ms "
                        f"(threshold: {threshold_ms:.2f}ms)"
                    )
                else:
                    logger.debug(
                        f"PERFORMANCE_OK: {func.__name__} took {execution_time_ms:.2f}ms"
                    )
                
                return result
                
            except Exception as e:
                execution_time_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"PERFORMANCE_ERROR: {func.__name__} failed after {execution_time_ms:.2f}ms: {e}"
                )
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                if execution_time_ms > threshold_ms:
                    logger.warning(
                        f"PERFORMANCE_WARNING: {func.__name__} (async) took {execution_time_ms:.2f}ms "
                        f"(threshold: {threshold_ms:.2f}ms)"
                    )
                else:
                    logger.debug(
                        f"PERFORMANCE_OK: {func.__name__} (async) took {execution_time_ms:.2f}ms"
                    )
                
                return result
                
            except Exception as e:
                execution_time_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"PERFORMANCE_ERROR: {func.__name__} (async) failed after {execution_time_ms:.2f}ms: {e}"
                )
                raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return wrapper
    
    return decorator


def trace_errors(
    reraise: bool = True,
    log_full_traceback: bool = True,
    error_types: Optional[List[type]] = None
):
    """
    Decorator to trace and handle errors with detailed logging.
    
    Args:
        reraise: Whether to re-raise the exception after logging
        log_full_traceback: Whether to log the full traceback
        error_types: List of exception types to catch (None for all)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check if we should catch this error type
                if error_types and not any(isinstance(e, error_type) for error_type in error_types):
                    raise
                
                logger.error(f"ERROR in {func.__name__}: {e}")
                
                if log_full_traceback:
                    import traceback
                    logger.error(f"Full traceback:\n{traceback.format_exc()}")
                
                if reraise:
                    raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Check if we should catch this error type
                if error_types and not any(isinstance(e, error_type) for error_type in error_types):
                    raise
                
                logger.error(f"ERROR in {func.__name__} (async): {e}")
                
                if log_full_traceback:
                    import traceback
                    logger.error(f"Full traceback:\n{traceback.format_exc()}")
                
                if reraise:
                    raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return wrapper
    
    return decorator 