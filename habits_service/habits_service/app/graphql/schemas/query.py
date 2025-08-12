import strawberry
from datetime import date
from typing import List, Optional

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


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"

    @strawberry.field
    def service(self) -> str:
        return "habits"

    @strawberry.field
    async def todaysTasks(self, userId: str, onDate: date) -> List[Task]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            planned = await plan_daily_tasks(userId, onDate, repo)

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

    @strawberry.field
    async def programTemplates(self) -> List[ProgramTemplateType]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            rows = await repo.list_program_templates()
            return [Query.ProgramTemplateType(id=str(r.id), slug=r.slug, title=r.title, description=r.description) for r in rows]

    @strawberry.field
    async def programTemplateBySlug(self, slug: str) -> Optional[ProgramTemplateType]:
        async with UnitOfWork() as uow:
            repo = HabitsReadRepository(uow.session)
            r = await repo.get_program_template_by_slug(slug)
            if not r:
                return None
            return Query.ProgramTemplateType(id=str(r.id), slug=r.slug, title=r.title, description=r.description)


