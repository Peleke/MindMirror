"""
Tests for agent state management.

These tests verify that state creation, updates, and transformations
work correctly for different types of agent workflows.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from langchain_core.documents import Document

from agent_service.agents.state import (
    BaseAgentState,
    RAGAgentState,
    JournalAgentState,
    CoachingAgentState,
    MultiAgentState,
    AgentStateFactory,
    StateManager,
)


class TestAgentStateFactory:
    """Test agent state factory methods."""
    
    def test_create_rag_state(self):
        """Test creation of RAG agent state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="What is the meaning of life?",
            session_id="test-session",
        )
        
        # TypedDict doesn't support isinstance checks, so we validate structure instead
        assert "user_id" in state
        assert "tradition" in state
        assert "query" in state
        assert "session_id" in state
        assert "input" in state
        assert "output" in state
        assert "context" in state
        assert "retrieved_documents" in state
        assert "retrieval_scores" in state
        assert "generated_response" in state
        
        assert state["user_id"] == "test-user"
        assert state["tradition"] == "canon-default"
        assert state["query"] == "What is the meaning of life?"
        assert state["session_id"] == "test-session"
        assert state["input"] == "What is the meaning of life?"
        assert state["output"] is None
        assert state["error"] is None
        assert state["context"] == []
        assert state["retrieved_documents"] == []
        assert state["retrieval_scores"] == []
        assert state["generated_response"] is None
        assert isinstance(state["created_at"], datetime)
        assert isinstance(state["updated_at"], datetime)
    
    def test_create_journal_state(self):
        """Test creation of journal agent state."""
        journal_entries = [
            {"text": "I had a great day", "entry_type": "REFLECTION"},
            {"text": "I'm grateful for my family", "entry_type": "GRATITUDE"},
        ]
        
        state = AgentStateFactory.create_journal_state(
            user_id="test-user",
            tradition="canon-default",
            journal_entries=journal_entries,
            session_id="test-session",
        )
        
        # TypedDict doesn't support isinstance checks, so we validate structure instead
        assert "user_id" in state
        assert "tradition" in state
        assert "journal_entries" in state
        assert "entry_count" in state
        assert "entry_types" in state
        assert "summary" in state
        assert "analysis" in state
        assert "review" in state
        assert "date_range" in state
        
        assert state["user_id"] == "test-user"
        assert state["tradition"] == "canon-default"
        assert state["journal_entries"] == journal_entries
        assert state["entry_count"] == 2
        for e in state["entry_types"]:
            assert e in ["REFLECTION", "GRATITUDE"]
        assert state["summary"] is None
        assert state["analysis"] is None
        assert state["review"] is None
        assert state["date_range"] is None
    
    def test_create_coaching_state(self):
        """Test creation of coaching agent state."""
        state = AgentStateFactory.create_coaching_state(
            user_id="test-user",
            tradition="canon-default",
            session_type="meal_suggestion",
            session_id="test-session",
        )
        
        # TypedDict doesn't support isinstance checks, so we validate structure instead
        assert "user_id" in state
        assert "tradition" in state
        assert "session_type" in state
        assert "session_id" in state
        assert "user_goals" in state
        assert "user_preferences" in state
        assert "user_history" in state
        assert "recommendations" in state
        assert "next_actions" in state
        assert "progress_metrics" in state
        
        assert state["user_id"] == "test-user"
        assert state["tradition"] == "canon-default"
        assert state["session_type"] == "meal_suggestion"
        assert state["session_id"] == "test-session"
        assert state["user_goals"] is None
        assert state["user_preferences"] is None
        assert state["user_history"] is None
        assert state["recommendations"] == []
        assert state["next_actions"] == []
        assert state["progress_metrics"] is None
    
    def test_create_multi_agent_state(self):
        """Test creation of multi-agent state."""
        workflow_steps = ["step1", "step2", "step3"]
        
        state = AgentStateFactory.create_multi_agent_state(
            user_id="test-user",
            tradition="canon-default",
            workflow_steps=workflow_steps,
            session_id="test-session",
        )
        
        # TypedDict doesn't support isinstance checks, so we validate structure instead
        assert "user_id" in state
        assert "tradition" in state
        assert "workflow_steps" in state
        assert "current_step" in state
        assert "completed_steps" in state
        assert "active_agents" in state
        assert "agent_results" in state
        assert "coordination_data" in state
        assert "external_data" in state
        assert "integration_results" in state
        
        assert state["user_id"] == "test-user"
        assert state["tradition"] == "canon-default"
        assert state["workflow_steps"] == workflow_steps
        assert state["current_step"] == "step1"
        assert state["completed_steps"] == []
        assert state["active_agents"] == []
        assert state["agent_results"] == {}
        assert state["coordination_data"] == {}
        assert state["external_data"] == {}
        assert state["integration_results"] == {}


class TestStateManager:
    """Test state management utilities."""
    
    def test_update_state(self):
        """Test basic state updates."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        original_updated_at = state["updated_at"]
        
        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        updated_state = StateManager.update_state(state, {
            "output": "test response",
            "generated_response": "test response",
        })
        
        assert updated_state["output"] == "test response"
        assert updated_state["generated_response"] == "test response"
        assert updated_state["updated_at"] > original_updated_at
        assert updated_state["user_id"] == "test-user"  # Unchanged fields preserved
    
    def test_add_error(self):
        """Test adding error information to state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        updated_state = StateManager.add_error(
            state,
            error="Something went wrong",
            error_type="ValidationError",
        )
        
        assert updated_state["error"] == "Something went wrong"
        assert updated_state["error_type"] == "ValidationError"
        assert updated_state["updated_at"] > state["updated_at"]
    
    def test_clear_error(self):
        """Test clearing error information from state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        # Add error first
        state_with_error = StateManager.add_error(state, "test error")
        assert state_with_error["error"] == "test error"
        
        # Clear error
        cleared_state = StateManager.clear_error(state_with_error)
        assert cleared_state["error"] is None
        assert cleared_state["error_type"] is None
    
    def test_add_document_to_context(self):
        """Test adding documents to RAG agent context."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        document = Document(
            page_content="This is a test document",
            metadata={"source": "test", "score": 0.95}
        )
        
        updated_state = StateManager.add_document_to_context(
            state,
            document=document,
            score=0.95,
        )
        
        assert len(updated_state["context"]) == 1
        assert len(updated_state["retrieved_documents"]) == 1
        assert len(updated_state["retrieval_scores"]) == 1
        assert updated_state["context"][0] == document
        assert updated_state["retrieved_documents"][0] == document
        assert updated_state["retrieval_scores"][0] == 0.95
    
    def test_add_document_to_context_without_score(self):
        """Test adding documents without score."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        document = Document(
            page_content="This is a test document",
            metadata={"source": "test"}
        )
        
        updated_state = StateManager.add_document_to_context(
            state,
            document=document,
        )
        
        assert len(updated_state["context"]) == 1
        assert len(updated_state["retrieved_documents"]) == 1
        assert len(updated_state["retrieval_scores"]) == 0  # No score added
    
    def test_set_generated_response(self):
        """Test setting generated response in RAG agent state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        metadata = {"tokens_used": 150, "model": "gpt-4"}
        
        updated_state = StateManager.set_generated_response(
            state,
            response="This is the generated response",
            metadata=metadata,
        )
        
        assert updated_state["generated_response"] == "This is the generated response"
        assert updated_state["response_metadata"] == metadata
        assert updated_state["output"] == "This is the generated response"
    
    def test_set_generated_response_without_metadata(self):
        """Test setting generated response without metadata."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        updated_state = StateManager.set_generated_response(
            state,
            response="This is the generated response",
        )
        
        assert updated_state["generated_response"] == "This is the generated response"
        assert updated_state["response_metadata"] == {}
        assert updated_state["output"] == "This is the generated response"


class TestStateTypeSafety:
    """Test type safety and validation of state structures."""
    
    def test_rag_state_structure(self):
        """Test that RAG state has all required fields."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        # Test that all required fields are present
        required_fields = [
            "user_id", "tradition", "session_id", "input", "output",
            "created_at", "updated_at", "error", "error_type",
            "query", "context", "retrieved_documents", "retrieval_scores",
            "generated_response", "response_metadata"
        ]
        
        for field in required_fields:
            assert field in state
    
    def test_journal_state_structure(self):
        """Test that journal state has all required fields."""
        state = AgentStateFactory.create_journal_state(
            user_id="test-user",
            tradition="canon-default",
            journal_entries=[],
        )
        
        # Test that all required fields are present
        required_fields = [
            "user_id", "tradition", "session_id", "input", "output",
            "created_at", "updated_at", "error", "error_type",
            "journal_entries", "entry_count", "summary", "analysis",
            "review", "date_range", "entry_types"
        ]
        
        for field in required_fields:
            assert field in state
    
    def test_coaching_state_structure(self):
        """Test that coaching state has all required fields."""
        state = AgentStateFactory.create_coaching_state(
            user_id="test-user",
            tradition="canon-default",
            session_type="meal_suggestion",
        )
        
        # Test that all required fields are present
        required_fields = [
            "user_id", "tradition", "session_id", "input", "output",
            "created_at", "updated_at", "error", "error_type",
            "user_goals", "user_preferences", "user_history",
            "session_type", "session_data", "recommendations",
            "next_actions", "progress_metrics"
        ]
        
        for field in required_fields:
            assert field in state
    
    def test_multi_agent_state_structure(self):
        """Test that multi-agent state has all required fields."""
        state = AgentStateFactory.create_multi_agent_state(
            user_id="test-user",
            tradition="canon-default",
            workflow_steps=["step1"],
        )
        
        # Test that all required fields are present
        required_fields = [
            "user_id", "tradition", "session_id", "input", "output",
            "created_at", "updated_at", "error", "error_type",
            "active_agents", "agent_results", "coordination_data",
            "workflow_steps", "current_step", "completed_steps",
            "external_data", "integration_results"
        ]
        
        for field in required_fields:
            assert field in state


class TestStateImmutableOperations:
    """Test that state operations don't modify original state."""
    
    def test_update_state_immutability(self):
        """Test that update_state doesn't modify original state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        original_output = state["output"]
        original_updated_at = state["updated_at"]
        
        updated_state = StateManager.update_state(state, {
            "output": "new output",
        })
        
        # Original state should be unchanged
        assert state["output"] == original_output
        assert state["updated_at"] == original_updated_at
        
        # Updated state should have new values
        assert updated_state["output"] == "new output"
        assert updated_state["updated_at"] > original_updated_at
    
    def test_add_document_immutability(self):
        """Test that add_document_to_context doesn't modify original state."""
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        original_context_length = len(state["context"])
        
        document = Document(page_content="test", metadata={})
        updated_state = StateManager.add_document_to_context(state, document)
        
        # Original state should be unchanged
        assert len(state["context"]) == original_context_length
        
        # Updated state should have new document
        assert len(updated_state["context"]) == original_context_length + 1 