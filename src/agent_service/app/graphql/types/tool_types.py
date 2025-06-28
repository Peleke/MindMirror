"""
GraphQL Types for MCP Tool Registry Integration

Enhanced GraphQL types for tool introspection, execution, and health monitoring.
"""

from typing import List, Optional

import strawberry


@strawberry.type
class ToolMetadata:
    """Enhanced tool metadata for GraphQL introspection."""

    name: str
    description: str
    owner_domain: str
    version: str
    backend: str
    effect_boundary: str
    tags: List[str]
    subtools: List[str]
    input_schema: strawberry.scalars.JSON
    output_schema: strawberry.scalars.JSON


@strawberry.type
class ToolExecutionResult:
    """Result of tool execution."""

    success: bool
    result: List[strawberry.scalars.JSON]
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


@strawberry.type
class ToolRegistryHealth:
    """Health status of the tool registry."""

    status: str
    total_tools: int
    unique_tools: int
    backends: strawberry.scalars.JSON
    error: Optional[str] = None
