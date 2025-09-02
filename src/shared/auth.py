import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

import jwt
from pydantic import BaseModel, Field
from starlette.requests import Request
from strawberry.permission import BasePermission
from strawberry.types import Info

from shared.clients.user_service_client import users_service_client
from shared.data_models import UserRole

# A mock key for JWT decoding. In a real application, this should be fetched securely.
# e.g., from a JWKS endpoint provided by your auth server (Hive/Supabase).
SUPABASE_JWT_SECRET = "your-supabase-jwt-secret-for-local-dev"  # Replace with a real secret or loading mechanism

# It's better to get this from a central client library if available
# from practices.service.clients.user_service_client import users_service_client, UserRole


class CurrentUser(BaseModel):
    """
    A Pydantic model representing the authenticated user.

    This object is created by the `get_current_user` dependency and injected
    into the GraphQL context. It standardizes access to user identity information.
    """

    id: UUID = Field(..., description="The user's internal ID.")
    supabase_id: Optional[str] = Field(
        None, description="The user's Supabase ID, from the JWT 'sub' claim."
    )
    roles: List[UserRole] = Field(
        default_factory=list,
        description="The user's roles, fetched from the users service.",
    )

    def has_role(self, role: str, domain: str) -> bool:
        """Checks if the user has a specific role within a given domain."""
        rl = (role or "").lower()
        dl = (domain or "").lower()
        return any(str(r.role).lower() == rl and str(r.domain).lower() == dl for r in self.roles)


async def get_current_user(request: Request) -> Optional[CurrentUser]:
    """
    FastAPI dependency to authenticate a request and build a CurrentUser object.

    It extracts the user's internal ID from the `x-internal-id` header.
    It also decodes the JWT from the `Authorization` header to get the Supabase ID.
    Finally, it fetches the user's roles from the `users` service.

    Note on ID resolution:
    - `x-internal-id`: This is the primary identifier. The gateway should set this header.
    - JWT `sub` claim: If the header is missing, we can use the Supabase ID from the token
      as a fallback to fetch the internal ID, though this is less efficient.
      For this MVP, we assume `x-internal-id` is present.
    """
    logger = logging.getLogger(__name__)
    internal_id_header = request.headers.get("x-internal-id")
    # Starlette headers are case-insensitive, but fetch both just in case
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

    supabase_id: Optional[str] = None
    token: Optional[str] = None

    # Try to parse JWT first, so we can potentially map sub -> internal UUID when header is missing
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_signature": False},
            )
            supabase_id = decoded_token.get("sub")
            # Extract user profile data for new user creation
            user_email = decoded_token.get("email")
            user_metadata = decoded_token.get("user_metadata", {})
            first_name = user_metadata.get("first_name") or user_metadata.get("firstName")
            last_name = user_metadata.get("last_name") or user_metadata.get("lastName")
        except jwt.PyJWTError as e:
            logger.error("JWT decoding failed: %s", e)

    user_internal_id: Optional[UUID] = None

    if internal_id_header:
        try:
            user_internal_id = UUID(internal_id_header)
        except (ValueError, TypeError):
            logger.error("Invalid UUID format for x-internal-id: %s", internal_id_header)
            return None
    else:
        # Fallback: map Supabase ID -> internal UUID via Users service
        if supabase_id:
            try:
                # Pass profile data to user service for new user creation
                profile_data = {}
                if 'user_email' in locals() and user_email:
                    profile_data['email'] = user_email
                if 'first_name' in locals() and first_name:
                    profile_data['first_name'] = first_name  
                if 'last_name' in locals() and last_name:
                    profile_data['last_name'] = last_name
                    
                mapped_id = await users_service_client.get_or_create_user_by_supabase_id(supabase_id, profile_data)
                if mapped_id is not None:
                    user_internal_id = mapped_id
                else:
                    logger.warning("Could not map supabase_id %s to internal user id via users service.", supabase_id)
                    return None
            except Exception as e:
                logger.error("Users service mapping failed: %s", e)
                return None
        else:
            logger.warning("x-internal-id header is missing and no valid JWT sub; rejecting request.")
            return None

    # Re-enable role fetching from Users service; fallback to empty list if unavailable
    roles = await users_service_client.get_user_roles(user_internal_id)
    if roles is None:
        logger.error("Could not fetch roles for user %s. Proceeding with empty roles.", user_internal_id)
        roles = []

    return CurrentUser(id=user_internal_id, supabase_id=supabase_id, roles=roles)


class RequireRolePermission(BasePermission):
    """
    A Strawberry permission class to enforce role-based access control.

    This is a base class. Subclasses must define `required_role` and `required_domain`.

    Usage:
        class CanAccessX(RequireRolePermission):
            required_role = "admin"
            required_domain = "x"

        @strawberry.field(permission_classes=[CanAccessX])
        def some_resolver(self, info: Info) -> str:
            return "You are an admin for X!"
    """

    message: str = "User does not have the required permissions."
    required_role: str
    required_domain: str

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        if not getattr(self, "required_role", None) or not getattr(
            self, "required_domain", None
        ):
            raise NotImplementedError(
                "Permission classes must define required_role and required_domain."
            )

        current_user: Optional[CurrentUser] = info.context.get("current_user")

        if not current_user:
            self.message = "Authentication required. No user found in context."
            return False

        if current_user.has_role(self.required_role, self.required_domain):
            return True

        self.message = f"User does not have the required role ('{self.required_role}') in domain ('{self.required_domain}')."
        return False
