# import uuid
# from datetime import date
# from typing import Optional
#
# import pytest
# from fastapi.testclient import TestClient
#
# from practices.repository.models import (
#     PracticeModel,
#     ProgramModel,
#     ProgramPracticeLinkModel,
#     ProgramTagModel,
# )
# from practices.repository.repositories import PracticeRepository, ProgramRepository
# from practices.repository.uow import get_uow
# from practices.service.services import PracticeService, ProgramService
# from practices.web.app import app
#
#
# @pytest.mark.asyncio
# @pytest.mark.skip(reason="Obsolete")
# class TestProgramQuery:
#     @pytest.mark.asyncio
#     async def test_programs_query(self, create_tables, client, sample_program_id, docker_compose_up_down):
#         """Test querying all programs."""
#         query = """
#         query {
#             programs {
#                 id_
#                 name
#                 description
#                 level
#                 createdAt
#                 modifiedAt
#                 tags {
#                     id_
#                     name
#                 }
#                 practiceLinks {
#                     id_
#                     sequenceOrder
#                     intervalDaysAfter
#                     practice {
#                         id_
#                         title
#                     }
#                 }
#                 practiceCount
#                 totalDurationDays
#             }
#         }
#         """
#         response = await client.post("/graphql", json={"query": query})
#         assert response.status_code == 200
#         data = response.json()
#         assert "data" in data, f"Response missing 'data': {data}"
#         assert "programs" in data["data"], f"Response data missing 'programs': {data['data']}"
#         programs = data["data"]["programs"]
#         assert len(programs) > 0
#
#         # Find our created program
#         test_program = next((p for p in programs if p["id_"] == sample_program_id), None)
#         assert test_program is not None
#         assert test_program["name"] == "Test Program for GraphQL Tests"
#         assert test_program["description"] == "A program for GraphQL testing"
#         assert test_program["level"] == "INTERMEDIATE"
#
#         # Check tags
#         assert len(test_program["tags"]) == 2
#         tag_names = {tag["name"] for tag in test_program["tags"]}
#         assert tag_names == {"Test", "GraphQL"}
#
#         # Check practice links
#         assert len(test_program["practiceLinks"]) == 1
#         assert test_program["practiceLinks"][0]["sequenceOrder"] == 0
#         assert test_program["practiceLinks"][0]["intervalDaysAfter"] == 2
#         assert test_program["practiceLinks"][0]["practice"] is not None
#
#         # Check computed properties
#         assert test_program["practiceCount"] == 1
#         assert test_program["totalDurationDays"] == 3  # 1 day for practice + 2 days interval
#
#     @pytest.mark.asyncio
#     async def test_program_by_id_query(self, client, sample_program_id, docker_compose_up_down):
#         """Test querying a specific program by ID."""
#         query = f"""
#         query {{
#             program(id: "{sample_program_id}") {{
#                 id_
#                 name
#                 description
#                 level
#                 tags {{
#                     name
#                 }}
#             }}
#         }}
#         """
#         response = await client.post("/graphql", json={"query": query})
#         assert response.status_code == 200
#         data = response.json()
#         assert "data" in data and "program" in data["data"]
#         program = data["data"]["program"]
#         assert program is not None
#         assert program["id_"] == sample_program_id
#         assert program["name"] == "Test Program for GraphQL Tests"
#         assert len(program["tags"]) == 2
#
#     @pytest.mark.asyncio
#     async def test_programs_by_level_query(self, client, sample_program_id, docker_compose_up_down):
#         """Test querying programs by level."""
#         query = """
#         query {
#             programsByLevel(level: "INTERMEDIATE") {
#                 id_
#                 name
#                 level
#             }
#         }
#         """
#         response = await client.post("/graphql", json={"query": query})
#         assert response.status_code == 200
#         data = response.json()
#         assert "data" in data and "programsByLevel" in data["data"]
#         programs = data["data"]["programsByLevel"]
#         assert len(programs) > 0
#         assert any(p["id_"] == sample_program_id for p in programs)
#         assert all(p["level"] == "INTERMEDIATE" for p in programs)
#
#     @pytest.mark.asyncio
#     async def test_programs_by_tag_query(self, client, sample_program_id, docker_compose_up_down):
#         """Test querying programs by tag."""
#         query = """
#         query {
#             programsByTag(tagName: "GraphQL") {
#                 id_
#                 name
#                 tags {
#                     name
#                 }
#             }
#         }
#         """
#         response = await client.post("/graphql", json={"query": query})
#         assert response.status_code == 200
#         data = response.json()
#         assert "data" in data and "programsByTag" in data["data"]
#         programs = data["data"]["programsByTag"]
#         assert len(programs) > 0
#         graphql_program = next((p for p in programs if p["id_"] == sample_program_id), None)
#         assert graphql_program is not None
#         assert any(tag["name"] == "GraphQL" for tag in graphql_program["tags"])
#
#
# class TestProgramMutation:
#     @pytest.mark.asyncio
#     async def test_create_program(self, create_tables, client, sample_practice_id, docker_compose_up_down):
#         """Test creating a new program."""
#         mutation = f"""
#         mutation {{
#             createProgram(input: {{
#                 name: "New Test Program",
#                 description: "Created via GraphQL mutation",
#                 level: "BEGINNER",
#                 tags: [
#                     {{ name: "New" }},
#                     {{ name: "Test" }}
#                 ],
#                 practiceLinks: [
#                     {{
#                         practiceId: "{sample_practice_id}",
#                         sequenceOrder: 0,
#                         intervalDaysAfter: 1
#                     }}
#                 ]
#             }}) {{
#                 id_
#                 name
#                 description
#                 level
#                 tags {{
#                     name
#                 }}
#                 practiceLinks {{
#                     sequenceOrder
#                     practice {{
#                         id_
#                     }}
#                 }}
#             }}
#         }}
#         """
#         response = await client.post("/graphql", json={"query": mutation})
#         assert response.status_code == 200
#         data = response.json()
#         assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
#         assert "data" in data and "createProgram" in data["data"]
#
#         created_program = data["data"]["createProgram"]
#         assert created_program is not None
#         assert created_program["name"] == "New Test Program"
#         assert created_program["description"] == "Created via GraphQL mutation"
#         assert created_program["level"] == "BEGINNER"
#
#         assert len(created_program["tags"]) == 2
#         tag_names = {tag["name"] for tag in created_program["tags"]}
#         assert tag_names == {"New", "Test"}
#
#         assert len(created_program["practiceLinks"]) == 1
#         assert created_program["practiceLinks"][0]["sequenceOrder"] == 0
#         assert created_program["practiceLinks"][0]["practice"]["id_"] == sample_practice_id
#
#     @pytest.mark.asyncio
#     async def test_update_program(
#         self, create_tables, client, sample_program_id, sample_practice_id, docker_compose_up_down
#     ):
#         """Test updating an existing program."""
#         # Create a second practice to add to the program
#         practice_mutation = """
#         mutation {
#             createPractice(input: {
#                 title: "Second Test Practice",
#                 description: "For program update test",
#                 date: "2023-10-10",
#                 complete: false
#             }) {
#                 id_
#             }
#         }
#         """
#         response = await client.post("/graphql", json={"query": practice_mutation})
#         data = response.json()
#         second_practice_id = data["data"]["createPractice"]["id_"]
#
#         # Update the program with new tags and practice links
#         update_mutation = f"""
#         mutation {{
#             updateProgram(
#                 id: "{sample_program_id}",
#                 input: {{
#                     name: "Updated Program Name",
#                     description: "Updated via GraphQL mutation",
#                     level: "ADVANCED",
#                     tags: [
#                         {{ name: "Updated" }},
#                         {{ name: "Tag" }}
#                     ],
#                     practiceLinks: [
#                         {{
#                             practiceId: "{sample_practice_id}",
#                             sequenceOrder: 0,
#                             intervalDaysAfter: 3
#                         }},
#                         {{
#                             practiceId: "{second_practice_id}",
#                             sequenceOrder: 1,
#                             intervalDaysAfter: 2
#                         }}
#                     ]
#                 }}
#             ) {{
#                 id_
#                 name
#                 description
#                 level
#                 tags {{
#                     name
#                 }}
#                 practiceLinks {{
#                     sequenceOrder
#                     intervalDaysAfter
#                     practice {{
#                         id_
#                         title
#                     }}
#                 }}
#                 totalDurationDays
#             }}
#         }}
#         """
#         response = await client.post("/graphql", json={"query": update_mutation})
#         assert response.status_code == 200
#         data = response.json()
#         assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
#         assert "data" in data and "updateProgram" in data["data"]
#
#         updated_program = data["data"]["updateProgram"]
#         assert updated_program is not None
#         assert updated_program["id_"] == sample_program_id
#         assert updated_program["name"] == "Updated Program Name"
#         assert updated_program["description"] == "Updated via GraphQL mutation"
#         assert updated_program["level"] == "ADVANCED"
#
#         # Check updated tags
#         assert len(updated_program["tags"]) == 2
#         tag_names = {tag["name"] for tag in updated_program["tags"]}
#         assert tag_names == {"Updated", "Tag"}
#
#         # Check updated practice links
#         assert len(updated_program["practiceLinks"]) == 2
#         practice_ids = {link["practice"]["id_"] for link in updated_program["practiceLinks"]}
#         assert practice_ids == {sample_practice_id, second_practice_id}
#
#         # Check the first link has updated interval
#         first_link = next(link for link in updated_program["practiceLinks"] if link["sequenceOrder"] == 0)
#         assert first_link["intervalDaysAfter"] == 3
#
#         # Check computed duration
#         assert (
#             updated_program["totalDurationDays"] == 6
#         )  # 1 (first practice) + 3 (interval) + 1 (second practice) + 1 (from sequence_order)
#
#     @pytest.mark.asyncio
#     async def test_delete_program(self, create_tables, client, sample_program_id, docker_compose_up_down):
#         """Test deleting a program."""
#         # First verify the program exists
#         query = f"""
#         query {{
#             program(id: "{sample_program_id}") {{
#                 id_
#             }}
#         }}
#         """
#         response = await client.post("/graphql", json={"query": query})
#         data = response.json()
#         assert data["data"]["program"] is not None
#
#         # Delete the program
#         delete_mutation = f"""
#         mutation {{
#             deleteProgram(id: "{sample_program_id}")
#         }}
#         """
#         response = await client.post("/graphql", json={"query": delete_mutation})
#         assert response.status_code == 200
#         data = response.json()
#         assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
#         assert data["data"]["deleteProgram"] is True
#
#         # Verify it's gone
#         response = await client.post("/graphql", json={"query": query})
#         data = response.json()
#         assert data["data"]["program"] is None
