"""
GraphQL Query Schema

Clean GraphQL query schema with proper separation of concerns and error handling.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import strawberry
from strawberry.types import Info

from ...clients.journal_client import JournalClient
from ...clients.qdrant_client import get_qdrant_client
from ..context import GraphQLContext, get_current_user_from_context
from ..types.suggestion_types import JournalSummary
from ..types.tool_types import ToolMetadata, ToolRegistryHealth
from ...repositories.tradition_repository import TraditionRepository
from ...services.embedding_service import EmbeddingService
from ...services.llm_service import LLMService
from ...services.search_service import SearchService
from ...services.tradition_service import TraditionService

logger = logging.getLogger(__name__)


@strawberry.type
class Query:
    """GraphQL Query schema with all query fields."""

    @strawberry.field
    def ask(
        self,
        info: Info[GraphQLContext, None],
        query: str,
        tradition: str = "canon-default",
    ) -> str:
        """
        Answers a question using the underlying RAG chain for a specific tradition.

        Args:
            query: The question to ask
            tradition: The tradition to use for answering

        Returns:
            str: The answer to the question
        """
        try:
            current_user = get_current_user_from_context(info)

            # Add debug logging
            logger.info(
                f"GraphQL ask() called with tradition: '{tradition}', query: '{query[:100]}...'"
            )

            # Import here to avoid circular imports
            from agent_service.langgraph_.graphs.chat_graph import ChatGraphFactory
            from agent_service.langgraph_.state import StateManager

            # Create chat graph using ProviderManager for LLM selection
            chat_graph_builder = ChatGraphFactory.create_default_chat_graph()

            # Create initial state with user context
            state = StateManager.create_initial_state(
                user_id=str(current_user.id),
                tradition_id=tradition,
                initial_message=query,
            )

            logger.info(
                f"Created state with tradition_id: '{state.get('tradition_id')}'"
            )

            # Build and execute the graph
            chat_graph = chat_graph_builder.get_chat_graph()
            updated_state = chat_graph.invoke(state)

            # Extract response
            response = updated_state.get(
                "last_response", "I apologize, but I couldn't generate a response."
            )

            logger.info(
                f"Final state tradition_id: '{updated_state.get('tradition_id')}', response length: {len(response) if response else 0}"
            )

            return response

        except Exception as e:
            logger.error(f"Error in ask method: {e}")
            return f"Sorry, I encountered an error while processing your question about the tradition '{tradition}'. Please try again."

    @strawberry.field
    def list_traditions(self) -> List[str]:
        """
        Lists all available knowledge base traditions.

        Returns:
            List[str]: List of available traditions
        """
        repo = TraditionRepository()
        service = TraditionService(repo)
        return service.list_traditions()

    @strawberry.field
    async def get_meal_suggestion(
        self, info: Info[GraphQLContext, None], meal_type: str, tradition: str
    ) -> str:
        """
        Generates a meal suggestion for the authenticated user.

        Args:
            info: GraphQL context info
            meal_type: Type of meal to suggest
            tradition: Tradition to use for suggestions

        Returns:
            str: Meal suggestion

        Raises:
            NotImplementedError: Feature not yet implemented
        """
        # This will be refactored to call the journal service via its API
        # instead of accessing its repository directly. For now, it's disabled.
        raise NotImplementedError("Journal service communication not yet implemented.")

    @strawberry.field
    async def summarize_journals(
        self, info: Info[GraphQLContext, None]
    ) -> JournalSummary:
        """
        Generates a summary of the user's journal entries from the last 3 days.

        Args:
            info: GraphQL context info

        Returns:
            JournalSummary: Summary of journal entries

        Raises:
            Exception: If authentication fails or processing fails
        """
        current_user = get_current_user_from_context(info)

        logger.info(f"summarize_journals called for user {current_user.id}")

        journal_client = JournalClient()
        llm_service = LLMService()

        try:
            # 1. Fetch journal entries from the last 3 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=3)

            logger.info(
                f"Fetching journal entries for user {current_user.id} from {start_date} to {end_date}"
            )

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

            # 2. Generate summary using the LLM service
            summary_text = await llm_service.get_journal_summary(entry_dicts)

            logger.info(f"Generated summary: {summary_text[:100]}...")

            # 3. Return the summary in the specified GraphQL type
            return JournalSummary(
                summary=summary_text, generated_at=datetime.now(timezone.utc)
            )

        except Exception as e:
            logger.error(
                f"Failed to summarize journals for user {current_user.id}: {e}"
            )
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
        """
        Performs semantic search across knowledge base and personal journal entries.

        Args:
            info: GraphQL context info
            query: Search query
            tradition: Tradition to search in
            include_personal: Whether to include personal entries
            include_knowledge: Whether to include knowledge base
            entry_types: Types of entries to include
            limit: Maximum number of results

        Returns:
            List[str]: List of search results
        """
        current_user = get_current_user_from_context(info)

        try:
            search_service = SearchService()
            search_results = await search_service.semantic_search(
                query=query,
                user_id=str(current_user.id),
                tradition=tradition,
                include_personal=include_personal,
                include_knowledge=include_knowledge,
                entry_types=entry_types,
                limit=limit,
            )

            return [result["text"] for result in search_results]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    # --- Phase 4.5 Enhanced Tool Registry Integration ---

    @strawberry.field
    async def list_tools(
        self,
        info: Info[GraphQLContext, None],
        backend: Optional[str] = None,
        tags: Optional[List[str]] = None,
        owner_domain: Optional[str] = None,
        version: Optional[str] = None,
    ) -> List[ToolMetadata]:
        """
        List available MCP tools with optional filtering.

        Args:
            info: GraphQL context info
            backend: Filter by backend (langgraph, prompt, retriever, etc.)
            tags: Filter by tags
            owner_domain: Filter by owner domain
            version: Filter by version

        Returns:
            List[ToolMetadata]: List of available tools
        """
        get_current_user_from_context(info)  # Ensure authentication

        try:
            llm_service = LLMService()
            tools = llm_service.list_tools(backend, tags, owner_domain, version)

            return [
                ToolMetadata(
                    name=tool["name"],
                    description=tool["description"],
                    owner_domain=tool["owner_domain"],
                    version=tool["version"],
                    backend=tool["backend"],
                    effect_boundary=tool["effect_boundary"],
                    tags=tool["tags"],
                    subtools=tool["subtools"],
                    input_schema=tool["input_schema"],
                    output_schema=tool["output_schema"],
                )
                for tool in tools
            ]
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []

    @strawberry.field
    async def get_tool_metadata(
        self,
        info: Info[GraphQLContext, None],
        tool_name: str,
        version: Optional[str] = None,
    ) -> Optional[ToolMetadata]:
        """
        Get metadata for a specific tool.

        Args:
            info: GraphQL context info
            tool_name: Name of the tool
            version: Optional version of the tool

        Returns:
            Optional[ToolMetadata]: Tool metadata if found
        """
        get_current_user_from_context(info)  # Ensure authentication

        try:
            llm_service = LLMService()
            metadata = llm_service.get_tool_metadata(tool_name, version)

            if not metadata:
                return None

            return ToolMetadata(
                name=metadata["name"],
                description=metadata["description"],
                owner_domain=metadata["owner_domain"],
                version=metadata["version"],
                backend=metadata["backend"],
                effect_boundary=metadata["effect_boundary"],
                tags=metadata["tags"],
                subtools=metadata["subtools"],
                input_schema=metadata["input_schema"],
                output_schema=metadata["output_schema"],
            )
        except Exception as e:
            logger.error(f"Failed to get tool metadata for {tool_name}: {e}")
            return None

    @strawberry.field
    async def get_tool_registry_health(
        self, info: Info[GraphQLContext, None]
    ) -> ToolRegistryHealth:
        """
        Get health status of the tool registry.

        Args:
            info: GraphQL context info

        Returns:
            ToolRegistryHealth: Health status of the tool registry
        """
        get_current_user_from_context(info)  # Ensure authentication

        try:
            llm_service = LLMService()
            health = llm_service.get_tool_registry_health()

            return ToolRegistryHealth(
                status=health["status"],
                total_tools=health["total_tools"],
                unique_tools=health["unique_tools"],
                backends=health["backends"],
                error=health.get("error"),
            )
        except Exception as e:
            logger.error(f"Failed to get tool registry health: {e}")
            return ToolRegistryHealth(
                status="unhealthy",
                total_tools=0,
                unique_tools=0,
                backends={},
                error=str(e),
            )

    @strawberry.field
    async def list_tool_names(self, info: Info[GraphQLContext, None]) -> List[str]:
        """
        List all registered tool names.

        Args:
            info: GraphQL context info

        Returns:
            List[str]: List of registered tool names
        """
        get_current_user_from_context(info)  # Ensure authentication

        try:
            llm_service = LLMService()
            return llm_service.list_tool_names()
        except Exception as e:
            logger.error(f"Failed to list tool names: {e}")
            return []
