"""
Test Driven Development tests for AgentServiceClient.

These tests validate the client behavior against mocked HTTP responses,
ensuring the client correctly handles all success and error scenarios for RAG operations.
"""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from shared.clients.agent_client import (AgentServiceClient,
                                         DocumentSearchResult,
                                         SuggestionResponse,
                                         create_agent_client)
from shared.clients.base import (AuthContext, AuthenticationError,
                                 DataNotFoundError, ServiceClientError,
                                 ServiceConfig, ServiceUnavailableError)


# Fixtures
@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def auth_context(user_id):
    return AuthContext(user_id=user_id)


@pytest.fixture
def service_config():
    return ServiceConfig(
        base_url="http://test-agent-service:8000",
        service_name="test-agent-service",
        timeout=10.0,
        max_retries=1,
    )


@pytest.fixture
def agent_client(service_config):
    return AgentServiceClient(service_config)


@pytest.fixture
def mock_search_response():
    """Sample search response matching the agent service format."""
    return {
        "results": [
            {
                "content": "This is a sample document about productivity methods.",
                "score": 0.95,
                "metadata": {
                    "title": "Productivity Guide",
                    "author": "John Doe",
                    "date": "2024-01-15"
                },
                "document_id": "doc-123",
                "source_type": "user_upload"
            },
            {
                "content": "Another document discussing time management techniques.",
                "score": 0.87,
                "metadata": {
                    "title": "Time Management",
                    "category": "self-help"
                },
                "document_id": "doc-456",
                "source_type": "web_article"
            }
        ]
    }


@pytest.fixture
def mock_suggestion_response():
    """Sample AI suggestion response."""
    return {
        "suggestion": "Based on your recent journal entries, consider focusing on gratitude practices.",
        "confidence": 0.92,
        "reasoning": "Your entries show stress patterns that gratitude practices can help address.",
        "sources": ["doc-123", "journal-entry-456"]
    }


# Test Data Transfer Objects
class TestDocumentSearchResult:
    """Test the DocumentSearchResult DTO creation and data handling."""
    
    def test_from_response_complete_data(self):
        """Test creating DocumentSearchResult from complete response data."""
        response_data = {
            "content": "Test content",
            "score": 0.95,
            "metadata": {"title": "Test Doc"},
            "document_id": "doc-123",
            "source_type": "user_upload"
        }
        
        result = DocumentSearchResult.from_response(response_data)
        
        assert result.content == "Test content"
        assert result.score == 0.95
        assert result.metadata == {"title": "Test Doc"}
        assert result.document_id == "doc-123"
        assert result.source_type == "user_upload"
    
    def test_from_response_minimal_data(self):
        """Test creating DocumentSearchResult with minimal required data."""
        response_data = {
            "content": "Minimal content"
        }
        
        result = DocumentSearchResult.from_response(response_data)
        
        assert result.content == "Minimal content"
        assert result.score == 0.0
        assert result.metadata == {}
        assert result.document_id is None
        assert result.source_type is None


class TestSuggestionResponse:
    """Test the SuggestionResponse DTO creation and data handling."""
    
    def test_from_response_complete_data(self):
        """Test creating SuggestionResponse from complete response data."""
        response_data = {
            "suggestion": "Test suggestion",
            "confidence": 0.85,
            "reasoning": "Test reasoning",
            "sources": ["doc-1", "doc-2"]
        }
        
        response = SuggestionResponse.from_response(response_data)
        
        assert response.suggestion == "Test suggestion"
        assert response.confidence == 0.85
        assert response.reasoning == "Test reasoning"
        assert response.sources == ["doc-1", "doc-2"]
    
    def test_from_response_minimal_data(self):
        """Test creating SuggestionResponse with minimal required data."""
        response_data = {
            "suggestion": "Minimal suggestion"
        }
        
        response = SuggestionResponse.from_response(response_data)
        
        assert response.suggestion == "Minimal suggestion"
        assert response.confidence == 0.0
        assert response.reasoning is None
        assert response.sources == []


# Test AgentServiceClient
class TestAgentServiceClient:
    """Test the AgentServiceClient functionality."""
    
    @pytest.mark.asyncio
    async def test_search_documents_success(
        self, agent_client, auth_context, mock_search_response
    ):
        """Test successful document search."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_search_response
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                results = await client.search_documents(
                    user_id=auth_context.user_id,
                    query="productivity methods",
                    limit=5
                )
            
            # Verify the request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            
            # Check method and path
            assert call_args[1]['method'] == 'POST'
            assert call_args[1]['url'].endswith('/search/documents')
            
            # Check request data
            request_data = call_args[1]['json']
            assert request_data['query'] == "productivity methods"
            assert request_data['limit'] == 5
            assert request_data['filters'] == {}
            
            # Check headers
            headers = call_args[1]['headers']
            assert headers['x-internal-id'] == str(auth_context.user_id)
            
            # Verify results were parsed correctly
            assert len(results) == 2
            assert results[0].content == "This is a sample document about productivity methods."
            assert results[0].score == 0.95
            assert results[0].document_id == "doc-123"
            assert results[1].content == "Another document discussing time management techniques."
            assert results[1].score == 0.87
    
    @pytest.mark.asyncio
    async def test_search_documents_with_filters(
        self, agent_client, auth_context, mock_search_response
    ):
        """Test document search with filters."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_search_response
            mock_request.return_value = mock_response
            
            filters = {"source_type": "user_upload", "date_range": "last_30_days"}
            
            async with agent_client as client:
                results = await client.search_documents(
                    user_id=auth_context.user_id,
                    query="test query",
                    filters=filters
                )
            
            # Check request data includes filters
            call_args = mock_request.call_args
            request_data = call_args[1]['json']
            assert request_data['filters'] == filters
    
    @pytest.mark.asyncio
    async def test_get_ai_suggestions_success(
        self, agent_client, auth_context, mock_suggestion_response
    ):
        """Test successful AI suggestions retrieval."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_suggestion_response
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                suggestion = await client.get_ai_suggestions(
                    user_id=auth_context.user_id,
                    context="Recent journal entries show stress",
                    suggestion_type="journal_prompt"
                )
            
            # Verify the request was made correctly
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'POST'
            assert call_args[1]['url'].endswith('/ai/suggestions')
            
            request_data = call_args[1]['json']
            assert request_data['context'] == "Recent journal entries show stress"
            assert request_data['suggestion_type'] == "journal_prompt"
            assert request_data['include_sources'] is True
            
            # Verify response was parsed correctly
            assert suggestion.suggestion == "Based on your recent journal entries, consider focusing on gratitude practices."
            assert suggestion.confidence == 0.92
            assert suggestion.reasoning == "Your entries show stress patterns that gratitude practices can help address."
            assert suggestion.sources == ["doc-123", "journal-entry-456"]
    
    @pytest.mark.asyncio
    async def test_index_document_success(self, agent_client, auth_context):
        """Test successful document indexing."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = {"success": True}
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                success = await client.index_document(
                    user_id=auth_context.user_id,
                    document_id="new-doc-123",
                    content="This is new document content to index",
                    metadata={"title": "New Document", "category": "personal"}
                )
            
            # Verify the request was made correctly
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'POST'
            assert call_args[1]['url'].endswith('/index/document')
            
            request_data = call_args[1]['json']
            assert request_data['document_id'] == "new-doc-123"
            assert request_data['content'] == "This is new document content to index"
            assert request_data['metadata'] == {"title": "New Document", "category": "personal"}
            assert request_data['source_type'] == "user_upload"
            
            # Verify response
            assert success is True
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, agent_client, auth_context):
        """Test successful document deletion."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = {"success": True}
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                success = await client.delete_document(
                    user_id=auth_context.user_id,
                    document_id="doc-to-delete"
                )
            
            # Verify the request was made correctly
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'DELETE'
            assert call_args[1]['url'].endswith('/index/document/doc-to-delete')
            
            # Verify response
            assert success is True
    
    @pytest.mark.asyncio
    async def test_get_user_stats_success(self, agent_client, auth_context):
        """Test successful user statistics retrieval."""
        mock_stats = {
            "document_count": 42,
            "index_size_mb": 15.7,
            "last_indexed": "2024-01-15T10:30:00Z"
        }
        
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = {"stats": mock_stats}
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                stats = await client.get_user_stats(user_id=auth_context.user_id)
            
            # Verify the request was made correctly
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'GET'
            assert call_args[1]['url'].endswith('/user/stats')
            
            # Verify response
            assert stats == mock_stats
    
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, agent_client, auth_context):
        """Test handling of authentication errors."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.is_success = False
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                with pytest.raises(AuthenticationError) as exc_info:
                    await client.search_documents(
                        user_id=auth_context.user_id,
                        query="test"
                    )
                
                assert exc_info.value.status_code == 401
                assert exc_info.value.service == "test-agent-service"
    
    @pytest.mark.asyncio
    async def test_service_unavailable_error_handling(self, agent_client, auth_context):
        """Test handling of 5xx server errors."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.is_success = False
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                with pytest.raises(ServiceUnavailableError) as exc_info:
                    await client.get_ai_suggestions(
                        user_id=auth_context.user_id,
                        context="test context"
                    )
                
                assert exc_info.value.status_code == 503
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, agent_client, auth_context):
        """Test handling of empty search results."""
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = {"results": []}
            mock_request.return_value = mock_response
            
            async with agent_client as client:
                results = await client.search_documents(
                    user_id=auth_context.user_id,
                    query="no matches"
                )
            
            assert results == []


# Test Factory Function
class TestAgentClientFactory:
    """Test the factory function for creating agent clients."""
    
    def test_create_agent_client_default_config(self):
        """Test creating client with default configuration."""
        client = create_agent_client()
        
        assert client.config.base_url == "http://localhost:8000"
        assert client.config.service_name == "agent-service"
        assert client.config.timeout == 30.0
        assert client.config.max_retries == 3
    
    def test_create_agent_client_custom_url(self):
        """Test creating client with custom base URL."""
        custom_url = "http://production-agent:8000"
        client = create_agent_client(base_url=custom_url)
        
        assert client.config.base_url == custom_url 