import uuid
from datetime import date
from typing import List, Optional, cast

import strawberry
from graphql import GraphQLError
from shared.auth import CurrentUser, RequireRolePermission
from shared.clients.user_service_client import users_service_client
from strawberry.types import Info

from practices.domain.models import DomainProgramEnrollment
from practices.repository.models.progress import ScheduledPracticeModel
from practices.repository.repositories import (
    EnrollmentRepository,
    ScheduledPracticeRepository,
)
from practices.repository.uow import UnitOfWork
from practices.service.services import EnrollmentService
from practices.service.services.progress_service import (
    ProgressService,
    ProgressServiceError,
)
from practices.web.graphql.dependencies import CustomContext

from .enrollment_types import EnrollmentStatusGQL, ProgramEnrollmentTypeGQL
from .progress_types import ScheduledPracticeTypeGQL


# Concrete permission classes for this resolver
class CanSelfEnroll(RequireRolePermission):
    required_role = "client"
    required_domain = "practices"


class CanEnrollOthers(RequireRolePermission):
    required_role = "coach"
    required_domain = "practices"


class CanAdvanceProgress(RequireRolePermission):
    required_role = "client"
    required_domain = "practices"


class CanDeferPractice(RequireRolePermission):
    required_role = "client"
    required_domain = "practices"


def to_gql_enrollment(enrollment: DomainProgramEnrollment) -> ProgramEnrollmentTypeGQL:
    """Converts a domain enrollment model to its GraphQL type."""
    return ProgramEnrollmentTypeGQL(
        id_=enrollment.id_,
        program_id=enrollment.program_id,
        user_id=enrollment.user_id,
        enrolled_by_user_id=enrollment.enrolled_by_user_id,
        status=EnrollmentStatusGQL[enrollment.status.name],
        created_at=enrollment.created_at,
        modified_at=enrollment.modified_at,
        current_practice_link_id=enrollment.current_practice_link_id,
    )


def to_gql_scheduled_practice(scheduled_practice: ScheduledPracticeModel) -> ScheduledPracticeTypeGQL:
    """Converts a scheduled practice model to its GraphQL type."""
    return ScheduledPracticeTypeGQL(
        id_=scheduled_practice.id_,
        enrollment_id=scheduled_practice.enrollment_id,
        practice_id=scheduled_practice.practice_template_id,
        scheduled_date=scheduled_practice.scheduled_date,
    )


@strawberry.type
class EnrollmentQuery:
    @strawberry.field
    async def enrollment(self, info: Info, id: strawberry.ID) -> Optional[ProgramEnrollmentTypeGQL]:
        """
        Retrieves a single program enrollment by its ID.

        Authorization Rules:
        - A user can retrieve their own enrollment.
        - A coach can retrieve the enrollment of their verified client.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]
        enrollment_uuid = uuid.UUID(str(id))

        async with uow:
            repo = EnrollmentRepository(uow.session)
            enrollment = await repo.get_enrollment_by_id(enrollment_uuid)

            if not enrollment:
                return None

            # Authorization Check
            is_owner = enrollment.user_id == current_user.id
            is_authorized_coach = False
            if current_user.has_role("coach", "practices"):
                is_authorized_coach = await users_service_client.verify_coach_client_relationship(
                    coach_id=current_user.id, client_id=enrollment.user_id, domain="practices"
                )

            if not is_owner and not is_authorized_coach:
                # Instead of raising an error, we follow GraphQL best practices and return None
                # as if the resource doesn't exist for this user.
                return None

            return to_gql_enrollment(enrollment)

    @strawberry.field
    async def enrollments(self, info: Info, user_id: strawberry.ID) -> List[ProgramEnrollmentTypeGQL]:
        """
        Retrieves all program enrollments for a given user.

        Authorization Rules:
        - A user can retrieve their own enrollments.
        - A coach can retrieve the enrollments of their verified client.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]
        target_user_uuid = uuid.UUID(str(user_id))

        # Authorization Check
        is_owner = target_user_uuid == current_user.id
        is_authorized_coach = False
        if current_user.has_role("coach", "practices"):
            is_authorized_coach = await users_service_client.verify_coach_client_relationship(
                coach_id=current_user.id, client_id=target_user_uuid, domain="practices"
            )

        if not is_owner and not is_authorized_coach:
            # Return empty list if not authorized, as per GraphQL best practices.
            return []

        async with uow:
            repo = EnrollmentRepository(uow.session)
            enrollments_models = await repo.get_enrollments_for_user(target_user_uuid)
            return [to_gql_enrollment(e) for e in enrollments_models]

    @strawberry.field
    async def my_upcoming_practices(self, info: Info) -> List[ScheduledPracticeTypeGQL]:
        """Retrieves all upcoming scheduled practices for the current user."""
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]

        async with uow:
            enrollment_repo = EnrollmentRepository(uow.session)
            enrollments = await enrollment_repo.get_enrollments_for_user(current_user.id)
            enrollment_ids = [e.id_ for e in enrollments]

            if not enrollment_ids:
                return []

            progress_repo = ScheduledPracticeRepository(uow.session)
            upcoming_practices = await progress_repo.list(enrollment_ids=enrollment_ids, from_date=date.today())
            return [to_gql_scheduled_practice(p) for p in upcoming_practices]

    @strawberry.field
    async def my_upcoming_practices_in_program(
        self, info: Info, program_id: strawberry.ID
    ) -> List[ScheduledPracticeTypeGQL]:
        """Retrieves all upcoming scheduled practices for the current user in a specific program."""
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]
        program_uuid = uuid.UUID(str(program_id))

        async with uow:
            enrollment_repo = EnrollmentRepository(uow.session)
            # Find the specific enrollment for the user and program
            enrollments = await enrollment_repo.get_enrollments_for_user(current_user.id)
            target_enrollment = next((e for e in enrollments if e.program_id == program_uuid), None)

            if not target_enrollment:
                return []

            progress_repo = ScheduledPracticeRepository(uow.session)
            upcoming_practices = await progress_repo.list(
                enrollment_ids=[target_enrollment.id_], from_date=date.today()
            )
            return [to_gql_scheduled_practice(p) for p in upcoming_practices]


@strawberry.type
class EnrollmentMutation:
    @strawberry.mutation(permission_classes=[CanSelfEnroll])
    async def enroll_in_program(self, info: Info, program_id: strawberry.ID) -> ProgramEnrollmentTypeGQL:
        """
        Allows a user to self-enroll in a program.
        The user must have the 'client' role in the 'practices' domain.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]

        async with uow:
            repo = EnrollmentRepository(uow.session)
            service = EnrollmentService(repo)
            domain_enrollment = await service.enroll_user(
                program_id=uuid.UUID(str(program_id)),
                user_to_enroll_id=current_user.id,
                enrolling_user_id=current_user.id,  # For self-enrollment
            )
            # The Unit of Work context manager handles the commit.
            return to_gql_enrollment(domain_enrollment)

    @strawberry.mutation(permission_classes=[CanEnrollOthers])
    async def enroll_user_in_program(
        self, info: Info, program_id: strawberry.ID, user_id: strawberry.ID
    ) -> ProgramEnrollmentTypeGQL:
        """
        Allows a coach to enroll another user in a program.
        The acting user must have the 'coach' role in the 'practices' domain.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]
        user_to_enroll_id = uuid.UUID(str(user_id))

        # --- Enhanced Authorization Check ---
        # A coach can only enroll a user if they have an accepted coaching relationship.
        is_verified_coach = await users_service_client.verify_coach_client_relationship(
            coach_id=current_user.id, client_id=user_to_enroll_id, domain="practices"
        )
        if not is_verified_coach:
            raise Exception("You are not authorized to enroll this user in a program.")
        # --- End Enhanced Authorization Check ---

        async with uow:
            repo = EnrollmentRepository(uow.session)
            service = EnrollmentService(repo)
            domain_enrollment = await service.enroll_user(
                program_id=uuid.UUID(str(program_id)),
                user_to_enroll_id=user_to_enroll_id,
                enrolling_user_id=current_user.id,  # The coach is the enroller
            )
            return to_gql_enrollment(domain_enrollment)

    @strawberry.mutation
    async def update_enrollment_status(
        self, info: Info, enrollment_id: strawberry.ID, status: EnrollmentStatusGQL
    ) -> ProgramEnrollmentTypeGQL:
        """
        Updates the status of a program enrollment (e.g., to CANCELLED or COMPLETED).

        Authorization Rules:
        - A user can update their own enrollment.
        - A user with the 'coach' role in the 'practices' domain can update any enrollment.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]
        enrollment_uuid = uuid.UUID(str(enrollment_id))

        if not current_user:
            raise Exception("Authentication required.")

        async with uow:
            # First, we need to fetch the enrollment to check ownership
            enrollment_repo = EnrollmentRepository(uow.session)
            enrollment = await enrollment_repo.get_enrollment_by_id(enrollment_uuid)

            if not enrollment:
                raise Exception("Enrollment not found.")

            # Check permissions
            is_owner = enrollment.user_id == current_user.id

            # A coach can only manage an enrollment if they are the coach for that specific client.
            is_authorized_coach = False
            if current_user.has_role(role="coach", domain="practices"):
                is_authorized_coach = await users_service_client.verify_coach_client_relationship(
                    coach_id=current_user.id, client_id=enrollment.user_id, domain="practices"
                )

            if not is_owner and not is_authorized_coach:
                raise Exception("You do not have permission to update this enrollment.")

            # If authorized, proceed to update
            service = EnrollmentService(enrollment_repo)
            updated_enrollment = await service.update_enrollment_status(
                enrollment_id=enrollment_uuid,
                status=status.value,
            )
            if not updated_enrollment:
                # This case should ideally not be hit if the initial fetch succeeded
                raise Exception("Failed to update enrollment.")

            return to_gql_enrollment(updated_enrollment)

    @strawberry.mutation(permission_classes=[CanAdvanceProgress])
    async def complete_and_advance_progress(self, info: Info, enrollment_id: strawberry.ID) -> ProgramEnrollmentTypeGQL:
        """Completes the current practice for an enrollment and advances the progress marker."""
        context = cast(CustomContext, info.context)
        current_user = cast(CurrentUser, context.current_user)
        uow = context.uow
        enrollment_uuid = uuid.UUID(str(enrollment_id))

        try:
            async with uow:
                enrollment_repo = EnrollmentRepository(uow.session)
                scheduled_practice_repo = ScheduledPracticeRepository(uow.session)
                progress_service = ProgressService(enrollment_repo, scheduled_practice_repo)

                # The service returns the domain model
                updated_enrollment = await progress_service.complete_and_advance_progress(
                    enrollment_id=enrollment_uuid, user_id=current_user.id
                )
                # We convert it to the GQL type for the response
                return to_gql_enrollment(updated_enrollment)
        except ProgressServiceError as e:
            raise GraphQLError(str(e))

    @strawberry.mutation(permission_classes=[CanDeferPractice])
    async def defer_practice(self, info: Info, enrollment_id: strawberry.ID, mode: str) -> bool:
        """
        Defers a user's scheduled practice.
        'push': Pushes today's practice to tomorrow.
        'shift': Pushes today's and all subsequent practices forward by one day.
        """
        context = cast(CustomContext, info.context)
        current_user = cast(CurrentUser, context.current_user)
        uow = context.uow
        enrollment_uuid = uuid.UUID(str(enrollment_id))

        try:
            async with uow:
                enrollment_repo = EnrollmentRepository(uow.session)
                scheduled_practice_repo = ScheduledPracticeRepository(uow.session)
                progress_service = ProgressService(enrollment_repo, scheduled_practice_repo)
                await progress_service.defer_practice(enrollment_id=enrollment_uuid, user_id=current_user.id, mode=mode)
            return True
        except ProgressServiceError as e:
            raise GraphQLError(str(e))
