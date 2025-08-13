export type TaskType = 'habit' | 'lesson' | 'journal'

export type TaskStatus = 'pending' | 'completed' | 'dismissed'

export interface BaseTask {
  taskId: string
  type: TaskType
  status: TaskStatus
  title: string
}

export interface HabitTask extends BaseTask {
  type: 'habit'
  habitTemplateId: string
  description?: string | null
}

export interface LessonTask extends BaseTask {
  type: 'lesson'
  lessonTemplateId: string
  summary?: string | null
}

export interface JournalTask extends BaseTask {
  type: 'journal'
  description?: string | null
}

export type Task = HabitTask | LessonTask | JournalTask

export interface ProgramTemplate {
  id: string
  slug: string
  title: string
  description?: string | null
}

export interface ProgramAssignment {
  id: string
  userId: string
  programTemplateId: string
  status: string
  startDate: string // ISO date
}


