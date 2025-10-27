from typing import Any, Dict, Optional
from uuid import UUID

from meals.domain.models import DomainUserGoals
from meals.repository.repositories import UserGoalsRepository


class UserGoalsService:
    def __init__(self, repository: UserGoalsRepository):
        self.repository = repository

    async def create_user_goals(self, goals_data: Dict[str, Any]) -> DomainUserGoals:
        """Create new user goals."""
        return await self.repository.create_user_goals(goals_data)

    async def get_user_goals_by_id(self, goals_id: UUID) -> Optional[DomainUserGoals]:
        """Get user goals by ID."""
        return await self.repository.get_user_goals_by_id(goals_id)

    async def get_user_goals_by_user_id(self, user_id: str) -> Optional[DomainUserGoals]:
        """Get user goals by user ID."""
        return await self.repository.get_user_goals_by_user_id(user_id)

    async def update_user_goals(self, goals_id: UUID, update_data: Dict[str, Any]) -> Optional[DomainUserGoals]:
        """Update user goals by ID."""
        return await self.repository.update_user_goals(goals_id, update_data)

    async def update_user_goals_by_user_id(
        self, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[DomainUserGoals]:
        """Update user goals by user ID."""
        return await self.repository.update_user_goals_by_user_id(user_id, update_data)

    async def upsert_user_goals(self, user_id: str, goals_data: Dict[str, Any]) -> DomainUserGoals:
        """Create or update user goals for a user."""
        return await self.repository.upsert_user_goals(user_id, goals_data)

    async def delete_user_goals(self, goals_id: UUID) -> bool:
        """Delete user goals."""
        return await self.repository.delete_user_goals(goals_id)
