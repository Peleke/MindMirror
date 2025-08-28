"""Integration tests for the GraphQL mutation endpoints."""

import uuid
from typing import Any, Dict

import pytest
from httpx import AsyncClient

from tests.conftest import create_auth_headers
from users.repository.models import (
    AssociationStatusModel,
    DomainModel,
    RoleModel,
    UserModel,
)

# region Mutations and Queries
SEND_COACHING_REQUEST_MUTATION = """
    mutation SendCoachingRequest($clientId: UUID!, $domain: DomainGQL!) {
      sendCoachingRequest(clientId: $clientId, domain: $domain) {
        id_
        status
        coach { id_ }
        client { id_ }
      }
    }
"""

RESPOND_TO_COACHING_REQUEST_MUTATION = """
    mutation RespondToCoachingRequest($associationId: UUID!, $accept: Boolean!) {
      respondToCoachingRequest(associationId: $associationId, accept: $accept) {
        id_
        status
      }
    }
"""

TERMINATE_COACHING_RELATIONSHIP_MUTATION = """
    mutation TerminateCoachingRelationship($associationId: UUID!) {
      terminateCoachingRelationship(associationId: $associationId)
    }
"""

VERIFY_RELATIONSHIP_QUERY = """
    query VerifyCoachClientRelationship($coachId: UUID!, $clientId: UUID!, $domain: DomainGQL!) {
      verifyCoachClientRelationship(coachId: $coachId, clientId: $clientId, domain: $domain)
    }
"""

ASSIGN_ROLE_MUTATION = """
    mutation AssignRoleToUser($userId: UUID!, $role: RoleGQL!, $domain: DomainGQL!) {
      assignRoleToUser(userId: $userId, role: $role, domain: $domain) {
        id_
        role
        domain
      }
    }
"""

REMOVE_ROLE_MUTATION = """
    mutation RemoveRoleFromUser($userId: UUID!, $role: RoleGQL!, $domain: DomainGQL!) {
      removeRoleFromUser(userId: $userId, role: $role, domain: $domain)
    }
"""

USER_ROLES_QUERY = """
    query UserRoles($userId: UUID!) {
        userRoles(userId: $userId) {
            role
            domain
        }
    }
"""
# endregion


@pytest.mark.asyncio
class TestGraphQLMutations:
    async def test_send_coaching_request_lifecycle(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """
        Tests the full lifecycle of a coaching relationship:
        1. Coach sends a request.
        2. Client accepts the request.
        3. The relationship is verified as active.
        4. Coach terminates the relationship.
        5. The relationship is verified as no longer active.
        """
        coach: UserModel = seed_data["user1_coach"]
        client_user: UserModel = seed_data[
            "user3_client"
        ]  # This client has no prior association with the coach in 'meals'
        domain = DomainModel.meals

        # --- 1. Coach sends request ---
        coach_headers = create_auth_headers(user_id=str(coach.id_))
        variables = {"clientId": str(client_user.id_), "domain": domain.name.upper()}
        response = await client.post(
            "/graphql", json={"query": SEND_COACHING_REQUEST_MUTATION, "variables": variables}, headers=coach_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None, f"GraphQL Error: {data.get('errors')}"

        request_data = data["data"]["sendCoachingRequest"]
        assert request_data["status"] == AssociationStatusModel.pending.name.upper()
        assert request_data["coach"]["id_"] == str(coach.id_)
        assert request_data["client"]["id_"] == str(client_user.id_)
        association_id = request_data["id_"]

        # --- 2. Client accepts request ---
        client_headers = create_auth_headers(user_id=str(client_user.id_))
        variables = {"associationId": association_id, "accept": True}
        response = await client.post(
            "/graphql",
            json={"query": RESPOND_TO_COACHING_REQUEST_MUTATION, "variables": variables},
            headers=client_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None, f"GraphQL Error: {data.get('errors')}"
        assert data["data"]["respondToCoachingRequest"]["status"] == AssociationStatusModel.accepted.name.upper()

        # --- 3. Verify relationship is active ---
        variables = {"coachId": str(coach.id_), "clientId": str(client_user.id_), "domain": domain.name.upper()}
        response = await client.post(
            "/graphql", json={"query": VERIFY_RELATIONSHIP_QUERY, "variables": variables}, headers=coach_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None
        assert data["data"]["verifyCoachClientRelationship"] is True

        # --- 4. Coach terminates relationship ---
        variables = {"associationId": association_id}
        response = await client.post(
            "/graphql",
            json={"query": TERMINATE_COACHING_RELATIONSHIP_MUTATION, "variables": variables},
            headers=coach_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None
        assert data["data"]["terminateCoachingRelationship"] is True

        # --- 5. Verify relationship is terminated (check_existing returns false for 'accepted' status) ---
        variables = {"coachId": str(coach.id_), "clientId": str(client_user.id_), "domain": domain.name.upper()}
        response = await client.post(
            "/graphql", json={"query": VERIFY_RELATIONSHIP_QUERY, "variables": variables}, headers=coach_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None
        assert data["data"]["verifyCoachClientRelationship"] is False

    async def test_send_coaching_request_unauthorized(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Ensures a user without a COACH role cannot send a coaching request."""
        non_coach_user: UserModel = seed_data["user2_client"]
        target_client: UserModel = seed_data["user3_client"]
        domain = DomainModel.practices

        headers = create_auth_headers(user_id=str(non_coach_user.id_))
        variables = {"clientId": str(target_client.id_), "domain": domain.name.upper()}
        response = await client.post(
            "/graphql", json={"query": SEND_COACHING_REQUEST_MUTATION, "variables": variables}, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "You do not have a COACH role" in data["errors"][0]["message"]

    async def test_respond_to_coaching_request_unauthorized(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Ensures a third-party user cannot respond to a pending request."""
        third_party_user: UserModel = seed_data["user2_client"]
        pending_assoc = seed_data["assoc_pending"]

        headers = create_auth_headers(user_id=str(third_party_user.id_))
        variables = {"associationId": str(pending_assoc.id_), "accept": True}
        response = await client.post(
            "/graphql",
            json={"query": RESPOND_TO_COACHING_REQUEST_MUTATION, "variables": variables},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "You are not a party to this coaching request" in data["errors"][0]["message"]

    async def test_terminate_coaching_relationship_unauthorized(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Ensures a third-party user cannot terminate an active coaching relationship."""
        third_party_user: UserModel = seed_data["user3_client"]
        active_assoc = seed_data["assoc_accepted"]

        headers = create_auth_headers(user_id=str(third_party_user.id_))
        variables = {"associationId": str(active_assoc.id_)}
        response = await client.post(
            "/graphql",
            json={"query": TERMINATE_COACHING_RELATIONSHIP_MUTATION, "variables": variables},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "You are not part of this coaching relationship" in data["errors"][0]["message"]

    async def test_role_management_mutations(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Tests assigning and removing roles from a user."""
        admin_user: UserModel = seed_data["user1_coach"]  # Acting as an admin
        target_user: UserModel = seed_data["user3_client"]
        domain_to_add = DomainModel.sleep
        role_to_add = RoleModel.client

        headers = create_auth_headers(user_id=str(admin_user.id_))

        # --- 1. Assign Role ---
        variables = {
            "userId": str(target_user.id_),
            "role": role_to_add.name.upper(),
            "domain": domain_to_add.name.upper(),
        }
        response = await client.post(
            "/graphql", json={"query": ASSIGN_ROLE_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None
        assigned_role = data["data"]["assignRoleToUser"]
        assert assigned_role["role"] == role_to_add.name.upper()
        assert assigned_role["domain"] == domain_to_add.name.upper()

        # --- 2. Verify Role Assignment ---
        variables = {"userId": str(target_user.id_)}
        response = await client.post(
            "/graphql", json={"query": USER_ROLES_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None
        roles = data["data"]["userRoles"]
        assert any(
            r["role"] == role_to_add.name.upper() and r["domain"] == domain_to_add.name.upper() for r in roles
        ), "Newly assigned role was not found on the user."

        # --- 3. Remove Role ---
        variables = {
            "userId": str(target_user.id_),
            "role": role_to_add.name.upper(),
            "domain": domain_to_add.name.upper(),
        }
        response = await client.post(
            "/graphql", json={"query": REMOVE_ROLE_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None
        assert data["data"]["removeRoleFromUser"] is True

        # --- 4. Verify Role Removal ---
        variables = {"userId": str(target_user.id_)}
        response = await client.post(
            "/graphql", json={"query": USER_ROLES_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None
        roles = data["data"]["userRoles"]
        assert not any(
            r["role"] == role_to_add.name.upper() and r["domain"] == domain_to_add.name.upper() for r in roles
        ), "Removed role was still found on the user."
