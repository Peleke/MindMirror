from typing import Any, Dict, Optional
from fastapi import Depends, Header
from shared.auth import CurrentUser
from shared.data_models import UserRole
from strawberry.types import Info


GraphQLContext = Dict[str, Any]


async def get_current_user_from_header(
    x_internal_id: Optional[str] = Header(None, alias="x-internal-id")
) -> CurrentUser:
    if not x_internal_id:
        raise Exception("Authentication required.")
    return CurrentUser(
        id=x_internal_id,  # type: ignore[arg-type]
        supabase_id=x_internal_id,
        roles=[UserRole(role="user", domain="habits")],
    )


async def get_context(current_user: CurrentUser = Depends(get_current_user_from_header)) -> GraphQLContext:
    return {
        "current_user": current_user,
    }


def get_current_user_from_context(info: Info[GraphQLContext, None]) -> CurrentUser:
    user = info.context.get("current_user")
    if not user:
        raise Exception("Authentication required.")
    return user


