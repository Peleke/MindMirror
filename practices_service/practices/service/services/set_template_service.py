from typing import Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainSetTemplate
from practices.repository.repositories.set_template_repository import (
    SetTemplateRepository,
)


class SetTemplateService:
    def __init__(self, repository: SetTemplateRepository):
        self.repository = repository

    async def create_set_template(self, set_data: Dict) -> DomainSetTemplate:
        """Create a new reusable set template"""
        return await self.repository.create_set_template(set_data)

    async def get_set_template_by_id(self, set_id: UUID) -> Optional[DomainSetTemplate]:
        """Get set template by ID"""
        return await self.repository.get_set_template_by_id(set_id)

    async def get_set_templates_by_movement_template_id(self, movement_template_id: UUID) -> List[DomainSetTemplate]:
        """Get all set templates for a movement template"""
        return await self.repository.get_set_templates_by_movement_template_id(movement_template_id)

    async def update_set_template(self, set_id: UUID, update_data: Dict) -> Optional[DomainSetTemplate]:
        """Update set template parameters"""
        return await self.repository.update_set_template(set_id, update_data)

    async def delete_set_template(self, set_id: UUID) -> bool:
        """Delete set template - only if no instances exist"""
        # Check if there are any set instances using this template
        usage_count = await self.repository.get_template_usage_count(set_id)
        if usage_count > 0:
            raise ValueError(f"Cannot delete set template: {usage_count} set instances are using this template")

        return await self.repository.delete_set_template(set_id)

    async def reorder_sets_in_movement_template(
        self, movement_template_id: UUID, set_orders: List[Dict]
    ) -> List[DomainSetTemplate]:
        """Reorder sets within a movement template"""
        return await self.repository.reorder_sets_in_movement_template(movement_template_id, set_orders)

    async def get_template_usage_count(self, template_id: UUID) -> int:
        """Get number of times this template has been used"""
        return await self.repository.get_template_usage_count(template_id)
