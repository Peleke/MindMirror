import React from 'react'
import { Pressable } from '@/components/ui/pressable'
import { Box } from '@/components/ui/box'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { Text } from '@/components/ui/text'
import { LessonTask } from '@/types/habits'
import { BookOpen } from 'lucide-react-native'

export default function LessonCard({
  task,
  onOpen,
  onComplete,
}: {
  task: LessonTask
  onOpen: () => void
  onComplete: () => void
}) {
  return (
      <Pressable className="w-full" onPress={onOpen}>
        <Box className="p-4 rounded-lg border bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800 shadow">
          <VStack space="sm">
            <HStack space="sm" className="items-center">
              <Icon as={BookOpen} size="md" className="text-green-700 dark:text-green-300" />
              <Text className="text-lg font-semibold text-typography-900 dark:text-white">{task.title}</Text>
            </HStack>
            <Text className="text-typography-600 dark:text-gray-300">{task.summary || 'No summary provided.'}</Text>
          </VStack>
        </Box>
      </Pressable>
  )
}


