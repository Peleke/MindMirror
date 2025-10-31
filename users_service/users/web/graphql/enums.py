import enum

import strawberry


# Mirroring users.repository.models.ServiceEnum
@strawberry.enum
class ServiceTypeGQL(enum.Enum):
    MEALS = "meals"
    PRACTICE = "practice"
    SHADOW_BOXING = "shadow_boxing"
    FITNESS_DB = "fitness_db"
    PROGRAMS = "programs"


__all__ = ["ServiceTypeGQL"]
