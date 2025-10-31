import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainPrescriptionInstance
from practices.repository.models import (
    MovementInstanceModel,
    PrescriptionInstanceModel,
    SetInstanceModel,
)


class PrescriptionInstanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_prescription_instance(self, prescription_data: dict) -> DomainPrescriptionInstance:
        """Create a new prescription instance with optional movements"""
        movements_data = prescription_data.pop("movements", [])
        print(f"DEBUG REPO: movements_data extracted: {movements_data}")
        print(f"DEBUG REPO: prescription_data after pop: {prescription_data}")

        new_prescription = PrescriptionInstanceModel(**prescription_data)
        self.session.add(new_prescription)
        await self.session.flush()
        await self.session.refresh(new_prescription)
        print(f"DEBUG REPO: Created prescription with ID: {new_prescription.id_}")

        # Create movements if provided
        for i, movement_data in enumerate(movements_data):
            print(f"DEBUG REPO: Processing movement {i}: {movement_data}")
            sets_data = movement_data.pop("sets", [])
            print(f"DEBUG REPO: Extracted sets data: {sets_data}")
            print(f"DEBUG REPO: Movement data after pop: {movement_data}")

            try:
                new_movement = MovementInstanceModel(**movement_data, prescription_instance_id=new_prescription.id_)
                print(f"DEBUG REPO: Created movement instance: {new_movement}")
                self.session.add(new_movement)
                await self.session.flush()
                await self.session.refresh(new_movement)
                print(f"DEBUG REPO: Movement saved with ID: {new_movement.id_}")

                # Create sets for the movement
                for j, set_data in enumerate(sets_data):
                    print(f"DEBUG REPO: Processing set {j}: {set_data}")
                    new_set = SetInstanceModel(**set_data, movement_instance_id=new_movement.id_)
                    print(f"DEBUG REPO: Created set instance: {new_set}")
                    self.session.add(new_set)
            except Exception as e:
                print(f"DEBUG REPO: Error creating movement {i}: {e}")
                raise

        # await self.session.commit()
        print(f"DEBUG REPO: Transaction committed")
        await self.session.refresh(new_prescription)
        return DomainPrescriptionInstance.model_validate(new_prescription)

    async def get_prescription_instance_by_id(self, prescription_id: UUID) -> Optional[DomainPrescriptionInstance]:
        """Get prescription instance by ID with movements and sets"""
        stmt = (
            select(PrescriptionInstanceModel)
            .where(PrescriptionInstanceModel.id_ == prescription_id)
            .options(selectinload(PrescriptionInstanceModel.movements).selectinload(MovementInstanceModel.sets))
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Convert to domain model
        prescription_dict = {
            "id_": record.id_,
            "practice_instance_id": record.practice_instance_id,
            "prescription_template_id": getattr(record, "template_id", None),
            "name": record.name,
            "position": record.position,
            "description": record.description,
            "block": record.block,
            "prescribed_rounds": record.prescribed_rounds,
            "complete": record.complete,
            "notes": record.notes,
            "completed_at": record.completed_at,
            "created_at": record.created_at,
            "modified_at": record.modified_at,
            "movements": [],
        }

        if record.movements:
            prescription_dict["movements"] = []
            for movement in record.movements:
                movement_dict = {
                    "id_": movement.id_,
                    "prescription_instance_id": movement.prescription_instance_id,
                    "movement_template_id": getattr(movement, "template_id", None),
                    "name": movement.name,
                    "position": movement.position,
                    "description": movement.description,
                    "metric_unit": movement.metric_unit,
                    "metric_value": movement.metric_value,
                    "movement_class": movement.movement_class,
                    "prescribed_sets": movement.prescribed_sets,
                    "rest_duration": movement.rest_duration,
                    "video_url": movement.video_url,
                    "exercise_id": movement.exercise_id,
                    "complete": movement.complete,
                    "notes": movement.notes,
                    "completed_at": movement.completed_at,
                    "created_at": movement.created_at,
                    "modified_at": movement.modified_at,
                    "sets": [],
                }

                if movement.sets:
                    movement_dict["sets"] = [
                        {
                            "id_": s.id_,
                            "movement_instance_id": s.movement_instance_id,
                            "set_template_id": getattr(s, "template_id", None),
                            "position": s.position,
                            "reps": s.reps,
                            "duration": s.duration,
                            "load_value": s.load_value,
                            "load_unit": s.load_unit,
                            "rest_duration": s.rest_duration,
                            "complete": s.complete,
                            "perceived_exertion": s.perceived_exertion,
                            "notes": s.notes,
                            "completed_at": s.completed_at,
                            "created_at": s.created_at,
                            "modified_at": s.modified_at,
                        }
                        for s in movement.sets
                    ]

                prescription_dict["movements"].append(movement_dict)

        return DomainPrescriptionInstance.model_validate(prescription_dict)

    async def get_prescription_instances_by_practice_id(
        self, practice_instance_id: UUID
    ) -> List[DomainPrescriptionInstance]:
        """Get all prescription instances for a practice"""
        stmt = (
            select(PrescriptionInstanceModel)
            .where(PrescriptionInstanceModel.practice_instance_id == practice_instance_id)
            .options(selectinload(PrescriptionInstanceModel.movements).selectinload(MovementInstanceModel.sets))
            .order_by(PrescriptionInstanceModel.position)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        prescriptions = []
        for record in records:
            prescription_dict = {
                "id_": record.id_,
                "practice_instance_id": record.practice_instance_id,
                "prescription_template_id": getattr(record, "template_id", None),
                "name": record.name,
                "position": record.position,
                "description": record.description,
                "block": record.block,
                "prescribed_rounds": record.prescribed_rounds,
                "complete": record.complete,
                "notes": record.notes,
                "completed_at": record.completed_at,
                "created_at": record.created_at,
                "modified_at": record.modified_at,
                "movements": [],
            }

            if record.movements:
                prescription_dict["movements"] = []
                for movement in record.movements:
                    movement_dict = {
                        "id_": movement.id_,
                        "prescription_instance_id": movement.prescription_instance_id,
                        "movement_template_id": getattr(movement, "template_id", None),
                        "name": movement.name,
                        "position": movement.position,
                        "description": movement.description,
                        "metric_unit": movement.metric_unit,
                        "metric_value": movement.metric_value,
                        "movement_class": movement.movement_class,
                        "prescribed_sets": movement.prescribed_sets,
                        "rest_duration": movement.rest_duration,
                        "video_url": movement.video_url,
                        "exercise_id": movement.exercise_id,
                        "complete": movement.complete,
                        "notes": movement.notes,
                        "completed_at": movement.completed_at,
                        "created_at": movement.created_at,
                        "modified_at": movement.modified_at,
                        "sets": [],
                    }

                    if movement.sets:
                        movement_dict["sets"] = [
                            {
                                "id_": s.id_,
                                "movement_instance_id": s.movement_instance_id,
                                "set_template_id": getattr(s, "template_id", None),
                                "position": s.position,
                                "reps": s.reps,
                                "duration": s.duration,
                                "load_value": s.load_value,
                                "load_unit": s.load_unit,
                                "rest_duration": s.rest_duration,
                                "complete": s.complete,
                                "perceived_exertion": s.perceived_exertion,
                                "notes": s.notes,
                                "completed_at": s.completed_at,
                                "created_at": s.created_at,
                                "modified_at": s.modified_at,
                            }
                            for s in movement.sets
                        ]

                    prescription_dict["movements"].append(movement_dict)

            prescriptions.append(DomainPrescriptionInstance.model_validate(prescription_dict))

        return prescriptions

    async def update_prescription_instance(
        self, prescription_id: UUID, update_data: dict
    ) -> Optional[DomainPrescriptionInstance]:
        """Update prescription instance"""
        stmt = select(PrescriptionInstanceModel).where(PrescriptionInstanceModel.id_ == prescription_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Handle completion timestamp
        if update_data.get("complete") and not record.completed_at:
            update_data["completed_at"] = datetime.utcnow()
        elif not update_data.get("complete", True) and record.completed_at:
            update_data["completed_at"] = None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        # Flush to make changes visible within the same transaction
        await self.session.flush()

        # Return the full prescription with relationships loaded
        return await self.get_prescription_instance_by_id(prescription_id)

    async def delete_prescription_instance(self, prescription_id: UUID) -> bool:
        """Delete prescription instance"""
        stmt = select(PrescriptionInstanceModel).where(PrescriptionInstanceModel.id_ == prescription_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.commit()
            return True
        return False

    async def check_prescription_completion(self, prescription_id: UUID) -> bool:
        """Check if prescription should be marked complete based on movement completion"""
        prescription = await self.get_prescription_instance_by_id(prescription_id)
        if not prescription or not prescription.movements:
            return False

        # First, check completion for any movements that have no sets (they should be auto-completed)
        from practices.repository.repositories.movement_instance_repository import (
            MovementInstanceRepository,
        )

        movement_repo = MovementInstanceRepository(self.session)

        for movement in prescription.movements:
            if not movement.sets and not movement.complete:
                await movement_repo.update_movement_instance(movement.id_, {"complete": True})

        # Re-fetch prescription to get updated movement completion status
        prescription = await self.get_prescription_instance_by_id(prescription_id)

        # Prescription is complete if all movements are complete
        all_movements_complete = all(m.complete for m in prescription.movements)

        if all_movements_complete and not prescription.complete:
            await self.update_prescription_instance(prescription_id, {"complete": True})
            return True
        elif not all_movements_complete and prescription.complete:
            await self.update_prescription_instance(prescription_id, {"complete": False})
            return False

        return prescription.complete
