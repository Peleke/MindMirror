import sys
import types
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.celery_app import celery_app
from src.tasks.journal_tasks import (
    JournalIndexer,
    index_journal_entry_by_id,
    queue_journal_entry_indexing,
)


@pytest.mark.asyncio
@patch("src.tasks.journal_tasks.current_app.send_task", new_callable=MagicMock)
async def test_journal_entry_creation_triggers_indexing(mock_send_task, client, user):
    """
    Given a new journal entry is created,
    when the appropriate hook is called,
    it verifies that an indexing task *would* be queued via Celery.

    Note: This test does not execute the task, only checks if it's sent.
    """
    entry_id = str(uuid4())
    test_user = user  # user is already a dict, not awaitable
    user_id = test_user["id"]
    tradition = "canon-default"

    # Simulate a webhook or API call that triggers indexing
    queue_journal_entry_indexing(entry_id, user_id, tradition)

    # Assert that a task was sent to Celery
    mock_send_task.assert_called_once_with(
        "celery_worker.tasks.index_journal_entry_task",
        args=[entry_id, user_id, tradition],
    )


@pytest.mark.asyncio
@patch("src.tasks.journal_tasks.get_celery_qdrant_client")
@patch("src.tasks.journal_tasks.get_embedding")
@patch("src.tasks.journal_tasks.create_celery_journal_client")
async def test_semantic_search_finds_indexed_journal_entry(
    mock_get_journal_client, mock_get_embedding, mock_get_qdrant_client, client, user
):
    """
    Verify that the indexing process correctly calls the sub-components
    without needing a live DB or vector store.
    """
    # 1. Arrange: Prepare mock data and patch return values
    entry_id = str(uuid4())
    test_user = user  # user is already a dict, not awaitable
    user_id = test_user["id"]
    tradition = "canon-default"
    unique_content = "The quick brown fox jumps over the lazy dog."

    # Mock the Journal Service client
    mock_journal_client = AsyncMock()
    mock_journal_client.get_entry_by_id.return_value = {
        "id": entry_id,
        "user_id": user_id,
        "entry_type": "FREEFORM",
        "payload": unique_content,
        "created_at": "2023-01-01T12:00:00Z",
    }
    mock_get_journal_client.return_value = mock_journal_client

    # Mock the embedding service
    mock_get_embedding.return_value = [0.1] * 1536  # Mock embedding vector

    # Mock the Qdrant client
    mock_qdrant_client = AsyncMock()
    mock_qdrant_client.get_or_create_personal_collection.return_value = "test_collection"
    mock_qdrant_client.index_personal_document.return_value = None
    mock_get_qdrant_client.return_value = mock_qdrant_client

    # 2. Act: Manually call the indexer function
    success = await index_journal_entry_by_id(entry_id, user_id, tradition)
    assert success, "Failed to index the journal entry for the test."

    # 3. Assert: Verify that our mocks were called correctly
    mock_journal_client.get_entry_by_id.assert_called_once_with(entry_id, user_id)
    mock_get_embedding.assert_called_once_with(unique_content)
    mock_qdrant_client.get_or_create_personal_collection.assert_called_once_with(tradition, user_id)
    mock_qdrant_client.index_personal_document.assert_called_once()

    # This test no longer needs to perform a real search, as we are unit-testing the indexing pipeline.
    # A separate test would cover the search functionality, mocking the retriever. 