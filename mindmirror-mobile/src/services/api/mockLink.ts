import { ApolloLink, Observable, Operation, FetchResult, NextLink } from '@apollo/client'

function isTodaysTasksOp(operation: Operation): boolean {
  return operation.operationName === 'TodaysTasks'
}

export function createMockLink(): ApolloLink {
  return new ApolloLink((operation: Operation, forward?: NextLink) => {
    if (isTodaysTasksOp(operation)) {
      return new Observable<FetchResult>((observer) => {
        // Minimal, accurate Task union shape
        const data = {
          todaysTasks: [
            {
              __typename: 'HabitTask',
              taskId: 'habits:mock-user:2025-08-13:habit:habit-1',
              type: 'habit',
              habitTemplateId: 'habit-1',
              title: 'Eat Slowly',
              description: 'Take 20 minutes to finish a meal.',
              status: 'pending',
            },
            {
              __typename: 'LessonTask',
              taskId: 'habits:mock-user:2025-08-13:lesson:lesson-1',
              type: 'lesson',
              lessonTemplateId: 'lesson-1',
              title: 'Why Slowing Down Helps',
              summary: 'Learn how slowing down improves digestion.',
              status: 'pending',
            },
            {
              __typename: 'JournalTask',
              taskId: 'habits:mock-user:2025-08-13:journal:daily',
              type: 'journal',
              title: 'Daily Journal',
              description: 'Reflect or free-write.',
              status: 'pending',
            },
          ],
        }
        observer.next({ data })
        observer.complete()
      })
    }

    // Fallback to next link (do not swallow non-matching ops)
    return forward ? forward(operation) : new Observable<FetchResult>((o) => o.complete())
  })
}


