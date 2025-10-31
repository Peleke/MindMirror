import strawberry

from .enrollment_types import ProgramEnrollmentTypeGQL
from .federation import (
    ArchetypeRef,
    EquipmentRef,
    ExerciseType,
    ProgressionRef,
    RegressionRef,
)
from .practice_instance_types import (
    MovementInstanceType,
    PracticeInstanceType,
    PrescriptionInstanceType,
    SetInstanceType,
)
from .practice_template_types import (
    MovementTemplateType,
    PracticeTemplateType,
    PrescriptionTemplateType,
    SetTemplateType,
)
from .resolvers import Mutation, Query
from .program_types import (
    ProgramPracticeLinkType,
    ProgramTagType,
    ProgramType,
)

# from strawberry.federation.schema_directives import Key # Key not directly used here


# Key directive for ExerciseType is defined on the type itself via keys=["id"]


def get_schema(extensions=None):
    """
    Returns a schema with optional extensions.

    Args:
        extensions: Optional list of Strawberry extensions

    Returns:
        A Strawberry Federation Schema
    """
    return strawberry.federation.Schema(
        query=Query,
        mutation=Mutation,
        types=[
            # Instance Types
            PracticeInstanceType,
            PrescriptionInstanceType,
            MovementInstanceType,
            SetInstanceType,
            # Template Types
            PracticeTemplateType,
            PrescriptionTemplateType,
            MovementTemplateType,
            SetTemplateType,
            # Federation Types
            ExerciseType,
            ArchetypeRef,
            EquipmentRef,
            ProgressionRef,
            RegressionRef,
            # Program Types
            ProgramType,
            ProgramTagType,
            ProgramPracticeLinkType,
            # Enrollment Types
            ProgramEnrollmentTypeGQL,
        ],
        enable_federation_2=True,
        extensions=extensions,
    )


# Keep the default schema without extensions for backward compatibility
schema = get_schema()

__all__ = ["schema", "get_schema"]
