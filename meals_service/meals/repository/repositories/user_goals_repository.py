from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meals.domain.models import DomainUserGoals
from meals.repository.models import UserGoalsModel


class UserGoalsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_goals(self, goals_data: dict) -> DomainUserGoals:
        """Create new user goals."""
        new_goals = UserGoalsModel(**goals_data)
        self.session.add(new_goals)
        await self.session.flush()
        await self.session.refresh(new_goals)
        return DomainUserGoals.model_validate(new_goals)

    async def get_user_goals_by_id(self, goals_id: UUID) -> Optional[DomainUserGoals]:
        """Get user goals by ID."""
        stmt = select(UserGoalsModel).where(UserGoalsModel.id_ == goals_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainUserGoals.model_validate(record) if record else None

    async def get_user_goals_by_user_id(self, user_id: str) -> Optional[DomainUserGoals]:
        """Get user goals by user ID (should be unique per user)."""
        stmt = select(UserGoalsModel).where(UserGoalsModel.user_id == user_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainUserGoals.model_validate(record) if record else None

    async def list_all_user_goals(
        self, limit: Optional[int] = None, offset: Optional[int] = None, **filters: Any
    ) -> List[DomainUserGoals]:
        """List all user goals with optional filtering and pagination."""
        stmt = select(UserGoalsModel).order_by(UserGoalsModel.created_at.desc())

        # Apply filters
        for key, value in filters.items():
            if hasattr(UserGoalsModel, key):
                stmt = stmt.where(getattr(UserGoalsModel, key) == value)

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainUserGoals.model_validate(record) for record in records]

    async def update_user_goals(self, goals_id: UUID, update_data: dict) -> Optional[DomainUserGoals]:
        """Update user goals."""
        stmt = select(UserGoalsModel).where(UserGoalsModel.id_ == goals_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.flush()
        await self.session.refresh(record)
        return DomainUserGoals.model_validate(record)

    async def update_user_goals_by_user_id(self, user_id: str, update_data: dict) -> Optional[DomainUserGoals]:
        """Update user goals by user ID."""
        stmt = select(UserGoalsModel).where(UserGoalsModel.user_id == user_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.flush()
        await self.session.refresh(record)
        return DomainUserGoals.model_validate(record)

    async def delete_user_goals(self, goals_id: UUID) -> bool:
        """Delete user goals."""
        stmt = select(UserGoalsModel).where(UserGoalsModel.id_ == goals_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def delete_user_goals_by_user_id(self, user_id: str) -> bool:
        """Delete user goals by user ID."""
        stmt = select(UserGoalsModel).where(UserGoalsModel.user_id == user_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def upsert_user_goals(self, user_id: str, goals_data: dict) -> DomainUserGoals:
        """Create or update user goals for a user."""
        # Try to get existing goals
        existing_goals = await self.get_user_goals_by_user_id(user_id)

        if existing_goals:
            # Update existing goals
            updated_goals = await self.update_user_goals_by_user_id(user_id, goals_data)
            return updated_goals
        else:
            # Create new goals
            goals_data["user_id"] = user_id
            return await self.create_user_goals(goals_data)
