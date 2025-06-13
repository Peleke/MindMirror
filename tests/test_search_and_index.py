import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from contextlib import asynccontextmanager
import sys, types

from src.models.journal import JournalEntry
from src.journal_indexer import index_journal_entry_by_id
from src.models.sql.journal import JournalEntryModel


@pytest.mark.asyncio
async def test_journal_entry_creation_triggers_indexing(client, user):
    """
    Verify that creating a journal entry queues an indexing task.
    """
    with patch("src.tasks.queue_journal_entry_indexing") as mock_queue_task:
        # Create a freeform journal entry using the client fixture
        response = await client.post(
            "/graphql",
            json={
                "query": """
                    mutation CreateEntry($input: FreeformEntryInput!) {
                        createFreeformJournalEntry(input: $input) {
                            id
                            entryType
                            payload
                        }
                    }
                """,
                "variables": {"input": {"content": "This is a test entry for indexing."}},
            },
        )

        assert response.status_code == 200
        data = response.json()["data"]["createFreeformJournalEntry"]
        entry_id = data["id"]

        # Verify that the indexing task was called with expected kwargs
        mock_queue_task.assert_called_once()
        kwargs = mock_queue_task.call_args.kwargs
        assert kwargs["entry_id"] == entry_id
        assert kwargs["user_id"] == str(user.id)
        assert kwargs["tradition"] == "canon-default"


@pytest.mark.asyncio
async def test_semantic_search_finds_indexed_journal_entry(
    client, user, session
):
    """
    Verify that semantic search can find a manually indexed journal entry.
    """
    # 1. Create a journal entry object with unique text
    entry_id = uuid4()
    user_id = str(user.id)
    unique_content = "The quick brown fox jumps over the lazy dog."
    
    # 2. Save the entry to the DB using the session fixture
    db_entry = JournalEntryModel(
        id=entry_id,
        user_id=user_id,
        entry_type="FREEFORM",
        payload=unique_content
    )
    session.add(db_entry)
    # The session fixture will auto-commit on successful test completion

    # Ensure DB commit so the entry is persisted
    await session.commit()

    # Patch embedding module to avoid external dependency BEFORE indexing
    dummy_emb = types.ModuleType("src.embedding")
    async def fake_get_embedding(text):
        return [0.0] * 384
    dummy_emb.get_embedding = fake_get_embedding
    sys.modules["src.embedding"] = dummy_emb

    # 3. Manually index this entry using patched session
    # We patch get_session to use our test session, ensuring the indexer finds the entry
    @asynccontextmanager
    async def session_context_manager(*args, **kwargs):
        yield session

    with patch("src.database.get_session", return_value=session_context_manager()):
        success = await index_journal_entry_by_id(str(entry_id), user_id)
        assert success, "Failed to index the journal entry for the test."

    # 4. Perform a semantic search query
    response = await client.post(
        "/graphql",
        json={
            "query": """
                query Search($query: String!) {
                    semanticSearch(query: $query, includePersonal: true, limit: 5)
                }
            """,
            "variables": {"query": "A fast, brown animal and a sleepy canine."},
        },
    )

    # 5. Verify the results
    assert response.status_code == 200
    search_results = response.json()["data"]["semanticSearch"]

    assert len(search_results) > 0, "Semantic search returned no results."

    # Results are plain strings; check containment
    found = any(unique_content in result for result in search_results)
    assert found, "The indexed journal entry was not found in the search results."

    # Patch embedding module to avoid external dependency
    dummy_emb = types.ModuleType("src.embedding")
    async def fake_get_embedding(text):
        return [0.0]*384  # sample vector
    dummy_emb.get_embedding = fake_get_embedding
    sys.modules["src.embedding"] = dummy_emb 