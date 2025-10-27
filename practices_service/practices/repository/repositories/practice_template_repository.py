import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import (
    DomainPracticeTemplate,  # This will need to be created
)
from practices.repository.models import (
    MovementTemplateModel,
    PracticeTemplateModel,
    PrescriptionTemplateModel,
    SetTemplateModel,
)


class PracticeTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_dict(self, model: PracticeTemplateModel) -> Dict[str, Any]:
        result = {
            "id_": model.id_,
            "created_at": model.created_at,
            "modified_at": model.modified_at,
            "title": model.title,
            "description": model.description,
            "duration": model.duration,
            "user_id": model.user_id,
            "prescriptions": [],
        }

        if model.prescriptions:
            result["prescriptions"] = []
            for pres in model.prescriptions:
                pres_dict = {
                    "id_": pres.id_,
                    "practice_template_id": pres.practice_template_id,
                    "block": pres.block,
                    "name": pres.name,
                    "description": pres.description,
                    "prescribed_rounds": pres.prescribed_rounds,
                    "position": pres.position,
                    "movements": [],
                }
                if pres.movements:
                    pres_dict["movements"] = []
                    for mov in pres.movements:
                        mov_dict = {
                            "id_": mov.id_,
                            "prescription_template_id": mov.prescription_template_id,
                            "name": mov.name,
                            "description": mov.description,
                            "movement_class": mov.movement_class,
                            "metric_unit": mov.metric_unit,
                            "metric_value": mov.metric_value,
                            "prescribed_sets": mov.prescribed_sets,
                            "rest_duration": mov.rest_duration,
                            "position": mov.position,
                            "exercise_id": mov.exercise_id,
                            "movement_id": getattr(mov, "movement_id", None),
                            "sets": [],
                        }
                        if mov.sets:
                            mov_dict["sets"] = []
                            for s in mov.sets:
                                set_dict = {
                                    "id_": s.id_,
                                    "movement_template_id": s.movement_template_id,
                                    "reps": s.reps,
                                    "load_value": s.load_value,
                                    "load_unit": s.load_unit,
                                    "duration": s.duration,
                                    "rest_duration": s.rest_duration,
                                    "position": s.position,
                                }
                                mov_dict["sets"].append(set_dict)
                        pres_dict["movements"].append(mov_dict)
                result["prescriptions"].append(pres_dict)
        return result

    async def create_template_with_nested_data(self, template_data: dict) -> DomainPracticeTemplate:
        prescriptions_data = template_data.pop("prescriptions", [])
        new_template = PracticeTemplateModel(**template_data)
        self.session.add(new_template)
        await self.session.flush()

        for pres_data in prescriptions_data:
            movements_data = pres_data.pop("movements", [])
            new_prescription = PrescriptionTemplateModel(**pres_data, practice_template_id=new_template.id_)
            self.session.add(new_prescription)
            await self.session.flush()

            for mov_data in movements_data:
                sets_data = mov_data.pop("sets", [])
                # Normalize movement fields for DB constraints
                if mov_data.get("metric_unit") is not None:
                    mov_data["metric_unit"] = str(mov_data["metric_unit"]).lower()
                if mov_data.get("movement_class") is not None:
                    mov_data["movement_class"] = str(mov_data["movement_class"]).lower()
                if mov_data.get("rest_duration") is not None:
                    try:
                        mov_data["rest_duration"] = int(mov_data["rest_duration"])
                    except Exception:
                        pass
                if mov_data.get("position") is not None:
                    try:
                        mov_data["position"] = int(mov_data["position"])
                    except Exception:
                        pass
                # movement_id may be provided by client; pass through if present
                new_movement = MovementTemplateModel(**mov_data, prescription_template_id=new_prescription.id_)
                self.session.add(new_movement)
                await self.session.flush()

                for set_data in sets_data:
                    # Normalize set fields for DB constraints
                    if set_data.get("load_unit") is not None:
                        set_data["load_unit"] = str(set_data["load_unit"]).lower()
                    for key in ("reps", "duration", "rest_duration", "position"):
                        if set_data.get(key) is not None:
                            try:
                                set_data[key] = int(set_data[key])
                            except Exception:
                                pass
                    new_set = SetTemplateModel(**set_data, movement_template_id=new_movement.id_)
                    self.session.add(new_set)

        await self.session.commit()

        stmt = (
            select(PracticeTemplateModel)
            .where(PracticeTemplateModel.id_ == new_template.id_)
            .options(
                selectinload(PracticeTemplateModel.prescriptions)
                .selectinload(PrescriptionTemplateModel.movements)
                .selectinload(MovementTemplateModel.sets)
            )
        )
        result = await self.session.execute(stmt)
        refetched_template = result.scalar_one()

        template_dict = self._model_to_dict(refetched_template)
        return DomainPracticeTemplate.model_validate(template_dict)

    async def get_template_by_id(self, template_id: uuid.UUID) -> Optional[DomainPracticeTemplate]:
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
        record = result.scalar_one_or_none()

        if not record:
            return None

        template_dict = self._model_to_dict(record)
        return DomainPracticeTemplate.model_validate(template_dict)

    async def list_templates(self) -> List[DomainPracticeTemplate]:
        stmt = select(PracticeTemplateModel).options(
            selectinload(PracticeTemplateModel.prescriptions)
            .selectinload(PrescriptionTemplateModel.movements)
            .selectinload(MovementTemplateModel.sets)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPracticeTemplate.model_validate(self._model_to_dict(rec)) for rec in records]

    async def update_template(self, template_id: uuid.UUID, update_data: dict) -> Optional[DomainPracticeTemplate]:
        stmt = select(PracticeTemplateModel).where(PracticeTemplateModel.id_ == template_id)
        result = await self.session.execute(stmt)
        template = result.scalar_one_or_none()

        if not template:
            return None

        for key, value in update_data.items():
            setattr(template, key, value)

        await self.session.commit()
        await self.session.refresh(template)

        template_dict = self._model_to_dict(template)
        return DomainPracticeTemplate.model_validate(template_dict)

    async def delete_template(self, template_id: uuid.UUID) -> bool:
        stmt = select(PracticeTemplateModel).where(PracticeTemplateModel.id_ == template_id)
        result = await self.session.execute(stmt)
        template = result.scalar_one_or_none()

        if not template:
            return False

        await self.session.delete(template)
        await self.session.commit()
        return True
