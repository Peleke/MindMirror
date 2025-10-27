import strawberry


# Placeholder Ref types for entities from other services
@strawberry.federation.type(keys=["id"], name="Archetype")
class ArchetypeRef:
    id: strawberry.ID


@strawberry.federation.type(keys=["id"], name="Equipment")
class EquipmentRef:
    id: strawberry.ID


@strawberry.federation.type(keys=["id"], name="Progression")
class ProgressionRef:
    id: strawberry.ID


@strawberry.federation.type(keys=["id"], name="Regression")
class RegressionRef:
    id: strawberry.ID


@strawberry.federation.type(keys=["id"])  # legacy, kept for backward-compat where needed
class ExerciseType:
    id: strawberry.ID

    @classmethod
    async def resolve_reference(cls, id: strawberry.ID):
        # This is a stub resolver for the federation gateway.
        # It allows other services to resolve an Exercise by its ID.
        return cls(id=id)


# Movements service entity reference (matches Movements schema: keys=["id_"])
@strawberry.federation.type(keys=["id_"], name="Movement")
class MovementRef:
    id_: strawberry.ID

    @classmethod
    async def resolve_reference(cls, id_: strawberry.ID):
        return cls(id_=id_)


__all__ = [
    "ArchetypeRef",
    "EquipmentRef",
    "ProgressionRef",
    "RegressionRef",
    "ExerciseType",
    "MovementRef",
]
