import React, { useRef, useState } from 'react'
import { Pressable } from '@/components/ui/pressable'
import { Box } from '@/components/ui/box'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { Text } from '@/components/ui/text'
import { JournalTask } from '@/types/habits'
import { useRouter } from 'expo-router'
// Swipe gestures removed per spec; keep UI stable with tap only
import { PenTool } from 'lucide-react-native'
import { useThemeVariant } from '@/theme/ThemeContext'

export default function JournalCard({ task }: { task: JournalTask }) {
  const router = useRouter()
  const [dismissed, setDismissed] = useState(false)
  const placeholder = task.description || ''
  const habitTemplateId = (task as any).habitTemplateId || ''
  const route = `/journal/freeform?placeholder=${encodeURIComponent(placeholder)}${habitTemplateId ? `&habitTemplateId=${encodeURIComponent(habitTemplateId)}` : ''}`
  const { themeId } = useThemeVariant()
  const isClassic = themeId === 'classic'
  return (
    <>
      <Pressable className="w-full" onPress={() => router.push(route)}>
        <Box className={`p-4 rounded-lg border shadow ${isClassic ? 'bg-stone-50 dark:bg-stone-900 border-stone-200 dark:border-stone-700' : 'bg-background-200 dark:bg-background-700 border-border-300 dark:border-border-700'}`}>
          <VStack space="sm">
            <HStack space="sm" className="items-center">
              <Icon as={PenTool} size="md" className={isClassic ? 'text-stone-700 dark:text-stone-300' : 'text-primary-700 dark:text-primary-300'} />
              <Text className="text-lg font-semibold text-typography-900 dark:text-white">{task.title}</Text>
            </HStack>
            {dismissed ? (
              <Text className="text-typography-600 dark:text-gray-300">Dismissed</Text>
            ) : task.description ? (
              <Text className="text-typography-600 dark:text-gray-300">{task.description}</Text>
            ) : null}
          </VStack>
        </Box>
      </Pressable>
    </>
  )
}


