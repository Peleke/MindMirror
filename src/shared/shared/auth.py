import logging
from typing import List, Optional, Any, Dict
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
SUPABASE_JWT_SECRET = "your-supabase-jwt-secret-for-local-dev" # Replace with a real secret or loading mechanism

# It's better to get this from a central client library if available
# from practices.service.clients.user_service_client import users_service_client, UserRole

class CurrentUser(BaseModel):
    """
    A Pydantic model representing the authenticated user.

    This object is created by the `get_current_user` dependency and injected
    into the GraphQL context. It standardizes access to user identity information.
    """
    id: UUID = Field(..., description="The user's internal ID.")
    supabase_id: Optional[str] = Field(None, description="The user's Supabase ID, from the JWT 'sub' claim.")
    roles: List[UserRole] = Field(default_factory=list, description="The user's roles, fetched from the users service.")

    def has_role(self, role: str, domain: str) -> bool:
        """Checks if the user has a specific role within a given domain."""
        return any(r.role == role and r.domain == domain for r in self.roles)

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
    auth_header = request.headers.get("Authorization")

    if not internal_id_header:
        logger.warning("x-internal-id header is missing.")
        # Fallback logic to use JWT can be implemented here if needed.
        # For now, we will deny access if the primary ID is missing.
        return None

    try:
        user_internal_id = UUID(internal_id_header)
    except (ValueError, TypeError):
        logger.error("Invalid UUID format for x-internal-id: %s", internal_id_header)
        return None

    supabase_id: Optional[str] = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # Note: In production, use a library like `python-jose` to fetch keys
            # from a JWKS URL and verify the signature properly.
            # Here we are just decoding without verification for simplicity.
            decoded_token = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_signature": False})
            supabase_id = decoded_token.get("sub")
        except jwt.PyJWTError as e:
            logger.error("JWT decoding failed: %s", e)
            # Proceed without supabase_id, but the internal ID is what matters most.

    # Fetch roles from the users service
    roles = await users_service_client.get_user_roles(user_internal_id)
    if roles is None:
        # This means the service call failed. We should deny access.
        logger.error("Could not fetch roles for user %s. Denying access.", user_internal_id)
        return None

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
        if not getattr(self, "required_role", None) or not getattr(self, "required_domain", None):
             raise NotImplementedError("Permission classes must define required_role and required_domain.")

        current_user: Optional[CurrentUser] = info.context.get("current_user")

        if not current_user:
            self.message = "Authentication required. No user found in context."
            return False

        if current_user.has_role(self.required_role, self.required_domain):
            return True

        self.message = f"User does not have the required role ('{self.required_role}') in domain ('{self.required_domain}')."
        return False 