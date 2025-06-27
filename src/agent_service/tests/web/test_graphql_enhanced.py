"""
Enhanced GraphQL Tests for Phase 4.5

Comprehensive tests for the enhanced GraphQL integration with MCP tool registry.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from agent_service.app.graphql.schemas.query import Query
from agent_service.app.graphql.schemas.mutation import Mutation
from agent_service.app.graphql.types.tool_types import ToolMetadata, ToolExecutionResult, ToolRegistryHealth
from agent_service.app.services.llm_service import LLMService
from agent_service.mcp.tools.base import ToolRegistry, MCPTool, ToolMetadata as MCPToolMetadata, ToolBackend, EffectBoundary
from shared.auth import CurrentUser
from uuid import uuid4


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
    
    def get_metadata(self) -> MCPToolMetadata:
        """Get tool metadata."""
        return MCPToolMetadata(
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
        
        return [{"summary": f"Summary of {len(journal_entries)} entries in {style} style"}]
    
    def get_metadata(self) -> MCPToolMetadata:
        """Get tool metadata."""
        return MCPToolMetadata(
            name=self._name,
            description=self._description,
            input_schema={
                "type": "object",
                "properties": {
                    "journal_entries": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "style": {
                        "type": "string",
                        "enum": ["concise", "detailed"]
                    }
                },
                "required": ["journal_entries"]
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"}
                    }
                }
            },
            backend=ToolBackend.LANGGRAPH,
            owner_domain="journaling",
            version="2.1.0",
            tags=frozenset(["journal", "summary"]),
            effect_boundary=EffectBoundary.LLM
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
        
        review_text = f"SUCCESS: Performance review for {len(journal_entries)} entries over {period}\nIMPROVEMENT: Consider adding more detailed entries\nPROMPT: What would you like to focus on next?"
        return [{"review": review_text}]
    
    def get_metadata(self) -> MCPToolMetadata:
        """Get tool metadata."""
        return MCPToolMetadata(
            name=self._name,
            description=self._description,
            input_schema={
                "type": "object",
                "properties": {
                    "journal_entries": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "period": {
                        "type": "string",
                        "enum": ["week", "month", "quarter", "year"]
                    }
                },
                "required": ["journal_entries"]
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "review": {"type": "string"}
                    }
                }
            },
            backend=ToolBackend.LANGGRAPH,
            owner_domain="review",
            version="1.0.0",
            tags=frozenset(["review", "performance"]),
            effect_boundary=EffectBoundary.LLM
        )


class TestEnhancedGraphQLQuery:
    """Test enhanced GraphQL query fields for Phase 4.5."""
    
    @pytest.fixture
    def mock_current_user(self):
        """Create a mock current user."""
        return CurrentUser(id=uuid4(), email="test@test.com")
    
    @pytest.fixture
    def mock_info(self, mock_current_user):
        """Create a mock GraphQL info object."""
        info = MagicMock()
        info.context = {"current_user": mock_current_user}
        return info
    
    def mock_llm_service(self):
        """Create a mock LLMService with tool registry."""
        service = Mock(spec=LLMService)
        
        # Mock tool registry methods
        service.list_tools.return_value = [
            {
                "name": "journal_summary_graph",
                "description": "Journal summary tool",
                "owner_domain": "journaling",
                "version": "2.1.0",
                "backend": "langgraph",
                "effect_boundary": "llm",
                "tags": ["journal", "summary"],
                "subtools": ["summarizer"],
                "input_schema": {"type": "object"},
                "output_schema": {"type": "array"}
            },
            {
                "name": "performance_review_graph",
                "description": "Performance review tool",
                "owner_domain": "review",
                "version": "1.0.0",
                "backend": "langgraph",
                "effect_boundary": "llm",
                "tags": ["review", "performance"],
                "subtools": ["analyzer"],
                "input_schema": {"type": "object"},
                "output_schema": {"type": "array"}
            }
        ]
        
        service.get_tool_metadata.return_value = {
            "name": "journal_summary_graph",
            "description": "Journal summary tool",
            "owner_domain": "journaling",
            "version": "2.1.0",
            "backend": "langgraph",
            "effect_boundary": "llm",
            "tags": ["journal", "summary"],
            "subtools": ["summarizer"],
            "input_schema": {"type": "object"},
            "output_schema": {"type": "array"}
        }
        
        service.get_tool_registry_health.return_value = {
            "status": "healthy",
            "total_tools": 2,
            "unique_tools": 2,
            "backends": {"langgraph": 2}
        }
        
        service.list_tool_names.return_value = ["journal_summary_graph", "performance_review_graph"]
        
        return service
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_list_tools_no_filter(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        query = Query()
        result = await query.list_tools(info=mock_info)
        assert len(result) == 2
        assert result[0].name == "journal_summary_graph"
        assert result[0].owner_domain == "journaling"
        assert result[0].version == "2.1.0"
        assert result[0].backend == "langgraph"
        assert "journal" in result[0].tags
        assert "summarizer" in result[0].subtools
        assert result[1].name == "performance_review_graph"
        assert result[1].owner_domain == "review"
        assert result[1].version == "1.0.0"
        mock_llm_service.list_tools.assert_called_once_with(None, None, None, None)
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_list_tools_with_filters(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        query = Query()
        result = await query.list_tools(
            info=mock_info,
            backend="langgraph",
            tags=["journal"],
            owner_domain="journaling"
        )
        mock_llm_service.list_tools.assert_called_once_with("langgraph", ["journal"], "journaling", None)
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_get_tool_metadata(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        query = Query()
        result = await query.get_tool_metadata(info=mock_info, tool_name="journal_summary_graph")
        assert result is not None
        assert result.name == "journal_summary_graph"
        assert result.owner_domain == "journaling"
        assert result.version == "2.1.0"
        assert result.backend == "langgraph"
        assert "journal" in result.tags
        assert "summarizer" in result.subtools
        mock_llm_service.get_tool_metadata.assert_called_once_with("journal_summary_graph", None)
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_get_tool_metadata_with_version(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        query = Query()
        result = await query.get_tool_metadata(info=mock_info, tool_name="journal_summary_graph", version="2.1.0")
        mock_llm_service.get_tool_metadata.assert_called_once_with("journal_summary_graph", "2.1.0")
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_get_tool_metadata_not_found(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.get_tool_metadata.return_value = None
        query = Query()
        result = await query.get_tool_metadata(info=mock_info, tool_name="non_existent")
        assert result is None
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_get_tool_registry_health(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        query = Query()
        result = await query.get_tool_registry_health(info=mock_info)
        assert result.status == "healthy"
        assert result.total_tools == 2
        assert result.unique_tools == 2
        assert result.backends["langgraph"] == 2
        assert result.error is None
        mock_llm_service.get_tool_registry_health.assert_called_once()
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_get_tool_registry_health_error(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.get_tool_registry_health.side_effect = Exception("Registry error")
        query = Query()
        result = await query.get_tool_registry_health(info=mock_info)
        assert result.status == "unhealthy"
        assert result.total_tools == 0
        assert result.unique_tools == 0
        assert result.backends == {}
        assert "Registry error" in result.error
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @pytest.mark.asyncio
    async def test_list_tool_names(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        query = Query()
        result = await query.list_tool_names(info=mock_info)
        assert result == ["journal_summary_graph", "performance_review_graph"]
        mock_llm_service.list_tool_names.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_tools_no_authentication(self, mock_info):
        """Test listing tools without authentication."""
        mock_info.context = {}  # No current_user
        
        query = Query()
        
        with pytest.raises(Exception, match="Authentication required"):
            await query.list_tools(info=mock_info)
    
    @pytest.mark.asyncio
    async def test_get_tool_metadata_no_authentication(self, mock_info):
        """Test getting tool metadata without authentication."""
        mock_info.context = {}  # No current_user
        
        query = Query()
        
        with pytest.raises(Exception, match="Authentication required"):
            await query.get_tool_metadata(info=mock_info, tool_name="test")
    
    @pytest.mark.asyncio
    async def test_get_tool_registry_health_no_authentication(self, mock_info):
        """Test getting tool registry health without authentication."""
        mock_info.context = {}  # No current_user
        
        query = Query()
        
        with pytest.raises(Exception, match="Authentication required"):
            await query.get_tool_registry_health(info=mock_info)
    
    @pytest.mark.asyncio
    async def test_list_tool_names_no_authentication(self, mock_info):
        """Test listing tool names without authentication."""
        mock_info.context = {}  # No current_user
        
        query = Query()
        
        with pytest.raises(Exception, match="Authentication required"):
            await query.list_tool_names(info=mock_info)


class TestEnhancedGraphQLMutation:
    """Test enhanced GraphQL mutation fields for Phase 4.5."""
    
    @pytest.fixture
    def mock_current_user(self):
        """Create a mock current user."""
        return CurrentUser(id=uuid4(), email="test@test.com")
    
    @pytest.fixture
    def mock_info(self, mock_current_user):
        """Create a mock GraphQL info object."""
        info = MagicMock()
        info.context = {"current_user": mock_current_user}
        return info
    
    def mock_llm_service(self):
        """Create a mock LLMService with tool registry."""
        service = Mock(spec=LLMService)
        return service
    
    @patch("agent_service.app.graphql.schemas.mutation.LLMService")
    @pytest.mark.asyncio
    async def test_execute_tool_success(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.execute_tool.return_value = [{"result": "success"}]
        mutation = Mutation()
        result = await mutation.execute_tool(
            info=mock_info,
            tool_name="journal_summary_graph",
            arguments={"journal_entries": [], "style": "concise"}
        )
        assert result.success is True
        assert result.result == [{"result": "success"}]
        assert result.error is None
        assert result.execution_time_ms is not None
        mock_llm_service.execute_tool.assert_called_once_with(
            "journal_summary_graph",
            {"journal_entries": [], "style": "concise"},
            None
        )
    
    @patch("agent_service.app.graphql.schemas.mutation.LLMService")
    @pytest.mark.asyncio
    async def test_execute_tool_with_version(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.execute_tool.return_value = [{"result": "success"}]
        mutation = Mutation()
        result = await mutation.execute_tool(
            info=mock_info,
            tool_name="journal_summary_graph",
            arguments={"journal_entries": []},
            version="2.1.0"
        )
        assert result.success is True
        mock_llm_service.execute_tool.assert_called_once_with(
            "journal_summary_graph",
            {"journal_entries": []},
            "2.1.0"
        )
    
    @patch("agent_service.app.graphql.schemas.mutation.LLMService")
    @pytest.mark.asyncio
    async def test_execute_tool_error(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.execute_tool.side_effect = ValueError("Tool not found")
        mutation = Mutation()
        result = await mutation.execute_tool(
            info=mock_info,
            tool_name="non_existent",
            arguments={}
        )
        assert result.success is False
        assert result.result == []
        assert "Tool not found" in result.error
        assert result.execution_time_ms is not None
    
    @patch("agent_service.app.graphql.schemas.mutation.LLMService")
    @pytest.mark.asyncio
    async def test_execute_subtool_success(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.execute_subtool.return_value = {"result": "subtool_success"}
        mutation = Mutation()
        result = await mutation.execute_subtool(
            info=mock_info,
            tool_name="journal_summary_graph",
            subtool_name="summarizer",
            arguments={"arg": "value"}
        )
        assert result.success is True
        assert result.result == [{"result": "subtool_success"}]
        assert result.error is None
        assert result.execution_time_ms is not None
        mock_llm_service.execute_subtool.assert_called_once_with(
            "journal_summary_graph",
            "summarizer",
            {"arg": "value"},
            None
        )
    
    @patch("agent_service.app.graphql.schemas.mutation.LLMService")
    @pytest.mark.asyncio
    async def test_execute_subtool_with_version(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.execute_subtool.return_value = {"result": "subtool_success"}
        mutation = Mutation()
        result = await mutation.execute_subtool(
            info=mock_info,
            tool_name="journal_summary_graph",
            subtool_name="summarizer",
            arguments={"arg": "value"},
            version="2.1.0"
        )
        assert result.success is True
        mock_llm_service.execute_subtool.assert_called_once_with(
            "journal_summary_graph",
            "summarizer",
            {"arg": "value"},
            "2.1.0"
        )
    
    @patch("agent_service.app.graphql.schemas.mutation.LLMService")
    @pytest.mark.asyncio
    async def test_execute_subtool_error(self, mock_llm_service_class, mock_info):
        mock_llm_service = self.mock_llm_service()
        mock_llm_service_class.return_value = mock_llm_service
        mock_llm_service.execute_subtool.side_effect = ValueError("Subtool not found")
        mutation = Mutation()
        result = await mutation.execute_subtool(
            info=mock_info,
            tool_name="journal_summary_graph",
            subtool_name="non_existent",
            arguments={}
        )
        assert result.success is False
        assert result.result == []
        assert "Subtool not found" in result.error
        assert result.execution_time_ms is not None
    
    @pytest.mark.asyncio
    async def test_execute_tool_no_authentication(self, mock_info):
        """Test tool execution without authentication."""
        mock_info.context = {}  # No current_user
        
        mutation = Mutation()
        
        with pytest.raises(Exception, match="Authentication required"):
            await mutation.execute_tool(info=mock_info, tool_name="test", arguments={})
    
    @pytest.mark.asyncio
    async def test_execute_subtool_no_authentication(self, mock_info):
        """Test subtool execution without authentication."""
        mock_info.context = {}  # No current_user
        
        mutation = Mutation()
        
        with pytest.raises(Exception, match="Authentication required"):
            await mutation.execute_subtool(info=mock_info, tool_name="test", subtool_name="test", arguments={})


class TestEnhancedGraphQLIntegration:
    """Integration tests for enhanced GraphQL functionality."""
    
    @pytest.fixture
    def mock_current_user(self):
        """Create a mock current user."""
        return CurrentUser(id=uuid4(), email="test@test.com")
    
    @pytest.fixture
    def mock_info(self, mock_current_user):
        """Create a mock GraphQL info object."""
        info = MagicMock()
        info.context = {"current_user": mock_current_user}
        return info
    
    @patch("agent_service.app.graphql.schemas.query.LLMService")
    @patch("agent_service.app.graphql.schemas.mutation.LLMService")
    @pytest.mark.asyncio
    async def test_full_tool_workflow(self, mock_mutation_llm_service_class, mock_query_llm_service_class, mock_info):
        """Test complete tool workflow: list -> metadata -> execute."""
        from agent_service.mcp.tools.base import ToolRegistry
        registry = ToolRegistry()
        journal_tool = MockJournalTool()
        review_tool = MockPerformanceReviewTool()
        registry.register(journal_tool)
        registry.register(review_tool)
        mock_llm_service = Mock(spec=LLMService)
        mock_llm_service.tool_registry = registry
        mock_llm_service.list_tools.return_value = [
            {
                "name": "journal_summary_graph",
                "description": "Journal summary tool",
                "owner_domain": "journaling",
                "version": "2.1.0",
                "backend": "langgraph",
                "effect_boundary": "llm",
                "tags": ["journal", "summary"],
                "subtools": ["summarizer"],
                "input_schema": {"type": "object"},
                "output_schema": {"type": "array"}
            }
        ]
        mock_llm_service.get_tool_metadata.return_value = {
            "name": "journal_summary_graph",
            "description": "Journal summary tool",
            "owner_domain": "journaling",
            "version": "2.1.0",
            "backend": "langgraph",
            "effect_boundary": "llm",
            "tags": ["journal", "summary"],
            "subtools": ["summarizer"],
            "input_schema": {"type": "object"},
            "output_schema": {"type": "array"}
        }
        mock_llm_service.execute_tool.return_value = [{"summary": "Test summary"}]
        mock_llm_service.get_tool_registry_health.return_value = {
            "status": "healthy",
            "total_tools": 2,
            "unique_tools": 2,
            "backends": {"langgraph": 2}
        }
        mock_query_llm_service_class.return_value = mock_llm_service
        mock_mutation_llm_service_class.return_value = mock_llm_service
        query = Query()
        tools = await query.list_tools(info=mock_info)
        assert len(tools) == 1
        assert tools[0].name == "journal_summary_graph"
        metadata = await query.get_tool_metadata(info=mock_info, tool_name="journal_summary_graph")
        assert metadata.name == "journal_summary_graph"
        assert metadata.owner_domain == "journaling"
        mutation = Mutation()
        result = await mutation.execute_tool(
            info=mock_info,
            tool_name="journal_summary_graph",
            arguments={"journal_entries": [], "style": "concise"}
        )
        assert result.success is True
        assert result.result == [{"summary": "Test summary"}]
        health = await query.get_tool_registry_health(info=mock_info)
        assert health.status == "healthy"
        assert health.total_tools == 2 