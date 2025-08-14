import React from 'react'
import { useLocalSearchParams } from 'expo-router'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Text } from '@/components/ui/text'
import { Box } from '@/components/ui/box'
import { AppBar } from '@/components/common/AppBar'

// For now, render markdown as plain text; later replace with a proper MD renderer
export default function LessonDetailScreen() {
  const params = useLocalSearchParams<{ id: string; title?: string; summary?: string }>()

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Lesson" showBackButton />
        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
          <VStack className="px-6 py-6 w-full max-w-screen-md mx-auto" space="lg">
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">{params.title || 'Lesson'}</Text>
              {params.summary ? (
                <Text className="text-typography-600 dark:text-gray-300">{params.summary}</Text>
              ) : null}
            </VStack>

            {/* Placeholder for markdown content: fetch and render later */}
            <Box className="p-4 rounded-lg border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
              <Text className="text-typography-700 dark:text-gray-200">
                Markdown content rendering will be added. For now, we show summary and leave full content as TODO.
              </Text>
            </Box>
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


