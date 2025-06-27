"""
Test Suite for MCP Tool Base Classes

Comprehensive tests for the tool orchestration layer base classes.
"""

import pytest
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock

from agent_service.mcp.tools.base import (
    MCPTool,
    ToolMetadata,
    ToolRegistry,
    ToolBackend,
    EffectBoundary
)


class MockTool(MCPTool):
    """Mock tool for testing."""
    
    def __init__(self, name: str = "mock_tool", description: str = "A mock tool"):
        self._name = name
        self._description = description
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the mock tool."""
        return [{"type": "text", "text": f"Mock result for {self._name}"}]
    
    def get_metadata(self) -> ToolMetadata:
        """Get mock tool metadata."""
        return ToolMetadata(
            name=self._name,
            description=self._description,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "text": {"type": "string"}
                    }
                }
            },
            backend=ToolBackend.PROMPT,
            tags=frozenset(["test", "mock"]),
            effect_boundary=EffectBoundary.LLM
        )


class TestToolMetadata:
    """Test ToolMetadata functionality."""
    
    def test_metadata_creation(self):
        """Test metadata creation with valid data."""
        metadata = ToolMetadata(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
            output_schema={"type": "array", "items": {"type": "object"}},
            backend=ToolBackend.LANGGRAPH,
            tags=frozenset(["test", "langgraph"]),
            effect_boundary=EffectBoundary.LLM
        )
        
        assert metadata.name == "test_tool"
        assert metadata.description == "A test tool"
        assert metadata.backend == ToolBackend.LANGGRAPH
        assert "test" in metadata.tags
        assert "langgraph" in metadata.tags
        assert metadata.effect_boundary == EffectBoundary.LLM
    
    def test_metadata_defaults(self):
        """Test metadata creation with defaults."""
        metadata = ToolMetadata(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
            output_schema={"type": "array", "items": {"type": "object"}},
            backend=ToolBackend.PROMPT
        )
        
        assert metadata.tags == frozenset()
        assert metadata.effect_boundary == EffectBoundary.LLM
        assert metadata.version == "1.0.0"
        assert metadata.owner_domain == "default"


class TestMCPTool:
    """Test MCPTool base class functionality."""
    
    def test_tool_creation(self):
        """Test tool creation."""
        tool = MockTool()
        assert tool is not None
        assert isinstance(tool, MCPTool)
    
    def test_tool_metadata(self):
        """Test tool metadata retrieval."""
        tool = MockTool("test_tool", "A test tool")
        metadata = tool.get_metadata()
        
        assert metadata.name == "test_tool"
        assert metadata.description == "A test tool"
        assert metadata.backend == ToolBackend.PROMPT
    
    def test_argument_validation_valid(self):
        """Test argument validation with valid arguments."""
        tool = MockTool()
        arguments = {"query": "test query"}
        
        assert tool.validate_arguments(arguments) is True
    
    def test_argument_validation_invalid(self):
        """Test argument validation with invalid arguments."""
        tool = MockTool()
        arguments = {"wrong_field": "test"}
        
        assert tool.validate_arguments(arguments) is False
    
    def test_argument_validation_empty(self):
        """Test argument validation with empty arguments."""
        tool = MockTool()
        arguments = {}
        
        assert tool.validate_arguments(arguments) is False
    
    @pytest.mark.asyncio
    async def test_execute_with_validation_valid(self):
        """Test execute with validation using valid arguments."""
        tool = MockTool()
        arguments = {"query": "test query"}
        
        result = await tool.execute_with_validation(arguments)
        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "Mock result" in result[0]["text"]
    
    @pytest.mark.asyncio
    async def test_execute_with_validation_invalid(self):
        """Test execute with validation using invalid arguments."""
        tool = MockTool()
        arguments = {"wrong_field": "test"}
        
        with pytest.raises(ValueError, match="Invalid arguments"):
            await tool.execute_with_validation(arguments)


class TestToolRegistry:
    """Test ToolRegistry functionality."""
    
    def test_registry_creation(self):
        """Test registry creation."""
        registry = ToolRegistry()
        assert registry is not None
        assert len(registry.list_tool_names()) == 0
    
    def test_tool_registration(self):
        """Test tool registration."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        
        assert len(registry.list_tool_names()) == 1
        assert "mock_tool" in registry.list_tool_names()
    
    def test_tool_registration_duplicate(self):
        """Test duplicate tool registration with versioning."""
        registry = ToolRegistry()
        tool1 = MockTool("test_tool", "First tool")
        tool2 = MockTool("test_tool", "Second tool")
        
        # With versioning, duplicate names are allowed
        registry.register(tool1)
        registry.register(tool2)  # This should work now
        
        # Both tools should be registered (with different versions)
        assert len(registry.list_tool_names()) == 1  # Same name
        assert registry.get_tool("test_tool") is not None  # Should get latest version
    
    def test_tool_registration_invalid(self):
        """Test registration of invalid tool."""
        registry = ToolRegistry()
        
        with pytest.raises(ValueError, match="must implement MCPTool"):
            registry.register("not a tool")
    
    def test_tool_registration_none(self):
        """Test registration of None tool."""
        registry = ToolRegistry()
        
        with pytest.raises(ValueError, match="must implement MCPTool"):
            registry.register(None)
    
    def test_tool_unregistration(self):
        """Test tool unregistration."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        assert len(registry.list_tool_names()) == 1
        
        registry.unregister("mock_tool")
        assert len(registry.list_tool_names()) == 0
    
    def test_get_tool(self):
        """Test getting a tool by name."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        retrieved_tool = registry.get_tool("mock_tool")
        
        assert retrieved_tool is tool
    
    def test_get_tool_not_found(self):
        """Test getting a non-existent tool."""
        registry = ToolRegistry()
        
        tool = registry.get_tool("non_existent")
        assert tool is None
    
    def test_get_tool_metadata(self):
        """Test getting tool metadata."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        metadata = registry.get_tool_metadata("mock_tool")
        
        assert metadata is not None
        assert metadata.name == "mock_tool"
        assert metadata.description == "A mock tool"
    
    def test_get_tool_metadata_not_found(self):
        """Test getting metadata for non-existent tool."""
        registry = ToolRegistry()
        
        metadata = registry.get_tool_metadata("non_existent")
        assert metadata is None
    
    def test_list_tools_no_filter(self):
        """Test listing tools without filters."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1", "First tool")
        tool2 = MockTool("tool2", "Second tool")
        
        registry.register(tool1)
        registry.register(tool2)
        
        tools = registry.list_tools()
        assert len(tools) == 2
        assert any(t.name == "tool1" for t in tools)
        assert any(t.name == "tool2" for t in tools)
    
    def test_list_tools_by_backend(self):
        """Test listing tools filtered by backend."""
        registry = ToolRegistry()
        
        # Create tools with different backends
        class MockTool1(MockTool):
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name=self._name,
                    description=self._description,
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    },
                    output_schema={
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "text": {"type": "string"}
                            }
                        }
                    },
                    backend=ToolBackend.PROMPT,
                    tags=frozenset(["test", "mock"]),
                    effect_boundary=EffectBoundary.LLM
                )
        
        class MockTool2(MockTool):
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name=self._name,
                    description=self._description,
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    },
                    output_schema={
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "text": {"type": "string"}
                            }
                        }
                    },
                    backend=ToolBackend.LANGGRAPH,
                    tags=frozenset(["test", "mock"]),
                    effect_boundary=EffectBoundary.LLM
                )
        
        tool1 = MockTool1("tool1", "First tool")
        tool2 = MockTool2("tool2", "Second tool")
        
        registry.register(tool1)
        registry.register(tool2)
        
        prompt_tools = registry.list_tools(backend="prompt")
        assert len(prompt_tools) == 1
        assert prompt_tools[0].name == "tool1"
    
    def test_list_tools_by_tags(self):
        """Test listing tools filtered by tags."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1", "First tool")
        tool2 = MockTool("tool2", "Second tool")
        
        registry.register(tool1)
        registry.register(tool2)
        
        test_tools = registry.list_tools(tags=["test"])
        assert len(test_tools) == 2
        
        mock_tools = registry.list_tools(tags=["mock"])
        assert len(mock_tools) == 2
    
    def test_get_tools_by_backend(self):
        """Test getting tools by backend."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1", "First tool")
        tool2 = MockTool("tool2", "Second tool")
        
        registry.register(tool1)
        registry.register(tool2)
        
        prompt_tools = registry.get_tools_by_backend(ToolBackend.PROMPT)
        assert len(prompt_tools) == 2
    
    def test_get_tools_by_effect_boundary(self):
        """Test getting tools by effect boundary."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1", "First tool")
        tool2 = MockTool("tool2", "Second tool")
        
        registry.register(tool1)
        registry.register(tool2)
        
        llm_tools = registry.get_tools_by_effect_boundary(EffectBoundary.LLM)
        assert len(llm_tools) == 2
    
    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test tool execution."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        
        result = await registry.execute_tool("mock_tool", {"query": "test"})
        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "Mock result" in result[0]["text"]
    
    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """Test executing non-existent tool."""
        registry = ToolRegistry()
        
        with pytest.raises(ValueError, match="not found"):
            await registry.execute_tool("non_existent", {})
    
    @pytest.mark.asyncio
    async def test_execute_tool_invalid_arguments(self):
        """Test tool execution with invalid arguments."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        
        # The registry doesn't validate arguments, it just calls the tool
        # So we need to test the tool's validation directly
        with pytest.raises(ValueError, match="Invalid arguments"):
            await tool.execute_with_validation({"wrong_field": "test"})
    
    def test_export_to_yaml(self):
        """Test YAML export functionality."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        
        yaml_content = registry.export_to_yaml()
        assert "tools:" in yaml_content
        assert "name: mock_tool" in yaml_content
        assert "description: A mock tool" in yaml_content
    
    def test_health_check(self):
        """Test health check functionality."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        
        health = registry.health_check()
        assert health["status"] == "healthy"
        assert health["total_tools"] == 1
        assert "prompt" in health["backends"]
        assert health["backends"]["prompt"] == 1
        assert "llm" in health["effect_boundaries"]
        assert health["effect_boundaries"]["llm"] == 1


class TestToolBackend:
    """Test ToolBackend enum."""
    
    def test_backend_values(self):
        """Test backend enum values."""
        assert ToolBackend.LANGGRAPH.value == "langgraph"
        assert ToolBackend.PROMPT.value == "prompt"
        assert ToolBackend.RETRIEVER.value == "retriever"
        assert ToolBackend.HYBRID.value == "hybrid"
        assert ToolBackend.EXTERNAL.value == "external"


class TestEffectBoundary:
    """Test EffectBoundary enum."""
    
    def test_boundary_values(self):
        """Test effect boundary enum values."""
        assert EffectBoundary.PURE.value == "pure"
        assert EffectBoundary.RETRIEVER.value == "retriever"
        assert EffectBoundary.LLM.value == "llm"
        assert EffectBoundary.EXTERNAL.value == "external" 