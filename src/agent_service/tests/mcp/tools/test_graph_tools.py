"""
Test Suite for Enhanced Graph Tools

Comprehensive tests for graph-based MCP tools that wrap LangGraph builders.
"""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agent_service.mcp.tools.base import EffectBoundary, ToolBackend
from agent_service.mcp.tools.graph_tools import (
    GraphTool,
    GraphToolConfig,
    GraphToolFactory,
    JournalSummaryGraphTool,
    PerformanceReviewGraphTool,
)


class MockGraphBuilder:
    """Mock graph builder for testing."""

    def __init__(self, name: str = "mock_graph", description: str = "Mock graph"):
        self.name = name
        self.description = description
        self.nodes = {"mock_node": Mock()}
        self.graph = Mock()

    def build(self):
        """Build the mock graph."""
        return Mock()

    def list_nodes(self) -> List[str]:
        """List available nodes."""
        return list(self.nodes.keys())

    def get_node(self, name: str):
        """Get a node by name."""
        return self.nodes.get(name)


class TestGraphToolConfig:
    """Test GraphToolConfig functionality."""

    def test_config_creation(self):
        """Test config creation with valid data."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test", "graph"],
            effect_boundary=EffectBoundary.LLM,
            subtools=["node1", "node2"],
        )

        assert config.name == "test_graph"
        assert config.description == "A test graph"
        assert config.owner_domain == "test"
        assert config.version == "1.0.0"
        assert "test" in config.tags
        assert config.effect_boundary == EffectBoundary.LLM
        assert "node1" in config.subtools


class TestGraphTool:
    """Test base GraphTool functionality."""

    def test_graph_tool_creation(self):
        """Test graph tool creation."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test"],
            effect_boundary=EffectBoundary.LLM,
            subtools=[],
        )

        tool = GraphTool(config, MockGraphBuilder, name="test")
        assert tool is not None
        assert tool.owner_domain == "test"
        assert tool.version == "1.0.0"

    def test_graph_tool_metadata(self):
        """Test graph tool metadata."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test"],
            effect_boundary=EffectBoundary.LLM,
            subtools=[],
        )

        tool = GraphTool(config, MockGraphBuilder, name="test")
        metadata = tool.get_metadata()

        assert metadata.name == "test_graph"
        assert metadata.description == "A test graph"
        assert metadata.backend == ToolBackend.LANGGRAPH
        assert metadata.owner_domain == "test"
        assert metadata.version == "1.0.0"

    def test_list_subtools(self):
        """Test listing subtools."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test"],
            effect_boundary=EffectBoundary.LLM,
            subtools=[],
        )

        tool = GraphTool(config, MockGraphBuilder, name="test")
        subtools = tool.list_subtools()

        assert "mock_node" in subtools

    @pytest.mark.asyncio
    async def test_execute_subtool(self):
        """Test executing a subtool."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test"],
            effect_boundary=EffectBoundary.LLM,
            subtools=[],
        )

        tool = GraphTool(config, MockGraphBuilder, name="test")

        # Mock the node's ainvoke method
        mock_node = Mock()
        mock_node.ainvoke = AsyncMock(return_value={"result": "success"})

        with patch.object(tool, "_get_graph_builder") as mock_get_builder:
            mock_builder = Mock()
            mock_builder.get_node.return_value = mock_node
            mock_get_builder.return_value = mock_builder

            result = await tool.execute_subtool("mock_node", {"test": "data"})

            assert result == {"result": "success"}
            mock_node.ainvoke.assert_called_once_with({"test": "data"})

    @pytest.mark.asyncio
    async def test_execute_subtool_not_found(self):
        """Test executing a non-existent subtool."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test"],
            effect_boundary=EffectBoundary.LLM,
            subtools=[],
        )

        tool = GraphTool(config, MockGraphBuilder, name="test")

        with pytest.raises(ValueError, match="Subtool non_existent not found"):
            await tool.execute_subtool("non_existent", {})

    @pytest.mark.asyncio
    async def test_execute_graph_tool_success(self):
        """Test successful graph execution."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test"],
            effect_boundary=EffectBoundary.LLM,
            subtools=[],
        )

        tool = GraphTool(config, MockGraphBuilder, name="test")

        # Mock the compiled graph
        mock_graph = Mock()
        mock_graph.ainvoke = AsyncMock(return_value={"summary": "test summary"})

        with patch.object(tool, "_get_compiled_graph") as mock_get_graph:
            mock_get_graph.return_value = mock_graph

            result = await tool.execute({"journal_entries": []})

            assert len(result) == 1
            assert result[0]["type"] == "graph_result"
            assert result[0]["graph_name"] == "test_graph"
            assert result[0]["result"] == {"summary": "test summary"}
            assert result[0]["arguments"] == {"journal_entries": []}

    @pytest.mark.asyncio
    async def test_execute_graph_tool_error(self):
        """Test graph execution with error."""
        config = GraphToolConfig(
            name="test_graph",
            description="A test graph",
            input_schema={"type": "object"},
            output_schema={"type": "array"},
            owner_domain="test",
            version="1.0.0",
            tags=["test"],
            effect_boundary=EffectBoundary.LLM,
            subtools=[],
        )

        tool = GraphTool(config, MockGraphBuilder, name="test")

        # Mock the compiled graph to raise an exception
        mock_graph = Mock()
        mock_graph.ainvoke = AsyncMock(side_effect=Exception("Graph execution failed"))

        with patch.object(tool, "_get_compiled_graph") as mock_get_graph:
            mock_get_graph.return_value = mock_graph

            result = await tool.execute({"journal_entries": []})

            assert len(result) == 1
            assert result[0]["type"] == "error"
            assert result[0]["error"] == "Graph execution failed"
            assert result[0]["graph_name"] == "test_graph"


class TestJournalSummaryGraphTool:
    """Test JournalSummaryGraphTool functionality."""

    def test_journal_summary_tool_creation(self):
        """Test journal summary tool creation."""
        tool = JournalSummaryGraphTool()

        assert tool is not None
        assert tool.owner_domain == "journaling"
        assert tool.version == "2.1.0"

    def test_journal_summary_tool_metadata(self):
        """Test journal summary tool metadata."""
        tool = JournalSummaryGraphTool()
        metadata = tool.get_metadata()

        assert metadata.name == "journal_summary_graph"
        assert (
            metadata.description
            == "Generate journal summaries using LangGraph workflow"
        )
        assert metadata.backend == ToolBackend.LANGGRAPH
        assert metadata.owner_domain == "journaling"
        assert metadata.version == "2.1.0"
        assert "journal" in metadata.tags
        assert "summary" in metadata.tags
        assert "langgraph" in metadata.tags
        assert metadata.effect_boundary == EffectBoundary.LLM
        assert "summarizer" in metadata.subtools

    def test_journal_summary_tool_input_schema(self):
        """Test journal summary tool input schema."""
        tool = JournalSummaryGraphTool()
        input_schema = tool.input_schema

        assert input_schema["type"] == "object"
        assert "journal_entries" in input_schema["properties"]
        assert "style" in input_schema["properties"]
        assert "provider" in input_schema["properties"]
        assert "journal_entries" in input_schema["required"]

        # Check style enum
        style_prop = input_schema["properties"]["style"]
        assert style_prop["type"] == "string"
        assert "concise" in style_prop["enum"]
        assert "detailed" in style_prop["enum"]
        assert "analytical" in style_prop["enum"]


class TestPerformanceReviewGraphTool:
    """Test PerformanceReviewGraphTool functionality."""

    def test_performance_review_tool_creation(self):
        """Test performance review tool creation."""
        tool = PerformanceReviewGraphTool()

        assert tool is not None
        assert tool.owner_domain == "review"
        assert tool.version == "1.0.0"

    def test_performance_review_tool_metadata(self):
        """Test performance review tool metadata."""
        tool = PerformanceReviewGraphTool()
        metadata = tool.get_metadata()

        assert metadata.name == "performance_review_graph"
        assert (
            metadata.description
            == "Generate performance reviews using LangGraph workflow"
        )
        assert metadata.backend == ToolBackend.LANGGRAPH
        assert metadata.owner_domain == "review"
        assert metadata.version == "1.0.0"
        assert "review" in metadata.tags
        assert "performance" in metadata.tags
        assert "langgraph" in metadata.tags
        assert metadata.effect_boundary == EffectBoundary.LLM
        assert "analyzer" in metadata.subtools
        assert "evaluator" in metadata.subtools

    def test_performance_review_tool_input_schema(self):
        """Test performance review tool input schema."""
        tool = PerformanceReviewGraphTool()
        input_schema = tool.input_schema

        assert input_schema["type"] == "object"
        assert "journal_entries" in input_schema["properties"]
        assert "period" in input_schema["properties"]
        assert "focus_areas" in input_schema["properties"]
        assert "provider" in input_schema["properties"]
        assert "journal_entries" in input_schema["required"]
        assert "period" in input_schema["required"]

        # Check period enum
        period_prop = input_schema["properties"]["period"]
        assert period_prop["type"] == "string"
        assert "week" in period_prop["enum"]
        assert "month" in period_prop["enum"]
        assert "quarter" in period_prop["enum"]
        assert "year" in period_prop["enum"]


class TestGraphToolFactory:
    """Test GraphToolFactory functionality."""

    def test_create_journal_summary_tool(self):
        """Test creating journal summary tool."""
        tool = GraphToolFactory.create_journal_summary_tool(
            provider="openai", overrides={"temperature": 0.7}
        )

        assert isinstance(tool, JournalSummaryGraphTool)
        assert tool.owner_domain == "journaling"
        assert tool.version == "2.1.0"

    def test_create_performance_review_tool(self):
        """Test creating performance review tool."""
        tool = GraphToolFactory.create_performance_review_tool(
            provider="anthropic", overrides={"max_tokens": 1000}
        )

        assert isinstance(tool, PerformanceReviewGraphTool)
        assert tool.owner_domain == "review"
        assert tool.version == "1.0.0"

    def test_list_available_tools(self):
        """Test listing available tools."""
        tools = GraphToolFactory.list_available_tools()

        assert "journal_summary_graph" in tools
        assert "performance_review_graph" in tools
        assert len(tools) == 2

    def test_get_tool_metadata(self):
        """Test getting tool metadata."""
        # Test journal summary tool metadata
        metadata = GraphToolFactory.get_tool_metadata("journal_summary_graph")
        assert metadata is not None
        assert metadata.name == "journal_summary_graph"
        assert metadata.owner_domain == "journaling"

        # Test performance review tool metadata
        metadata = GraphToolFactory.get_tool_metadata("performance_review_graph")
        assert metadata is not None
        assert metadata.name == "performance_review_graph"
        assert metadata.owner_domain == "review"

        # Test non-existent tool
        metadata = GraphToolFactory.get_tool_metadata("non_existent")
        assert metadata is None


class TestGraphToolIntegration:
    """Test graph tool integration with registry."""

    def test_graph_tool_registration(self):
        """Test registering graph tools in registry."""
        from agent_service.mcp.tools.base import ToolRegistry

        registry = ToolRegistry()

        # Register journal summary tool
        journal_tool = JournalSummaryGraphTool()
        registry.register(journal_tool)

        # Register performance review tool
        review_tool = PerformanceReviewGraphTool()
        registry.register(review_tool)

        # Check registration
        assert len(registry.list_tool_names()) == 2
        assert "journal_summary_graph" in registry.list_tool_names()
        assert "performance_review_graph" in registry.list_tool_names()

        # Check filtering by domain
        journaling_tools = registry.list_tools(owner_domain="journaling")
        assert len(journaling_tools) == 1
        assert journaling_tools[0].name == "journal_summary_graph"

        review_tools = registry.list_tools(owner_domain="review")
        assert len(review_tools) == 1
        assert review_tools[0].name == "performance_review_graph"

        # Check filtering by backend
        langgraph_tools = registry.list_tools(backend="langgraph")
        assert len(langgraph_tools) == 2

        # Check filtering by tags
        summary_tools = registry.list_tools(tags=["summary"])
        assert len(summary_tools) == 1
        assert summary_tools[0].name == "journal_summary_graph"

        performance_tools = registry.list_tools(tags=["performance"])
        assert len(performance_tools) == 1
        assert performance_tools[0].name == "performance_review_graph"
