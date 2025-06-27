"""
Tracing decorators for monitoring and debugging.

This module provides decorators for tracing function execution,
performance monitoring, and error tracking using LangSmith.
"""

import functools
import logging
import time
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
import uuid

import langsmith

logger = logging.getLogger(__name__)


def trace_function(func=None, *, name=None, tags=None):
    """
    Decorator to trace function execution using LangSmith.
    
    Args:
        func: Function to trace
        name: Name for the trace (defaults to function name)
        tags: List of tags to associate with the trace
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            trace_name = name or f.__name__
            trace_tags = tags or []
            
            # Get LangSmith client
            client = langsmith.Client()
            
            # Start trace
            with client.trace(
                name=trace_name,
                tags=trace_tags,
                inputs={"args": str(args), "kwargs": str(kwargs)}
            ) as trace:
                try:
                    result = f(*args, **kwargs)
                    
                    # Add success metadata
                    trace.add_metadata({
                        "result_type": type(result).__name__,
                        "success": True,
                    })
                    
                    return result
                    
                except Exception as e:
                    # Add error metadata
                    trace.add_metadata({
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "success": False,
                    })
                    raise
        
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            trace_name = name or f.__name__
            trace_tags = tags or []
            
            # Get LangSmith client
            client = langsmith.Client()
            
            # Start trace
            with client.trace(
                name=trace_name,
                tags=trace_tags,
                inputs={"args": str(args), "kwargs": str(kwargs)}
            ) as trace:
                try:
                    result = await f(*args, **kwargs)
                    
                    # Add success metadata
                    trace.add_metadata({
                        "result_type": type(result).__name__,
                        "success": True,
                    })
                    
                    return result
                    
                except Exception as e:
                    # Add error metadata
                    trace.add_metadata({
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "success": False,
                    })
                    raise
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(f):
            return async_wrapper
        else:
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
        if inspect.iscoroutinefunction(func):
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
        if inspect.iscoroutinefunction(func):
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
        # Add LangChain-specific tags
        langchain_tags = ["langchain", operation_name]
        if tags:
            langchain_tags.extend(tags)
        
        # Use the existing trace_function with LangChain tags
        traced_func = trace_function(name=operation_name, tags=langchain_tags)(func)
        return traced_func
    
    return decorator


def trace_agent_workflow(workflow_name: str, tags: Optional[List[str]] = None):
    """
    Decorator to trace agent workflows with specific tags.
    
    Args:
        workflow_name: Name of the agent workflow
        tags: List of tags to associate with the trace
    """
    def decorator(func: Callable) -> Callable:
        # Add agent-specific tags
        agent_tags = ["agent", "workflow", workflow_name]
        if tags:
            agent_tags.extend(tags)
        
        # Use the existing trace_function with agent tags
        traced_func = trace_function(name=workflow_name, tags=agent_tags)(func)
        return traced_func
    
    return decorator


def trace_runnable(runnable, name: str, tags: Optional[List[str]] = None):
    """
    Create a traced version of a LangChain Runnable.
    
    Args:
        runnable: The LangChain Runnable to trace
        name: Name for the trace
        tags: List of tags to associate with the trace
    """
    runnable_tags = ["runnable", name]
    if tags:
        runnable_tags.extend(tags)
    
    @trace_function(name=name, tags=runnable_tags)
    def traced_invoke(input_data, config=None):
        return runnable.invoke(input_data, config)
    
    @trace_function(name=f"{name}_async", tags=runnable_tags)
    async def traced_ainvoke(input_data, config=None):
        return await runnable.ainvoke(input_data, config)
    
    # Create a wrapper that preserves the original runnable interface
    class TracedRunnable:
        def __init__(self, original_runnable):
            self._runnable = original_runnable
        
        def invoke(self, input_data, config=None):
            return traced_invoke(input_data, config)
        
        async def ainvoke(self, input_data, config=None):
            return await traced_ainvoke(input_data, config)
    
    return TracedRunnable(runnable)


# Export langsmith for tests
langsmith = langsmith 