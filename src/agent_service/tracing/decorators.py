"""
Tracing decorators for automatic observability of agent operations.

This module provides decorators that automatically trace function calls,
LangChain operations, and agent workflows for debugging and evaluation.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import langsmith
from langchain_core.runnables import Runnable
from langsmith import Client

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def trace_function(
    name: Optional[str] = None,
    tags: Optional[list[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator to trace function execution with LangSmith.
    
    Args:
        name: Custom name for the trace (defaults to function name)
        tags: Tags to associate with the trace
        metadata: Additional metadata for the trace
    
    Returns:
        Decorated function with tracing
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            trace_name = name or f"{func.__module__}.{func.__name__}"
            
            try:
                # Use LangSmith's tracing API directly
                with langsmith.trace(
                    name=trace_name,
                    tags=tags or [],
                    metadata=metadata or {},
                ) as trace:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Add result metadata
                    trace.add_metadata({
                        "result_type": type(result).__name__,
                        "success": True,
                    })
                    
                    return result
                    
            except Exception as e:
                # Log the error and re-raise
                logger.error(f"Error in traced function {trace_name}: {e}")
                
                # Add error metadata if we have a trace
                try:
                    with langsmith.trace(
                        name=trace_name,
                        tags=tags or [],
                        metadata=metadata or {},
                    ) as trace:
                        trace.add_metadata({
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "success": False,
                        })
                except Exception:
                    # If tracing fails, just log and continue
                    pass
                
                raise
        
        return cast(F, wrapper)
    
    return decorator


def trace_langchain_operation(
    operation_name: str,
    tags: Optional[list[str]] = None,
) -> Callable[[F], F]:
    """
    Decorator specifically for LangChain operations.
    
    Args:
        operation_name: Name of the LangChain operation
        tags: Tags to associate with the trace
    
    Returns:
        Decorated function with LangChain-specific tracing
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Add LangChain-specific tags
            langchain_tags = ["langchain", operation_name]
            if tags:
                langchain_tags.extend(tags)
            
            return trace_function(
                name=f"langchain.{operation_name}",
                tags=langchain_tags,
                metadata={
                    "operation": operation_name,
                    "module": func.__module__,
                }
            )(func)(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator


def trace_agent_workflow(
    workflow_name: str,
    tags: Optional[list[str]] = None,
) -> Callable[[F], F]:
    """
    Decorator for agent workflow tracing.
    
    Args:
        workflow_name: Name of the agent workflow
        tags: Tags to associate with the trace
    
    Returns:
        Decorated function with agent workflow tracing
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Add agent-specific tags
            agent_tags = ["agent", "workflow", workflow_name]
            if tags:
                agent_tags.extend(tags)
            
            return trace_function(
                name=f"agent.{workflow_name}",
                tags=agent_tags,
                metadata={
                    "workflow": workflow_name,
                    "module": func.__module__,
                }
            )(func)(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator


def trace_runnable(
    runnable: Runnable,
    name: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Runnable:
    """
    Wrap a LangChain Runnable with tracing.
    
    Args:
        runnable: The Runnable to wrap
        name: Custom name for the trace
        tags: Tags to associate with the trace
    
    Returns:
        Traced Runnable
    """
    trace_name = name or f"runnable.{runnable.__class__.__name__}"
    runnable_tags = tags or ["runnable"]
    
    # Create a traced version of the runnable
    class TracedRunnable(Runnable):
        def __init__(self, inner_runnable: Runnable):
            self.inner_runnable = inner_runnable
        
        def invoke(self, input_data: Any, config: Optional[Dict[str, Any]] = None) -> Any:
            try:
                with langsmith.trace(
                    name=trace_name,
                    tags=runnable_tags,
                    metadata={
                        "runnable_type": type(self.inner_runnable).__name__,
                        "input_type": type(input_data).__name__,
                    }
                ) as trace:
                    result = self.inner_runnable.invoke(input_data, config)
                    
                    trace.add_metadata({
                        "result_type": type(result).__name__,
                        "success": True,
                    })
                    
                    return result
                    
            except Exception as e:
                logger.error(f"Error in traced runnable {trace_name}: {e}")
                raise
        
        async def ainvoke(self, input_data: Any, config: Optional[Dict[str, Any]] = None) -> Any:
            try:
                with langsmith.trace(
                    name=f"{trace_name}.async",
                    tags=runnable_tags + ["async"],
                    metadata={
                        "runnable_type": type(self.inner_runnable).__name__,
                        "input_type": type(input_data).__name__,
                    }
                ) as trace:
                    result = await self.inner_runnable.ainvoke(input_data, config)
                    
                    trace.add_metadata({
                        "result_type": type(result).__name__,
                        "success": True,
                    })
                    
                    return result
                    
            except Exception as e:
                logger.error(f"Error in traced async runnable {trace_name}: {e}")
                raise
    
    return TracedRunnable(runnable) 