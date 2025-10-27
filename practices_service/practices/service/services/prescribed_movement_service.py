from typing import Any, Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainPrescribedMovement
from practices.repository.repositories import (
    PrescribedMovementRepository,  # , SetRepository
)


class PrescribedMovementService:
    def __init__(self, movement_repository: PrescribedMovementRepository):
        # Potentially also SetRepository if managing sets explicitly here
        self.movement_repository = movement_repository

    async def create_prescribed_movement(self, movement_data: Dict[str, Any]) -> DomainPrescribedMovement:
        """Creates a new prescribed movement with nested sets."""
        # Expects prescription_id to be in movement_data
        return await self.movement_repository.create_movement_with_sets(movement_data)

    async def get_prescribed_movement_by_id(self, movement_id: UUID) -> Optional[DomainPrescribedMovement]:
        return await self.movement_repository.get_movement_by_id(movement_id)

    async def list_movements_for_prescription(
        self, prescription_id: UUID, limit: Optional[int] = None
    ) -> List[DomainPrescribedMovement]:
        return await self.movement_repository.list_movements_by_prescription_id(prescription_id, limit=limit)

    async def list_all_prescribed_movements(self) -> List[DomainPrescribedMovement]:
        return await self.movement_repository.list_all_prescribed_movements()

    async def update_prescribed_movement(
        self, movement_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[DomainPrescribedMovement]:
        # Note: Deep updates of nested sets are handled by the repository.
        return await self.movement_repository.update_movement(movement_id, update_data)

    async def delete_prescribed_movement(self, movement_id: UUID) -> bool:
        return await self.movement_repository.delete_movement(movement_id)

    # Example of more complex set management if needed, (see swae-be reference)
    # async def add_set_to_prescribed_movement(
    #     self, movement_id: UUID, set_data: Dict[str, Any]
    # ) -> Optional[DomainPrescribedMovement]:
    #     movement = await self.get_prescribed_movement_by_id(movement_id)
    #     if not movement:
    #         return None
    #     # This assumes repository.update_movement can handle partial updates / appends to sets
    #     # or that set_data includes the movement_id and a SetRepository is used directly.
    #     # A more robust way might be to fetch, modify the Pydantic model, then pass to update.
    #
    #     # For simplicity, if sets are fully replaced by repository update:
    #     current_sets_as_dicts = [s.model_dump() for s in movement.sets]
    #     current_sets_as_dicts.append(set_data)
    #     return await self.update_prescribed_movement(movement_id, {"sets": current_sets_as_dicts})

    # async def remove_set_from_prescribed_movement(
    #     self, movement_id: UUID, set_id: UUID
    # ) -> Optional[DomainPrescribedMovement]:
    #     movement = await self.get_prescribed_movement_by_id(movement_id)
    #     if not movement:
    #         return None

    #     updated_sets = [s.model_dump() for s in movement.sets if s.id_ != set_id]
    #     return await self.update_prescribed_movement(movement_id, {"sets": updated_sets})
