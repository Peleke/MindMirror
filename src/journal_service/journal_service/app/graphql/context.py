"""
GraphQL Context Management

Clean GraphQL context management with proper typing and dependency injection.
"""

from typing import Any, Dict, Optional

from fastapi import Depends, Header
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole
from strawberry.types import Info

from journal_service.journal_service.app.config import get_settings
from journal_service.journal_service.app.db.database import get_session
from journal_service.journal_service.app.db.repositories.journal import JournalRepository
from journal_service.journal_service.app.services.journal_service import JournalService

# Type alias for GraphQL context
GraphQLContext = Dict[str, Any]


# TODO: INTEGRATE WITH ACTUAL USERS SERVICE
# Currently mocking role for development - replace with real users service integration
async def get_current_user_from_header(
    x_internal_id: Optional[str] = Header(None, alias="x-internal-id")
) -> CurrentUser:
    """Get current user from x-internal-id header (real user ID) with mocked role."""
    settings = get_settings()
    
    if x_internal_id:
        # Real user request with header
        return CurrentUser(
            id=x_internal_id,
            supabase_id=x_internal_id,  # TODO: Should never be used after this
            roles=[
                UserRole(role="user", domain="journaling"),  # TODO: Get from users service
            ]
        )
    else:
        # No header present, assume introspection/development
        return CurrentUser(
            id=settings.faux_mesh_user_id,
            supabase_id=settings.faux_mesh_supabase_id,
            roles=[
                UserRole(role="user", domain="journaling"),
            ]
        )


async def get_context(
    session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> GraphQLContext:
    """
    Create GraphQL context with dependencies.

    Args:
        session: Database session
        current_user: Authenticated user (from x-internal-id header or fallback)

    Returns:
        GraphQLContext: Context dictionary for GraphQL resolvers
    """
    # Create service instance
    repository = JournalRepository(session)
    journal_service = JournalService(repository)

    return {
        "session": session,
        "current_user": current_user,
        "journal_service": journal_service,
    }


def get_current_user_from_context(info: Info[GraphQLContext, None]) -> CurrentUser:
    """
    Extract current user from GraphQL context.

    Args:
        info: GraphQL info object

    Returns:
        CurrentUser: Authenticated user

    Raises:
        Exception: If user is not authenticated
    """
    current_user = info.context.get("current_user")
    if not current_user:
        raise Exception("Authentication required.")
    return current_user


def get_journal_service_from_context(info: Info[GraphQLContext, None]) -> JournalService:
    """
    Extract journal service from GraphQL context.

    Args:
        info: GraphQL info object

    Returns:
        JournalService: Journal service instance
    """
    return info.context["journal_service"]


def get_session_from_context(info: Info[GraphQLContext, None]):
    """
    Extract database session from GraphQL context.

    Args:
        info: GraphQL info object

    Returns:
        Database session
    """
    return info.context["session"]


def get_user_roles_from_context(info: Info[GraphQLContext, None]) -> list[UserRole]:
    """
    Extract user roles from GraphQL context.

    Args:
        info: GraphQL info object

    Returns:
        list[UserRole]: User roles
    """
    return info.context.get("user_roles", []) 