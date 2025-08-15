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
import { PROGRAM_ASSIGNMENTS, LIST_PROGRAM_TEMPLATES } from '@/services/api/habits'
import { Pressable } from '@/components/ui/pressable'
import { useRouter } from 'expo-router'

export default function ProgramsAndResourcesScreen() {
  const router = useRouter()
  const { data: assignments } = useQuery(PROGRAM_ASSIGNMENTS, { fetchPolicy: 'cache-and-network' })
  const { data: templates } = useQuery(LIST_PROGRAM_TEMPLATES, { fetchPolicy: 'cache-and-network' })
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<'habits' | 'lessons'>('habits')

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
                      <SelectItem label="Habits" value="habits" />
                      <SelectItem label="Lessons" value="lessons" />
                    </SelectContent>
                  </SelectPortal>
                </Select>
              </VStack>
            </VStack>

            {category === 'lessons' ? (
              <Text className="text-typography-600 dark:text-gray-300">Completed lessons listing coming soon.</Text>
            ) : enrolled.length === 0 ? (
              <Text className="text-typography-600 dark:text-gray-300">No programs enrolled.</Text>
            ) : (
              <VStack space="md">
                {enrolled.map((p: any) => (
                  <Pressable key={p.id} onPress={() => router.push(`/marketplace/${p.slug}?from=marketplace`)}>
                    <Box className="p-5 min-h-[120px] rounded-2xl border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800 shadow">
                      <VStack space="xs">
                        <Text className="text-lg font-semibold text-indigo-800 dark:text-indigo-200">{p.title}</Text>
                        {p.description ? (
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
    </SafeAreaView>
  )
}


