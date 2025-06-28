import pytest
import asyncio
from celery_worker.src.utils.embedding import (
    EmbeddingServiceFactory, 
    OllamaEmbeddingService, 
    MockEmbeddingService,
    get_embedding_service,
    set_embedding_service
)


@pytest.fixture
def mock_embedding_service():
    """Fixture to provide a mock embedding service."""
    service = MockEmbeddingService(dimension=768)
    set_embedding_service(service)
    return service


@pytest.mark.asyncio
async def test_mock_embedding_service(mock_embedding_service):
    """Test the mock embedding service."""
    # Test single embedding
    text = "Hello, world!"
    embedding = await mock_embedding_service.get_embedding(text)
    
    assert len(embedding) == 768
    assert all(isinstance(x, float) for x in embedding)
    
    # Test multiple embeddings
    texts = ["Hello", "World", "Test"]
    embeddings = await mock_embedding_service.get_embeddings(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 768 for emb in embeddings)


@pytest.mark.asyncio
async def test_ollama_embedding_service():
    """Test the Ollama embedding service."""
    try:
        service = OllamaEmbeddingService()
        text = "Hello, world!"
        embedding = await service.get_embedding(text)
        
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
        
    except Exception as e:
        pytest.skip(f"Ollama not available: {e}")


@pytest.mark.asyncio
async def test_embedding_service_factory():
    """Test the embedding service factory."""
    # Test mock service creation
    mock_service = EmbeddingServiceFactory.create("mock")
    embedding = await mock_service.get_embedding("test")
    
    assert len(embedding) > 0
    
    # Test global service
    service = get_embedding_service()
    embedding = await service.get_embedding("test")
    
    assert len(embedding) > 0


@pytest.mark.asyncio
async def test_embedding_service_factory_invalid_type():
    """Test factory with invalid service type."""
    with pytest.raises(ValueError, match="Unknown embedding service type"):
        EmbeddingServiceFactory.create("invalid_service")


@pytest.mark.asyncio
async def test_convenience_functions():
    """Test the convenience functions."""
    from celery_worker.src.utils.embedding import get_embedding, get_embeddings
    
    # Test single embedding
    text = "Hello, world!"
    embedding = await get_embedding(text)
    
    assert len(embedding) > 0
    
    # Test multiple embeddings
    texts = ["Hello", "World"]
    embeddings = await get_embeddings(texts)
    
    assert len(embeddings) == 2
    assert all(len(emb) > 0 for emb in embeddings) 