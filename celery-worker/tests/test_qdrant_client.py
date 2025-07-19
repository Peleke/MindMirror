"""Tests for the CeleryQdrantClient."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import uuid

from src.clients.qdrant_client import (
    CeleryQdrantClient,
    SearchResult,
    get_celery_qdrant_client,
)
from src.config import Config


class TestCeleryQdrantClient:
    """Test the CeleryQdrantClient."""

    @patch("src.clients.qdrant_client.QdrantClientBase")
    def test_init_default_values(self, mock_qdrant_base):
        """Test Qdrant client initialization with default values."""
        client = CeleryQdrantClient()

        assert client.url == Config.QDRANT_URL
        assert client.api_key == Config.QDRANT_API_KEY
        assert client.client is not None
        mock_qdrant_base.assert_called_once_with(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)

    @patch("src.clients.qdrant_client.QdrantClientBase")
    def test_init_custom_values(self, mock_qdrant_base):
        """Test client initialization with custom values."""
        custom_url = "http://custom-qdrant:9999"
        custom_api_key = "test-api-key"

        client = CeleryQdrantClient(url=custom_url, api_key=custom_api_key)

        assert client.url == custom_url
        assert client.api_key == custom_api_key
        mock_qdrant_base.assert_called_once_with(url=custom_url, api_key=custom_api_key)

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_qdrant_base):
        """Test successful health check."""
        mock_client = Mock()
        mock_client.get_collections.return_value = Mock()
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()
        result = await client.health_check()

        assert result is True
        mock_client.get_collections.assert_called_once()

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_qdrant_base):
        """Test health check failure."""
        mock_client = Mock()
        mock_client.get_collections.side_effect = Exception("Connection error")
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()
        result = await client.health_check()

        assert result is False

    def test_get_knowledge_collection_name(self):
        """Test knowledge collection name generation."""
        client = CeleryQdrantClient()

        assert client.get_knowledge_collection_name("stoicism") == "stoicism_knowledge"
        assert client.get_knowledge_collection_name("buddhism") == "buddhism_knowledge"

    def test_get_personal_collection_name(self):
        """Test personal collection name generation."""
        client = CeleryQdrantClient()

        result = client.get_personal_collection_name("stoicism", "user-123")
        assert result == "stoicism_user-123_personal"

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_create_collection_new_collection(self, mock_qdrant_base):
        """Test creating a new collection."""
        mock_client = Mock()
        mock_collections_response = Mock()
        mock_collections_response.collections = []
        mock_client.get_collections.return_value = mock_collections_response
        mock_client.create_collection.return_value = True
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()
        result = await client._create_collection("test_collection")

        assert result is True
        mock_client.create_collection.assert_called_once()

        # Check the create_collection call arguments
        call_args = mock_client.create_collection.call_args
        assert call_args[1]["collection_name"] == "test_collection"

        # Check vector configuration
        vectors_config = call_args[1]["vectors_config"]
        assert vectors_config.size == Config.VECTOR_SIZE
        assert vectors_config.distance.value == "Cosine"

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_create_collection_existing_collection(self, mock_qdrant_base):
        """Test creating an existing collection."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collections_response = Mock()
        mock_collections_response.collections = [mock_collection]
        mock_client.get_collections.return_value = mock_collections_response
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()
        result = await client._create_collection("test_collection")

        assert result is True
        mock_client.create_collection.assert_not_called()

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_create_collection_error(self, mock_qdrant_base):
        """Test collection creation error."""
        mock_client = Mock()
        mock_client.get_collections.side_effect = Exception("Connection error")
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()
        result = await client._create_collection("test_collection")

        assert result is False

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_get_or_create_knowledge_collection(self, mock_qdrant_base):
        """Test getting or creating knowledge collection."""
        mock_client = Mock()
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()

        with patch.object(
            client, "_create_collection", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = True

            result = await client.get_or_create_knowledge_collection("stoicism")

            assert result == "stoicism_knowledge"
            mock_create.assert_called_once_with("stoicism_knowledge")

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_get_or_create_personal_collection(self, mock_qdrant_base):
        """Test getting or creating personal collection."""
        mock_client = Mock()
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()

        with patch.object(
            client, "_create_collection", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = True

            result = await client.get_or_create_personal_collection(
                "stoicism", "user-123"
            )

            assert result == "stoicism_user-123_personal"
            mock_create.assert_called_once_with("stoicism_user-123_personal")

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_index_personal_document(self, mock_qdrant_base):
        """Test indexing a personal document."""
        mock_client = Mock()
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()

        with patch.object(
            client, "get_or_create_personal_collection", new_callable=AsyncMock
        ) as mock_get_collection:
            with patch.object(
                client, "index_document", new_callable=AsyncMock
            ) as mock_index:
                mock_get_collection.return_value = "stoicism_user-123_personal"
                mock_index.return_value = "doc-id-123"

                result = await client.index_personal_document(
                    tradition="stoicism",
                    user_id="user-123",
                    text="Test journal entry",
                    embedding=[0.1] * Config.VECTOR_SIZE,
                    metadata={"entry_id": "entry-123"},
                )

                assert result == "doc-id-123"
                mock_get_collection.assert_called_once_with("stoicism", "user-123")

                # Check that metadata is properly updated with source_type and user_id
                call_args = mock_index.call_args
                metadata = call_args[0][3]
                assert metadata["source_type"] == "journal"
                assert metadata["user_id"] == "user-123"
                assert metadata["entry_id"] == "entry-123"

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_index_document(self, mock_qdrant_base):
        """Test indexing a document."""
        mock_client = Mock()
        mock_operation_info = Mock()
        mock_operation_info.status = "completed"
        mock_client.upsert.return_value = mock_operation_info
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()

        with patch("src.clients.qdrant_client.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value="test-doc-id")

            result = await client.index_document(
                collection_name="test_collection",
                text="Test document",
                embedding=[0.1] * Config.VECTOR_SIZE,
                metadata={"source": "test"},
            )

            assert result == "test-doc-id"
            mock_client.upsert.assert_called_once()

            # Check the upsert call
            call_args = mock_client.upsert.call_args
            assert call_args[1]["collection_name"] == "test_collection"

            points = call_args[1]["points"]
            assert len(points) == 1
            point = points[0]
            assert point.id == "test-doc-id"
            assert point.vector == [0.1] * Config.VECTOR_SIZE
            assert point.payload["text"] == "Test document"
            assert point.payload["source"] == "test"

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_index_knowledge_documents(self, mock_qdrant_base):
        """Test indexing knowledge documents."""
        mock_client = Mock()
        mock_operation_info = Mock()
        mock_operation_info.status = "completed"
        mock_client.upsert.return_value = mock_operation_info
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()

        texts = ["Text 1", "Text 2"]
        embeddings = [[0.1] * Config.VECTOR_SIZE, [0.2] * Config.VECTOR_SIZE]
        metadatas = [{"source": "doc1"}, {"source": "doc2"}]

        with patch("src.clients.qdrant_client.uuid.uuid4") as mock_uuid:
            mock_uuid.side_effect = [
                Mock(__str__=Mock(return_value="id1")),
                Mock(__str__=Mock(return_value="id2")),
            ]

            result = await client.index_knowledge_documents(
                tradition="stoicism",
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            assert result == ["id1", "id2"]
            mock_client.upsert.assert_called_once()

            # Check the upsert call
            call_args = mock_client.upsert.call_args
            assert call_args[1]["collection_name"] == "stoicism_knowledge"

            points = call_args[1]["points"]
            assert len(points) == 2
            assert points[0].payload["text"] == "Text 1"
            assert points[1].payload["text"] == "Text 2"

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, mock_qdrant_base):
        """Test searching the knowledge base."""
        mock_client = Mock()
        mock_result1 = Mock()
        mock_result1.id = "result-1"
        mock_result1.score = 0.9
        mock_result1.payload = {"text": "Result 1", "source": "doc1"}
        mock_result1.vector = [0.1] * Config.VECTOR_SIZE

        mock_result2 = Mock()
        mock_result2.id = "result-2"
        mock_result2.score = 0.8
        mock_result2.payload = {"text": "Result 2", "source": "doc2"}
        mock_result2.vector = [0.2] * Config.VECTOR_SIZE

        mock_client.search.return_value = [mock_result1, mock_result2]
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()

        query_vector = [0.1] * Config.VECTOR_SIZE
        results = await client.search_knowledge_base(
            collection_name="test_collection",
            query_vector=query_vector,
            limit=5,
            score_threshold=0.7,
        )

        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].id == "result-1"
        assert results[0].score == 0.9
        assert results[0].payload["text"] == "Result 1"

        # Check the search call
        mock_client.search.assert_called_once_with(
            collection_name="test_collection",
            query_vector=query_vector,
            limit=5,
            score_threshold=0.7,
        )

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_delete_collection(self, mock_qdrant_base):
        """Test deleting a collection."""
        mock_client = Mock()
        mock_client.delete_collection.return_value = True
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()
        result = await client.delete_collection("test_collection")

        assert result is True
        mock_client.delete_collection.assert_called_once_with(
            collection_name="test_collection"
        )

    @patch("src.clients.qdrant_client.QdrantClientBase")
    @pytest.mark.asyncio
    async def test_get_collection_info(self, mock_qdrant_base):
        """Test getting collection information."""
        mock_client = Mock()
        mock_info = Mock()
        mock_info.name = "test_collection"
        mock_info.vectors_count = 100
        mock_info.points_count = 100
        mock_info.status = "green"
        mock_client.get_collection.return_value = mock_info
        mock_qdrant_base.return_value = mock_client

        client = CeleryQdrantClient()
        result = await client.get_collection_info("test_collection")

        expected = {
            "name": "test_collection",
            "vectors_count": 100,
            "points_count": 100,
            "status": "green",
        }
        assert result == expected


class TestSearchResult:
    """Test the SearchResult class."""

    def test_search_result_initialization(self):
        """Test SearchResult initialization."""
        payload = {"text": "Test", "source_type": "journal"}
        result = SearchResult(
            id="test-id", score=0.9, payload=payload, vector=[0.1, 0.2, 0.3]
        )

        assert result.id == "test-id"
        assert result.score == 0.9
        assert result.payload == payload
        assert result.vector == [0.1, 0.2, 0.3]

    def test_is_personal_content_true(self):
        """Test is_personal_content returns True for journal content."""
        result = SearchResult(
            id="test-id", score=0.9, payload={"source_type": "journal"}
        )

        assert result.is_personal_content() is True

    def test_is_personal_content_false(self):
        """Test is_personal_content returns False for non-journal content."""
        result = SearchResult(
            id="test-id", score=0.9, payload={"source_type": "knowledge"}
        )

        assert result.is_personal_content() is False

    def test_is_personal_content_missing_source_type(self):
        """Test is_personal_content returns False when source_type is missing."""
        result = SearchResult(id="test-id", score=0.9, payload={})

        assert result.is_personal_content() is False


class TestGlobalClient:
    """Test the global client functions."""

    def test_get_celery_qdrant_client_singleton(self):
        """Test that get_celery_qdrant_client returns a singleton."""
        # Reset the global client
        import src.clients.qdrant_client as qdrant_module

        qdrant_module._celery_qdrant_client = None

        client1 = get_celery_qdrant_client()
        client2 = get_celery_qdrant_client()

        assert client1 is client2
        assert isinstance(client1, CeleryQdrantClient)
