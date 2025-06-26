"""
Tests for LangGraph components.

This module tests the LangGraph integration including state management,
nodes, graph builders, runners, and services.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from agent_service.langgraph.state import (
    BaseAgentState,
    JournalAgentState,
    RAGAgentState,
    StateManager,
    AgentStateFactory,
)
from agent_service.langgraph.nodes.base import BaseNode, LLMNode
from agent_service.langgraph.nodes.summarizer_node import SummarizerNode
from agent_service.langgraph.nodes.reviewer_node import ReviewerNode
from agent_service.langgraph.graphs.base import BaseGraphBuilder
from agent_service.langgraph.graphs.journal_graph import JournalGraphBuilder
from agent_service.langgraph.graphs.review_graph import ReviewGraphBuilder
from agent_service.langgraph.runner import GraphRunner, GraphRunnerFactory
from agent_service.langgraph.service import LangGraphService, LangGraphServiceFactory


class TestStateManagement:
    """Test state management functionality."""
    
    def test_base_agent_state_creation(self):
        """Test creating a base agent state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test_user",
            tradition="test_tradition",
            query="test query"
        )
        
        assert state["user_id"] == "test_user"
        assert state["tradition"] == "test_tradition"
        assert "created_at" in state
        assert "error" in state
    
    def test_journal_agent_state_creation(self):
        """Test creating a journal agent state."""
        journal_entries = [
            {"content": "Entry 1", "date": "2024-01-01"},
            {"content": "Entry 2", "date": "2024-01-02"},
        ]
        
        state = AgentStateFactory.create_journal_state(
            user_id="test_user",
            tradition="test_tradition",
            journal_entries=journal_entries
        )
        
        assert state["user_id"] == "test_user"
        assert state["tradition"] == "test_tradition"
        assert state["journal_entries"] == journal_entries
        assert state["summary"] is None
        assert state["analysis"] is None
    
    def test_rag_agent_state_creation(self):
        """Test creating a RAG agent state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test_user",
            tradition="test_tradition",
            query="test query"
        )
        
        assert state["user_id"] == "test_user"
        assert state["tradition"] == "test_tradition"
        assert state["query"] == "test query"
        assert state["generated_response"] is None
        assert "retrieved_documents" in state
    
    def test_state_manager_add_error(self):
        """Test adding errors to state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test_user", 
            tradition="test_tradition",
            query="test"
        )
        
        error_state = StateManager.add_error(
            state,
            error="Test error message",
            error_type="TestError"
        )
        
        assert error_state["error"] == "Test error message"
        assert error_state["error_type"] == "TestError"
    
    def test_state_manager_update_state(self):
        """Test updating state."""
        state = AgentStateFactory.create_journal_state(
            user_id="test_user",
            tradition="test_tradition",
            journal_entries=[]
        )
        
        updates = {"summary": "Test summary"}
        updated_state = StateManager.update_state(state, updates)
        
        assert updated_state["summary"] == "Test summary"


class TestNodes:
    """Test node functionality."""
    
    def test_base_node_creation(self):
        """Test creating a base node."""
        class TestNode(BaseNode):
            def execute(self, state):
                return state
        
        node = TestNode(name="test_node", description="Test node description")
        
        assert node.name == "test_node"
        assert node.description == "Test node description"
    
    def test_llm_node_creation(self):
        """Test creating an LLM node."""
        class TestLLMNode(LLMNode):
            def execute(self, state):
                return state
        
        node = TestLLMNode(
            name="test_llm_node",
            description="Test LLM node",
            task="test_task"
        )
        
        assert node.name == "test_llm_node"
        assert node.task == "test_task"
    
    @patch('agent_service.services.llm_service.LLMService')
    def test_summarizer_node_execution(self, mock_llm_service):
        """Test summarizer node execution."""
        mock_service = Mock()
        mock_service.get_journal_summary.return_value = "Test summary"
        mock_llm_service.return_value = mock_service
        
        node = SummarizerNode()
        
        state = AgentStateFactory.create_journal_state(
            user_id="test_user",
            tradition="test_tradition",
            journal_entries=[{"content": "Test entry"}]
        )
        
        result = node.execute(state)
        
        assert "summary" in result
        assert result["summary"] == "Test summary"
        mock_service.get_journal_summary.assert_called_once()
    
    @patch('agent_service.services.llm_service.LLMService')
    def test_reviewer_node_execution(self, mock_llm_service):
        """Test reviewer node execution."""
        mock_service = Mock()
        mock_review = Mock()
        mock_review.key_success = "Test success"
        mock_review.improvement_area = "Test improvement"
        mock_review.journal_prompt = "Test prompt"
        mock_service.get_performance_review.return_value = mock_review
        mock_llm_service.return_value = mock_service
        
        node = ReviewerNode()
        
        state = AgentStateFactory.create_journal_state(
            user_id="test_user",
            tradition="test_tradition",
            journal_entries=[{"content": "Test entry"}]
        )
        
        result = node.execute(state)
        
        assert "review" in result
        assert result["review"]["key_success"] == "Test success"
        mock_service.get_performance_review.assert_called_once()


class TestGraphBuilders:
    """Test graph builder functionality."""
    
    def test_base_graph_builder_creation(self):
        """Test creating a base graph builder."""
        class TestGraphBuilder(BaseGraphBuilder):
            def build(self):
                return Mock()
        
        builder = TestGraphBuilder(
            name="test_graph",
            description="Test graph description"
        )
        
        assert builder.name == "test_graph"
        assert builder.description == "Test graph description"
        assert builder.nodes == {}
    
    def test_journal_graph_builder(self):
        """Test journal graph builder."""
        builder = JournalGraphBuilder()
        
        graph = builder.get_summary_graph()
        
        assert graph is not None
        assert hasattr(graph, 'invoke')
    
    def test_review_graph_builder(self):
        """Test review graph builder."""
        builder = ReviewGraphBuilder()
        
        graph = builder.get_review_graph()
        
        assert graph is not None
        assert hasattr(graph, 'invoke')


class TestGraphRunner:
    """Test graph runner functionality."""
    
    def test_graph_runner_creation(self):
        """Test creating a graph runner."""
        mock_graph = Mock()
        runner = GraphRunner(mock_graph)
        
        assert runner.graph == mock_graph
    
    def test_graph_runner_validate_state(self):
        """Test state validation."""
        mock_graph = Mock()
        runner = GraphRunner(mock_graph)
        
        valid_state = AgentStateFactory.create_rag_state(
            user_id="test_user", 
            tradition="test_tradition",
            query="test"
        )
        assert runner.validate_state(valid_state) is True
        
        invalid_state = AgentStateFactory.create_rag_state(
            user_id=None, 
            tradition="test_tradition",
            query="test"
        )
        assert runner.validate_state(invalid_state) is False
    
    def test_graph_runner_get_execution_info(self):
        """Test getting execution info."""
        mock_graph = Mock()
        mock_graph.__class__.__name__ = "TestGraph"
        mock_graph.ainvoke = Mock()
        mock_graph.stream = Mock()
        
        runner = GraphRunner(mock_graph)
        info = runner.get_execution_info()
        
        assert info["graph_type"] == "TestGraph"
        assert info["has_async"] is True
        assert info["has_stream"] is True


class TestGraphRunnerFactory:
    """Test graph runner factory."""
    
    def test_create_journal_summary_runner(self):
        """Test creating journal summary runner."""
        runner = GraphRunnerFactory.create_journal_summary_runner()
        
        assert isinstance(runner, GraphRunner)
        assert runner.graph is not None
    
    def test_create_performance_review_runner(self):
        """Test creating performance review runner."""
        runner = GraphRunnerFactory.create_performance_review_runner()
        
        assert isinstance(runner, GraphRunner)
        assert runner.graph is not None


class TestLangGraphService:
    """Test LangGraph service functionality."""
    
    def test_langgraph_service_creation(self):
        """Test creating a LangGraph service."""
        service = LangGraphService()
        
        assert service.provider_manager is None
        assert service._runners == {}
    
    def test_get_available_graphs(self):
        """Test getting available graphs."""
        service = LangGraphService()
        graphs = service.get_available_graphs()
        
        assert len(graphs) == 2
        assert any(g["type"] == "journal_summary" for g in graphs)
        assert any(g["type"] == "performance_review" for g in graphs)
    
    def test_get_graph_info(self):
        """Test getting graph info."""
        service = LangGraphService()
        
        info = service.get_graph_info("journal_summary")
        assert info is not None
        assert "graph_type" in info
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        service = LangGraphService()
        
        service._get_runner("journal_summary")
        assert len(service._runners) > 0
        
        service.clear_cache()
        assert len(service._runners) == 0


class TestLangGraphServiceFactory:
    """Test LangGraph service factory."""
    
    def test_create_default_service(self):
        """Test creating default service."""
        service = LangGraphServiceFactory.create_default_service()
        
        assert isinstance(service, LangGraphService)
        assert service.provider_manager is None
    
    def test_create_service_with_provider(self):
        """Test creating service with provider."""
        service = LangGraphServiceFactory.create_service_with_provider("openai")
        
        assert isinstance(service, LangGraphService)
        assert service.provider_manager is not None
    
    def test_create_service_with_overrides(self):
        """Test creating service with overrides."""
        overrides = {"temperature": 0.7}
        service = LangGraphServiceFactory.create_service_with_overrides(overrides)
        
        assert isinstance(service, LangGraphService)
        assert len(service._runners) > 0


class TestIntegration:
    """Integration tests for LangGraph components."""
    
    @pytest.mark.asyncio
    async def test_journal_summary_workflow(self):
        """Test complete journal summary workflow."""
        service = LangGraphService()
        
        journal_entries = [
            {"content": "Today was productive", "date": "2024-01-01"},
            {"content": "Learned new things", "date": "2024-01-02"},
        ]
        
        with patch('agent_service.services.llm_service.LLMService'):
            result = await service.generate_journal_summary(
                user_id="test_user",
                journal_entries=journal_entries,
                tradition="test_tradition"
            )
            
            assert isinstance(result, dict)
            assert result["user_id"] == "test_user"
            assert result["journal_entries"] == journal_entries
    
    @pytest.mark.asyncio
    async def test_performance_review_workflow(self):
        """Test complete performance review workflow."""
        service = LangGraphService()
        
        performance_data = {
            "metrics": {"accuracy": 0.95, "speed": 0.8},
            "period": "Q1 2024"
        }
        
        with patch('agent_service.services.llm_service.LLMService'):
            result = await service.generate_performance_review(
                user_id="test_user",
                performance_data=performance_data,
                tradition="test_tradition"
            )
            
            assert isinstance(result, dict)
            assert result["user_id"] == "test_user"
            assert "journal_entries" in result 