from __future__ import annotations

import strawberry
from strawberry.types import Info
from habits_service.habits_service.app.graphql.context import get_current_user_from_context
from datetime import date
from typing import Optional

from habits_service.habits_service.app.db.uow import UnitOfWork
from habits_service.habits_service.app.db.repositories.write import (
    HabitTemplateRepository,
    LessonTemplateRepository,
    ProgramTemplateRepository,
)
from habits_service.habits_service.app.db.repositories.write_structural import (
    ProgramStepTemplateRepository,
    StepLessonTemplateRepository,
    UserProgramAssignmentRepository,
)
from habits_service.habits_service.app.db.repositories.write_events import (
    HabitEventRepository,
    LessonEventRepository,
)
from habits_service.habits_service.app.db.repositories import HabitsReadRepository
from habits_service.habits_service.app.config import get_settings


@strawberry.input
class HabitTemplateInput:
    slug: str
    title: str
    shortDescription: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    defaultDurationDays: int = 7


@strawberry.type
class HabitTemplatePayload:
    id: str
    slug: str
    title: str


@strawberry.input
class LessonTemplateInput:
    slug: str
    title: str
    markdownContent: str
    summary: Optional[str] = None


@strawberry.type
class LessonTemplatePayload:
    id: str
    slug: str
    title: str


@strawberry.input
class ProgramTemplateInput:
    slug: str
    title: str
    description: Optional[str] = None


@strawberry.type
class ProgramTemplatePayload:
    id: str
    slug: str
    title: str


@strawberry.input
class ProgramStepInput:
    sequenceIndex: int
    habitTemplateId: str
    durationDays: int


@strawberry.type
class ProgramStepPayload:
    id: str
    programTemplateId: str
    sequenceIndex: int
    habitTemplateId: str
    durationDays: int


@strawberry.type
class AssignmentPayload:
    id: str
    userId: str
    programTemplateId: str
    status: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def createHabitTemplate(self, input: HabitTemplateInput) -> HabitTemplatePayload:
        async with UnitOfWork() as uow:
            repo = HabitTemplateRepository(uow.session)
            obj = await repo.create(
                slug=input.slug,
                title=input.title,
                short_description=input.shortDescription,
                description=input.description,
                level=input.level,
                default_duration_days=input.defaultDurationDays,
            )
            return HabitTemplatePayload(id=str(obj.id), slug=obj.slug, title=obj.title)

    @strawberry.mutation
    async def createLessonTemplate(self, input: LessonTemplateInput) -> LessonTemplatePayload:
        async with UnitOfWork() as uow:
            repo = LessonTemplateRepository(uow.session)
            obj = await repo.create(
                slug=input.slug,
                title=input.title,
                markdown_content=input.markdownContent,
                summary=input.summary,
            )
            return LessonTemplatePayload(id=str(obj.id), slug=obj.slug, title=obj.title)

    @strawberry.mutation
    async def createProgramTemplate(self, input: ProgramTemplateInput) -> ProgramTemplatePayload:
        async with UnitOfWork() as uow:
            repo = ProgramTemplateRepository(uow.session)
            obj = await repo.create(slug=input.slug, title=input.title, description=input.description)
            return ProgramTemplatePayload(id=str(obj.id), slug=obj.slug, title=obj.title)

    @strawberry.mutation
    async def addProgramStep(self, programId: str, input: ProgramStepInput) -> ProgramStepPayload:
        async with UnitOfWork() as uow:
            repo = ProgramStepTemplateRepository(uow.session)
            created = await repo.bulk_create(
                program_template_id=programId,
                steps=[
                    {
                        "sequence_index": input.sequenceIndex,
                        "habit_template_id": input.habitTemplateId,
                        "duration_days": input.durationDays,
                    }
                ],
            )
            s = created[0]
            return ProgramStepPayload(
                id=str(s.id),
                programTemplateId=str(s.program_template_id),
                sequenceIndex=s.sequence_index,
                habitTemplateId=str(s.habit_template_id),
                durationDays=s.duration_days,
            )

    @strawberry.mutation
    async def addStepLesson(self, stepId: str, dayIndex: int, lessonTemplateId: str) -> bool:
        async with UnitOfWork() as uow:
            repo = StepLessonTemplateRepository(uow.session)
            await repo.bulk_create(step_id=stepId, lessons=[{"day_index": dayIndex, "lesson_template_id": lessonTemplateId}])
            return True

    @strawberry.mutation
    async def assignProgramToUser(self, programId: str, startDate: date, info: Info) -> AssignmentPayload:
        async with UnitOfWork() as uow:
            repo = UserProgramAssignmentRepository(uow.session)
            current_user = get_current_user_from_context(info)
            a = await repo.create(user_id=str(current_user.id), program_template_id=programId, start_date=startDate)
            return AssignmentPayload(id=str(a.id), userId=a.user_id, programTemplateId=str(a.program_template_id), status=a.status)

    @strawberry.mutation
    async def unenrollProgram(self, programId: str, info: Info) -> bool:
        async with UnitOfWork() as uow:
            current_user = get_current_user_from_context(info)
            read = HabitsReadRepository(uow.session)
            active = await read.get_active_assignments(str(current_user.id))
            target = next((a for a in active if str(a.program_template_id) == programId), None)
            if not target:
                return True
            write = UserProgramAssignmentRepository(uow.session)
            await write.set_status(str(target.id), 'cancelled')
            await uow.session.commit()
            return True

    @strawberry.mutation
    async def recordHabitResponse(self, habitTemplateId: str, onDate: date, response: str, info: Info) -> bool:
        async with UnitOfWork() as uow:
            repo = HabitEventRepository(uow.session)
            current_user = get_current_user_from_context(info)
            await repo.upsert(user_id=str(current_user.id), habit_template_id=habitTemplateId, on_date=onDate, response=response)
            return True

    @strawberry.mutation
    async def recordLessonOpened(self, lessonTemplateId: str, onDate: date, info: Info) -> bool:
        async with UnitOfWork() as uow:
            repo = LessonEventRepository(uow.session)
            current_user = get_current_user_from_context(info)
            await repo.upsert(user_id=str(current_user.id), lesson_template_id=lessonTemplateId, on_date=onDate, event_type="opened")
            return True

    @strawberry.mutation
    async def markLessonCompleted(self, lessonTemplateId: str, onDate: date, info: Info) -> bool:
        async with UnitOfWork() as uow:
            repo = LessonEventRepository(uow.session)
            current_user = get_current_user_from_context(info)
            await repo.upsert(user_id=str(current_user.id), lesson_template_id=lessonTemplateId, on_date=onDate, event_type="completed")
            return True

    @strawberry.mutation
    async def autoEnroll(self, campaign: str, info: Info) -> bool:
        """Proxy auto-enroll: calls web vouchers autoenroll, then ensures a habits assignment exists."""
        current_user = get_current_user_from_context(info)
        settings = get_settings()
        # Call web REST autoenroll with bearer
        import httpx
        web_base = settings.vouchers_web_base_url
        if not web_base:
            return False
        url = f"{web_base.rstrip('/')}/api/vouchers/autoenroll"
        # Try to forward Authorization header if present
        token = None
        try:
            # strawberry context stores request
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
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=headers)
            ok = resp.status_code == 200
            # proceed regardless; web may not have a voucher
        # Create habits assignment if we have a mapping
        campaign_l = (campaign or '').lower()
        program_id = None
        if campaign_l == 'uye':
            program_id = settings.uye_program_template_id
        elif campaign_l == 'mindmirror':
            program_id = settings.mindmirror_program_template_id
        if not program_id:
            return False
        from datetime import date as _date
        async with UnitOfWork() as uow:
            read = HabitsReadRepository(uow.session)
            active = await read.get_active_assignments(str(current_user.id))
            if any(str(a.program_template_id) == program_id for a in active):
                return True
            write = UserProgramAssignmentRepository(uow.session)
            await write.create(user_id=str(current_user.id), program_template_id=program_id, start_date=_date.today())
            await uow.session.commit()
        return True


