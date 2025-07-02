"""
GraphQL Mutation Schema

Clean GraphQL mutation schema with proper separation of concerns and error handling.
"""

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import strawberry
from strawberry.types import Info

from agent_service.app.clients.journal_client import JournalClient
from agent_service.app.clients.qdrant_client import get_qdrant_client
from agent_service.app.graphql.context import (
    GraphQLContext,
    get_current_user_from_context,
)
from agent_service.app.graphql.types.suggestion_types import PerformanceReview
from agent_service.app.graphql.types.tool_types import ToolExecutionResult
from agent_service.app.services.llm_service import LLMService
from agent_service.app.services.search_service import SearchService

logger = logging.getLogger(__name__)


@strawberry.type
class Mutation:
    """GraphQL Mutation schema with all mutation fields."""

    @strawberry.mutation
    async def generate_review(
        self, info: Info[GraphQLContext, None], tradition: str
    ) -> PerformanceReview:
        """
        Generates a bi-weekly performance review for the authenticated user.

        Args:
            info: GraphQL context info
            tradition: Tradition to use for the review

        Returns:
            PerformanceReview: Generated performance review

        Raises:
            Exception: If authentication fails or processing fails
        """
        current_user = get_current_user_from_context(info)

        logger.info(f"generate_review called for user {current_user.id}")

        journal_client = JournalClient()
        llm_service = LLMService()

        try:
            # 1. Define date range for the last 14 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=14)

            logger.info(
                f"Fetching journal entries for user {current_user.id} from {start_date} to {end_date}"
            )

            # 2. Fetch journal entries directly from the journal service (same as summarize_journals)
            entries = await journal_client.list_by_user_for_period(
                user_id=str(current_user.id),
                start_date=start_date,
                end_date=end_date,
            )

            logger.info(
                f"Retrieved {len(entries)} journal entries for user {current_user.id}"
            )
            if entries:
                logger.info(
                    f"Sample entry: {entries[0].model_dump() if hasattr(entries[0], 'model_dump') else entries[0]}"
                )

            # Convert model instances to dictionaries for the LLM service
            entry_dicts = [entry.model_dump() for entry in entries]

            logger.info(f"Converted {len(entry_dicts)} entries to dictionaries")

            # 3. Generate the structured review using the LLM service
            review = await llm_service.get_performance_review(
                entry_dicts, period="bi-weekly"
            )

            logger.info(f"Generated review: key_success='{review.key_success[:50]}...'")

            return review

        except Exception as e:
            logger.error(
                f"Failed to generate performance review for user {current_user.id}: {e}"
            )
            return PerformanceReview(
                key_success="An error occurred while generating your review.",
                improvement_area="We could not process your journal entries at this time.",
                journal_prompt="Please try again later. How are you feeling right now?",
            )

    # --- Phase 4.5 Tool Execution Mutation ---

    @strawberry.mutation
    async def execute_tool(
        self,
        info: Info[GraphQLContext, None],
        tool_name: str,
        arguments: strawberry.scalars.JSON,
        version: Optional[str] = None,
    ) -> ToolExecutionResult:
        """
        Execute a tool from the registry.

        Args:
            info: GraphQL context info
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            version: Optional version of the tool to use

        Returns:
            ToolExecutionResult: Result of tool execution
        """
        get_current_user_from_context(info)  # Ensure authentication

        start_time = time.time()

        try:
            llm_service = LLMService()
            result = await llm_service.execute_tool(tool_name, arguments, version)

            execution_time_ms = int((time.time() - start_time) * 1000)

            return ToolExecutionResult(
                success=True, result=result, execution_time_ms=execution_time_ms
            )
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Failed to execute tool {tool_name}: {e}")

            return ToolExecutionResult(
                success=False,
                result=[],
                error=str(e),
                execution_time_ms=execution_time_ms,
            )

    @strawberry.mutation
    async def execute_subtool(
        self,
        info: Info[GraphQLContext, None],
        tool_name: str,
        subtool_name: str,
        arguments: strawberry.scalars.JSON,
        version: Optional[str] = None,
    ) -> ToolExecutionResult:
        """
        Execute a subtool of a specific tool.

        Args:
            info: GraphQL context info
            tool_name: Name of the parent tool
            subtool_name: Name of the subtool to execute
            arguments: Arguments to pass to the subtool
            version: Optional version of the tool

        Returns:
            ToolExecutionResult: Result of subtool execution
        """
        get_current_user_from_context(info)  # Ensure authentication

        start_time = time.time()

        try:
            llm_service = LLMService()
            result = await llm_service.execute_subtool(
                tool_name, subtool_name, arguments, version
            )

            execution_time_ms = int((time.time() - start_time) * 1000)

            return ToolExecutionResult(
                success=True,
                result=[result] if not isinstance(result, list) else result,
                execution_time_ms=execution_time_ms,
            )
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Failed to execute subtool {subtool_name} of tool {tool_name}: {e}"
            )

            return ToolExecutionResult(
                success=False,
                result=[],
                error=str(e),
                execution_time_ms=execution_time_ms,
            )

    @strawberry.mutation
    def upload_document(
        self,
        file_name: str,
        content: strawberry.scalars.Base64,
        tradition: str = "canon-default",
    ) -> bool:
        """
        Uploads a new document to the knowledge base for a specific tradition.

        Args:
            file_name: Name of the file to upload
            content: Base64 encoded content
            tradition: Tradition to upload to

        Returns:
            bool: Success status

        Raises:
            NotImplementedError: Feature moved to ingestion pipeline
        """
        # This functionality will be moved to the ingestion service pipeline
        # and triggered by a webhook, not a direct GraphQL mutation.
        raise NotImplementedError(
            "Document upload is now handled by the GCS ingestion pipeline."
        )
