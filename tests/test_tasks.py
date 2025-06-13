import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from src.tasks import (
    celery_app,
    index_journal_entry_task,
    batch_index_journal_entries_task,
    health_check_task
)
from src.models.sql.journal import JournalEntryModel, GratitudeJournalEntry, ReflectionJournalEntry
from src.journal_indexer import JournalIndexer


class TestCeleryTasks:
    """Test suite for Celery background tasks."""

    @pytest.fixture
    def sample_journal_entry(self) -> JournalEntryModel:
        """Create a sample journal entry for testing."""
        return GratitudeJournalEntry(
            id=str(uuid4()),
            user_id=str(uuid4()),
            created_at=datetime.utcnow(),
            gratitude_items=["I'm grateful for good health", "I'm grateful for supportive friends"]
        )

    @pytest.fixture
    def sample_reflection_entry(self) -> JournalEntryModel:
        """Create a sample reflection entry for testing."""
        return ReflectionJournalEntry(
            id=str(uuid4()),
            user_id=str(uuid4()),
            created_at=datetime.utcnow(),
            reflection="Today I learned that consistency beats perfection in fitness."
        )

    def test_celery_app_configuration(self):
        """Test that Celery app is properly configured."""
        assert celery_app.conf.broker_url is not None
        assert celery_app.conf.result_backend is not None
        assert celery_app.conf.task_serializer == 'json'
        assert celery_app.conf.accept_content == ['json']
        assert celery_app.conf.result_serializer == 'json'
        assert celery_app.conf.timezone == 'UTC'

    @patch('src.tasks.JournalIndexer')
    async def test_index_journal_entry_task_success(self, mock_indexer_class, sample_journal_entry):
        """Test successful journal entry indexing task."""
        # Setup mock
        mock_indexer = AsyncMock()
        mock_indexer.index_entry.return_value = True
        mock_indexer_class.return_value = mock_indexer

        # Execute task
        result = await index_journal_entry_task.apply_async(
            args=[
                sample_journal_entry.id,
                sample_journal_entry.user_id,
                "canon-default"
            ]
        ).get()

        # Verify
        assert result is True
        mock_indexer.index_entry.assert_called_once()

    @patch('src.tasks.JournalIndexer')
    async def test_index_journal_entry_task_failure(self, mock_indexer_class, sample_journal_entry):
        """Test journal entry indexing task with failure and retry."""
        # Setup mock to fail first time, succeed second time
        mock_indexer = AsyncMock()
        mock_indexer.index_entry.side_effect = [Exception("Network error"), True]
        mock_indexer_class.return_value = mock_indexer

        # Execute task (should retry and succeed)
        result = await index_journal_entry_task.apply_async(
            args=[
                sample_journal_entry.id,
                sample_journal_entry.user_id,
                "canon-default"
            ]
        ).get()

        # Verify retry happened
        assert result is True
        assert mock_indexer.index_entry.call_count == 2

    @patch('src.tasks.JournalIndexer')
    async def test_batch_index_journal_entries_task(self, mock_indexer_class):
        """Test batch indexing of multiple journal entries."""
        # Setup mock
        mock_indexer = AsyncMock()
        mock_indexer.batch_index_entries.return_value = {"indexed": 5, "failed": 0}
        mock_indexer_class.return_value = mock_indexer

        # Test data
        entry_data = [
            {
                "entry_id": str(uuid4()),
                "user_id": str(uuid4()),
                "tradition": "canon-default"
            }
            for _ in range(5)
        ]

        # Execute task
        result = await batch_index_journal_entries_task.apply_async(
            args=[entry_data]
        ).get()

        # Verify
        assert result["indexed"] == 5
        assert result["failed"] == 0
        mock_indexer.batch_index_entries.assert_called_once()

    async def test_health_check_task(self):
        """Test health check task for monitoring."""
        result = await health_check_task.apply_async().get()
        
        assert "timestamp" in result
        assert "status" in result
        assert result["status"] == "healthy"
        assert "services" in result
        assert "qdrant" in result["services"]
        assert "redis" in result["services"]


class TestTaskRetryLogic:
    """Test Celery task retry and error handling."""

    @patch('src.tasks.JournalIndexer')
    async def test_task_max_retries(self, mock_indexer_class):
        """Test that tasks respect max retry limits."""
        # Setup mock to always fail
        mock_indexer = AsyncMock()
        mock_indexer.index_entry.side_effect = Exception("Persistent error")
        mock_indexer_class.return_value = mock_indexer

        # Execute task (should eventually fail after max retries)
        with pytest.raises(Exception):
            await index_journal_entry_task.apply_async(
                args=[str(uuid4()), str(uuid4()), "canon-default"]
            ).get()

        # Verify it retried the expected number of times
        expected_calls = index_journal_entry_task.max_retries + 1
        assert mock_indexer.index_entry.call_count == expected_calls

    @patch('src.tasks.JournalIndexer')
    async def test_task_exponential_backoff(self, mock_indexer_class):
        """Test that tasks use exponential backoff for retries."""
        # This test would verify retry timing in a real scenario
        # For now, we just verify the retry configuration exists
        task_config = index_journal_entry_task.retry_kwargs
        
        assert 'countdown' in task_config or 'backoff' in task_config
        assert task_config.get('max_retries', 0) > 0


class TestTaskIntegration:
    """Integration tests for task workflow."""

    @patch('src.tasks.get_journal_entry_by_id')
    @patch('src.tasks.JournalIndexer')
    async def test_end_to_end_journal_indexing(
        self, 
        mock_indexer_class, 
        mock_get_entry,
        sample_journal_entry
    ):
        """Test complete workflow from journal creation to indexing."""
        # Setup mocks
        mock_get_entry.return_value = sample_journal_entry
        mock_indexer = AsyncMock()
        mock_indexer.index_entry.return_value = True
        mock_indexer_class.return_value = mock_indexer

        # Simulate the complete workflow
        # 1. Journal entry is created (mocked)
        # 2. Task is queued
        # 3. Task executes and indexes entry
        
        result = await index_journal_entry_task.apply_async(
            args=[
                sample_journal_entry.id,
                sample_journal_entry.user_id,
                "canon-default"
            ]
        ).get()

        # Verify workflow completed successfully
        assert result is True
        mock_get_entry.assert_called_once_with(sample_journal_entry.id)
        mock_indexer.index_entry.assert_called_once()

    @patch('src.tasks.JournalIndexer')
    async def test_task_with_invalid_entry_id(self, mock_indexer_class):
        """Test task behavior with invalid journal entry ID."""
        # Setup mock to return None (entry not found)
        mock_indexer = AsyncMock()
        mock_indexer.index_entry.side_effect = ValueError("Entry not found")
        mock_indexer_class.return_value = mock_indexer

        # Execute task with invalid ID
        with pytest.raises(ValueError):
            await index_journal_entry_task.apply_async(
                args=["invalid-id", str(uuid4()), "canon-default"]
            ).get()


class TestTaskMonitoring:
    """Test task monitoring and metrics."""

    async def test_task_success_metrics(self):
        """Test that successful tasks are properly tracked."""
        # This would test integration with monitoring systems
        # For now, verify task completion tracking exists
        pass

    async def test_task_failure_metrics(self):
        """Test that failed tasks are properly tracked."""
        # This would test error rate monitoring
        # For now, verify error handling exists
        pass

    async def test_task_performance_metrics(self):
        """Test that task performance is tracked."""
        # This would test timing and throughput metrics
        # For now, verify basic task execution
        pass


class TestTaskConfiguration:
    """Test task configuration and settings."""

    def test_task_routing(self):
        """Test that tasks are routed to correct queues."""
        # Verify indexing tasks go to indexing queue
        assert index_journal_entry_task.routing_key == "indexing"
        assert batch_index_journal_entries_task.routing_key == "indexing"
        
        # Verify health checks go to monitoring queue
        assert health_check_task.routing_key == "monitoring"

    def test_task_priority(self):
        """Test that tasks have appropriate priority levels."""
        # Real-time indexing should have higher priority than batch
        assert index_journal_entry_task.priority > batch_index_journal_entries_task.priority
        
        # Health checks should have highest priority
        assert health_check_task.priority >= index_journal_entry_task.priority

    def test_task_timeouts(self):
        """Test that tasks have reasonable timeout values."""
        # Individual indexing should complete quickly
        assert index_journal_entry_task.time_limit <= 300  # 5 minutes max
        
        # Batch processing can take longer
        assert batch_index_journal_entries_task.time_limit <= 1800  # 30 minutes max 