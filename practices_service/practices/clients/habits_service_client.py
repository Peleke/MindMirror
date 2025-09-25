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
        auth_token: Optional[str] = None,
        internal_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a GraphQL query/mutation against habits_service."""

        headers = self.default_headers.copy()
        if auth_token:
            headers['authorization'] = f"Bearer {auth_token}"
        # Mesh/habits service recognizes x-internal-id for current user context
        if internal_user_id:
            headers['x-internal-id'] = internal_user_id

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

    async def enroll_user_in_program(
        self,
        program_template_id: str,
        start_date: date,
        auth_token: Optional[str] = None,
        internal_user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Enroll a user in a habits program template."""

        query = """
            mutation AssignProgramToUser($programId: String!, $startDate: Date!) {
                assignProgramToUser(programId: $programId, startDate: $startDate) {
                    id
                    userId
                    programTemplateId
                    status
                }
            }
        """

        variables = {
            "programId": program_template_id,
            "startDate": start_date.isoformat()
        }

        try:
            logger.info(f"Executing habits enrollment GraphQL for program {program_template_id} with variables: {variables} internal_user_id={bool(internal_user_id)}")
            result = await self._execute_graphql(query, variables, auth_token, internal_user_id)
            logger.info(f"Habits enrollment GraphQL response: {result}")
            enrollment_result = result.get("assignProgramToUser")
            if enrollment_result:
                logger.info(f"Habits enrollment successful: {enrollment_result}")
            else:
                logger.warning(f"Habits enrollment returned null/empty result: {result}")
            return enrollment_result
        except Exception as e:
            logger.error(f"Failed to enroll user in habits program {program_template_id}: {e}", exc_info=True)
            # Don't raise - we don't want to fail the practices enrollment if habits enrollment fails
            return None

    async def get_program_templates(self, auth_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all program templates from habits_service."""

        query = """
            query {
                programTemplates {
                    id
                    slug
                    title
                    description
                    subtitle
                    heroImageUrl
                }
            }
        """

        result = await self._execute_graphql(query, None, auth_token)
        return result.get("programTemplates", [])

    async def create_initial_program_tasks(
        self,
        program_template_id: str,
        user_id: str,
        start_date: date,
        auth_token: Optional[str] = None
    ) -> bool:
        """
        Create initial lesson tasks for day 0 of a program.
        
        Note: This method is deprecated. The habits service planner (todaysTasks) now
        automatically shows lesson tasks based on program step template mappings.
        This method is kept for backward compatibility but does nothing.
        """
        logger.info(f"create_initial_program_tasks called for program {program_template_id} - this is deprecated and no longer needed")
        return True
