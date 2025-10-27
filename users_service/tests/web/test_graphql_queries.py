"""Integration tests for the GraphQL query endpoints."""

import uuid
from typing import Any, Dict, Optional

import pytest
from httpx import AsyncClient

from tests.conftest import create_auth_headers
from users.repository.models import (
    AssociationStatusModel,
    CoachClientAssociationModel,
    DomainModel,
    RoleModel,
    UserModel,
)

LIST_COACHES_QUERY = """
    query ListCoaches {
      listCoaches {
        id_
        roles {
          role
          domain
        }
      }
    }
"""

LIST_CLIENTS_QUERY = """
    query ListClients {
      listClients {
        id_
        roles {
            role
            domain
        }
      }
    }
"""

INCOMING_REQUESTS_QUERY = """
    query IncomingCoachingRequests {
      incomingCoachingRequests {
        id_
        status
        coach {
          id_
        }
        client {
          id_
        }
      }
    }
"""

OUTGOING_REQUESTS_QUERY = """
    query OutgoingCoachingRequests {
      outgoingCoachingRequests {
        id_
        status
        coach {
          id_
        }
        client {
          id_
        }
      }
    }
"""

VERIFY_RELATIONSHIP_QUERY = """
    query VerifyCoachClientRelationship($coachId: UUID!, $clientId: UUID!, $domain: DomainGQL!) {
      verifyCoachClientRelationship(coachId: $coachId, clientId: $clientId, domain: $domain)
    }
"""


@pytest.mark.asyncio
class TestGraphQLQueries:
    async def test_list_coaches(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Verifies the listCoaches query returns only users with the COACH role."""
        coach: UserModel = seed_data["user1_coach"]
        headers = create_auth_headers(user_id=str(coach.id_))

        response = await client.post("/graphql", json={"query": LIST_COACHES_QUERY}, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None, f"GraphQL Error: {data.get('errors')}"

        coaches_list = data["data"]["listCoaches"]
        assert isinstance(coaches_list, list)
        assert len(coaches_list) > 0

        # Verify all returned users have a coach role
        for user_data in coaches_list:
            has_coach_role = any(role["role"] == "COACH" for role in user_data["roles"])
            assert has_coach_role

        # Verify our specific seeded coach is in the list
        assert any(c["id_"] == str(coach.id_) for c in coaches_list)

    async def test_list_clients_for_coach(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Verifies that listClients returns only the coach's accepted clients."""
        coach: UserModel = seed_data["user1_coach"]
        accepted_client: UserModel = seed_data["user2_client"]

        headers = create_auth_headers(user_id=str(coach.id_))
        response = await client.post("/graphql", json={"query": LIST_CLIENTS_QUERY}, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None

        clients_list = data["data"]["listClients"]
        assert isinstance(clients_list, list)
        assert len(clients_list) == 1
        assert clients_list[0]["id_"] == str(accepted_client.id_)

    async def test_incoming_coaching_requests(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Verifies a client can see their pending invitations."""
        client_user: UserModel = seed_data["user3_client"]  # This user has a pending request in seed_data
        pending_assoc: CoachClientAssociationModel = seed_data["assoc_pending"]

        headers = create_auth_headers(user_id=str(client_user.id_))
        response = await client.post("/graphql", json={"query": INCOMING_REQUESTS_QUERY}, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None

        requests = data["data"]["incomingCoachingRequests"]
        assert len(requests) == 1
        request = requests[0]
        assert request["id_"] == str(pending_assoc.id_)
        assert request["status"] == AssociationStatusModel.pending.name.upper()
        assert request["client"]["id_"] == str(client_user.id_)

    async def test_outgoing_coaching_requests(self, client: AsyncClient, seed_data: Dict[str, Any]):
        """Verifies a coach can see the requests they have sent."""
        coach: UserModel = seed_data["user1_coach"]  # This user sent the pending request
        pending_assoc: CoachClientAssociationModel = seed_data["assoc_pending"]

        headers = create_auth_headers(user_id=str(coach.id_))
        response = await client.post("/graphql", json={"query": OUTGOING_REQUESTS_QUERY}, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None

        requests = data["data"]["outgoingCoachingRequests"]
        assert len(requests) == 1
        request = requests[0]
        assert request["id_"] == str(pending_assoc.id_)
        assert request["status"] == AssociationStatusModel.pending.name.upper()
        assert request["coach"]["id_"] == str(coach.id_)

    @pytest.mark.parametrize(
        "coach_key, client_key, domain, expected",
        [
            ("user1_coach", "user2_client", DomainModel.practices, True),  # Accepted
            ("user1_coach", "user3_client", DomainModel.practices, False),  # Pending
            ("user1_coach", "user2_client", DomainModel.meals, False),  # Rejected
            ("user2_client", "user1_coach", DomainModel.practices, False),  # Non-existent reverse
        ],
    )
    async def test_verify_coach_client_relationship(
        self,
        client: AsyncClient,
        seed_data: Dict[str, Any],
        coach_key: str,
        client_key: str,
        domain: DomainModel,
        expected: bool,
    ):
        """Tests the verifyCoachClientRelationship query against various relationship statuses."""
        coach_user: UserModel = seed_data[coach_key]
        client_user: UserModel = seed_data[client_key]

        # This query can be run by any authenticated user
        headers = create_auth_headers(user_id=str(coach_user.id_))

        variables = {
            "coachId": str(coach_user.id_),
            "clientId": str(client_user.id_),
            "domain": domain.name.upper(),  # GraphQL enums are typically uppercase
        }

        response = await client.post(
            "/graphql", json={"query": VERIFY_RELATIONSHIP_QUERY, "variables": variables}, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is None

        verification_result = data["data"]["verifyCoachClientRelationship"]
        assert verification_result is expected
