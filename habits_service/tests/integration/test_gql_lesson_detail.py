from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_lesson_template_by_id_gql(db_session, test_app):
    transport = ASGITransport(app=test_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    user_id = str(uuid.uuid4())

    # Create lesson via mutation
    lesson_slug = f"lesson-detail-{uuid.uuid4().hex[:8]}"
    m = {
        "query": "mutation($i: LessonTemplateInput!){ createLessonTemplate(input:$i){ id slug title } }",
        "variables": {
            "i": {
                "slug": lesson_slug,
                "title": "Lesson Detail",
                "markdownContent": "# Hello World\n\nThis is a test.",
                "summary": "This is a test.",
            }
        },
    }
    r = await client.post("/graphql", json=m, headers={"x-internal-id": user_id})
    payload = r.json()
    assert "errors" not in payload, payload
    lesson_id = payload["data"]["createLessonTemplate"]["id"]

    # Query by id
    q = {
        "query": "query($id:String!){ lessonTemplateById(id:$id){ id slug title summary markdownContent } }",
        "variables": {"id": lesson_id},
    }
    rq = await client.post("/graphql", json=q, headers={"x-internal-id": user_id})
    data = rq.json()
    assert "errors" not in data, data
    lt = data["data"]["lessonTemplateById"]
    assert lt["id"] == lesson_id
    assert lt["slug"] == lesson_slug
    assert lt["title"] == "Lesson Detail"
    assert lt["summary"] == "This is a test."
    assert lt["markdownContent"].startswith("# Hello World")

    await client.aclose()


