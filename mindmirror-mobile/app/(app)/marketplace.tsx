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
import { LIST_PROGRAM_TEMPLATES } from '@/services/api/habits'
import { useRouter } from 'expo-router'
import { Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectInput, SelectItem, SelectPortal, SelectTrigger } from '@/components/ui/select'

export default function MarketplaceScreen() {
  const router = useRouter()
  const { data, loading, error } = useQuery(LIST_PROGRAM_TEMPLATES, { fetchPolicy: 'cache-and-network' })
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<'habits'>('habits')

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
              <Text className="text-typography-600 dark:text-gray-300">Find habit programs to enroll in</Text>
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
                    </SelectContent>
                  </SelectPortal>
                </Select>
              </VStack>
            </VStack>

            {loading && !data ? (
              <Text className="text-typography-600 dark:text-gray-300">Loading...</Text>
            ) : error ? (
              <Text className="text-red-600 dark:text-red-400">Failed to load programs</Text>
            ) : programs.length === 0 ? (
              <Text className="text-typography-600 dark:text-gray-300">No programs found</Text>
            ) : (
              <VStack space="md">
                {programs.map((p: any) => (
                  <Pressable key={p.id} onPress={() => router.push(`/marketplace/${p.slug}?from=marketplace`)}>
                    <Box className="p-4 rounded-lg border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700 shadow">
                      <Text className="text-lg font-semibold text-typography-900 dark:text-white">{p.title}</Text>
                      {p.description ? (
                        <Text className="text-typography-600 dark:text-gray-300">{p.description}</Text>
                      ) : null}
                      <Text className="text-primary-600 dark:text-primary-400 mt-2">View</Text>
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


