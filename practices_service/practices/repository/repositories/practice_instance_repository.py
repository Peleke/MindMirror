import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainPracticeInstance
from practices.repository.models import (
    MovementInstanceModel,
    MovementTemplateModel,
    PracticeInstanceModel,
    PracticeTemplateModel,
    PrescriptionInstanceModel,
    PrescriptionTemplateModel,
    SetInstanceModel,
    SetTemplateModel,
)
from practices.repository.models.program import ProgramPracticeLinkModel


class PracticeInstanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_dict(self, model: PracticeInstanceModel) -> Dict[str, Any]:
        result = {
            "id_": model.id_,
            "created_at": model.created_at,
            "modified_at": model.modified_at,
            "date": model.date,
            "title": model.title,
            "description": model.description,
            "duration": model.duration,
            "completed_at": model.completed_at,
            "notes": model.notes,
            "user_id": model.user_id,
            "template_id": model.template_id,
            "prescriptions": [],
        }

        if model.prescriptions:
            result["prescriptions"] = []
            for pres in model.prescriptions:
                pres_dict = {
                    "id_": pres.id_,
                    "practice_instance_id": pres.practice_instance_id,
                    "block": pres.block,
                    "name": pres.name,
                    "description": pres.description,
                    "prescribed_rounds": pres.prescribed_rounds,
                    "position": pres.position,
                    "notes": pres.notes,
                    "template_id": pres.template_id,
                    "movements": [],
                }
                if pres.movements:
                    pres_dict["movements"] = []
                    for mov in pres.movements:
                        mov_dict = {
                            "id_": mov.id_,
                            "prescription_instance_id": mov.prescription_instance_id,
                            "name": mov.name,
                            "description": mov.description,
                            "movement_class": mov.movement_class,
                            "metric_unit": mov.metric_unit,
                            "metric_value": mov.metric_value,
                            "prescribed_sets": mov.prescribed_sets,
                            "rest_duration": mov.rest_duration,
                            "video_url": mov.video_url,
                            "position": mov.position,
                            "notes": mov.notes,
                            "exercise_id": mov.exercise_id,
                            # movement_id column does not exist on MovementInstanceModel; use template_id as the movement reference exposed as movement { id_ }
                            "movement_id": mov.template_id,
                            "template_id": mov.template_id,
                            "sets": [],
                        }
                        if mov.sets:
                            mov_dict["sets"] = []
                            for s in mov.sets:
                                set_dict = {
                                    "id_": s.id_,
                                    "movement_instance_id": s.movement_instance_id,
                                    "reps": s.reps,
                                    "load_value": s.load_value,
                                    "load_unit": s.load_unit,
                                    "duration": s.duration,
                                    "rest_duration": s.rest_duration,
                                    "perceived_exertion": s.perceived_exertion,
                                    "notes": s.notes,
                                    "position": s.position,
                                    "template_id": s.template_id,
                                }
                                mov_dict["sets"].append(set_dict)
                        pres_dict["movements"].append(mov_dict)
                result["prescriptions"].append(pres_dict)
        return result

    async def create_standalone_instance(self, instance_data: dict) -> DomainPracticeInstance:
        prescriptions_data = instance_data.pop("prescriptions", [])
        # Ensure we can accept camelCase keys coming from GQL layer
        new_instance = PracticeInstanceModel(
            title=instance_data.get("title"),
            date=instance_data.get("date"),
            description=instance_data.get("description"),
            duration=instance_data.get("duration", 0.0) or 0.0,
            notes=instance_data.get("notes"),
            user_id=instance_data.get("user_id"),
            template_id=instance_data.get("template_id"),
        )
        self.session.add(new_instance)
        await self.session.flush()

        for pres_data in prescriptions_data:
            movements_data = pres_data.pop("movements", [])
            # Map camelCase to model fields
            new_prescription = PrescriptionInstanceModel(
                name=pres_data.get("name"),
                description=pres_data.get("description", ""),
                block=pres_data.get("block"),
                prescribed_rounds=pres_data.get("prescribed_rounds", pres_data.get("prescribedRounds", 1)) or 1,
                position=pres_data.get("position", 0) or 0,
                practice_instance_id=new_instance.id_,
            )
            self.session.add(new_prescription)
            await self.session.flush()

            for mov_data in movements_data:
                sets_data = mov_data.pop("sets", [])
                new_movement = MovementInstanceModel(
                    name=mov_data.get("name"),
                    description=mov_data.get("description", ""),
                    movement_class=mov_data.get("movement_class", mov_data.get("movementClass", "other")),
                    metric_unit=mov_data.get("metric_unit", mov_data.get("metricUnit", "iterative")),
                    metric_value=mov_data.get("metric_value", mov_data.get("metricValue", 1.0)) or 1.0,
                    prescribed_sets=mov_data.get("prescribed_sets", mov_data.get("prescribedSets", 0)) or 0,
                    rest_duration=mov_data.get("rest_duration", mov_data.get("restDuration", 0)) or 0,
                    video_url=mov_data.get("video_url", mov_data.get("videoUrl")),
                    position=mov_data.get("position", 0) or 0,
                    notes=mov_data.get("notes"),
                    exercise_id=mov_data.get("exercise_id", mov_data.get("exerciseId")),
                    template_id=mov_data.get("template_id", mov_data.get("templateId")),
                    prescription_instance_id=new_prescription.id_,
                )
                self.session.add(new_movement)
                await self.session.flush()

                for set_data in sets_data:
                    new_set = SetInstanceModel(
                        position=set_data.get("position", 0) or 0,
                        reps=set_data.get("reps"),
                        load_value=set_data.get("load_value", set_data.get("loadValue")),
                        load_unit=set_data.get("load_unit", set_data.get("loadUnit")),
                        duration=set_data.get("duration"),
                        rest_duration=set_data.get("rest_duration", set_data.get("restDuration", 0)) or 0,
                        perceived_exertion=set_data.get("perceived_exertion"),
                        notes=set_data.get("notes"),
                        movement_instance_id=new_movement.id_,
                    )
                    self.session.add(new_set)

        await self.session.commit()

        stmt = (
            select(PracticeInstanceModel)
            .where(PracticeInstanceModel.id_ == new_instance.id_)
            .options(
                selectinload(PracticeInstanceModel.prescriptions)
                .selectinload(PrescriptionInstanceModel.movements)
                .selectinload(MovementInstanceModel.sets)
            )
        )
        result = await self.session.execute(stmt)
        refetched_instance = result.scalar_one()

        instance_dict = self._model_to_dict(refetched_instance)
        return DomainPracticeInstance.model_validate(instance_dict)

    async def create_instance_from_template(
        self, template_id: uuid.UUID, user_id: uuid.UUID, date: date
    ) -> DomainPracticeInstance:
        # 1. Fetch the full template
        stmt = (
            select(PracticeTemplateModel)
            .where(PracticeTemplateModel.id_ == template_id)
            .options(
                selectinload(PracticeTemplateModel.prescriptions)
                .selectinload(PrescriptionTemplateModel.movements)
                .selectinload(MovementTemplateModel.sets)
            )
        )
        result = await self.session.execute(stmt)
        template = result.scalar_one_or_none()

        if not template:
            raise ValueError("Template not found")

        # 2. Create the instance
        instance_data = {
            "title": template.title,
            "description": template.description,
            "duration": template.duration,
            "user_id": user_id,
            "template_id": template.id_,
            "date": date,
            "prescriptions": [],
        }

        for pres_template in template.prescriptions:
            prescription_data = {
                "name": pres_template.name,
                "description": pres_template.description,
                "block": pres_template.block,
                "prescribed_rounds": pres_template.prescribed_rounds,
                "position": pres_template.position,
                "template_id": pres_template.id_,
                "movements": [],
            }
            for mov_template in pres_template.movements:
                movement_data = {
                    "name": mov_template.name,
                    "description": mov_template.description,
                    "metric_unit": mov_template.metric_unit,
                    "metric_value": mov_template.metric_value,
                    "movement_class": mov_template.movement_class,
                    "prescribed_sets": mov_template.prescribed_sets,
                    "rest_duration": mov_template.rest_duration,
                    "video_url": mov_template.video_url,
                    "movement_id": mov_template.movement_id,
                    "position": mov_template.position,
                    "exercise_id": mov_template.exercise_id,
                    "template_id": mov_template.id_,
                    "sets": [],
                }
                for set_template in mov_template.sets:
                    set_data = {
                        "reps": set_template.reps,
                        "load_value": set_template.load_value,
                        "load_unit": set_template.load_unit,
                        "duration": set_template.duration,
                        "rest_duration": set_template.rest_duration,
                        "position": set_template.position,
                        "template_id": set_template.id_,
                    }
                    movement_data["sets"].append(set_data)
                prescription_data["movements"].append(movement_data)
            instance_data["prescriptions"].append(prescription_data)

        return await self.create_standalone_instance(instance_data)

    async def get_instance_by_id(self, instance_id: uuid.UUID) -> Optional[DomainPracticeInstance]:
        stmt = (
            select(PracticeInstanceModel)
            .where(PracticeInstanceModel.id_ == instance_id)
            .options(
                selectinload(PracticeInstanceModel.prescriptions)
                .selectinload(PrescriptionInstanceModel.movements)
                .selectinload(MovementInstanceModel.sets)
            )
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        instance_dict = self._model_to_dict(record)
        return DomainPracticeInstance.model_validate(instance_dict)

    async def list_instances_for_user(self, user_id: uuid.UUID) -> List[DomainPracticeInstance]:
        stmt = (
            select(PracticeInstanceModel)
            .where(PracticeInstanceModel.user_id == user_id)
            .options(
                selectinload(PracticeInstanceModel.prescriptions)
                .selectinload(PrescriptionInstanceModel.movements)
                .selectinload(MovementInstanceModel.sets)
            )
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPracticeInstance.model_validate(self._model_to_dict(rec)) for rec in records]

    async def list_instances_by_date_range(
        self,
        user_id: uuid.UUID,
        date_from: date,
        date_to: date,
        program_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> List[DomainPracticeInstance]:
        stmt = (
            select(PracticeInstanceModel)
            .where(PracticeInstanceModel.user_id == user_id)
            .where(PracticeInstanceModel.date >= date_from)
            .where(PracticeInstanceModel.date <= date_to)
            .options(
                selectinload(PracticeInstanceModel.prescriptions)
                .selectinload(PrescriptionInstanceModel.movements)
                .selectinload(MovementInstanceModel.sets)
            )
        )
        # Filter by program via template links
        if program_id:
            sub = (
                select(ProgramPracticeLinkModel.practice_template_id)
                .where(ProgramPracticeLinkModel.program_id == program_id)
            )
            stmt = stmt.where(PracticeInstanceModel.template_id.in_(sub))

        # Status filter: scheduled/completed/missed
        today = date.today()
        if status:
            s = status.lower()
            if s == "completed":
                stmt = stmt.where(PracticeInstanceModel.completed_at.is_not(None))
            elif s == "scheduled":
                stmt = stmt.where(PracticeInstanceModel.completed_at.is_(None)).where(PracticeInstanceModel.date >= today)
            elif s == "missed":
                stmt = stmt.where(PracticeInstanceModel.completed_at.is_(None)).where(PracticeInstanceModel.date < today)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPracticeInstance.model_validate(self._model_to_dict(rec)) for rec in records]

    async def list_instances_on_dates(
        self,
        user_id: uuid.UUID,
        dates: List[date],
        program_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> List[DomainPracticeInstance]:
        if not dates:
            return []
        stmt = (
            select(PracticeInstanceModel)
            .where(PracticeInstanceModel.user_id == user_id)
            .where(PracticeInstanceModel.date.in_(dates))
            .options(
                selectinload(PracticeInstanceModel.prescriptions)
                .selectinload(PrescriptionInstanceModel.movements)
                .selectinload(MovementInstanceModel.sets)
            )
        )
        if program_id:
            sub = (
                select(ProgramPracticeLinkModel.practice_template_id)
                .where(ProgramPracticeLinkModel.program_id == program_id)
            )
            stmt = stmt.where(PracticeInstanceModel.template_id.in_(sub))

        today = date.today()
        if status:
            s = status.lower()
            if s == "completed":
                stmt = stmt.where(PracticeInstanceModel.completed_at.is_not(None))
            elif s == "scheduled":
                stmt = stmt.where(PracticeInstanceModel.completed_at.is_(None)).where(PracticeInstanceModel.date >= today)
            elif s == "missed":
                stmt = stmt.where(PracticeInstanceModel.completed_at.is_(None)).where(PracticeInstanceModel.date < today)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPracticeInstance.model_validate(self._model_to_dict(rec)) for rec in records]

    async def update_instance(self, instance_id: uuid.UUID, update_data: dict) -> Optional[DomainPracticeInstance]:
        stmt = select(PracticeInstanceModel).where(PracticeInstanceModel.id_ == instance_id)
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()

        if not instance:
            return None

        for key, value in update_data.items():
            setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)

        instance_dict = self._model_to_dict(instance)
        return DomainPracticeInstance.model_validate(instance_dict)

    async def delete_instance(self, instance_id: uuid.UUID) -> bool:
        stmt = select(PracticeInstanceModel).where(PracticeInstanceModel.id_ == instance_id)
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()

        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        return True
