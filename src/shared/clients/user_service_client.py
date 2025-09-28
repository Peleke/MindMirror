# NOTE: serious code smells
import logging
import os
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from pydantic import BaseModel, Field

from shared.data_models import UserRole

# --- Pydantic models for parsing the response from the users service ---


class UserRolesResponse(BaseModel):
    """The expected structure of the 'data' field in the GraphQL response."""

    user_roles: List[UserRole] = Field(..., alias="userRoles")


class GraphQLResponse(BaseModel):
    """The top-level structure of the GraphQL response."""

    data: Optional[UserRolesResponse] = None
    errors: Optional[List[Dict[str, Any]]] = None


class VerifyRelationshipResponse(BaseModel):
    verify_coach_client_relationship: bool = Field(
        ..., alias="verifyCoachClientRelationship"
    )


class GraphQLVerifyResponse(BaseModel):
    data: Optional[VerifyRelationshipResponse] = None
    errors: Optional[List[Dict[str, Any]]] = None


class GetOrCreateUserData(BaseModel):
    id_: UUID = Field(..., alias="id_")
    supabase_id: str = Field(..., alias="supabase_id")


class GetOrCreateUserResponse(BaseModel):
    data: Optional[Dict[str, GetOrCreateUserData]] = None
    errors: Optional[List[Dict[str, Any]]] = None


class UsersServiceClient:
    """
    A client for communicating with the `users` service.

    This client is responsible for fetching user-related data, such as roles,
    which is required for authorization decisions in other services.

    Security Note:
    In a production environment, service-to-service communication must be secured.
    Current approach (no auth) is only suitable for a trusted internal VPC.
    Recommendations for improvement:
    1. mTLS: Mutual TLS ensures that both the client and server authenticate each other.
    2. JWT/OAuth 2.0 Client Credentials: The client service could obtain a token from
       an auth server (like Hive or Keycloak) to present to the user service.
    3. API Keys/HMAC: A simpler, though less robust, method involves pre-shared
       API keys. The client signs requests with the key, and the server verifies the signature.
    """

    def __init__(self, base_url: Optional[str] = None):
        raw_base = base_url or os.getenv(
            "USERS_SERVICE_URL", "http://localhost:8000/graphql"
        )
        # Normalize: strip trailing slashes to avoid posting to /graphql/
        self.base_url = raw_base.rstrip("/")
        # Ensure we are targeting the GraphQL endpoint even if a root URL is provided
        if not self.base_url.endswith("/graphql"):
            self.base_url = f"{self.base_url}/graphql"
        if not self.base_url:
            raise ValueError("USERS_SERVICE_URL must be set.")
        self.client = httpx.AsyncClient(timeout=5.0, follow_redirects=True)
        self.logger = logging.getLogger(__name__)

    async def get_user_roles(self, user_id: UUID) -> Optional[List[UserRole]]:
        """
        Fetches the roles for a given user ID from the `users` service.
        """
        query = """
            query GetUserRoles($userId: UUID!) {
                userRoles(userId: $userId) {
                    role
                    domain
                }
            }
        """
        variables = {"userId": str(user_id)}

        try:
            response = await self.client.post(self.base_url, json={"query": query, "variables": variables})
            response.raise_for_status()

            response_data = response.json()
            parsed_response = GraphQLResponse.model_validate(response_data)

            if parsed_response.errors:
                self.logger.error(
                    "GraphQL errors while fetching user roles: %s",
                    parsed_response.errors,
                )
                return None

            if parsed_response.data and parsed_response.data.user_roles:
                return parsed_response.data.user_roles

            return []  # User exists but has no roles

        except httpx.HTTPStatusError as e:
            self.logger.error(
                "HTTP error occurred while fetching user roles for user %s: %s",
                user_id,
                e,
            )
            return None
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching user roles for user %s: %s",
                user_id,
                e,
            )
            return None

    async def verify_coach_client_relationship(
        self, coach_id: UUID, client_id: UUID, domain: str
    ) -> bool:
        """
        Verifies that an 'ACCEPTED' coach-client relationship exists in the users service.
        """
        query = """
            query VerifyCoachClient($coachId: UUID!, $clientId: UUID!, $domain: DomainGQL!) {
                verifyCoachClientRelationship(coachId: $coachId, clientId: $clientId, domain: $domain)
            }
        """
        variables = {
            "coachId": str(coach_id),
            "clientId": str(client_id),
            "domain": domain.upper(),  # Match the GQL enum value
        }

        try:
            response = await self.client.post(self.base_url, json={"query": query, "variables": variables})
            response.raise_for_status()
            response_data = response.json()
            parsed_response = GraphQLVerifyResponse.model_validate(response_data)

            if parsed_response.errors:
                self.logger.error(
                    "GraphQL errors while verifying relationship: %s",
                    parsed_response.errors,
                )
                return False

            if parsed_response.data:
                return parsed_response.data.verify_coach_client_relationship

            return False

        except httpx.HTTPStatusError as e:
            self.logger.error("HTTP error occurred while verifying relationship: %s", e)
            return False
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while verifying relationship: %s", e
            )
            return False

    async def get_or_create_user_by_supabase_id(self, supabase_id: str, profile_data: Optional[Dict[str, str]] = None) -> Optional[UUID]:
        """Create or fetch a user by supabase_id, returning the internal UUID."""
        query = """
            mutation GetOrCreate($sub: String!, $email: String, $firstName: String, $lastName: String) {
                getOrCreateUser(supabaseId: $sub, email: $email, firstName: $firstName, lastName: $lastName) { id_ supabase_id email firstName lastName }
            }
        """
        variables = {"sub": supabase_id}
        if profile_data:
            variables.update({
                "email": profile_data.get("email"),
                "firstName": profile_data.get("first_name"),
                "lastName": profile_data.get("last_name"),
            })
        try:
            response = await self.client.post(self.base_url, json={"query": query, "variables": variables})
            response.raise_for_status()
            data = response.json()
            if data.get("errors"):
                self.logger.error("GraphQL errors in getOrCreateUser: %s", data["errors"])
                return None
            user_node = data.get("data", {}).get("getOrCreateUser")
            if not user_node:
                return None
            return UUID(user_node["id_"])
        except Exception as e:
            self.logger.error("Error in get_or_create_user_by_supabase_id: %s", e)
            return None


# Global client instance
users_service_client = UsersServiceClient()
