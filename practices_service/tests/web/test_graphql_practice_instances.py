from datetime import date
from uuid import uuid4

import pytest


@pytest.mark.asyncio
class TestPracticeInstanceQueries:
    async def test_get_practice_instances_list_for_user(self, client, auth_headers_for, seed_db):
        user = seed_db["client_user_one"]
        headers = auth_headers_for(user)
        query = """
            query GetPracticeInstancesList($userId: ID!) {
              practiceInstances(userId: $userId) {
                id_
                title
                date
                userId
                templateId
                completedAt
              }
            }
        """
        variables = {"userId": str(user.id)}
        response = await client.post("/graphql", json={"query": query, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        instances = data["data"]["practiceInstances"]
        # The seed fixture creates instances for this user
        assert len(instances) > 0
        assert all(i["userId"] == str(user.id) for i in instances)

    async def test_get_practice_instance_details(self, client, auth_headers_for, seed_db):
        instance_to_fetch = seed_db["practice_instances"][0]
        user = seed_db["client_user_one"]
        headers = auth_headers_for(user)
        query = """
            query GetPracticeInstanceDetails($instanceId: ID!) {
                practiceInstance(id: $instanceId) {
                    id_
                    title
                    notes
                    completedAt
                    userId
                    prescriptions {
                        name
                        movements {
                            name
                            sets {
                                reps
                            }
                        }
                    }
                }
            }
        """
        variables = {"instanceId": str(instance_to_fetch.id_)}
        response = await client.post("/graphql", json={"query": query, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        instance = data["data"]["practiceInstance"]
        assert instance["id_"] == str(instance_to_fetch.id_)
        assert instance["userId"] == str(instance_to_fetch.user_id)


@pytest.mark.asyncio
class TestPracticeInstanceMutations:
    async def test_create_instance_from_template(self, client, auth_headers_for, seed_db):
        template = seed_db["practice_templates"][0]
        user = seed_db["client_user_one"]
        headers = auth_headers_for(user)
        mutation = """
            mutation CreateInstanceFromTemplate($templateId: ID!, $date: Date!) {
              createPracticeInstanceFromTemplate(templateId: $templateId, date: $date) {
                id_
                title
                templateId
                userId
              }
            }
        """
        variables = {"templateId": str(template.id_), "date": date.today().isoformat()}
        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        instance = data["data"]["createPracticeInstanceFromTemplate"]
        assert instance["title"] == template.title
        assert instance["templateId"] == str(template.id_)
        assert instance["userId"] == str(user.id)

    async def test_update_practice_instance(self, client, auth_headers_for, seed_db):
        instance_to_update = seed_db["practice_instances"][0]
        user = seed_db["client_user_one"]
        headers = auth_headers_for(user)

        mutation = """
            mutation UpdatePracticeInstance($instanceId: ID!, $input: PracticeInstanceUpdateInput!) {
              updatePracticeInstance(id: $instanceId, input: $input) {
                id_
                title
                notes
                completedAt
              }
            }
        """
        variables = {
            "instanceId": str(instance_to_update.id_),
            "input": {
                "title": "Updated Title",
                "notes": "These are updated notes.",
                "completedAt": date.today().isoformat(),
            },
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        updated_instance = data["data"]["updatePracticeInstance"]
        assert updated_instance["id_"] == str(instance_to_update.id_)
        assert updated_instance["title"] == "Updated Title"
        assert updated_instance["notes"] == "These are updated notes."
        assert updated_instance["completedAt"] == date.today().isoformat()

    async def test_delete_practice_instance(self, client, auth_headers_for, seed_db):
        instance_to_delete = seed_db["practice_instances"][0]
        user = seed_db["client_user_one"]
        headers = auth_headers_for(user)
        mutation = """
            mutation DeletePracticeInstance($instanceId: ID!) {
              deletePracticeInstance(id: $instanceId)
            }
        """
        variables = {"instanceId": str(instance_to_delete.id_)}

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        assert data["data"]["deletePracticeInstance"] is True
