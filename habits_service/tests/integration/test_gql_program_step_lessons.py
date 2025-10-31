from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_program_step_lessons_gql(db_session, test_app):
    transport = ASGITransport(app=test_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    user_id = str(uuid.uuid4())

    # Create a lesson template
    lesson_slug = f"lesson-{uuid.uuid4().hex[:8]}"
    m_lesson = {
        "query": "mutation($i: LessonTemplateInput!){ createLessonTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": lesson_slug, "title": "Welcome", "markdownContent": "# hi"}},
    }
    rl = await client.post("/graphql", json=m_lesson, headers={"x-internal-id": user_id})
    assert "errors" not in rl.json(), rl.json()
    lesson_id = rl.json()["data"]["createLessonTemplate"]["id"]

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
    step_id = r3.json()["data"]["addProgramStep"]["id"]

    # Map lesson to day 0 of the step
    m4 = {
        "query": "mutation($sid:String!, $day:Int!, $lid:String!){ addStepLesson(stepId:$sid, dayIndex:$day, lessonTemplateId:$lid) }",
        "variables": {"sid": step_id, "day": 0, "lid": lesson_id},
    }
    r4 = await client.post("/graphql", json=m4, headers={"x-internal-id": user_id})
    assert "errors" not in r4.json(), r4.json()

    # Query step lessons
    q = {"query": "query($sid:String!){ programStepLessons(programStepId:$sid){ dayIndex lessonTemplateId title summary estReadMinutes } }", "variables": {"sid": step_id}}
    rs = await client.post("/graphql", json=q, headers={"x-internal-id": user_id})
    payload = rs.json()
    assert "errors" not in payload, payload
    items = payload["data"]["programStepLessons"]
    assert len(items) == 1
    assert items[0]["lessonTemplateId"] == lesson_id
    assert items[0]["dayIndex"] == 0

    await client.aclose()


