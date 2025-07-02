"""
Enhanced LLMService Tests

Comprehensive tests for the enhanced LLMService with MCP tool registry integration.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agent_service.app.graphql.types.suggestion_types import PerformanceReview
from agent_service.app.services.llm_service import LLMService
from agent_service.mcp.tools.base import (
    EffectBoundary,
    MCPTool,
    ToolBackend,
    ToolMetadata,
    ToolRegistry,
)


class MockTool(MCPTool):
    """Mock tool for testing."""

    def __init__(self, name: str = "mock_tool", description: str = "A mock tool"):
        self._name = name
        self._description = description

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the mock tool."""
        if "invalid" in arguments:
            raise ValueError("Invalid arguments")

        return [{"type": "text", "text": f"Mock result for {self._name}"}]

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self._name,
            description=self._description,
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "text": {"type": "string"},
                    },
                },
            },
            backend=ToolBackend.PROMPT,
            tags=frozenset(["test", "mock"]),
            effect_boundary=EffectBoundary.LLM,
        )

    def list_subtools(self) -> List[str]:
        """List available subtools."""
        return ["subtool1", "subtool2"]

    async def execute_subtool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a subtool."""
        if name == "subtool1":
            return {"result": "subtool1_result"}
        elif name == "subtool2":
            return {"result": "subtool2_result"}
        raise ValueError(f"Unknown subtool: {name}")


class MockJournalTool(MockTool):
    """Mock journal summary tool."""

    def __init__(self):
        super().__init__("journal_summary_graph", "Journal summary tool")

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the journal summary tool."""
        journal_entries = arguments.get("journal_entries", [])
        style = arguments.get("style", "concise")

        if not journal_entries:
            return [{"summary": "No entries to summarize"}]

        return [
            {"summary": f"Summary of {len(journal_entries)} entries in {style} style"}
        ]

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self._name,
            description=self._description,
            input_schema={
                "type": "object",
                "properties": {
                    "journal_entries": {"type": "array", "items": {"type": "object"}},
                    "style": {"type": "string", "enum": ["concise", "detailed"]},
                },
                "required": ["journal_entries"],
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"summary": {"type": "string"}},
                },
            },
            backend=ToolBackend.LANGGRAPH,
            owner_domain="journaling",
            version="2.1.0",
            tags=frozenset(["journal", "summary"]),
            effect_boundary=EffectBoundary.LLM,
        )


class MockPerformanceReviewTool(MockTool):
    """Mock performance review tool."""

    def __init__(self):
        super().__init__("performance_review_graph", "Performance review tool")

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the performance review tool."""
        journal_entries = arguments.get("journal_entries", [])
        period = arguments.get("period", "month")

        if not journal_entries:
            return [{"review": "No entries to review"}]

        # Return a properly formatted review string that can be parsed
        review_text = f"SUCCESS: Performance review for {len(journal_entries)} entries over {period}\nIMPROVEMENT: Consider adding more detailed entries\nPROMPT: What would you like to focus on next?"
        return [{"review": review_text}]

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self._name,
            description=self._description,
            input_schema={
                "type": "object",
                "properties": {
                    "journal_entries": {"type": "array", "items": {"type": "object"}},
                    "period": {
                        "type": "string",
                        "enum": ["week", "month", "quarter", "year"],
                    },
                },
                "required": ["journal_entries"],
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"review": {"type": "string"}},
                },
            },
            backend=ToolBackend.LANGGRAPH,
            owner_domain="review",
            version="1.0.0",
            tags=frozenset(["review", "performance"]),
            effect_boundary=EffectBoundary.LLM,
        )


class TestLLMServiceEnhanced:
    """Test enhanced LLMService with tool registry integration."""

    @pytest.fixture
    def mock_tool_registry(self):
        """Create a mock tool registry."""
        registry = ToolRegistry()

        # Register mock tools
        journal_tool = MockJournalTool()
        review_tool = MockPerformanceReviewTool()
        generic_tool = MockTool()

        registry.register(journal_tool)
        registry.register(review_tool)
        registry.register(generic_tool)

        return registry

    @pytest.fixture
    def mock_prompt_service(self):
        """Create a mock prompt service."""
        service = Mock()
        service.render_prompt = Mock(return_value="Mock rendered prompt")
        service.get_prompt = Mock(return_value=Mock(metadata={"model": "gpt-4o"}))
        service.health_check = Mock(return_value={"status": "healthy"})
        return service

    @pytest.fixture
    def mock_provider_manager(self):
        """Create a mock provider manager."""
        manager = Mock()
        manager.create_model_with_fallback = Mock(return_value=Mock())
        manager.get_provider_status = Mock(return_value={"openai": "healthy"})
        manager.list_available_providers = Mock(return_value=["openai", "ollama"])
        manager.get_working_providers = Mock(return_value=["openai"])
        return manager

    @pytest.fixture
    def enhanced_llm_service(
        self, mock_tool_registry, mock_prompt_service, mock_provider_manager
    ):
        """Create an enhanced LLMService instance."""
        return LLMService(
            prompt_service=mock_prompt_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_tool_registry,
        )

    def test_enhanced_llm_service_creation(self, enhanced_llm_service):
        """Test enhanced LLMService creation with tool registry."""
        assert enhanced_llm_service.tool_registry is not None
        assert len(enhanced_llm_service.list_tool_names()) == 3

    def test_enhanced_llm_service_creation_with_global_registry(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test LLMService creation with global tool registry."""
        # Clear global registry
        from agent_service.mcp.tools.base import set_global_registry

        set_global_registry(ToolRegistry())

        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        assert service.tool_registry is not None
        assert len(service.list_tool_names()) == 0  # Empty global registry

    @pytest.mark.asyncio
    async def test_execute_tool(self, enhanced_llm_service):
        """Test tool execution."""
        result = await enhanced_llm_service.execute_tool("mock_tool", {"query": "test"})

        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "Mock result" in result[0]["text"]

    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self, enhanced_llm_service):
        """Test executing non-existent tool."""
        with pytest.raises(ValueError, match="not found"):
            await enhanced_llm_service.execute_tool("non_existent", {})

    @pytest.mark.asyncio
    async def test_execute_tool_with_version(self, enhanced_llm_service):
        """Test tool execution with specific version."""
        # This would require a tool with multiple versions
        # For now, test that it doesn't crash
        result = await enhanced_llm_service.execute_tool(
            "mock_tool", {"query": "test"}, version="1.0.0"
        )
        assert len(result) == 1

    def test_get_tool_metadata(self, enhanced_llm_service):
        """Test getting tool metadata."""
        metadata = enhanced_llm_service.get_tool_metadata("journal_summary_graph")

        assert metadata is not None
        assert metadata["name"] == "journal_summary_graph"
        assert metadata["owner_domain"] == "journaling"
        assert metadata["version"] == "2.1.0"
        assert metadata["backend"] == "langgraph"
        assert "journal" in metadata["tags"]

    def test_get_tool_metadata_not_found(self, enhanced_llm_service):
        """Test getting metadata for non-existent tool."""
        metadata = enhanced_llm_service.get_tool_metadata("non_existent")
        assert metadata is None

    def test_list_tools_no_filter(self, enhanced_llm_service):
        """Test listing tools without filters."""
        tools = enhanced_llm_service.list_tools()

        assert len(tools) == 3
        tool_names = [tool["name"] for tool in tools]
        assert "journal_summary_graph" in tool_names
        assert "performance_review_graph" in tool_names
        assert "mock_tool" in tool_names

    def test_list_tools_by_backend(self, enhanced_llm_service):
        """Test listing tools filtered by backend."""
        langgraph_tools = enhanced_llm_service.list_tools(backend="langgraph")
        assert len(langgraph_tools) == 2

        prompt_tools = enhanced_llm_service.list_tools(backend="prompt")
        assert len(prompt_tools) == 1

    def test_list_tools_by_domain(self, enhanced_llm_service):
        """Test listing tools filtered by domain."""
        journaling_tools = enhanced_llm_service.list_tools(owner_domain="journaling")
        assert len(journaling_tools) == 1
        assert journaling_tools[0]["name"] == "journal_summary_graph"

        review_tools = enhanced_llm_service.list_tools(owner_domain="review")
        assert len(review_tools) == 1
        assert review_tools[0]["name"] == "performance_review_graph"

    def test_list_tools_by_tags(self, enhanced_llm_service):
        """Test listing tools filtered by tags."""
        summary_tools = enhanced_llm_service.list_tools(tags=["summary"])
        assert len(summary_tools) == 1
        assert summary_tools[0]["name"] == "journal_summary_graph"

        performance_tools = enhanced_llm_service.list_tools(tags=["performance"])
        assert len(performance_tools) == 1
        assert performance_tools[0]["name"] == "performance_review_graph"

    def test_list_tool_names(self, enhanced_llm_service):
        """Test listing tool names."""
        names = enhanced_llm_service.list_tool_names()
        assert len(names) == 3
        assert "journal_summary_graph" in names
        assert "performance_review_graph" in names
        assert "mock_tool" in names

    @pytest.mark.asyncio
    async def test_execute_subtool(self, enhanced_llm_service):
        """Test subtool execution."""
        result = await enhanced_llm_service.execute_subtool(
            "mock_tool", "subtool1", {"arg": "value"}
        )

        assert result["result"] == "subtool1_result"

    @pytest.mark.asyncio
    async def test_execute_subtool_not_found(self, enhanced_llm_service):
        """Test executing non-existent subtool."""
        with pytest.raises(ValueError, match="not found"):
            await enhanced_llm_service.execute_subtool("mock_tool", "non_existent", {})

    @pytest.mark.asyncio
    async def test_execute_subtool_parent_not_found(self, enhanced_llm_service):
        """Test executing subtool of non-existent parent tool."""
        with pytest.raises(ValueError, match="not found"):
            await enhanced_llm_service.execute_subtool("non_existent", "subtool1", {})

    @pytest.mark.asyncio
    async def test_get_journal_summary_with_tool_registry(self, enhanced_llm_service):
        """Test journal summary using tool registry."""
        journal_entries = [{"text": "Entry 1"}, {"text": "Entry 2"}]

        result = await enhanced_llm_service.get_journal_summary(
            journal_entries, "concise"
        )

        assert "Summary of 2 entries in concise style" in result

    @pytest.mark.asyncio
    async def test_get_journal_summary_with_tool_registry_detailed(
        self, enhanced_llm_service
    ):
        """Test journal summary with detailed style."""
        journal_entries = [{"text": "Entry 1"}, {"text": "Entry 2"}]

        result = await enhanced_llm_service.get_journal_summary(
            journal_entries, "detailed"
        )

        assert "Summary of 2 entries in detailed style" in result

    @pytest.mark.asyncio
    async def test_get_journal_summary_empty_entries(self, enhanced_llm_service):
        """Test journal summary with empty entries."""
        result = await enhanced_llm_service.get_journal_summary([])

        # Fix: The LLMService returns fallback message for empty entries before trying tool registry
        assert "No recent journal entries to summarize" in result

    @pytest.mark.asyncio
    async def test_get_journal_summary_fallback_to_direct(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test journal summary fallback to direct prompt execution."""
        # Create service without tool registry
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        # Mock LLM response
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value.content = "Direct prompt summary"
        mock_provider_manager.create_model_with_fallback.return_value = mock_llm

        journal_entries = [{"text": "Entry 1"}]
        result = await service.get_journal_summary(journal_entries)

        assert "Direct prompt summary" in result
        mock_prompt_service.render_prompt.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_performance_review_with_tool_registry(
        self, enhanced_llm_service
    ):
        """Test performance review using tool registry."""
        journal_entries = [{"text": "Entry 1"}, {"text": "Entry 2"}]

        result = await enhanced_llm_service.get_performance_review(
            journal_entries, "month"
        )

        assert isinstance(result, PerformanceReview)
        # Fix: Check for the actual content from the mock tool
        assert "Performance review for 2 entries over month" in result.key_success

    @pytest.mark.asyncio
    async def test_get_performance_review_with_tool_registry_quarter(
        self, enhanced_llm_service
    ):
        """Test performance review with quarter period."""
        journal_entries = [{"text": "Entry 1"}, {"text": "Entry 2"}]

        result = await enhanced_llm_service.get_performance_review(
            journal_entries, "quarter"
        )

        assert isinstance(result, PerformanceReview)
        # Fix: Check for the actual content from the mock tool
        assert "Performance review for 2 entries over quarter" in result.key_success

    @pytest.mark.asyncio
    async def test_get_performance_review_empty_entries(self, enhanced_llm_service):
        """Test performance review with empty entries."""
        result = await enhanced_llm_service.get_performance_review([])

        assert isinstance(result, PerformanceReview)
        # Fix: The LLMService returns fallback message for empty entries before trying tool registry
        assert "No recent journal entries to review" in result.key_success

    @pytest.mark.asyncio
    async def test_get_performance_review_fallback_to_direct(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test performance review fallback to direct prompt execution."""
        # Create service without tool registry
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        # Mock LLM response for fallback
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value.content = (
            "SUCCESS: Fallback review\nIMPROVEMENT: More details\nPROMPT: What's next?"
        )
        mock_provider_manager.create_model_with_fallback.return_value = mock_llm

        journal_entries = [{"text": "Entry 1"}]
        result = await service.get_performance_review(journal_entries)

        assert isinstance(result, PerformanceReview)
        assert "Fallback review" in result.key_success
        mock_prompt_service.render_prompt.assert_called_once()

    def test_get_tool_registry_health(self, enhanced_llm_service):
        """Test tool registry health check."""
        health = enhanced_llm_service.get_tool_registry_health()

        assert health["status"] == "healthy"
        assert health["total_tools"] == 3
        assert health["unique_tools"] == 3
        assert "langgraph" in health["backends"]
        assert health["backends"]["langgraph"] == 2
        assert "prompt" in health["backends"]
        assert health["backends"]["prompt"] == 1

    def test_get_tool_registry_health_error(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test tool registry health check with error."""
        # Create a mock registry that raises an error
        mock_registry = Mock()
        mock_registry.health_check.side_effect = Exception("Registry error")

        service = LLMService(
            prompt_service=mock_prompt_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_registry,
        )

        health = service.get_tool_registry_health()

        assert health["status"] == "unhealthy"
        assert "Registry error" in health["error"]

    def test_enhanced_health_check(self, enhanced_llm_service):
        """Test enhanced health check including tool registry."""
        health = enhanced_llm_service.health_check()

        assert "tool_registry" in health
        assert health["tool_registry"]["status"] == "healthy"
        assert health["tool_registry"]["total_tools"] == 3

    def test_backward_compatibility(self, mock_prompt_service, mock_provider_manager):
        """Test backward compatibility with existing methods."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        # Test that existing methods still work
        assert service.get_prompt_service() == mock_prompt_service
        assert service.get_available_providers() == ["openai", "ollama"]
        assert service.get_working_providers() == ["openai"]

        # Test that tool registry is available even if not explicitly provided
        assert service.tool_registry is not None

    @pytest.mark.asyncio
    async def test_tool_execution_error_handling(self, enhanced_llm_service):
        """Test error handling in tool execution."""
        # Test with invalid arguments that cause tool to raise error
        with pytest.raises(ValueError, match="Invalid arguments"):
            await enhanced_llm_service.execute_tool("mock_tool", {"invalid": True})

    @pytest.mark.asyncio
    async def test_journal_summary_tool_registry_error_handling(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test error handling when tool registry fails."""
        # Create a mock registry that raises an error
        mock_registry = Mock()
        mock_registry.list_tool_names.return_value = ["journal_summary_graph"]
        mock_registry.execute_tool.side_effect = Exception("Tool execution failed")

        service = LLMService(
            prompt_service=mock_prompt_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_registry,
        )

        # Mock LLM response for fallback
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value.content = "Fallback summary"
        mock_provider_manager.create_model_with_fallback.return_value = mock_llm

        journal_entries = [{"text": "Entry 1"}]
        result = await service.get_journal_summary(journal_entries)

        # Should fallback to direct prompt execution
        assert "Fallback summary" in result
        mock_prompt_service.render_prompt.assert_called_once()

    @pytest.mark.asyncio
    async def test_performance_review_tool_registry_error_handling(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test error handling when tool registry fails for performance review."""
        # Create a mock registry that raises an error
        mock_registry = Mock()
        mock_registry.list_tool_names.return_value = ["performance_review_graph"]
        mock_registry.execute_tool.side_effect = Exception("Tool execution failed")

        service = LLMService(
            prompt_service=mock_prompt_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_registry,
        )

        # Mock LLM response for fallback
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value.content = (
            "SUCCESS: Fallback review\nIMPROVEMENT: More details\nPROMPT: What's next?"
        )
        mock_provider_manager.create_model_with_fallback.return_value = mock_llm

        journal_entries = [{"text": "Entry 1"}]
        result = await service.get_performance_review(journal_entries)

        # Should fallback to direct prompt execution
        assert isinstance(result, PerformanceReview)
        assert "Fallback review" in result.key_success
        mock_prompt_service.render_prompt.assert_called_once()


class TestLLMServiceIntegration:
    """Integration tests for LLMService with real tool registry."""

    @pytest.fixture
    def real_tool_registry(self):
        """Create a real tool registry with actual tools."""
        from agent_service.mcp.tools.graph_tools import (
            JournalSummaryGraphTool,
            PerformanceReviewGraphTool,
        )

        registry = ToolRegistry()

        # Register real graph tools
        journal_tool = JournalSummaryGraphTool()
        review_tool = PerformanceReviewGraphTool()

        registry.register(journal_tool)
        registry.register(review_tool)

        return registry

    @pytest.fixture
    def mock_prompt_service_integration(self):
        """Create a mock prompt service for integration tests."""
        service = Mock()
        service.render_prompt = Mock(return_value="Mock rendered prompt")
        service.get_prompt = Mock(return_value=Mock(metadata={"model": "gpt-4o"}))
        service.health_check = Mock(return_value={"status": "healthy"})
        return service

    @pytest.fixture
    def mock_provider_manager_integration(self):
        """Create a mock provider manager for integration tests."""
        manager = Mock()
        manager.create_model_with_fallback = Mock(return_value=Mock())
        manager.get_provider_status = Mock(return_value={"openai": "healthy"})
        manager.list_available_providers = Mock(return_value=["openai", "ollama"])
        manager.get_working_providers = Mock(return_value=["openai"])
        return manager

    @pytest.fixture
    def integration_llm_service(
        self,
        real_tool_registry,
        mock_prompt_service_integration,
        mock_provider_manager_integration,
    ):
        """Create LLMService with real tool registry."""
        return LLMService(
            prompt_service=mock_prompt_service_integration,
            provider_manager=mock_provider_manager_integration,
            tool_registry=real_tool_registry,
        )

    def test_integration_tool_registry_health(self, integration_llm_service):
        """Test health check with real tool registry."""
        health = integration_llm_service.get_tool_registry_health()

        assert health["status"] == "healthy"
        assert health["total_tools"] == 2
        assert health["unique_tools"] == 2
        assert "langgraph" in health["backends"]
        assert health["backends"]["langgraph"] == 2

    def test_integration_list_tools(self, integration_llm_service):
        """Test listing tools with real tool registry."""
        tools = integration_llm_service.list_tools()

        assert len(tools) == 2
        tool_names = [tool["name"] for tool in tools]
        assert "journal_summary_graph" in tool_names
        assert "performance_review_graph" in tool_names

        # Test filtering by domain
        journaling_tools = integration_llm_service.list_tools(owner_domain="journaling")
        assert len(journaling_tools) == 1
        assert journaling_tools[0]["name"] == "journal_summary_graph"

        review_tools = integration_llm_service.list_tools(owner_domain="review")
        assert len(review_tools) == 1
        assert review_tools[0]["name"] == "performance_review_graph"

    def test_integration_tool_metadata(self, integration_llm_service):
        """Test getting tool metadata with real tools."""
        journal_metadata = integration_llm_service.get_tool_metadata(
            "journal_summary_graph"
        )
        assert journal_metadata is not None
        assert journal_metadata["owner_domain"] == "journaling"
        assert journal_metadata["version"] == "2.1.0"

        review_metadata = integration_llm_service.get_tool_metadata(
            "performance_review_graph"
        )
        assert review_metadata is not None
        assert review_metadata["owner_domain"] == "review"
        assert review_metadata["version"] == "1.0.0"
