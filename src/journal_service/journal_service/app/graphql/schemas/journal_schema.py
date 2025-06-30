import strawberry
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from ..types.journal_types import (
    JournalEntryType,
    GratitudeJournalEntry,
    ReflectionJournalEntry,
    FreeformJournalEntry,
    GratitudeEntryInput,
    ReflectionEntryInput,
    FreeformEntryInput,
)
from ..context import (
    GraphQLContext,
    get_current_user_from_context,
    get_journal_service_from_context,
    get_session_from_context,
)


@strawberry.type
class Query:
    @strawberry.field
    async def journal_entries(
        self,
        info,
        entry_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[JournalEntryType]:
        """Get journal entries for the current user."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        entries = await service.get_journal_entries(
            user_id=current_user.id,
            entry_type=entry_type,
            limit=limit,
            offset=offset,
        )
        return entries

    @strawberry.field
    async def journal_entry(
        self,
        info,
        entry_id: UUID,
    ) -> Optional[JournalEntryType]:
        """Get a specific journal entry by ID."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        entry = await service.get_journal_entry(
            entry_id=entry_id,
            user_id=current_user.id,
        )
        return entry

    @strawberry.field
    async def gratitude_entries(
        self,
        info,
        limit: int = 10,
        offset: int = 0,
    ) -> List[GratitudeJournalEntry]:
        """Get gratitude journal entries for the current user."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        entries = await service.get_journal_entries(
            user_id=current_user.id,
            entry_type="gratitude",
            limit=limit,
            offset=offset,
        )
        return [GratitudeJournalEntry(**entry.dict()) for entry in entries]

    @strawberry.field
    async def reflection_entries(
        self,
        info,
        limit: int = 10,
        offset: int = 0,
    ) -> List[ReflectionJournalEntry]:
        """Get reflection journal entries for the current user."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        entries = await service.get_journal_entries(
            user_id=current_user.id,
            entry_type="reflection",
            limit=limit,
            offset=offset,
        )
        return [ReflectionJournalEntry(**entry.dict()) for entry in entries]

    @strawberry.field
    async def freeform_entries(
        self,
        info,
        limit: int = 10,
        offset: int = 0,
    ) -> List[FreeformJournalEntry]:
        """Get freeform journal entries for the current user."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        entries = await service.get_journal_entries(
            user_id=current_user.id,
            entry_type="freeform",
            limit=limit,
            offset=offset,
        )
        return [FreeformJournalEntry(**entry.dict()) for entry in entries]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_gratitude_entry(
        self,
        info,
        input: GratitudeEntryInput,
    ) -> GratitudeJournalEntry:
        """Create a new gratitude journal entry."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        session = get_session_from_context(info)
        
        entry = await service.create_gratitude_entry(
            user_id=current_user.id,
            grateful_for=input.grateful_for,
            impact=input.impact,
            reflection=input.reflection,
        )
        await session.commit()
        return GratitudeJournalEntry(**entry.dict())

    @strawberry.mutation
    async def create_reflection_entry(
        self,
        info,
        input: ReflectionEntryInput,
    ) -> ReflectionJournalEntry:
        """Create a new reflection journal entry."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        session = get_session_from_context(info)
        
        entry = await service.create_reflection_entry(
            user_id=current_user.id,
            prompt=input.prompt,
            response=input.response,
            insights=input.insights,
        )
        await session.commit()
        return ReflectionJournalEntry(**entry.dict())

    @strawberry.mutation
    async def create_freeform_entry(
        self,
        info,
        input: FreeformEntryInput,
    ) -> FreeformJournalEntry:
        """Create a new freeform journal entry."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        session = get_session_from_context(info)
        
        entry = await service.create_freeform_entry(
            user_id=current_user.id,
            content=input.content,
        )
        await session.commit()
        return FreeformJournalEntry(**entry.dict())

    @strawberry.mutation
    async def delete_journal_entry(
        self,
        info,
        entry_id: UUID,
    ) -> bool:
        """Delete a journal entry."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        session = get_session_from_context(info)
        
        success = await service.delete_journal_entry(
            entry_id=entry_id,
            user_id=current_user.id,
        )
        if success:
            await session.commit()
        return success


# Create the main schema
schema = strawberry.Schema(query=Query, mutation=Mutation) 