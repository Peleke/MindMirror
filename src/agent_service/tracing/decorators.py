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


def trace_function(func=None, *, name=None, tags=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Optionally use name and tags here for tracing
            return f(*args, **kwargs)
        wrapper._trace_name = name
        wrapper._trace_tags = tags
        return wrapper
    if func is not None:
        return decorator(func)
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


def trace_langchain_operation(operation_name: str, tags: Optional[List[str]] = None):
    """
    Decorator to trace LangChain operations with specific tags.
    
    Args:
        operation_name: Name of the LangChain operation
        tags: List of tags to associate with the trace
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Add LangChain-specific tags
            langchain_tags = ["langchain", operation_name]
            if tags:
                langchain_tags.extend(tags)
            
            # Use the existing trace_function with LangChain tags
            traced_func = trace_function(name=operation_name, tags=langchain_tags)(func)
            return traced_func(*args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Add LangChain-specific tags
            langchain_tags = ["langchain", operation_name]
            if tags:
                langchain_tags.extend(tags)
            
            # Use the existing trace_function with LangChain tags
            traced_func = trace_function(name=operation_name, tags=langchain_tags)(func)
            return await traced_func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return wrapper
    
    return decorator


def trace_agent_workflow(workflow_name: str, tags: Optional[List[str]] = None):
    """
    Decorator to trace agent workflow operations.
    
    Args:
        workflow_name: Name of the agent workflow
        tags: List of tags to associate with the trace
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Add agent-specific tags
            agent_tags = ["agent", "workflow", workflow_name]
            if tags:
                agent_tags.extend(tags)
            
            # Use the existing trace_function with agent tags
            traced_func = trace_function(name=workflow_name, tags=agent_tags)(func)
            return traced_func(*args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Add agent-specific tags
            agent_tags = ["agent", "workflow", workflow_name]
            if tags:
                agent_tags.extend(agent_tags)
            
            # Use the existing trace_function with agent tags
            traced_func = trace_function(name=workflow_name, tags=agent_tags)(func)
            return await traced_func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return wrapper
    
    return decorator


def trace_runnable(runnable, name: str, tags: Optional[List[str]] = None):
    """
    Decorator to trace LangChain Runnables.
    
    Args:
        runnable: The LangChain runnable to trace
        name: Name for the trace
        tags: List of tags to associate with the trace
    """
    # Add runnable-specific tags
    runnable_tags = ["runnable", name]
    if tags:
        runnable_tags.extend(tags)
    
    # Create traced versions of invoke and ainvoke methods
    original_invoke = runnable.invoke
    original_ainvoke = getattr(runnable, 'ainvoke', None)
    
    @trace_function(name=name, tags=runnable_tags)
    def traced_invoke(input_data, config=None):
        return original_invoke(input_data, config)
    
    @trace_function(name=f"{name}_async", tags=runnable_tags)
    async def traced_ainvoke(input_data, config=None):
        if original_ainvoke:
            return await original_ainvoke(input_data, config)
        else:
            raise NotImplementedError("Async invoke not supported by this runnable")
    
    # Replace methods with traced versions
    runnable.invoke = traced_invoke
    if original_ainvoke:
        runnable.ainvoke = traced_ainvoke
    
    return runnable 