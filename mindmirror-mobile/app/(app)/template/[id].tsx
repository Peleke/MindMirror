import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { ScrollView } from '@/components/ui/scroll-view'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { usePracticeTemplate } from '@/services/api/practices'

export default function TemplateDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const router = useRouter()
  const { data, loading } = usePracticeTemplate(id || '')
  const t = data?.practice_template

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title={t?.title || 'Template'} showBackButton onBackPress={() => router.back()} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {loading ? (
              <Text className="text-typography-600">Loading…</Text>
            ) : !t ? (
              <Text className="text-typography-600">Not found</Text>
            ) : (
              <>
                <VStack space="xs">
                  <Text className="text-2xl font-bold text-typography-900 dark:text-white">{t.title}</Text>
                  {t.description ? <Text className="text-typography-600 dark:text-gray-300">{t.description}</Text> : null}
                </VStack>

                <VStack space="md">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">Blocks</Text>
                  {(t.prescriptions || []).map((p: any, idx: number) => (
                    <VStack key={p.id_ || idx}>
                      <Text className="text-sm font-semibold text-typography-900 dark:text-white">{p.name || String(p.block).toUpperCase()}</Text>
                      <Box className="h-2" />
                      {(p.movements || []).map((m: any, mi: number) => (
                        <Box key={m.id_ || mi} className="p-4 rounded-xl border border-border-200 bg-background-50 dark:bg-background-100">
                          <VStack>
                            <VStack className="flex-row items-center justify-between">
                              <Text className="font-semibold text-typography-900 dark:text-white">{m.name}</Text>
                              <Text className="text-typography-600 dark:text-gray-300">{m.prescribed_sets || (m.sets?.length || 0)} sets</Text>
                            </VStack>
                            <Box className="h-2" />
                            <VStack>
                              <VStack className="flex-row px-3 py-2 rounded bg-background-100 border border-border-200">
                                <Box className="w-10"><Text className="text-xs font-semibold text-typography-600">#</Text></Box>
                                <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Reps/Dur</Text></Box>
                                <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Load</Text></Box>
                                <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Rest</Text></Box>
                              </VStack>
                              {(m.sets || []).map((s: any, si: number) => (
                                <VStack key={si}>
                                  <VStack className="flex-row items-center px-3 py-2 bg-white dark:bg-background-50">
                                    <Box className="w-10"><Text className="text-typography-700">{si + 1}</Text></Box>
                                    <Box className="flex-1"><Text className="text-typography-900">{s.reps ?? s.duration ?? '—'}</Text></Box>
                                    <Box className="flex-1"><Text className="text-typography-900">{s.load_value ?? '—'} {s.load_unit ?? ''}</Text></Box>
                                    <Box className="flex-1"><Text className="text-typography-900">{s.rest_duration ? `${s.rest_duration}s` : '—'}</Text></Box>
                                  </VStack>
                                  <Box className="h-px bg-border-200" />
                                </VStack>
                              ))}
                            </VStack>
                          </VStack>
                        </Box>
                      ))}
                    </VStack>
                  ))}
                </VStack>
              </>
            )}
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 