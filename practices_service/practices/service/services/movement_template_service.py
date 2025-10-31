from typing import Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainMovementTemplate
from practices.repository.repositories.movement_template_repository import (
    MovementTemplateRepository,
)


class MovementTemplateService:
    def __init__(self, repository: MovementTemplateRepository):
        self.repository = repository

    async def create_movement_template(self, movement_data: Dict) -> DomainMovementTemplate:
        """Create a new reusable movement template"""
        return await self.repository.create_movement_template(movement_data)

    async def get_movement_template_by_id(self, movement_id: UUID) -> Optional[DomainMovementTemplate]:
        """Get movement template by ID"""
        return await self.repository.get_movement_template_by_id(movement_id)

    async def get_movement_templates_by_prescription_id(
        self, prescription_template_id: UUID
    ) -> List[DomainMovementTemplate]:
        """Get all movement templates for a prescription template"""
        return await self.repository.get_movement_templates_by_prescription_id(prescription_template_id)

    async def get_movement_templates_by_coach(self, coach_id: UUID) -> List[DomainMovementTemplate]:
        """Get all movement templates created by a coach"""
        return await self.repository.get_movement_templates_by_coach(coach_id)

    async def get_shared_movement_templates_for_user(self, user_id: UUID) -> List[DomainMovementTemplate]:
        """Get movement templates shared with a user"""
        return await self.repository.get_shared_movement_templates_for_user(user_id)

    async def update_movement_template(self, movement_id: UUID, update_data: Dict) -> Optional[DomainMovementTemplate]:
        """Update movement template parameters"""
        return await self.repository.update_movement_template(movement_id, update_data)

    async def delete_movement_template(self, movement_id: UUID) -> bool:
        """Delete movement template - only if no instances exist"""
        # Check if there are any movement instances using this template
        usage_count = await self.repository.get_template_usage_count(movement_id)
        if usage_count > 0:
            raise ValueError(
                f"Cannot delete movement template: {usage_count} movement instances are using this template"
            )

        return await self.repository.delete_movement_template(movement_id)

    async def get_template_usage_count(self, template_id: UUID) -> int:
        """Get number of times this template has been used"""
        return await self.repository.get_template_usage_count(template_id)

    async def get_programs_using_template(self, template_id: UUID) -> List:
        """Get programs that use this movement template"""
        return await self.repository.get_programs_using_template(template_id)

    async def get_template_shares(self, template_id: UUID) -> List:
        """Get users this template is shared with"""
        return await self.repository.get_template_shares(template_id)
