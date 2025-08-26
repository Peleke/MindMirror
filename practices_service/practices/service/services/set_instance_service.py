from typing import Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainSetInstance
from practices.repository.repositories.set_instance_repository import (
    SetInstanceRepository,
)


class SetInstanceService:
    def __init__(self, repository: SetInstanceRepository):
        self.repository = repository

    async def create_set_instance(self, set_data: Dict) -> DomainSetInstance:
        """Create a new set instance during workout"""
        return await self.repository.create(set_data)

    async def get_set_instance_by_id(self, set_id: UUID) -> Optional[DomainSetInstance]:
        """Get set instance by ID"""
        return await self.repository.get_by_id(set_id)

    async def get_sets_by_movement_instance_id(self, movement_instance_id: UUID) -> List[DomainSetInstance]:
        """Get all sets for a movement instance"""
        return await self.repository.get_sets_by_movement_instance_id(movement_instance_id)

    async def get_set_instances_by_template_id(self, template_id: UUID) -> List[DomainSetInstance]:
        """Get all set instances created from a template"""
        return await self.repository.get_set_instances_by_template_id(template_id)

    async def update_set_instance(self, set_id: UUID, update_data: Dict) -> Optional[DomainSetInstance]:
        """Update set instance with performance data"""
        return await self.repository.update(set_id, update_data)

    async def mark_set_complete(
        self, set_id: UUID, performance_data: Optional[Dict] = None
    ) -> Optional[DomainSetInstance]:
        """Mark a set as complete with optional performance data"""
        update_data = {"complete": True}
        if performance_data:
            update_data.update(performance_data)
        return await self.repository.update(set_id, update_data)

    async def delete_set_instance(self, set_id: UUID) -> bool:
        """Delete set instance"""
        return await self.repository.delete(set_id)

    async def reorder_sets_in_movement(
        self, movement_instance_id: UUID, set_orders: List[Dict]
    ) -> List[DomainSetInstance]:
        """Reorder sets within a movement instance"""
        return await self.repository.reorder_sets_in_movement(movement_instance_id, set_orders)
