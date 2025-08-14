import { ApolloLink, Observable, Operation, FetchResult, NextLink } from '@apollo/client'

function isTodaysTasksOp(operation: Operation): boolean {
  if (operation.operationName === 'TodaysTasks') return true
  const src = operation.query && (operation.query.loc as any)?.source?.body
  return typeof src === 'string' && src.includes('todaysTasks')
}

export function createMockLink(): ApolloLink {
  return new ApolloLink((operation: Operation, forward?: NextLink) => {
    if (isTodaysTasksOp(operation)) {
      const src = (operation.query && (operation.query.loc as any)?.source?.body) || ''
      // Debug log for intercepted operation
      // eslint-disable-next-line no-console
      console.log('[mockLink] Intercepting TodaysTasks', {
        operationName: operation.operationName,
        variables: operation.variables,
        hasQueryText: Boolean(src),
      })
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
        // eslint-disable-next-line no-console
        console.log('[mockLink] Responding with mocked todaysTasks', data)
        observer.next({ data })
        observer.complete()
      })
    }

    // Mock lesson detail by id (in lesson detail screen we'll query markdown content later)
    if (((operation.query.loc as any)?.source?.body || '').includes('lessonTemplateById')) {
      const vars: any = operation.variables || {}
      const id = vars.id || 'lesson-1'
      const data = {
        lessonTemplateById: {
          id,
          slug: 'eat-slowly-why',
          title: 'Why Slowing Down Helps',
          summary: 'Learn how slowing down improves digestion.',
          markdownContent: '# Why Slowing Down Helps\n\nSlowing down your meals aids digestion by allowing **more thorough chewing** and better satiety signaling.\n\n## Key Points\n- Chew each bite 20-30 times\n- Put down your fork between bites\n- Take sips of water\n\n> “Nature does not hurry, yet everything is accomplished.” — Lao Tzu',
        },
      }
      return new Observable<FetchResult>((observer) => { observer.next({ data }); observer.complete() })
    }

    // Mock program templates (marketplace)
    if (operation.operationName === 'ListProgramTemplates' || ((operation.query.loc as any)?.source?.body || '').includes('programTemplates')) {
      const data = {
        programTemplates: [
          { id: 'prog-1', slug: 'unfck-your-eating', title: "Unf*ck Your Eating", description: "A 7-habit sequence to reset your relationship with food." },
          { id: 'prog-2', slug: 'sleep-better', title: "Sleep Better", description: "Habits to improve sleep hygiene over two weeks." },
        ],
      }
      return new Observable<FetchResult>((observer) => { observer.next({ data }); observer.complete() })
    }

    // Mock program by slug
    if (operation.operationName === 'ProgramTemplateBySlug' || ((operation.query.loc as any)?.source?.body || '').includes('programTemplateBySlug')) {
      const vars: any = operation.variables || {}
      const slug = vars.slug || 'unfck-your-eating'
      const data = {
        programTemplateBySlug: {
          id: slug === 'unfck-your-eating' ? 'prog-1' : 'prog-2',
          slug,
          title: slug === 'unfck-your-eating' ? 'Unf*ck Your Eating' : 'Sleep Better',
          description: slug === 'unfck-your-eating' ? 'A 7-habit sequence to reset your relationship with food.' : 'Habits to improve sleep hygiene over two weeks.',
        },
      }
      return new Observable<FetchResult>((observer) => { observer.next({ data }); observer.complete() })
    }

    // Mock program steps
    if (operation.operationName === 'ProgramTemplateSteps' || ((operation.query.loc as any)?.source?.body || '').includes('programTemplateSteps')) {
      const data = {
        programTemplateSteps: [
          { id: 'step-1', sequenceIndex: 0, durationDays: 7, habit: { id: 'habit-1', title: 'Eat Slowly', shortDescription: 'Take 20 minutes to finish a meal.' } },
          { id: 'step-2', sequenceIndex: 1, durationDays: 7, habit: { id: 'habit-2', title: 'Protein First', shortDescription: 'Start meals with protein for satiety.' } },
        ],
      }
      return new Observable<FetchResult>((observer) => { observer.next({ data }); observer.complete() })
    }

    // Fallback to next link (do not swallow non-matching ops)
    return forward ? forward(operation) : new Observable<FetchResult>((o) => o.complete())
  })
}

// Dev guard link: short-circuit specific mutations in mock mode
export function createDevGuardLink(): ApolloLink {
  return new ApolloLink((operation: Operation, forward?: NextLink) => {
    const name = operation.operationName || ''
    const body: string = ((operation.query && (operation.query.loc as any)?.source?.body) || '') as string
    const isMutation = body.includes('mutation')
    if (isMutation) {
      const respond = (field: string, value: any) =>
        new Observable<FetchResult>((observer) => {
          observer.next({ data: { [field]: value } })
          observer.complete()
        })
      if (name === 'RecordHabitResponse' || body.includes('recordHabitResponse')) {
        return respond('recordHabitResponse', true)
      }
      if (name === 'RecordLessonOpened' || body.includes('recordLessonOpened')) {
        return respond('recordLessonOpened', true)
      }
      if (name === 'MarkLessonCompleted' || body.includes('markLessonCompleted')) {
        return respond('markLessonCompleted', true)
      }
      if (name === 'RecordJournalAction' || body.includes('recordJournalAction')) {
        return respond('recordJournalAction', true)
      }
    }
    return forward ? forward(operation) : new Observable<FetchResult>((o) => o.complete())
  })
}


