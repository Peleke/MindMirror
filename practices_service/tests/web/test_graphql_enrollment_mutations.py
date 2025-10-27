import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import API_VERSION

ENROLL_IN_PROGRAM_MUTATION = """
    mutation EnrollInProgram($programId: ID!) {
      enrollInProgram(programId: $programId) {
        id_
        programId
        userId
        status
      }
    }
"""

ENROLL_USER_IN_PROGRAM_MUTATION = """
    mutation EnrollUserInProgram($programId: ID!, $userId: ID!) {
        enrollUserInProgram(programId: $programId, userId: $userId) {
            id_
            programId
            userId
            enrolledByUserId
            status
        }
    }
"""

UPDATE_ENROLLMENT_STATUS_MUTATION = """
    mutation UpdateEnrollmentStatus($enrollmentId: ID!, $status: EnrollmentStatusGQL!) {
        updateEnrollmentStatus(enrollmentId: $enrollmentId, status: $status) {
            id_
            status
            currentPracticeLinkId
        }
    }
"""

DEFER_PRACTICE_MUTATION = """
    mutation DeferPractice($enrollmentId: ID!, $mode: String!) {
        deferPractice(enrollmentId: $enrollmentId, mode: $mode)
    }
"""


@pytest.mark.asyncio
class TestEnrollmentMutations:
    # Test `enroll_in_program`
    async def test_client_can_self_enroll(self, client, auth_headers_for, seed_db):
        program_to_enroll_in = seed_db["programs"][0]
        client_user = seed_db["client_user_two"]
        headers = auth_headers_for(client_user)

        variables = {"programId": str(program_to_enroll_in.id_)}
        response = await client.post(
            "/graphql", json={"query": ENROLL_IN_PROGRAM_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
        enrollment = data["data"]["enrollInProgram"]
        assert enrollment["programId"] == str(program_to_enroll_in.id_)
        assert enrollment["userId"] == str(client_user.id)
        assert enrollment["status"] == "ACTIVE"

    async def test_unauthorized_role_cannot_self_enroll(self, client, auth_headers_for, seed_db):
        program_id = str(seed_db["programs"][0].id_)
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"programId": program_id}

        response = await client.post(
            "/graphql", json={"query": ENROLL_IN_PROGRAM_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "does not have the required role" in data["errors"][0]["message"]
        assert data["data"] is None

    # Test `enroll_user_in_program`
    async def test_coach_can_enroll_verified_client(self, client, auth_headers_for, seed_db):
        program_to_enroll_in = seed_db["programs"][1]
        client_to_enroll = seed_db["client_user_one"]
        coach_user = seed_db["coach_user"]
        headers = auth_headers_for(coach_user)

        variables = {"programId": str(program_to_enroll_in.id_), "userId": str(client_to_enroll.id)}
        response = await client.post(
            "/graphql", json={"query": ENROLL_USER_IN_PROGRAM_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
        enrollment = data["data"]["enrollUserInProgram"]
        assert enrollment["programId"] == str(program_to_enroll_in.id_)
        assert enrollment["userId"] == str(client_to_enroll.id)
        assert enrollment["enrolledByUserId"] == str(coach_user.id)
        assert enrollment["status"] == "ACTIVE"

    async def test_coach_cannot_enroll_unrelated_client(self, client, auth_headers_for, seed_db):
        program_id = str(seed_db["programs"][0].id_)
        unrelated_client_id = str(seed_db["unrelated_client_user"].id)
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"programId": program_id, "userId": unrelated_client_id}

        response = await client.post(
            "/graphql", json={"query": ENROLL_USER_IN_PROGRAM_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "You are not authorized to enroll this user" in data["errors"][0]["message"]
        assert data["data"] is None

    async def test_client_cannot_enroll_another_user(self, client, auth_headers_for, seed_db):
        program_id = str(seed_db["programs"][0].id_)
        client_two_id = str(seed_db["client_user_two"].id)
        headers = auth_headers_for(seed_db["client_user_one"])
        variables = {"programId": program_id, "userId": client_two_id}

        response = await client.post(
            "/graphql", json={"query": ENROLL_USER_IN_PROGRAM_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "does not have the required role" in data["errors"][0]["message"]
        assert data["data"] is None

    # Test `update_enrollment_status`
    async def test_user_can_update_own_enrollment(self, client, auth_headers_for, seed_db):
        enrollment_to_update = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_one"])
        variables = {"enrollmentId": str(enrollment_to_update.id_), "status": "CANCELLED"}

        response = await client.post(
            "/graphql", json={"query": UPDATE_ENROLLMENT_STATUS_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
        updated_enrollment = data["data"]["updateEnrollmentStatus"]
        assert updated_enrollment["id_"] == str(enrollment_to_update.id_)
        assert updated_enrollment["status"] == "CANCELLED"

    async def test_coach_can_update_verified_clients_enrollment(self, client, auth_headers_for, seed_db):
        enrollment_to_update = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"enrollmentId": str(enrollment_to_update.id_), "status": "COMPLETED"}

        response = await client.post(
            "/graphql", json={"query": UPDATE_ENROLLMENT_STATUS_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
        updated_enrollment = data["data"]["updateEnrollmentStatus"]
        assert updated_enrollment["id_"] == str(enrollment_to_update.id_)
        assert updated_enrollment["status"] == "COMPLETED"
        assert updated_enrollment["currentPracticeLinkId"] is None

    async def test_user_cannot_update_others_enrollment(self, client, auth_headers_for, seed_db):
        enrollment_of_client_one = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_two"])
        variables = {"enrollmentId": str(enrollment_of_client_one.id_), "status": "CANCELLED"}

        response = await client.post(
            "/graphql", json={"query": UPDATE_ENROLLMENT_STATUS_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "You do not have permission to update this enrollment" in data["errors"][0]["message"]
        assert data["data"] is None

    async def test_coach_cannot_update_unrelated_clients_enrollment(self, client, auth_headers_for, seed_db):
        enrollment_of_unrelated_client = next(
            e for e in seed_db["enrollments"] if e.user_id == seed_db["unrelated_client_user"].id
        )
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"enrollmentId": str(enrollment_of_unrelated_client.id_), "status": "COMPLETED"}

        response = await client.post(
            "/graphql", json={"query": UPDATE_ENROLLMENT_STATUS_MUTATION, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("errors") is not None
        assert "You do not have permission to update this enrollment" in data["errors"][0]["message"]
        assert data["data"] is None

    @pytest.mark.asyncio
    async def test_complete_and_advance_progress(self, client, seed_db, auth_headers_for):
        # Arrange
        enrollment = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_one"])

        # Act
        # Call it twice to go from practice 1 -> practice 2 -> completed
        await client.post(
            "/graphql",
            json={
                "query": """
                    mutation CompleteAndAdvanceProgress($enrollmentId: ID!) {
                        completeAndAdvanceProgress(enrollmentId: $enrollmentId) {
                            id_
                            status
                            currentPracticeLinkId
                        }
                    }
                """,
                "variables": {"enrollmentId": str(enrollment.id_)},
            },
            headers=headers,
        )
        response = await client.post(
            "/graphql",
            json={
                "query": """
                    mutation CompleteAndAdvanceProgress($enrollmentId: ID!) {
                        completeAndAdvanceProgress(enrollmentId: $enrollmentId) {
                            id_
                            status
                            currentPracticeLinkId
                        }
                    }
                """,
                "variables": {"enrollmentId": str(enrollment.id_)},
            },
            headers=headers,
        )

        # Assert
        response_data = response.json()
        assert response.status_code == 200
        assert "errors" not in response_data

        updated_enrollment = response_data["data"]["completeAndAdvanceProgress"]
        assert updated_enrollment["status"] == "COMPLETED"
        assert updated_enrollment["currentPracticeLinkId"] is None

    async def test_client_can_defer_practice_push_mode(self, client, seed_db, auth_headers_for):
        """Test that a client can defer their practice using 'push' mode."""
        enrollment = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_one"])

        response = await client.post(
            "/graphql",
            json={
                "query": DEFER_PRACTICE_MUTATION,
                "variables": {"enrollmentId": str(enrollment.id_), "mode": "push"},
            },
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "errors" not in response_data
        assert response_data["data"]["deferPractice"] is True

    async def test_client_can_defer_practice_shift_mode(self, client, seed_db, auth_headers_for):
        """Test that a client can defer their practice using 'shift' mode."""
        enrollment = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_one"])

        response = await client.post(
            "/graphql",
            json={
                "query": DEFER_PRACTICE_MUTATION,
                "variables": {"enrollmentId": str(enrollment.id_), "mode": "shift"},
            },
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "errors" not in response_data
        assert response_data["data"]["deferPractice"] is True

    async def test_client_cannot_defer_others_practice(self, client, seed_db, auth_headers_for):
        """Test that a client cannot defer another client's practice."""
        enrollment_of_client_one = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_two"])

        response = await client.post(
            "/graphql",
            json={
                "query": DEFER_PRACTICE_MUTATION,
                "variables": {"enrollmentId": str(enrollment_of_client_one.id_), "mode": "push"},
            },
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "errors" in response_data
        assert "User is not authorized to update this enrollment" in response_data["errors"][0]["message"]

    async def test_coach_cannot_defer_practice(self, client, seed_db, auth_headers_for):
        """Test that a coach cannot defer practices (only clients can)."""
        enrollment = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["coach_user"])

        response = await client.post(
            "/graphql",
            json={
                "query": DEFER_PRACTICE_MUTATION,
                "variables": {"enrollmentId": str(enrollment.id_), "mode": "push"},
            },
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "errors" in response_data
        assert "does not have the required role" in response_data["errors"][0]["message"]
