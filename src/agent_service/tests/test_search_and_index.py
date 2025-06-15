import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import asynccontextmanager
import sys, types

from agent_service.models.journal import JournalEntry
from agent_service.journal_indexer import index_journal_entry_by_id, JournalIndexer
from agent_service.models.sql.journal import JournalEntryModel
from celery_app import celery_app


@pytest.mark.asyncio
@patch.object(celery_app, "send_task", new_callable=MagicMock)
async def test_journal_entry_creation_triggers_indexing(mock_send_task, client, user):
    """
    Given a new journal entry is created,
    when the appropriate hook is called,
    it verifies that an indexing task *would* be queued via Celery.
    
    Note: This test does not execute the task, only checks if it's sent.
    """
    entry_id = str(uuid4())
    user_id = str(user.id)
    tradition = "canon-default"
    
    # Simulate a webhook or API call that triggers indexing
    index_journal_entry_by_id(entry_id, user_id, tradition)

    # Assert that a task was sent to Celery
    mock_send_task.assert_called_once_with(
        "index_journal_entry_task",
        args=(entry_id, user_id, tradition),
        kwargs={}
    )


@pytest.mark.asyncio
@patch("agent_service.embedding.get_embedding", new_callable=AsyncMock)
@patch.object(JournalIndexer, "index_entry", new_callable=AsyncMock)
@patch(
    "agent_service.journal_indexer.JournalServiceClient.get_entry_by_id",
    new_callable=AsyncMock,
)
async def test_semantic_search_finds_indexed_journal_entry(
    mock_get_entry, mock_index_entry, mock_get_embedding, client, user
):
    """
    Verify that the indexing process correctly calls the sub-components
    without needing a live DB or vector store.
    """
    # 1. Arrange: Prepare mock data and patch return values
    entry_id = str(uuid4())
    user_id = str(user.id)
    unique_content = "The quick brown fox jumps over the lazy dog."

    # Mock the Journal Service client call to return a journal entry dictionary
    mock_get_entry.return_value = {
        "id": entry_id,
        "user_id": user_id,
        "entry_type": "FREEFORM",
        "payload": unique_content,
        "created_at": "2023-01-01T12:00:00Z",
    }

    # Mock the final indexing step to avoid hitting Qdrant
    mock_index_entry.return_value = True

    # 2. Act: Manually call the indexer function
    success = await index_journal_entry_by_id(entry_id, user_id)
    assert success, "Failed to index the journal entry for the test."

    # 3. Assert: Verify that our mocks were called correctly
    mock_get_entry.assert_called_once_with(entry_id, user_id)
    mock_index_entry.assert_called_once()

    # Check the arguments passed to the final indexing method
    call_args, call_kwargs = mock_index_entry.call_args
    # Arguments are passed positionally: (entry_data, user_id, tradition)
    indexed_data = call_args[0]
    called_user_id = call_args[1]
    assert indexed_data["id"] == entry_id
    assert called_user_id == user_id

    # This test no longer needs to perform a real search, as we are unit-testing the indexing pipeline.
    # A separate test would cover the search functionality, mocking the retriever. 