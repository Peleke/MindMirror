from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainProgram
from practices.repository.repositories.program_repository import ProgramRepository


class ProgramService:
    def __init__(self, repository: ProgramRepository):
        self.repository = repository

    async def create_program(self, program_data: Dict[str, Any]) -> DomainProgram:
        """Create a new program with nested tags and practice links."""
        # Transform the input data if needed (e.g., renaming fields, handling special cases)
        # For example, ensuring tags and practice_links are correctly formatted

        transformed_data = program_data.copy()

        # If practice links are provided, ensure they're under practice_links_data
        if "practice_links" in transformed_data and "practice_links_data" not in transformed_data:
            transformed_data["practice_links_data"] = transformed_data.pop("practice_links")

        # If tags are provided, ensure they're under tags_data
        if "tags" in transformed_data and "tags_data" not in transformed_data:
            transformed_data["tags_data"] = transformed_data.pop("tags")

        return await self.repository.create_program_with_links_and_tags(transformed_data)

    async def get_program_by_id(self, program_id: UUID) -> Optional[DomainProgram]:
        """Get a program by ID."""
        return await self.repository.get_program_by_id(program_id)

    async def list_programs(self, limit: Optional[int] = None, **filters: Any) -> List[DomainProgram]:
        """List programs with optional filtering."""
        return await self.repository.list_programs(limit=limit, **filters)

    async def update_program(self, program_id: UUID, update_data: Dict[str, Any]) -> Optional[DomainProgram]:
        """Update a program and its relationships."""
        # Transform the input data if needed
        transformed_data = update_data.copy()

        # Handle nested data renames for consistency with repository method names
        if "practice_links" in transformed_data and "practice_links_data" not in transformed_data:
            transformed_data["practice_links_data"] = transformed_data.pop("practice_links")
            print(f"Transformed practice_links to practice_links_data: {transformed_data['practice_links_data']}")

        if "tags" in transformed_data and "tags_data" not in transformed_data:
            transformed_data["tags_data"] = transformed_data.pop("tags")
            print(f"Transformed tags to tags_data: {transformed_data['tags_data']}")

        return await self.repository.update_program(program_id, transformed_data)

    async def delete_program(self, program_id: UUID) -> bool:
        """Delete a program by ID."""
        return await self.repository.delete_program(program_id)

    async def get_program_by_name(self, name: str) -> Optional[DomainProgram]:
        """Get a program by name."""
        return await self.repository.get_program_by_name(name)

    # Additional business logic methods can be added here

    async def filter_programs_by_level(self, level: str, limit: Optional[int] = None) -> List[DomainProgram]:
        """Filter programs by their level (e.g., BEGINNER, INTERMEDIATE, ADVANCED)."""
        return await self.repository.list_programs(limit=limit, level=level)

    async def filter_programs_by_tag(self, tag_name: str, limit: Optional[int] = None) -> List[DomainProgram]:
        """
        Filter programs by tag name.

        This is more complex as it requires joining with the tags table.
        For now, we'll fetch all programs with their tags and filter in-memory.

        A more efficient implementation would involve a custom query in the repository.
        """
        all_programs = await self.repository.list_programs()
        filtered_programs = [
            program for program in all_programs if any(tag.name.lower() == tag_name.lower() for tag in program.tags)
        ]

        if limit is not None:
            filtered_programs = filtered_programs[:limit]

        return filtered_programs
