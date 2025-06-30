"""
GraphQL Context Management

Clean GraphQL context management with proper typing and dependency injection.
"""

from typing import Any, Dict

from fastapi import Depends
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole
from strawberry.types import Info

from journal_service.journal_service.app.db.database import get_session
from journal_service.journal_service.app.db.repositories.journal import JournalRepository
from journal_service.journal_service.app.services.journal_service import JournalService

# Type alias for GraphQL context
GraphQLContext = Dict[str, Any]


async def get_context(
    session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> GraphQLContext:
    """
    Create GraphQL context with dependencies.

    Args:
        session: Database session
        current_user: Authenticated user

    Returns:
        GraphQLContext: Context dictionary for GraphQL resolvers
    """
    # Mock user roles for development
    # In production, this would come from the users service
    user_roles = [
        UserRole(role="user", domain="journaling"),
    ]

    # Create service instance
    repository = JournalRepository(session)
    journal_service = JournalService(repository)

    return {
        "session": session,
        "current_user": current_user,
        "journal_service": journal_service,
        "user_roles": user_roles,
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