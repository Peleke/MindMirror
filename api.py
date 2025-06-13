import base64
import logging
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
from src.web.hooks import router as hooks_router

logger = logging.getLogger(__name__)

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

    @strawberry.field
    async def semantic_search(
        self, 
        info: Info[GraphQLContext, None], 
        query: str,
        tradition: str = "canon-default",
        include_personal: bool = True,
        include_knowledge: bool = True,
        entry_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[str]:
        """Performs semantic search across knowledge base and personal journal entries."""
        from src.vector_stores.qdrant_client import get_qdrant_client
        from src.embedding import get_embedding
        
        current_user = info.context["current_user"]
        
        try:
            # Generate embedding for the search query
            query_embedding = await get_embedding(query)
            if not query_embedding:
                return []
            
            # Get Qdrant client and perform hybrid search
            qdrant_client = get_qdrant_client()
            search_results = await qdrant_client.hybrid_search(
                query=query,
                user_id=str(current_user.id),
                tradition=tradition,
                query_embedding=query_embedding,
                include_personal=include_personal,
                include_knowledge=include_knowledge,
                entry_types=entry_types,
                limit=limit
            )
            
            # Return the text content from search results
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
                # Clean up the response text
                cleaned_text = review_text.strip()
                
                # Initialize default values
                key_success = "Your progress shows positive momentum - keep building on your current habits."
                improvement_area = "Focus on consistency in your daily practices to maximize long-term growth."
                journal_prompt = "What one small change could you make this week to move closer to your goals?"

                # Strategy 1: Look for bold markdown headers (most specific)
                import re
                
                # Patterns to match the sections with various formatting
                patterns = {
                    'key_success': [
                        r'\*\*Key Success:?\*\*\s*(.+?)(?=\*\*|\n\n|\Z)',
                        r'Key Success:?\s*(.+?)(?=\n(?:Area|Journal|\*\*)|$)',
                        r'\*\*Success:?\*\*\s*(.+?)(?=\*\*|\n\n|\Z)',
                        r'Success:?\s*(.+?)(?=\n(?:Area|Journal|\*\*)|$)'
                    ],
                    'improvement_area': [
                        r'\*\*Area for Improvement:?\*\*\s*(.+?)(?=\*\*|\n\n|\Z)',
                        r'Area for Improvement:?\s*(.+?)(?=\n(?:Journal|\*\*)|$)',
                        r'\*\*Improvement:?\*\*\s*(.+?)(?=\*\*|\n\n|\Z)',
                        r'Improvement:?\s*(.+?)(?=\n(?:Journal|\*\*)|$)'
                    ],
                    'journal_prompt': [
                        r'\*\*Journal Prompt:?\*\*\s*(.+?)(?=\*\*|\n\n|\Z)',
                        r'Journal Prompt:?\s*(.+?)(?=\n|\Z)',
                        r'\*\*Prompt:?\*\*\s*(.+?)(?=\*\*|\n\n|\Z)',
                        r'Prompt:?\s*(.+?)(?=\n|\Z)'
                    ]
                }
                
                # Try to extract each section using regex patterns
                for section, section_patterns in patterns.items():
                    for pattern in section_patterns:
                        match = re.search(pattern, cleaned_text, re.IGNORECASE | re.DOTALL)
                        if match:
                            extracted_text = match.group(1).strip()
                            # Clean up the extracted text
                            extracted_text = re.sub(r'\*+', '', extracted_text)  # Remove asterisks
                            extracted_text = extracted_text.replace('\n', ' ')  # Replace newlines with spaces
                            extracted_text = re.sub(r'\s+', ' ', extracted_text)  # Normalize whitespace
                            
                            if len(extracted_text) > 10:  # Only use if it's substantial
                                if section == 'key_success':
                                    key_success = extracted_text
                                elif section == 'improvement_area':
                                    improvement_area = extracted_text
                                elif section == 'journal_prompt':
                                    journal_prompt = extracted_text
                                break  # Found a match for this section, stop trying patterns
                
                # Strategy 2: If regex failed, try line-by-line parsing
                if (key_success == "Your progress shows positive momentum - keep building on your current habits." or 
                    improvement_area == "Focus on consistency in your daily practices to maximize long-term growth." or 
                    journal_prompt == "What one small change could you make this week to move closer to your goals?"):
                    
                    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
                    
                    current_section = None
                    section_content = []
                    
                    for line in lines:
                        line_lower = line.lower()
                        
                        # Check for section headers
                        if any(keyword in line_lower for keyword in ['key success', 'success:']):
                            # Save previous section if any
                            if current_section and section_content:
                                content = ' '.join(section_content).strip()
                                content = re.sub(r'\*+', '', content)
                                if len(content) > 10:
                                    if current_section == 'key_success':
                                        key_success = content
                                    elif current_section == 'improvement_area':
                                        improvement_area = content
                                    elif current_section == 'journal_prompt':
                                        journal_prompt = content
                            
                            current_section = 'key_success'
                            section_content = []
                            # Extract content after colon if present
                            if ':' in line:
                                after_colon = line.split(':', 1)[1].strip()
                                after_colon = re.sub(r'\*+', '', after_colon)
                                if after_colon:
                                    section_content.append(after_colon)
                                    
                        elif any(keyword in line_lower for keyword in ['area for improvement', 'improvement:']):
                            # Save previous section
                            if current_section and section_content:
                                content = ' '.join(section_content).strip()
                                content = re.sub(r'\*+', '', content)
                                if len(content) > 10:
                                    if current_section == 'key_success':
                                        key_success = content
                                    elif current_section == 'improvement_area':
                                        improvement_area = content
                                    elif current_section == 'journal_prompt':
                                        journal_prompt = content
                            
                            current_section = 'improvement_area'
                            section_content = []
                            if ':' in line:
                                after_colon = line.split(':', 1)[1].strip()
                                after_colon = re.sub(r'\*+', '', after_colon)
                                if after_colon:
                                    section_content.append(after_colon)
                                    
                        elif any(keyword in line_lower for keyword in ['journal prompt', 'prompt:']):
                            # Save previous section
                            if current_section and section_content:
                                content = ' '.join(section_content).strip()
                                content = re.sub(r'\*+', '', content)
                                if len(content) > 10:
                                    if current_section == 'key_success':
                                        key_success = content
                                    elif current_section == 'improvement_area':
                                        improvement_area = content
                                    elif current_section == 'journal_prompt':
                                        journal_prompt = content
                            
                            current_section = 'journal_prompt'
                            section_content = []
                            if ':' in line:
                                after_colon = line.split(':', 1)[1].strip()
                                after_colon = re.sub(r'\*+', '', after_colon)
                                if after_colon:
                                    section_content.append(after_colon)
                                    
                        else:
                            # This is content for the current section
                            if current_section and line and not line.startswith('#'):
                                cleaned_line = re.sub(r'\*+', '', line)
                                if cleaned_line.strip():
                                    section_content.append(cleaned_line.strip())
                    
                    # Don't forget the last section
                    if current_section and section_content:
                        content = ' '.join(section_content).strip()
                        content = re.sub(r'\*+', '', content)
                        if len(content) > 10:
                            if current_section == 'key_success':
                                key_success = content
                            elif current_section == 'improvement_area':
                                improvement_area = content
                            elif current_section == 'journal_prompt':
                                journal_prompt = content

                # Strategy 3: Last resort - use the first few lines if structured parsing failed
                if (key_success == "Your progress shows positive momentum - keep building on your current habits." and
                    len(lines) >= 3):
                    
                    # Simple fallback: assume first 3 non-empty lines are the sections
                    try:
                        meaningful_lines = [line for line in lines if len(line) > 20]  # Filter out short lines
                        if len(meaningful_lines) >= 3:
                            key_success = re.sub(r'\*+', '', meaningful_lines[0]).strip()
                            improvement_area = re.sub(r'\*+', '', meaningful_lines[1]).strip()
                            journal_prompt = re.sub(r'\*+', '', meaningful_lines[2]).strip()
                            
                            # Remove section labels if they were included
                            key_success = re.sub(r'^(Key Success|Success):\s*', '', key_success, flags=re.IGNORECASE)
                            improvement_area = re.sub(r'^(Area for Improvement|Improvement):\s*', '', improvement_area, flags=re.IGNORECASE)
                            journal_prompt = re.sub(r'^(Journal Prompt|Prompt):\s*', '', journal_prompt, flags=re.IGNORECASE)
                    except Exception:
                        pass  # Keep the defaults

                # Final cleanup
                key_success = key_success[:300] if len(key_success) > 300 else key_success
                improvement_area = improvement_area[:300] if len(improvement_area) > 300 else improvement_area
                journal_prompt = journal_prompt[:200] if len(journal_prompt) > 200 else journal_prompt

                # Debug output
                print("=== DEBUG: Final Parsed Sections ===")
                print(f"Key Success: {repr(key_success)}")
                print(f"Improvement Area: {repr(improvement_area)}")
                print(f"Journal Prompt: {repr(journal_prompt)}")
                print("=== END FINAL DEBUG ===")

                return PerformanceReview(
                    key_success=key_success,
                    improvement_area=improvement_area,
                    journal_prompt=journal_prompt,
                )

            except Exception as parsing_error:
                print(f"ERROR during parsing: {type(parsing_error).__name__}: {parsing_error}")
                import traceback
                traceback.print_exc()
                
                # Ultimate fallback with meaningful defaults
                return PerformanceReview(
                    key_success="Your recent activities show positive engagement with your health journey.",
                    improvement_area="Consider focusing on consistency in your daily practices for better long-term results.",
                    journal_prompt="What is one habit you could improve this week to better support your goals?",
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
            
            # Queue indexing task after successful creation
            try:
                from src.tasks import queue_journal_entry_indexing
                queue_journal_entry_indexing(
                    entry_id=str(new_entry.id),
                    user_id=str(current_user.id),
                    tradition="canon-default"  # Default tradition
                )
                logger.info(f"Queued indexing for freeform entry {new_entry.id}")
            except Exception as e:
                logger.error(f"Failed to queue indexing for entry {new_entry.id}: {e}")
                # Don't fail the mutation if indexing fails
            
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
            
            # Queue indexing task after successful creation
            try:
                from src.tasks import queue_journal_entry_indexing
                queue_journal_entry_indexing(
                    entry_id=str(new_entry.id),
                    user_id=str(current_user.id),
                    tradition="canon-default"  # Default tradition
                )
                logger.info(f"Queued indexing for gratitude entry {new_entry.id}")
            except Exception as e:
                logger.error(f"Failed to queue indexing for entry {new_entry.id}: {e}")
                # Don't fail the mutation if indexing fails
            
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
            
            # Queue indexing task after successful creation
            try:
                from src.tasks import queue_journal_entry_indexing
                queue_journal_entry_indexing(
                    entry_id=str(new_entry.id),
                    user_id=str(current_user.id),
                    tradition="canon-default"  # Default tradition
                )
                logger.info(f"Queued indexing for reflection entry {new_entry.id}")
            except Exception as e:
                logger.error(f"Failed to queue indexing for entry {new_entry.id}: {e}")
                # Don't fail the mutation if indexing fails
            
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
app.include_router(hooks_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
