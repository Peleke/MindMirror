import { gql } from '@apollo/client'

// Shared fragment for Task union
export const TASK_FIELDS = gql`
  fragment TaskFields on Task {
    __typename
    ... on HabitTask {
      taskId
      type
      title
      description
      status
      habitTemplateId
    }
    ... on LessonTask {
      taskId
      type
      title
      summary
      status
      lessonTemplateId
    }
    ... on JournalTask {
      taskId
      type
      title
      description
      status
    }
  }
`

// 1) Daily tasks
export const GET_TODAYS_TASKS = gql`
  ${TASK_FIELDS}
  query TodaysTasks($onDate: Date!) {
    todaysTasks(onDate: $onDate) {
      ...TaskFields
    }
  }
`

// 2) Program discovery
export const LIST_PROGRAM_TEMPLATES = gql`
  query ListProgramTemplates {
    programTemplates {
      id
      slug
      title
      description
    }
  }
`

export const PROGRAM_TEMPLATE_BY_SLUG = gql`
  query ProgramTemplateBySlug($slug: String!) {
    programTemplateBySlug(slug: $slug) {
      id
      slug
      title
      description
    }
  }
`

// 3) User assignments
export const PROGRAM_ASSIGNMENTS = gql`
  query ProgramAssignments($status: String) {
    programAssignments(status: $status) {
      id
      userId
      programTemplateId
      status
      startDate
    }
  }
`

// 4) Mutations for task interactions
export const RECORD_HABIT_RESPONSE = gql`
  mutation RecordHabitResponse($habitTemplateId: String!, $onDate: Date!, $response: String!) {
    recordHabitResponse(habitTemplateId: $habitTemplateId, onDate: $onDate, response: $response)
  }
`

export const RECORD_LESSON_OPENED = gql`
  mutation RecordLessonOpened($lessonTemplateId: String!, $onDate: Date!) {
    recordLessonOpened(lessonTemplateId: $lessonTemplateId, onDate: $onDate)
  }
`

export const MARK_LESSON_COMPLETED = gql`
  mutation MarkLessonCompleted($lessonTemplateId: String!, $onDate: Date!) {
    markLessonCompleted(lessonTemplateId: $lessonTemplateId, onDate: $onDate)
  }
`

export const ASSIGN_PROGRAM_TO_USER = gql`
  mutation AssignProgramToUser($programId: String!, $startDate: Date!) {
    assignProgramToUser(programId: $programId, startDate: $startDate) {
      id
      userId
      programTemplateId
      status
    }
  }
`


// 5) Associated lessons for a habit (for current step/day)
export const LESSONS_FOR_HABIT = gql`
  query LessonsForHabit($habitTemplateId: String!, $onDate: Date!) {
    lessonsForHabit(habitTemplateId: $habitTemplateId, onDate: $onDate) {
      lessonTemplateId
      title
      summary
      completed
    }
  }
`

// 6) Program steps (mock for now; wire when backend exposes)
export const PROGRAM_STEPS = gql`
  query ProgramTemplateSteps($programId: String!) {
    programTemplateSteps(programId: $programId) {
      id
      sequenceIndex
      durationDays
      habit {
        id
        title
        shortDescription
      }
    }
  }
`


