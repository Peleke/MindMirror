"""
Test Suite for MCP Core Infrastructure

Comprehensive tests for base classes, registry, and server implementation
following TDD principles and property-based testing.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agent_service.mcp.core import (
    BaseMCPServer,
    MCPCheckpoint,
    MCPCheckpointHandler,
    MCPPlugin,
    MCPPluginRegistry,
    MCPPrompt,
    MCPPromptHandler,
    MCPResource,
    MCPResourceHandler,
    MCPTool,
    MCPToolHandler,
    PluginInfo,
    create_checkpoint,
    validate_plugin_interface,
)

# ============================================================================
# Test Data
# ============================================================================


@pytest.fixture
def sample_tool():
    return MCPTool(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object", "properties": {"input": {"type": "string"}}},
    )


@pytest.fixture
def sample_resource():
    return MCPResource(
        uri="test://resource/1",
        name="Test Resource",
        description="A test resource",
        mime_type="text/plain",
    )


@pytest.fixture
def sample_prompt():
    return MCPPrompt(
        name="test_prompt",
        description="A test prompt",
        arguments=[{"name": "input", "type": "string", "description": "Input text"}],
    )


@pytest.fixture
def sample_checkpoint():
    return MCPCheckpoint(
        plugin_name="test_plugin",
        tool_name="test_tool",
        input_state={"input": "test"},
        output_state={"result": "success"},
        execution_time=0.1,
        timestamp=datetime.now(),
        thread_id="12345",
        metadata={"test": True},
    )


# ============================================================================
# Base Classes Tests
# ============================================================================


class TestMCPTool:
    """Test MCPTool dataclass."""

    def test_tool_creation(self, sample_tool):
        """Test tool creation with valid data."""
        assert sample_tool.name == "test_tool"
        assert sample_tool.description == "A test tool"
        assert sample_tool.input_schema["type"] == "object"

    def test_tool_immutability(self, sample_tool):
        """Test that tool is immutable."""
        with pytest.raises(Exception):
            sample_tool.name = "new_name"

    def test_tool_equality(self):
        """Test tool equality comparison."""
        tool1 = MCPTool(
            name="test", description="test", input_schema={"type": "object"}
        )
        tool2 = MCPTool(
            name="test", description="test", input_schema={"type": "object"}
        )
        assert tool1 == tool2


class TestMCPResource:
    """Test MCPResource dataclass."""

    def test_resource_creation(self, sample_resource):
        """Test resource creation with valid data."""
        assert sample_resource.uri == "test://resource/1"
        assert sample_resource.name == "Test Resource"
        assert sample_resource.mime_type == "text/plain"

    def test_resource_immutability(self, sample_resource):
        """Test that resource is immutable."""
        with pytest.raises(Exception):
            sample_resource.uri = "new://uri"


class TestMCPPrompt:
    """Test MCPPrompt dataclass."""

    def test_prompt_creation(self, sample_prompt):
        """Test prompt creation with valid data."""
        assert sample_prompt.name == "test_prompt"
        assert len(sample_prompt.arguments) == 1
        assert sample_prompt.arguments[0]["name"] == "input"


class TestMCPCheckpoint:
    """Test MCPCheckpoint dataclass."""

    def test_checkpoint_creation(self, sample_checkpoint):
        """Test checkpoint creation with valid data."""
        assert sample_checkpoint.plugin_name == "test_plugin"
        assert sample_checkpoint.tool_name == "test_tool"
        assert sample_checkpoint.execution_time == 0.1
        assert sample_checkpoint.metadata["test"] is True


# ============================================================================
# Protocol Tests
# ============================================================================


class TestMCPToolHandler:
    """Test MCPToolHandler protocol."""

    def test_tool_handler_protocol(self):
        """Test that a class implementing the protocol works correctly."""

        class TestToolHandler:
            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return [{"type": "text", "text": f"Executed {name} with {arguments}"}]

        handler = TestToolHandler()
        assert isinstance(handler, MCPToolHandler)


class TestMCPResourceHandler:
    """Test MCPResourceHandler protocol."""

    def test_resource_handler_protocol(self):
        """Test that a class implementing the protocol works correctly."""

        class TestResourceHandler:
            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return [{"type": "text", "text": f"Read resource {uri}"}]

        handler = TestResourceHandler()
        assert isinstance(handler, MCPResourceHandler)


class TestMCPPromptHandler:
    """Test MCPPromptHandler protocol."""

    def test_prompt_handler_protocol(self):
        """Test that a class implementing the protocol works correctly."""

        class TestPromptHandler:
            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {"content": f"Prompt {name}", "arguments": arguments}

        handler = TestPromptHandler()
        assert isinstance(handler, MCPPromptHandler)


# ============================================================================
# Base Plugin Tests
# ============================================================================


class TestMCPPlugin:
    """Test MCPPlugin abstract base class."""

    def test_plugin_abstract_methods(self):
        """Test that MCPPlugin cannot be instantiated directly."""
        with pytest.raises(TypeError):
            MCPPlugin()

    def test_concrete_plugin_implementation(self):
        """Test a concrete plugin implementation."""

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)
                self.tools = [
                    MCPTool(
                        name="test_tool",
                        description="Test tool",
                        input_schema={"type": "object"},
                    )
                ]
                self.resources = [
                    MCPResource(
                        uri="test://resource",
                        name="Test Resource",
                        description="Test resource",
                        mime_type="text/plain",
                    )
                ]
                self.prompts = [
                    MCPPrompt(
                        name="test_prompt", description="Test prompt", arguments=[]
                    )
                ]

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return self.tools

            def _create_resources(self) -> List[MCPResource]:
                return self.resources

            def _create_prompts(self) -> List[MCPPrompt]:
                return self.prompts

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return [{"type": "text", "text": f"Executed {name}"}]

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return [{"type": "text", "text": f"Read {uri}"}]

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {"content": f"Prompt {name}"}

        plugin = TestPlugin({"test": True}, {})
        assert isinstance(plugin, MCPPlugin)
        assert plugin.config["test"] is True


# ============================================================================
# Registry Tests
# ============================================================================


class TestMCPPluginRegistry:
    """Test MCPPluginRegistry functionality."""

    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = MCPPluginRegistry()
        assert registry._plugins == {}
        assert registry._instances == {}

    def test_register_plugin(self):
        """Test plugin registration."""
        registry = MCPPluginRegistry()

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        registry.register_plugin_class(
            TestPlugin, name="test_plugin", version="1.0.0", description="A test plugin"
        )

        assert "test_plugin" in registry._plugins
        plugin_info = registry._plugins["test_plugin"]
        assert plugin_info.name == "test_plugin"
        assert plugin_info.description == "A test plugin"

    def test_duplicate_registration(self):
        """Test that duplicate registration raises error."""
        registry = MCPPluginRegistry()

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        registry.register_plugin_class(TestPlugin, name="test_plugin")

        with pytest.raises(
            ValueError, match="Plugin test_plugin is already registered"
        ):
            registry.register_plugin_class(TestPlugin, name="test_plugin")

    def test_create_plugin_instance(self):
        """Test plugin instance creation."""
        registry = MCPPluginRegistry()

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        registry.register_plugin_class(TestPlugin, name="test_plugin")

        config = {"test": True}
        dependencies = {}
        instance = registry.create_plugin_instance("test_plugin", config, dependencies)

        assert isinstance(instance, TestPlugin)
        assert instance.config["test"] is True
        assert "test_plugin" in registry._instances

    def test_get_or_create_instance(self):
        """Test get or create instance functionality."""
        registry = MCPPluginRegistry()

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        registry.register_plugin_class(TestPlugin, name="test_plugin")

        config = {"test": True}
        dependencies = {}

        # First call should create instance
        instance1 = registry.get_or_create_instance("test_plugin", config, dependencies)
        assert isinstance(instance1, TestPlugin)

        # Second call should return same instance
        instance2 = registry.get_or_create_instance("test_plugin", config, dependencies)
        assert instance1 is instance2

    def test_list_registered_plugins(self):
        """Test listing registered plugins."""
        registry = MCPPluginRegistry()

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        registry.register_plugin_class(TestPlugin, name="plugin1")
        registry.register_plugin_class(TestPlugin, name="plugin2")

        plugins = registry.list_registered_plugins()
        assert len(plugins) == 2
        assert "plugin1" in [p.name for p in plugins]
        assert "plugin2" in [p.name for p in plugins]

    def test_filter_plugins_by_tags(self):
        """Test filtering plugins by tags."""
        registry = MCPPluginRegistry()

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        registry.register_plugin_class(
            TestPlugin, name="plugin1", tags=["test", "core"]
        )
        registry.register_plugin_class(TestPlugin, name="plugin2", tags=["test"])
        registry.register_plugin_class(TestPlugin, name="plugin3", tags=["core"])

        test_plugins = registry.filter_plugins_by_tags(["test"])
        assert len(test_plugins) == 2
        assert "plugin1" in [p.name for p in test_plugins]
        assert "plugin2" in [p.name for p in test_plugins]

        core_plugins = registry.filter_plugins_by_tags(["core"])
        assert len(core_plugins) == 2
        assert "plugin1" in [p.name for p in core_plugins]
        assert "plugin3" in [p.name for p in core_plugins]


# ============================================================================
# Server Tests
# ============================================================================


class TestBaseMCPServer:
    """Test BaseMCPServer functionality."""

    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        config = {"test": True}
        return BaseMCPServer("TestServer", "1.0.0", config)

    @pytest.fixture
    def test_plugin(self):
        """Create a test plugin."""

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)
                self.tools = [
                    MCPTool(
                        name="test_tool",
                        description="Test tool",
                        input_schema={"type": "object"},
                    )
                ]
                self.resources = [
                    MCPResource(
                        uri="test://resource",
                        name="Test Resource",
                        description="Test resource",
                        mime_type="text/plain",
                    )
                ]
                self.prompts = [
                    MCPPrompt(
                        name="test_prompt", description="Test prompt", arguments=[]
                    )
                ]

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return self.tools

            def _create_resources(self) -> List[MCPResource]:
                return self.resources

            def _create_prompts(self) -> List[MCPPrompt]:
                return self.prompts

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return [{"type": "text", "text": f"Executed {name} with {arguments}"}]

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return [{"type": "text", "text": f"Read resource {uri}"}]

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {"content": f"Prompt {name}", "arguments": arguments}

        return TestPlugin({"test": True}, {})

    def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.name == "TestServer"
        assert server.version == "1.0.0"
        assert server.config["test"] is True
        assert len(server.plugins) == 0
        assert isinstance(server.registry, MCPPluginRegistry)

    def test_register_plugin(self, server, test_plugin):
        """Test plugin registration."""
        server.register_plugin("test_plugin", test_plugin)
        assert "test_plugin" in server.plugins
        assert server.plugins["test_plugin"] is test_plugin

    def test_get_server_info(self, server, test_plugin):
        """Test server info retrieval."""
        server.register_plugin("test_plugin", test_plugin)
        info = server.get_server_info()

        assert info["name"] == "TestServer"
        assert info["version"] == "1.0.0"
        assert info["plugins_count"] == 1
        assert "test_plugin" in info["plugins"]

    @pytest.mark.asyncio
    async def test_health_check(self, server, test_plugin):
        """Test health check functionality."""
        server.register_plugin("test_plugin", test_plugin)
        health = await server.health_check()

        assert health["server_status"] == "healthy"
        assert health["server_name"] == "TestServer"
        assert health["plugins_count"] == 1
        assert health["plugin_health"]["test_plugin"]["status"] == "healthy"

    def test_thread_id_generation(self, server):
        """Test thread ID generation."""
        thread_id = server._get_thread_id()
        assert isinstance(thread_id, str)
        assert len(thread_id) > 0


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_checkpoint(self):
        """Test checkpoint creation."""
        checkpoint = create_checkpoint(
            plugin_name="test_plugin",
            tool_name="test_tool",
            input_state={"input": "test"},
            output_state={"result": "success"},
            execution_time=0.1,
            thread_id="12345",
            metadata={"test": True},
        )

        assert checkpoint.plugin_name == "test_plugin"
        assert checkpoint.tool_name == "test_tool"
        assert checkpoint.input_state["input"] == "test"
        assert checkpoint.output_state["result"] == "success"
        assert checkpoint.execution_time == 0.1
        assert checkpoint.thread_id == "12345"
        assert checkpoint.metadata["test"] is True
        assert isinstance(checkpoint.timestamp, datetime)

    def test_validate_plugin_interface(self):
        """Test plugin interface validation."""

        class ValidPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        # Should not raise any exception
        validate_plugin_interface(ValidPlugin)

    def test_validate_plugin_interface_invalid(self):
        """Test plugin interface validation with invalid plugin."""

        class InvalidPlugin:
            pass

        with pytest.raises(
            ValueError, match="InvalidPlugin must inherit from MCPPlugin"
        ):
            validate_plugin_interface(InvalidPlugin)


# ============================================================================
# Property-Based Tests
# ============================================================================


class TestPropertyBased:
    """Property-based tests for complex behaviors."""

    def test_checkpoint_roundtrip(self):
        """Test that checkpoint data can be round-tripped correctly."""
        original_data = {
            "plugin_name": "test_plugin",
            "tool_name": "test_tool",
            "input_state": {"complex": {"nested": {"data": [1, 2, 3]}}},
            "output_state": {"result": "success", "metadata": {"count": 42}},
            "execution_time": 0.123456,
            "thread_id": "thread_12345",
            "metadata": {"test": True, "nested": {"value": "test"}},
        }

        checkpoint = create_checkpoint(**original_data)

        # Verify all data is preserved
        assert checkpoint.plugin_name == original_data["plugin_name"]
        assert checkpoint.tool_name == original_data["tool_name"]
        assert checkpoint.input_state == original_data["input_state"]
        assert checkpoint.output_state == original_data["output_state"]
        assert checkpoint.execution_time == original_data["execution_time"]
        assert checkpoint.thread_id == original_data["thread_id"]
        assert checkpoint.metadata == original_data["metadata"]

    def test_registry_plugin_lifecycle(self):
        """Test complete plugin lifecycle in registry."""
        registry = MCPPluginRegistry()

        class TestPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)
                self.initialized = True

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return []

            def _create_resources(self) -> List[MCPResource]:
                return []

            def _create_prompts(self) -> List[MCPPrompt]:
                return []

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                return {}

        # Register plugin
        registry.register_plugin_class(TestPlugin, name="test_plugin")

        # Create instance
        config = {"test": True}
        dependencies = {}
        instance = registry.create_plugin_instance("test_plugin", config, dependencies)

        # Verify instance
        assert isinstance(instance, TestPlugin)
        assert instance.initialized is True
        assert instance.config["test"] is True

        # Get same instance again
        instance2 = registry.get_plugin_instance("test_plugin")
        assert instance is instance2

        # Unregister plugin
        registry.unregister_plugin("test_plugin")
        assert "test_plugin" not in registry._plugins

        # Verify instance is removed when plugin is unregistered
        instance3 = registry.get_plugin_instance("test_plugin")
        assert instance3 is None


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for the complete MCP core system."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test a complete MCP workflow from plugin to server."""
        # Create registry
        registry = MCPPluginRegistry()

        # Define plugin
        class WorkflowPlugin(MCPPlugin):
            def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
                super().__init__(config, dependencies)
                self.tools = [
                    MCPTool(
                        name="process_data",
                        description="Process input data",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "input": {"type": "string"},
                                "options": {"type": "object"},
                            },
                        },
                    )
                ]
                self.resources = [
                    MCPResource(
                        uri="workflow://data/1",
                        name="Workflow Data",
                        description="Workflow data resource",
                        mime_type="application/json",
                    )
                ]
                self.prompts = [
                    MCPPrompt(
                        name="workflow_prompt",
                        description="Workflow prompt",
                        arguments=[{"name": "context", "type": "string"}],
                    )
                ]

            def _validate_dependencies(self) -> None:
                pass

            def _create_tools(self) -> List[MCPTool]:
                return self.tools

            def _create_resources(self) -> List[MCPResource]:
                return self.resources

            def _create_prompts(self) -> List[MCPPrompt]:
                return self.prompts

            async def execute_tool(
                self, name: str, arguments: Dict[str, Any]
            ) -> List[Dict[str, Any]]:
                if name == "process_data":
                    input_data = arguments.get("input", "")
                    return [{"type": "text", "text": f"Processed: {input_data}"}]
                return []

            async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
                if uri == "workflow://data/1":
                    return [{"type": "text", "text": "Workflow data content"}]
                return []

            async def get_prompt_content(
                self, name: str, arguments: Optional[Dict[str, Any]]
            ) -> Dict[str, Any]:
                if name == "workflow_prompt":
                    context = arguments.get("context", "") if arguments else ""
                    return {"content": f"Workflow prompt with context: {context}"}
                return {}

        # Register plugin
        registry.register_plugin_class(WorkflowPlugin, name="workflow")

        # Create server
        server = BaseMCPServer("WorkflowServer", "1.0.0", {"workflow": True})

        # Register plugin with server
        config = {"workflow_config": True}
        dependencies = {}
        plugin = registry.get_or_create_instance("workflow", config, dependencies)
        server.register_plugin("workflow", plugin)

        # Test server functionality
        info = server.get_server_info()
        assert info["plugins_count"] == 1
        assert "workflow" in info["plugins"]

        health = await server.health_check()
        assert health["server_status"] == "healthy"
        assert health["plugin_health"]["workflow"]["status"] == "healthy"

        # Test plugin functionality through server
        tools = await plugin.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "process_data"

        resources = await plugin.get_resources()
        assert len(resources) == 1
        assert resources[0].uri == "workflow://data/1"

        prompts = await plugin.get_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "workflow_prompt"

        # Test tool execution
        result = await plugin.execute_tool("process_data", {"input": "test data"})
        assert len(result) == 1
        assert result[0]["text"] == "Processed: test data"

        # Test resource reading
        resource_result = await plugin.read_resource("workflow://data/1")
        assert len(resource_result) == 1
        assert resource_result[0]["text"] == "Workflow data content"

        # Test prompt retrieval
        prompt_result = await plugin.get_prompt_content(
            "workflow_prompt", {"context": "test context"}
        )
        assert prompt_result["content"] == "Workflow prompt with context: test context"
