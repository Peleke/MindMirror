from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_program_template_steps_gql(db_session, test_app):
    transport = ASGITransport(app=test_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    user_id = str(uuid.uuid4())

    # Create habit template
    habit_slug = f"habit-{uuid.uuid4().hex[:8]}"
    m1 = {
        "query": "mutation($i: HabitTemplateInput!){ createHabitTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": habit_slug, "title": "Eat Slowly", "shortDescription": "Take 20 minutes"}},
    }
    r1 = await client.post("/graphql", json=m1, headers={"x-internal-id": user_id})
    assert "errors" not in r1.json(), r1.json()
    habit_id = r1.json()["data"]["createHabitTemplate"]["id"]

    # Create program template
    prog_slug = f"prog-{uuid.uuid4().hex[:8]}"
    m2 = {
        "query": "mutation($i: ProgramTemplateInput!){ createProgramTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": prog_slug, "title": "Test Program"}},
    }
    r2 = await client.post("/graphql", json=m2, headers={"x-internal-id": user_id})
    assert "errors" not in r2.json(), r2.json()
    program_id = r2.json()["data"]["createProgramTemplate"]["id"]

    # Add a step
    m3 = {
        "query": "mutation($pid:String!, $i:ProgramStepInput!){ addProgramStep(programId:$pid, input:$i){ id } }",
        "variables": {"pid": program_id, "i": {"sequenceIndex": 0, "habitTemplateId": habit_id, "durationDays": 7}},
    }
    r3 = await client.post("/graphql", json=m3, headers={"x-internal-id": user_id})
    assert "errors" not in r3.json(), r3.json()

    # Query steps
    q = {"query": "query($pid:String!){ programTemplateSteps(programId:$pid){ id sequenceIndex durationDays habit{ id title shortDescription } } }", "variables": {"pid": program_id}}
    rs = await client.post("/graphql", json=q, headers={"x-internal-id": user_id})
    payload = rs.json()
    assert "errors" not in payload, payload
    steps = payload["data"]["programTemplateSteps"]
    assert len(steps) == 1
    s0 = steps[0]
    assert s0["sequenceIndex"] == 0
    assert s0["durationDays"] == 7
    assert s0["habit"]["id"] == habit_id
    assert s0["habit"]["title"] == "Eat Slowly"
    assert s0["habit"]["shortDescription"] == "Take 20 minutes"

    await client.aclose()


