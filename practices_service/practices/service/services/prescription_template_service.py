from typing import Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainPrescriptionTemplate
from practices.repository.repositories.prescription_template_repository import (
    PrescriptionTemplateRepository,
)


class PrescriptionTemplateService:
    def __init__(self, repository: PrescriptionTemplateRepository):
        self.repository = repository

    async def create_prescription_template(self, prescription_data: Dict) -> DomainPrescriptionTemplate:
        """Create a new reusable prescription template"""
        return await self.repository.create_prescription_template(prescription_data)

    async def get_prescription_template_by_id(self, prescription_id: UUID) -> Optional[DomainPrescriptionTemplate]:
        """Get prescription template by ID"""
        return await self.repository.get_prescription_template_by_id(prescription_id)

    async def get_prescription_templates_by_practice_id(
        self, practice_template_id: UUID
    ) -> List[DomainPrescriptionTemplate]:
        """Get all prescription templates for a practice template"""
        return await self.repository.get_prescription_templates_by_practice_id(practice_template_id)

    async def update_prescription_template(
        self, prescription_id: UUID, update_data: Dict
    ) -> Optional[DomainPrescriptionTemplate]:
        """Update prescription template parameters"""
        return await self.repository.update_prescription_template(prescription_id, update_data)

    async def delete_prescription_template(self, prescription_id: UUID) -> bool:
        """Delete prescription template"""
        return await self.repository.delete_prescription_template(prescription_id)

    async def get_template_usage_count(self, template_id: UUID) -> int:
        """Get number of times this template has been used"""
        return await self.repository.get_template_usage_count(template_id)

    async def get_programs_using_template(self, template_id: UUID) -> List:
        """Get programs that use this prescription template"""
        return await self.repository.get_programs_using_template(template_id)
