from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from habits_service.habits_service.app.db.repositories import HabitsReadRepository
from habits_service.habits_service.app.db.tables import ProgramStepTemplate


from habits_service.habits_service.app.graphql.schemas.task_types import TaskType, TaskStatus


@dataclass
class HabitTask:
    taskId: str
    type: TaskType
    habitTemplateId: str
    title: str
    description: Optional[str]
    status: TaskStatus


@dataclass
class LessonTask:
    taskId: str
    type: TaskType
    lessonTemplateId: str
    title: str
    summary: Optional[str]
    status: TaskStatus


@dataclass
class JournalTask:
    taskId: str
    type: TaskType
    title: str
    description: Optional[str]
    status: TaskStatus


Task = HabitTask | LessonTask | JournalTask


def _deterministic_task_id(namespace: str, user_id: str, on_date: date, ttype: str, entity_id: str) -> str:
    return f"{namespace}:{user_id}:{on_date.isoformat()}:{ttype}:{entity_id}"


async def plan_daily_tasks(user_id: str, on_date: date, repo: HabitsReadRepository) -> List[Task]:
    tasks: List[Task] = []
    assignments = await repo.get_active_assignments(user_id)

    for assignment in assignments:
        steps: List[ProgramStepTemplate] = await repo.get_program_steps(str(assignment.program_template_id))
        if not steps:
            continue

        # Compute day offset
        day_offset = (on_date - assignment.start_date).days
        if day_offset < 0:
            continue

        # Map into step/dayIndex
        cursor = 0
        active_step: Optional[ProgramStepTemplate] = None
        day_index = 0
        for step in steps:
            if day_offset < cursor + step.duration_days:
                active_step = step
                day_index = day_offset - cursor
                break
            cursor += step.duration_days
        if active_step is None:
            continue

        # Habit card
        habit = await repo.get_habit_template(str(active_step.habit_template_id))
        if habit:
            ev = await repo.find_habit_event(user_id, str(habit.id), on_date)
            status: TaskStatus = TaskStatus.completed if ev and ev.response == "yes" else TaskStatus.pending
            tasks.append(
                HabitTask(
                    taskId=_deterministic_task_id("habits", user_id, on_date, "habit", str(habit.id)),
                    type=TaskType.habit,
                    habitTemplateId=str(habit.id),
                    title=habit.title,
                    description=habit.short_description,
                    status=status,
                )
            )

        # Lessons for the day
        step_lessons = await repo.get_step_lessons_for_day(str(active_step.id), day_index)
        lesson_ids = [str(sl.lesson_template_id) for sl in step_lessons]
        lessons = await repo.get_lesson_templates(lesson_ids)
        if lessons:
            # For simplicity, consider lesson completed if a 'completed' event exists; else pending
            lesson_events = await repo.find_lesson_events(user_id, [str(l.id) for l in lessons], on_date)
            completed_ids = {str(le.lesson_template_id) for le in lesson_events if le.event_type == "completed"}
            for lesson in lessons:
                status = TaskStatus.completed if str(lesson.id) in completed_ids else TaskStatus.pending
                summary = lesson.summary or None
                tasks.append(
                    LessonTask(
                        taskId=_deterministic_task_id("habits", user_id, on_date, "lesson", str(lesson.id)),
                        type=TaskType.lesson,
                        lessonTemplateId=str(lesson.id),
                        title=lesson.title,
                        summary=summary,
                        status=status,
                    )
                )

    # Always include journal card (configurable later)
    tasks.append(
        JournalTask(
            taskId=_deterministic_task_id("habits", user_id, on_date, "journal", "daily"),
            type=TaskType.journal,
            title="Daily Journal",
            description="Reflect or free-write.",
            status=TaskStatus.pending,
        )
    )

    return tasks
