from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from habits.app.db.repositories import HabitsReadRepository
from habits.app.db.tables import ProgramStepTemplate


from habits.app.graphql.schemas.task_types import TaskType, TaskStatus


@dataclass
class HabitTask:
    taskId: str
    type: TaskType
    habitTemplateId: str
    title: str
    description: Optional[str]
    subtitle: Optional[str]
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
    habitTemplateId: Optional[str] = None


Task = HabitTask | LessonTask | JournalTask


def _deterministic_task_id(namespace: str, user_id: str, on_date: date, ttype: str, entity_id: str) -> str:
    return f"{namespace}:{user_id}:{on_date.isoformat()}:{ttype}:{entity_id}"


def _strip_leading_headings_and_blank(markdown_text: Optional[str]) -> str:
    """Remove leading markdown heading lines (any level) and blank lines; return remaining content.

    This is used to create cleaner summaries for daily extracted segments so cards don't start with a heading.
    """
    if not markdown_text:
        return ""
    lines = markdown_text.split('\n')
    idx = 0
    # Skip leading headings and blank lines
    while idx < len(lines):
        raw = lines[idx]
        stripped = raw.lstrip()
        if not stripped:
            idx += 1
            continue
        if stripped.startswith('#'):
            idx += 1
            continue
        break
    # Also trim any subsequent blank lines after the heading block
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    return '\n'.join(lines[idx:]).lstrip()


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

        # Habit card (welcome-only steps may have no habit)
        habit = None
        if getattr(active_step, "habit_template_id", None):
            habit = await repo.get_habit_template(str(active_step.habit_template_id))
        if habit:
            # derive subtitle: daily plan variant overrides, else habit.short_description, else lesson subtitle/summary
            subtitle_text: Optional[str] = None
            daily_plan = await repo.get_step_daily_plan_for_day(str(active_step.id), day_index)
            if daily_plan and daily_plan.habit_variant_text:
                subtitle_text = daily_plan.habit_variant_text
            if not subtitle_text:
                subtitle_text = habit.short_description
            if not subtitle_text:
                # Fallback: use program description for a friendlier line when nothing else exists
                try:
                    steps_program = await repo.get_program_template_by_slug(None)  # placeholder to avoid lint; will replace
                except Exception:
                    steps_program = None
                # Fetch program by id (we don't have slug; use active_step.program_template_id via another repo method)
                try:
                    from habits.app.db.tables import ProgramTemplate
                    # simple lookup by id via existing session
                    program_id = str(active_step.program_template_id)
                    # reusing session in repo
                    from sqlalchemy import select
                    result = await repo.session.execute(select(ProgramTemplate).where(ProgramTemplate.id == program_id))
                    program_row = result.scalars().first()
                    if program_row and getattr(program_row, 'description', None):
                        subtitle_text = program_row.description
                except Exception:
                    pass
            if not subtitle_text:
                # Prefer today's lesson subtitle if available
                step_lessons_for_day = await repo.get_step_lessons_for_day(str(active_step.id), day_index)
                if step_lessons_for_day:
                    first_lesson_id = str(step_lessons_for_day[0].lesson_template_id)
                    lessons_for_sub = await repo.get_lesson_templates([first_lesson_id])
                    if lessons_for_sub:
                        l0 = lessons_for_sub[0]
                        subtitle_text = getattr(l0, "subtitle", None) or l0.summary or None
                # Fallback to the first mapped lesson of the step if today has none
                if not subtitle_text:
                    all_step_lessons = await repo.get_step_lessons(str(active_step.id))
                    if all_step_lessons:
                        first_any_id = str(all_step_lessons[0].lesson_template_id)
                        lessons_any = await repo.get_lesson_templates([first_any_id])
                        if lessons_any:
                            l0 = lessons_any[0]
                            subtitle_text = getattr(l0, "subtitle", None) or l0.summary or None

            ev = await repo.find_habit_event(user_id, str(habit.id), on_date)
            status: TaskStatus = TaskStatus.completed if ev and ev.response == "yes" else TaskStatus.pending
            tasks.append(
                HabitTask(
                    taskId=_deterministic_task_id("habits", user_id, on_date, "habit", str(habit.id)),
                    type=TaskType.habit,
                    habitTemplateId=str(habit.id),
                    title=habit.title,
                    description=habit.short_description,
                    subtitle=subtitle_text,
                    status=status,
                )
            )

        # Lessons for the day (segment-aware)
        # First check for explicit LessonTask records (created by practices_service integration)
        explicit_lesson_tasks = await repo.get_lesson_tasks_for_user_and_date(user_id, on_date)
        for lesson_task in explicit_lesson_tasks:
            lesson_template = await repo.get_lesson_template_by_id(str(lesson_task.lesson_template_id))
            if lesson_template:
                # Use segments if specified
                if lesson_task.segment_ids_json:
                    # Render specific segments
                    segments = await repo.list_lesson_segments_by_lesson(str(lesson_template.id))
                    from habits.app.services.lesson_render_service import LessonRenderService
                    from habits.app.services.lesson_loader import LessonLoader

                    segment_objects = LessonLoader.segments_from_json(LessonLoader.segments_to_json(segments))
                    if segment_objects:
                        rendered_content = LessonRenderService.render_segments(
                            lesson_template.markdown_content or "",
                            segment_objects,
                            lesson_task.segment_ids_json,
                            lesson_template.default_segment
                        )
                        clean = _strip_leading_headings_and_blank(rendered_content)
                        summary = (clean[:200] + ("…" if len(clean) > 200 else "")) or None
                    else:
                        summary = lesson_template.summary
                else:
                    summary = lesson_template.summary

                tasks.append(
                    LessonTask(
                        taskId=_deterministic_task_id("habits", user_id, on_date, "lesson", str(lesson_template.id)),
                        type=TaskType.lesson,
                        lessonTemplateId=str(lesson_template.id),
                        title=lesson_template.title,
                        summary=summary,
                        status=TaskStatus.pending,  # LessonTasks are always pending until completed
                    )
                )

        # If no explicit lesson tasks, fall back to program-based lessons
        if not explicit_lesson_tasks:
            if 'daily_plan' not in locals():
                daily_plan = await repo.get_step_daily_plan_for_day(str(active_step.id), day_index)
            segment_used = False
            if daily_plan and daily_plan.lesson_segment_id:
                seg = await repo.get_lesson_segment_by_id(str(daily_plan.lesson_segment_id))
                if seg:
                    # Use parent lesson id for identity; title/summary from segment
                    parent_id = str(seg.lesson_template_id)
                    status = TaskStatus.pending
                    # Fallback for summary when segment lacks one: derive from excerpt content
                    if seg.summary:
                        seg_summary = seg.summary
                    else:
                        clean_seg = _strip_leading_headings_and_blank(seg.markdown_content or "")
                        seg_summary = (clean_seg[:200] + ("…" if len(clean_seg) > 200 else ""))
                    tasks.append(
                        LessonTask(
                            taskId=_deterministic_task_id("habits", user_id, on_date, "lesson", parent_id),
                            type=TaskType.lesson,
                            lessonTemplateId=parent_id,
                            title=seg.title,
                            summary=seg_summary or None,
                            status=status,
                        )
                    )
                    segment_used = True
            if not segment_used:
                step_lessons = await repo.get_step_lessons_for_day(str(active_step.id), day_index)
                lesson_ids = [str(sl.lesson_template_id) for sl in step_lessons]
                lessons = await repo.get_lesson_templates(lesson_ids)
                if lessons:
                    # Consider lesson completed if a 'completed' event exists; else pending
                    lesson_events = await repo.find_lesson_events(user_id, [str(l.id) for l in lessons], on_date)
                    completed_ids = {str(le.lesson_template_id) for le in lesson_events if le.event_type == "completed"}
                    for lesson in lessons:
                        status = TaskStatus.completed if str(lesson.id) in completed_ids else TaskStatus.pending
                        # Fallback for summary when lesson lacks one: derive from lesson markdown
                        summary = lesson.summary or ((lesson.markdown_content or "")[:200] + ("…" if lesson.markdown_content and len(lesson.markdown_content) > 200 else "")) or None
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

        # Journal prompt from daily plan -> JournalTask
        if daily_plan and daily_plan.journal_prompt_text:
            tasks.append(
                JournalTask(
                    taskId=_deterministic_task_id("habits", user_id, on_date, "journal", str(active_step.id)),
                    type=TaskType.journal,
                    title="Daily Journal",
                    description=daily_plan.journal_prompt_text,
                    status=TaskStatus.pending,
                    habitTemplateId=str(habit.id) if habit else None,
                )
            )

    # JournalTask now optionally emitted via StepDailyPlan.journal_prompt_text

    return tasks
