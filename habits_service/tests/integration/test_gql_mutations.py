from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
import uuid

from habits_service.habits_service.app.main import app


@pytest.mark.asyncio
async def test_create_templates_and_assignment_via_gql(db_session):
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    # Create habit template
    habit_slug = f"hydrate-gql-{uuid.uuid4().hex[:8]}"
    q1 = {
        "query": "mutation($input: HabitTemplateInput!){ createHabitTemplate(input:$input){ id slug title } }",
        "variables": {"input": {"slug": habit_slug, "title": "Hydrate"}},
    }
    r1 = await client.post("/graphql", json=q1)
    payload1 = r1.json()
    assert "errors" not in payload1, payload1
    data1 = payload1["data"]["createHabitTemplate"]
    habit_id = data1["id"]

    # Create lesson template
    lesson_slug = f"lesson-gql-{uuid.uuid4().hex[:8]}"
    q2 = {
        "query": "mutation($input: LessonTemplateInput!){ createLessonTemplate(input:$input){ id slug title } }",
        "variables": {"input": {"slug": lesson_slug, "title": "Lesson GQL", "markdownContent": "# md"}},
    }
    r2 = await client.post("/graphql", json=q2)
    payload2 = r2.json()
    assert "errors" not in payload2, payload2
    lesson_id = payload2["data"]["createLessonTemplate"]["id"]

    # Create program and step, add step lesson, assign
    program_slug = f"prog-gql-{uuid.uuid4().hex[:8]}"
    q3 = {
        "query": "mutation($input: ProgramTemplateInput!){ createProgramTemplate(input:$input){ id slug title } }",
        "variables": {"input": {"slug": program_slug, "title": "Prog GQL"}},
    }
    r3 = await client.post("/graphql", json=q3)
    payload3 = r3.json()
    assert "errors" not in payload3, payload3
    program_id = payload3["data"]["createProgramTemplate"]["id"]

    q4 = {
        "query": "mutation($pid: String!, $input: ProgramStepInput!){ addProgramStep(programId:$pid, input:$input){ id } }",
        "variables": {"pid": program_id, "input": {"sequenceIndex": 0, "habitTemplateId": habit_id, "durationDays": 7}},
    }
    r4 = await client.post("/graphql", json=q4)
    payload4 = r4.json()
    assert "errors" not in payload4, payload4
    step_id = payload4["data"]["addProgramStep"]["id"]

    q5 = {
        "query": "mutation($sid: String!, $did: Int!, $lid: String!){ addStepLesson(stepId:$sid, dayIndex:$did, lessonTemplateId:$lid) }",
        "variables": {"sid": step_id, "did": 0, "lid": lesson_id},
    }
    r5 = await client.post("/graphql", json=q5)
    payload5 = r5.json()
    assert "errors" not in payload5, payload5
    assert payload5["data"]["addStepLesson"] is True

    q6 = {
        "query": "mutation($uid: String!, $pid: String!){ assignProgramToUser(userId:$uid, programId:$pid, startDate:\"2025-08-11\"){ id status } }",
        "variables": {"uid": "u-gql", "pid": program_id},
    }
    r6 = await client.post("/graphql", json=q6)
    payload6 = r6.json()
    assert "errors" not in payload6, payload6
    assert payload6["data"]["assignProgramToUser"]["status"] == "active"

    await client.aclose()
