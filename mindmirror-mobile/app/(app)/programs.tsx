import React, { useMemo, useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectInput, SelectItem, SelectPortal, SelectTrigger } from '@/components/ui/select'
import { AppBar } from '@/components/common/AppBar'
import { useQuery } from '@apollo/client'
import { useLocalSearchParams } from 'expo-router'
import { PROGRAM_ASSIGNMENTS, LIST_PROGRAM_TEMPLATES, RECENT_LESSON_COMPLETIONS } from '@/services/api/habits'
import { Pressable } from '@/components/ui/pressable'
import { useRouter } from 'expo-router'
import GlobalFab from '@/components/common/GlobalFab'
import { usePrograms as useWorkoutPrograms, useMyEnrollments } from '@/services/api/practices'
import { useAuth } from '@/features/auth/context/AuthContext'

export default function ProgramsAndResourcesScreen() {
  const router = useRouter()
  const params = useLocalSearchParams<{ reload?: string }>()
  const { data: assignments } = useQuery(PROGRAM_ASSIGNMENTS, { fetchPolicy: params?.reload === '1' ? 'network-only' : 'cache-and-network', variables: { status: 'active' } })
  const { data: templates } = useQuery(LIST_PROGRAM_TEMPLATES, { fetchPolicy: 'cache-and-network' })
  const { data: completedLessons } = useQuery(RECENT_LESSON_COMPLETIONS, { fetchPolicy: 'cache-and-network', variables: { limit: 50 } })
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<'habits' | 'lessons' | 'workouts'>('workouts')
  const { session } = useAuth()

  // Habits enrollments (web side)
  const enrolled = useMemo(() => {
    const as = assignments?.programAssignments || []
    const map = new Map<string, any>()
    for (const a of as) {
      const t = (templates?.programTemplates || []).find((p: any) => p.id === a.programTemplateId)
      if (t) map.set(t.id, t)
    }
    const arr = Array.from(map.values())
    return arr.filter((p: any) => p.title.toLowerCase().includes(search.toLowerCase()))
  }, [assignments?.programAssignments, templates?.programTemplates, search])

  // Workout enrollments (practices side)
  const workoutProgramsQ = useWorkoutPrograms()
  const myEnrollmentsQ = useMyEnrollments(session?.user?.id)
  const enrolledWorkouts = useMemo(() => {
    const enrolls = (myEnrollmentsQ.data?.enrollments || []).filter((e: any) => (e.status || '').toLowerCase() === 'active')
    const programs = workoutProgramsQ.data?.programs || []
    const set = new Map<string, any>()
    for (const e of enrolls) {
      const p = programs.find((x: any) => x.id_ === e.program_id)
      if (p?.id_) set.set(p.id_, p)
    }
    return Array.from(set.values()).filter((p: any) => (p.name || '').toLowerCase().includes(search.toLowerCase()))
  }, [myEnrollmentsQ.data?.enrollments, workoutProgramsQ.data?.programs, search])

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Programs & Resources" />
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">Your Programs</Text>
              <Text className="text-typography-600 dark:text-gray-300">Review enrolled programs and past resources</Text>
            </VStack>

            <VStack space="sm">
              <Input className="bg-background-50 dark:bg-background-100">
                <InputField placeholder="Search…" value={search} onChangeText={setSearch} />
              </Input>
              <VStack>
                <Text className="text-typography-600 dark:text-gray-300 mb-1">Category</Text>
                <Select selectedValue={category} onValueChange={(v: any) => setCategory(v)}>
                  <SelectTrigger variant="outline">
                    <SelectInput placeholder="Select category" />
                  </SelectTrigger>
                  <SelectPortal>
                    <SelectBackdrop />
                    <SelectContent>
                      <SelectDragIndicatorWrapper>
                        <SelectDragIndicator />
                      </SelectDragIndicatorWrapper>
                      <SelectItem label="Workouts" value="workouts" />
                      <SelectItem label="Habits" value="habits" />
                      <SelectItem label="Lessons" value="lessons" />
                    </SelectContent>
                  </SelectPortal>
                </Select>
              </VStack>
            </VStack>

            {category === 'workouts' ? (
              myEnrollmentsQ.loading || workoutProgramsQ.loading ? (
                <Text className="text-typography-600 dark:text-gray-300">Loading…</Text>
              ) : myEnrollmentsQ.error || workoutProgramsQ.error ? (
                <Text className="text-red-600 dark:text-red-400">Failed to load workout programs</Text>
              ) : enrolledWorkouts.length === 0 ? (
                <VStack space="md">
                  <Text className="text-typography-600 dark:text-gray-300">No workout programs enrolled yet.</Text>
                  <Pressable onPress={() => router.push('/marketplace?filter=workouts')} className="self-start px-3 py-1.5 rounded-md border border-indigo-300 bg-indigo-50">
                    <Text className="text-indigo-700 font-semibold">Browse workout programs</Text>
                  </Pressable>
                </VStack>
              ) : (
                <VStack space="md">
                  {enrolledWorkouts.map((p: any) => (
                    <Pressable key={p.id_} onPress={() => router.push(`/(app)/program/${p.id_}`)}>
                      <Box className="p-5 min-h-[120px] rounded-2xl border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800 shadow">
                        <VStack space="xs">
                          <Text className="text-lg font-semibold text-indigo-800 dark:text-indigo-200">{p.name}</Text>
                          {p.description ? (
                            <Text className="text-indigo-800/80 dark:text-indigo-300">{p.description}</Text>
                          ) : null}
                          <Text className="self-start px-3 py-1.5 rounded-full text-xs font-semibold bg-white border border-green-200 text-green-700 shadow-sm dark:bg-green-900 dark:border-green-700 dark:text-green-100">Enrolled</Text>
                        </VStack>
                      </Box>
                    </Pressable>
                  ))}
                </VStack>
              )
            ) : category === 'lessons' ? (
              <VStack space="md">
                {((completedLessons?.recentLessonCompletions as any[]) || []).length === 0 ? (
                  <Text className="text-typography-600 dark:text-gray-300">No completed lessons yet.</Text>
                ) : (
                  ((completedLessons?.recentLessonCompletions as any[]) || []).map((l: any) => (
                    <Box key={`${l.lessonTemplateId}-${l.completedAt}`} className="p-4 rounded-xl border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                      <VStack>
                        <Text className="text-base font-semibold text-typography-900 dark:text-white">{l.title}</Text>
                        {l.summary ? (
                          <Text className="text-typography-600 dark:text-gray-300">{l.summary}</Text>
                        ) : null}
                        <Text className="text-typography-500 dark:text-gray-400 mt-1">Completed {new Date(l.completedAt).toLocaleDateString()}</Text>
                      </VStack>
                    </Box>
                  ))
                )}
              </VStack>
            ) : enrolled.length === 0 ? (
              <Text className="text-typography-600 dark:text-gray-300">No programs enrolled.</Text>
            ) : (
              <VStack space="md">
                {enrolled.map((p: any) => (
                  <Pressable key={p.id} onPress={() => router.push(`/marketplace/${p.slug}?from=programs`)}>
                    <Box className="p-5 min-h-[120px] rounded-2xl border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800 shadow">
                      <VStack space="xs">
                        <Text className="text-lg font-semibold text-indigo-800 dark:text-indigo-200">{p.title}</Text>
                        {p.subtitle ? (
                          <Text className="text-indigo-800/80 dark:text-indigo-300">{p.subtitle}</Text>
                        ) : p.description ? (
                          <Text className="text-indigo-800/80 dark:text-indigo-300">{p.description}</Text>
                        ) : null}
                        <Text className="self-start px-3 py-1.5 rounded-full text-xs font-semibold bg-white border border-green-200 text-green-700 shadow-sm dark:bg-green-900 dark:border-green-700 dark:text-green-100">Enrolled</Text>
                      </VStack>
                    </Box>
                  </Pressable>
                ))}
              </VStack>
            )}
          </VStack>
        </ScrollView>
      </VStack>
      <GlobalFab />
    </SafeAreaView>
  )
}
