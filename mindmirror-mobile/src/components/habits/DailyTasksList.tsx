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
import WorkoutCard from './cards/WorkoutCard'
import { useRouter } from 'expo-router'
import Constants from 'expo-constants'
import { useAuth } from '@/features/auth/context/AuthContext'
import { useTodaysWorkouts, useMyUpcomingPractices, useDeferPractice, QUERY_PRACTICE_INSTANCE, QUERY_MY_UPCOMING_PRACTICES, QUERY_TODAYS_WORKOUTS } from '@/services/api/practices'
import { useApolloClient } from '@apollo/client'
import dayjs from 'dayjs'
import LottieView from 'lottie-react-native'

function todayIsoDate(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default function DailyTasksList({ forceNetwork = false, onDate: onDateProp, onAfterHabitResponse }: { forceNetwork?: boolean, onDate?: string, onAfterHabitResponse?: () => void }) {
  const onDate = useMemo(() => onDateProp || todayIsoDate(), [onDateProp])
  const router = useRouter()
  const mockEnabled = ((process.env.EXPO_PUBLIC_MOCK_TASKS || Constants.expoConfig?.extra?.mockTasks) || '').toString().toLowerCase() === 'true'
  const { session, loading: authLoading } = useAuth()
  const hasSession = !!session?.access_token
  const [showConfetti, setShowConfetti] = useState(false)
  const [prevRemainingCount, setPrevRemainingCount] = useState<number | null>(null)
  const isToday = useMemo(() => onDate === todayIsoDate(), [onDate])

  const GET_TODAYS_TASKS_INLINE = gql`
    query TodaysTasksInline($onDate: Date!) {
      todaysTasks(onDate: $onDate) {
        __typename
        ... on HabitTask {
          taskId
          title
          description
          subtitle
          status
          habitTemplateId
          # prefer to pass subtitle for UI
          # this requires backend to include it on HabitTask; temporarily omitted
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
    skip: authLoading || !hasSession,
  })

  const [recordHabitResponse] = useMutation(RECORD_HABIT_RESPONSE, {
    onCompleted: async () => {
      await refetch()
      if (onAfterHabitResponse) onAfterHabitResponse()
    },
  })

  const [recordLessonOpened] = useMutation(RECORD_LESSON_OPENED)
  const [markLessonCompleted] = useMutation(MARK_LESSON_COMPLETED, {
    onCompleted: () => refetch(),
  })

  const tasks: Task[] = data?.todaysTasks ?? []
  const [activeTab, setActiveTab] = useState<'today' | 'completed'>('today')
  const remainingTasks = tasks.filter((t: any) => t.status !== 'completed')
  const completedTasks = tasks.filter((t: any) => t.status === 'completed')

  // Confetti trigger: only for Today, only on the current day, and only when count transitions >0 -> 0
  React.useEffect(() => {
    // Only evaluate when data is settled and visible for Today on the current day
    if (!isToday || activeTab !== 'today' || loading || authLoading) return
    const current = remainingTasks.length
    const total = tasks.length
    // Ignore empty state while query is still filling in
    if (total === 0) return
    if (prevRemainingCount !== null && prevRemainingCount > 0 && current === 0) {
      setShowConfetti(true)
    }
    setPrevRemainingCount(current)
  }, [isToday, activeTab, loading, authLoading, remainingTasks.length, tasks.length])

  // Reset confetti state when changing date
  React.useEffect(() => { setShowConfetti(false); setPrevRemainingCount(null) }, [onDate])

  // Completed Workouts (from Practices)
  const { data: workoutsData } = useTodaysWorkouts(onDate)
  const completedWorkouts = (workoutsData?.todaysWorkouts || []).filter((w: any) => !!w.completedAt)

  // Get workout data for integration
  const { data: upcomingData } = useMyUpcomingPractices()
  const [deferPractice] = useDeferPractice()
  const apollo = useApolloClient()
  
  // Create workout tasks from scheduled practices and actual instances
  const todaysUpcoming = (upcomingData?.my_upcoming_practices || []).filter((sp: any) => 
    dayjs(sp.scheduled_date).format('YYYY-MM-DD') === onDate && !!sp.practice_instance_id
  )
  const todaysWorkoutsMap: Record<string, any> = {}
  for (const w of (workoutsData?.todaysWorkouts || [])) { 
    todaysWorkoutsMap[w.id_] = w 
  }
  
  const workoutTasks = (
    (workoutsData?.todaysWorkouts || []).map((w: any) => ({
      __typename: 'WorkoutTask',
      taskId: w.id_,
      id_: w.id_,
      name: w.title || 'Workout',
      description: w.description || '',
      level: w.level,
      date: w.date,
      completed: !!w.completedAt,
      practice_instance_id: w.id_,
      status: w.completedAt ? 'completed' : 'pending'
    }))
  )

  // Combine all tasks
  const allTasks = [...tasks, ...workoutTasks]
  const allRemainingTasks = allTasks.filter((t: any) => t.status !== 'completed')
  const allCompletedTasks = allTasks.filter((t: any) => t.status === 'completed')

  if ((authLoading || loading) && !data) {
    return (
      <Box className="items-center py-8" style={{ minHeight: 200, justifyContent: 'center' }}>
        <LottieView
          autoPlay
          loop
          source={require('../../../assets/lottie/loading.lottie')}
          style={{ width: 110, height: 110, transform: [{ translateY: -20 }] }}
        />
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

  if (!allTasks.length) {
    return (
      <VStack space="md">
        {/* Tabs placeholder to keep layout consistent */}
        <HStack className="w-full border-b border-border-200 dark:border-border-700">
          <Pressable className="flex-1 py-2 border-b-2 border-primary-600">
            <Text className="text-center text-typography-900 dark:text-white">Today</Text>
          </Pressable>
          <Pressable className="flex-1 py-2 border-l border-border-200 dark:border-border-700 border-b-2 border-transparent">
            <Text className="text-center text-typography-700 dark:text-gray-300">Completed</Text>
          </Pressable>
        </HStack>
        <Box className="items-center py-8">
          <Text className="text-typography-600 dark:text-gray-300 mb-3">No tasks today. Why not explore the Marketplace?</Text>
          <Pressable onPress={() => router.replace('/marketplace')}>
            <Box className="px-3 py-1.5 rounded-md bg-indigo-50 dark:bg-gray-800 border border-indigo-300 dark:border-gray-600 shadow-sm">
              <Text className="text-xs font-semibold text-indigo-900 dark:text-gray-100 text-center">
                Explore Marketplace
              </Text>
            </Box>
          </Pressable>
        </Box>
      </VStack>
    )
  }

  return (
    <VStack space="md">
      {showConfetti && (
        <Box className="absolute inset-0 items-center justify-center" style={{ zIndex: 10 }}>
          <LottieView
            autoPlay
            loop={false}
            source={require('../../../assets/lottie/confetti.lottie')}
            style={{ width: 260, height: 260 }}
            onAnimationFinish={() => setShowConfetti(false)}
          />
        </Box>
      )}
      {/* Tabs */}
      <HStack className="w-full border-b border-border-200 dark:border-border-700">
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

      {(activeTab==='today' ? allRemainingTasks : allCompletedTasks).length === 0 ? (
        <Box className="items-center py-8">
          {activeTab==='today' ? (
            <Text className="text-typography-600 dark:text-gray-300">✨ Wow, you nailed everything!</Text>
          ) : (
            <Text className="text-typography-600 dark:text-gray-300">No completed tasks yet</Text>
          )}
        </Box>
      ) : null}

      {(activeTab==='today' ? allRemainingTasks : allCompletedTasks).map((t) => {
        // eslint-disable-next-line no-console
        console.log('[DailyTasksList] task item', t)
        if (t.__typename === 'HabitTask') {
          const ht = t as HabitTask
          const title = ht.title || 'Habit'
          const subtitle = (ht as any).subtitle || ''
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
                router.push(`/lesson/${lt.lessonTemplateId}?title=${encodeURIComponent(title)}&summary=${encodeURIComponent(summary)}&from=tasks&onDate=${encodeURIComponent(onDate)}`)
              }}
              onComplete={async () => {
                await markLessonCompleted({ variables: { lessonTemplateId: lt.lessonTemplateId, onDate } })
              }}
            />
          )
        }
        if (t.__typename === 'WorkoutTask') {
          const wt = t as any // Assuming WorkoutTask is a custom type or has specific fields
          const title = wt.name || 'Workout'
          const description = wt.description || ''
          const level = wt.level || 'Beginner'
          const date = wt.date || onDate
          const completed = wt.completed
          const status = wt.status || 'pending'

          return (
            <WorkoutCard
              key={wt.taskId}
              task={{ ...wt, name: title, description, level, date, completed }}
              onPress={async () => {
                const wid = wt.practice_instance_id || wt.id_
                try {
                  const res = await apollo.query({ query: QUERY_PRACTICE_INSTANCE, variables: { id: wid }, fetchPolicy: 'network-only' })
                  const exists = !!res?.data?.practiceInstance?.id_
                  if (exists) {
                    router.push(`/(app)/workout/${wid}`)
                  } else {
                    await apollo.refetchQueries({ include: [QUERY_TODAYS_WORKOUTS, QUERY_MY_UPCOMING_PRACTICES] })
                  }
                } catch {
                  try { await apollo.refetchQueries({ include: [QUERY_TODAYS_WORKOUTS, QUERY_MY_UPCOMING_PRACTICES] }) } catch {}
                }
              }}
              onDefer={wt.enrollment_id ? (async () => { try { await deferPractice({ variables: { enrollmentId: wt.enrollment_id, mode: 'push' } }); await apollo.refetchQueries({ include: [QUERY_TODAYS_WORKOUTS, QUERY_MY_UPCOMING_PRACTICES] }) } catch {} }) : (() => {})}
            />
          )
        }
        const jt = t as JournalTask
        const title = jt.title || 'Daily Journal'
        const description = jt.description || 'Reflect or free-write.'
        return <JournalCard key={jt.taskId} task={{ ...jt, title, description }} />
      })}

      {/* Completed Workouts card(s) under Completed tab */}
      {activeTab === 'completed' && completedWorkouts.length > 0 && (
        <VStack space="sm">
          {completedWorkouts.map((w: any) => (
            <Pressable key={w.id_} onPress={() => router.push(`/(app)/workout/${w.id_}`)}>
              <Box className="p-4 rounded-lg bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800">
                <HStack className="items-center justify-between">
                  <Text className="font-semibold text-green-800 dark:text-green-200">Completed Workout</Text>
                  <Text className="text-green-700 dark:text-green-300">{w.title || 'Workout'}</Text>
                </HStack>
                <Text className="text-typography-600 dark:text-gray-300 mt-1">{w.date}</Text>
              </Box>
            </Pressable>
          ))}
        </VStack>
      )}
    </VStack>
  )
}


