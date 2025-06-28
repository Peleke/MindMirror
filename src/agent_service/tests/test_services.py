"""
Tests for the new service layer components.

These tests verify that the service layer works correctly
and provides proper abstraction over the underlying clients.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List

from agent_service.app.services.embedding_service import EmbeddingService
from agent_service.app.services.qdrant_service import QdrantService
from agent_service.app.services.search_service import SearchService
from agent_service.app.clients.embedding_client import EmbeddingClient
from agent_service.app.clients.qdrant_client import QdrantClient


class TestEmbeddingService:
    """Test embedding service functionality."""
    
    @pytest.fixture
    def mock_embedding_client(self):
        """Create a mock embedding client."""
        client = Mock(spec=EmbeddingClient)
        client.get_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        client.get_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        client.health_check = AsyncMock(return_value=True)
        return client
    
    @pytest.fixture
    def embedding_service(self, mock_embedding_client):
        """Create embedding service with mock client."""
        return EmbeddingService(embedding_client=mock_embedding_client)
    
    @pytest.mark.asyncio
    async def test_get_embedding_success(self, embedding_service, mock_embedding_client):
        """Test successful embedding generation."""
        result = await embedding_service.get_embedding("test text")
        
        assert result == [0.1, 0.2, 0.3]
        mock_embedding_client.get_embedding.assert_called_once_with("test text")
    
    @pytest.mark.asyncio
    async def test_get_embedding_failure(self, embedding_service, mock_embedding_client):
        """Test embedding generation failure."""
        mock_embedding_client.get_embedding.return_value = None
        
        result = await embedding_service.get_embedding("test text")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_embeddings_success(self, embedding_service, mock_embedding_client):
        """Test successful batch embedding generation."""
        texts = ["text1", "text2"]
        result = await embedding_service.get_embeddings(texts)
        
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_embedding_client.get_embeddings.assert_called_once_with(texts)
    
    @pytest.mark.asyncio
    async def test_get_embedding_safe_with_fallback(self, embedding_service, mock_embedding_client):
        """Test safe embedding with fallback."""
        mock_embedding_client.get_embedding.return_value = None
        fallback = [0.0, 0.0, 0.0]
        
        result = await embedding_service.get_embedding_safe("test text", fallback)
        
        assert result == fallback
    
    def test_validate_embedding_valid(self, embedding_service):
        """Test embedding validation with valid embedding."""
        embedding = [0.1, 0.2, 0.3]
        assert embedding_service.validate_embedding(embedding) is True
    
    def test_validate_embedding_invalid(self, embedding_service):
        """Test embedding validation with invalid embedding."""
        assert embedding_service.validate_embedding(None) is False
        assert embedding_service.validate_embedding("not a list") is False
        assert embedding_service.validate_embedding(["not", "numbers"]) is False


class TestQdrantService:
    """Test Qdrant service functionality."""
    
    @pytest.fixture
    def mock_qdrant_client(self):
        """Create a mock Qdrant client."""
        client = Mock(spec=QdrantClient)
        client.search_knowledge_base = AsyncMock(return_value=[])
        client.search_personal_entries = AsyncMock(return_value=[])
        client.hybrid_search = AsyncMock(return_value=[])
        client.health_check = AsyncMock(return_value=True)
        return client
    
    @pytest.fixture
    def qdrant_service(self, mock_qdrant_client):
        """Create Qdrant service with mock client."""
        return QdrantService(qdrant_client=mock_qdrant_client)
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, qdrant_service, mock_qdrant_client):
        """Test knowledge base search."""
        await qdrant_service.search_knowledge_base("test query", "test-tradition")
        
        mock_qdrant_client.search_knowledge_base.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_personal_entries(self, qdrant_service, mock_qdrant_client):
        """Test personal entries search."""
        await qdrant_service.search_personal_entries("test query", "user123", "test-tradition")
        
        mock_qdrant_client.search_personal_entries.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, qdrant_service, mock_qdrant_client):
        """Test hybrid search."""
        await qdrant_service.hybrid_search("test query", "user123", "test-tradition")
        
        mock_qdrant_client.hybrid_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self, qdrant_service, mock_qdrant_client):
        """Test health check."""
        result = await qdrant_service.health_check()
        
        assert result is True
        mock_qdrant_client.health_check.assert_called_once()


class TestSearchService:
    """Test search service functionality."""
    
    @pytest.fixture
    def mock_embedding_service(self):
        """Create a mock embedding service."""
        service = Mock(spec=EmbeddingService)
        service.get_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        service.validate_embedding = Mock(return_value=True)
        return service
    
    @pytest.fixture
    def mock_qdrant_service(self):
        """Create a mock Qdrant service."""
        service = Mock(spec=QdrantService)
        service.hybrid_search = AsyncMock(return_value=[])
        service.search_knowledge_base = AsyncMock(return_value=[])
        service.search_personal_entries = AsyncMock(return_value=[])
        service.health_check = AsyncMock(return_value=True)
        return service
    
    @pytest.fixture
    def search_service(self, mock_qdrant_service, mock_embedding_service):
        """Create search service with mock dependencies."""
        return SearchService(
            qdrant_service=mock_qdrant_service,
            embedding_service=mock_embedding_service
        )
    
    @pytest.mark.asyncio
    async def test_semantic_search_success(self, search_service, mock_embedding_service, mock_qdrant_service):
        """Test successful semantic search."""
        result = await search_service.semantic_search("test query", "user123")
        
        assert result == []
        mock_embedding_service.get_embedding.assert_called_once_with("test query")
        mock_qdrant_service.hybrid_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_semantic_search_embedding_failure(self, search_service, mock_embedding_service, mock_qdrant_service):
        """Test semantic search with embedding failure."""
        mock_embedding_service.get_embedding.return_value = None
        
        result = await search_service.semantic_search("test query", "user123")
        
        assert result == []
        mock_qdrant_service.hybrid_search.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, search_service, mock_qdrant_service):
        """Test knowledge base search."""
        await search_service.search_knowledge_base("test query", "test-tradition")
        
        mock_qdrant_service.search_knowledge_base.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_personal_entries(self, search_service, mock_qdrant_service):
        """Test personal entries search."""
        await search_service.search_personal_entries("test query", "user123", "test-tradition")
        
        mock_qdrant_service.search_personal_entries.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self, search_service, mock_qdrant_service, mock_embedding_service):
        """Test health check."""
        # Create a mock embedding client and attach it to the mock embedding service
        mock_embedding_client = Mock()
        mock_embedding_client.health_check = AsyncMock(return_value=True)
        mock_embedding_service.embedding_client = mock_embedding_client
        
        result = await search_service.health_check()
        
        assert result["qdrant"] is True
        assert result["embedding"] is True
        assert result["overall"] is True


class TestServiceIntegration:
    """Integration tests for service layer."""
    
    @pytest.mark.asyncio
    async def test_search_service_with_real_services(self):
        """Test search service with real service instances."""
        # This test would use real service instances to verify integration
        # For now, we'll just verify that services can be instantiated
        search_service = SearchService()
        
        assert search_service.qdrant_service is not None
        assert search_service.embedding_service is not None
    
    @pytest.mark.asyncio
    async def test_service_dependency_injection(self):
        """Test that services can be injected with custom dependencies."""
        mock_qdrant_client = Mock(spec=QdrantClient)
        mock_embedding_client = Mock(spec=EmbeddingClient)
        
        qdrant_service = QdrantService(qdrant_client=mock_qdrant_client)
        embedding_service = EmbeddingService(embedding_client=mock_embedding_client)
        search_service = SearchService(
            qdrant_service=qdrant_service,
            embedding_service=embedding_service
        )
        
        assert search_service.qdrant_service.qdrant_client == mock_qdrant_client
        assert search_service.embedding_service.embedding_client == mock_embedding_client 