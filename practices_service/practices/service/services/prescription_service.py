from typing import Any, Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainPrescription
from practices.repository.repositories import PrescriptionRepository


class PrescriptionService:
    def __init__(self, repository: PrescriptionRepository):
        self.repository = repository

    async def create_prescription(self, prescription_data: Dict[str, Any]) -> DomainPrescription:
        """Creates a new prescription with nested movements and sets."""
        # Expects practice_id to be in prescription_data
        return await self.repository.create_prescription_with_movements(prescription_data)

    async def get_prescription_by_id(self, prescription_id: UUID) -> Optional[DomainPrescription]:
        return await self.repository.get_prescription_by_id(prescription_id)

    async def list_prescriptions_for_practice(
        self, practice_id: UUID, limit: Optional[int] = None
    ) -> List[DomainPrescription]:
        return await self.repository.list_prescriptions_by_practice_id(practice_id, limit=limit)

    async def list_all_prescriptions(self) -> List[DomainPrescription]:
        return await self.repository.list_all_prescriptions()

    async def update_prescription(
        self, prescription_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[DomainPrescription]:
        # Note: Deep updates of nested movements are handled by the repository
        # or would require more complex service logic if the repo was simpler.
        return await self.repository.update_prescription(prescription_id, update_data)

    async def delete_prescription(self, prescription_id: UUID) -> bool:
        return await self.repository.delete_prescription(prescription_id)
