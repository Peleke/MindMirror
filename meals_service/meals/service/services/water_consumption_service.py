from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from meals.domain.models import DomainWaterConsumption
from meals.repository.repositories import WaterConsumptionRepository


class WaterConsumptionService:
    def __init__(self, repository: WaterConsumptionRepository):
        self.repository = repository

    async def create_water_consumption(self, consumption_data: Dict[str, Any]) -> DomainWaterConsumption:
        """Create a new water consumption entry."""
        # Handle consumed_at string conversion if provided
        if "consumed_at" in consumption_data and isinstance(consumption_data["consumed_at"], str):
            try:
                consumption_data["consumed_at"] = datetime.fromisoformat(consumption_data["consumed_at"])
            except ValueError as e:
                raise ValueError(
                    f"Invalid datetime format for 'consumed_at': {consumption_data['consumed_at']}. Expected ISO format. Error: {e}"
                )

        return await self.repository.create_water_consumption(consumption_data)

    async def get_water_consumption_by_id(self, consumption_id: UUID) -> Optional[DomainWaterConsumption]:
        """Get water consumption by ID."""
        return await self.repository.get_water_consumption_by_id(consumption_id)

    async def list_water_consumption_by_user(
        self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[DomainWaterConsumption]:
        """List water consumption entries for a user with pagination."""
        return await self.repository.list_water_consumption_by_user(user_id, limit, offset)

    async def list_water_consumption_by_user_and_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[DomainWaterConsumption]:
        """List water consumption for a user within a date range."""
        return await self.repository.list_water_consumption_by_user_and_date_range(
            user_id=user_id, start_date=start_date, end_date=end_date, limit=limit, offset=offset
        )

    async def get_total_water_consumption_by_user_and_date(self, user_id: str, consumption_date: date) -> float:
        """Get total water consumption for a user on a specific date."""
        return await self.repository.get_total_water_consumption_by_user_and_date(user_id, consumption_date)

    async def update_water_consumption(
        self, consumption_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[DomainWaterConsumption]:
        """Update a water consumption entry."""
        # Handle consumed_at string conversion if provided
        if "consumed_at" in update_data and isinstance(update_data["consumed_at"], str):
            try:
                update_data["consumed_at"] = datetime.fromisoformat(update_data["consumed_at"])
            except ValueError as e:
                raise ValueError(
                    f"Invalid datetime format for 'consumed_at': {update_data['consumed_at']}. Expected ISO format. Error: {e}"
                )

        return await self.repository.update_water_consumption(consumption_id, update_data)

    async def delete_water_consumption(self, consumption_id: UUID) -> bool:
        """Delete a water consumption entry."""
        return await self.repository.delete_water_consumption(consumption_id)
