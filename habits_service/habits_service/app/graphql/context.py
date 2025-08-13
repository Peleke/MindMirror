from typing import Any, Dict, Optional
from fastapi import Header, Request
from shared.auth import CurrentUser
from shared.data_models import UserRole
from strawberry.types import Info
from habits_service.habits_service.app.config import get_settings


GraphQLContext = Dict[str, Any]

async def get_context(
    request: Request,
    x_internal_id: Optional[str] = Header(None, alias="x-internal-id"),
) -> GraphQLContext:
    settings = get_settings()

    if x_internal_id:
        user = CurrentUser(
            id=x_internal_id,  # type: ignore[arg-type]
            supabase_id=x_internal_id,
            roles=[UserRole(role="user", domain="habits")],
        )
    else:
        # Always fallback to faux user when header is missing (mirrors journal_service)
        user = CurrentUser(
            id=getattr(settings, 'faux_mesh_user_id', '00000000-0000-0000-0000-000000000001'),
            supabase_id=getattr(settings, 'faux_mesh_supabase_id', '00000000-0000-0000-0000-000000000002'),
            roles=[UserRole(role="user", domain="habits")],
        )

    return {"current_user": user, "request": request}


def get_current_user_from_context(info: Info[GraphQLContext, None]) -> CurrentUser:
    user = info.context.get("current_user")
    if not user:
        raise Exception("Authentication required.")
    return user


