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
    LessonSegmentRepository,
    StepDailyPlanRepository,
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
class AutoEnrollResult:
    ok: bool
    enrolled: bool
    reason: Optional[str] = None


@strawberry.input
class StepDayPlanInput:
    dayIndex: int
    habitVariantText: Optional[str] = None
    journalPromptText: Optional[str] = None
    lessonSegmentId: Optional[str] = None


@strawberry.input
class LessonSegmentInput:
    lessonTemplateId: str
    dayIndexWithinStep: Optional[int] = None
    title: str
    subtitle: Optional[str] = None
    markdownContent: str
    summary: Optional[str] = None


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
            # Avoid duplicate active assignments for the same program
            read = HabitsReadRepository(uow.session)
            active = await read.get_active_assignments(str(current_user.id))
            existing = next((x for x in active if str(x.program_template_id) == programId), None)
            if existing:
                return AssignmentPayload(
                    id=str(existing.id), userId=existing.user_id, programTemplateId=str(existing.program_template_id), status=existing.status
                )
            a = await repo.create(user_id=str(current_user.id), program_template_id=programId, start_date=startDate)
            await uow.session.commit()
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
            await uow.session.commit()
            return True

    @strawberry.mutation
    async def recordLessonOpened(self, lessonTemplateId: str, onDate: date, info: Info) -> bool:
        async with UnitOfWork() as uow:
            repo = LessonEventRepository(uow.session)
            current_user = get_current_user_from_context(info)
            await repo.upsert(user_id=str(current_user.id), lesson_template_id=lessonTemplateId, on_date=onDate, event_type="opened")
            await uow.session.commit()
            return True

    @strawberry.mutation
    async def markLessonCompleted(self, lessonTemplateId: str, onDate: date, info: Info) -> bool:
        async with UnitOfWork() as uow:
            repo = LessonEventRepository(uow.session)
            current_user = get_current_user_from_context(info)
            await repo.upsert(user_id=str(current_user.id), lesson_template_id=lessonTemplateId, on_date=onDate, event_type="completed")
            await uow.session.commit()
            return True

    @strawberry.mutation
    async def upsertStepDailyPlan(self, programStepId: str, items: list[StepDayPlanInput]) -> bool:
        async with UnitOfWork() as uow:
            dprepo = StepDailyPlanRepository(uow.session)
            payload = []
            for it in items or []:
                payload.append({
                    "day_index": int(it.dayIndex),
                    "habit_variant_text": it.habitVariantText,
                    "journal_prompt_text": it.journalPromptText,
                    "lesson_segment_id": it.lessonSegmentId,
                })
            await dprepo.bulk_upsert(step_id=programStepId, plans=payload)
            await uow.session.commit()
            return True

    @strawberry.mutation
    async def upsertLessonSegments(self, segments: list[LessonSegmentInput]) -> bool:
        async with UnitOfWork() as uow:
            segrepo = LessonSegmentRepository(uow.session)
            payload = []
            for s in segments or []:
                payload.append({
                    "lesson_template_id": s.lessonTemplateId,
                    "day_index_within_step": s.dayIndexWithinStep,
                    "title": s.title,
                    "subtitle": s.subtitle,
                    "markdown_content": s.markdownContent,
                    "summary": s.summary,
                })
            await segrepo.bulk_upsert(payload)
            await uow.session.commit()
            return True

    @strawberry.mutation
    async def autoEnroll(self, campaign: str, info: Info) -> AutoEnrollResult:
        """Proxy auto-enroll: calls web vouchers autoenroll, then ensures a habits assignment exists when eligible."""
        current_user = get_current_user_from_context(info)
        settings = get_settings()

        # Prepare call to web REST autoenroll with bearer
        import httpx
        web_base = settings.vouchers_web_base_url
        if not web_base:
            return AutoEnrollResult(ok=False, enrolled=False, reason="web_base_url_not_configured")
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
            # If web call fails, continue; we'll return ok=False
            return AutoEnrollResult(ok=False, enrolled=False, reason="web_call_failed")

        # Map campaign to program id
        campaign_l = (campaign or '').lower()
        program_id = None
        if campaign_l == 'uye':
            program_id = settings.uye_program_template_id
        elif campaign_l == 'mindmirror':
            program_id = settings.mindmirror_program_template_id
        if not program_id:
            return AutoEnrollResult(ok=False, enrolled=False, reason="unknown_campaign")

        # Only create assignment if web reported enrolled True
        if not web_enrolled:
            return AutoEnrollResult(ok=True, enrolled=False, reason=web_reason)

        from datetime import date as _date
        async with UnitOfWork() as uow:
            read = HabitsReadRepository(uow.session)
            active = await read.get_active_assignments(str(current_user.id))

            # Determine if primary program; daily journaling auto-enroll disabled
            journaling_program_id = None  # auto-enrollment for daily journaling reverted
            has_primary = any(str(a.program_template_id) == program_id for a in active)
            has_journaling = False

            write = UserProgramAssignmentRepository(uow.session)

            # Ensure primary program assignment exists
            if not has_primary:
                await write.create(
                    user_id=str(current_user.id),
                    program_template_id=program_id,
                    start_date=_date.today(),
                )
            # Daily journaling program auto-enrollment intentionally disabled
            await uow.session.commit()
        return AutoEnrollResult(ok=True, enrolled=True)
