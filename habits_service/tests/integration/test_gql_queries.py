from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from habits_service.habits_service.app.main import app


@pytest.mark.asyncio
async def test_program_queries_and_assignments(db_session, test_app):
    transport = ASGITransport(app=test_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    user_id = str(uuid.uuid4())

    # Seed minimal program via mutations
    habit_slug = f"hydrate-q-{uuid.uuid4().hex[:8]}"
    m1 = {
        "query": "mutation($i: HabitTemplateInput!){ createHabitTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": habit_slug, "title": "Hydrate"}},
    }
    r1 = await client.post("/graphql", json=m1, headers={"x-internal-id": user_id})
    payload1 = r1.json()
    assert "errors" not in payload1, payload1
    habit_id = payload1["data"]["createHabitTemplate"]["id"]

    program_slug = f"prog-q-{uuid.uuid4().hex[:8]}"
    m2 = {
        "query": "mutation($i: ProgramTemplateInput!){ createProgramTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": program_slug, "title": "Prog Q"}},
    }
    r2 = await client.post("/graphql", json=m2, headers={"x-internal-id": user_id})
    payload2 = r2.json()
    assert "errors" not in payload2, payload2
    program_id = payload2["data"]["createProgramTemplate"]["id"]

    m3 = {
        "query": "mutation($pid: String!, $i: ProgramStepInput!){ addProgramStep(programId:$pid, input:$i){ id } }",
        "variables": {"pid": program_id, "i": {"sequenceIndex": 0, "habitTemplateId": habit_id, "durationDays": 7}},
    }
    payload3 = (await client.post("/graphql", json=m3, headers={"x-internal-id": user_id})).json()
    assert "errors" not in payload3, payload3

    # Query list and by slug
    q1 = {"query": "{ programTemplates { id slug title } }"}
    rlist = await client.post("/graphql", json=q1, headers={"x-internal-id": user_id})
    assert any(p["slug"] == program_slug for p in rlist.json()["data"]["programTemplates"])  # type: ignore

    q2 = {"query": "query($s:String!){ programTemplateBySlug(slug:$s){ id slug title } }", "variables": {"s": program_slug}}
    rprog = await client.post("/graphql", json=q2, headers={"x-internal-id": user_id})
    assert rprog.json()["data"]["programTemplateBySlug"]["slug"] == program_slug

    # Assign and list assignments
    m4 = {
        "query": "mutation($pid:String!){ assignProgramToUser(programId:$pid, startDate:\"2025-08-12\"){ id status } }",
        "variables": {"pid": program_id},
    }
    payload4 = (await client.post("/graphql", json=m4, headers={"x-internal-id": user_id})).json()
    assert "errors" not in payload4, payload4

    q3 = {"query": "{ programAssignments { programTemplateId status } }"}
    rass = await client.post("/graphql", json=q3, headers={"x-internal-id": user_id})
    rows = rass.json()["data"]["programAssignments"]
    assert len(rows) >= 1 and rows[0]["status"] == "active"
    await client.aclose()


