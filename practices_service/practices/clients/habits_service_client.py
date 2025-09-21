"""
Dedicated client for communicating with habits_service.
This can be extended with HMAC authentication when needed.
"""
import os
import httpx
from typing import List, Optional, Dict, Any
from datetime import date
import logging

logger = logging.getLogger(__name__)


class HabitsServiceClient:
    """Client for interacting with habits_service GraphQL API."""

    def __init__(self):
        self.base_url = os.getenv("HABITS_SERVICE_BASE_URL", "").strip()
        if not self.base_url:
            raise ValueError("HABITS_SERVICE_BASE_URL environment variable not set")

        # TODO: Add HMAC authentication headers when implementing auth
        self.default_headers = {
            'content-type': 'application/json',
        }

    async def _execute_graphql(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query/mutation against habits_service."""

        headers = self.default_headers.copy()
        if auth_token:
            headers['authorization'] = f"Bearer {auth_token}"

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/graphql",
                    headers=headers,
                    json={
                        "query": query,
                        "variables": variables or {}
                    }
                )

                if response.status_code != 200:
                    logger.error(f"Habits service error: {response.status_code} - {response.text}")
                    raise Exception(f"Habits service returned {response.status_code}: {response.text}")

                result = response.json()
                if result.get("errors"):
                    logger.error(f"GraphQL errors from habits service: {result['errors']}")
                    raise Exception(f"GraphQL errors: {result['errors']}")

                return result["data"]

            except httpx.RequestError as e:
                logger.error(f"Failed to connect to habits service: {e}")
                raise Exception(f"Failed to connect to habits service: {e}")

    async def create_lesson_task(
        self,
        user_id: str,
        lesson_template_id: str,
        task_date: date,
        segment_ids: Optional[List[str]] = None,
        auth_token: Optional[str] = None
    ) -> bool:
        """Create a lesson task for a specific user and date."""

        query = """
            mutation CreateLessonTask($userId: ID!, $date: Date!, $lessonTemplateId: ID!, $segmentIds: [String!]) {
                createLessonTask(userId: $userId, date: $date, lessonTemplateId: $lessonTemplateId, segmentIds: $segmentIds)
            }
        """

        variables = {
            "userId": user_id,
            "date": task_date.isoformat(),
            "lessonTemplateId": lesson_template_id,
            "segmentIds": segment_ids
        }

        result = await self._execute_graphql(query, variables, auth_token)
        return result["createLessonTask"]

    async def get_lesson_templates(self, auth_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all lesson templates from habits_service."""

        query = """
            query {
                lessonTemplates {
                    id
                    slug
                    title
                    summary
                    markdownContent
                    segments {
                        id
                        label
                        selector
                    }
                    defaultSegment
                }
            }
        """

        result = await self._execute_graphql(query, None, auth_token)
        return result.get("lessonTemplates", [])

    async def get_lesson_template_by_slug(self, slug: str, auth_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a lesson template by slug."""

        query = """
            query GetLessonTemplateBySlug($slug: String!) {
                lessonTemplateBySlug(slug: $slug) {
                    id
                    slug
                    title
                    summary
                    markdownContent
                    segments {
                        id
                        label
                        selector
                    }
                    defaultSegment
                }
            }
        """

        variables = {"slug": slug}
        result = await self._execute_graphql(query, variables, auth_token)
        return result.get("lessonTemplateBySlug")
