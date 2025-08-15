import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from journal_service.journal_service.main import app


@pytest.mark.asyncio
async def test_journal_entries_for_habit(client):
    # client fixture is provided in existing test setup
    user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    habit_id = str(uuid.uuid4())

    # Create a freeform entry linked to habit via mutation
    q = {
        "query": "mutation($input: FreeformEntryInput!){ createFreeformJournalEntry(input:$input){ id createdAt } }",
        "variables": {"input": {"content": "did my habit", "habitTemplateId": habit_id}},
    }
    r = await client.post("/graphql", json=q, headers={"x-internal-id": user_id})
    payload = r.json()
    assert "errors" not in payload, payload

    # Query entries for habit
    q2 = {
        "query": "query($hid: UUID!){ journalEntriesForHabit(habitTemplateId:$hid){ __typename id } }",
        "variables": {"hid": habit_id},
    }
    r2 = await client.post("/graphql", json=q2, headers={"x-internal-id": user_id})
    p2 = r2.json()
    assert "errors" not in p2, p2
    items = p2["data"]["journalEntriesForHabit"]
    assert len(items) >= 1

