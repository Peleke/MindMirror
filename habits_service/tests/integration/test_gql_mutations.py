from __future__ import annotations

import json
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from habits_service.habits_service.app.main import app


@pytest.mark.asyncio
async def test_create_templates_and_assignment_via_gql(db_session):
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    # Create habit template
    q1 = {
        "query": "mutation($input: HabitTemplateInput!){ createHabitTemplate(input:$input){ id slug title } }",
        "variables": {"input": {"slug": "hydrate-gql", "title": "Hydrate"}},
    }
    r1 = await client.post("/graphql", json=q1)
    data1 = r1.json()["data"]["createHabitTemplate"]
    habit_id = data1["id"]

    # Create lesson template
    q2 = {
        "query": "mutation($input: LessonTemplateInput!){ createLessonTemplate(input:$input){ id slug title } }",
        "variables": {"input": {"slug": "lesson-gql", "title": "Lesson GQL", "markdownContent": "# md"}},
    }
    r2 = await client.post("/graphql", json=q2)
    lesson_id = r2.json()["data"]["createLessonTemplate"]["id"]

    # Create program and step, add step lesson, assign
    q3 = {
        "query": "mutation($input: ProgramTemplateInput!){ createProgramTemplate(input:$input){ id slug title } }",
        "variables": {"input": {"slug": "prog-gql", "title": "Prog GQL"}},
    }
    r3 = await client.post("/graphql", json=q3)
    program_id = r3.json()["data"]["createProgramTemplate"]["id"]

    q4 = {
        "query": "mutation($pid: String!, $input: ProgramStepInput!){ addProgramStep(programId:$pid, input:$input){ id } }",
        "variables": {"pid": program_id, "input": {"sequenceIndex": 0, "habitTemplateId": habit_id, "durationDays": 7}},
    }
    r4 = await client.post("/graphql", json=q4)
    step_id = r4.json()["data"]["addProgramStep"]["id"]

    q5 = {
        "query": "mutation($sid: String!, $did: Int!, $lid: String!){ addStepLesson(stepId:$sid, dayIndex:$did, lessonTemplateId:$lid) }",
        "variables": {"sid": step_id, "did": 0, "lid": lesson_id},
    }
    r5 = await client.post("/graphql", json=q5)
    assert r5.json()["data"]["addStepLesson"] is True

    q6 = {
        "query": "mutation($uid: String!, $pid: String!){ assignProgramToUser(userId:$uid, programId:$pid, startDate:\"2025-08-11\"){ id status } }",
        "variables": {"uid": "u-gql", "pid": program_id},
    }
    r6 = await client.post("/graphql", json=q6)
    assert r6.json()["data"]["assignProgramToUser"]["status"] == "active"

    await client.aclose()
