from uuid import uuid4

import pytest


@pytest.mark.asyncio
class TestPracticeTemplateQueries:
    async def test_get_practice_templates_list(self, client, auth_headers_for, seed_db):
        headers = auth_headers_for(seed_db["coach_user"])
        query = """
            query GetPracticeTemplatesList {
              practiceTemplates {
                id_
                title
                description
                userId
              }
            }
        """
        response = await client.post("/graphql", json={"query": query}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        templates = data["data"]["practiceTemplates"]
        assert len(templates) > 0
        assert templates[0]["userId"] == str(seed_db["coach_user"].id)

    async def test_get_practice_template_details(self, client, auth_headers_for, seed_db):
        template_to_fetch = seed_db["practice_templates"][0]
        headers = auth_headers_for(seed_db["coach_user"])
        query = """
            query GetPracticeTemplateDetails($templateId: ID!) {
              practiceTemplate(id: $templateId) {
                id_
                title
                prescriptions {
                  id_
                  name
                  movements {
                    id_
                    name
                  }
                }
              }
            }
        """
        variables = {"templateId": str(template_to_fetch.id_)}
        response = await client.post("/graphql", json={"query": query, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        template = data["data"]["practiceTemplate"]
        assert template["id_"] == str(template_to_fetch.id_)
        assert template["title"] == template_to_fetch.title
        assert len(template["prescriptions"]) > 0


@pytest.mark.asyncio
class TestPracticeTemplateMutations:
    async def test_create_practice_template(self, client, auth_headers_for, seed_db):
        headers = auth_headers_for(seed_db["coach_user"])
        mutation = """
            mutation CreatePracticeTemplate($input: PracticeTemplateCreateInput!) {
              createPracticeTemplate(input: $input) {
                id_
                title
                description
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
        variables = {
            "input": {
                "title": "New Template from Test",
                "description": "A detailed description.",
                "prescriptions": [
                    {
                        "name": "Warmup",
                        "block": "warmup",
                        "position": 1,
                        "movements": [
                            {
                                "name": "Jumping Jacks",
                                "position": 1,
                                "metricUnit": "iterative",
                                "metricValue": 50,
                                "sets": [{"position": 1, "reps": 50}],
                            }
                        ],
                    }
                ],
            }
        }
        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        template = data["data"]["createPracticeTemplate"]
        assert template["title"] == "New Template from Test"
        assert len(template["prescriptions"]) == 1
        assert template["prescriptions"][0]["name"] == "Warmup"

    async def test_delete_practice_template(self, client, auth_headers_for, seed_db):
        # Use the template specifically created for deletion tests, which is not tied to any programs.
        # This will be the third template created in the seed_db fixture.
        template_to_delete = seed_db["practice_templates"][2]
        headers = auth_headers_for(seed_db["coach_user"])
        mutation = """
            mutation DeletePracticeTemplate($templateId: ID!) {
              deletePracticeTemplate(id: $templateId)
            }
        """
        variables = {"templateId": str(template_to_delete.id_)}

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

        assert data["data"]["deletePracticeTemplate"] is True

        # Verify it's gone
        query = """
            query GetPracticeTemplateDetails($templateId: ID!) {
              practiceTemplate(id: $templateId) {
                id_
              }
            }
        """
        verify_response = await client.post("/graphql", json={"query": query, "variables": variables}, headers=headers)
        verify_data = verify_response.json()
        assert verify_data["data"]["practiceTemplate"] is None
