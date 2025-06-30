import strawberry
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from ..types.journal_types import (
    JournalEntryInterface,
    GratitudeJournalEntry,
    ReflectionJournalEntry,
    FreeformJournalEntry,
    GratitudeEntryInput,
    ReflectionEntryInput,
    FreeformEntryInput,
    GratitudePayloadType,
    ReflectionPayloadType,
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
    ) -> List[JournalEntryInterface]:
        """Get journal entries for the current user."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        entries = await service.get_entries_for_user(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
        )
        
        # Convert service responses to proper GraphQL types
        result = []
        for entry in entries:
            if entry.entry_type == "GRATITUDE":
                payload = GratitudePayloadType(**entry.payload)
                result.append(GratitudeJournalEntry(
                    id=str(entry.id),
                    userId=str(entry.user_id),
                    entryType=entry.entry_type,
                    createdAt=entry.created_at,
                    modifiedAt=entry.modified_at,
                    payload=payload
                ))
            elif entry.entry_type == "REFLECTION":
                payload = ReflectionPayloadType(**entry.payload)
                result.append(ReflectionJournalEntry(
                    id=str(entry.id),
                    userId=str(entry.user_id),
                    entryType=entry.entry_type,
                    createdAt=entry.created_at,
                    modifiedAt=entry.modified_at,
                    payload=payload
                ))
            elif entry.entry_type == "FREEFORM":
                result.append(FreeformJournalEntry(
                    id=str(entry.id),
                    userId=str(entry.user_id),
                    entryType=entry.entry_type,
                    createdAt=entry.created_at,
                    modifiedAt=entry.modified_at,
                    payload=entry.payload["content"]
                ))
        
        return result

    @strawberry.field
    async def journal_entry(
        self,
        info,
        entry_id: UUID,
    ) -> Optional[JournalEntryInterface]:
        """Get a specific journal entry by ID."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        entry = await service.get_entry(
            entry_id=entry_id,
            user_id=str(current_user.id),
        )
        if not entry:
            return None
            
        # Convert to proper GraphQL type
        if entry.entry_type == "GRATITUDE":
            payload = GratitudePayloadType(**entry.payload)
            return GratitudeJournalEntry(
                id=str(entry.id),
                userId=str(entry.user_id),
                entryType=entry.entry_type,
                createdAt=entry.created_at,
                modifiedAt=entry.modified_at,
                payload=payload
            )
        elif entry.entry_type == "REFLECTION":
            payload = ReflectionPayloadType(**entry.payload)
            return ReflectionJournalEntry(
                id=str(entry.id),
                userId=str(entry.user_id),
                entryType=entry.entry_type,
                createdAt=entry.created_at,
                modifiedAt=entry.modified_at,
                payload=payload
            )
        elif entry.entry_type == "FREEFORM":
            return FreeformJournalEntry(
                id=str(entry.id),
                userId=str(entry.user_id),
                entryType=entry.entry_type,
                createdAt=entry.created_at,
                modifiedAt=entry.modified_at,
                payload=entry.payload["content"]
            )
        return None

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
        entries = await service.get_entries_for_user(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
        )
        
        # Filter for gratitude entries and convert to GraphQL types
        result = []
        for entry in entries:
            if entry.entry_type == "GRATITUDE":
                payload = GratitudePayloadType(**entry.payload)
                result.append(GratitudeJournalEntry(
                    id=str(entry.id),
                    userId=str(entry.user_id),
                    entryType=entry.entry_type,
                    createdAt=entry.created_at,
                    modifiedAt=entry.modified_at,
                    payload=payload
                ))
        return result

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
        entries = await service.get_entries_for_user(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
        )
        
        # Filter for reflection entries and convert to GraphQL types
        result = []
        for entry in entries:
            if entry.entry_type == "REFLECTION":
                payload = ReflectionPayloadType(**entry.payload)
                result.append(ReflectionJournalEntry(
                    id=str(entry.id),
                    userId=str(entry.user_id),
                    entryType=entry.entry_type,
                    createdAt=entry.created_at,
                    modifiedAt=entry.modified_at,
                    payload=payload
                ))
        return result

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
        entries = await service.get_entries_for_user(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
        )
        
        # Filter for freeform entries and convert to GraphQL types
        result = []
        for entry in entries:
            if entry.entry_type == "FREEFORM":
                result.append(FreeformJournalEntry(
                    id=str(entry.id),
                    userId=str(entry.user_id),
                    entryType=entry.entry_type,
                    createdAt=entry.created_at,
                    modifiedAt=entry.modified_at,
                    payload=entry.payload["content"]
                ))
        return result


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def createGratitudeJournalEntry(
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
            gratefulFor=input.gratefulFor,
            excitedAbout=input.excitedAbout,
            focus=input.focus,
            affirmation=input.affirmation,
            mood=input.mood,
        )
        await session.commit()
        
        # Convert service response to GraphQL type with proper field mapping
        payload = GratitudePayloadType(**entry.payload)
        return GratitudeJournalEntry(
            id=str(entry.id),
            userId=str(entry.user_id),
            entryType=entry.entry_type,
            createdAt=entry.created_at,
            modifiedAt=entry.modified_at,
            payload=payload
        )

    @strawberry.mutation
    async def createReflectionJournalEntry(
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
            wins=input.wins,
            improvements=input.improvements,
            mood=input.mood,
        )
        await session.commit()
        
        # Convert service response to GraphQL type with proper field mapping
        payload = ReflectionPayloadType(**entry.payload)
        return ReflectionJournalEntry(
            id=str(entry.id),
            userId=str(entry.user_id),
            entryType=entry.entry_type,
            createdAt=entry.created_at,
            modifiedAt=entry.modified_at,
            payload=payload
        )

    @strawberry.mutation
    async def createFreeformJournalEntry(
        self,
        info,
        input: FreeformEntryInput,
    ) -> FreeformJournalEntry:
        """Create a new freeform journal entry."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        session = get_session_from_context(info)
        
        entry = await service.create_freeform_entry(
            user=current_user,
            content=input.content,
        )
        await session.commit()
        return FreeformJournalEntry(
            id=str(entry.id),
            userId=str(entry.user_id),
            entryType=entry.entry_type,
            createdAt=entry.created_at,
            modifiedAt=entry.modified_at,
            payload=entry.payload["content"]
        )

    @strawberry.mutation
    async def deleteJournalEntry(
        self,
        info,
        entry_id: UUID,
    ) -> bool:
        """Delete a journal entry."""
        current_user = get_current_user_from_context(info)
        service = get_journal_service_from_context(info)
        session = get_session_from_context(info)
        
        success = await service.delete_entry(
            entry_id=entry_id,
            user_id=str(current_user.id),
        )
        if success:
            await session.commit()
        return success


# Create the main schema
schema = strawberry.Schema(query=Query, mutation=Mutation) 