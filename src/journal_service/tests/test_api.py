import uuid
from datetime import datetime
from uuid import UUID

import pytest
from httpx import AsyncClient

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_list_journal_entries_for_user(client: AsyncClient, seed_db):
    """
    Tests fetching all journal entries for the authenticated user.
    """
    # The union type doesn't expose common fields directly - need fragments for everything
    # Also need aliases for payload fields since they have different types
    query = """
        query GetJournalEntries {
          journalEntries {
            __typename
            ... on GratitudeJournalEntry {
              id
              userId
              gratitudePayload: payload {
                gratefulFor
              }
            }
            ... on FreeformJournalEntry {
              id
              userId
              freeformPayload: payload
            }
            ... on ReflectionJournalEntry {
              id
              userId
              reflectionPayload: payload {
                wins
              }
            }
          }
        }
    """
    response = await client.post("/graphql", json={"query": query})

    assert response.status_code == 200
    response_data = response.json()
    assert (
        "errors" not in response_data
    ), f"GraphQL Errors: {response_data.get('errors')}"

    entries = response_data["data"]["journalEntries"]
    assert len(entries) == 3  # The seed data has 3 entries for this user

    # Check that both entries belong to the authenticated user
    for entry in entries:
        assert entry["userId"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    # Check for the presence of the specific entry types
    typenames = {entry["__typename"] for entry in entries}
    assert "GratitudeJournalEntry" in typenames
    assert "FreeformJournalEntry" in typenames


@pytest.mark.asyncio
async def test_journal_entry_not_found_for_other_user(client: AsyncClient, seed_db):
    """
    This test ensures that the authenticated user only sees their own entries.
    """
    query = """
        query GetJournalEntries {
          journalEntries {
            __typename
            ... on GratitudeJournalEntry {
              id
              userId
            }
            ... on FreeformJournalEntry {
              id
              userId
            }
            ... on ReflectionJournalEntry {
              id
              userId
            }
          }
        }
    """
    response = await client.post("/graphql", json={"query": query})

    assert response.status_code == 200
    response_data = response.json()
    assert "errors" not in response_data

    entries = response_data["data"]["journalEntries"]
    # There should be 3 entries for the main test user, and zero for the other user.
    assert len(entries) == 3
    assert not any(entry["userId"] == "other-user-456" for entry in entries)


@pytest.mark.asyncio
async def test_create_and_delete_reflection_entry(client: AsyncClient, seed_db):
    """
    Tests the full lifecycle of creating and then deleting a structured journal entry
    for the authenticated user.
    """
    # 1. Create a Reflection Journal Entry with proper validation constraints
    create_mutation = """
        mutation CreateReflection($input: ReflectionEntryInput!) {
          createReflectionJournalEntry(input: $input) {
            id
            userId
            __typename
            payload {
              wins
              improvements
            }
          }
        }
    """
    create_variables = {
        "input": {
            "wins": [
                "Deployed a new feature successfully.",
                "Fixed critical bug",
                "Improved test coverage",
            ],
            "improvements": [
                "Better pre-deployment testing.",
                "More thorough code reviews",
            ],
            "mood": "Optimistic",
        }
    }

    response = await client.post(
        "/graphql", json={"query": create_mutation, "variables": create_variables}
    )
    assert response.status_code == 200
    response_json = response.json()
    assert (
        "errors" not in response_json
    ), f"GraphQL Errors: {response_json.get('errors')}"
    create_data = response_json["data"]["createReflectionJournalEntry"]
    entry_id = create_data["id"]

    # The user_id should match the one from the authenticated context
    assert create_data["userId"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    assert create_data["__typename"] == "ReflectionJournalEntry"
    assert len(create_data["payload"]["wins"]) == 3

    # 2. Verify the entry exists by listing it
    list_query = """
        query GetJournalEntries {
            journalEntries {
              __typename
              ... on GratitudeJournalEntry { id }
              ... on FreeformJournalEntry { id }
              ... on ReflectionJournalEntry { id }
            }
        }
    """
    response = await client.post("/graphql", json={"query": list_query})
    response_data = response.json()

    # This will now include the 3 seeded entries plus the one we just created
    assert len(response_data["data"]["journalEntries"]) == 4

    # 3. Delete the newly created entry
    delete_mutation = """
        mutation DeleteEntry($entryId: String!) {
          deleteJournalEntry(entryId: $entryId)
        }
    """
    delete_variables = {"entryId": entry_id}
    response = await client.post(
        "/graphql", json={"query": delete_mutation, "variables": delete_variables}
    )
    assert response.status_code == 200
    assert response.json()["data"]["deleteJournalEntry"] is True

    # 4. Verify the entry is gone
    response = await client.post("/graphql", json={"query": list_query})
    response_data = response.json()
    assert len(response_data["data"]["journalEntries"]) == 3


@pytest.mark.asyncio
async def test_check_for_entry_today(client: AsyncClient, seed_db):
    """
    Tests the journal_entry_exists_today query for the authenticated user.
    """
    query = """
        query CheckEntryToday($entryType: String!) {
            journalEntryExistsToday(entryType: $entryType)
        }
    """

    # Check for a GRATITUDE entry, which was created today in seed_db for the user
    variables_true = {"entryType": "GRATITUDE"}
    response_true = await client.post(
        "/graphql", json={"query": query, "variables": variables_true}
    )
    assert response_true.status_code == 200
    response_json_true = response_true.json()
    assert (
        "errors" not in response_json_true
    ), f"GraphQL Errors: {response_json_true.get('errors')}"
    assert response_json_true["data"]["journalEntryExistsToday"] is True

    # Check for a REFLECTION entry, which should also exist today for the user
    variables_false = {"entryType": "REFLECTION"}
    response_false = await client.post(
        "/graphql", json={"query": query, "variables": variables_false}
    )
    assert response_false.status_code == 200
    response_json_false = response_false.json()
    assert (
        "errors" not in response_json_false
    ), f"GraphQL Errors: {response_json_false.get('errors')}"
    assert response_json_false["data"]["journalEntryExistsToday"] is True
