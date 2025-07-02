"""
Core MCP Infrastructure

Base classes, interfaces, and utilities for the Model Context Protocol ecosystem.
"""

from .base import (
    MCPCheckpoint,
    MCPCheckpointHandler,
    MCPPlugin,
    MCPPrompt,
    MCPPromptHandler,
    MCPResource,
    MCPResourceHandler,
    MCPTool,
    MCPToolHandler,
    create_checkpoint,
    validate_plugin_interface,
)
from .registry import MCPPluginRegistry, PluginInfo
from .server import BaseMCPServer

__all__ = [
    # Base classes and interfaces
    "MCPPlugin",
    "MCPTool",
    "MCPResource",
    "MCPPrompt",
    "MCPCheckpoint",
    "MCPToolHandler",
    "MCPResourceHandler",
    "MCPPromptHandler",
    "MCPCheckpointHandler",
    # Registry
    "MCPPluginRegistry",
    "PluginInfo",
    # Server
    "BaseMCPServer",
    # Utilities
    "create_checkpoint",
    "validate_plugin_interface",
]
