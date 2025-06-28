"""
MCP Tool Base Classes

Core abstractions for the MCP Tool Orchestration Layer.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional

from packaging import version as parse_version


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
    """Enhanced metadata for MCP tools."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    backend: ToolBackend
    owner_domain: str = "default"
    version: str = "1.0.0"
    tags: FrozenSet[str] = field(default_factory=lambda: frozenset())
    effect_boundary: EffectBoundary = EffectBoundary.LLM
    subtools: FrozenSet[str] = field(default_factory=lambda: frozenset())


class MCPTool(ABC):
    """Enhanced base interface for all MCP tools."""

    @property
    def owner_domain(self) -> str:
        """Get the owner domain for this tool."""
        return "default"

    @property
    def version(self) -> str:
        """Get the tool version (semver)."""
        return "1.0.0"

    @property
    def input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool."""
        return self.get_metadata().input_schema

    @property
    def output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this tool."""
        return self.get_metadata().output_schema

    def list_subtools(self) -> List[str]:
        """List available subtools (optional)."""
        return []

    async def execute_subtool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a subtool (optional)."""
        raise NotImplementedError(f"Subtool {name} not implemented")

    async def on_execute(
        self, args: Dict[str, Any], result: Any, success: bool, latency_ms: int
    ) -> None:
        """Hook called after tool execution for observability."""
        pass

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments against input schema."""
        # Basic validation - can be enhanced with JSON Schema validation
        required_fields = self.input_schema.get("required", [])
        for field in required_fields:
            if field not in arguments:
                return False
        return True

    async def execute_with_validation(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute tool with argument validation."""
        if not self.validate_arguments(arguments):
            raise ValueError("Invalid arguments for tool execution")
        return await self.execute(arguments)

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the tool with given arguments."""
        pass

    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        pass


class ToolRegistry:
    """Enhanced registry for managing MCP tools with versioning and domain support."""

    def __init__(self):
        self._tools: Dict[str, Dict[str, MCPTool]] = {}  # name -> version -> tool
        self._metadata: Dict[str, Dict[str, ToolMetadata]] = {}

    def register(self, tool: MCPTool) -> None:
        """Register a tool with versioning."""
        if not isinstance(tool, MCPTool):
            raise ValueError("Tool must implement MCPTool interface")

        metadata = tool.get_metadata()
        if metadata.name not in self._tools:
            self._tools[metadata.name] = {}
            self._metadata[metadata.name] = {}

        self._tools[metadata.name][metadata.version] = tool
        self._metadata[metadata.name][metadata.version] = metadata

    def unregister(self, name: str, version: Optional[str] = None) -> None:
        """Unregister a tool."""
        if name not in self._tools:
            return

        if version:
            if version in self._tools[name]:
                del self._tools[name][version]
                del self._metadata[name][version]
                if not self._tools[name]:
                    del self._tools[name]
                    del self._metadata[name]
        else:
            # Remove all versions
            del self._tools[name]
            del self._metadata[name]

    def get_tool(self, name: str, version: Optional[str] = None) -> Optional[MCPTool]:
        """Get a tool by name and optional version."""
        if name not in self._tools:
            return None

        if version:
            return self._tools[name].get(version)
        else:
            # Return latest version
            try:
                versions = sorted(
                    self._tools[name].keys(), key=parse_version, reverse=True
                )
                return self._tools[name][versions[0]] if versions else None
            except Exception:
                # Fallback to string comparison if version parsing fails
                versions = sorted(self._tools[name].keys(), reverse=True)
                return self._tools[name][versions[0]] if versions else None

    def get_tool_metadata(
        self, name: str, version: Optional[str] = None
    ) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        if name not in self._metadata:
            return None

        if version:
            return self._metadata[name].get(version)
        else:
            # Return latest version metadata
            try:
                versions = sorted(
                    self._metadata[name].keys(), key=parse_version, reverse=True
                )
                return self._metadata[name][versions[0]] if versions else None
            except Exception:
                # Fallback to string comparison if version parsing fails
                versions = sorted(self._metadata[name].keys(), reverse=True)
                return self._metadata[name][versions[0]] if versions else None

    def list_tools(
        self,
        backend: Optional[str] = None,
        tags: Optional[List[str]] = None,
        owner_domain: Optional[str] = None,
        version: Optional[str] = None,
    ) -> List[ToolMetadata]:
        """List tools with enhanced filtering."""
        tools = []
        for name, versions in self._metadata.items():
            try:
                target_version = version or max(versions.keys(), key=parse_version)
            except Exception:
                # Fallback to string comparison if version parsing fails
                target_version = version or max(versions.keys())

            metadata = versions[target_version]

            if backend and metadata.backend.value != backend:
                continue
            if tags and not any(tag in metadata.tags for tag in tags):
                continue
            if owner_domain and metadata.owner_domain != owner_domain:
                continue

            tools.append(metadata)

        return tools

    def list_tool_names(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_tools_by_backend(self, backend: ToolBackend) -> List[MCPTool]:
        """Get all tools for a specific backend."""
        tools = []
        for name, versions in self._tools.items():
            for version, tool in versions.items():
                if tool.get_metadata().backend == backend:
                    tools.append(tool)
        return tools

    def get_tools_by_effect_boundary(
        self, effect_boundary: EffectBoundary
    ) -> List[MCPTool]:
        """Get all tools for a specific effect boundary."""
        tools = []
        for name, versions in self._tools.items():
            for version, tool in versions.items():
                if tool.get_metadata().effect_boundary == effect_boundary:
                    tools.append(tool)
        return tools

    async def execute_tool(
        self, name: str, arguments: Dict[str, Any], version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a tool with versioning and telemetry."""
        tool = self.get_tool(name, version)
        if not tool:
            raise ValueError(f"Tool {name} not found")

        start_time = time.time()
        success = False
        result = None

        try:
            result = await tool.execute(arguments)
            success = True
            return result
        finally:
            latency_ms = int((time.time() - start_time) * 1000)
            await tool.on_execute(arguments, result, success, latency_ms)

    def export_to_yaml(self) -> str:
        """Export registry to YAML for CI/deployment."""
        import yaml

        export_data = {
            "tools": [],
            "metadata": {
                "total_tools": len(self.list_tool_names()),
                "backends": {},
                "domains": {},
                "effect_boundaries": {},
            },
        }

        # Collect tool data
        for name, versions in self._metadata.items():
            for version, metadata in versions.items():
                tool_data = {
                    "name": metadata.name,
                    "version": metadata.version,
                    "description": metadata.description,
                    "owner_domain": metadata.owner_domain,
                    "backend": metadata.backend.value,
                    "effect_boundary": metadata.effect_boundary.value,
                    "tags": list(metadata.tags),
                    "subtools": list(metadata.subtools),
                    "input_schema": metadata.input_schema,
                    "output_schema": metadata.output_schema,
                }
                export_data["tools"].append(tool_data)

        # Collect metadata
        for metadata in self.list_tools():
            backend = metadata.backend.value
            domain = metadata.owner_domain
            effect_boundary = metadata.effect_boundary.value

            export_data["metadata"]["backends"][backend] = (
                export_data["metadata"]["backends"].get(backend, 0) + 1
            )
            export_data["metadata"]["domains"][domain] = (
                export_data["metadata"]["domains"].get(domain, 0) + 1
            )
            export_data["metadata"]["effect_boundaries"][effect_boundary] = (
                export_data["metadata"]["effect_boundaries"].get(effect_boundary, 0) + 1
            )

        return yaml.dump(export_data, default_flow_style=False, sort_keys=False)

    def health_check(self) -> Dict[str, Any]:
        """Get registry health status."""
        total_tools = sum(len(versions) for versions in self._tools.values())

        backends = {}
        effect_boundaries = {}
        domains = {}

        for metadata in self.list_tools():
            backend = metadata.backend.value
            effect_boundary = metadata.effect_boundary.value
            domain = metadata.owner_domain

            backends[backend] = backends.get(backend, 0) + 1
            effect_boundaries[effect_boundary] = (
                effect_boundaries.get(effect_boundary, 0) + 1
            )
            domains[domain] = domains.get(domain, 0) + 1

        return {
            "status": "healthy",
            "total_tools": total_tools,
            "unique_tools": len(self._tools),
            "backends": backends,
            "effect_boundaries": effect_boundaries,
            "domains": domains,
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
