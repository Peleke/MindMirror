import logging
from contextlib import asynccontextmanager
from typing import List
from unittest.mock import AsyncMock, patch
from uuid import UUID

import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

# Import the TaskClient for celery-worker communication
from journal_service.clients.task_client import TaskClient
# Imports relative to journal_service
from journal_service.api.types.journal_types import (FreeformEntryInput,
                                                     FreeformJournalEntry,
                                                     GratitudeEntryInput,
                                                     GratitudeJournalEntry,
                                                     GratitudePayloadType,
                                                     JournalEntryType,
                                                     ReflectionEntryInput,
                                                     ReflectionJournalEntry,
                                                     ReflectionPayloadType)
from journal_service.database import init_db
from journal_service.models import GratitudePayload, ReflectionPayload
from journal_service.repository import JournalRepository
from journal_service.service import JournalService
from journal_service.uow import UnitOfWork, get_uow
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole

logger = logging.getLogger(__name__)

# Initialize TaskClient
task_client = TaskClient()

# --- App Lifespan Management ---
mock_users_service_client = AsyncMock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with patch("shared.auth.users_service_client", new=mock_users_service_client):
        print("Initializing Journal Service Database...")
        await init_db()
        print("Database initialization complete.")
        yield
    print("Journal Service shutting down.")


# --- Context Management for GraphQL ---
async def get_context(
    uow: UnitOfWork = Depends(get_uow),
    current_user: CurrentUser = Depends(get_current_user),
):
    mock_users_service_client.get_user_roles.return_value = [
        UserRole(role="user", domain="coaching"),
    ]
    return {"uow": uow, "current_user": current_user}


GraphQLContext = dict


@strawberry.type
class Query:
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


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_freeform_journal_entry(
        self, info: Info[GraphQLContext, None], input: FreeformEntryInput
    ) -> FreeformJournalEntry:
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]
        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)
            new_entry = await service.create_freeform_entry(current_user, input.content)
            await uow.commit()  # Commit to get the ID

        try:
            await task_client.queue_journal_indexing(
                entry_id=str(new_entry.id),
                user_id=str(current_user.id),
            )
            logger.info(f"Queued indexing for freeform entry {new_entry.id}")
        except Exception as e:
            logger.error(f"Failed to queue indexing for entry {new_entry.id}: {e}")

        return FreeformJournalEntry.from_pydantic(new_entry)

    @strawberry.mutation
    async def create_gratitude_journal_entry(
        self, info: Info[GraphQLContext, None], input: GratitudeEntryInput
    ) -> GratitudeJournalEntry:
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]
        payload = GratitudePayload(**input.__dict__)

        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)
            new_entry = await service.create_gratitude_entry(current_user, payload)
            await uow.commit()

        try:
            await task_client.queue_journal_indexing(
                entry_id=str(new_entry.id), user_id=str(current_user.id)
            )
            logger.info(f"Queued indexing for gratitude entry {new_entry.id}")
        except Exception as e:
            logger.error(f"Failed to queue indexing for entry {new_entry.id}: {e}")

        return GratitudeJournalEntry.from_pydantic(new_entry)

    @strawberry.mutation
    async def create_reflection_journal_entry(
        self, info: Info[GraphQLContext, None], input: ReflectionEntryInput
    ) -> ReflectionJournalEntry:
        uow: UnitOfWork = info.context["uow"]
        current_user = info.context["current_user"]
        payload = ReflectionPayload(**input.__dict__)

        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)
            new_entry = await service.create_reflection_entry(current_user, payload)
            await uow.commit()

        try:
            await task_client.queue_journal_indexing(
                entry_id=str(new_entry.id), user_id=str(current_user.id)
            )
            logger.info(f"Queued indexing for reflection entry {new_entry.id}")
        except Exception as e:
            logger.error(f"Failed to queue indexing for entry {new_entry.id}: {e}")

        return ReflectionJournalEntry.from_pydantic(new_entry)

    @strawberry.mutation
    async def delete_journal_entry(
        self, info: Info[GraphQLContext, None], entry_id: str
    ) -> bool:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = JournalRepository(uow.session)
            service = JournalService(repo)
            success = await service.delete_entry(UUID(entry_id))
            await uow.commit()
        return success


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, graphiql=True, context_getter=get_context)

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "journal-service"}


app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
