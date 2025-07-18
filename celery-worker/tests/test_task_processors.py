"""
Tests for task processors that handle business logic directly.

These tests replace the old Celery task tests with tests for the new
task processors that execute business logic directly.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.tasks.task_processors import (
    JournalIndexingProcessor,
    TraditionRebuildProcessor,
    HealthCheckProcessor,
    get_journal_processor,
    get_tradition_processor,
    get_health_processor,
)


@pytest.fixture
def sample_journal_data():
    """Create sample journal entry data for testing."""
    return {
        "entry_id": str(uuid4()),
        "user_id": str(uuid4()),
        "tradition": "canon-default",
    }


@pytest.fixture
def sample_batch_data():
    """Create sample batch data for testing."""
    return [
        {
            "entry_id": str(uuid4()),
            "user_id": str(uuid4()),
            "tradition": "canon-default",
        }
        for _ in range(3)
    ]


class TestJournalIndexingProcessor:
    """Test suite for JournalIndexingProcessor."""

    @patch("src.tasks.task_processors.create_celery_journal_client")
    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_processor_initialization(self, mock_get_qdrant, mock_create_journal):
        """Test that processor initializes correctly."""
        mock_journal_client = AsyncMock()
        mock_qdrant_client = MagicMock()
        mock_create_journal.return_value = mock_journal_client
        mock_get_qdrant.return_value = mock_qdrant_client

        processor = JournalIndexingProcessor()

        assert processor.journal_client == mock_journal_client
        assert processor.qdrant_client == mock_qdrant_client

    @patch("src.tasks.task_processors.create_celery_journal_client")
    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    @patch("src.tasks.task_processors.get_embedding")
    def test_process_journal_indexing_success(
        self, mock_get_embedding, mock_get_qdrant, mock_create_journal, sample_journal_data
    ):
        """Test successful journal entry indexing."""
        # Setup mocks
        mock_journal_client = AsyncMock()
        mock_qdrant_client = MagicMock()
        mock_get_embedding.return_value = [0.1] * 1536

        mock_journal_client.get_journal_entry.return_value = {
            "id": sample_journal_data["entry_id"],
            "content": "Test journal entry content",
            "title": "Test Title",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        mock_create_journal.return_value = mock_journal_client
        mock_get_qdrant.return_value = mock_qdrant_client

        # Create processor and test
        processor = JournalIndexingProcessor()
        result = processor.process_journal_indexing(
            sample_journal_data["entry_id"],
            sample_journal_data["user_id"],
            sample_journal_data["tradition"],
        )

        assert result is True
        mock_journal_client.get_journal_entry.assert_called_once_with(
            sample_journal_data["entry_id"]
        )
        mock_get_embedding.assert_called_once()
        mock_qdrant_client.index_journal_entry.assert_called_once()

    @patch("src.tasks.task_processors.create_celery_journal_client")
    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_process_journal_indexing_entry_not_found(
        self, mock_get_qdrant, mock_create_journal, sample_journal_data
    ):
        """Test journal indexing when entry is not found."""
        # Setup mocks
        mock_journal_client = AsyncMock()
        mock_qdrant_client = MagicMock()
        mock_journal_client.get_journal_entry.return_value = None

        mock_create_journal.return_value = mock_journal_client
        mock_get_qdrant.return_value = mock_qdrant_client

        # Create processor and test
        processor = JournalIndexingProcessor()
        result = processor.process_journal_indexing(
            sample_journal_data["entry_id"],
            sample_journal_data["user_id"],
            sample_journal_data["tradition"],
        )

        assert result is False
        mock_journal_client.get_journal_entry.assert_called_once()
        mock_qdrant_client.index_journal_entry.assert_not_called()

    @patch("src.tasks.task_processors.create_celery_journal_client")
    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_process_journal_indexing_no_content(
        self, mock_get_qdrant, mock_create_journal, sample_journal_data
    ):
        """Test journal indexing when entry has no content."""
        # Setup mocks
        mock_journal_client = AsyncMock()
        mock_qdrant_client = MagicMock()
        mock_journal_client.get_journal_entry.return_value = {
            "id": sample_journal_data["entry_id"],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        mock_create_journal.return_value = mock_journal_client
        mock_get_qdrant.return_value = mock_qdrant_client

        # Create processor and test
        processor = JournalIndexingProcessor()
        result = processor.process_journal_indexing(
            sample_journal_data["entry_id"],
            sample_journal_data["user_id"],
            sample_journal_data["tradition"],
        )

        assert result is False
        mock_journal_client.get_journal_entry.assert_called_once()
        mock_qdrant_client.index_journal_entry.assert_not_called()

    def test_extract_text_from_entry(self, sample_journal_data):
        """Test text extraction from journal entry data."""
        processor = JournalIndexingProcessor()

        # Test with content only
        entry_data = {"content": "Test content"}
        text = processor._extract_text_from_entry(entry_data)
        assert text == "Test content"

        # Test with title and content
        entry_data = {"title": "Test Title", "content": "Test content"}
        text = processor._extract_text_from_entry(entry_data)
        assert "Title: Test Title" in text
        assert "Test content" in text

        # Test with tags
        entry_data = {"content": "Test content", "tags": ["tag1", "tag2"]}
        text = processor._extract_text_from_entry(entry_data)
        assert "Tags: tag1, tag2" in text

        # Test with summary
        entry_data = {"content": "Test content", "summary": "Test summary"}
        text = processor._extract_text_from_entry(entry_data)
        assert "Summary: Test summary" in text

    @patch("src.tasks.task_processors.JournalIndexer")
    def test_process_batch_indexing(self, mock_indexer_class, sample_batch_data):
        """Test batch indexing processing."""
        # Setup mock
        mock_indexer = AsyncMock()
        mock_indexer.batch_index_entries.return_value = {
            "indexed": 2,
            "failed": 0,
            "total": 2,
        }
        mock_indexer_class.return_value = mock_indexer

        processor = JournalIndexingProcessor()
        result = processor.process_batch_indexing(sample_batch_data)

        assert result["indexed"] == 2
        assert result["failed"] == 0
        assert result["total"] == 2

    @patch("src.tasks.task_processors.JournalIndexer")
    def test_process_user_reindex(self, mock_indexer_class, sample_journal_data):
        """Test user reindexing processing."""
        # Setup mock
        mock_indexer = AsyncMock()
        mock_indexer.reindex_user_entries.return_value = {
            "indexed": 5,
            "total_entries": 5,
            "user_id": sample_journal_data["user_id"],
            "tradition": sample_journal_data["tradition"],
        }
        mock_indexer_class.return_value = mock_indexer

        processor = JournalIndexingProcessor()
        result = processor.process_user_reindex(
            sample_journal_data["user_id"], sample_journal_data["tradition"]
        )

        assert result["indexed"] == 5
        assert result["total_entries"] == 5
        assert result["user_id"] == sample_journal_data["user_id"]
        assert result["tradition"] == sample_journal_data["tradition"]


class TestTraditionRebuildProcessor:
    """Test suite for TraditionRebuildProcessor."""

    @patch("src.tasks.task_processors.get_gcs_client")
    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_processor_initialization(self, mock_get_qdrant, mock_get_gcs):
        """Test that processor initializes correctly."""
        mock_gcs_client = MagicMock()
        mock_qdrant_client = MagicMock()
        mock_get_gcs.return_value = mock_gcs_client
        mock_get_qdrant.return_value = mock_qdrant_client

        processor = TraditionRebuildProcessor()

        assert processor.gcs_client == mock_gcs_client
        assert processor.qdrant_client == mock_qdrant_client

    @patch("src.tasks.task_processors.get_gcs_client")
    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    @patch("src.tasks.task_processors.get_embeddings")
    @patch("src.tasks.task_processors.run_async_in_sync")
    @patch("tempfile.NamedTemporaryFile")
    @patch("os.remove")
    @patch("src.tasks.task_processors.PyPDFLoader")
    @patch("src.tasks.task_processors.RecursiveCharacterTextSplitter")
    def test_process_tradition_rebuild_success(
        self, mock_text_splitter, mock_pdf_loader, mock_os_remove, mock_tempfile, mock_run_async, mock_get_embeddings, mock_get_qdrant, mock_get_gcs
    ):
        """Test successful tradition rebuild."""
        # Setup mocks
        mock_gcs_client = MagicMock()
        mock_qdrant_client = MagicMock()
        mock_get_embeddings.return_value = [[0.1] * 1536]
        mock_run_async.return_value = [[0.1] * 1536]  # Mock the async embedding call

        # Mock tempfile
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test.pdf"
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_tempfile.return_value.__exit__.return_value = None

        # Mock PyPDFLoader and text splitter
        mock_loader = MagicMock()
        mock_docs = [MagicMock(page_content="Test content", metadata={"page": 0})]
        mock_loader.load_and_split.return_value = mock_docs
        mock_pdf_loader.return_value = mock_loader

        mock_splitter = MagicMock()
        mock_text_splitter.return_value = mock_splitter

        # Mock GCS file listing
        mock_blob = MagicMock()
        mock_blob.name = "test-tradition/test.pdf"
        mock_gcs_client.list_files.return_value = [mock_blob]

        # Mock Qdrant operations
        mock_qdrant_client.get_knowledge_collection_name.return_value = "test-tradition-knowledge"
        mock_qdrant_client.get_or_create_knowledge_collection.return_value = None

        mock_get_gcs.return_value = mock_gcs_client
        mock_get_qdrant.return_value = mock_qdrant_client

        # Create processor and test
        processor = TraditionRebuildProcessor()
        result = processor.process_tradition_rebuild("test-tradition")

        assert result["status"] == "success"
        assert result["processed_files"] == 1

    @patch("src.tasks.task_processors.get_gcs_client")
    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_process_tradition_rebuild_no_documents(
        self, mock_get_qdrant, mock_get_gcs
    ):
        """Test tradition rebuild when no documents are found."""
        # Setup mocks
        mock_gcs_client = MagicMock()
        mock_qdrant_client = MagicMock()

        # Mock empty GCS file listing
        mock_gcs_client.list_files.return_value = []

        mock_get_gcs.return_value = mock_gcs_client
        mock_get_qdrant.return_value = mock_qdrant_client

        # Create processor and test
        processor = TraditionRebuildProcessor()
        result = processor.process_tradition_rebuild("test-tradition")

        assert result["status"] == "success"
        assert result["message"] == "No documents to process."


class TestHealthCheckProcessor:
    """Test suite for HealthCheckProcessor."""

    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_processor_initialization(self, mock_get_qdrant):
        """Test that processor initializes correctly."""
        mock_qdrant_client = MagicMock()
        mock_get_qdrant.return_value = mock_qdrant_client

        processor = HealthCheckProcessor()

        assert processor.qdrant_client == mock_qdrant_client

    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_process_health_check_healthy(self, mock_get_qdrant):
        """Test health check when all services are healthy."""
        # Setup mocks
        mock_qdrant_client = AsyncMock()
        mock_qdrant_client.health_check.return_value = True
        mock_get_qdrant.return_value = mock_qdrant_client

        processor = HealthCheckProcessor()
        result = processor.process_health_check()

        assert result["status"] == "healthy"
        assert result["services"]["qdrant"] == "healthy"

    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_process_health_check_degraded(self, mock_get_qdrant):
        """Test health check when some services are unhealthy."""
        # Setup mocks
        mock_qdrant_client = AsyncMock()
        mock_qdrant_client.health_check.return_value = False
        mock_get_qdrant.return_value = mock_qdrant_client

        processor = HealthCheckProcessor()
        result = processor.process_health_check()

        assert result["status"] == "degraded"
        assert result["services"]["qdrant"] == "unhealthy"

    @patch("src.tasks.task_processors.get_celery_qdrant_client")
    def test_process_health_check_exception(self, mock_get_qdrant):
        """Test health check when an exception occurs."""
        # Setup mocks
        mock_qdrant_client = AsyncMock()
        mock_qdrant_client.health_check.side_effect = Exception("Connection error")
        mock_get_qdrant.return_value = mock_qdrant_client

        processor = HealthCheckProcessor()
        result = processor.process_health_check()

        assert result["status"] == "degraded"
        assert result["services"]["qdrant"] == "unhealthy"


class TestProcessorFactories:
    """Test suite for processor factory functions."""

    def test_get_journal_processor_singleton(self):
        """Test that get_journal_processor returns the same instance."""
        processor1 = get_journal_processor()
        processor2 = get_journal_processor()
        assert processor1 is processor2

    def test_get_tradition_processor_singleton(self):
        """Test that get_tradition_processor returns the same instance."""
        processor1 = get_tradition_processor()
        processor2 = get_tradition_processor()
        assert processor1 is processor2

    def test_get_health_processor_singleton(self):
        """Test that get_health_processor returns the same instance."""
        processor1 = get_health_processor()
        processor2 = get_health_processor()
        assert processor1 is processor2 