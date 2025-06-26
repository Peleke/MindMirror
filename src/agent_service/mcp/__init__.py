"""
MindMirror Model Context Protocol Ecosystem

A comprehensive MCP implementation providing tools, resources, and prompts
for AI model interactions with external data sources and capabilities.
"""

__version__ = "1.0.0"
__author__ = "MindMirror Team"

# Core MCP Infrastructure
from .core import (
    MCPPlugin,
    MCPTool,
    MCPResource,
    MCPPrompt,
    MCPCheckpoint,
    MCPToolHandler,
    MCPResourceHandler,
    MCPPromptHandler,
    MCPCheckpointHandler,
    MCPPluginRegistry,
    PluginInfo,
    BaseMCPServer,
    create_checkpoint,
    validate_plugin_interface
)

__all__ = [
    # Core Infrastructure
    "MCPPlugin",
    "MCPTool",
    "MCPResource", 
    "MCPPrompt",
    "MCPCheckpoint",
    "MCPToolHandler",
    "MCPResourceHandler",
    "MCPPromptHandler",
    "MCPCheckpointHandler",
    "MCPPluginRegistry",
    "PluginInfo",
    "BaseMCPServer",
    "create_checkpoint",
    "validate_plugin_interface"
] 