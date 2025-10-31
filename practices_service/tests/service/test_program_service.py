import pytest

from practices.repository.repositories import ProgramRepository
from practices.service.services import ProgramService


@pytest.mark.asyncio
class TestProgramService:
    async def test_create_program(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        coach_id = seed_db["coach_user"].id
        practice_template_id = seed_db["practice_templates"][0].id_
        program_data = {
            "user_id": coach_id,
            "name": "Service Test Program",
            "description": "A program for testing the service layer.",
            "level": "INTERMEDIATE",
            "practice_links": [
                {
                    "practice_template_id": practice_template_id,
                    "sequence_order": 1,
                    "interval_days_after": 3,
                }
            ],
            "tags": [{"name": "Service-Created"}],
        }
        created = await service.create_program(program_data)
        assert created is not None
        assert created.name == "Service Test Program"
        assert len(created.practice_links) == 1
        assert len(created.tags) == 1
        assert created.tags[0].name == "Service-Created"

    async def test_get_program_by_id(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        program_id = seed_db["programs"][0].id_
        program = await service.get_program_by_id(program_id)
        assert program is not None
        assert program.id_ == program_id

    async def test_list_programs(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        programs = await service.list_programs()
        assert len(programs) >= 1
        assert any(p.id_ == seed_db["programs"][0].id_ for p in programs)

    async def test_update_program(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        program_id = seed_db["programs"][0].id_
        update_data = {
            "name": "Updated Name via Service",
            "tags": [{"name": "Updated"}],
        }
        updated = await service.update_program(program_id, update_data)
        assert updated is not None
        assert updated.name == "Updated Name via Service"
        assert len(updated.tags) == 1
        assert updated.tags[0].name == "Updated"

    async def test_delete_program(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        program_id = seed_db["programs"][0].id_
        result = await service.delete_program(program_id)
        assert result is True
        program = await service.get_program_by_id(program_id)
        assert program is None

    async def test_get_program_by_name(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        program_name = seed_db["programs"][0].name
        program = await service.get_program_by_name(program_name)
        assert program is not None
        assert program.name == program_name

    async def test_filter_programs_by_level(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        level = seed_db["programs"][0].level
        programs = await service.filter_programs_by_level(level)
        assert len(programs) >= 1
        assert all(p.level == level for p in programs)

    async def test_filter_programs_by_tag(self, uow, seed_db):
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        tag_name = seed_db["programs"][0].tags[0].name
        programs = await service.filter_programs_by_tag(tag_name)
        assert len(programs) >= 1
        assert any(tag.name == tag_name for program in programs for tag in program.tags)
