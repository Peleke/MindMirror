import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainProgram  # Updated import path
from practices.repository.models import (
    PracticeTemplateModel,
    ProgramModel,
    ProgramPracticeLinkModel,
    ProgramTagModel,
)


class ProgramRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_dict(self, model: ProgramModel) -> Dict[str, Any]:
        """Convert a SQLAlchemy model to a dictionary for Pydantic validation."""
        # Basic program attributes
        result = {
            "id_": str(model.id_),
            "name": model.name,
            "description": model.description,
            "level": model.level,
            "created_at": model.created_at,
            "modified_at": model.modified_at,
            "user_id": str(model.user_id),
            "tags": [],
            "practice_links": [],
        }

        # Add tags if loaded
        if model.tags:
            result["tags"] = [
                {
                    "id_": str(tag.id_),
                    "program_id": str(tag.program_id),
                    "name": tag.name,
                    "created_at": tag.created_at,
                    "modified_at": tag.modified_at,
                }
                for tag in model.tags
            ]

        # Add practice links with practice data properly loaded
        if model.practice_links:
            result["practice_links"] = []
            for link in model.practice_links:
                link_dict = {
                    "id_": str(link.id_),
                    "program_id": str(link.program_id),
                    "practice_template_id": str(link.practice_template_id),
                    "sequence_order": link.sequence_order,
                    "interval_days_after": link.interval_days_after,
                    "created_at": link.created_at,
                    "modified_at": link.modified_at,
                }

                # Include practice data if it's loaded
                if hasattr(link, "practice_template") and link.practice_template is not None:
                    practice_template = link.practice_template
                    link_dict["practice_template"] = {
                        "id_": str(practice_template.id_),
                        "title": practice_template.title,
                        "description": practice_template.description,
                        "duration": practice_template.duration,
                        "created_at": practice_template.created_at,
                        "modified_at": practice_template.modified_at,
                        "user_id": str(practice_template.user_id),
                    }
                else:
                    link_dict["practice_template"] = None

                result["practice_links"].append(link_dict)

        return result

    async def create_program_with_links_and_tags(self, program_data: dict) -> DomainProgram:
        """Creates a new program along with its nested practice links and tags."""
        practice_links_data = program_data.pop("practice_links", []) or program_data.pop("practice_links_data", [])
        tags_data = program_data.pop("tags", []) or program_data.pop("tags_data", [])

        new_program = ProgramModel(**program_data)
        self.session.add(new_program)
        await self.session.flush()

        for tag_data in tags_data:
            new_tag = ProgramTagModel(**tag_data, program_id=new_program.id_)
            self.session.add(new_tag)

        for link_data in practice_links_data:
            new_link = ProgramPracticeLinkModel(**link_data, program_id=new_program.id_)
            self.session.add(new_link)

        await self.session.commit()

        stmt = (
            select(ProgramModel)
            .where(ProgramModel.id_ == new_program.id_)
            .options(
                selectinload(ProgramModel.tags),
                selectinload(ProgramModel.practice_links).selectinload(ProgramPracticeLinkModel.practice_template),
            )
        )
        result = await self.session.execute(stmt)
        refetched_program = result.scalar_one()

        program_dict = self._model_to_dict(refetched_program)
        return DomainProgram.model_validate(program_dict)

    async def get_program_by_id(self, program_id: uuid.UUID) -> Optional[DomainProgram]:
        """Gets a program by ID with all its relationships loaded."""
        stmt = (
            select(ProgramModel)
            .where(ProgramModel.id_ == program_id)
            .options(
                selectinload(ProgramModel.tags),
                selectinload(ProgramModel.practice_links).selectinload(ProgramPracticeLinkModel.practice_template),
            )
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            return None

        # Convert to dict before passing to model_validate
        program_dict = self._model_to_dict(record)
        return DomainProgram.model_validate(program_dict)

    async def list_programs(self, limit: Optional[int] = None, **filters: Any) -> List[DomainProgram]:
        """Lists programs with optional filtering and limit."""
        stmt = (
            select(ProgramModel)
            .options(
                selectinload(ProgramModel.tags),
                selectinload(ProgramModel.practice_links).selectinload(ProgramPracticeLinkModel.practice_template),
            )
            .order_by(ProgramModel.name, ProgramModel.created_at.desc())
        )

        # Apply filters if any
        for key, value in filters.items():
            if hasattr(ProgramModel, key):
                stmt = stmt.where(getattr(ProgramModel, key) == value)

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # Convert each record to dict before passing to model_validate
        return [DomainProgram.model_validate(self._model_to_dict(record)) for record in records]

    async def update_program(self, program_id: uuid.UUID, update_data: dict) -> Optional[DomainProgram]:
        """
        Updates a program and its relationships.

        For nested updates (tags, practice_links), replaces the entire collections
        if they are provided in the update_data.
        """
        print(f"Starting update for program {program_id} with data: {update_data}")

        # Fetch the program to update
        stmt = (
            select(ProgramModel)
            .where(ProgramModel.id_ == program_id)
            .options(selectinload(ProgramModel.tags), selectinload(ProgramModel.practice_links))
        )
        result = await self.session.execute(stmt)
        program = result.scalar_one_or_none()

        if program is None:
            return None

        # Update direct attributes first
        for key, value in update_data.items():
            if key not in ["practice_links_data", "tags_data"] and hasattr(program, key):
                setattr(program, key, value)

        # Set modified timestamp
        program.modified_at = datetime.utcnow()
        await self.session.flush()  # Flush changes to ensure attributes are updated

        # Handle practice_links update if provided
        if "practice_links_data" in update_data:
            practice_links_data = update_data.pop("practice_links_data")
            print(f"Updating practice links with {len(practice_links_data)} new links: {practice_links_data}")

            # Delete existing links
            await self.session.execute(
                delete(ProgramPracticeLinkModel).where(ProgramPracticeLinkModel.program_id == program_id)
            )
            await self.session.flush()

            # Create new links
            for link_data in practice_links_data:
                new_link = ProgramPracticeLinkModel(**link_data, program_id=program_id)
                self.session.add(new_link)
            await self.session.flush()

            # Verify creation
            verify_stmt = select(ProgramPracticeLinkModel).where(ProgramPracticeLinkModel.program_id == program_id)
            verify_result = await self.session.execute(verify_stmt)
            verify_links = verify_result.scalars().all()
            print(f"After creating links - found {len(verify_links)} links in database")

        # Handle tags update if provided
        if "tags_data" in update_data:
            tags_data = update_data.pop("tags_data")
            print(f"Updating tags with {len(tags_data)} new tags: {tags_data}")

            # Delete existing tags
            await self.session.execute(delete(ProgramTagModel).where(ProgramTagModel.program_id == program_id))
            await self.session.flush()

            # Create new tags
            for tag_data in tags_data:
                new_tag = ProgramTagModel(**tag_data, program_id=program_id)
                self.session.add(new_tag)
            await self.session.flush()

            # Verify creation
            verify_stmt = select(ProgramTagModel).where(ProgramTagModel.program_id == program_id)
            verify_result = await self.session.execute(verify_stmt)
            verify_tags = verify_result.scalars().all()
            print(f"After creating tags - found {len(verify_tags)} tags in database")

        # Ensure all changes are flushed before refreshing
        await self.session.flush()
        # Refresh program to ensure it has the latest state of all relations
        await self.session.refresh(program)
        # Commit all changes
        await self.session.commit()

        # Re-fetch with all relationships to ensure consistency
        # Select with explicit loading to avoid lazy loading
        stmt = (
            select(ProgramModel)
            .where(ProgramModel.id_ == program_id)
            .options(
                selectinload(ProgramModel.tags),
                selectinload(ProgramModel.practice_links).selectinload(ProgramPracticeLinkModel.practice_template),
            )
        )
        result = await self.session.execute(stmt)
        refetched_program = result.scalar_one_or_none()
        if not refetched_program:
            return None

        # Print tags for debugging
        if hasattr(refetched_program, "tags"):
            print(f"After update: Found {len(refetched_program.tags)} tags")
        if hasattr(refetched_program, "practice_links"):
            print(f"After update: Found {len(refetched_program.practice_links)} practice links")

        # Convert to dict before passing to model_validate
        program_dict = self._model_to_dict(refetched_program)
        return DomainProgram.model_validate(program_dict)

    async def delete_program(self, program_id: uuid.UUID) -> bool:
        """Deletes a program and its related entities."""
        stmt = select(ProgramModel).where(ProgramModel.id_ == program_id)
        result = await self.session.execute(stmt)
        program = result.scalar_one_or_none()

        if program:
            await self.session.delete(program)  # Cascading deletes should handle related items
            await self.session.commit()
            return True
        return False

    # Utility methods for testing or specialized queries

    async def count_programs(self) -> int:
        """Returns the total count of programs."""
        stmt = select(ProgramModel)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def get_program_by_name(self, name: str) -> Optional[DomainProgram]:
        """Gets a program by name."""
        stmt = (
            select(ProgramModel)
            .where(ProgramModel.name == name)
            .options(
                selectinload(ProgramModel.tags),
                selectinload(ProgramModel.practice_links).selectinload(ProgramPracticeLinkModel.practice_template),
            )
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            return None

        # Convert to dict before passing to model_validate
        program_dict = self._model_to_dict(record)
        return DomainProgram.model_validate(program_dict)
