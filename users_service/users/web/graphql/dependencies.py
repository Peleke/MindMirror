from typing import Annotated, AsyncGenerator, Optional
from uuid import UUID
import logging
import jwt

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from users.domain.models import DomainUser
from users.repository.database import (
    async_session_factory,
)
from users.repository.repositories import UserRepository
from users.repository.uow import UnitOfWork

logger = logging.getLogger(__name__)


# New dependency to manage request-scoped UoW
async def get_request_uow(request: Request) -> AsyncGenerator[UnitOfWork, None]:
    """
    Dependency that creates and manages a request-scoped UnitOfWork.
    It stores the UoW in the request state to be shared across the request.
    """
    if not hasattr(request.state, "uow"):
        if async_session_factory is None:
            raise RuntimeError("async_session_factory not initialized.")
        request.state.uow = UnitOfWork(session_factory=async_session_factory)

    uow: UnitOfWork = request.state.uow
    async with uow:
        yield uow


# Updated get_uow to be a simple retriever from request.state
def get_uow(request: Request) -> UnitOfWork:
    """
    Retrieves the request-scoped UnitOfWork instance.
    This relies on `get_request_uow` having been run for the request.
    """
    if not hasattr(request.state, "uow"):
        raise RuntimeError(
            "UnitOfWork not found in request.state. " "Ensure the main router depends on `get_request_uow`."
        )
    return request.state.uow


class CurrentUser:
    """Dependency to get the current user from the request headers."""

    def __init__(
        self,
        internal_id: Optional[str] = Header(None, alias="x-internal-id"),
        override_user_id: Optional[str] = Header(None, alias="x-user-id"),
    ):
        # Prefer explicit override for testing/seed paths
        raw_id = override_user_id or internal_id
        self.internal_id: Optional[UUID] = None
        if raw_id is not None:
            try:
                self.internal_id = UUID(raw_id)
            except (ValueError, TypeError):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id header format")
        # If neither header provided, remain None; callers can treat as anonymous


async def get_current_user(
    request: Request,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    current_user_dep: CurrentUser = Depends(),
) -> Optional[DomainUser]:
    """
    FastAPI dependency that retrieves the current user from the database.
    It uses the request-scoped UoW.
    Returns None if no user header provided (anonymous).

    If user doesn't exist in database but has valid JWT:
    - Extracts profile data from JWT
    - Creates user automatically using get_or_create pattern
    """
    if hasattr(request.state, "user"):
        return request.state.user

    if current_user_dep.internal_id is None:
        # Anonymous access allowed for now (e.g., role assignment by admin tools or local testing)
        return None

    repo = UserRepository(uow.session)
    user_model = await repo.get_user_by_id(current_user_dep.internal_id)

    # If user doesn't exist, try to create from JWT
    if not user_model:
        logger.info(f"User {current_user_dep.internal_id} not found in database, attempting auto-creation from JWT")

        # Extract JWT from Authorization header
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Decode JWT (without signature verification for profile extraction)
                decoded_token = jwt.decode(
                    token,
                    options={"verify_signature": False}  # Gateway already validated
                )

                # Extract profile data from JWT
                supabase_id = decoded_token.get("sub")
                user_email = decoded_token.get("email")
                user_metadata = decoded_token.get("user_metadata", {})
                first_name = user_metadata.get("first_name") or user_metadata.get("firstName")
                last_name = user_metadata.get("last_name") or user_metadata.get("lastName")

                if supabase_id:
                    # Build profile data dict
                    profile_data = {}
                    if user_email:
                        profile_data['email'] = user_email
                    if first_name:
                        profile_data['first_name'] = first_name
                    if last_name:
                        profile_data['last_name'] = last_name

                    # Create user using repository's get_or_create method
                    logger.info(f"Creating user with supabase_id={supabase_id}, profile={profile_data}")
                    user_model = await repo.get_or_create_user(supabase_id, profile_data)
                    await uow.commit()
                    logger.info(f"Successfully created user {user_model.id_} from JWT")
                else:
                    logger.error("JWT missing 'sub' field, cannot create user")
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT: missing user ID")

            except jwt.PyJWTError as e:
                logger.error(f"JWT decoding failed: {e}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token")
            except Exception as e:
                logger.error(f"User auto-creation failed: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
        else:
            # No JWT to extract profile from, return 401
            logger.error(f"User {current_user_dep.internal_id} not found and no JWT provided for auto-creation")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    domain_user = DomainUser.model_validate(user_model)
    request.state.user = domain_user
    return domain_user


__all__ = ["get_uow", "get_current_user", "CurrentUser", "get_request_uow"]
