"""
Test Suite for Journal Plugin

Comprehensive tests for journal plugin with real retriever integration,
following TDD principles and property-based testing.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from langchain_core.documents import Document

from agent_service.mcp.core.base import (MCPPlugin, MCPPrompt, MCPResource,
                                         MCPTool)
from agent_service.mcp.plugins.journal.metadata import (JournalPluginMetadata,
                                                        PluginMetadata)
from agent_service.mcp.plugins.journal.server import JournalPlugin
from agent_service.mcp.retrievers.base import (Retriever, RetrieverMetadata,
                                               RetrieverRegistry)
from agent_service.mcp.retrievers.journal import (JournalRetriever,
                                                  JournalRetrieverFactory)

# ============================================================================
# Test Data
# ============================================================================


@pytest.fixture
def sample_journal_entries():
    """Sample journal entries for testing."""
    return [
        Mock(
            id="1",
            user_id="user123",
            entry_type="text",
            payload={"content": "Today was a productive day"},
            created_at=datetime.now() - timedelta(days=1),
            modified_at=None,
        ),
        Mock(
            id="2",
            user_id="user123",
            entry_type="mood",
            payload={"mood": "happy", "note": "Feeling great"},
            created_at=datetime.now() - timedelta(days=2),
            modified_at=None,
        ),
        Mock(
            id="3",
            user_id="user123",
            entry_type="goal",
            payload={
                "title": "Learn Python",
                "description": "Master Python programming",
                "status": "in_progress",
            },
            created_at=datetime.now() - timedelta(days=3),
            modified_at=None,
        ),
    ]


@pytest.fixture
def mock_journal_client(sample_journal_entries):
    """Mock journal client for testing."""
    client = Mock()
    client.list_by_user_for_period = AsyncMock(return_value=sample_journal_entries)
    return client


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    service = Mock()
    service.get_journal_summary = AsyncMock(return_value="Mock summary")
    service.get_performance_review = AsyncMock(return_value="Mock review")
    return service


@pytest.fixture
def retriever_registry():
    """Retriever registry for testing."""
    return RetrieverRegistry()


@pytest.fixture
def plugin_config():
    """Plugin configuration for testing."""
    return {
        "user_id": "user123",
        "default_time_period": "month",
        "max_entries_per_query": 100,
    }


@pytest.fixture
def plugin_dependencies(mock_journal_client, mock_llm_service, retriever_registry):
    """Plugin dependencies for testing."""
    return {
        "retriever_registry": retriever_registry,
        "llm_service": mock_llm_service,
        "journal_client": mock_journal_client,
    }


# ============================================================================
# Metadata Tests
# ============================================================================


class TestJournalPluginMetadata:
    """Test journal plugin metadata functionality."""

    def test_metadata_creation(self):
        """Test metadata creation with valid data."""
        metadata = JournalPluginMetadata.get_metadata()

        assert metadata.name == "journal_plugin"
        assert metadata.version == "1.0.0"
        assert (
            metadata.description
            == "Journal processing and analysis capabilities with real retriever integration"
        )
        assert "retriever_registry" in metadata.dependencies
        assert "llm_service" in metadata.dependencies
        assert "journal_client" in metadata.dependencies
        assert "journal" in metadata.tags
        assert "analysis" in metadata.tags
        assert "journal_summarization" in metadata.capabilities

    def test_tool_metadata(self):
        """Test tool metadata retrieval."""
        tool_metadata = JournalPluginMetadata.get_tool_metadata()

        assert "summarize_journals" in tool_metadata
        assert "generate_review" in tool_metadata
        assert "list_retrievers" in tool_metadata
        assert "get_entries_by_type" in tool_metadata

        summarize_tool = tool_metadata["summarize_journals"]
        assert summarize_tool["name"] == "summarize_journals"
        assert summarize_tool["uses_retriever"] is True
        assert "query" in summarize_tool["input_schema"]["properties"]

    def test_resource_metadata(self):
        """Test resource metadata retrieval."""
        user_id = "user123"
        resource_metadata = JournalPluginMetadata.get_resource_metadata(user_id)

        assert "retrievers" in resource_metadata
        assert "entries" in resource_metadata
        assert "user_entries" in resource_metadata

        user_entries = resource_metadata["user_entries"]
        assert user_id in user_entries["uri"]
        assert user_entries["metadata"]["user_specific"] is True

    def test_prompt_metadata(self):
        """Test prompt metadata retrieval."""
        prompt_metadata = JournalPluginMetadata.get_prompt_metadata()

        assert "summarize_journals" in prompt_metadata
        summarize_prompt = prompt_metadata["summarize_journals"]
        assert summarize_prompt["name"] == "summarize_journals"
        assert len(summarize_prompt["arguments"]) == 2


# ============================================================================
# Journal Plugin Tests
# ============================================================================


class TestJournalPlugin:
    """Test JournalPlugin functionality."""

    def test_plugin_initialization(self, plugin_config, plugin_dependencies):
        """Test plugin initialization with valid config and dependencies."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        assert plugin.user_id == "user123"
        assert plugin.retriever_registry is plugin_dependencies["retriever_registry"]
        assert plugin.llm_service is plugin_dependencies["llm_service"]
        assert plugin.journal_client is plugin_dependencies["journal_client"]
        assert plugin.journal_retriever is not None
        assert isinstance(plugin.journal_retriever, JournalRetriever)

    def test_plugin_initialization_missing_user_id(self, plugin_dependencies):
        """Test plugin initialization with missing user_id."""
        config = {"other_config": "value"}

        with pytest.raises(
            ValueError, match="JournalPlugin requires user_id in config"
        ):
            JournalPlugin(config, plugin_dependencies)

    def test_plugin_initialization_missing_dependencies(self, plugin_config):
        """Test plugin initialization with missing dependencies."""
        dependencies = {"retriever_registry": RetrieverRegistry()}

        with pytest.raises(
            ValueError, match="JournalPlugin requires llm_service dependency"
        ):
            JournalPlugin(plugin_config, dependencies)

    def test_plugin_initialization_invalid_registry(self, plugin_config):
        """Test plugin initialization with invalid retriever registry."""
        dependencies = {
            "retriever_registry": "invalid",
            "llm_service": Mock(),
            "journal_client": Mock(),
        }

        with pytest.raises(
            ValueError,
            match="retriever_registry must be an instance of RetrieverRegistry",
        ):
            JournalPlugin(plugin_config, dependencies)

    def test_plugin_metadata_inheritance(self, plugin_config, plugin_dependencies):
        """Test that plugin inherits metadata correctly."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        # Check that plugin has the expected metadata
        assert plugin.version == "1.0.0"
        assert (
            plugin.description
            == "Journal processing and analysis capabilities with real retriever integration"
        )
        assert "journal" in plugin.tags
        assert "analysis" in plugin.tags


# ============================================================================
# Tool Creation Tests
# ============================================================================


class TestJournalPluginTools:
    """Test journal plugin tool creation and functionality."""

    def test_create_tools(self, plugin_config, plugin_dependencies):
        """Test tool creation."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)
        tools = plugin._create_tools()

        assert len(tools) == 4

        tool_names = [tool.name for tool in tools]
        assert "summarize_journals" in tool_names
        assert "generate_review" in tool_names
        assert "list_retrievers" in tool_names
        assert "get_entries_by_type" in tool_names

    def test_summarize_journals_tool(self, plugin_config, plugin_dependencies):
        """Test summarize_journals tool structure."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)
        tools = plugin._create_tools()

        summarize_tool = next(t for t in tools if t.name == "summarize_journals")
        assert (
            summarize_tool.description
            == "Summarize journal entries using real retriever architecture"
        )
        assert "query" in summarize_tool.input_schema["properties"]
        assert "style" in summarize_tool.input_schema["properties"]
        assert "entry_types" in summarize_tool.input_schema["properties"]
        assert "journal" in summarize_tool.tags
        assert "summarization" in summarize_tool.tags

    def test_generate_review_tool(self, plugin_config, plugin_dependencies):
        """Test generate_review tool structure."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)
        tools = plugin._create_tools()

        review_tool = next(t for t in tools if t.name == "generate_review")
        assert (
            review_tool.description
            == "Generate a performance review from journal entries"
        )
        assert "query" in review_tool.input_schema["properties"]
        assert "period" in review_tool.input_schema["properties"]
        assert "focus_areas" in review_tool.input_schema["properties"]
        assert "journal" in review_tool.tags
        assert "review" in review_tool.tags


# ============================================================================
# Resource Creation Tests
# ============================================================================


class TestJournalPluginResources:
    """Test journal plugin resource creation."""

    def test_create_resources(self, plugin_config, plugin_dependencies):
        """Test resource creation."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)
        resources = plugin._create_resources()

        assert len(resources) == 3

        resource_uris = [resource.uri for resource in resources]
        assert "mindmirror://journal/retrievers" in resource_uris
        assert "mindmirror://journal/entries" in resource_uris
        assert (
            f"mindmirror://journal/user/{plugin_config['user_id']}/entries"
            in resource_uris
        )

    def test_retrievers_resource(self, plugin_config, plugin_dependencies):
        """Test retrievers resource structure."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)
        resources = plugin._create_resources()

        retrievers_resource = next(r for r in resources if "retrievers" in r.uri)
        assert retrievers_resource.name == "Journal Retrievers"
        assert (
            retrievers_resource.description == "Access to available journal retrievers"
        )
        assert retrievers_resource.mime_type == "application/json"
        assert retrievers_resource.metadata["category"] == "meta"
        assert retrievers_resource.metadata["retriever_aware"] is True


# ============================================================================
# Prompt Creation Tests
# ============================================================================


class TestJournalPluginPrompts:
    """Test journal plugin prompt creation."""

    def test_create_prompts(self, plugin_config, plugin_dependencies):
        """Test prompt creation."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)
        prompts = plugin._create_prompts()

        assert len(prompts) == 1

        prompt = prompts[0]
        assert prompt.name == "summarize_journals"
        assert (
            prompt.description
            == "Summarize journal entries using real retriever architecture"
        )
        assert len(prompt.arguments) == 2
        assert prompt.arguments[0]["name"] == "query"
        assert prompt.arguments[1]["name"] == "style"


# ============================================================================
# Tool Execution Tests
# ============================================================================


class TestJournalPluginToolExecution:
    """Test journal plugin tool execution."""

    @pytest.mark.asyncio
    async def test_summarize_journals_execution(
        self, plugin_config, plugin_dependencies
    ):
        """Test summarize_journals tool execution."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        arguments = {
            "query": "this week",
            "style": "concise",
            "entry_types": ["text", "mood"],
        }

        result = await plugin.execute_tool("summarize_journals", arguments)

        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "Mock summary" in result[0]["text"]

        # Verify LLM service was called
        plugin.llm_service.get_journal_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_review_execution(self, plugin_config, plugin_dependencies):
        """Test generate_review tool execution."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        arguments = {
            "query": "this quarter",
            "period": "quarter",
            "focus_areas": ["productivity", "learning"],
        }

        result = await plugin.execute_tool("generate_review", arguments)

        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "Mock review" in result[0]["text"]

        # Verify LLM service was called
        plugin.llm_service.get_performance_review.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_retrievers_execution(self, plugin_config, plugin_dependencies):
        """Test list_retrievers tool execution."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        result = await plugin.execute_tool("list_retrievers", {})

        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "journal" in result[0]["text"]

    @pytest.mark.asyncio
    async def test_get_entries_by_type_execution(
        self, plugin_config, plugin_dependencies
    ):
        """Test get_entries_by_type tool execution."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        arguments = {"entry_type": "text", "days_back": 7}

        result = await plugin.execute_tool("get_entries_by_type", arguments)

        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "productive day" in result[0]["text"]

    @pytest.mark.asyncio
    async def test_unknown_tool_execution(self, plugin_config, plugin_dependencies):
        """Test execution of unknown tool."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
            await plugin.execute_tool("unknown_tool", {})


# ============================================================================
# Resource Access Tests
# ============================================================================


class TestJournalPluginResourceAccess:
    """Test journal plugin resource access."""

    @pytest.mark.asyncio
    async def test_get_retrievers_info(self, plugin_config, plugin_dependencies):
        """Test getting retrievers info."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        result = await plugin.read_resource("mindmirror://journal/retrievers")

        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert "journal" in result[0]["text"]

    @pytest.mark.asyncio
    async def test_get_journal_entries(self, plugin_config, plugin_dependencies):
        """Test getting journal entries."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        result = await plugin.read_resource("mindmirror://journal/entries")

        # Should return one result per journal entry (3 entries in sample data)
        assert len(result) == 3
        assert result[0]["type"] == "text"
        assert "productive day" in result[0]["text"]
        assert "happy" in result[1]["text"]
        assert "Learn Python" in result[2]["text"]

    @pytest.mark.asyncio
    async def test_get_user_journal_entries(self, plugin_config, plugin_dependencies):
        """Test getting user-specific journal entries."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        uri = f"mindmirror://journal/user/{plugin_config['user_id']}/entries"
        result = await plugin.read_resource(uri)

        # Should return one result per journal entry (3 entries in sample data)
        assert len(result) == 3
        assert result[0]["type"] == "text"
        assert "productive day" in result[0]["text"]
        assert "happy" in result[1]["text"]
        assert "Learn Python" in result[2]["text"]

    @pytest.mark.asyncio
    async def test_unknown_resource_access(self, plugin_config, plugin_dependencies):
        """Test access to unknown resource."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        with pytest.raises(ValueError, match="Unknown resource: unknown://resource"):
            await plugin.read_resource("unknown://resource")


# ============================================================================
# Prompt Access Tests
# ============================================================================


class TestJournalPluginPromptAccess:
    """Test journal plugin prompt access."""

    @pytest.mark.asyncio
    async def test_get_summarize_prompt(self, plugin_config, plugin_dependencies):
        """Test getting summarize prompt."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        arguments = {"query": "this week", "style": "detailed"}

        result = await plugin.get_prompt_content("summarize_journals", arguments)

        assert "description" in result
        assert "messages" in result
        assert "this week" in result["description"]
        assert "detailed" in result["description"]
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_get_summarize_prompt_no_arguments(
        self, plugin_config, plugin_dependencies
    ):
        """Test getting summarize prompt without arguments."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        result = await plugin.get_prompt_content("summarize_journals", None)

        assert "description" in result
        assert "messages" in result
        assert "concise" in result["description"]  # Default style

    @pytest.mark.asyncio
    async def test_unknown_prompt_access(self, plugin_config, plugin_dependencies):
        """Test access to unknown prompt."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        with pytest.raises(ValueError, match="Unknown prompt: unknown_prompt"):
            await plugin.get_prompt_content("unknown_prompt", {})


# ============================================================================
# Integration Tests
# ============================================================================


class TestJournalPluginIntegration:
    """Integration tests for journal plugin."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, plugin_config, plugin_dependencies):
        """Test complete journal plugin workflow."""
        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        # Test tool creation
        tools = plugin._create_tools()
        assert len(tools) == 4

        # Test resource creation
        resources = plugin._create_resources()
        assert len(resources) == 3

        # Test prompt creation
        prompts = plugin._create_prompts()
        assert len(prompts) == 1

        # Test tool execution
        result = await plugin.execute_tool("summarize_journals", {"query": "this week"})
        assert len(result) == 1
        assert result[0]["type"] == "text"

        # Test resource access
        resource_result = await plugin.read_resource("mindmirror://journal/retrievers")
        assert len(resource_result) == 1
        assert resource_result[0]["type"] == "text"

        # Test prompt access
        prompt_result = await plugin.get_prompt_content(
            "summarize_journals", {"query": "test"}
        )
        assert "description" in prompt_result
        assert "messages" in prompt_result


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestJournalPluginErrorHandling:
    """Test journal plugin error handling."""

    @pytest.mark.asyncio
    async def test_network_error_handling(self, plugin_config, plugin_dependencies):
        """Test handling of network errors."""
        # Setup mock journal client to raise an exception
        plugin_dependencies["journal_client"].list_by_user_for_period.side_effect = (
            Exception("Network error")
        )

        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        # Should raise the exception (correct behavior for network errors)
        with pytest.raises(Exception, match="Network error"):
            await plugin.execute_tool("summarize_journals", {"query": "this week"})

    @pytest.mark.asyncio
    async def test_missing_data_handling(self, plugin_config, plugin_dependencies):
        """Test handling of missing data."""
        # Setup mock journal client to return empty list
        plugin_dependencies["journal_client"].list_by_user_for_period.return_value = []

        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        result = await plugin.execute_tool("summarize_journals", {"query": "this week"})
        assert len(result) == 1
        assert result[0]["type"] == "text"
        # Should still call LLM service with empty content
        plugin.llm_service.get_journal_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_llm_service_error_handling(self, plugin_config, plugin_dependencies):
        """Test handling of LLM service errors."""
        # Setup mock LLM service to raise an exception
        plugin_dependencies["llm_service"].get_journal_summary.side_effect = Exception(
            "LLM service error"
        )

        plugin = JournalPlugin(plugin_config, plugin_dependencies)

        with pytest.raises(Exception, match="LLM service error"):
            await plugin.execute_tool("summarize_journals", {"query": "this week"})
