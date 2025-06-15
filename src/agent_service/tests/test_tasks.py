import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from celery.exceptions import Retry

from agent_service.tasks import (
    index_journal_entry_task,
    batch_index_journal_entries_task,
    health_check_task,
    reindex_user_entries_task,
    queue_journal_entry_indexing,
    queue_batch_indexing,
    queue_user_reindex,
    queue_health_check,
)


@pytest.fixture
def sample_journal_data():
    """Create sample journal entry data for testing."""
    return {
        "entry_id": str(uuid4()),
        "user_id": str(uuid4()),
        "tradition": "canon-default"
    }


@pytest.fixture
def sample_batch_data():
    """Create sample batch data for testing."""
    return [
        {
            "entry_id": str(uuid4()),
            "user_id": str(uuid4()),
            "tradition": "canon-default"
        }
        for _ in range(3)
    ]


class TestCeleryTasks:
    """Test suite for Celery background tasks."""

    def test_celery_app_configuration(self, celery_app):
        """Test that Celery app is properly configured."""
        assert celery_app.conf.task_always_eager is True
        assert celery_app.conf.task_eager_propagates is True
        assert celery_app.conf.task_track_started is True
        assert "agent_service.tasks" in celery_app.conf.include

    @patch('agent_service.tasks.index_journal_entry_by_id')
    @pytest.mark.asyncio
    async def test_index_journal_entry_task_success(self, mock_index_func, sample_journal_data, celery_app):
        """Test successful journal entry indexing task."""
        # Setup mock for the async function to return True
        mock_index_func.return_value = True

        # Execute task directly (eager mode)
        result = index_journal_entry_task.apply(
            args=[sample_journal_data["entry_id"], sample_journal_data["user_id"], sample_journal_data["tradition"]]
        )

        # Verify
        assert result.successful()
        # The result of an async task in eager mode is a coroutine
        final_result = await result.get()
        assert final_result is True
        mock_index_func.assert_called_once_with(
            sample_journal_data["entry_id"], 
            sample_journal_data["user_id"], 
            sample_journal_data["tradition"]
        )

    @patch('agent_service.tasks.index_journal_entry_by_id')
    @pytest.mark.asyncio
    async def test_index_journal_entry_task_failure(self, mock_index_func, sample_journal_data, celery_app):
        """Test journal entry indexing task with failure."""
        # Setup mock for the async function to return False, which causes the task to raise an exception
        mock_index_func.return_value = False

        # Execute task
        result = index_journal_entry_task.apply(
            args=[sample_journal_data["entry_id"], sample_journal_data["user_id"], sample_journal_data["tradition"]]
        )

        # Verify failure. The task raises an exception which is caught by Celery.
        # The result of a failed task is the exception object. Awaiting .get() will reraise it.
        with pytest.raises(Exception, match="Failed to index journal entry"):
            await result.get()

    @patch('agent_service.tasks.index_journal_entry_by_id')
    @pytest.mark.asyncio
    async def test_index_journal_entry_task_exception(self, mock_index_func, sample_journal_data, celery_app):
        """Test journal entry indexing task with exception."""
        # Setup mock to raise exception when awaited
        mock_index_func.side_effect = Exception("Network error")

        # Execute task
        result = index_journal_entry_task.apply(
            args=[sample_journal_data["entry_id"], sample_journal_data["user_id"], sample_journal_data["tradition"]]
        )

        # Verify exception handling
        with pytest.raises(Exception, match="Network error"):
            await result.get()

    @patch('agent_service.tasks.JournalIndexer')
    @pytest.mark.asyncio
    async def test_batch_index_journal_entries_task(self, mock_indexer_class, sample_batch_data, celery_app):
        """Test batch indexing of multiple journal entries."""
        # Setup mock
        mock_indexer = AsyncMock()
        mock_indexer.batch_index_entries.return_value = {"indexed": 3, "failed": 0}
        mock_indexer_class.return_value = mock_indexer

        # Execute task
        result = batch_index_journal_entries_task.apply(args=[sample_batch_data])

        # Verify
        assert result.successful()
        final_result = await result.get()
        assert final_result["indexed"] == 3
        assert final_result["failed"] == 0

    @patch('agent_service.vector_stores.qdrant_client.get_qdrant_client')
    @patch('agent_service.tasks.current_app')
    @pytest.mark.asyncio
    async def test_health_check_task_healthy(self, mock_current_app, mock_get_qdrant_client, celery_app):
        """Test health check task when all services are healthy."""
        # Setup mocks
        mock_qdrant = AsyncMock()
        mock_qdrant.health_check.return_value = True
        mock_get_qdrant_client.return_value = mock_qdrant

        # Mock Redis connection
        mock_conn = MagicMock()
        mock_conn.ensure_connection.return_value = None
        mock_current_app.connection_for_read.return_value.__enter__.return_value = mock_conn

        # Execute task
        result = health_check_task.apply()

        # Verify
        assert result.successful()
        health_data = await result.get()
        assert health_data["status"] == "healthy"
        assert health_data["services"]["qdrant"] == "healthy"
        assert health_data["services"]["redis"] == "healthy"
        assert "timestamp" in health_data

    @patch('agent_service.vector_stores.qdrant_client.get_qdrant_client')
    @patch('agent_service.tasks.current_app')
    @pytest.mark.asyncio
    async def test_health_check_task_degraded(self, mock_current_app, mock_get_qdrant_client, celery_app):
        """Test health check task when some services are unhealthy."""
        # Setup mocks - Qdrant healthy, Redis unhealthy
        mock_qdrant = AsyncMock()
        mock_qdrant.health_check.return_value = True
        mock_get_qdrant_client.return_value = mock_qdrant

        # Mock Redis connection failure
        mock_current_app.connection_for_read.side_effect = Exception("Redis connection failed")

        # Execute task
        result = health_check_task.apply()

        # Verify
        assert result.successful()
        health_data = await result.get()
        assert health_data["status"] == "degraded"
        assert health_data["services"]["qdrant"] == "healthy"
        assert health_data["services"]["redis"] == "unhealthy"

    @patch('agent_service.tasks.JournalIndexer')
    @pytest.mark.asyncio
    async def test_reindex_user_entries_task(self, mock_indexer_class, sample_journal_data, celery_app):
        """Test reindexing all entries for a user."""
        # Setup mock
        mock_indexer = AsyncMock()
        mock_indexer.reindex_user_entries.return_value = {"indexed": 10, "failed": 1}
        mock_indexer_class.return_value = mock_indexer

        # Execute task
        result = reindex_user_entries_task.apply(
            args=[sample_journal_data["user_id"], sample_journal_data["tradition"]]
        )

        # Verify
        assert result.successful()
        final_result = await result.get()
        assert final_result["indexed"] == 10
        assert final_result["failed"] == 1


class TestTaskRetryLogic:
    """Test Celery task retry and error handling."""

    @patch('agent_service.tasks.index_journal_entry_by_id')
    def test_task_retry_configuration(self, mock_index_func, sample_journal_data, celery_app):
        """Test that tasks have proper retry configuration."""
        task = celery_app.tasks['agent_service.tasks.index_journal_entry_task']
        
        # Check retry configuration
        assert task.autoretry_for == (Exception,)
        assert task.retry_kwargs["max_retries"] == 3
        assert task.retry_kwargs["countdown"] == 60
        assert task.retry_backoff is True
        assert task.time_limit == 300

    @patch('agent_service.tasks.index_journal_entry_by_id')
    def test_task_retry_behavior(self, mock_index_func, sample_journal_data, celery_app):
        """Test task retry behavior in eager mode."""
        # In eager mode, retries are handled differently
        # We test that the task respects retry settings
        task = celery_app.tasks['agent_service.tasks.index_journal_entry_task']
        
        # Verify retry settings exist
        assert hasattr(task, 'retry_kwargs')
        assert task.retry_kwargs["max_retries"] > 0


class TestTaskIntegration:
    """Integration tests for task workflow."""

    @patch('agent_service.tasks.index_journal_entry_by_id')
    @pytest.mark.asyncio
    async def test_end_to_end_journal_indexing(self, mock_index_func, sample_journal_data, celery_app):
        """Test complete workflow from journal creation to indexing."""
        # Setup mock
        mock_index_func.return_value = True

        # Execute task
        result = index_journal_entry_task.apply(
            args=[sample_journal_data["entry_id"], sample_journal_data["user_id"], sample_journal_data["tradition"]]
        )

        # Verify workflow completed successfully
        assert result.successful()
        assert await result.get() is True
        mock_index_func.assert_called_once()

    @patch('agent_service.tasks.index_journal_entry_by_id')
    @pytest.mark.asyncio
    async def test_task_with_invalid_entry_id(self, mock_index_func, celery_app):
        """Test task behavior with invalid journal entry ID."""
        # Setup mock to raise exception
        mock_index_func.side_effect = ValueError("Entry not found")

        # Execute task
        result = index_journal_entry_task.apply(args=["invalid-id", str(uuid4()), "canon-default"])

        # Verify
        with pytest.raises(ValueError, match="Entry not found"):
            await result.get()


class TestConvenienceFunctions:
    """Test convenience functions for queueing tasks."""

    @patch('agent_service.tasks.current_app')
    def test_queue_journal_entry_indexing(self, mock_current_app, sample_journal_data):
        """Test queueing individual journal entry for indexing."""
        mock_current_app.send_task.return_value = MagicMock()
        
        result = queue_journal_entry_indexing(
            sample_journal_data["entry_id"],
            sample_journal_data["user_id"],
            sample_journal_data["tradition"]
        )
        
        mock_current_app.send_task.assert_called_once_with(
            'agent_service.tasks.index_journal_entry_task',
            args=[sample_journal_data["entry_id"], sample_journal_data["user_id"], sample_journal_data["tradition"]]
        )

    @patch('agent_service.tasks.current_app')
    def test_queue_batch_indexing(self, mock_current_app, sample_batch_data):
        """Test queueing batch indexing."""
        mock_current_app.send_task.return_value = MagicMock()
        
        result = queue_batch_indexing(sample_batch_data)
        
        mock_current_app.send_task.assert_called_once_with(
            'agent_service.tasks.batch_index_journal_entries_task',
            args=[sample_batch_data]
        )

    @patch('agent_service.tasks.current_app')
    def test_queue_user_reindex(self, mock_current_app, sample_journal_data):
        """Test queueing user reindex."""
        mock_current_app.send_task.return_value = MagicMock()
        
        result = queue_user_reindex(
            sample_journal_data["user_id"],
            sample_journal_data["tradition"]
        )
        
        mock_current_app.send_task.assert_called_once_with(
            'agent_service.tasks.reindex_user_entries_task',
            args=[sample_journal_data["user_id"], sample_journal_data["tradition"]]
        )

    @patch('agent_service.tasks.current_app')
    def test_queue_health_check(self, mock_current_app):
        """Test queueing health check."""
        mock_current_app.send_task.return_value = MagicMock()
        
        result = queue_health_check()
        
        mock_current_app.send_task.assert_called_once_with('agent_service.tasks.health_check_task')


class TestTaskConfiguration:
    """Test task configuration and settings."""

    def test_task_routing(self, celery_app):
        """Test that tasks are routed to correct queues."""
        routes = celery_app.conf.task_routes
        
        # Verify indexing tasks go to indexing queue
        assert routes['agent_service.tasks.index_journal_entry_task']['routing_key'] == "indexing"
        assert routes['agent_service.tasks.batch_index_journal_entries_task']['routing_key'] == "indexing"
        
        # Verify health checks go to monitoring queue
        assert routes['agent_service.tasks.health_check_task']['routing_key'] == "monitoring"
        
        # Verify maintenance tasks go to maintenance queue
        assert routes['agent_service.tasks.reindex_user_entries_task']['routing_key'] == "maintenance"

    def test_task_priority(self, celery_app):
        """Test that tasks have appropriate priority levels."""
        routes = celery_app.conf.task_routes
        
        # Real-time indexing should have higher priority than batch
        assert routes['agent_service.tasks.index_journal_entry_task']['priority'] > \
               routes['agent_service.tasks.batch_index_journal_entries_task']['priority']
        
        # Health checks should have highest priority
        assert routes['agent_service.tasks.health_check_task']['priority'] >= \
               routes['agent_service.tasks.index_journal_entry_task']['priority']
        
        # Maintenance tasks should have lowest priority
        assert routes['agent_service.tasks.reindex_user_entries_task']['priority'] < \
               routes['agent_service.tasks.index_journal_entry_task']['priority']

    def test_task_timeouts(self, celery_app):
        """Test that tasks have reasonable timeout values."""
        # Individual indexing should complete quickly
        task = celery_app.tasks['agent_service.tasks.index_journal_entry_task']
        assert task.time_limit == 300  # 5 minutes
        
        # Batch processing can take longer
        batch_task = celery_app.tasks['agent_service.tasks.batch_index_journal_entries_task']
        assert batch_task.time_limit == 1800  # 30 minutes
        
        # Reindexing can take longest
        reindex_task = celery_app.tasks['agent_service.tasks.reindex_user_entries_task']
        assert reindex_task.time_limit == 3600  # 1 hour
        
        # Health checks should be quick
        health_task = celery_app.tasks['agent_service.tasks.health_check_task']
        assert health_task.time_limit == 60  # 1 minute

    def test_task_retry_settings(self, celery_app):
        """Test that tasks have appropriate retry settings."""
        # Index task
        index_task = celery_app.tasks['agent_service.tasks.index_journal_entry_task']
        assert index_task.retry_kwargs["max_retries"] == 3
        assert index_task.retry_kwargs["countdown"] == 60
        
        # Batch task
        batch_task = celery_app.tasks['agent_service.tasks.batch_index_journal_entries_task']
        assert batch_task.retry_kwargs["max_retries"] == 2
        assert batch_task.retry_kwargs["countdown"] == 120
        
        # Reindex task
        reindex_task = celery_app.tasks['agent_service.tasks.reindex_user_entries_task']
        assert reindex_task.retry_kwargs["max_retries"] == 2
        assert reindex_task.retry_kwargs["countdown"] == 300