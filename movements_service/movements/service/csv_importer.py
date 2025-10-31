from __future__ import annotations

import csv
from typing import Iterable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..repository.movements_repo import MovementsRepoPg


async def import_movements_csv(session: AsyncSession, csv_path: str) -> int:
    repo = MovementsRepoPg(session)
    count = 0
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            name = (row.get("Exercise") or "").strip()
            if not name:
                continue
            data = {
                "name": name,
                "difficulty": (row.get("Difficulty Level") or None),
                "bodyRegion": (row.get("Body Region") or None),
                "targetMuscleGroup": (row.get("Target Muscle Group ") or None),
                "primeMoverMuscle": (row.get("Prime Mover Muscle") or None),
                "secondaryMuscles": [m.strip() for m in (row.get("Secondary Muscle") or "").split("/") if m.strip()],
                "tertiaryMuscles": [m.strip() for m in (row.get("Tertiary Muscle") or "").split("/") if m.strip()],
                "primaryEquipment": [e.strip() for e in (row.get("Primary Equipment ") or "").split("/") if e.strip()],
                "movementPatterns": [p.strip() for p in [row.get("Movement Pattern #1"), row.get("Movement Pattern #2"), row.get("Movement Pattern #3")] if p and p.strip()],
                "planesOfMotion": [p.strip() for p in [row.get("Plane Of Motion #1"), row.get("Plane Of Motion #2"), row.get("Plane Of Motion #3")] if p and p.strip()],
                "posture": (row.get("Posture") or None),
                "armMode": (row.get("Single or Double Arm") or None),
                "armPattern": (row.get("Continuous or Alternating Arms ") or None),
                "grip": (row.get("Grip") or None),
                "loadPosition": (row.get("Load Position (Ending)") or None),
                "legPattern": (row.get("Continuous or Alternating Legs ") or None),
                "footElevation": (row.get("Foot Elevation") or None),
                "comboType": (row.get("Combination Exercises") or None),
                "mechanics": (row.get("Mechanics") or None),
                "laterality": (row.get("Laterality") or None),
                "primaryClassification": (row.get("Primary Exercise Classification") or None),
            }
            try:
                await repo.create(user_id=None, data=data)
                count += 1
            except IntegrityError:
                # Likely a duplicate slug/name; skip and continue
                await session.rollback()
                continue
        await session.commit()
    return count 