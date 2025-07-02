"""
Base Classes and Interfaces for MCP Plugins

Defines the core abstractions for the Model Context Protocol ecosystem with
dependency injection and functional programming patterns.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, FrozenSet, List, Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

# ============================================================================
# Core Data Models
# ============================================================================


@dataclass(frozen=True)
class MCPTool:
    """Immutable representation of an MCP tool."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    tags: FrozenSet[str] = field(default_factory=frozenset)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MCPResource:
    """Immutable representation of an MCP resource."""

    uri: str
    name: str
    description: str
    mime_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MCPPrompt:
    """Immutable representation of an MCP prompt."""

    name: str
    description: str
    arguments: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MCPCheckpoint:
    """Immutable checkpoint for MCP operations."""

    plugin_name: str
    tool_name: str
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    thread_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Protocol Interfaces
# ============================================================================


@runtime_checkable
class MCPToolHandler(Protocol):
    """Protocol for tool execution handlers."""

    async def execute_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a tool by name with arguments."""
        ...


@runtime_checkable
class MCPResourceHandler(Protocol):
    """Protocol for resource access handlers."""

    async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Read a resource by URI."""
        ...


@runtime_checkable
class MCPPromptHandler(Protocol):
    """Protocol for prompt content handlers."""

    async def get_prompt_content(
        self, name: str, arguments: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get prompt content by name with optional arguments."""
        ...


@runtime_checkable
class MCPCheckpointHandler(Protocol):
    """Protocol for checkpoint management."""

    async def save_checkpoint(self, checkpoint: MCPCheckpoint) -> None:
        """Save a checkpoint."""
        ...

    async def load_checkpoint(self, thread_id: str) -> Optional[MCPCheckpoint]:
        """Load the latest checkpoint for a thread."""
        ...

    async def get_checkpoint_history(self, thread_id: str) -> List[MCPCheckpoint]:
        """Get checkpoint history for a thread."""
        ...


# ============================================================================
# Base Plugin Class
# ============================================================================


class MCPPlugin(ABC):
    """
    Base class for MCP plugins with dependency injection.

    This abstract base class provides the foundation for all MCP plugins,
    ensuring consistent interfaces and dependency management.
    """

    # Plugin metadata - should be overridden by subclasses
    version: str = "1.0.0"
    description: str = "Base MCP Plugin"
    dependencies: List[str] = []
    tags: FrozenSet[str] = frozenset()

    def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
        """
        Initialize the plugin with configuration and dependencies.

        Args:
            config: Plugin-specific configuration
            dependencies: Injected dependencies required by the plugin
        """
        self.config = config
        self.dependencies = dependencies
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Validate dependencies before proceeding
        self._validate_dependencies()

        # Initialize plugin state
        self._initialized = False
        self._tools: Optional[List[MCPTool]] = None
        self._resources: Optional[List[MCPResource]] = None
        self._prompts: Optional[List[MCPPrompt]] = None

        self.logger.info(f"Initialized {self.__class__.__name__} v{self.version}")

    @abstractmethod
    def _validate_dependencies(self) -> None:
        """
        Validate that all required dependencies are provided.

        Raises:
            ValueError: If required dependencies are missing or invalid
        """
        pass

    @abstractmethod
    def _create_tools(self) -> List[MCPTool]:
        """Create the list of tools provided by this plugin."""
        pass

    @abstractmethod
    def _create_resources(self) -> List[MCPResource]:
        """Create the list of resources provided by this plugin."""
        pass

    @abstractmethod
    def _create_prompts(self) -> List[MCPPrompt]:
        """Create the list of prompts provided by this plugin."""
        pass

    def _ensure_initialized(self) -> None:
        """Ensure the plugin is properly initialized."""
        if not self._initialized:
            self._tools = self._create_tools()
            self._resources = self._create_resources()
            self._prompts = self._create_prompts()
            self._initialized = True
            self.logger.debug(
                f"Plugin {self.__class__.__name__} initialized with "
                f"{len(self._tools)} tools, {len(self._resources)} resources, "
                f"{len(self._prompts)} prompts"
            )

    async def get_tools(self) -> List[MCPTool]:
        """Get the list of tools provided by this plugin."""
        self._ensure_initialized()
        return self._tools or []

    async def get_resources(self) -> List[MCPResource]:
        """Get the list of resources provided by this plugin."""
        self._ensure_initialized()
        return self._resources or []

    async def get_prompts(self) -> List[MCPPrompt]:
        """Get the list of prompts provided by this plugin."""
        self._ensure_initialized()
        return self._prompts or []

    @abstractmethod
    async def execute_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute a tool by name with arguments.

        Args:
            name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            List of content dictionaries

        Raises:
            ValueError: If tool name is unknown
            Exception: If tool execution fails
        """
        pass

    @abstractmethod
    async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
        """
        Read a resource by URI.

        Args:
            uri: Resource URI to read

        Returns:
            List of content dictionaries

        Raises:
            ValueError: If resource URI is unknown
            Exception: If resource read fails
        """
        pass

    @abstractmethod
    async def get_prompt_content(
        self, name: str, arguments: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get prompt content by name with optional arguments.

        Args:
            name: Name of the prompt
            arguments: Optional prompt arguments

        Returns:
            Prompt content dictionary

        Raises:
            ValueError: If prompt name is unknown
            Exception: If prompt retrieval fails
        """
        pass

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin metadata and information."""
        return {
            "name": self.__class__.__name__,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "tags": list(self.tags),
            "initialized": self._initialized,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the plugin."""
        try:
            self._ensure_initialized()
            return {
                "status": "healthy",
                "plugin": self.get_plugin_info(),
                "tools_count": len(self._tools or []),
                "resources_count": len(self._resources or []),
                "prompts_count": len(self._prompts or []),
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "plugin": self.get_plugin_info(),
            }


# ============================================================================
# Utility Functions
# ============================================================================


def validate_plugin_interface(plugin_class: type) -> bool:
    """
    Validate that a class properly implements the MCPPlugin interface.

    Args:
        plugin_class: Class to validate

    Returns:
        True if valid, raises ValueError if invalid
    """
    if not issubclass(plugin_class, MCPPlugin):
        raise ValueError(f"{plugin_class.__name__} must inherit from MCPPlugin")

    required_methods = [
        "_validate_dependencies",
        "_create_tools",
        "_create_resources",
        "_create_prompts",
        "execute_tool",
        "read_resource",
        "get_prompt_content",
    ]

    for method in required_methods:
        if not hasattr(plugin_class, method):
            raise ValueError(f"{plugin_class.__name__} must implement {method}")

    return True


def create_checkpoint(
    plugin_name: str,
    tool_name: str,
    input_state: Dict[str, Any],
    output_state: Dict[str, Any],
    execution_time: float,
    thread_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> MCPCheckpoint:
    """
    Create a checkpoint for MCP operations.

    Args:
        plugin_name: Name of the plugin
        tool_name: Name of the tool executed
        input_state: Input state
        output_state: Output state
        execution_time: Execution time in seconds
        thread_id: Thread identifier
        metadata: Optional metadata

    Returns:
        MCPCheckpoint instance
    """
    return MCPCheckpoint(
        plugin_name=plugin_name,
        tool_name=tool_name,
        input_state=input_state,
        output_state=output_state,
        execution_time=execution_time,
        timestamp=datetime.now(timezone.utc),
        thread_id=thread_id,
        metadata=metadata or {},
    )
