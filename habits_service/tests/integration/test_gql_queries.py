from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from habits_service.habits_service.app.main import app


@pytest.mark.asyncio
async def test_program_queries_and_assignments(db_session):
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    # Seed minimal program via mutations
    habit_slug = f"hydrate-q-{uuid.uuid4().hex[:8]}"
    m1 = {
        "query": "mutation($i: HabitTemplateInput!){ createHabitTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": habit_slug, "title": "Hydrate"}},
    }
    r1 = await client.post("/graphql", json=m1)
    payload1 = r1.json()
    assert "errors" not in payload1, payload1
    habit_id = payload1["data"]["createHabitTemplate"]["id"]

    program_slug = f"prog-q-{uuid.uuid4().hex[:8]}"
    m2 = {
        "query": "mutation($i: ProgramTemplateInput!){ createProgramTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": program_slug, "title": "Prog Q"}},
    }
    r2 = await client.post("/graphql", json=m2)
    payload2 = r2.json()
    assert "errors" not in payload2, payload2
    program_id = payload2["data"]["createProgramTemplate"]["id"]

    m3 = {
        "query": "mutation($pid: String!, $i: ProgramStepInput!){ addProgramStep(programId:$pid, input:$i){ id } }",
        "variables": {"pid": program_id, "i": {"sequenceIndex": 0, "habitTemplateId": habit_id, "durationDays": 7}},
    }
    payload3 = (await client.post("/graphql", json=m3)).json()
    assert "errors" not in payload3, payload3

    # Query list and by slug
    q1 = {"query": "{ programTemplates { id slug title } }"}
    rlist = await client.post("/graphql", json=q1)
    assert any(p["slug"] == program_slug for p in rlist.json()["data"]["programTemplates"])  # type: ignore

    q2 = {"query": "query($s:String!){ programTemplateBySlug(slug:$s){ id slug title } }", "variables": {"s": program_slug}}
    rprog = await client.post("/graphql", json=q2)
    assert rprog.json()["data"]["programTemplateBySlug"]["slug"] == "prog-q"

    # Assign and list assignments
    m4 = {
        "query": "mutation($uid:String!,$pid:String!){ assignProgramToUser(userId:$uid, programId:$pid, startDate:\"2025-08-12\"){ id status } }",
        "variables": {"uid": "u-q", "pid": program_id},
    }
    payload4 = (await client.post("/graphql", json=m4)).json()
    assert "errors" not in payload4, payload4

    q3 = {"query": "query($uid:String!){ programAssignments(userId:$uid){ programTemplateId status } }", "variables": {"uid": "u-q"}}
    rass = await client.post("/graphql", json=q3)
    rows = rass.json()["data"]["programAssignments"]
    assert len(rows) >= 1 and rows[0]["status"] == "active"
    await client.aclose()


