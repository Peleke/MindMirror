"""
MCP Tool Orchestration Layer - Base Classes

Core abstractions for the code-first, type-safe tool orchestration system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, FrozenSet
from enum import Enum


class ToolBackend(Enum):
    """Supported tool backends."""
    LANGGRAPH = "langgraph"
    PROMPT = "prompt"
    RETRIEVER = "retriever"
    HYBRID = "hybrid"
    EXTERNAL = "external"


class EffectBoundary(Enum):
    """Effect boundaries for tools."""
    PURE = "pure"
    RETRIEVER = "retriever"
    LLM = "llm"
    EXTERNAL = "external"


@dataclass(frozen=True)
class ToolMetadata:
    """Metadata for tool capabilities and configuration."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    backend: ToolBackend
    tags: FrozenSet[str] = field(default_factory=frozenset)
    effect_boundary: EffectBoundary = EffectBoundary.LLM
    version: str = "1.0.0"
    author: str = "MindMirror Team"
    latency_ms: Optional[float] = None
    cost_per_execution: Optional[float] = None


class MCPTool(ABC):
    """Base interface for all MCP tools."""
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the tool with given arguments."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate input arguments against schema."""
        # Basic validation - can be overridden for more complex validation
        schema = self.get_metadata().input_schema
        required = schema.get("required", [])
        
        for field in required:
            if field not in arguments:
                return False
        
        return True
    
    async def execute_with_validation(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute tool with argument validation."""
        if not self.validate_arguments(arguments):
            raise ValueError(f"Invalid arguments for tool {self.get_metadata().name}")
        
        return await self.execute(arguments)


class ToolRegistry:
    """Registry for managing MCP tools with decorator-based registration."""
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        self._global_registry: Optional['ToolRegistry'] = None
    
    def register(self, tool: MCPTool) -> None:
        """Register a tool."""
        if tool is None:
            raise ValueError("Tool cannot be None")
        
        if not isinstance(tool, MCPTool):
            raise ValueError("Tool must implement MCPTool interface")
        
        metadata = tool.get_metadata()
        
        if metadata.name in self._tools:
            raise ValueError(f"Tool {metadata.name} is already registered")
        
        self._tools[metadata.name] = tool
        self._metadata[metadata.name] = metadata
    
    def unregister(self, name: str) -> None:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            del self._metadata[name]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a tool by name."""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        
        return await tool.execute_with_validation(arguments)
    
    def list_tools(self, backend: Optional[ToolBackend] = None, tags: Optional[List[str]] = None) -> List[ToolMetadata]:
        """List tools with optional filtering."""
        tools = list(self._metadata.values())
        
        if backend:
            tools = [t for t in tools if t.backend == backend]
        
        if tags:
            tools = [t for t in tools if any(tag in t.tags for tag in tags)]
        
        return tools
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self._metadata.get(name)
    
    def list_tool_names(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def get_tools_by_backend(self, backend: ToolBackend) -> List[MCPTool]:
        """Get tools by backend type."""
        return [
            tool for tool in self._tools.values()
            if tool.get_metadata().backend == backend
        ]
    
    def get_tools_by_effect_boundary(self, effect_boundary: EffectBoundary) -> List[MCPTool]:
        """Get tools by effect boundary."""
        return [
            tool for tool in self._tools.values()
            if tool.get_metadata().effect_boundary == effect_boundary
        ]
    
    def export_to_yaml(self) -> str:
        """Export registry to YAML for CI/deployment."""
        import yaml
        
        export_data = {
            "tools": [
                {
                    "name": metadata.name,
                    "description": metadata.description,
                    "input_schema": metadata.input_schema,
                    "backend": metadata.backend.value,
                    "tags": list(metadata.tags),
                    "effect_boundary": metadata.effect_boundary.value,
                    "version": metadata.version,
                    "author": metadata.author,
                    "latency_ms": metadata.latency_ms,
                    "cost_per_execution": metadata.cost_per_execution
                }
                for metadata in self._metadata.values()
            ]
        }
        
        return yaml.dump(export_data, default_flow_style=False, sort_keys=False)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the tool registry."""
        return {
            "status": "healthy",
            "total_tools": len(self._tools),
            "backends": {
                backend.value: len(self.get_tools_by_backend(backend))
                for backend in ToolBackend
            },
            "effect_boundaries": {
                boundary.value: len(self.get_tools_by_effect_boundary(boundary))
                for boundary in EffectBoundary
            }
        }


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def set_global_registry(registry: ToolRegistry) -> None:
    """Set the global tool registry instance."""
    global _global_registry
    _global_registry = registry 