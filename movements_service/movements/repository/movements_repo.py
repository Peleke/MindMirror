from __future__ import annotations

from typing import Optional, List, Dict
from sqlalchemy import select, delete, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    MovementModel,
    MovementAliasModel,
    MovementMuscleLink,
    MovementEquipmentLink,
    MovementPatternLink,
    MovementPlaneLink,
    MovementTagLink,
    MovementInstruction,
)


async def _links_to_lists(session: AsyncSession, movement_id: str) -> dict:
    res = await session.execute(select(MovementMuscleLink).where(MovementMuscleLink.movement_id == movement_id))
    muscles = res.scalars().all()
    primary = [m.muscle_name for m in muscles if m.role == "primary"]
    secondary = [m.muscle_name for m in muscles if m.role == "secondary"]
    tertiary = [m.muscle_name for m in muscles if m.role == "tertiary"]

    res = await session.execute(select(MovementEquipmentLink).where(MovementEquipmentLink.movement_id == movement_id))
    eq = res.scalars().all()
    equipment = [e.equipment_name for e in eq if e.role == "primary"] + [e.equipment_name for e in eq if e.role == "secondary"]

    res = await session.execute(select(MovementPatternLink).where(MovementPatternLink.movement_id == movement_id).order_by(MovementPatternLink.position.asc()))
    patterns = [p.pattern_name for p in res.scalars().all()]

    res = await session.execute(select(MovementPlaneLink).where(MovementPlaneLink.movement_id == movement_id).order_by(MovementPlaneLink.position.asc()))
    planes = [p.plane_name for p in res.scalars().all()]

    res = await session.execute(select(MovementTagLink).where(MovementTagLink.movement_id == movement_id))
    tags = [t.tag_name for t in res.scalars().all()]

    res = await session.execute(select(MovementInstruction).where(MovementInstruction.movement_id == movement_id).order_by(MovementInstruction.position.asc()))
    instructions = [i.text for i in res.scalars().all()]

    return {
        "primaryMuscles": primary,
        "secondaryMuscles": secondary + tertiary,  # surface both as secondary for now
        "movementPatterns": patterns,
        "planesOfMotion": planes,
        "equipment": equipment,
        "tags": tags,
        "instructions": instructions,
    }


def _row_to_dict(row: MovementModel) -> dict:
    return {
        "id_": row.id_,
        "name": row.name,
        "slug": row.slug,
        "difficulty": row.difficulty,
        "bodyRegion": row.body_region,
        "archetype": row.archetype,
        "description": getattr(row, "description", None),
        "shortVideoUrl": row.short_video_url,
        "longVideoUrl": row.long_video_url,
        "gifUrl": row.gif_url,
        "isPublic": row.is_public,
        "userId": row.user_id,
    }


async def _apply_links(session: AsyncSession, movement_id: str, data: dict) -> None:
    # Replace links only for provided keys
    if "primaryMuscles" in data or "secondaryMuscles" in data or "tertiaryMuscles" in data:
        await session.execute(delete(MovementMuscleLink).where(MovementMuscleLink.movement_id == movement_id))
        for name in data.get("primaryMuscles", []) or []:
            session.add(MovementMuscleLink(movement_id=movement_id, muscle_name=name, role="primary"))
        for name in data.get("secondaryMuscles", []) or []:
            session.add(MovementMuscleLink(movement_id=movement_id, muscle_name=name, role="secondary"))
        for name in data.get("tertiaryMuscles", []) or []:
            session.add(MovementMuscleLink(movement_id=movement_id, muscle_name=name, role="tertiary"))

    if "equipment" in data or "primaryEquipment" in data or "secondaryEquipment" in data:
        await session.execute(delete(MovementEquipmentLink).where(MovementEquipmentLink.movement_id == movement_id))
        for name in (data.get("primaryEquipment") or data.get("equipment") or []):
            session.add(MovementEquipmentLink(movement_id=movement_id, equipment_name=name, role="primary", item_count=None))
        for name in data.get("secondaryEquipment", []) or []:
            session.add(MovementEquipmentLink(movement_id=movement_id, equipment_name=name, role="secondary", item_count=None))

    if "movementPatterns" in data:
        await session.execute(delete(MovementPatternLink).where(MovementPatternLink.movement_id == movement_id))
        for idx, name in enumerate(data.get("movementPatterns") or [], start=1):
            session.add(MovementPatternLink(movement_id=movement_id, pattern_name=name, position=idx))

    if "planesOfMotion" in data:
        await session.execute(delete(MovementPlaneLink).where(MovementPlaneLink.movement_id == movement_id))
        for idx, name in enumerate(data.get("planesOfMotion") or [], start=1):
            session.add(MovementPlaneLink(movement_id=movement_id, plane_name=name, position=idx))

    if "tags" in data:
        await session.execute(delete(MovementTagLink).where(MovementTagLink.movement_id == movement_id))
        for name in data.get("tags") or []:
            session.add(MovementTagLink(movement_id=movement_id, tag_name=name))

    if "instructions" in data:
        await session.execute(delete(MovementInstruction).where(MovementInstruction.movement_id == movement_id))
        for idx, text in enumerate(data.get("instructions") or [], start=1):
            session.add(MovementInstruction(movement_id=movement_id, position=idx, text=text))


class MovementsRepoPg:
    def __init__(self, session: AsyncSession):
        self.session = session
        # NOTE: DB should ideally enforce unique (source, external_id) to ensure idempotent imports.
        # See data/alter_movements_external.sql for an index option.

    async def get(self, id_: str) -> Optional[dict]:
        async with self.session.begin():
            res = await self.session.execute(select(MovementModel).where(MovementModel.id_ == id_))
            row = res.scalar_one_or_none()
            if not row:
                return None
            data = _row_to_dict(row)
            data.update(await _links_to_lists(self.session, row.id_))
            return data

    async def get_by_external(self, source: str, external_id: str) -> Optional[dict]:
        if not source or not external_id:
            return None
        async with self.session.begin():
            res = await self.session.execute(
                select(MovementModel).where(MovementModel.source == source, MovementModel.external_id == external_id)
            )
            row = res.scalar_one_or_none()
        if not row:
            return None
        data = _row_to_dict(row)
        data.update(await _links_to_lists(self.session, row.id_))
        return data

    async def get_many(self, ids: List[str]) -> Dict[str, dict]:
        if not ids:
            return {}
        unique_ids = list({str(i) for i in ids})
        out: Dict[str, dict] = {}
        async with self.session.begin():
            res = await self.session.execute(select(MovementModel).where(MovementModel.id_.in_(unique_ids)))
            rows = res.scalars().all()
            for r in rows:
                out[r.id_] = _row_to_dict(r)

            # Bulk fetch links
            # Muscles
            res = await self.session.execute(select(MovementMuscleLink).where(MovementMuscleLink.movement_id.in_(unique_ids)))
            for m in res.scalars().all():
                d = out.get(m.movement_id)
                if d is None:
                    continue
                # Initialize lists lazily
                d.setdefault("_primaryMuscles", [])
                d.setdefault("_secondaryMuscles", [])
                if m.role == "primary":
                    d["_primaryMuscles"].append(m.muscle_name)
                else:
                    d["_secondaryMuscles"].append(m.muscle_name)

            # Equipment
            res = await self.session.execute(select(MovementEquipmentLink).where(MovementEquipmentLink.movement_id.in_(unique_ids)))
            for e in res.scalars().all():
                d = out.get(e.movement_id)
                if d is None:
                    continue
                d.setdefault("_equipment", [])
                d["_equipment"].append(e.equipment_name)

            # Patterns (preserve order by position)
            res = await self.session.execute(
                select(MovementPatternLink).where(MovementPatternLink.movement_id.in_(unique_ids)).order_by(MovementPatternLink.movement_id.asc(), MovementPatternLink.position.asc())
            )
            for p in res.scalars().all():
                d = out.get(p.movement_id)
                if d is None:
                    continue
                d.setdefault("_patterns", [])
                d["_patterns"].append(p.pattern_name)

            # Planes
            res = await self.session.execute(
                select(MovementPlaneLink).where(MovementPlaneLink.movement_id.in_(unique_ids)).order_by(MovementPlaneLink.movement_id.asc(), MovementPlaneLink.position.asc())
            )
            for pl in res.scalars().all():
                d = out.get(pl.movement_id)
                if d is None:
                    continue
                d.setdefault("_planes", [])
                d["_planes"].append(pl.plane_name)

            # Tags
            res = await self.session.execute(select(MovementTagLink).where(MovementTagLink.movement_id.in_(unique_ids)))
            for t in res.scalars().all():
                d = out.get(t.movement_id)
                if d is None:
                    continue
                d.setdefault("_tags", [])
                d["_tags"].append(t.tag_name)

            # Instructions
            res = await self.session.execute(
                select(MovementInstruction).where(MovementInstruction.movement_id.in_(unique_ids)).order_by(MovementInstruction.movement_id.asc(), MovementInstruction.position.asc())
            )
            for inst in res.scalars().all():
                d = out.get(inst.movement_id)
                if d is None:
                    continue
                d.setdefault("_instructions", [])
                d["_instructions"].append(inst.text)

        # Normalize lists into public keys expected by mappers
        for k, v in out.items():
            v["primaryMuscles"] = v.pop("_primaryMuscles", [])
            # Surface all non-primary as secondary, consistent with single fetch path
            v["secondaryMuscles"] = v.pop("_secondaryMuscles", [])
            v["movementPatterns"] = v.pop("_patterns", [])
            v["planesOfMotion"] = v.pop("_planes", [])
            v["equipment"] = v.pop("_equipment", [])
            v["tags"] = v.pop("_tags", [])
            v["instructions"] = v.pop("_instructions", [])

        return out

    async def search(
        self,
        searchTerm: Optional[str] = None,
        bodyRegion: Optional[str] = None,
        pattern: Optional[str] = None,
        equipment: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> List[dict]:
        stmt = select(MovementModel).order_by(MovementModel.name.asc()).limit(limit).offset(offset)
        if searchTerm:
            ilike = f"%{searchTerm}%"
            stmt = stmt.where(or_(MovementModel.name.ilike(ilike), MovementModel.slug.ilike(ilike)))
        if bodyRegion:
            stmt = stmt.where(MovementModel.body_region == bodyRegion)
        if pattern:
            sub = select(MovementPatternLink.movement_id).where(MovementPatternLink.pattern_name == pattern)
            stmt = stmt.where(MovementModel.id_.in_(sub))
        if equipment:
            sub = select(MovementEquipmentLink.movement_id).where(MovementEquipmentLink.equipment_name == equipment)
            stmt = stmt.where(MovementModel.id_.in_(sub))

        async with self.session.begin():
            res = await self.session.execute(stmt)
            rows = res.scalars().all()
        out: List[dict] = []
        for r in rows:
            d = _row_to_dict(r)
            d.update(await _links_to_lists(self.session, r.id_))
            out.append(d)
        return out

    async def create(self, user_id: Optional[str], data: dict) -> dict:
        slug = data.get("slug") or (data.get("name", "").lower().replace(" ", "-"))
        model = MovementModel(
            slug=slug,
            name=data.get("name", ""),
            difficulty=data.get("difficulty"),
            body_region=data.get("bodyRegion"),
            target_muscle_group=data.get("targetMuscleGroup"),
            prime_mover_muscle=data.get("primeMoverMuscle"),
            posture=data.get("posture"),
            arm_mode=data.get("armMode"),
            arm_pattern=data.get("armPattern"),
            grip=data.get("grip"),
            load_position=data.get("loadPosition"),
            leg_pattern=data.get("legPattern"),
            foot_elevation=data.get("footElevation"),
            combo_type=data.get("comboType"),
            mechanics=data.get("mechanics"),
            laterality=data.get("laterality"),
            primary_classification=data.get("primaryClassification"),
            force_type=data.get("forceType"),
            archetype=data.get("archetype"),
            description=data.get("description"),
            short_video_url=data.get("shortVideoUrl"),
            long_video_url=data.get("longVideoUrl"),
            gif_url=data.get("gifUrl"),
            source=data.get("source"),
            external_id=data.get("externalId"),
            is_public=bool(data.get("isPublic", user_id is None)),
            user_id=user_id,
        )
        self.session.add(model)
        await self.session.flush()
        await _apply_links(self.session, model.id_, data)
        await self.session.commit()
        await self.session.refresh(model)
        d = _row_to_dict(model)
        d.update(await _links_to_lists(self.session, model.id_))
        return d

    async def update(self, id_: str, data: dict) -> Optional[dict]:
        res = await self.session.execute(select(MovementModel).where(MovementModel.id_ == id_))
        model = res.scalar_one_or_none()
        if not model:
            return None
        # Scalars
        for key, attr in (
            ("name", "name"),
            ("slug", "slug"),
            ("difficulty", "difficulty"),
            ("bodyRegion", "body_region"),
            ("targetMuscleGroup", "target_muscle_group"),
            ("primeMoverMuscle", "prime_mover_muscle"),
            ("posture", "posture"),
            ("armMode", "arm_mode"),
            ("armPattern", "arm_pattern"),
            ("grip", "grip"),
            ("loadPosition", "load_position"),
            ("legPattern", "leg_pattern"),
            ("footElevation", "foot_elevation"),
            ("comboType", "combo_type"),
            ("mechanics", "mechanics"),
            ("laterality", "laterality"),
            ("primaryClassification", "primary_classification"),
            ("forceType", "force_type"),
            ("archetype", "archetype"),
            ("description", "description"),
            ("shortVideoUrl", "short_video_url"),
            ("longVideoUrl", "long_video_url"),
            ("gifUrl", "gif_url"),
        ):
            if key in data:
                setattr(model, attr, data[key])
        # Links
        await _apply_links(self.session, id_, data)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(model)
        d = _row_to_dict(model)
        d.update(await _links_to_lists(self.session, model.id_))
        return d

    async def delete(self, id_: str) -> bool:
        res = await self.session.execute(select(MovementModel).where(MovementModel.id_ == id_))
        model = res.scalar_one_or_none()
        if not model:
            return False
        await self.session.execute(delete(MovementMuscleLink).where(MovementMuscleLink.movement_id == id_))
        await self.session.execute(delete(MovementEquipmentLink).where(MovementEquipmentLink.movement_id == id_))
        await self.session.execute(delete(MovementPatternLink).where(MovementPatternLink.movement_id == id_))
        await self.session.execute(delete(MovementPlaneLink).where(MovementPlaneLink.movement_id == id_))
        await self.session.execute(delete(MovementTagLink).where(MovementTagLink.movement_id == id_))
        await self.session.execute(delete(MovementInstruction).where(MovementInstruction.movement_id == id_))
        await self.session.delete(model)
        await self.session.flush()
        await self.session.commit()
        return True 