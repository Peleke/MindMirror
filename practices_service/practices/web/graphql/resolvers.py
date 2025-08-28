from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

import strawberry
from shared.auth import CurrentUser
from shared.clients.user_service_client import users_service_client
from strawberry.types import Info

from practices.domain.models import (
    DomainMovementInstance,
    DomainMovementTemplate,
    DomainPracticeInstance,
    DomainPracticeTemplate,
    DomainPrescriptionInstance,
    DomainPrescriptionTemplate,
    DomainProgram,
    DomainProgramPracticeLink,
    DomainSetInstance,
    DomainSetTemplate,
)
from practices.repository.models import ProgramPracticeLinkModel
from practices.repository.models.practice_template import (
    MovementTemplateModel,
    PrescriptionTemplateModel,
    SetTemplateModel,
)
from practices.repository.repositories import (
    MovementInstanceRepository,
    MovementTemplateRepository,
    PracticeInstanceRepository,
    PracticeTemplateRepository,
    PrescriptionInstanceRepository,
    PrescriptionTemplateRepository,
    ProgramRepository,
    SetInstanceRepository,
    SetTemplateRepository,
)
from practices.repository.uow import UnitOfWork
from practices.service.services import (
    MovementInstanceService,
    MovementTemplateService,
    PracticeInstanceService,
    PracticeTemplateService,
    PrescriptionInstanceService,
    PrescriptionTemplateService,
    ProgramService,
    SetInstanceService,
    SetTemplateService,
)

from .enrollment_resolvers import EnrollmentMutation, EnrollmentQuery
from .enums import MetricUnitGQL, MovementClassGQL
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
from .program_types import (
    ProgramPracticeLinkType,
    ProgramTagType,
    ProgramType,
    ProgramCreateInput,
    ProgramUpdateInput,
)


# Helper function to recursively convert Strawberry input objects to dicts
def to_dict(obj):
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "__dict__"):
        return {k: to_dict(v) for k, v in vars(obj).items()}
    elif isinstance(obj, list):
        return [to_dict(i) for i in obj]
    else:
        return obj


# Helper function to get current user from GraphQL context
def get_current_user_from_info(info: Info) -> Optional[CurrentUser]:
    """Get current user from GraphQL context"""
    return info.context.get("current_user")


# Helper functions for authorization
async def is_coach(user: CurrentUser) -> bool:
    """Checks if a user has a coach role."""
    return user.has_role("coach", "practices")


async def is_coach_by_id(user_id: UUID) -> bool:
    """Check if a user is a coach by their ID."""
    # In a real scenario, we might want to cache this.
    # This is inefficient as it fetches roles for every check.
    roles = await users_service_client.get_user_roles(user_id)
    if roles is None:
        return False
    return any(r.role == "coach" and r.domain == "practices" for r in roles)


async def is_coach_for_client(coach_user: CurrentUser, client_id: UUID) -> bool:
    """Check if coach has relationship with client"""
    if not await is_coach(coach_user):
        return False
    return await users_service_client.verify_coach_client_relationship(
        coach_id=coach_user.id, client_id=client_id, domain="practices"
    )


async def has_template_access(template_id: UUID, user_id: UUID) -> bool:
    """Check if user has access to template (through sharing)"""
    # This would check template sharing permissions
    # For now, return False (only owners can access)
    return False


# Input types for mutations


# Phase 1: Instance Input Types
@strawberry.input
class NestedSetInstanceCreateInput:
    position: int
    reps: Optional[int] = None
    duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[str] = None
    rest_duration: Optional[int] = None
    complete: bool = False
    perceived_exertion: Optional[int] = None
    notes: Optional[str] = None


@strawberry.input
class NestedMovementInstanceCreateInput:
    name: str
    position: int
    metric_unit: MetricUnitGQL
    metric_value: float
    description: Optional[str] = None
    movement_class: Optional[MovementClassGQL] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None
    video_url: Optional[str] = None
    exercise_id: Optional[strawberry.ID] = None
    sets: List[NestedSetInstanceCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class SetInstanceCreateInput:
    movement_instance_id: strawberry.ID
    position: int
    reps: Optional[int] = None
    duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[str] = None
    rest_duration: Optional[int] = None
    complete: bool = False
    perceived_exertion: Optional[int] = None
    notes: Optional[str] = None


@strawberry.input
class SetInstanceUpdateInput:
    reps: Optional[int] = None
    duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[str] = None
    rest_duration: Optional[int] = None
    complete: Optional[bool] = None
    perceived_exertion: Optional[int] = None
    notes: Optional[str] = None


@strawberry.input
class MovementInstanceCreateInput:
    prescription_instance_id: strawberry.ID
    name: str
    position: int
    metric_unit: MetricUnitGQL
    metric_value: float
    description: Optional[str] = None
    movement_class: Optional[MovementClassGQL] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None
    video_url: Optional[str] = None
    exercise_id: Optional[strawberry.ID] = None
    sets: List[NestedSetInstanceCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class MovementInstanceFromTemplateInput:
    prescription_instance_id: strawberry.ID
    movement_template_id: strawberry.ID
    position: int


@strawberry.input
class MovementInstanceUpdateInput:
    name: Optional[str] = None
    notes: Optional[str] = None
    rest_duration: Optional[float] = None


@strawberry.input
class MovementOrderInput:
    movement_id: strawberry.ID
    position: int


@strawberry.input
class PrescriptionInstanceCreateInput:
    practice_instance_id: strawberry.ID
    name: str
    position: int
    block: str
    description: Optional[str] = None
    prescribed_rounds: int = 1
    movements: List[NestedMovementInstanceCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class PrescriptionInstanceUpdateInput:
    name: Optional[str] = None
    notes: Optional[str] = None
    prescribed_rounds: Optional[int] = None


# Phase 2: Template Input Types
@strawberry.input
class SetTemplateCreateInput:
    movement_template_id: strawberry.ID
    position: int
    reps: Optional[int] = None
    duration: Optional[float] = None
    rest_duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[str] = None


@strawberry.input
class SetTemplateUpdateInput:
    reps: Optional[int] = None
    duration: Optional[float] = None
    rest_duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[str] = None


@strawberry.input
class NestedSetTemplateCreateInput:
    position: int
    reps: Optional[int] = None
    duration: Optional[float] = None
    rest_duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[str] = None


@strawberry.input
class MovementTemplateCreateInput:
    prescription_template_id: strawberry.ID
    name: str
    position: int
    metric_unit: str
    metric_value: float
    description: Optional[str] = None
    movement_class: Optional[str] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None
    video_url: Optional[str] = None
    exercise_id: Optional[strawberry.ID] = None
    sets: List[NestedSetTemplateCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class MovementTemplateUpdateInput:
    name: Optional[str] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None


@strawberry.input
class NestedMovementTemplateCreateInput:
    name: str
    position: int
    metric_unit: str
    metric_value: float
    description: Optional[str] = None
    movement_class: Optional[str] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None
    video_url: Optional[str] = None
    exercise_id: Optional[strawberry.ID] = None
    sets: List[NestedSetTemplateCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class PrescriptionTemplateCreateInput:
    practice_template_id: strawberry.ID
    name: str
    position: int
    block: str
    description: Optional[str] = None
    prescribed_rounds: int = 1
    movements: List[NestedMovementTemplateCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class PrescriptionTemplateUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None
    prescribed_rounds: Optional[int] = None
    rest_duration: Optional[float] = None
    video_url: Optional[str] = None
    exercise_id: Optional[strawberry.ID] = None


# Existing input types

@strawberry.input
class NestedPrescriptionTemplateCreateInput:
    name: str
    position: int
    block: str
    description: Optional[str] = None
    prescribed_rounds: int = 1
    movements: List[NestedMovementTemplateCreateInput] = strawberry.field(default_factory=list)

@strawberry.input
class PracticeTemplateCreateInput:
    title: str
    description: Optional[str] = None
    duration: Optional[float] = None
    prescriptions: List[NestedPrescriptionTemplateCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class NestedPrescriptionInstanceCreateInput:
    name: str
    position: int
    block: str
    description: Optional[str] = None
    prescribed_rounds: int = 1
    movements: List[NestedMovementInstanceCreateInput] = strawberry.field(default_factory=list)

@strawberry.input
class PracticeInstanceCreateStandaloneInput:
    title: str
    date: date
    description: Optional[str] = None
    duration: Optional[float] = None
    notes: Optional[str] = None
    prescriptions: List[NestedPrescriptionInstanceCreateInput] = strawberry.field(default_factory=list)


@strawberry.input
class PracticeInstanceUpdateInput:
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[float] = None
    notes: Optional[str] = None
    # completed_at must be defined before `date`
    completed_at: Optional[date] = None
    date: Optional[date] = None


# Conversion functions (Domain Model -> GQL Type)
def convert_set_template_to_gql(domain_obj: DomainSetTemplate) -> SetTemplateType:
    return SetTemplateType(**domain_obj.model_dump())


def convert_movement_template_to_gql(domain_obj: DomainMovementTemplate) -> MovementTemplateType:
    data = domain_obj.model_dump()
    data["sets"] = [convert_set_template_to_gql(s) for s in domain_obj.sets]
    return MovementTemplateType(**data)


def convert_prescription_template_to_gql(domain_obj: DomainPrescriptionTemplate) -> PrescriptionTemplateType:
    data = domain_obj.model_dump()
    data["movements"] = [convert_movement_template_to_gql(m) for m in domain_obj.movements]
    return PrescriptionTemplateType(**data)


def convert_practice_template_to_gql(domain_obj: DomainPracticeTemplate) -> PracticeTemplateType:
    data = domain_obj.model_dump()
    data["prescriptions"] = [convert_prescription_template_to_gql(p) for p in domain_obj.prescriptions]
    return PracticeTemplateType(**data)


def convert_set_instance_to_gql(domain_obj: DomainSetInstance) -> SetInstanceType:
    return SetInstanceType(**domain_obj.model_dump())


def convert_movement_instance_to_gql(domain_obj: DomainMovementInstance) -> MovementInstanceType:
    data = domain_obj.model_dump()
    data["sets"] = [convert_set_instance_to_gql(s) for s in domain_obj.sets]
    return MovementInstanceType(**data)


def convert_prescription_instance_to_gql(domain_obj: DomainPrescriptionInstance) -> PrescriptionInstanceType:
    data = domain_obj.model_dump()
    data["movements"] = [convert_movement_instance_to_gql(m) for m in domain_obj.movements]
    return PrescriptionInstanceType(**data)


def convert_practice_instance_to_gql(domain_obj: DomainPracticeInstance) -> PracticeInstanceType:
    data = domain_obj.model_dump()
    data["prescriptions"] = [convert_prescription_instance_to_gql(p) for p in domain_obj.prescriptions]
    return PracticeInstanceType(**data)


def convert_program_practice_link_to_gql(domain_link: DomainProgramPracticeLink) -> ProgramPracticeLinkType:
    """Helper to convert domain ProgramPracticeLink to GQL ProgramPracticeLinkType."""
    return ProgramPracticeLinkType(
        id_=domain_link.id_,
        program_id=domain_link.program_id,
        practice_id=domain_link.practice_template_id,
        sequence_order=domain_link.sequence_order,
        interval_days_after=domain_link.interval_days_after,
        created_at=getattr(domain_link, "created_at", None),
        modified_at=getattr(domain_link, "modified_at", None),
        practice_template=(
            convert_practice_template_to_gql(domain_link.practice_template) if domain_link.practice_template else None
        ),
    )


def convert_program_to_gql(domain_program: DomainProgram) -> ProgramType:
    """Converts a domain program model to its GraphQL counterpart."""
    # Note: Strawberry will automatically handle the nested objects if their types are defined correctly.
    # We might need to handle enum conversions if they don't map directly.
    links_gql = [convert_program_practice_link_to_gql(link) for link in domain_program.practice_links]
    practice_count = len(links_gql)
    total_duration_days = (sum((l.interval_days_after or 0) for l in links_gql) + 1) if links_gql else 0
    return ProgramType(
        id_=domain_program.id_,
        name=domain_program.name,
        description=domain_program.description,
        level=domain_program.level,
        created_at=domain_program.created_at,
        modified_at=domain_program.modified_at,
        tags=[ProgramTagType(**tag.model_dump()) for tag in domain_program.tags],
        practice_links=links_gql,
        enrollments=[],
        practice_count=practice_count,
        total_duration_days=total_duration_days,
    )


@strawberry.type
class Query(EnrollmentQuery):
    @strawberry.field
    async def practice_templates(self, info: Info) -> List[PracticeTemplateType]:
        uow: UnitOfWork = info.context["uow"]
        repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(repo)
        templates = await service.list_templates()
        return [convert_practice_template_to_gql(t) for t in templates]

    @strawberry.field
    async def practice_template(self, info: Info, id: strawberry.ID) -> Optional[PracticeTemplateType]:
        uow: UnitOfWork = info.context["uow"]
        repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(repo)
        template = await service.get_template_by_id(UUID(id))
        return convert_practice_template_to_gql(template) if template else None

    @strawberry.field
    async def practice_instances(self, info: Info, user_id: strawberry.ID) -> List[PracticeInstanceType]:
        uow: UnitOfWork = info.context["uow"]
        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)
        instances = await service.list_instances_for_user(UUID(user_id))
        return [convert_practice_instance_to_gql(i) for i in instances]

    @strawberry.field
    async def practice_instance(self, info: Info, id: strawberry.ID) -> Optional[PracticeInstanceType]:
        uow: UnitOfWork = info.context["uow"]
        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)
        instance = await service.get_instance_by_id(UUID(id))
        return convert_practice_instance_to_gql(instance) if instance else None

    @strawberry.field
    async def programs(self, info: Info) -> List[ProgramType]:
        uow: UnitOfWork = info.context["uow"]
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        programs = await service.list_programs()
        return [convert_program_to_gql(p) for p in programs]

    @strawberry.field
    async def program(self, info: Info, id: strawberry.ID) -> Optional[ProgramType]:
        uow: UnitOfWork = info.context["uow"]
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        program = await service.get_program_by_id(UUID(str(id)))
        return convert_program_to_gql(program) if program else None

    @strawberry.field
    async def programs_by_level(self, info: Info, level: str) -> List[ProgramType]:
        uow: UnitOfWork = info.context["uow"]
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        programs = await service.filter_programs_by_level(level)
        return [convert_program_to_gql(p) for p in programs]

    @strawberry.field
    async def programs_by_tag(self, info: Info, tag: str) -> List[ProgramType]:
        uow: UnitOfWork = info.context["uow"]
        repo = ProgramRepository(uow.session)
        service = ProgramService(repo)
        programs = await service.filter_programs_by_tag(tag)
        return [convert_program_to_gql(p) for p in programs]

    # RAG-friendly workout fetchers
    @strawberry.field(name="todaysWorkouts")
    async def todays_workouts(self, info: Info, onDate: Optional[date] = None) -> List[PracticeInstanceType]:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required")
        target_date = onDate or date.today()
        repo = PracticeInstanceRepository(uow.session)
        instances = await repo.list_instances_on_dates(current_user.id, [target_date])
        return [convert_practice_instance_to_gql(i) for i in instances]

    @strawberry.field(name="workouts")
    async def workouts(
        self,
        info: Info,
        dateFrom: Optional[date] = None,
        dateTo: Optional[date] = None,
        dates: Optional[List[date]] = None,
        programId: Optional[strawberry.ID] = None,
        status: Optional[str] = None,
    ) -> List[PracticeInstanceType]:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required")
        repo = PracticeInstanceRepository(uow.session)
        program_uuid = UUID(str(programId)) if programId else None
        if dates:
            instances = await repo.list_instances_on_dates(current_user.id, dates, program_uuid, status)
        else:
            df = dateFrom or (date.today())
            dt = dateTo or date.today()
            instances = await repo.list_instances_by_date_range(current_user.id, df, dt, program_uuid, status)
        return [convert_practice_instance_to_gql(i) for i in instances]

    # Phase 1: Instance Queries
    @strawberry.field
    async def set_instance(self, id: strawberry.ID, info: Info) -> Optional[SetInstanceType]:
        """Get set instance by ID"""
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required")

        set_instance_service = SetInstanceService(SetInstanceRepository(uow.session))
        set_instance = await set_instance_service.get_set_instance_by_id(UUID(id))

        if not set_instance:
            return None

        # Verify access through practice instance ownership
        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        movement_instance = await movement_instance_service.get_movement_instance_by_id(
            set_instance.movement_instance_id
        )
        if not movement_instance:
            raise PermissionError("Not authorized to view this set")

        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
            movement_instance.prescription_instance_id
        )
        if not prescription_instance:
            raise PermissionError("Not authorized to view this set")

        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))
        practice_instance = await practice_instance_service.get_instance_by_id(
            prescription_instance.practice_instance_id
        )
        if not practice_instance:
            raise PermissionError("Not authorized to view this set")

        # Allow access if user owns the practice or is the coach
        is_owner = practice_instance.user_id == current_user.id
        is_clients_coach = await is_coach_for_client(current_user, practice_instance.user_id)

        if is_owner or is_clients_coach:
            return convert_set_instance_to_gql(set_instance)

        raise PermissionError("Not authorized to view this set")

    @strawberry.field
    async def set_instances_by_template(self, template_id: strawberry.ID, info: Info) -> List[SetInstanceType]:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        set_instance_service = SetInstanceService(SetInstanceRepository(uow.session))
        set_template_service = SetTemplateService(SetTemplateRepository(uow.session))
        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Get the set template first to check authorization
            set_template = await set_template_service.get_set_template_by_id(UUID(template_id))
            if not set_template:
                raise ValueError("Set template not found.")

            # Get the movement template to check authorization through hierarchy
            movement_template = await movement_template_service.get_movement_template_by_id(
                set_template.movement_template_id
            )
            if not movement_template:
                raise ValueError("Movement template not found.")

            # Authorization: Check ownership through practice template hierarchy
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to view set instances for this template.")

            instances = await set_instance_service.get_set_instances_by_template_id(UUID(template_id))
            return [convert_set_instance_to_gql(instance) for instance in instances]

    @strawberry.field
    async def movement_instance(self, id: strawberry.ID, info: Info) -> Optional[MovementInstanceType]:
        """Get movement instance by ID"""
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required")

        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        movement_instance = await movement_instance_service.get_movement_instance_by_id(UUID(id))
        if not movement_instance:
            return None

        # Verify access
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
            movement_instance.prescription_instance_id
        )
        if not prescription_instance:
            raise PermissionError("Not authorized to view this movement")

        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))
        practice_instance = await practice_instance_service.get_instance_by_id(
            prescription_instance.practice_instance_id
        )
        if not practice_instance:
            raise PermissionError("Not authorized to view this movement")

        is_owner = practice_instance.user_id == current_user.id
        is_clients_coach = await is_coach_for_client(current_user, practice_instance.user_id)

        if is_owner or is_clients_coach:
            return convert_movement_instance_to_gql(movement_instance)

        raise PermissionError("Not authorized to view this movement")

    @strawberry.field
    async def movement_instances_by_template(
        self, template_id: strawberry.ID, info: Info
    ) -> List[MovementInstanceType]:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))

        async with uow:
            # Get the movement template and check authorization through hierarchy
            movement_template = await movement_template_service.get_movement_template_by_id(UUID(template_id))
            if not movement_template:
                raise ValueError("Movement template not found.")

            # Check ownership through practice template hierarchy
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                raise PermissionError("Associated prescription template not found.")

            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to view instances from this template.")

            movement_instances = await movement_instance_service.get_movement_instances_by_template_id(
                UUID(template_id)
            )

        return [convert_movement_instance_to_gql(instance) for instance in movement_instances]

    @strawberry.field
    async def prescription_instance(self, id: strawberry.ID, info: Info) -> Optional[PrescriptionInstanceType]:
        """Get prescription instance by ID"""
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required")

        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(UUID(id))
        if not prescription_instance:
            return None

        # Verify access
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))
        practice_instance = await practice_instance_service.get_instance_by_id(
            prescription_instance.practice_instance_id
        )
        if not practice_instance:
            raise PermissionError("Not authorized to view this prescription")

        is_owner = practice_instance.user_id == current_user.id
        is_clients_coach = await is_coach_for_client(current_user, practice_instance.user_id)

        if is_owner or is_clients_coach:
            return convert_prescription_instance_to_gql(prescription_instance)

        raise PermissionError("Not authorized to view this prescription")

    # Phase 2: Template Queries
    @strawberry.field
    async def set_template(self, id: strawberry.ID, info: Info) -> Optional[SetTemplateType]:
        """Get set template by ID"""
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required")

        set_template_service = SetTemplateService(SetTemplateRepository(uow.session))
        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            set_template = await set_template_service.get_set_template_by_id(UUID(id))
            if not set_template:
                return None

            # Check authorization through practice template hierarchy
            movement_template = await movement_template_service.get_movement_template_by_id(
                set_template.movement_template_id
            )
            if not movement_template:
                raise PermissionError("Not authorized to view this template")

            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                raise PermissionError("Not authorized to view this template")

            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                can_access = await has_template_access(UUID(id), current_user.id)
                if not can_access:
                    raise PermissionError("Not authorized to view this template")

        return convert_set_template_to_gql(set_template)

    @strawberry.field
    async def movement_template(self, id: strawberry.ID, info: Info) -> Optional[MovementTemplateType]:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))

        async with uow:
            movement_template = await movement_template_service.get_movement_template_by_id(UUID(id))
            if not movement_template:
                return None

            # Check ownership through practice template hierarchy
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                return None

            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            can_access = (
                practice_template and practice_template.user_id == current_user.id
            ) or await has_template_access(UUID(id), current_user.id)

            if not can_access:
                return None

        return convert_movement_template_to_gql(movement_template)

    @strawberry.field
    async def movement_templates_by_coach(
        self, info: Info, coach_id: Optional[strawberry.ID] = None
    ) -> List[MovementTemplateType]:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        # Use current user's ID if coach_id is not provided
        target_coach_id = UUID(coach_id) if coach_id else current_user.id

        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))

        async with uow:
            movement_templates = await movement_template_service.get_movement_templates_by_coach(target_coach_id)

            # Filter templates based on access rights
            accessible_templates = []
            for template in movement_templates:
                # Check ownership through practice template hierarchy
                prescription_template = await prescription_template_service.get_prescription_template_by_id(
                    template.prescription_template_id
                )
                if not prescription_template:
                    continue

                practice_template = await practice_template_service.get_template_by_id(
                    prescription_template.practice_template_id
                )
                can_access = (
                    practice_template and practice_template.user_id == current_user.id
                ) or await has_template_access(template.id_, current_user.id)

                if can_access:
                    accessible_templates.append(template)

        return [convert_movement_template_to_gql(template) for template in accessible_templates]

    @strawberry.field
    async def prescription_template(self, id: strawberry.ID, info: Info) -> Optional[PrescriptionTemplateType]:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            prescription_template = await prescription_template_service.get_prescription_template_by_id(UUID(id))
            if not prescription_template:
                return None

            # Check ownership through practice template hierarchy
            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to view this prescription template.")

        return convert_prescription_template_to_gql(prescription_template)


@strawberry.type
class Mutation(EnrollmentMutation):
    # RAG-friendly mutations for workouts
    @strawberry.mutation(name="createAdHocWorkout")
    async def create_ad_hoc_workout(
        self, info: Info, input: PracticeInstanceCreateStandaloneInput
    ) -> PracticeInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")
        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)
        payload = to_dict(input)
        payload["user_id"] = current_user.id
        async with uow:
            instance = await service.create_standalone_instance(payload)
        return convert_practice_instance_to_gql(instance)

    @strawberry.mutation(name="scheduleWorkout")
    async def schedule_workout(
        self, info: Info, template_id: strawberry.ID, date: date
    ) -> PracticeInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")
        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)
        async with uow:
            instance = await service.create_instance_from_template(UUID(template_id), current_user.id, date)
            refreshed = await service.get_instance_by_id(instance.id_)
        return convert_practice_instance_to_gql(refreshed)

    @strawberry.mutation(name="completeWorkout")
    async def complete_workout(self, info: Info, id: strawberry.ID) -> PracticeInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")
        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)
        async with uow:
            updated = await service.complete_instance(UUID(id))
        return convert_practice_instance_to_gql(updated)  # type: ignore

    @strawberry.mutation(name="logSet")
    async def log_set(self, info: Info, input: SetInstanceCreateInput) -> SetInstanceType:
        # Alias to create_set_instance for convenience
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))
        set_instance_service = SetInstanceService(SetInstanceRepository(uow.session))

        input_data = to_dict(input)
        movement_instance_id = UUID(input_data["movement_instance_id"])

        async with uow:
            # Authorization: Ensure the user owns the practice this set belongs to.
            movement_instance = await movement_instance_service.get_movement_instance_by_id(movement_instance_id)
            if not movement_instance:
                raise ValueError("MovementInstance not found.")

            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
                movement_instance.prescription_instance_id
            )
            if not prescription_instance:
                raise ValueError("Associated PrescriptionInstance not found.")

            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance:
                raise ValueError("Associated PracticeInstance not found.")

            # Only the user who owns the practice can add a set instance.
            if practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to add a set to this practice.")

            # Prepare data for the service layer
            set_create_data = input_data
            set_create_data["movement_instance_id"] = movement_instance_id

            new_set_instance = await set_instance_service.create_set_instance(set_create_data)
        return convert_set_instance_to_gql(new_set_instance)

    @strawberry.mutation
    async def create_practice_template(self, info: Info, input: PracticeTemplateCreateInput) -> PracticeTemplateType:
        uow: UnitOfWork = info.context["uow"]
        # TODO: Add authorization logic (e.g., check for coach role)
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(repo)

        template_dict = to_dict(input)
        template_dict["user_id"] = current_user.id

        async with uow:
            new_template = await service.create_template(template_dict)
        return convert_practice_template_to_gql(new_template)

    @strawberry.mutation
    async def delete_practice_template(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(repo)

        async with uow:
            # Authorization: Ensure the user owns the template
            template = await service.get_template_by_id(UUID(id))
            if not template or template.user_id != current_user.id:
                raise PermissionError("Not authorized to delete this template.")

            await service.delete_template(UUID(id))
            return True

    @strawberry.mutation
    async def create_practice_instance_from_template(
        self, info: Info, template_id: strawberry.ID, date: date
    ) -> PracticeInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)

        async with uow:
            new_instance = await service.create_instance_from_template(
                template_id=UUID(template_id), user_id=current_user.id, date=date
            )
            # The service returns a domain model, we need to refresh to get the GQL model with relationships
            refreshed_instance = await service.get_instance_by_id(new_instance.id_)
            return convert_practice_instance_to_gql(refreshed_instance)

    @strawberry.mutation
    async def update_practice_instance(
        self, info: Info, id: strawberry.ID, input: PracticeInstanceUpdateInput
    ) -> PracticeInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)

        async with uow:
            # Authorization: Ensure user owns the instance
            instance = await service.get_instance_by_id(UUID(id))
            if not instance or instance.user_id != current_user.id:
                raise PermissionError("Not authorized to update this practice.")

            # Build a dictionary containing only the fields that were explicitly provided
            # in the input. This avoids overwriting existing values with `None` for
            # fields that were not sent in the mutation.
            update_data = {k: v for k, v in to_dict(input).items() if v is not None}

            # If the update_data is empty, it means no fields were provided to update.
            # In this case, we can just return the existing instance without change.
            if not update_data:
                return convert_practice_instance_to_gql(instance)

            updated_instance = await service.update_instance(UUID(id), update_data)
            return convert_practice_instance_to_gql(updated_instance)

    @strawberry.mutation
    async def delete_practice_instance(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(repo)

        async with uow:
            # Authorization: Ensure user owns the instance
            instance = await service.get_instance_by_id(UUID(id))
            if not instance or instance.user_id != current_user.id:
                raise PermissionError("Not authorized to delete this practice.")

            await service.delete_instance(UUID(id))
            return True

    # --- Granular CRUD Mutations ---

    # Set Instance
    @strawberry.mutation
    async def create_set_instance(self, info: Info, input: SetInstanceCreateInput) -> SetInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        # Instantiate services
        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))
        set_instance_service = SetInstanceService(SetInstanceRepository(uow.session))

        input_data = to_dict(input)
        movement_instance_id = UUID(input_data["movement_instance_id"])

        async with uow:
            # Authorization: Ensure the user owns the practice this set belongs to.
            movement_instance = await movement_instance_service.get_movement_instance_by_id(movement_instance_id)
            if not movement_instance:
                raise ValueError("MovementInstance not found.")

            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
                movement_instance.prescription_instance_id
            )
            if not prescription_instance:
                raise ValueError("Associated PrescriptionInstance not found.")

            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance:
                raise ValueError("Associated PracticeInstance not found.")

            # Only the user who owns the practice can add a set instance.
            if practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to add a set to this practice.")

            # Prepare data for the service layer
            set_create_data = input_data
            set_create_data["movement_instance_id"] = movement_instance_id

            new_set_instance = await set_instance_service.create_set_instance(set_create_data)
        return convert_set_instance_to_gql(new_set_instance)

    @strawberry.mutation
    async def update_set_instance(
        self, info: Info, id: strawberry.ID, input: SetInstanceUpdateInput
    ) -> SetInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        set_instance_service = SetInstanceService(SetInstanceRepository(uow.session))
        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        set_id = UUID(id)
        update_data = {k: v for k, v in to_dict(input).items() if v is not None}

        async with uow:
            # Authorization check
            set_instance = await set_instance_service.get_set_instance_by_id(set_id)
            if not set_instance:
                raise ValueError("SetInstance not found.")

            movement_instance = await movement_instance_service.get_movement_instance_by_id(
                set_instance.movement_instance_id
            )
            if not movement_instance:
                raise ValueError("Associated MovementInstance not found.")

            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
                movement_instance.prescription_instance_id
            )
            if not prescription_instance:
                raise ValueError("Associated PrescriptionInstance not found.")

            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance:
                raise ValueError("Associated PracticeInstance not found.")

            # For now, only the owner can update. Coach logic can be added later.
            if practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to update this set.")

            updated_set_instance = await set_instance_service.update_set_instance(set_id, update_data)

            # If the 'complete' flag was part of the update, check movement completion
            if "complete" in update_data:
                await movement_instance_service.check_movement_completion(set_instance.movement_instance_id)
                # Also check if the prescription should now be marked as complete
                await prescription_instance_service.check_prescription_completion(
                    movement_instance.prescription_instance_id
                )

        return convert_set_instance_to_gql(updated_set_instance)

    @strawberry.mutation
    async def delete_set_instance(self, info: Info, id: strawberry.ID) -> bool:
        raise NotImplementedError

    @strawberry.mutation
    async def complete_set_instance(self, info: Info, id: strawberry.ID) -> SetInstanceType:
        """Mark a set instance as complete"""
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        set_instance_service = SetInstanceService(SetInstanceRepository(uow.session))
        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        set_id = UUID(id)

        async with uow:
            # Authorization check
            set_instance = await set_instance_service.get_set_instance_by_id(set_id)
            if not set_instance:
                raise ValueError("SetInstance not found.")

            movement_instance = await movement_instance_service.get_movement_instance_by_id(
                set_instance.movement_instance_id
            )
            if not movement_instance:
                raise ValueError("Associated MovementInstance not found.")

            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
                movement_instance.prescription_instance_id
            )
            if not prescription_instance:
                raise ValueError("Associated PrescriptionInstance not found.")

            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance:
                raise ValueError("Associated PracticeInstance not found.")

            # For now, only the owner can complete. Coach logic can be added later.
            if practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to complete this set.")

            # Complete the set
            completed_set_instance = await set_instance_service.update_set_instance(set_id, {"complete": True})

            # Check if the movement should now be marked as complete
            await movement_instance_service.check_movement_completion(set_instance.movement_instance_id)

            # Check if the prescription should now be marked as complete
            await prescription_instance_service.check_prescription_completion(
                movement_instance.prescription_instance_id
            )

        return convert_set_instance_to_gql(completed_set_instance)

    # Movement Instance
    @strawberry.mutation
    async def create_movement_instance(self, info: Info, input: MovementInstanceCreateInput) -> MovementInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        # Instantiate services
        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        input_data = to_dict(input)
        prescription_instance_id = UUID(input_data["prescription_instance_id"])

        async with uow:
            # Authorization: Ensure the user owns the practice this movement belongs to.
            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
                prescription_instance_id
            )
            if not prescription_instance:
                raise ValueError("PrescriptionInstance not found.")

            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance:
                raise ValueError("Associated PracticeInstance not found.")

            # Only the user who owns the practice can add a movement instance.
            if practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to add a movement to this practice.")

            # The service expects a plain dict
            # Convert ID fields from string to UUID
            input_data["prescription_instance_id"] = prescription_instance_id
            if input_data.get("exercise_id"):
                input_data["exercise_id"] = UUID(input_data["exercise_id"])

            new_movement_instance = await movement_instance_service.create_movement_instance(input_data)

        return convert_movement_instance_to_gql(new_movement_instance)

    @strawberry.mutation
    async def update_movement_instance(
        self, info: Info, id: strawberry.ID, input: MovementInstanceUpdateInput
    ) -> MovementInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        movement_id = UUID(id)
        update_data = {k: v for k, v in to_dict(input).items() if v is not None}

        async with uow:
            # Authorization check
            movement_instance = await movement_instance_service.get_movement_instance_by_id(movement_id)
            if not movement_instance:
                raise ValueError("MovementInstance not found.")

            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
                movement_instance.prescription_instance_id
            )
            if not prescription_instance:
                raise ValueError("Associated PrescriptionInstance not found.")

            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance:
                raise ValueError("Associated PracticeInstance not found.")

            # For now, only the owner can update.
            if practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to update this movement.")

            updated_movement_instance = await movement_instance_service.update_movement_instance(
                movement_id, update_data
            )
        return convert_movement_instance_to_gql(updated_movement_instance)

    @strawberry.mutation
    async def reorder_movements_in_prescription(
        self, info: Info, prescription_id: strawberry.ID, movements: List[MovementOrderInput]
    ) -> PrescriptionInstanceType:
        raise NotImplementedError

    @strawberry.mutation
    async def delete_movement_instance(self, info: Info, id: strawberry.ID) -> bool:
        raise NotImplementedError

    @strawberry.mutation
    async def create_movement_instance_from_template(
        self, info: Info, input: MovementInstanceFromTemplateInput
    ) -> MovementInstanceType:
        """Create movement instance from template"""
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        movement_instance_service = MovementInstanceService(MovementInstanceRepository(uow.session))
        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        input_data = to_dict(input)
        prescription_instance_id = UUID(input_data["prescription_instance_id"])
        movement_template_id = UUID(input_data["movement_template_id"])

        async with uow:
            # Authorization: Ensure the user owns the practice this movement belongs to
            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(
                prescription_instance_id
            )
            if not prescription_instance:
                raise ValueError("PrescriptionInstance not found.")

            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance:
                raise ValueError("Associated PracticeInstance not found.")

            # Only the user who owns the practice can add a movement instance
            if practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to add a movement to this practice.")

            # Get the movement template
            movement_template = await movement_template_service.get_movement_template_by_id(movement_template_id)
            if not movement_template:
                raise ValueError("MovementTemplate not found.")

            # Check if user has access to the template through the prescription template
            prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                raise ValueError("Associated PrescriptionTemplate not found.")

            practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))
            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template:
                raise ValueError("Associated PracticeTemplate not found.")

            # Allow using templates if:
            # 1. User owns the template, OR
            # 2. User is creating an instance within their own practice (client using coach's template)
            template_owner = practice_template.user_id == current_user.id
            creating_in_own_practice = practice_instance.user_id == current_user.id

            if not (template_owner or creating_in_own_practice):
                raise PermissionError("Not authorized to use this movement template.")

            # Create movement instance from template
            new_movement_instance = await movement_instance_service.create_movement_from_template(
                template_id=movement_template_id,
                prescription_instance_id=prescription_instance_id,
                position=input_data["position"],
            )

        return convert_movement_instance_to_gql(new_movement_instance)

    # Prescription Instance
    @strawberry.mutation
    async def create_prescription_instance(
        self, info: Info, input: PrescriptionInstanceCreateInput
    ) -> PrescriptionInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        async with uow:
            # Authorization: Ensure user owns the practice instance
            practice_instance = await practice_instance_service.get_instance_by_id(UUID(input.practice_instance_id))
            if not practice_instance or practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to create prescription for this practice.")

            # Convert input to dictionary and create prescription
            prescription_data = to_dict(input)

            new_prescription = await prescription_instance_service.create_prescription_instance(prescription_data)

        return convert_prescription_instance_to_gql(new_prescription)

    @strawberry.mutation
    async def update_prescription_instance(
        self, info: Info, id: strawberry.ID, input: PrescriptionInstanceUpdateInput
    ) -> PrescriptionInstanceType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        async with uow:
            # Get the prescription instance
            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(UUID(id))
            if not prescription_instance:
                raise ValueError("Prescription instance not found.")

            # Authorization: Ensure user owns the associated practice instance
            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance or practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to update this prescription.")

            # Build update data from input
            update_data = {k: v for k, v in to_dict(input).items() if v is not None}

            if not update_data:
                return convert_prescription_instance_to_gql(prescription_instance)

            updated_prescription = await prescription_instance_service.update_prescription_instance(
                UUID(id), update_data
            )

        return convert_prescription_instance_to_gql(updated_prescription)

    @strawberry.mutation
    async def delete_prescription_instance(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        prescription_instance_service = PrescriptionInstanceService(PrescriptionInstanceRepository(uow.session))
        practice_instance_service = PracticeInstanceService(PracticeInstanceRepository(uow.session))

        async with uow:
            # Get the prescription instance
            prescription_instance = await prescription_instance_service.get_prescription_instance_by_id(UUID(id))
            if not prescription_instance:
                raise ValueError("Prescription instance not found.")

            # Authorization: Check ownership through practice template hierarchy
            practice_instance = await practice_instance_service.get_instance_by_id(
                prescription_instance.practice_instance_id
            )
            if not practice_instance or practice_instance.user_id != current_user.id:
                raise PermissionError("Not authorized to delete this prescription.")

            await prescription_instance_service.delete_prescription_instance(UUID(id))

        return True

    # Set Template
    @strawberry.mutation
    async def create_set_template(self, info: Info, input: SetTemplateCreateInput) -> SetTemplateType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        set_template_service = SetTemplateService(SetTemplateRepository(uow.session))
        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Authorization: Check ownership through movement template hierarchy
            movement_template = await movement_template_service.get_movement_template_by_id(
                UUID(input.movement_template_id)
            )
            if not movement_template:
                raise ValueError("Movement template not found.")

            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to create set template for this movement template.")

            # Convert input to dict and create set template
            set_data = to_dict(input)
            set_template = await set_template_service.create_set_template(set_data)

        return convert_set_template_to_gql(set_template)

    @strawberry.mutation
    async def update_set_template(
        self, info: Info, id: strawberry.ID, input: SetTemplateUpdateInput
    ) -> SetTemplateType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        set_template_service = SetTemplateService(SetTemplateRepository(uow.session))
        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Get the set template
            set_template = await set_template_service.get_set_template_by_id(UUID(id))
            if not set_template:
                raise ValueError("Set template not found.")

            # Authorization: Check ownership through movement template hierarchy
            movement_template = await movement_template_service.get_movement_template_by_id(
                set_template.movement_template_id
            )
            if not movement_template:
                raise ValueError("Movement template not found.")

            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to update this set template.")

            # Build update data from input
            update_data = {k: v for k, v in to_dict(input).items() if v is not None}

            if not update_data:
                return convert_set_template_to_gql(set_template)

            updated_set_template = await set_template_service.update_set_template(UUID(id), update_data)

        return convert_set_template_to_gql(updated_set_template)

    @strawberry.mutation
    async def delete_set_template(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        set_template_service = SetTemplateService(SetTemplateRepository(uow.session))
        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Get the set template
            set_template = await set_template_service.get_set_template_by_id(UUID(id))
            if not set_template:
                raise ValueError("Set template not found.")

            # Authorization: Check ownership through movement template hierarchy
            movement_template = await movement_template_service.get_movement_template_by_id(
                set_template.movement_template_id
            )
            if not movement_template:
                raise ValueError("Movement template not found.")

            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to delete this set template.")

            await set_template_service.delete_set_template(UUID(id))
            return True

    # Movement Template
    @strawberry.mutation
    async def create_movement_template(self, info: Info, input: MovementTemplateCreateInput) -> MovementTemplateType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        # Only coaches can create templates
        if not await is_coach(current_user):
            raise PermissionError("Only coaches can create movement templates.")

        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Authorization: Ensure user owns the prescription template
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                UUID(input.prescription_template_id)
            )
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            # Check ownership through practice template
            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to add movement to this prescription template.")

            # Convert input to dictionary - don't add created_by since movement templates don't have this field
            movement_data = to_dict(input)

            new_movement_template = await movement_template_service.create_movement_template(movement_data)

        return convert_movement_template_to_gql(new_movement_template)

    @strawberry.mutation
    async def update_movement_template(
        self, info: Info, id: strawberry.ID, input: MovementTemplateUpdateInput
    ) -> MovementTemplateType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Get the movement template
            movement_template = await movement_template_service.get_movement_template_by_id(UUID(id))
            if not movement_template:
                raise ValueError("Movement template not found.")

            # Authorization: Check ownership through practice template hierarchy
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to update this movement template.")

            # Build update data from input
            update_data = {k: v for k, v in to_dict(input).items() if v is not None}

            if not update_data:
                return convert_movement_template_to_gql(movement_template)

            updated_movement_template = await movement_template_service.update_movement_template(UUID(id), update_data)

        return convert_movement_template_to_gql(updated_movement_template)

    @strawberry.mutation
    async def delete_movement_template(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        movement_template_service = MovementTemplateService(MovementTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Get the movement template
            movement_template = await movement_template_service.get_movement_template_by_id(UUID(id))
            if not movement_template:
                raise ValueError("Movement template not found.")

            # Authorization: Check ownership through practice template hierarchy
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                movement_template.prescription_template_id
            )
            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to delete this movement template.")

            await movement_template_service.delete_movement_template(UUID(id))

        return True

    @strawberry.mutation
    async def share_movement_template(self, info: Info, template_id: strawberry.ID, user_id: strawberry.ID) -> bool:
        raise NotImplementedError

    @strawberry.mutation
    async def add_prescription_template_to_program(
        self, info: Info, program_id: strawberry.ID, prescription_template_id: strawberry.ID, position: int
    ) -> ProgramType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        program_service = ProgramService(ProgramRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))
        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))

        async with uow:
            program = await program_service.get_program_by_id(UUID(program_id))
            if not program or program.user_id != current_user.id:
                raise PermissionError("Program not found or not authorized.")

            # Get the prescription template using the service
            prescription_template = await prescription_template_service.get_prescription_template_by_id(
                UUID(prescription_template_id)
            )
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            # Find the next available sequence position
            existing_positions = [link.sequence_order for link in program.practice_links]
            next_position = max(existing_positions, default=0) + 1

            # Create a new practice template from the prescription template
            new_practice_template_data = {
                "user_id": current_user.id,
                "title": f"Practice From: {prescription_template.name}",
                "prescriptions": [
                    {
                        "name": prescription_template.name,
                        "block": prescription_template.block,
                        "position": 0,
                        "prescribed_rounds": prescription_template.prescribed_rounds,
                        "description": prescription_template.description,
                        "movements": [
                            {
                                "name": m.name,
                                "position": m.position,
                                "metric_unit": m.metric_unit,
                                "metric_value": m.metric_value,
                                "prescribed_sets": m.prescribed_sets,
                                "description": m.description,
                                "movement_class": m.movement_class,
                                "rest_duration": m.rest_duration,
                                "video_url": m.video_url,
                                "exercise_id": str(m.exercise_id) if m.exercise_id else None,
                                "sets": [
                                    {
                                        "position": s.position,
                                        "reps": s.reps,
                                        "duration": s.duration,
                                        "rest_duration": s.rest_duration,
                                        "load_value": s.load_value,
                                        "load_unit": s.load_unit,
                                    }
                                    for s in m.sets
                                ],
                            }
                            for m in prescription_template.movements
                        ],
                    }
                ],
            }

            new_practice_template = await practice_template_service.create_template(new_practice_template_data)

            # Link the new practice template to the program using the next available position
            link = ProgramPracticeLinkModel(
                program_id=program.id_,
                practice_template_id=new_practice_template.id_,
                sequence_order=next_position,
                interval_days_after=1,  # Default value from test
            )
            uow.session.add(link)

        refreshed_program = await program_service.get_program_by_id(program.id_)
        return convert_program_to_gql(refreshed_program)

    @strawberry.mutation
    async def share_prescription_template(self, info: Info, template_id: strawberry.ID, user_id: strawberry.ID) -> bool:
        raise NotImplementedError

    @strawberry.mutation
    async def create_prescription_template(
        self, info: Info, input: PrescriptionTemplateCreateInput
    ) -> PrescriptionTemplateType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        # Only coaches can create templates
        if not await is_coach(current_user):
            raise PermissionError("Only coaches can create prescription templates.")

        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Authorization: Ensure user owns the practice template
            practice_template = await practice_template_service.get_template_by_id(UUID(input.practice_template_id))
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to add prescription to this practice template.")

            # Convert input to dictionary - don't add created_by since prescription templates don't have this field
            prescription_data = to_dict(input)

            new_prescription_template = await prescription_template_service.create_prescription_template(
                prescription_data
            )

        return convert_prescription_template_to_gql(new_prescription_template)

    @strawberry.mutation
    async def update_prescription_template(
        self, info: Info, id: strawberry.ID, input: PrescriptionTemplateUpdateInput
    ) -> PrescriptionTemplateType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Get the prescription template
            prescription_template = await prescription_template_service.get_prescription_template_by_id(UUID(id))
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            # Authorization: Check ownership through practice template hierarchy
            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to update this prescription template.")

            # Build update data from input
            update_data = {k: v for k, v in to_dict(input).items() if v is not None}

            if not update_data:
                return convert_prescription_template_to_gql(prescription_template)

            updated_prescription_template = await prescription_template_service.update_prescription_template(
                UUID(id), update_data
            )

        return convert_prescription_template_to_gql(updated_prescription_template)

    @strawberry.mutation
    async def delete_prescription_template(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")

        prescription_template_service = PrescriptionTemplateService(PrescriptionTemplateRepository(uow.session))
        practice_template_service = PracticeTemplateService(PracticeTemplateRepository(uow.session))

        async with uow:
            # Get the prescription template
            prescription_template = await prescription_template_service.get_prescription_template_by_id(UUID(id))
            if not prescription_template:
                raise ValueError("Prescription template not found.")

            # Authorization: Check ownership through practice template hierarchy
            practice_template = await practice_template_service.get_template_by_id(
                prescription_template.practice_template_id
            )
            if not practice_template or practice_template.user_id != current_user.id:
                raise PermissionError("Not authorized to delete this prescription template.")

            await prescription_template_service.delete_prescription_template(UUID(id))

        return True

    # Program mutations
    @strawberry.mutation(name="createProgram")
    async def create_program(self, info: Info, input: ProgramCreateInput) -> ProgramType:
        uow: UnitOfWork = info.context["uow"]
        current_user = get_current_user_from_info(info)
        if not current_user:
            raise PermissionError("Authentication required.")
        payload = input.to_dict()
        payload["user_id"] = current_user.id
        async with uow:
            program_repo = ProgramRepository(uow.session)
            program_service = ProgramService(program_repo)
            program = await program_service.create_program(payload)
        return convert_program_to_gql(program)

    @strawberry.mutation(name="updateProgram")
    async def update_program(self, info: Info, id: strawberry.ID, input: ProgramUpdateInput) -> Optional[ProgramType]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            program_repo = ProgramRepository(uow.session)
            program_service = ProgramService(program_repo)
            updated = await program_service.update_program(UUID(str(id)), input.to_dict())
        return convert_program_to_gql(updated) if updated else None

    @strawberry.mutation(name="deleteProgram")
    async def delete_program(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            program_repo = ProgramRepository(uow.session)
            program_service = ProgramService(program_repo)
            return await program_service.delete_program(UUID(str(id)))


@strawberry.input
class NestedPrescriptionTemplateCreateInput:
    name: str
    position: int
    block: str
    description: Optional[str] = None
    prescribed_rounds: int = 1
    movements: List[NestedMovementTemplateCreateInput] = strawberry.field(default_factory=list)
