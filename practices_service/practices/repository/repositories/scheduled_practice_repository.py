import uuid
from datetime import date
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from practices.repository.models.progress import ScheduledPracticeModel


class ScheduledPracticeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, scheduled_practice: ScheduledPracticeModel) -> None:
        """Adds a ScheduledPracticeModel to the session."""
        self.session.add(scheduled_practice)

    async def list(
        self, enrollment_ids: Optional[List[uuid.UUID]] = None, from_date: Optional[date] = None, **filters: Any
    ) -> List[ScheduledPracticeModel]:
        """
        Lists scheduled practices with optional filtering.

        Args:
            enrollment_ids: A list of enrollment IDs to filter by.
            from_date: A date to filter practices on or after.
            **filters: Additional exact match filters.
        """
        stmt = select(ScheduledPracticeModel)

        if enrollment_ids:
            stmt = stmt.where(ScheduledPracticeModel.enrollment_id.in_(enrollment_ids))

        if from_date:
            stmt = stmt.where(ScheduledPracticeModel.scheduled_date >= from_date)

        for key, value in filters.items():
            if hasattr(ScheduledPracticeModel, key):
                stmt = stmt.where(getattr(ScheduledPracticeModel, key) == value)

        stmt = stmt.order_by(ScheduledPracticeModel.scheduled_date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_for_enrollments_from_date(self, enrollment_ids: List[uuid.UUID], from_date: Optional[date] = None) -> int:
        """Deletes scheduled practices for the given enrollments on/after a date. Returns rows deleted."""
        from sqlalchemy import delete
        stmt = delete(ScheduledPracticeModel).where(ScheduledPracticeModel.enrollment_id.in_(enrollment_ids))
        if from_date:
            stmt = stmt.where(ScheduledPracticeModel.scheduled_date >= from_date)
        result = await self.session.execute(stmt)
        return result.rowcount or 0
