import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta, timezone

import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

# Imports relative to agent_service
from agent_service.api.types.suggestion_types import (MealSuggestion,
                                                      PerformanceReview, JournalSummary)
from agent_service.clients.history_client import HistoryClient
from agent_service.clients.journal_client import JournalClient
from agent_service.clients.users_client import UsersClient
from agent_service.database import get_session
from agent_service.embedding import get_embedding
from agent_service.engine import get_engine_for_tradition
from agent_service.qdrant_engine import get_qdrant_engine_for_tradition
from agent_service.services.llm_service import LLMService
from agent_service.services.suggestion_service import SuggestionService
from agent_service.services.tradition_repository import TraditionRepository
from agent_service.services.tradition_service import TraditionService
from agent_service.uow import UnitOfWork, get_uow
from agent_service.vector_stores.qdrant_client import get_qdrant_client
from agent_service.web.hooks import router as hooks_router
from config import DATA_DIR
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole

logger = logging.getLogger(__name__)

# --- App Lifespan Management ---
mock_users_service_client = AsyncMock()


# --- Context Management for GraphQL ---
async def get_context(
    uow: UnitOfWork = Depends(get_uow),
    current_user: CurrentUser = Depends(get_current_user),
):
    mock_users_service_client.get_user_roles.return_value = [
        UserRole(role="coach", domain="coaching"),
        UserRole(role="user", domain="coaching"),
    ]
    return {"uow": uow, "current_user": current_user}


GraphQLContext = dict


@strawberry.type
class Query:
    @strawberry.field
    def ask(self, query: str, tradition: str = "canon-default") -> str:
        """Answers a question using the underlying RAG chain for a specific tradition."""
        engine = get_qdrant_engine_for_tradition(tradition)
        if not engine:
            return f"Sorry, the knowledge base for the tradition '{tradition}' has not been built."
        return engine.ask(query)

    @strawberry.field
    def list_traditions(self) -> list[str]:
        """Lists all available knowledge base traditions."""
        repo = TraditionRepository()
        service = TraditionService(repo)
        return service.list_traditions()

    @strawberry.field
    async def get_meal_suggestion(
        self, info: Info[GraphQLContext, None], meal_type: str, tradition: str
    ) -> MealSuggestion:
        """Generates a meal suggestion for the authenticated user based on their goals and recent activity."""
        # This will be refactored to call the journal service via its API
        # instead of accessing its repository directly. For now, it's disabled.
        raise NotImplementedError("Journal service communication not yet implemented.")

    @strawberry.field
    async def summarize_journals(
        self, info: Info[GraphQLContext, None]
    ) -> JournalSummary:
        """
        Generates a summary of the user's journal entries from the last 3 days.
        """
        current_user = info.context["current_user"]
        journal_client = JournalClient()
        llm_service = LLMService()

        try:
            # 1. Fetch journal entries from the last 3 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=3)

            entries = await journal_client.list_by_user_for_period(
                user_id=str(current_user.id),
                start_date=start_date,
                end_date=end_date,
            )
            
            # Convert model instances to dictionaries for the LLM service
            entry_dicts = [entry.model_dump() for entry in entries]

            # 2. Generate summary using the LLM service
            summary_text = await llm_service.get_journal_summary(entry_dicts)

            # 3. Return the summary in the specified GraphQL type
            return JournalSummary(
                summary=summary_text,
                generated_at=datetime.now(timezone.utc)
            )

        except Exception as e:
            logger.error(f"Failed to summarize journals for user {current_user.id}: {e}")
            return JournalSummary(
                summary="An error occurred while generating your summary. Please try again later.",
                generated_at=datetime.now(timezone.utc),
            )

    @strawberry.field
    async def semantic_search(
        self,
        info: Info[GraphQLContext, None],
        query: str,
        tradition: str = "canon-default",
        include_personal: bool = True,
        include_knowledge: bool = True,
        entry_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[str]:
        """Performs semantic search across knowledge base and personal journal entries."""
        current_user = info.context["current_user"]

        try:
            query_embedding = await get_embedding(query)
            if not query_embedding:
                return []

            qdrant_client = get_qdrant_client()
            search_results = await qdrant_client.hybrid_search(
                query=query,
                user_id=str(current_user.id),
                tradition=tradition,
                query_embedding=query_embedding,
                include_personal=include_personal,
                include_knowledge=include_knowledge,
                entry_types=entry_types,
                limit=limit,
            )

            return [result.text for result in search_results]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def generate_review(
        self, info: Info[GraphQLContext, None], tradition: str
    ) -> PerformanceReview:
        """
        Generates a bi-weekly performance review for the authenticated user.
        """
        current_user = info.context["current_user"]
        qdrant_client = get_qdrant_client()
        llm_service = LLMService()

        try:
            # 1. Define date range for the last 14 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=14)

            # 2. Use a general query to find relevant entries via semantic search
            search_query = "A review of my personal growth, successes, challenges, and areas for improvement."
            query_embedding = await get_embedding(search_query)

            if not query_embedding:
                raise ValueError("Failed to generate embedding for search query.")

            # 3. Fetch relevant journal entries from Qdrant within the date range
            search_results = await qdrant_client.search_personal_documents_by_date(
                user_id=str(current_user.id),
                tradition=tradition,
                query_embedding=query_embedding,
                start_date=start_date,
                end_date=end_date,
                limit=25,  # Fetch a good number of entries for context
            )
            
            # Convert search results to dictionaries for the LLM service
            entry_dicts = [result.__dict__ for result in search_results]

            # 4. Generate the structured review using the LLM service
            review = await llm_service.generate_performance_review(entry_dicts)
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

    @strawberry.mutation
    def upload_document(
        self,
        file_name: str,
        content: strawberry.scalars.Base64,
        tradition: str = "canon-default",
    ) -> bool:
        """
        Uploads a new document to the knowledge base for a specific tradition.
        """
        # This functionality will be moved to the ingestion service pipeline
        # and triggered by a webhook, not a direct GraphQL mutation.
        raise NotImplementedError(
            "Document upload is now handled by the GCS ingestion pipeline."
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, graphiql=True, context_getter=get_context)

app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agent-service"}


app.include_router(graphql_app, prefix="/graphql")
app.include_router(hooks_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
