from __future__ import annotations

import enum
import strawberry
from typing import Optional


@strawberry.enum
class TaskType(enum.Enum):
    habit = "habit"
    lesson = "lesson"
    journal = "journal"


@strawberry.enum
class TaskStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    dismissed = "dismissed"


@strawberry.type
class HabitTask:
    taskId: str
    type: TaskType
    habitTemplateId: str
    title: str
    description: Optional[str]
    status: TaskStatus


@strawberry.type
class LessonTask:
    taskId: str
    type: TaskType
    lessonTemplateId: str
    title: str
    summary: Optional[str]
    status: TaskStatus


@strawberry.type
class JournalTask:
    taskId: str
    type: TaskType
    title: str
    description: Optional[str]
    status: TaskStatus


Task = strawberry.union("Task", (HabitTask, LessonTask, JournalTask))


