import React, { useMemo, useState } from 'react'
import { ActivityIndicator } from 'react-native'
import { useQuery, useMutation, gql } from '@apollo/client'
import { Box } from '@/components/ui/box'
import { VStack } from '@/components/ui/vstack'
import { Text } from '@/components/ui/text'
import { HStack } from '@/components/ui/hstack'
import { Pressable } from '@/components/ui/pressable'
import { RECORD_HABIT_RESPONSE, RECORD_LESSON_OPENED, MARK_LESSON_COMPLETED } from '@/services/api/habits'
import { Task, HabitTask, LessonTask, JournalTask } from '@/types/habits'
import HabitCard from './cards/HabitCard'
import LessonCard from './cards/LessonCard'
import JournalCard from './cards/JournalCard'
import { useRouter } from 'expo-router'
import Constants from 'expo-constants'

function todayIsoDate(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default function DailyTasksList({ forceNetwork = false }: { forceNetwork?: boolean }) {
  const onDate = useMemo(() => todayIsoDate(), [])
  const router = useRouter()
  const mockEnabled = ((process.env.EXPO_PUBLIC_MOCK_TASKS || Constants.expoConfig?.extra?.mockTasks) || '').toString().toLowerCase() === 'true'

  const GET_TODAYS_TASKS_INLINE = gql`
    query TodaysTasksInline($onDate: Date!) {
      todaysTasks(onDate: $onDate) {
        __typename
        ... on HabitTask {
          taskId
          title
          description
          status
          habitTemplateId
        }
        ... on LessonTask {
          taskId
          title
          summary
          status
          lessonTemplateId
        }
        ... on JournalTask {
          taskId
          title
          description
          status
        }
      }
    }
  `

  const { data, loading, error, refetch } = useQuery(GET_TODAYS_TASKS_INLINE, {
    variables: { onDate },
    fetchPolicy: forceNetwork ? 'network-only' : 'cache-and-network',
    errorPolicy: 'none',
    returnPartialData: false,
  })

  const [recordHabitResponse] = useMutation(RECORD_HABIT_RESPONSE, {
    onCompleted: () => refetch(),
  })

  const [recordLessonOpened] = useMutation(RECORD_LESSON_OPENED)
  const [markLessonCompleted] = useMutation(MARK_LESSON_COMPLETED, {
    onCompleted: () => refetch(),
  })

  const tasks: Task[] = data?.todaysTasks ?? []
  const [activeTab, setActiveTab] = useState<'today' | 'completed'>('today')
  const remainingTasks = tasks.filter((t: any) => t.status !== 'completed')
  const completedTasks = tasks.filter((t: any) => t.status === 'completed')

  if (loading && !data) {
    return (
      <Box className="items-center py-8">
        <ActivityIndicator />
      </Box>
    )
  }

  if (error) {
    return (
      <Box className="items-center py-8">
        <Text className="text-red-600 dark:text-red-400">Failed to load tasks</Text>
      </Box>
    )
  }

  if (!tasks.length) {
    return (
      <Box className="items-center py-8">
        <Text className="text-typography-600 dark:text-gray-300">No tasks for today</Text>
      </Box>
    )
  }

  return (
    <VStack space="md">
      {/* Tabs */}
      <HStack className="w-full border-b border-border-200 dark:border-border-700" space="none">
        <Pressable
          className={`flex-1 py-2 border-b-2 ${activeTab==='today' ? 'border-primary-600' : 'border-transparent'}`}
          onPress={() => setActiveTab('today')}
        >
          <Text className={`text-center ${activeTab==='today' ? 'text-typography-900 dark:text-white' : 'text-typography-700 dark:text-gray-300'}`}>Today</Text>
        </Pressable>
        <Pressable
          className={`flex-1 py-2 border-l border-border-200 dark:border-border-700 border-b-2 ${activeTab==='completed' ? 'border-primary-600' : 'border-transparent'}`}
          onPress={() => setActiveTab('completed')}
        >
          <Text className={`text-center ${activeTab==='completed' ? 'text-typography-900 dark:text-white' : 'text-typography-700 dark:text-gray-300'}`}>Completed</Text>
        </Pressable>
      </HStack>

      {(activeTab==='today' ? remainingTasks : completedTasks).length === 0 ? (
        <Box className="items-center py-8">
          <Text className="text-typography-600 dark:text-gray-300">{activeTab==='today' ? 'No remaining tasks' : 'No completed tasks yet'}</Text>
        </Box>
      ) : null}

      {(activeTab==='today' ? remainingTasks : completedTasks).map((t) => {
        // eslint-disable-next-line no-console
        console.log('[DailyTasksList] task item', t)
        if (t.__typename === 'HabitTask') {
          const ht = t as HabitTask
          const title = ht.title || 'Habit'
          // eslint-disable-next-line no-console
          console.log('[DailyTasksList] HabitTask title/desc', ht.title, ht.description)
          return (
            <HabitCard
              key={ht.taskId}
              task={{ ...ht, title }}
              onRespond={async (response: 'yes' | 'no') => {
                if (!mockEnabled) {
                  await recordHabitResponse({ variables: { habitTemplateId: ht.habitTemplateId, onDate, response } })
                }
              }}
              onPress={() => {
                const desc = ht.description ?? ''
                router.push(`/habit/${ht.habitTemplateId}?title=${encodeURIComponent(title)}&description=${encodeURIComponent(desc)}&from=tasks`)
              }}
            />
          )
        }
        if (t.__typename === 'LessonTask') {
          const lt = t as LessonTask
          const title = lt.title || 'Lesson'
          // eslint-disable-next-line no-console
          console.log('[DailyTasksList] LessonTask title/summary', lt.title, lt.summary)
          return (
            <LessonCard
              key={lt.taskId}
              task={{ ...lt, title }}
              onOpen={async () => {
                if (!mockEnabled) {
                  await recordLessonOpened({ variables: { lessonTemplateId: lt.lessonTemplateId, onDate } })
                }
                const summary = lt.summary ?? ''
                router.push(`/lesson/${lt.lessonTemplateId}?title=${encodeURIComponent(title)}&summary=${encodeURIComponent(summary)}&from=tasks`)
              }}
              onComplete={async () => {
                await markLessonCompleted({ variables: { lessonTemplateId: lt.lessonTemplateId, onDate } })
              }}
            />
          )
        }
        const jt = t as JournalTask
        const title = jt.title || 'Daily Journal'
        const description = jt.description || 'Reflect or free-write.'
        return <JournalCard key={jt.taskId} task={{ ...jt, title, description }} />
      })}
    </VStack>
  )
}


