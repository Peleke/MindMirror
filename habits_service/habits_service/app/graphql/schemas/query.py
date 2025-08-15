import strawberry
from strawberry.types import Info
from datetime import date
from typing import List, Optional, Set
from datetime import timedelta

from habits_service.habits_service.app.db.uow import UnitOfWork
from habits_service.habits_service.app.db.repositories import HabitsReadRepository
from habits_service.habits_service.app.services.planner import (
    plan_daily_tasks,
    HabitTask as PHabitTask,
    LessonTask as PLessonTask,
    JournalTask as PJournalTask,
)
from .task_types import (
    Task,
    HabitTask as GHabitTask,
    LessonTask as GLessonTask,
    JournalTask as GJournalTask,
    TaskType as GTaskType,
    TaskStatus as GTaskStatus,
)
from habits_service.habits_service.app.graphql.context import get_current_user_from_context


# Top-level GraphQL types to avoid unresolved nested type issues
@strawberry.type
class LessonTemplateType:
    id: str
    slug: str
    title: str
    summary: Optional[str]
    markdownContent: str
    subtitle: Optional[str]
    heroImageUrl: Optional[str]


@strawberry.type
class HabitBasicType:
    id: str
    title: str
    shortDescription: Optional[str]


@strawberry.type
class ProgramStepType:
    id: str
    sequenceIndex: int
    durationDays: int
    habit: HabitBasicType
    started: bool
    daysCompleted: int
    totalDays: int


@strawberry.type
class LessonForHabitType:
    lessonTemplateId: str
    title: str
    summary: Optional[str]
    completed: bool


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"

    @strawberry.field
    def service(self) -> str:
        return "habits"

    @strawberry.field
    async def todaysTasks(self, info: Info, onDate: date) -> List[Task]:
        current_user = get_current_user_from_context(info)
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            planned = await plan_daily_tasks(str(current_user.id), onDate, repo)

            converted: List[Task] = []
            for t in planned:
                if isinstance(t, PHabitTask):
                    converted.append(
                        GHabitTask(
                            taskId=t.taskId,
                            type=GTaskType.habit,
                            habitTemplateId=t.habitTemplateId,
                            title=t.title,
                            description=t.description,
                            subtitle=getattr(t, 'subtitle', None),
                            status=GTaskStatus(t.status.value) if hasattr(t.status, "value") else GTaskStatus[t.status],
                        )
                    )
                elif isinstance(t, PLessonTask):
                    converted.append(
                        GLessonTask(
                            taskId=t.taskId,
                            type=GTaskType.lesson,
                            lessonTemplateId=t.lessonTemplateId,
                            title=t.title,
                            summary=t.summary,
                            status=GTaskStatus(t.status.value) if hasattr(t.status, "value") else GTaskStatus[t.status],
                        )
                    )
                elif isinstance(t, PJournalTask):
                    converted.append(
                        GJournalTask(
                            taskId=t.taskId,
                            type=GTaskType.journal,
                            title=t.title,
                            description=t.description,
                            status=GTaskStatus(t.status.value) if hasattr(t.status, "value") else GTaskStatus[t.status],
                        )
                    )

            return converted

    @strawberry.type
    class ProgramTemplateType:
        id: str
        slug: str
        title: str
        description: Optional[str]
        subtitle: Optional[str]
        heroImageUrl: Optional[str]
        # future: subtitle, heroImageUrl

    @strawberry.field
    async def programTemplates(self) -> List[ProgramTemplateType]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            rows = await repo.list_program_templates()
            return [Query.ProgramTemplateType(id=str(r.id), slug=r.slug, title=r.title, description=r.description, subtitle=getattr(r, 'subtitle', None), heroImageUrl=getattr(r, 'hero_image_url', None)) for r in rows]

    @strawberry.field
    async def programTemplateBySlug(self, slug: str) -> Optional[ProgramTemplateType]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            r = await repo.get_program_template_by_slug(slug)
            if not r:
                return None
            return Query.ProgramTemplateType(id=str(r.id), slug=r.slug, title=r.title, description=r.description, subtitle=getattr(r, 'subtitle', None), heroImageUrl=getattr(r, 'hero_image_url', None))

    @strawberry.type
    class ProgramAssignmentType:
        id: str
        userId: str
        programTemplateId: str
        status: str
        startDate: date

    @strawberry.field
    async def programAssignments(self, info: Info, status: Optional[str] = None) -> List[ProgramAssignmentType]:
        current_user = get_current_user_from_context(info)
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            rows = await repo.list_assignments(str(current_user.id), status)
            return [
                Query.ProgramAssignmentType(
                    id=str(r.id),
                    userId=r.user_id,
                    programTemplateId=str(r.program_template_id),
                    status=r.status,
                    startDate=r.start_date,
                )
                for r in rows
            ]

    @strawberry.field
    async def lessonTemplateById(self, id: str) -> Optional[LessonTemplateType]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            row = await repo.get_lesson_template_by_id(id)
            if not row:
                return None
            return LessonTemplateType(
                id=str(row.id),
                slug=row.slug,
                title=row.title,
                summary=row.summary,
                markdownContent=row.markdown_content,
                subtitle=getattr(row, "subtitle", None),
                heroImageUrl=getattr(row, "hero_image_url", None),
            )

    @strawberry.field
    async def programTemplateSteps(self, info: Info, programId: str) -> List[ProgramStepType]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            steps = await repo.get_program_steps(programId)
            out: List[ProgramStepType] = []
            # compute progress using user's assignment for this program, if any
            current_user = get_current_user_from_context(info)
            assignments = await repo.get_active_assignments(str(current_user.id))
            assignment = next((a for a in assignments if str(a.program_template_id) == programId), None)
            from datetime import date as _date
            today = _date.today()
            day_offset = (today - assignment.start_date).days if assignment else -1
            # precompute prefix sums of duration
            cursor = 0
            for s in steps:
                habit = await repo.get_habit_template(str(s.habit_template_id))
                if not habit:
                    continue
                total_days = int(s.duration_days)
                started = assignment is not None and day_offset >= cursor
                if not started:
                    days_completed = 0
                elif day_offset >= cursor + total_days:
                    days_completed = total_days
                else:
                    days_completed = max(0, min(total_days, (day_offset - cursor + 1)))
                out.append(
                    ProgramStepType(
                        id=str(s.id),
                        sequenceIndex=s.sequence_index,
                        durationDays=s.duration_days,
                        habit=HabitBasicType(
                            id=str(habit.id),
                            title=habit.title,
                            shortDescription=habit.short_description,
                        ),
                        started=started,
                        daysCompleted=days_completed,
                        totalDays=total_days,
                    )
                )
                cursor += s.duration_days
            return out

    @strawberry.type
    class StepLessonType:
        dayIndex: int
        lessonTemplateId: str
        title: str
        summary: Optional[str]
        estReadMinutes: Optional[int]
        subtitle: Optional[str]
        heroImageUrl: Optional[str]

    @strawberry.field
    async def programStepLessons(self, programStepId: str) -> List[StepLessonType]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            sl = await repo.get_step_lessons(programStepId)
            if not sl:
                return []
            lesson_ids = [str(x.lesson_template_id) for x in sl]
            lessons = {str(l.id): l for l in await repo.get_lesson_templates(lesson_ids)}
            out: List[Query.StepLessonType] = []
            for m in sl:
                l = lessons.get(str(m.lesson_template_id))
                if not l:
                    continue
                out.append(Query.StepLessonType(
                    dayIndex=m.day_index,
                    lessonTemplateId=str(l.id),
                    title=l.title,
                    summary=l.summary,
                    estReadMinutes=l.est_read_minutes,
                    subtitle=getattr(l, "subtitle", None),
                    heroImageUrl=getattr(l, "hero_image_url", None),
                ))
            return out

    @strawberry.type
    class LessonCompletionType:
        lessonTemplateId: str
        title: str
        summary: Optional[str]
        completedAt: date

    @strawberry.field
    async def recentLessonCompletions(self, info: Info, limit: int = 50) -> List[LessonCompletionType]:
        current_user = get_current_user_from_context(info)
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            events = await repo.list_recent_lesson_completions(str(current_user.id), limit)
            if not events:
                return []
            lesson_ids = list({str(e.lesson_template_id) for e in events})
            lessons = {str(l.id): l for l in (await repo.get_lesson_templates(lesson_ids))}
            out: List[Query.LessonCompletionType] = []
            for e in events:
                l = lessons.get(str(e.lesson_template_id))
                if not l:
                    continue
                out.append(Query.LessonCompletionType(
                    lessonTemplateId=str(l.id),
                    title=l.title,
                    summary=l.summary,
                    completedAt=e.date,
                ))
            return out

    @strawberry.field
    async def lessonsForHabit(self, info: Info, habitTemplateId: str, onDate: date) -> List[LessonForHabitType]:
        current_user = get_current_user_from_context(info)
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            assignments = await repo.get_active_assignments(str(current_user.id))
            lesson_ids: List[str] = []

            for a in assignments:
                day_offset = (onDate - a.start_date).days
                if day_offset < 0:
                    continue
                steps = await repo.get_program_steps(str(a.program_template_id))
                acc = 0
                for s in steps:
                    step_len = s.duration_days
                    if acc <= day_offset < acc + step_len:
                        if str(s.habit_template_id) != habitTemplateId:
                            break
                        day_in_step = day_offset - acc
                        sl = await repo.get_step_lessons_for_day(str(s.id), day_in_step)
                        lesson_ids.extend([str(x.lesson_template_id) for x in sl])
                        break
                    acc += step_len

            ids_set: Set[str] = set(lesson_ids)
            if not ids_set:
                return []

            lessons = await repo.get_lesson_templates(list(ids_set))
            events = await repo.find_lesson_events(str(current_user.id), list(ids_set), onDate)
            completed_ids: Set[str] = {str(e.lesson_template_id) for e in events if e.event_type == 'completed'}

            result: List[LessonForHabitType] = []
            for l in lessons:
                result.append(
                    LessonForHabitType(
                        lessonTemplateId=str(l.id),
                        title=l.title,
                        summary=l.summary,
                        completed=str(l.id) in completed_ids,
                    )
                )
            result.sort(key=lambda x: x.title.lower())
            return result

    @strawberry.type
    class HabitStatsType:
        presentedCount: int
        completedCount: int
        adherenceRate: float
        currentStreak: int

    @strawberry.field
    async def habitStats(self, info: Info, habitTemplateId: str, lookbackDays: int = 14) -> HabitStatsType:
        current_user = get_current_user_from_context(info)
        today = date.today()
        start_day = today - timedelta(days=lookbackDays - 1)

        presented = 0
        completed = 0
        streak = 0

        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            assignments = await repo.get_active_assignments(str(current_user.id))

            # Helper to determine if habit was presented on a given day based on step mapping
            async def is_presented(on_day: date) -> bool:
                for a in assignments:
                    day_offset = (on_day - a.start_date).days
                    if day_offset < 0:
                        continue
                    steps = await repo.get_program_steps(str(a.program_template_id))
                    cursor = 0
                    for s in steps:
                        if day_offset < cursor + s.duration_days:
                            if str(s.habit_template_id) == habitTemplateId:
                                return True
                            break
                        cursor += s.duration_days
                return False

            # Iterate range for presented/completed counts
            d = start_day
            while d <= today:
                if await is_presented(d):
                    presented += 1
                    ev = await repo.find_habit_event(str(current_user.id), habitTemplateId, d)
                    if ev and ev.response == "yes":
                        completed += 1
                d += timedelta(days=1)

            # Compute current streak (consecutive presented+completed backwards from today)
            d = today
            while d >= start_day:
                if await is_presented(d):
                    ev = await repo.find_habit_event(str(current_user.id), habitTemplateId, d)
                    if ev and ev.response == "yes":
                        streak += 1
                        d -= timedelta(days=1)
                        continue
                    break
                else:
                    # If not presented this day, stop streak
                    break

            rate = (completed / presented) if presented else 0.0
            return Query.HabitStatsType(
                presentedCount=presented,
                completedCount=completed,
                adherenceRate=rate,
                currentStreak=streak,
            )


