import uuid
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainPrescriptionTemplate
from practices.repository.models import (
    MovementTemplateModel,
    PrescriptionTemplateModel,
    SetTemplateModel,
)


class PrescriptionTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_prescription_template(self, prescription_data: dict) -> DomainPrescriptionTemplate:
        """Create a new prescription template with optional movements"""
        movements_data = prescription_data.pop("movements", [])
        new_prescription = PrescriptionTemplateModel(**prescription_data)
        self.session.add(new_prescription)
        await self.session.flush()
        await self.session.refresh(new_prescription)

        # Create movement templates if provided
        for movement_data in movements_data:
            sets_data = movement_data.pop("sets", [])
            new_movement = MovementTemplateModel(**movement_data, prescription_template_id=new_prescription.id_)
            self.session.add(new_movement)
            await self.session.flush()
            await self.session.refresh(new_movement)

            # Create set templates for the movement
            for set_data in sets_data:
                new_set = SetTemplateModel(**set_data, movement_template_id=new_movement.id_)
                self.session.add(new_set)

        await self.session.refresh(new_prescription)
        return DomainPrescriptionTemplate.model_validate(new_prescription)

    async def get_prescription_template_by_id(self, prescription_id: uuid.UUID) -> Optional[DomainPrescriptionTemplate]:
        """Get prescription template by ID with movements and sets"""
        stmt = (
            select(PrescriptionTemplateModel)
            .where(PrescriptionTemplateModel.id_ == prescription_id)
            .options(selectinload(PrescriptionTemplateModel.movements).selectinload(MovementTemplateModel.sets))
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Convert to domain model
        prescription_dict = {
            "id_": record.id_,
            "practice_template_id": record.practice_template_id,
            "name": record.name,
            "position": record.position,
            "description": record.description,
            "block": record.block,
            "prescribed_rounds": record.prescribed_rounds,
            "created_at": record.created_at,
            "modified_at": record.modified_at,
            "movements": [],
        }

        if record.movements:
            prescription_dict["movements"] = []
            for movement in record.movements:
                movement_dict = {
                    "id_": movement.id_,
                    "prescription_template_id": movement.prescription_template_id,
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
                    "created_at": movement.created_at,
                    "modified_at": movement.modified_at,
                    "sets": [],
                }

                if movement.sets:
                    movement_dict["sets"] = [
                        {
                            "id_": s.id_,
                            "movement_template_id": s.movement_template_id,
                            "position": s.position,
                            "reps": s.reps,
                            "duration": s.duration,
                            "load_value": s.load_value,
                            "load_unit": s.load_unit,
                            "rest_duration": s.rest_duration,
                            "created_at": s.created_at,
                            "modified_at": s.modified_at,
                        }
                        for s in movement.sets
                    ]

                prescription_dict["movements"].append(movement_dict)

        return DomainPrescriptionTemplate.model_validate(prescription_dict)

    async def get_prescription_templates_by_practice_id(
        self, practice_template_id: uuid.UUID
    ) -> List[DomainPrescriptionTemplate]:
        """Get all prescription templates for a practice template"""
        stmt = (
            select(PrescriptionTemplateModel)
            .where(PrescriptionTemplateModel.practice_template_id == practice_template_id)
            .options(selectinload(PrescriptionTemplateModel.movements).selectinload(MovementTemplateModel.sets))
            .order_by(PrescriptionTemplateModel.position)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        prescriptions = []
        for record in records:
            prescription_dict = {
                "id_": record.id_,
                "practice_template_id": record.practice_template_id,
                "name": record.name,
                "position": record.position,
                "description": record.description,
                "block": record.block,
                "prescribed_rounds": record.prescribed_rounds,
                "created_at": record.created_at,
                "modified_at": record.modified_at,
                "movements": [],
            }

            if record.movements:
                prescription_dict["movements"] = []
                for movement in record.movements:
                    movement_dict = {
                        "id_": movement.id_,
                        "prescription_template_id": movement.prescription_template_id,
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
                        "created_at": movement.created_at,
                        "modified_at": movement.modified_at,
                        "sets": [],
                    }

                    if movement.sets:
                        movement_dict["sets"] = [
                            {
                                "id_": s.id_,
                                "movement_template_id": s.movement_template_id,
                                "position": s.position,
                                "reps": s.reps,
                                "duration": s.duration,
                                "load_value": s.load_value,
                                "load_unit": s.load_unit,
                                "rest_duration": s.rest_duration,
                                "created_at": s.created_at,
                                "modified_at": s.modified_at,
                            }
                            for s in movement.sets
                        ]

                    prescription_dict["movements"].append(movement_dict)

            prescriptions.append(DomainPrescriptionTemplate.model_validate(prescription_dict))

        return prescriptions

    async def update_prescription_template(
        self, prescription_id: uuid.UUID, update_data: dict
    ) -> Optional[DomainPrescriptionTemplate]:
        """Update prescription template"""
        stmt = select(PrescriptionTemplateModel).where(PrescriptionTemplateModel.id_ == prescription_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.commit()
        return await self.get_prescription_template_by_id(prescription_id)

    async def delete_prescription_template(self, prescription_id: uuid.UUID) -> bool:
        """Delete prescription template"""
        stmt = select(PrescriptionTemplateModel).where(PrescriptionTemplateModel.id_ == prescription_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.commit()
            return True
        return False

    async def get_template_usage_count(self, template_id: uuid.UUID) -> int:
        """Get number of times this template has been used to create instances"""
        # This would need to query PrescriptionInstanceModel where prescription_template_id = template_id
        # For now, return 0 as placeholder
        return 0

    async def get_programs_using_template(self, template_id: uuid.UUID) -> List:
        """Get programs that use this prescription template"""
        # This would need complex joins through practice templates
        # For now, return empty list as placeholder
        return []
