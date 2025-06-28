"""
Plugin Registry and Discovery

Manages MCP plugin registration, discovery, and dependency injection.
"""

import importlib
import inspect
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .base import MCPPlugin, validate_plugin_interface

logger = logging.getLogger(__name__)

# ============================================================================
# Plugin Information
# ============================================================================


@dataclass(frozen=True)
class PluginInfo:
    """Immutable plugin information."""

    name: str
    version: str
    description: str
    plugin_class: Type[MCPPlugin]
    dependencies: List[str]
    tags: frozenset[str]
    module_path: str


# ============================================================================
# Plugin Registry
# ============================================================================


class MCPPluginRegistry:
    """
    Registry for MCP plugins with dependency injection.

    Provides plugin discovery, registration, and instance management
    with proper dependency validation and lifecycle management.
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, PluginInfo] = {}
        self._instances: Dict[str, MCPPlugin] = {}
        self.logger = logging.getLogger(f"{__name__}.MCPPluginRegistry")

        self.logger.info("Initialized MCP Plugin Registry")

    def register_plugin(self, plugin_info: PluginInfo) -> None:
        """
        Register a plugin with the registry.

        Args:
            plugin_info: Plugin information to register

        Raises:
            ValueError: If plugin is already registered or invalid
        """
        if plugin_info.name in self._plugins:
            raise ValueError(f"Plugin {plugin_info.name} is already registered")

        # Validate plugin interface
        try:
            validate_plugin_interface(plugin_info.plugin_class)
        except ValueError as e:
            raise ValueError(f"Invalid plugin {plugin_info.name}: {e}")

        self._plugins[plugin_info.name] = plugin_info
        self.logger.info(
            f"Registered plugin: {plugin_info.name} v{plugin_info.version}"
        )

    def register_plugin_class(
        self,
        plugin_class: Type[MCPPlugin],
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Register a plugin class directly.

        Args:
            plugin_class: Plugin class to register
            name: Optional custom name (defaults to class name)
            version: Optional version override
            description: Optional description override
            dependencies: Optional dependencies override
            tags: Optional tags override

        Raises:
            ValueError: If plugin is invalid or already registered
        """
        plugin_name = name or plugin_class.__name__

        # Extract plugin metadata
        plugin_info = PluginInfo(
            name=plugin_name,
            version=version or getattr(plugin_class, "version", "1.0.0"),
            description=description or getattr(plugin_class, "description", ""),
            plugin_class=plugin_class,
            dependencies=dependencies or getattr(plugin_class, "dependencies", []),
            tags=frozenset(tags or getattr(plugin_class, "tags", [])),
            module_path=f"{plugin_class.__module__}.{plugin_class.__name__}",
        )

        self.register_plugin(plugin_info)

    def discover_plugins(self, plugin_dir: Path) -> None:
        """
        Discover plugins from a directory.

        Args:
            plugin_dir: Directory containing plugin modules

        Raises:
            ValueError: If plugin directory doesn't exist
        """
        if not plugin_dir.exists():
            raise ValueError(f"Plugin directory does not exist: {plugin_dir}")

        if not plugin_dir.is_dir():
            raise ValueError(f"Plugin path is not a directory: {plugin_dir}")

        self.logger.info(f"Discovering plugins in: {plugin_dir}")

        # Find all plugin modules
        for plugin_path in plugin_dir.glob("*/__init__.py"):
            plugin_name = plugin_path.parent.name

            # Skip non-plugin directories
            if plugin_name.startswith("_") or plugin_name in ["__pycache__", "tests"]:
                continue

            try:
                # Import the plugin module
                module_path = f"agent_service.mcp.plugins.{plugin_name}"
                module = importlib.import_module(module_path)

                # Look for plugin class (convention: {PluginName}Plugin)
                plugin_class_name = f"{plugin_name.title()}Plugin"
                plugin_class = getattr(module, plugin_class_name, None)

                if plugin_class is None:
                    self.logger.warning(
                        f"No plugin class found in {plugin_name}: {plugin_class_name}"
                    )
                    continue

                # Register the plugin
                self.register_plugin_class(plugin_class, plugin_name)

            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
                continue

        self.logger.info(f"Discovered {len(self._plugins)} plugins")

    def create_plugin_instance(
        self, plugin_name: str, config: Dict[str, Any], dependencies: Dict[str, Any]
    ) -> MCPPlugin:
        """
        Create a plugin instance with dependency injection.

        Args:
            plugin_name: Name of the plugin to instantiate
            config: Plugin configuration
            dependencies: Injected dependencies

        Returns:
            Plugin instance

        Raises:
            ValueError: If plugin not found or dependencies missing
        """
        if plugin_name not in self._plugins:
            raise ValueError(f"Plugin {plugin_name} not found in registry")

        plugin_info = self._plugins[plugin_name]

        # Validate dependencies
        missing_deps = [
            dep for dep in plugin_info.dependencies if dep not in dependencies
        ]
        if missing_deps:
            raise ValueError(f"Missing dependencies for {plugin_name}: {missing_deps}")

        # Create instance
        try:
            instance = plugin_info.plugin_class(config, dependencies)
            self._instances[plugin_name] = instance

            self.logger.info(f"Created instance of plugin: {plugin_name}")
            return instance

        except Exception as e:
            self.logger.error(f"Failed to create instance of plugin {plugin_name}: {e}")
            raise

    def get_plugin_instance(self, plugin_name: str) -> Optional[MCPPlugin]:
        """
        Get an existing plugin instance.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance if exists, None otherwise
        """
        return self._instances.get(plugin_name)

    def get_or_create_instance(
        self, plugin_name: str, config: Dict[str, Any], dependencies: Dict[str, Any]
    ) -> MCPPlugin:
        """
        Get existing instance or create new one.

        Args:
            plugin_name: Name of the plugin
            config: Plugin configuration
            dependencies: Injected dependencies

        Returns:
            Plugin instance
        """
        instance = self.get_plugin_instance(plugin_name)
        if instance is not None:
            return instance

        return self.create_plugin_instance(plugin_name, config, dependencies)

    def list_plugins(self) -> List[PluginInfo]:
        """List all registered plugins."""
        return list(self._plugins.values())

    def list_registered_plugins(self) -> List[PluginInfo]:
        """List all registered plugins (alias for list_plugins)."""
        return self.list_plugins()

    def get_plugins_by_tag(self, tag: str) -> List[PluginInfo]:
        """
        Get plugins by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of plugins with the specified tag
        """
        return [plugin for plugin in self._plugins.values() if tag in plugin.tags]

    def filter_plugins_by_tags(self, tags: List[str]) -> List[PluginInfo]:
        """
        Filter plugins by multiple tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of plugins that have any of the specified tags
        """
        return [
            plugin
            for plugin in self._plugins.values()
            if any(tag in plugin.tags for tag in tags)
        ]

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        Get plugin information.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin information if found, None otherwise
        """
        return self._plugins.get(plugin_name)

    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of the plugin to unregister

        Raises:
            ValueError: If plugin not found
        """
        if plugin_name not in self._plugins:
            raise ValueError(f"Plugin {plugin_name} not found")

        # Clean up instance if exists
        if plugin_name in self._instances:
            del self._instances[plugin_name]

        # Remove from registry
        del self._plugins[plugin_name]

        self.logger.info(f"Unregistered plugin: {plugin_name}")

    def clear(self) -> None:
        """Clear all plugins and instances."""
        self._plugins.clear()
        self._instances.clear()
        self.logger.info("Cleared plugin registry")

    def get_registry_info(self) -> Dict[str, Any]:
        """Get registry information and statistics."""
        return {
            "total_plugins": len(self._plugins),
            "active_instances": len(self._instances),
            "plugins": [
                {
                    "name": info.name,
                    "version": info.version,
                    "description": info.description,
                    "dependencies": info.dependencies,
                    "tags": list(info.tags),
                    "has_instance": info.name in self._instances,
                }
                for info in self._plugins.values()
            ],
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all plugin instances."""
        results = {}

        for plugin_name, instance in self._instances.items():
            try:
                health = await instance.health_check()
                results[plugin_name] = health
            except Exception as e:
                results[plugin_name] = {"status": "error", "error": str(e)}

        return {
            "registry_status": "healthy",
            "total_instances": len(self._instances),
            "plugin_health": results,
        }


# ============================================================================
# Global Registry Instance
# ============================================================================

# Global registry instance for convenience
_global_registry: Optional[MCPPluginRegistry] = None


def get_global_registry() -> MCPPluginRegistry:
    """Get the global plugin registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = MCPPluginRegistry()
    return _global_registry


def set_global_registry(registry: MCPPluginRegistry) -> None:
    """Set the global plugin registry instance."""
    global _global_registry
    _global_registry = registry
