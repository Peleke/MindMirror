"""Tests for embedding services."""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import httpx
import asyncio
import numpy as np

from src.utils.embedding import (
    OllamaEmbeddingService,
    OpenAIEmbeddingService,
    SentenceTransformersEmbeddingService,
    MockEmbeddingService,
    EmbeddingServiceFactory,
    get_embedding_service,
    set_embedding_service,
    get_embedding,
    get_embeddings
)
from src.config import Config


class TestOllamaEmbeddingService:
    """Test OllamaEmbeddingService."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        service = OllamaEmbeddingService()
        assert service.base_url == "http://host.docker.internal:11434"
        assert service.model == "nomic-embed-text"
        assert service.client is not None

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        custom_url = "http://custom-ollama:11434"
        custom_model = "custom-model"
        
        service = OllamaEmbeddingService(base_url=custom_url, model=custom_model)
        assert service.base_url == custom_url
        assert service.model == custom_model

    @pytest.mark.asyncio
    async def test_get_embedding_success(self):
        """Test successful embedding generation."""
        service = OllamaEmbeddingService()
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3] * (Config.VECTOR_SIZE // 3)
        }
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await service.get_embedding("test text")
            
            assert len(result) == len([0.1, 0.2, 0.3] * (Config.VECTOR_SIZE // 3))
            mock_post.assert_called_once_with(
                f"{service.base_url}/api/embeddings",
                json={
                    "model": service.model,
                    "prompt": "test text"
                }
            )

    @pytest.mark.asyncio
    async def test_get_embedding_failure(self):
        """Test embedding generation failure."""
        service = OllamaEmbeddingService()
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.HTTPError("Connection failed")
            
            result = await service.get_embedding("test text")
            
            # Should return zero vector as fallback
            assert result == [0.0] * Config.VECTOR_SIZE

    @pytest.mark.asyncio
    async def test_get_embeddings_multiple_texts(self):
        """Test embedding generation for multiple texts."""
        service = OllamaEmbeddingService()
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "embedding": [0.1] * Config.VECTOR_SIZE
        }
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            texts = ["text 1", "text 2", "text 3"]
            results = await service.get_embeddings(texts)
            
            assert len(results) == 3
            assert all(len(result) == Config.VECTOR_SIZE for result in results)
            assert mock_post.call_count == 3


class TestOpenAIEmbeddingService:
    """Test OpenAIEmbeddingService."""

    @patch.dict('os.environ', {"OPENAI_API_KEY": "test-api-key"})
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        service = OpenAIEmbeddingService()
        assert service.api_key == "test-api-key"
        assert service.model == "text-embedding-ada-002"

    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
                OpenAIEmbeddingService()

    @patch.dict('os.environ', {"OPENAI_API_KEY": "test-api-key"})
    @pytest.mark.asyncio
    async def test_get_embedding_success(self):
        """Test successful OpenAI embedding generation."""
        service = OpenAIEmbeddingService()
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1] * 1536}]
        }
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await service.get_embedding("test text")
            
            assert len(result) == 1536
            mock_post.assert_called_once()
            
            # Check headers
            call_args = mock_post.call_args
            headers = call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer test-api-key"

    @patch.dict('os.environ', {"OPENAI_API_KEY": "test-api-key"})
    @pytest.mark.asyncio
    async def test_get_embedding_failure(self):
        """Test OpenAI embedding generation failure."""
        service = OpenAIEmbeddingService()
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.HTTPError("API error")
            
            result = await service.get_embedding("test text")
            
            # Should return 1536-dimensional zero vector
            assert result == [0.0] * 1536


class TestSentenceTransformersEmbeddingService:
    """Test SentenceTransformersEmbeddingService."""

    @patch('builtins.__import__')
    def test_init_default_model(self, mock_import):
        """Test initialization with default model."""
        # Mock successful import
        mock_import.side_effect = lambda name, *args: Mock() if name == 'sentence_transformers' else __import__(name, *args)
        
        service = SentenceTransformersEmbeddingService()
        assert service.model_name == "all-MiniLM-L6-v2"
        assert service._model is None

    @patch('builtins.__import__')
    def test_init_custom_model(self, mock_import):
        """Test initialization with custom model."""
        # Mock successful import
        mock_import.side_effect = lambda name, *args: Mock() if name == 'sentence_transformers' else __import__(name, *args)
        
        custom_model = "custom-model"
        service = SentenceTransformersEmbeddingService(model_name=custom_model)
        assert service.model_name == custom_model

    @patch('builtins.__import__')
    def test_init_with_config_dict(self, mock_import):
        """Test initialization with config dictionary."""
        # Mock successful import
        mock_import.side_effect = lambda name, *args: Mock() if name == 'sentence_transformers' else __import__(name, *args)
        
        config = {"model_name": "test-model"}
        service = SentenceTransformersEmbeddingService(config)
        assert service.model_name == "test-model"

    @patch('builtins.__import__')
    def test_get_embedding_success(self, mock_import):
        """Test successful embedding generation."""
        # Mock successful import
        mock_import.side_effect = lambda name, *args: Mock() if name == 'sentence_transformers' else __import__(name, *args)
        
        service = SentenceTransformersEmbeddingService("test-model")
        
        # Mock the model directly on the service instance
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1] * 768])
        service._model = mock_model
        
        # Test
        embedding = service.get_embedding("test text")
        
        # Verify
        assert len(embedding) == 768
        assert all(x == 0.1 for x in embedding)
        mock_model.encode.assert_called_once_with(["test text"])

    @patch('builtins.__import__')
    def test_get_embedding_import_error(self, mock_import):
        """Test handling when sentence-transformers is not available."""
        # Mock import to raise ImportError for sentence_transformers
        def side_effect(name, *args, **kwargs):
            if name == 'sentence_transformers':
                raise ImportError("No module named 'sentence_transformers'")
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = side_effect
        
        with pytest.raises(ImportError, match="sentence_transformers package"):
            SentenceTransformersEmbeddingService("test-model")

    @patch('builtins.__import__')
    def test_get_embedding_failure(self, mock_import):
        """Test handling of embedding generation failure."""
        # Mock successful import
        mock_import.side_effect = lambda name, *args: Mock() if name == 'sentence_transformers' else __import__(name, *args)
        
        service = SentenceTransformersEmbeddingService("test-model")
        
        # Mock the model to raise exception during encode
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Model error")
        service._model = mock_model
        
        # Test - the original exception should be raised
        with pytest.raises(Exception, match="Model error"):
            service.get_embedding("test text")


class TestMockEmbeddingService:
    """Test MockEmbeddingService."""

    def test_init_default_dimension(self):
        """Test initialization with default dimension."""
        service = MockEmbeddingService()
        assert service.dimension == Config.VECTOR_SIZE

    def test_init_custom_dimension(self):
        """Test initialization with custom dimension."""
        custom_dim = 512
        service = MockEmbeddingService(dimension=custom_dim)
        assert service.dimension == custom_dim

    @pytest.mark.asyncio
    async def test_get_embedding(self):
        """Test mock embedding generation."""
        service = MockEmbeddingService()
        
        result = await service.get_embedding("test text")
        
        assert len(result) == Config.VECTOR_SIZE
        assert all(-1 <= val <= 1 for val in result)  # Values should be in [-1, 1] range

    @pytest.mark.asyncio
    async def test_get_embeddings_multiple(self):
        """Test mock embedding generation for multiple texts."""
        service = MockEmbeddingService()
        
        texts = ["text 1", "text 2"]
        results = await service.get_embeddings(texts)
        
        assert len(results) == 2
        assert all(len(result) == Config.VECTOR_SIZE for result in results)


class TestEmbeddingServiceFactory:
    """Test EmbeddingServiceFactory."""

    def test_create_ollama_service(self):
        """Test creating Ollama service."""
        service = EmbeddingServiceFactory.create("ollama")
        assert isinstance(service, OllamaEmbeddingService)

    @patch.dict('os.environ', {"OPENAI_API_KEY": "test-key"})
    def test_create_openai_service(self):
        """Test creating OpenAI service."""
        service = EmbeddingServiceFactory.create("openai")
        assert isinstance(service, OpenAIEmbeddingService)

    @patch('builtins.__import__')
    def test_create_sentence_transformers_service(self, mock_import):
        """Test creating SentenceTransformers service."""
        # Mock successful import
        mock_import.side_effect = lambda name, *args: Mock() if name == 'sentence_transformers' else __import__(name, *args)
        
        service = EmbeddingServiceFactory.create("sentence-transformers")
        assert isinstance(service, SentenceTransformersEmbeddingService)

    def test_create_mock_service(self):
        """Test creating mock service."""
        service = EmbeddingServiceFactory.create("mock")
        assert isinstance(service, MockEmbeddingService)

    def test_create_unknown_service(self):
        """Test creating unknown service type raises error."""
        with pytest.raises(ValueError, match="Unknown embedding service type"):
            EmbeddingServiceFactory.create("unknown")

    @patch.dict('os.environ', {"EMBEDDING_SERVICE": "mock"})
    def test_create_from_environment(self):
        """Test creating service from environment variable."""
        service = EmbeddingServiceFactory.create()
        assert isinstance(service, MockEmbeddingService)


class TestGlobalEmbeddingService:
    """Test global embedding service functions."""

    def test_get_embedding_service_singleton(self):
        """Test that get_embedding_service returns a singleton."""
        # Reset global service
        set_embedding_service(None)
        
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        
        assert service1 is service2

    def test_set_embedding_service(self):
        """Test setting custom embedding service."""
        custom_service = MockEmbeddingService()
        set_embedding_service(custom_service)
        
        retrieved_service = get_embedding_service()
        assert retrieved_service is custom_service

    @pytest.mark.asyncio
    async def test_convenience_get_embedding(self):
        """Test convenience get_embedding function."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "embedding": [0.1] * Config.VECTOR_SIZE
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await get_embedding("test text")
            
            assert len(result) == Config.VECTOR_SIZE
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_convenience_get_embedding_failure(self):
        """Test convenience get_embedding function failure."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.HTTPError("Connection failed")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await get_embedding("test text")
            
            # Should return zero vector as fallback
            assert result == [0.0] * Config.VECTOR_SIZE

    @pytest.mark.asyncio
    async def test_convenience_get_embeddings(self):
        """Test convenience get_embeddings function."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "embedding": [0.1] * Config.VECTOR_SIZE
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            texts = ["text 1", "text 2"]
            results = await get_embeddings(texts)
            
            assert len(results) == 2
            assert all(len(result) == Config.VECTOR_SIZE for result in results)
            assert mock_client.post.call_count == 2 