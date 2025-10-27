from typing import List, Optional
from uuid import UUID

import strawberry
from strawberry.types import Info

from practices.domain.models import DomainProgram
from practices.repository.repositories import ProgramRepository
from practices.service.services import ProgramService

from .program_types import ProgramCreateInput, ProgramType, ProgramUpdateInput


@strawberry.type
class ProgramQuery:
    @strawberry.field
    async def program(self, info: Info, id: strawberry.ID) -> Optional[ProgramType]:
        """Get a program by ID."""
        uow = info.context["uow"]
        async with uow.start() as session:
            program_repo = ProgramRepository(session)
            program_service = ProgramService(program_repo)
            program = await program_service.get_program_by_id(UUID(id))

            if program:
                return ProgramType.from_domain(program)
            return None

    @strawberry.field
    async def programs(self, info: Info, limit: Optional[int] = None) -> List[ProgramType]:
        """Get a list of all programs."""
        uow = info.context["uow"]
        async with uow.start() as session:
            program_repo = ProgramRepository(session)
            program_service = ProgramService(program_repo)
            programs = await program_service.list_programs(limit=limit)

            return [ProgramType.from_domain(program) for program in programs]

    @strawberry.field
    async def programs_by_level(self, info: Info, level: str, limit: Optional[int] = None) -> List[ProgramType]:
        """Get programs filtered by level."""
        uow = info.context["uow"]
        async with uow.start() as session:
            program_repo = ProgramRepository(session)
            program_service = ProgramService(program_repo)
            programs = await program_service.filter_programs_by_level(level, limit=limit)

            return [ProgramType.from_domain(program) for program in programs]

    @strawberry.field
    async def programs_by_tag(self, info: Info, tag_name: str, limit: Optional[int] = None) -> List[ProgramType]:
        """Get programs filtered by tag name."""
        uow = info.context["uow"]
        async with uow.start() as session:
            program_repo = ProgramRepository(session)
            program_service = ProgramService(program_repo)
            programs = await program_service.filter_programs_by_tag(tag_name, limit=limit)

            return [ProgramType.from_domain(program) for program in programs]


@strawberry.type
class ProgramMutation:
    @strawberry.mutation
    async def create_program(self, info: Info, input: ProgramCreateInput) -> ProgramType:
        """Create a new program."""
        uow = info.context["uow"]
        async with uow.start() as session:
            program_repo = ProgramRepository(session)
            program_service = ProgramService(program_repo)

            # Convert input to dictionary
            program_data = input.to_dict()

            # Create program
            program = await program_service.create_program(program_data)

            return ProgramType.from_domain(program)

    @strawberry.mutation
    async def update_program(self, info: Info, id: strawberry.ID, input: ProgramUpdateInput) -> Optional[ProgramType]:
        """Update an existing program."""
        uow = info.context["uow"]
        async with uow.start() as session:
            program_repo = ProgramRepository(session)
            program_service = ProgramService(program_repo)

            # Convert input to dictionary
            update_data = input.to_dict()

            # Update program
            updated_program = await program_service.update_program(UUID(id), update_data)

            if updated_program:
                return ProgramType.from_domain(updated_program)
            return None

    @strawberry.mutation
    async def delete_program(self, info: Info, id: strawberry.ID) -> bool:
        """Delete a program."""
        uow = info.context["uow"]
        async with uow.start() as session:
            program_repo = ProgramRepository(session)
            program_service = ProgramService(program_repo)

            # Delete program
            success = await program_service.delete_program(UUID(id))

            return success
