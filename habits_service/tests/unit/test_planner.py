from __future__ import annotations

import uuid
from datetime import date, timedelta
import pytest

from habits_service.habits_service.app.services.planner import plan_daily_tasks
from habits_service.habits_service.app.graphql.schemas.task_types import TaskType, TaskStatus


class StubRepo:
    def __init__(self):
        self.assignments = []
        self.steps_by_program = {}
        self.habits = {}
        self.step_lessons = {}
        self.lessons = {}
        self.habit_events = {}
        self.lesson_events = []

    async def get_active_assignments(self, user_id: str):
        return [a for a in self.assignments if a.user_id == user_id and a.status == "active"]

    async def get_program_steps(self, program_template_id: str):
        return self.steps_by_program.get(program_template_id, [])

    async def get_habit_template(self, habit_template_id: str):
        return self.habits.get(habit_template_id)

    async def get_step_lessons_for_day(self, step_id: str, day_index: int):
        return [sl for sl in self.step_lessons.get(step_id, []) if sl.day_index == day_index]

    async def get_lesson_templates(self, lesson_ids):
        return [self.lessons[_id] for _id in lesson_ids if _id in self.lessons]

    async def find_habit_event(self, user_id: str, habit_template_id: str, on_date: date):
        return self.habit_events.get((user_id, habit_template_id, on_date))

    async def find_lesson_events(self, user_id: str, lesson_ids, on_date: date):
        return [e for e in self.lesson_events if e.user_id == user_id and str(e.lesson_template_id) in lesson_ids and e.date == on_date]


class Obj:
    pass


def make_uuid():
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_plan_single_step_day0_includes_habit_and_journal():
    repo = StubRepo()

    # Program and step
    program_id = make_uuid()
    step = Obj(); step.id = make_uuid(); step.program_template_id = program_id; step.sequence_index = 0; step.habit_template_id = make_uuid(); step.duration_days = 7
    repo.steps_by_program[program_id] = [step]

    # Habit template
    habit = Obj(); habit.id = step.habit_template_id; habit.title = "Eat Slowly"; habit.short_description = "Chew thoroughly";
    repo.habits[str(habit.id)] = habit

    # Assignment
    assign = Obj(); assign.id = make_uuid(); assign.user_id = "u1"; assign.program_template_id = program_id; assign.start_date = date(2025, 8, 1); assign.status = "active"
    repo.assignments.append(assign)

    tasks = await plan_daily_tasks("u1", date(2025, 8, 1), repo)

    types = [t.type for t in tasks]
    assert TaskType.habit in types
    assert TaskType.journal in types
    ht = next(t for t in tasks if t.type == TaskType.habit)
    assert ht.title == "Eat Slowly"
    assert ht.status == TaskStatus.pending


@pytest.mark.asyncio
async def test_plan_lesson_on_specific_day():
    repo = StubRepo()
    program_id = make_uuid()
    step = Obj(); step.id = make_uuid(); step.program_template_id = program_id; step.sequence_index = 0; step.habit_template_id = make_uuid(); step.duration_days = 7
    repo.steps_by_program[program_id] = [step]

    habit = Obj(); habit.id = step.habit_template_id; habit.title = "Mindful Eating"; habit.short_description = None
    repo.habits[str(habit.id)] = habit

    # Lesson mapping on day 2
    lesson_id = make_uuid()
    sl = Obj(); sl.id = make_uuid(); sl.program_step_template_id = step.id; sl.day_index = 2; sl.lesson_template_id = lesson_id
    repo.step_lessons[step.id] = [sl]
    lesson = Obj(); lesson.id = lesson_id; lesson.title = "Why slow eating?"; lesson.summary = "Slow eating helps digestion."
    repo.lessons[lesson_id] = lesson

    assign = Obj(); assign.id = make_uuid(); assign.user_id = "u1"; assign.program_template_id = program_id; assign.start_date = date(2025, 8, 1); assign.status = "active"
    repo.assignments.append(assign)

    # Day 3 (offset 2) should include lesson
    tasks = await plan_daily_tasks("u1", date(2025, 8, 3), repo)
    types = [t.type for t in tasks]
    assert TaskType.lesson in types
    lt = next(t for t in tasks if t.type == TaskType.lesson)
    assert lt.title == "Why slow eating?"
    assert lt.status == TaskStatus.pending


@pytest.mark.asyncio
async def test_habit_yes_marks_completed():
    repo = StubRepo()
    program_id = make_uuid()
    step = Obj(); step.id = make_uuid(); step.program_template_id = program_id; step.sequence_index = 0; step.habit_template_id = make_uuid(); step.duration_days = 7
    repo.steps_by_program[program_id] = [step]

    habit = Obj(); habit.id = step.habit_template_id; habit.title = "Hydrate"; habit.short_description = None
    repo.habits[str(habit.id)] = habit

    assign = Obj(); assign.id = make_uuid(); assign.user_id = "u1"; assign.program_template_id = program_id; assign.start_date = date(2025, 8, 1); assign.status = "active"
    repo.assignments.append(assign)

    # Habit event yes on day 1
    ev = Obj(); ev.user_id = "u1"; ev.habit_template_id = str(habit.id); ev.date = date(2025, 8, 1); ev.response = "yes"
    repo.habit_events[("u1", str(habit.id), date(2025, 8, 1))] = ev

    tasks = await plan_daily_tasks("u1", date(2025, 8, 1), repo)
    ht = next(t for t in tasks if t.type == TaskType.habit)
    assert ht.status == TaskStatus.completed


