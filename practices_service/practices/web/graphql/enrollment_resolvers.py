import json
import uuid
from datetime import date, timedelta
from typing import List, Optional, cast, Dict

import strawberry
from graphql import GraphQLError
from shared.auth import CurrentUser, RequireRolePermission
from shared.clients.user_service_client import users_service_client
from strawberry.types import Info
import os

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

from practices.repository.repositories.program_repository import ProgramRepository
from practices.repository.repositories.practice_instance_repository import PracticeInstanceRepository
from practices.repository.models.practice_instance import PracticeInstanceModel

from .enrollment_types import (
    AttachLessonsToProgramEnrollmentInput,
    EnrollInProgramInput,
    EnrollUserInProgramInput,
    EnrollmentStatusGQL,
    ProgramEnrollmentTypeGQL
)
from practices.clients.habits_service_client import HabitsServiceClient


from .practice_instance_types import PracticeInstanceType
from .progress_types import ScheduledPracticeTypeGQL

# Lesson Template types for GraphQL (namespaced to avoid federation collisions)
@strawberry.type
class PracticesLessonTemplateType:
    id: str
    slug: str
    title: str
    summary: Optional[str]
    segments: Optional[List["PracticesLessonSegmentType"]]
    default_segment: Optional[str]

@strawberry.type
class PracticesLessonSegmentType:
    id: str
    label: str
    selector: str

# Habits Program Template types for GraphQL (namespaced to avoid federation collisions)
@strawberry.type
class HabitsProgramTemplateType:
    id: str
    slug: str
    title: str
    description: Optional[str] = None
    subtitle: Optional[str] = None
    hero_image_url: Optional[str] = None


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
        practice_instance_id=scheduled_practice.practice_instance_id,
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

    @strawberry.field
    async def workoutsForUser(
        self, 
        info: Info, 
        userId: strawberry.ID, 
        dateFrom: Optional[str] = None, 
        dateTo: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PracticeInstanceType]:
        """
        Retrieves workouts (practice instances) for a user.
        
        Authorization Rules:
        - A user can retrieve their own workouts.
        - A coach can retrieve workouts of their verified client.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]
        target_user_uuid = uuid.UUID(str(userId))

        # Authorization Check
        is_owner = target_user_uuid == current_user.id
        is_authorized_coach = False
        if current_user.has_role("coach", "practices"):
            is_authorized_coach = await users_service_client.verify_coach_client_relationship(
                coach_id=current_user.id, client_id=target_user_uuid, domain="practices"
            )

        if not is_owner and not is_authorized_coach:
            # Return empty list if not authorized
            return []

        # Parse dates if provided
        from_date = None
        to_date = None
        if dateFrom:
            try:
                from_date = date.fromisoformat(dateFrom)
            except ValueError:
                raise GraphQLError(f"Invalid dateFrom format: {dateFrom}")
        if dateTo:
            try:
                to_date = date.fromisoformat(dateTo)
            except ValueError:
                raise GraphQLError(f"Invalid dateTo format: {dateTo}")

        async with uow:
            from practices.repository.repositories.practice_instance_repository import PracticeInstanceRepository
            instance_repo = PracticeInstanceRepository(uow.session)
            
            # Get practice instances for the user
            # Note: Adjusted to call existing repository methods (list_*), since get_instances_for_user
            # was not implemented. This preserves intended filtering semantics.
            if from_date and to_date:
                instances = await instance_repo.list_instances_by_date_range(
                    user_id=target_user_uuid,
                    date_from=from_date,
                    date_to=to_date,
                    status=status
                )
            else:
                # Fallback to all instances for user, with optional status filtering
                instances = await instance_repo.list_instances_for_user(user_id=target_user_uuid)
                if status:
                    s = status.lower()
                    today = date.today()
                    if s == "completed":
                        instances = [i for i in instances if i.completed_at is not None]
                    elif s == "scheduled":
                        instances = [i for i in instances if i.completed_at is None and i.date >= today]
                    elif s == "missed":
                        instances = [i for i in instances if i.completed_at is None and i.date < today]
            
            # Convert to GraphQL types (top-level fields only)
            from practices.web.graphql.practice_instance_types import PracticeInstanceType
            return [
                PracticeInstanceType(
                    id_=inst.id_,
                    title=inst.title or "",
                    date=inst.date,
                    user_id=inst.user_id,
                    template_id=inst.template_id,
                    description=inst.description,
                    completed_at=inst.completed_at,
                    prescriptions=[],
                )
                for inst in instances
            ]


@strawberry.type
class EnrollmentMutation:
    @strawberry.type
    class PracticesAutoEnrollResult:
        ok: bool
        enrolled: bool
        reason: Optional[str] = None

    @strawberry.mutation
    async def autoEnrollPractices(self, campaign: str, info: Info) -> PracticesAutoEnrollResult:
        """Proxy auto-enroll for practices: calls web vouchers autoenroll, then ensures a practices program enrollment exists when eligible."""
        # Resolve vouchers web base URL
        web_base = os.getenv("VOUCHERS_WEB_BASE_URL", "").strip()
        if not web_base:
            return EnrollmentMutation.PracticesAutoEnrollResult(ok=False, enrolled=False, reason="web_base_url_not_configured")
        url = f"{web_base.rstrip('/')}/api/vouchers/autoenroll"

        # Forward Authorization header when available
        token = None
        try:
            req = info.context.get('request')
            if req:
                authz = req.headers.get('authorization')
                if authz and authz.lower().startswith('bearer '):
                    token = authz.split(' ', 1)[1]
        except Exception:
            pass
        headers = {'content-type': 'application/json'}
        if token:
            headers['authorization'] = f"Bearer {token}"

        # Call vouchers autoenroll
        web_enrolled = False
        web_reason: Optional[str] = None
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, headers=headers, json={})
                if resp.status_code == 200:
                    data = resp.json()
                    web_enrolled = bool(data.get('enrolled'))
                    web_reason = data.get('reason')
                else:
                    web_reason = f"web_status_{resp.status_code}"
        except Exception:
            return EnrollmentMutation.PracticesAutoEnrollResult(ok=False, enrolled=False, reason="web_call_failed")

        # Map campaign to program template id (env)
        campaign_l = (campaign or '').lower()
        program_id = None
        if campaign_l == 'uye':
            program_id = os.getenv('PRACTICES_UYE_PROGRAM_TEMPLATE_ID')
        elif campaign_l == 'mindmirror':
            program_id = os.getenv('PRACTICES_MINDMIRROR_PROGRAM_TEMPLATE_ID')
        if not program_id:
            return EnrollmentMutation.PracticesAutoEnrollResult(ok=False, enrolled=False, reason="unknown_campaign")

        # Only enroll if web reported enrolled True
        if not web_enrolled:
            return EnrollmentMutation.PracticesAutoEnrollResult(ok=True, enrolled=False, reason=web_reason)

        # Create enrollment for current user with default repeat count (1 week)
        context = cast(CustomContext, info.context)
        current_user = cast(CurrentUser, context.current_user)
        uow = context.uow

        # Use the same enrollment logic as self-enrollment with defaults
        enrollment_input = EnrollInProgramInput(
            program_id=program_id,
            repeat_count=1,  # Default to 1 week
            lessons=None  # No lessons by default for auto-enrollment
        )

        async with uow:
            domain_enrollment = await self.enroll_in_program(info, enrollment_input)

        return EnrollmentMutation.PracticesAutoEnrollResult(ok=True, enrolled=True)

    @strawberry.mutation(permission_classes=[CanSelfEnroll])
    async def enroll_in_program(self, info: Info, input: EnrollInProgramInput) -> ProgramEnrollmentTypeGQL:
        """
        Allows a user to self-enroll in a program with optional repeat count and lessons.
        The user must have the 'client' role in the 'practices' domain.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]

        async with uow:
            repo = EnrollmentRepository(uow.session)
            service = EnrollmentService(repo)
            domain_enrollment = await service.enroll_user(
                program_id=uuid.UUID(str(input.program_id)),
                user_to_enroll_id=current_user.id,
                enrolling_user_id=current_user.id,  # For self-enrollment
            )

            # Seed initial progress: set current practice to first link and schedule workouts for repeat cycle
            program_repo = ProgramRepository(uow.session)
            program_uuid = uuid.UUID(str(input.program_id))
            program = await program_repo.get_program_by_id(program_uuid)
            if program and program.practice_links:
                first_link = sorted(program.practice_links, key=lambda pl: pl.sequence_order)[0]
                # Fetch the enrollment model to update its current_practice_link_id
                enrollment_model = await repo.get_enrollment_by_id(uuid.UUID(str(domain_enrollment.id_)))
                if enrollment_model:
                    enrollment_model.current_practice_link_id = first_link.id_

                    # Schedule practices for the repeat cycle
                    sp_repo = ScheduledPracticeRepository(uow.session)
                    today = date.today()

                    # Get all practice links ordered by sequence
                    ordered_links = sorted(program.practice_links, key=lambda pl: pl.sequence_order)
                    link_index = 0

                    # Clear any existing scheduled practices for this enrollment from today forward to avoid duplication
                    from sqlalchemy import delete
                    await uow.session.execute(
                        delete(ScheduledPracticeModel).where(
                            ScheduledPracticeModel.enrollment_id == enrollment_model.id_
                        ).where(ScheduledPracticeModel.scheduled_date >= today)
                    )

                    # Honor interval_days_after per link: lay links sequentially with per-link spacing
                    current_date = today
                    total_weeks = max(1, int(input.repeat_count))
                    cycles = total_weeks * len(ordered_links)
                    for i in range(cycles):
                        current_link = ordered_links[link_index]
                        scheduled = ScheduledPracticeModel(
                            enrollment_id=enrollment_model.id_,
                            practice_template_id=current_link.practice_template_id,
                            scheduled_date=current_date,
                        )
                        await sp_repo.add(scheduled)

                        # Materialize instance if one does not already exist for this date/template
                        from sqlalchemy import select
                        exists_stmt = (
                            select(PracticeInstanceModel)
                            .where(PracticeInstanceModel.user_id == current_user.id)
                            .where(PracticeInstanceModel.date == current_date)
                            .where(PracticeInstanceModel.template_id == current_link.practice_template_id)
                        )
                        result = await uow.session.execute(exists_stmt)
                        existing = result.scalar_one_or_none()
                        if not existing:
                            pir = PracticeInstanceRepository(uow.session)
                            new_instance = await pir.create_instance_from_template(
                                template_id=current_link.practice_template_id,
                                user_id=current_user.id,
                                date=current_date,
                            )
                            scheduled.practice_instance_id = new_instance.id_

                        # Advance link and date by this link's interval
                        link_index = (link_index + 1) % len(ordered_links)
                        # interval_days_after = number of off days BETWEEN workouts; schedule gap = interval + 1 days
                        step = (int(current_link.interval_days_after or 0) + 1)
                        current_date = current_date + timedelta(days=step)

            # Attach lessons if provided
            if input.lessons:
                for lesson_input in input.lessons:
                    try:
                        await self.attachLessonsToProgramEnrollment(info, lesson_input)
                    except Exception as e:
                        # Log error but don't fail the entire enrollment
                        print(f"Failed to attach lesson {lesson_input.lesson_template_slug}: {e}")

            # Auto-enroll in paired habits program if specified
            if program and program.habits_program_template_id:
                try:
                    habits_client = HabitsServiceClient()
                    
                    # Get user token for authentication
                    req = info.context.get('request')
                    token = None
                    if req:
                        authz = req.headers.get('authorization')
                        if authz and authz.lower().startswith('bearer '):
                            token = authz.split(' ', 1)[1]
                    
                    # Enroll user in the paired habits program
                    from datetime import date as _date
                    habits_enrollment = await habits_client.enroll_user_in_program(
                        program_template_id=str(program.habits_program_template_id),
                        start_date=_date.today(),
                        auth_token=token
                    )
                    
                    if habits_enrollment:
                        print(f"Successfully enrolled user {current_user.id} in habits program {program.habits_program_template_id}")
                    else:
                        print(f"Failed to enroll user {current_user.id} in habits program {program.habits_program_template_id}")
                        
                except Exception as e:
                    # Log error but don't fail the practices enrollment
                    print(f"Failed to auto-enroll in habits program {program.habits_program_template_id}: {e}")

            # The Unit of Work context manager handles the commit.
            return to_gql_enrollment(domain_enrollment)

    @strawberry.mutation(permission_classes=[CanEnrollOthers])
    async def enroll_user_in_program(
        self, info: Info, input: EnrollUserInProgramInput
    ) -> ProgramEnrollmentTypeGQL:
        """
        Allows a coach to enroll another user in a program with optional repeat count and lessons.
        The acting user must have the 'coach' role in the 'practices' domain.
        """
        uow: UnitOfWork = info.context["uow"]
        current_user: CurrentUser = info.context["current_user"]
        user_to_enroll_id = uuid.UUID(str(input.user_id))

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
                program_id=uuid.UUID(str(input.program_id)),
                user_to_enroll_id=user_to_enroll_id,
                enrolling_user_id=current_user.id,  # The coach is the enroller
            )

            # Attach lessons if provided
            if input.lessons:
                for lesson_input in input.lessons:
                    try:
                        await self.attachLessonsToProgramEnrollment(info, lesson_input)
                    except Exception as e:
                        # Log error but don't fail the entire enrollment
                        print(f"Failed to attach lesson {lesson_input.lesson_template_slug}: {e}")

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

            # Cascade cleanup when cancelling enrollment
            if status.value == "CANCELLED":
                scheduled_practice_repo = ScheduledPracticeRepository(uow.session)
                await scheduled_practice_repo.delete_for_enrollments_from_date([enrollment_uuid], from_date=date.today())

                # Delete future uncompleted practice instances for templates in this program
                from sqlalchemy import delete
                from practices.repository.models.practice_instance import PracticeInstanceModel
                program_repo = ProgramRepository(uow.session)
                prog = await program_repo.get_program_by_id(updated_enrollment.program_id)
                template_ids = [pl.practice_id for pl in (prog.practice_links or [])]
                if template_ids:
                    await uow.session.execute(
                        delete(PracticeInstanceModel)
                        .where(PracticeInstanceModel.user_id == updated_enrollment.user_id)
                        .where(PracticeInstanceModel.template_id.in_(template_ids))
                        .where(PracticeInstanceModel.date >= date.today())
                        .where(PracticeInstanceModel.completed_at.is_(None))
                    )

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

    @strawberry.mutation(permission_classes=[CanEnrollOthers])
    async def assignProgramToClient(
        self, info: Info, programId: strawberry.ID, clientId: strawberry.ID, campaign: Optional[str] = None
    ) -> bool:
        """
        Coach assigns a workout program to a client by issuing a voucher.
        Requires coach role and verified coach-client relationship.
        """
        context = cast(CustomContext, info.context)
        current_user = cast(CurrentUser, context.current_user)
        uow = context.uow

        if not current_user:
            raise Exception("Authentication required.")

        # Verify coach role
        if not current_user.has_role(role="coach", domain="practices"):
            raise Exception("You do not have a COACH role in the practices domain.")

        # Verify coach-client relationship
        client_uuid = uuid.UUID(str(clientId))
        is_verified_coach = await users_service_client.verify_coach_client_relationship(
            coach_id=current_user.id, client_id=client_uuid, domain="practices"
        )
        if not is_verified_coach:
            raise Exception("You are not authorized to assign programs to this client.")

        # Determine campaign from argument or env mapping
        final_campaign = campaign
        if not final_campaign:
            # Map programId to campaign via environment variable
            program_campaign_map_str = os.getenv("PRACTICES_PROGRAM_CAMPAIGN_MAP", "{}")
            try:
                program_campaign_map = json.loads(program_campaign_map_str)
                final_campaign = program_campaign_map.get(str(programId))
            except (json.JSONDecodeError, AttributeError):
                pass
            
            # Fallback to template IDs from env
            if not final_campaign:
                uye_template_id = os.getenv("PRACTICES_UYE_PROGRAM_TEMPLATE_ID")
                mindmirror_template_id = os.getenv("PRACTICES_MINDMIRROR_PROGRAM_TEMPLATE_ID")
                if str(programId) == uye_template_id:
                    final_campaign = "uye"
                elif str(programId) == mindmirror_template_id:
                    final_campaign = "mindmirror"
                else:
                    final_campaign = "default"

        # Get client email (simplified - in production you'd get from users service)
        # For now, we'll use a placeholder since we need the client's email
        async with uow:
            # TODO: Get client email from users service
            # For now, raise not implemented
            raise NotImplementedError("Client email lookup not implemented yet. Voucher issuance requires client email.")

        # Call vouchers web API to mint/assign voucher
        # This would be implemented once we have the client email lookup working
        return True

    @strawberry.mutation(permission_classes=[CanEnrollOthers])
    async def attachLessonsToProgramEnrollment(
        self, info: Info, input: AttachLessonsToProgramEnrollmentInput
    ) -> bool:
        """
        Attaches lessons to a program enrollment by computing the target date and calling habits_service.

        Authorization Rules:
        - A user with the 'coach' role in the 'practices' domain can attach lessons.
        """
        context = cast(CustomContext, info.context)
        current_user = cast(CurrentUser, context.current_user)
        uow = context.uow

        if not current_user:
            raise Exception("Authentication required.")

        # Verify coach role
        if not current_user.has_role(role="coach", domain="practices"):
            raise Exception("You do not have a COACH role in the practices domain.")

        enrollment_uuid = uuid.UUID(str(input.enrollment_id))

        async with uow:
            # Get enrollment to verify authorization and get start date
            enrollment_repo = EnrollmentRepository(uow.session)
            enrollment = await enrollment_repo.get_enrollment_by_id(enrollment_uuid)

            if not enrollment:
                raise Exception("Enrollment not found.")

            # Verify coach can access this enrollment
            is_authorized_coach = await users_service_client.verify_coach_client_relationship(
                coach_id=current_user.id, client_id=enrollment.user_id, domain="practices"
            )
            if not is_authorized_coach:
                raise Exception("You are not authorized to modify this enrollment.")

            # Get lesson template by slug
            from habits_service.habits_service.app.db.repositories.write import LessonTemplateRepository
            lesson_repo = LessonTemplateRepository(uow.session)
            lesson_template = await lesson_repo.get_by_slug(input.lesson_template_slug)

            if not lesson_template:
                raise Exception(f"Lesson template with slug '{input.lesson_template_slug}' not found.")

            # Compute target date
            target_date = enrollment.created_at.date()
            if input.day_offset > 0:
                target_date = target_date + timedelta(days=input.day_offset)

            # If on_workout_day is true, align to next workout day
            if input.on_workout_day:
                # Get scheduled practices for this enrollment
                scheduled_repo = ScheduledPracticeRepository(uow.session)
                scheduled_practices = await scheduled_repo.list(
                    enrollment_ids=[enrollment.id_], from_date=target_date
                )
                if scheduled_practices:
                    target_date = scheduled_practices[0].scheduled_date
                else:
                    # Find next scheduled workout day
                    all_practices = await scheduled_repo.list(
                        enrollment_ids=[enrollment.id_], from_date=target_date
                    )
                    future_practices = [p for p in all_practices if p.scheduled_date >= target_date]
                    if future_practices:
                        target_date = min(p.scheduled_date for p in future_practices)

            # Create lesson task using the dedicated client
            habits_client = HabitsServiceClient()

            # Get user token for authentication
            req = info.context.get('request')
            token = None
            if req:
                authz = req.headers.get('authorization')
                if authz and authz.lower().startswith('bearer '):
                    token = authz.split(' ', 1)[1]

            await habits_client.create_lesson_task(
                user_id=str(enrollment.user_id),
                lesson_template_id=str(lesson_template.id),
                task_date=target_date,
                segment_ids=input.segment_ids,
                auth_token=token
            )

            return True

    @strawberry.field
    async def habits_lesson_templates(self, info: Info) -> List[PracticesLessonTemplateType]:
        """Get all lesson templates from habits_service."""
        habits_client = HabitsServiceClient()

        # Get user token for authentication
        req = info.context.get('request')
        token = None
        if req:
            authz = req.headers.get('authorization')
            if authz and authz.lower().startswith('bearer '):
                token = authz.split(' ', 1)[1]

        lesson_templates = await habits_client.get_lesson_templates(auth_token=token)

        out: List[PracticesLessonTemplateType] = []
        for template in lesson_templates:
            segs = template.get("segments") or []
            mapped_segments = [
                PracticesLessonSegmentType(
                    id=str(s.get("id")),
                    label=str(s.get("label")),
                    selector=str(s.get("selector")),
                )
                for s in segs
                if s is not None
            ]
            out.append(
                PracticesLessonTemplateType(
                    id=str(template["id"]),
                    slug=str(template["slug"]),
                    title=str(template["title"]),
                    summary=template.get("summary"),
                    segments=mapped_segments or None,
                    default_segment=template.get("defaultSegment"),
                )
            )
        return out

    @strawberry.field
    async def habits_lesson_template_by_slug(self, info: Info, slug: str) -> Optional[PracticesLessonTemplateType]:
        """Get a lesson template by slug from habits_service."""
        habits_client = HabitsServiceClient()

        # Get user token for authentication
        req = info.context.get('request')
        token = None
        if req:
            authz = req.headers.get('authorization')
            if authz and authz.lower().startswith('bearer '):
                token = authz.split(' ', 1)[1]

        lesson_template = await habits_client.get_lesson_template_by_slug(slug, auth_token=token)

        if not lesson_template:
            return None

        segs = lesson_template.get("segments") or []
        mapped_segments = [
            PracticesLessonSegmentType(
                id=str(s.get("id")),
                label=str(s.get("label")),
                selector=str(s.get("selector")),
            )
            for s in segs
            if s is not None
        ]
        return PracticesLessonTemplateType(
            id=str(lesson_template["id"]),
            slug=str(lesson_template["slug"]),
            title=str(lesson_template["title"]),
            summary=lesson_template.get("summary"),
            segments=mapped_segments or None,
            default_segment=lesson_template.get("defaultSegment"),
        )

    @strawberry.field
    async def habits_program_templates(self, info: Info) -> List[HabitsProgramTemplateType]:
        """Get all program templates from habits_service."""
        habits_client = HabitsServiceClient()

        # Get user token for authentication
        req = info.context.get('request')
        token = None
        if req:
            authz = req.headers.get('authorization')
            if authz and authz.lower().startswith('bearer '):
                token = authz.split(' ', 1)[1]

        templates = await habits_client.get_program_templates(auth_token=token)
        
        return [
            HabitsProgramTemplateType(
                id=tpl["id"],
                slug=tpl["slug"],
                title=tpl["title"],
                description=tpl.get("description"),
                subtitle=tpl.get("subtitle"),
                hero_image_url=tpl.get("heroImageUrl")
            ) for tpl in templates
        ]
