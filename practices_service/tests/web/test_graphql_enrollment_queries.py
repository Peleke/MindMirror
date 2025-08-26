import pytest

GET_ENROLLMENT_BY_ID_QUERY = """
    query GetEnrollment($id: ID!) {
        enrollment(id: $id) {
            id_
            status
            userId
            programId
        }
    }
"""

GET_ENROLLMENTS_FOR_USER_QUERY = """
    query GetEnrollmentsForUser($userId: ID!) {
        enrollments(userId: $userId) {
            id_
            status
            userId
        }
    }
"""

GET_UPCOMING_PRACTICES_QUERY = """
    query GetUpcomingPractices {
        myUpcomingPractices {
            id_
            enrollmentId
            practiceId
            scheduledDate
        }
    }
"""


@pytest.mark.usefixtures("seed_db")
class TestEnrollmentQueries:
    @pytest.mark.asyncio
    async def test_user_can_get_own_enrollment(self, client, auth_headers_for, seed_db):
        client_user = seed_db["client_user_one"]
        enrollment_to_fetch = next(e for e in seed_db["enrollments"] if e.user_id == client_user.id)
        headers = auth_headers_for(client_user)
        variables = {"id": str(enrollment_to_fetch.id_)}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENT_BY_ID_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL Error: {result.get('errors')}"
        assert result["data"]["enrollment"]["id_"] == str(enrollment_to_fetch.id_)
        assert result["data"]["enrollment"]["userId"] == str(client_user.id)

    @pytest.mark.asyncio
    async def test_coach_can_get_verified_client_enrollment(self, client, auth_headers_for, seed_db):
        client_user = seed_db["client_user_one"]
        enrollment_to_fetch = next(e for e in seed_db["enrollments"] if e.user_id == client_user.id)
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"id": str(enrollment_to_fetch.id_)}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENT_BY_ID_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert result["data"]["enrollment"]["id_"] == str(enrollment_to_fetch.id_)

    @pytest.mark.asyncio
    async def test_user_cannot_get_unrelated_enrollment(self, client, auth_headers_for, seed_db):
        enrollment_of_client_one = next(e for e in seed_db["enrollments"] if e.user_id == seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_two"])
        variables = {"id": str(enrollment_of_client_one.id_)}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENT_BY_ID_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert result["data"]["enrollment"] is None

    @pytest.mark.asyncio
    async def test_coach_cannot_get_unrelated_client_enrollment(self, client, auth_headers_for, seed_db):
        enrollment_of_unrelated_client = next(
            e for e in seed_db["enrollments"] if e.user_id == seed_db["unrelated_client_user"].id
        )
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"id": str(enrollment_of_unrelated_client.id_)}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENT_BY_ID_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert result["data"]["enrollment"] is None

    @pytest.mark.asyncio
    async def test_user_can_get_own_enrollments_list(self, client, auth_headers_for, seed_db):
        client_user = seed_db["client_user_one"]
        headers = auth_headers_for(client_user)
        variables = {"userId": str(client_user.id)}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENTS_FOR_USER_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert len(result["data"]["enrollments"]) > 0
        assert all(e["userId"] == str(client_user.id) for e in result["data"]["enrollments"])

    @pytest.mark.asyncio
    async def test_coach_can_get_verified_client_enrollments_list(self, client, auth_headers_for, seed_db):
        client_user = seed_db["client_user_one"]
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"userId": str(client_user.id)}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENTS_FOR_USER_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert len(result["data"]["enrollments"]) > 0
        assert all(e["userId"] == str(client_user.id) for e in result["data"]["enrollments"])

    @pytest.mark.asyncio
    async def test_user_cannot_get_unrelated_enrollments_list(self, client, auth_headers_for, seed_db):
        client_one_id = str(seed_db["client_user_one"].id)
        headers = auth_headers_for(seed_db["client_user_two"])
        variables = {"userId": client_one_id}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENTS_FOR_USER_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert result["data"]["enrollments"] == []

    @pytest.mark.asyncio
    async def test_coach_cannot_get_unrelated_client_enrollments_list(self, client, auth_headers_for, seed_db):
        unrelated_client_id = str(seed_db["unrelated_client_user"].id)
        headers = auth_headers_for(seed_db["coach_user"])
        variables = {"userId": unrelated_client_id}

        response = await client.post(
            "/graphql", json={"query": GET_ENROLLMENTS_FOR_USER_QUERY, "variables": variables}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert result["data"]["enrollments"] == []


@pytest.mark.usefixtures("seed_db")
class TestProgressQueries:
    @pytest.mark.asyncio
    async def test_query_my_upcoming_practices_across_all_programs(self, client, auth_headers_for, seed_db):
        headers = auth_headers_for(seed_db["client_user_one"])

        response = await client.post("/graphql", json={"query": GET_UPCOMING_PRACTICES_QUERY}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"

        practices = result["data"]["myUpcomingPractices"]
        assert len(practices) > 0  # Seed data creates scheduled practices
        assert all("enrollmentId" in p for p in practices)
        assert all("practiceId" in p for p in practices)

    @pytest.mark.asyncio
    async def test_query_upcoming_practices_returns_empty_for_no_enrollment(self, client, auth_headers_for, seed_db):
        # Use a user who has no enrollments and therefore no upcoming practices
        headers = auth_headers_for(seed_db["unrelated_client_user"])

        response = await client.post("/graphql", json={"query": GET_UPCOMING_PRACTICES_QUERY}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result
        assert result["data"]["myUpcomingPractices"] == []
