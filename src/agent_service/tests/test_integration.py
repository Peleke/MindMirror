"""
Integration tests for the complete RAG workflow.

This module tests the end-to-end integration between:
- Chat API endpoints
- LangGraph workflows
- Qdrant retrieval
- Embedding services
"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from shared.auth import CurrentUser, get_current_user

from agent_service.app.main import app

client = TestClient(app)


class TestRAGIntegration:
    """Test complete RAG workflow integration."""

    @pytest.fixture
    def mock_user(self):
        """Mock user for testing."""
        return CurrentUser(
            id=UUID("12345678-1234-5678-9abc-123456789abc"),
            supabase_id="test_supabase_id",
            roles=[],
        )

    @pytest.fixture
    def mock_auth_dependency(self, mock_user):
        """Mock authentication dependency."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        yield
        app.dependency_overrides.clear()

    def test_complete_rag_workflow(self, mock_auth_dependency):
        """Test complete RAG workflow from API to retrieval."""
        # Mock the embedding service
        with patch(
            "agent_service.app.services.embedding_service.EmbeddingService.get_embedding"
        ) as mock_embedding:
            mock_embedding.return_value = [0.1] * 1536  # Mock embedding vector

            # Mock Qdrant search
            with patch(
                "agent_service.app.services.qdrant_service.QdrantService.hybrid_search"
            ) as mock_search:
                mock_search.return_value = [
                    {
                        "id": "doc1",
                        "payload": {
                            "content": "Mindfulness is the practice of being present.",
                            "source": "test_document.md",
                            "chunk_id": "chunk_1",
                        },
                        "score": 0.95,
                    }
                ]

                # Mock the chat graph
                with patch(
                    "agent_service.app.api.chat.ChatGraphFactory"
                ) as mock_factory:
                    mock_graph = Mock()
                    mock_graph.invoke.return_value = {
                        "user_id": "12345678-1234-5678-9abc-123456789abc",
                        "tradition_id": "test_tradition",
                        "messages": [
                            {
                                "role": "user",
                                "content": "What is mindfulness?",
                                "timestamp": "2024-01-01T00:00:00",
                            },
                            {
                                "role": "assistant",
                                "content": "Mindfulness is the practice of being present and aware.",
                                "timestamp": "2024-01-01T00:00:01",
                            },
                        ],
                        "query": "What is mindfulness?",
                        "last_response": "Mindfulness is the practice of being present and aware.",
                        "retrieved_documents": [
                            {
                                "id": "doc1",
                                "content": "Mindfulness is the practice of being present.",
                                "score": 0.95,
                            }
                        ],
                        "metadata": {},
                        "error": None,
                        "error_type": None,
                    }

                    mock_builder = Mock()
                    mock_builder.get_chat_graph.return_value = mock_graph
                    mock_factory.create_default_chat_graph.return_value = mock_builder

                    # Make the API call
                    response = client.post(
                        "/chat/ask",
                        json={
                            "message": "What is mindfulness?",
                            "tradition_id": "test_tradition",
                            "search_type": "hybrid",
                        },
                    )

                    # Verify the response
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()

                    assert (
                        data["response"]
                        == "Mindfulness is the practice of being present and aware."
                    )
                    assert len(data["retrieved_documents"]) == 1
                    assert data["retrieved_documents"][0]["id"] == "doc1"
                    assert data["metadata"]["documents_retrieved"] == 1
                    assert data["metadata"]["search_type"] == "hybrid"

    def test_rag_with_multiple_documents(self, mock_auth_dependency):
        """Test RAG workflow with multiple retrieved documents."""
        with patch(
            "agent_service.app.services.embedding_service.EmbeddingService.get_embedding"
        ) as mock_embedding:
            mock_embedding.return_value = [0.1] * 1536

            with patch(
                "agent_service.app.services.qdrant_service.QdrantService.hybrid_search"
            ) as mock_search:
                mock_search.return_value = [
                    {
                        "id": "doc1",
                        "payload": {
                            "content": "Mindfulness is the practice of being present.",
                            "source": "doc1.md",
                            "chunk_id": "chunk_1",
                        },
                        "score": 0.95,
                    },
                    {
                        "id": "doc2",
                        "payload": {
                            "content": "Meditation helps develop mindfulness skills.",
                            "source": "doc2.md",
                            "chunk_id": "chunk_2",
                        },
                        "score": 0.87,
                    },
                ]

                with patch(
                    "agent_service.app.api.chat.ChatGraphFactory"
                ) as mock_factory:
                    mock_graph = Mock()
                    mock_graph.invoke.return_value = {
                        "user_id": "12345678-1234-5678-9abc-123456789abc",
                        "tradition_id": "test_tradition",
                        "messages": [
                            {
                                "role": "user",
                                "content": "How do I practice mindfulness?",
                                "timestamp": "2024-01-01T00:00:00",
                            },
                            {
                                "role": "assistant",
                                "content": "You can practice mindfulness through meditation and being present.",
                                "timestamp": "2024-01-01T00:00:01",
                            },
                        ],
                        "query": "How do I practice mindfulness?",
                        "last_response": "You can practice mindfulness through meditation and being present.",
                        "retrieved_documents": [
                            {
                                "id": "doc1",
                                "content": "Mindfulness is the practice of being present.",
                                "score": 0.95,
                            },
                            {
                                "id": "doc2",
                                "content": "Meditation helps develop mindfulness skills.",
                                "score": 0.87,
                            },
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
                            "message": "How do I practice mindfulness?",
                            "tradition_id": "test_tradition",
                        },
                    )

                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()

                    assert len(data["retrieved_documents"]) == 2
                    assert data["metadata"]["documents_retrieved"] == 2

    def test_rag_with_no_documents(self, mock_auth_dependency):
        """Test RAG workflow when no documents are found."""
        with patch(
            "agent_service.app.services.embedding_service.EmbeddingService.get_embedding"
        ) as mock_embedding:
            mock_embedding.return_value = [0.1] * 1536

            with patch(
                "agent_service.app.services.qdrant_service.QdrantService.hybrid_search"
            ) as mock_search:
                mock_search.return_value = []  # No documents found

                with patch(
                    "agent_service.app.api.chat.ChatGraphFactory"
                ) as mock_factory:
                    mock_graph = Mock()
                    mock_graph.invoke.return_value = {
                        "user_id": "12345678-1234-5678-9abc-123456789abc",
                        "tradition_id": "test_tradition",
                        "messages": [
                            {
                                "role": "user",
                                "content": "What is quantum physics?",
                                "timestamp": "2024-01-01T00:00:00",
                            },
                            {
                                "role": "assistant",
                                "content": "I don't have specific information about quantum physics in my knowledge base.",
                                "timestamp": "2024-01-01T00:00:01",
                            },
                        ],
                        "query": "What is quantum physics?",
                        "last_response": "I don't have specific information about quantum physics in my knowledge base.",
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
                            "message": "What is quantum physics?",
                            "tradition_id": "test_tradition",
                        },
                    )

                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()

                    assert len(data["retrieved_documents"]) == 0
                    assert data["metadata"]["documents_retrieved"] == 0

    def test_conversation_continuity(self, mock_auth_dependency):
        """Test that conversations maintain context across multiple messages."""
        with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
            mock_graph = Mock()

            # First message
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello",
                        "timestamp": "2024-01-01T00:00:00",
                    },
                    {
                        "role": "assistant",
                        "content": "Hi there! How can I help you?",
                        "timestamp": "2024-01-01T00:00:01",
                    },
                ],
                "query": "Hello",
                "last_response": "Hi there! How can I help you?",
                "retrieved_documents": [],
                "metadata": {},
                "error": None,
                "error_type": None,
            }

            mock_builder = Mock()
            mock_builder.get_chat_graph.return_value = mock_graph
            mock_factory.create_default_chat_graph.return_value = mock_builder

            # First message
            response1 = client.post(
                "/chat/ask", json={"message": "Hello", "tradition_id": "test_tradition"}
            )

            assert response1.status_code == status.HTTP_200_OK
            data1 = response1.json()
            conversation_id = data1["conversation_id"]

            # Second message in same conversation
            mock_graph.invoke.return_value = {
                "user_id": "12345678-1234-5678-9abc-123456789abc",
                "tradition_id": "test_tradition",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello",
                        "timestamp": "2024-01-01T00:00:00",
                    },
                    {
                        "role": "assistant",
                        "content": "Hi there! How can I help you?",
                        "timestamp": "2024-01-01T00:00:01",
                    },
                    {
                        "role": "user",
                        "content": "Tell me about mindfulness",
                        "timestamp": "2024-01-01T00:00:02",
                    },
                    {
                        "role": "assistant",
                        "content": "Mindfulness is about being present.",
                        "timestamp": "2024-01-01T00:00:03",
                    },
                ],
                "query": "Tell me about mindfulness",
                "last_response": "Mindfulness is about being present.",
                "retrieved_documents": [],
                "metadata": {},
                "error": None,
                "error_type": None,
            }

            response2 = client.post(
                "/chat/ask",
                json={
                    "message": "Tell me about mindfulness",
                    "tradition_id": "test_tradition",
                    "conversation_id": conversation_id,
                },
            )

            assert response2.status_code == status.HTTP_200_OK
            data2 = response2.json()

            # Should be the same conversation
            assert data2["conversation_id"] == conversation_id

    def test_error_handling_in_rag_chain(self, mock_auth_dependency):
        """Test error handling when RAG chain fails."""
        with patch(
            "agent_service.app.services.embedding_service.EmbeddingService.get_embedding"
        ) as mock_embedding:
            # Simulate embedding service failure
            mock_embedding.side_effect = Exception("Embedding service unavailable")

            with patch("agent_service.app.api.chat.ChatGraphFactory") as mock_factory:
                mock_graph = Mock()
                mock_graph.invoke.return_value = {
                    "user_id": "12345678-1234-5678-9abc-123456789abc",
                    "tradition_id": "test_tradition",
                    "messages": [
                        {
                            "role": "user",
                            "content": "What is mindfulness?",
                            "timestamp": "2024-01-01T00:00:00",
                        },
                        {
                            "role": "assistant",
                            "content": "I apologize, but I encountered an error processing your request.",
                            "timestamp": "2024-01-01T00:00:01",
                        },
                    ],
                    "query": "What is mindfulness?",
                    "last_response": "I apologize, but I encountered an error processing your request.",
                    "retrieved_documents": [],
                    "metadata": {},
                    "error": "Embedding service unavailable",
                    "error_type": "EmbeddingError",
                }

                mock_builder = Mock()
                mock_builder.get_chat_graph.return_value = mock_graph
                mock_factory.create_default_chat_graph.return_value = mock_builder

                response = client.post(
                    "/chat/ask",
                    json={
                        "message": "What is mindfulness?",
                        "tradition_id": "test_tradition",
                    },
                )

                assert response.status_code == status.HTTP_200_OK
                data = response.json()

                # Should still return a response, but with error metadata
                assert data["metadata"]["has_error"] is True
                assert "error" in data["metadata"]
                assert data["metadata"]["error"] == "Embedding service unavailable"


class TestServiceIntegration:
    """Test service layer integration."""

    def test_embedding_service_integration(self):
        """Test embedding service integration."""
        from agent_service.app.services.embedding_service import EmbeddingService

        service = EmbeddingService()

        # Test that service can be instantiated
        assert service is not None
        assert hasattr(service, "get_embedding")

    def test_qdrant_service_integration(self):
        """Test Qdrant service integration."""
        from agent_service.app.services.qdrant_service import QdrantService

        service = QdrantService()

        # Test that service can be instantiated
        assert service is not None
        assert hasattr(service, "hybrid_search")
        assert hasattr(service, "search_knowledge_base")
        assert hasattr(service, "search_personal_entries")
        assert hasattr(service, "health_check")

    def test_search_service_integration(self):
        """Test search service integration."""
        from agent_service.app.services.embedding_service import EmbeddingService
        from agent_service.app.services.qdrant_service import QdrantService
        from agent_service.app.services.search_service import SearchService

        embedding_service = EmbeddingService()
        qdrant_service = QdrantService()
        search_service = SearchService(
            embedding_service=embedding_service, qdrant_service=qdrant_service
        )

        # Test that service can be instantiated
        assert search_service is not None
        assert hasattr(search_service, "create_retriever")
        assert hasattr(search_service, "semantic_search")
        assert hasattr(search_service, "search_knowledge_base")
        assert hasattr(search_service, "search_personal_entries")
