import React from 'react'
import { Pressable } from '@/components/ui/pressable'
import { Box } from '@/components/ui/box'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { Text } from '@/components/ui/text'
import { JournalTask } from '@/types/habits'
import { useRouter } from 'expo-router'
import { PenTool } from 'lucide-react-native'

export default function JournalCard({ task }: { task: JournalTask }) {
  const router = useRouter()
  return (
    <Pressable className="w-full" onPress={() => router.push('/journal/freeform')}>
      <Box className="p-4 rounded-lg border bg-purple-50 dark:bg-purple-950 border-purple-200 dark:border-purple-800 shadow">
        <VStack space="sm">
          <HStack space="sm" className="items-center">
            <Icon as={PenTool} size="md" className="text-indigo-600 dark:text-indigo-400" />
            <Text className="text-lg font-semibold text-typography-900 dark:text-white">{task.title}</Text>
          </HStack>
          {task.description ? (
            <Text className="text-typography-600 dark:text-gray-300">{task.description}</Text>
          ) : null}
        </VStack>
      </Box>
    </Pressable>
  )
}


