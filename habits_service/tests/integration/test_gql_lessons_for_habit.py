from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_lessons_for_habit_end_to_end(db_session, test_app):
    transport = ASGITransport(app=test_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    user_id = str(uuid.uuid4())

    # Create habit
    habit_slug = f"habit-lfh-{uuid.uuid4().hex[:8]}"
    m_h = {
        "query": "mutation($i: HabitTemplateInput!){ createHabitTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": habit_slug, "title": "Hydrate", "shortDescription": "Drink water"}},
    }
    rh = await client.post("/graphql", json=m_h, headers={"x-internal-id": user_id})
    assert "errors" not in rh.json(), rh.json()
    habit_id = rh.json()["data"]["createHabitTemplate"]["id"]

    # Create lesson
    lesson_slug = f"lesson-lfh-{uuid.uuid4().hex[:8]}"
    m_l = {
        "query": "mutation($i: LessonTemplateInput!){ createLessonTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": lesson_slug, "title": "Why Water", "markdownContent": "# Water", "summary": "Water matters."}},
    }
    rl = await client.post("/graphql", json=m_l, headers={"x-internal-id": user_id})
    assert "errors" not in rl.json(), rl.json()
    lesson_id = rl.json()["data"]["createLessonTemplate"]["id"]

    # Create program
    prog_slug = f"prog-lfh-{uuid.uuid4().hex[:8]}"
    m_p = {
        "query": "mutation($i: ProgramTemplateInput!){ createProgramTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": prog_slug, "title": "LFH Program"}},
    }
    rp = await client.post("/graphql", json=m_p, headers={"x-internal-id": user_id})
    assert "errors" not in rp.json(), rp.json()
    program_id = rp.json()["data"]["createProgramTemplate"]["id"]

    # Add step (7 days)
    m_s = {
        "query": "mutation($pid:String!, $i:ProgramStepInput!){ addProgramStep(programId:$pid, input:$i){ id } }",
        "variables": {"pid": program_id, "i": {"sequenceIndex": 0, "habitTemplateId": habit_id, "durationDays": 7}},
    }
    rs = await client.post("/graphql", json=m_s, headers={"x-internal-id": user_id})
    assert "errors" not in rs.json(), rs.json()
    step_id = rs.json()["data"]["addProgramStep"]["id"]

    # Add step lesson on day 0
    m_sl = {
        "query": "mutation($sid:String!,$did:Int!,$lid:String!){ addStepLesson(stepId:$sid, dayIndex:$did, lessonTemplateId:$lid) }",
        "variables": {"sid": step_id, "did": 0, "lid": lesson_id},
    }
    rsl = await client.post("/graphql", json=m_sl, headers={"x-internal-id": user_id})
    assert "errors" not in rsl.json(), rsl.json()

    # Assign program to user starting today
    today = "2025-08-13"
    m_a = {
        "query": "mutation($pid:String!){ assignProgramToUser(programId:$pid, startDate:\"2025-08-13\"){ id status } }",
        "variables": {"pid": program_id},
    }
    ra = await client.post("/graphql", json=m_a, headers={"x-internal-id": user_id})
    assert "errors" not in ra.json(), ra.json()

    # Query lessonsForHabit -> should show pending
    q1 = {
        "query": "query($hid:String!,$d:Date!){ lessonsForHabit(habitTemplateId:$hid, onDate:$d){ lessonTemplateId title summary completed } }",
        "variables": {"hid": habit_id, "d": today},
    }
    r_q1 = await client.post("/graphql", json=q1, headers={"x-internal-id": user_id})
    payload1 = r_q1.json()
    assert "errors" not in payload1, payload1
    lessons1 = payload1["data"]["lessonsForHabit"]
    assert len(lessons1) == 1
    assert lessons1[0]["lessonTemplateId"] == lesson_id
    assert lessons1[0]["completed"] is False

    # Mark lesson completed on same date
    m_c = {
        "query": "mutation($lid:String!,$d:Date!){ markLessonCompleted(lessonTemplateId:$lid, onDate:$d) }",
        "variables": {"lid": lesson_id, "d": today},
    }
    rc = await client.post("/graphql", json=m_c, headers={"x-internal-id": user_id})
    assert "errors" not in rc.json(), rc.json()

    # Query again -> completed true
    r_q2 = await client.post("/graphql", json=q1, headers={"x-internal-id": user_id})
    payload2 = r_q2.json()
    assert "errors" not in payload2, payload2
    lessons2 = payload2["data"]["lessonsForHabit"]
    assert len(lessons2) == 1
    assert lessons2[0]["completed"] is True

    await client.aclose()


