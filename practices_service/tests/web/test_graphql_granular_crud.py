"""
GraphQL CRUD Tests for Granular Workout Management

This module tests the GraphQL mutations for:
- Phase 1: Instance Management (Set/Movement/Prescription Instances)
- Phase 2: Template Management (Set/Movement/Prescription Templates)

Tests follow TDD approach and validate the entire stack through GraphQL layer.
"""

from datetime import date, datetime
from uuid import uuid4

import pytest


class TestSetInstanceCRUD:
    """Phase 1.1: Set Instance Management - Real-time workout tracking"""

    @pytest.mark.asyncio
    async def test_create_set_instance_during_workout(self, client, auth_headers_for, seed_db):
        """Client can create set instance during workout"""
        # Get a movement instance from seeded data
        movement_instance_id = seed_db["movement_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation CreateSetInstance($input: SetInstanceCreateInput!) {
            createSetInstance(input: $input) {
                id_
                reps
                loadValue
                duration
                complete
                perceivedExertion
                notes
                movementInstanceId
            }
        }
        """

        variables = {
            "input": {
                "movementInstanceId": str(movement_instance_id),
                "position": 1,
                "reps": 10,
                "loadValue": 135.0,
                "loadUnit": "pounds",
                "duration": None,
                "restDuration": 90,
                "complete": False,
                "perceivedExertion": 2,
                "notes": "Felt strong on this set",
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createSetInstance"]
        assert data["reps"] == 10
        assert data["loadValue"] == 135.0
        assert data["complete"] is False
        assert data["notes"] == "Felt strong on this set"
        assert data["movementInstanceId"] == str(movement_instance_id)

    @pytest.mark.asyncio
    async def test_update_set_with_actual_performance(self, client, auth_headers_for, seed_db):
        """Client can update set with actual reps/weight/duration"""
        set_instance_id = seed_db["set_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation UpdateSetInstance($id: ID!, $input: SetInstanceUpdateInput!) {
            updateSetInstance(id: $id, input: $input) {
                id_
                reps
                loadValue
                duration
                complete
                perceivedExertion
                notes
                completedAt
            }
        }
        """

        variables = {
            "id": str(set_instance_id),
            "input": {
                "reps": 8,  # Actual reps performed (less than prescribed)
                "loadValue": 140.0,  # Actual weight used
                "perceivedExertion": 2,
                "notes": "Struggled on last 2 reps",
                "complete": True,
            },
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["updateSetInstance"]
        print(data)
        assert data["reps"] == 8
        assert data["loadValue"] == 140.0
        assert data["complete"] is True
        assert data["perceivedExertion"] == 2
        assert data["notes"] == "Struggled on last 2 reps"
        assert data["completedAt"] is not None

    @pytest.mark.asyncio
    async def test_mark_set_complete(self, client, auth_headers_for, seed_db):
        """Client can mark set as complete"""
        set_instance_id = seed_db["set_instances"][1].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation CompleteSetInstance($id: ID!) {
            completeSetInstance(id: $id) {
                id_
                complete
                completedAt
            }
        }
        """

        variables = {"id": str(set_instance_id)}
        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["completeSetInstance"]
        assert data["complete"] is True
        assert data["completedAt"] is not None

    @pytest.mark.asyncio
    async def test_client_cannot_modify_other_users_sets(self, client, auth_headers_for, seed_db):
        """Client cannot modify other users' set instances"""
        set_instance_id = seed_db["set_instances"][0].id_  # Belongs to client_user_one
        headers = auth_headers_for(seed_db["unrelated_client_user"])

        mutation = """
        mutation UpdateSetInstance($id: ID!, $input: SetInstanceUpdateInput!) {
            updateSetInstance(id: $id, input: $input) {
                id_
                reps
            }
        }
        """

        variables = {"id": str(set_instance_id), "input": {"reps": 999}}

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" in result
        assert "not authorized" in str(result["errors"][0]).lower()

    @pytest.mark.asyncio
    async def test_coach_can_view_but_not_modify_client_sets(self, client, auth_headers_for, seed_db):
        """Coach can view but not modify client set instances"""
        set_instance_id = seed_db["set_instances"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        # Coach can query set
        query = """
        query GetSetInstance($id: ID!) {
            setInstance(id: $id) {
                id_
                reps
                loadValue
                complete
            }
        }
        """

        response = await client.post(
            "/graphql", json={"query": query, "variables": {"id": str(set_instance_id)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        assert result["data"]["setInstance"]["id_"] == str(set_instance_id)

        # But coach cannot modify
        mutation = """
        mutation UpdateSetInstance($id: ID!, $input: SetInstanceUpdateInput!) {
            updateSetInstance(id: $id, input: $input) {
                id_
                reps
            }
        }
        """

        variables = {"id": str(set_instance_id), "input": {"reps": 999}}

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" in result
        assert "not authorized" in str(result["errors"][0]).lower()

    @pytest.mark.asyncio
    async def test_set_completion_triggers_movement_completion_check(self, client, auth_headers_for, seed_db):
        """Set completion triggers movement completion check"""
        # Get movement with incomplete sets
        movement_instance_id = seed_db["movement_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        # Complete all sets in the movement
        for set_instance in seed_db["set_instances"]:
            if set_instance.movement_instance_id == movement_instance_id:
                mutation = """
                mutation CompleteSetInstance($id: ID!) {
                    completeSetInstance(id: $id) {
                        id_
                        complete
                    }
                }
                """

                response = await client.post(
                    "/graphql", json={"query": mutation, "variables": {"id": str(set_instance.id_)}}, headers=headers
                )
                assert response.status_code == 200
                result = response.json()
                assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"

        # Verify movement is now complete
        query = """
        query GetMovementInstance($id: ID!) {
            movementInstance(id: $id) {
                id_
                complete
                completedAt
                sets {
                    complete
                }
            }
        }
        """

        response = await client.post(
            "/graphql", json={"query": query, "variables": {"id": str(movement_instance_id)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["movementInstance"]
        assert all(set_data["complete"] for set_data in data["sets"])
        assert data["complete"] is True
        assert data["completedAt"] is not None


class TestMovementInstanceCRUD:
    """Phase 1.2: Movement Instance Management - Exercise-level workout customization"""

    @pytest.mark.asyncio
    async def test_create_movement_instance_from_template(self, client, auth_headers_for, seed_db):
        """Client can create movement instance from template"""
        prescription_instance_id = seed_db["prescription_instances"][0].id_
        movement_template_id = seed_db["movement_templates"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation CreateMovementFromTemplate($input: MovementInstanceFromTemplateInput!) {
            createMovementInstanceFromTemplate(input: $input) {
                id_
                name
                templateId
                prescriptionInstanceId
                sets {
                    id_
                    reps
                }
            }
        }
        """

        variables = {
            "input": {
                "prescriptionInstanceId": str(prescription_instance_id),
                "movementTemplateId": str(movement_template_id),
                "position": 99,  # Add to the end
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createMovementInstanceFromTemplate"]
        assert data["templateId"] == str(movement_template_id)
        assert data["prescriptionInstanceId"] == str(prescription_instance_id)
        # Check if sets were instantiated from the template
        assert len(data["sets"]) > 0

    @pytest.mark.asyncio
    async def test_create_standalone_movement_instance(self, client, auth_headers_for, seed_db):
        """Client can create a new, standalone movement instance during a workout"""
        prescription_instance_id = seed_db["prescription_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation CreateMovementInstance($input: MovementInstanceCreateInput!) {
            createMovementInstance(input: $input) {
                id_
                name
                metricUnit
                metricValue
                templateId
                sets {
                    reps
                }
            }
        }
        """

        variables = {
            "input": {
                "prescriptionInstanceId": str(prescription_instance_id),
                "name": "Spontaneous Bicep Curls",
                "position": 98,
                "metricUnit": "ITERATIVE",
                "metricValue": 12.0,
                "prescribedSets": 3,
                "sets": [
                    {"position": 0, "reps": 12},
                    {"position": 1, "reps": 12},
                    {"position": 2, "reps": 12},
                ],
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createMovementInstance"]
        assert data["name"] == "Spontaneous Bicep Curls"
        assert data["templateId"] is None  # Not from a template
        assert len(data["sets"]) == 3

    @pytest.mark.asyncio
    async def test_update_movement_parameters_during_workout(self, client, auth_headers_for, seed_db):
        """Client can update movement notes and rest duration"""
        movement_instance_id = seed_db["movement_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation UpdateMovementInstance($id: ID!, $input: MovementInstanceUpdateInput!) {
            updateMovementInstance(id: $id, input: $input) {
                id_
                notes
                restDuration
            }
        }
        """

        variables = {
            "id": str(movement_instance_id),
            "input": {"notes": "Felt a pinch in my shoulder, reduced weight.", "restDuration": 120.0},
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["updateMovementInstance"]
        assert data["notes"] == "Felt a pinch in my shoulder, reduced weight."
        assert data["restDuration"] == 120.0

    @pytest.mark.asyncio
    async def test_add_set_to_movement_during_workout(self, client, auth_headers_for, seed_db):
        """Client can add a new set to a movement instance mid-workout"""
        movement_instance_id = seed_db["movement_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation CreateSetInstance($input: SetInstanceCreateInput!) {
            createSetInstance(input: $input) {
                id_
                reps
            }
        }
        """

        variables = {
            "input": {
                "movementInstanceId": str(movement_instance_id),
                "position": 10,  # Add as the last set
                "reps": 5,  # A drop set
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        assert result["data"]["createSetInstance"]["reps"] == 5

    @pytest.mark.asyncio
    async def test_movement_completion_based_on_set_completion(self, client, auth_headers_for, seed_db):
        """Movement completes automatically when all its sets are complete"""
        movement_instance = seed_db["movement_instances"][0]
        headers = auth_headers_for(seed_db["client_user_one"])

        # Ensure all sets are marked as complete
        for s in movement_instance.sets:
            set_mutation = """
            mutation UpdateSetInstance($id: ID!, $input: SetInstanceUpdateInput!) {
                updateSetInstance(id: $id, input: $input) { id_ }
            }
            """
            await client.post(
                "/graphql",
                json={"query": set_mutation, "variables": {"id": str(s.id_), "input": {"complete": True}}},
                headers=headers,
            )

        # Query the movement's completion status
        query = """
        query GetMovementInstance($id: ID!) {
            movementInstance(id: $id) {
                id_
                complete
            }
        }
        """
        response = await client.post(
            "/graphql", json={"query": query, "variables": {"id": str(movement_instance.id_)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["movementInstance"]
        assert data["complete"] is True

    @pytest.mark.asyncio
    async def test_exercise_database_integration(self, client, auth_headers_for, seed_db):
        """Movement instance can link to and retrieve data from an Exercise Database"""
        movement_instance_id = seed_db["movement_instances"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        # This test assumes the exercise field resolver exists and can fetch from a mock/real service
        query = """
        query GetMovementWithExercise($id: ID!) {
            movementInstance(id: $id) {
                id_
                name
                exercise {
                    id
                }
            }
        }
        """
        response = await client.post(
            "/graphql", json={"query": query, "variables": {"id": str(movement_instance_id)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"


class TestPrescriptionInstanceCRUD:
    """Phase 1.3: Prescription Instance Management - Workout block organization"""

    @pytest.mark.asyncio
    async def test_create_prescription_instance_warmup(self, client, auth_headers_for, seed_db):
        """Client can create a new prescription instance (e.g., a warm-up block)"""
        practice_instance_id = seed_db["practice_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation CreatePrescriptionInstance($input: PrescriptionInstanceCreateInput!) {
            createPrescriptionInstance(input: $input) {
                id_
                name
                block
                movements {
                    name
                    sets {
                        duration
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "practiceInstanceId": str(practice_instance_id),
                "name": "Dynamic Warm-up",
                "block": "warmup",
                "position": 0,
                "movements": [
                    {
                        "name": "Jumping Jacks",
                        "position": 0,
                        "metricUnit": "TEMPORAL",
                        "metricValue": 60,
                        "prescribedSets": 1,
                        "sets": [{"position": 0, "duration": 60}],
                    },
                    {
                        "name": "High Knees",
                        "position": 1,
                        "metricUnit": "TEMPORAL",
                        "metricValue": 60,
                        "prescribedSets": 1,
                        "sets": [{"position": 0, "duration": 60}],
                    },
                ],
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createPrescriptionInstance"]
        print(data)
        assert data["name"] == "Dynamic Warm-up"
        assert data["block"] == "WARMUP"
        assert len(data["movements"]) == 2

    @pytest.mark.asyncio
    async def test_update_prescription_during_workout(self, client, auth_headers_for, seed_db):
        """Client can update prescription notes during workout"""
        prescription_instance_id = seed_db["prescription_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation UpdatePrescriptionInstance($id: ID!, $input: PrescriptionInstanceUpdateInput!) {
            updatePrescriptionInstance(id: $id, input: $input) {
                id_
                notes
            }
        }
        """

        variables = {
            "id": str(prescription_instance_id),
            "input": {"notes": "This warm-up felt great. Ready for the main workout."},
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["updatePrescriptionInstance"]
        assert data["notes"] == "This warm-up felt great. Ready for the main workout."

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Reordering is not supported.")
    async def test_reorder_movements_within_prescription(self, client, auth_headers_for, seed_db):
        """Client can reorder movements within a prescription"""
        prescription_instance_id = seed_db["prescription_instances"][0].id_
        movements = seed_db["movement_instances"]
        headers = auth_headers_for(seed_db["client_user_one"])

        # Get movements belonging to this prescription
        movements_in_prescription = [m for m in movements if m.prescription_instance_id == prescription_instance_id]
        original_order_ids = [m.id_ for m in sorted(movements_in_prescription, key=lambda x: x.position)]

        # Reverse the order
        new_order = [
            {"movementId": str(original_order_ids[1]), "position": 0},
            {"movementId": str(original_order_ids[0]), "position": 1},
        ]

        mutation = """
        mutation ReorderMovements($prescriptionId: ID!, $newOrder: [MovementOrderInput!]!) {
            reorderMovements(prescriptionId: $prescriptionId, newOrder: $newOrder) {
                id_
                movements {
                    id_
                    name
                    position
                }
            }
        }
        """

        variables = {"prescriptionId": str(prescription_instance_id), "newOrder": new_order}

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"

        data = result["data"]["reorderMovements"]
        reordered_movements = data["movements"]
        assert reordered_movements[0]["id_"] == str(original_order_ids[1])
        assert reordered_movements[0]["position"] == 0
        assert reordered_movements[1]["id_"] == str(original_order_ids[0])
        assert reordered_movements[1]["position"] == 1

    @pytest.mark.asyncio
    async def test_prescription_completion_based_on_movement_completion(
        self, session, client, auth_headers_for, seed_db
    ):
        """Prescription completes automatically when all its movements are complete"""
        prescription_instance = seed_db["prescription_instances"][0]
        headers = auth_headers_for(seed_db["client_user_one"])

        # Get the movements for this specific prescription instance first
        query_movements = """
        query GetPrescriptionInstance($id: ID!) {
            prescriptionInstance(id: $id) {
                movements {
                    sets {
                        id_
                    }
                }
            }
        }
        """
        response = await client.post(
            "/graphql",
            json={"query": query_movements, "variables": {"id": str(prescription_instance.id_)}},
            headers=headers,
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"

        # Complete all sets that belong to this specific prescription's movements
        movements = result["data"]["prescriptionInstance"]["movements"]
        for movement in movements:
            for set_data in movement["sets"]:
                await client.post(
                    "/graphql",
                    json={"query": 'mutation { completeSetInstance(id:"' + set_data["id_"] + '") { id_ } }'},
                    headers=headers,
                )

        # Query the prescription's completion status
        query = """
        query GetPrescriptionInstance($id: ID!) {
            prescriptionInstance(id: $id) {
                id_
                complete
            }
        }
        """
        response = await client.post(
            "/graphql", json={"query": query, "variables": {"id": str(prescription_instance.id_)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["prescriptionInstance"]
        assert data["complete"] is True

    @pytest.mark.asyncio
    async def test_block_specific_validation(self, client, auth_headers_for, seed_db):
        """Prescription creation validates against block-specific rules"""
        practice_instance_id = seed_db["practice_instances"][0].id_
        headers = auth_headers_for(seed_db["client_user_one"])

        mutation = """
        mutation CreatePrescriptionInstance($input: PrescriptionInstanceCreateInput!) {
            createPrescriptionInstance(input: $input) { id_ }
        }
        """

        # Test invalid block type
        variables = {
            "input": {
                "practiceInstanceId": str(practice_instance_id),
                "name": "Invalid Block",
                "block": "INVALID_BLOCK",
                "position": 1,
            }
        }
        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" in result
        assert "checkviolationerror" in str(result["errors"][0]["message"]).lower()


class TestSetTemplateCRUD:
    """Phase 2.1: Set Template Management - Reusable set components"""

    @pytest.mark.asyncio
    async def test_coach_create_reusable_set_template(self, client, auth_headers_for, seed_db):
        """Coach can create reusable set templates"""
        movement_template_id = seed_db["movement_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        mutation = """
        mutation CreateSetTemplate($input: SetTemplateCreateInput!) {
            createSetTemplate(input: $input) {
                id_
                reps
                loadValue
                loadUnit
                restDuration
                movementTemplateId
            }
        }
        """

        variables = {
            "input": {
                "movementTemplateId": str(movement_template_id),
                "position": 1,
                "reps": 12,
                "loadValue": 100.0,
                "loadUnit": "pounds",
                "restDuration": 60,
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createSetTemplate"]
        assert data["reps"] == 12
        assert data["loadValue"] == 100.0
        assert data["loadUnit"] == "POUNDS"
        assert data["movementTemplateId"] == str(movement_template_id)

    @pytest.mark.asyncio
    async def test_coach_update_set_template_parameters(self, client, auth_headers_for, seed_db):
        """Coach can update set template parameters"""
        set_template_id = seed_db["set_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        mutation = """
        mutation UpdateSetTemplate($id: ID!, $input: SetTemplateUpdateInput!) {
            updateSetTemplate(id: $id, input: $input) {
                id_
                reps
                loadValue
            }
        }
        """

        variables = {
            "id": str(set_template_id),
            "input": {"reps": 15, "loadValue": 95.0},  # Increase reps  # Decrease weight
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["updateSetTemplate"]
        assert data["reps"] == 15
        assert data["loadValue"] == 95.0

    @pytest.mark.asyncio
    async def test_set_template_deletion_handles_existing_instances(self, client, auth_headers_for, seed_db):
        """Set template deletion handles existing instances (soft delete or warning)"""
        set_template_id = seed_db["set_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        # Verify there are instances using this template
        query = """
        query GetSetInstancesByTemplate($templateId: ID!) {
            setInstancesByTemplate(templateId: $templateId) {
                id_
            }
        }
        """
        response = await client.post(
            "/graphql", json={"query": query, "variables": {"templateId": str(set_template_id)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]["setInstancesByTemplate"]) > 0

        # Attempt to delete the template
        mutation = """
        mutation DeleteSetTemplate($id: ID!) {
            deleteSetTemplate(id: $id)
        }
        """

        response = await client.post(
            "/graphql", json={"query": mutation, "variables": {"id": str(set_template_id)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()

        # Deletion should either fail or the flag `canBeDeleted` should be false
        assert "errors" in result
        assert "cannot delete set template" in str(result["errors"][0]).lower()

    @pytest.mark.asyncio
    async def test_load_unit_and_rep_range_validation(self, client, auth_headers_for, seed_db):
        """Set template creation validates load units and rep ranges"""
        movement_template_id = seed_db["movement_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        mutation = """
        mutation CreateSetTemplate($input: SetTemplateCreateInput!) {
            createSetTemplate(input: $input) {
                id_
                reps
                loadValue
                loadUnit
            }
        }
        """

        # Test invalid rep range
        variables = {
            "input": {
                "movementTemplateId": str(movement_template_id),
                "position": 1,
                "reps": -5,  # Invalid negative reps
                "loadValue": 135.0,
                "loadUnit": "pounds",
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" in result
        assert "checkviolationerror" in str(result["errors"][0]).lower()

        # Test invalid load unit
        variables["input"]["reps"] = 10
        variables["input"]["loadUnit"] = "invalid_unit"

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" in result
        assert "checkviolationerror" in str(result["errors"][0]).lower()


class TestMovementTemplateCRUD:
    """Phase 2.2: Movement Template Management - Reusable exercises"""

    @pytest.mark.asyncio
    async def test_coach_create_movement_template_with_exercise_reference(self, client, auth_headers_for, seed_db):
        """Coach can create movement templates with exercise references"""
        prescription_template_id = seed_db["prescription_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        mutation = """
        mutation CreateMovementTemplate($input: MovementTemplateCreateInput!) {
            createMovementTemplate(input: $input) {
                id_
                name
                metricUnit
                metricValue
                exerciseId
                prescriptionTemplateId
                sets {
                    id_
                    reps
                    loadValue
                }
            }
        }
        """

        mock_exercise_id = str(uuid4())
        variables = {
            "input": {
                "prescriptionTemplateId": str(prescription_template_id),
                "name": "Barbell Back Squat",
                "position": 1,
                "metricUnit": "iterative",
                "metricValue": 10.0,
                "movementClass": "strength",
                "prescribedSets": 3,
                "restDuration": 180,
                "exerciseId": mock_exercise_id,  # Reference to exercise database
                "sets": [
                    {"position": 0, "reps": 10, "loadValue": 185.0, "loadUnit": "pounds", "restDuration": 180},
                    {"position": 1, "reps": 10, "loadValue": 185.0, "loadUnit": "pounds", "restDuration": 180},
                    {"position": 2, "reps": 10, "loadValue": 185.0, "loadUnit": "pounds", "restDuration": 0},
                ],
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createMovementTemplate"]
        assert data["name"] == "Barbell Back Squat"
        assert data["exerciseId"] == mock_exercise_id
        assert len(data["sets"]) == 3
        assert all(s["reps"] == 10 for s in data["sets"])

    @pytest.mark.asyncio
    async def test_coach_define_default_sets_for_movement_template(self, client, auth_headers_for, seed_db):
        """Coach can define default sets for movement templates"""
        prescription_template_id = seed_db["prescription_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        mutation = """
        mutation CreateMovementTemplate($input: MovementTemplateCreateInput!) {
            createMovementTemplate(input: $input) {
                id_
                name
                prescribedSets
                sets {
                    position
                    reps
                    loadValue
                    loadUnit
                    restDuration
                }
            }
        }
        """

        variables = {
            "input": {
                "prescriptionTemplateId": str(prescription_template_id),
                "name": "Progressive Push-ups",
                "position": 1,
                "metricUnit": "iterative",
                "metricValue": 12.0,
                "movementClass": "strength",
                "prescribedSets": 4,
                "sets": [
                    {"position": 0, "reps": 15, "restDuration": 60},  # Warm-up set
                    {"position": 1, "reps": 12, "restDuration": 90},  # Working set
                    {"position": 2, "reps": 10, "restDuration": 90},  # Working set
                    {"position": 3, "reps": 8, "restDuration": 0},  # Drop set
                ],
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createMovementTemplate"]
        assert data["prescribedSets"] == 4
        assert len(data["sets"]) == 4
        # Verify progressive rep scheme
        assert data["sets"][0]["reps"] == 15
        assert data["sets"][1]["reps"] == 12
        assert data["sets"][2]["reps"] == 10
        assert data["sets"][3]["reps"] == 8

    @pytest.mark.asyncio
    async def test_movement_template_updates_dont_affect_existing_instances(self, client, auth_headers_for, seed_db):
        """Movement template updates don't affect existing instances"""
        movement_template_id = seed_db["movement_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        # Get existing instances using this template
        query = """
        query GetMovementInstancesUsingTemplate($templateId: ID!) {
            movementInstancesByTemplate(templateId: $templateId) {
                id_
                name
                prescribedSets
            }
        }
        """

        response = await client.post(
            "/graphql", json={"query": query, "variables": {"templateId": str(movement_template_id)}}, headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        instances_before = result.get("data", {}).get("movementInstancesByTemplate", [])

        # Update the template
        mutation = """
        mutation UpdateMovementTemplate($id: ID!, $input: MovementTemplateUpdateInput!) {
            updateMovementTemplate(id: $id, input: $input) {
                id_
                name
                prescribedSets
            }
        }
        """

        variables = {
            "id": str(movement_template_id),
            "input": {"name": "Updated Movement Name", "prescribedSets": 5},  # Changed from original
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"

        # Verify existing instances unchanged
        if instances_before:
            instance_query = """
            query GetMovementInstance($id: ID!) {
                movementInstance(id: $id) {
                    id_
                    name
                    prescribedSets
                }
            }
            """

            response = await client.post(
                "/graphql",
                json={"query": instance_query, "variables": {"id": instances_before[0]["id_"]}},
                headers=headers,
            )
            assert response.status_code == 200
            result = response.json()
            assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
            # Instance should retain original values
            assert result["data"]["movementInstance"]["name"] != "Updated Movement Name"

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Template sharing is not implemented yet.")
    async def test_template_sharing_between_coaches(self, client, auth_headers_for, seed_db):
        """Template sharing between coaches"""
        movement_template_id = seed_db["movement_templates"][0].id_
        coach1_headers = auth_headers_for(seed_db["coach_user"])
        coach2_headers = auth_headers_for(seed_db["coach2_user"])  # Assumes a second coach exists in seed data

        # Coach 1 shares template with Coach 2
        mutation = """
        mutation ShareMovementTemplate($templateId: ID!, $shareWithUserId: ID!) {
            shareMovementTemplate(templateId: $templateId, shareWithUserId: $shareWithUserId) {
                id_
                name
                sharedWith {
                    userId
                    permissions
                }
            }
        }
        """

        variables = {"templateId": str(movement_template_id), "shareWithUserId": str(seed_db["coach2_user"].id)}

        response = await client.post(
            "/graphql", json={"query": mutation, "variables": variables}, headers=coach1_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"

        # Coach 2 can now access the template
        query = """
        query GetSharedMovementTemplate($id: ID!) {
            movementTemplate(id: $id) {
                id_
                name
                canEdit
                sharedBy {
                    id_
                    name
                }
            }
        }
        """

        response = await client.post(
            "/graphql", json={"query": query, "variables": {"id": str(movement_template_id)}}, headers=coach2_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["movementTemplate"]
        assert data["canEdit"] is False  # Read-only access
        assert data["sharedBy"]["id_"] == str(seed_db["coach_user"].id)


class TestPrescriptionTemplateCRUD:
    """Phase 2.3: Prescription Template Management - Reusable workout blocks"""

    @pytest.mark.asyncio
    async def test_coach_create_prescription_template_by_block_type(self, client, auth_headers_for, seed_db):
        """Coach can create prescription templates by block type"""
        practice_template_id = seed_db["practice_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        mutation = """
        mutation CreatePrescriptionTemplate($input: PrescriptionTemplateCreateInput!) {
            createPrescriptionTemplate(input: $input) {
                id_
                name
                block
                prescribedRounds
                practiceTemplateId
                movements {
                    id_
                    name
                    position
                }
            }
        }
        """

        variables = {
            "input": {
                "practiceTemplateId": str(practice_template_id),
                "name": "Strength Circuit",
                "block": "workout",
                "position": 1,
                "prescribedRounds": 3,
                "movements": [
                    {
                        "name": "Deadlift",
                        "position": 0,
                        "metricUnit": "iterative",
                        "metricValue": 5.0,
                        "movementClass": "strength",
                        "prescribedSets": 3,
                        "restDuration": 180,
                        "sets": [
                            {"position": 0, "reps": 5, "loadValue": 225.0, "loadUnit": "pounds", "restDuration": 180},
                            {"position": 1, "reps": 5, "loadValue": 245.0, "loadUnit": "pounds", "restDuration": 180},
                            {"position": 2, "reps": 5, "loadValue": 265.0, "loadUnit": "pounds", "restDuration": 0},
                        ],
                    },
                    {
                        "name": "Pull-ups",
                        "position": 1,
                        "metricUnit": "iterative",
                        "metricValue": 8.0,
                        "movementClass": "strength",
                        "prescribedSets": 3,
                        "restDuration": 120,
                        "sets": [
                            {"position": 0, "reps": 8, "restDuration": 120},
                            {"position": 1, "reps": 8, "restDuration": 120},
                            {"position": 2, "reps": 8, "restDuration": 0},
                        ],
                    },
                ],
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createPrescriptionTemplate"]
        assert data["name"] == "Strength Circuit"
        assert data["block"] == "WORKOUT"
        assert data["prescribedRounds"] == 3
        assert len(data["movements"]) == 2
        assert data["movements"][0]["name"] == "Deadlift"
        assert data["movements"][1]["name"] == "Pull-ups"

    @pytest.mark.asyncio
    async def test_coach_define_movement_sequences_in_templates(self, client, auth_headers_for, seed_db):
        """Coach can define movement sequences in templates"""
        practice_template_id = seed_db["practice_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        mutation = """
        mutation CreatePrescriptionTemplate($input: PrescriptionTemplateCreateInput!) {
            createPrescriptionTemplate(input: $input) {
                id_
                name
                movements {
                    name
                    position
                }
            }
        }
        """

        variables = {
            "input": {
                "practiceTemplateId": str(practice_template_id),
                "name": "HIIT Sequence",
                "block": "workout",
                "position": 1,
                "movements": [
                    {
                        "name": "Burpees",
                        "position": 0,
                        "metricUnit": "temporal",
                        "metricValue": 45.0,
                        "movementClass": "conditioning",
                        "prescribedSets": 1,
                        "sets": [{"position": 0, "duration": 45, "restDuration": 15}],
                    },
                    {
                        "name": "Mountain Climbers",
                        "position": 1,
                        "metricUnit": "temporal",
                        "metricValue": 45.0,
                        "movementClass": "conditioning",
                        "prescribedSets": 1,
                        "sets": [{"position": 0, "duration": 45, "restDuration": 15}],
                    },
                    {
                        "name": "Jump Squats",
                        "position": 2,
                        "metricUnit": "temporal",
                        "metricValue": 45.0,
                        "movementClass": "power",
                        "prescribedSets": 1,
                        "sets": [{"position": 0, "duration": 45, "restDuration": 60}],
                    },
                ],
            }
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()

        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
        data = result["data"]["createPrescriptionTemplate"]
        movements = data["movements"]

        # Verify sequence order and timing
        assert movements[0]["position"] == 0
        assert movements[1]["position"] == 1
        assert movements[2]["position"] == 2

    @pytest.mark.asyncio
    async def test_prescription_template_reuse_across_programs(self, client, auth_headers_for, seed_db):
        """Prescription template reuse across programs"""
        prescription_template_id = seed_db["prescription_templates"][0].id_
        headers = auth_headers_for(seed_db["coach_user"])

        # Use template in multiple practice templates
        mutation = """
        mutation AddPrescriptionTemplateToProgram($programId: ID!, $prescriptionTemplateId: ID!, $position: Int!) {
            addPrescriptionTemplateToProgram(
                programId: $programId,
                prescriptionTemplateId: $prescriptionTemplateId,
                position: $position
            ) {
                id_
                name
                practiceLinks {
                    practiceTemplate {
                        prescriptions {
                            id_
                            name
                        }
                    }
                }
            }
        }
        """

        variables = {
            "programId": str(seed_db["programs"][0].id_),
            "prescriptionTemplateId": str(prescription_template_id),
            "position": 1,
        }

        response = await client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "errors" not in result, f"GraphQL errors: {result.get('errors')}"
