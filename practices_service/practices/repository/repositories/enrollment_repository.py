import uuid
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.repository.models import EnrollmentStatus, ProgramEnrollmentModel
from practices.repository.models.program import ProgramModel


class EnrollmentRepository:
    """Repository for managing program enrollments in the database."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_enrollment(self, **kwargs) -> ProgramEnrollmentModel:
        # NOTE: This assumes a simple creation. A real implementation
        # might check for existing enrollments first.
        enrollment = ProgramEnrollmentModel(**kwargs)
        self.session.add(enrollment)
        await self.session.commit()
        await self.session.refresh(enrollment)
        return enrollment

    async def get_by_id(self, enrollment_id: uuid.UUID) -> Optional[ProgramEnrollmentModel]:
        stmt = select(ProgramEnrollmentModel).where(ProgramEnrollmentModel.id_ == enrollment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, enrollment_id: uuid.UUID, update_data: dict) -> Optional[ProgramEnrollmentModel]:
        enrollment = await self.get_by_id(enrollment_id)
        if enrollment:
            for key, value in update_data.items():
                setattr(enrollment, key, value)
            await self.session.commit()
            await self.session.refresh(enrollment)
        return enrollment

    async def get_enrollment_by_id(
        self, enrollment_id: uuid.UUID, options: Optional[List] = None
    ) -> Optional[ProgramEnrollmentModel]:
        """Retrieves an enrollment by its ID."""
        stmt = select(ProgramEnrollmentModel).where(ProgramEnrollmentModel.id_ == enrollment_id)
        if options:
            stmt = stmt.options(*options)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_enrollments_for_user(self, user_id: uuid.UUID) -> Sequence[ProgramEnrollmentModel]:
        """Retrieves all enrollments for a given user."""
        stmt = (
            select(ProgramEnrollmentModel)
            .where(ProgramEnrollmentModel.user_id == user_id)
            .options(selectinload(ProgramEnrollmentModel.program))
            .order_by(ProgramEnrollmentModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_enrollments_for_program(self, program_id: uuid.UUID) -> Sequence[ProgramEnrollmentModel]:
        """Retrievels all enrollments for a specific program."""
        stmt = (
            select(ProgramEnrollmentModel)
            .where(ProgramEnrollmentModel.program_id == program_id)
            .order_by(ProgramEnrollmentModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_enrollment_status(
        self, enrollment_id: uuid.UUID, status: EnrollmentStatus
    ) -> Optional[ProgramEnrollmentModel]:
        """Updates the status of an existing enrollment."""
        enrollment = await self.get_enrollment_by_id(enrollment_id)
        if enrollment:
            enrollment.status = status
            await self.session.flush()
            await self.session.refresh(enrollment)
        return enrollment

    async def get_enrollments_by_user_id(self, user_id: uuid.UUID) -> List[ProgramEnrollmentModel]:
        stmt = (
            select(ProgramEnrollmentModel)
            .where(ProgramEnrollmentModel.user_id == user_id)
            .options(selectinload(ProgramEnrollmentModel.program))
            .order_by(ProgramEnrollmentModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
