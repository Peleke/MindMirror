import React, { useMemo, useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Pressable } from '@/components/ui/pressable'
import { AppBar } from '@/components/common/AppBar'
import { useQuery } from '@apollo/client'
import { LIST_PROGRAM_TEMPLATES, PROGRAM_ASSIGNMENTS } from '@/services/api/habits'
import { useRouter } from 'expo-router'
import { usePrograms as useWorkoutPrograms } from '@/services/api/practices'
import { Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectInput, SelectItem, SelectPortal, SelectTrigger } from '@/components/ui/select'
import GlobalFab from '@/components/common/GlobalFab'
import { useFocusEffect } from '@react-navigation/native'

export default function MarketplaceScreen() {
  const router = useRouter()
  const { data, loading, error, refetch } = useQuery(LIST_PROGRAM_TEMPLATES, { fetchPolicy: 'cache-and-network' })
  const { data: assignmentsData, refetch: refetchAssignments } = useQuery(PROGRAM_ASSIGNMENTS, { fetchPolicy: 'cache-and-network' })
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<'habits' | 'workouts'>('habits')
  const workoutProgramsQ = useWorkoutPrograms()

  useFocusEffect(React.useCallback(() => {
    refetch().catch(() => {})
    refetchAssignments().catch(() => {})
    if (typeof workoutProgramsQ.refetch === 'function') { try { (workoutProgramsQ as any).refetch() } catch {} }
    return () => {}
  }, []))

  const programs = useMemo(() => {
    const rows: any[] = data?.programTemplates || []
    const filtered = rows.filter((p) => p.title.toLowerCase().includes(search.toLowerCase()))
    return filtered
  }, [data?.programTemplates, search])

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Marketplace" />
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">Browse Programs</Text>
              <Text className="text-typography-600 dark:text-gray-300">Find programs to enroll in</Text>
            </VStack>

            <VStack space="sm">
              <Input className="bg-background-50 dark:bg-background-100">
                <InputField placeholder="Search programs..." value={search} onChangeText={setSearch} />
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
                      <SelectItem label="Habits" value="habits" />
                      <SelectItem label="Workouts" value="workouts" />
                    </SelectContent>
                  </SelectPortal>
                </Select>
              </VStack>
            </VStack>

            {category === 'workouts' ? (
              (() => {
                const raw = (workoutProgramsQ.data?.programs || [])
                const map = new Map<string, any>()
                for (const p of raw) { if (p?.id_) map.set(p.id_, p) }
                const programs = Array.from(map.values()).filter((p: any) => (p.name || '').toLowerCase().includes(search.toLowerCase()))
                if (workoutProgramsQ.loading) return (<Text className="text-typography-600 dark:text-gray-300">Loading...</Text>)
                if (!programs.length) return (<Text className="text-typography-600 dark:text-gray-300">No programs found</Text>)
                return (
                  <VStack space="md">
                    <Pressable onPress={() => router.push('/program-create')} className="self-start px-3 py-1.5 rounded-md border border-indigo-300 bg-indigo-50">
                      <Text className="text-indigo-700 font-semibold">＋ Create Program</Text>
                    </Pressable>
                    {programs.map((p: any) => (
                      <Pressable key={p.id_} onPress={() => router.push(`/(app)/program/${p.id_}`)}>
                        <Box className="p-5 min-h-[120px] rounded-2xl border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800 shadow">
                          <VStack space="xs">
                            <Text className="text-lg font-semibold text-indigo-800 dark:text-indigo-200">{p.name}</Text>
                            {p.description ? (
                              <Text className="text-indigo-800/80 dark:text-indigo-300">{p.description}</Text>
                            ) : null}
                          </VStack>
                          <VStack className="mt-3" space="xs">
                            <Text className="self-start px-3 py-1.5 rounded-full text-xs font-semibold bg-white border border-indigo-200 text-indigo-700 shadow-sm dark:bg-indigo-900 dark:border-indigo-700 dark:text-indigo-100">Explore</Text>
                          </VStack>
                        </Box>
                      </Pressable>
                    ))}
                  </VStack>
                )
              })()
            ) : loading && !data ? (
              <Text className="text-typography-600 dark:text-gray-300">Loading...</Text>
            ) : error ? (
              <Text className="text-red-600 dark:text-red-400">Failed to load programs</Text>
            ) : programs.length === 0 ? (
              <Text className="text-typography-600 dark:text-gray-300">No programs found</Text>
            ) : (
              <VStack space="md">
                {programs.map((p: any) => {
                  const isEnrolled = (assignmentsData?.programAssignments || []).some((a: any) => a.programTemplateId === p.id && a.status === 'active')
                  return (
                    <Pressable key={p.id} onPress={() => router.push(`/marketplace/${p.slug}?from=marketplace`)}>
                      <Box className="p-5 min-h-[120px] rounded-2xl border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800 shadow">
                        <VStack space="xs">
                          <Text className="text-lg font-semibold text-indigo-800 dark:text-indigo-200">{p.title}</Text>
                          {p.subtitle ? (
                            <Text className="text-indigo-800/80 dark:text-indigo-300">{p.subtitle}</Text>
                          ) : p.description ? (
                            <Text className="text-indigo-800/80 dark:text-indigo-300">{p.description}</Text>
                          ) : null}
                        </VStack>
                        <VStack className="mt-3" space="xs">
                          {isEnrolled ? (
                            <Text className="self-start px-3 py-1.5 rounded-full text-xs font-semibold bg-white border border-green-200 text-green-700 shadow-sm dark:bg-green-900 dark:border-green-700 dark:text-green-100">Enrolled</Text>
                          ) : (
                            <Text className="self-start px-3 py-1.5 rounded-full text-xs font-semibold bg-white border border-indigo-200 text-indigo-700 shadow-sm dark:bg-indigo-900 dark:border-indigo-700 dark:text-indigo-100">Explore</Text>
                          )}
                        </VStack>
                      </Box>
                    </Pressable>
                  )
                })}
              </VStack>
            )}
          </VStack>
        </ScrollView>
      </VStack>
      <GlobalFab />
    </SafeAreaView>
  )
}


