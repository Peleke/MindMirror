"""
LangSmith tracing configuration for the agent service.

This module provides centralized tracing setup for all LLM operations,
enabling observability, debugging, and evaluation of agent workflows.
"""

import os
from typing import Optional

import langsmith
from langsmith import Client

from .decorators import (
    trace_function,
    trace_performance,
    trace_errors,
    trace_langchain_operation,
    trace_agent_workflow,
    trace_runnable,
)


def setup_langsmith_tracing(
    api_key: Optional[str] = None,
    project_name: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> Client:
    """
    Configure LangSmith tracing for the agent service.
    
    Args:
        api_key: LangSmith API key (defaults to LANGCHAIN_API_KEY env var)
        project_name: Project name for tracing (defaults to LANGCHAIN_PROJECT env var)
        endpoint: LangSmith endpoint (defaults to LANGCHAIN_ENDPOINT env var)
    
    Returns:
        Configured LangSmith client
    """
    # Set environment variables for LangChain integration
    if api_key:
        os.environ["LANGCHAIN_API_KEY"] = api_key
    if project_name:
        os.environ["LANGCHAIN_PROJECT"] = project_name
    if endpoint:
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint
    
    # Ensure required environment variables are set
    if not os.getenv("LANGCHAIN_API_KEY"):
        raise ValueError(
            "LANGCHAIN_API_KEY environment variable is required for LangSmith tracing"
        )
    
    # Set default project name if not provided
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "mindmirror-agent"
    
    # Enable tracing by default
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    
    # Create and return LangSmith client
    client = langsmith.Client()
    
    return client


def get_langsmith_client() -> Client:
    """
    Get the configured LangSmith client.
    
    Returns:
        LangSmith client instance
    """
    return langsmith.Client()


# Initialize tracing on module import
try:
    _client = setup_langsmith_tracing()
except ValueError:
    # Tracing not configured, but don't fail the import
    _client = None

__all__ = [
    "trace_function",
    "trace_performance", 
    "trace_errors",
    "trace_langchain_operation",
    "trace_agent_workflow",
    "trace_runnable",
    "setup_langsmith_tracing",
    "get_langsmith_client",
] 