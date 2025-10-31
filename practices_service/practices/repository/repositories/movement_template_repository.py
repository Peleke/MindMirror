import uuid
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainMovementTemplate
from practices.repository.models import (
    MovementTemplateModel,
    PracticeTemplateModel,
    PrescriptionTemplateModel,
    SetTemplateModel,
)


class MovementTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_movement_template(self, movement_data: dict) -> DomainMovementTemplate:
        """Create a new movement template with optional set templates"""
        sets_data = movement_data.pop("sets", [])
        new_movement = MovementTemplateModel(**movement_data)
        self.session.add(new_movement)
        await self.session.flush()
        await self.session.refresh(new_movement)

        # Create set templates if provided
        for set_data in sets_data:
            new_set = SetTemplateModel(**set_data, movement_template_id=new_movement.id_)
            self.session.add(new_set)

        await self.session.refresh(new_movement)
        return DomainMovementTemplate.model_validate(new_movement)

    async def get_movement_template_by_id(self, movement_id: uuid.UUID) -> Optional[DomainMovementTemplate]:
        """Get movement template by ID with set templates"""
        stmt = (
            select(MovementTemplateModel)
            .where(MovementTemplateModel.id_ == movement_id)
            .options(selectinload(MovementTemplateModel.sets))
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Convert to domain model
        movement_dict = {
            "id_": record.id_,
            "prescription_template_id": record.prescription_template_id,
            "name": record.name,
            "position": record.position,
            "description": record.description,
            "metric_unit": record.metric_unit,
            "metric_value": record.metric_value,
            "movement_class": record.movement_class,
            "prescribed_sets": record.prescribed_sets,
            "rest_duration": record.rest_duration,
            "video_url": record.video_url,
            "exercise_id": record.exercise_id,
            "movement_id": record.movement_id,
            "sets": [],
        }

        if record.sets:
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
                for s in record.sets
            ]

        return DomainMovementTemplate.model_validate(movement_dict)

    async def get_movement_templates_by_prescription_id(
        self, prescription_template_id: uuid.UUID
    ) -> List[DomainMovementTemplate]:
        """Get all movement templates for a prescription template"""
        stmt = (
            select(MovementTemplateModel)
            .where(MovementTemplateModel.prescription_template_id == prescription_template_id)
            .options(selectinload(MovementTemplateModel.sets))
            .order_by(MovementTemplateModel.position)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        movements = []
        for record in records:
            movement_dict = {
                "id_": record.id_,
                "prescription_template_id": record.prescription_template_id,
                "name": record.name,
                "position": record.position,
                "description": record.description,
                "metric_unit": record.metric_unit,
                "metric_value": record.metric_value,
                "movement_class": record.movement_class,
                "prescribed_sets": record.prescribed_sets,
                "rest_duration": record.rest_duration,
                "video_url": record.video_url,
                "exercise_id": record.exercise_id,
                "movement_id": record.movement_id,
                "created_at": record.created_at,
                "modified_at": record.modified_at,
                "sets": [],
            }

            if record.sets:
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
                    for s in record.sets
                ]

            movements.append(DomainMovementTemplate.model_validate(movement_dict))

        return movements

    async def get_movement_templates_by_coach(self, coach_id: uuid.UUID) -> List[DomainMovementTemplate]:
        """Get all movement templates created by a coach"""
        # Join through prescription template to practice template to get user_id
        stmt = (
            select(MovementTemplateModel)
            .join(PrescriptionTemplateModel)
            .join(PracticeTemplateModel)
            .where(PracticeTemplateModel.user_id == coach_id)
            .options(selectinload(MovementTemplateModel.sets))
            .order_by(MovementTemplateModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        movements = []
        for record in records:
            movement_dict = {
                "id_": record.id_,
                "prescription_template_id": record.prescription_template_id,
                "name": record.name,
                "position": record.position,
                "description": record.description,
                "metric_unit": record.metric_unit,
                "metric_value": record.metric_value,
                "movement_class": record.movement_class,
                "prescribed_sets": record.prescribed_sets,
                "rest_duration": record.rest_duration,
                "video_url": record.video_url,
                "exercise_id": record.exercise_id,
                "movement_id": record.movement_id,
                "created_at": record.created_at,
                "modified_at": record.modified_at,
                "sets": [],
            }

            if record.sets:
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
                    for s in record.sets
                ]

            movements.append(DomainMovementTemplate.model_validate(movement_dict))

        return movements

    async def get_shared_movement_templates_for_user(self, user_id: uuid.UUID) -> List[DomainMovementTemplate]:
        """Get movement templates shared with a user"""
        # This would need to join with a sharing table
        # For now, return empty list as placeholder
        return []

    async def update_movement_template(
        self, movement_id: uuid.UUID, update_data: dict
    ) -> Optional[DomainMovementTemplate]:
        """Update movement template"""
        stmt = select(MovementTemplateModel).where(MovementTemplateModel.id_ == movement_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.commit()
        return await self.get_movement_template_by_id(movement_id)

    async def delete_movement_template(self, movement_id: uuid.UUID) -> bool:
        """Delete movement template"""
        stmt = select(MovementTemplateModel).where(MovementTemplateModel.id_ == movement_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.commit()
            return True
        return False

    async def get_template_usage_count(self, template_id: uuid.UUID) -> int:
        """Get number of times this template has been used to create instances"""
        from practices.repository.models.practice_instance import MovementInstanceModel

        stmt = select(MovementInstanceModel).where(MovementInstanceModel.template_id == template_id)
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        return len(instances)

    async def get_programs_using_template(self, template_id: uuid.UUID) -> List:
        """Get programs that use this movement template"""
        # This would need complex joins through prescription templates and practice templates
        # For now, return empty list as placeholder
        return []

    async def get_template_shares(self, template_id: uuid.UUID) -> List:
        """Get users this template is shared with"""
        # This would need to query a sharing table
        # For now, return empty list as placeholder
        return []
