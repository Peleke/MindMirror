import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Pressable } from '@/components/ui/pressable'
import { ScrollView } from '@/components/ui/scroll-view'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { useProgram, useDeleteProgram } from '@/services/api/practices'
import GlobalFab from '@/components/common/GlobalFab'

export default function ProgramDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const router = useRouter()
  const { data, loading } = useProgram(id || '')
  const [deleteProgram] = useDeleteProgram()
  const p = data?.program

  const onDelete = async () => {
    try {
      await deleteProgram({ variables: { id } })
      router.back()
    } catch {}
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title={p?.name || 'Program'} showBackButton onBackPress={() => router.back()} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {loading ? (
              <Text className="text-typography-600">Loading…</Text>
            ) : !p ? (
              <Text className="text-typography-600">Not found</Text>
            ) : (
              <>
                <VStack space="xs">
                  <Text className="text-2xl font-bold text-typography-900 dark:text-white">{p.name}</Text>
                  {p.description ? <Text className="text-typography-600 dark:text-gray-300">{p.description}</Text> : null}
                </VStack>

                <VStack space="sm">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">Sequence</Text>
                  {(p.practice_links || []).length === 0 ? (
                    <Text className="text-typography-600 dark:text-gray-300">No workouts added</Text>
                  ) : (
                    (p.practice_links || []).map((l: any, i: number) => (
                      <Pressable key={i} onPress={() => router.push(`/(app)/template/${l.practice_template?.id_}`)}>
                        <Box className="p-4 rounded-xl border border-border-200 bg-background-50 dark:bg-background-100">
                          <VStack>
                            <Text className="font-semibold text-typography-900 dark:text-white">{i + 1}. {l.practice_template?.title || 'Workout'}</Text>
                            <Text className="text-typography-600 dark:text-gray-300">Rest days after: {l.interval_days_after}</Text>
                          </VStack>
                        </Box>
                      </Pressable>
                    ))
                  )}
                </VStack>

                <Pressable onPress={onDelete} className="self-start px-3 py-1.5 rounded-md border border-red-300">
                  <Text className="text-red-700 font-semibold">Delete Program</Text>
                </Pressable>
              </>
            )}
          </VStack>
        </ScrollView>
      </VStack>
      <GlobalFab onPress={() => router.push('/(app)/workout-create')} />
    </SafeAreaView>
  )
} 