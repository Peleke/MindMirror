import base64
import os
from contextlib import asynccontextmanager
from typing import List, Optional
from unittest.mock import AsyncMock, patch
from uuid import UUID

import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from config import DATA_DIR
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole
from src.api.types.journal_types import (FreeformEntryInput,
                                         FreeformJournalEntry,
                                         GratitudeEntryInput,
                                         GratitudeJournalEntry,
                                         GratitudePayloadType,
                                         JournalEntryType,
                                         ReflectionEntryInput,
                                         ReflectionJournalEntry,
                                         ReflectionPayloadType)
from src.api.types.suggestion_types import MealSuggestion, PerformanceReview
from src.clients.history_client import HistoryClient
from src.clients.users_client import UsersClient
from src.database import get_session, init_db
from src.engine import get_engine_for_tradition
from src.models.journal import GratitudePayload, ReflectionPayload
from src.repositories.journal_repository import JournalRepository
from src.repositories.tradition_repository import TraditionRepository
from src.services.journal_service import JournalService
from src.services.suggestion_service import SuggestionService
from src.services.tradition_service import TraditionService
from src.uow import UnitOfWork, get_uow

# --- App Lifespan Management ---

# Create a mock for the users service client that is used by the shared auth logic
mock_users_service_client = AsyncMock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup, patch the real client with our mock
    with patch("shared.auth.users_service_client", new=mock_users_service_client):
        print("Initializing database...")
        await init_db()
        print("Database initialization complete. User service client patched.")
        yield
    # On shutdown
    print("Application shutting down.")


# --- Context Management for GraphQL ---
async def get_context(
    uow: UnitOfWork = Depends(get_uow),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Creates a GraphQL context for each request.
    Injects the UnitOfWork and the authenticated user.
    """
    # Simulate the roles that would be returned by the real users_service
    mock_users_service_client.get_user_roles.return_value = [
        UserRole(role="coach", domain="coaching"),
        UserRole(role="user", domain="coaching"),
    ]
    return {"uow": uow, "current_user": current_user}


# Type hint for the GraphQL context
GraphQLContext = dict

# --- Engine Cache ---
# This has been moved to src/engine.py to resolve a circular import.
# The `get_engine_for_tradition` function is now imported from there.


@strawberry.type
class Query:
    @strawberry.field
    def ask(self, query: str, tradition: str = "canon-default") -> str:
        """Answers a question using the underlying RAG chain for a specific tradition."""
        engine = get_engine_for_tradition(tradition)
        if not engine:
            return f"Sorry, the knowledge base for the tradition '{tradition}' has not been built."
        return engine.ask(query)

    @strawberry.field
    def list_traditions(self) -> list[str]:
        """Lists all available knowledge base traditions."""
        # This now uses the service and repository layers
        repo = TraditionRepository()
        service = TraditionService(repo)
        return service.list_traditions()

    @strawberry.field
    async def journal_entries(
        self, info: Info[GraphQLContext, None]
    ) -> list[JournalEntryType]:
        """Retrieves all journal entries for the authenticated user."""
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]
        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)
            entries = await service.get_entries_for_user(str(current_user.id))

            # Convert Pydantic models to Strawberry types based on entry_type
            result = []
            for entry in entries:
                if entry.entry_type == "GRATITUDE":
                    payload = GratitudePayloadType(**entry.payload.model_dump())
                    result.append(
                        GratitudeJournalEntry(
                            id=str(entry.id),
                            user_id=str(entry.user_id),
                            payload=payload,
                            created_at=entry.created_at,
                            modified_at=entry.modified_at,
                        )
                    )
                elif entry.entry_type == "REFLECTION":
                    payload = ReflectionPayloadType(**entry.payload.model_dump())
                    result.append(
                        ReflectionJournalEntry(
                            id=str(entry.id),
                            user_id=str(entry.user_id),
                            payload=payload,
                            created_at=entry.created_at,
                            modified_at=entry.modified_at,
                        )
                    )
                else:  # FREEFORM
                    result.append(
                        FreeformJournalEntry(
                            id=str(entry.id),
                            user_id=str(entry.user_id),
                            payload=entry.payload,
                            created_at=entry.created_at,
                            modified_at=entry.modified_at,
                        )
                    )
            return result

    @strawberry.field
    async def journal_entry_exists_today(
        self, info: Info[GraphQLContext, None], entry_type: str
    ) -> bool:
        """Checks if a journal entry of a specific type exists for the authenticated user today."""
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]
        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)
            return await service.check_for_entry_today(str(current_user.id), entry_type)

    @strawberry.field
    async def get_meal_suggestion(
        self, info: Info[GraphQLContext, None], meal_type: str, tradition: str
    ) -> MealSuggestion:
        """Generates a meal suggestion for the authenticated user based on their goals and recent activity."""
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]

        engine = get_engine_for_tradition(tradition)
        users_client = UsersClient()
        history_client = HistoryClient()

        async with uow:
            journal_repo = JournalRepository(uow.session)

            service = SuggestionService(
                users_client=users_client,
                history_client=history_client,
                journal_repo=journal_repo,
                engine=engine,
            )

            suggestion_text = await service.get_meal_suggestion(
                current_user, tradition, meal_type
            )
            return MealSuggestion(suggestion=suggestion_text)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def generate_review(
        self, info: Info[GraphQLContext, None], tradition: str
    ) -> PerformanceReview:
        """
        Generates a bi-weekly performance review for the authenticated user.
        """
        try:
            uow: UnitOfWork = info.context["uow"]
            current_user = info.context["current_user"]

            engine = get_engine_for_tradition(tradition)
            if not engine:
                print(f"ERROR: Failed to get engine for tradition '{tradition}'")
                raise ValueError(
                    f"Knowledge base for tradition '{tradition}' is not available"
                )

            users_client = UsersClient()
            history_client = HistoryClient()

            # 2. Instantiate the service with UoW
            async with uow:
                journal_repo = JournalRepository(uow.session)
                service = SuggestionService(
                    users_client=users_client,
                    history_client=history_client,
                    journal_repo=journal_repo,
                    engine=engine,
                )

                print(
                    f"Generating review for user {current_user.id} with tradition {tradition}"
                )
                review_text = await service.generate_biweekly_review(
                    current_user, tradition
                )

            if not review_text or not review_text.strip():
                print("ERROR: Empty response from LLM")
                raise ValueError("Received empty response from language model")

            # Debug logging to see what Ollama is actually returning
            print("=== DEBUG: Raw LLM Response ===")
            print(repr(review_text))
            print("=== END DEBUG ===")

            # Improved parsing that can handle various formats
            try:
                lines = [
                    line.strip() for line in review_text.split("\n") if line.strip()
                ]

                # Try to extract structured data from various formats
                key_success = "Unable to identify key success."
                improvement_area = "Unable to identify improvement area."
                journal_prompt = "Reflect on your recent progress and set an intention for the week ahead."

                # Parse the response looking for the sections
                current_section = None
                section_content = []

                for line in lines:
                    lower_line = line.lower()

                    # Check if this line is a section header
                    if any(
                        keyword in lower_line
                        for keyword in ["**key success", "key success:", "**success"]
                    ):
                        if current_section and section_content:
                            # Save previous section
                            content = " ".join(section_content).strip()
                            if current_section == "key_success":
                                key_success = content
                            elif current_section == "improvement":
                                improvement_area = content
                            elif current_section == "journal":
                                journal_prompt = content
                        current_section = "key_success"
                        section_content = []
                        # Extract content after the colon if present
                        if ":" in line:
                            content_after_colon = line.split(":", 1)[1].strip()
                            if content_after_colon:
                                section_content.append(content_after_colon)
                    elif any(
                        keyword in lower_line
                        for keyword in [
                            "**area for improvement",
                            "area for improvement:",
                            "improvement:",
                        ]
                    ):
                        if current_section and section_content:
                            # Save previous section
                            content = " ".join(section_content).strip()
                            if current_section == "key_success":
                                key_success = content
                            elif current_section == "improvement":
                                improvement_area = content
                            elif current_section == "journal":
                                journal_prompt = content
                        current_section = "improvement"
                        section_content = []
                        # Extract content after the colon if present
                        if ":" in line:
                            content_after_colon = line.split(":", 1)[1].strip()
                            if content_after_colon:
                                section_content.append(content_after_colon)
                    elif any(
                        keyword in lower_line
                        for keyword in [
                            "**journal prompt",
                            "journal prompt:",
                            "**prompt",
                        ]
                    ):
                        if current_section and section_content:
                            # Save previous section
                            content = " ".join(section_content).strip()
                            if current_section == "key_success":
                                key_success = content
                            elif current_section == "improvement":
                                improvement_area = content
                            elif current_section == "journal":
                                journal_prompt = content
                        current_section = "journal"
                        section_content = []
                        # Extract content after the colon if present
                        if ":" in line:
                            content_after_colon = line.split(":", 1)[1].strip()
                            if content_after_colon:
                                section_content.append(content_after_colon)
                    else:
                        # This is content for the current section
                        if current_section and line and not line.startswith("**"):
                            section_content.append(line)

                # Don't forget to save the last section
                if current_section and section_content:
                    content = " ".join(section_content).strip()
                    if current_section == "key_success":
                        key_success = content
                    elif current_section == "improvement":
                        improvement_area = content
                    elif current_section == "journal":
                        journal_prompt = content

                # Clean up the extracted content (remove markdown formatting)
                key_success = key_success.replace("**", "").strip()
                improvement_area = improvement_area.replace("**", "").strip()
                journal_prompt = journal_prompt.replace("**", "").strip()

                # Debug output to see what was parsed
                print("=== DEBUG: Parsed Sections ===")
                print(f"Key Success: {repr(key_success)}")
                print(f"Improvement Area: {repr(improvement_area)}")
                print(f"Journal Prompt: {repr(journal_prompt)}")
                print("=== END PARSED DEBUG ===")

                # If we still couldn't parse properly, try a fallback approach
                if key_success == "Unable to identify key success." and len(lines) >= 3:
                    # Try the original rigid parsing as fallback
                    try:
                        key_success = (
                            lines[0].split(":", 1)[1].strip()
                            if ":" in lines[0]
                            else lines[0]
                        )
                        improvement_area = (
                            lines[1].split(":", 1)[1].strip()
                            if ":" in lines[1]
                            else lines[1]
                        )
                        journal_prompt = (
                            lines[2].split(":", 1)[1].strip()
                            if ":" in lines[2]
                            else lines[2]
                        )
                        print("Used fallback parsing")
                    except Exception as fallback_error:
                        # If all else fails, just use the raw text as context
                        print(f"Fallback parsing failed: {fallback_error}")
                        key_success = (
                            "Review generated - see full response for details."
                        )
                        improvement_area = (
                            review_text[:200] + "..."
                            if len(review_text) > 200
                            else review_text
                        )
                        journal_prompt = (
                            "Reflect on the insights shared in your review."
                        )

                return PerformanceReview(
                    key_success=key_success,
                    improvement_area=improvement_area,
                    journal_prompt=journal_prompt,
                )

            except Exception as parsing_error:
                print(
                    f"ERROR during parsing: {type(parsing_error).__name__}: {parsing_error}"
                )
                print(f"Raw review text length: {len(review_text)}")
                # Fallback for when parsing completely fails
                return PerformanceReview(
                    key_success="Review generated successfully - check logs for details.",
                    improvement_area="See raw response for improvement suggestions.",
                    journal_prompt="Reflect on your recent progress and set intentions for the week ahead.",
                )

        except Exception as outer_error:
            print(
                f"ERROR in generate_review: {type(outer_error).__name__}: {outer_error}"
            )
            import traceback

            traceback.print_exc()
            # Re-raise with more context
            raise RuntimeError(
                f"Failed to generate review: {str(outer_error)}"
            ) from outer_error

    @strawberry.mutation
    async def create_freeform_journal_entry(
        self, info: Info[GraphQLContext, None], input: FreeformEntryInput
    ) -> FreeformJournalEntry:
        """Creates a new freeform journal entry."""
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]

        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)

            new_entry = await service.create_freeform_entry(
                current_user=current_user, content=input.content
            )
            return FreeformJournalEntry(
                id=str(new_entry.id),
                user_id=str(new_entry.user_id),
                payload=new_entry.payload,
                created_at=new_entry.created_at,
                modified_at=new_entry.modified_at,
            )

    @strawberry.mutation
    async def create_gratitude_journal_entry(
        self, info: Info[GraphQLContext, None], input: GratitudeEntryInput
    ) -> GratitudeJournalEntry:
        """Creates a new structured gratitude journal entry."""
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]

        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)

            # Explicitly create the payload to avoid passing the user_id from the input
            payload = GratitudePayload(
                grateful_for=input.grateful_for,
                excited_about=input.excited_about,
                focus=input.focus,
                affirmation=input.affirmation,
                mood=input.mood,
            )

            new_entry = await service.create_gratitude_entry(
                current_user=current_user, payload=payload
            )
            graphql_payload = GratitudePayloadType(**new_entry.payload.model_dump())
            return GratitudeJournalEntry(
                id=str(new_entry.id),
                user_id=str(new_entry.user_id),
                payload=graphql_payload,
                created_at=new_entry.created_at,
                modified_at=new_entry.modified_at,
            )

    @strawberry.mutation
    async def create_reflection_journal_entry(
        self, info: Info[GraphQLContext, None], input: ReflectionEntryInput
    ) -> ReflectionJournalEntry:
        """Creates a new structured reflection journal entry."""
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]

        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)

            # Explicitly create the payload
            payload = ReflectionPayload(
                wins=input.wins,
                improvements=input.improvements,
                mood=input.mood,
            )

            new_entry = await service.create_reflection_entry(
                current_user=current_user, payload=payload
            )
            graphql_payload = ReflectionPayloadType(**new_entry.payload.model_dump())
            return ReflectionJournalEntry(
                id=str(new_entry.id),
                user_id=str(new_entry.user_id),
                payload=graphql_payload,
                created_at=new_entry.created_at,
                modified_at=new_entry.modified_at,
            )

    @strawberry.mutation
    async def delete_journal_entry(
        self, info: Info[GraphQLContext, None], entry_id: str
    ) -> bool:
        """Deletes a journal entry."""
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)
            return await service.delete_entry(entry_id)

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
        try:
            # Construct the path within the specific tradition's PDF directory
            tradition_pdf_dir = os.path.join("pdfs", tradition)
            os.makedirs(tradition_pdf_dir, exist_ok=True)

            file_path = os.path.join(tradition_pdf_dir, file_name)

            # Decode the Base64 content
            file_content = base64.b64decode(content)

            with open(file_path, "wb") as f:
                f.write(file_content)

            # NOTE: In a production system, you would not block the API to rebuild.
            # You would trigger a background worker task.
            print(
                f"Document '{file_name}' uploaded to tradition '{tradition}'. Rebuilding knowledge base..."
            )
            from src.data_processing import build_knowledge_base

            build_knowledge_base()  # Rebuild all traditions for simplicity in PoC

            # Clear the engine cache so it reloads on next request
            from src.engine import engine_cache

            if tradition in engine_cache:
                del engine_cache[tradition]

            print("Knowledge base rebuild triggered.")
            return True
        except Exception as e:
            print(f"Error uploading document: {e}")
            return False


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema, graphiql=True, context_getter=get_context)

app = FastAPI(lifespan=lifespan)


# Health check endpoint for Docker
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker containers."""
    return {"status": "healthy", "service": "cyborg-coach-api"}


app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
