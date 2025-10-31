import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainMovementInstance
from practices.repository.models import MovementInstanceModel, SetInstanceModel


class MovementInstanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_movement_instance(self, movement_data: dict) -> DomainMovementInstance:
        """Create a new movement instance with optional sets"""
        sets_data = movement_data.pop("sets", [])
        new_movement_model = MovementInstanceModel(**movement_data)
        self.session.add(new_movement_model)
        await self.session.flush()
        await self.session.refresh(new_movement_model)

        created_sets = []
        if sets_data:
            for set_data in sets_data:
                new_set_model = SetInstanceModel(**set_data, movement_instance_id=new_movement_model.id_)
                self.session.add(new_set_model)
                created_sets.append(new_set_model)
            await self.session.flush()

        # Manually construct the domain model to ensure sets are included
        # without needing a premature commit or a separate query.
        movement_dict = {
            key: getattr(new_movement_model, key) for key in new_movement_model.__mapper__.column_attrs.keys()
        }
        movement_dict["sets"] = [
            {key: getattr(s, key) for key in s.__mapper__.column_attrs.keys()} for s in created_sets
        ]

        return DomainMovementInstance.model_validate(movement_dict)

    async def create_movement_from_template(
        self, template_id: uuid.UUID, prescription_instance_id: uuid.UUID, position: int
    ) -> DomainMovementInstance:
        """Create movement instance from template"""
        # First, get the movement template
        from practices.repository.repositories.movement_template_repository import (
            MovementTemplateRepository,
        )

        template_repo = MovementTemplateRepository(self.session)
        template = await template_repo.get_movement_template_by_id(template_id)

        if not template:
            raise ValueError(f"MovementTemplate with id {template_id} not found")

        # Create movement instance with data from template
        movement_data = {
            "prescription_instance_id": prescription_instance_id,
            "template_id": template_id,
            "position": position,
            "name": template.name,
            "description": template.description,
            "metric_unit": template.metric_unit,
            "metric_value": template.metric_value,
            "movement_class": template.movement_class,
            "prescribed_sets": template.prescribed_sets,
            "rest_duration": template.rest_duration,
            "video_url": template.video_url,
            "exercise_id": template.exercise_id,
        }

        # Create the movement instance
        movement_instance = await self.create_movement_instance(movement_data)

        # Create sets from template sets
        if template.sets:
            from practices.repository.repositories.set_instance_repository import (
                SetInstanceRepository,
            )

            set_repo = SetInstanceRepository(self.session)

            for set_template in template.sets:
                set_data = {
                    "movement_instance_id": movement_instance.id_,
                    "template_id": set_template.id_,
                    "position": set_template.position,
                    "reps": set_template.reps,
                    "duration": set_template.duration,
                    "load_value": set_template.load_value,
                    "load_unit": set_template.load_unit,
                    "rest_duration": set_template.rest_duration,
                }
                await set_repo.create(set_data)

        # Return the complete movement instance with sets
        return await self.get_movement_instance_by_id(movement_instance.id_)

    async def get_movement_instance_by_id(self, movement_id: uuid.UUID) -> Optional[DomainMovementInstance]:
        """Get movement instance by ID with sets"""
        stmt = (
            select(MovementInstanceModel)
            .where(MovementInstanceModel.id_ == movement_id)
            .options(selectinload(MovementInstanceModel.sets))
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Convert to domain model
        movement_dict = {
            "id_": record.id_,
            "prescription_instance_id": record.prescription_instance_id,
            "template_id": getattr(record, "template_id", None),
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
            "complete": record.complete,
            "notes": record.notes,
            "completed_at": record.completed_at,
            "created_at": record.created_at,
            "modified_at": record.modified_at,
            "sets": [],
        }

        if record.sets:
            movement_dict["sets"] = [
                {
                    "id_": s.id_,
                    "movement_instance_id": s.movement_instance_id,
                    "template_id": getattr(s, "template_id", None),
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
                for s in record.sets
            ]

        return DomainMovementInstance.model_validate(movement_dict)

    async def get_movement_instances_by_prescription_id(
        self, prescription_instance_id: uuid.UUID
    ) -> List[DomainMovementInstance]:
        """Get all movement instances for a prescription"""
        stmt = (
            select(MovementInstanceModel)
            .where(MovementInstanceModel.prescription_instance_id == prescription_instance_id)
            .options(selectinload(MovementInstanceModel.sets))
            .order_by(MovementInstanceModel.position)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        movements = []
        for record in records:
            movement_dict = {
                "id_": record.id_,
                "prescription_instance_id": record.prescription_instance_id,
                "template_id": getattr(record, "template_id", None),
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
                "complete": record.complete,
                "notes": record.notes,
                "completed_at": record.completed_at,
                "created_at": record.created_at,
                "modified_at": record.modified_at,
                "sets": [],
            }

            if record.sets:
                movement_dict["sets"] = [
                    {
                        "id_": s.id_,
                        "movement_instance_id": s.movement_instance_id,
                        "template_id": getattr(s, "template_id", None),
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
                    for s in record.sets
                ]

            movements.append(DomainMovementInstance.model_validate(movement_dict))

        return movements

    async def get_movement_instances_by_template_id(self, template_id: uuid.UUID) -> List[DomainMovementInstance]:
        """Get all movement instances created from a template"""
        stmt = (
            select(MovementInstanceModel)
            .where(MovementInstanceModel.template_id == template_id)
            .options(selectinload(MovementInstanceModel.sets))
            .order_by(MovementInstanceModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        movements = []
        for record in records:
            movement_dict = {
                "id_": record.id_,
                "prescription_instance_id": record.prescription_instance_id,
                "template_id": getattr(record, "template_id", None),
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
                "complete": record.complete,
                "notes": record.notes,
                "completed_at": record.completed_at,
                "created_at": record.created_at,
                "modified_at": record.modified_at,
                "sets": [],
            }

            if record.sets:
                movement_dict["sets"] = [
                    {
                        "id_": s.id_,
                        "movement_instance_id": s.movement_instance_id,
                        "template_id": getattr(s, "template_id", None),
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
                    for s in record.sets
                ]

            movements.append(DomainMovementInstance.model_validate(movement_dict))

        return movements

    async def update_movement_instance(
        self, movement_id: uuid.UUID, update_data: dict
    ) -> Optional[DomainMovementInstance]:
        """Update movement instance"""
        stmt = select(MovementInstanceModel).where(MovementInstanceModel.id_ == movement_id)
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

        # Return the full movement with relationships loaded
        return await self.get_movement_instance_by_id(movement_id)

    async def delete_movement_instance(self, movement_id: uuid.UUID) -> bool:
        """Delete movement instance"""
        stmt = select(MovementInstanceModel).where(MovementInstanceModel.id_ == movement_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def check_movement_completion(self, movement_id: uuid.UUID) -> bool:
        """Check if movement should be marked complete based on set completion"""
        movement = await self.get_movement_instance_by_id(movement_id)
        if not movement:
            return False

        # If movement has no sets, it should be considered complete
        if not movement.sets:
            if not movement.complete:
                await self.update_movement_instance(movement_id, {"complete": True})
                return True
            else:
                return True

        # Movement is complete if all sets are complete
        all_sets_complete = all(s.complete for s in movement.sets)

        if all_sets_complete and not movement.complete:
            await self.update_movement_instance(movement_id, {"complete": True})
            return True
        elif not all_sets_complete and movement.complete:
            await self.update_movement_instance(movement_id, {"complete": False})
            return False

        return movement.complete
