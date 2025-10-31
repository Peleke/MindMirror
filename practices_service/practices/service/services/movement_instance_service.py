from typing import Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainMovementInstance
from practices.repository.repositories.movement_instance_repository import (
    MovementInstanceRepository,
)


class MovementInstanceService:
    def __init__(self, repository: MovementInstanceRepository):
        self.repository = repository

    async def create_movement_instance(self, movement_data: Dict) -> DomainMovementInstance:
        """Create a new movement instance during workout"""
        return await self.repository.create_movement_instance(movement_data)

    async def create_movement_from_template(
        self, template_id: UUID, prescription_instance_id: UUID, position: int
    ) -> DomainMovementInstance:
        """Create movement instance from template"""
        return await self.repository.create_movement_from_template(template_id, prescription_instance_id, position)

    async def get_movement_instance_by_id(self, movement_id: UUID) -> Optional[DomainMovementInstance]:
        """Get movement instance by ID"""
        return await self.repository.get_movement_instance_by_id(movement_id)

    async def get_movement_instances_by_prescription_id(
        self, prescription_instance_id: UUID
    ) -> List[DomainMovementInstance]:
        """Get all movement instances for a prescription"""
        return await self.repository.get_movement_instances_by_prescription_id(prescription_instance_id)

    async def get_movement_instances_by_template_id(self, template_id: UUID) -> List[DomainMovementInstance]:
        """Get all movement instances created from a template"""
        return await self.repository.get_movement_instances_by_template_id(template_id)

    async def update_movement_instance(self, movement_id: UUID, update_data: Dict) -> Optional[DomainMovementInstance]:
        """Update movement instance parameters"""
        return await self.repository.update_movement_instance(movement_id, update_data)

    async def delete_movement_instance(self, movement_id: UUID) -> bool:
        """Delete movement instance"""
        return await self.repository.delete_movement_instance(movement_id)

    async def reorder_movements_in_prescription(
        self, prescription_instance_id: UUID, movement_orders: List[Dict]
    ) -> List[DomainMovementInstance]:
        """Reorder movements within a prescription instance"""
        return await self.repository.reorder_movements_in_prescription(prescription_instance_id, movement_orders)

    async def check_movement_completion(self, movement_id: UUID) -> bool:
        """Check if movement should be marked complete based on set completion"""
        return await self.repository.check_movement_completion(movement_id)
