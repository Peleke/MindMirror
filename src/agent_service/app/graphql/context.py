"""
GraphQL Context Management

Clean GraphQL context management with proper typing and dependency injection.
"""

from typing import Dict, Any

from fastapi import Depends
from strawberry.types import Info

from app.db.uow import UnitOfWork, get_uow
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole


# Type alias for GraphQL context
GraphQLContext = Dict[str, Any]


async def get_context(
    uow: UnitOfWork = Depends(get_uow),
    current_user: CurrentUser = Depends(get_current_user),
) -> GraphQLContext:
    """
    Create GraphQL context with dependencies.
    
    Args:
        uow: Unit of work for database operations
        current_user: Authenticated user
        
    Returns:
        GraphQLContext: Context dictionary for GraphQL resolvers
    """
    # Mock user roles for development
    # In production, this would come from the users service
    user_roles = [
        UserRole(role="user", domain="coaching"),
    ]
    
    return {
        "uow": uow,
        "current_user": current_user,
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


def get_uow_from_context(info: Info[GraphQLContext, None]) -> UnitOfWork:
    """
    Extract unit of work from GraphQL context.
    
    Args:
        info: GraphQL info object
        
    Returns:
        UnitOfWork: Database unit of work
    """
    return info.context["uow"]


def get_user_roles_from_context(info: Info[GraphQLContext, None]) -> list[UserRole]:
    """
    Extract user roles from GraphQL context.
    
    Args:
        info: GraphQL info object
        
    Returns:
        list[UserRole]: User roles
    """
    return info.context.get("user_roles", []) 