from typing import Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainPrescriptionInstance
from practices.repository.repositories.prescription_instance_repository import (
    PrescriptionInstanceRepository,
)


class PrescriptionInstanceService:
    def __init__(self, repository: PrescriptionInstanceRepository):
        self.repository = repository

    async def create_prescription_instance(self, prescription_data: Dict) -> DomainPrescriptionInstance:
        """Create a new prescription instance during workout"""
        return await self.repository.create_prescription_instance(prescription_data)

    async def get_prescription_instance_by_id(self, prescription_id: UUID) -> Optional[DomainPrescriptionInstance]:
        """Get prescription instance by ID"""
        return await self.repository.get_prescription_instance_by_id(prescription_id)

    async def get_prescription_instances_by_practice_id(
        self, practice_instance_id: UUID
    ) -> List[DomainPrescriptionInstance]:
        """Get all prescription instances for a practice"""
        return await self.repository.get_prescription_instances_by_practice_id(practice_instance_id)

    async def update_prescription_instance(
        self, prescription_id: UUID, update_data: Dict
    ) -> Optional[DomainPrescriptionInstance]:
        """Update prescription instance parameters"""
        return await self.repository.update_prescription_instance(prescription_id, update_data)

    async def delete_prescription_instance(self, prescription_id: UUID) -> bool:
        """Delete prescription instance"""
        return await self.repository.delete_prescription_instance(prescription_id)

    async def check_prescription_completion(self, prescription_id: UUID) -> bool:
        """Check if prescription should be marked complete based on movement completion"""
        return await self.repository.check_prescription_completion(prescription_id)
