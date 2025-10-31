from __future__ import annotations

from typing import Any, Dict


def external_to_local_row(ex: Dict[str, Any]) -> Dict[str, Any]:
    # Map normalized ExerciseDB payload into our local create shape
    return {
        "name": ex.get("name", ""),
        "slug": (ex.get("name", "").lower().replace(" ", "-")[:120] if ex.get("name") else None),
        "shortVideoUrl": ex.get("videoUrl"),
        "gifUrl": ex.get("imageUrl"),
        "source": "exercise-db",
        "externalId": ex.get("externalId"),
        # Extended attributes we store in link tables or scalars when possible
        "equipment": ex.get("equipments") or [],
        "primaryMuscles": ex.get("targetMuscles") or [],
        "secondaryMuscles": ex.get("secondaryMuscles") or [],
        # Freeform fields stored on scalars not present; instructions stored via MovementInstruction
        "instructions": ex.get("instructions") or [],
        # Keep optional descriptive text
        "overview": ex.get("overview"),
        # Not all fields map 1:1 into current schema (e.g., bodyParts). For now include as tags
        "tags": (ex.get("bodyParts") or []) + (ex.get("keywords") or []),
    } 