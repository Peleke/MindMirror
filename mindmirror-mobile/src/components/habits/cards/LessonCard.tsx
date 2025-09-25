import React from 'react'
import { Pressable } from '@/components/ui/pressable'
import { Box } from '@/components/ui/box'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { Text } from '@/components/ui/text'
import { LessonTask } from '@/types/habits'
import Markdown from 'react-native-markdown-display'
import { BookOpen } from 'lucide-react-native'
import { useThemeVariant } from '@/theme/ThemeContext'

export default function LessonCard({
  task,
  onOpen,
  onComplete,
}: {
  task: LessonTask
  onOpen: () => void
  onComplete: () => void
}) {
  const { themeId } = useThemeVariant()
  const isClassic = themeId === 'classic'
  return (
      <Pressable className="w-full" onPress={onOpen}>
        <Box className={`p-4 rounded-lg border shadow ${isClassic ? 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800' : 'bg-background-200 dark:bg-background-700 border-border-300 dark:border-border-700'}`}>
          <VStack space="sm">
            <HStack space="sm" className="items-center">
              <Icon as={BookOpen} size="md" className={isClassic ? 'text-green-700 dark:text-green-300' : 'text-primary-700 dark:text-primary-300'} />
              <Text className="text-lg font-semibold text-typography-900 dark:text-white">{task.title}</Text>
            </HStack>
            {task.summary ? (
              <Box className="rounded border border-border-200 bg-white/70 dark:bg-background-800 p-2">
                <Markdown>{task.summary}</Markdown>
              </Box>
            ) : (
              <Text className="text-typography-600 dark:text-gray-300">No summary provided.</Text>
            )}
          </VStack>
        </Box>
      </Pressable>
  )
}


