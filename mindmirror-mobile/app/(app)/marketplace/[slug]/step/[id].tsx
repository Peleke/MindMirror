import React, { useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { AppBar } from '@/components/common/AppBar'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { Tabs, TabsBar, TabsTab, TabsContent } from '@/components/common/Tabs'
import { useQuery, gql } from '@apollo/client'
import { Pressable } from '@/components/ui/pressable'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { CheckCircle, Circle } from 'lucide-react-native'
import { LESSONS_FOR_HABIT } from '@/services/api/habits'

const STEP_QUERY = gql`
  query StepById($programId: String!) {
    programTemplateSteps(programId: $programId) {
      id
      sequenceIndex
      durationDays
      habit { id title shortDescription }
    }
  }
`

const STEP_LESSONS = gql`
  query StepLessons($programStepId: String!) {
    programStepLessons(programStepId: $programStepId) {
      dayIndex
      lessonTemplateId
      title
      summary
      estReadMinutes
    }
  }
`

const JOURNAL_ENTRIES_FOR_HABIT = gql`
  query JournalEntriesForHabit($habitTemplateId: UUID!, $limit: Int, $offset: Int) {
    journalEntriesForHabit(habitTemplateId: $habitTemplateId, limit: $limit, offset: $offset) {
      __typename
      ... on FreeformJournalEntry { id createdAt payload }
      ... on GratitudeJournalEntry { id createdAt payload { gratefulFor excitedAbout focus affirmation mood } }
      ... on ReflectionJournalEntry { id createdAt payload { wins improvements mood } }
    }
  }
`

export default function ProgramStepDetailScreen() {
  const params = useLocalSearchParams<{ slug: string; id: string; programId?: string; habitId?: string }>()
  const router = useRouter()
  const programId = String(params.programId || '')
  const { data } = useQuery(STEP_QUERY, { variables: { programId }, skip: !programId })
  const step = (data?.programTemplateSteps || []).find((s: any) => String(s.id) === String(params.id))
  const habitId = String(params.habitId || step?.habit?.id || '')
  const { data: lessonsData } = useQuery(STEP_LESSONS, { variables: { programStepId: String(params.id) }, skip: !params.id })
  const today = new Date().toISOString().slice(0, 10)
  const { data: todayLessonsData } = useQuery(LESSONS_FOR_HABIT, { variables: { habitTemplateId: habitId, onDate: today }, skip: !habitId })
  const { data: entriesData } = useQuery(JOURNAL_ENTRIES_FOR_HABIT, { variables: { habitTemplateId: habitId, limit: 10, offset: 0 }, skip: !habitId })
  const [tab, setTab] = useState<'detail' | 'stats'>('detail')
  const completedIds = new Set<string>(((todayLessonsData?.lessonsForHabit as any[]) || []).filter((x: any) => x.completed).map((x: any) => x.lessonTemplateId))

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar
          title={step ? (step.habit?.title || 'Step') : 'Step'}
          showBackButton
          onBackPress={() => {
            try {
              router.back()
            } catch {
              router.replace(`/marketplace/${params.slug}`)
            }
          }}
        />
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            <Tabs>
              <TabsBar>
                <TabsTab active={tab==='detail'} onPress={() => setTab('detail')}>Detail</TabsTab>
                <TabsTab active={tab==='stats'} onPress={() => setTab('stats')}>Stats</TabsTab>
              </TabsBar>
              <TabsContent hidden={tab!=='detail'}>
                <VStack space="sm">
                  <Text className="text-xl font-bold text-typography-900 dark:text-white">{step?.habit?.title || 'Habit'}</Text>
                  {step?.habit?.shortDescription ? (
                    <Text className="text-typography-600 dark:text-gray-300">{step.habit.shortDescription}</Text>
                  ) : null}
                  <Box className="h-px bg-border-200 dark:bg-border-700" />
                  <VStack space="sm">
                    <Text className="text-base font-semibold text-typography-900 dark:text-white">Lessons</Text>
                    {((lessonsData?.programStepLessons as any[]) || []).length === 0 ? (
                      <Text className="text-typography-600 dark:text-gray-300">No lessons mapped.</Text>
                    ) : (
                      ((lessonsData?.programStepLessons as any[]) || []).map((l: any) => (
                        <Pressable
                          key={`${l.lessonTemplateId}-${l.dayIndex}`}
                          onPress={() => router.push(`/lesson/${l.lessonTemplateId}?title=${encodeURIComponent(l.title)}&summary=${encodeURIComponent(l.summary || '')}&from=step`)}
                        >
                          <HStack className="p-3 rounded-lg border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700 items-center justify-between">
                            <VStack className="flex-1" space="xs">
                              <Text className="text-sm font-semibold text-typography-900 dark:text-white">Day {l.dayIndex + 1}: {l.title}</Text>
                              {l.summary ? (
                                <Text className="text-typography-600 dark:text-gray-300">{l.summary}</Text>
                              ) : null}
                            </VStack>
                            <Icon as={completedIds.has(l.lessonTemplateId) ? CheckCircle : Circle} size="md" className={`${completedIds.has(l.lessonTemplateId) ? 'text-green-600' : 'text-gray-400'}`} />
                          </HStack>
                        </Pressable>
                      ))
                    )}
                  </VStack>
                  <Box className="h-px bg-border-200 dark:bg-border-700" />
                  <VStack space="sm">
                    <Text className="text-base font-semibold text-typography-900 dark:text-white">Linked Journal Entries</Text>
                    {((entriesData?.journalEntriesForHabit as any[]) || []).length === 0 ? (
                      <Text className="text-typography-600 dark:text-gray-300">No linked entries yet.</Text>
                    ) : (
                      ((entriesData?.journalEntriesForHabit as any[]) || []).map((e: any) => (
                        <Box key={e.id} className="p-3 rounded-lg border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                          <Text className="text-sm font-semibold text-typography-900 dark:text-white">{new Date(e.createdAt).toLocaleDateString()}</Text>
                          {e.__typename === 'FreeformJournalEntry' ? (
                            <Text className="text-typography-600 dark:text-gray-300">{e.payload}</Text>
                          ) : e.__typename === 'GratitudeJournalEntry' ? (
                            <Text className="text-typography-600 dark:text-gray-300">Gratitude entry</Text>
                          ) : (
                            <Text className="text-typography-600 dark:text-gray-300">Reflection entry</Text>
                          )}
                        </Box>
                      ))
                    )}
                  </VStack>
                </VStack>
              </TabsContent>
              <TabsContent hidden={tab!=='stats'}>
                <Text className="text-typography-700 dark:text-gray-300">Adherence, streaks, and counts will display here.</Text>
              </TabsContent>
            </Tabs>
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


