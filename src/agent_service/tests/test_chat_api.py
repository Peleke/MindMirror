"""
Tests for chat API endpoints.

This module tests the chat API functionality including
ask operations, conversation management, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
from uuid import UUID

from agent_service.app.main import app
from shared.auth import CurrentUser, get_current_user

client = TestClient(app)


class TestChatAPI:
    """Test chat API endpoints."""
    
    @pytest.fixture
    def mock_user(self):
        """Mock user for testing."""
        return CurrentUser(
            id=UUID("12345678-1234-5678-9abc-123456789abc"),
            supabase_id="test_supabase_id",
            roles=[]
        )
    
    @pytest.fixture
    def mock_auth_dependency(self, mock_user):
        """Mock authentication dependency."""
        # Override the dependency in the FastAPI app
        app.dependency_overrides[get_current_user] = lambda: mock_user
        yield
        # Clean up after test
        app.dependency_overrides.clear()
    
    def test_ask_question_success(self, mock_auth_dependency):
        """Test successful ask question."""
        # Mock the entire chain to avoid calling real services
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            # Mock the chat graph
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {"role": "user", "content": "What is mindfulness?", "timestamp": "2024-01-01T00:00:00"},
                    {"role": "assistant", "content": "Mindfulness is the practice of being present and aware of your thoughts and feelings without judgment.", "timestamp": "2024-01-01T00:00:01"}
                ],
                "query": "What is mindfulness?",
                "last_response": "Mindfulness is the practice of being present and aware of your thoughts and feelings without judgment.",
                "retrieved_documents": [
                    {"id": "doc1", "content": "Mindfulness content", "score": 0.9}
                ],
                "metadata": {},
                "error": None,
                "error_type": None,
            }
            
            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder
            
            response = client.post(
                "/chat/ask",
                json={
                    "message": "What is mindfulness?",
                    "tradition_id": "test_tradition",
                    "search_type": "hybrid"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert "response" in data
            assert "conversation_id" in data
            assert "retrieved_documents" in data
            assert "metadata" in data
            
            assert data["response"] == "Mindfulness is the practice of being present and aware of your thoughts and feelings without judgment."
            assert len(data["retrieved_documents"]) == 1
            assert data["metadata"]["user_id"] == "12345678-1234-5678-9abc-123456789abc"
            assert data["metadata"]["tradition_id"] == "test_tradition"
    
    def test_ask_question_with_conversation_id(self, mock_auth_dependency):
        """Test ask question with existing conversation."""
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            # Mock the chat graph
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"},
                    {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T00:00:01"},
                    {"role": "user", "content": "What is mindfulness?", "timestamp": "2024-01-01T00:00:02"},
                    {"role": "assistant", "content": "Mindfulness is the practice of being present.", "timestamp": "2024-01-01T00:00:03"}
                ],
                "query": "What is mindfulness?",
                "last_response": "Mindfulness is the practice of being present.",
                "retrieved_documents": [],
                "metadata": {},
                "error": None,
                "error_type": None,
            }
            
            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder
            
            response = client.post(
                "/chat/ask",
                json={
                    "message": "What is mindfulness?",
                    "tradition_id": "test_tradition",
                    "conversation_id": "existing_conv_123"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["conversation_id"] == "existing_conv_123"
    
    def test_ask_question_error_handling(self, mock_auth_dependency):
        """Test error handling in ask question."""
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            # Mock an exception
            mock_factory.create_default_chat_graph.side_effect = Exception("Graph creation failed")
            
            response = client.post(
                "/chat/ask",
                json={
                    "message": "What is mindfulness?",
                    "tradition_id": "test_tradition"
                }
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Failed to process chat request" in data["detail"]
    
    def test_get_conversations(self, mock_auth_dependency):
        """Test getting user conversations."""
        # First, create a conversation
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"},
                    {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T00:00:01"}
                ],
                "query": "Hello",
                "last_response": "Hi there!",
                "retrieved_documents": [],
                "metadata": {},
                "error": None,
                "error_type": None,
            }
            
            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder
            
            # Create a conversation
            client.post(
                "/chat/ask",
                json={
                    "message": "Hello",
                    "tradition_id": "test_tradition"
                }
            )
        
        # Now get conversations
        response = client.get("/chat/conversations")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            conversation = data[0]
            assert "conversation_id" in conversation
            assert "messages" in conversation
            assert "created_at" in conversation
            assert "updated_at" in conversation
    
    def test_get_conversations_with_limit(self, mock_auth_dependency):
        """Test getting conversations with limit parameter."""
        response = client.get("/chat/conversations?limit=5")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_get_conversation_success(self, mock_auth_dependency):
        """Test getting a specific conversation."""
        # First, create a conversation
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"},
                    {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T00:00:01"}
                ],
                "query": "Hello",
                "last_response": "Hi there!",
                "retrieved_documents": [],
                "metadata": {},
                "error": None,
                "error_type": None,
            }
            
            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder
            
            # Create a conversation
            create_response = client.post(
                "/chat/ask",
                json={
                    "message": "Hello",
                    "tradition_id": "test_tradition"
                }
            )
            
            conversation_id = create_response.json()["conversation_id"]
        
        # Now get the specific conversation
        response = client.get(f"/chat/conversations/{conversation_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["conversation_id"] == conversation_id
        assert "messages" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_conversation_not_found(self, mock_auth_dependency):
        """Test getting a non-existent conversation."""
        response = client.get("/chat/conversations/nonexistent_conv")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Conversation not found" in data["detail"]
    
    def test_delete_conversation_success(self, mock_auth_dependency):
        """Test deleting a conversation."""
        # First, create a conversation
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"},
                    {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T00:00:01"}
                ],
                "query": "Hello",
                "last_response": "Hi there!",
                "retrieved_documents": [],
                "metadata": {},
                "error": None,
                "error_type": None,
            }
            
            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder
            
            # Create a conversation
            create_response = client.post(
                "/chat/ask",
                json={
                    "message": "Hello",
                    "tradition_id": "test_tradition"
                }
            )
            
            conversation_id = create_response.json()["conversation_id"]
        
        # Now delete the conversation
        response = client.delete(f"/chat/conversations/{conversation_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Conversation deleted successfully"
        
        # Verify conversation is deleted
        get_response = client.get(f"/chat/conversations/{conversation_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_conversation_not_found(self, mock_auth_dependency):
        """Test deleting a non-existent conversation."""
        response = client.delete("/chat/conversations/nonexistent_conv")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Conversation not found" in data["detail"]
    
    def test_clear_conversation_success(self, mock_auth_dependency):
        """Test clearing a conversation."""
        # First, create a conversation
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"},
                    {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T00:00:01"}
                ],
                "query": "Hello",
                "last_response": "Hi there!",
                "retrieved_documents": [],
                "metadata": {},
                "error": None,
                "error_type": None,
            }
            
            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder
            
            # Create a conversation
            create_response = client.post(
                "/chat/ask",
                json={
                    "message": "Hello",
                    "tradition_id": "test_tradition"
                }
            )
            
            conversation_id = create_response.json()["conversation_id"]
        
        # Now clear the conversation
        response = client.post(f"/chat/conversations/{conversation_id}/clear")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Conversation cleared successfully"
        
        # Verify conversation is cleared but still exists
        get_response = client.get(f"/chat/conversations/{conversation_id}")
        assert get_response.status_code == status.HTTP_200_OK
        
        data = get_response.json()
        assert len(data["messages"]) == 0
    
    def test_clear_conversation_not_found(self, mock_auth_dependency):
        """Test clearing a non-existent conversation."""
        response = client.post("/chat/conversations/nonexistent_conv/clear")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Conversation not found" in data["detail"]
    
    def test_ask_question_invalid_request(self, mock_auth_dependency):
        """Test ask question with invalid request data."""
        response = client.post(
            "/chat/ask",
            json={
                # Missing required 'message' field
                "tradition_id": "test_tradition"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_ask_question_empty_message(self, mock_auth_dependency):
        """Test ask question with empty message."""
        response = client.post(
            "/chat/ask",
            json={
                "message": "",
                "tradition_id": "test_tradition"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_ask_question_with_error_in_response(self, mock_auth_dependency):
        """Test ask question when graph returns an error."""
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            # Mock the chat graph with error
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {"role": "user", "content": "What is mindfulness?", "timestamp": "2024-01-01T00:00:00"},
                    {"role": "assistant", "content": "I apologize, but I encountered an error.", "timestamp": "2024-01-01T00:00:01"}
                ],
                "query": "What is mindfulness?",
                "last_response": "I apologize, but I encountered an error.",
                "retrieved_documents": [],
                "metadata": {},
                "error": "Failed to retrieve documents",
                "error_type": "RetrievalError",
            }
            
            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder
            
            response = client.post(
                "/chat/ask",
                json={
                    "message": "What is mindfulness?",
                    "tradition_id": "test_tradition"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["metadata"]["has_error"] is True
            assert "error" in data["metadata"]
            assert data["metadata"]["error"] == "Failed to retrieve documents" 